#!/usr/bin/env python3
"""039 READY：固定原型與原版來源重建正式本機圖片，不修改原型。"""
import argparse
import json
import os
from pathlib import Path
import struct
import zlib

from full_asset_catalog import ROMS, image, sha
from illustration_sources import iv2
from hd_file_dialogs_check import rgba

INVENTORY = 'd67d234268f912cfc049ebad59ecf706d967ee2e6ce6d5d95a9c21678d356f5a'
PROTOTYPE = 'ebe1576eeb2899058aff4ef8a3bba4b64a1e24f56f9cbb4ed17b15fd54dc519b'
CHECK = '9b62f6e54995669823ae2c192fb7237ec365d0d104abf53725c759977a04862d'


def png(raw, w, h):
    def chunk(kind, data):
        return struct.pack('>I', len(data))+kind+data+struct.pack('>I', zlib.crc32(kind+data))
    rows = b''.join(b'\0'+raw[y*w*4:(y+1)*w*4] for y in range(h))
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))+chunk(b'IDAT', zlib.compress(rows, 9))+chunk(b'IEND', b'')


def palette(rom, member):
    off, size = struct.unpack_from('<IH', rom, 18+member*16)
    assert size == 768
    expand = lambda v: (v >> 2)*4 | ((v >> 2) >> 4)
    return [list(map(expand, rom[off+i:off+i+3])) for i in range(0, 768, 3)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--inputs', type=Path, required=True)
    ap.add_argument('--prototype', type=Path, required=True)
    ap.add_argument('--check', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    assert not a.out.exists() and a.out.parent.stat().st_uid == os.getuid()
    inventory_raw = (a.inputs/'inventory.json').read_bytes()
    prototype_raw = (a.prototype/'manifest.json').read_bytes()
    assert sha(inventory_raw) == INVENTORY and sha(prototype_raw) == PROTOTYPE
    assert sha(a.check.read_bytes()) == CHECK
    inventory, prototype = json.loads(inventory_raw), json.loads(prototype_raw)
    roms = {n: Path('/orig', n).read_bytes() for n in ROMS}
    assert all(sha(b) == ROMS[n][0] for n, b in roms.items())
    city = json.loads((a.inputs.parent/'map-completion-v1/inventory.json').read_text())['palette']
    palettes = {'rom0': palette(roms['RS201.ROM'], 0),
                'roma3': palette(roms['RS201A.ROM'], 3),
                'city': [city[str(i)] for i in range(256)]}
    sources, canonical = [], {}
    for r in inventory['images']:
        rom = roms[r['rom']]
        off, size = struct.unpack_from('<IH', rom, 18+r['member']*16)
        end = min([q['file_offset'] for q in inventory['images'] if q['rom'] == r['rom'] and q['member'] == r['member'] and q['file_offset'] > r['file_offset']]+[off+size])
        raw = rom[r['file_offset']:end]
        assert sha(raw) == r['raw_sha256']
        w, h, pixels = iv2(raw) if r['encoding'] == 'iv2' else image(raw)[:3]
        assert (w, h, sha(pixels)) == (r['width'], r['height'], r['pixels_sha256'])
        rec = {k: r[k] for k in ['id', 'canonical', 'rom', 'member', 'image', 'file_offset', 'width', 'height', 'encoding', 'raw_sha256', 'pixels_sha256']}
        rec['end'] = end
        sources.append(rec)
        if r['id'] == r['canonical']:
            canonical[r['id']] = (rec, pixels)
    assert len(sources) == 209 and len(canonical) == 197
    a.out.mkdir()
    assets, files = [], {}
    for r in prototype['images']:
        ident = r['id']
        rec, pixels = canonical[ident]
        w, h = rec['width'], rec['height']
        picture_path = a.prototype/(ident+'.png')
        assert sha(picture_path.read_bytes()) == r['png_sha256']
        picture = bytearray(rgba(picture_path, (w*4, h*4)))
        assert set(picture[3::4]) == {255}
        reference = palettes['roma3' if ident.startswith('a') else 'city']
        fields = []
        if ident in {f'r{i:02d}-00' for i in range(4, 11)}:
            for x in [1, 127]:
                for y, key in [(22, 'art.maximum'), (101, 'art.minimum')]:
                    box = [x, y, x+17, y+5]
                    values = {pixels[yy*w+xx] for yy in range(y, y+5) for xx in range(x, x+17)}
                    assert values == {14, 129}
                    fields.append({'rect': box, 'key': key, 'background': 129, 'ink': 14})
                    for yy in range(y*4, (y+5)*4):
                        start = (yy*w*4+x*4)*4
                        picture[start:start+17*16] = bytes(reference[129]+[255])*(17*4)
        variants = []
        for name, target in palettes.items():
            modified = picture[:]
            differences = {v: [target[v][c]-reference[v][c] for c in range(3)] for v in set(pixels) if target[v] != reference[v]}
            for i, v in enumerate(pixels):
                if v not in differences:
                    continue
                for dy in range(4):
                    start = (((i//w*4+dy)*w*4)+i%w*4)*4
                    for dx in range(4):
                        for c, delta in enumerate(differences[v]):
                            at = start+dx*4+c
                            modified[at] = min(255, max(0, modified[at]+delta))
            encoded = png(modified, w*4, h*4)
            digest = sha(encoded)
            filename = digest+'.png'
            if digest not in files:
                (a.out/filename).write_bytes(encoded)
                files[digest] = len(encoded)
            variants.append({'palette': name, 'file': filename, 'sha256': digest})
        assets.append({'id': ident, 'variants': variants, 'fields': fields})
    result = {'schema': 1, 'stage': 'READY', 'issue': 32,
              'prototype_sha256': PROTOTYPE, 'prototype_check_sha256': CHECK,
              'source_inventory_sha256': INVENTORY, 'sources': sources,
              'palettes': palettes, 'images': assets,
              'excluded_existing_ui_noto': prototype['excluded_existing_ui_noto'],
              'unique_files': len(files), 'tool_sha256': sha(Path(__file__).read_bytes()),
              'rights': 'local-only original-derived; no Git or Release',
              'colour_method': 'HD display approximation: RGB + target index colour - reference index colour; clamp'}
    assert len(assets) == 179
    (a.out/'manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print('READY', len(assets), 'sources;', len(files), 'PNG;', sha((a.out/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
