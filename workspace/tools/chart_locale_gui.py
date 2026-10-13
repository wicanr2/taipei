#!/usr/bin/env python3
"""#54: normal DISA1 F4 controls, five languages, save/load and native exit."""
from datetime import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import time
import zipfile
from zoneinfo import ZoneInfo

import city_menu_playtest as base
from chart_window_playtest import key, model, return_chart, console_sync
from chart_window_source_check import crop, NATIVE, DATA
from hd_source_audit import scene

LANGS = ['zh-Hant', 'zh-Hans', 'ja', 'ko', 'en']
NAMES = ['power', 'traffic', 'population', 'crime', 'land-value', 'pollution']
root = base.root
assert not root.exists() and root.parent.stat().st_uid == os.getuid()
root.mkdir(mode=0o700)
out = root / 'gui'
out.mkdir()
saves = root / 'saves'
saves.mkdir()
base.out = out
binary = Path('/workspace/runs/taipei-preview')
shots, controls = [], []
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def front_key(name):
    subprocess.run(['xdotool', 'keydown', name], check=True)
    time.sleep(.15)
    subprocess.run(['xdotool', 'keyup', name], check=True)


def language(lang):
    before = base.status()
    if before['language'] == lang:
        return
    front_key('F11')
    opened = base.wait_for(lambda s: s.get('language_panel') is True, 'language-open')
    target = LANGS.index(lang)
    for _ in range((target - LANGS.index(before['language'])) % 5):
        front_key('Down')
    selected = base.wait_for(lambda s: s.get('language_selection') == target, 'language-select')
    for field in ['steps', 'frame_index_sha256', 'registers', 'segments', 'ip', 'ticks', 'key_reads', 'file_ops', 'palette']:
        assert opened[field] == selected[field], field
    front_key('Return')
    after = base.wait_for(lambda s: s.get('language') == lang and not s.get('language_panel'), 'language-' + lang)
    assert after['key_reads'] == before['key_reads'] and not after['language_warning']


def capture(label):
    raw = (out / 'capture.zip').read_bytes()
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        s = json.loads(z.read('status.json'))
        frame = z.read('frame-index.bin')
        png = z.read('presentation.png')
        assert sha(frame) == s['frame_index_sha256']
        assert not s['help_panel'] and not s['language_panel']
        assert not (s.get('missing') or s.get('unimplemented'))
        (out / (label + '.png')).write_bytes(png)
    (out / (label + '-capture.zip')).write_bytes(raw)
    shots.append({'file': label + '.png', 'capture_sha256': sha(raw), 'png_sha256': sha(png),
                  'frame_index_sha256': sha(frame), 'language': s['language'], 'hd_enabled': s['hd_enabled'],
                  'steps': s['steps'], 'ticks': s['ticks'], 'map_origin': s['map_origin']})
    return s, frame


def menu_target(function, target, count):
    key(function + '-open', function)
    s = base.wait_for(lambda s: s['hd']['panel'] == 'city-' + function.lower(), function + '-ready')
    for _ in range((target - s['hd']['panel_selection']) % count):
        key(function + '-down', 'Down')
    assert base.status()['hd']['panel_selection'] == target


raw = Path('/workspace/prototypes/hd-style/city-menu-sources-v1.json').read_bytes()
assert sha(raw) == 'eb98c1def205eb39e533f9646ad9336fafc7268559998e93e3a1ed1c7157f870'
menu_sources = {s['source_sha256']: s['selection'] for s in json.loads(raw)['states'] if s['id'] == 'city-f4'}

log = (out / 'app.log').open('w')
p = subprocess.Popen([str(binary), '-original', '/orig', '-saves', str(saves), '-receipts', str(out),
                      '-mute', '-steps-per-update', '400000', '-theme', 'hd-b',
                      '-materials', '/workspace/prototypes/hd-style',
                      '-catalog', '/workspace/app/locales/ui.tsv', '-stop-file', str(out / 'stop')],
                     stdout=log, stderr=subprocess.STDOUT)
try:
    base.wait_for(lambda s: s.get('steps', 0) >= 700_000_000, 'intro')
    subprocess.run(['xdotool', 'search', '--onlyvisible', '--pid', str(p.pid), 'windowfocus'], check=True)
    base.action('intro-space', 'space')
    base.wait_for(lambda s: s.get('steps', 0) >= 800_000_000, 'intro-wait')
    base.action('main', 'space')
    base.wait_for(lambda s: s['hd']['panel'] == 'main', 'main-ready')
    for label, value in [('scenario-choice', 'Right'), ('scenario-open', 'space'),
                         ('scenario-city', 'space'), ('scenario-instructions', 'space'),
                         ('scenario-start', 'space'), ('pause', '0')]:
        key(label, value)
    initial, city = model()
    assert scene(initial, city) and any(f.get('Op') == 'read' and f.get('Name', '').lower() == 'disa1.dsa'
                                       for f in initial['file_ops'])
    capture('city-paused')
    for target, name in enumerate(NAMES):
        language('zh-Hant')
        menu_target('F4', target, 6)
        chosen, pixels = model()
        menu_sha = sha(crop(pixels, 320, (141, 35, 68, 94)))
        assert menu_sources[menu_sha] == target
        key(name + '-open', 'space')
        s = base.wait_for(lambda s: s.get('dos_blocked') is True and s['hd']['chart_window'], name + '-ready')
        _, frame = model()
        data_sha = sha(crop(crop(frame, 320, NATIVE), 145, DATA))
        assert s['hd']['chart_data_sha256'] == data_sha
        for lang in (LANGS if target == 0 else ['zh-Hant']):
            language(lang)
            s, pixels = capture('chart-' + name + '-' + lang)
            assert pixels == frame and s['hd']['chart_window'] and s['hd']['localized_fields'] >= 4
        before = base.status()
        for enabled, suffix in [(False, 'original'), (True, 'hd')]:
            front_key('F12')
            after = base.wait_for(lambda s: s['hd_enabled'] is enabled, name + '-' + suffix)
            assert after['key_reads'] == before['key_reads'] and after['frame_index_sha256'] == sha(frame)
            assert after['hd']['chart_window'] is enabled
            capture('chart-' + name + '-' + suffix)
        for observation in range(2):
            start = base.status()['steps']
            base.wait_for(lambda s: s['steps'] >= start + 24_000_000, name + '-observe')
            observed, pixels = capture('chart-' + name + '-observe-' + str(observation))
            assert observed['hd']['chart_window'] and observed['dos_blocked'] and pixels == frame
        return_chart(name + '-return')
        returned, pixels = model()
        assert scene(returned, pixels) and pixels == city and returned['map_origin'] == initial['map_origin']
        controls.append({'selection': target, 'name': name, 'menu_source_sha256': menu_sha,
                         'data_sha256': data_sha, 'f12_roundtrip': True, 'restored_complete_city': True})
    assert len({c['data_sha256'] for c in controls}) == 6
    language('en')
    menu_target('F2', 0, 4)
    key('save-open', 'space')
    base.wait_for(lambda s: s['hd']['file_dialog'] == 'file-browser', 'save-ready')
    subprocess.run(['xdotool', 'type', '--delay', '150', 'charts'], check=True)
    base.wait_for(lambda s: s['hd']['file_text'][0].strip() == 'CHARTS', 'save-name')
    key('save-accept', 'space')
    saved = saves / 'CHARTS.SAV'
    assert saved.is_file() and saved.stat().st_size == 93567
    save_sha = sha(saved.read_bytes())
    menu_target('F2', 1, 4)
    key('load-open', 'space')
    base.wait_for(lambda s: s['hd']['file_dialog'] == 'file-browser', 'load-ready')
    # The native browser preselects the only existing save. Typing its name
    # again would leave pending ASCII reads behind an already-satisfied label.
    if base.status()['hd']['file_text'][0].strip() != 'CHARTS':
        subprocess.run(['xdotool', 'type', '--delay', '150', 'charts'], check=True)
    base.wait_for(lambda s: s['hd']['file_text'][0].strip() == 'CHARTS', 'load-name')
    key('load-accept', 'space')
    base.wait_for(lambda s: any(f.get('Op') == 'read' and f.get('Name', '').upper() == 'CHARTS.SAV'
                               for f in s['file_ops']), 'save-read')
    assert sha(saved.read_bytes()) == save_sha
    menu_target('F1', 0, 2)
    key('quit-confirm', 'space')
    base.wait_for(lambda s: s['hd']['file_dialog'] == 'quit-confirm', 'quit-ready')
    subprocess.run(['xdotool', 'type', '--delay', '150', 'Y'], check=True)
    base.wait_for(lambda s: s.get('dos_blocked') is True and s['hd']['ending_screen'] == 'achievement-base', 'ending', seconds=180)
    front_key('space')
    base.wait_for(lambda s: s.get('dos_exited') is True, 'native-exit')
finally:
    (out / 'stop').write_text('stop\n')
    try:
        assert p.wait(timeout=10) == 0
    finally:
        if p.poll() is None:
            p.kill()
            p.wait()
        log.close()

(root / 'verification.json').write_text(json.dumps({
    'issue': 54, 'normal_gui': True, 'checkpoint': False, 'state_injection': False,
    'long_state_sampling': False, 'scenario': 'DISA1.DSA, normal menu, original 0 pause',
    'captured_at': datetime.now(ZoneInfo('Asia/Taipei')).isoformat(),
    'binary_sha256': sha(binary.read_bytes()), 'catalog_sha256': sha(Path('/workspace/app/locales/ui.tsv').read_bytes()),
    'charts': controls, 'screenshots': shots, 'ordinary_keys': base.ordinary_sync, 'function_keys': base.sync,
    'console_keys': console_sync, 'save_sha256': save_sha, 'original_save_read': True,
    'save_unchanged_after_read': True, 'native_exit_tested': True, 'cold_reload_tested': False,
}, ensure_ascii=False, indent=2) + '\n')
print('PASS: six actual charts, five languages, F12, return, original save/load and native exit', flush=True)
