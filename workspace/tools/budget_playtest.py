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
    mode = os.environ.get('TAIPEI_BUDGET_MODE', 'full')
    assert mode in ('full', 'persistence', 'scenario')

    def state():
        with zipfile.ZipFile(root/'capture.zip') as z:
            s, frame = json.loads(z.read('status.json')), z.read('frame-index.bin')
        return s, frame, decode_budget(frame, refs)

    def key(label, value):
        before = base.status()
        base.action(label, value, acknowledge=True)
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
            if mode == 'scenario':
                # 只探索正常災難城市入口，不把未知畫面假定為某個選單。
                base.wait_for(lambda s: s.get('steps', 0) >= 700_000_000, 'intro', progress=True)
                subprocess.run(['xdotool', 'search', '--name', '模擬台北', 'windowfocus'], check=True)
                base.action('intro-space', 'space')
                base.wait_for(lambda s: s.get('steps', 0) >= 800_000_000, 'intro-wait')
                base.action('main', 'space')
                base.wait_for(lambda s: s.get('frame_index_sha256') == '5442a8135d36552561f03a46fc443978a76989979e0c25dc016027229b24dda4', 'main-ready')
                key('scenario-choice', 'Right')
                key('scenario-open', 'space')
                # 此順序已由 scenario-extra 的逐幀原件查證：台北、說明、難度、城市。
                # 本批只有普通按鍵改為明示讀取確認；不注入狀態或改動資料。
                for index, value in enumerate(['space','space','space','0','F3','space']):
                    key(f'scenario-step-{index:02d}', value)
                model = state()[2]
                assert model is not None, '災難城市預算完整來源未重建'
                key('scenario-escape', 'Escape')
                (root/'result.json').write_text(json.dumps({'normal_gui': True, 'checkpoint': False,
                    'mode': mode, 'records': records, 'final_budget': model,
                    'ordinary_acknowledgments': base.ordinary_sync,
                    'arrow_acknowledgments': base.sync,
                    'scope': '正常災難入口逐幀研究；有界停止，非原版退出或 HD 完成'}, ensure_ascii=False, indent=2)+'\n')
                return
            base.cold_city()
            pause = state()[1]
            initial = open_budget('first')
            if mode == 'persistence':
                key('tax-decrease', 'Right')
                key('select-safety', 'Down')
                adjusted = key('safety-decrease', 'Right')
                key('adjusted-escape', 'Escape')
                reopened = open_budget('changed-reopen')
                enter = key('enter', 'Return')
                if enter is not None:
                    key('enter-return', 'Escape')
                key('save-menu', 'F2')
                file_menu = json.loads(manifest)['states']
                file_selections = {s['source_sha256']: s['selection'] for s in file_menu if s['id'] == 'city-f2'}
                for i in range(4):
                    current = file_selections.get(hashlib.sha256(crop(state()[1], (53, 35, 68, 64))).hexdigest())
                    assert current is not None
                    if current == 0: break
                    key(f'save-choice-{i}', 'Down')
                else: raise AssertionError('沒有到達存檔選項')
                key('save-open', 'space')
                before = base.status()
                subprocess.run(['xdotool', 'type', '--clearmodifiers', '--delay', '150', '--', 'BUDGET39'], check=True)
                base.wait_for(lambda s: len(s.get('key_reads', [])) == len(before['key_reads'])+8, 'save-name-read')
                base.capture('save-name')
                key('save-confirm', 'space')
                saved = Path(saves)/'BUDGET39.SAV'
                saved_data = saved.read_bytes()
                assert len(saved_data) == 93567
                open_budget('after-save')
                modified_after_save = key('tax-second-decrease', 'Right')
                key('load-return', 'Escape')
                key('load-menu', 'F2')
                for i in range(4):
                    current = file_selections.get(hashlib.sha256(crop(state()[1], (53, 35, 68, 64))).hexdigest())
                    assert current is not None
                    if current == 1: break
                    key(f'load-choice-{i}', 'Down')
                else: raise AssertionError('沒有到達讀檔選項')
                key('load-open', 'space')
                key('load-confirm', 'space')
                assert any(f.get('Op') == 'read' and f.get('Name', '').upper() == 'BUDGET39.SAV' for f in base.status()['file_ops'])
                loaded = open_budget('after-load')
                key('loaded-return', 'Escape')
                assert saved.read_bytes() == saved_data
                (root/'result.json').write_text(json.dumps({'normal_gui': True, 'checkpoint': False,
                    'mode': mode, 'initial': initial, 'adjusted': adjusted, 'reopened': reopened,
                    'enter_kept_window': enter is not None, 'modified_after_save': modified_after_save,
                    'loaded': loaded, 'saves': saves, 'save_sha256': hashlib.sha256(saved_data).hexdigest(),
                    'records': records, 'acknowledged_keys': base.sync, 'ordinary_acknowledgments': base.ordinary_sync,
                    'scope': '原版 Escape／Enter、實際存檔及正常 F2 重讀；尚未 HD 或全新 EXE 重讀驗收'}, ensure_ascii=False, indent=2)+'\n')
                return
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
                'records': records, 'acknowledged_keys': base.sync, 'ordinary_acknowledgments': base.ordinary_sync, 'idle_return': idle,
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
