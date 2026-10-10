#!/usr/bin/env python3
"""#5：實際單幀收據的 HD 呈現條件研究，不改原版或接產品路徑。"""
import argparse
import hashlib
import json
import struct
import zipfile
from pathlib import Path

from rom_catalog import library

ROM_SHA = '0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29'
UI_SHA = 'b9b27e2010b2d581cb55c349b5944492ea0077104e15126236fc50b859b51eda'
PAL_SHA = '9bd7a6f66fe9e1da47ea3360ffbd0e114616d466034ff8b999529ae38afe6b0b'
MATERIAL_INDICES = tuple(range(103,108)) + tuple(range(144,148)) + tuple(range(201,205))

def sha(data):
    return hashlib.sha256(data).hexdigest()

def read_bundle(path):
    with zipfile.ZipFile(path) as z:
        state = json.loads(z.read('status.json'))
        px = z.read('frame-index.bin')
    assert len(px) == 64000 and sha(px) == state['frame_index_sha256']
    return state, px

def presentation_allowed(state, px):
    if state.get('mode') != 19 or state.get('dos_blocked') is not False:
        return False
    palette = state['palette']
    if sha(bytes(v for i in MATERIAL_INDICES for v in palette[i])) != PAL_SHA:
        return False
    top = b''.join(px[y*320:y*320+270] for y in range(33))
    return sha(top) == UI_SHA

def counts(state, px, sources):
    allowed = presentation_allowed(state, px)
    matched = eligible = 0
    cells = []
    for y in range(34,169,9):
        for x in range(5,266,9):
            tile = b''.join(px[(y+r)*320+x:(y+r)*320+x+9] for r in range(9))
            if tile in sources:
                matched += 1
                if all(i in MATERIAL_INDICES for i in tile):
                    eligible += 1
                    cells.append((x,y))
    return {'allowed':allowed,'matched':matched,'eligible':eligible,
            'would_paint':eligible if allowed else 0,
            'fallback':435-(eligible if allowed else 0)}, cells

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--original',type=Path,required=True)
    ap.add_argument('--receipts',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args = ap.parse_args()
    rom = (args.original/'RS201.ROM').read_bytes()
    assert sha(rom) == ROM_SHA
    off,n = struct.unpack_from('<IH',rom,18+59*16)
    parsed = library(rom[off:off+n])
    assert parsed is not None
    _,images = parsed
    assert len(images) == 135 and all((w,h)==(9,9) for w,h,_ in images)
    sources = {pixels for _,_,pixels in images}
    records = []
    for path in sorted(args.receipts.rglob('*-capture.zip')):
        state,px = read_bundle(path)
        record,_ = counts(state,px,sources)
        records.append({'capture':str(path.relative_to(args.receipts)),
                        'native_sha256':sha(px),'steps':state['steps'],**record})
    assert records
    base,px = read_bundle(args.receipts/'city-map-capture.zip')
    normal,cells = counts(base,px,sources)
    assert normal['allowed'] and normal['would_paint'] > 400
    changed_palette = json.loads(json.dumps(base))
    changed_palette['palette'][144][0] ^= 1
    assert counts(changed_palette,px,sources)[0]['would_paint'] == 0
    blocked = dict(base,dos_blocked=True)
    assert counts(blocked,px,sources)[0]['would_paint'] == 0
    wrong_source = bytearray(px)
    x,y = cells[0]
    wrong_source[y*320+x] = 255
    wrong,_ = counts(base,wrong_source,sources)
    assert wrong['would_paint'] == normal['would_paint']-1
    for record in records:
        if any(token in record['capture'] for token in ['file-menu','save-dialog','save-name','quit-menu','quit-confirm']):
            assert record['would_paint'] == 0, record
    result = {'prototype':True,'rom_sha256':ROM_SHA,'ui_sha256':UI_SHA,'material_palette_sha256':PAL_SHA,
              'negative_palette':True,'negative_blocking_input':True,'negative_source':True,'captures':records}
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'captures':len(records),'normal':normal,'negative_controls':True}))

if __name__ == '__main__':
    main()
