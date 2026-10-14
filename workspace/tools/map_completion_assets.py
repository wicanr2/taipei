#!/usr/bin/env python3
"""#62／038：完整原圖、整張 B 圖與既有材質的可重現本機資產。"""
import argparse
import json
import os
from pathlib import Path
import subprocess

from infrastructure_catalog import sources, sha, ROM_SHA
from infrastructure_prototype import geometry, render, png, MATERIAL_SHA, SIZE
from hd_file_dialogs_check import rgba


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
    return sha(path.read_bytes())


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--inputs',type=Path,required=True)
    ap.add_argument('--materials',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--stage',choices=['DRAFT','READY'],required=True)
    a=ap.parse_args()
    assert not a.out.exists() and a.out.parent.stat().st_uid==os.getuid()
    inventory=json.loads((a.inputs/'inventory.json').read_text())
    rom=Path('/orig/RS201.ROM').read_bytes();assert sha(rom)==ROM_SHA
    aliases=sources(rom);bysha={sha(raw):raw for raw in aliases}
    palette=[inventory['palette'][str(i)] for i in range(256)]
    textures={}
    for name,want in MATERIAL_SHA.items():
        path=a.materials/(name+'-b-v1.png');assert sha(path.read_bytes())==want
        textures[name]=rgba(path,(SIZE,SIZE))
    a.out.mkdir();seals={}
    for kind in ['complex','zones']:
        out=a.out/kind;out.mkdir();records=[];colors=set();unique=set()
        for record in inventory['groups']:
            if record['kind']!=kind:continue
            root=a.inputs/kind/record['id'];proof=json.loads((root/'source.json').read_text())
            assert sha((root/'source.json').read_bytes())==record['source_sha256']
            native=bytearray(144*144*4);background=bytearray(len(native))
            for tile in proof['tiles']:
                raw=bysha[tile['source_sha256']]
                assert aliases[raw]==tile['sources'] and sorted(set(raw))==tile['used_colors']
                unique.add(sha(raw));colors.update(raw);x,y=tile['cell']
                if kind=='zones':
                    # 原版白色字樣擦除為同一沙地；Noto 在執行時按 TSV 覆繪。
                    erased=bytes(204 if v==15 else v for v in raw)
                    painted=render(geometry(erased),(0,0),palette,textures)
                for dy in range(36):
                    for dx in range(36):
                        at=((y*36+dy)*144+x*36+dx)*4
                        native[at:at+4]=bytes(palette[raw[(dy//4)*9+dx//4]]+[255])
                    if kind=='zones':
                        at=((y*36+dy)*144+x*36)*4
                        background[at:at+144]=painted[dy*144:(dy+1)*144]
            if kind=='complex':
                generation=json.loads((root/'generation.json').read_text())
                assert sha((root/'generated.png').read_bytes())==generation['generated_sha256']
                assert sha((root/'prompt.txt').read_bytes())==generation['prompt_sha256']
                assert sha((root/'reference.png').read_bytes())==generation['reference_sha256']
                painted=subprocess.check_output(['convert',str(root/'generated.png'),'-filter','Lanczos',
                    '-resize','144x144!','-depth','8','rgba:-'])
            else:painted=background;generation={'method':'既有 B 材質與原版完整邊框，字樣接執行期 Noto'}
            assert len(painted)==144*144*4 and set(painted[3::4])=={255}
            encoded=png(painted,144,144);(out/(proof['id']+'.png')).write_bytes(encoded)
            if a.stage=='DRAFT':
                comparison=b''.join(native[y*576:(y+1)*576]+painted[y*576:(y+1)*576] for y in range(144))
                (out/(proof['id']+'-comparison.png')).write_bytes(png(comparison,288,144))
            records.append({'id':proof['id'],'size':[4,4],'atlas':proof['id']+'.png','sha256':sha(encoded),
                'rgba_sha256':sha(painted),'source_proof_sha256':record['source_sha256'],
                'generated':generation,'tiles':proof['tiles']})
        expected=(208,207,13) if kind=='complex' else (48,36,3)
        assert (sum(len(r['tiles']) for r in records),len(unique),len(records))==expected
        manifest={'schema':1,'stage':'map-'+kind,'issue':62,'rom_sha256':ROM_SHA,
            'palette':{str(i):palette[i] for i in sorted(colors)},'facilities':records,
            'tiles':expected[0],'unique_sources':expected[1],
            'image_processing':'整張144x144切格；區域原圖白字由執行期Noto取代，沙地格相位相同以保留同源裁切'}
        seals[kind]=write_json(out/'manifest.json',manifest)
    out=a.out/'detail';out.mkdir();records=[];colors=set()
    for record in inventory['misc']:
        raw=bysha[record['source_sha256']];assert aliases[raw]==record['sources']
        assert (a.inputs/'misc'/(record['id']+'.bin')).read_bytes()==raw
        indices,weights=geometry(raw);colors.update(raw)
        for suffix,data in [('indices',indices),('weights',weights)]:
            (out/(record['id']+'-'+suffix+'.bin')).write_bytes(data)
        if a.stage=='DRAFT':(out/(record['id']+'.png')).write_bytes(png(render((indices,weights),(0,0),palette,textures),36,36))
        records.append(dict(record,indices_sha256=sha(indices),weights_sha256=sha(weights)))
    assert len(records)==58
    seals['detail']=write_json(out/'manifest.json',{'schema':1,'stage':'map-detail','issue':62,
        'rom_sha256':ROM_SHA,'geometry_version':3,'asphalt_frequency':4,'material_size':SIZE,
        'sources':records,'palette':{str(i):palette[i] for i in sorted(colors)},'materials':MATERIAL_SHA,
        'scope':'58種完整非空原圖；不由用途或鄰格推導連接與模擬規則'})
    seal=write_json(a.out/'manifest.json',{'schema':1,'stage':a.stage,'issue':62,'rom_sha256':ROM_SHA,
        'source_inventory_sha256':sha((a.inputs/'inventory.json').read_bytes()),
        'submanifests':seals,'unique_nonempty_sources':301,'opaque':True,
        'rights':'依原圖重繪／原版來源未確認散布權，留本機；程式與腳本另依專案授權',
        'source_coverage_is_normal_playtest':False,'tool_sha256':sha(Path(__file__).read_bytes())})
    print(a.stage,'301 unique nonempty sources',seals,'root',seal)


if __name__=='__main__':main()
