"""#48：真實圖表收據的有效破壞，重算 PNG／雜湊後雙側核對。"""
import argparse
import copy
import json
import os
import subprocess
import zipfile
from pathlib import Path

from hd_chart_window_check import expected_frame
from hd_file_dialogs_check import rgba
from hd_scroll_check import audit_bundle, source59
from hd_source_audit import sha
from infrastructure_prototype import png


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--receipt',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args = ap.parse_args()
    assert not args.out.exists() and args.out.parent.stat().st_uid == os.getuid()
    args.out.mkdir()
    with zipfile.ZipFile(args.receipt) as z:
        files = {n:z.read(n) for n in z.namelist()}
    original = json.loads(files['status.json'])
    source = files['frame-index.bin']
    assert original['hd']['chart_window']
    pixels = expected_frame(source,original['palette'])
    assert sha(pixels) == original['presentation_sha256']
    root = Path('/workspace/prototypes/hd-style')
    mask = rgba(root/'chart-windows-v2/0/text-ink.png',(1280,800))
    ink = next(i for i,a in enumerate(mask[3::4]) if a)
    results = []
    for fault in ['positive','unused-palette-positive','frame-pixel','text-pixel','data-pixel',
                  'outside-pixel','source-pixel','palette-fallback','phase-fallback','mode-fallback',
                  'family-id','data-sha']:
        directory = args.out/fault
        directory.mkdir()
        s = copy.deepcopy(original)
        output, indices = bytearray(pixels), bytearray(source)
        if fault == 'frame-pixel':
            output[(140*1280+264)*4] ^= 1
        elif fault == 'text-pixel':
            output[ink*4] ^= 1
        elif fault == 'data-pixel':
            output[(220*1280+344)*4] ^= 1
        elif fault == 'outside-pixel':
            output[0] ^= 1
        elif fault == 'source-pixel':
            indices[35*320+66] ^= 128
            s['hd'].update(chart_window=False,chart_data_sha256='',chart_reason='scene-fallback',reason='blocking-input')
        elif fault == 'palette-fallback':
            s['palette'][14][0] ^= 1
            s['hd'].update(chart_window=False,chart_data_sha256='',chart_reason='chart-palette-mismatch',reason='chart-palette-mismatch')
        elif fault == 'phase-fallback':
            s['dos_blocked'] = False
            s['hd'].update(chart_window=False,chart_data_sha256='',chart_reason='chart-unverified-phase',reason='chart-unverified-phase')
        elif fault == 'mode-fallback':
            s['mode'] = 3
            s['hd'].update(chart_window=False,chart_data_sha256='',chart_reason='scene-fallback',reason='video-mode')
        elif fault == 'family-id':
            s['hd']['chart_window'] = False
        elif fault == 'data-sha':
            s['hd']['chart_data_sha256'] = '0'*64
        elif fault == 'unused-palette-positive':
            s['palette'][next(i for i in range(256) if i not in set(source))][0] ^= 1
        changed = dict(files)
        changed['frame-index.bin'] = bytes(indices)
        changed['frame.png'] = png(bytes(v for i in indices for v in s['palette'][i]+[255]),320,200)
        changed['presentation.png'] = png(output,1280,800)
        s['frame_index_sha256'], s['presentation_sha256'] = sha(indices), sha(output)
        changed['status.json'] = (json.dumps(s,ensure_ascii=False,indent=2)+'\n').encode()
        path = directory/'case-capture.zip'
        with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED) as z:
            for name,raw in changed.items():
                z.writestr(name,raw)
        error = ''
        try:
            audit_bundle(path,source59(Path('/orig')))
        except AssertionError as e:
            error = str(e) or 'AssertionError'
        run = subprocess.run(['/workspace/runs/receipt-check-chart-r1','-dir',str(directory),
            '-original','/orig','-chart-reference',str(root)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        positive = fault.endswith('positive')
        assert bool(error) is not positive and (run.returncode!=0) is not positive, (fault,error,run.stdout[:700])
        results.append({'fault':fault,'positive':positive,'python_rejected':bool(error),
            'go_rejected':run.returncode!=0,'python_error':error,'go_output':run.stdout[:500],
            'receipt_sha256':sha(path.read_bytes()),'affected_digests_recomputed':True,'native_png_consistent':True})
    (args.out/'result.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'positive':sum(r['positive'] for r in results),
        'both_checkers_rejected':sum(r['python_rejected'] and r['go_rejected'] for r in results)}))


if __name__ == '__main__':
    main()
