#!/usr/bin/env python3
"""#52：從原版字模獨立重建文字，不匯入產品呈現器。"""
import argparse
import hashlib
import json
import struct
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--original', type=Path, required=True)
    ap.add_argument('--audit', type=Path, required=True)
    args = ap.parse_args()
    rom = (args.original / 'RS201.ROM').read_bytes()
    assert hashlib.sha256(rom).hexdigest() == '0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29'
    members = {i: rom[o:o+n] for i in [56, 57, 58]
               for o, n in [struct.unpack_from('<IH', rom, 18+16*i)]}
    glyphs = {}
    for i in range(402):
        glyphs.setdefault(members[58][2+i*2:4+i*2], members[57][6+i*30:6+(i+1)*30])
    audit = json.loads((args.audit / 'audit.json').read_text())
    results = []
    for i, call in enumerate(audit['calls']):
        if call['EA'] not in [0x149b8, 0x14a92, 0x14ed2, 0x14d74]:
            continue
        code = bytes.fromhex(call['Code'])
        if not code or not code.decode('cp950').strip():
            continue
        chars = []
        at = 0
        while at < len(code):
            c = code[at:at+(1 if code[at] < 128 else 2)]
            chars.append(c)
            at += len(c)
        width = sum(6 if len(c) == 1 else 16 for c in chars)
        x, y = call['X'], call['Y']
        assert x+width <= 320 and y+14 <= 200, (i, x, y, width)
        backgrounds = [call['Background']] if call['EA'] != 0x149b8 else [0, 31]
        for file in sorted(args.audit.glob(f'call-{i:03d}-*.bin')):
            if 'before' in file.name:
                continue
            frame = file.read_bytes()
            found = []
            for background in backgrounds:
                if not 0 <= background < 256:
                    continue
                before = (args.audit / f'call-{i:03d}-before.bin').read_bytes()
                expected = bytearray(b''.join(before[(y+row)*320+x:(y+row)*320+x+width] for row in range(14))) if call['EA'] == 0x14ed2 else bytearray([background] * (width*14))
                dx = 0
                for count, c in enumerate([b'']+chars):
                    if c:
                        if len(c) == 1:
                            g = members[56][6+(c[0]-32)*7:6+(c[0]-31)*7]
                            w, h, stride, dy = 5, 7, 1, 4
                        else:
                            g = glyphs[c]
                            w, h, stride, dy = 15, 14, 2, 0
                        for gy in range(h):
                            for gx in range(w):
                                ink = bool(g[gy*stride+gx//8] & (128 >> (gx % 8)))
                                if ink or call['EA'] in [0x14ed2, 0x14d74]:
                                    expected[(dy+gy)*width+dx+gx] = call['Ink'] if ink else background
                        dx += 6 if len(c) == 1 else 16
                    actual = b''.join(frame[(y+row)*320+x:(y+row)*320+x+width] for row in range(14))
                    if actual == expected:
                        found.append({'characters': count, 'background': background})
            results.append({'file': file.name, 'call': i, 'matches': found})
    output = {'schema': 1, 'scope': 'exact original glyph rectangle reconstruction',
              'results': results, 'matched': sum(bool(r['matches']) for r in results),
              'unmatched': [r for r in results if not r['matches']]}
    (args.audit / 'source-check.json').write_text(json.dumps(output, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'matched': output['matched'], 'unmatched_count': len(output['unmatched']),
                      'unmatched_first': output['unmatched'][:3]}, ensure_ascii=False))


if __name__ == '__main__':
    main()
