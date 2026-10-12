#!/usr/bin/env python3
"""#51: normal GUI source inventory and translated field checks; no checkpoint."""
import hashlib
import io
import json
import os
import subprocess
import time
import zipfile
from pathlib import Path

root = Path('/workspace/runs') / os.environ['TAIPEI_INTERFACE_RUN']
root.mkdir(mode=0o700)
saves = root / 'saves'
saves.mkdir()
out = root / 'gui'
out.mkdir()
binary = Path(os.environ.get('TAIPEI_INTERFACE_BINARY','/workspace/runs/taipei-preview'))
catalog = Path('/workspace/app/locales/ui.tsv')
checks = []
roundtrips = []
acknowledged = []
phase = os.environ.get('TAIPEI_INTERFACE_PHASE', 'all')
assert phase in ['all', 'settings', 'files'], phase
tail_only, file_only = phase != 'all', phase == 'files'

def status():
    try:
        with zipfile.ZipFile(out / 'capture.zip') as z:
            s = json.loads(z.read('status.json'))
            assert hashlib.sha256(z.read('frame-index.bin')).hexdigest() == s['frame_index_sha256']
            return s
    except (FileNotFoundError, zipfile.BadZipFile):
        return {}

def wait(predicate, label, seconds=90):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        s = status()
        if predicate(s):
            print(label, s.get('steps'), s.get('language'), flush=True)
            return s
        time.sleep(.1)
    raise RuntimeError(f'{label}: {status().get("hd")}; {(out / "app.log").read_text()[-1500:]}')

def key(name):
    subprocess.run(['xdotool', 'keydown', name], check=True)
    time.sleep(.15)
    subprocess.run(['xdotool', 'keyup', name], check=True)

def native(name, label):
    before = status()
    ascii_keys={'space':(32,0x39),'Return':(13,0x1c),'Escape':(27,1),'Tab':(9,0x0f),
                **{str(i):(48+i,0x0b if i==0 else i+1) for i in range(10)}}
    scan={'Left':0x4b,'Right':0x4d,'Up':0x48,'Down':0x50,
          **{f'F{i}':0x3a+i for i in range(1,7)}}.get(name)
    if name in ascii_keys:
        code,scan=ascii_keys[name]
        matches=lambda k:k.get('Key')==code
    else:
        assert scan is not None,name
        matches=lambda k:k.get('Word')==scan<<8
    reads=sum(matches(k) for k in before.get('key_reads',[]))
    breaks=sum(i['kind']=='keyboard' and i.get('scan')==scan+128 for i in before.get('inputs',[]))
    subprocess.run(['xdotool','keydown',name],check=True)
    ordinary = name in ascii_keys
    if ordinary:
        # Text keys auto-repeat in X11. Release before waiting for the periodic
        # receipt, as the existing city-menu player-path harness does.
        time.sleep(.15)
        subprocess.run(['xdotool','keyup',name],check=True)
    try:
        pressed=wait(lambda s:sum(matches(k) for k in s.get('key_reads',[]))>=reads+1,
                     label+'-original-read',seconds=180)
    finally:
        if not ordinary:
            subprocess.run(['xdotool','keyup',name],check=True)
    released=wait(lambda s:sum(i['kind']=='keyboard' and i.get('scan')==scan+128
                               for i in s.get('inputs',[]))>=breaks+1 and
                   (s.get('dos_blocked') is True or
                    s.get('steps',0)>=pressed['steps']+24_000_000),label+'-release')
    actual=[k for k in released['key_reads'] if matches(k)]
    assert len(actual)==reads+1,(label,'duplicate original read')
    acknowledged.append({'label':label,'key':name,'read':actual[-1],
                         'read_receipt_step':pressed['steps'],'release_receipt_step':released['steps']})
    return released

def capture(label):
    raw = (out / 'capture.zip').read_bytes()
    (out / (label + '-capture.zip')).write_bytes(raw)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        (out / (label + '.png')).write_bytes(z.read('presentation.png'))
        (out / (label + '-native.png')).write_bytes(z.read('frame.png'))

def theme_roundtrip(label):
    before=status()
    key('F12')
    off=wait(lambda s:s.get('hd_enabled') is False,label+'-original')
    assert off['frame_index_sha256']==before['frame_index_sha256']
    assert off['key_reads']==before['key_reads']
    with zipfile.ZipFile(out/'capture.zip') as z:
        raw=z.read('frame.png')
        shown=z.read('presentation.png')
    expected=subprocess.run(['convert','png:-','-filter','point','-resize','1280x800!',
                             '-depth','8','rgba:-'],input=raw,stdout=subprocess.PIPE,check=True).stdout
    actual=subprocess.run(['convert','png:-','-depth','8','rgba:-'],input=shown,
                          stdout=subprocess.PIPE,check=True).stdout
    assert actual==expected,label
    capture(label+'-original')
    key('F12')
    after=wait(lambda s:s.get('hd_enabled') is True,label+'-hd')
    assert after['frame_index_sha256']==before['frame_index_sha256']
    assert after['key_reads']==before['key_reads']
    capture(label+'-hd')
    roundtrips.append(label)

def language(lang):
    before = status()
    key('F11')
    opened = wait(lambda s: s.get('language_panel') is True, 'picker')
    index = ['zh-Hant', 'zh-Hans', 'ja', 'ko', 'en'].index(lang)
    for _ in range((index - ['zh-Hant', 'zh-Hans', 'ja', 'ko', 'en'].index(before['language'])) % 5):
        key('Down')
    selected = wait(lambda s: s.get('language_selection') == index, 'select-' + lang)
    for field in ['steps','frame_index_sha256','registers','segments','ip','ticks','key_reads','file_ops','palette']:
        assert opened[field] == selected[field], field
    key('Return')
    after = wait(lambda s: s.get('language') == lang and not s.get('language_panel'), lang)
    for field in ['frame_index_sha256','file_ops','palette']:
        assert before[field] == after[field], field
    assert after['hd'].get('locale_reason') in ['matched-interface', 'source-fallback', 'preserved-player-filenames'], after['hd']

log = (out / 'app.log').open('w')
p = subprocess.Popen([str(binary), '-original','/orig','-saves',str(saves),'-receipts',str(out),
                      '-mute','-steps-per-update','400000','-theme','hd-b',
                      '-materials','/workspace/prototypes/hd-style','-catalog',str(catalog),
                      '-stop-file',str(out / 'stop')], stdout=log, stderr=subprocess.STDOUT)
try:
    wait(lambda s:s.get('steps',0)>=700_000_000,'intro',seconds=180)
    subprocess.run(['xdotool','search','--name','模擬台北','windowfocus'],check=True)
    key('space')
    wait(lambda s:s.get('steps',0)>=800_000_000,'intro-wait')
    key('space')
    wait(lambda s:s.get('hd',{}).get('panel')=='main','main')
    if os.environ.get('TAIPEI_INTERFACE_SOURCE_ONLY')=='disaster':
        native('Right','disaster-main-select')
        assert status()['hd']['panel_selection']==1
        native('space','disaster-city-open')
        capture('disaster-city-0')
        for selection in range(1,6):
            native('Down','disaster-city-select')
            capture('disaster-city-'+str(selection))
        (root/'inventory.json').write_text(json.dumps({'normal_gui':True,'checkpoint':False,
            'scope':'disaster city source inventory only','native_exit_tested':False})+'\n')
        raise SystemExit(0)
    for scene in ['main','city','new-game','difficulty']:
        if scene!='main': native('space',scene)
        if os.environ.get('TAIPEI_INTERFACE_QUICK')=='1':
            capture(scene+'-zh-Hant')
            continue
        for lang in ['zh-Hans','ja','ko','en','zh-Hant']:
            language(lang)
            assert status()['hd']['localized_fields']>0, (scene,lang,status()['hd'])
            capture(scene+'-'+lang)
            checks.append([scene,lang])
    native('space','city-map')
    wait(lambda s:s.get('hd',{}).get('font_labels')==6,'city-labels')
    native('0','pause')
    capture('city-paused')
    if not tail_only:
        # The original toolbar starts at index 0; one Down reaches road/metro.
        native('Down','road-tool-select')
        native('space','road-tool-open')
        assert status()['hd']['panel']=='tool-02'
        language('en')
        assert status()['hd']['localized_fields']>0
        capture('road-tool-en')
        checks.append(['tool-02','en'])
        theme_roundtrip('road-tool')
        native('space','road-tool-confirm')
        native('Tab','return-toolbar')
        subprocess.run(['xdotool','keydown','Shift_L'],check=True)
        try:
            key('F1')
        finally:
            subprocess.run(['xdotool','keyup','Shift_L'],check=True)
        wait(lambda s:s.get('help_panel') is True,'help-en')
        capture('help-en')
        key('Escape')
        wait(lambda s:s.get('help_panel') is False,'help-close')
        checks.append(['help','en'])
    for row in ([] if tail_only else [1,2]):
        native('F3','mayor-menu')
        wait(lambda s:s.get('hd',{}).get('panel')=='city-f3','mayor-ready')
        # Opening F3 remembers its selection; use its receipt rather than assuming zero.
        current=status()['hd']['panel_selection']
        for _ in range((row-current)%3): native('Down','mayor-select')
        native('space','mayor-open')
        capture('mayor-'+str(row))
        for lang in ['zh-Hans','ja','ko','en','zh-Hant']:
            language(lang)
            assert status()['hd']['interface_panel']==('population' if row==1 else 'opinion')
            capture('mayor-'+str(row)+'-'+lang)
            checks.append(['mayor-'+str(row),lang])
            if lang=='en': theme_roundtrip('mayor-'+str(row))
        native('Escape','mayor-close')
    language('en')
    for row in ([] if file_only else range(5)):
        native('F6','environment-menu')
        wait(lambda s:s.get('hd',{}).get('panel')=='city-f6','environment-ready')
        current=status()['hd']['panel_selection']
        for _ in range((row-current)%5): native('Down','environment-select')
        native('space','environment-open')
        if row==0:
            assert status()['hd']['interface_panel']=='settings.message_speed'
            capture('environment-'+str(row))
            native('5','environment-message-speed-set')
        elif row==1:
            assert status()['hd']['interface_panel']=='speed'
            capture('environment-'+str(row))
            native('space','environment-speed-confirm')
        else:
            # Timed notices return without a confirmation key. Space here would
            # select the toolbar tool after the notice and change the input mode.
            expected = {2:['notice.start_only'],
                        3:['settings.speaker_on','settings.speaker_off'],
                        4:['settings.sound_on','settings.sound_off']}[row]
            wait(lambda s:s.get('hd',{}).get('interface_panel') in expected,
                 'environment-complete-'+str(row))
            capture('environment-'+str(row))
        checks.append(['environment-'+str(row),'en'])
    # A matched budget panel must keep the original numeric fields in all locales.
    if not file_only:
        native('F3','budget-menu')
        current=status()['hd']['panel_selection']
        for _ in range((0-current)%3): native('Down','budget-select')
        native('space','budget-open')
        for lang in ['zh-Hans','ja','ko','en','zh-Hant']:
            language(lang)
            assert status()['hd']['budget'] and status()['hd']['localized_fields']>=25
            capture('budget-'+lang)
            checks.append(['budget',lang])
        native('Escape','budget-close')
    language('en')
    native('F2','save-menu')
    wait(lambda s:s.get('hd',{}).get('panel')=='city-f2','save-menu-ready')
    current=status()['hd']['panel_selection']
    for _ in range((0-current)%4): native('Down','save-select')
    native('space','save-dialog')
    assert status()['hd']['file_dialog']=='file-browser'
    theme_roundtrip('save-dialog')
    subprocess.run(['xdotool','type','--delay','150','locale'],check=True)
    wait(lambda s:s.get('hd',{}).get('file_text',[''])[0].strip()=='LOCALE','save-name')
    capture('save-name-en')
    native('space','save-accept')
    saved=saves/'LOCALE.SAV'
    assert saved.is_file() and saved.stat().st_size==93567
    saved_sha=hashlib.sha256(saved.read_bytes()).hexdigest()
    native('F2','load-menu')
    current=status()['hd']['panel_selection']
    for _ in range((1-current)%4): native('Down','load-select')
    native('space','load-dialog')
    assert status()['hd']['file_dialog']=='file-browser'
    subprocess.run(['xdotool','type','--delay','150','locale'],check=True)
    wait(lambda s:s.get('hd',{}).get('file_text',[''])[0].strip()=='LOCALE','load-name')
    native('space','load-accept')
    loaded=wait(lambda s:any(f.get('Op')=='read' and f.get('Name','').upper()=='LOCALE.SAV'
                            for f in s.get('file_ops',[])),'original-save-read')
    assert hashlib.sha256(saved.read_bytes()).hexdigest()==saved_sha
    assert loaded['language']=='en'
    capture('loaded-city-en')
    native('F1','quit-menu')
    native('space','quit-confirm')
    wait(lambda s:s.get('hd',{}).get('file_dialog')=='quit-confirm','quit-text-complete')
    assert status()['hd']['file_dialog']=='quit-confirm'
    assert status()['hd']['localized_fields']>0
    capture('quit-confirm-en')
    theme_roundtrip('quit-confirm')
    subprocess.run(['xdotool','type','--delay','150','Y'],check=True)
    ending=wait(lambda s:s.get('dos_blocked') is True and s.get('hd',{}).get('ending_screen')=='achievement-base',
                'ending-en',seconds=180)
    assert ending['hd']['localized_fields']==1
    capture('ending-en')
    key('space')
    wait(lambda s:s.get('dos_exited') is True,'native-exit')
    capture('native-exit')
finally:
    (out/'stop').write_text('stop\n')
    try:
        code=p.wait(timeout=10)
        assert code==0, code
    finally:
        if p.poll() is None: p.kill();p.wait()
        log.close()

(root/'verification.json').write_text(json.dumps({'issue':51,'normal_gui':True,'checkpoint':False,
    'checks':checks,'phase':phase,'f12_roundtrips':roundtrips,'acknowledged':acknowledged,
    'original_save_written':True,'save_sha256':saved_sha,
    'original_save_read':True,'save_unchanged_after_read':True,'player_filename_preserved':'LOCALE',
    'native_exit_tested':True,'long_state_sampling':False,'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),
    'catalog_sha256':hashlib.sha256(catalog.read_bytes()).hexdigest()},ensure_ascii=False,indent=2)+'\n')
print('PASS: localized interfaces, F11/F12, original save/load and DOS exit',flush=True)
