"""#38：獨立核對固定 Noto 原型墨跡及離開提示的完整組合。"""
import argparse
import functools
import json
import subprocess
from pathlib import Path

from full_asset_catalog import sha

MANIFEST = '6fc74370c334d77b62f2e0d224a80cb967d158da3e632a79aa1e4017636792b6'
FONT = 'dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4'
LICENSE = '6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2'


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
    return root, manifest, pictures


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
    args = ap.parse_args()
    result = audit_ink()
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))


if __name__ == '__main__':
    main()
