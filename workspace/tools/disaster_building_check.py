#!/usr/bin/env python3
"""#56: independent frozen atlas, full city pixels and effective negative controls."""
import argparse
import copy
import functools
import json
from pathlib import Path
import struct
import subprocess
import zipfile

from hd_file_dialogs_check import rgba
from hd_source_audit import cell, sha, scene
from chart_locale_check import localized_reference, paste, original_pixels, load

ROOT = Path('/workspace/prototypes/hd-style')
PROTOTYPE_SHA = '46aa12d3616bfa98fee4aa794f9553d6ce8f4dfd93ad70ad5495f2ba6f28f0be'


@functools.lru_cache(maxsize=1)
def references():
    proto = ROOT/'disaster-buildings-prototype-v1'
    raw = (proto/'manifest.json').read_bytes()
    assert sha(raw) == PROTOTYPE_SHA
    manifest = json.loads(raw)
    rom = Path('/orig/RS201.ROM').read_bytes()
    assert sha(rom) == manifest['rom_sha256']
    proof = json.loads((ROOT/'disaster-buildings-v1/sources.json').read_text())
    assert sha((ROOT/'disaster-buildings-v1/sources.json').read_bytes()) == manifest['source_proof_sha256']
    tiles, pal = {}, {}
    for member in [34, 35, 36]:
        asset = manifest['atlases'][str(member)]
        generated = ROOT/f'disaster-buildings-v1/{member}-generated.png'
        assert sha(generated.read_bytes()) == asset['generated_sha256']
        expected = subprocess.run(['convert', str(generated), '-filter', 'Lanczos', '-resize', '144x144!',
                                   '-depth', '8', 'rgba:-'], check=True, stdout=subprocess.PIPE).stdout
        image = proto/asset['file']
        assert sha(image.read_bytes()) == asset['sha256']
        assert rgba(image, (144, 144)) == expected and sha(expected) == asset['rgba_sha256']
        off, size = struct.unpack_from('<IH', rom, 18+member*16)
        assert struct.unpack_from('<H', rom, off)[0] == 96 and size == 8354
        for row in range(4):
            for col in range(4):
                index = 4+row*24+col
                a, b = struct.unpack_from('<HH', rom, off+2+index*2)
                assert b-a == 85 and rom[off+a:off+a+4] == b'\x09\x00\x09\x00'
                source = rom[off+a+4:off+b]
                record = next(r for r in manifest['sources'] if r['member']==member and r['image']==index)
                assert sha(source) == record['source_sha256'] and sorted(set(source)) == record['used_colors']
                assert source not in tiles
                fragment = b''.join(expected[((row*36+y)*144+col*36)*4:((row*36+y)*144+col*36+36)*4] for y in range(36))
                tiles[source] = (f'{member}/{index}', fragment)
        pal.update(next(b['used_palette'] for b in proof['buildings'] if b['member']==member))
    with zipfile.ZipFile(proof['receipt']) as z:
        state = json.loads(z.read('status.json'))
        frame = z.read('frame-index.bin')
    assert sha((proto/'base.png').read_bytes()) == '603fee2fb7ac13e1983a20a0143466cecf09275a5ca9c40a87d482151776bfd5'
    base = bytearray(rgba(proto/'base.png', (1280, 800)))
    for row in range(15):
        for col in range(29):
            match = tiles.get(cell(frame, 5+col*9, 34+row*9))
            if match:
                for y in range(36):
                    at = ((136+row*36+y)*1280+20+col*36)*4
                    base[at:at+144] = match[1][y*144:(y+1)*144]
    assert rgba(proto/'city-candidate.png', (1280, 800)) == base
    return tiles, pal, state, frame, bytes(base)


def audit(s, frame, shown):
    tiles, pal, _, native, candidate = references()
    assert sha(frame) == s['frame_index_sha256'] and sha(shown) == s['presentation_sha256']
    assert frame == native and scene(s, frame)
    assert not s['help_panel'] and not s['language_panel']
    assert s['map_origin'] == {'X': 6, 'Y': 22, 'Valid': True}
    count, images = 0, {}
    expected = bytearray(candidate)
    if s['hd_enabled']:
        frozen = localized_reference(s['language'])
        for index in range(6):
            paste(expected, frozen, (28+index*176, 40, 136, 68))
        for rect in [(1132,704,24,28), (1212,704,48,28), (1212,736,48,28)]:
            paste(expected, frozen, rect)
        for row in range(15):
            for col in range(29):
                source = cell(frame, 5+col*9, 34+row*9)
                if source not in tiles:
                    continue
                assert all(s['palette'][i] == pal[str(i)] for i in set(source))
                count += 1
                key = tiles[source][0]
                images[key] = images.get(key, 0)+1
        stats = s['hd']['city_buildings']
        assert stats['matched'] == stats['painted'] == count and stats['fallback'] == 0 and count > 0
        assert stats['images'] == images
    else:
        expected = original_pixels(frame, s['palette'])
        assert s['hd']['city_buildings']['painted'] == 0
    assert shown == expected, ('complete city pixels', next((i for i,(a,b) in enumerate(zip(shown, expected)) if a!=b), None))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    assert not args.out.exists()
    tiles, _, _, _, _ = references()
    report = {'issue': 56, 'tiles': len(tiles), 'prototype_complete': True, 'receipts': [], 'controls': []}
    if args.run:
        for path in sorted((args.run/'gui').glob('city-*-capture.zip')):
            s, frame, shown = load(path)
            audit(s, frame, shown)
            report['receipts'].append({'file': path.name, 'sha256': sha(path.read_bytes()),
                                       'language': s['language'], 'hd_enabled': s['hd_enabled'], 'complete_pixels': True})
            if s['hd_enabled'] and s['language']=='zh-Hant':
                baseline = s, frame, shown
        assert len(report['receipts']) == 6
        for fault in ['positive', 'tile', 'outside', 'source', 'reported-count', 'wrong-language']:
            s, frame, shown = copy.deepcopy(baseline[0]), bytearray(baseline[1]), bytearray(baseline[2])
            if fault == 'tile':
                shown[(180*1280+760)*4] ^= 1
            elif fault == 'outside':
                shown[0] ^= 1
            elif fault == 'source':
                frame[43*320+185] ^= 128
            elif fault == 'reported-count':
                s['hd']['city_buildings']['painted'] += 1
            elif fault == 'wrong-language':
                s['language'] = 'en'
            s['frame_index_sha256'], s['presentation_sha256'] = sha(frame), sha(shown)
            rejected = False
            try:
                audit(s, bytes(frame), bytes(shown))
            except AssertionError:
                rejected = True
            assert rejected is (fault != 'positive'), fault
            report['controls'].append({'fault': fault, 'rejected': rejected, 'affected_hashes_recomputed': True})
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print('PASS: 48 frozen atlas tiles, full prototype;', len(report['receipts']), 'GUI frames;', len(report['controls']), 'controls')


if __name__ == '__main__':
    main()
