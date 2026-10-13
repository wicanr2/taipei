#!/usr/bin/env python3
"""#57: export six reviewed facility screenshots without replacing older evidence."""
import argparse
import json
import os
from pathlib import Path
import zipfile

from civic_facility_check import audit, reference, load
from hd_source_audit import sha


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source-commit',required=True)
    args=ap.parse_args()
    assert len(args.source_commit)==40 and all(c in '0123456789abcdef' for c in args.source_commit)
    root=Path('/workspace/runs/gui-civic-r1')
    out=Path('/repo/workspace/screenshots')
    manifest_path=out/'manifest.json'
    assert out.stat().st_uid==manifest_path.stat().st_uid==os.getuid()
    manifest=json.loads(manifest_path.read_text())
    proof=json.loads((root/'verification.json').read_text())
    pixels=json.loads((root/'pixel-verification.json').read_text())
    assert proof['issue']==pixels['issue']==57 and len(proof['screenshots'])==len(pixels['receipts'])==6
    assert proof['normal_gui'] and proof['native_exit_tested'] and proof['original_save_read'] and proof['save_unchanged_after_read']
    assert not (proof['checkpoint'] or proof['state_injection'] or proof['long_state_sampling'])
    assert all(r['facility_pixels_and_locale_labels'] for r in pixels['receipts'])
    assert len(pixels['controls'])==5 and all(r['rejected']==(r['fault']!='positive') for r in pixels['controls'])
    assert sha(Path('/workspace/runs/taipei-preview-civic-r1').read_bytes())==proof['binary_sha256']
    tiles,palette=reference()
    files={}
    for shot in proof['screenshots']:
        capture=root/'gui'/(Path(shot['file']).stem+'-capture.zip')
        assert sha(capture.read_bytes())==shot['capture_sha256']
        state,frame,shown=load(capture)
        audit(state,frame,shown,tiles,palette)
        with zipfile.ZipFile(capture) as z:raw=z.read('presentation.png')
        assert raw==(root/'gui'/shot['file']).read_bytes() and sha(raw)==shot['png_sha256']
        lang=state['language'] if state['hd_enabled'] else 'zh-Hant'
        name='city-civic-'+(lang if state['hd_enabled'] else 'original')+'.png'
        assert not (out/name).exists()
        manifest['screenshots'].append({'file':name,'scene':'normal-civic-construction','language':lang,
            'mode':'hd-b' if state['hd_enabled'] else 'original','size':[1280,800],'png_sha256':sha(raw),
            'capture_sha256':shot['capture_sha256'],'frame_index_sha256':shot['frame_index_sha256'],
            'source_commit':args.source_commit,'steps':shot['steps'],'ticks':shot['ticks'],
            'map_origin':shot['map_origin'],'batch':'civic-facilities',
            'local_capture':'workspace/runs/gui-civic-r1/gui/'+capture.name})
        files[name]=raw
    manifest['civic_capture']={'issue':'https://github.com/wicanr2/taipei/issues/57','source_commit':args.source_commit,
        'captured_at':proof['captured_at'],'binary_sha256':proof['binary_sha256'],'catalog_sha256':proof['catalog_sha256'],
        'local_receipt':'workspace/runs/gui-civic-r1/verification.json',
        'local_receipt_sha256':sha((root/'verification.json').read_bytes()),
        'pixel_verification_sha256':sha((root/'pixel-verification.json').read_bytes()),
        'scenario':proof['scenario'],'painted_cells':proof['painted_cells'],'normal_gui':True,
        'original_save_read':True,'native_exit_tested':True,'cold_reload_tested':False,'long_state_sampling':False,
        'tools_sha256':{p.name:sha(p.read_bytes()) for p in [Path(__file__),
            Path('/workspace/tools/civic_facility_gui.py'),Path('/workspace/tools/civic_facility_playtest.sh'),
            Path('/workspace/tools/civic_facility_check.py')]},
        'limits':'限兩種正常施工圖、F11/F12、同次存讀檔與退出；其餘相位、真機、正式封包另案。'}
    assert len(manifest['screenshots'])==len({r['file'] for r in manifest['screenshots']})==40
    for name,raw in files.items():(out/name).write_bytes(raw)
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print('Exported six civic original/five-language PNGs; 40 README images total')


if __name__=='__main__':main()
