"""#31：完整說明視窗的獨立來源、固定參考及區外像素核對。"""
import argparse
import functools
import json
import subprocess
import zipfile
from pathlib import Path

from hd_source_audit import sha

SOURCE_SHA = 'a6299b68e4e28c3309bcbf10f2e562c4a9be7fb7d2a43f8a4bc79e69a77ccc8b'
PALETTE_SHA = '701e28d343effaf04f5e2b535626a87a3b18e4a1c2fcdc10cbb2a6939714e4de'
REFERENCE_SHA = '6bfa6faeffd0950d31af1a5bb9da84aa71af4a34dc36dae374d3d387b1e6c7e9'
DEFAULT_REFERENCE = Path('/workspace/prototypes/hd-style/new-game-noto-reference-v1.png')


@functools.lru_cache(maxsize=4)
def reference_rgba(path=DEFAULT_REFERENCE):
    assert sha(path.read_bytes()) == REFERENCE_SHA, '說明視窗固定參考失配'
    rgba = subprocess.check_output(['convert', str(path), '-depth', '8', 'rgba:-'])
    assert len(rgba) == 944*528*4
    return rgba


def source_matches(s, frame):
    box = b''.join(frame[y*320+18:y*320+254] for y in range(37, 169))
    colors = bytes(c for i in [15, 16, 20, 23, 27, 134] for c in s['palette'][i])
    return (s['hd_enabled'] and s['mode'] == 19 and sha(box) == SOURCE_SHA
            and sha(colors) == PALETTE_SHA)


def audit_dialog(s, frame, rgba, reference=DEFAULT_REFERENCE):
    # 舊版收據沒有本批欄位，仍按原版回退規則核對。
    active = 'dialog' in s['hd'] and source_matches(s, frame)
    assert s['hd'].get('dialog', '') == ('new-game' if active else ''), '視窗旗標不符完整來源'
    if not active:
        return False
    assert s['hd']['dialog_reason'] == 'matched-dialog'
    assert s['hd']['Painted'] == s['hd']['font_labels'] == s['hd']['ui_icons'] == 0
    ref = reference_rgba(reference)
    for y in range(800):
        native = bytes(c for x in range(1280) for c in s['palette'][frame[(y//4)*320+x//4]]+[255])
        if 148 <= y < 676:
            at = (y-148)*944*4
            want = native[:72*4]+ref[at:at+944*4]+native[1016*4:]
        else:
            want = native
        at = y*1280*4
        assert rgba[at:at+1280*4] == want, ('說明視窗或區外像素失配', y)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--receipts', type=Path, required=True)
    ap.add_argument('--reference', type=Path, default=DEFAULT_REFERENCE)
    args = ap.parse_args()
    samples = []
    for path in sorted(args.receipts.rglob('*-capture.zip')):
        with zipfile.ZipFile(path) as z:
            s = json.loads(z.read('status.json'))
            frame = z.read('frame-index.bin')
            rgba = subprocess.check_output(['convert', 'png:-', '-depth', '8', 'rgba:-'], input=z.read('presentation.png'))
        assert len(frame) == 64000 and sha(frame) == s['frame_index_sha256']
        assert sha(rgba) == s['presentation_sha256']
        samples.append({'receipt': str(path.relative_to(args.receipts)),
                        'dialog': audit_dialog(s, frame, rgba, args.reference)})
    assert any(x['dialog'] for x in samples), '未實際經過 HD 說明視窗'
    labels = {x['receipt']: x['dialog'] for x in samples}
    assert labels['new-game-capture.zip'] and labels['new-game-theme-hd-capture.zip']
    assert not labels['new-game-theme-original-capture.zip'] and not labels['difficulty-capture.zip']
    result = {'reference_sha256': REFERENCE_SHA, 'full_panel_and_outside_pixels_equal': True,
              'source_independently_matched': True, 'f12_roundtrip': True,
              'closed_without_residue': True, 'samples': samples}
    (args.receipts/'dialog-verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'samples'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
