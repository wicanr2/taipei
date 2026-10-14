#!/usr/bin/env python3
"""038：正常原版讀取、方向鍵、五語系、存退讀。沒有城市／RAM注入。"""
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
from hd_source_audit import cell,scene,sha

CASES=[('m37-b08','C1',[43,14],[32,9]),('m35-b00','C1',[38,24],[27,19]),
       ('m34-b08','C1',[54,44],[43,39]),('m34-b00','C1',[54,49],[43,44]),
       ('m36-b00','C1',[16,39],[5,34]),('m35-b12','C2',[83,64],[72,59]),
       ('m36-b16','C2',[71,76],[60,71])]
SEEDS={'C1':('/seed1/FUND.SAV','fdd4e3a9c0da6320bb0a2a4357f948589ebc34d0061d54ae624951b190bbc96f'),
       'C2':('/seed2/FUND.SAV','249faf6a9f4b16878dbd4faa9b8bc124b7698f5cac540beb20e492c0bbcfedf7')}


def route_key(label,value):
    # 每次按放／原版讀取照驗。路由中不複製每一格的完整zip，保留原始輸入紀錄與最終原件。
    capture=base.capture
    try:base.capture=lambda _:None;key(label,value)
    finally:base.capture=capture


def main():
    root=base.root;assert not root.exists() and root.parent.stat().st_uid==1000
    root.mkdir();saves=root/'saves';saves.mkdir()
    for name,(path,expected) in SEEDS.items():
        source=Path(path);assert sha(source.read_bytes())==expected;shutil.copyfile(source,saves/(name+'.SAV'))
    phase=os.environ.get('TAIPEI_MAP_PHASE','hd');assert phase in ['baseline','hd']
    binary=Path('/workspace/runs')/os.environ.get('TAIPEI_MAP_BINARY','taipei-preview-map-r2')
    aliases=sources(Path('/orig/RS201.ROM').read_bytes())
    groups={p.parent.name:json.loads(p.read_text()) for p in Path('/workspace/prototypes/hd-style/map-completion-v1').glob('*/*/source.json')}
    results=[];shots=[];script=Path(__file__).read_bytes();(root/'executed-driver.py').write_bytes(script)
    with (root/'app.log').open('w') as log:
        game=subprocess.Popen([str(binary),'-original','/orig','-saves',str(saves),'-receipts',str(root),
            '-mute','-steps-per-update','2000000','-receipt-every-updates','6','-theme','hd-b',
            '-materials','/workspace/prototypes/hd-style','-catalog','/workspace/app/locales/ui.tsv',
            '-stop-file',str(root/'stop')],stdout=log,stderr=subprocess.STDOUT)
        try:
            base.cold_city();_,pristine=model();loaded=None
            def navigate(case,label):
                id,_,world,origin=case
                for axis,goal in zip(['X','Y'],origin):
                    for i in range(128):
                        st=base.status()
                        if st['map_origin'][axis]==goal:break
                        direction=('Right' if axis=='X' else 'Down') if st['map_origin'][axis]<goal else ('Left' if axis=='X' else 'Up')
                        route_key(f'{label}-route-{axis}-{i}',direction)
                        base.wait_for(lambda s:s['map_origin']['Valid'],'map-redraw-ready')
                    else:raise AssertionError(('未到正常捲動目標',id,axis))
                observed={}
                def cursor_ready(_):
                    st,frame=model()
                    if not scene(st,frame) or not st['map_origin']['Valid']:return False
                    try:cursor=locate_small_cursor(frame,aliases)
                    except AssertionError:return False
                    observed['cursor']=cursor;return True
                base.wait_for(cursor_ready,label+'-cursor-ready');cursor=observed['cursor']
                for axis,keys,goal in [(0,('Left','Right'),26),(1,('Up','Down'),1)]:
                    while cursor[axis]!=goal:
                        delta=1 if cursor[axis]<goal else -1
                        route_key(f'{label}-cursor-{axis}-{cursor[axis]}',keys[delta>0]);cursor[axis]+=delta
                left,top=world[0]-origin[0],world[1]-origin[1]
                proof=groups[id];expected={tuple(t['cell']):t['source_sha256'] for t in proof['tiles']}
                def source_ready(_):
                    st,frame=model()
                    if not scene(st,frame) or st['map_origin']!={'X':origin[0],'Y':origin[1],'Valid':True}:return False
                    if not all(sha(cell(frame,5+(left+c)*9,34+(top+r)*9))==want for (c,r),want in expected.items()):return False
                    observed.update(status=st,frame=frame);return True
                base.wait_for(source_ready,label+'-complete-source');st=observed['status']
                if phase=='hd':
                    family='zones' if proof['base']==0 else 'complex'
                    assert st['hd']['map_completion'][family]['facilities'][id]>=16
                known=[dict(t,screen_cell=[left+t['cell'][0],top+t['cell'][1]]) for t in proof['tiles']]
                return st,known,[left,top,4,4]
            def screenshot(case,label):
                base.capture(label);path=root/(label+'-capture.zip')
                with zipfile.ZipFile(path) as z:st=json.loads(z.read('status.json'));frame=z.read('frame-index.bin');png=z.read('presentation.png')
                assert sha(frame)==st['frame_index_sha256'] and not st.get('unimplemented')
                want=next(r for r in results if r['id']==case[0])
                assert all(sha(cell(frame,5+t['screen_cell'][0]*9,34+t['screen_cell'][1]*9))==t['source_sha256'] for t in want['known'])
                (root/(label+'.png')).write_bytes(png)
                shots.append({'file':label+'.png','case':case[0],'png_sha256':sha(png),'capture_sha256':sha(path.read_bytes()),
                    'frame_index_sha256':sha(frame),'language':st['language'],'hd_enabled':st['hd_enabled'],
                    'steps':st['steps'],'ticks':st['ticks'],'map_origin':st['map_origin']})
            for case in CASES:
                id,seed,world,origin=case
                if loaded!=seed:
                    restore(seed,saves);loaded=seed;key('activate-saved-tool','Tab');_,frame=model();assert toolbar_selection(frame,pristine)==0
                st,known,bounds=navigate(case,id);base.capture(id+'-complete')
                results.append({'id':id,'seed':seed,'world':world,'origin':origin,'bounds':bounds,'known':known,
                    'receipt':id+'-complete-capture.zip','steps':st['steps'],'construction_tested':False})
                (root/'result-progress.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
                print('COMPLETE',id,seed,len(known),flush=True)
                if phase=='hd':
                    before=base.status();front_key('F12');base.wait_for(lambda s:not s['hd_enabled'],'original-ready')
                    screenshot(case,id+'-original');assert base.status()['key_reads']==before['key_reads']
                    front_key('F12');base.wait_for(lambda s:s['hd_enabled'],'hd-ready')
                    for lang in LANGS:language(lang);screenshot(case,id+'-'+lang)
            if phase=='hd':
                before=base.status();front_key('Shift_L+F1');opened=base.wait_for(lambda s:s['help_panel'],'help-open')
                front_key('Escape');closed=base.wait_for(lambda s:not s['help_panel'],'help-close')
                assert opened['key_reads']==closed['key_reads']==before['key_reads']
            saved=save('MAPHD',saves);restore('MAPHD',saves)
            key('readback-activate','Tab');navigate(CASES[-1],'readback');base.capture('map-readback')
            key('quit-menu','F1');base.wait_for(lambda s:s['hd']['panel']=='city-f1','quit-menu-ready')
            if base.status()['hd']['panel_selection']!=0:key('quit-choice','Down')
            key('quit-confirm','space');base.wait_for(lambda s:s['hd']['file_dialog']=='quit-confirm','quit-ready')
            subprocess.run(['xdotool','type','--delay','150','Y'],check=True)
            base.wait_for(lambda s:s['dos_blocked'] and any(k.get('Via')=='int21-AH07' and k.get('Key')==89 for k in s.get('key_reads') or []),'ending',seconds=180)
            front_key('space');base.wait_for(lambda s:s.get('dos_exited'),'dos-exit');assert game.wait(timeout=10)==0
            assert all(sha(Path(p).read_bytes())==h for p,h in SEEDS.values())
            (root/'verification.json').write_text(json.dumps({'issue':62,'phase':phase,'normal_gui':True,'state_injection':False,
                'checkpoint':False,'native_exit_tested':True,'original_save_read':True,'seeds':SEEDS,'seed_unchanged':True,
                'final_save_sha256':saved,'save_unchanged_after_read':sha((saves/'MAPHD.SAV').read_bytes())==saved,
                'cases':results,'screenshots':shots,'new_construction_tested':False,
                'binary_sha256':sha(binary.read_bytes()),'script_sha256':sha(script)},ensure_ascii=False,indent=2)+'\n')
        finally:
            if game.poll() is None:
                (root/'stop').write_text('stop\n')
                try:game.wait(timeout=10)
                except subprocess.TimeoutExpired:game.kill();game.wait()
            assert game.returncode==0,game.returncode


if __name__=='__main__':main()
