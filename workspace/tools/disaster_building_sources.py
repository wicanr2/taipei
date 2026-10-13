#!/usr/bin/env python3
"""#56: verify three complete 4x4 buildings from the normal DISA1 receipt."""
import argparse
import json
import os
from pathlib import Path
import struct
import subprocess
import zipfile

from infrastructure_catalog import sources, sha, ROM_SHA, EXE_SHA
from hd_source_audit import cell, scene
from rom_catalog import png

TARGETS = [(34, 24, 11), (35, 20, 1), (36, 10, 7)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--original', type=Path, required=True)
    ap.add_argument('--receipt', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    assert args.out.parent.is_dir() and not args.out.exists()
    assert args.out.parent.stat().st_uid == os.getuid()
    rom = (args.original / 'RS201.ROM').read_bytes()
    assert sha(rom) == ROM_SHA and sha((args.original / 'RS201.EXE').read_bytes()) == EXE_SHA
    aliases = sources(rom)
    with zipfile.ZipFile(args.receipt) as z:
        status = json.loads(z.read('status.json'))
        frame = z.read('frame-index.bin')
    assert sha(frame) == status['frame_index_sha256'] and scene(status, frame)
    assert any(f.get('Op') == 'read' and f.get('Name', '').lower() == 'disa1.dsa' for f in status['file_ops'])
    args.out.mkdir()
    records, unique = [], {}
    for member, col, row in TARGETS:
        tiles = []
        for y in range(4):
            for x in range(4):
                raw = cell(frame, 5 + (col+x)*9, 34 + (row+y)*9)
                expected = 4 + y*24 + x
                assert any(a['member'] == member and a['image'] == expected for a in aliases.get(raw, []))
                used = sorted(set(raw))
                record = {'cell': [x, y], 'member': member, 'image': expected,
                          'source_sha256': sha(raw), 'sources': aliases[raw],
                          'used_colors': used}
                tiles.append(record)
                unique.setdefault(sha(raw), []).append([member, expected])
        nx, ny = 5 + col*9, 34 + row*9
        raster = b''.join(frame[y*320+nx:y*320+nx+36] for y in range(ny, ny+36))
        path = args.out / f'{member}-source.png'
        png(path, 36, 36, raster, bytes(v for c in status['palette'] for v in c))
        ref = args.out / f'{member}-reference.png'
        subprocess.run(['convert', str(path), '-filter', 'point', '-resize', '864x864!', '-strip', str(ref)], check=True)
        used = sorted(set(raster))
        records.append({'member': member, 'normal_cell': [col, row], 'native_rect': [nx, ny, 36, 36],
                        'world_cell': [status['map_origin']['X']+col, status['map_origin']['Y']+row],
                        'source_sha256': sha(raster), 'source_png_sha256': sha(path.read_bytes()),
                        'reference_png_sha256': sha(ref.read_bytes()), 'tiles': tiles,
                        'used_palette': {str(c): status['palette'][c] for c in used}})
    report = {'schema': 1, 'issue': 56, 'stage': 'DRAFT',
              'rom_sha256': ROM_SHA, 'exe_sha256': EXE_SHA,
              'receipt': str(args.receipt), 'receipt_sha256': sha(args.receipt.read_bytes()),
              'frame_index_sha256': sha(frame), 'steps': status['steps'], 'origin': status['map_origin'],
              'address_space': 'RS201.ROM file offsets, zero-based member/image; native 320x200 pixels',
              'tool': 'disaster_building_sources.py / Python 3.11.2 / ImageMagick 6.9.11',
              'buildings': records, 'unique_tiles': len(unique),
              'duplicate_sources': [v for v in unique.values() if len(v)>1],
              'level': '已證實，限正常 DISA1 可見複合圖及完整 ROM 來源；不推定建造或發展規則'}
    (args.out / 'sources.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'buildings': len(records), 'tiles': 48, 'unique_tiles': len(unique),
                      'duplicates': report['duplicate_sources']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
