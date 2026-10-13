#!/usr/bin/env python3
"""#55: review existing normal gameplay evidence and export its city overview.

Run inside the pinned GUI Docker image, with the project mounted at /project
and its workspace at /workspace. This does not start or modify the game.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import zipfile


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_json(path):
    return json.loads(path.read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--reviewed-commit', required=True)
    args = parser.parse_args()
    assert len(args.reviewed_commit) == 40
    assert all(c in '0123456789abcdef' for c in args.reviewed_commit)
    manifest = read_json(args.manifest)
    run = args.run
    evidence = read_json(run / 'verification.json')
    pixels = read_json(run / 'pixel-verification.json')
    chart = manifest['chart_capture']
    assert sha((run / 'verification.json').read_bytes()) == chart['local_receipt_sha256']
    assert sha((run / 'pixel-verification.json').read_bytes()) == chart['pixel_verification_sha256']
    assert evidence['issue'] == pixels['issue'] == 54
    assert evidence['normal_gui'] and evidence['native_exit_tested']
    assert evidence['original_save_read'] and evidence['save_unchanged_after_read']
    assert not any(evidence[k] for k in ['checkpoint', 'state_injection', 'long_state_sampling'])
    assert [c['selection'] for c in evidence['charts']] == list(range(6))
    assert len({c['data_sha256'] for c in evidence['charts']}) == 6
    assert all(c['f12_roundtrip'] and c['restored_complete_city'] for c in evidence['charts'])
    assert len(pixels['receipts']) == 34
    assert all(r['complete_pixels'] for r in pixels['receipts'])
    assert len(pixels['negative_controls']) == 14

    provenance = read_json(Path('/workspace/runs/localization-final-provenance.json'))
    for name, expected in provenance['source_sha256'].items():
        assert sha((Path('/project') / name).read_bytes()) == expected, name
    for name, record in provenance['artifacts'].items():
        assert sha((Path('/workspace/runs') / name).read_bytes()) == record['sha256'], name
    assert evidence['binary_sha256'] == manifest['binary_sha256'] == provenance['artifacts']['taipei-preview']['sha256']
    assert evidence['catalog_sha256'] == sha(Path('/workspace/app/locales/ui.tsv').read_bytes())
    saved = run / 'saves/CHARTS.SAV'
    assert saved.stat().st_size == 93567 and sha(saved.read_bytes()) == evidence['save_sha256']

    for shot in evidence['screenshots']:
        capture = run / 'gui' / (shot['file'][:-4] + '-capture.zip')
        assert sha(capture.read_bytes()) == shot['capture_sha256'], capture
        with zipfile.ZipFile(capture) as z:
            status = json.loads(z.read('status.json'))
            assert sha(z.read('frame-index.bin')) == shot['frame_index_sha256'] == status['frame_index_sha256']
            png = z.read('presentation.png')
            assert png == (run / 'gui' / shot['file']).read_bytes()
            assert sha(png) == shot['png_sha256']
            assert png[:8] == b'\x89PNG\r\n\x1a\n' and struct.unpack('>II', png[16:24]) == (1280, 800)
    for item in pixels['receipts']:
        assert sha((run / 'gui' / item['receipt']).read_bytes()) == item['receipt_sha256']

    shot = next(s for s in evidence['screenshots'] if s['file'] == 'city-paused.png')
    capture = run / 'gui/city-paused-capture.zip'
    with zipfile.ZipFile(capture) as z:
        status = json.loads(z.read('status.json'))
        png = z.read('presentation.png')
    assert status['language'] == 'zh-Hant' and status['hd_enabled']
    assert not status['help_panel'] and not status['language_panel'] and not status['hd']['chart_window']
    assert any(f.get('Op') == 'read' and f.get('Name', '').lower() == 'disa1.dsa' for f in status['file_ops'])
    assert not (status.get('missing') or status.get('unimplemented'))
    target = args.manifest.parent / 'city-disaster-zh-Hant.png'
    record = {
        'file': target.name, 'scene': 'disaster-city', 'language': 'zh-Hant',
        'mode': 'hd-b', 'size': [1280, 800], 'png_sha256': sha(png),
        'capture_sha256': shot['capture_sha256'], 'frame_index_sha256': shot['frame_index_sha256'],
        'source_commit': chart['source_commit'], 'steps': shot['steps'], 'ticks': shot['ticks'],
        'map_origin': shot['map_origin'], 'batch': 'gameplay-overview',
        'local_capture': 'workspace/runs/' + run.name + '/gui/city-paused-capture.zip',
    }
    prior = [r for r in manifest['screenshots'] if r['file'] == target.name]
    assert not prior or prior == [record]
    for path in [args.manifest, args.manifest.parent]:
        assert path.stat().st_uid == os.getuid() and path.stat().st_gid == os.getgid(), path
    if target.exists():
        assert target.stat().st_uid == os.getuid() and target.stat().st_gid == os.getgid()
        assert target.read_bytes() == png
    else:
        target.write_bytes(png)
    if not prior:
        manifest['screenshots'].append(record)
    manifest['play_acceptance'] = {
        'issue': 'https://github.com/wicanr2/taipei/issues/55',
        'accepted_scope': 'F4 六圖表呈現與已驗正常玩家路徑，029 CONFORMED。',
        'basis': '使用者 2026-10-13 指定以正常遊玩抽驗驗收。',
        'reviewed_commit': args.reviewed_commit,
        'local_receipt': chart['local_receipt'], 'local_receipt_sha256': chart['local_receipt_sha256'],
        'export_tool_sha256': sha(Path(__file__).read_bytes()),
        'normal_gui': True, 'original_save_read': True, 'native_exit_tested': True,
        'cold_reload_tested': evidence['cold_reload_tested'],
        'long_state_sampling': False,
        'limits': '依正常遊玩抽驗完成，不宣稱完整機器狀態或亂數對拍、全部 HD、平台真機或正式封包完成。',
    }
    for item in manifest['screenshots']:
        path = args.manifest.parent / item['file']
        raw = path.read_bytes()
        assert sha(raw) == item['png_sha256']
        assert struct.unpack('>II', raw[16:24]) == (1280, 800)
        assert path.stat().st_uid == os.getuid() and path.stat().st_gid == os.getgid()
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print('PASS: six normal chart paths; current product and 35 captures verified; '
          f'{len(manifest["screenshots"])} README PNGs, including disaster city')


if __name__ == '__main__':
    main()
