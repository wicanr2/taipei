"""#38：獨立重建來源、Noto 墨跡、完整視窗與全部區外像素。"""
import argparse
import functools
import json
import subprocess
import zipfile
from pathlib import Path

from full_asset_catalog import sha
from file_dialog_catalog import BROWSER, PROMPT, crop, decode_browser, references as source_references

MANIFEST = '6fc74370c334d77b62f2e0d224a80cb967d158da3e632a79aa1e4017636792b6'
FONT = 'dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4'
LICENSE = '6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2'
PALETTE = '4103f1e8410a2ee91de3074579ce3062de27f48c1d2c415f46bbd195c50b56df'


def rgba(path, size):
    data = subprocess.check_output(['convert', str(path), '-depth', '8', 'rgba:-'])
    assert len(data) == size[0]*size[1]*4
    return data


def premultiply(data):
    data = bytearray(data)
    for at in range(0, len(data), 4):
        for c in range(3):
            data[at+c] = (data[at+c]*data[at+3]*257//255) >> 8
    return data


def glyph(dst, width, atlas, index, x, y, w, h):
    for dy in range(h):
        for dx in range(w):
            src = ((index//16*64+dy)*1024+index % 16*64+dx)*4
            at = ((y+dy)*width+x+dx)*4
            alpha = atlas[src+3]
            for c in range(4):
                dst[at+c] = (dst[at+c]*(65535-alpha*257)*257//65535+atlas[src+c]*257) >> 8


@functools.lru_cache(maxsize=1)
def references():
    root = Path('/workspace/prototypes/hd-style')
    raw = (root/'file-dialogs-v1/manifest.json').read_bytes()
    assert sha(raw) == MANIFEST
    manifest = json.loads(raw)
    assert sha((root/'fonts/NotoSansCJKtc-Regular.otf').read_bytes()) == FONT == manifest['font_sha256']
    assert sha((root/'fonts/LICENSE').read_bytes()) == LICENSE == manifest['license_sha256']
    pictures = {}
    sizes = {'glyphs.png': (1024,832), 'browser.png': (268,428), 'quit-confirm.png': (896,72)}
    for name, size in sizes.items():
        path = root/'file-dialogs-v1'/name
        assert sha(path.read_bytes()) == manifest['images'][name]
        pictures[name] = rgba(path,size)
    assert sha((root/'file-dialogs-v1/palette.json').read_bytes()) == PALETTE
    return root, manifest, pictures


@functools.lru_cache(maxsize=1)
def sources():
    return source_references(Path('/orig/RS201.ROM').read_bytes())


def audit_file(s, frame, pixels):
    # 舊收據保留當時的原版回退契約，不追加新版能力。
    if 'file_dialog' not in s['hd']:
        return False
    assert len(frame) == 64000 and len(pixels) == 1280*800*4
    refs = sources()
    decoded = decode_browser(frame, refs)
    family, rect = ('file-browser', BROWSER) if decoded else ('quit-confirm', PROMPT)
    known = bool(decoded) or crop(frame, PROMPT) == refs['prompt']
    if not known or s['mode'] != 19:
        assert not s['hd']['file_dialog'] and s['hd']['file_text'] == ['']*8 and s['hd']['file_colors'] == [0]*8
        return False
    root, _, pictures = references()
    palette = json.loads((root/'file-dialogs-v1/palette.json').read_bytes())
    palette_ok = all(s['palette'][i] == palette[i] for i in set(crop(frame,rect)))
    enabled = s['hd_enabled'] and palette_ok
    assert s['hd']['file_dialog'] == (family if enabled else ''), '檔案視窗旗標不符完整來源與色盤'
    assert s['hd']['file_text'] == (decoded['rows'] if enabled and decoded else ['']*8)
    assert s['hd']['file_colors'] == (decoded['colors'] if enabled and decoded else [0]*8)
    reason = 'matched-file-dialog' if enabled else ('file-palette-mismatch' if s['hd_enabled'] else 'original')
    assert s['hd']['file_reason'] == s['hd']['reason'] == reason
    assert all(s['hd'].get(k,0) == 0 for k in ['Painted','font_labels','ui_icons','chrome_mask','chrome_ring_mask','footer_mask'])
    assert not s['hd'].get('panel') and not s['hd'].get('dialog')
    expected = bytearray()
    for y in range(200):
        row = b''.join(bytes(s['palette'][i]+[255])*4 for i in frame[y*320:(y+1)*320])
        expected.extend(row*4)
    if enabled:
        x,y,w,h = [i*4 for i in rect]
        overlay = bytearray(pictures['browser.png' if decoded else 'quit-confirm.png'])
        if decoded:
            atlas = premultiply(pictures['glyphs.png'])
            for line, text in enumerate(decoded['rows']):
                yy = 8 if line == 0 else 26+11*(line-1)
                for column,ch in enumerate(text):
                    if ch != ' ':
                        index = ord(ch)-32+(95 if decoded['colors'][line] == 32 else 0)
                        glyph(overlay,w,atlas,index,(10+6*column)*4,yy*4,24,28)
        for yy in range(h):
            expected[((y+yy)*1280+x)*4:((y+yy)*1280+x+w)*4] = overlay[yy*w*4:(yy+1)*w*4]
    assert pixels == expected, ('檔案視窗或區外像素失配', family)
    return True


def audit_ink():
    root, manifest, pictures = references()
    atlas = pictures['glyphs.png']
    assert len(manifest['ink_checks']) == 198
    for index, check in enumerate(manifest['ink_checks']):
        assert check['index'] == index
        x0,y0 = index % 16*64,index//16*64
        w,h = (24,28) if index < 190 else (60,56)
        expected_safe = {'Min': {'X':x0,'Y':y0}, 'Max': {'X':x0+w,'Y':y0+h}}
        assert check['safe'] == expected_safe
        points = [(x,y) for y in range(y0,y0+64) for x in range(x0,x0+64) if atlas[(y*1024+x)*4+3]]
        assert bool(points) == (index not in [0,95])
        assert all(x0 <= x < x0+w and y0 <= y < y0+h for x,y in points)
        if points:
            actual = {'Min': {'X':min(x for x,y in points), 'Y':min(y for x,y in points)},
                      'Max': {'X':max(x for x,y in points)+1, 'Y':max(y for x,y in points)+1}}
            assert check['actual_ink'] == actual
        assert check['missing_glyph'] is False and check['clipped'] is False
    assert all(pictures['browser.png'][i] == 255 for i in range(3, len(pictures['browser.png']), 4))
    # 八個最寬 W 仍位於原輸入列與清單列的安全矩形。
    assert 40+8*24 <= 248 and 32+28 <= 72 and 104+6*44+28 < 428
    chrome = root/'city-chrome-v1/frame.png'
    assert sha(chrome.read_bytes()) == 'd3391282c3fde64b60b64fe59ba756537c4bb60b3766a161106e5432b4e396d6'
    bg = rgba(chrome,(1280,800))
    expected = bytearray(b''.join(bg[(y*1280+28)*4:(y*1280+924)*4] for y in range(700,772)))
    alpha = premultiply(atlas)
    for i in range(8):
        glyph(expected,896,alpha,190+i,(19+16*i-7)*4,8,60,56)
    for i,ch in enumerate('?(Y/N)'):
        glyph(expected,896,alpha,95+ord(ch)-32,(153+6*i-7)*4,24,24,28)
    assert expected == pictures['quit-confirm.png'], '離開提示完整組合不符固定參考'
    return {'glyphs':198,'actual_alpha_checked':True,'eight_w_safe':True,
            'prompt_fixed_composition_equal':True,'manifest_sha256':MANIFEST}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--receipts', type=Path)
    args = ap.parse_args()
    result = audit_ink()
    if args.receipts:
        samples = []
        for path in sorted(args.receipts.rglob('*-capture.zip')):
            with zipfile.ZipFile(path) as z:
                s, frame = json.loads(z.read('status.json')), z.read('frame-index.bin')
                pixels = subprocess.check_output(['convert','png:-','-depth','8','rgba:-'],input=z.read('presentation.png'))
            assert sha(frame) == s['frame_index_sha256'] and sha(pixels) == s['presentation_sha256']
            if audit_file(s,frame,pixels):
                samples.append({'receipt':str(path.relative_to(args.receipts)), 'family':s['hd']['file_dialog'],
                                'enabled':s['hd_enabled'], 'steps':s['steps']})
        assert {'file-browser','quit-confirm'} <= {s['family'] for s in samples}, '缺少正常 GUI 的兩個家族'
        result.update({'full_source_and_palette_checked':True,'full_roi_and_outside_equal':True,'samples':samples})
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))


if __name__ == '__main__':
    main()
