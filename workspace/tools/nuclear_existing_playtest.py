#!/usr/bin/env python3
"""#46：正常冷讀既有核電廠、捲動、F11／F12及原版存讀退出。"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import zipfile

import city_menu_playtest as base
from chart_window_playtest import model
from facility_batch_playtest import key, front_key, save, restore, toolbar_selection, language, LANGS
from facility_cursor import locate_small_cursor
from hd_source_audit import scene, cell, sha
from infrastructure_catalog import sources


def main():
    root=base.root; assert not root.exists() and root.parent.stat().st_uid==1000
    root.mkdir(); saves=root/'saves'; saves.mkdir()
    seed=Path('/seed/FUND.SAV'); seed_sha='fdd4e3a9c0da6320bb0a2a4357f948589ebc34d0061d54ae624951b190bbc96f'
    assert sha(seed.read_bytes())==seed_sha
    shutil.copyfile(seed,saves/'FUND.SAV')
    phase=os.environ.get('TAIPEI_NUCLEAR_PHASE','baseline'); assert phase in ['baseline','hd']
    binary=Path('/workspace/runs')/os.environ.get('TAIPEI_NUCLEAR_BINARY','taipei-preview')
    aliases=sources(Path('/orig/RS201.ROM').read_bytes()); script=Path(__file__).read_bytes()
    (root/'executed-driver.py').write_bytes(script)
    shots=[]; navigation=[]; expected=None
    with (root/'app.log').open('w') as log:
        game=subprocess.Popen([str(binary),'-original','/orig','-saves',str(saves),'-receipts',str(root),
            '-mute','-steps-per-update','2000000','-receipt-every-updates','6','-theme','hd-b',
            '-materials','/workspace/prototypes/hd-style','-catalog','/workspace/app/locales/ui.tsv',
            '-stop-file',str(root/'stop')],stdout=log,stderr=subprocess.STDOUT)
        try:
            base.cold_city(); _,pristine=model(); restore('FUND',saves)
            assert int(base.status()['hd']['footer_text'][3])==77413
            def prepare(label):
                key(label+'-toolbar','Tab'); _,frame=model()
                # This saved city restores without a border; Tab activates its
                # existing single-cell tool directly. Space would demolish.
                selected=toolbar_selection(frame,pristine); assert selected==0
                for axis,goal in [('X',52),('Y',40)]:
                    for i in range(128):
                        st=base.status()
                        if st['map_origin'][axis]==goal:break
                        direction=('Right' if axis=='X' else 'Down') if st['map_origin'][axis]<goal else ('Left' if axis=='X' else 'Up')
                        key(f'{label}-route-{axis}-{i}',direction)
                        base.wait_for(lambda s:s['map_origin']['Valid'],'map-redraw-ready')
                        navigation.append({'key':direction,'steps':base.status()['steps'],'origin':base.status()['map_origin']})
                    else:raise AssertionError(('正常捲動未到達原版核電廠視窗',axis))
                st,frame=model(); assert scene(st,frame)
                cursor=locate_small_cursor(frame,aliases)
                for axis,keys,goal in [(0,('Left','Right'),26),(1,('Up','Down'),1)]:
                    while cursor[axis]!=goal:
                        delta=1 if cursor[axis]<goal else -1
                        key(f'{label}-cursor-{axis}-{cursor[axis]}',keys[delta>0]); cursor[axis]+=delta
                st,frame=model(); assert st['map_origin']=={'X':52,'Y':40,'Valid':True} and scene(st,frame)
                assert int(st['hd']['footer_text'][3])==77413
                tiles=[sha(cell(frame,77+x*9,70+y*9)) for y in range(6) for x in range(6)]
                if expected is not None:assert tiles==expected
                if phase=='hd':assert st['hd']['nuclear_facility']['painted']==36
                return tiles
            def capture(label):
                base.capture(label)
                with zipfile.ZipFile(root/(label+'-capture.zip')) as z:
                    st=json.loads(z.read('status.json')); raw=z.read('frame-index.bin'); png=z.read('presentation.png')
                assert sha(raw)==st['frame_index_sha256'] and not st.get('unimplemented')
                assert [sha(cell(raw,77+x*9,70+y*9)) for y in range(6) for x in range(6)]==expected
                if phase=='hd':assert st['hd']['nuclear_facility']['painted']==(36 if st['hd_enabled'] else 0)
                (root/(label+'.png')).write_bytes(png)
                shots.append({'file':label+'.png','png_sha256':sha(png),'capture_sha256':sha((root/(label+'-capture.zip')).read_bytes()),
                    'frame_index_sha256':sha(raw),'language':st['language'],'hd_enabled':st['hd_enabled'],
                    'steps':st['steps'],'ticks':st['ticks'],'map_origin':st['map_origin']})
            expected=prepare('first-view'); capture('existing-nuclear')
            before=base.status(); front_key('F12'); base.wait_for(lambda s:not s['hd_enabled'],'original-ready')
            capture('nuclear-original'); assert base.status()['key_reads']==before['key_reads']
            front_key('F12'); base.wait_for(lambda s:s['hd_enabled'],'hd-ready')
            for lang in LANGS:language(lang); capture('nuclear-'+lang)
            saved=save('NUCLEAR',saves); restore('NUCLEAR',saves); prepare('readback'); capture('readback-nuclear')
            key('quit-menu','F1'); base.wait_for(lambda s:s['hd']['panel']=='city-f1','quit-menu-ready')
            if base.status()['hd']['panel_selection']!=0:key('quit-choice','Down')
            key('quit-confirm','space'); base.wait_for(lambda s:s['hd']['file_dialog']=='quit-confirm','quit-ready')
            subprocess.run(['xdotool','type','--delay','150','Y'],check=True)
            base.wait_for(lambda s:s['dos_blocked'] and any(k.get('Via')=='int21-AH07' and k.get('Key')==89
                for k in s.get('key_reads') or []),'ending',seconds=180)
            base.capture('native-ending'); front_key('space'); base.wait_for(lambda s:s.get('dos_exited'),'dos-exit')
            assert game.wait(timeout=10)==0
            (root/'verification.json').write_text(json.dumps({'issue':46,'phase':phase,'normal_gui':True,'state_injection':False,
                'checkpoint':False,'new_nuclear_construction_tested':False,'existing_plant_world':[60,44],
                'native_rect':[77,70,54,54],'origin':{'X':52,'Y':40,'Valid':True},'source_cells':expected,
                'seed_save_sha256':seed_sha,'seed_unchanged':sha(seed.read_bytes())==seed_sha,
                'binary_sha256':sha(binary.read_bytes()),'script_sha256':sha(script),'screenshots':shots,
                'navigation':navigation,'save_sha256':saved,'original_save_read':True,'native_exit':True,
                'scope':'正常冷讀既有核電廠、捲動、五語系及F12、原版存讀退出；baseline期核電廠保持原像素，HD期另驗。'},ensure_ascii=False,indent=2)+'\n')
            print('PASS existing nuclear',phase,'source cells',len(expected),'native exit',flush=True)
        finally:
            if game.poll() is None:
                (root/'stop').write_text('stop\n')
                try:game.wait(timeout=10)
                except subprocess.TimeoutExpired:game.kill();game.wait()
            assert game.returncode==0,game.returncode


if __name__=='__main__':main()
