"""#47／028：直接重讀原版與 READY 前固定底圖，核對整張實際畫面。"""
import argparse
import functools
import json
import struct
import zipfile
from pathlib import Path

from full_asset_catalog import image, sha
from hd_file_dialogs_check import rgba


@functools.lru_cache(maxsize=1)
def reference():
    root = Path('/workspace/prototypes/hd-style')
    raw = (root/'ending-scene-v1/manifest.json').read_bytes()
    assert sha(raw) == 'a86c26d3d8731d0d59042d7f461e3cf9468c32f431e127ecae5e1d421d357e41'
    proto = json.loads(raw)
    raw = Path('/workspace/runs/ending-scene-native/source-check.json').read_bytes()
    assert sha(raw) == proto['source_check_sha256']
    source = json.loads(raw)
    rom = Path('/orig/RS201.ROM').read_bytes()
    assert sha(rom) == '0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29'
    offset, size = struct.unpack_from('<IH', rom, 18+23*16)
    assert (offset, size) == (193647, 17587)
    decoded = image(rom[offset:offset+size])
    assert decoded is not None and decoded[:2] == (320, 200)
    assert sha(decoded[2]) == '0040b4374f37464862ae2f89da5bc897ddb7f53d539edd597cf8b2b6ff784ebd'
    path = root/'ending-scene-v1/presentation.png'
    assert sha(path.read_bytes()) == 'b37fddad8ea9cc3bbc505af3a3daad1f5cb59e86c213d98d12bbf279da81cfb0'
    return decoded[2], {int(k): v for k, v in source['used_palette'].items()}, rgba(path, (1280, 800))


def audit_ending(s, frame, pixels):
    hd = s['hd']
    if 'ending_screen' not in hd:
        return False
    source, palette, expected = reference()
    known = frame == source
    active = known and s['mode'] == 19 and s['hd_enabled'] and s['dos_blocked']
    palette_ok = all(s['palette'][i] == rgb for i, rgb in palette.items())
    reason = 'scene-fallback'
    if not s['hd_enabled']:
        reason = 'original'
    elif known and s['mode'] == 19:
        reason = ('ending-unverified-phase' if not s['dos_blocked'] else
                  'ending-palette-mismatch' if not palette_ok else 'matched-ending-screen')
    assert hd['ending_reason'] == reason
    if active and palette_ok:
        assert hd['ending_screen'] == 'achievement-base' and hd['reason'] == reason
        assert not any(hd[k] for k in ['Painted', 'font_labels', 'ui_icons', 'dialog', 'panel',
                                      'chrome_mask', 'footer_mask', 'file_dialog', 'budget'])
        assert hd['power_facility']['painted'] == hd['infrastructure']['painted'] == 0
        assert pixels == expected
    else:
        assert hd['ending_screen'] == ''
        if known:
            native = b''.join(bytes(s['palette'][p]+[255])*4 for p in frame)
            native = b''.join(native[y*5120:(y+1)*5120]*4 for y in range(200))
            assert pixels == native
    return known


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--receipts', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    assert not args.out.exists()
    from hd_scroll_check import audit_bundle, source59
    sources = source59(Path('/orig'))
    count = painted = 0
    for path in sorted(args.receipts.rglob('*-capture.zip')):
        s, _, _, _, _ = audit_bundle(path, sources)
        count += 1
        painted += bool(s['hd'].get('ending_screen'))
    assert count and painted >= 4
    result = {'issue': 47, 'receipts': count, 'painted_receipts': painted,
              'complete_pixels_and_fallback': True,
              'scope': '逐原子收據獨立核對，不代替固定時間原版狀態'}
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
