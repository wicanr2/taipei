"""#29：真實冷啟動逐一選取及確認十四工具，沒有快照或狀態注入。"""
import hashlib
import json
import os
import subprocess
import time
import zipfile
from pathlib import Path

out = Path('/workspace/runs/city-chrome-gui')


def receipt():
    try:
        with zipfile.ZipFile(out/'capture.zip') as z:
            s = json.loads(z.read('status.json')); frame = z.read('frame-index.bin')
        assert hashlib.sha256(frame).hexdigest() == s['frame_index_sha256']
        return s, frame
    except (OSError, zipfile.BadZipFile, json.JSONDecodeError):
        return {}, b''


def wait_for(predicate, label):
    end = time.monotonic()+120
    while time.monotonic() < end:
        s, frame = receipt()
        if predicate(s):
            print(label, s['steps'], s['frame_index_sha256'], flush=True)
            return s
        time.sleep(.2)
    raise RuntimeError(f'工具列 GUI 等待逾時：{label}; steps={receipt()[0].get("steps")}')


def keypress(key):
    subprocess.run(['xdotool', 'keydown', key], check=True)
    time.sleep(.15)
    subprocess.run(['xdotool', 'keyup', key], check=True)


def capture(label):
    (out/(label+'-capture.zip')).write_bytes((out/'capture.zip').read_bytes())


def action(label, key):
    before = receipt()[0]['steps']
    keypress(key)
    wait_for(lambda s: s.get('steps', 0) >= before+24_000_000, label)
    capture(label)


def ring(index):
    _, frame = receipt()
    x, y = 273+23*(index % 2), 4+24*(index//2)
    return {frame[(y+yy)*320+x+xx] for yy in range(22) for xx in range(22)
            if yy in [0, 21] or xx in [0, 21]}


wait_for(lambda s: s.get('steps', 0) >= 700_000_000, 'intro')
subprocess.run(['xdotool', 'search', '--name', '模擬台北', 'windowfocus'], check=True)
keypress('space')
wait_for(lambda s: s.get('steps', 0) >= 800_000_000, 'intro-wait')
keypress('space')
wait_for(lambda s: s.get('frame_index_sha256') == '5442a8135d36552561f03a46fc443978a76989979e0c25dc016027229b24dda4', 'main')
capture('main')
for label in ['city-choice', 'new-game', 'difficulty', 'city-map']:
    action(label, 'space')
action('pause', '0')
# Tab 的焦點切換及恢復已選工具已有原版證據，見 re/004。
action('initial-map-focus', 'Tab')
action('initial-toolbar-focus', 'Tab')
order = [0, 1, 3, 5, 7, 9, 11, 13, 12, 10, 8, 6, 4, 2]
submenus = []
for i, index in enumerate(order):
    if i:
        previous = order[i-1]
        key = 'Right' if index == previous+1 else 'Left' if index == previous-1 else 'Down' if index > previous else 'Up'
        action(f'hover-{index:02d}', key)
    else:
        capture('hover-00')
    assert ring(index) == ({32} if i == 0 else {186}), ('游標外框不符', index, ring(index))
    action(f'confirm-{index:02d}', 'space')
    # 部分工具先開原版子選單；保留完整模態來源，選第一項後才驗確認外框。
    for sub in range(3):
        if not receipt()[0]['dos_blocked']:
            break
        submenus.append({'tool': index, 'receipt': f'confirm-{index:02d}' if sub == 0 else f'submenu-{index:02d}-{sub-1}'})
        action(f'submenu-{index:02d}-{sub}', 'space')
    assert not receipt()[0]['dos_blocked'], ('子選單未返回', index)
    assert ring(index) == {32}, ('確認外框不符', index, ring(index))
    action(f'return-{index:02d}', 'Tab')
    assert ring(index) == {32}
action('cancel-hover-00', 'Up')
action('cancel-hover-01', 'Right')
action('cancel-return-map', 'Tab')
assert ring(2) == {32} and ring(1) == {15}, 'Tab 未恢復已選工具'
action('cancel-return-toolbar', 'Tab')
assert ring(2) == {32}
action('file-menu', 'F2')
action('file-cancel', 'Escape')
roundtrip = False
if os.environ.get('TAIPEI_THEME') == 'hd-b':
    before = receipt()[0]
    for label, enabled in [('theme-original', False), ('theme-hd', True)]:
        action(label, 'F12')
        s = receipt()[0]
        assert s['hd_enabled'] is enabled
        assert s['frame_index_sha256'] == before['frame_index_sha256']
        assert (s.get('key_reads') or []) == (before.get('key_reads') or [])
    roundtrip = True
(out/'result.json').write_text(json.dumps({'normal_gui': True, 'checkpoint': False,
    'hover_and_confirmed_tools': order, 'tab_cancel_restores_selected': True,
    'tool_submenus': submenus,
    'f12_roundtrip': roundtrip,
    'scope': '來源與呈現探索；末尾採有界停止，非原版退出驗收',
    'final_status': receipt()[0]}, ensure_ascii=False, indent=2)+'\n')
(out/'stop').write_text('stop\n')
