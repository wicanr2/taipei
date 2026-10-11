"""#38：正常冷啟動探查檔名字集、長度、清單、取消及離開確認。"""
import hashlib
import json
import os
import subprocess
import tempfile
import zipfile
from pathlib import Path

os.environ['TAIPEI_CITY_MENU_RUN'] = os.environ['TAIPEI_FILE_DIALOG_RUN']
import city_menu_playtest as base
from file_dialog_catalog import crop, decode_browser, references


def main():
    root = base.root
    assert root.stat().st_uid == os.getuid()
    assert not any(root.glob('*-capture.zip')), '保留先前收據，先另存原件'
    refs = references(Path('/orig/RS201.ROM').read_bytes())
    menu_raw = Path('/workspace/prototypes/hd-style/city-menus-v1/manifest.json').read_bytes()
    assert hashlib.sha256(menu_raw).hexdigest() == '699c3ed0baed752327667f3d50cc9b0ee45b0124407338eb4f41be94d6239fc5'
    file_selections = {s['source_sha256']: s['selection'] for s in json.loads(menu_raw)['states'] if s['id'] == 'city-f2'}
    seed = Path('/workspace/runs/gui-cold-saves.zRF8kg/ROUND4.SAV')
    seed_bytes = seed.read_bytes()
    seed_sha = hashlib.sha256(seed_bytes).hexdigest()
    assert seed_sha == '8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad'
    saves = Path(tempfile.mkdtemp(prefix='file-dialog-saves.', dir='/workspace/runs'))
    records = []

    def state():
        with zipfile.ZipFile(root/'capture.zip') as z:
            s, frame = json.loads(z.read('status.json')), z.read('frame-index.bin')
        return s, frame, decode_browser(frame, refs)

    def key(label, value):
        before = base.status()
        base.action(label, value)
        after = base.status()
        assert len(after['key_reads']) == len(before['key_reads'])+1, (label, '原版讀鍵數')
        records.append({'label': label, 'kind': 'key', 'value': value,
                        'before_step': before['steps'], 'after_step': after['steps'],
                        'original_reads': after['key_reads'][-1:]})

    def text(label, value):
        before = base.status()
        subprocess.run(['xdotool','type','--clearmodifiers','--delay','150','--',value], check=True)
        base.wait_for(lambda s: len(s.get('key_reads',[])) >= len(before['key_reads'])+len(value), label+'-read')
        after = base.wait_for(lambda s: s.get('steps',0) >= before['steps']+24_000_000, label)
        assert len(after['key_reads']) == len(before['key_reads'])+len(value), (label, '重複或漏讀字元')
        base.capture(label)
        records.append({'label': label, 'kind': 'text', 'value': value,
            'before_step': before['steps'], 'after_step': after['steps'],
            'original_reads': after['key_reads'][len(before['key_reads']):]})

    def browser(label):
        result = state()[2]
        assert result is not None, (label, '完整原版檔案視窗未重建')
        return result

    def open_file(label, load):
        key(label+'-menu','F2')
        for attempt in range(4):
            current = file_selections.get(hashlib.sha256(crop(state()[1], (53,35,68,64))).hexdigest())
            assert current is not None, (label, 'F2 完整來源未辨識')
            if current == int(load):
                break
            key(f'{label}-choice-{attempt+1}','Down')
        else:
            raise AssertionError((label, 'F2 選項未抵達'))
        key(label+'-open','space')
        return browser(label)

    def cancel(label):
        key(label,'Escape')
        s, _, decoded = state()
        records[-1]['browser_after'] = decoded
        records[-1]['blocked_after'] = s['dos_blocked']
        assert decoded is None and not s['dos_blocked'], (label, '尚未確認正常取消契約')

    with (root/'app.log').open('w') as log:
        game = subprocess.Popen(['/workspace/runs/taipei-preview','-original','/orig','-saves',str(saves),
            '-receipts',str(root),'-mute','-steps-per-update','400000','-materials',
            '/workspace/prototypes/hd-style','-theme','original','-stop-file',str(root/'stop')],
            stdout=log, stderr=subprocess.STDOUT)
        try:
            base.cold_city()
            pause = state()[1]
            characters = []
            eight = nine = cleared = empty_load = empty_confirm = None
            phase = os.environ['TAIPEI_FILE_DIALOG_RUN'].rsplit('-',1)[-1]
            short_phase = phase in ['list','edges','missing']
            empty_save = overwrite = missing_name = None
            if phase == 'edges':
                open_file('save-empty',False)
                key('save-empty-confirm','space')
                empty_save = {'status':base.status(),'browser':state()[2],
                    'files':[p.name for p in saves.iterdir()], 'restored':state()[1] == pause}
                assert state()[1] == pause and not base.status()['dos_blocked'], '空白存檔確認另有狀態，保留來源'
            if not short_phase:
                assert open_file('save-empty',False)['rows'] == [' '*8]*8
                # 首次 33–47 已留下完整正常讀鍵收據；第二輪從首次停點繼續。
                first_code = 48 if os.environ['TAIPEI_FILE_DIALOG_RUN'].endswith('-extra') else 33
                for code in range(first_code,127):
                    label = f'char-{code:02x}'
                    text(label,chr(code))
                    observed = browser(label)
                    characters.append({'input_code': code, 'displayed': observed['rows'][0],
                        'colors': observed['colors'], 'receipt': label+'-capture.zip'})
                    key(label+'-backspace','BackSpace')
                    characters[-1]['after_backspace'] = browser(label)
                text('length-eight','ABCDEFGH')
                eight = browser('length-eight')
                text('length-nine','I')
                nine = browser('length-nine')
                for i in range(8):
                    key(f'clear-eight-{i+1}','BackSpace')
                cleared = browser('clear-eight')
                cancel('save-empty-cancel')
                assert state()[1] == pause
                empty_load = open_file('load-empty',True)
                key('load-empty-confirm','space')
                empty_confirm = {'status': base.status(), 'browser': state()[2]}
                if state()[2] is not None:
                    cancel('load-empty-cancel')
            names = ['ALPHA001','BETA0002','CITY0003','DELTA004','ECHO0005',
                     'FILE0006','GAMMA007','WWWWWWWW','ZZZZZZZZ','11111111']
            for name in names:
                path = saves/(name+'.SAV')
                assert not path.exists()
                path.write_bytes(seed_bytes)
            selected = open_file('load-list',True)
            list_states = [selected]
            for direction in ([] if phase in ['edges','missing'] else ['Down','Up']):
                for i in range(1,12):
                    label = f'load-list-{direction.lower()}-{i:02d}'
                    key(label,direction)
                    list_states.append(browser(label))
            if phase == 'missing':
                before_name = state()[1]
                text('load-unavailable-name','MISSING9')
                missing_name = {'typed':'MISSING9','browser':browser('load-unavailable-name'),
                    'frame_unchanged':state()[1] == before_name}
                assert missing_name['frame_unchanged'], '讀檔名稱可編輯，需另查不存在檔案分支'
            cancel('load-list-cancel')
            if phase == 'edges':
                open_file('overwrite',False)
                text('overwrite-name','ALPHA001')
                key('overwrite-confirm','space')
                path = saves/'ALPHA001.SAV'
                overwrite = {'status':base.status(),'browser':state()[2],
                    'before_sha256':seed_sha,'after_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                    'bytes':path.stat().st_size,'restored':state()[1] == pause}
                assert state()[1] == pause and not base.status()['dos_blocked'], '覆寫另有狀態，保留來源'
            key('quit-menu','F1'); key('quit-confirm','space')
            question = state()[1]
            text('quit-no','n')
            assert state()[1] == pause and not base.status()['dos_blocked']
            result = {'normal_gui': True, 'cold_start': True, 'checkpoint': False,
                'save_dir': str(saves), 'seed_sha256': seed_sha, 'characters': characters,
                'source_phase': phase, 'empty_save':empty_save, 'overwrite':overwrite,
                'missing_name':missing_name,
                'length_eight': eight, 'length_nine': nine, 'after_eight_backspaces': cleared,
                'empty_load': empty_load,
                'empty_load_confirm': empty_confirm, 'list_states': list_states,
                'quit_prompt_sha256': hashlib.sha256(question).hexdigest(),
                'acknowledged_actions': records, 'arrow_acknowledgments': base.sync,
                'scope': '正常來源探索；有界停止，正式存退讀與原版退出另驗'}
            (root/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        finally:
            (root/'partial-actions.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
            if game.poll() is None:
                (root/'stop').write_text('stop\n')
                try: game.wait(timeout=10)
                except subprocess.TimeoutExpired: game.kill(); game.wait()
            assert game.returncode == 0, game.returncode
    assert seed.read_bytes() == seed_bytes


if __name__ == '__main__':
    main()
