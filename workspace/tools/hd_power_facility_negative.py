"""#46：重算所有受影響雜湊後，以兩個獨立核對器拒絕有效畫面破壞。"""
import argparse
import copy
import json
import subprocess
import zipfile
from pathlib import Path

from hd_power_facility_check import references
from hd_scroll_check import audit_bundle,source59
from hd_source_audit import cell,sha,MATERIAL
from infrastructure_prototype import png


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--receipt',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    assert not args.out.exists()
    args.out.mkdir()
    with zipfile.ZipFile(args.receipt) as z:files={name:z.read(name) for name in z.namelist()}
    original=json.loads(files['status.json'])
    frame=files['frame-index.bin']
    pixels=subprocess.check_output(['convert','png:-','-depth','8','rgba:-'],input=files['presentation.png'])
    sources,_=references()
    col,row,source=next((c,r,cell(frame,5+c*9,34+r*9)) for r in range(15) for c in range(29)
        if cell(frame,5+c*9,34+r*9) in sources)
    x,y=20+col*36,136+row*36
    results=[]
    for fault in ['positive','unused-palette-positive','tile-pixel','wrong-fragment','source-pixel','fallback-pixel','image-count']:
        directory=args.out/fault
        directory.mkdir()
        s=copy.deepcopy(original)
        output,indices=bytearray(pixels),bytearray(frame)
        index,fragment=sources[source]
        if fault=='tile-pixel':output[((y+18)*1280+x+18)*4]^=1
        elif fault=='wrong-fragment':
            replacement=next(v[1] for k,v in sources.items() if k!=source and v[1]!=fragment)
            for dy in range(36):
                at=((y+dy)*1280+x)*4
                output[at:at+144]=replacement[dy*144:(dy+1)*144]
        elif fault=='source-pixel':
            indices[(34+row*9)*320+5+col*9]^=128
            assert cell(indices,5+col*9,34+row*9) not in sources
            h=s['hd'];h['Matched']-=1;h['Painted']-=1;h['Fallback']+=1
            family=h['power_facility'];family['matched']-=1;family['painted']-=1
            family['images'][str(index)]-=1
            if not family['images'][str(index)]:del family['images'][str(index)]
            family['reasons']['matched-power-facility']-=1
            if not family['reasons']['matched-power-facility']:del family['reasons']['matched-power-facility']
        elif fault=='fallback-pixel':
            from hd_infrastructure_check import references as infrastructure
            terrain=source59(Path('/orig'));infra=infrastructure()[0]
            cx,cy=next((5+c*9,34+r*9) for r in range(15) for c in range(29)
                if cell(frame,5+c*9,34+r*9) not in sources and cell(frame,5+c*9,34+r*9) not in terrain and cell(frame,5+c*9,34+r*9) not in infra)
            output[((cy*4+18)*1280+cx*4+18)*4]^=1
        elif fault=='image-count':s['hd']['power_facility']['images'][str(index)]+=1
        elif fault=='unused-palette-positive':s['palette'][next(i for i in range(256) if i not in frame and i not in MATERIAL)][0]^=1
        changed=dict(files)
        changed['frame-index.bin']=bytes(indices)
        changed['frame.png']=png(bytes(v for i in indices for v in s['palette'][i]+[255]),320,200)
        changed['presentation.png']=png(output,1280,800)
        s['frame_index_sha256'],s['presentation_sha256']=sha(indices),sha(output)
        changed['status.json']=(json.dumps(s,ensure_ascii=False,indent=2)+'\n').encode()
        path=directory/'case-capture.zip'
        with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED) as z:
            for name,raw in changed.items():z.writestr(name,raw)
        error=''
        try:audit_bundle(path,source59(Path('/orig')))
        except AssertionError as e:error=str(e) or 'AssertionError'
        root='/workspace/prototypes/hd-style'
        command=['/workspace/runs/receipt-check','-dir',str(directory),'-original','/orig',
            '-power-reference',root,'-budget-reference',root,'-file-reference',root,
            '-panel-manifest',root+'/startup-menus-v1/manifest.json',
            '-tool-panel-manifest',root+'/tool-menus-v1/manifest.json',
            '-city-panel-manifest',root+'/city-menus-v1/manifest.json',
            '-font-reference',root+'/font-comparison/noto-font.png','-ui-reference',root+'/city-icons-b-v1.png',
            '-dialog-reference',root+'/new-game-noto-reference-v1.png','-chrome-reference',root+'/city-chrome-v1',
            '-footer-reference',root]
        run=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        positive=fault.endswith('positive')
        assert bool(error) is not positive and (run.returncode!=0) is not positive,(fault,error,run.stdout[:600])
        results.append({'fault':fault,'positive':positive,'python_rejected':bool(error),'go_rejected':run.returncode!=0,
            'python_error':error,'go_output':run.stdout[:500],'receipt_sha256':sha(path.read_bytes()),
            'affected_digests_recomputed':True,'native_png_consistent':True})
    (args.out/'result.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'positive':sum(r['positive'] for r in results),
        'both_checkers_rejected':sum(r['python_rejected'] and r['go_rejected'] for r in results)}))


if __name__=='__main__':main()
