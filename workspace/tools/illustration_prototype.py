#!/usr/bin/env python3
"""039 DRAFT：整組美術固定尺寸、相位靜態區一致與小形狀精修。"""
import argparse
import json
import math
import os
from pathlib import Path
import struct
import subprocess

from full_asset_catalog import sha
from hd_file_dialogs_check import rgba
from infrastructure_prototype import png,shader,MATERIAL_SHA,SIZE


def smooth_patch(pixels,width,height,palette,textures,background):
    out=bytearray(width*height*16*4)
    for y in range(height*4):
        for x in range(width*4):
            nx,ny=(x+.5)/4-.5,(y+.5)/4-.5;left,top=math.floor(nx),math.floor(ny)
            fx,fy=nx-left,ny-top;fx,fy=fx*fx*(3-2*fx),fy*fy*(3-2*fy)
            total=[0.,0.,0.];alpha=0.
            for dx,dy,weight in [(0,0,(1-fx)*(1-fy)),(1,0,fx*(1-fy)),(0,1,(1-fx)*fy),(1,1,fx*fy)]:
                index=pixels[min(height-1,max(0,top+dy))*width+min(width-1,max(0,left+dx))]
                if index not in {0,9,20,32,38,41,71,153,168,169,175,184}:continue
                color=shader(index,x,y,palette,textures)
                alpha+=weight
                for c in range(3):total[c]+=color[c]*weight
            at=(y*width*4+x)*4
            out[at:at+4]=bytes([max(0,min(255,int(v+background[at+c]*(1-alpha)))) for c,v in enumerate(total)]+[255])
    return out


def trim_unambiguous(raw,width,height,reference,rw,rh):
    # 只移除參考外緣沒有的完全單色外框；不裁圖片內部或真正純色背景。
    def uniform(data):
        return bool(data) and all(max(data[c::4])-min(data[c::4])<=5 for c in range(4))
    top,bottom,left,right=0,height,0,width
    reference_top=reference[:rw*4];reference_bottom=reference[(rh-1)*rw*4:]
    if not uniform(reference_top):
        while top<height//8 and uniform(raw[top*width*4:(top+1)*width*4]):top+=1
    if not uniform(reference_bottom):
        while bottom>height*7//8 and uniform(raw[(bottom-1)*width*4:bottom*width*4]):bottom-=1
    def column(data,w,h,x):return b''.join(data[(y*w+x)*4:(y*w+x+1)*4] for y in range(h))
    if not uniform(column(reference,rw,rh,0)):
        while left<width//8 and uniform(column(raw,width,height,left)):left+=1
    if not uniform(column(reference,rw,rh,rw-1)):
        while right>width*7//8 and uniform(column(raw,width,height,right-1)):right-=1
    cropped=b''.join(raw[(y*width+left)*4:(y*width+right)*4] for y in range(top,bottom))
    return cropped,right-left,bottom-top,[left,top,right-left,bottom-top]


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--inputs',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    assert not a.out.exists() and a.out.parent.stat().st_uid==os.getuid()
    a.out.mkdir();groups=a.inputs/'groups';records=[]
    material_root=a.inputs.parent;textures={}
    for name,want in MATERIAL_SHA.items():
        path=material_root/(name+'-b-v1.png');assert sha(path.read_bytes())==want;textures[name]=rgba(path,(SIZE,SIZE))
    m=json.loads((material_root/'map-completion-v1/inventory.json').read_text());palette=[m['palette'][str(i)] for i in range(256)]
    for root in sorted(groups.iterdir()):
        if not root.is_dir() or not (root/'generation.json').exists():continue
        layout=json.loads((root/'layout.json').read_text())
        selection=json.loads((root/'selection.json').read_text()) if (root/'selection.json').exists() else {'generation':'generation.json','image':'generated.png'}
        assert all(Path(selection[k]).name==selection[k] for k in ['generation','image'])
        gpath=root/selection['generation'];g=json.loads(gpath.read_text())
        generated=root/selection['image'];assert sha(generated.read_bytes())==g['generated_sha256']
        assert sha((root/'layout.json').read_bytes())==g['layout_sha256']
        width,height=struct.unpack_from('>II',generated.read_bytes(),16)
        raw=rgba(generated,(width,height));rw,rh=layout['native_size'];reference=rgba(root/'source.png',(rw,rh))
        trimmed,tw,th,crop=trim_unambiguous(raw,width,height,reference,rw,rh)
        normalized=subprocess.check_output(['convert','-size',f'{tw}x{th}','-depth','8','rgba:-','-filter','Lanczos','-resize',f'{rw*4}x{rh*4}!','-depth','8','rgba:-'],input=trimmed)
        assert len(normalized)==rw*rh*64 and set(normalized[3::4])=={255}
        base=None;originals=[];pictures=[]
        for cell in layout['cells']:
            x,y,w,h=cell['rect'];pixels=(a.inputs/cell['id']/'source.bin').read_bytes();assert sha(pixels)==cell['source_sha256']
            picture=bytearray(b''.join(normalized[((y*4+dy)*rw*4+x*4)*4:((y*4+dy)*rw*4+x*4+w*4)*4] for dy in range(h*4)))
            originals.append(pixels);pictures.append(picture)
        same_shape=len({tuple(c['rect'][2:]) for c in layout['cells']})==1
        stable=0
        if same_shape and len(pictures)>1:
            w,h=layout['cells'][0]['rect'][2:];base=pictures[0]
            for i in range(w*h):
                if not all(p[i]==originals[0][i] for p in originals):continue
                stable+=1;x,y=i%w,i//w
                for picture in pictures[1:]:
                    for dy in range(4):
                        at=((y*4+dy)*w*4+x*4)*4;picture[at:at+16]=base[at:at+16]
        refinements=[]
        if root.name in {f'r{i}' for i in range(42,52)}:
            # 原圖小形狀保持抽象，不讓模型加造手持物或猜角色用途。
            x,y,w,h=48,52,72,22
            assert g.get('background_plate'),'先由imagegen移除猜造人物道具，才覆原形狀'
            for i,picture in enumerate(pictures):
                width=layout['cells'][i]['rect'][2];rawpatch=b''.join(originals[i][(y+dy)*width+x:(y+dy)*width+x+w] for dy in range(h))
                background=b''.join(picture[((y*4+dy)*width*4+x*4)*4:((y*4+dy)*width*4+x*4+w*4)*4] for dy in range(h*4))
                patch=smooth_patch(rawpatch,w,h,palette,textures,background)
                for dy in range(h*4):
                    at=((y*4+dy)*width*4+x*4)*4;picture[at:at+w*16]=patch[dy*w*16:(dy+1)*w*16]
            refinements.append({'native_rect':[x,y,w,h],'method':'原始形狀四權重細化與已驗B材質，不猜人物／道具'})
        for cell,picture in zip(layout['cells'],pictures):
            w,h=cell['rect'][2:];encoded=png(picture,w*4,h*4);(a.out/(cell['id']+'.png')).write_bytes(encoded)
            records.append({'id':cell['id'],'group':root.name,'size':[w*4,h*4],'png_sha256':sha(encoded),
                'source_sha256':cell['source_sha256'],'generation_sha256':sha(gpath.read_bytes()),
                'removed_outer_rect':crop,'stable_native_pixels':stable,'refinements':refinements})
    assert records
    result={'schema':1,'stage':'DRAFT','issue':32,'images':records,'count':len(records),
        'tool_sha256':sha(Path(__file__).read_bytes()),'scope':'只供整圖／相位與原始形狀比較，不是READY或產品資產'}
    (a.out/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('DRAFT',len(records),'complete phase images',sha((a.out/'manifest.json').read_bytes()))


if __name__=='__main__':main()
