#!/usr/bin/env python3
"""#54: append selected actual chart screenshots to the private README catalog."""
import argparse
import json
import os
from pathlib import Path
import zipfile

from chart_locale_check import audit, load, sha, original_pixels, FROZEN

ap = argparse.ArgumentParser()
ap.add_argument('--run', type=Path, required=True)
ap.add_argument('--catalog', type=Path, required=True)
ap.add_argument('--source-commit', required=True)
args = ap.parse_args()
assert len(args.source_commit) == 40 and all(c in '0123456789abcdef' for c in args.source_commit)
assert args.catalog.is_file() and args.catalog.stat().st_uid == os.getuid()
out = args.catalog.parent
assert out.stat().st_uid == os.getuid()
manifest = json.loads(args.catalog.read_text())
verification = json.loads((args.run/'verification.json').read_text())
pixels = json.loads((args.run/'pixel-verification.json').read_text())
assert verification['issue'] == pixels['issue'] == 54 and verification['native_exit_tested']
assert verification['original_save_read'] and verification['save_unchanged_after_read']
assert not (verification['checkpoint'] or verification['state_injection'] or verification['long_state_sampling'])
assert len(verification['charts']) == 6
assert verification['binary_sha256'] == manifest['binary_sha256']
assert verification['catalog_sha256'] == manifest['catalog_sha256']
names = ['chart-power-original.png'] + ['chart-power-' + lang + '.png' for lang in FROZEN]
names += ['chart-' + name + '-zh-Hant.png' for name in ['traffic', 'population', 'crime', 'land-value', 'pollution']]
assert len(names) == 11 and all(not (out/name).exists() for name in names)
records, images = [], {}
power_original = None
for name in names:
    path = args.run/'gui'/(name[:-4]+'-capture.zip')
    s, frame, shown = load(path)
    audit(s, frame, shown)
    data = (args.run/'gui'/name).read_bytes()
    with zipfile.ZipFile(path) as z:
        assert data == z.read('presentation.png')
    rgb_sha = sha(original_pixels(frame, s['palette']))
    if name.startswith('chart-power-'):
        if power_original is None:
            power_original = s['frame_index_sha256'], rgb_sha
        assert power_original == (s['frame_index_sha256'], rgb_sha)
    records.append({'file': name, 'scene': name.removesuffix('.png'),
                    'language': s['language'] if s['hd_enabled'] else 'zh-Hant',
                    'selected_locale': s['language'], 'mode': 'hd-b' if s['hd_enabled'] else 'original',
                    'size': [1280, 800], 'png_sha256': sha(data), 'capture_sha256': sha(path.read_bytes()),
                    'frame_index_sha256': s['frame_index_sha256'], 'original_rgba_4x_sha256': rgb_sha,
                    'source_commit': args.source_commit, 'steps': s['steps'], 'ticks': s['ticks'],
                    'map_origin': s['map_origin'], 'batch': 'chart-locales'})
    images[name] = data
manifest['screenshots'].extend(records)
manifest['chart_capture'] = {
    'issue': 'https://github.com/wicanr2/taipei/issues/54', 'source_commit': args.source_commit,
    'captured_at': verification['captured_at'], 'scenario': 'DISA1.DSA；正常災難台北選單進入，原版 0 鍵暫停。',
    'local_receipt': 'workspace/runs/' + args.run.name + '/verification.json',
    'local_receipt_sha256': sha((args.run/'verification.json').read_bytes()),
    'pixel_verification_sha256': sha((args.run/'pixel-verification.json').read_bytes()),
    'frozen_localization_png_sha256': FROZEN,
    'normal_gui': True, 'original_save_read': True, 'native_exit_tested': True,
    'cold_reload_tested': False, 'long_state_sampling': False,
    'tools_sha256': {name: sha((Path('/workspace/tools')/name).read_bytes()) for name in
                     ['chart_locale_gui.sh', 'chart_locale_gui.py', 'chart_locale_check.py', 'export_chart_screenshots.py']},
    'limits': '六圖表及電力圖五語系的呈現比較；存檔於同次執行讀回。沒有完整 RAM／RNG 對拍、全新 EXE 冷讀或平台真機驗收。',
    'reproduce': 'TAIPEI_CHART_LOCALE_RUN=<新目錄> bash workspace/tools/chart_locale_gui.sh；在同一 Docker image 執行 chart_locale_check.py，再以 export_chart_screenshots.py 收錄選定圖。',
}
assert len(manifest['screenshots']) == len({r['file'] for r in manifest['screenshots']})
for name, data in images.items():
    (out/name).write_bytes(data)
args.catalog.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
print('Exported 11 verified chart PNGs;', len(manifest['screenshots']), 'README images total')
