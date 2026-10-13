#!/usr/bin/env python3
"""#54: independent chart pixels plus frozen pre-task localization references."""
import argparse
import copy
import functools
import io
import json
from pathlib import Path
import zipfile

from hd_chart_window_check import reference, expected_frame
from chart_window_source_check import crop, fixed, NATIVE, DATA
from hd_file_dialogs_check import rgba
from hd_footer_check import references as footer_references, expected_pixels, PALETTES
from footer_catalog import decode, crop as footer_crop, RECTS
from full_asset_catalog import sha

FROZEN = {
    'zh-Hant': 'df0b2960255a89d6c3260f9a1504cda4b5cb1b7e650857aae18e95f835d60184',
    'zh-Hans': '06d316921836d5cd08787b4d1f3e458d32b80c03f0cded265d1a72122f1cc98a',
    'ja': 'c5ccb3b730af3f3f8a9d86be0039caf5aa1e16bc0b2233b4e354abc75fc70654',
    'ko': '70d5ac993f0672e5917b1ae81886a077b34525ccc9f4e32a4df4c18f28083f6f',
    'en': 'c402dd1feda411cc76a88fd22fdd95e2b5a845ac7141c57b20ccb7831334c3e3',
}


@functools.lru_cache(maxsize=5)
def localized_reference(lang):
    p = Path('/workspace/runs/interface-locale-gallery-r2') / (
        lang + '-dialog--budget-false-file--chart-true-ending--footer-3.png')
    assert sha(p.read_bytes()) == FROZEN[lang]
    return rgba(p, (1280, 800))


def paste(dst, src, rect):
    x, y, w, h = rect
    for row in range(y, y + h):
        start = (row * 1280 + x) * 4
        dst[start:start + w * 4] = src[start:start + w * 4]


def original_pixels(frame, pal):
    rows = [b''.join(bytes(pal[v] + [255]) * 4 for v in frame[y*320:(y+1)*320]) for y in range(200)]
    return b''.join(row * 4 for row in rows)


def localized_pixels(s, frame):
    frozen = localized_reference(s['language'])
    output = bytearray(expected_frame(frame, s['palette']))
    # Only previously confirmed, fixed text rectangles come from frozen art.
    for y in [22, 101]:
        for x in [1, 127]:
            paste(output, frozen, (264 + x*4, 140 + y*4, 68, 20))
    for index in range(6):
        paste(output, frozen, (28 + index*176, 40, 136, 68))
    refs, background, atlas = footer_references()
    digits_only = bytearray(atlas)
    for index in range(11, 18):
        for y in range(64):
            start = (((index//6)*64 + y)*384 + (index%6)*64)*4
            digits_only[start:start+64*4] = bytes(64*4)
    mask, texts = 0, ['', '', '', '']
    for part, rect in enumerate(RECTS):
        values = decode(frame, refs, part)
        indices = sorted(set(footer_crop(refs[0], rect)) | ({15, 32} if part == 0 else {15}))
        matched = values is not None and sha(bytes(v for i in indices for v in s['palette'][i])) == PALETTES[part]
        if not matched:
            continue
        mask |= 1 << part
        if part == 0:
            texts[0] = values[0]
        else:
            texts[1:] = values
        pixels = expected_pixels(frame, s['palette'], part, values, background, digits_only)
        x, y, w, h = rect
        for row in range(h*4):
            start = ((y*4 + row)*1280 + x*4)*4
            output[start:start+w*16] = pixels[row*w*16:(row+1)*w*16]
        labels = ([(76, 708, 192, 56), (412, 708, 64, 56)] if part == 0 and values[0] else
                  [(1132, 704, 24, 28), (1212, 704, 48, 28), (1212, 736, 48, 28)] if part == 1 else [])
        for label in labels:
            paste(output, frozen, label)
    assert s['hd']['footer_mask'] == mask and s['hd']['footer_text'] == texts
    return bytes(output)


def audit(s, frame, pixels):
    assert len(frame) == 64000 and len(pixels) == 1280*800*4
    assert s['frame_index_sha256'] == sha(frame) and s['presentation_sha256'] == sha(pixels)
    assert not s['language_panel'] and not s['help_panel']
    base, _, _, palettes = reference()
    raw = crop(frame, 320, NATIVE)
    assert fixed(raw) == fixed(base), 'complete original chart frame'
    assert s['mode'] == 19 and s['dos_blocked']
    if not s['hd_enabled']:
        assert not s['hd']['chart_window'] and s['hd']['chart_reason'] == 'original'
        assert pixels == original_pixels(frame, s['palette']), 'complete original F12 pixels'
        return
    assert all(s['palette'][v] in [p[v] for p in palettes] for v in set(raw))
    h = s['hd']
    assert h['chart_window'] and h['chart_reason'] == h['reason'] == 'matched-chart-window'
    assert h['chart_data_sha256'] == sha(crop(raw, 145, DATA))
    assert h['font_labels'] == 6 and h['locale_reason'] == 'matched-interface' and h['localized_fields'] >= 4
    assert not any(h[k] for k in ['Painted', 'ui_icons', 'dialog', 'panel', 'chrome_mask', 'file_dialog', 'budget', 'ending_screen'])
    assert h['power_facility']['painted'] == h['infrastructure']['painted'] == 0
    expected = localized_pixels(s, frame)
    assert pixels == expected, ('full localized pixels', next((i for i, (a, b) in enumerate(zip(pixels, expected)) if a != b), None))


def load(path):
    raw = path.read_bytes()
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        s = json.loads(z.read('status.json'))
        frame = z.read('frame-index.bin')
        pixels = rgba_from_bytes(z.read('presentation.png'))
        assert rgba_from_bytes(z.read('frame.png')) == bytes(v for c in frame for v in s['palette'][c]+[255])
    return s, frame, pixels


def rgba_from_bytes(data):
    import subprocess
    return subprocess.run(['convert', 'png:-', '-depth', '8', 'rgba:-'], input=data,
                          check=True, stdout=subprocess.PIPE).stdout


def negative_controls(s, frame, pixels):
    result = []
    positions = {'frame': (264, 140), 'chart-text': (268, 228), 'data': (344, 220),
                 'menu-text': (28, 40), 'footer-text': (1132, 704), 'outside': (0, 0)}
    for fault in ['positive', 'unused-palette-positive', *positions, 'source', 'raw-data', 'family', 'data-sha', 'language', 'original-mode']:
        state, source, shown = copy.deepcopy(s), bytearray(frame), bytearray(pixels)
        if fault in positions:
            x, y = positions[fault]
            shown[(y*1280+x)*4] ^= 1
        elif fault == 'unused-palette-positive':
            state['palette'][next(i for i in range(256) if i not in set(frame))][0] ^= 1
        elif fault == 'source':
            source[35*320+66] ^= 128
        elif fault == 'raw-data':
            at = 55*320+86
            source[at] = 15 if source[at] != 15 else 0
            state['hd']['chart_data_sha256'] = sha(crop(crop(source, 320, NATIVE), 145, DATA))
        elif fault == 'family':
            state['hd']['chart_window'] = False
        elif fault == 'data-sha':
            state['hd']['chart_data_sha256'] = '0'*64
        elif fault == 'language':
            state['language'] = 'en' if s['language'] != 'en' else 'zh-Hant'
        elif fault == 'original-mode':
            state['hd_enabled'] = False
            state['hd']['chart_window'], state['hd']['chart_reason'] = False, 'original'
        state['frame_index_sha256'], state['presentation_sha256'] = sha(source), sha(shown)
        error = ''
        try:
            audit(state, bytes(source), bytes(shown))
        except AssertionError as e:
            error = str(e) or 'AssertionError'
        positive = fault.endswith('positive')
        assert bool(error) is not positive, (fault, error)
        result.append({'fault': fault, 'positive': positive, 'rejected': bool(error), 'affected_hashes_recomputed': True})
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    assert not args.out.exists()
    report, first = [], None
    for p in sorted((args.run/'gui').glob('chart-*-capture.zip')):
        s, frame, pixels = load(p)
        audit(s, frame, pixels)
        report.append({'receipt': p.name, 'receipt_sha256': sha(p.read_bytes()),
                       'language': s['language'], 'hd_enabled': s['hd_enabled'], 'complete_pixels': True})
        if first is None and s['hd_enabled']:
            first = s, frame, pixels
    assert len(report) >= 30 and {r['language'] for r in report} == set(FROZEN)
    result = {'issue': 54, 'receipts': report, 'frozen_localization_png_sha256': FROZEN,
              'negative_controls': negative_controls(*first),
              'scope': '原始框架與資料重算；翻譯文字使用本次開工前固定 Noto 圖，只取已確認的文字矩形。完整整幀核對，不使用目前呈現器。'}
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print('PASS:', len(report), 'complete localized chart frames;', len(result['negative_controls']), 'controls')


if __name__ == '__main__':
    main()
