#!/usr/bin/env python3
"""#58: one cold boot, original BASE.SAV reload between twelve facilities."""
import json
import os
from pathlib import Path
import subprocess
import time
import zipfile

import city_menu_playtest as base
from chart_window_playtest import model
from infrastructure_playtest import key as ordinary_key
from infrastructure_catalog import sources
from hd_source_audit import cell, scene, sha, MATERIAL

CASES=[('waste',9,0),('sewage',9,1)]+[(n,10,i) for i,n in enumerate([
    'sun-yat-sen','chiang-kai-shek','palace-museum','february-28','art-museum',
    'amusement-park','stadium','confucius-temple','zoo','baseball-dome'])]
LANGS=['zh-Hant','zh-Hans','ja','ko','en']
actions=[]


def key(label,value):
    # Confirm the front end saw a press, release it, then confirm DOS consumed
    # exactly one word. Holding until consumption can block a native release gate.
    scans={'Left':0x4b,'Right':0x4d,'Up':0x48,'Down':0x50,'Tab':0x0f,'Escape':0x01,
           **{f'F{i}':0x3a+i for i in range(1,7)}}
    if value not in scans:
        ordinary_key(label,value)
        return
    scan=scans[value];word=(scan<<8)|({'Tab':9,'Escape':27}.get(value,0))
    before=base.status()
    inputs=lambda s,c:sum(e.get('kind')=='keyboard' and e.get('scan')==c for e in s.get('inputs',[]))
    reads=lambda s:sum(e.get('Word')==word for e in s.get('key_reads') or [])
    presses,breaks,count=inputs(before,scan),inputs(before,scan+128),reads(before)
    subprocess.run(['xdotool','keydown',value],check=True)
    try:base.wait_for(lambda s:inputs(s,scan)==presses+1,label+'-press')
    finally:subprocess.run(['xdotool','keyup',value],check=True)
    base.wait_for(lambda s:inputs(s,scan+128)==breaks+1,label+'-release')
    after=base.wait_for(lambda s:reads(s)==count+1,label+'-read')
    assert len(after['key_reads'])==len(before['key_reads'])+1,label
    base.capture(label)
    actions.append({'label':label,'key':value,'word':word,'steps':after['steps'],
                    'original_read':after['key_reads'][-1],'release_before_read_wait':True})


def language(lang):
    before=base.status()
    if before['language']==lang:return
    front_key('F11');opened=base.wait_for(lambda s:s['language_panel'],'language-open')
    for _ in range((LANGS.index(lang)-LANGS.index(before['language']))%5):front_key('Down')
    chosen=base.wait_for(lambda s:s['language_selection']==LANGS.index(lang),'language-selected')
    for field in ['steps','frame_index_sha256','registers','segments','ip','ticks','key_reads','file_ops','palette']:
        assert chosen[field]==opened[field],field
    front_key('Return')
    after=base.wait_for(lambda s:s['language']==lang and not s['language_panel'],'language-'+lang)
    assert not after['language_warning'] and after['key_reads']==before['key_reads']


def screenshot(root,label,shots):
    base.capture(label)
    raw=(root/(label+'-capture.zip')).read_bytes()
    with zipfile.ZipFile(root/(label+'-capture.zip')) as z:
        s=json.loads(z.read('status.json'));frame=z.read('frame-index.bin');png=z.read('presentation.png')
    assert sha(frame)==s['frame_index_sha256'] and not s.get('unimplemented')
    # Original save-browser probes before creation are retained in MissingFiles.
    # Successful scratch save/load is verified separately using hashes and reads.
    assert {n.upper() for n in s.get('missing') or []}<={'*.SAV','BASE.SAV','PUBLIC.SAV'}
    (root/(label+'.png')).write_bytes(png)
    shots.append({'file':label+'.png','png_sha256':sha(png),'capture_sha256':sha(raw),
        'frame_index_sha256':sha(frame),'language':s['language'],'hd_enabled':s['hd_enabled'],
        'steps':s['steps'],'ticks':s['ticks'],'map_origin':s['map_origin']})
    return s,frame


def front_key(value):
    subprocess.run(['xdotool','keydown',value],check=True)
    time.sleep(.15)
    subprocess.run(['xdotool','keyup',value],check=True)


def menu(selection):
    key('file-menu','F2')
    s=base.wait_for(lambda s:s['hd']['panel']=='city-f2','file-ready')
    for _ in range((selection-s['hd']['panel_selection'])%4):key('file-down','Down')
    key('file-open','space')
    base.wait_for(lambda s:s['hd']['file_dialog']=='file-browser','file-browser')


def save(name,saves):
    menu(0)
    for _ in range(len(base.status()['hd']['file_text'][0].strip())):key('filename-backspace','BackSpace')
    subprocess.run(['xdotool','type','--delay','150',name.lower()],check=True)
    base.wait_for(lambda s:s['hd']['file_text'][0].strip()==name,'save-name')
    key('save-accept','space')
    f=saves/(name+'.SAV')
    assert f.is_file() and f.stat().st_size==93567
    return sha(f.read_bytes())


def restore(name,saves):
    before=base.status()
    count=lambda s:sum(f.get('Op')=='read' and f.get('Name','').upper()==name+'.SAV' for f in s['file_ops'])
    reads=count(before)
    expected=sha((saves/(name+'.SAV')).read_bytes())
    menu(1)
    for _ in range(8):
        if base.status()['hd']['file_text'][0].strip()==name:break
        key('load-file-down','Down')
    assert base.status()['hd']['file_text'][0].strip()==name
    key('load-accept','space')
    base.wait_for(lambda s:count(s)>reads,'save-read')
    assert sum(f['Len'] for f in base.status()['file_ops'] if f.get('Op')=='read' and
        f.get('Name','').upper()==name+'.SAV' and f['Step']>before['steps'])==93567
    assert sha((saves/(name+'.SAV')).read_bytes())==expected
    s,f=model();assert scene(s,f)


def toolbar(frame):
    return sha(b''.join(frame[y*320+270:y*320+320] for y in range(175)))


def toolbar_selection(frame,pristine):
    # 019's complete 22x22 icon variants: white, selected red, hover purple.
    hover,selected=[],[]
    for i in range(14):
        x,y=273+23*(i%2),4+24*(i//2)
        color=frame[y*320+x]
        assert color in [15,32,186],('工具外框來源未知',i,color)
        for dy in range(22):
            for dx in range(22):
                at=(y+dy)*320+x+dx
                want=color if dx in [0,21] or dy in [0,21] else pristine[at]
                assert frame[at]==want,('完整工具來源不符',i,dx,dy)
        if color==186:hover.append(i)
        elif color==32:selected.append(i)
    assert len(hover)<=1 and len(selected)<=1
    return (hover or selected)[0] if hover or selected else None


def main():
    root=base.root
    assert not root.exists() and root.parent.stat().st_uid==1000
    root.mkdir();saves=root/'saves';saves.mkdir()
    aliases=sources(Path('/orig/RS201.ROM').read_bytes())
    manifest=json.loads(Path('/workspace/prototypes/hd-style/tool-menus-v1/manifest.json').read_text())
    entries={t:{s['source_sha256']:s['selection'] for s in manifest['states'] if s['id']==f'tool-{t:02d}'} for t in [9,10]}
    phase=os.environ.get('TAIPEI_FACILITY_PHASE','source')
    cases=CASES if phase=='source' else CASES[:2]
    cases=[c for c in cases if c[0] not in os.environ.get('TAIPEI_FACILITY_SKIP','').split(',')]
    binary=Path('/workspace/runs')/('taipei-preview-public-probe-r1' if phase=='source' else 'taipei-preview-public-r1')
    if os.environ.get('TAIPEI_FACILITY_BINARY'):
        binary=Path(os.environ['TAIPEI_FACILITY_BINARY'])
    results=[];shots=[]
    p=subprocess.Popen([str(binary),'-original','/orig','-saves',str(saves),'-receipts',str(root),
        '-mute','-steps-per-update','400000','-receipt-every-updates','6','-theme','hd-b','-materials','/workspace/prototypes/hd-style',
        '-catalog','/workspace/app/locales/ui.tsv','-stop-file',str(root/'stop')],stdout=(root/'app.log').open('w'),stderr=subprocess.STDOUT)
    try:
        base.cold_city()
        save_sha=save('BASE',saves)
        initial,pristine=model();assert scene(initial,pristine)
        assert toolbar_selection(pristine,pristine) is None
        current=0  # 004: cold new-city toolbar cursor starts at tool zero.
        for number,(case,tool,option) in enumerate(cases):
            if number:
                restore('BASE',saves)
                # 004: after the original load returns to the map, Tab restores
                # the selected tool and switches back to toolbar focus.
                key('restore-toolbar','Tab')
                st,frame=model()
                current=toolbar_selection(frame,pristine)
                assert current is not None,'讀檔後選取框未知'
            while current//2 != tool//2:
                direction=1 if current//2<tool//2 else -1
                key(case+'-tool-row','Down' if direction>0 else 'Up');current+=2*direction
            if current%2!=tool%2:
                key(case+'-tool-col','Right' if tool%2 else 'Left');current+=1 if tool%2 else -1
            assert current==tool
            st,frame=model();assert toolbar_selection(frame,pristine)==tool
            key(case+'-submenu','space')
            rect=(196,124,69,35) if tool==9 else (18,37,235,132)
            def choice():
                st,frame=model();assert st['dos_blocked']
                x,y,w,h=rect
                return entries[tool].get(sha(b''.join(frame[cy*320+x:cy*320+x+w] for cy in range(y,y+h))))
            selected=choice();assert selected is not None
            for _ in range((option-selected)%len(entries[tool])):key(case+'-choose','Down')
            assert choice()==option
            key(case+'-confirm','space')
            st,frame=model();assert scene(st,frame) and st['map_origin']==initial['map_origin']
            fee,budget=int(st['hd']['footer_text'][0]),int(st['hd']['footer_text'][3])
            if fee>budget:
                results.append({'id':case,'tool':tool,'option':option,'fee':fee,'budget':budget,'blocked':'原版資金不足，未取得施工來源'})
                (root/'result-progress.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
                continue
            # Empty city loaded normally: changed map cells are the visible cursor outline.
            changed=[(x,y) for y in range(15) for x in range(29) if cell(frame,5+x*9,34+y*9)!=cell(pristine,5+x*9,34+y*9)]
            assert changed
            cursor=[min(x for x,y in changed),min(y for x,y in changed)]
            span=[max(x for x,y in changed)-cursor[0]+1,max(y for x,y in changed)-cursor[1]+1]
            assert span[0]==span[1] and span[0] in [4,6],(case,'游標矩形未知',cursor,span)
            def walk(target):
                for axis,keys in [(0,('Left','Right')),(1,('Up','Down'))]:
                    while cursor[axis]!=target[axis]:
                        direction=1 if cursor[axis]<target[axis] else -1
                        key(f'{case}-walk-{axis}-{cursor[axis]}',keys[direction>0]);cursor[axis]+=direction
            walk((22,3));key(case+'-place','space')
            # Preserve the completed-construction observation window used by
            # the validated 60-update probes; only other key waits are shorter.
            placed=base.status()['steps']
            base.wait_for(lambda s:s['steps']>=placed+24_000_000,case+'-construction-fence')
            walk((16,3))
            st,frame=model();assert scene(st,frame) and st['map_origin']==initial['map_origin']
            known=[]
            for y in range(15):
                for x in range(29):
                    raw=cell(frame,5+x*9,34+y*9)
                    if raw!=cell(pristine,5+x*9,34+y*9) and raw in aliases and not set(raw)<=MATERIAL:
                        known.append({'cell':[x,y],'source_sha256':sha(raw),'sources':aliases[raw]})
            assert known,(case,'沒有已知施工圖像')
            xs=[r['cell'][0] for r in known];ys=[r['cell'][1] for r in known]
            bounds=[min(xs),min(ys),max(xs)-min(xs)+1,max(ys)-min(ys)+1]
            assert bounds[:2]==[22,3] and len(known)==bounds[2]*bounds[3] and bounds[2:]==span,(case,bounds,len(known),span)
            base.capture(case+'-complete')
            results.append({'id':case,'tool':tool,'option':option,'fee':fee,'before_budget':budget,
                'after_budget':int(st['hd']['footer_text'][3]),'bounds':bounds,'known':known,
                'receipt':case+'-complete-capture.zip','steps':st['steps'],'origin':st['map_origin']})
            (root/'result-progress.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
            print('COMPLETE',case,bounds,'ROM',sorted({a['member'] for r in known for a in r['sources']}),flush=True)
            if phase=='hd':
                expected=len(known)
                assert st['hd']['public_facilities']['painted']==expected
                before=base.status();front_key('F12')
                base.wait_for(lambda s:not s['hd_enabled'],'original-ready')
                original,raw=screenshot(root,case+'-original',shots)
                assert raw==frame and original['key_reads']==before['key_reads']
                assert original['hd']['public_facilities']['painted']==0
                front_key('F12');base.wait_for(lambda s:s['hd_enabled'],'hd-ready')
                for lang in (LANGS if number==len(cases)-1 else ['zh-Hant']):
                    language(lang);shown,raw=screenshot(root,case+'-'+lang,shots)
                    assert raw==frame and shown['hd']['public_facilities']['painted']==expected
        if phase=='hd':
            final_sha=save('PUBLIC',saves)
            restore('PUBLIC',saves)
            assert base.status()['hd']['public_facilities']['painted']==len(results[-1]['known'])
        key('quit-menu','F1');base.wait_for(lambda s:s['hd']['panel']=='city-f1','quit-menu-ready')
        if base.status()['hd']['panel_selection']!=0:key('quit-choice','Down')
        key('quit-confirm','space');base.wait_for(lambda s:s['hd']['file_dialog']=='quit-confirm','quit-ready')
        subprocess.run(['xdotool','type','--delay','150','Y'],check=True)
        base.wait_for(lambda s:s['dos_blocked'] and s['hd']['ending_screen']=='achievement-base','ending',seconds=180)
        front_key('space');base.wait_for(lambda s:s.get('dos_exited'),'dos-exit')
        report={'issue':58,'phase':phase,'normal_gui':True,'state_injection':False,'checkpoint':False,
            'baseline_save_sha256':save_sha,'native_exit_tested':True,'binary_sha256':sha(binary.read_bytes()),
            'receipt_every_updates':6,'steps_per_update':400000,
            'construction_input_fence_steps':24_000_000,
            'cases':results,'screenshots':shots,'actions':actions,'ordinary_sync':base.ordinary_sync,'arrow_sync':base.sync}
        if phase=='hd':report.update(final_save_sha256=final_sha,original_save_read=True,save_unchanged_after_read=True,cold_reload_tested=False)
        (root/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    finally:
        if p.poll() is None:
            (root/'stop').write_text('stop\n')
            try:p.wait(timeout=10)
            except subprocess.TimeoutExpired:p.kill();p.wait()
        assert p.returncode==0


if __name__=='__main__':main()
