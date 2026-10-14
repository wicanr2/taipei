#!/usr/bin/env python3
"""039：複製內建imagegen原件與提示，保留預設原件及DRAFT審查狀態。"""
import argparse
import json
import os
from pathlib import Path
import re
import shutil

from full_asset_catalog import sha


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--plan',type=Path,required=True)
    ap.add_argument('--root',type=Path,required=True)
    ap.add_argument('--version',default='v1');ap.add_argument('--select',action='store_true');a=ap.parse_args()
    assert re.fullmatch('v[1-9][0-9]*',a.version)
    assert a.root.stat().st_uid==os.getuid()
    plan=json.loads(a.plan.read_text());added=0
    for p in plan:
        if not p['generation']:continue
        assert re.fullmatch('[ar][0-9]{2}',p['id'])
        root=a.root/p['id'];assert root.is_dir() and root.stat().st_uid==os.getuid()
        source_path=p['generation']['source_path'];source=Path('/generated')/Path(source_path).name
        assert source.is_file() and source_path.startswith('/home/anr2/.codex/generated_images/')
        suffix='' if a.version=='v1' else '-'+a.version
        target=root/('generated'+suffix+'.png')
        if target.exists():assert sha(target.read_bytes())==sha(source.read_bytes());continue
        shutil.copyfile(source,target);(root/('prompt'+suffix+'.txt')).write_text(p['prompt']+'\n')
        layout=json.loads((root/'layout.json').read_text())
        assert [p['columns'],p['rows'],p['count']]==[layout['columns'],layout['rows'],len(layout['cells'])]
        assert sha((root/'reference.png').read_bytes())==layout['reference_sha256']
        record={'schema':1,'stage':'DRAFT','issue':32,'tool':'built-in image_gen.imagegen',
            'generated_source_path':source_path,'generated_sha256':sha(target.read_bytes()),
            'reference_sha256':layout['reference_sha256'],'layout_sha256':sha((root/'layout.json').read_bytes()),
            'prompt_sha256':sha((root/('prompt'+suffix+'.txt')).read_bytes()),'sources':len(layout['cells']),
            'reference_builder_sha256':sha(Path('/workspace/tools/illustration_groups.py').read_bytes()),
            'rights':'原版與衍生素材留本機，不入Git／Release',
            'review':'完整圖／相位／色盤與裁切待核對，不能自動進production'}
        reference=p.get('reference_file','reference.png');assert Path(reference).name==reference
        record['tool_reference_sha256']=sha((root/reference).read_bytes())
        paths=p.get('tool_reference_paths',[p['id']+'/'+reference])
        assert paths and len(set(paths))==len(paths)
        record['tool_reference_files']=[]
        for path in paths:
            assert re.fullmatch('[ar][0-9]{2}/(?:reference|generated(?:-v[1-9][0-9]*)?)\\.png',path)
            item=a.root/path;assert item.is_file()
            record['tool_reference_files'].append({'relative_path':path,'sha256':sha(item.read_bytes())})
        record['background_plate']=p.get('background_plate',False)
        (root/('generation'+suffix+'.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');added+=1
        if a.select:
            (root/'selection.json').write_text(json.dumps({'stage':'DRAFT','generation':'generation'+suffix+'.json',
                'image':target.name,'reason':'只作DRAFT原型，不自動進產品'},ensure_ascii=False,indent=2)+'\n')
    print('copied',added,'new DRAFT atlases; default generated originals unchanged')


if __name__=='__main__':main()
