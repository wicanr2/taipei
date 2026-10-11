"""#39：獨立來源重建、固定 HD 合成與全部區外核對。"""
import argparse
import functools
import json
import subprocess
import zipfile
from pathlib import Path

from budget_catalog import NATIVE, crop, decode_budget, references as source_references
from hd_file_dialogs_check import premultiply, rgba
from full_asset_catalog import sha


@functools.lru_cache(maxsize=1)
def references():
    root = Path('/workspace/prototypes/hd-style')
    raw = (root/'budget-v1/manifest.json').read_bytes()
    assert sha(raw) == 'f6a3052430ad3cc1cda5c737fb21ce6c73c13237e191e29cf0c92684553b9933'
    manifest = json.loads(raw)
    assert sha((root/'fonts/NotoSansCJKtc-Regular.otf').read_bytes()) == manifest['font_sha256']
    assert sha((root/'fonts/LICENSE').read_bytes()) == manifest['license_sha256']
    pictures = {}
    for name, size in [('panel.png',(940,528)),('glyphs.png',(288,56))]:
        path = root/'budget-v1'/name
        assert sha(path.read_bytes()) == manifest['images'][name]
        pictures[name] = rgba(path,size)
    raw = (root/'budget-v1/palette.json').read_bytes()
    assert sha(raw) == '92e63b93ecf043e77d45db64975aecae89116937314f3985972e864cb7f1f37b'
    return source_references(Path('/orig/RS201.ROM').read_bytes()), manifest, pictures, json.loads(raw)


def audit_budget(s, frame, pixels):
    # 舊收據沿用當時能力，不追加後來的完成旗標。
    if 'budget' not in s['hd']:
        return False
    refs, manifest, pictures, palette = references()
    decoded = decode_budget(frame,refs)
    h = s['hd']
    if not decoded or s['mode'] != 19:
        assert not h['budget'] and h['budget_text'] == ['']*11 and h['budget_colors'] == [0]*11 and h['budget_selection'] == -1
        return False
    palette_ok = all(s['palette'][i] == palette[i] for i in set(crop(frame,NATIVE)))
    enabled = s['hd_enabled'] and palette_ok
    assert h['budget'] is enabled
    assert h['budget_text'] == ([f['text'] for f in decoded['fields']] if enabled else ['']*11)
    assert h['budget_colors'] == ([f['color'] for f in decoded['fields']] if enabled else [0]*11)
    assert h['budget_selection'] == (decoded['selected_rows'][0] if enabled else -1)
    assert h['budget_reason'] == ('matched-budget' if enabled else ('budget-palette-mismatch' if s['hd_enabled'] else 'original'))
    if enabled:
        assert h['reason'] == 'matched-budget'
    assert all(h.get(k,0) == 0 for k in ['Painted','font_labels','ui_icons','chrome_mask','chrome_ring_mask','footer_mask'])
    assert all(not h.get(k) for k in ['panel','dialog','file_dialog'])
    expected = bytearray()
    for y in range(200):
        row = b''.join(bytes(s['palette'][i]+[255])*4 for i in frame[y*320:(y+1)*320])
        expected.extend(row*4)
    if enabled:
        overlay, atlas = bytearray(pictures['panel.png']), premultiply(pictures['glyphs.png'])
        for field in decoded['fields']:
            for col,ch in enumerate(field['text']):
                ix,iy = manifest['atlas_characters'].index(ch)*24,28 if field['color'] == 12 else 0
                x,y = (field['x']+col*6)*4,field['y']*4
                for dy in range(28):
                    for dx in range(24):
                        src = ((iy+dy)*288+ix+dx)*4
                        at = ((y+dy)*940+x+dx)*4
                        alpha = atlas[src+3]
                        for c in range(4):
                            overlay[at+c] = (overlay[at+c]*(65535-alpha*257)*257//65535+atlas[src+c]*257) >> 8
        for dy in range(528):
            expected[((148+dy)*1280+72)*4:((148+dy)*1280+1012)*4] = overlay[dy*940*4:(dy+1)*940*4]
    assert pixels == expected, '預算完整面板或全部區外像素失配'
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--receipts',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--require-five-rows',action='store_true')
    ap.add_argument('--require-nonzero',action='store_true')
    args = ap.parse_args()
    samples = []
    for path in sorted(args.receipts.rglob('*-capture.zip')):
        with zipfile.ZipFile(path) as z:
            s, frame = json.loads(z.read('status.json')), z.read('frame-index.bin')
            pixels = subprocess.check_output(['convert','png:-','-depth','8','rgba:-'],input=z.read('presentation.png'))
        assert sha(frame) == s['frame_index_sha256'] and sha(pixels) == s['presentation_sha256']
        if audit_budget(s,frame,pixels):
            model = decode_budget(frame,references()[0])
            samples.append({'receipt':str(path.relative_to(args.receipts)),'enabled':s['hd_enabled'],
                'selection':model['selected_rows'][0], 'texts':[f['text'] for f in model['fields']], 'steps':s['steps']})
    assert samples, '沒有完整預算收據'
    if args.require_five_rows:
        assert {s['selection'] for s in samples if s['enabled']} == set(range(5))
        assert {s['enabled'] for s in samples} == {False,True}
    if args.require_nonzero:
        assert any(int(t) for s in samples if s['enabled'] for t in s['texts'][5:])
    args.out.write_text(json.dumps({'samples':samples,'full_source_and_palette':True,
        'whole_roi_and_all_outside_equal':True,'scope':'正常收據的預算呈現核對，原版規則及其他家族另驗'},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'budget_receipts':len(samples),'rows':sorted({s['selection'] for s in samples}),
        'theme_states':sorted({s['enabled'] for s in samples})},ensure_ascii=False))


if __name__ == '__main__':
    main()
