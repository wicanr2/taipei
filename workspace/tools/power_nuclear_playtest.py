#!/usr/bin/env python3
"""#46 DRAFT：冷讀原版籌資存檔，正常整地、核能施工及存退讀。"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import zipfile

import city_menu_playtest as base
from chart_window_playtest import model
from facility_batch_playtest import key, front_key, save, restore, toolbar_selection
from facility_cursor import ConstructionGate
from hd_source_audit import cell, scene, sha, MATERIAL
from infrastructure_catalog import sources


def main():
    root=base.root
    assert not root.exists() and root.parent.stat().st_uid==1000
    seed=Path(os.environ['TAIPEI_NUCLEAR_SAVE'])
    phase=os.environ.get('TAIPEI_NUCLEAR_PHASE','build'); assert phase in ['plan','build']
    assert seed.is_file() and seed.stat().st_size==93567
    expected=os.environ['TAIPEI_NUCLEAR_SAVE_SHA']; assert sha(seed.read_bytes())==expected
    root.mkdir(); saves=root/'saves'; saves.mkdir()
    shutil.copyfile(seed,saves/'FUND.SAV')
    assert sha((saves/'FUND.SAV').read_bytes())==expected
    binary=Path('/workspace/runs/taipei-preview')
    aliases=sources(Path('/orig/RS201.ROM').read_bytes()); gate=ConstructionGate(aliases)
    script_sha=sha(Path(__file__).read_bytes())
    with (root/'app.log').open('w') as log:
        game=subprocess.Popen([str(binary),'-original','/orig','-saves',str(saves),'-receipts',str(root),
            '-mute','-steps-per-update','2000000','-receipt-every-updates','6','-theme','hd-b',
            '-materials','/workspace/prototypes/hd-style','-catalog','/workspace/app/locales/ui.tsv',
            '-stop-file',str(root/'stop')],stdout=log,stderr=subprocess.STDOUT)
        try:
            base.cold_city(); _,pristine=model()
            restore('FUND',saves)
            loaded,frame=model(); origin=loaded['map_origin']; loaded_frame=frame
            assert scene(loaded,frame) and origin['Valid']
            initial_funds=int(loaded['hd']['footer_text'][3])
            if phase=='build':assert initial_funds>=100000
            base.capture('funded-city')
            # 004／#58 的原版冷讀路徑：回地圖後 Tab 恢復已選工具。
            key('demolition-toolbar','Tab'); _,frame=model()
            current=toolbar_selection(frame,pristine); assert current is not None
            while current//2:
                key(f'demolition-row-{current}','Up'); current-=2
            if current%2:key('demolition-column','Left')
            _,frame=model(); assert toolbar_selection(frame,pristine)==0
            key('demolition-confirm','space')
            st,frame=model(); assert scene(st,frame) and st['map_origin']==origin
            changed=[(x,y) for y in range(15) for x in range(29)
                if cell(frame,5+x*9,34+y*9)!=cell(loaded_frame,5+x*9,34+y*9)]
            if not changed:
                # The original load can already display the same small cursor.
                # Match only the exact observed border with a real ROM interior.
                variants=set()
                for raw in aliases:
                    v=bytearray(raw)
                    for dx in range(9):v[dx]=15 if dx%2==0 else 0
                    for dy in range(9):v[dy*9]=15; v[dy*9+8]=15
                    for dx in range(9):v[72+dx]=15 if dx%2==0 else 0
                    variants.add(bytes(v))
                changed=[(x,y) for y in range(15) for x in range(29)
                    if cell(frame,5+x*9,34+y*9) not in aliases and cell(frame,5+x*9,34+y*9) in variants]
                assert len(changed)==1,('無法唯一辨識原版單格游標',changed)
            assert changed
            cursor=[min(x for x,y in changed),min(y for x,y in changed)]
            assert [max(x for x,y in changed)-cursor[0]+1,max(y for x,y in changed)-cursor[1]+1]==[1,1],changed
            def walk(label,target):
                for axis,keys in [(0,('Left','Right')),(1,('Up','Down'))]:
                    while cursor[axis]!=target[axis]:
                        direction=1 if cursor[axis]<target[axis] else -1
                        key(f'{label}-{axis}-{cursor[axis]}',keys[direction>0]); cursor[axis]+=direction
                assert base.status()['map_origin']==origin,'正常研究走位意外捲動，停止'
            def land(raw):return set(raw)<=MATERIAL and not set(raw)&set(range(144,148))
            def eligible(raw):return raw in aliases and (not set(raw)<=MATERIAL or land(raw))
            # 只選已識別的陸地／建物，避開水域與視窗邊界。
            baseline=model_from(root/'funded-city-capture.zip')[1]
            sites=[]
            for row in range(2,8):
                for col in range(2,16):
                    tiles=[cell(baseline,5+x*9,34+y*9) for y in range(row,row+6) for x in range(col,col+6)]
                    if all(eligible(t) for t in tiles):sites.append((sum(not land(t) for t in tiles),col,row))
            assert sites,'目前視窗沒有已識別的完整六格陸地，不猜測其他位置'
            _,left,top=min(sites)
            fee=int(st['hd']['footer_text'][0])
            def native_quit():
                key('quit-menu','F1'); base.wait_for(lambda s:s['hd']['panel']=='city-f1','quit-menu-ready')
                if base.status()['hd']['panel_selection']!=0:key('quit-choice','Down')
                key('quit-confirm','space'); base.wait_for(lambda s:s['hd']['file_dialog']=='quit-confirm','quit-ready')
                subprocess.run(['xdotool','type','--delay','150','Y'],check=True)
                base.wait_for(lambda s:s['dos_blocked'] and s['hd']['ending_screen']=='achievement-base','ending',seconds=180)
                front_key('space'); base.wait_for(lambda s:s.get('dos_exited'),'dos-exit'); assert game.wait(timeout=10)==0
            if phase=='plan':
                native_quit()
                (root/'preflight.json').write_text(json.dumps({'issue':46,'phase':phase,'normal_gui':True,
                    'state_injection':False,'checkpoint':False,'script_sha256':script_sha,'binary_sha256':sha(binary.read_bytes()),
                    'seed_save_sha256':expected,'seed_unchanged':sha(seed.read_bytes())==expected,
                    'funds':initial_funds,'origin':origin,'cursor':cursor,'demolition_fee':fee,
                    'site':[left,top,6,6],'native_exit':True,'construction_tested':False},ensure_ascii=False,indent=2)+'\n')
                return
            assert initial_funds>=100000+36*fee
            clearing=[]
            for row in range(top,top+6):
                for col in range(left,left+6):
                    walk('clear-target',(col,row))
                    before=base.status(); key(f'clear-{col}-{row}','space')
                    step=base.status()['steps']
                    base.wait_for(lambda s:s['steps']>=step+24_000_000,'clear-drawing')
                    after=base.status()
                    clearing.append({'cell':[col,row],'before_funds':int(before['hd']['footer_text'][3]),
                        'after_funds':int(after['hd']['footer_text'][3])})
            uncover=(left+6,top)
            walk('clear-uncover',uncover)
            _,frame=model()
            assert all(land(cell(frame,5+x*9,34+y*9)) for y in range(top,top+6) for x in range(left,left+6))
            base.capture('cleared-site')
            key('nuclear-toolbar','Tab'); key('nuclear-column','Right')
            for row in range(5):key(f'nuclear-row-{row}','Down')
            _,frame=model(); assert toolbar_selection(frame,pristine)==11
            key('nuclear-submenu','space')
            choices={r['source_sha256']:r['selection'] for r in json.loads(Path(
                '/workspace/prototypes/hd-style/tool-menus-v1/manifest.json').read_text())['states'] if r['id']=='tool-11'}
            def selection():
                s,f=model(); assert s['dos_blocked']
                return choices.get(sha(b''.join(f[y*320+196:y*320+265] for y in range(124,159))))
            assert selection() in [0,1]
            if selection()!=1:key('nuclear-choose','Down')
            assert selection()==1; base.capture('nuclear-choose')
            key('nuclear-confirm','space'); st,frame=model()
            assert scene(st,frame) and int(st['hd']['footer_text'][0])==100000
            assert int(st['hd']['footer_text'][3])>=100000
            small=model_from(root/'cleared-site-capture.zip')[1]
            large=[(x,y) for y in range(15) for x in range(29)
                if cell(frame,5+x*9,34+y*9)!=cell(small,5+x*9,34+y*9)]
            assert large and [min(x for x,y in large),min(y for x,y in large)]==cursor
            assert [max(x for x,y in large)-cursor[0]+1,max(y for x,y in large)-cursor[1]+1]==[6,6],('核能游標不是已見六格形態',large)
            # 原版工具切換保留已見游標原點，完整施工前／後另核對。
            walk('nuclear-target',(left,top)); base.capture('nuclear-before')
            before,old=model(); key('nuclear-place','space')
            def constructed():
                s,f=model()
                return scene(s,f) and s['map_origin']==origin and gate.ready(f,left,top,6,6)
            base.wait_for(lambda _:constructed(),'nuclear-complete-drawing')
            walk('nuclear-uncover',uncover); after,new=model(); assert scene(after,new)
            base.capture('nuclear-complete')
            known=[]; unknown=[]
            for row in range(15):
                for col in range(29):
                    x,y=5+col*9,34+row*9; a,b=cell(old,x,y),cell(new,x,y)
                    if a==b:continue
                    record={'cell':[col,row],'native_xy':[x,y],'before_sha256':sha(a),'after_sha256':sha(b)}
                    if b in aliases:
                        record.update(sources=aliases[b],terrain_only=set(b)<=MATERIAL); known.append(record)
                    else:unknown.append(record)
            cells=[{'cell':[x,y],'source_sha256':sha(cell(new,5+x*9,34+y*9))}
                for y in range(top,top+6) for x in range(left,left+6)]
            assert all(cell(new,5+r['cell'][0]*9,34+r['cell'][1]*9) in aliases and
                not set(cell(new,5+r['cell'][0]*9,34+r['cell'][1]*9))<=MATERIAL for r in cells)
            saved=save('NUCLEAR',saves); restore('NUCLEAR',saves); _,restored=model()
            assert all(sha(cell(restored,5+r['cell'][0]*9,34+r['cell'][1]*9))==r['source_sha256'] for r in cells)
            native_quit()
            report={'issue':46,'normal_gui':True,'checkpoint':False,'state_injection':False,'actions':[],
                'patterns':[{'label':'nuclear','choice':1,'before_receipt':'nuclear-before-capture.zip',
                    'receipt':'nuclear-complete-capture.zip','origin':origin,'known_changes':known,'unknown_changes':unknown}],
                'seed_save_file':str(seed),'seed_save_sha256':expected,'seed_unchanged':sha(seed.read_bytes())==expected,
                'script_sha256':script_sha,'binary_sha256':sha(binary.read_bytes()),'clearing':clearing,
                'initial_funds':initial_funds,'final_funds':int(after['hd']['footer_text'][3]),
                'native_exit':True,'original_save_read':True,'save_sha256':saved,'cells':cells,
                'ordinary_keys':base.ordinary_sync,'function_keys':base.sync,
                'scope':'正常冷讀原版籌資 SAV、整地、核能施工及存讀退出；未接核能 HD。'}
            (root/'result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        finally:
            if game.poll() is None:
                (root/'stop').write_text('stop\n')
                try:game.wait(timeout=10)
                except subprocess.TimeoutExpired:game.kill();game.wait()
            assert game.returncode==0,game.returncode


def model_from(path):
    with zipfile.ZipFile(path) as z:
        s=json.loads(z.read('status.json')); f=z.read('frame-index.bin')
    assert sha(f)==s['frame_index_sha256']; return s,f


if __name__=='__main__':main()
