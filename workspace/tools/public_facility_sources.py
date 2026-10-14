#!/usr/bin/env python3
"""#58: export complete normal construction references, preserving all aliases."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import zipfile

from infrastructure_catalog import sources, sha, ROM_SHA, EXE_SHA
from hd_source_audit import cell, scene
from rom_catalog import png


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--run',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--case')
    ap.add_argument('--issue',type=int,default=58)
    a=ap.parse_args()
    assert a.out.parent.is_dir() and a.out.parent.stat().st_uid==os.getuid()
    a.out.mkdir(exist_ok=True)
    assert a.out.stat().st_uid==os.getuid()
    rom=Path('/orig/RS201.ROM').read_bytes()
    assert sha(rom)==ROM_SHA and sha(Path('/orig/RS201.EXE').read_bytes())==EXE_SHA
    aliases=sources(rom)
    cases=json.loads((a.run/'result-progress.json').read_text())
    for case in cases:
        if case.get('blocked') or (a.case and a.case!=case['id']):continue
        root=a.out/case['id']
        if root.exists():continue
        receipt=a.run/case['receipt']
        with zipfile.ZipFile(receipt) as z:
            s=json.loads(z.read('status.json'));frame=z.read('frame-index.bin')
        assert scene(s,frame) and sha(frame)==s['frame_index_sha256']
        left,top,w,h=case['bounds']
        tiles=[]
        for y in range(h):
            for x in range(w):
                raw=cell(frame,5+(left+x)*9,34+(top+y)*9)
                expected=next(r for r in case['known'] if r['cell']==[left+x,top+y])
                assert sha(raw)==expected['source_sha256'] and aliases[raw]==expected['sources']
                tiles.append({'cell':[x,y],'source_sha256':sha(raw),'sources':aliases[raw],
                              'used_colors':sorted(set(raw))})
        nx,ny=5+left*9,34+top*9
        raster=b''.join(frame[y*320+nx:y*320+nx+w*9] for y in range(ny,ny+h*9))
        root.mkdir()
        png(root/'source.png',w*9,h*9,raster,bytes(v for c in s['palette'] for v in c))
        subprocess.run(['convert',str(root/'source.png'),'-filter','point','-resize','864x864!',
                        '-strip',str(root/'reference.png')],check=True)
        report={'schema':1,'issue':a.issue,'id':case['id'],'tool':case['tool'],'option':case['option'],
            'size':[w,h],'fee':case['fee'],'before_budget':case['before_budget'],'after_budget':case['after_budget'],
            'rom_sha256':ROM_SHA,'exe_sha256':EXE_SHA,'receipt':str(receipt),'receipt_sha256':sha(receipt.read_bytes()),
            'frame_index_sha256':sha(frame),'steps':s['steps'],'origin':s['map_origin'],'tiles':tiles,
            'used_palette':{str(i):s['palette'][i] for i in sorted(set(raster))},
            'source_png_sha256':sha((root/'source.png').read_bytes()),'reference_png_sha256':sha((root/'reference.png').read_bytes()),
            'address_space':'RS201.ROM file offsets; zero-based member/image, native pixels',
            'level':'已證實，限原版子選單正常施工與移開游標後的完整圖像' if a.issue==58 else '已證實，限原版工具正常施工與移開游標後的完整圖像',
            'tool_version':'Python 3.11.2 / ImageMagick 6.9.11 / pinned GUI image c3d8835a9d39'}
        if not case.get('construction_tested',True):
            report.update(construction_tested=False,existing_city=case['existing_city'],native_world=case['native_world'],
                level='已證實，限原版城市正常冷讀與捲動後的完整圖像；新建施工未抽測')
        if case.get('source_prefix'):
            report.update(source_prefix=True,normal_path_complete=False)
        (root/'source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        print(case['id'],[w,h],sha((root/'source.json').read_bytes()),flush=True)


if __name__=='__main__':main()
