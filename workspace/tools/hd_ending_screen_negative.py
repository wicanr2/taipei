"""#47：以真實政績收據建立有效破壞，重算 PNG／雜湊後要求雙重拒絕。"""
import argparse
import copy
import json
import os
import subprocess
import zipfile
from pathlib import Path

from hd_ending_screen_check import reference
from hd_file_dialogs_check import rgba
from hd_scroll_check import audit_bundle, source59
from hd_source_audit import sha
from infrastructure_prototype import png


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--receipt', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    assert not args.out.exists() and args.out.parent.stat().st_uid == os.getuid()
    args.out.mkdir()
    with zipfile.ZipFile(args.receipt) as z:
        files = {name: z.read(name) for name in z.namelist()}
    original = json.loads(files['status.json'])
    source, palette, pixels = reference()
    assert files['frame-index.bin'] == source and original['hd']['ending_screen'] == 'achievement-base'
    assert original['presentation_sha256'] == sha(pixels)
    root = Path('/workspace/prototypes/hd-style')
    mask = rgba(root/'ending-scene-v1/title-ink.png', (1280, 800))
    ink = next(i for i, alpha in enumerate(mask[3::4]) if alpha)
    results = []
    for fault in ['positive', 'unused-palette-positive', 'background-pixel', 'title-pixel',
                  'source-pixel', 'phase-fallback', 'mode-fallback', 'palette-fallback', 'family-id']:
        directory = args.out/fault
        directory.mkdir()
        s = copy.deepcopy(original)
        output, indices = bytearray(pixels), bytearray(source)
        if fault == 'background-pixel':
            output[(450*1280+640)*4] ^= 1
        elif fault == 'title-pixel':
            output[ink*4] ^= 1
        elif fault == 'source-pixel':
            indices[100*320+160] ^= 128
            s['hd'].update(ending_screen='', ending_reason='scene-fallback', reason='blocking-input')
        elif fault == 'phase-fallback':
            s['dos_blocked'] = False
            s['hd'].update(ending_screen='', ending_reason='ending-unverified-phase', reason='ending-unverified-phase')
        elif fault == 'mode-fallback':
            s['mode'] = 3
            s['hd'].update(ending_screen='', ending_reason='scene-fallback', reason='video-mode')
        elif fault == 'palette-fallback':
            s['palette'][148][0] ^= 1
            s['hd'].update(ending_screen='', ending_reason='ending-palette-mismatch', reason='ending-palette-mismatch')
        elif fault == 'family-id':
            s['hd']['ending_screen'] = 'all-achievements'
        elif fault == 'unused-palette-positive':
            s['palette'][next(i for i in range(256) if i not in palette)][0] ^= 1
        changed = dict(files)
        changed['frame-index.bin'] = bytes(indices)
        changed['frame.png'] = png(bytes(v for i in indices for v in s['palette'][i]+[255]), 320, 200)
        changed['presentation.png'] = png(output, 1280, 800)
        s['frame_index_sha256'], s['presentation_sha256'] = sha(indices), sha(output)
        changed['status.json'] = (json.dumps(s, ensure_ascii=False, indent=2)+'\n').encode()
        path = directory/'case-capture.zip'
        with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
            for name, raw in changed.items():
                z.writestr(name, raw)
        error = ''
        try:
            audit_bundle(path, source59(Path('/orig')))
        except AssertionError as e:
            error = str(e) or 'AssertionError'
        command = ['/workspace/runs/receipt-check-ending-r1', '-dir', str(directory),
                   '-original', '/orig', '-ending-reference', str(root)]
        run = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        positive = fault.endswith('positive')
        assert bool(error) is not positive and (run.returncode != 0) is not positive, (fault, error, run.stdout[:700])
        results.append({'fault': fault, 'positive': positive, 'python_rejected': bool(error),
                        'go_rejected': run.returncode != 0, 'python_error': error,
                        'go_output': run.stdout[:500], 'receipt_sha256': sha(path.read_bytes()),
                        'affected_digests_recomputed': True, 'native_png_consistent': True})
    (args.out/'result.json').write_text(json.dumps(results, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'positive': sum(r['positive'] for r in results),
                      'both_checkers_rejected': sum(r['python_rejected'] and r['go_rejected'] for r in results)}))


if __name__ == '__main__':
    main()
