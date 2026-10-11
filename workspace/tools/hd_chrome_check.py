"""#29：獨立重算六部分、42 外框來源，核對固定參考及回退像素。"""
import argparse
import functools
import json
import struct
import subprocess
import zipfile
from pathlib import Path

from full_asset_catalog import image
from hd_source_audit import scene, sha

FRAME_SHA = 'd3391282c3fde64b60b64fe59ba756537c4bb60b3766a161106e5432b4e396d6'
RINGS_SHA = '8b4c017f525d6b947e7fc446132cef79af053f1916e6d36ea6a8b2d746cc9fc0'
PAL = ['812a09c150893419cfdbd5735fdc7ae1894d9269cb700b13aaec67c3145796bd',
       '72cc9a45a3dcc4f0b4203eb8dfff2aa331815a7b9e440b8f5f5c059743efe3ee',
       'de9cb1deaf78560bcbe58d5aa914357cc0deb3ac7109aa1f693e73b859e55961',
       'f18f4072f4d8deb4093618b7a70d385a8ad93db3b1a48db90d198b135e44e73f',
       '31c580975a1bf0e9163b077268235237dfc0dc5bf6dd464aa6e77c1d06eb6a57',
       '69fb4bfd6e40e197712e5ba31a22c8b338a0cf947c4818f4831a586423fb46b0']


@functools.lru_cache(maxsize=1)
def geometry():
    def box(x, y, w, h):
        return {row*320+col for row in range(y, y+h) for col in range(x, x+w)}
    slots = [box(273+23*(i % 2), 4+24*(i//2), 22, 22) for i in range(14)]
    return [sorted(p) for p in [box(0, 0, 270, 34), box(0, 34, 5, 135),
        box(266, 34, 4, 135), box(0, 169, 270, 5),
        box(270, 0, 50, 174)-set.union(*slots),
        box(0, 174, 320, 26)-box(7, 175, 224, 18)-box(244, 175, 71, 18)]]


@functools.lru_cache(maxsize=1)
def references():
    raw = Path('/orig/RS201.ROM').read_bytes()
    assert sha(raw) == '0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29'
    off, n = struct.unpack_from('<IH', raw, 34)
    w, h, base, _ = image(raw[off:off+n])
    assert (w, h) == (320, 200) and sha(base) == 'a35e8372b6dbd661444299f3241ad36634291b1c6657e6feacf8189c53e04dd7'
    arts = []
    for name, digest, size in [('frame.png', FRAME_SHA, 1280*800*4), ('rings.png', RINGS_SHA, 264*88*4)]:
        path = Path('/workspace/prototypes/hd-style/city-chrome-v1')/name
        assert sha(path.read_bytes()) == digest
        pixels = subprocess.check_output(['convert', str(path), '-depth', '8', 'rgba:-'])
        assert len(pixels) == size
        arts.append(pixels)
    return base, *arts


def covered_native(s):
    """只能在 audit_chrome 已驗來源與實際像素後，用來分派其他區外檢查。"""
    hd = s['hd']; points = set()
    for i, part in enumerate(geometry()):
        if hd.get('chrome_mask', 0) & (1 << i):
            points.update(part)
    for i in range(14):
        if hd.get('chrome_ring_mask', 0) & (1 << i):
            x, y = 273+23*(i % 2), 4+24*(i//2)
            points.update((y+yy)*320+x+xx for yy in range(22) for xx in range(22)
                          if xx in [0, 21] or yy in [0, 21])
    return points


def audit_chrome(s, frame, rgba):
    if 'chrome_mask' not in s['hd']:
        return None  # 保留舊版歷史收據，不能用來證明新框架完成。
    # 呼叫端 audit_bundle 已以完整來源、選取與固定參考驗證整個面板及區外。
    if s['hd'].get('panel') or s['hd'].get('dialog'):
        assert s['hd']['chrome_mask'] == s['hd']['chrome_ring_mask'] == 0
        assert s['hd']['chrome_parts'] == s['hd']['chrome_rings'] == 0
        return {'parts': 0, 'rings': 0, 'states': []}
    base, ref, rings = references()
    hd = s['hd']; origin = s.get('map_origin', {})
    active = (s['hd_enabled'] and scene(s, frame) and origin.get('Valid')
              and 0 <= origin['X'] <= 76 and 0 <= origin['Y'] <= 74)
    mask, ring_mask = 0, 0
    for i, points in enumerate(geometry()):
        indices = sorted({base[p] for p in points} | ({15} if i == 0 else set()))
        source = (sha(bytes(frame[p] for p in points)) == '8e292a6de746cfe2d55f3d3c1db3856f3b247c23512e471b2cbfd4f35272fa76'
                  if i == 0 else all(frame[p] == base[p] for p in points))
        matched = active and source and sha(bytes(c for j in indices for c in s['palette'][j])) == PAL[i]
        if matched:
            mask |= 1 << i
        for p in points:
            x, y = p % 320*4, p//320*4
            for yy in range(y, y+4):
                at = (yy*1280+x)*4
                label = (i == 0 and hd.get('font_labels') == 6 and 40 <= yy < 108
                         and any(28+j*176 <= x < 164+j*176 for j in range(6)))
                want = ref[at:at+16] if matched or label else bytes(s['palette'][frame[p]]+[255])*4
                assert rgba[at:at+16] == want, ('城市框架失配', i, x, yy)
    icon_indices = sorted({base[(5+24*(i//2)+r)*320+274+23*(i % 2)+c]
                           for i in range(14) for r in range(20) for c in range(20)})
    icon_pal = sha(bytes(v for i in icon_indices for v in s['palette'][i])) == '39592c7fa30a9605b79cc18217f320484e16e3d301c6c8a2a4e992951b32a759'
    states = []
    for i in range(14):
        x, y = 273+23*(i % 2), 4+24*(i//2)
        value = frame[y*320+x]
        variant = [15, 32, 186].index(value) if value in [15, 32, 186] else None
        matched = active and icon_pal and variant is not None
        if matched:
            matched = (s['palette'][value] == [[255, 255, 255], [255, 0, 0], [182, 0, 182]][variant]
                       and all(frame[(y+yy)*320+x+xx] == (value if xx in [0, 21] or yy in [0, 21] else base[(y+yy)*320+x+xx])
                               for yy in range(22) for xx in range(22)))
        if matched:
            ring_mask |= 1 << i; states.append([i, value])
        for yy in range(88):
            for xx in range(88):
                if 4 <= xx < 84 and 4 <= yy < 84:
                    continue
                at = ((y*4+yy)*1280+x*4+xx)*4
                src = (yy*264+(variant or 0)*88+xx)*4
                want = rings[src:src+4] if matched else bytes(s['palette'][frame[(y+yy//4)*320+x+xx//4]]+[255])
                assert rgba[at:at+4] == want, ('工具外框失配', i, xx, yy)
    assert hd['chrome_mask'] == mask and hd['chrome_parts'] == mask.bit_count(), '框架旗標不符完整來源'
    assert hd['chrome_ring_mask'] == ring_mask and hd['chrome_rings'] == ring_mask.bit_count(), '外框旗標不符完整來源'
    return {'parts': mask.bit_count(), 'rings': ring_mask.bit_count(), 'states': states}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--receipts', type=Path, required=True)
    ap.add_argument('--require-all-tools', action='store_true')
    args = ap.parse_args(); samples = []; states = set()
    from hd_scroll_check import audit_bundle, source59
    sources = source59(Path('/orig'))
    for path in sorted(args.receipts.rglob('*-capture.zip')):
        s, frame, _, rgba, _ = audit_bundle(path, sources)
        row = audit_chrome(s, frame, rgba)
        assert row is not None, '本批驗收不接受沒有框架欄位的舊版收據'
        states.update(tuple(v) for v in row['states'])
        samples.append({'receipt': str(path.relative_to(args.receipts)), 'blocked': s['dos_blocked'],
                        'native_frame_sha256': sha(frame), **row})
    if args.require_all_tools:
        assert states == {(i, value) for i in range(14) for value in [15, 32, 186]}, '缺少十四工具三種完整來源'
        for i in [2, 5, 9, 10, 11]:
            assert any(r['receipt'] == f'confirm-{i:02d}-capture.zip' and r['blocked'] and r['parts'] == r['rings'] == 0 for r in samples), '缺少子選單完整回退'
        original = next(r for r in samples if r['receipt'] == 'theme-original-capture.zip')
        hd = next(r for r in samples if r['receipt'] == 'theme-hd-capture.zip')
        assert original['parts'] == original['rings'] == 0 and hd['parts'] == 6 and hd['rings'] == 14
        assert original['native_frame_sha256'] == hd['native_frame_sha256'], 'F12 改變原版畫面'
    result = {'bundles': len(samples), 'observed_tool_states': sorted(states),
              'source_and_palette_recomputed': True, 'fixed_reference_pixels_equal': True,
              'fallback_parts_native': True, 'samples': samples}
    (args.receipts/'chrome-verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'samples'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
