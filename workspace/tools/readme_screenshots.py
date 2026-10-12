#!/usr/bin/env python3
"""#53: capture actual original/HD GUI for README, without state injection."""
import hashlib
from datetime import datetime
import io
import json
import os
from pathlib import Path
import subprocess
import time
import zipfile
from zoneinfo import ZoneInfo

LANGUAGES = ['zh-Hant', 'zh-Hans', 'ja', 'ko', 'en']
root = Path('/workspace/runs') / os.environ['TAIPEI_SCREENSHOTS_RUN']
assert not root.exists(), root
assert root.parent.stat().st_uid == os.getuid()
root.mkdir(mode=0o700)
saves = root / 'saves'
saves.mkdir()
out = root / 'gui'
out.mkdir()
binary = Path('/workspace/runs/taipei-preview')
catalog = Path('/workspace/app/locales/ui.tsv')
shots = []
reads = []


def sha(data):
    return hashlib.sha256(data).hexdigest()


def bundle():
    try:
        raw = (out / 'capture.zip').read_bytes()
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            s = json.loads(z.read('status.json'))
            assert sha(z.read('frame-index.bin')) == s['frame_index_sha256']
            return s, raw
    except (FileNotFoundError, zipfile.BadZipFile):
        return {}, b''


def wait(predicate, label, seconds=90):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        s, raw = bundle()
        if predicate(s):
            print(label, s.get('steps'), s.get('language'), flush=True)
            return s, raw
        time.sleep(.1)
    raise RuntimeError(f'{label}: {bundle()[0].get("hd")}')


def key(name):
    subprocess.run(['xdotool', 'keydown', name], check=True)
    time.sleep(.15)
    subprocess.run(['xdotool', 'keyup', name], check=True)


def native(name, label):
    before, _ = bundle()
    ascii_keys = {'space': (32, 0x39), 'Escape': (27, 1), '0': (48, 0x0b)}
    ordinary = name in ascii_keys
    code, scan = ascii_keys[name] if ordinary else (None, {'Down': 0x50, 'F1': 0x3b, 'F3': 0x3d}[name])
    matches = lambda k: k.get('Key') == code if ordinary else k.get('Word') == scan << 8
    count = sum(matches(k) for k in before.get('key_reads', []))
    breaks = sum(i['kind'] == 'keyboard' and i.get('scan') == scan + 128 for i in before.get('inputs', []))
    subprocess.run(['xdotool', 'keydown', name], check=True)
    try:
        if ordinary:
            time.sleep(.15)
            subprocess.run(['xdotool', 'keyup', name], check=True)
        pressed, _ = wait(lambda s: sum(matches(k) for k in s.get('key_reads', [])) >= count + 1,
                          label + '-read', seconds=180)
    finally:
        if not ordinary:
            subprocess.run(['xdotool', 'keyup', name], check=True)
    released, _ = wait(lambda s: sum(i['kind'] == 'keyboard' and i.get('scan') == scan + 128
                                    for i in s.get('inputs', [])) >= breaks + 1 and
                       (s.get('dos_blocked') is True or s.get('steps', 0) >= pressed['steps'] + 24_000_000),
                       label + '-release')
    actual = [k for k in released['key_reads'] if matches(k)]
    assert len(actual) == count + 1, (label, actual)
    reads.append({'label': label, 'key': name, 'read': actual[-1]})


def language(lang):
    before, _ = bundle()
    if before.get('language') == lang:
        return before
    key('F11')
    opened, _ = wait(lambda s: s.get('language_panel') is True, 'picker')
    index = LANGUAGES.index(lang)
    for _ in range((index - LANGUAGES.index(before['language'])) % 5):
        key('Down')
    selected, _ = wait(lambda s: s.get('language_selection') == index, 'select-' + lang)
    for field in ['steps', 'frame_index_sha256', 'registers', 'segments', 'ip', 'ticks', 'key_reads', 'file_ops', 'palette']:
        assert opened[field] == selected[field], field
    key('Return')
    after, _ = wait(lambda s: s.get('language') == lang and not s.get('language_panel') and
                    s.get('help_panel') == before['help_panel'], 'language-' + lang)
    assert not after.get('language_warning'), after.get('language_warning')
    assert after['key_reads'] == before['key_reads'], 'F11 leaked to DOS'
    return after


def capture(label, scene, lang, original=False):
    s, raw = wait(lambda s: s.get('language') == lang and not s.get('language_panel') and
                  s.get('hd_enabled') is (not original) and
                  s.get('help_panel') is (scene == 'help'), 'capture-' + label)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        shown = z.read('presentation.png')
        native_png = z.read('frame.png')
        native_rgb = subprocess.run(['convert', 'png:-', '-depth', '8', 'rgb:-'], input=native_png,
                                    check=True, stdout=subprocess.PIPE).stdout
        if original:
            expected = subprocess.run(['convert', 'png:-', '-filter', 'point', '-resize', '1280x800!',
                                       '-depth', '8', 'rgba:-'], input=native_png, check=True,
                                      stdout=subprocess.PIPE).stdout
            actual = subprocess.run(['convert', 'png:-', '-depth', '8', 'rgba:-'], input=shown,
                                    check=True, stdout=subprocess.PIPE).stdout
            assert actual == expected, 'original must be an exact nearest-neighbor 4x frame'
        else:
            assert shown != native_png
        assert not (s.get('missing') or s.get('unimplemented')), s
        (out / (label + '.png')).write_bytes(shown)
        (out / (label + '-native.png')).write_bytes(native_png)
    (out / (label + '-capture.zip')).write_bytes(raw)
    shots.append({'file': label + '.png', 'scene': scene, 'language': 'zh-Hant' if original else lang,
                  'mode': 'original' if original else 'hd-b', 'size': [1280, 800],
                  'png_sha256': sha(shown), 'capture_sha256': sha(raw),
                  'original_rgb_sha256': sha(native_rgb),
                  'frame_index_sha256': s['frame_index_sha256'], 'palette': s['palette'],
                  'steps': s['steps'], 'ticks': s['ticks'], 'bios_ticks': s['bios_ticks'],
                  'map_origin': s['map_origin'], 'help_panel': s['help_panel'],
                  'localized_fields': s['hd']['localized_fields'],
                  'budget_text': s['hd']['budget_text'] if scene == 'budget' and not original else None})
    return s


def scene_gallery(scene):
    language('zh-Hant')
    before, _ = bundle()
    key('F12')
    off, _ = wait(lambda s: s.get('hd_enabled') is False, scene + '-original')
    assert off['key_reads'] == before['key_reads'], 'F12 leaked to DOS'
    capture(scene + '-original', scene, 'zh-Hant', original=True)
    key('F12')
    wait(lambda s: s.get('hd_enabled') is True, scene + '-hd')
    for lang in LANGUAGES:
        language(lang)
        s = capture(scene + '-' + lang, scene, lang)
        assert s['hd'].get('font_labels') == 6
        if scene == 'budget':
            assert s['hd']['budget'] and s['hd']['localized_fields'] >= 25
    group = [shot for shot in shots if shot['scene'] == scene]
    assert len({shot['frame_index_sha256'] for shot in group}) == 1, (scene, 'original frame changed')
    assert len({shot['original_rgb_sha256'] for shot in group}) == 1, (scene, 'visible original colors changed')


def budget_gallery():
    # The original may return to the city without a new key while the panel is
    # idle. Open each locale through the normal menu rather than assuming the
    # dialog survives the whole screenshot session. Verify the resulting frames.
    for index, lang in enumerate(LANGUAGES):
        language(lang)
        native('F3', 'budget-menu')
        s, _ = wait(lambda s: s.get('hd', {}).get('panel') == 'city-f3', 'budget-menu-ready')
        for _ in range((0 - s['hd']['panel_selection']) % 3):
            native('Down', 'budget-select')
        native('space', 'budget-open')
        wait(lambda s: s.get('hd', {}).get('budget') is True, 'budget-ready')
        if index == 0:
            before, _ = bundle()
            key('F12')
            off, _ = wait(lambda s: s.get('hd_enabled') is False, 'budget-original')
            assert off['key_reads'] == before['key_reads'], 'F12 leaked to DOS'
            capture('budget-original', 'budget', lang, original=True)
            key('F12')
            wait(lambda s: s.get('hd_enabled') is True, 'budget-hd')
        s = capture('budget-' + lang, 'budget', lang)
        assert s['hd']['budget'] and s['hd']['localized_fields'] >= 25
        native('Escape', 'budget-close')
    group = [shot for shot in shots if shot['scene'] == 'budget']
    assert len({shot['frame_index_sha256'] for shot in group}) == 1, 'budget original frame changed'
    assert len({shot['original_rgb_sha256'] for shot in group}) == 1, 'budget original visible colors changed'


log = (out / 'app.log').open('w')
p = subprocess.Popen([str(binary), '-original', '/orig', '-saves', str(saves), '-receipts', str(out),
                      '-mute', '-steps-per-update', '400000', '-theme', 'hd-b',
                      '-materials', '/workspace/prototypes/hd-style', '-catalog', str(catalog),
                      '-stop-file', str(out / 'stop')], stdout=log, stderr=subprocess.STDOUT)
try:
    wait(lambda s: s.get('steps', 0) >= 700_000_000, 'intro', seconds=180)
    subprocess.run(['xdotool', 'search', '--onlyvisible', '--pid', str(p.pid), 'windowfocus'], check=True)
    key('space')
    wait(lambda s: s.get('steps', 0) >= 800_000_000, 'intro-wait')
    key('space')
    wait(lambda s: s.get('hd', {}).get('panel') == 'main', 'main')
    for scene in ['city', 'new-game', 'difficulty', 'city-map']:
        native('space', scene)
    wait(lambda s: s.get('hd', {}).get('font_labels') == 6, 'city-ready')
    native('0', 'pause')
    scene_gallery('city')
    for lang in LANGUAGES:
        language(lang)
        subprocess.run(['xdotool', 'keydown', 'Shift_L'], check=True)
        try:
            key('F1')
        finally:
            subprocess.run(['xdotool', 'keyup', 'Shift_L'], check=True)
        wait(lambda s: s.get('help_panel') is True, 'help-' + lang)
        capture('help-' + lang, 'help', lang)
        key('Escape')
        wait(lambda s: s.get('help_panel') is False, 'help-close')
    budget_gallery()
    native('F1', 'quit-menu')
    native('space', 'quit-confirm')
    wait(lambda s: s.get('hd', {}).get('file_dialog') == 'quit-confirm', 'quit-text')
    subprocess.run(['xdotool', 'type', '--delay', '150', 'Y'], check=True)
    wait(lambda s: s.get('dos_blocked') is True and s.get('hd', {}).get('ending_screen') == 'achievement-base',
         'ending', seconds=180)
    key('space')
    wait(lambda s: s.get('dos_exited') is True, 'native-exit')
finally:
    (out / 'stop').write_text('stop\n')
    try:
        assert p.wait(timeout=10) == 0
    finally:
        if p.poll() is None:
            p.kill()
            p.wait()
        log.close()

assert len(shots) == 17
for scene in ['city', 'budget']:
    group = [shot for shot in shots if shot['scene'] == scene]
    assert len({shot['frame_index_sha256'] for shot in group}) == 1
budget_values = [shot['budget_text'] for shot in shots if shot['scene'] == 'budget' and shot['mode'] == 'hd-b']
assert all(value == budget_values[0] for value in budget_values)
(root / 'verification.json').write_text(json.dumps({
    'issue': 53, 'normal_gui': True, 'checkpoint': False, 'state_injection': False,
    'captured_at': datetime.now(ZoneInfo('Asia/Taipei')).isoformat(),
    'long_state_sampling': False, 'native_exit_tested': True,
    'binary_sha256': sha(binary.read_bytes()), 'catalog_sha256': sha(catalog.read_bytes()),
    'scenario': 'normal new game, first city, default difficulty, original 0 pause',
    'rng_seed': 'not overridden; comparisons use one running original instance',
    'same_original_frame_and_visible_rgb': ['city', 'budget'],
    'acknowledged': reads, 'screenshots': shots,
}, ensure_ascii=False, indent=2) + '\n')
print('PASS: 17 actual GUI screenshots; original/HD use the same original frame', flush=True)
