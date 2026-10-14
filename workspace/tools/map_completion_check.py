#!/usr/bin/env python3
"""038：獨立重讀ROM、實際GUI圖像、封存整圖與原版SAV。"""
import argparse
import json
from pathlib import Path
import zipfile

from infrastructure_catalog import sources,sha,ROM_SHA
from hd_file_dialogs_check import rgba
from infrastructure_prototype import native


def crop(raw,x,y,w,h,width=1280):
    return b''.join(raw[((y+r)*width+x)*4:((y+r)*width+x+w)*4] for r in range(h))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True)
    ap.add_argument('--baseline',type=Path,required=True);ap.add_argument('--materials',type=Path,required=True)
    ap.add_argument('--prefix',type=Path)
    ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    assert not a.out.exists()
    rom=Path('/orig/RS201.ROM').read_bytes();assert sha(rom)==ROM_SHA
    aliases=sources(rom);bysha={sha(b):b for b in aliases}
    run=json.loads((a.run/'verification.json').read_text());base=json.loads((a.baseline/'verification.json').read_text())
    assert run['normal_gui'] and not run['checkpoint'] and not run['state_injection'] and run['native_exit_tested']
    assert base['normal_gui'] and base['native_exit_tested'] and run['seed_unchanged'] and base['seed_unchanged']
    assert run['save_unchanged_after_read'] and base['save_unchanged_after_read']
    saved=(a.run/'saves/MAPHD.SAV').read_bytes();assert len(saved)==93567
    assert saved==(a.baseline/'saves/MAPHD.SAV').read_bytes()
    assert sha(saved)==run['final_save_sha256']==base['final_save_sha256']
    inventory=json.loads((a.materials/'map-completion-v1/inventory.json').read_text())
    groups={}
    for g in inventory['groups']:
        proof=json.loads((a.materials/'map-completion-v1'/g['kind']/g['id']/'source.json').read_text())
        groups[g['id']]=(g['kind'],proof)
    views=[(a.run,case,shot,True) for case in run['cases'] for shot in run['screenshots'] if shot['case']==case['id']]
    if a.prefix:
        prefix_cases=json.loads((a.prefix/'result-progress.json').read_text());assert len(prefix_cases)==5
        assert (a.prefix/'executed-driver.py').is_file()
        # 原件是失敗流程前已完成的正常圖像，只承認來源與呈現，沒有補造退出收據。
        for case in prefix_cases:
            for suffix in ['original','zh-Hant','zh-Hans','ja','ko','en']:
                filename=case['id']+'-'+suffix+'.png';receipt=a.prefix/filename.replace('.png','-capture.zip')
                with zipfile.ZipFile(receipt) as z:st=json.loads(z.read('status.json'));frame=z.read('frame-index.bin');picture=z.read('presentation.png')
                assert picture==(a.prefix/filename).read_bytes() and sha(frame)==st['frame_index_sha256']
                shot={'file':filename,'case':case['id'],'png_sha256':sha(picture),'capture_sha256':sha(receipt.read_bytes()),
                    'frame_index_sha256':sha(frame),'language':st['language'],'hd_enabled':st['hd_enabled']}
                views.append((a.prefix,case,shot,False))
        assert len(run['cases'])==2 and len(run['screenshots'])==12 and len(views)==42
    else:assert len(run['cases'])==7 and len(views)==42
    outputs=[];negative=0
    for source_run,case,shot,complete in views:
        path=source_run/shot['file'];png=path.read_bytes();assert sha(png)==shot['png_sha256']
        receipt=source_run/shot['file'].replace('.png','-capture.zip');assert sha(receipt.read_bytes())==shot['capture_sha256']
        with zipfile.ZipFile(receipt) as z:s=json.loads(z.read('status.json'));frame=z.read('frame-index.bin');assert z.read('presentation.png')==png
        assert sha(frame)==s['frame_index_sha256']==shot['frame_index_sha256']
        assert s['language']==shot['language'] and s['hd_enabled']==shot['hd_enabled']
        assert not s.get('unimplemented') and not s['help_panel'] and not s['language_panel']
        actual=rgba(path,(1280,800));kind,proof=groups[case['id']]
        col,row,w,h=case['bounds'];left,top=20+36*col,136+36*row
        for tile in proof['tiles']:
            c,r=tile['cell'];raw=b''.join(frame[(34+(row+r)*9+y)*320+5+(col+c)*9:(34+(row+r)*9+y)*320+14+(col+c)*9] for y in range(9))
            assert raw==bysha[tile['source_sha256']] and aliases[raw]==tile['sources']
        original=native(frame,s['palette'])
        if not s['hd_enabled']:
            assert actual==original,'F12整張原版不相同'
            bad=bytearray(actual);bad[100]^=1;assert bad!=original;negative+=1
        else:
            atlas=rgba(a.materials/'map-completion-ready-v1'/kind/(case['id']+'.png'),(144,144))
            shown=crop(actual,left,top,144,144)
            assert shown!=crop(original,left,top,144,144)
            if kind=='complex':assert shown==atlas,'實際整圖與封存圖不相同'
            else:
                ink=0
                for y in range(144):
                    for x in range(144):
                        at=(y*144+x)*4
                        if shown[at:at+4]!=atlas[at:at+4]:
                            assert 44<=x<108 and 44<=y<100,'區域字墨越界'
                            ink+=1
                assert ink>=40,'區域未有實際Noto字墨'
            bad=bytearray(shown);bad[0]^=1
            if kind=='complex':assert bad!=atlas
            else:assert bad[:4]!=atlas[:4]
            negative+=1
        outputs.append({'file':shot['file'],'case':case['id'],'language':s['language'],'hd':s['hd_enabled'],
            'source_run':source_run.name,'normal_path_complete':complete,'capture_sha256':sha(receipt.read_bytes()),
            'frame_index_sha256':sha(frame),'steps':s['steps'],'ticks':s['ticks'],'map_origin':s['map_origin'],
            'png_sha256':sha(png),'source_and_aliases_checked':16,'full_original_checked':not s['hd_enabled'],
            'full_atlas_checked':s['hd_enabled'] and kind=='complex','noto_ink_and_background_checked':s['hd_enabled'] and kind=='zones'})
    result={'schema':1,'issue':62,'normal_gui':True,'state_injection':False,'checkpoint':False,
        'verification_sha256':sha((a.run/'verification.json').read_bytes()),'baseline_sha256':sha((a.baseline/'verification.json').read_bytes()),
        'original_save_sha256':sha(saved),'baseline_save_identical':True,'sources':7*16,'unique_normal_representatives':5 if a.prefix else 7,'screenshots':outputs,
        'source_prefix':{'run':a.prefix.name,'normal_path_complete':False,'source_cases':5,'progress_sha256':sha((a.prefix/'result-progress.json').read_bytes()),
            'executed_driver_sha256':sha((a.prefix/'executed-driver.py').read_bytes())} if a.prefix else None,
        'effective_pixel_negative_controls':negative,'tool_sha256':sha(Path(__file__).read_bytes()),
        'scope':'五種正常來源與完成流程兩個重複代表、42張真實GUI；前五種來源原件為未完成退出的前段，存讀退出由另一正常冷啟C1流程驗證；未取得C2高階建物路由，不外推成長／災害分支與真機'}
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('PASS: normal source views, 42 real GUI images, explicit prefix/complete scopes, full original/atlases/Noto, 42 controls, identical 93567-byte SAV',sha(a.out.read_bytes()))


if __name__=='__main__':main()
