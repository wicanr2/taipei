#!/usr/bin/env python3
"""#28：唯讀完整成員清單；未知格式保留，不以檔案數當圖片數。"""
import argparse
import collections
import hashlib
import json
import struct
import zipfile
from pathlib import Path

from rom_catalog import png

ROMS = {
    'RS201.ROM': ('0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29', 69),
    'RS201A.ROM': ('5d66f238dce650b8a407986100392ee4b8ac2aa23a033e80a7ca18ed91b3d9b0', 49),
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def image(data):
    if len(data) < 4:
        return None
    w, h = struct.unpack_from('<HH', data)
    if not (0 < w <= 320 and 0 < h <= 200):
        return None
    if len(data) == 4 + w*h:
        return w, h, data[4:], 'raw'
    # 研究候選：0,color,count；要求輸入與輸出均完整消耗。
    # 來源畫面的精確比對另列，不能單憑能解碼宣稱原版語意。
    at = 4
    pixels = bytearray()
    while at < len(data) and len(pixels) < w*h:
        value = data[at]
        at += 1
        if value:
            pixels.append(value)
        else:
            if at + 2 > len(data):
                return None
            value, count = data[at:at+2]
            at += 2
            pixels.extend(bytes([value])*count)
        if len(pixels) > w*h:
            return None
    if at == len(data) and len(pixels) == w*h:
        return w, h, bytes(pixels), 'zero-color-count-candidate'
    return None


def library(data):
    if len(data) < 6:
        return None
    count = struct.unpack_from('<H', data)[0]
    if not (0 < count < 1024 and 2 + count*2 <= len(data)):
        return None
    offsets = list(struct.unpack_from('<'+'H'*count, data, 2))
    unique = sorted(set(offsets))
    if unique[0] != 2 + count*2 or unique[-1] >= len(data):
        return None
    decoded = {}
    for start, end in zip(unique, unique[1:]+[len(data)]):
        im = image(data[start:end])
        if im is None:
            return None
        decoded[start] = im
    return [(offset, decoded[offset]) for offset in offsets]


def locate(frame, w, h, pixels):
    """完整來源矩形逐 byte 比對，不使用 RGB 相似度。"""
    hits = []
    first = pixels[:w]
    start = 0
    while True:
        at = frame.find(first, start)
        if at < 0:
            break
        start = at + 1
        y, x = divmod(at, 320)
        if x+w > 320 or y+h > 200:
            continue
        if all(frame[(y+r)*320+x:(y+r)*320+x+w] == pixels[r*w:(r+1)*w] for r in range(h)):
            hits.append([x, y])
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--original', type=Path, required=True)
    ap.add_argument('--receipts', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.receipts/'city-map-capture.zip') as z:
        status = json.loads(z.read('status.json'))
    palette = bytes(c for rgb in status['palette'] for c in rgb)
    frames = {}
    for file in sorted(args.receipts.rglob('*-capture.zip')):
        with zipfile.ZipFile(file) as z:
            data = z.read('frame-index.bin')
        assert len(data) == 64000
        key = sha(data)
        frames.setdefault(key, {'pixels': data, 'receipts': []})['receipts'].append(str(file.relative_to(args.receipts)))
    result = {
        'schema': 1, 'scope': '全部 ROM 成員及候選圖片，不是 HD 完成清單',
        'address_space': 'ROM file offsets; image indices start at zero',
        'tool': 'full_asset_catalog.py / Python '+__import__('platform').python_version(),
        'preview_palette': 'actual city receipt palette; not a claim about other scenes',
        'roms': [], 'images': [], 'unknown_members': [], 'receipt_frame_count': len(frames),
    }
    for name, (expected, count) in ROMS.items():
        raw = (args.original/name).read_bytes()
        assert sha(raw) == expected, (name, 'SHA-256 mismatch')
        assert struct.unpack_from('<H', raw)[0] == count
        members = [struct.unpack_from('<IH', raw, 18+i*16) for i in range(count)]
        assert members[0][0] >= 8+count*16
        assert all(n > 0 and off+n == (members[i+1][0] if i+1<count else len(raw)) for i, (off, n) in enumerate(members))
        records = []
        for index, (offset, size) in enumerate(members):
            data = raw[offset:offset+size]
            member = {'index': index, 'offset': offset, 'bytes': size, 'sha256': sha(data), 'kind': 'unknown'}
            entries = library(data)
            if entries:
                member['kind'] = 'image-library'
            else:
                single = image(data)
                entries = [(0, single)] if single else []
                if single:
                    member['kind'] = 'image'
            member['image_references'] = len(entries)
            member['unique_offsets'] = len({off for off, im in entries})
            for number, (relative, (w, h, pixels, encoding)) in enumerate(entries):
                ident = f'{name}-{index:02d}-{number:03d}'
                rec = {
                    'id': ident, 'rom': name, 'member': index, 'image': number,
                    'file_offset': offset+relative, 'member_offset': relative,
                    'width': w, 'height': h, 'encoding': encoding, 'pixels_sha256': sha(pixels),
                    'evidence': 'confirmed container' if encoding == 'raw' else 'hypothesis; exact-sized candidate only',
                    'redraw_batch': 'map' if (w, h) == (9, 9) else 'needs-normal-scene-mapping',
                }
                # 小圖塊來源已由 #22 盤點；本次查非圖塊的正常畫面。
                if (w, h) != (9, 9):
                    png(args.out/(ident+'.png'), w, h, pixels, palette)
                    matches = []
                    for digest, frame in frames.items():
                        hits = locate(frame['pixels'], w, h, pixels)
                        if hits:
                            matches.append({'frame_sha256': digest, 'xy': hits, 'receipts': frame['receipts']})
                    rec['exact_normal_frame_matches'] = matches
                    if matches:
                        rec['evidence'] = 'confirmed visible indexed pixels; palette and timing separate'
                result['images'].append(rec)
            if not entries:
                result['unknown_members'].append({'rom': name, **member, 'prefix_hex': data[:24].hex()})
            records.append(member)
        result['roms'].append({'file': name, 'sha256': expected, 'count': count, 'members': records})
    by_hash = collections.defaultdict(list)
    for record in result['images']:
        by_hash[(record['width'], record['height'], record['pixels_sha256'])].append(record['id'])
    result['aliases'] = [ids for ids in by_hash.values() if len(ids) > 1]
    result['counts'] = {
        'members': sum(r['count'] for r in result['roms']),
        'image_references': len(result['images']), 'unique_images': len(by_hash),
        'unknown_members': len(result['unknown_members']),
        'encodings': dict(collections.Counter(i['encoding'] for i in result['images'])),
        'images_with_normal_frame_match': sum(bool(i.get('exact_normal_frame_matches')) for i in result['images']),
    }
    (args.out/'catalog.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(result['counts'], ensure_ascii=False))
    print('matched', [(i['id'], i['width'], i['height']) for i in result['images'] if i.get('exact_normal_frame_matches')])


if __name__ == '__main__':
    main()
