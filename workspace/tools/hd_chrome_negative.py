"""#29：有效竄改負對照；重算雜湊與原版 PNG，區分來源及像素核對責任。"""
import argparse
import json
import subprocess
import zipfile
from pathlib import Path

from hd_scroll_check import audit_bundle, source59
from hd_source_audit import sha


def png(rgba, w, h):
    return subprocess.check_output(['convert', '-size', f'{w}x{h}', '-depth', '8', 'rgba:-',
                                    '-define', 'png:color-type=6', 'png:-'], input=rgba)


def check(checker, directory):
    art = Path('/workspace/prototypes/hd-style')
    return subprocess.run([str(checker), '-dir', str(directory),
        '-font-reference', str(art/'font-comparison/noto-font.png'),
        '-ui-reference', str(art/'city-icons-b-v1.png'),
        '-dialog-reference', str(art/'new-game-noto-reference-v1.png'),
        '-panel-manifest', str(art/'startup-menus-v1/manifest.json'),
        '-chrome-reference', str(art/'city-chrome-v1')],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


def main():
    ap = argparse.ArgumentParser()
    for name in ['receipt', 'checker', 'out']:
        ap.add_argument('--'+name, type=Path, required=True)
    args = ap.parse_args(); sources = source59(Path('/orig'))
    audit_bundle(args.receipt, sources)
    with zipfile.ZipFile(args.receipt) as z:
        files = {name: z.read(name) for name in z.namelist()}
    initial = json.loads(files['status.json'])
    assert initial['hd']['chrome_mask'] == 63 and initial['hd']['chrome_ring_mask'] == 0x3fff
    rgba = subprocess.check_output(['convert', 'png:-', '-depth', '8', 'rgba:-'], input=files['presentation.png'])
    positive = args.out/'positive'; positive.mkdir(parents=True, exist_ok=True)
    (positive/'positive-capture.zip').write_bytes(args.receipt.read_bytes())
    assert check(args.checker, positive).returncode == 0, '負對照前的有效正對照失敗'
    results = []
    for name, xy in [('frame', [0, 136]), ('fkey', [100, 12]), ('ring', [1092, 16]),
                     ('dynamic-status', [28, 704]), ('source', [0, 34]),
                     ('palette', [162, 0]), ('mask', [0, 0]), ('ring-mask', [0, 0])]:
        changed = dict(files); status = json.loads(files['status.json'])
        if name in ['source', 'palette']:
            frame = bytearray(files['frame-index.bin'])
            if name == 'source':
                frame[xy[1]*320+xy[0]] ^= 1
            else:
                status['palette'][xy[0]][0] ^= 1
            changed['frame-index.bin'] = bytes(frame)
            status['frame_index_sha256'] = sha(frame)
            native = bytes(v for index in frame for v in status['palette'][index]+[255])
            changed['frame.png'] = png(native, 320, 200)
        elif name == 'mask':
            status['hd'].update(chrome_mask=61, chrome_parts=5, chrome_reason='partial-chrome')
        elif name == 'ring-mask':
            status['hd'].update(chrome_ring_mask=0x3ffe, chrome_rings=13, chrome_reason='partial-chrome')
        else:
            pixels = bytearray(rgba); at = (xy[1]*1280+xy[0])*4
            pixels[at] ^= 127
            assert pixels != rgba
            changed['presentation.png'] = png(pixels, 1280, 800)
            status['presentation_sha256'] = sha(pixels)
        changed['status.json'] = json.dumps(status).encode()
        directory = args.out/name; directory.mkdir(parents=True, exist_ok=True)
        path = directory/'mutated-capture.zip'
        with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_STORED) as z:
            for member, data in changed.items():
                z.writestr(member, data)
        source_error = ''
        try:
            audit_bundle(path, sources)
        except AssertionError as error:
            source_error = str(error)
        run = check(args.checker, directory)
        if name != 'dynamic-status':
            assert source_error, (name, '來源或固定參考核對器未拒絕')
        if name not in ['source', 'palette']:
            assert run.returncode != 0, (name, '像素或區外核對器未拒絕')
        assert source_error or run.returncode != 0
        results.append({'case': name, 'xy': xy, 'source_checker_rejected': bool(source_error),
                        'source_error': source_error, 'pixel_checker_rejected': run.returncode != 0,
                        'native_png_consistent': True, 'affected_digest_updated': True})
    (args.out/'result.json').write_text(json.dumps(results, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(results, ensure_ascii=False))


if __name__ == '__main__':
    main()
