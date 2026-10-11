"""#38：完整 ROM3 檔案視窗及 ROM1 離開提示重建，尚非產品辨識器。"""
import argparse
import collections
import json
import os
import struct
import zipfile
from pathlib import Path

from full_asset_catalog import image, sha

ROM_SHA = '0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29'
BROWSER = (34, 41, 67, 107)
PROMPT = (7, 175, 224, 18)


def crop(frame, rect):
    x, y, w, h = rect
    return b''.join(frame[yy*320+x:yy*320+x+w] for yy in range(y, y+h))


def stamp(pixels, width, x, y, rows, glyph_width, color):
    for dy, row in enumerate(rows):
        for dx in range(glyph_width):
            if row & (1 << (glyph_width-1-dx)):
                pixels[(y+dy)*width+x+dx] = color


def references(rom):
    assert sha(rom) == ROM_SHA
    members = {}
    for i in [1, 3, 56, 57, 58]:
        offset, size = struct.unpack_from('<IH', rom, 18+i*16)
        members[i] = (offset, rom[offset:offset+size])
    _, _, city, _ = image(members[1][1])
    w, h, browser, _ = image(members[3][1])
    assert (w, h) == (67, 107) and sha(browser) == '697dff15cb595e693f514500531196d2be7f415a2b10e9e99a1182da431657c8'
    browser = bytearray(browser)
    for yy in range(4, 18):
        browser[yy*w+5:yy*w+62] = bytes([31])*57
    for line in range(7):
        for yy in range(26+11*line, 33+11*line):
            browser[yy*w+10:yy*w+58] = bytes([136])*48
    ascii_font = members[56][1]
    assert struct.unpack_from('<HHH', ascii_font) == (5, 7, 7)
    ascii_rows = {chr(c): tuple(v >> 3 for v in ascii_font[6+(c-32)*7:13+(c-32)*7]) for c in range(32, 127)}
    reverse = collections.defaultdict(list)
    for ch, rows in ascii_rows.items():
        reverse[rows].append(ch)
    assert all(len(v) == 1 for v in reverse.values()), 'ASCII 字模別名需審查'
    chinese = []
    for i in [188, 301, 55, 302, 51, 49, 50, 167]:
        code = members[58][1][2+i*2:4+i*2]
        rows = tuple(int.from_bytes(members[57][1][6+i*30+y*2:8+i*30+y*2], 'big') >> 1 for y in range(14))
        chinese.append({'index': i, 'text': code.decode('cp950'), 'rows': rows,
            'code_hex': code.hex(), 'glyph_file_offset': members[57][0]+6+i*30,
            'code_file_offset': members[58][0]+2+i*2})
    prompt = bytearray(crop(city, PROMPT))
    for column, g in enumerate(chinese):
        stamp(prompt, PROMPT[2], 19+16*column-PROMPT[0], 177-PROMPT[1], g['rows'], 15, 32)
    for column, ch in enumerate('?(Y/N)'):
        stamp(prompt, PROMPT[2], 153+6*column-PROMPT[0], 181-PROMPT[1], ascii_rows[ch], 5, 32)
    return {'browser': bytes(browser), 'prompt': bytes(prompt), 'ascii': ascii_rows,
        'ascii_reverse': {k: v[0] for k, v in reverse.items()}, 'chinese': chinese,
        'members': {str(i): {'file_offset': off, 'bytes': len(data), 'sha256': sha(data)} for i, (off, data) in members.items()}}


def decode_browser(frame, refs):
    raw = crop(frame, BROWSER)
    rebuilt = bytearray(refs['browser'])
    width = BROWSER[2]
    rows, colors = [], []
    for line in range(8):
        y, background = (8, 31) if line == 0 else (26+11*(line-1), 136)
        values = {raw[(y+dy)*width+10+dx] for dy in range(7) for dx in range(48)}-{background}
        if len(values) > 1:
            return None
        color = next(iter(values)) if values else (15 if line == 0 else 0)
        if values and color not in ([15] if line == 0 else [31,32]):
            return None
        text = ''
        for column in range(8):
            x = 10+6*column
            glyph = tuple(sum((raw[(y+dy)*width+x+dx] == color) << (4-dx) for dx in range(5)) for dy in range(7))
            ch = refs['ascii_reverse'].get(glyph)
            if ch is None:
                return None
            text += ch
            stamp(rebuilt, width, x, y, refs['ascii'][ch], 5, color)
        rows.append(text)
        colors.append(color)
    if raw != rebuilt:
        return None
    if colors[1:].count(32) > 1:
        return None
    return {'rows': rows, 'colors': colors, 'source_sha256': sha(raw)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--original', type=Path, required=True)
    ap.add_argument('--receipts', type=Path, nargs='+', required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    assert args.out.parent.is_dir() and args.out.parent.stat().st_uid == os.getuid()
    args.out.mkdir(exist_ok=True)
    assert args.out.stat().st_uid == os.getuid()
    refs = references((args.original/'RS201.ROM').read_bytes())
    samples, rejected, negatives, palettes = [], [], [], {'browser': set(), 'quit-confirm': set()}
    palette_reference = palette_receipt = None
    for root in args.receipts:
        for path in sorted(root.rglob('*-capture.zip')):
            with zipfile.ZipFile(path) as z:
                s, frame = json.loads(z.read('status.json')), z.read('frame-index.bin')
            assert len(frame) == 64000 and sha(frame) == s['frame_index_sha256']
            browser = decode_browser(frame, refs)
            prompt = crop(frame, PROMPT) == refs['prompt']
            if browser is None and not prompt:
                rejected.append(str(path))
                continue
            family, rect = ('browser', BROWSER) if browser else ('quit-confirm', PROMPT)
            indices = sorted(set(crop(frame, rect)))
            if palette_reference is None:
                palette_reference, palette_receipt = s['palette'], str(path)
            assert all(s['palette'][i] == palette_reference[i] for i in indices), '使用中色盤有不同變體，先審查'
            palettes[family].add(sha(bytes(v for i in indices for v in s['palette'][i])))
            samples.append({'receipt': str(path), 'receipt_sha256': sha(path.read_bytes()),
                'steps': s['steps'], 'family': family, 'native': rect, 'source': browser,
                'palette_indices': indices, 'palette_sha256': sha(bytes(v for i in indices for v in s['palette'][i])),
                'dos_blocked': s['dos_blocked']})
            for x, y in [(rect[0], rect[1]), (rect[0]+rect[2]-1, rect[1]+rect[3]-1),
                         (44, 49) if browser else (19, 177)]:
                changed = bytearray(frame); changed[y*320+x] ^= 128
                assert decode_browser(changed, refs) is None if browser else crop(changed, PROMPT) != refs['prompt']
                negatives.append({'receipt': str(path), 'xy': [x,y], 'one_pixel_rejected': True})
    assert palette_reference is not None
    palette_raw = (json.dumps(palette_reference,indent=2)+'\n').encode()
    palette_path = args.out/'palette.json'
    if palette_path.exists():
        assert palette_path.stat().st_uid == os.getuid()
    palette_path.write_bytes(palette_raw)
    result = {'schema': 1, 'issue': 38, 'rom_sha256': ROM_SHA,
        'address_space': 'RS201.ROM file offsets; zero-based indices; native 320x200 pixel coordinates',
        'members': refs['members'], 'chinese_prompt': refs['chinese'],
        'browser': {'native': BROWSER, 'base_sha256': sha(refs['browser']),
                    'slots': 8, 'columns': 8, 'ascii_glyphs': 95, 'ascii_aliases': []},
        'quit_prompt': {'native': PROMPT, 'source_sha256': sha(refs['prompt'])},
        'palettes': {k: sorted(v) for k,v in palettes.items()}, 'samples': samples,
        'palette_reference_receipt': palette_receipt, 'palette_reference_sha256': sha(palette_raw),
        'negative_controls': negatives, 'nonmatching_receipts': rejected,
        'scope': '完整可見像素與字模來源；正常操作、所有可達狀態與 HD 尚待驗證'}
    catalog_path = args.out/'catalog.json'
    if catalog_path.exists():
        assert catalog_path.stat().st_uid == os.getuid()
    catalog_path.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'samples': len(samples), 'families': dict(collections.Counter(s['family'] for s in samples)),
        'negative_controls': len(negatives), 'distinct_rows': len({tuple(s['source']['rows']) for s in samples if s['source']}),
        'palette_reference_sha256':sha(palette_raw)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
