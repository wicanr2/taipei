"""#46／027：從已審查離線原型匯出本機火力 36 格正式素材。"""
import argparse
import json
import os
from pathlib import Path

from hd_source_audit import sha


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--prototype',type=Path,required=True)
    p.add_argument('--check',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    assert not args.out.exists() and args.out.parent.is_dir() and args.out.parent.stat().st_uid==os.getuid()
    raw=(args.prototype/'manifest.json').read_bytes()
    assert sha(raw)=='d1d887b33ce64737a4f7939880316317bd2a2547837c5c0b1c10beff48b4ee7a'
    proof=json.loads(args.check.read_text())
    assert proof['prototype_manifest_sha256']==sha(raw) and proof['fragments']==36
    assert proof['source_pixel_negatives']==2916 and proof['full_reassembly_equal']
    case=json.loads(raw)['cases'][0]
    atlas=(args.prototype/'thermal-hd.png').read_bytes()
    assert sha(atlas)==case['files']['thermal-hd.png']
    records=[]
    for record in case['fragments']:
        col,row=record['relative_cell']
        source=(args.prototype/record['source_file']).read_bytes()
        assert len(source)==81 and sha(source)==record['source_sha256']
        records.append({'image':12+row*30+col,'cell':[col,row],'source_sha256':sha(source),
            'aliases':record['sources'],'used_colors':sorted(set(source))})
    manifest={'schema':1,'stage':'thermal36','rom_sha256':proof['rom_sha256'],
        'atlas':'thermal.png','atlas_sha256':sha(atlas),'atlas_size':[216,216],
        'palette':case['used_palette'],'sources':records,
        'prototype_manifest_sha256':sha(raw),'prototype_check_sha256':sha(args.check.read_bytes()),
        'scope':'027 READY 火力已見靜態來源 36 格，未知來源回退；核能及其他相位未完成'}
    args.out.mkdir()
    (args.out/'thermal.png').write_bytes(atlas)
    (args.out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'manifest_sha256':sha((args.out/'manifest.json').read_bytes()),'atlas_sha256':sha(atlas)}))


if __name__=='__main__':main()
