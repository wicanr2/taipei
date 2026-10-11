"""#44：更新受影響雜湊後破壞正式道路電線收據，驗證獨立核對有效。"""
import argparse
import copy
import json
import subprocess
import zipfile
from pathlib import Path

from hd_infrastructure_check import expected_tile,references
from hd_scroll_check import audit_bundle,source59
from hd_source_audit import cell,sha
from infrastructure_prototype import png


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--receipt',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args = ap.parse_args()
    assert not args.out.exists()
    args.out.mkdir()
    with zipfile.ZipFile(args.receipt) as z:
        files = {name:z.read(name) for name in z.namelist()}
    original = json.loads(files['status.json'])
    pixels = subprocess.check_output(['convert','png:-','-depth','8','rgba:-'],input=files['presentation.png'])
    frame = files['frame-index.bin']
    sources,_,_ = references()
    chosen = next((col,row,cell(frame,5+col*9,34+row*9)) for row in range(15) for col in range(29)
        if cell(frame,5+col*9,34+row*9) in sources)
    col,row,source = chosen
    x,y = 20+col*36,136+row*36
    origin = original['map_origin']
    results = []
    for fault in ['positive','unused-palette','tile-pixel','wrong-world-phase','source-pixel','fallback-pixel','image-count']:
        changed = dict(files)
        s = copy.deepcopy(original)
        output,indices = bytearray(pixels),bytearray(frame)
        if fault=='tile-pixel':output[((y+18)*1280+x+18)*4]^=1
        elif fault=='wrong-world-phase':
            replacement = expected_tile(source,((origin['X']+col)*36+40,(origin['Y']+row)*36-40),tuple(map(tuple,s['palette'])))
            assert any(output[((y+dy)*1280+x)*4:((y+dy)*1280+x+36)*4]!=replacement[dy*144:(dy+1)*144] for dy in range(36))
            for dy in range(36):
                at = ((y+dy)*1280+x)*4
                output[at:at+144] = replacement[dy*144:(dy+1)*144]
        elif fault=='source-pixel':
            indices[(34+row*9)*320+5+col*9] = 255
            assert cell(indices,5+col*9,34+row*9) not in sources
            h = s['hd']
            h['Matched']-=1;h['Painted']-=1;h['Fallback']+=1
            family = h['infrastructure']
            family['matched']-=1;family['painted']-=1
            key = str(sources[source])
            family['images'][key]-=1
            if not family['images'][key]:del family['images'][key]
            family['reasons']['matched-infrastructure']-=1
            if not family['reasons']['matched-infrastructure']:del family['reasons']['matched-infrastructure']
        elif fault=='fallback-pixel':
            terrain = source59(Path('/orig'))
            cx,cy = next((5+c*9,34+r*9) for r in range(15) for c in range(29)
                if cell(frame,5+c*9,34+r*9) not in sources and cell(frame,5+c*9,34+r*9) not in terrain)
            output[((cy*4+18)*1280+cx*4+18)*4]^=1
        elif fault=='image-count':s['hd']['infrastructure']['images'][str(sources[source])]+=1
        elif fault=='unused-palette':
            unused = next(i for i in range(256) if i not in frame)
            s['palette'][unused][0]^=1
        native = bytearray()
        for index in indices:native.extend(s['palette'][index]+[255])
        changed['frame-index.bin'] = bytes(indices)
        changed['frame.png'] = png(native,320,200)
        changed['presentation.png'] = png(output,1280,800)
        s['frame_index_sha256'],s['presentation_sha256'] = sha(indices),sha(output)
        changed['status.json'] = (json.dumps(s,ensure_ascii=False,indent=2)+'\n').encode()
        path = args.out/(fault+'-capture.zip')
        with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED) as z:
            for name,raw in changed.items():z.writestr(name,raw)
        positive = fault in ['positive','unused-palette']
        try:audit_bundle(path,source59(Path('/orig')))
        except AssertionError as error:
            assert not positive,(fault,str(error))
            rejected,reason = True,str(error)[:240]
        else:
            assert positive,('有效破壞未拒絕',fault)
            rejected,reason = False,'完整正對照通過'
        results.append({'fault':fault,'positive':positive,'rejected':rejected,'reason':reason,
            'receipt_sha256':sha(path.read_bytes()),'affected_digests_recomputed':True,'native_png_consistent':True})
    (args.out/'result.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'positive':sum(r['positive'] for r in results),'effective_negative':sum(r['rejected'] for r in results)},ensure_ascii=False))


if __name__=='__main__':
    main()
