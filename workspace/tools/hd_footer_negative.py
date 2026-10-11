"""#31：更新雜湊後的有效欄位、來源、色盤與中繼資料負對照。"""
import argparse
import json
import subprocess
import zipfile
from pathlib import Path
from hd_scroll_check import audit_bundle, source59
from hd_chrome_negative import png
from hd_source_audit import sha
from hd_footer_check import audit_footer


def check(directory):
    root = Path('/workspace/prototypes/hd-style')
    return subprocess.run(['/workspace/runs/receipt-check', '-dir', str(directory),
        '-font-reference', str(root/'font-comparison/noto-font.png'),
        '-ui-reference', str(root/'city-icons-b-v1.png'),
        '-dialog-reference', str(root/'new-game-noto-reference-v1.png'),
        '-panel-manifest', str(root/'startup-menus-v1/manifest.json'),
        '-chrome-reference', str(root/'city-chrome-v1'), '-footer-reference', str(root)],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--receipt', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True); args = ap.parse_args()
    sources = source59(Path('/orig')); s, frame, _, rgba, _ = audit_bundle(args.receipt, sources)
    assert s['hd']['footer_mask'] == 3 and s['hd']['footer_text'][0].strip()
    with zipfile.ZipFile(args.receipt) as z: files = {n:z.read(n) for n in z.namelist()}
    positive = args.out/'positive'; positive.mkdir(parents=True, exist_ok=True)
    (positive/'positive-capture.zip').write_bytes(args.receipt.read_bytes())
    assert check(positive).returncode == 0, '負對照之前的正對照失敗'
    results = []
    for name, xy in [('glyph', [83, 720]), ('background', [32, 704]), ('symbol', [996, 740]),
                     ('outside', [10, 690]), ('source', [19, 177]), ('palette', [32, 0]),
                     ('mask', [0, 0]), ('text', [0, 0])]:
        changed = dict(files); status = json.loads(files['status.json'])
        if name in ['source', 'palette']:
            native = bytearray(frame)
            if name == 'source': native[xy[1]*320+xy[0]] ^= 128
            else: status['palette'][32][0] ^= 1
            changed['frame-index.bin'] = native; status['frame_index_sha256'] = sha(native)
            changed['frame.png'] = png(bytes(v for i in native for v in status['palette'][i]+[255]), 320, 200)
        elif name == 'mask': status['hd'].update(footer_mask=2, footer_reason='partial-footer')
        elif name == 'text': status['hd']['footer_text'][0] = '000000'
        else:
            pixels = bytearray(rgba); pixels[(xy[1]*1280+xy[0])*4] ^= 127
            changed['presentation.png'] = png(pixels, 1280, 800); status['presentation_sha256'] = sha(pixels)
        changed['status.json'] = json.dumps(status).encode()
        directory = args.out/name; directory.mkdir(parents=True, exist_ok=True)
        path = directory/'mutated-capture.zip'
        with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_STORED) as z:
            for n, raw in changed.items(): z.writestr(n, raw)
        error = ''
        try:
            if name == 'outside': audit_bundle(path, sources)
            else:
                actual = subprocess.check_output(['convert','png:-','-depth','8','rgba:-'], input=changed['presentation.png'])
                audit_footer(status, changed['frame-index.bin'], actual)
        except AssertionError as e: error = str(e)
        run = check(directory)
        if name != 'outside': assert error, (name, '完整來源與固定參考未拒絕')
        if name not in ['source', 'palette']: assert run.returncode != 0, (name, '完整像素核對未拒絕')
        assert error or run.returncode != 0
        results.append({'case': name, 'source_checker_rejected': bool(error),
            'pixel_checker_rejected': run.returncode != 0, 'error': error,
            'affected_digest_updated': True, 'native_png_consistent': True})
    (args.out/'result.json').write_text(json.dumps(results, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(results, ensure_ascii=False))


if __name__ == '__main__': main()
