#!/usr/bin/env python3
"""039 DRAFT：完整相位按原始圖庫組成重繪參考，不增刪相位。"""
import argparse
import json
import os
from pathlib import Path
import struct
import subprocess

from full_asset_catalog import sha
from infrastructure_prototype import png


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--inputs',type=Path,required=True);a=ap.parse_args()
    root=a.inputs/'groups';assert not root.exists() and a.inputs.stat().st_uid==os.getuid()
    inventory=json.loads((a.inputs/'inventory.json').read_text())
    palette0=json.loads(Path('/workspace/prototypes/hd-style/map-completion-v1/inventory.json').read_text())['palette']
    palette0=[palette0[str(i)] for i in range(256)]
    raw=Path('/orig/RS201A.ROM').read_bytes();assert sha(raw)=='5d66f238dce650b8a407986100392ee4b8ac2aa23a033e80a7ca18ed91b3d9b0'
    off,n=struct.unpack_from('<IH',raw,18+3*16);assert n==768;data=raw[off:off+n]
    expand=lambda v:(v>>2)*4|((v>>2)>>4)
    palette3=[list(map(expand,data[i:i+3])) for i in range(0,768,3)]
    root.mkdir();groups=[]
    for rom,members in [('RS201.ROM',[24,*range(25,34),*range(42,56)]),
                        ('RS201A.ROM',list(range(7,36)))]:
        for member in members:
            records=[r for r in inventory['images'] if r['rom']==rom and r['member']==member and r['id']==r['canonical']]
            if not records:continue
            name=('r' if rom=='RS201.ROM' else 'a')+f'{member:02d}'
            group=root/name;group.mkdir();cols=2 if len(records)>1 else 1;rows=(len(records)+cols-1)//cols
            width,height=max(r['width'] for r in records),max(r['height'] for r in records)
            gap=8;cw,ch=cols*width+(cols-1)*gap,rows*height+(rows-1)*gap
            rgba=bytearray(bytes([48,54,60,255])*(cw*ch));cells=[]
            palette=palette3 if rom=='RS201A.ROM' else palette0
            for i,r in enumerate(records):
                x=i%cols*(width+gap)+(width-r['width'])//2;y=i//cols*(height+gap)+(height-r['height'])//2
                pixels=(a.inputs/r['id']/'source.bin').read_bytes();assert sha(pixels)==r['pixels_sha256']
                for dy in range(r['height']):
                    for dx in range(r['width']):
                        value=pixels[dy*r['width']+dx]
                        rgb=[48,54,60] if value==255 and (r['encoding']=='iv2' or rom=='RS201A.ROM' and 7<=member<=14) else palette[value]
                        at=((y+dy)*cw+x+dx)*4;rgba[at:at+4]=bytes(rgb+[255])
                cells.append({'id':r['id'],'rect':[x,y,r['width'],r['height']],'ordinal':i,
                    'source_sha256':r['pixels_sha256'],'source_record':r})
            (group/'source.png').write_bytes(png(rgba,cw,ch))
            subprocess.run(['convert',str(group/'source.png'),'-filter','point','-resize','400%',
                '-strip',str(group/'reference.png')],check=True)
            m={'schema':1,'stage':'DRAFT','issue':32,'id':name,'rom':rom,'member':member,
                'columns':cols,'rows':rows,'cell_size':[width,height],'gap':gap,'native_size':[cw,ch],
                'target_size':[cw*4,ch*4],'cells':cells,'reference_sha256':sha((group/'reference.png').read_bytes()),
                'palette_method':'ROMA3量化供開場原型；其他正常城市色盤；正式發布色盤仍由唯讀原版核對',
                'rights':'原版與衍生素材留本機','normal_player_test':False}
            (group/'layout.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
            groups.append({'id':name,'sources':len(cells),'layout_sha256':sha((group/'layout.json').read_bytes()),
                'reference_sha256':m['reference_sha256'],'target_size':m['target_size']})
    result={'schema':1,'stage':'DRAFT','issue':32,'source_inventory_sha256':sha((a.inputs/'inventory.json').read_bytes()),
        'groups':groups,'groups_count':len(groups),'unique_sources':sum(g['sources'] for g in groups),
        'scope':'已完成UI與Noto標題另列；城市預覽七張及小游標另以既有B材質／輪廓處理；兩門樓已有DRAFT，不重做'}
    (root/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('DRAFT',len(groups),'groups',result['unique_sources'],'complete source phases',sha((root/'manifest.json').read_bytes()))


if __name__=='__main__':main()
