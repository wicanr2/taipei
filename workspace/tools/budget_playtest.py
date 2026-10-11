"""#39：正常冷啟動、F3 預算入口及數值操作；禁止狀態注入。"""
import hashlib
import json
import os
import subprocess
import tempfile
import zipfile
from pathlib import Path

os.environ['TAIPEI_CITY_MENU_RUN'] = os.environ['TAIPEI_BUDGET_RUN']
import city_menu_playtest as base
from budget_catalog import crop, decode_budget, references


def main():
    root = base.root
    assert root.stat().st_uid == os.getuid() and not any(root.glob('*-capture.zip'))
    refs = references(Path('/orig/RS201.ROM').read_bytes())
    manifest = Path('/workspace/prototypes/hd-style/city-menus-v1/manifest.json').read_bytes()
    assert hashlib.sha256(manifest).hexdigest() == '699c3ed0baed752327667f3d50cc9b0ee45b0124407338eb4f41be94d6239fc5'
    choices = {s['source_sha256']: s['selection'] for s in json.loads(manifest)['states'] if s['id'] == 'city-f3'}
    records = []

    def state():
        with zipfile.ZipFile(root/'capture.zip') as z:
            s, frame = json.loads(z.read('status.json')), z.read('frame-index.bin')
        return s, frame, decode_budget(frame, refs)

    def key(label, value):
        before = base.status()
        base.action(label, value)
        s, _, decoded = state()
        assert len(s['key_reads']) == len(before['key_reads'])+1, (label, '讀鍵數')
        records.append({'label': label, 'key': value, 'before_steps': before['steps'], 'after_steps': s['steps'],
                        'original_read': s['key_reads'][-1], 'dos_blocked': s['dos_blocked'], 'budget': decoded})
        return decoded

    def open_budget(label):
        key(label+'-menu', 'F3')
        for i in range(3):
            selection = choices.get(hashlib.sha256(crop(state()[1], (97, 35, 68, 49))).hexdigest())
            assert selection is not None, '完整 F3 來源未辨識'
            if selection == 0:
                break
            key(f'{label}-choice-{i}', 'Down')
        else:
            raise AssertionError('未抵達預算選項')
        decoded = key(label+'-open', 'space')
        if decoded is None:
            # 保留暫停時選取後的正常原件，再觀察恢復計時的結果。
            key(label+'-resume', '1')
            base.wait_for(lambda s: state()[2] is not None, label+'-wait-budget')
            base.capture(label+'-visible')
            decoded = state()[2]
        assert decoded is not None, (label, '完整預算來源尚未重建')
        return decoded

    saves = tempfile.mkdtemp(prefix='budget-saves.', dir='/workspace/runs')
    with (root/'app.log').open('w') as log:
        game = subprocess.Popen(['/workspace/runs/taipei-preview', '-original', '/orig', '-saves', saves,
            '-receipts', str(root), '-mute', '-steps-per-update', '400000', '-materials',
            '/workspace/prototypes/hd-style', '-theme', 'original', '-stop-file', str(root/'stop')],
            stdout=log, stderr=subprocess.STDOUT)
        try:
            base.cold_city()
            pause = state()[1]
            initial = open_budget('first')
            for i in range(6):
                assert key(f'down-{i+1}', 'Down') is not None
            for i in range(6):
                assert key(f'up-{i+1}', 'Up') is not None
            for row in range(5):
                before = state()[2]
                assert before is not None
                assert key(f'row-{row}-right', 'Right') is not None
                assert key(f'row-{row}-left', 'Left') is not None
                assert key(f'row-{row}-down', 'Down') is not None
            # 上下邊界及每列數值由收據記錄，不預設取消會還原數值。
            escaped = key('escape', 'Escape')
            assert escaped is None
            after_escape = state()[1]
            reopened = open_budget('reopen')
            accepted = key('space', 'space')
            after_space = state()[1]
            idle = None
            if accepted is not None:
                before_idle = base.status()
                base.wait_for(lambda s: state()[2] is None, 'idle-return')
                base.capture('idle-return')
                after_idle = base.status()
                assert len(after_idle['key_reads']) == len(before_idle['key_reads']), '閒置等待多出原版輸入'
                idle = {'before_steps': before_idle['steps'], 'after_steps': after_idle['steps'],
                        'before_bios_ticks': before_idle.get('bios_ticks'),
                        'after_bios_ticks': after_idle.get('bios_ticks'),
                        'before_pit_ticks': before_idle['ticks'], 'after_pit_ticks': after_idle['ticks']}
            result = {'normal_gui': True, 'checkpoint': False, 'saves': saves, 'initial': initial,
                'reopened': reopened, 'space_kept_window': accepted is not None,
                'pause_frame_sha256': hashlib.sha256(pause).hexdigest(),
                'after_escape_frame_sha256': hashlib.sha256(after_escape).hexdigest(),
                'after_space_frame_sha256': hashlib.sha256(after_space).hexdigest(),
                'records': records, 'acknowledged_keys': base.sync, 'idle_return': idle,
                'scope': '預算來源探索；有界停止，不代替原版正常退出'}
            (root/'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
        finally:
            if game.poll() is None:
                (root/'stop').write_text('stop\n')
                try:
                    game.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    game.kill(); game.wait()
            assert game.returncode == 0, game.returncode


if __name__ == '__main__':
    main()
