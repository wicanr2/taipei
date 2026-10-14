#!/usr/bin/env python3
"""#58: append eight reviewed normal-play screenshots to the private README set."""
import argparse
import json
import os
from pathlib import Path
import zipfile

from public_facility_check import check
from hd_source_audit import sha


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--run',type=Path,required=True)
    ap.add_argument('--source-commit',required=True)
    a=ap.parse_args()
    assert len(a.source_commit)==40 and all(c in '0123456789abcdef' for c in a.source_commit)
    out=Path('/repo/workspace/screenshots');manifest_path=out/'manifest.json'
    assert out.stat().st_uid==manifest_path.stat().st_uid==os.getuid()
    manifest=json.loads(manifest_path.read_text())
    report=json.loads((a.run/'verification.json').read_text())
    pixel_report=json.loads((a.run/'pixel-verification.json').read_text())
    assert check(a.run)==pixel_report
    assert sha(Path('/workspace/runs/taipei-preview-public-r1').read_bytes())==report['binary_sha256']
    assert len(manifest['screenshots'])==40 and 'environment_capture' not in manifest
    files={}
    for shot in report['screenshots']:
        with zipfile.ZipFile(a.run/shot['file'].replace('.png','-capture.zip')) as z:
            s=json.loads(z.read('status.json'));raw=z.read('presentation.png')
        assert raw==(a.run/shot['file']).read_bytes() and sha(raw)==shot['png_sha256']
        case=shot['file'].split('-')[0]
        lang=s['language'] if s['hd_enabled'] else 'zh-Hant'
        name='city-'+case+'-'+(lang if s['hd_enabled'] else 'original')+'.png'
        assert not (out/name).exists()
        manifest['screenshots'].append({'file':name,'scene':'normal-'+case+'-construction','language':lang,
            'mode':'hd-b' if s['hd_enabled'] else 'original','size':[1280,800],'png_sha256':sha(raw),
            'capture_sha256':shot['capture_sha256'],'frame_index_sha256':shot['frame_index_sha256'],
            'source_commit':a.source_commit,'steps':shot['steps'],'ticks':shot['ticks'],
            'map_origin':shot['map_origin'],'batch':'environment-facilities',
            'local_capture':'workspace/runs/'+a.run.name+'/'+shot['file'].replace('.png','-capture.zip')})
        files[name]=raw
    manifest['environment_capture']={'issue':'https://github.com/wicanr2/taipei/issues/58',
        'source_commit':a.source_commit,'binary_sha256':report['binary_sha256'],
        'local_receipt':'workspace/runs/'+a.run.name+'/verification.json',
        'local_receipt_sha256':sha((a.run/'verification.json').read_bytes()),
        'pixel_verification_sha256':sha((a.run/'pixel-verification.json').read_bytes()),
        'normal_gui':True,'original_save_read':True,'native_exit_tested':True,
        'cold_reload_tested':False,'long_state_sampling':False,'facilities':['waste','sewage'],
        'tools_sha256':{p.name:sha(p.read_bytes()) for p in [Path(__file__),
            Path('/workspace/tools/facility_batch_playtest.py'),Path('/workspace/tools/facility_batch_playtest.sh'),
            Path('/workspace/tools/public_facility_check.py')]},
        'limits':'限兩種正常施工圖；公共設施、其他相位、真機及正式封包未完成。'}
    assert len(files)==8 and len(manifest['screenshots'])==len({r['file'] for r in manifest['screenshots']})==48
    for name,raw in files.items():(out/name).write_bytes(raw)
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print('Exported eight environmental-facility PNGs; 48 README images total')


if __name__=='__main__':main()
