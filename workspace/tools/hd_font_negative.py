"""#27：破壞文字或區外像素並同步更新呈現雜湊，驗收據檢查器仍拒絕。"""
import argparse
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--receipt',type=Path,required=True)
    ap.add_argument('--reference',type=Path,required=True)
    ap.add_argument('--checker',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    with zipfile.ZipFile(args.receipt) as z:files={name:z.read(name) for name in z.namelist()}
    original=json.loads(files['status.json']);assert original['hd']['font_labels']==6
    results=[]
    for name,x,y,expected in [('font',28,40,'Noto pixels differ from selected reference'),
                              ('gap',200,40,'presentation changed native pixel')]:
        png=subprocess.run(['convert','png:-','-fill','rgb(255,0,0)','-draw',f'point {x},{y}',
                            '-define','png:color-type=6','png:-'],input=files['presentation.png'],
                            stdout=subprocess.PIPE,check=True).stdout
        rgba=subprocess.run(['convert','png:-','-depth','8','rgba:-'],input=png,stdout=subprocess.PIPE,check=True).stdout
        status=dict(original);status['presentation_sha256']=hashlib.sha256(rgba).hexdigest()
        status['negative_control']=name
        changed=dict(files);changed['presentation.png']=png
        changed['status.json']=json.dumps(status).encode()
        directory=args.out/name;directory.mkdir(parents=True,exist_ok=True)
        path=directory/'mutated-capture.zip'
        with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_STORED) as z:
            for member,data in changed.items():z.writestr(member,data)
        run=subprocess.run([str(args.checker),'-dir',str(directory),'-font-reference',str(args.reference)],
                           stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        assert run.returncode!=0 and expected in run.stdout,(name,run.returncode,run.stdout)
        results.append({'negative_control':name,'presentation_hash_updated':True,
                        'rejected':True,'expected_error':expected,'xy':[x,y]})
    (args.out/'result.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(results,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
