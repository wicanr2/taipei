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
    cases={r['id']:r for r in run['cases']};assert len(cases)==7 and len(run['screenshots'])==42
    outputs=[];negative=0
    for shot in run['screenshots']:
        path=a.run/shot['file'];png=path.read_bytes();assert sha(png)==shot['png_sha256']
        receipt=a.run/shot['file'].replace('.png','-capture.zip');assert sha(receipt.read_bytes())==shot['capture_sha256']
        with zipfile.ZipFile(receipt) as z:s=json.loads(z.read('status.json'));frame=z.read('frame-index.bin');assert z.read('presentation.png')==png
        assert sha(frame)==s['frame_index_sha256']==shot['frame_index_sha256']
        assert s['language']==shot['language'] and s['hd_enabled']==shot['hd_enabled']
        assert not s.get('unimplemented') and not s['help_panel'] and not s['language_panel']
        actual=rgba(path,(1280,800));case=cases[shot['case']];kind,proof=groups[case['id']]
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
            'png_sha256':sha(png),'source_and_aliases_checked':16,'full_original_checked':not s['hd_enabled'],
            'full_atlas_checked':s['hd_enabled'] and kind=='complex','noto_ink_and_background_checked':s['hd_enabled'] and kind=='zones'})
    result={'schema':1,'issue':62,'normal_gui':True,'state_injection':False,'checkpoint':False,
        'verification_sha256':sha((a.run/'verification.json').read_bytes()),'baseline_sha256':sha((a.baseline/'verification.json').read_bytes()),
        'original_save_sha256':sha(saved),'baseline_save_identical':True,'sources':7*16,'screenshots':outputs,
        'effective_pixel_negative_controls':negative,'tool_sha256':sha(Path(__file__).read_bytes()),
        'scope':'七種正常代表、42張真實GUI、整張原版／封存建物／Noto墨跡及原版存讀退出；未走過成長與災害分支、平台真機不外推'}
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('PASS: seven normal sources, 42 real GUI images, full original/atlases/Noto, 42 effective controls, identical 93567-byte SAV',sha(a.out.read_bytes()))


if __name__=='__main__':main()
