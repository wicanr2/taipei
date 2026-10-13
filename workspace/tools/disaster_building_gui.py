#!/usr/bin/env python3
"""#56: normal DISA1, six screenshots, original save/load and DOS exit."""
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
from hd_source_audit import scene, sha

LANGS = ['zh-Hant', 'zh-Hans', 'ja', 'ko', 'en']
root = base.root
assert not root.exists() and root.parent.stat().st_uid == 1000
root.mkdir(mode=0o700)
out, saves = root/'gui', root/'saves'
out.mkdir()
saves.mkdir()
base.out = out
binary = Path('/workspace/runs/taipei-preview-buildings-r1')
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
    base.wait_for(lambda s:s.get('steps',0)>=700_000_000, 'intro', progress=True)
    subprocess.run(['xdotool', 'search', '--onlyvisible', '--pid', str(p.pid), 'windowfocus'], check=True)
    base.action('intro-space', 'space')
    base.wait_for(lambda s:s.get('steps',0)>=800_000_000, 'intro-wait')
    base.action('main', 'space')
    base.wait_for(lambda s:s['hd']['panel']=='main', 'main-ready')
    for label, value in [('scenario-choice','Right'), ('scenario-open','space'), ('scenario-city','space'),
                         ('instructions','space'), ('start','space'), ('pause','0')]:
        key(label, value)
    initial, frame = model()
    assert scene(initial, frame) and initial['hd']['city_buildings']['painted'] > 0
    assert any(f.get('Op')=='read' and f.get('Name','').lower()=='disa1.dsa' for f in initial['file_ops'])
    before = base.status()
    front_key('F12')
    base.wait_for(lambda s:not s['hd_enabled'], 'original-ready')
    s, raw = capture('city-original')
    assert raw == frame and s['key_reads'] == before['key_reads'] and s['hd']['city_buildings']['painted']==0
    front_key('F12')
    base.wait_for(lambda s:s['hd_enabled'], 'hd-ready')
    for lang in LANGS:
        language(lang)
        s, raw = capture('city-'+lang)
        assert raw == frame and s['hd']['city_buildings']['painted'] == initial['hd']['city_buildings']['painted']
    menu('F2', 0, 4)
    key('save-open', 'space')
    base.wait_for(lambda s:s['hd']['file_dialog']=='file-browser', 'save-ready')
    subprocess.run(['xdotool', 'type', '--delay', '150', 'bldg'], check=True)
    base.wait_for(lambda s:s['hd']['file_text'][0].strip()=='BLDG', 'save-name')
    key('save-accept', 'space')
    saved = saves/'BLDG.SAV'
    assert saved.is_file() and saved.stat().st_size == 93567
    save_sha = sha(saved.read_bytes())
    menu('F2', 1, 4)
    key('load-open', 'space')
    base.wait_for(lambda s:s['hd']['file_dialog']=='file-browser' and s['hd']['file_text'][0].strip()=='BLDG', 'load-ready')
    key('load-accept', 'space')
    base.wait_for(lambda s:any(f.get('Op')=='read' and f.get('Name','').upper()=='BLDG.SAV' for f in s['file_ops']), 'save-read')
    loaded = base.wait_for(lambda s:s['hd']['city_buildings']['painted']>0, 'buildings-restored')
    assert sha(saved.read_bytes()) == save_sha and loaded['hd']['city_buildings']['painted']==initial['hd']['city_buildings']['painted']
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
    'issue':56, 'normal_gui':True, 'checkpoint':False, 'state_injection':False, 'long_state_sampling':False,
    'scenario':'DISA1.DSA, normal menu and original 0 pause', 'captured_at':datetime.now(ZoneInfo('Asia/Taipei')).isoformat(),
    'binary_sha256':sha(binary.read_bytes()), 'catalog_sha256':sha(Path('/workspace/app/locales/ui.tsv').read_bytes()),
    'screenshots':shots, 'painted_cells':initial['hd']['city_buildings']['painted'], 'save_sha256':save_sha,
    'original_save_read':True, 'save_unchanged_after_read':True, 'native_exit_tested':True, 'cold_reload_tested':False,
    'ordinary_keys':base.ordinary_sync, 'function_keys':base.sync,
}, ensure_ascii=False, indent=2)+'\n')
print('PASS: normal DISA1 buildings, F12, five languages, original save/load and DOS exit', flush=True)
