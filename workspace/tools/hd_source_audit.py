"""#22：正常 GUI 同幀收據的完整 9×9 來源別名；只輸出本機 metadata。"""
import argparse
import hashlib
import json
import platform
import struct
import zipfile
from pathlib import Path

from rom_catalog import library

EXPECTED={
    'RS201.ROM':'0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29',
    'RS201A.ROM':'5d66f238dce650b8a407986100392ee4b8ac2aa23a033e80a7ca18ed91b3d9b0',
}
MATERIAL=set(range(103,108))|set(range(144,148))|set(range(201,205))
def sha(raw): return hashlib.sha256(raw).hexdigest()
def cell(frame,x,y):
    return b''.join(frame[(y+r)*320+x:(y+r)*320+x+9] for r in range(9))
def load(path):
    with zipfile.ZipFile(path) as z:
        frame=z.read('frame-index.bin');s=json.loads(z.read('status.json'))
    assert len(frame)==64000 and sha(frame)==s['frame_index_sha256']
    return s,frame
def scene(s,frame):
    top=b''.join(frame[y*320:y*320+270] for y in range(33))
    colors=bytes(v for i in sorted(MATERIAL) for v in s['palette'][i])
    return (s['mode']==19 and not s['dos_blocked']
            and sha(top)=='b9b27e2010b2d581cb55c349b5944492ea0077104e15126236fc50b859b51eda'
            and sha(colors)=='9bd7a6f66fe9e1da47ea3360ffbd0e114616d466034ff8b999529ae38afe6b0b')
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--original',type=Path,required=True)
    ap.add_argument('--receipts',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    sources={};libraries=[]
    for name,digest in EXPECTED.items():
        raw=(args.original/name).read_bytes();assert sha(raw)==digest
        count=struct.unpack_from('<H',raw)[0];assert count==(69 if name=='RS201.ROM' else 49)
        members=[struct.unpack_from('<IH',raw,18+i*16) for i in range(count)]
        assert members[0][0]>=8+count*16
        assert all(off+n==(members[i+1][0] if i+1<count else len(raw)) for i,(off,n) in enumerate(members))
        for member,(off,n) in enumerate(members):
            parsed=library(raw[off:off+n])
            if not parsed: continue
            offsets,images=parsed;tiles=0
            for ordinal,(w,h,px) in enumerate(images):
                if (w,h)!=(9,9): continue
                sources.setdefault(px,[]).append({'file':name,'member':member,'image':ordinal,
                    'file_offset':off+offsets[ordinal],'pixel_file_offset':off+offsets[ordinal]+4})
                tiles+=1
            if tiles: libraries.append({'file':name,'member':member,'tiles':tiles})
    samples=[]
    for path in sorted(args.receipts.rglob('*-capture.zip')):
        s,frame=load(path);known=eligible=0;unknown=[];observed={}
        for y in range(34,169,9):
            for x in range(5,266,9):
                tile=cell(frame,x,y);aliases=sources.get(tile,[])
                if not aliases: unknown.append([x,y]);continue
                known+=1;digest=sha(tile)
                if digest not in observed: observed[digest]={'cells':[],'sources':aliases,'indices':sorted(set(tile))}
                observed[digest]['cells'].append([x,y])
                if all(i in MATERIAL for i in tile) and any(a['file']=='RS201.ROM' and a['member']==59 for a in aliases): eligible+=1
        samples.append({'receipt':str(path.relative_to(args.receipts)), 'steps':s['steps'],
            'frame_sha256':sha(frame),'scene_valid':scene(s,frame),'grid_cells':435,
            'matched_cells':known,'eligible_current_prototype':eligible,'unknown_cells':unknown,'tiles':observed})
    _,before=load(args.receipts/'city-map-capture.zip')
    _,after=load(args.receipts/'uncover-power-capture.zip')
    _,loaded=load(args.receipts/'reload/load-accept-capture.zip')
    a=cell(before,230,43);b=cell(after,230,43);c=cell(loaded,230,43)
    assert a!=b and b==c and b in sources
    corrupt=bytes([255])+a[1:];assert corrupt not in sources
    result={'schema':1,'python':platform.python_version(),'input_sha256':EXPECTED,
        'address_space':'ROM file offsets; zero-based member/image indices',
        'source_tiles':sum(x['tiles'] for x in libraries),'unique_tiles':len(sources),
        'libraries':libraries,'samples':samples,
        'construction':{'xy':[230,43],'before_sha256':sha(a),'after_sha256':sha(b),
            'loaded_same':b==c,'sources':sources[b],'indices':sorted(set(b)),
            'current_material_eligible':all(i in MATERIAL for i in b)},
        'negative_corrupt_source_rejected':True,
        'limits':'完整色號匹配只證明抽樣幀來源；不證明全部動畫、捲動或正式 HD 完成。'}
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['source_tiles','unique_tiles','libraries','construction','negative_corrupt_source_rejected']},ensure_ascii=False,indent=2))
    print('samples',len(samples),'scene-valid',sum(s['scene_valid'] for s in samples))

if __name__=='__main__': main()
