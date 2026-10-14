#!/usr/bin/env python3
"""038：只匯出七代表中明列的兩組真實GUI，原始收據留本機。"""
import argparse
import json
import os
from pathlib import Path
import re
import struct
import zipfile

from infrastructure_catalog import sha


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True)
    ap.add_argument('--source-commit',required=True);a=ap.parse_args()
    assert re.fullmatch('[0-9a-f]{40}',a.source_commit)
    report=json.loads((a.run/'verification.json').read_text())
    pixels=json.loads((a.run/'pixel-verification.json').read_text())
    assert report['normal_gui'] and report['native_exit_tested'] and pixels['baseline_save_identical']
    assert len(pixels['screenshots'])==42 and pixels['effective_pixel_negative_controls']==42
    assert pixels['verification_sha256']==sha((a.run/'verification.json').read_bytes())
    out=Path('/repo/workspace/screenshots');path=out/'manifest.json'
    assert out.stat().st_uid==path.stat().st_uid==os.getuid()
    m=json.loads(path.read_text());assert len(m['screenshots'])==72 and 'map_capture' not in m
    selected={'m34-b08':'map-buildings','m34-b00':'map-zones'};files={}
    for shot in report['screenshots']:
        if shot['case'] not in selected:continue
        receipt=a.run/shot['file'].replace('.png','-capture.zip')
        assert sha(receipt.read_bytes())==shot['capture_sha256']
        with zipfile.ZipFile(receipt) as z:s=json.loads(z.read('status.json'));raw=z.read('presentation.png')
        assert raw==(a.run/shot['file']).read_bytes() and sha(raw)==shot['png_sha256']
        assert struct.unpack_from('>II',raw,16)==(1280,800)
        suffix=s['language'] if s['hd_enabled'] else 'original'
        name='city-'+selected[shot['case']]+'-'+suffix+'.png';assert not (out/name).exists()
        files[name]=raw
        m['screenshots'].append({'file':name,'scene':'existing-'+selected[shot['case']],
            'language':s['language'] if s['hd_enabled'] else 'zh-Hant','mode':'hd-b' if s['hd_enabled'] else 'original',
            'size':[1280,800],'png_sha256':sha(raw),'capture_sha256':shot['capture_sha256'],
            'frame_index_sha256':shot['frame_index_sha256'],'source_commit':a.source_commit,
            'steps':shot['steps'],'ticks':shot['ticks'],'map_origin':shot['map_origin'],'batch':'map-completion',
            'local_capture':'workspace/runs/'+a.run.name+'/'+shot['file'].replace('.png','-capture.zip')})
    assert len(files)==12 and len(m['screenshots'])==len({s['file'] for s in m['screenshots']})==84
    m['map_capture']={'issue':'https://github.com/wicanr2/taipei/issues/62','source_commit':a.source_commit,
        'binary_sha256':report['binary_sha256'],'local_receipt':'workspace/runs/'+a.run.name+'/verification.json',
        'local_receipt_sha256':sha((a.run/'verification.json').read_bytes()),
        'pixel_verification_sha256':sha((a.run/'pixel-verification.json').read_bytes()),
        'normal_gui':True,'state_injection':False,'original_save_read':True,'native_exit_tested':True,
        'source_entries':1134,'unique_map_sources':1049,'new_nonempty_sources':301,
        'normal_representatives':7,'selected_scenes':selected,'screenshots':12,
        'tools_sha256':{p.name:sha(p.read_bytes()) for p in [Path(__file__),Path('/workspace/tools/map_completion_gui.py'),Path('/workspace/tools/map_completion_check.py')]},
        'limits':'完整原圖表格與七種正常代表；沒有逐種成長／災害分支、人耳或外平台真機驗收。正式封包另驗。'}
    for name,raw in files.items():(out/name).write_bytes(raw)
    path.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
    print('Exported twelve actual GUI PNGs; 84 total',sha(path.read_bytes()))


if __name__=='__main__':main()
