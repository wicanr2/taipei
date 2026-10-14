#!/usr/bin/env python3
"""#61：正常冷讀 DISA4 既有港口／機場、捲動、存讀與原版退出。"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import zipfile

import city_menu_playtest as base
from chart_window_playtest import model
from facility_batch_playtest import key,front_key,save,restore,toolbar_selection,language,LANGS
from facility_cursor import locate_small_cursor
from infrastructure_catalog import sources
from hd_source_audit import scene,cell,sha

CASES=[{'id':'airport','tool':13,'world':[47,29],'origin':[36,24],'base':0},
       {'id':'port','tool':12,'world':[43,73],'origin':[32,68],'base':6}]
SEED_SHA='47f73cbe590a26bc8b9b792d8de4eea4f2d9efb6723ca664c931075f1d4d52b1'


def main():
    root=base.root;assert not root.exists() and root.parent.stat().st_uid==1000
    root.mkdir();saves=root/'saves';saves.mkdir()
    seed=Path('/seed/FUND.SAV');assert sha(seed.read_bytes())==SEED_SHA
    shutil.copyfile(seed,saves/'FUND.SAV')
    binary=Path('/workspace/runs')/os.environ.get('TAIPEI_TRANSPORT_BINARY','taipei-preview')
    phase=os.environ.get('TAIPEI_TRANSPORT_PHASE','source');assert phase in ['source','hd']
    aliases=sources(Path('/orig/RS201.ROM').read_bytes())
    results=[];shots=[];script=Path(__file__).read_bytes();(root/'executed-driver.py').write_bytes(script)
    with (root/'app.log').open('w') as log:
        game=subprocess.Popen([str(binary),'-original','/orig','-saves',str(saves),'-receipts',str(root),
            '-mute','-steps-per-update','2000000','-receipt-every-updates','6','-theme','hd-b',
            '-materials','/workspace/prototypes/hd-style','-catalog','/workspace/app/locales/ui.tsv',
            '-stop-file',str(root/'stop')],stdout=log,stderr=subprocess.STDOUT)
        try:
            base.cold_city();_,pristine=model();restore('FUND',saves)
            key('activate-saved-tool','Tab');_,frame=model();assert toolbar_selection(frame,pristine)==0
            def navigate(case,label):
                for axis,goal in zip(['X','Y'],case['origin']):
                    for i in range(128):
                        st=base.status()
                        if st['map_origin'][axis]==goal:break
                        value=('Right' if axis=='X' else 'Down') if st['map_origin'][axis]<goal else ('Left' if axis=='X' else 'Up')
                        key(f'{label}-route-{axis}-{i}',value)
                        base.wait_for(lambda s:s['map_origin']['Valid'],'map-redraw-ready')
                    else:raise AssertionError(('原版捲動未到目標',case['id'],axis))
                observed={}
                def cursor_ready(_):
                    st,frame=model()
                    if not scene(st,frame) or not st['map_origin']['Valid']:return False
                    try:cursor=locate_small_cursor(frame,aliases)
                    except AssertionError:return False
                    observed.update(cursor=cursor)
                    return True
                base.wait_for(cursor_ready,label+'-cursor-ready')
                cursor=observed['cursor']
                for axis,keys,goal in [(0,('Left','Right'),26),(1,('Up','Down'),1)]:
                    while cursor[axis]!=goal:
                        d=1 if cursor[axis]<goal else -1
                        key(f'{label}-cursor-{axis}-{cursor[axis]}',keys[d>0]);cursor[axis]+=d
                ox,oy=case['origin'];wx,wy=case['world']
                left,top=wx-ox,wy-oy
                expected=[next(raw for raw,a in aliases.items() if any(t['member']==38 and
                    t['image']==case['base']+30*row+col for t in a)) for row in range(6) for col in range(6)]
                def facility_ready(_):
                    st,frame=model()
                    if not scene(st,frame) or st['map_origin']!={'X':ox,'Y':oy,'Valid':True}:return False
                    if [cell(frame,5+(left+col)*9,34+(top+row)*9) for row in range(6) for col in range(6)]!=expected:return False
                    observed.update(status=st,frame=frame)
                    return True
                base.wait_for(facility_ready,label+'-complete-source-ready')
                st,frame=observed['status'],observed['frame']
                assert st['map_origin']=={'X':ox,'Y':oy,'Valid':True} and scene(st,frame)
                assert int(st['hd']['footer_text'][3])==73455
                known=[]
                for row in range(6):
                    for col in range(6):
                        raw=cell(frame,5+(left+col)*9,34+(top+row)*9)
                        assert raw in aliases and any(a['member']==38 and a['image']==case['base']+30*row+col for a in aliases[raw]),(case['id'],col,row)
                        known.append({'cell':[left+col,top+row],'source_sha256':sha(raw),'sources':aliases[raw]})
                if phase=='hd':assert st['hd']['transport_facilities']['painted']==36
                return st,known,[left,top,6,6]
            def screenshot(case,label):
                base.capture(label);receipt=root/(label+'-capture.zip')
                with zipfile.ZipFile(receipt) as z:
                    st=json.loads(z.read('status.json'));raw=z.read('frame-index.bin');png=z.read('presentation.png')
                assert sha(raw)==st['frame_index_sha256'] and not st.get('unimplemented')
                want=next(r for r in results if r['id']==case['id'])
                assert all(sha(cell(raw,5+r['cell'][0]*9,34+r['cell'][1]*9))==r['source_sha256'] for r in want['known'])
                assert st['hd']['transport_facilities']['painted']==(36 if st['hd_enabled'] else 0)
                (root/(label+'.png')).write_bytes(png)
                shots.append({'file':label+'.png','case':case['id'],'png_sha256':sha(png),'capture_sha256':sha(receipt.read_bytes()),
                    'frame_index_sha256':sha(raw),'language':st['language'],'hd_enabled':st['hd_enabled'],
                    'steps':st['steps'],'ticks':st['ticks'],'map_origin':st['map_origin']})
            for case in CASES:
                st,known,bounds=navigate(case,case['id']);base.capture(case['id']+'-complete')
                results.append({'id':case['id'],'tool':case['tool'],'option':None,'fee':None,
                    'before_budget':73455,'after_budget':73455,'bounds':bounds,'known':known,
                    'receipt':case['id']+'-complete-capture.zip','steps':st['steps'],'origin':st['map_origin'],
                    'construction_tested':False,'existing_city':'DISA4.DSA','native_world':case['world']})
                (root/'result-progress.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
                print('COMPLETE',case['id'],'existing city cells',len(known),flush=True)
                if phase=='hd':
                    before=base.status();front_key('F12');base.wait_for(lambda s:not s['hd_enabled'],'original-ready')
                    screenshot(case,case['id']+'-original');assert base.status()['key_reads']==before['key_reads']
                    front_key('F12');base.wait_for(lambda s:s['hd_enabled'],'hd-ready')
                    for lang in LANGS:language(lang);screenshot(case,case['id']+'-'+lang)
            saved=save('TRANSP',saves);restore('TRANSP',saves)
            key('readback-activate','Tab');_,frame=model();assert toolbar_selection(frame,pristine)==0
            _,known,_=navigate(CASES[-1],'readback')
            assert [r['source_sha256'] for r in known]==[r['source_sha256'] for r in results[-1]['known']]
            base.capture('facility-readback')
            key('quit-menu','F1');base.wait_for(lambda s:s['hd']['panel']=='city-f1','quit-menu-ready')
            if base.status()['hd']['panel_selection']!=0:key('quit-choice','Down')
            key('quit-confirm','space');base.wait_for(lambda s:s['hd']['file_dialog']=='quit-confirm','quit-ready')
            subprocess.run(['xdotool','type','--delay','150','Y'],check=True)
            base.wait_for(lambda s:s['dos_blocked'] and any(k.get('Via')=='int21-AH07' and k.get('Key')==89
                for k in s.get('key_reads') or []),'ending',seconds=180)
            front_key('space');base.wait_for(lambda s:s.get('dos_exited'),'dos-exit');assert game.wait(timeout=10)==0
            (root/'verification.json').write_text(json.dumps({'issue':61,'phase':phase,'normal_gui':True,
                'state_injection':False,'checkpoint':False,'native_exit_tested':True,'original_save_read':True,
                'seed_save_sha256':SEED_SHA,'seed_unchanged':sha(seed.read_bytes())==SEED_SHA,
                'final_save_sha256':saved,'save_unchanged_after_read':sha((saves/'TRANSP.SAV').read_bytes())==saved,
                'cases':results,'screenshots':shots,'new_construction_tested':False,
                'binary_sha256':sha(binary.read_bytes()),'script_sha256':sha(script)},ensure_ascii=False,indent=2)+'\n')
        finally:
            if game.poll() is None:
                (root/'stop').write_text('stop\n')
                try:game.wait(timeout=10)
                except subprocess.TimeoutExpired:game.kill();game.wait()
            assert game.returncode==0,game.returncode


if __name__=='__main__':main()
