#!/usr/bin/env python3
"""039：重讀ROM與封存PNG，核對正常GUI可見插畫的完整四倍像素。"""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import struct
import subprocess
import zipfile

from full_asset_catalog import ROMS, image, sha
from illustration_sources import iv2

MANIFEST = '545b4f94b6454debc0de5110bab646d5e68ae19dfa126f700361cd12d9d276af'


def rgba(raw):
    return subprocess.run(['convert', 'png:-', '-depth', '8', 'rgba:-'], input=raw,
                          stdout=subprocess.PIPE, check=True).stdout


def rect(value):
    return (value['Min']['X'], value['Min']['Y'], value['Max']['X'], value['Max']['Y'])


def mask_rect(mask, box):
    left, top, right, bottom = box
    left, top, right, bottom = max(0, left), max(0, top), min(320, right), min(200, bottom)
    if left >= right or top >= bottom:
        return
    for y in range(top, bottom):
        mask[y*320+left:y*320+right] = bytes([1])*(right-left)


def compare(actual, expected, label):
    assert actual == expected, label


def verify_blocks(actual, expected_blocks, label):
    counts = Counter()
    for at, (identifier, expected) in expected_blocks.items():
        got = b''.join(actual[((at//320*4+dy)*1280+at%320*4)*4:((at//320*4+dy)*1280+at%320*4)*4+16] for dy in range(4))
        compare(got, expected, (label, identifier, at))
        counts[identifier] += 1
    return counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', type=Path, required=True)
    ap.add_argument('--normal-run', type=Path, help='同一候選程式的完整正常存退讀流程；未指定時與插畫來源相同')
    ap.add_argument('--assets', type=Path, required=True)
    ap.add_argument('--binary', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    assert not a.out.exists() and a.out.parent.stat().st_uid == os.getuid()
    manifest_raw = (a.assets/'manifest.json').read_bytes()
    assert sha(manifest_raw) == MANIFEST
    manifest = json.loads(manifest_raw)
    normal_run = a.normal_run
    verification_raw = None
    if normal_run is not None:
        verification_raw = (normal_run/'verification.json').read_bytes()
        verification = json.loads(verification_raw)
        assert verification['normal_gui'] and not verification['checkpoint'] and verification['native_exit_tested']
        assert verification['original_save_written'] and verification['original_save_read'] and verification['save_unchanged_after_read']
        assert verification['binary_sha256'] == sha(a.binary.read_bytes())
    gallery = json.loads((a.run/'illustration-gallery.json').read_text())
    assert gallery['normal_gui'] and not gallery['checkpoint'] and gallery['help_input_isolation']
    roms = {n: Path('/orig', n).read_bytes() for n in ROMS}
    assert all(sha(b) == ROMS[n][0] for n, b in roms.items())
    sources = {}
    for r in manifest['sources']:
        raw = roms[r['rom']][r['file_offset']:r['end']]
        assert sha(raw) == r['raw_sha256']
        w, h, pixels = iv2(raw) if r['encoding'] == 'iv2' else image(raw)[:3]
        assert (w, h, sha(pixels)) == (r['width'], r['height'], r['pixels_sha256'])
        sources[r['canonical']] = (w, h, pixels)
    assets = {r['id']: r for r in manifest['images']}
    cache = {}
    labels = ['opening-startup.title', 'opening-art.department_store', 'opening-art.protest',
              'opening-intro.traffic', 'opening-intro.medals',
              *['illustration-bank-'+lang for lang in ['zh-Hant', 'zh-Hans', 'ja', 'ko', 'en']]]
    results = []
    for label in labels:
        path = a.run/'gui'/(label+'-capture.zip')
        raw = path.read_bytes()
        with zipfile.ZipFile(path) as z:
            status = json.loads(z.read('status.json'))
            native = z.read('frame-index.bin')
            actual = rgba(z.read('presentation.png'))
        assert len(native) == 64000 and sha(native) == status['frame_index_sha256']
        assert len(actual) == 1280*800*4 and status['hd_enabled']
        assert status['original_sha256'] == '798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3'
        # Exclude only known text rectangles. Their native source/ink is tested
        # separately by 033; no image-wide text exemption is used.
        text = bytearray(64000)
        for t in status.get('source_text') or []:
            mask_rect(text, (t['X'], t['Y'], 320, t['Y']+14))
        for t in status.get('source_images') or []:
            identifier = t['id']
            boxes = []
            if identifier == 'small-title':
                boxes = [(0, 0, 61, 18)]
            elif identifier == 'romA-6-0':
                boxes = [(0, 0, 242, 74)]
            elif identifier.startswith('romA-10-'):
                boxes = [(108, 2, 149, 35)]
            elif identifier in ['romA-15-0', 'romA-16-0']:
                boxes = [(47, 2, 161, 23), (6, 22, 34, 37), (178, 22, 206, 37)]
            elif identifier == 'romA-17-0':
                boxes = [(45, 0, 174, 25)]
            for l, top, right, bottom in boxes:
                mask_rect(text, (l+t['x'], top+t['y'], right+t['x'], bottom+t['y']))
        covered = bytearray(64000)
        expected_blocks = {}
        accepted = set(status['hd']['illustrations']['images'] or [])
        for d in reversed(status['source_illustrations']):
            l, top, right, bottom = rect(d['Clip'])
            source = sources.get(d['id'])
            if source is None:
                mask_rect(covered, (l, top, right, bottom))
                continue
            w, h, pixels = source
            l, top, right, bottom = max(l, d['X']), max(top, d['Y']), min(right, d['X']+w), min(bottom, d['Y']+h)
            owned, visible, used, matched = [], [], set(), True
            for y in range(top, bottom):
                for x in range(l, right):
                    index = (y-d['Y'])*w+x-d['X']
                    v = pixels[index]
                    if d['Transparent'] and v == d['Key']:
                        continue
                    used.add(v)
                    at = y*320+x
                    owned.append(at)
                    if covered[at] or text[at]:
                        continue
                    if native[at] != v:
                        matched = False
                    visible.append((at, index, v))
            colours = {v for _, _, v in visible}
            art = None
            if matched and len(colours) >= 2 and d['id'] in accepted:
                for variant in assets[d['id']]['variants']:
                    palette = manifest['palettes'][variant['palette']]
                    if not all(palette[v] == status['palette'][v] for v in used):
                        continue
                    name = variant['file']
                    if name not in cache:
                        png = (a.assets/name).read_bytes()
                        assert sha(png) == variant['sha256']
                        cache[name] = rgba(png)
                    art = cache[name]
                    break
                assert art is not None, (label, d['id'], 'no known palette')
                for at, index, _ in visible:
                    block = b''.join(art[((index//w*4+dy)*w*4+index%w*4)*4:((index//w*4+dy)*w*4+index%w*4)*4+16] for dy in range(4))
                    expected_blocks[at] = (d['id'], block)
            title = d['id'] in ['a06-00', 'a38-00']
            for at in owned:
                if not (title and text[at]):
                    covered[at] = 1
        assert len(expected_blocks) >= 100, (label, len(expected_blocks))
        counts = verify_blocks(actual, expected_blocks, label)
        # Change a checked subpixel while keeping the same source and metadata.
        at = next(iter(expected_blocks))
        modified = bytearray(actual)
        modified[((at//320*4)*1280+at%320*4)*4] ^= 1
        try:
            verify_blocks(modified, expected_blocks, label)
        except AssertionError:
            pass
        else:
            raise AssertionError('pixel negative was accepted')
        results.append({'capture': path.name, 'sha256': sha(raw), 'blocks': len(expected_blocks),
                        'visible_sources': dict(counts), 'negative_pixel_rejected': True})
        print('PASS', label, len(expected_blocks), dict(counts), flush=True)
    result = {'issue': 32, 'binary_sha256': sha(a.binary.read_bytes()), 'manifest_sha256': MANIFEST,
              'normal_gui': True, 'checkpoint': False, 'normal_verification_sha256': sha(verification_raw) if verification_raw else None,
              'illustration_source_run': a.run.name, 'normal_complete_run': normal_run.name if normal_run else None,
              'normal_path_complete': normal_run is not None,
              'results': results, 'tool_sha256': sha(Path(__file__).read_bytes()),
              'scope': '十份正常冷啟GUI前段照片中明列可見插畫的完整四倍格；完整存退讀另列同程式流程。文字沿033，不外推所有出現分支'}
    a.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print('PASS', sha(a.out.read_bytes()))


if __name__ == '__main__':
    main()
