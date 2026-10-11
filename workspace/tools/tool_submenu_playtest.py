"""#31：正常冷啟動遍歷五工具子選單，不注入狀態或按鍵佇列。"""
import hashlib
import json
import os
import subprocess
import time
import zipfile
from pathlib import Path

out = Path('/workspace/runs')/os.environ['TAIPEI_SUBMENU_RUN']
hd = os.environ.get('TAIPEI_THEME') == 'hd-b'
sync, roundtrips, cancels = [], [], []


def status():
    try:
        with zipfile.ZipFile(out/'capture.zip') as z:
            s = json.loads(z.read('status.json'))
            assert hashlib.sha256(z.read('frame-index.bin')).hexdigest() == s['frame_index_sha256']
            return s
    except (OSError, zipfile.BadZipFile, json.JSONDecodeError):
        return {}


def wait_for(predicate, label):
    end = time.monotonic()+120
    while time.monotonic() < end:
        s = status()
        if predicate(s):
            print(label, s['steps'], s['frame_index_sha256'], flush=True)
            return s
        time.sleep(.2)
    raise RuntimeError(f'子選單等待逾時：{label}; steps={status().get("steps")}')


def capture(label):
    (out/(label+'-capture.zip')).write_bytes((out/'capture.zip').read_bytes())


def action(label, key):
    before = status()
    words = {'Left': (0x4b00, 0x4b), 'Right': (0x4d00, 0x4d),
             'Up': (0x4800, 0x48), 'Down': (0x5000, 0x50), 'Tab': (0x0f09, 0x0f),
             'Escape': (0x011b, 0x01)}
    subprocess.run(['xdotool', 'keydown', key], check=True)
    if key in words:
        word, scan = words[key]
        reads = sum(k.get('Word') == word for k in before.get('key_reads', []))
        breaks = sum(k.get('kind') == 'keyboard' and k.get('scan') == scan+128 for k in before.get('inputs', []))
        try:
            pressed = wait_for(lambda s: sum(k.get('Word') == word for k in s.get('key_reads', [])) >= reads+1, label+'-read')
        finally:
            subprocess.run(['xdotool', 'keyup', key], check=True)
        released = wait_for(lambda s: sum(k.get('kind') == 'keyboard' and k.get('scan') == scan+128 for k in s.get('inputs', [])) >= breaks+1, label+'-release')
        assert sum(k.get('Word') == word for k in released.get('key_reads', [])) == reads+1
        sync.append({'label': label, 'word': word, 'press_step': pressed['steps'], 'release_step': released['steps']})
    else:
        time.sleep(.15)
        subprocess.run(['xdotool', 'keyup', key], check=True)
        wait_for(lambda s: s.get('steps', 0) >= before['steps']+24_000_000, label)
    capture(label)


def theme_roundtrip(tool):
    before = status()
    for label, enabled in [('original', False), ('hd', True)]:
        action(f'tool-{tool:02d}-theme-{label}', 'F12')
        s = status()
        assert s['hd_enabled'] is enabled
        assert s['frame_index_sha256'] == before['frame_index_sha256']
        assert (s.get('key_reads') or []) == (before.get('key_reads') or [])
        assert [e for e in s['inputs'] if e['kind'] == 'keyboard'] == [e for e in before['inputs'] if e['kind'] == 'keyboard']
    roundtrips.append(tool)


wait_for(lambda s: s.get('steps', 0) >= 700_000_000, 'intro')
subprocess.run(['xdotool', 'search', '--name', '模擬台北', 'windowfocus'], check=True)
action('intro-space', 'space')
wait_for(lambda s: s.get('steps', 0) >= 800_000_000, 'intro-wait')
action('main', 'space')
wait_for(lambda s: s.get('frame_index_sha256') == '5442a8135d36552561f03a46fc443978a76989979e0c25dc016027229b24dda4', 'main-ready')
for label in ['city-choice', 'new-game', 'difficulty', 'city-map']:
    action(label, 'space')
action('pause', '0')
current = 0
tools = [10] if os.environ.get('TAIPEI_SUBMENU_ONLY') == '10' else [2, 5, 9, 10, 11]
for tool in tools:
    if current % 2 != tool % 2:
        action(f'hover-{tool:02d}-column', 'Right' if tool % 2 else 'Left')
    for row in range(current//2, tool//2):
        action(f'hover-{tool:02d}-row-{row+1}', 'Down')
    action(f'tool-{tool:02d}-open', 'space')
    assert status()['dos_blocked'], (tool, '沒有進入原版子選單')
    if hd:
        theme_roundtrip(tool)
    if tool == 10:
        # 原版上下依索引走完左欄再右欄，左右鍵不移動。
        moves = [('down-'+str(i), 'Down') for i in range(1, 11)]
        moves += [('right', 'Right'), ('up-wrap', 'Up'), ('left', 'Left')]
    else:
        moves = [('down', 'Down'), ('down-boundary', 'Down'), ('up', 'Up'),
                 ('up-boundary', 'Up'), ('left', 'Left'), ('right', 'Right')]
    for label, key in moves:
        action(f'tool-{tool:02d}-{label}', key)
        assert status()['dos_blocked'], (tool, label, '方向鍵提前離開子選單')
    before = status()
    action(f'tool-{tool:02d}-escape', 'Escape')
    after = status()
    cancels.append({'tool': tool, 'blocked_after': after['dos_blocked'],
                    'source_unchanged': before['frame_index_sha256'] == after['frame_index_sha256']})
    if after['dos_blocked']:
        action(f'tool-{tool:02d}-confirm', 'space')
    assert not status()['dos_blocked'], (tool, '確認沒有返回')
    action(f'tool-{tool:02d}-return-toolbar', 'Tab')
    current = tool
(out/'result.json').write_text(json.dumps({'normal_gui': True, 'checkpoint': False,
    'tools': tools, 'f12_tools': roundtrips, 'escape_observations': cancels,
    'acknowledged_keys': sync, 'final_status': status(),
    'scope': '正常子選單來源及呈現；有界停止，原版存退讀另驗'}, ensure_ascii=False, indent=2)+'\n')
(out/'stop').write_text('stop\n')
