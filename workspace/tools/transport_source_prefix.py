#!/usr/bin/env python3
"""#61：保留實際 GUI 前綴原件，僅匯出完整已知圖像，不冒稱退出。"""
import argparse
import json
from pathlib import Path
import zipfile
from infrastructure_catalog import sources
from hd_source_audit import scene,cell,sha


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True);a=ap.parse_args()
    out=a.run/'result-progress.json';assert not out.exists()
    receipt=a.run/'capture.zip';aliases=sources(Path('/orig/RS201.ROM').read_bytes())
    with zipfile.ZipFile(receipt) as z:s=json.loads(z.read('status.json'));frame=z.read('frame-index.bin')
    assert scene(s,frame) and s['map_origin']=={'X':36,'Y':24,'Valid':True}
    assert int(s['hd']['footer_text'][3])==73455 and sha(frame)==s['frame_index_sha256']
    known=[]
    for row in range(6):
        for col in range(6):
            raw=cell(frame,104+9*col,79+9*row)
            assert raw in aliases and any(r['member']==38 and r['image']==30*row+col for r in aliases[raw])
            known.append({'cell':[11+col,5+row],'source_sha256':sha(raw),'sources':aliases[raw]})
    out.write_text(json.dumps([{'id':'airport','tool':13,'option':None,'fee':None,
        'before_budget':73455,'after_budget':73455,'bounds':[11,5,6,6],'known':known,
        'receipt':'capture.zip','steps':s['steps'],'origin':s['map_origin'],'construction_tested':False,
        'existing_city':'DISA4.DSA','native_world':[47,29],'source_prefix':True,'normal_path_complete':False,
        'scope':'實際GUI前綴停止前原件的完整36格；未完成同次存讀或原版退出。'}],ensure_ascii=False,indent=2)+'\n')
    print('PASS airport source prefix only:',len(known),'cells; no native-exit claim')


if __name__=='__main__':main()
