"""#29：固定底圖對正常 GUI 的框架、動態欄位及工具外框來源盤點。"""
import argparse
import collections
import json
import struct
import zipfile
from pathlib import Path

from full_asset_catalog import image
from hd_source_audit import sha, scene

ROM_SHA = '0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29'
BASE_SHA = 'a35e8372b6dbd661444299f3241ad36634291b1c6657e6feacf8189c53e04dd7'


def box(px, rect):
    x, y, w, h = rect
    return b''.join(px[row*320+x:row*320+x+w] for row in range(y, y+h))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--original', type=Path, required=True)
    ap.add_argument('--receipts', type=Path, nargs='+', required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    raw = (args.original/'RS201.ROM').read_bytes()
    assert sha(raw) == ROM_SHA
    off, n = struct.unpack_from('<IH', raw, 34)
    assert (off, n) == (1888, 10774)
    w, h, base, encoding = image(raw[off:off+n])
    assert (w, h) == (320, 200) and sha(base) == BASE_SHA
    # 這些是待正常畫面審查的候選範圍，輸出不授權正式覆繪。
    regions = [('top', [0, 0, 270, 34]), ('map-left', [0, 34, 5, 135]),
               ('map-right', [266, 34, 4, 135]), ('map-bottom', [0, 169, 270, 5]),
               ('left-status', [7, 175, 224, 18]), ('right-status', [244, 175, 71, 18])]
    status_excluded = {(x, y) for x0, y0, ww, hh in [regions[-2][1], regions[-1][1]]
                       for y in range(y0, y0+hh) for x in range(x0, x0+ww)}
    slot_excluded = {(x, y) for i in range(14) for y in range(4+24*(i//2), 26+24*(i//2))
                     for x in range(273+23*(i % 2), 295+23*(i % 2))}
    masks = {'toolbar-plate': [(x, y) for y in range(174) for x in range(270, 320) if (x, y) not in slot_excluded],
             'status-frame': [(x, y) for y in range(174, 200) for x in range(320) if (x, y) not in status_excluded]}
    result = {'schema': 1, 'rom_sha256': ROM_SHA, 'base_sha256': BASE_SHA,
              'encoding': encoding, 'source_member': 1, 'file_offset': off,
              'regions': [], 'masks': [], 'slots': [], 'samples': []}
    for name, rect in regions:
        px = box(base, rect)
        # 原版另以白色色號 15 畫上十二個已證實中文字，ROM1 沒有這些字。
        indices = set(px) | ({15} if name == 'top' else set())
        result['regions'].append({'id': name, 'native': rect, 'source_sha256': sha(px), 'indices': sorted(indices)})
    for name, points in masks.items():
        px = bytes(base[y*320+x] for x, y in points)
        result['masks'].append({'id': name, 'points': len(points), 'source_sha256': sha(px), 'indices': sorted(set(px))})
    slots = [collections.defaultdict(list) for i in range(14)]
    palettes = collections.defaultdict(set)
    for root in args.receipts:
        for path in sorted(root.rglob('*-capture.zip')):
            with zipfile.ZipFile(path) as z:
                s = json.loads(z.read('status.json')); frame = z.read('frame-index.bin')
            assert len(frame) == 64000 and sha(frame) == s['frame_index_sha256']
            if not scene(s, frame):
                continue
            row = {'receipt': str(path), 'steps': s['steps'], 'frame_sha256': sha(frame), 'regions': {}, 'masks': {}}
            for region in result['regions']:
                value = box(frame, region['native'])
                row['regions'][region['id']] = {'matched_base': sha(value) == region['source_sha256'], 'sha256': sha(value)}
                palettes[region['id']].add(sha(bytes(c for index in region['indices'] for c in s['palette'][index])))
            for mask in result['masks']:
                points = masks[mask['id']]
                value = bytes(frame[y*320+x] for x, y in points)
                diffs = [[x, y, base[y*320+x], frame[y*320+x]] for x, y in points if base[y*320+x] != frame[y*320+x]]
                row['masks'][mask['id']] = {'matched_base': sha(value) == mask['source_sha256'], 'differences': diffs}
                palettes[mask['id']].add(sha(bytes(c for index in mask['indices'] for c in s['palette'][index])))
            for i in range(14):
                rect = [273+23*(i % 2), 4+24*(i//2), 22, 22]
                native = box(frame, rect)
                original = box(base, rect)
                diffs = [[j % 22, j//22, original[j], native[j]] for j in range(484) if native[j] != original[j]]
                assert all(x in [0, 21] or y in [0, 21] for x, y, _, _ in diffs), (path, i, '圖示內部變化')
                slots[i][sha(native)].append({'receipt': str(path), 'differences': diffs, 'palette': s['palette']})
            result['samples'].append(row)
    result['palette_hashes'] = {key: sorted(values) for key, values in palettes.items()}
    for i, variants in enumerate(slots):
        result['slots'].append({'index': i, 'native': [273+23*(i % 2), 4+24*(i//2), 22, 22],
                                'variants': [{'source_sha256': key, 'samples': samples} for key, samples in variants.items()]})
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out/'catalog.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'normal_city_samples': len(result['samples']),
                      'unmatched_regions': {r['id']: sum(not s['regions'][r['id']]['matched_base'] for s in result['samples']) for r in result['regions']},
                      'unmatched_masks': {r['id']: sum(not s['masks'][r['id']]['matched_base'] for s in result['samples']) for r in result['masks']},
                      'slot_variants': [len(s['variants']) for s in result['slots']]}, ensure_ascii=False))


if __name__ == '__main__':
    main()
