"""#31：完整底部欄位 round-trip；不推算遊戲數值。"""
import argparse
import collections
import json
import struct
import zipfile
from pathlib import Path

from full_asset_catalog import image, sha
from hd_source_audit import scene

RECTS = [(7, 175, 224, 18), (244, 175, 71, 18)]
LABELS = [(19, 107, '每'), (35, 108, '單'), (51, 109, '位'), (103, 110, '萬')]


def crop(px, rect):
    x, y, w, h = rect
    return b''.join(px[j*320+x:j*320+x+w] for j in range(y, y+h))


def source(rom):
    assert sha(rom) == '0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29'
    members = {}
    for i in [1, 56, 57, 58]:
        off, n = struct.unpack_from('<IH', rom, 18+16*i)
        members[i] = rom[off:off+n]
    _, _, base, _ = image(members[1])
    assert sha(base) == 'a35e8372b6dbd661444299f3241ad36634291b1c6657e6feacf8189c53e04dd7'
    assert struct.unpack_from('<HHH', members[56]) == (5, 7, 7)
    digits = {ch: tuple(v >> 3 for v in members[56][6+(ord(ch)-32)*7:13+(ord(ch)-32)*7])
              for ch in '0123456789-'}
    chinese = {}
    for _, index, ch in LABELS:
        code = members[58][2+index*2:4+index*2]
        assert code.decode('cp950') == ch
        chinese[index] = tuple(int.from_bytes(members[57][6+index*30+y*2:8+index*30+y*2], 'big') >> 1 for y in range(14))
    return base, digits, chinese


def stamp(px, x, y, width, rows, foreground):
    for dy, row in enumerate(rows):
        for dx in range(width):
            if row & (1 << (width-1-dx)):
                px[(y+dy)*320+x+dx] = foreground


def read_slots(frame, rebuilt, digits, xs, y, negative=False):
    text = ''
    for x in xs:
        raw = crop(frame, (x, y, 5, 7))
        if raw == crop(rebuilt, (x, y, 5, 7)):
            text += ' '
            continue
        found = []
        for ch, rows in digits.items():
            candidate = bytearray(rebuilt)
            stamp(candidate, x, y, 5, rows, 15)
            if crop(candidate, (x, y, 5, 7)) == raw:
                found.append(ch)
        if len(found) != 1:
            return None
        text += found[0]
        stamp(rebuilt, x, y, 5, digits[found[0]], 15)
    stripped = text.lstrip()
    numeric = stripped[1:] if negative and stripped.startswith('-') else stripped
    if not numeric or not numeric.isascii() or not numeric.isdigit():
        return None
    return text


def decode(frame, refs, part):
    base, digits, chinese = refs
    rebuilt = bytearray(base)
    if part == 0:
        if crop(frame, RECTS[0]) == crop(base, RECTS[0]):
            return ['']
        for x, index, _ in LABELS:
            stamp(rebuilt, x, 177, 15, chinese[index], 32)
        text = read_slots(frame, rebuilt, digits, range(67, 98, 6), 181)
        values = [text]
    else:
        values = [read_slots(frame, rebuilt, digits, range(253, 278, 6), 176),
                  read_slots(frame, rebuilt, digits, [289, 295], 176),
                  read_slots(frame, rebuilt, digits, range(253, 296, 6), 184, True)]
    if None in values or crop(frame, RECTS[part]) != crop(rebuilt, RECTS[part]):
        return None
    return values


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--original', type=Path, required=True)
    ap.add_argument('--receipts', type=Path, nargs='+', required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    refs = source((args.original/'RS201.ROM').read_bytes())
    samples, palettes = [], [set(), set()]
    negatives = 0
    for root in args.receipts:
        for path in sorted(root.rglob('*-capture.zip')):
            with zipfile.ZipFile(path) as z:
                frame = z.read('frame-index.bin'); s = json.loads(z.read('status.json'))
            if not scene(s, frame) and not path.name.startswith(('confirm-', 'submenu-')):
                continue
            fields = []
            for part, rect in enumerate(RECTS):
                result = decode(frame, refs, part)
                assert result is not None, (path, part)
                indices = sorted(set(crop(refs[0], rect)) | ({15, 32} if part == 0 else {15}))
                palettes[part].add(sha(bytes(v for i in indices for v in s['palette'][i])))
                fields.append(result)
                # 全欄 round-trip 同時保護墨跡與背景，不能只改 receipt digest。
                points = [rect[1]*320+rect[0], (181 if part == 0 else 176)*320+(97 if part == 0 else 277)]
                points.append(177*320+19 if part == 0 else 176*320+284)
                for at in points:
                    changed = bytearray(frame); changed[at] ^= 128
                    assert decode(changed, refs, part) is None, (path, part, at)
                    negatives += 1
            samples.append({'receipt': str(path), 'steps': s['steps'], 'frame_sha256': sha(frame), 'fields': fields})
    result = {'schema': 1, 'rom_sha256': sha((args.original/'RS201.ROM').read_bytes()),
              'address_space': 'RS201.ROM file offsets / zero-based glyph indices / native pixels',
              'rects': RECTS, 'labels': LABELS, 'samples': samples,
              'palette_sha256': [sorted(p) for p in palettes], 'single_pixel_negatives': negatives,
              'full_rectangle_roundtrip': True, 'scope': 'observed field strings; no numeric gameplay inference'}
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out/'catalog.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'samples': len(samples), 'palette_sha256': result['palette_sha256'],
                      'negative_controls': negatives, 'costs': sorted({r['fields'][0][0].strip() for r in samples})}, ensure_ascii=False))


if __name__ == '__main__':
    main()
