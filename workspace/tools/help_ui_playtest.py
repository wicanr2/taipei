#!/usr/bin/env python3
"""#50：READY 031 的正常視窗短流程，不注入快照或恢復長時間抽樣。"""
import hashlib
import io
import json
import os
import subprocess
import time
import zipfile
from pathlib import Path

root = Path('/workspace/runs') / os.environ['TAIPEI_HELP_RUN']
root.mkdir(mode=0o700)
saves = root / 'saves'
saves.mkdir()
out = root / 'gui'
out.mkdir()
binary = Path('/workspace/runs/taipei-preview-help-r1')
catalog = Path('/workspace/app/locales/ui.tsv')
results = []


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
    s = status()
    raise RuntimeError(f'{label}: steps={s.get("steps")}, help={s.get("help_panel")}, '
                       f'language_panel={s.get("language_panel")}, hd={s.get("hd")}, '
                       f'log={(out / "app.log").read_text()[-2000:]}')


def down(name):
    subprocess.run(['xdotool', 'keydown', name], check=True)
    time.sleep(.2)


def up(name):
    subprocess.run(['xdotool', 'keyup', name], check=True)


def key(name):
    down(name)
    up(name)


def capture(label):
    raw = (out / 'capture.zip').read_bytes()
    (out / (label + '.zip')).write_bytes(raw)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        (out / (label + '.png')).write_bytes(z.read('presentation.png'))
    return raw


def modal_unchanged(before, after):
    for field in ['steps', 'registers', 'segments', 'ip', 'ticks', 'bios_ticks',
                  'bios_modifiers', 'frame_index_sha256', 'key_reads', 'file_ops', 'palette']:
        assert before[field] == after[field], field
    for kind in ['keyboard', 'text', 'mouse-move', 'mouse-button']:
        assert [i for i in before['inputs'] if i['kind'] == kind] == [
            i for i in after['inputs'] if i['kind'] == kind], kind


def help_reference(lang):
    with zipfile.ZipFile(out / 'capture.zip') as z:
        got = z.read('presentation.png')
        native = z.read('frame.png')
    ref = (Path('/workspace/prototypes/hd-style/locale-help-draft-r1') /
           f'help-shift-f1-{lang}.png').read_bytes()
    args = ['convert', 'png:-', '-crop', '1200x720+40+40', '+repage', '-depth', '8', 'rgba:-']
    actual = subprocess.run(args, input=got, stdout=subprocess.PIPE, check=True).stdout
    expected = subprocess.run(args, input=ref, stdout=subprocess.PIPE, check=True).stdout
    assert len(actual) == 1200 * 720 * 4 and actual == expected, lang
    if not status()['hd_enabled']:
        # Raw mode provides an independent base for exact outside-panel checks.
        base = subprocess.run(['convert', 'png:-', '-filter', 'point', '-resize', '1280x800!',
                               '-depth', '8', 'rgba:-'], input=native,
                              stdout=subprocess.PIPE, check=True).stdout
        whole = subprocess.run(['convert', 'png:-', '-depth', '8', 'rgba:-'], input=got,
                               stdout=subprocess.PIPE, check=True).stdout
        for y in range(800):
            for x0, x1 in ([(0, 1280)] if y < 40 or y >= 760 else [(0, 40), (1240, 1280)]):
                a, b = (y * 1280 + x0) * 4, (y * 1280 + x1) * 4
                assert whole[a:b] == base[a:b], ('outside-panel', y, x0)


log = (out / 'app.log').open('w')
p = subprocess.Popen([str(binary), '-original', '/orig', '-saves', str(saves), '-receipts', str(out),
                      '-mute', '-steps-per-update', '400000', '-theme', 'hd-b',
                      '-materials', '/workspace/prototypes/hd-style', '-catalog', str(catalog),
                      '-stop-file', str(out / 'stop')], stdout=log, stderr=subprocess.STDOUT)
try:
    wait(lambda s: s.get('steps', 0) >= 700_000_000, 'intro')
    subprocess.run(['xdotool', 'search', '--name', '模擬台北', 'windowfocus'], check=True)
    key('space')
    wait(lambda s: s.get('steps', 0) >= 800_000_000, 'intro-wait')
    key('space')
    wait(lambda s: s.get('frame_index_sha256') ==
         '5442a8135d36552561f03a46fc443978a76989979e0c25dc016027229b24dda4', 'main-menu')
    for panel in ['city', 'new-game', 'difficulty', 'map']:
        before = status()['steps']
        key('space')
        wait(lambda s: s.get('steps', 0) >= before + 24_000_000, panel)
    wait(lambda s: s.get('hd', {}).get('font_labels') == 6, 'city-labels')
    key('0')
    wait(lambda s: any(k.get('Key') == 48 for k in s.get('key_reads', [])), 'native-pause')

    # Forward Shift first, then hold the Help chord. Its queued release must balance it.
    down('Shift_L')
    shifted = wait(lambda s: s.get('bios_modifiers', 0) & 2, 'left-shift-forwarded')
    down('F1')
    opened = wait(lambda s: s.get('help_panel') is True, 'help-open-held-left')
    assert any(i['kind'] == 'keyboard' and i.get('scan') == 0xaa for i in opened['inputs'])
    assert not any(i['kind'] == 'keyboard' and i.get('scan') in [0x3b, 0xbb] for i in opened['inputs'])
    help_reference('zh-Hant')
    capture('help-zh-Hant')
    key('Escape')
    fenced = wait(lambda s: s.get('help_panel') is False and s.get('frontend_input_fence') is True,
                  'close-while-chord-held')
    modal_unchanged(opened, fenced)
    held = wait(lambda s: s.get('frames', 0) >= fenced['frames'] + 60, 'held-close-fence')
    modal_unchanged(fenced, held)
    up('F1')
    up('Shift_L')
    wait(lambda s: s.get('frontend_input_fence') is False and s.get('steps', 0) > held['steps']
         and s.get('bios_modifiers', 0) & 3 == 0, 'resume-with-shift-released')

    down('Shift_R')
    wait(lambda s: s.get('bios_modifiers', 0) & 1, 'right-shift-forwarded')
    key('F1')
    up('Shift_R')
    opened = wait(lambda s: s.get('help_panel') is True, 'help-open-right')
    assert any(i['kind'] == 'keyboard' and i.get('scan') == 0xb6 for i in opened['inputs'])
    for name in ['Tab', 'Up', 'Return', 'space', 'F1']:
        key(name)
    subprocess.run(['xdotool', 'type', '--delay', '60', 'abc'], check=True)
    window = subprocess.check_output(['xdotool', 'getwindowfocus'], text=True).strip()
    subprocess.run(['xdotool', 'mousemove', '--window', window, '20', '20', 'click', '1'], check=True)
    blocked = wait(lambda s: s.get('frames', 0) >= opened['frames'] + 180, 'modal-input-blocked')
    modal_unchanged(opened, blocked)
    for lang in ['zh-Hans', 'ja', 'ko', 'en', 'zh-Hant']:
        key('F11')
        picker = wait(lambda s: s.get('language_panel') is True, 'picker-over-help')
        assert picker['help_panel'] is True
        modal_unchanged(opened, picker)
        key('Down')
        index = ['zh-Hant', 'zh-Hans', 'ja', 'ko', 'en'].index(lang)
        wait(lambda s: s.get('language_selection') == index, 'pick-' + lang)
        key('Return')
        translated = wait(lambda s: s.get('language') == lang and s.get('language_panel') is False
                          and s.get('help_panel') is True, 'return-help-' + lang)
        modal_unchanged(opened, translated)
        assert json.loads((saves / 'frontend-settings.json').read_text()) == {'schema': 1, 'language': lang}
        help_reference(lang)
        capture('help-' + lang)
        results.append({'language': lang, 'fixed_panel_pixels': True, 'return_from_f11': True,
                        'settings_saved': True, 'no_dos_input_or_steps': True})
    key('F11')
    wait(lambda s: s.get('language_panel') is True, 'cancel-picker-open')
    key('Down')
    wait(lambda s: s.get('language_selection') == 1, 'cancel-picker-select')
    key('Escape')
    cancelled = wait(lambda s: s.get('language_panel') is False, 'cancel-picker-return-help')
    assert cancelled['help_panel'] is True and cancelled['language'] == 'zh-Hant'
    modal_unchanged(opened, cancelled)
    key('F12')
    original = wait(lambda s: s.get('hd_enabled') is False, 'help-over-original')
    modal_unchanged(opened, original)
    help_reference('zh-Hant')
    capture('help-original-mode')
    key('F12')
    restored = wait(lambda s: s.get('hd_enabled') is True, 'help-back-hd')
    modal_unchanged(opened, restored)

    down('Shift_R')
    key('F1')
    closed = wait(lambda s: s.get('help_panel') is False, 'same-chord-close')
    modal_unchanged(opened, closed)
    up('Shift_R')
    wait(lambda s: s.get('frontend_input_fence') is False and s.get('bios_modifiers', 0) & 3 == 0,
         'same-chord-release')
    key('F1')
    native_f1 = wait(lambda s: s.get('hd', {}).get('panel') == 'city-f1', 'native-f1-preserved')
    capture('native-f1')
    assert any(i['kind'] == 'keyboard' and i.get('scan') == 0x3b for i in native_f1['inputs'])
    assert any(i['kind'] == 'keyboard' and i.get('scan') == 0xbb for i in native_f1['inputs'])
    key('Escape')
    wait(lambda s: s.get('hd', {}).get('font_labels') == 6, 'native-f1-return')
    key('Tab')
    key('Right')
    # These are now genuine native keys, after all frontend fences have cleared.
    wait(lambda s: all(any(k.get('Word') == word and k.get('Step', 0) > native_f1['steps']
                          for k in s.get('key_reads', [])) for word in [0x0f09, 0x4d00]),
         'native-controls-restored')
    capture('returned-city')
finally:
    subprocess.run(['xdotool', 'keyup', 'Shift_L', 'Shift_R', 'F1', 'Escape'], check=False)
    (out / 'stop').write_text('stop\n')
    try:
        code = p.wait(timeout=10)
        assert code == 0, ('frontend-exit', code)
    finally:
        if p.poll() is None:
            p.kill()
            p.wait()
        log.close()

report = {'issue': 50, 'cold_starts': 1, 'checkpoint': False, 'normal_gui': True,
          'languages': results, 'both_shift_keys': True, 'held_close_fence': True,
          'keyboard_text_mouse_blocked': True, 'f11_cancel_returns_help': True,
          'f12_roundtrip': True, 'original_mode_outside_panel_unchanged': True,
          'same_chord_close': True, 'escape_close': True, 'native_f1_preserved': True,
          'native_controls_restored': True, 'original_save_written': False,
          'native_exit_tested': False, 'long_state_sampling': False,
          'binary_sha256': hashlib.sha256(binary.read_bytes()).hexdigest(),
          'catalog_sha256': hashlib.sha256(catalog.read_bytes()).hexdigest()}
(root / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print('PASS: Shift+F1 Help, five locales, F11, F12, modal isolation, held release, native F1', flush=True)
