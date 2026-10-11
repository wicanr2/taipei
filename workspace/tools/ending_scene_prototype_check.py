"""#47：獨立核對完整來源、固定 B 畫面、Noto 墨跡與全部合成像素。"""
import argparse
import json
import os
import struct
import zipfile
from pathlib import Path

from full_asset_catalog import image, sha
from hd_file_dialogs_check import rgba

FIXED = {
    'art-scaled.png': 'ac77b0cc8fc8f085d6c09d6e3c9ea3107afbe57494d3ef6417c0cc8ce9250c2c',
    'title-ink.png': 'd243859975cedfb527e393cfc1b18cd64a8f7a99fe11d8769f7fbb83dbeeb1ba',
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--original', type=Path, required=True)
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--materials', type=Path, required=True)
    ap.add_argument('--prototype', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    assert not args.out.exists() and args.out.parent.stat().st_uid == os.getuid()
    source_raw = (args.source/'source-check.json').read_bytes()
    source = json.loads(source_raw)
    meta_raw = (args.prototype/'manifest.json').read_bytes()
    meta = json.loads(meta_raw)
    assert meta['stage'] == 'DRAFT' and meta['prototype'] and meta['issue'] == 47
    assert meta['source_check_sha256'] == sha(source_raw)
    assert source['source_size'] == [320, 200] and len(source['sources']) == 2
    assert meta['font_sha256'] == sha((args.materials/'fonts/NotoSansCJKtc-Regular.otf').read_bytes()) == 'dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4'
    assert sha((args.materials/'fonts/LICENSE').read_bytes()) == '6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2'
    assert meta['art_sha256'] == sha((args.materials/'ending-scene-b-candidate-v1-generated.png').read_bytes()) == '2dbdb09f57fe5324542117b2c00bc2b0d4ded4b24781594920f05663f6ad3284'
    pixels = (args.source/'source-index.bin').read_bytes()
    assert sha(pixels) == meta['source_sha256'] == source['source_sha256']
    for entry in source['sources']:
        raw = (args.original/entry['rom']).read_bytes()
        assert sha(raw) == entry['rom_sha256']
        offset, size = struct.unpack_from('<IH', raw, 18+entry['member']*16)
        assert (offset, size) == (entry['file_offset'], entry['length'])
        decoded = image(raw[offset:offset+size])
        assert decoded is not None and decoded[:2] == (320, 200) and decoded[2] == pixels
    for entry in source['receipts']:
        path = Path(entry['receipt'])
        assert sha(path.read_bytes()) == entry['receipt_sha256']
        with zipfile.ZipFile(path) as z:
            status = json.loads(z.read('status.json'))
            assert z.read('frame-index.bin') == pixels
        assert all(status['palette'][int(c)] == rgb for c, rgb in source['used_palette'].items())
    for name, expected in FIXED.items():
        assert sha((args.prototype/name).read_bytes()) == expected
    art = rgba(args.prototype/'art-scaled.png', (1280, 800))
    mask = rgba(args.prototype/'title-ink.png', (1280, 800))
    actual = rgba(args.prototype/'presentation.png', (1280, 800))
    assert set(art[3::4]) == set(actual[3::4]) == {255}
    points = [(i % 1280, i // 1280) for i, a in enumerate(mask[3::4]) if a]
    ink = [min(x for x, y in points), min(y for x, y in points),
           max(x for x, y in points)+1, max(y for x, y in points)+1]
    assert ink == [537, 16, 742, 65]
    assert meta['title'] == source['title']['text'] == '您的政績' and meta['font_size'] == 52
    assert set(meta['glyph_indices']) == set('您的政績') and all(meta['glyph_indices'].values())
    assert all(512 <= x < 768 and 12 <= y < 68 for x, y in points)
    assert all(any(left <= x < left+52 for x, y in points) for left in [536, 588, 640, 692])
    expected = bytearray(art)
    for x, y in points:
        at = (y*1280+x)*4
        alpha = mask[at+3]*257
        for c, value in enumerate([0, 0, 203]):
            expected[at+c] = (art[at+c]*257*(65535-alpha)+value*257*alpha)//65535 >> 8
    assert bytes(expected) == actual
    assert sha(actual) == meta['presentation_rgba_sha256']
    comparison = rgba(args.prototype/'comparison.png', (2560, 800))
    palette = source['used_palette']
    original = b''.join(bytes(palette[str(c)]+[255])*4 for c in pixels)
    original = b''.join(original[y*5120:(y+1)*5120]*4 for y in range(200))
    for y in range(800):
        assert comparison[y*10240:y*10240+5120] == original[y*5120:(y+1)*5120]
        assert comparison[y*10240+5120:(y+1)*10240] == actual[y*5120:(y+1)*5120]
    result = {'issue': 47, 'stage': 'DRAFT', 'prototype_only': True,
              'source_aliases': 2, 'normal_receipts': len(source['receipts']),
              'complete_rgba_pixels': 1280*800, 'ink_pixels': len(points),
              'ink_rect': ink, 'title_characters': 4, 'outside_ink_equal': True,
              'comparison_complete_equal': True, 'manifest_sha256': sha(meta_raw),
              'presentation_rgba_sha256': sha(actual),
              'scope': '獨立來源與合成核對，不代替正式呈現、正常 GUI 或原版狀態重播'}
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
