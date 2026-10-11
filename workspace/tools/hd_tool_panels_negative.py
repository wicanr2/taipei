"""#31：完整工具面板與區外的有效負對照，更新所有受影響雜湊。"""
import argparse
import json
import subprocess
import zipfile
from pathlib import Path
from hd_chrome_negative import png
from hd_panels_check import audit_panel, references, TOOL_MANIFEST, CITY_MANIFEST
from hd_source_audit import sha


def check(directory, manifest=TOOL_MANIFEST):
    root = Path('/workspace/prototypes/hd-style')
    return subprocess.run(['/workspace/runs/receipt-check', '-dir', str(directory),
        '-panel-manifest', str(root/'startup-menus-v1/manifest.json'),
        '-tool-panel-manifest', str(TOOL_MANIFEST),
        '-city-panel-manifest', str(manifest) if manifest == CITY_MANIFEST else ''],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--receipt', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--family', choices=['tool', 'city'], default='tool')
    args = ap.parse_args()
    manifest = CITY_MANIFEST if args.family == 'city' else TOOL_MANIFEST
    prefix = 'city-f' if args.family == 'city' else 'tool-'
    with zipfile.ZipFile(args.receipt) as z: files = {n:z.read(n) for n in z.namelist()}
    s = json.loads(files['status.json']); frame = files['frame-index.bin']
    rgba = subprocess.check_output(['convert','png:-','-depth','8','rgba:-'], input=files['presentation.png'])
    assert sha(frame) == s['frame_index_sha256'] and sha(rgba) == s['presentation_sha256']
    assert audit_panel(s, frame, rgba) and s['hd']['panel'].startswith(prefix)
    state = next(v for v,_ in references(manifest) if (v['id'],v['selection']) == (s['hd']['panel'],s['hd']['panel_selection']))
    count = sum(v['id'] == state['id'] for v,_ in references(manifest))
    x,y,w,h = state['native']
    glyph = next((xx,yy) for yy in range(y*4,(y+h)*4) for xx in range(x*4,(x+w)*4)
                 if rgba[(yy*1280+xx)*4:(yy*1280+xx)*4+3] == b'\xff\x00\x00')
    positive=args.out/'positive'; positive.mkdir(parents=True, exist_ok=True)
    (positive/'positive-capture.zip').write_bytes(args.receipt.read_bytes())
    assert check(positive, manifest).returncode == 0, '有效負對照之前的正對照失敗'
    results=[]
    for name,xy in [('glyph',glyph),('background',(x*4,y*4)),('outside',((x+w)*4+1,y*4+1)),
                    ('source',(x,y)),('palette',(state['palette_indices'][0],0)),('selection',(0,0)),('id',(0,0))]:
        changed=dict(files); status=json.loads(files['status.json'])
        pixels=bytearray(rgba); native=bytearray(frame)
        if name in ['source','palette']:
            if name=='source': native[xy[1]*320+xy[0]] ^= 128
            else: status['palette'][xy[0]][0] ^= 1
            changed['frame-index.bin']=native; status['frame_index_sha256']=sha(native)
            changed['frame.png']=png(bytes(v for i in native for v in status['palette'][i]+[255]),320,200)
        elif name=='selection': status['hd']['panel_selection']=(state['selection']+1) % count if count > 1 else 1
        elif name=='id': status['hd']['panel']=prefix+'unknown'
        else:
            pixels[(xy[1]*1280+xy[0])*4] ^= 127
            changed['presentation.png']=png(pixels,1280,800); status['presentation_sha256']=sha(pixels)
        changed['status.json']=json.dumps(status).encode()
        directory=args.out/name; directory.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(directory/'mutated-capture.zip','w',compression=zipfile.ZIP_STORED) as z:
            for n,raw in changed.items(): z.writestr(n,raw)
        error=''
        try: audit_panel(status,native,pixels)
        except AssertionError as e: error=str(e)
        run=check(directory, manifest)
        assert error and run.returncode!=0,(name,error,run.stdout)
        expected='panel source, palette or metadata mismatch' if name in ['source','palette','selection','id'] else ('presentation changed native pixel' if name=='outside' else 'panel pixels differ')
        assert expected in run.stdout,(name,run.stdout)
        results.append({'case':name,'source_checker_rejected':True,'pixel_checker_rejected':True,
                        'affected_digest_updated':True,'native_png_consistent':True,'error':error})
    (args.out/'result.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'panel':state['id'],'cases':len(results),'all_rejected':True}))


if __name__=='__main__': main()
