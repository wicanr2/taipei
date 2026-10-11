"""#31：固定 ROM 底圖、正常選取畫面與原文位置的完整來源審查。"""
import argparse
import json
import struct
import zipfile
from pathlib import Path

from full_asset_catalog import image
from hd_source_audit import sha


def crop(frame, rect):
    x, y, w, h = rect
    return b''.join(frame[(y+r)*320+x:(y+r)*320+x+w] for r in range(h))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--original', type=Path, required=True)
    ap.add_argument('--receipts', type=Path, required=True)
    ap.add_argument('--layout', type=Path, required=True)
    ap.add_argument('--glyphs', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    raw = (args.original/'RS201.ROM').read_bytes()
    assert sha(raw) == '0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29'
    layout = json.loads(args.layout.read_text())
    glyphs = {g['encoded_cp950']: g['rows_15bit'][:14]
              for g in json.loads(args.glyphs.read_text())['glyphs']}
    states, evidence, rejected, glyph_count = [], [], 0, 0
    for scene in layout['scenes']:
        off, n = struct.unpack_from('<IH', raw, 18+scene['member']*16)
        w, h, base, encoding = image(raw[off:off+n])
        assert [w, h] == scene['native'][2:]
        text_pixels = { (c['y']+dy)*w+c['x']+dx for c in scene['cells'] if c['option'] >= 0
                       for dy in range(14) for dx in range(15) }
        background = 131 if scene['id'] == 'main' else 38
        def matches(box):
            return len(box) == len(base) and all(a == b or
                i in text_pixels and a == background and b in [15, 55]
                for i, (a, b) in enumerate(zip(base, box)))
        found = {}
        for path in sorted(args.receipts.glob('*-capture.zip')):
            with zipfile.ZipFile(path) as z:
                s = json.loads(z.read('status.json'))
                f = z.read('frame-index.bin')
            assert len(f) == 64000 and sha(f) == s['frame_index_sha256']
            box = crop(f, scene['native'])
            if not matches(box):
                continue
            option_colors = {}
            for c in scene['cells']:
                if c['option'] < 0:
                    continue
                rows = glyphs[c['text']]
                colors = {box[(c['y']+y)*w+c['x']+x] for y, row in enumerate(rows)
                          for x in range(15) if row & (1 << (14-x))}
                assert len(colors) == 1 and next(iter(colors)) in [15, 55], (scene['id'], c)
                fg = next(iter(colors))
                painted_rows = [sum(1 << (14-x) for x in range(15)
                                    if box[(c['y']+y)*w+c['x']+x] == fg) for y in range(14)]
                assert painted_rows == rows, (scene['id'], c, '原文墨跡失配')
                option_colors.setdefault(c['option'], set()).add(fg)
            assert all(len(colors) == 1 for colors in option_colors.values())
            selected = [i for i, colors in option_colors.items() if scene['selected_index'] in colors]
            assert len(selected) == 1
            selected = selected[0]
            indices = sorted(set(base) | set(box))
            record = {'id': scene['id'], 'selection': selected, 'native': scene['native'],
                      'source_sha256': sha(box), 'palette_indices': indices,
                      'palette_sha256': sha(bytes(v for i in indices for v in s['palette'][i]))}
            if selected in found:
                assert record == found[selected]['record'], (scene['id'], selected, '同狀態來源改變')
                found[selected]['receipts'].append(path.name)
            else:
                found[selected] = {'record': record, 'receipts': [path.name],
                                  'frame_sha256': sha(f), 'steps': s['steps']}
            corrupt = bytearray(box)
            corrupt[0] ^= 1
            assert not matches(corrupt)
            rejected += 1
        want = {'main': 3, 'city': 7, 'difficulty': 3}[scene['id']]
        assert set(found) == set(range(want)), (scene['id'], sorted(found), '缺少正常選取狀態')
        states.extend(found[i]['record'] for i in range(want))
        glyph_count += sum(c['option'] >= 0 for c in scene['cells'])
        evidence.append({'id': scene['id'], 'member': scene['member'], 'file_offset': off,
                         'bytes': n, 'base_sha256': sha(base), 'encoding': encoding,
                         'all_other_pixels_exact': True, 'options': [found[i] for i in range(want)]})
    result = {'schema': 1, 'rom_sha256': sha(raw), 'layout_sha256': sha(args.layout.read_bytes()),
              'address_space': 'RS201.ROM file offsets; zero-based member indices',
              'states': states, 'evidence': evidence, 'confirmed_option_glyphs': glyph_count,
              'negative_corrupt_source_rejected': rejected,
              'limits': '完整來源與選取顏色；控制流只限正常收據，不推測未見取消語意'}
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'states': len(states), 'glyphs': glyph_count, 'negative_controls': rejected,
                      'scenes': [(e['id'], len(e['options'])) for e in evidence]}, ensure_ascii=False))


if __name__ == '__main__':
    main()
