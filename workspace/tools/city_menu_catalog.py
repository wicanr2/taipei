"""#37：以原字模與完整邊框重建六個功能選單，衍生資料只留本機。"""
import argparse
import json
import struct
import zipfile
from pathlib import Path

from hd_source_audit import sha

ROM_SHA = '0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29'


def crop(px, rect):
    x, y, w, h = rect
    return b''.join(px[yy*320+x:yy*320+x+w] for yy in range(y, y+h))


def rectangle(frame):
    points = {y*320+x for y in range(29, 200) for x in range(320) if frame[y*320+x] == 3}
    boxes = []
    while points:
        at = points.pop(); todo, component = [at], [at]
        while todo:
            at = todo.pop()
            for other in [at-320, at+320, at-1, at+1]:
                if other in points:
                    points.remove(other); todo.append(other); component.append(other)
        if len(component) > 50:
            xs, ys = [v % 320 for v in component], [v//320 for v in component]
            boxes.append((len(component), [min(xs)-1, min(ys)-1, max(xs)-min(xs)+3, max(ys)-min(ys)+3]))
    return max(boxes)[1]


def background(w, h):
    p = bytearray([3])*(w*h)
    for x in range(w):
        p[x] = p[(h-1)*w+x] = 126 if x % 2 == 0 else 0
    for y in range(h-1):
        p[y*w] = p[y*w+w-1] = 126
    return p


def stamp(p, w, x, y, width, rows, foreground):
    for dy, row in enumerate(rows):
        for dx in range(width):
            if row & (1 << (width-1-dx)):
                p[(y+dy)*w+x+dx] = foreground


def main():
    ap = argparse.ArgumentParser()
    for name in ['original', 'receipts', 'materials', 'out']:
        ap.add_argument('--'+name, type=Path, required=True)
    ap.add_argument('--extra-receipts', type=Path, nargs='*', default=[])
    args = ap.parse_args(); rom = (args.original/'RS201.ROM').read_bytes()
    assert sha(rom) == ROM_SHA
    members = {}
    for i in [56, 57, 58]:
        off, n = struct.unpack_from('<IH', rom, 18+16*i)
        members[i] = (off, rom[off:off+n])
    off, font = members[57]; codes = members[58][1]
    assert struct.unpack_from('<HHH', font) == (15, 15, 30)
    glyphs = []
    for index in range(402):
        rows = tuple(int.from_bytes(font[6+index*30+y*2:8+index*30+y*2], 'big') >> 1 for y in range(14))
        glyphs.append({'index': index, 'text': codes[2+index*2:4+index*2].decode('cp950'),
                       'rows': rows, 'file_offset': off+6+index*30})
    ascii_off, ascii_font = members[56]
    assert struct.unpack_from('<HHH', ascii_font) == (5, 7, 7)
    receipts = []
    roots = [args.receipts]+args.extra_receipts
    for root_index, root in enumerate(roots):
        assert root.is_dir()
        prefix = '' if root_index == 0 else f'extra{root_index}/'
        for path in sorted(root.rglob('*-capture.zip')):
            with zipfile.ZipFile(path) as z:
                s, px = json.loads(z.read('status.json')), z.read('frame-index.bin')
            assert len(px) == 64000 and sha(px) == s['frame_index_sha256']
            receipts.append((prefix+str(path.relative_to(root)), s, px))
    scenes, states, evidence, negatives = [], [], [], 0
    for key in range(1, 7):
        root_index = next(i for i, root in enumerate(roots) if (root/f'f{key}/result.json').is_file())
        name = ('' if root_index == 0 else f'extra{root_index}/')+f'f{key}/open-capture.zip'
        _, _, frame = next(v for v in receipts if v[0] == name)
        x, y, w, h = rect = rectangle(frame)
        assert y == 35 and (h-4) % 15 == 0 and w >= 36, (key, rect)
        count = (h-4)//15
        observed = json.loads((roots[root_index]/f'f{key}/result.json').read_text())
        assert len(observed['distinct_down_frames']) == count, (key, count)
        native = crop(frame, rect); cells = []
        for option in range(count):
            cy = 2+15*option
            foreground = 55 if option == 0 else 15
            for cx in range(1, w-15):
                rows = tuple(sum((native[(cy+dy)*w+cx+dx] == foreground) << (14-dx) for dx in range(15)) for dy in range(14))
                found = [g for g in glyphs if any(g['rows']) and g['rows'] == rows]
                if not found:
                    continue
                assert len({g['text'] for g in found}) == 1, (key, option, cx, found)
                assert (cx-2) % 16 == 0, (key, option, cx, '字模位置不符完整原位，需審查')
                g = found[0]
                cells.append({'x': cx, 'y': cy, 'option': option, 'index': g['index'], 'text': g['text'],
                              'size': 52, 'member': 57, 'file_offset': g['file_offset'],
                              'glyph_aliases': [{'index': v['index'], 'file_offset': v['file_offset']} for v in found]})
        if key == 1:
            # ASCII 原版字模逐點證實；不把字形來源推定成 EXE 呼叫來源。
            assert [(c['index'], c['x']) for c in cells] == [(389, 2), (390, 18)]
            for i, ch in enumerate('DOS'):
                cells.append({'x': 40+i*6, 'y': 6, 'option': 0, 'index': ord(ch), 'text': ch,
                              'size': 28, 'member': 56, 'file_offset': ascii_off+6+(ord(ch)-32)*7})
        scene = {'id': f'city-f{key}', 'native': rect, 'options': count,
                 'background': 'menu-blue-b-v1.png', 'background_border': 8, 'buttons': [], 'cells': cells}
        for selection in range(count):
            wanted = background(w, h)
            for c in cells:
                if c['member'] == 57:
                    rows, width = glyphs[c['index']]['rows'], 15
                else:
                    at = 6+(c['index']-32)*7
                    rows, width = [v >> 3 for v in ascii_font[at:at+7]], 5
                stamp(wanted, w, c['x'], c['y'], width, rows, 55 if c['option'] == selection else 15)
            matches, palette = [], None
            indices = sorted(set(wanted))
            for receipt, s, px in receipts:
                if crop(px, rect) != wanted:
                    continue
                digest = sha(bytes(v for i in indices for v in s['palette'][i]))
                assert palette in [None, digest]
                palette = digest; matches.append(receipt)
                for at in [0, len(wanted)-1, next(i for i, v in enumerate(wanted) if v == 55)]:
                    changed = bytearray(wanted); changed[at] ^= 128
                    assert changed != crop(px, rect); negatives += 1
            assert matches, (scene['id'], selection, '完整來源不符，保留未知，不猜補')
            states.append({'id': scene['id'], 'selection': selection, 'native': rect,
                           'source_sha256': sha(wanted), 'palette_indices': indices, 'palette_sha256': palette})
            evidence.append({'id': scene['id'], 'selection': selection, 'receipts': matches})
        scenes.append(scene)
    art = 'menu-blue-b-v1.png'; art_sha = sha((args.materials/art).read_bytes())
    assert art_sha == 'eeb1aa620c179a7fa0233bdfc9d9ad6abf8719d36f1ad05dc93c84343a164ea9'
    layout = {'schema': 1, 'scenes': scenes, 'art_sha256': {art: art_sha}}
    raw = (json.dumps(layout, ensure_ascii=False, indent=2)+'\n').encode()
    catalog = {'schema': 1, 'rom_sha256': ROM_SHA, 'layout_sha256': sha(raw), 'states': states,
               'address_space': 'RS201.ROM file offsets; zero-based member/glyph indices; native pixels'}
    args.out.mkdir(parents=True, exist_ok=True)
    (args.materials/'city-menu-layout-v1.json').write_bytes(raw)
    (args.materials/'city-menu-sources-v1.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2)+'\n')
    (args.out/'catalog.json').write_text(json.dumps({'scenes': scenes, 'evidence': evidence,
        'receipt_roots': [str(root) for root in roots],
        'source_negatives': negatives, 'normal_bundles': len(receipts), 'rom_sha256': ROM_SHA}, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'scenes': [(s['id'], s['native'], s['options']) for s in scenes],
                      'states': len(states), 'source_negatives': negatives, 'normal_bundles': len(receipts)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
