"""#46／027 DRAFT：保留完整電廠幾何的 B 材質離線原型。"""
import argparse
import json
import math
import os
import subprocess
import zipfile
from pathlib import Path

from hd_file_dialogs_check import rgba
from infrastructure_prototype import png
from hd_source_audit import sha

MATERIALS={'industrial-paint':'25e851a18d35960f95be339337b706e3b2c433686a6ecd32e9cfc176cdde8094',
    'sand':'90c23e56f9c8a116fbe8cc7d8b2c1a494eb7044d3ff57c3ff28a60f5b911717f',
    'forest':'0bb1f136ce10e014e27626ab11dc5f3c18431fdcb9c6ab8fbd063b478e8644f7'}


def geometry(source,width,height):
    indices=bytearray(); weights=bytearray()
    for y in range(height*4):
        for x in range(width*4):
            nx,ny=(x+.5)/4-.5,(y+.5)/4-.5
            left,top=math.floor(nx),math.floor(ny)
            fx,fy=nx-left,ny-top
            fx,fy=fx*fx*(3-2*fx),fy*fy*(3-2*fy)
            parts={}
            for dx,dy,weight in [(0,0,(1-fx)*(1-fy)),(1,0,fx*(1-fy)),(0,1,(1-fx)*fy),(1,1,fx*fy)]:
                index=source[min(height-1,max(0,top+dy))*width+min(width-1,max(0,left+dx))]
                parts[index]=parts.get(index,0)+weight
            values=sorted(parts)
            quantized=[int(parts[i]*255) for i in values]
            ranked=sorted(range(len(values)),key=lambda n:(-(parts[values[n]]*255-quantized[n]),values[n]))
            for n in ranked[:255-sum(quantized)]:quantized[n]+=1
            indices.extend(values+[0]*(4-len(values))); weights.extend(quantized+[0]*(4-len(values)))
    for y in range(height):
        for x in range(width):
            for dy in [1,2]:
                for dx in [1,2]:
                    at=((y*4+dy)*width*4+x*4+dx)*4
                    dominant=max(range(4),key=lambda j:weights[at+j])
                    assert indices[at+dominant]==source[y*width+x]
    assert all(sum(weights[i:i+4])==255 for i in range(0,len(weights),4))
    return indices,weights


def paint(index,x,y,palette,textures):
    original=palette[index]
    if 96<=index<=107:
        texture=textures['forest']; factor=original[1]*700//166
    elif 193<=index<=208:
        texture=textures['sand']; factor=sum(original)*1000//534
    else:
        at=(((y*4)%1254)*1254+(x*4)%1254)*4
        grain=sum(textures['industrial-paint'][at:at+3])-480
        r,g,b=original
        base=[r*95+1000,g*100+1400,b*100+2000] if r==g==b else [v*90+800 for v in original]
        return [max(0,min(255,round((v*3+grain*25)/300))) for v in base]
    at=((y%1254)*1254+x%1254)*4
    return [min(255,v*factor//1000) for v in texture[at:at+3]]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--original',type=Path,required=True)
    parser.add_argument('--source-check',type=Path,required=True)
    parser.add_argument('--materials',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--illustration',type=Path,help='固定 B 插畫候選；只作尺寸正規化與原圖格切片')
    args=parser.parse_args()
    assert args.out.parent.is_dir() and args.out.parent.stat().st_uid==os.getuid() and not args.out.exists()
    proof=json.loads(args.source_check.read_text())
    rom=(args.original/'RS201.ROM').read_bytes()
    assert sha(rom)==proof['rom_sha256']=='0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29'
    textures={}
    for name,digest in (MATERIALS.items() if args.illustration is None else []):
        path=args.materials/(name+'-b-v1.png')
        assert sha(path.read_bytes())==digest
        raw=rgba(path,(1254,1254))
        textures[name]=raw
    args.out.mkdir()
    outputs=[]
    for case in proof['cases']:
        receipt=args.source_check.parent/case['receipt']
        assert sha(receipt.read_bytes())==case['receipt_sha256']
        with zipfile.ZipFile(receipt) as z:s,frame=json.loads(z.read('status.json')),z.read('frame-index.bin')
        assert sha(frame)==s['frame_index_sha256']
        ox,oy,width,height=case['native_rect']
        source=b''.join(frame[y*320+ox:y*320+ox+width] for y in range(oy,oy+height))
        assert sha(source)==case['composite_source_sha256']
        for record in case['cells']:
            cx,cy=record['relative_cell']
            cell=b''.join(source[(cy*9+y)*width+cx*9:(cy*9+y)*width+cx*9+9] for y in range(9))
            assert sha(cell)==record['source_sha256']
            for ref in record['sources']:
                at=ref['pixel_file_offset']; assert rom[at-4:at]==b'\x09\x00\x09\x00' and rom[at:at+81]==cell
        indices,weights=geometry(source,width,height)
        native=bytearray(); rendered=bytearray()
        illustration=None
        if args.illustration is not None:
            assert case['label']=='thermal' and (width,height)==(54,54)
            assert sha(args.illustration.read_bytes())=='16642276a2ba54203e2b745525e65ba92106698fc9ac9b1151720f621211aa2c'
            assert len(rgba(args.illustration,(1254,1254)))==1254*1254*4
            illustration=subprocess.run(['convert',str(args.illustration),'-filter','Lanczos','-resize','216x216!',
                '-depth','8','rgba:-'],check=True,stdout=subprocess.PIPE).stdout
            assert len(illustration)==216*216*4 and set(illustration[3::4])=={255}
        for y in range(height*4):
            for x in range(width*4):
                native.extend(s['palette'][source[y//4*width+x//4]]+[255])
                at=(y*width*4+x)*4; total=[0,0,0]
                if illustration is not None:
                    rendered.extend(illustration[at:at+4])
                    continue
                for index,weight in zip(indices[at:at+4],weights[at:at+4]):
                    if weight:
                        for channel,value in enumerate(paint(index,x,y,s['palette'],textures)):total[channel]+=value*weight
                rendered.extend([v//255 for v in total]+[255])
        label=case['label']
        files={label+'-native4x.png':png(native,width*4,height*4),label+'-hd.png':png(rendered,width*4,height*4),
            label+'-indices.bin':indices,label+'-weights.bin':weights}
        comparison=b''.join(native[y*width*16:(y+1)*width*16]+rendered[y*width*16:(y+1)*width*16] for y in range(height*4))
        files[label+'-comparison.png']=png(comparison,width*8,height*4)
        fragments=[]
        if illustration is not None:
            for record in case['cells']:
                col,row=record['relative_cell']
                source_cell=b''.join(source[(row*9+y)*width+col*9:(row*9+y)*width+col*9+9] for y in range(9))
                fragment=b''.join(rendered[((row*36+y)*width*4+col*36)*4:((row*36+y)*width*4+col*36+36)*4] for y in range(36))
                stem=f'{label}-{row}-{col}'
                files[stem+'-source.bin']=source_cell
                files[stem+'.png']=png(fragment,36,36)
                fragments.append(dict(record,source_file=stem+'-source.bin',image_file=stem+'.png',
                    image_sha256=sha(files[stem+'.png'])))
        for name,data in files.items():(args.out/name).write_bytes(data)
        outputs.append({'label':label,'native_size':[width,height],'hd_size':[width*4,height*4],
            'source_sha256':sha(source),'used_palette':case['used_palette'],'cells':case['cells'],
            'source_receipt':str(receipt),'source_receipt_sha256':case['receipt_sha256'],
            'files':{name:sha(data) for name,data in files.items()},'center_checks':width*height*4,
            'fragments':fragments})
    result={'schema':1,'issue':46,'stage':'DRAFT','geometry_version':3,
        'tool':'power_facility_prototype.py / Python 3.11.2','tool_sha256':sha(Path(__file__).read_bytes()),
        'source_check_sha256':sha(args.source_check.read_bytes()),'rom_sha256':proof['rom_sha256'],
        'materials':MATERIALS if args.illustration is None else {},'cases':outputs,
        'illustration_sha256':sha(args.illustration.read_bytes()) if args.illustration is not None else None,
        'illustration_processing':'ImageMagick 6.9.11-60 / Lanczos 1254→216 / RGBA8 / fixed PNG' if args.illustration is not None else None,
        'scope':'固定原版複合來源／幾何與 B 材質離線候選；尚未獨立核對或正式 GUI，不接產品'}
    (args.out/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'cases':len(outputs),'center_checks':sum(c['center_checks'] for c in outputs)},ensure_ascii=False))


if __name__=='__main__':main()
