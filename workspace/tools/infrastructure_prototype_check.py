"""#44／026：由唯讀 ROM、整數幾何與實際 PNG 獨立核對離線草案。"""
import argparse
import hashlib
import json
import platform
import shutil
import struct
import tempfile
import zipfile
from fractions import Fraction
from pathlib import Path

from hd_file_dialogs_check import rgba
from hd_chrome_negative import png

ROM_SHA = '0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29'
EXPECTED = list(range(15,30))+list(range(43,56))+list(range(60,75))
MATERIALS = {
    'water':'c5946a794cb44daea5e1492ecd880a0e2bb42e9ebe6da62e472a651abfa26015',
    'sand':'90c23e56f9c8a116fbe8cc7d8b2c1a494eb7044d3ff57c3ff28a60f5b911717f',
    'forest':'0bb1f136ce10e014e27626ab11dc5f3c18431fdcb9c6ab8fbd063b478e8644f7',
    'asphalt':'61057d15840d65801652de6af95b1b27b56706d67774a66f41bec3fb852cd384',
}


def sha(raw):return hashlib.sha256(raw).hexdigest()


def read_sources(rom):
    assert sha(rom)==ROM_SHA
    refs,tiles = {},{}
    for member,count in {34:96,35:96,36:96,37:96,38:180,39:75,40:180,41:180,59:135}.items():
        start,length = struct.unpack_from('<IH',rom,18+member*16)
        library = rom[start:start+length]
        assert struct.unpack_from('<H',library)[0]==count
        offsets = list(struct.unpack_from('<'+'H'*count,library,2))+[length]
        for i in range(count):
            a,b = offsets[i:i+2]
            assert b-a==85 and struct.unpack_from('<HH',library,a)==(9,9)
            pixels = library[a+4:b]
            ref = {'rom':'RS201.ROM','member':member,'image':i,'member_offset':a,
                'file_offset':start+a,'pixel_file_offset':start+a+4}
            refs.setdefault(pixels,[]).append(ref)
            if member==39:tiles[i]=pixels
    assert len(refs)==1049 and sum(map(len,refs.values()))==1134
    return tiles,refs


def lattice(pixels,x,y,version):
    # 與產生器的浮點座標不同，直接計算整數面積。
    ix,rx = divmod(2*x-3,8)
    iy,ry = divmod(2*y-3,8)
    scale = 8
    if version==3:
        rx,ry = rx*rx*(24-2*rx),ry*ry*(24-2*ry)
        scale = 512
    denominator = scale*scale
    counts = {}
    for nx,wx in [(ix,scale-rx),(ix+1,rx)]:
        for ny,wy in [(iy,scale-ry),(iy+1,ry)]:
            index = pixels[min(8,max(0,ny))*9+min(8,max(0,nx))]
            counts[index] = counts.get(index,0)+wx*wy
    indices = sorted(counts)
    values = [counts[i]*255//denominator for i in indices]
    ranked = sorted(range(len(indices)),key=lambda n:(-(counts[indices[n]]*255%denominator),indices[n]))
    for n in ranked[:255-sum(values)]:values[n]+=1
    return bytes(indices+[0]*(4-len(indices))),bytes(values+[0]*(4-len(values)))


def sample(index,x,y,palette,materials,frequency):
    # 獨立以 Fraction 定義色彩契約，避免複製產生器的浮點或整數捨入程式。
    def coord(value):
        q,r = divmod(value,1254)
        return r if q%2==0 else 1253-r
    at = (coord(y)*1254+coord(x))*4
    asphalt_at = (coord(y*frequency)*1254+coord(x*frequency))*4
    name,factor = '',Fraction(1)
    if 103<=index<=107:name,factor='forest',Fraction(7+index-103,10)
    elif 144<=index<=147:name,factor='water',Fraction(38+index-144,40)
    elif 201<=index<=204:name,factor='sand',Fraction(188+5*(index-201),200)
    elif index==21:name,at='asphalt',asphalt_at
    if name:return tuple(min(255,int(v*factor)) for v in materials[name][at:at+3])
    grain = Fraction(sum(materials['asphalt'][asphalt_at:asphalt_at+3])-225,30)
    if index==15:base=[Fraction(v) for v in (242,239,224)]
    elif index==0:base=[Fraction(v) for v in (15,23,27)]
    else:
        r,g,b = palette[index]
        if r==g==b:base=[Fraction(r*95,100)+10,Fraction(g+14),Fraction(b+20)]
        else:base=[Fraction(v*9,10)+8 for v in (r,g,b)]
    return tuple(max(0,min(255,round(v+grain))) for v in base)


def tile_image(source,world,palette,materials,version,frequency):
    out = bytearray()
    for y in range(36):
        for x in range(36):
            indices,weights = lattice(source,x,y,version)
            total = [0,0,0]
            for index,weight in zip(indices,weights):
                if not weight:continue
                for c,value in enumerate(sample(index,world[0]+x,world[1]+y,palette,materials,frequency)):
                    total[c]+=value*weight
            out.extend([v//255 for v in total]+[255])
    return out


def check(args):
    tiles,refs = read_sources(args.rom.read_bytes())
    catalog = json.loads(args.catalog.read_text())
    manifest = json.loads((args.prototype/'manifest.json').read_text())
    assert manifest['status']=='DRAFT' and manifest['source_catalog_sha256']==sha(args.catalog.read_bytes())
    assert manifest['materials']==MATERIALS
    version = manifest.get('geometry_version',2)
    assert version in (2,3)
    frequency = manifest.get('asphalt_frequency',1)
    assert frequency in (1,4)
    assert [r['image'] for r in manifest['candidate_images']]==EXPECTED
    materials = {}
    for name,want in MATERIALS.items():
        p = args.materials/(name+'-b-v1.png')
        assert sha(p.read_bytes())==want
        materials[name]=rgba(p,(1254,1254))
    by_source = {tiles[i]:i for i in EXPECTED}
    edges,centers,pixels = {},0,0
    for record in manifest['candidate_images']:
        i = record['image']
        source = tiles[i]
        assert record['member']==39 and record['source_sha256']==sha(source)
        assert record['aliases']==refs[source]
        assert catalog['target'][i]['pixels_hex']==source.hex()
        prefix = args.prototype/f'39-{i:03d}'
        indices,weights = [Path(str(prefix)+'-'+suffix+'.bin').read_bytes() for suffix in ('indices','weights')]
        assert len(indices)==len(weights)==36*36*4
        assert record['index_bytes']==sha(indices) and record['weight_bytes']==sha(weights)
        for y in range(36):
            for x in range(36):
                at = (y*36+x)*4
                expected = lattice(source,x,y,version)
                assert (indices[at:at+4],weights[at:at+4])==expected,(i,x,y,'geometry')
                assert sum(weights[at:at+4])==255
                pixels+=1
        for y in range(9):
            for x in range(9):
                for dy in (1,2):
                    for dx in (1,2):
                        at = ((y*4+dy)*36+x*4+dx)*4
                        assert indices[at+max(range(4),key=lambda n:weights[at+n])]==source[y*9+x]
                        centers+=1
        # 四向邊界夾限與相同原邊的幾何連續性。只驗來源幾何，不猜道路連接規則。
        for axis in (0,1):
            for end in (0,8):
                native_edge = bytes(source[v*9+end] if axis==0 else source[end*9+v] for v in range(9))
                hd_edge = []
                for v in range(36):
                    x,y = (end//8*35,v) if axis==0 else (v,end//8*35)
                    at = (y*36+x)*4
                    hd_edge.append((indices[at:at+4],weights[at:at+4]))
                key = axis,native_edge
                if key in edges:assert hd_edge==edges[key]
                else:edges[key]=hd_edge
        p = Path(str(prefix)+'.png')
        assert sha(p.read_bytes())==record['png_sha256']
        assert rgba(p,(36,36))==tile_image(source,(0,0),catalog['palette'],materials,version,frequency),(i,'whole tile raster')
    phase_records = manifest['phase_proofs']
    expected_phases = [(i,list(w)) for i in [15,25,45,55,60,70] for w in [(0,0),(1250,1250),(-40,-40),(1260,-1260)]]
    assert [(p['image'],p['world']) for p in phase_records]==expected_phases
    for proof in phase_records:
        p = args.prototype/proof['png']
        assert sha(p.read_bytes())==proof['png_sha256']
        expected = tile_image(tiles[proof['image']],proof['world'],catalog['palette'],materials,version,frequency)
        assert rgba(p,(36,36))==expected,('world material phase',proof['png'])
    normal,painted_total = [],0
    for proof in manifest['proofs']:
        path = Path(proof['receipt'])
        assert sha(path.read_bytes())==proof['receipt_sha256']
        with zipfile.ZipFile(path) as z:
            s,frame = json.loads(z.read('status.json')),z.read('frame-index.bin')
        assert len(frame)==64000 and sha(frame)==s['frame_index_sha256']
        origin = s['map_origin']
        assert origin['Valid'] and proof['origin']==origin
        expected = bytearray()
        for y in range(200):
            row = b''.join(bytes(s['palette'][i]+[255])*4 for i in frame[y*320:(y+1)*320])
            expected.extend(row*4)
        cells = []
        for row in range(15):
            for col in range(29):
                source = b''.join(frame[(34+row*9+y)*320+5+col*9:(34+row*9+y)*320+14+col*9] for y in range(9))
                if source not in by_source:continue
                world = ((origin['X']+col)*36,(origin['Y']+row)*36)
                tile = tile_image(source,world,s['palette'],materials,version,frequency)
                for y in range(36):
                    at = ((136+row*36+y)*1280+20+col*36)*4
                    expected[at:at+144]=tile[y*144:(y+1)*144]
                cells.append({'cell':[col,row],'source_sha256':sha(source)})
        assert cells==proof['painted'] and cells
        actual = rgba(args.prototype/proof['png'],(1280,800))
        assert actual==expected,(proof['png'],'完整 1280×800 及全部區外')
        painted_total+=len(cells)
        normal.append({'receipt':str(path),'cells':len(cells),'whole_frame':True})
    # 座標鏡像延伸在三個週期內逐點交叉比對兩種算法。
    for v in range(-5016,5017):
        r = v%2508
        expected = 2507-r if r>=1254 else r
        q,t = divmod(v,1254)
        assert expected==(t if q%2==0 else 1253-t)
    return {'schema':1,'issue':44,'status':'DRAFT','geometry_version':version,'asphalt_frequency':frequency,
        'inputs':{'RS201.ROM':sha(args.rom.read_bytes())},
        'tool':f'infrastructure_prototype_check.py / Python {platform.python_version()}',
        'address_space':'RS201.ROM file offsets; zero-based member/image; 1280x800 presentation pixels',
        'candidate_tiles':len(EXPECTED),
        'checked_hd_pixels':pixels,'checked_source_centers':centers,'unique_native_edges':len(edges),
        'normal_proofs':normal,'painted_cells':painted_total,'world_phase_rasters':len(phase_records),
        'mirror_coordinates':10033,'prototype_manifest_sha256':sha((args.prototype/'manifest.json').read_bytes()),
        'scope':'離線草案完整來源、幾何、材質及區外；不代替正式 GUI、狀態或存退讀驗收'}


def negatives(args):
    # 更新自報雜湊後仍須被拒絕，避免只測檔案完整性。
    original = args.prototype
    results = []
    for fault in ['source-index','weights-preserve-sum','tile-raster','world-phase','outside-pixel']:
        with tempfile.TemporaryDirectory(prefix='infrastructure-negative-',dir=original.parent) as root:
            target = Path(root)/'copy'
            shutil.copytree(original,target)
            manifest = json.loads((target/'manifest.json').read_text())
            record = manifest['candidate_images'][0]
            if fault in ('source-index','weights-preserve-sum'):
                suffix = 'indices' if fault=='source-index' else 'weights'
                p = target/f'39-015-{suffix}.bin'
                raw = bytearray(p.read_bytes())
                if fault=='source-index':raw[0]=255
                else:
                    # 第一像素全部屬同一原色；保留 255 總和，加入錯誤混色。
                    assert raw[:4]==bytes([255,0,0,0])
                    raw[0],raw[1]=254,1
                p.write_bytes(raw)
                record['index_bytes' if suffix=='indices' else 'weight_bytes']=sha(raw)
            elif fault=='tile-raster':
                p = target/'39-015.png'
                raw = bytearray(rgba(p,(36,36)));raw[0]^=1
                p.write_bytes(png(raw,36,36));record['png_sha256']=sha(p.read_bytes())
            elif fault=='world-phase':
                proof = manifest['phase_proofs'][1]
                p = target/proof['png']
                # 換成同來源、不同世界座標的真實素材，且更新自報雜湊。
                p.write_bytes((target/manifest['phase_proofs'][0]['png']).read_bytes())
                proof['png_sha256']=sha(p.read_bytes())
            else:
                p = target/manifest['proofs'][0]['png']
                raw = bytearray(rgba(p,(1280,800)));raw[0]^=1
                p.write_bytes(png(raw,1280,800))
            (target/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
            args.prototype=target
            try:check(args)
            except AssertionError as error:
                results.append({'fault':fault,'rejected':True,'reason':str(error)[:180]})
            else:raise AssertionError(('negative accepted',fault))
            finally:args.prototype=original
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rom',type=Path,required=True)
    ap.add_argument('--catalog',type=Path,required=True)
    ap.add_argument('--materials',type=Path,required=True)
    ap.add_argument('--prototype',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--negative',action='store_true')
    args=ap.parse_args()
    assert not args.out.exists()
    result=check(args)
    if args.negative:result['effective_negative_controls']=negatives(args)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
