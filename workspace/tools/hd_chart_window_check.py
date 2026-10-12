"""#48／029：直接讀原版與 READY 前參考，獨立核對圖表整幀。"""
import argparse
import functools
import json
import struct
import zipfile
from pathlib import Path

from chart_window_source_check import crop, fixed, NATIVE, DATA
from full_asset_catalog import image, sha
from hd_file_dialogs_check import rgba


@functools.lru_cache(maxsize=1)
def reference():
    root = Path('/workspace/prototypes/hd-style')
    rom = Path('/orig/RS201.ROM').read_bytes()
    assert sha(rom) == '0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29'
    offset, size = struct.unpack_from('<IH', rom, 18+4*16)
    assert (offset,size) == (27667,9294)
    decoded = image(rom[offset:offset+size])
    assert decoded is not None and decoded[:2] == (145,127)
    assert sha(decoded[2]) == 'c3b7fa8fdc7246e48cd051d375cf36566c3f01c69e33f7eb9ac4bcd1c2ffc961'
    raw = (root/'chart-windows-v2/0/manifest.json').read_bytes()
    assert sha(raw) == '511ffcec3a1a125b6ca4878e8d384624e2772f9500c47c7e6db1a2abce0ebd45'
    meta = json.loads(raw)
    texture_path = root/'city-chrome-gray-v1.png'
    assert sha(texture_path.read_bytes()) == meta['texture_sha256']
    texture = rgba(texture_path,(944,528))
    proto = rgba(root/'chart-windows-v2/0/presentation.png',(1280,800))
    assert sha(proto) == meta['presentation_rgba_sha256']
    raw = Path('/workspace/runs/chart-windows-native/palette-audit-r1.json').read_bytes()
    assert sha(raw) == '392dc069f4c39632d14c3991c7f2b0e4f11e5dcf6084b397b744f39caad17473'
    palettes = [p['rgb'] for p in json.loads(raw)['palettes']]
    return decoded[2], proto, texture, palettes


def expected_frame(frame, pal):
    _, proto, texture, _ = reference()
    native = b''.join(bytes(pal[c]+[255])*4 for c in frame)
    native = b''.join(native[y*5120:(y+1)*5120]*4 for y in range(200))
    expected = bytearray(native)
    for y in range(508):
        for x in range(580):
            at = ((140+y)*1280+264+x)*4
            if 80 <= x < 500 and 80 <= y < 436:
                v = frame[(35+y//4)*320+66+x//4]
                grain = texture[((32+y%464)*944+32+x%880)*4]//8-18
                expected[at:at+4] = bytes([max(0,min(255,c+grain)) for c in pal[v]]+[255])
            else:
                expected[at:at+4] = proto[at:at+4]
    return bytes(expected)


def audit_chart(s, frame, pixels):
    h = s['hd']
    if 'chart_window' not in h:
        return False
    base, _, _, palettes = reference()
    raw = crop(frame,320,NATIVE)
    known = fixed(raw) == fixed(base)
    palette_ok = all(s['palette'][v] in [p[v] for p in palettes] for v in set(raw))
    reason = 'scene-fallback'
    if not s['hd_enabled']:
        reason = 'original'
    elif known and s['mode'] == 19:
        reason = ('chart-unverified-phase' if not s['dos_blocked'] else
                  'chart-palette-mismatch' if not palette_ok else 'matched-chart-window')
    assert h['chart_reason'] == reason
    active = known and s['mode'] == 19 and s['hd_enabled'] and s['dos_blocked'] and palette_ok
    if active:
        assert h['chart_window'] and h['reason'] == reason
        assert h['chart_data_sha256'] == sha(crop(raw,145,DATA))
        assert not any(h[k] for k in ['Painted','font_labels','ui_icons','dialog','panel',
                                      'chrome_mask','footer_mask','file_dialog','budget','ending_screen'])
        assert h['power_facility']['painted'] == h['infrastructure']['painted'] == 0
        assert pixels == expected_frame(frame,s['palette'])
    else:
        assert not h['chart_window'] and h['chart_data_sha256'] == ''
        if known:
            native = b''.join(bytes(s['palette'][c]+[255])*4 for c in frame)
            native = b''.join(native[y*5120:(y+1)*5120]*4 for y in range(200))
            assert pixels == native
    return known


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--receipts',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args = ap.parse_args()
    assert not args.out.exists()
    from hd_scroll_check import audit_bundle, source59
    sources = source59(Path('/orig'))
    count = painted = 0
    data = set()
    for path in sorted(args.receipts.rglob('*-capture.zip')):
        s, _, _, _, _ = audit_bundle(path,sources)
        count += 1
        if s['hd'].get('chart_window'):
            painted += 1
            data.add(s['hd']['chart_data_sha256'])
    assert count and painted >= 12
    result = {'issue':48,'receipts':count,'painted_receipts':painted,'data_sha256':sorted(data),
        'complete_pixels_and_fallback':True,'scope':'正常原子收據整幀獨立核對；固定原版狀態另驗'}
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))


if __name__ == '__main__':
    main()
