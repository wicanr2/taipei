#!/usr/bin/env python3
"""#5：唯讀 ROM 成員與原始點陣圖證據。未知資料不猜解。"""
import argparse
import hashlib
import json
import struct
import zlib
from pathlib import Path

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def png(path, width, height, indices, palette):
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
    rows = b''.join(b'\0' + indices[y*width:(y+1)*width] for y in range(height))
    path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width,height,8,3,0,0,0))
                     + chunk(b'PLTE', palette) + chunk(b'IDAT', zlib.compress(rows)) + chunk(b'IEND', b''))

def raw_image(raw):
    if len(raw) < 4:
        return None
    w,h = struct.unpack_from('<HH', raw)
    return (w,h,raw[4:]) if w and h and len(raw)==4+w*h else None

def library(raw):
    if len(raw)<6:
        return None
    count=struct.unpack_from('<H',raw)[0]
    if not 0<count<1024 or 2+count*2>len(raw):
        return None
    offsets=list(struct.unpack_from('<'+'H'*count,raw,2))+[len(raw)]
    if offsets[0]!=2+count*2 or any(a>=b for a,b in zip(offsets,offsets[1:])):
        return None
    images=[raw_image(raw[a:b]) for a,b in zip(offsets,offsets[1:])]
    return (offsets,images) if all(images) else None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--original',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--frame',type=Path)
    args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    result={'schema':1,'address_space':'ROM file offsets; library offsets relative to member','roms':[]}
    tiles={}
    for name in ['RS201.ROM','RS201A.ROM']:
        raw=(args.original/name).read_bytes()
        count=struct.unpack_from('<H',raw)[0]
        assert count in (69,49), 'unverified ROM version'
        members=[struct.unpack_from('<IH',raw,18+i*16) for i in range(count)]
        assert 8+count*16<=members[0][0]
        assert all(off+n==(members[i+1][0] if i+1<count else len(raw)) for i,(off,n) in enumerate(members))
        palette=raw[members[0][0]:sum(members[0])]
        assert len(palette)==768
        records=[]
        for i,(off,n) in enumerate(members):
            data=raw[off:off+n]
            rec={'index':i,'offset':off,'bytes':n,'sha256':sha(data),'unknown_directory_bytes':raw[8+i*16:18+i*16].hex(),'kind':'unknown'}
            lib=library(data)
            if lib:
                offsets,images=lib
                rec['kind']='raw-image-library';rec['image_count']=len(images);rec['images']=[]
                for j,im in enumerate(images):
                    w,h,px=im
                    rec['images'].append({'index':j,'member_offset':offsets[j],'width':w,'height':h,'pixels_sha256':sha(px)})
                    if (w,h)==(9,9):
                        tiles.setdefault(px,[]).append([name,i,j])
                if all((im[0],im[1])==(9,9) for im in images):
                    cols=12;rows=(len(images)+cols-1)//cols
                    sheet=bytearray(cols*9*rows*9)
                    for j,(_,_,px) in enumerate(images):
                        for y in range(9):
                            at=((j//cols)*9+y)*cols*9+(j%cols)*9
                            sheet[at:at+9]=px[y*9:(y+1)*9]
                    png(args.out/f'{name}-{i:02d}-tiles.png',cols*9,rows*9,bytes(sheet),palette)
            elif raw_image(data):
                w,h,px=raw_image(data)
                rec.update(kind='raw-image',width=w,height=h,pixels_sha256=sha(px))
            records.append(rec)
        result['roms'].append({'file':name,'sha256':sha(raw),'count':count,'members':records})
    if args.frame:
        frame=args.frame.read_bytes();assert len(frame)==320*200
        best=[]
        for dy in range(9):
            for dx in range(9):
                hits=[];total=0
                for y in range(33+dy,176-8,9):
                    for x in range(16+dx,268-8,9):
                        total+=1
                        tile=b''.join(frame[(y+r)*320+x:(y+r)*320+x+9] for r in range(9))
                        if tile in tiles:
                            hits.append({'x':x,'y':y,'sources':tiles[tile]})
                best.append({'dx':dx,'dy':dy,'total':total,'hits':hits})
        match=max(best,key=lambda x:len(x['hits']))
        result['frame_match']={'frame_sha256':sha(frame),'unique_source_tiles':len(tiles),**match}
    (args.out/'catalog.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('ROM counts',[(r['file'],r['count']) for r in result['roms']])
    print('raw libraries',[(r['file'],m['index'],m['image_count']) for r in result['roms'] for m in r['members'] if m['kind']=='raw-image-library'])
    if args.frame:
        m=result['frame_match'];print('best map match',len(m['hits']),'/',m['total'],'offset',m['dx'],m['dy'])

if __name__=='__main__':
    main()
