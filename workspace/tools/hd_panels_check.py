"""#31：啟動選單以完整原版來源及固定面板獨立逐像素核對。"""
import argparse
import functools
import json
import subprocess
import zipfile
from pathlib import Path

from hd_source_audit import sha

MANIFEST_SHA = 'daeb0a0b440bce18b792cae3b89bcacc98b78e19ae05ab5a7e19f86c6cc3384d'
DEFAULT_MANIFEST = Path('/workspace/prototypes/hd-style/startup-menus-v1/manifest.json')
TOOL_MANIFEST = Path('/workspace/prototypes/hd-style/tool-menus-v1/manifest.json')
TOOL_MANIFEST_SHA = '288687aa21460d01aa87dd24060c5bbd3ff50035bf26bab5c821d23688f2543e'


@functools.lru_cache(maxsize=2)
def references(path=DEFAULT_MANIFEST):
    expected, count = (TOOL_MANIFEST_SHA, 18) if path == TOOL_MANIFEST else (MANIFEST_SHA, 13)
    assert sha(path.read_bytes()) == expected, '完整面板 manifest 失配'
    data = json.loads(path.read_bytes())
    assert data['schema'] == 1 and len(data['states']) == count
    result = []
    for state in data['states']:
        image = path.parent/state['image']
        assert sha(image.read_bytes()) == state['image_sha256'], '啟動面板參考失配'
        pixels = subprocess.check_output(['convert', str(image), '-depth', '8', 'rgba:-'])
        assert len(pixels) == state['native'][2]*state['native'][3]*16*4
        result.append((state, pixels))
    return result


def matching_state(s, frame, manifest=DEFAULT_MANIFEST):
    if not s['hd_enabled'] or s['mode'] != 19:
        return None
    candidates = references(manifest)
    if manifest == DEFAULT_MANIFEST and TOOL_MANIFEST.exists():
        candidates = candidates+references(TOOL_MANIFEST)
    for state, pixels in candidates:
        x, y, w, h = state['native']
        box = b''.join(frame[row*320+x:row*320+x+w] for row in range(y, y+h))
        colors = bytes(c for i in state['palette_indices'] for c in s['palette'][i])
        if sha(box) == state['source_sha256'] and sha(colors) == state['palette_sha256']:
            return state, pixels
    return None


def audit_panel(s, frame, rgba, manifest=DEFAULT_MANIFEST):
    # 舊版收據沒有本批欄位，仍按當時的原版回退核對。
    match = matching_state(s, frame, manifest) if 'panel' in s['hd'] else None
    assert s['hd'].get('panel', '') == (match[0]['id'] if match else ''), '面板旗標不符完整來源'
    if not match:
        return False
    state, ref = match
    assert s['hd']['panel_selection'] == state['selection'], '選取值不符完整來源'
    assert s['hd']['panel_reason'] == 'matched-panel'
    assert s['hd']['Painted'] == s['hd']['font_labels'] == s['hd']['ui_icons'] == 0
    assert s['hd'].get('chrome_mask', 0) == s['hd'].get('chrome_ring_mask', 0) == s['hd'].get('footer_mask', 0) == 0
    assert not s['hd'].get('dialog')
    x, y, w, h = [i*4 for i in state['native']]
    for yy in range(800):
        native = b''.join(bytes(s['palette'][index]+[255])*4 for index in frame[(yy//4)*320:(yy//4+1)*320])
        if y <= yy < y+h:
            at = (yy-y)*w*4
            want = native[:x*4]+ref[at:at+w*4]+native[(x+w)*4:]
        else:
            want = native
        at = yy*1280*4
        assert rgba[at:at+1280*4] == want, ('選單或區外像素失配', state['id'], state['selection'], yy)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--receipts', type=Path, required=True)
    ap.add_argument('--manifest', type=Path, default=DEFAULT_MANIFEST)
    args = ap.parse_args()
    samples, states = [], set()
    for path in sorted(args.receipts.rglob('*-capture.zip')):
        with zipfile.ZipFile(path) as z:
            s = json.loads(z.read('status.json'))
            frame = z.read('frame-index.bin')
            rgba = subprocess.check_output(['convert', 'png:-', '-depth', '8', 'rgba:-'], input=z.read('presentation.png'))
        assert len(frame) == 64000 and sha(frame) == s['frame_index_sha256']
        assert sha(rgba) == s['presentation_sha256']
        active = audit_panel(s, frame, rgba, args.manifest)
        if active:
            states.add((s['hd']['panel'], s['hd']['panel_selection']))
        samples.append({'receipt': str(path.relative_to(args.receipts)), 'active': active,
                        'panel': s['hd'].get('panel'), 'selection': s['hd'].get('panel_selection')})
    assert states == {(scene, i) for scene, n in [('main', 3), ('city', 7), ('difficulty', 3)] for i in range(n)}, '缺少十三種正常狀態'
    for scene in ['main', 'city', 'difficulty']:
        assert any(x['receipt'] == scene+'-theme-original-capture.zip' and not x['active'] for x in samples)
        assert any(x['receipt'] == scene+'-theme-hd-capture.zip' and x['active'] for x in samples)
    result = {'manifest_sha256': MANIFEST_SHA, 'states': sorted(states), 'full_panel_and_outside_equal': True,
              'source_and_selection_independently_matched': True, 'samples': samples}
    (args.receipts/'panels-verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'samples'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
