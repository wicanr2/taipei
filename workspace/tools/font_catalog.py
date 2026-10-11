#!/usr/bin/env python3
"""#31：字模與原版字碼對照證據；候選辨識不直接進呈現層。"""
import argparse
import collections
import functools
import json
import operator
import struct
import zipfile
from pathlib import Path

from full_asset_catalog import sha
from rom_catalog import png


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--original', type=Path, required=True)
    ap.add_argument('--receipts', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    rom = (args.original/'RS201.ROM').read_bytes()
    assert sha(rom) == '0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29'
    members = {}
    for i in [56, 57, 58]:
        off, n = struct.unpack_from('<IH', rom, 18+16*i)
        members[i] = (off, rom[off:off+n])
    glyph_offset, glyphs = members[57]
    code_offset, codes = members[58]
    count = struct.unpack_from('<H', codes)[0]
    assert count == 402 and len(codes) == 2+count*2
    assert struct.unpack_from('<HHH', glyphs) == (15, 15, 30)
    assert len(glyphs) == 6+count*30
    records, signatures = [], collections.defaultdict(list)
    width, height = 20*32, ((count+19)//20)*32
    sheet = bytearray(width*height)
    for i in range(count):
        code = codes[2+i*2:4+i*2]
        data = glyphs[6+i*30:6+(i+1)*30]
        rows = tuple(int.from_bytes(data[r*2:r*2+2], 'big') >> 1 for r in range(15))
        encoded = code.decode('cp950')
        record = {'index': i, 'code_file_offset': code_offset+2+i*2,
                  'glyph_file_offset': glyph_offset+6+i*30, 'code_hex': code.hex(),
                  'encoded_cp950': encoded, 'glyph_sha256': sha(data), 'rows_15bit': rows,
                  'evidence': 'confirmed bytes; Unicode glyph identity needs visual review'}
        records.append(record)
        if any(rows):
            signatures[rows].append(i)
        for y, row in enumerate(rows):
            for x in range(15):
                value = 1 if row & (1 << (14-x)) else 0
                for dy in range(2):
                    at = ((i//20)*32+y*2+dy)*width+(i % 20)*32+x*2
                    sheet[at:at+2] = bytes([value, value])
    png(args.out/'glyphs.png', width, height, bytes(sheet), bytes([255,255,255,0,0,0]))
    first = {rows[:3] for rows in signatures}
    captures = []
    # 限目前已實際走過的正常畫面；這六個前景色是研究抽樣，不宣稱所有字型顏色。
    labels = ['main-menu', 'city-choice', 'new-game', 'difficulty', 'city-map',
              'power-tool', 'power-confirm', 'file-menu', 'save-dialog', 'save-name',
              'quit-confirm', 'quit-score']
    for label in labels:
        with zipfile.ZipFile(args.receipts/(label+'-capture.zip')) as z:
            frame = z.read('frame-index.bin')
        found = []
        for foreground in [0, 1, 14, 15, 31, 32]:
            board = [int(''.join('1' if p == foreground else '0' for p in frame[y*320:(y+1)*320]), 2)
                     for y in range(200)]
            occupied = [functools.reduce(operator.or_, board[y:y+15]) for y in range(186)]
            for y in range(186):
                for x in range(306):
                    shift = 320-x-15
                    if not (occupied[y] >> shift) & 0x7fff:
                        continue
                    values = []
                    for row in range(15):
                        values.append((board[y+row] >> shift) & 0x7fff)
                        if row == 2 and tuple(values) not in first:
                            break
                    if len(values) != 15:
                        continue
                    indexes = signatures.get(tuple(values))
                    if indexes:
                        found.append({'x': x, 'y': y, 'foreground': foreground,
                                      'glyph_indices': indexes,
                                      'encoded_candidates': [records[i]['encoded_cp950'] for i in indexes]})
        captures.append({'receipt': label+'-capture.zip', 'frame_sha256': sha(frame), 'matches': found})
    # 已由原版標題人工確認的十二字，字模排列及原位是固定的正對照。
    city = next(c for c in captures if c['receipt'] == 'city-map-capture.zip')
    anchors = [('離',10),('開',26),('檔',53),('案',69),('市',98),('長',114),
               ('圖',141),('表',157),('災',185),('難',201),('環',229),('境',245)]
    for ch, x in anchors:
        assert any(m['x'] == x and m['y'] == 11 and m['foreground'] == 15
                   and ch in m['encoded_candidates'] for m in city['matches']), (ch, x)
    with zipfile.ZipFile(args.receipts/'city-map-capture.zip') as z:
        native = z.read('frame-index.bin')
    negatives = []
    for ch, x in anchors:
        expected = next(g for g in records if g['encoded_cp950'] == ch)
        row, col = next((r, c) for r in range(15) for c in range(15)
                        if native[(11+r)*320+x+c] == 15)
        changed = bytearray(native)
        changed[(11+row)*320+x+col] = 14
        rows = tuple(sum((1 << (14-c)) for c in range(15)
                         if changed[(11+r)*320+x+c] == 15) for r in range(15))
        assert rows != tuple(expected['rows_15bit']) and rows not in signatures
        negatives.append({'character': ch, 'native_xy': [x+col,11+row], 'single_ink_pixel_removed': True,
                          'original_unchanged': True, 'rejected_all_glyphs': True})
    result = {'schema': 1, 'issue': 31, 'rom_sha256': sha(rom),
              'address_space': 'RS201.ROM file offsets; glyph indices start at zero',
              'font_header': [15,15,30], 'glyph_count': count, 'glyphs': records,
              'normal_captures': captures, 'confirmed_title_anchors': anchors, 'negative_controls': negatives,
              'scope': 'raw glyph/code evidence and candidate bitmap matches; not HD text implementation'}
    (args.out/'catalog.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'glyphs': count, 'anchors': len(anchors),
                      'candidate_matches': {c['receipt']: len(c['matches']) for c in captures}}, ensure_ascii=False))


if __name__ == '__main__':
    main()
