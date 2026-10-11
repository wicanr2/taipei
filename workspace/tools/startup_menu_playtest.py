"""#31：正常 GUI 冷啟動的選單來源探索；不載入快照或注入狀態。"""
import hashlib
import json
import os
import subprocess
import time
import zipfile
from pathlib import Path

out = Path('/workspace/runs/startup-menus')
hd = os.environ.get('TAIPEI_THEME') == 'hd-b'
roundtrips = []


def status():
    try:
        with zipfile.ZipFile(out/'capture.zip') as z:
            s = json.loads(z.read('status.json'))
            assert hashlib.sha256(z.read('frame-index.bin')).hexdigest() == s['frame_index_sha256']
            return s
    except (OSError, zipfile.BadZipFile):
        return {}


def wait_for(predicate, label, seconds=120):
    end = time.monotonic()+seconds
    while time.monotonic() < end:
        s = status()
        if predicate(s):
            print(label, s.get('steps'), s.get('frame_index_sha256'), flush=True)
            return s
        time.sleep(.2)
    raise RuntimeError(f'選單 GUI 等待逾時：{label}; steps={status().get("steps")}')


def keypress(key):
    subprocess.run(['xdotool', 'keydown', key], check=True)
    time.sleep(.15)
    subprocess.run(['xdotool', 'keyup', key], check=True)


def capture(label):
    (out/(label+'-capture.zip')).write_bytes((out/'capture.zip').read_bytes())


def action(label, key):
    before = status()['steps']
    keypress(key)
    wait_for(lambda s: s.get('steps', 0) >= before+24_000_000, label)
    capture(label)
    if hd and label in ['city-0', 'difficulty-0']:
        theme_roundtrip(label.split('-')[0])


def theme_roundtrip(scene):
    before = status()
    assert before['hd']['panel'] == scene and before['hd']['panel_selection'] == 0
    keypress('F12')
    wait_for(lambda s: not s.get('hd_enabled', True), scene+'-original')
    capture(scene+'-theme-original')
    off = status()
    assert off['frame_index_sha256'] == before['frame_index_sha256']
    assert not off['hd']['panel']
    keypress('F12')
    after = wait_for(lambda s: s.get('hd_enabled') and s.get('hd', {}).get('panel') == scene, scene+'-hd')
    capture(scene+'-theme-hd')
    assert after['frame_index_sha256'] == before['frame_index_sha256']
    assert (after.get('key_reads') or []) == (before.get('key_reads') or [])
    assert [e for e in after['inputs'] if e['kind'] == 'keyboard'] == [e for e in before['inputs'] if e['kind'] == 'keyboard']
    roundtrips.append(scene)


wait_for(lambda s: s.get('steps', 0) >= 700_000_000, 'intro')
subprocess.run(['xdotool', 'search', '--name', '模擬台北', 'windowfocus'], check=True)
keypress('space')
wait_for(lambda s: s.get('steps', 0) >= 800_000_000, 'intro-wait')
keypress('space')
wait_for(lambda s: s.get('frame_index_sha256') == '5442a8135d36552561f03a46fc443978a76989979e0c25dc016027229b24dda4', 'main')
capture('main-0')
if hd:
    theme_roundtrip('main')
for label, key in [('main-1', 'Right'), ('main-2', 'Right'), ('main-back-1', 'Left'),
                   ('main-back-0', 'Left'), ('city-0', 'space'), ('city-right-0', 'Right'),
                   ('city-right-1', 'Down'), ('city-right-2', 'Down'),
                   ('city-right-back-1', 'Up'), ('city-right-back-0', 'Up'),
                   ('city-left-0', 'Left'), ('city-left-1', 'Down'),
                   ('city-left-2', 'Down'), ('city-left-3', 'Down'),
                   ('city-left-4', 'Down'), ('city-left-5', 'Down'), ('city-left-6', 'Down'),
                   ('city-left-back-5', 'Up'), ('city-left-back-4', 'Up'), ('city-left-back-3', 'Up'),
                   ('city-left-back-2', 'Up'), ('city-left-back-1', 'Up'), ('city-left-back-0', 'Up'),
                   ('new-game', 'space'), ('difficulty-0', 'space'),
                   ('difficulty-1', 'Down'), ('difficulty-2', 'Down'),
                   ('difficulty-back-1', 'Up'), ('difficulty-back-0', 'Up'),
                   ('difficulty-cancel', 'Escape')]:
    action(label, key)
assert status()['frame_index_sha256'] == json.loads(zipfile.ZipFile(out/'difficulty-back-0-capture.zip').read('status.json'))['frame_index_sha256'], '原版 Escape 語意改變'
if hd:
    action('city-map', 'space')
    wait_for(lambda s: s.get('hd', {}).get('Painted', 0) > 0, 'city-map-ready')
    capture('city-map')
    action('city-scroll-right', 'Right')
    action('city-scroll-down', 'Down')
(out/'result.json').write_text(json.dumps({'normal_gui': True, 'checkpoint': False,
    'scope': '正常選單來源與呈現驗證；結束方式為有界工具停止，非原版退出驗收',
    'f12_scenes': roundtrips, 'difficulty_escape_unchanged': True,
    'final_status': status()}, ensure_ascii=False, indent=2)+'\n')
(out/'stop').write_text('stop\n')
