"""#25：正常城市時間推進、來源回退與相同地景像素的獨立核對。"""
import argparse
import collections
import json
import subprocess
import zipfile
from pathlib import Path

from hd_scroll_check import audit_bundle, source59
from hd_source_audit import MATERIAL, budget_window, scene, sha

DATE_RECT=(270,174,50,11)
def rectangle(frame,x,y,w,h):
    return b''.join(frame[(y+r)*320+x:(y+r)*320+x+w] for r in range(h))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--original',type=Path,required=True)
    ap.add_argument('--receipts',type=Path,required=True)
    args=ap.parse_args();sources=source59(args.original)
    samples=[];dates={};reasons=collections.Counter();previous=None;same=changed=0;budget_samples=[]
    for path in sorted(args.receipts.glob('running-*-capture.zip')):
        s,frame,grid,rgba,sample=audit_bundle(path,sources)
        label=path.name.removesuffix('-capture.zip');date=sha(rectangle(frame,*DATE_RECT))
        colors=bytes(v for i in sorted(MATERIAL) for v in s['palette'][i])
        sample.update({'date_crop_sha256':date,'palette_sha256':sha(bytes(v for c in s['palette'] for v in c)),
                       'material_palette_sha256':sha(colors),'origin':s['map_origin'],
                       'source_eligible_cells':sum(tile in sources and all(i in MATERIAL for i in tile) for tile in grid)})
        reasons[s['hd']['reason']]+=1
        if budget_window(frame):
            assert s['hd']['Painted']==0,'年度預算視窗未整幀回退'
            budget_samples.append(label)
        if date not in dates:
            dates[date]=label
            with zipfile.ZipFile(path) as z:png=z.read('frame.png')
            target=args.receipts/(label+'-date.png')
            subprocess.run(['convert','png:-','-crop','50x11+270+174','+repage','-filter','point','-resize','600%',str(target)],input=png,check=True)
        active=scene(s,frame) and s['map_origin']['Valid'] and s['hd_enabled']
        if previous and active and previous[0] and s['map_origin']==previous[1]:
            oldgrid,oldrgba=previous[2:]
            for index,tile in enumerate(grid):
                if tile!=oldgrid[index] or tile not in sources or not all(i in MATERIAL for i in tile):continue
                x,y=index%29,index//29;same+=1
                for row in range(36):
                    at=((136+y*36+row)*1280+20+x*36)*4
                    if rgba[at:at+144]!=oldrgba[at:at+144]:changed+=1;break
        previous=(active,s['map_origin'],grid,rgba);samples.append(sample)
    assert len(samples)==60,'固定間隔抽樣不完整'
    assert [x['steps'] for x in samples]==[samples[0]['steps']+i*24000000 for i in range(60)],'實際收據間隔不符'
    assert any(k.get('Key')==51 for k in s['key_reads']),'未見原版讀取速度鍵 3'
    assert not any(k.get('Key')==48 for k in s['key_reads']),'抽樣收到暫停鍵 0'
    assert len(dates)>=3,'尚未證實至少三種不同日期畫面'
    assert budget_samples,'沒有捕捉到正常年度預算視窗'
    assert same>0 and changed==0,'同一原版地景及原點的 HD 像素不穩定'
    restored=[]
    for label in budget_samples:
        index=next(i for i,x in enumerate(samples) if x['receipt']==label+'-capture.zip')
        later=next((x for x in samples[index+1:] if x['reason']=='matched-city' and x['painted']>400),None)
        assert later is not None,(label,'年度視窗後沒有正常城市恢復證據')
        restored.append({'budget':label,'restored':later['receipt']})
    date_images=[str(args.receipts/(label+'-date.png')) for label in dates.values()]
    rows=[]
    for i in range(0,len(date_images),6):
        row=args.receipts/f'date-row-{i//6:02d}.png';rows.append(str(row))
        subprocess.run(['convert',*date_images[i:i+6],'-background','#303030','+append',str(row)],check=True)
    subprocess.run(['convert',*rows,'-background','#303030','-append',str(args.receipts/'dates-contact.png')],check=True)
    result={'schema':1,'scope':'DRAFT 地景正常持續運行抽樣；日期需人工辨識，不等於全遊戲動畫或正式 HD 驗收',
            'samples':samples,'date_rectangle':DATE_RECT,'distinct_date_crops':dates,'reasons':dict(reasons),
            'same_material_cells_compared':same,'same_material_cells_changed':changed,
            'budget_samples':budget_samples,'budget_full_frame_native':True,
            'budget_returns':restored,
            'source_count_matches':True,'fallback_pixels_native':True,
            'native_months_require_manual_review':True,'date_contact_sheet':'dates-contact.png'}
    (args.receipts/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='samples'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
