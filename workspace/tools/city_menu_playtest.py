"""#37：六功能入口的正常冷啟動來源探索，不注入狀態。"""
import hashlib
import json
import os
import subprocess
import tempfile
import time
import zipfile
from pathlib import Path

root = Path('/workspace/runs')/os.environ['TAIPEI_CITY_MENU_RUN']
out = root
sync = []


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
            print(out.name, label, s['steps'], s['frame_index_sha256'], flush=True)
            return s
        time.sleep(.2)
    raise RuntimeError(f'功能選單等待逾時 {out.name}/{label}; {status().get("steps")}')


def capture(label):
    (out/(label+'-capture.zip')).write_bytes((out/'capture.zip').read_bytes())


def action(label, key):
    before = status()
    scan = {'Left': 0x4b, 'Right': 0x4d, 'Up': 0x48, 'Down': 0x50,
            'Escape': 1, **{f'F{i}': 0x3a+i for i in range(1, 7)}}.get(key)
    word = (scan << 8) | (27 if key == 'Escape' else 0) if scan else None
    subprocess.run(['xdotool', 'keydown', key], check=True)
    if scan:
        reads = sum(k.get('Word') == word for k in before.get('key_reads', []))
        breaks = sum(k.get('kind') == 'keyboard' and k.get('scan') == scan+128 for k in before.get('inputs', []))
        try:
            pressed = wait_for(lambda s: sum(k.get('Word') == word for k in s.get('key_reads', [])) >= reads+1, label+'-read')
        finally:
            subprocess.run(['xdotool', 'keyup', key], check=True)
        released = wait_for(lambda s: sum(k.get('kind') == 'keyboard' and k.get('scan') == scan+128 for k in s.get('inputs', [])) >= breaks+1, label+'-release')
        assert sum(k.get('Word') == word for k in released.get('key_reads', [])) == reads+1
        sync.append({'scene': out.name, 'label': label, 'word': word, 'press_step': pressed['steps'], 'release_step': released['steps']})
    else:
        time.sleep(.15)
        subprocess.run(['xdotool', 'keyup', key], check=True)
        wait_for(lambda s: s.get('steps', 0) >= before['steps']+24_000_000, label)
    capture(label)


def cold_city():
    wait_for(lambda s: s.get('steps', 0) >= 700_000_000, 'intro')
    subprocess.run(['xdotool', 'search', '--name', '模擬台北', 'windowfocus'], check=True)
    action('intro-space', 'space')
    wait_for(lambda s: s.get('steps', 0) >= 800_000_000, 'intro-wait')
    action('main', 'space')
    wait_for(lambda s: s.get('frame_index_sha256') == '5442a8135d36552561f03a46fc443978a76989979e0c25dc016027229b24dda4', 'main-ready')
    for label in ['city-choice', 'new-game', 'difficulty', 'city-map']:
        action(label, 'space')
    action('pause', '0')


def main():
    global out
    only = os.environ.get('TAIPEI_CITY_MENU_ONLY', 'all')
    keys = range(1, 7) if only == 'all' else [int(only)]
    assert all(1 <= i <= 6 for i in keys)
    results = []
    for i in keys:
        out = root/f'f{i}'
        out.mkdir(parents=True, exist_ok=True)
        assert out.stat().st_uid == os.getuid()
        assert not (out/'result.json').exists(), '保留既有研究收據，使用新的 run 名稱'
        for name in ['capture.zip', 'stop']:
            (out/name).unlink(missing_ok=True)
        saves = tempfile.mkdtemp(prefix='city-menu-saves.', dir='/workspace/runs')
        with (out/'app.log').open('w') as log:
            game = subprocess.Popen(['/workspace/runs/taipei-preview', '-original', '/orig', '-saves', saves,
                '-receipts', str(out), '-mute', '-steps-per-update', '400000', '-materials',
                '/workspace/prototypes/hd-style', '-theme', os.environ.get('TAIPEI_THEME', 'original'),
                '-stop-file', str(out/'stop')], stdout=log, stderr=subprocess.STDOUT)
            try:
                cold_city()
                action('open', f'F{i}')
                first = status()
                states = [first['frame_index_sha256']]
                # 僅以正常靜止畫面觀察循環，不把上限視為實際選項數。
                for index in range(1, 33):
                    action(f'down-{index:02d}', 'Down')
                    frame = status()['frame_index_sha256']
                    if frame in states:
                        break
                    states.append(frame)
                else:
                    raise RuntimeError('三十二次正常 Down 未觀察到重複畫面')
                for index in range(1, len(states)+1):
                    action(f'up-{index:02d}', 'Up')
                for label, key in [('left', 'Left'), ('right', 'Right'), ('escape', 'Escape')]:
                    action(label, key)
                result = {'normal_gui': True, 'checkpoint': False, 'function_key': i,
                    'distinct_down_frames': states, 'last_status': status(),
                    'scope': '正常功能入口來源探索；有界停止，不代替原版退出驗收'}
                (out/'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
                results.append({'function_key': i, 'distinct_down_frames': len(states),
                                'blocked_after_escape': status().get('dos_blocked')})
            finally:
                if game.poll() is None:
                    (out/'stop').write_text('stop\n')
                    try:
                        game.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        game.kill(); game.wait()
                assert game.returncode == 0, game.returncode
    (root/'result.json').write_text(json.dumps({'scenes': results, 'acknowledged_keys': sync}, ensure_ascii=False, indent=2)+'\n')


if __name__ == '__main__':
    main()
