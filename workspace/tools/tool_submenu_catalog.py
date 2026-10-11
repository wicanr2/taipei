"""#31：完整重建五工具子選單，只接受正常收據中實見的十八個狀態。"""
import argparse
import json
import struct
import zipfile
from pathlib import Path

from full_asset_catalog import image
from hd_source_audit import sha

ROM_SHA = '0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29'
# 字模索引及座標由正常像素逐點比對；索引不是遊戲規則。
SCENES = [
    (2, [228, 29, 37, 35], [[10, 11], [12, 13]]),
    (5, [212, 52, 53, 35], [[14, 15, 16], [17, 18, 19]]),
    (9, [196, 124, 69, 35], [[20, 21, 22, 23], [24, 25, 22, 23]]),
    (10, [18, 37, 235, 132], [[56, 57, 58, 59, 60], [61, 62, 58, 59, 63],
        [64, 65, 66, 67, 68], [69, 69, 70, 58, 59, 71], [72, 73, 74, 73, 60],
        [75, 76, 77, 78], [79, 73, 80, 73, 81], [82, 73, 73, 73, 83],
        [84, 73, 67, 73, 78], [85, 86, 87, 88, 81]]),
    (11, [196, 124, 69, 35], [[26, 27, 28, 29], [30, 31, 28, 29]]),
]


def geometry(glyphs):
    result = []
    for tool, rect, options in SCENES:
        cells, buttons = [], []
        for option, indices in enumerate(options):
            x, y = ((16+110*(option//5), 9+25*(option % 5)) if tool == 10 else (2, 2+15*option))
            if tool == 10:
                buttons.append({'rect': [10+110*(option//5), 5+25*(option % 5), 104, 21], 'art': 'menu-blue-b-v1.png'})
            for pos, index in enumerate(indices):
                g = glyphs[index]
                cells.append({'x': x+16*pos, 'y': y, 'option': option, 'index': index,
                              'text': g['encoded_cp950'], 'size': 52})
        result.append({'id': f'tool-{tool:02d}', 'tool': tool, 'native': rect,
                       'background': 'city-chrome-lime-v1.png' if tool == 10 else 'menu-blue-b-v1.png',
                       'background_border': 8, 'buttons': buttons, 'cells': cells})
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--original', type=Path, required=True)
    ap.add_argument('--receipts', type=Path, required=True)
    ap.add_argument('--glyphs', type=Path, required=True)
    ap.add_argument('--materials', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    raw = (args.original/'RS201.ROM').read_bytes()
    assert sha(raw) == ROM_SHA
    glyphs = json.loads(args.glyphs.read_text())['glyphs']
    assert len(glyphs) == 402
    for index, g in enumerate(glyphs):
        offset = 936898+6+index*30
        data = raw[offset:offset+30]
        code = raw[948964+2+index*2:948964+4+index*2]
        assert g['index'] == index and g['glyph_file_offset'] == offset
        assert g['rows_15bit'] == [int.from_bytes(data[r*2:r*2+2], 'big') >> 1 for r in range(15)]
        assert g['encoded_cp950'] == code.decode('cp950') and g['glyph_sha256'] == sha(data)
    scenes = geometry(glyphs)
    receipts = []
    for path in sorted(args.receipts.rglob('*-capture.zip')):
        with zipfile.ZipFile(path) as z:
            s, frame = json.loads(z.read('status.json')), z.read('frame-index.bin')
        assert len(frame) == 64000 and sha(frame) == s['frame_index_sha256']
        receipts.append((str(path.relative_to(args.receipts)), s, frame))
    states, evidence, negatives = [], [], 0
    for scene in scenes:
        x, y, w, h = scene['native']
        base = bytes([3])*(w*h)
        if scene['tool'] == 10:
            off, n = struct.unpack_from('<IH', raw, 18+19*16)
            bw, bh, base, _ = image(raw[off:off+n])
            assert (bw, bh) == (w, h)
        options = len(SCENES[[v[0] for v in SCENES].index(scene['tool'])][2])
        for selected in range(options):
            wanted = bytearray(base)
            for c in scene['cells']:
                for yy, row in enumerate(glyphs[c['index']]['rows_15bit'][:14]):
                    for xx in range(15):
                        if row & (1 << (14-xx)):
                            at = (c['y']+yy)*w+c['x']+xx
                            assert base[at] == (9 if scene['tool'] == 10 else 3)
                            wanted[at] = 55 if c['option'] == selected else 15
            matches = []
            indices = sorted(set(wanted))
            color_sha = None
            for name, s, frame in receipts:
                box = b''.join(frame[yy*320+x:yy*320+x+w] for yy in range(y, y+h))
                if box != wanted:
                    continue
                colors = sha(bytes(v for i in indices for v in s['palette'][i]))
                assert color_sha in [None, colors]
                color_sha = colors
                matches.append(name)
                # 空白背景、文字及完整矩形邊角都不能略過。
                for at in [0, len(box)-1, next(i for i, v in enumerate(box) if v == 55)]:
                    bad = bytearray(box); bad[at] ^= 1
                    assert bad != wanted
                    negatives += 1
            assert matches, (scene['id'], selected, '沒有完整正常來源')
            states.append({'id': scene['id'], 'selection': selected, 'native': scene['native'],
                           'source_sha256': sha(wanted), 'palette_indices': indices,
                           'palette_sha256': color_sha})
            evidence.append({'id': scene['id'], 'selection': selected, 'receipts': matches,
                             'full_background_and_glyphs_equal': True})
    layout = {'schema': 1, 'scenes': scenes, 'art_sha256': {
        name: sha((args.materials/name).read_bytes()) for name in ['city-chrome-lime-v1.png', 'menu-blue-b-v1.png']}}
    assert layout['art_sha256'] == {
        'city-chrome-lime-v1.png': '73948266299d3a892614da7f13a5ca67cdd097867348f16c5b0539a4440c83c7',
        'menu-blue-b-v1.png': 'eeb1aa620c179a7fa0233bdfc9d9ad6abf8719d36f1ad05dc93c84343a164ea9'}
    layout_raw = (json.dumps(layout, ensure_ascii=False, indent=2)+'\n').encode()
    (args.materials/'tool-menu-layout-v1.json').write_bytes(layout_raw)
    result = {'schema': 1, 'rom_sha256': ROM_SHA, 'layout_sha256': sha(layout_raw),
              'address_space': 'RS201.ROM file offsets; zero-based member/glyph indices',
              'font_members': [57, 58], 'large_panel': {'member': 19, 'offset': 159578, 'bytes': 7386},
              'small_panel_background': {'index': 3, 'evidence': 'confirmed visible complete rectangle; drawing implementation not inferred'},
              'states': states, 'evidence': evidence, 'negative_controls': negatives,
              'scope': '正常 GUI 可見來源；不推定模擬規則或未見字串'}
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'states': len(states), 'negative_controls': negatives,
                      'layout_sha256': sha(layout_raw), 'sources_sha256': sha(args.out.read_bytes())}))


if __name__ == '__main__':
    main()
