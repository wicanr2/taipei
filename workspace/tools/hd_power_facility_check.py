"""#46／027：以原版 ROM 與 READY 前完整原型獨立核對正式火力畫面。"""
import argparse
import functools
import json
import struct
from pathlib import Path

from hd_file_dialogs_check import rgba
from hd_source_audit import cell,scene,sha


@functools.lru_cache(maxsize=1)
def references():
    root=Path('/workspace/prototypes/hd-style')
    raw=(root/'power-facility-ready-v1/manifest.json').read_bytes()
    assert sha(raw)=='bd571fa7a9ca49cbc8de1adde54cf1aa64642db4ff29bf158a567a75ca027c11'
    manifest=json.loads(raw)
    rom=Path('/orig/RS201.ROM').read_bytes()
    assert sha(rom)==manifest['rom_sha256']=='0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29'
    at,length=struct.unpack_from('<IH',rom,18+38*16)
    assert struct.unpack_from('<H',rom,at)[0]==180 and length==15662
    atlas=root/'power-facility-v2/thermal-hd.png'
    assert sha(atlas.read_bytes())==manifest['atlas_sha256']=='ceb6c9a9dfe64330c4004c6492b6c0997fc84a2f8881688d506c44e481de8dc2'
    pixels=rgba(atlas,(216,216))
    sources={}
    assert len(manifest['sources'])==36
    for record in manifest['sources']:
        col,row=record['cell']
        index=12+row*30+col
        assert record['image']==index
        a,b=struct.unpack_from('<HH',rom,at+2+index*2)
        assert b-a==85 and rom[at+a:at+a+4]==b'\x09\x00\x09\x00'
        source=rom[at+a+4:at+b]
        assert len(source)==81 and sha(source)==record['source_sha256']
        assert record['used_colors']==sorted(set(source)) and source not in sources
        fragment=b''.join(pixels[((row*36+y)*216+col*36)*4:((row*36+y)*216+col*36+36)*4] for y in range(36))
        sources[source]=(index,fragment)
    return sources,manifest


def audit_power_facility(s,frame,pixels):
    if 'power_facility' not in s['hd']:return set()
    sources,manifest=references()
    origin=s.get('map_origin') or {}
    active=(s['hd_enabled'] and scene(s,frame) and origin.get('Valid')
        and 0<=origin['X']<=76 and 0<=origin['Y']<=74)
    matched,painted,images,reasons=0,set(),{},{}
    for row in range(15):
        for col in range(29):
            x,y=5+col*9,34+row*9
            source=cell(frame,x,y)
            if not active or source not in sources:continue
            matched+=1
            index,expected=sources[source]
            if any(s['palette'][i]!=manifest['palette'][str(i)] for i in set(source)):
                reason='palette-mismatch'
                expected=b''.join(b''.join(bytes(s['palette'][i]+[255])*4 for i in source[r*9:(r+1)*9])*4 for r in range(9))
            else:
                reason='matched-power-facility'
                painted.add((x,y))
                images[str(index)]=images.get(str(index),0)+1
            reasons[reason]=reasons.get(reason,0)+1
            for dy in range(36):
                at=((y*4+dy)*1280+x*4)*4
                assert pixels[at:at+144]==expected[dy*144:(dy+1)*144],(col,row,'火力完整原型像素失配')
    reported=s['hd']['power_facility']
    assert reported['matched']==matched and reported['painted']==len(painted) and reported['fallback']==matched-len(painted)
    assert reported.get('images',{})==images and reported.get('reasons',{})==reasons
    return painted


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--receipts',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    assert not args.out.exists()
    from hd_scroll_check import audit_bundle,source59
    terrain=source59(Path('/orig'))
    records=[]
    for path in sorted(args.receipts.rglob('*-capture.zip')):
        s,_,_,_,_=audit_bundle(path,terrain)
        records.append({'receipt':str(path.relative_to(args.receipts)),'steps':s['steps'],
            'theme':s['hd_enabled'],'origin':s.get('map_origin'),'power_facility':s['hd']['power_facility']})
    assert records and any(r['power_facility']['painted'] for r in records)
    args.out.write_text(json.dumps({'issue':46,'records':records,'full_source_pixels_and_fallback':True,
        'scope':'正式原子收據像素／來源／統計核對；正常流程、原版狀態及存檔另核對'},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'receipts':len(records),'painted_receipts':sum(bool(r['power_facility']['painted']) for r in records)}))


if __name__=='__main__':main()
