"""#29：從原版完整來源重算圖示遮罩，核對固定 atlas 與選取外框。"""
import argparse
import collections
import json
import struct
import subprocess
from pathlib import Path

from full_asset_catalog import image
from hd_scroll_check import audit_bundle, source59
from hd_source_audit import scene, sha

ATLAS_SHA = '9ad97735f45cab2c968e23d8f1d6924c6b1937854fa4cda1c1c7a5ee90a089ab'
PALETTE_SHA = '39592c7fa30a9605b79cc18217f320484e16e3d301c6c8a2a4e992951b32a759'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--original', type=Path, required=True)
    ap.add_argument('--materials', type=Path, required=True)
    ap.add_argument('--receipts', type=Path, required=True)
    args = ap.parse_args()
    sources = source59(args.original)  # 此函式另驗固定 ROM SHA-256。
    raw = (args.original/'RS201.ROM').read_bytes()
    off, n = struct.unpack_from('<IH', raw, 34)
    w, h, base, encoding = image(raw[off:off+n])
    assert (w, h) == (320, 200)
    assert sha(base) == 'a35e8372b6dbd661444299f3241ad36634291b1c6657e6feacf8189c53e04dd7'
    indices = sorted({base[(5+24*(i//2)+r)*320+274+23*(i % 2)+c]
                      for i in range(14) for r in range(20) for c in range(20)})
    assert len(indices) == 88
    atlas = args.materials/'city-icons-b-v1.png'
    assert sha(atlas.read_bytes()) == ATLAS_SHA
    rgba_atlas = subprocess.check_output(['convert', str(atlas), '-depth', '8', 'rgba:-'])
    assert len(rgba_atlas) == 320*320*4
    counts = collections.Counter()
    samples = []
    for path in sorted(args.receipts.rglob('*-capture.zip')):
        s, frame, grid, rgba, sample = audit_bundle(path, sources)
        # 完整選單已由 audit_bundle 依獨立來源及固定參考驗全幀。
        if s['hd'].get('panel') or s['hd'].get('file_dialog'):
            assert s['hd']['ui_icons'] == s['hd']['ui_icon_mask'] == 0
            sample.update(receipt=str(path.relative_to(args.receipts)), icons=0, icon_mask=0)
            samples.append(sample)
            counts[0] += 1
            continue
        origin = s.get('map_origin', {})
        active = (s['hd_enabled'] and scene(s, frame) and origin.get('Valid')
                  and 0 <= origin['X'] <= 76 and 0 <= origin['Y'] <= 74
                  and sha(bytes(c for i in indices for c in s['palette'][i])) == PALETTE_SHA)
        mask = 0
        for i in range(14):
            x, y = 274+23*(i % 2), 5+24*(i//2)
            matched = active and all(frame[(y+r)*320+x:(y+r)*320+x+20]
                                     == base[(y+r)*320+x:(y+r)*320+x+20] for r in range(20))
            if matched:
                mask |= 1 << i
            # 內部逐像素比 atlas；019 覆繪外框已獨立核對，其餘外框保留原版。
            for yy in range(y*4-4, (y+20)*4+4):
                for xx in range(x*4-4, (x+20)*4+4):
                    # 新外框已由 audit_bundle 獨立驗完整來源與固定 rings 參考。
                    if s['hd'].get('chrome_ring_mask', 0)&(1 << i) and not (x*4 <= xx < (x+20)*4 and y*4 <= yy < (y+20)*4):
                        continue
                    if matched and x*4 <= xx < (x+20)*4 and y*4 <= yy < (y+20)*4:
                        ax, ay = (i % 4)*80+xx-x*4, (i//4)*80+yy-y*4
                        at = (ay*320+ax)*4
                        want = rgba_atlas[at:at+4]
                    else:
                        want = bytes(s['palette'][frame[(yy//4)*320+xx//4]]+[255])
                    at = (yy*1280+xx)*4
                    assert rgba[at:at+4] == want, (path.name, i, xx, yy, '圖示或原版外框失配')
        assert s['hd']['ui_icon_mask'] == mask, (path.name, '原版來源重算遮罩不符')
        assert s['hd']['ui_icons'] == mask.bit_count(), (path.name, '圖示數不符來源')
        sample.update(receipt=str(path.relative_to(args.receipts)), icons=mask.bit_count(), icon_mask=mask)
        counts[mask.bit_count()] += 1
        samples.append(sample)
    assert counts[14] > 0 and counts[0] > 0, '缺少真正 HD 圖示或回退收據'
    assert any(s['receipt'] == 'reload/load-accept-capture.zip' and s['icons'] == 14 for s in samples)
    result = {'scope': '十四個工具圖示內部；非完整介面或全部圖片完成',
              'atlas_sha256': ATLAS_SHA, 'bundles': len(samples), 'icon_counts': dict(counts),
              'source_mask_independently_matched': True, 'atlas_pixels_equal': True,
              'selection_borders_independently_verified': True, 'cold_load_restored': True, 'samples': samples}
    (args.receipts/'icons-verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'samples'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
