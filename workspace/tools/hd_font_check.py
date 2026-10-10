"""#27：動態 Noto 六標題對已展示原型的實際像素核對。"""
import argparse
import collections
import json
import subprocess
from pathlib import Path

from hd_scroll_check import audit_bundle, source59
from hd_source_audit import scene, sha

REFERENCE_SHA='feefbf252a77ab01322c72654a2c6d8b7cb42118494949604f194c20d4f331da'
FONT_SHA='dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4'
LICENSE_SHA='6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2'
PALETTE_SHA='1acb802a98b9fb298f4d68b1f4e5a74b0d3bfca88cba6d347795dbafbab63a1e'
RECTS=[(28+i*176,40,136,68) for i in range(6)]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--original',type=Path,required=True)
    ap.add_argument('--materials',type=Path,required=True)
    ap.add_argument('--receipts',type=Path,required=True)
    args=ap.parse_args(); sources=source59(args.original)
    for name,expected in [('fonts/NotoSansCJKtc-Regular.otf',FONT_SHA),('fonts/LICENSE',LICENSE_SHA),
                          ('font-comparison/noto-font.png',REFERENCE_SHA)]:
        assert sha((args.materials/name).read_bytes())==expected,('固定字型或已展示參考失配',name)
    reference=subprocess.run(['convert',str(args.materials/'font-comparison/noto-font.png'),'-depth','8','rgba:-'],
                             stdout=subprocess.PIPE,check=True).stdout
    assert len(reference)==1280*800*4
    samples=[];counts=collections.Counter()
    for path in sorted(args.receipts.rglob('*-capture.zip')):
        s,frame,grid,rgba,sample=audit_bundle(path,sources)
        origin=s.get('map_origin',{})
        colors=bytes(v for i in [15,21,27] for v in s['palette'][i])
        active=(s['hd_enabled'] and scene(s,frame) and origin.get('Valid')
                and 0<=origin['X']<=76 and 0<=origin['Y']<=74 and sha(colors)==PALETTE_SHA)
        expected=6 if active else 0
        assert s['hd']['font_labels']==expected,(str(path),s['hd'],'標題數不符來源條件')
        for x,y,w,h in RECTS:
            for row in range(y,y+h):
                at=(row*1280+x)*4
                if active:want=reference[at:at+w*4]
                else:
                    want=bytes(v for xx in range(x,x+w) for v in s['palette'][frame[(row//4)*320+xx//4]]+[255])
                assert rgba[at:at+w*4]==want,(str(path),x,row,'字型像素不同於定案參考或原版回退')
        # 矩形外只允許現有地圖覆繪；原生 F1–F6 及其他 UI 逐像素不變。
        for row in range(800):
            spans=[(0,1280)]
            if 136<=row<676:spans=[(0,20),(1064,1280)]
            if active and 40<=row<108:
                spans=[];left=0
                for x,_,w,_ in RECTS:spans.append((left,x));left=x+w
                spans.append((left,1280))
            for left,right in spans:
                want=bytes(v for xx in range(left,right) for v in s['palette'][frame[(row//4)*320+xx//4]]+[255])
                at=(row*1280+left)*4
                assert rgba[at:at+(right-left)*4]==want,(str(path),row,left,right,'文字與地圖區外出現差異')
        sample['font_labels']=expected;sample['font_reason']=s['hd']['font_reason']
        sample['receipt']=str(path.relative_to(args.receipts));samples.append(sample);counts[expected]+=1
    assert counts[6]>0 and counts[0]>0,'缺少實際覆字或原版回退收據'
    assert any(x['receipt']=='reload/load-accept-capture.zip' and x['font_labels']==6 for x in samples),'冷啟動讀檔後文字未恢復'
    result={'scope':'Noto 六個主選單標題 DRAFT，非全遊戲文字或正式 HD 驗收',
            'reference_sha256':REFERENCE_SHA,'bundles':len(samples),'font_counts':dict(counts),
            'font_pixels_match_selected_reference':True,'fallback_labels_native':True,
            'outside_map_and_labels_native':True,'cold_loaded_font_restored':True,'samples':samples}
    (args.receipts/'font-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='samples'},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
