"""#37：一次真實冷啟動遍歷六選單、二十九選取及六次 F12 往返。"""
import json
import os
import subprocess
import tempfile

import city_menu_playtest as base


def main():
    root = base.root
    assert os.environ['TAIPEI_THEME'] == 'hd-b'
    assert not (root/'result.json').exists(), '保留既有收據'
    assert root.stat().st_uid == os.getuid()
    for name in ['capture.zip', 'stop']:
        (root/name).unlink(missing_ok=True)
    capture_dir = root

    def capture(label):
        (capture_dir/(label+'-capture.zip')).write_bytes((root/'capture.zip').read_bytes())

    base.capture = capture
    saves = tempfile.mkdtemp(prefix='city-menu-hd-saves.', dir='/workspace/runs')
    results = []
    with (root/'app.log').open('w') as log:
        game = subprocess.Popen(['/workspace/runs/taipei-preview', '-original', '/orig', '-saves', saves,
            '-receipts', str(root), '-mute', '-steps-per-update', '400000', '-materials',
            '/workspace/prototypes/hd-style', '-theme', 'hd-b', '-stop-file', str(root/'stop')],
            stdout=log, stderr=subprocess.STDOUT)
        try:
            base.cold_city()
            for key, count in enumerate([1, 4, 3, 6, 10, 5], 1):
                capture_dir = root/f'f{key}'
                capture_dir.mkdir(exist_ok=True)
                start_sync = len(base.sync)
                capture('pause')
                base.action('open', f'F{key}')
                first = base.status()
                assert first['hd']['panel'] == f'city-f{key}' and first['hd']['panel_selection'] == 0
                for label, enabled in [('theme-original', False), ('theme-hd', True)]:
                    base.action(label, 'F12')
                    current = base.status()
                    assert current['hd_enabled'] == enabled
                    assert current['frame_index_sha256'] == first['frame_index_sha256']
                    assert current['key_reads'] == first['key_reads']
                    keyboard = lambda s: [i for i in s['inputs'] if i['kind'] == 'keyboard']
                    assert keyboard(current) == keyboard(first), 'F12 送入原版鍵盤'
                    assert current['hd'].get('panel', '') == (f'city-f{key}' if enabled else '')
                states = {first['frame_index_sha256']}
                for i in range(1, count+1):
                    base.action(f'down-{i:02d}', 'Down')
                    states.add(base.status()['frame_index_sha256'])
                assert len(states) == count
                for i in range(1, count+1):
                    base.action(f'up-{i:02d}', 'Up')
                for label, control in [('left', 'Left'), ('right', 'Right'), ('escape', 'Escape')]:
                    base.action(label, control)
                for record in base.sync[start_sync:]:
                    record['scene'] = f'f{key}'
                result = {'normal_gui': True, 'checkpoint': False, 'function_key': key,
                    'distinct_down_frames': sorted(states), 'f12_roundtrip': True,
                    'last_status': base.status(),
                    'scope': '六選單正常 HD 輸入；有界停止，原版退出另由存退讀驗證'}
                (capture_dir/'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
                results.append({'function_key': key, 'states': count, 'f12_roundtrip': True})
        finally:
            if game.poll() is None:
                (root/'stop').write_text('stop\n')
                try:
                    game.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    game.kill(); game.wait()
            assert game.returncode == 0, game.returncode
    (root/'result.json').write_text(json.dumps({'normal_gui': True, 'cold_start': True,
        'checkpoint': False, 'scenes': results, 'acknowledged_keys': base.sync,
        'scope': '一次正常冷啟動，六選單二十九狀態；此探針有界停止'}, ensure_ascii=False, indent=2)+'\n')


if __name__ == '__main__':
    main()
