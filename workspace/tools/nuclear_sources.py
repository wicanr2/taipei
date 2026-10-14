#!/usr/bin/env python3
"""#46：從正常遊玩既有核電廠核對完整 ROM 來源，不注入城市。"""
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
    a=ap.parse_args()
    assert a.out.parent.is_dir() and a.out.parent.stat().st_uid==os.getuid() and not a.out.exists()
    rom=Path('/orig/RS201.ROM').read_bytes()
    assert sha(rom)==ROM_SHA and sha(Path('/orig/RS201.EXE').read_bytes())==EXE_SHA
    aliases=sources(rom)
    receipt=a.run/'existing-nuclear-capture.zip'
    with zipfile.ZipFile(receipt) as z:
        s=json.loads(z.read('status.json'));frame=z.read('frame-index.bin')
    assert scene(s,frame) and sha(frame)==s['frame_index_sha256']
    assert s['map_origin']=={'X':52,'Y':40,'Valid':True}
    tiles=[]
    for row in range(6):
        for col in range(6):
            raw=cell(frame,77+9*col,70+9*row)
            assert raw in aliases and any(r['member']==38 and r['image']==18+30*row+col for r in aliases[raw]),(col,row)
            tiles.append({'cell':[col,row],'source_sha256':sha(raw),'sources':aliases[raw],
                          'used_colors':sorted(set(raw))})
    assert len({t['source_sha256'] for t in tiles})==35
    raster=b''.join(frame[y*320+77:y*320+131] for y in range(70,124))
    a.out.mkdir()
    png(a.out/'source.png',54,54,raster,bytes(v for c in s['palette'] for v in c))
    subprocess.run(['convert',str(a.out/'source.png'),'-filter','point','-resize','864x864!',
                    '-strip',str(a.out/'reference.png')],check=True)
    report={'schema':1,'issue':46,'id':'nuclear','size':[6,6],
        'rom_sha256':ROM_SHA,'exe_sha256':EXE_SHA,'receipt':str(receipt),'receipt_sha256':sha(receipt.read_bytes()),
        'frame_index_sha256':sha(frame),'steps':s['steps'],'origin':s['map_origin'],'tiles':tiles,
        'composite_source_sha256':sha(raster),'used_palette':{str(i):s['palette'][i] for i in sorted(set(raster))},
        'source_png_sha256':sha((a.out/'source.png').read_bytes()),'reference_png_sha256':sha((a.out/'reference.png').read_bytes()),
        'address_space':'RS201.ROM file offsets; zero-based member/image, native pixels',
        'level':'已證實：正常冷讀 DISA1 既有電廠完整畫面與 ROM 逐 byte 相符；核能選項至基底18由 IDA sub_19102/sub_17BF8 證實',
        'new_construction_tested':False,
        'tool_version':'Python 3.11.2 / ImageMagick 6.9.11 / pinned GUI image c3d8835a9d39'}
    (a.out/'source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('nuclear 36 cells / 35 sources',sha((a.out/'source.json').read_bytes()))


if __name__=='__main__':main()
