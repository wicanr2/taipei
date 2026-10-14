#!/usr/bin/env python3
"""#62：完整原始圖庫與補齊來源，無 VM、無規則或用途推測。"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import zipfile

from infrastructure_catalog import sources,sha,ROM_SHA
from rom_catalog import png


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--coverage',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    assert not a.out.exists() and a.out.parent.stat().st_uid==os.getuid()
    coverage=json.loads(a.coverage.read_text())
    assert coverage['unique_sources']==1049 and coverage['synthetic_renderer_input'] and not coverage['normal_player_test']
    rom=Path('/orig/RS201.ROM').read_bytes();assert sha(rom)==ROM_SHA
    aliases=sources(rom);byid={(v['member'],v['image']):raw for raw,refs in aliases.items() for v in refs}
    receipt=Path('/workspace/runs/gui-public-r2/pause-capture.zip')
    with zipfile.ZipFile(receipt) as z:status=json.loads(z.read('status.json'))
    assert sha(receipt.read_bytes())==coverage['normal_seed_receipt_sha256']
    palette=status['palette'];a.out.mkdir()
    for sub in ['complex','zones','misc']:(a.out/sub).mkdir()
    groups=[]
    def export_group(member,base,kind):
        root=a.out/kind/f'm{member}-b{base:02d}';root.mkdir()
        tiles=[];raster=bytearray(36*36)
        for row in range(4):
            for col in range(4):
                index=base+24*row+col;raw=byid[member,index]
                assert all(not r['source_known'] for r in coverage['records'] if r['source_sha256']==sha(raw))
                for dy in range(9):raster[(row*9+dy)*36+col*9:(row*9+dy)*36+col*9+9]=raw[dy*9:(dy+1)*9]
                tiles.append({'cell':[col,row],'source_sha256':sha(raw),'sources':aliases[raw],
                    'used_colors':sorted(set(raw))})
        png(root/'source.png',36,36,raster,bytes(v for c in palette for v in c))
        subprocess.run(['convert',str(root/'source.png'),'-filter','point','-resize','864x864!',
            '-strip',str(root/'reference.png')],check=True)
        proof={'schema':1,'issue':62,'id':root.name,'member':member,'base':base,'size':[4,4],
            'rom_sha256':ROM_SHA,'tiles':tiles,'used_palette':{str(i):palette[i] for i in sorted(set(raster))},
            'source_png_sha256':sha((root/'source.png').read_bytes()),'reference_png_sha256':sha((root/'reference.png').read_bytes()),
            'composite_source_sha256':sha(raster),'normal_player_test':False,
            'address_space':'RS201.ROM file offsets; zero-based member/image',
            'level':'已證實：完整ROM bytes與9x9形態；4x4排列依sub_17BF8原始指令24*row+4*arg6+col，圖像用途未推定',
            'ida_evidence':'workspace/runs/ida-46/nuclear-check.json; sub_17BF8 IDA loader linear 0x17FD1..0x17FE6'}
        (root/'source.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
        groups.append({'id':root.name,'kind':kind,'member':member,'base':base,'source_sha256':sha((root/'source.json').read_bytes())})
    for member in [34,35,36]:
        export_group(member,0,'zones')
        for base in [8,12,16,20]:export_group(member,base,'complex')
    export_group(37,8,'complex')
    misc=[]
    for record in coverage['records']:
        if record['painted_in_synthetic_context'] or record['all_zero_placeholder']:continue
        refs=record['aliases']
        if not all(v['member'] in [39,59] for v in refs):continue
        raw=next(raw for raw in aliases if sha(raw)==record['source_sha256'])
        v=refs[0];name=f'{v["member"]}-{v["image"]:03d}'
        (a.out/'misc'/(name+'.bin')).write_bytes(raw)
        misc.append({'id':name,'source_sha256':sha(raw),'sources':aliases[raw],'used_colors':sorted(set(raw))})
    assert len(groups)==16 and len([g for g in groups if g['kind']=='complex'])==13 and len(misc)==58
    roots=[Path('/workspace/runs/power-scenario-scan-r1/city-1/saves/FUND.SAV')]+sorted(
        Path('/workspace/runs/power-scenario-scan-r2').glob('*/saves/FUND.SAV'))
    candidates=[]
    for p in roots:
        saved=p.read_bytes();assert len(saved)==93567
        types,variants=saved[115:9460],saved[9460:18805]
        for i,typ in enumerate(types):
            t=typ&127;x,y=i%105,i//105;base=variants[i]
            if not typ&128 or t not in [1,2,3,4] or base not in [0,8,12,16,20] or x+4>105 or y+4>89:continue
            if t==4 and base!=8:continue
            if not all((types[(y+r)*105+x+c]&127)==t and variants[(y+r)*105+x+c]==base+24*r+c for r in range(4) for c in range(4)):continue
            candidates.append({'id':f'm{33+t}-b{base:02d}','save':str(p),'save_sha256':sha(saved),
                'world':[x,y],'level':'強推論，唯讀SAV候選；正常GUI仍逐byte核對完整圖像'})
    m={'schema':1,'issue':62,'stage':'DRAFT','rom_sha256':ROM_SHA,
        'coverage_sha256':sha(a.coverage.read_bytes()),'palette':{str(i):c for i,c in enumerate(palette)},
        'groups':groups,'misc':misc,'candidates':candidates,'tool_sha256':sha(Path(__file__).read_bytes()),
        'scope':'301種非空待補來源：13張4x4複合圖、3種區域字樣與58種小格；候選不作正常驗收'}
    (a.out/'inventory.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
    print('DRAFT:',len(groups),'groups,',len(misc),'misc,',len(candidates),'intact original-save candidates')


if __name__=='__main__':main()
