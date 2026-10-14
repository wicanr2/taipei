#!/usr/bin/env python3
"""039 DRAFT：整組美術固定尺寸、相位靜態區一致與小形狀精修。"""
import argparse
from collections import deque
import json
import math
import os
from pathlib import Path
import struct
import subprocess

from full_asset_catalog import sha
from hd_file_dialogs_check import rgba
from infrastructure_prototype import png,shader,MATERIAL_SHA,SIZE


def smooth_patch(pixels,width,height,palette,textures,background,indices=None,preview=False):
    out=bytearray(width*height*16*4)
    for y in range(height*4):
        for x in range(width*4):
            nx,ny=(x+.5)/4-.5,(y+.5)/4-.5;left,top=math.floor(nx),math.floor(ny)
            fx,fy=nx-left,ny-top;fx,fy=fx*fx*(3-2*fx),fy*fy*(3-2*fy)
            total=[0.,0.,0.];alpha=0.
            for dx,dy,weight in [(0,0,(1-fx)*(1-fy)),(1,0,fx*(1-fy)),(0,1,(1-fx)*fy),(1,1,fx*fy)]:
                index=pixels[min(height-1,max(0,top+dy))*width+min(width-1,max(0,left+dx))]
                if indices is not None and index not in indices:continue
                if preview and index==99:
                    color=shader(105,x,y,palette,textures)
                elif preview and index==208:
                    at=((y%SIZE)*SIZE+x%SIZE)*4;sample=textures['sand'][at:at+3]
                    factor=(sample[0]*3+sample[1]*6+sample[2])*1000//1800
                    color=tuple(min(255,v*max(650,min(1250,factor))//1000) for v in palette[index])
                else:color=shader(index,x,y,palette,textures)
                alpha+=weight
                for c in range(3):total[c]+=color[c]*weight
            at=(y*width*4+x)*4
            out[at:at+4]=bytes([max(0,min(255,int(v+background[at+c]*(1-alpha)))) for c,v in enumerate(total)]+[255])
    return out


# 這些矩形逐張由原始完整圖確認，只供DRAFT美術合成，不是執行器座標。
FOREGROUND_RECTS={
    'r42':[(48,52,72,22)],'r43':[(48,52,72,22)],'r44':[(48,52,76,25),(13,43,16,10)],
    'r45':[(51,42,73,29),(123,59,14,14)],'r46':[(63,42,61,21)],
    'r47':[(63,49,61,23),(12,51,9,9)],'r48':[(49,52,65,19)],
    'r49':[(59,48,58,27)],'r50':[(61,53,53,19)],'r51':[(61,53,53,19)],
}


def source_refine(picture,pixels,width,rect,palette,textures,indices=None):
    x,y,w,h=rect
    assert x>=0 and y>=0 and x+w<=width and (y+h)*width<=len(pixels)
    rawpatch=b''.join(pixels[(y+dy)*width+x:(y+dy)*width+x+w] for dy in range(h))
    background=b''.join(picture[((y*4+dy)*width*4+x*4)*4:((y*4+dy)*width*4+x*4+w*4)*4] for dy in range(h*4))
    patch=smooth_patch(rawpatch,w,h,palette,textures,background,indices)
    for dy in range(h*4):
        at=((y*4+dy)*width*4+x*4)*4;picture[at:at+w*16]=patch[dy*w*16:(dy+1)*w*16]


def outer_255(pixels,width,height):
    # 只處理連到圖片外邊的空白；raw內部的白眼／白紙仍可有B筆觸。
    points=set(range(width))|set(range((height-1)*width,height*width))
    points|={y*width+x for y in range(height) for x in [0,width-1]}
    found={i for i in points if pixels[i]==255};queue=deque(found)
    while queue:
        i=queue.popleft();x,y=i%width,i//width
        for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx,ny=x+dx,y+dy
            if not (0<=nx<width and 0<=ny<height):continue
            n=ny*width+nx
            if pixels[n]==255 and n not in found:found.add(n);queue.append(n)
    return found


def trim_unambiguous(raw,width,height,reference,rw,rh,max_fraction=.125):
    # 只移除參考外緣沒有的完全單色外框；不裁圖片內部或真正純色背景。
    def uniform(data):
        return bool(data) and all(max(data[c::4])-min(data[c::4])<=5 for c in range(4))
    def removable(candidate,edge):
        matte=[48,54,60]
        is_matte=lambda data:all(abs(data[i+c]-matte[c])<=24 for i in range(0,len(data),4) for c in range(3))
        # 原邊包含黑框與灰間隙；新增整列灰漸層沒有原黑框。
        if is_matte(candidate) and not is_matte(edge):return True
        if not uniform(candidate):return False
        if not uniform(edge):return True
        # 真正純色背景保留。只在原黑框外辨識額外白色畫布。
        return min(edge[:3])<16 and all(min(candidate[i:i+3])>=245 for i in range(0,len(candidate),4))
    top,bottom,left,right=0,height,0,width
    reference_top=reference[:rw*4];reference_bottom=reference[(rh-1)*rw*4:]
    while top<int(height*max_fraction) and removable(raw[top*width*4:(top+1)*width*4],reference_top):top+=1
    while bottom>height*(1-max_fraction) and removable(raw[(bottom-1)*width*4:bottom*width*4],reference_bottom):bottom-=1
    def column(data,w,h,x):return b''.join(data[(y*w+x)*4:(y*w+x+1)*4] for y in range(h))
    while left<int(width*max_fraction) and removable(column(raw,width,height,left),column(reference,rw,rh,0)):left+=1
    while right>width*(1-max_fraction) and removable(column(raw,width,height,right-1),column(reference,rw,rh,rw-1)):right-=1
    assert left<right and top<bottom
    cropped=b''.join(raw[(y*width+left)*4:(y*width+right)*4] for y in range(top,bottom))
    return cropped,right-left,bottom-top,[left,top,right-left,bottom-top]


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--inputs',type=Path,required=True)
    ap.add_argument('--original',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    assert not a.out.exists() and a.out.parent.stat().st_uid==os.getuid()
    a.out.mkdir();groups=a.inputs/'groups';records=[];all_pictures={};all_sources={}
    material_root=a.inputs.parent;textures={}
    for name,want in MATERIAL_SHA.items():
        path=material_root/(name+'-b-v1.png');assert sha(path.read_bytes())==want;textures[name]=rgba(path,(SIZE,SIZE))
    m=json.loads((material_root/'map-completion-v1/inventory.json').read_text());palette0=[m['palette'][str(i)] for i in range(256)]
    roma=(a.original/'RS201A.ROM').read_bytes()
    assert sha(roma)=='5d66f238dce650b8a407986100392ee4b8ac2aa23a033e80a7ca18ed91b3d9b0'
    off,size=struct.unpack_from('<IH',roma,18+3*16);assert size==768
    expand=lambda v:(v>>2)*4|((v>>2)>>4)
    palette3=[list(map(expand,roma[off+i:off+i+3])) for i in range(0,768,3)]
    inventory=json.loads((a.inputs/'inventory.json').read_text())
    canonical={r['id']:r for r in inventory['images'] if r['id']==r['canonical']}
    for root in sorted(groups.iterdir()):
        if not root.is_dir() or not (root/'generation.json').exists():continue
        palette=palette3 if root.name.startswith('a') else palette0
        layout=json.loads((root/'layout.json').read_text())
        selection=json.loads((root/'selection.json').read_text()) if (root/'selection.json').exists() else {'generation':'generation.json','image':'generated.png'}
        assert all(Path(selection[k]).name==selection[k] for k in ['generation','image'])
        gpath=root/selection['generation'];g=json.loads(gpath.read_text())
        generated=root/selection['image'];assert sha(generated.read_bytes())==g['generated_sha256']
        assert sha((root/'layout.json').read_bytes())==g['layout_sha256']
        width,height=struct.unpack_from('>II',generated.read_bytes(),16)
        raw=rgba(generated,(width,height));rw,rh=layout['native_size'];reference=rgba(root/'source.png',(rw,rh))
        # a32的原參考上下邊有貫穿間隙；生成圖加了約三成純白上下邊。
        # 保留近單色／參考閘門，只放寬此極窄圖的外框上限。
        trimmed,tw,th,crop=trim_unambiguous(raw,width,height,reference,rw,rh,.49 if root.name=='a32' else .125)
        normalized=subprocess.check_output(['convert','-size',f'{tw}x{th}','-depth','8','rgba:-','-filter','Lanczos','-resize',f'{rw*4}x{rh*4}!','-depth','8','rgba:-'],input=trimmed)
        assert len(normalized)==rw*rh*64 and set(normalized[3::4])=={255}
        base=None;originals=[];pictures=[]
        for cell in layout['cells']:
            x,y,w,h=cell['rect'];pixels=(a.inputs/cell['id']/'source.bin').read_bytes();assert sha(pixels)==cell['source_sha256']
            picture=bytearray(b''.join(normalized[((y*4+dy)*rw*4+x*4)*4:((y*4+dy)*rw*4+x*4+w*4)*4] for dy in range(h*4)))
            originals.append(pixels);pictures.append(picture)
        stable=0
        refinements=[]
        if root.name in FOREGROUND_RECTS:
            # 原圖小形狀保持抽象，不讓模型加造手持物或猜角色用途。
            assert g.get('background_plate'),'先由imagegen移除猜造人物道具，才覆原形狀'
            excluded={84,85,87,102}|set(range(192,211))
            if root.name=='r49':excluded.remove(194)
            indices=set(range(255))-excluded
            # 背景板整張共用。色號偶然相同不代表角色部位可拼貼。
            base=pictures[0][:];pictures=[bytearray(base) for p in pictures]
            differences={i for i,(x,y) in enumerate(zip(originals[0],originals[1])) if x!=y}
            for i,picture in enumerate(pictures):
                width=layout['cells'][i]['rect'][2]
                selected={j for j,v in enumerate(originals[i]) if v in indices and
                    any(x<=j%width<x+w and y<=j//width<y+h for x,y,w,h in FOREGROUND_RECTS[root.name])}
                # 大磚堆的原紅色不混進前景遮罩；小中央磚堆仍保留。
                selected-={j for j in selected if originals[i][j] in {32,38,41} and (j%width<54 or j%width>=124)}
                # 完整相位差異保留膚色、灰道具、飛行小形狀與地面微粒。
                selected|={j for j in differences if originals[i][j] not in {84,85,87,102,255}}
                stencil=bytes(v if j in selected else 255 for j,v in enumerate(originals[i]))
                x=min(j%width for j in selected);y=min(j//width for j in selected)
                w=max(j%width for j in selected)-x+1;h=max(j//width for j in selected)-y+1
                source_refine(picture,stencil,width,(x,y,w,h),palette,textures,set(range(255)))
            refinements.append({'native_rects':FOREGROUND_RECTS[root.name],'indices':sorted(indices),
                'full_source_delta_pixels':len(differences),
                'method':'共用B背景板加原始前景與完整相位差異，不以同色拼貼人物'})
        for cell,picture in zip(layout['cells'],pictures):
            w,h=cell['rect'][2:];all_pictures[cell['id']]=picture;all_sources[cell['id']]=(a.inputs/cell['id']/'source.bin').read_bytes()
            records.append({'id':cell['id'],'group':root.name,'size':[w*4,h*4],
                'source_sha256':cell['source_sha256'],'generation_sha256':sha(gpath.read_bytes()),
                'removed_outer_rect':crop,'stable_native_pixels':stable,'refinements':list(refinements)})
    # 兩門樓沿既有生成版本；七張預覽與游標用已驗B材質細化原始色形。
    for identifier in ['a04-00','a05-00',*[f'r{i:02d}-00' for i in range(4,11)],'a35-00']:
        source=canonical[identifier];w,h=source['width'],source['height']
        pixels=(a.inputs/identifier/'source.bin').read_bytes();assert sha(pixels)==source['pixels_sha256']
        palette=palette3 if identifier.startswith('a') else palette0
        refinements=[];generation_sha=None;crop=None
        if identifier in {'a04-00','a05-00'}:
            root=a.inputs/identifier;gpath=root/'generation-v2.json';g=json.loads(gpath.read_text())
            generated=root/'generated-v2.png';assert sha(generated.read_bytes())==g['generated_sha256']
            gw,gh=struct.unpack_from('>II',generated.read_bytes(),16);raw=rgba(generated,(gw,gh))
            reference=rgba(root/'source.png',(w,h));trimmed,tw,th,crop=trim_unambiguous(raw,gw,gh,reference,w,h)
            picture=bytearray(subprocess.check_output(['convert','-size',f'{tw}x{th}','-depth','8','rgba:-',
                '-filter','Lanczos','-resize',f'{w*4}x{h*4}!','-depth','8','rgba:-'],input=trimmed))
            generation_sha=sha(gpath.read_bytes())
            if identifier=='a04-00':
                rect=(130,35,44,16);source_refine(picture,pixels,w,rect,palette,textures)
                refinements.append({'native_rect':rect,'method':'完整原匾額色形細化，不猜Unicode'})
        else:
            picture=smooth_patch(pixels,w,h,palette,textures,bytes(w*h*64),preview=identifier.startswith('r'))
            refinements.append({'method':'已驗B材質與完整原始色號輪廓四權重細化','material_sha256':MATERIAL_SHA})
        assert len(picture)==w*h*64
        all_pictures[identifier]=picture;all_sources[identifier]=pixels
        records.append({'id':identifier,'group':identifier[:3],'size':[w*4,h*4],
            'source_sha256':sha(pixels),'generation_sha256':generation_sha,
            'removed_outer_rect':crop,'stable_native_pixels':0,'refinements':refinements})

    by_id={r['id']:r for r in records}
    # 已逐byte確認的同一畫面，避免重複生成讓背景或手部抖動。
    for identifiers,mode in [([f'a{i:02d}-00' for i in range(19,23)],'first-52-rows'),
                             (['a30-00','a31-00'],'same-native-pixels')]:
        first=identifiers[0];w,h=canonical[first]['width'],canonical[first]['height']
        assert all((canonical[k]['width'],canonical[k]['height'])==(w,h) for k in identifiers)
        count=0
        for i in range(w*h):
            if mode=='first-52-rows' and i//w>=52:continue
            equal=all(all_sources[k][i]==all_sources[first][i] for k in identifiers)
            if mode=='first-52-rows':assert equal
            if not equal:continue
            count+=1;x,y=i%w,i//w
            for k in identifiers[1:]:
                for dy in range(4):
                    at=((y*4+dy)*w*4+x*4)*4
                    all_pictures[k][at:at+16]=all_pictures[first][at:at+16]
        for k in identifiers:by_id[k]['cross_member_stability']={'sources':identifiers,'mode':mode,'native_pixels':count}

    # 細小原形保留定位與色號，不用猜出的新字、動物徽飾或表情代替。
    decor={'r24-03':[(10,31,29,40)],'r24-04':[(16,40,16,18)],'a31-00':[(45,46,60,76)]}
    for identifier,rects in decor.items():
        w=canonical[identifier]['width'];palette=palette3 if identifier.startswith('a') else palette0
        for rect in rects:source_refine(all_pictures[identifier],all_sources[identifier],w,rect,palette,textures)
        by_id[identifier]['refinements'].append({'native_rects':rects,'method':'不明細紋／原字墨保留原色形，不猜造符號'})
    assert json.loads((groups/'a15/generation-v2.json').read_text())['background_plate']
    all_pictures['a16-00']=all_pictures['a15-00'][:]
    by_id['a16-00']['reused_background_generation_sha256']=by_id['a15-00']['generation_sha256']
    for identifier in ['a15-00','a16-00']:
        w=canonical[identifier]['width'];picture=all_pictures[identifier];pixels=all_sources[identifier]
        source_refine(picture,pixels,w,(76,23,57,27),palette3,textures,{6,*range(63,81)})
        rects=[(128,55,41,15),(136,71,11,5),(156,71,10,5),(138,77,5,6),(155,77,14,7)]
        for rect in rects:source_refine(picture,pixels,w,rect,palette3,textures,{0,12,15})
        by_id[identifier]['refinements'].append({'native_rects':rects,'logo_rect':[76,23,57,27],
            'method':'同B臉部背景板加原黑白眼鏡／眼睛／鼻口與斜體標誌，不覆整塊舊膚色'})
    white={i for i,c in enumerate(palette0) if min(c)>=210}
    for identifier in [f'r32-{i:02d}' for i in range(6)]:
        rects=[(5,0,23,22),(57,30,21,32),(35,47,10,12)]
        for rect in rects:source_refine(all_pictures[identifier],all_sources[identifier],80,rect,palette0,textures,white)
        by_id[identifier]['refinements'].append({'native_rects':rects,'indices':sorted(white),
            'method':'原白色旗面記號，不將模型十字當原符號'})
    # a33末三相位的角色底圖相同；弧線另含195號淡色羽化像素。
    # 僅取對無弧線相位的完整差異，不能把角色本身的195號膚色當弧線。
    assert json.loads((groups/'a33/generation-v3.json').read_text())['background_plate']
    character=all_pictures['a33-02'][:]
    for identifier in [f'a33-{i:02d}' for i in range(2,5)]:
        pixels=all_sources[identifier]
        changed={i for i,(x,y) in enumerate(zip(all_sources['a33-02'],pixels)) if x!=y}
        assert all(pixels[i] in {14,195} for i in changed)
        stencil=bytes(v if i in changed else 255 for i,v in enumerate(pixels))
        all_pictures[identifier]=bytearray(character)
        source_refine(all_pictures[identifier],stencil,66,(0,0,66,32),palette3,textures,{14,195})
        by_id[identifier]['refinements'].append({'native_rect':[0,0,66,32],'indices':[14,195],
            'source_delta_pixels':len(changed),'same_character_source':'a33-02',
            'method':'同角色B背景板加原弧線完整差異，含原195號淡色邊緣'})

    for r in records:
        identifier=r['id'];w,h=canonical[identifier]['width'],canonical[identifier]['height']
        picture=all_pictures[identifier];pixels=all_sources[identifier]
        palette=palette3 if identifier.startswith('a') else palette0
        # 255在raw可為不透明白，在IV2／透明呼叫才跳過。素材不猜呼叫。
        outer=outer_255(pixels,w,h)
        for i,index in enumerate(pixels):
            rgb=palette[index] if i in outer or identifier=='r33-07' and index==0 else None
            if rgb is None:continue
            x,y=i%w,i//w
            for dy in range(4):
                at=((y*4+dy)*w*4+x*4)*4;picture[at:at+16]=bytes(rgb+[255])*4
        encoded=png(picture,w*4,h*4);(a.out/(identifier+'.png')).write_bytes(encoded)
        r['png_sha256']=sha(encoded);r['palette_sha256']=sha(bytes(c for rgb in palette for c in rgb))
        r['outer_background_255_pixels']=len(outer)
        r['source_record']=canonical[identifier]
    excluded=set(canonical)-set(all_pictures)
    assert len(records)==179 and len(excluded)==18,(len(records),sorted(excluded))
    result={'schema':1,'stage':'DRAFT','issue':32,'images':records,'count':len(records),
        'tool_sha256':sha(Path(__file__).read_bytes()),
        'source_inventory_sha256':sha((a.inputs/'inventory.json').read_bytes()),
        'artist_groups':52,'excluded_existing_ui_noto':sorted(excluded),
        'scope':'179個完整原圖的DRAFT呈現，含169相位／兩門樓／七預覽／游標；不是READY或產品資產'}
    (a.out/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    (a.out/'executed-builder.py').write_bytes(Path(__file__).read_bytes())
    print('DRAFT',len(records),'complete phase images',sha((a.out/'manifest.json').read_bytes()))


if __name__=='__main__':main()
