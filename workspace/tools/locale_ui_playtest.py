#!/usr/bin/env python3
"""#49：兩次冷啟動的 F11 短流程；不注入快照或抽樣 VM 狀態。"""
import hashlib
import io
import json
import os
import subprocess
import time
import zipfile
from pathlib import Path

root=Path('/workspace/runs')/os.environ['TAIPEI_LOCALE_RUN']
root.mkdir(mode=0o700)
saves=root/'saves';saves.mkdir()
binary=Path('/workspace/runs/taipei-preview-locale-r1')
catalog=Path('/workspace/app/locales/ui.tsv')
results=[]

def status(out):
    try:
        with zipfile.ZipFile(out/'capture.zip') as z:
            s=json.loads(z.read('status.json'))
            assert hashlib.sha256(z.read('frame-index.bin')).hexdigest()==s['frame_index_sha256']
            return s
    except (FileNotFoundError,zipfile.BadZipFile):return {}

def wait(out,predicate,label,seconds=90):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        s=status(out)
        if predicate(s):
            print(label,s.get('steps'),s.get('language'),flush=True);return s
        time.sleep(.1)
    raise RuntimeError(f'{label}: {status(out)}')

def key(name):
    subprocess.run(['xdotool','keydown',name],check=True)
    time.sleep(.2)
    subprocess.run(['xdotool','keyup',name],check=True)

def capture(out,label):
    raw=(out/'capture.zip').read_bytes()
    (out/(label+'.zip')).write_bytes(raw)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        (out/(label+'.png')).write_bytes(z.read('presentation.png'))

def modal_unchanged(before,after):
    for field in ['steps','registers','segments','ip','ticks','frame_index_sha256','key_reads','file_ops','palette']:
        assert before[field]==after[field],field
    for kind in ['keyboard','text','mouse-move','mouse-button']:
        assert [i for i in before['inputs'] if i['kind']==kind]==[i for i in after['inputs'] if i['kind']==kind],kind

def labels(out,language):
    with zipfile.ZipFile(out/'capture.zip') as z:
        got=z.read('presentation.png')
    base=Path('/workspace/prototypes/hd-style')
    path=base/'locale-draft-r1'/f'city-{language}.png'
    if language=='zh-Hant':path=base/'font-comparison/noto-font.png'
    ref=path.read_bytes()
    for i in range(6):
        args=['convert','png:-','-crop',f'136x68+{28+i*176}+40','+repage','-depth','8','rgba:-']
        actual=subprocess.run(args,input=got,stdout=subprocess.PIPE,check=True).stdout
        expected=subprocess.run(args,input=ref,stdout=subprocess.PIPE,check=True).stdout
        assert len(actual)==136*68*4 and actual==expected,(language,i)

def start(out):
    out.mkdir()
    log=(out/'app.log').open('w')
    p=subprocess.Popen([str(binary),'-original','/orig','-saves',str(saves),'-receipts',str(out),
        '-mute','-steps-per-update','400000','-theme','hd-b','-materials','/workspace/prototypes/hd-style',
        '-catalog',str(catalog),'-stop-file',str(out/'stop')],stdout=log,stderr=subprocess.STDOUT)
    return p,log

def stop(p,out,log):
    (out/'stop').write_text('stop\n')
    try:assert p.wait(timeout=10)==0
    finally:
        if p.poll() is None:p.kill();p.wait()
        log.close()

out=root/'first';p,log=start(out)
try:
    wait(out,lambda s:s.get('steps',0)>=700_000_000,'intro')
    subprocess.run(['xdotool','search','--name','模擬台北','windowfocus'],check=True)
    key('space')
    wait(out,lambda s:s.get('steps',0)>=800_000_000,'intro-wait')
    key('space')
    wait(out,lambda s:s.get('frame_index_sha256')=='5442a8135d36552561f03a46fc443978a76989979e0c25dc016027229b24dda4','main-menu')
    for panel in ['city','new-game','difficulty','map']:
        before=status(out)['steps'];key('space')
        wait(out,lambda s:s.get('steps',0)>=before+24_000_000,panel)
    wait(out,lambda s:s.get('hd',{}).get('FontLabels')==6 or s.get('hd',{}).get('font_labels')==6,'six-labels')
    key('0')
    wait(out,lambda s:any(k.get('Key')==48 for k in s.get('key_reads',[])),'native-pause')
    for index,language in [(1,'zh-Hans'),(2,'ja'),(3,'ko'),(4,'en'),(0,'zh-Hant')]:
        key('F11');opened=wait(out,lambda s:s.get('language_panel') is True,'open-language')
        key('Down');selected=wait(out,lambda s:s.get('language_selection')==index,'select-'+language)
        modal_unchanged(opened,selected)
        capture(out,'picker-'+language)
        key('F12');original=wait(out,lambda s:s.get('hd_enabled') is False,'modal-original')
        modal_unchanged(opened,original)
        key('F12');restored=wait(out,lambda s:s.get('hd_enabled') is True,'modal-hd')
        modal_unchanged(opened,restored)
        key('Return')
        applied=wait(out,lambda s:s.get('language')==language and s.get('language_panel') is False,'apply-'+language)
        assert json.loads((saves/'frontend-settings.json').read_text())=={'schema':1,'language':language}
        assert applied['key_reads']==opened['key_reads'],'selection leaked to DOS'
        labels(out,language);capture(out,'city-'+language)
        results.append({'language':language,'modal_vm_unchanged':True,'no_dos_input':True,'six_reference_labels':True,'settings_saved':True})
    key('F1');wait(out,lambda s:s.get('hd',{}).get('panel')=='city-f1','original-f1')
    capture(out,'original-f1');key('Escape')
    wait(out,lambda s:s.get('hd',{}).get('font_labels')==6,'return-from-f1')
    key('F11');wait(out,lambda s:s.get('language_panel') is True,'persist-open')
    # Mouse choice uses logical 1280x800 coordinates in the real window.
    window=subprocess.check_output(['xdotool','getwindowfocus'],text=True).strip()
    subprocess.run(['xdotool','mousemove','--window',window,'640','547','click','1'],check=True)
    wait(out,lambda s:s.get('language')=='en' and s.get('language_panel') is False,'mouse-english')
    capture(out,'mouse-english')
finally:stop(p,out,log)

out=root/'reload';p,log=start(out)
try:
    initial=wait(out,lambda s:s.get('frames',0)>=60,'fresh-process-settings')
    assert initial['language']=='en' and initial['catalog_source']=='external-tsv'
    # English window title after restart proves startup settings affect the real window.
    subprocess.run(['xdotool','search','--name','Taipei Simulation','windowfocus'],check=True)
    key('F11');opened=wait(out,lambda s:s.get('language_panel') is True,'reload-picker')
    assert opened['language_selection']==4
    capture(out,'persisted-english-picker')
    key('Down');wait(out,lambda s:s.get('language_selection')==0,'cancel-selection')
    key('Escape');closed=wait(out,lambda s:s.get('language_panel') is False,'cancel-picker')
    assert closed['language']=='en'
    assert json.loads((saves/'frontend-settings.json').read_text())['language']=='en'
finally:stop(p,out,log)

report={'issue':49,'cold_starts':2,'checkpoint':False,'normal_gui':True,'languages':results,
    'f1_preserved':True,'mouse_english':True,'settings_cold_reload':True,'escape_cancel':True,
    'original_save_written':False,'native_exit_tested':False,'long_state_sampling':False,
    'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'catalog_sha256':hashlib.sha256(catalog.read_bytes()).hexdigest()}
(root/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS: F11 five locales, modal isolation, F12, native F1, mouse, settings cold reload, Escape cancel',flush=True)
