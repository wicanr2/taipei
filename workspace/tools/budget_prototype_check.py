"""#39：獨立核對離線預算原型、實際墨跡及原版來源，不執行產品呈現器。"""
import argparse
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

from budget_catalog import decode_budget, references
from full_asset_catalog import image
from hd_file_dialogs_check import premultiply


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def rgba(raw, size):
    pixels = subprocess.check_output(['convert', 'png:-', '-depth', '8', 'rgba:-'], input=raw)
    assert len(pixels) == size[0]*size[1]*4
    return pixels


def box(rect):
    return rect['Min']['X'], rect['Min']['Y'], rect['Max']['X'], rect['Max']['Y']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--materials', type=Path, required=True)
    ap.add_argument('--original', type=Path, required=True)
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    root = args.materials/'budget-v1'
    manifest_raw = (root/'manifest.json').read_bytes()
    manifest = json.loads(manifest_raw)
    catalog_raw = args.source.read_bytes()
    assert manifest['sources_sha256'] == sha(catalog_raw)
    catalog = json.loads(catalog_raw)
    layout_raw = (args.materials/'budget-layout-v1.json').read_bytes()
    assert manifest['layout_sha256'] == sha(layout_raw)
    layout = json.loads(layout_raw)
    rom = (args.original/'RS201.ROM').read_bytes()
    refs = references(rom)
    off, size = refs['members']['2']['file_offset'], refs['members']['2']['bytes']
    native = image(rom[off:off+size])[2]
    assert manifest['font_sha256'] == sha((args.materials/'fonts/NotoSansCJKtc-Regular.otf').read_bytes()) == 'dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4'
    assert manifest['license_sha256'] == sha((args.materials/'fonts/LICENSE').read_bytes()) == '6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2'
    assert manifest['art_sha256'] == sha((args.materials/'menu-blue-b-v1.png').read_bytes()) == 'eeb1aa620c179a7fa0233bdfc9d9ad6abf8719d36f1ad05dc93c84343a164ea9'
    pictures = {}
    for name, size in [('panel.png', (940,528)), ('static-ink.png', (940,528)), ('glyphs.png', (288,56))]:
        raw = (root/name).read_bytes()
        assert sha(raw) == manifest['images'][name]
        pictures[name] = rgba(raw,size)
    assert all(pictures['panel.png'][i] == 255 for i in range(3,len(pictures['panel.png']),4))
    static_allowed, ink_rectangles = set(), []
    for check in manifest['ink_checks']:
        x0,y0,x1,y1 = box(check['safe'])
        if check['kind'] == 'static':
            c = layout['cells'][check['index']]
            assert (x0,y0,x1,y1) == (c['x']*4,c['y']*4,(c['x']+c['w'])*4,(c['y']+c['h'])*4)
            source = b''.join(native[(c['y']+dy)*235+c['x']:(c['y']+dy)*235+c['x']+c['w']] for dy in range(c['h']))
            assert sha(source) == c['source_index_sha256']
            data, width = pictures['static-ink.png'], 940
            assert 0 <= x0 < x1 <= 940 and 0 <= y0 < y1 <= 528
            static_allowed.update((x,y) for y in range(y0,y1) for x in range(x0,x1))
        else:
            index = check['index']
            assert (x0,y0,x1,y1) == ((index%12)*24,(index//12)*28,(index%12+1)*24,(index//12+1)*28)
            assert check['text'] == manifest['atlas_characters'][index%12] and check['font_size'] == 32
            data, width = pictures['glyphs.png'], 288
        points = [(x,y) for y in range(y0,y1) for x in range(x0,x1) if data[(y*width+x)*4+3]]
        assert bool(points) == (check['text'] != ' ')
        if points:
            actual = min(x for x,y in points), min(y for x,y in points), max(x for x,y in points)+1, max(y for x,y in points)+1
            assert actual == box(check['actual_ink'])
            if check['kind'] == 'static': ink_rectangles.append(actual)
        assert not check['missing_glyph'] and not check['clipped']
    static = pictures['static-ink.png']
    assert all((x,y) in static_allowed for y in range(528) for x in range(940) if static[(y*940+x)*4+3])
    for i,(x0,y0,x1,y1) in enumerate(ink_rectangles):
        for a,b,c,d in ink_rectangles[i+1:]:
            assert x1 <= a or c <= x0 or y1 <= b or d <= y0, '靜態字形墨跡重疊'
    atlas = premultiply(pictures['glyphs.png'])
    negative_controls = []
    assert {p['selection'] for p in manifest['proofs']} == set(range(5))
    for proof in manifest['proofs']:
        path = Path(proof['receipt'])
        assert sha(path.read_bytes()) == proof['receipt_sha256']
        with zipfile.ZipFile(path) as z:
            status, frame = json.loads(z.read('status.json')), z.read('frame-index.bin')
        model = decode_budget(frame,refs)
        assert model and model['selected_rows'] == [proof['selection']]
        assert proof['nonzero_amounts'] == any(int(f['text']) != 0 for f in model['fields'][5:])
        for name, slot, old, new in [('no-selection',model['fields'][proof['selection']],12,0),
            ('double-selection',model['fields'][(proof['selection']+1)%5],0,12),
            ('cost-red',model['fields'][5],0,12)]:
            changed = bytearray(frame)
            for dy in range(7):
                for dx in range(slot['columns']*6):
                    at = (37+slot['y']+dy)*320+18+slot['x']+dx
                    if changed[at] == old: changed[at] = new
            assert changed != frame and decode_budget(changed,refs) is None
            negative_controls.append({'selection':proof['selection'],'mutation':name,'rejected':True})
        expected = bytearray()
        for y in range(200):
            row = b''.join(bytes(status['palette'][i]+[255])*4 for i in frame[y*320:(y+1)*320])
            expected.extend(row*4)
        overlay = bytearray(pictures['panel.png'])
        for field in model['fields']:
            for column,ch in enumerate(field['text']):
                ix = manifest['atlas_characters'].index(ch)*24
                iy = 28 if field['color'] == 12 else 0
                x,y = (field['x']+column*6)*4,field['y']*4
                assert 0 <= x and x+24 <= 940 and 0 <= y and y+28 <= 528
                for dy in range(28):
                    for dx in range(24):
                        src = ((iy+dy)*288+ix+dx)*4
                        at = ((y+dy)*940+x+dx)*4
                        alpha = atlas[src+3]
                        for c in range(4):
                            overlay[at+c] = (overlay[at+c]*(65535-alpha*257)*257//65535+atlas[src+c]*257) >> 8
        for dy in range(528):
            expected[((148+dy)*1280+72)*4:((148+dy)*1280+1012)*4] = overlay[dy*940*4:(dy+1)*940*4]
        raw = (root/proof['image']).read_bytes()
        assert sha(raw) == proof['image_sha256'] == manifest['images'][proof['image']]
        assert rgba(raw,(1280,800)) == expected, '離線完整原位或區外失配'
    result = {'scope':'離線預算原型，非產品 HD 收據','manifest_sha256':sha(manifest_raw),
        'static_cells':len(layout['cells']),'actual_ink_checks':len(manifest['ink_checks']),
        'normal_source_proofs':len(manifest['proofs']),
        'nonzero_amount_proofs':sum(p['nonzero_amounts'] for p in manifest['proofs']),
        'selected_rows':sorted({p['selection'] for p in manifest['proofs']}),'source_rectangles_equal':True,
        'static_alpha_safe':True,'numeric_alpha_safe':True,'no_static_ink_overlap':True,
        'whole_compositions_and_outside_equal':True,'selection_negative_controls':negative_controls,
        'numeric_safety':'數字及負號逐字實際墨跡核對；每列固定字距，合成最多三／八欄，非原版極值規則驗收'}
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))


if __name__ == '__main__':
    main()
