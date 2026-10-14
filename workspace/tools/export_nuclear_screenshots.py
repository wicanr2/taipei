#!/usr/bin/env python3
"""#46：核對後匯出六張既有核電廠實際畫面至私人 README。"""
import argparse
import json
import os
from pathlib import Path
import zipfile

from nuclear_check import check
from hd_source_audit import sha


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True)
    ap.add_argument('--source-commit',required=True);a=ap.parse_args()
    assert len(a.source_commit)==40 and all(c in '0123456789abcdef' for c in a.source_commit)
    out=Path('/repo/workspace/screenshots');path=out/'manifest.json'
    assert out.stat().st_uid==path.stat().st_uid==os.getuid()
    m=json.loads(path.read_text());assert len(m['screenshots'])==54 and 'nuclear_capture' not in m
    r=json.loads((a.run/'verification.json').read_text())
    assert check(a.run)==json.loads((a.run/'pixel-verification.json').read_text())
    assert sha(Path('/workspace/runs/taipei-preview-nuclear-r1').read_bytes())==r['binary_sha256']
    exported={}
    for shot in r['screenshots']:
        if not shot['file'].startswith('nuclear-'):continue
        receipt=a.run/shot['file'].replace('.png','-capture.zip')
        with zipfile.ZipFile(receipt) as z:s=json.loads(z.read('status.json'));raw=z.read('presentation.png')
        assert raw==(a.run/shot['file']).read_bytes() and sha(raw)==shot['png_sha256']
        name='city-'+shot['file'];assert not (out/name).exists()
        m['screenshots'].append({'file':name,'scene':'existing-nuclear-plant',
            'language':s['language'] if s['hd_enabled'] else 'zh-Hant','mode':'hd-b' if s['hd_enabled'] else 'original',
            'size':[1280,800],'png_sha256':sha(raw),'capture_sha256':shot['capture_sha256'],
            'frame_index_sha256':shot['frame_index_sha256'],'source_commit':a.source_commit,
            'steps':shot['steps'],'ticks':shot['ticks'],'map_origin':shot['map_origin'],'batch':'nuclear-plant',
            'local_capture':'workspace/runs/'+a.run.name+'/'+receipt.name})
        exported[name]=raw
    assert len(exported)==6 and len(m['screenshots'])==len({s['file'] for s in m['screenshots']})==60
    m['nuclear_capture']={'issue':'https://github.com/wicanr2/taipei/issues/46','source_commit':a.source_commit,
        'binary_sha256':r['binary_sha256'],'normal_gui':True,'original_save_read':True,'native_exit_tested':True,
        'new_nuclear_construction_tested':False,'long_state_sampling':False,
        'local_receipt':'workspace/runs/'+a.run.name+'/verification.json',
        'local_receipt_sha256':sha((a.run/'verification.json').read_bytes()),
        'pixel_verification_sha256':sha((a.run/'pixel-verification.json').read_bytes()),
        'tools_sha256':{p.name:sha(p.read_bytes()) for p in [Path(__file__),Path('/workspace/tools/nuclear_check.py'),
            Path('/workspace/tools/nuclear_existing_playtest.py'),Path('/workspace/tools/nuclear_existing_playtest.sh')]},
        'limits':'限正常冷讀既有核電廠的靜態圖與已驗路徑；新建施工、其他相位、真機及正式封包未驗。'}
    for name,raw in exported.items():(out/name).write_bytes(raw)
    path.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
    print('Exported six nuclear PNGs; 60 README images total')


if __name__=='__main__':main()
