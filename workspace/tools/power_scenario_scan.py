#!/usr/bin/env python3
"""#46：正常選單檢查六座災難城市的核能施工資金。"""
import json
import os
from pathlib import Path
import subprocess
import city_menu_playtest as base
from chart_window_playtest import model
from facility_batch_playtest import key, front_key, save
from hd_source_audit import scene, sha

def main():
    root=base.root
    assert not root.exists() and root.parent.stat().st_uid==1000
    root.mkdir(); binary=Path('/workspace/runs/taipei-preview'); results=[]
    script_sha=sha(Path(__file__).read_bytes())
    start=int(os.environ.get('TAIPEI_SCAN_START','0')); assert 0<=start<=5
    for index in range(start,6):
        out=root/f'city-{index+1}'; out.mkdir(); saves=out/'saves'; saves.mkdir(); base.out=out
        with (out/'app.log').open('w') as log:
            game=subprocess.Popen([str(binary),'-original','/orig','-saves',str(saves),
                '-receipts',str(out),'-mute','-steps-per-update','2000000',
                '-receipt-every-updates','6','-theme','hd-b','-materials','/workspace/prototypes/hd-style',
                '-catalog','/workspace/app/locales/ui.tsv','-stop-file',str(out/'stop')],stdout=log,stderr=subprocess.STDOUT)
            try:
                base.wait_for(lambda s:s.get('steps',0)>=700_000_000,'intro',progress=True)
                subprocess.run(['xdotool','search','--onlyvisible','--pid',str(game.pid),'windowfocus'],check=True)
                base.action('intro-space','space')
                base.wait_for(lambda s:s.get('steps',0)>=800_000_000,'intro-wait')
                base.action('main','space')
                base.wait_for(lambda s:s.get('hd',{}).get('panel')=='main','main-ready')
                key('scenario-choice','Right'); key('scenario-open','space')
                # 033 的正常收據：選項依欄序以 Down 遞增，Right 不改選取。
                base.wait_for(lambda s:s['hd']['interface_panel']=='disaster-city-0','scenario-ready')
                for selection in range(1,index+1):
                    key(f'scenario-select-{selection}','Down')
                    base.wait_for(lambda s:s['hd']['interface_panel']==f'disaster-city-{selection}','scenario-selection-ready')
                base.capture('scenario-selection')
                for label,value in [('scenario-city','space'),('instructions','space'),('difficulty','space'),('pause','0')]:key(label,value)
                status,frame=model(); assert scene(status,frame)
                names=sorted({f['Name'].upper() for f in status['file_ops'] if f.get('Op')=='read' and f.get('Name','').upper().endswith('.DSA')})
                assert len(names)==1,names
                funds=int(status['hd']['footer_text'][3]); base.capture('paused-city')
                saved=save('FUND',saves)
                key('quit-menu','F1'); base.wait_for(lambda s:s['hd']['panel']=='city-f1','quit-menu-ready')
                if base.status()['hd']['panel_selection']!=0:key('quit-choice','Down')
                key('quit-confirm','space'); base.wait_for(lambda s:s['hd']['file_dialog']=='quit-confirm','quit-ready')
                subprocess.run(['xdotool','type','--delay','150','Y'],check=True)
                base.wait_for(lambda s:s['dos_blocked'] and s['hd']['ending_screen']=='achievement-base','ending',seconds=180)
                front_key('space'); base.wait_for(lambda s:s.get('dos_exited'),'dos-exit'); assert game.wait(timeout=10)==0
                results.append({'selection':index,'original_file':names[0],'funds':funds,'native_exit':True,
                    'save_file':str(saves/'FUND.SAV'),'save_sha256':saved,'receipt':str(out/'paused-city-capture.zip')})
                (root/'result-progress.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
                print('CITY',names[0],funds,flush=True)
                if funds>=120000:break
            finally:
                if game.poll() is None:
                    (out/'stop').write_text('stop\n')
                    try:game.wait(timeout=10)
                    except subprocess.TimeoutExpired:game.kill();game.wait()
                assert game.returncode==0,game.returncode
    assert len({r['original_file'] for r in results})==len(results)
    (root/'verification.json').write_text(json.dumps({'issue':46,'normal_gui':True,
        'state_injection':False,'checkpoint':False,'binary_sha256':sha(binary.read_bytes()),
        'script_sha256':script_sha,'steps_per_update':2000000,'start_selection':start,'cases':results,
        'funded_city':next((r for r in results if r['funds']>=120000),None),
        'scope':'正常選單逐座檢查至第一座資金達120000的城市；不改寫城市、財政或存檔內容。'},ensure_ascii=False,indent=2)+'\n')
    print('DONE',len(results),'normal city checks',flush=True)

if __name__=='__main__':main()
