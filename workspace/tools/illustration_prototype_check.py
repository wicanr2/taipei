#!/usr/bin/env python3
"""039 DRAFT素材核對：重讀原ROM，驗完整覆蓋與來源導出的視覺條件。"""
import argparse
from collections import deque
import json
import os
from pathlib import Path
import struct

from full_asset_catalog import ROMS,image,sha
from hd_file_dialogs_check import rgba
from illustration_sources import iv2


EXISTING={'a06-00','a38-00',*[f'r{i:02d}-00' for i in [1,2,3,*range(11,24)]]}


def block(raw,w,index):
    x,y=index%w,index//w
    return b''.join(raw[((y*4+dy)*w*4+x*4)*4:((y*4+dy)*w*4+x*4)*4+16] for dy in range(4))


def in_rect(index,w,rect):
    x,y,rw,rh=rect
    return x<=index%w<x+rw and y<=index//w<y+rh


def outside_background(pixels,w,h):
    edge=[*range(w),*range((h-1)*w,h*w),*[y*w+x for y in range(h) for x in [0,w-1]]]
    result={i for i in edge if pixels[i]==255};queue=deque(result)
    while queue:
        i=queue.popleft()
        for x,y in [(i%w-1,i//w),(i%w+1,i//w),(i%w,i//w-1),(i%w,i//w+1)]:
            if 0<=x<w and 0<=y<h:
                j=y*w+x
                if pixels[j]==255 and j not in result:result.add(j);queue.append(j)
    return result


def check_background(raw,pixels,w,rgb,value,label,points=None):
    count=0
    for i in (range(len(pixels)) if points is None else points):
        v=pixels[i]
        if v!=value:continue
        assert block(raw,w,i)==bytes(rgb+[255])*16,label
        count+=1
    return count


def check_registry(ids,expected):
    assert set(ids)==expected,'相位登錄'


def check_street_prefix(pictures,w):
    prefix=w*4*52*4*4
    assert all(pictures[k][:prefix]==pictures['a19-00'][:prefix]
        for k in ['a20-00','a21-00','a22-00']),'同街景背景'


def rejects(function,label):
    try:function()
    except AssertionError as e:
        assert str(e)==label,('錯誤反例原因',str(e),label)
        return
    raise AssertionError(('反例未被實際核對拒絕',label))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--inputs',type=Path,required=True)
    ap.add_argument('--prototype',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    assert not a.out.exists() and a.out.parent.stat().st_uid==os.getuid()
    inventory=json.loads((a.inputs/'inventory.json').read_text());manifest=json.loads((a.prototype/'manifest.json').read_text())
    assert sha((a.inputs/'inventory.json').read_bytes())=='d67d234268f912cfc049ebad59ecf706d967ee2e6ce6d5d95a9c21678d356f5a'
    assert manifest['source_inventory_sha256']==sha((a.inputs/'inventory.json').read_bytes())
    assert manifest['stage']=='DRAFT' and manifest['count']==179 and manifest['artist_groups']==52
    assert manifest['tool_sha256']==sha((a.prototype/'executed-builder.py').read_bytes())
    originals={name:Path('/orig',name).read_bytes() for name in ROMS}
    assert all(sha(raw)==ROMS[name][0] for name,raw in originals.items())
    canonical={};decoded={}
    for r in inventory['images']:
        rom=originals[r['rom']];off,size=struct.unpack_from('<IH',rom,18+r['member']*16)
        end=min([q['file_offset'] for q in inventory['images'] if q['rom']==r['rom'] and q['member']==r['member'] and q['file_offset']>r['file_offset']]+[off+size])
        raw=rom[r['file_offset']:end];assert sha(raw)==r['raw_sha256']
        result=iv2(raw) if r['encoding']=='iv2' else image(raw)[:3]
        w,h,pixels=result;assert (w,h)==(r['width'],r['height']) and sha(pixels)==r['pixels_sha256']
        if r['id']==r['canonical']:
            canonical[r['id']]=r;decoded[r['id']]=pixels
            assert (a.inputs/r['id']/'source.bin').read_bytes()==pixels
    records={r['id']:r for r in manifest['images']}
    assert len(records)==179;check_registry(records,set(canonical)-EXISTING)
    assert set(manifest['excluded_existing_ui_noto'])==EXISTING
    assert {p.stem for p in a.prototype.glob('*.png')}==set(records)
    off,size=struct.unpack_from('<IH',originals['RS201A.ROM'],18+3*16);assert size==768
    expand=lambda v:(v>>2)*4|((v>>2)>>4)
    p3=[list(map(expand,originals['RS201A.ROM'][off+i:off+i+3])) for i in range(0,768,3)]
    mp=json.loads((a.inputs.parent/'map-completion-v1/inventory.json').read_text())['palette']
    p0=[mp[str(i)] for i in range(256)];pictures={};white_blocks=black_blocks=0;generations={}
    for identifier,r in records.items():
        src=canonical[identifier];w,h=src['width'],src['height'];palette=p3 if identifier.startswith('a') else p0
        assert r['source_record']==src and r['source_sha256']==sha(decoded[identifier])
        assert r['size']==[w*4,h*4] and r['palette_sha256']==sha(bytes(c for rgb in palette for c in rgb))
        if r['generation_sha256'] is not None:
            if identifier in {'a04-00','a05-00'}:
                root=a.inputs/identifier;gpath=root/'generation-v2.json';image_path=root/'generated-v2.png';prompt=root/'prompt-v2.txt'
            else:
                root=a.inputs/'groups'/r['group']
                selection=json.loads((root/'selection.json').read_text()) if (root/'selection.json').exists() else {'generation':'generation.json','image':'generated.png'}
                assert all(Path(selection[k]).name==selection[k] for k in ['generation','image'])
                gpath=root/selection['generation'];image_path=root/selection['image']
                prompt=root/selection['generation'].replace('generation','prompt').replace('.json','.txt')
            generated=json.loads(gpath.read_text());assert sha(gpath.read_bytes())==r['generation_sha256']
            assert sha(image_path.read_bytes())==generated['generated_sha256'] and sha(prompt.read_bytes())==generated['prompt_sha256']
            generations[str(gpath.relative_to(a.inputs))]=sha(gpath.read_bytes())
            for reference in generated.get('tool_reference_files',[]):
                path=Path(reference['relative_path']);assert not path.is_absolute() and '..' not in path.parts
                assert sha((a.inputs/'groups'/path).read_bytes())==reference['sha256']
        path=a.prototype/(identifier+'.png');assert path.stat().st_uid==os.getuid() and sha(path.read_bytes())==r['png_sha256']
        raw=rgba(path,(w*4,h*4));assert set(raw[3::4])=={255};pictures[identifier]=raw
        outer=outside_background(decoded[identifier],w,h);assert len(outer)==r['outer_background_255_pixels']
        white_blocks+=check_background(raw,decoded[identifier],w,palette[255],255,'原255外背景',outer)
        if identifier=='r33-07':black_blocks+=check_background(raw,decoded[identifier],w,[0,0,0],0,'原黑場')
    check_street_prefix(pictures,canonical['a19-00']['width'])
    assert records['a16-00']['reused_background_generation_sha256']==records['a15-00']['generation_sha256']
    assert len(generations)==54
    stable=0
    for identifiers,mode in [(['a15-00','a16-00'],'same-native-pixels'),
                             ([f'a{i:02d}-00' for i in range(19,23)],'first-52-rows'),
                             (['a30-00','a31-00'],'same-native-pixels')]:
        first=identifiers[0];w,h=canonical[first]['width'],canonical[first]['height']
        if first=='a15-00':assert sum(x!=y for x,y in zip(decoded[first],decoded[identifiers[1]]))==57
        exclusions=[]
        for k in identifiers:
            for refinement in records[k]['refinements']:
                exclusions.extend(refinement.get('native_rects',[]))
                if 'native_rect' in refinement:exclusions.append(refinement['native_rect'])
                if 'logo_rect' in refinement:exclusions.append(refinement['logo_rect'])
        for i in range(w*h):
            if mode=='first-52-rows' and i//w>=52:continue
            if any(in_rect(i,w,rect) for rect in exclusions):continue
            if not all(decoded[k][i]==decoded[first][i] for k in identifiers):continue
            assert all(block(pictures[k],w,i)==block(pictures[first],w,i) for k in identifiers),'跨圖庫靜態區'
            stable+=1
    body=['a33-02','a33-03','a33-04'];w,h=66,32;arc=set()
    for k in body:
        changed={i for i,(x,y) in enumerate(zip(decoded[body[0]],decoded[k])) if x!=y}
        assert all(decoded[k][i] in {14,195} for i in changed)
        for i in changed:
                arc.update((i//w+dy)*w+i%w+dx for dy in [-1,0,1] for dx in [-1,0,1]
                    if 0<=i//w+dy<h and 0<=i%w+dx<w)
    same_character=0
    for i in range(w*h):
        if i in arc:continue
        assert all(block(pictures[k],w,i)==block(pictures[body[0]],w,i) for k in body),'原同角色'
        same_character+=1
    # 有效反例改實際像素；不只破壞檔案雜湊。
    negatives=[]
    k='r33-07';w=canonical[k]['width'];i=next(i for i,v in enumerate(decoded[k]) if v==0)
    modified=bytearray(pictures[k]);at=((i//w*4)*w*4+i%w*4)*4;modified[at]=1
    rejects(lambda:check_background(modified,decoded[k],w,[0,0,0],0,'原黑場'),'原黑場');negatives.append('黑場增加亮點')
    k='r52-00';w=canonical[k]['width'];i=next(i for i,v in enumerate(decoded[k]) if v==255)
    modified=bytearray(pictures[k]);at=((i//w*4)*w*4+i%w*4)*4;modified[at]^=1
    outer=outside_background(decoded[k],w,canonical[k]['height'])
    rejects(lambda:check_background(modified,decoded[k],w,p0[255],255,'原255外背景',outer),'原255外背景');negatives.append('原255外背景增加圖像')
    altered=set(records)-{'r52-07'};rejects(lambda:check_registry(altered,set(canonical)-EXISTING),'相位登錄');negatives.append('八方向缺一相位')
    k='a20-00';w=canonical[k]['width'];modified=bytearray(pictures[k]);modified[0]^=1
    altered=dict(pictures);altered[k]=modified
    rejects(lambda:check_street_prefix(altered,w),'同街景背景');negatives.append('同街景背景改色')
    result={'schema':1,'issue':32,'stage':'DRAFT','prototype_sha256':sha((a.prototype/'manifest.json').read_bytes()),
        'source_images_decoded':len(inventory['images']),'canonical_sources':len(canonical),'art_images':len(records),
        'existing_ui_noto':sorted(EXISTING),'source_255_blocks':white_blocks,'native_blackout_blocks':black_blocks,
        'generation_metadata_verified':generations,'a16_background_reused_from':'a15-00',
        'cross_member_static_blocks':stable,'same_character_blocks':same_character,'effective_negative_controls':negatives,
        'tool_sha256':sha(Path(__file__).read_bytes()),'normal_gui':False,'production_ready':False,
        'scope':'來源／尺寸／背景與明列相位條件；非整體美術認可、正常GUI或發布色盤驗收'}
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('PASS DRAFT',len(records),'images;',white_blocks,'255 blocks;',black_blocks,'blackout blocks;',stable,'static blocks;',sha(a.out.read_bytes()))


if __name__=='__main__':main()
