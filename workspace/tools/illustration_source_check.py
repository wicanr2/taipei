#!/usr/bin/env python3
"""039：獨立從原版bytes重建透明／裁切合成，核對原版返回後緩衝。"""
import argparse
import json
from pathlib import Path
import struct

from full_asset_catalog import ROMS,image,sha
from illustration_sources import iv2


def compose(pixels,width,x,y,clip,before,transparent,key):
    left,top,w,h=clip;expected=bytearray(before)
    for dy in range(h):
        for dx in range(w):
            value=pixels[(top+dy-y)*width+left+dx-x]
            if not transparent or value!=key:expected[dy*w+dx]=value
    return expected


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--inputs',type=Path,required=True)
    ap.add_argument('--audit',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    assert not a.out.exists()
    inventory=json.loads((a.inputs/'inventory.json').read_text());audit=json.loads((a.audit/'audit.json').read_text())
    assert audit['inventory_sha256']==sha((a.inputs/'inventory.json').read_bytes())
    assert audit['normal_exe_entry'] and not audit['state_injection'] and not audit['checkpoint'] and not audit['normal_gui']
    roms={name:Path('/orig',name).read_bytes() for name in ROMS}
    assert all(sha(raw)==ROMS[name][0] for name,raw in roms.items())
    sources={}
    for r in inventory['images']:
        rom=roms[r['rom']];off,size=struct.unpack_from('<IH',rom,18+r['member']*16)
        end=min([q['file_offset'] for q in inventory['images'] if q['rom']==r['rom'] and q['member']==r['member'] and q['file_offset']>r['file_offset']]+[off+size])
        raw=rom[r['file_offset']:end];assert sha(raw)==r['raw_sha256']
        decoded=iv2(raw) if r['encoding']=='iv2' else image(raw)[:3]
        width,height,pixels=decoded
        assert [width,height]==[r['width'],r['height']] and sha(pixels)==r['pixels_sha256']
        sources[r['id']]=(width,height,pixels)
    records=[];negatives=0;empty=0
    for call in audit['calls']:
        width,height,pixels=sources[call['ID']];x,y=call['X'],call['Y'];clip=call['Clip']
        left,top,w,h=clip;assert w>0 and h>0 and 0<=left-x and 0<=top-y and left+w-x<=width and top+h-y<=height
        before=(a.audit/(call['Label']+'-before.bin')).read_bytes();after=(a.audit/(call['Label']+'-after.bin')).read_bytes()
        assert len(before)==len(after)==w*h and sha(before)==call['BeforeSHA'] and sha(after)==call['AfterSHA']
        ea=call['ida_loader_linear'];transparent=ea in [0x1605e,0x160c5,0x16164,0x16210]
        assert ea in [0x1605e,0x160c5,0x16129,0x16164,0x161c3,0x16210] and transparent==call['Transparent']
        if ea in [0x1605e,0x160c5,0x16164]:assert call['Key']==255
        expected=compose(pixels,width,x,y,clip,before,transparent,call['Key'])
        assert after==expected and sha(expected)==call['ExpectedSHA']
        written=[(top+dy-y)*width+left+dx-x for dy in range(h) for dx in range(w)
            if not transparent or pixels[(top+dy-y)*width+left+dx-x]!=call['Key']]
        if written:
            altered=bytearray(pixels);altered[written[0]]^=1
            if transparent and altered[written[0]]==call['Key']:altered[written[0]]^=2
            assert after!=compose(altered,width,x,y,clip,before,transparent,call['Key'])
            negatives+=1
        else:empty+=1
        records.append({'id':call['ID'],'label':call['Label'],'sample':call['Sample'],'clip':clip,'step':call['Step'],
            'ida_loader_linear':ea,'full_source_visible':w*h==width*height,'painted_source_pixels':len(written),
            'original_after_sha256':sha(after),'source_pixel_negative_effective':bool(written)})
    assert records and negatives
    result={'schema':1,'issue':32,'stage':'DRAFT','audit_sha256':sha((a.audit/'audit.json').read_bytes()),
        'inventory_sha256':sha((a.inputs/'inventory.json').read_bytes()),'original_files_verified':list(roms),
        'records':records,'effective_source_negative_controls':negatives,'empty_clips':empty,
        'full_source_samples':sum(r['full_source_visible'] for r in records),
        'normal_gui':False,'state_injection':False,'native_exit_tested':False,'tool_sha256':sha(Path(__file__).read_bytes()),
        'scope':'唯讀正常入口繪圖呼叫與完整返回後緩衝；原版bytes獨立重解，非HD與發布畫面／GUI驗收'}
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('PASS',len(records),'original call samples',result['full_source_samples'],'full source views',negatives,'effective source controls',sha(a.out.read_bytes()))


if __name__=='__main__':main()
