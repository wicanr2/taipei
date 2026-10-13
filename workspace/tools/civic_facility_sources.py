#!/usr/bin/env python3
"""#57: extract only complete facilities observed after normal construction."""
import json
import os
from pathlib import Path
import subprocess
import zipfile

from infrastructure_catalog import sources, sha, ROM_SHA, EXE_SHA
from hd_source_audit import cell, scene
from rom_catalog import png


def main():
    out = Path('/workspace/prototypes/hd-style/civic-facilities-v1')
    assert not out.exists() and out.parent.stat().st_uid == os.getuid()
    rom = Path('/orig/RS201.ROM').read_bytes()
    assert sha(rom) == ROM_SHA and sha(Path('/orig/RS201.EXE').read_bytes()) == EXE_SHA
    aliases = sources(rom)
    out.mkdir()
    buildings, receipts = [], []
    unique = set()
    for case in ['police', 'fire']:
        run = Path('/workspace/runs')/f'civic-{case}-native-r1'
        result = json.loads((run/'result.json').read_text())
        assert result['case'] == case and result['normal_gui'] and not result['checkpoint']
        pattern, = result['patterns']
        changed = [r for r in pattern['known_changes'] if not r['terrain_only']]
        left = min(r['cell'][0] for r in changed)
        top = min(r['cell'][1] for r in changed)
        width = max(r['cell'][0] for r in changed)-left+1
        height = max(r['cell'][1] for r in changed)-top+1
        assert len(changed) == width*height, '非完整矩形，停止審查'
        receipt = run/pattern['receipt']
        with zipfile.ZipFile(receipt) as z:
            status = json.loads(z.read('status.json'))
            frame = z.read('frame-index.bin')
        assert sha(frame) == status['frame_index_sha256'] and scene(status, frame)
        tiles, members = [], set()
        for y in range(height):
            for x in range(width):
                raw = cell(frame, 5+(left+x)*9, 34+(top+y)*9)
                source, = aliases[raw]
                members.add(source['member'])
                assert raw not in unique, '本批存在別名或重複，須另行審查'
                unique.add(raw)
                tiles.append({'cell':[x,y], 'member':source['member'], 'image':source['image'],
                              'source_sha256':sha(raw), 'sources':aliases[raw], 'used_colors':sorted(set(raw))})
        member, = members
        nx, ny = 5+left*9, 34+top*9
        raster = b''.join(frame[y*320+nx:y*320+nx+width*9] for y in range(ny, ny+height*9))
        path = out/f'{case}-source.png'
        png(path, width*9, height*9, raster, bytes(v for c in status['palette'] for v in c))
        reference = out/f'{case}-reference.png'
        subprocess.run(['convert',str(path),'-filter','point','-resize',f'{width*216}x{height*216}!',
                        '-strip',str(reference)],check=True)
        buildings.append({'id':case,'member':member,'normal_cell':[left,top],'size':[width,height],
                          'native_rect':[nx,ny,width*9,height*9],'tiles':tiles,
                          'source_sha256':sha(raster),'source_png_sha256':sha(path.read_bytes()),
                          'reference_png_sha256':sha(reference.read_bytes()),
                          'used_palette':{str(c):status['palette'][c] for c in sorted(set(raster))}})
        receipts.append({'case':case,'path':str(receipt),'sha256':sha(receipt.read_bytes()),
                         'result_sha256':sha((run/'result.json').read_bytes()),'steps':status['steps'],
                         'origin':status['map_origin'],'frame_index_sha256':sha(frame)})
    report = {'schema':1,'issue':57,'stage':'DRAFT','rom_sha256':ROM_SHA,'exe_sha256':EXE_SHA,
              'receipts':receipts,'buildings':buildings,'unique_tiles':len(unique),
              'address_space':'RS201.ROM file offsets; zero-based member/image; native 320x200 pixels',
              'level':'已證實，限工具 5 正常施工及移開游標後的完整圖像，不推定其他發展相位',
              'tool':'civic_facility_sources.py / Python 3.11.2 / ImageMagick 6.9.11'}
    (out/'sources.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'sha256':sha((out/'sources.json').read_bytes()),'tiles':len(unique),
                      'buildings':[(b['id'],b['member'],b['size'],[t['image'] for t in b['tiles']]) for b in buildings]}))


if __name__ == '__main__':
    main()
