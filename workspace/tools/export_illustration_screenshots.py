#!/usr/bin/env python3
"""039／#32：只匯出已核對的正常GUI原版與五語系文件PNG。"""
import argparse
import json
import os
from pathlib import Path
import zipfile

from full_asset_catalog import sha


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', type=Path, required=True)
    ap.add_argument('--normal-run', type=Path, help='同一候選程式的完整正常存退讀流程')
    ap.add_argument('--manifest', type=Path, required=True)
    ap.add_argument('--pixels', type=Path, help='獨立像素核對收據；預設插畫來源目錄的illustration-pixel-check.json')
    ap.add_argument('--source-commit', required=True)
    a = ap.parse_args()
    assert len(a.source_commit) == 40 and all(c in '0123456789abcdef' for c in a.source_commit)
    assert a.manifest.stat().st_uid == a.manifest.parent.stat().st_uid == os.getuid()
    normal_run = a.normal_run or a.run
    proof = json.loads((normal_run/'verification.json').read_text())
    pixels_path = a.pixels or a.run/'illustration-pixel-check.json'
    pixels_raw = pixels_path.read_bytes()
    pixels = json.loads(pixels_raw)
    gallery_raw = (a.run/'illustration-gallery.json').read_bytes()
    gallery = json.loads(gallery_raw)
    assert proof['normal_gui'] and proof['native_exit_tested'] and proof['original_save_read'] and not proof['checkpoint']
    assert pixels['binary_sha256'] == proof['binary_sha256'] and len(pixels['results']) == 10
    assert all(r['negative_pixel_rejected'] and r['blocks'] >= 100 for r in pixels['results'])
    assert gallery['normal_gui'] and gallery['help_input_isolation'] and gallery['f11_modal_state_unchanged']
    assert {p['language'] for p in gallery['photos']} == {'zh-Hant', 'zh-Hans', 'ja', 'ko', 'en'}
    manifest = json.loads(a.manifest.read_text())
    assert len(manifest['screenshots']) == 84
    verified = {r['capture']: r['sha256'] for r in pixels['results']}
    labels = ['illustration-bank-original', *['illustration-bank-'+lang for lang in ['zh-Hant', 'zh-Hans', 'ja', 'ko', 'en']],
              'opening-startup.title', 'opening-intro.traffic']
    records, files = [], {}
    for label in labels:
        capture = a.run/'gui'/(label+'-capture.zip')
        raw = capture.read_bytes()
        if label != 'illustration-bank-original':
            assert sha(raw) == verified[capture.name]
        with zipfile.ZipFile(capture) as z:
            s = json.loads(z.read('status.json'))
            png = z.read('presentation.png')
            native = z.read('frame-index.bin')
        assert sha(native) == s['frame_index_sha256'] and len(native) == 64000
        assert (a.run/'gui'/(label+'.png')).read_bytes() == png
        assert not s.get('language_panel') and not s.get('help_panel')
        if label == 'opening-startup.title':
            name, scene = 'illustration-title-zh-Hant.png', 'opening-title'
        elif label == 'opening-intro.traffic':
            name, scene = 'illustration-traffic-zh-Hant.png', 'opening-traffic'
        else:
            name, scene = label+'.png', 'opening-bank'
        assert not (a.manifest.parent/name).exists()
        files[name] = png
        records.append({'file': name, 'scene': scene, 'language': s['language'] if s['hd_enabled'] else 'zh-Hant',
                        'mode': 'hd-b' if s['hd_enabled'] else 'original', 'size': [1280, 800],
                        'png_sha256': sha(png), 'capture_sha256': sha(raw),
                        'frame_index_sha256': s['frame_index_sha256'], 'steps': s['steps'], 'ticks': s['ticks'],
                        'source_commit': a.source_commit, 'batch': 'illustrations',
                        'local_capture': 'workspace/runs/'+a.run.name+'/gui/'+capture.name})
    manifest['screenshots'] += records
    assert len(manifest['screenshots']) == len({r['file'] for r in manifest['screenshots']}) == 92
    manifest['illustrations_capture'] = {
        'issue': 'https://github.com/wicanr2/taipei/issues/32', 'source_commit': a.source_commit,
        'binary_sha256': proof['binary_sha256'], 'catalog_sha256': proof['catalog_sha256'],
        'local_receipt': 'workspace/runs/'+normal_run.name+'/verification.json',
        'illustration_source_run': a.run.name, 'normal_complete_run': normal_run.name,
        'normal_receipt_sha256': sha((normal_run/'verification.json').read_bytes()),
        'pixel_verification_sha256': sha(pixels_raw), 'gallery_sha256': sha(gallery_raw),
        'normal_gui': True, 'native_exit_tested': True, 'original_save_read': True,
        'same_state_across_languages': False, 'long_state_sampling': False,
        'limits': '同銀行背景上原版角色持續運行；不同語言照片不稱同狀態。正常代表抽驗，不外推所有事件／結局分支、真機或封包。',
        'tools_sha256': {p.name: sha(p.read_bytes()) for p in [Path(__file__),
            Path('/workspace/tools/illustration_gallery.py'), Path('/workspace/tools/illustration_gui_check.py')]}}
    for name, png in files.items():
        (a.manifest.parent/name).write_bytes(png)
    a.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    print('Exported 8 real PNGs; 92 README screenshots;', sha(a.manifest.read_bytes()))


if __name__ == '__main__':
    main()
