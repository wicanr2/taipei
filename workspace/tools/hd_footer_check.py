"""#31：從原版資料獨立還原欄位，核對固定字形、整欄與回退。"""
import argparse
import functools
import json
import subprocess
from pathlib import Path

from footer_catalog import source, decode, crop, RECTS
from hd_source_audit import scene, sha

PALETTES = ['3b4208dbfa57fcac1e09c52c785ec7f0732799de26e6ece81e1a257edd1ce081',
            'e2ca09da088ea18b2846c73ba9fddd03b32c20511ca0f60429d03356a37f0c1f']


@functools.lru_cache(maxsize=1)
def references():
    root = Path('/workspace/prototypes/hd-style')
    arts = []
    for name, digest, size in [
        ('city-chrome-v1/frame.png', 'd3391282c3fde64b60b64fe59ba756537c4bb60b3766a161106e5432b4e396d6', 1280*800*4),
        ('footer-v1/glyphs.png', 'df2a49313a51d2076e4880bf88cf4fd8a28d722ea49fb98973c05a094107cd7c', 384*192*4)]:
        path = root/name
        assert sha(path.read_bytes()) == digest
        raw = subprocess.check_output(['convert', str(path), '-depth', '8', 'rgba:-'])
        assert len(raw) == size
        arts.append(raw)
    atlas = bytearray(arts[1])
    # PNG 儲存 straight alpha，RGBA 快取為 premultiplied，按 Go image/draw 整數契約。
    for at in range(0, len(atlas), 4):
        alpha = atlas[at+3]
        for c in range(3):
            atlas[at+c] = (atlas[at+c]*alpha*257//255) >> 8
    return source(Path('/orig/RS201.ROM').read_bytes()), arts[0], atlas


def expected_pixels(frame, palette, part, text, background, atlas):
    x0, y0, w, h = RECTS[part]
    result = bytearray(b''.join(background[((y*4+dy)*1280+x0*4)*4:((y*4+dy)*1280+(x0+w)*4)*4]
                               for y in range(y0, y0+h) for dy in range(4)))
    def glyph(index, x, y, ww, hh):
        for dy in range(hh):
            for dx in range(ww):
                src = (((index//6)*64+dy)*384+(index % 6)*64+dx)*4
                dst = (((y-y0)*4+dy)*w*4+(x-x0)*4+dx)*4
                alpha = atlas[src+3]
                for c in range(4):
                    result[dst+c] = (result[dst+c]*(65535-alpha*257)*257//65535+atlas[src+c]*257) >> 8
    def digits(value, x, y):
        for i, ch in enumerate(value):
            if ch != ' ':
                glyph(10 if ch == '-' else int(ch), x+6*i, y, 24, 28)
    if part == 0:
        if text[0]:
            for i, x in enumerate([19, 35, 51, 103]): glyph(11+i, x, 177, 60, 56)
            digits(text[0], 67, 181)
    else:
        digits(text[0], 253, 176); digits(text[1], 289, 176); digits(text[2], 253, 184)
        for i, (x, y) in enumerate([(283, 176), (303, 176), (303, 184)]): glyph(15+i, x, y, 28, 28)
        for y in range(184, 191):
            for x in range(247, 254):
                for dy in range(4):
                    at = (((y-y0)*4+dy)*w*4+(x-x0)*4)*4
                    result[at:at+16] = bytes(palette[frame[y*320+x]]+[255])*4
    return result


def covered_native(s):
    return {y*320+x for i, (xx, yy, w, h) in enumerate(RECTS)
            if s['hd'].get('footer_mask', 0) & (1 << i)
            for y in range(yy, yy+h) for x in range(xx, xx+w)}


def audit_footer(s, frame, rgba):
    if 'footer_mask' not in s['hd']: return None  # 歷史收據不能證明本批。
    if s['hd'].get('panel') or s['hd'].get('dialog'):
        # 主選單覆蓋底部座標，由呼叫端完整面板來源與區外核對負責。
        assert s['hd']['footer_mask'] == 0 and s['hd']['footer_text'] == ['', '', '', '']
        return {'mask': 0, 'text': ['', '', '', '']}
    refs, bg, atlas = references()
    origin = s.get('map_origin', {})
    active = s['hd_enabled'] and scene(s, frame) and origin.get('Valid') and 0 <= origin['X'] <= 76 and 0 <= origin['Y'] <= 74
    mask = 0; texts = ['', '', '', '']
    for part, (x, y, w, h) in enumerate(RECTS):
        values = decode(frame, refs, part)
        indices = sorted(set(crop(refs[0], RECTS[part])) | ({15, 32} if part == 0 else {15}))
        pal_ok = sha(bytes(v for i in indices for v in s['palette'][i])) == PALETTES[part]
        matched = active and values is not None and pal_ok
        if matched:
            mask |= 1 << part
            if part == 0: texts[0] = values[0]
            else: texts[1:] = values
            expected = expected_pixels(frame, s['palette'], part, values, bg, atlas)
        else:
            expected = b''.join(bytes(s['palette'][frame[row*320+col]]+[255])*4
                                for row in range(y, y+h) for _ in range(4) for col in range(x, x+w))
        actual = b''.join(rgba[(row*1280+x*4)*4:(row*1280+(x+w)*4)*4] for row in range(y*4, (y+h)*4))
        assert actual == expected, ('底部整欄像素失配', part, next((i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b), None))
    assert s['hd']['footer_mask'] == mask, '底部遮罩不符完整來源或色盤'
    assert s['hd']['footer_text'] == texts, '底部字串不符原版字模'
    if mask: assert s['hd']['footer_reason'] == ('matched-footer' if mask == 3 else 'partial-footer')
    return {'mask': mask, 'text': texts}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--receipts', type=Path, required=True)
    ap.add_argument('--require-time-update', action='store_true'); args = ap.parse_args()
    from hd_scroll_check import audit_bundle, source59
    sources = source59(Path('/orig')); samples = []
    for path in sorted(args.receipts.rglob('*-capture.zip')):
        s, frame, _, rgba, _ = audit_bundle(path, sources)
        result = audit_footer(s, frame, rgba); assert result is not None
        samples.append({'receipt': str(path.relative_to(args.receipts)), **result})
    costs = {r['text'][0].strip() for r in samples if r['mask'] & 1}
    dates = {tuple(r['text'][1:3]) for r in samples if r['mask'] & 2}
    money = {r['text'][3] for r in samples if r['mask'] & 2}
    assert any(r['mask'] == 3 for r in samples)
    if args.require_time_update: assert len(dates) > 1, '未由正常時間推進更新年月'
    result = {'bundles': len(samples), 'costs': sorted(costs), 'dates': sorted(dates), 'money': sorted(money),
              'full_source_recomputed': True, 'fixed_reference_equal': True, 'fallback_native': True, 'samples': samples}
    (args.receipts/'footer-verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'samples'}, ensure_ascii=False))


if __name__ == '__main__': main()
