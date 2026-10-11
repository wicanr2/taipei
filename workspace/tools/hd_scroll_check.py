"""#23：獨立核對原版圖塊位移、來源條件及回退區域的實際呈現。"""
import argparse
import json
import struct
import subprocess
import zipfile
from pathlib import Path

from hd_source_audit import EXPECTED, MATERIAL, cell, scene, sha
from rom_catalog import library
from hd_dialog_check import audit_dialog
from hd_panels_check import audit_panel
from hd_chrome_check import audit_chrome
from hd_footer_check import audit_footer
from hd_file_dialogs_check import audit_file
from hd_budget_check import audit_budget
from hd_infrastructure_check import audit_infrastructure

ORDER=['map-focus','right-10','right-20','right-30','right-40',
       'down-6','down-12','down-18','left-10','left-20','left-30','left-40',
       'up-6','up-12','up-18']
def translation(a,b):
    candidates=[]
    for dy in range(-14,15):
        for dx in range(-28,29):
            total=(29-abs(dx))*(15-abs(dy))
            if total<100: continue
            matched=[]
            for y in range(max(0,-dy),min(15,15-dy)):
                for x in range(max(0,-dx),min(29,29-dx)):
                    if b[y*29+x]==a[(y+dy)*29+x+dx]: matched.append(b[y*29+x])
            ratio=len(matched)/total;distinct=len(set(matched))
            if ratio>=.98 and distinct>=8:
                candidates.append({'dx':dx,'dy':dy,'overlap':total,'matched':len(matched),'ratio':ratio,'distinct':distinct})
    return max(candidates,key=lambda c:(c['ratio'],c['matched'])) if candidates else None

def source59(original):
    raw=(original/'RS201.ROM').read_bytes();assert sha(raw)==EXPECTED['RS201.ROM']
    assert struct.unpack_from('<H',raw)[0]==69
    off,n=struct.unpack_from('<IH',raw,18+59*16)
    parsed=library(raw[off:off+n]);assert parsed
    _,images=parsed;assert len(images)==135 and all((w,h)==(9,9) for w,h,_ in images)
    return {px for _,_,px in images}

def audit_bundle(path,sources):
    """Independent source/count/fallback audit shared by normal GUI probes."""
    with zipfile.ZipFile(path) as z:
        s=json.loads(z.read('status.json'));frame=z.read('frame-index.bin')
        assert len(frame)==64000 and sha(frame)==s['frame_index_sha256']
        png=z.read('presentation.png')
    assert struct.unpack('>II',png[16:24])==(1280,800)
    rgba=subprocess.run(['convert','png:-','-depth','8','rgba:-'],input=png,stdout=subprocess.PIPE,check=True).stdout
    assert len(rgba)==1280*800*4 and sha(rgba)==s['presentation_sha256']
    if audit_budget(s,frame,rgba) or audit_file(s,frame,rgba) or audit_panel(s,frame,rgba) or audit_dialog(s,frame,rgba):
        grid=[cell(frame,x,y) for y in range(34,169,9) for x in range(5,266,9)]
        return s,frame,grid,rgba,{'receipt':path.name,'steps':s['steps'],'painted':0,
            'fallback':435,'fallback_cells':[],'reason':s['hd']['reason'],
            'dialog':s['hd'].get('dialog',''),'panel':s['hd'].get('panel',''),
            'file_dialog':s['hd'].get('file_dialog','')}
    audit_chrome(s,frame,rgba)
    audit_footer(s,frame,rgba)
    origin=s.get('map_origin')
    active=scene(s,frame) and s['hd_enabled'] and (origin is None or origin['Valid'])
    infrastructure=audit_infrastructure(s,frame,rgba)
    eligible=0;fallback=[];grid=[]
    for y in range(34,169,9):
        for x in range(5,266,9):
            tile=cell(frame,x,y);grid.append(tile)
            if (x,y) in infrastructure or (active and tile in sources and all(i in MATERIAL for i in tile)):eligible+=1
            else:
                fallback.append([x,y])
                for row in range(9):
                    want=b''.join(bytes(s['palette'][index]+[255])*4 for index in tile[row*9:(row+1)*9])
                    for dy in range(4):
                        at=(((y+row)*4+dy)*1280+x*4)*4
                        assert rgba[at:at+36*4]==want,(path.name,x,y,row,dy,'回退格被覆繪')
    assert eligible==s['hd']['Painted'],(path.name,eligible,s['hd'])
    if eligible==0:
        for y in range(200):
            row=b''.join(bytes(s['palette'][index]+[255])*4 for index in frame[y*320:(y+1)*320])
            for dy in range(4):
                at=(y*4+dy)*1280*4
                assert rgba[at:at+1280*4]==row,(path.name,y,dy,'整幀回退不等於原版')
    sample={'receipt':path.name,'steps':s['steps'],'painted':eligible,'fallback':len(fallback),
            'fallback_cells':fallback,'reason':s['hd']['reason']}
    return s,frame,grid,rgba,sample

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--original',type=Path,required=True)
    ap.add_argument('--receipts',type=Path,required=True)
    ap.add_argument('--require-world-origin',action='store_true')
    args=ap.parse_args()
    sources=source59(args.original)
    samples=[];grids={};presentations={};origins={}
    for path in sorted(args.receipts.glob('*-capture.zip')):
        s,frame,grid,rgba,sample=audit_bundle(path,sources)
        origin=s.get('map_origin')
        label=path.name.removesuffix('-capture.zip');grids[label]=grid
        if origin is not None:origins[label]=origin
        if label in ORDER:presentations[label]=rgba
        samples.append(sample)
    shifts=[]
    for a,b in zip(ORDER,ORDER[1:]):
        shift=translation(grids[a],grids[b]);record={'from':a,'to':b,'shift':shift}
        if shift and (shift['dx'] or shift['dy']):
            dx,dy=shift['dx'],shift['dy'];same=changed=0
            if args.require_world_origin:
                oa,ob=origins[a],origins[b]
                assert oa['Valid'] and ob['Valid'],(a,b,'原點未完成')
                assert (ob['X']-oa['X'],ob['Y']-oa['Y'])==(dx,dy),(a,b,oa,ob,shift)
                record['origin_delta_matches']=True
            for y in range(max(0,-dy),min(15,15-dy)):
                for x in range(max(0,-dx),min(29,29-dx)):
                    tile=grids[b][y*29+x]
                    if tile!=grids[a][(y+dy)*29+x+dx] or tile not in sources or not all(i in MATERIAL for i in tile):continue
                    same+=1;different=False
                    for row in range(36):
                        at=((136+y*36+row)*1280+20+x*36)*4
                        old=((136+(y+dy)*36+row)*1280+20+(x+dx)*36)*4
                        if presentations[b][at:at+144]!=presentations[a][old:old+144]:different=True
                    changed+=different
            record['same_world_material_cells']=same
            record['world_material_changed_cells']=changed
        shifts.append(record)
    nonzero=[x for x in shifts if x['shift'] and (x['shift']['dx'] or x['shift']['dy'])]
    assert any(x['shift']['dx'] for x in nonzero),'沒有充分證據證明水平捲動'
    assert any(x['shift']['dy'] for x in nonzero),'沒有充分證據證明垂直捲動'
    shuffled=[grids[ORDER[0]][(i*101)%435] for i in range(435)]
    assert translation(grids[ORDER[0]],shuffled) is None,'幾何負對照未被拒絕'
    phase_stable=all(x['world_material_changed_cells']==0 for x in nonzero)
    if args.require_world_origin:assert phase_stable,'同一世界地景捲動後材質改變'
    result={'scope':'DRAFT 原型抽樣，不宣稱正式 HD、全部動畫或世界座標材質已完成',
            'samples':samples,'translations':shifts,'horizontal_scroll':True,'vertical_scroll':True,
            'fallback_pixels_native':True,'source_count_matches':True,
            'world_material_phase_stable':phase_stable,'origins':origins,
            'origin_delta_matches':bool(args.require_world_origin),'negative_permuted_grid_rejected':True,
            'translation_gate':{'min_overlap':100,'min_distinct':8,'min_ratio':.98}}
    (args.receipts/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'bundles':len(samples),'nonzero_shifts':nonzero,'fallback_pixels_native':True,
                      'world_material_phase_stable':phase_stable},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
