"""#39：ROM2 預算視窗的完整索引來源研究；不接入正式呈現。"""
import argparse
import collections
import json
import os
import struct
import zipfile
from pathlib import Path

from full_asset_catalog import image, sha
from file_dialog_catalog import crop, stamp

ROM_SHA = '0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29'
NATIVE = (18, 37, 235, 132)
ROWS = (29, 49, 68, 85, 103)


def references(rom):
    assert sha(rom) == ROM_SHA
    members = {}
    for index in (2, 56, 57, 58):
        offset, size = struct.unpack_from('<IH', rom, 18+16*index)
        members[index] = (offset, rom[offset:offset+size])
    w, h, pixels, kind = image(members[2][1])
    assert (w, h) == NATIVE[2:] and sha(pixels) == 'db92d35996a6c8fc112d129ab0a92d1018384495cd38b31d637df468b52c7967'
    font = members[56][1]
    assert struct.unpack_from('<HHH', font) == (5, 7, 7)
    ascii_rows = {chr(c): tuple(v >> 3 for v in font[6+(c-32)*7:13+(c-32)*7]) for c in range(32, 127)}
    reverse = collections.defaultdict(list)
    for ch, rows in ascii_rows.items():
        reverse[rows].append(ch)
    assert all(len(v) == 1 for v in reverse.values())
    slots = [{'kind': 'percent', 'row': i, 'x': 93, 'y': y, 'columns': 3} for i, y in enumerate(ROWS)]
    slots += [{'kind': 'cost', 'row': i, 'x': 168, 'y': y, 'columns': 8} for i, y in enumerate(ROWS) if i]
    slots += [{'kind': 'income', 'row': 5, 'x': 51, 'y': 120, 'columns': 8},
              {'kind': 'net', 'row': 5, 'x': 168, 'y': 120, 'columns': 8}]
    base = bytearray(pixels)
    for s in slots:
        for y in range(s['y'], s['y']+7):
            base[y*w+s['x']:y*w+s['x']+6*s['columns']] = bytes([3])*(6*s['columns'])
    return {'base': bytes(base), 'ascii': ascii_rows,
            'reverse': {rows: chars[0] for rows, chars in reverse.items()}, 'slots': slots,
            'members': {str(i): {'file_offset': off, 'bytes': len(data), 'sha256': sha(data)} for i, (off, data) in members.items()},
            'codec': kind}


def decode_budget(frame, refs):
    raw = crop(frame, NATIVE)
    rebuilt = bytearray(refs['base'])
    fields = []
    for slot in refs['slots']:
        x, y, columns = slot['x'], slot['y'], slot['columns']
        ink = {raw[(y+dy)*235+x+dx] for dy in range(7) for dx in range(columns*6)}-{3}
        if len(ink) != 1 or next(iter(ink)) not in (0, 12):
            return None
        color = next(iter(ink))
        text = ''
        for column in range(columns):
            cx = x+6*column
            rows = tuple(sum((raw[(y+dy)*235+cx+dx] == color) << (4-dx) for dx in range(5)) for dy in range(7))
            ch = refs['reverse'].get(rows)
            if ch is None:
                return None
            text += ch
            stamp(rebuilt, 235, cx, y, refs['ascii'][ch], 5, color)
        stripped = text.lstrip()
        if not stripped or text != stripped.rjust(columns) or not stripped.lstrip('-').isdigit() or stripped.count('-') > 1 or ('-' in stripped and not stripped.startswith('-')):
            return None
        fields.append({**slot, 'text': text, 'color': color})
    if raw != rebuilt:
        return None
    return {'fields': fields, 'source_sha256': sha(raw),
            'percent': [int(s['text']) for s in fields if s['kind'] == 'percent'],
            'selected_rows': [s['row'] for s in fields if s['kind'] == 'percent' and s['color'] == 12]}


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
    samples, rejected, negatives = [], [], []
    for path in sorted({p for root in args.receipts for p in root.rglob('*-capture.zip')}):
        with zipfile.ZipFile(path) as z:
            s, frame = json.loads(z.read('status.json')), z.read('frame-index.bin')
        assert len(frame) == 64000 and sha(frame) == s['frame_index_sha256']
        decoded = decode_budget(frame, refs)
        if decoded is None:
            rejected.append(str(path))
            continue
        samples.append({'receipt': str(path), 'receipt_sha256': sha(path.read_bytes()),
                        'steps': s['steps'], 'dos_blocked': s['dos_blocked'], 'source': decoded,
                        'palette_indices': sorted(set(crop(frame, NATIVE)))})
        for x, y in [(18, 37), (252, 168), (111, 66), (228, 157)]:
            changed = bytearray(frame); changed[y*320+x] ^= 128
            assert decode_budget(changed, refs) is None
            negatives.append({'receipt': str(path), 'xy': [x, y], 'one_pixel_rejected': True})
    result = {'schema': 1, 'issue': 39, 'rom_sha256': ROM_SHA,
              'address_space': 'RS201.ROM file offsets; zero-based member indices; native 320x200 pixel coordinates',
              'members': refs['members'], 'native': NATIVE, 'codec': refs['codec'],
              'base_sha256': sha(refs['base']), 'slots': refs['slots'], 'samples': samples,
              'nonmatching_receipts': rejected, 'negative_controls': negatives,
              'scope': '完整來源重建研究；尚未 READY，操作及文字來源須另審查'}
    target = args.out/'catalog.json'
    assert not target.exists() or target.stat().st_uid == os.getuid()
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'samples': len(samples), 'negative_controls': len(negatives),
                      'percent_states': sorted({tuple(s['source']['percent']) for s in samples}),
                      'selected_rows': sorted({tuple(s['source']['selected_rows']) for s in samples})}, ensure_ascii=False))


if __name__ == '__main__':
    main()
