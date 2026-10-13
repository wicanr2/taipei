#!/usr/bin/env python3
"""#56: export reviewed original/five-language DISA1 GUI screenshots."""
import argparse
import json
import os
from pathlib import Path
import zipfile

from disaster_building_check import audit, load
from hd_source_audit import sha


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', type=Path, required=True)
    ap.add_argument('--manifest', type=Path, required=True)
    ap.add_argument('--source-commit', required=True)
    args = ap.parse_args()
    assert len(args.source_commit)==40 and all(c in '0123456789abcdef' for c in args.source_commit)
    manifest = json.loads(args.manifest.read_text())
    proof = json.loads((args.run/'verification.json').read_text())
    pixels = json.loads((args.run/'pixel-verification.json').read_text())
    assert proof['issue']==pixels['issue']==56 and len(proof['screenshots'])==6
    assert proof['normal_gui'] and proof['native_exit_tested'] and proof['original_save_read'] and proof['save_unchanged_after_read']
    assert not (proof['checkpoint'] or proof['state_injection'] or proof['long_state_sampling'])
    assert len(pixels['receipts'])==6 and all(r['complete_pixels'] for r in pixels['receipts'])
    assert len(pixels['controls'])==6 and all(r['rejected']==(r['fault']!='positive') for r in pixels['controls'])
    assert sha(Path('/workspace/runs/taipei-preview-buildings-r1').read_bytes())==proof['binary_sha256']
    out = args.manifest.parent
    assert out.stat().st_uid==os.getuid() and args.manifest.stat().st_uid==os.getuid()
    old = next(r for r in manifest['screenshots'] if r['file']=='city-disaster-zh-Hant.png')
    assert sha((out/old['file']).read_bytes())==old['png_sha256']
    records, files = [], {}
    for shot in proof['screenshots']:
        src = args.run/'gui'/shot['file']
        capture = src.with_name(src.stem+'-capture.zip')
        assert sha(capture.read_bytes())==shot['capture_sha256']
        state, frame, shown = load(capture)
        audit(state, frame, shown)
        with zipfile.ZipFile(capture) as z:
            raw = z.read('presentation.png')
        assert raw==src.read_bytes() and sha(raw)==shot['png_sha256']
        name = 'city-disaster-'+('original' if not state['hd_enabled'] else state['language'])+'.png'
        if name!=old['file']:
            assert not (out/name).exists()
        records.append({'file':name, 'scene':'disaster-city', 'language':state['language'] if state['hd_enabled'] else 'zh-Hant',
                        'mode':'hd-b' if state['hd_enabled'] else 'original', 'size':[1280,800],
                        'png_sha256':sha(raw), 'capture_sha256':shot['capture_sha256'],
                        'frame_index_sha256':shot['frame_index_sha256'], 'source_commit':args.source_commit,
                        'steps':shot['steps'], 'ticks':shot['ticks'], 'map_origin':shot['map_origin'],
                        'batch':'disaster-buildings', 'local_capture':'workspace/runs/'+args.run.name+'/gui/'+capture.name})
        files[name] = raw
    manifest['screenshots'] = [r for r in manifest['screenshots'] if r['file']!=old['file']]+records
    manifest['buildings_capture'] = {
        'issue':'https://github.com/wicanr2/taipei/issues/56', 'source_commit':args.source_commit,
        'captured_at':proof['captured_at'], 'binary_sha256':proof['binary_sha256'], 'catalog_sha256':proof['catalog_sha256'],
        'local_receipt':'workspace/runs/'+args.run.name+'/verification.json',
        'local_receipt_sha256':sha((args.run/'verification.json').read_bytes()),
        'pixel_verification_sha256':sha((args.run/'pixel-verification.json').read_bytes()),
        'scenario':proof['scenario'], 'painted_cells':proof['painted_cells'], 'normal_gui':True,
        'original_save_read':True, 'native_exit_tested':True, 'cold_reload_tested':False,
        'long_state_sampling':False, 'replaced_screenshot':old,
        'tools_sha256':{p.name:sha(p.read_bytes()) for p in [Path(__file__),
            Path('/workspace/tools/disaster_building_gui.py'), Path('/workspace/tools/disaster_building_gui.sh'),
            Path('/workspace/tools/disaster_building_check.py')]},
        'limits':'三種已見靜態來源及正常遊玩抽驗；原版統計、其餘建物／相位、真機與正式封包另案。',
    }
    for name, raw in files.items():
        (out/name).write_bytes(raw)
    assert len(manifest['screenshots'])==len({r['file'] for r in manifest['screenshots']})==34
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    print('Exported six reviewed DISA1 original/five-language PNGs; 34 README images total')


if __name__=='__main__':
    main()
