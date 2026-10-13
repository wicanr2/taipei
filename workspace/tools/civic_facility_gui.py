#!/usr/bin/env python3
"""#57: normal police/fire construction, six screenshots, save/load and DOS exit."""
from datetime import datetime
import io
import json
import subprocess
import time
from pathlib import Path
import zipfile
from zoneinfo import ZoneInfo

import city_menu_playtest as base
from chart_window_playtest import key, model
from hd_source_audit import scene, sha, cell
from infrastructure_playtest import key as native_key, actions as construction_actions
from infrastructure_catalog import sources

LANGS = ['zh-Hant', 'zh-Hans', 'ja', 'ko', 'en']
root = base.root
assert not root.exists() and root.parent.stat().st_uid == 1000
root.mkdir(mode=0o700)
out, saves = root/'gui', root/'saves'
out.mkdir()
saves.mkdir()
base.out = out
binary = Path('/workspace/runs/taipei-preview-civic-r1')
shots = []


def front_key(value):
    subprocess.run(['xdotool', 'keydown', value], check=True)
    time.sleep(.15)
    subprocess.run(['xdotool', 'keyup', value], check=True)


def language(lang):
    before = base.status()
    if before['language'] == lang:
        return
    front_key('F11')
    opened = base.wait_for(lambda s:s['language_panel'], 'language-open')
    for _ in range((LANGS.index(lang)-LANGS.index(before['language'])) % 5):
        front_key('Down')
    selected = base.wait_for(lambda s:s['language_selection']==LANGS.index(lang), 'language-select')
    for field in ['steps', 'frame_index_sha256', 'registers', 'segments', 'ip', 'ticks', 'key_reads', 'file_ops', 'palette']:
        assert selected[field] == opened[field], field
    front_key('Return')
    after = base.wait_for(lambda s:s['language']==lang and not s['language_panel'], 'language-'+lang)
    assert not after['language_warning'] and after['key_reads'] == before['key_reads']


def capture(name):
    raw = (out/'capture.zip').read_bytes()
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        s = json.loads(z.read('status.json'))
        shown = z.read('presentation.png')
        frame = z.read('frame-index.bin')
    assert sha(frame) == s['frame_index_sha256'] and not (s.get('missing') or s.get('unimplemented'))
    (out/(name+'-capture.zip')).write_bytes(raw)
    (out/(name+'.png')).write_bytes(shown)
    shots.append({'file': name+'.png', 'capture_sha256': sha(raw), 'png_sha256': sha(shown),
                  'frame_index_sha256': sha(frame), 'language': s['language'], 'hd_enabled': s['hd_enabled'],
                  'steps': s['steps'], 'ticks': s['ticks'], 'map_origin': s['map_origin']})
    return s, frame


def menu(function, selection, count):
    key(function+'-open', function)
    s = base.wait_for(lambda s:s['hd']['panel']=='city-'+function.lower(), function+'-ready')
    for _ in range((selection-s['hd']['panel_selection']) % count):
        key(function+'-down', 'Down')
    assert base.status()['hd']['panel_selection'] == selection


log = (out/'app.log').open('w')
p = subprocess.Popen([str(binary), '-original', '/orig', '-saves', str(saves), '-receipts', str(out),
                      '-mute', '-steps-per-update', '400000', '-theme', 'hd-b',
                      '-materials', '/workspace/prototypes/hd-style', '-catalog', '/workspace/app/locales/ui.tsv',
                      '-stop-file', str(out/'stop')], stdout=log, stderr=subprocess.STDOUT)
try:
    base.cold_city()
    aliases = sources(Path('/orig/RS201.ROM').read_bytes())
    choices = {s['source_sha256']:s['selection'] for s in json.loads(
        Path('/workspace/prototypes/hd-style/tool-menus-v1/manifest.json').read_text())['states'] if s['id']=='tool-05'}
    def select(wanted):
        native_key('civic-submenu','space')
        def choice():
            st,f=model()
            assert st['dos_blocked']
            return choices.get(sha(b''.join(f[y*320+212:y*320+265] for y in range(52,87))))
        current=choice()
        assert current in (0,1)
        if current != wanted:native_key('civic-choice','Down')
        assert choice()==wanted
        native_key('civic-confirm','space')
    cursor=[0,0]
    def walk(label,target):
        for axis,values in [(0,('Left','Right')),(1,('Up','Down'))]:
            while cursor[axis] != target[axis]:
                direction=1 if cursor[axis]<target[axis] else -1
                native_key(f'{label}-{axis}-{cursor[axis]}',values[direction>0])
                cursor[axis]+=direction
    native_key('civic-column','Right')
    native_key('civic-row-1','Down')
    native_key('civic-row-2','Down')
    for number,(case,top) in enumerate([('police',3),('fire',7)]):
        if number:native_key('civic-toolbar','Tab')
        select(number)
        walk(case+'-target',(22,top))
        native_key(case+'-place','space')
        walk(case+'-uncover',(16,top))
        st,f=model()
        assert scene(st,f) and st['map_origin']=={'X':12,'Y':12,'Valid':True}
        for y in range(4):
            for x in range(4):
                raw=cell(f,5+(22+x)*9,34+(top+y)*9)
                assert any(a['member']==37 and a['image']==number*4+y*24+x for a in aliases.get(raw,[])),(case,x,y,'正常施工來源不符')
    native_key('civic-toolbar-final','Tab')
    initial, frame = model()
    assert initial['hd']['civic_facilities']['painted']==32
    before = base.status()
    front_key('F12')
    base.wait_for(lambda s:not s['hd_enabled'], 'original-ready')
    s, raw = capture('city-original')
    assert raw == frame and s['key_reads'] == before['key_reads'] and s['hd']['civic_facilities']['painted']==0
    front_key('F12')
    base.wait_for(lambda s:s['hd_enabled'], 'hd-ready')
    for lang in LANGS:
        language(lang)
        s, raw = capture('city-'+lang)
        assert raw == frame and s['hd']['civic_facilities']['painted'] == initial['hd']['civic_facilities']['painted']
    menu('F2', 0, 4)
    key('save-open', 'space')
    base.wait_for(lambda s:s['hd']['file_dialog']=='file-browser', 'save-ready')
    subprocess.run(['xdotool', 'type', '--delay', '150', 'civic'], check=True)
    base.wait_for(lambda s:s['hd']['file_text'][0].strip()=='CIVIC', 'save-name')
    key('save-accept', 'space')
    saved = saves/'CIVIC.SAV'
    assert saved.is_file() and saved.stat().st_size == 93567
    save_sha = sha(saved.read_bytes())
    menu('F2', 1, 4)
    key('load-open', 'space')
    base.wait_for(lambda s:s['hd']['file_dialog']=='file-browser' and s['hd']['file_text'][0].strip()=='CIVIC', 'load-ready')
    key('load-accept', 'space')
    base.wait_for(lambda s:any(f.get('Op')=='read' and f.get('Name','').upper()=='CIVIC.SAV' for f in s['file_ops']), 'save-read')
    loaded = base.wait_for(lambda s:s['hd']['civic_facilities']['painted']>0, 'buildings-restored')
    assert sha(saved.read_bytes()) == save_sha and loaded['hd']['civic_facilities']['painted']==initial['hd']['civic_facilities']['painted']
    menu('F1', 0, 2)
    key('quit-confirm', 'space')
    base.wait_for(lambda s:s['hd']['file_dialog']=='quit-confirm', 'quit-ready')
    subprocess.run(['xdotool', 'type', '--delay', '150', 'Y'], check=True)
    base.wait_for(lambda s:s['dos_blocked'] and s['hd']['ending_screen']=='achievement-base', 'ending', seconds=180)
    front_key('space')
    base.wait_for(lambda s:s.get('dos_exited'), 'native-exit')
finally:
    (out/'stop').write_text('stop\n')
    try:
        assert p.wait(timeout=10)==0
    finally:
        if p.poll() is None:
            p.kill()
            p.wait()
        log.close()
(root/'verification.json').write_text(json.dumps({
    'issue':57, 'normal_gui':True, 'checkpoint':False, 'state_injection':False, 'long_state_sampling':False,
    'scenario':'normal new city, police/fire construction and original 0 pause', 'captured_at':datetime.now(ZoneInfo('Asia/Taipei')).isoformat(),
    'binary_sha256':sha(binary.read_bytes()), 'catalog_sha256':sha(Path('/workspace/app/locales/ui.tsv').read_bytes()),
    'screenshots':shots, 'painted_cells':initial['hd']['civic_facilities']['painted'], 'save_sha256':save_sha,
    'original_save_read':True, 'save_unchanged_after_read':True, 'native_exit_tested':True, 'cold_reload_tested':False,
    'ordinary_keys':base.ordinary_sync, 'function_keys':base.sync, 'construction_actions':construction_actions,
}, ensure_ascii=False, indent=2)+'\n')
print('PASS: normal police/fire construction, F12, five languages, original save/load and DOS exit', flush=True)
