"""#48：獨立重讀原版、六入口及全部原型像素，不呼叫產品呈現器。"""
import argparse
import json
import os
import struct
import zipfile
from pathlib import Path

from chart_window_source_check import crop, fixed, NATIVE, DATA
from full_asset_catalog import image, sha
from hd_file_dialogs_check import rgba

ART = 'fcdf6fc77b6fa84b7eacc12b335f6d30da7171d55628bc120194e1a9086ee7ae'
INK = '982ae4f59355973bb6230ae0f14bb260186dbbb01701d7824aca56cb83492057'


def rect(value):
    return [value['Min']['X'], value['Min']['Y'], value['Max']['X'], value['Max']['Y']]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--original', type=Path, required=True)
    ap.add_argument('--materials', type=Path, required=True)
    ap.add_argument('--receipts', type=Path, required=True)
    ap.add_argument('--prototype', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    assert not args.out.exists() and args.out.parent.stat().st_uid == os.getuid()
    rom = (args.original/'RS201.ROM').read_bytes()
    assert sha(rom) == '0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29'
    offset, size = struct.unpack_from('<IH', rom, 18+4*16)
    assert (offset, size) == (27667, 9294)
    decoded = image(rom[offset:offset+size])
    assert decoded is not None and decoded[:2] == (145, 127)
    base = decoded[2]
    assert sha(base) == 'c3b7fa8fdc7246e48cd051d375cf36566c3f01c69e33f7eb9ac4bcd1c2ffc961'
    menu_raw = (args.materials/'city-menu-sources-v1.json').read_bytes()
    assert sha(menu_raw) == 'eb98c1def205eb39e533f9646ad9336fafc7268559998e93e3a1ed1c7157f870'
    # 已完成 022 的六個完整來源雜湊，不從此原型的意圖名稱推定選取。
    menu_sha = ['05358ea206dac682b514b3db88f6ac663e98920c75f9f6ee428d84a98eac5068',
                'c858218f0909547a016125916612216a1e1e5b810b098db1d42be6b1eff98798',
                'd5849f168457683ff96ea0615d6886984bbb2dfc21e300192692320e9ea5859f',
                'fdc96470ec9b953c954c0c525e14071198c867dd6924f2cabbe6cd471693b103',
                '188c2a3f2ce694ef7924ee36c0b76925535e65c7e847fabe2940e16487c6da42',
                'cd33e67ebbf7de536c543cf7588965de23a5a168ea894567bded9b79cb089c0a']
    expected_inputs = {
        'fonts/NotoSansCJKtc-Regular.otf': 'dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4',
        'fonts/LICENSE': '6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2',
        'city-chrome-gray-v1.png': '6532e1daf962bb4abeed7a4c0a186a0ee9b606d4273d6d8ee5fce46e462efd37',
        'chart-frame-b-candidate-v1-generated.png': '109e7da267bed6a0b9dcb9baa0872bb3b5f1b0e1fa0ab1e8b532a82d99f41738',
    }
    for name, expected in expected_inputs.items():
        assert sha((args.materials/name).read_bytes()) == expected
    texture = rgba(args.materials/'city-chrome-gray-v1.png', (944, 528))
    results, palettes, used_palette = [], set(), {}
    for index in range(6):
        p = args.prototype/str(index)
        meta_raw = (p/'manifest.json').read_bytes()
        meta = json.loads(meta_raw)
        assert meta['issue'] == 48 and meta['stage'] == 'DRAFT' and meta['prototype']
        assert meta['native'] == list(NATIVE) and meta['data_local'] == list(DATA)
        path = args.receipts/f'chart-{index}-blocked-capture.zip'
        assert sha(path.read_bytes()) == meta['receipt_sha256']
        with zipfile.ZipFile(args.receipts/f'chart-{index}-chosen-capture.zip') as z:
            chosen = z.read('frame-index.bin')
        assert sha(crop(chosen, 320, (141, 35, 68, 94))) == menu_sha[index]
        with zipfile.ZipFile(path) as z:
            frame = z.read('frame-index.bin')
            s = json.loads(z.read('status.json'))
        assert s['mode'] == 19 and s['dos_blocked'] and not s['dos_exited']
        assert sha(frame) == s['frame_index_sha256'] == meta['source_frame_sha256']
        raw = crop(frame, 320, NATIVE)
        assert fixed(raw) == fixed(base)
        assert sha(raw) == meta['source_window_sha256']
        assert sha(crop(raw, 145, DATA)) == meta['source_data_sha256']
        pal = s['palette']
        palettes.add(sha(bytes(v for rgb in pal for v in rgb)))
        for color in set(raw):
            if color in used_palette:
                assert used_palette[color] == pal[color]
            used_palette[color] = pal[color]
        native = b''.join(bytes(pal[c]+[255]) for c in frame)
        assert rgba(p/'source.png', (320, 200)) == native
        scaled = b''.join(bytes(pal[c]+[255])*4 for c in frame)
        scaled = b''.join(scaled[y*5120:(y+1)*5120]*4 for y in range(200))
        assert sha((p/'frame-art-scaled.png').read_bytes()) == ART == meta['frame_art_scaled_png_sha256']
        assert sha((p/'text-ink.png').read_bytes()) == INK
        art = rgba(p/'frame-art-scaled.png', (580, 508))
        assert sha(art) == meta['frame_art_scaled_rgba_sha256']
        mask = rgba(p/'text-ink.png', (1280, 800))
        expected = bytearray(scaled)
        accepted = rejected = 0
        for y in range(508):
            for x in range(580):
                v = raw[y//4*145+x//4]
                rgb = pal[v]
                data = 80 <= x < 500 and 80 <= y < 436
                grain = texture[((32+y%464)*944+32+x%880)*4]//8-18
                amount = grain if data else grain*2 if 20 <= v <= 27 and len(set(rgb)) == 1 else grain
                out = bytes([max(0, min(255, c+amount)) for c in rgb]+[255])
                if not data and len(set(rgb)) == 1:
                    art_pixel = art[(y*580+x)*4:(y*580+x+1)*4]
                    if art_pixel[3] == 255 and max(art_pixel[:3])-min(art_pixel[:3]) <= 8:
                        out = art_pixel
                        accepted += 1
                    else:
                        rejected += 1
                at = ((140+y)*1280+264+x)*4
                expected[at:at+4] = out
        assert accepted == meta['frame_art_gray_pixels'] == 121432
        assert rejected == meta['frame_art_colored_pixel_fallback'] == 2120
        assert meta['generated_data_pixels_accepted'] == 0
        assert meta['font_size'] == 24 and meta['glyph_indices'] == {'A':34, 'I':42, 'M':46, 'N':47, 'X':57}
        for label, (text, x, y, count, ink) in zip(meta['labels'], [
                ('MAX',268,228,434,[279,229,325,247]), ('MAX',772,228,434,[783,229,829,247]),
                ('MIN',268,544,427,[282,545,322,563]), ('MIN',772,544,427,[786,545,826,563])]):
            safe = [x,y,x+68,y+20]
            assert label['text'] == text and rect(label['safe_rect']) == safe
            assert label['ink_pixels'] == count and rect(label['actual_ink_rect']) == ink
            points = [(xx, yy) for yy in range(y,y+20) for xx in range(x,x+68)
                      if mask[(yy*1280+xx)*4+3]]
            assert len(points) == count
            assert [min(xx for xx,yy in points), min(yy for xx,yy in points),
                    max(xx for xx,yy in points)+1,max(yy for xx,yy in points)+1] == ink
            # 三字各有墨跡，不只驗整串邊界。
            assert all(any(ink[0]+j*13 <= xx < ink[0]+(j+1)*13+8 for xx, yy in points) for j in range(3))
            for yy in range(y,y+20):
                for xx in range(x,x+68):
                    at = (yy*1280+xx)*4
                    expected[at:at+4] = bytes(pal[129]+[255])
        assert sum(a != 0 for a in mask[3::4]) == 1722
        assert rgba(p/'before-text.png', (1280,800)) == expected
        for at in range(0, len(expected), 4):
            alpha = mask[at+3]*257
            if alpha:
                for c,value in enumerate(pal[14]):
                    expected[at+c] = (expected[at+c]*257*(65535-alpha)+value*257*alpha)//65535 >> 8
        actual = rgba(p/'presentation.png', (1280,800))
        assert actual == bytes(expected) and sha(actual) == meta['presentation_rgba_sha256']
        comparison = rgba(p/'comparison.png', (2560,800))
        for y in range(800):
            assert comparison[y*10240:y*10240+5120] == scaled[y*5120:(y+1)*5120]
            assert comparison[y*10240+5120:(y+1)*10240] == actual[y*5120:(y+1)*5120]
        results.append({'selection':index,'manifest_sha256':sha(meta_raw),
            'presentation_rgba_sha256':sha(actual),'complete_pixels':1024000,
            'data_pixels':9345,'fixed_pixels':9070,'ink_pixels':1722,
            'generated_gray_pixels':accepted,'generated_colored_fallback':rejected})
    # 四個未用色盤項會正常變動，不將完整色盤相同誤當圖表的契約。
    assert palettes == {'67006a2d3081ebf55e24ac9a22a50abd94409a8072ccb34423d7e0893d6e238d',
                        'a4b7c0ddba0dcc9afde99e48a9fc5332390d5aede4039d8b97394b610ca8ec26'}
    assert len({r['presentation_rgba_sha256'] for r in results}) == 6
    result = {'issue':48,'prototype_only':True,'stage':'DRAFT', 'charts':results,
        'full_palette_sha256':sorted(palettes), 'used_palette':used_palette,
        'all_pixels_independently_equal':True,
        'data_positions_and_source_colors_preserved':True,'generated_data_pixels_accepted':0,
        'scope':'來源、六個實際選取及 B／Noto 原型；不代替正式 GUI、存退讀或原版狀態驗收'}
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))


if __name__ == '__main__':
    main()
