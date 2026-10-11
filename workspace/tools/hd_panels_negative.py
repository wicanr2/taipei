"""#31：重算受影響雜湊後，面板、區外、來源與選取竄改仍須拒絕。"""
import argparse
import json
import subprocess
import zipfile
from pathlib import Path

from hd_source_audit import sha


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--receipt', type=Path, required=True)
    ap.add_argument('--manifest', type=Path, required=True)
    ap.add_argument('--checker', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    with zipfile.ZipFile(args.receipt) as z:
        files = {name: z.read(name) for name in z.namelist()}
    s = json.loads(files['status.json'])
    assert s['hd']['panel'] == 'main' and s['hd']['panel_selection'] == 0
    rgba = subprocess.check_output(['convert', 'png:-', '-depth', '8', 'rgba:-'], input=files['presentation.png'])
    glyph = next((x, y) for y in range(610, 670) for x in range(140, 420)
                 if rgba[(y*1280+x)*4:(y*1280+x)*4+3] == b'\xff\x00\x00')
    cases = [('glyph', *glyph, 'panel pixels differ'),
             ('border', 68, 64, 'panel pixels differ'),
             ('outside', 60, 64, 'presentation changed native pixel'),
             ('source', 16, 15, 'panel source, palette or metadata mismatch'),
             ('palette', 14, 0, 'panel source, palette or metadata mismatch'),
             ('selection', 0, 0, 'panel source, palette or metadata mismatch')]
    results = []
    for name, x, y, expected in cases:
        changed = dict(files)
        status = json.loads(files['status.json'])
        if name == 'source':
            frame = bytearray(files['frame-index.bin'])
            frame[y*320+x] ^= 1
            changed['frame-index.bin'] = bytes(frame)
            status['frame_index_sha256'] = sha(frame)
        elif name == 'palette':
            status['palette'][x][0] ^= 1
        elif name == 'selection':
            status['hd']['panel_selection'] = 1
        else:
            png = subprocess.check_output(['convert', 'png:-', '-fill', 'rgb(0,255,0)', '-draw', f'point {x},{y}',
                                           '-define', 'png:color-type=6', 'png:-'], input=files['presentation.png'])
            pixels = subprocess.check_output(['convert', 'png:-', '-depth', '8', 'rgba:-'], input=png)
            assert pixels != rgba
            changed['presentation.png'] = png
            status['presentation_sha256'] = sha(pixels)
        changed['status.json'] = json.dumps(status).encode()
        directory = args.out/name
        directory.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(directory/'mutated-capture.zip', 'w', compression=zipfile.ZIP_STORED) as z:
            for member, data in changed.items():
                z.writestr(member, data)
        run = subprocess.run([str(args.checker), '-dir', str(directory), '-panel-manifest', str(args.manifest)],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        assert run.returncode != 0 and expected in run.stdout, (name, run.returncode, run.stdout)
        results.append({'case': name, 'xy': [x, y], 'rejected': True, 'expected_error': expected,
                        'affected_digest_updated': name in ['glyph', 'border', 'outside', 'source']})
    (args.out/'result.json').write_text(json.dumps(results, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
