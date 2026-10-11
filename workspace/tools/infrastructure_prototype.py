"""#44／026 DRAFT：完整來源的四權重幾何與 B 材質離線比較。"""
import argparse
import hashlib
import json
import math
import os
import platform
import struct
import zipfile
import zlib
from pathlib import Path

from hd_file_dialogs_check import rgba
from hd_source_audit import cell

MATERIAL_SHA = {
    'water':'c5946a794cb44daea5e1492ecd880a0e2bb42e9ebe6da62e472a651abfa26015',
    'sand':'90c23e56f9c8a116fbe8cc7d8b2c1a494eb7044d3ff57c3ff28a60f5b911717f',
    'forest':'0bb1f136ce10e014e27626ab11dc5f3c18431fdcb9c6ab8fbd063b478e8644f7',
    'asphalt':'61057d15840d65801652de6af95b1b27b56706d67774a66f41bec3fb852cd384',
}
SIZE = 1254
ASPHALT_FREQUENCY = 4
CANDIDATES = list(range(15,30))+list(range(43,56))+list(range(60,75))


def sha(raw):return hashlib.sha256(raw).hexdigest()


def png(raw,width,height):
    # #45：決定性 RGBA PNG；不寫 tIME／date metadata。
    assert len(raw)==width*height*4
    def chunk(kind,data):
        return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    rows=b''.join(b'\0'+raw[y*width*4:(y+1)*width*4] for y in range(height))
    return (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,6,0,0,0))
        +chunk(b'IDAT',zlib.compress(rows,9))+chunk(b'IEND',b''))


def geometry(pixels):
    indices,weights = bytearray(),bytearray()
    for y in range(36):
        for x in range(36):
            nx,ny = (x+.5)/4-.5,(y+.5)/4-.5
            left,top = math.floor(nx),math.floor(ny)
            fx,fy = nx-left,ny-top
            # 三次平滑過渡保留中心，縮窄薄線的混色帶。
            fx,fy = fx*fx*(3-2*fx),fy*fy*(3-2*fy)
            parts = {}
            for dx,dy,w in [(0,0,(1-fx)*(1-fy)),(1,0,fx*(1-fy)),(0,1,(1-fx)*fy),(1,1,fx*fy)]:
                index = pixels[min(8,max(0,top+dy))*9+min(8,max(0,left+dx))]
                parts[index] = parts.get(index,0)+w
            values = sorted(parts)
            quantized = [int(parts[i]*255) for i in values]
            for at in sorted(range(len(values)),key=lambda n:(-(parts[values[n]]*255-quantized[n]),values[n]))[:255-sum(quantized)]:
                quantized[at] += 1
            indices.extend(values+[0]*(4-len(values)))
            weights.extend(quantized+[0]*(4-len(values)))
    assert len(indices)==len(weights)==1296*4
    assert all(sum(weights[i:i+4])==255 for i in range(0,len(weights),4))
    for y in range(9):
        for x in range(9):
            for dy in [1,2]:
                for dx in [1,2]:
                    at = ((y*4+dy)*36+x*4+dx)*4
                    dominant = max(range(4),key=lambda n:weights[at+n])
                    assert indices[at+dominant] == pixels[y*9+x]
    return indices,weights


def material(index):
    if 103<=index<=107:return 'forest',700+(index-103)*100
    if 144<=index<=147:return 'water',950+(index-144)*25
    if 201<=index<=204:return 'sand',940+(index-201)*25
    if index==21:return 'asphalt',1000
    return '',1000


def mirror(value):
    value %= 2*SIZE
    return 2*SIZE-1-value if value>=SIZE else value


def shader(index,wx,wy,palette,textures):
    name,factor = material(index)
    at = (mirror(wy)*SIZE+mirror(wx))*4
    asphalt_at = (mirror(wy*ASPHALT_FREQUENCY)*SIZE+mirror(wx*ASPHALT_FREQUENCY))*4
    if name=='asphalt':at=asphalt_at
    if name:
        return tuple(min(255,v*factor//1000) for v in textures[name][at:at+3])
    # 色號來源決定輪廓及明暗；新筆觸只改呈現，不命名遊戲用途。
    grain = sum(textures['asphalt'][asphalt_at:asphalt_at+3])-225
    if index==15:base=(24200,23900,22400)
    elif index==0:base=(1500,2300,2700)
    else:
        r,g,b = palette[index]
        if r==g==b:base=(r*95+1000,g*100+1400,b*100+2000)
        else:base=(r*90+800,g*90+800,b*90+800)
    def nearest(value):
        q,r = divmod(value,300)
        return q+(r>150 or (r==150 and q%2==1))
    return tuple(max(0,min(255,nearest(v*3+grain*10))) for v in base)


def render(data,world,palette,textures):
    indices,weights = data
    result = bytearray(36*36*4)
    for y in range(36):
        for x in range(36):
            at = (y*36+x)*4
            colors = [shader(indices[at+i],world[0]+x,world[1]+y,palette,textures) if weights[at+i] else (0,0,0) for i in range(4)]
            result[at:at+4] = bytes([sum(colors[i][c]*weights[at+i] for i in range(4))//255 for c in range(3)]+[255])
    return result


def native(frame,palette):
    result = bytearray()
    for y in range(200):
        row = b''.join(bytes(palette[i]+[255])*4 for i in frame[y*320:(y+1)*320])
        result.extend(row*4)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--catalog',type=Path,required=True)
    ap.add_argument('--materials',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--receipt',type=Path,nargs='*',default=[])
    args = ap.parse_args()
    assert not args.out.exists() and args.out.parent.stat().st_uid==os.getuid()
    args.out.mkdir()
    catalog = json.loads(args.catalog.read_text())
    palette,textures = catalog['palette'],{}
    for name,expected in MATERIAL_SHA.items():
        path = args.materials/(name+'-b-v1.png')
        assert sha(path.read_bytes())==expected
        textures[name] = rgba(path,(SIZE,SIZE))
    geometries,records = {},[]
    contact = bytearray(bytes([32,38,48,255])*(12*72)*(4*72))
    for ordinal,index in enumerate(CANDIDATES):
        source = catalog['target'][index]
        assert source['source']['image']==index
        pixels = bytes.fromhex(source['pixels_hex'])
        assert len(pixels)==81 and sha(pixels)==source['pixels_sha256']
        data = geometry(pixels)
        geometries[pixels] = data
        prefix = f'39-{index:03d}'
        for suffix,raw in zip(['indices.bin','weights.bin'],data):
            (args.out/(prefix+'-'+suffix)).write_bytes(raw)
        image = render(data,(0,0),palette,textures)
        (args.out/(prefix+'.png')).write_bytes(png(image,36,36))
        ox,oy = ordinal%12*72+18,ordinal//12*72+8
        for y in range(36):
            at = ((oy+y)*12*72+ox)*4
            contact[at:at+144] = image[y*144:(y+1)*144]
        records.append({'member':39,'image':index,'source_sha256':sha(pixels),'aliases':source['aliases'],
            'index_bytes':sha(data[0]),'weight_bytes':sha(data[1]),'png_sha256':sha((args.out/(prefix+'.png')).read_bytes())})
    (args.out/'candidate-sheet.png').write_bytes(png(contact,12*72,4*72))
    phase_proofs = []
    for index in [15,25,45,55,60,70]:
        source = bytes.fromhex(catalog['target'][index]['pixels_hex'])
        for number,world in enumerate([(0,0),(1250,1250),(-40,-40),(1260,-1260)]):
            name = f'phase-39-{index:03d}-{number}.png'
            raw = png(render(geometries[source],world,palette,textures),36,36)
            (args.out/name).write_bytes(raw)
            phase_proofs.append({'image':index,'world':list(world),'png':name,'png_sha256':sha(raw)})
    proofs = []
    for receipt in args.receipt:
        with zipfile.ZipFile(receipt) as z:
            s,frame = json.loads(z.read('status.json')),z.read('frame-index.bin')
        assert sha(frame)==s['frame_index_sha256']
        # 正常十字研究不捲動；原點仍取實際收據，不注入原版。
        origin = s['map_origin']
        assert origin['Valid']
        canvas = native(frame,s['palette'])
        painted = []
        for y in range(15):
            for x in range(29):
                pixels = cell(frame,5+x*9,34+y*9)
                if pixels not in geometries:continue
                image = render(geometries[pixels],((origin['X']+x)*36,(origin['Y']+y)*36),s['palette'],textures)
                ox,oy = 20+x*36,136+y*36
                for dy in range(36):
                    at = ((oy+dy)*1280+ox)*4
                    canvas[at:at+144] = image[dy*144:(dy+1)*144]
                painted.append({'cell':[x,y],'source_sha256':sha(pixels)})
        assert painted
        name = receipt.name.replace('-capture.zip','-offline-prototype.png')
        (args.out/name).write_bytes(png(canvas,1280,800))
        proofs.append({'receipt':str(receipt),'receipt_sha256':sha(receipt.read_bytes()),'origin':origin,
            'png':name,'painted':painted,'scope':'原版正常收據的離線候選組合，非正式 GUI HD 收據'})
    result = {'schema':1,'issue':44,'status':'DRAFT','geometry_version':3,'asphalt_frequency':ASPHALT_FREQUENCY,
        'tool':f'infrastructure_prototype.py / Python {platform.python_version()}',
        'png_encoder':{'format':'RGBA8 / filter 0 / zlib level 9 / IHDR IDAT IEND',
            'zlib_compile':zlib.ZLIB_VERSION,'zlib_runtime':zlib.ZLIB_RUNTIME_VERSION},
        'tool_image':'sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3',
        'inputs':catalog['inputs'],'address_space':catalog['address_space'],
        'source_catalog_sha256':sha(args.catalog.read_bytes()),
        'materials':MATERIAL_SHA,'shader':'integer per-mille factors; exact nearest-even grain; integer blend / 255',
        'geometry':'cubic smoothstep / four indexed samples / weights sum 255 / source centers retained',
        'candidate_images':records,'proofs':proofs,'phase_proofs':phase_proofs,
        'scope':'候選幾何與素材，不代表完整來源、正式接入或全部道路 HD 完成'}
    (args.out/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'candidates':len(records),'source_centers_retained':len(records)*81*4,'normal_source_proofs':len(proofs)},ensure_ascii=False))


if __name__=='__main__':
    main()
