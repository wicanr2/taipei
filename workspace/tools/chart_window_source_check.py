"""#48：核對正常圖表框架與資料區；不推定圖表統計語意。"""
import argparse
import collections
import json
import os
import struct
import zipfile
from pathlib import Path

from full_asset_catalog import image, sha

NATIVE = (66, 35, 145, 127)
DATA = (20, 20, 105, 89)


def crop(pixels, stride, rect):
    x, y, w, h = rect
    return b''.join(pixels[(y+dy)*stride+x:(y+dy)*stride+x+w] for dy in range(h))


def fixed(pixels):
    x, y, w, h = DATA
    return bytes(v for at, v in enumerate(pixels)
                 if not (x<=at%145<x+w and y<=at//145<y+h))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--original', type=Path, required=True)
    ap.add_argument('--receipts', type=Path, nargs='+', required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    assert args.out.parent.is_dir() and args.out.parent.stat().st_uid == os.getuid()
    assert not args.out.exists()
    rom = (args.original/'RS201.ROM').read_bytes()
    assert sha(rom) == '0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29'
    members, bases = [], []
    for index in range(4, 11):
        offset, size = struct.unpack_from('<IH', rom, 18+16*index)
        raw = rom[offset:offset+size]
        decoded = image(raw)
        assert decoded is not None and decoded[:2] == NATIVE[2:]
        pixels = decoded[2]
        members.append({'member':index, 'file_offset':offset, 'bytes':size,
            'sha256':sha(raw), 'decoded_sha256':sha(pixels), 'codec':decoded[3]})
        bases.append(pixels)
    border = fixed(bases[0])
    assert all(fixed(p) == border for p in bases)
    # 直接記錄嵌入圖像的可見 5×5 墨跡，不稱為 ROM56 或 EXE 繪字來源。
    glyphs = {'M':[17,27,21,17,17], 'A':[4,10,17,31,17], 'X':[17,10,4,10,17],
              'I':[14,4,4,4,14], 'N':[17,25,21,19,17]}
    labels, ink = [], set()
    for text, y in [('MAX',22), ('MIN',101)]:
        for x in [1,127]:
            points = {(x+6*j+dx,y+dy) for j,ch in enumerate(text)
                      for dy,row in enumerate(glyphs[ch]) for dx in range(5) if row & (1<<(4-dx))}
            for base in bases:
                assert all(base[dy*145+dx]==14 for dx,dy in points)
                assert all((base[(y+dy)*145+x+dx]==14) == ((x+dx,y+dy) in points)
                           for dy in range(5) for dx in range(17))
            ink |= points
            labels.append({'text':text, 'local':[x,y,17,5], 'native':[x+66,y+35,17,5],
                'color':14, 'glyph_rows':{ch:glyphs[ch] for ch in text},
                'evidence':'已證實嵌入圖像可見墨跡；不是 ROM56 字模或 EXE 繪字呼叫證據'})
    assert len(ink)==138
    assert {(at%145,at//145) for at,v in enumerate(bases[0])
            if v==14 and not(20<=at%145<125 and 20<=at//145<109)} == ink
    samples, nonmatching = [], 0
    for path in sorted({p for root in args.receipts for p in root.rglob('*-capture.zip')}):
        with zipfile.ZipFile(path) as z:
            s, frame = json.loads(z.read('status.json')), z.read('frame-index.bin')
        assert len(frame) == 64000 and sha(frame) == s['frame_index_sha256']
        raw = crop(frame, 320, NATIVE)
        if s['mode'] != 19 or not s['dos_blocked'] or fixed(raw) != border:
            nonmatching += 1
            continue
        data = crop(raw, 145, DATA)
        used = sorted(set(raw))
        samples.append({'receipt':str(path), 'receipt_sha256':sha(path.read_bytes()),
            'steps':s['steps'], 'source_sha256':sha(raw), 'data_sha256':sha(data),
            'data_palette_counts':dict(sorted(collections.Counter(data).items())),
            'used_palette':{str(i):s['palette'][i] for i in used},
            'exact_full_member_matches':[m['member'] for m,p in zip(members,bases) if p == raw],
            'evidence':'已證實完整框架；資料區只記原始像素，統計語意未知'})
    assert samples
    args.out.write_text(json.dumps({'issue':48, 'rom_sha256':sha(rom),
        'tool':'chart_window_source_check.py', 'python':__import__('sys').version.split()[0],
        'address_space':'RS201.ROM file offsets; zero-based member indices; native 320x200 pixels',
        'native':NATIVE, 'data_local':DATA, 'fixed_pixels':len(border),
        'embedded_labels':labels, 'embedded_label_pixels':len(ink),
        'fixed_sha256':sha(border), 'members':members, 'samples':samples,
        'nonmatching_receipts':nonmatching,
        'scope':'固定框架來源與實際資料像素研究；六入口控制、資料與色盤契約尚未 READY'},
        ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'matched_receipts':len(samples), 'fixed_pixels':len(border),
        'distinct_data':len({s['data_sha256'] for s in samples}), 'scope':'source research only'}))


if __name__ == '__main__':
    main()
