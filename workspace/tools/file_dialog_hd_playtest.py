"""#38：READY 契約的正常 GUI 操作、清單捲動及兩家族 F12 往返。"""
import hashlib
import json
import os
import subprocess
import tempfile
import zipfile
from pathlib import Path

os.environ['TAIPEI_CITY_MENU_RUN'] = 'file-dialogs-hd'
import city_menu_playtest as base
from file_dialog_catalog import crop, decode_browser, references


def main():
    root = base.root
    assert root.stat().st_uid == os.getuid() and not any(root.glob('*-capture.zip'))
    refs = references(Path('/orig/RS201.ROM').read_bytes())
    menu = Path('/workspace/prototypes/hd-style/city-menus-v1/manifest.json').read_bytes()
    assert hashlib.sha256(menu).hexdigest() == '699c3ed0baed752327667f3d50cc9b0ee45b0124407338eb4f41be94d6239fc5'
    selections = {s['source_sha256']:s['selection'] for s in json.loads(menu)['states'] if s['id'] == 'city-f2'}
    seed = Path('/workspace/runs/gui-cold-saves.zRF8kg/ROUND4.SAV')
    seed_bytes = seed.read_bytes()
    assert hashlib.sha256(seed_bytes).hexdigest() == '8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad'
    saves = Path(tempfile.mkdtemp(prefix='file-dialog-hd-saves.',dir='/workspace/runs'))
    actions, toggles = [], []

    def state():
        with zipfile.ZipFile(root/'capture.zip') as z:
            return json.loads(z.read('status.json')), z.read('frame-index.bin')

    def key(label,value):
        before = base.status()
        base.action(label,value)
        after = base.status()
        assert len(after['key_reads']) == len(before['key_reads'])+1, (label,'原版讀鍵數')
        actions.append({'label':label,'key':value,'steps':after['steps'],'original_read':after['key_reads'][-1]})

    def text(label,value):
        before = base.status()
        subprocess.run(['xdotool','type','--clearmodifiers','--delay','150','--',value],check=True)
        base.wait_for(lambda s:len(s.get('key_reads',[])) >= len(before['key_reads'])+len(value),label+'-read')
        after = base.wait_for(lambda s:s.get('steps',0) >= before['steps']+24_000_000,label)
        assert len(after['key_reads']) == len(before['key_reads'])+len(value)
        base.capture(label)
        actions.append({'label':label,'text':value,'steps':after['steps'],'original_reads':after['key_reads'][len(before['key_reads']):]})

    def browser(label):
        s,frame = state()
        decoded = decode_browser(frame,refs)
        assert decoded and s['hd']['file_dialog'] == 'file-browser',label
        assert s['hd']['file_text'] == decoded['rows'] and s['hd']['file_colors'] == decoded['colors']
        return decoded

    def open_file(label,load):
        key(label+'-menu','F2')
        for attempt in range(4):
            current = selections.get(hashlib.sha256(crop(state()[1],(53,35,68,64))).hexdigest())
            assert current is not None
            if current == int(load):break
            key(f'{label}-choice-{attempt+1}','Down')
        else:raise AssertionError('未到達已驗證的 F2 選項')
        key(label+'-open','space')
        return browser(label)

    def toggle(label,family):
        before,frame = state()
        assert before['hd']['file_dialog'] == family
        for suffix,enabled in [('original',False),('hd',True)]:
            base.action(label+'-theme-'+suffix,'F12')
            after,current = state()
            keyboard = lambda s:[i for i in s['inputs'] if i['kind'] == 'keyboard']
            assert current == frame and after['key_reads'] == before['key_reads'] and keyboard(after) == keyboard(before)
            assert after['hd_enabled'] is enabled and after['hd']['file_dialog'] == (family if enabled else '')
            assert after['hd']['file_text'] == (before['hd']['file_text'] if enabled else ['']*8)
        toggles.append({'family':family,'normal_gui':True,'original_frame_unchanged':True,'no_dos_keyboard':True})

    with (root/'app.log').open('w') as log:
        game = subprocess.Popen(['/workspace/runs/taipei-preview','-original','/orig','-saves',str(saves),
            '-receipts',str(root),'-mute','-steps-per-update','400000','-materials','/workspace/prototypes/hd-style',
            '-theme','hd-b','-stop-file',str(root/'stop')],stdout=log,stderr=subprocess.STDOUT)
        try:
            base.cold_city()
            pause = state()[1]
            assert open_file('empty-load',True)['rows'] == [' '*8]*8
            key('empty-load-confirm','space')
            assert state()[1] == pause and not base.status()['dos_blocked']
            assert open_file('empty-save',False)['rows'] == [' '*8]*8
            toggle('empty-save','file-browser')
            key('empty-save-confirm','space')
            assert state()[1] == pause and not list(saves.glob('*.SAV'))
            open_file('edit-save',False)
            text('length-eight','ABCDEFGH')
            assert browser('length-eight')['rows'][0] == 'ABCDEFGH'
            eight = state()[1]
            text('length-nine','I')
            assert state()[1] == eight
            key('edit-backspace','BackSpace')
            assert browser('edit-backspace')['rows'][0] == 'ABCDEFG '
            key('edit-cancel','Escape')
            assert state()[1] == pause and not list(saves.glob('*.SAV'))
            names = ['11111111','ALPHA001','BETA0002','CITY0003','DELTA004','ECHO0005','FILE0006','GAMMA007','WWWWWWWW','ZZZZZZZZ']
            for name in names:(saves/(name+'.SAV')).write_bytes(seed_bytes)
            list_states = [open_file('load-list',True)]
            for direction in ['Down','Up']:
                for i in range(1,12):
                    label = f'load-list-{direction.lower()}-{i:02d}'
                    key(label,direction)
                    list_states.append(browser(label))
            assert [r['rows'][0].rstrip() for r in list_states] == [names[i] for i in [0,*range(1,10),9,9,*range(8,-1,-1),0,0]]
            text('read-name-ignored','MISSING9')
            assert browser('read-name-ignored') == list_states[-1]
            key('list-cancel','Escape')
            assert state()[1] == pause
            open_file('overwrite',False)
            text('overwrite-name','ALPHA001')
            key('overwrite-confirm','space')
            assert state()[1] == pause and (saves/'ALPHA001.SAV').stat().st_size == 93567
            assert (saves/'ALPHA001.SAV').read_bytes() != seed_bytes
            assert all((saves/(n+'.SAV')).read_bytes() == seed_bytes for n in names if n != 'ALPHA001')
            key('quit-menu','F1');key('quit-confirm','space')
            assert crop(state()[1],(7,175,224,18)) == refs['prompt']
            toggle('quit','quit-confirm')
            text('quit-no','n')
            assert state()[1] == pause and not base.status()['dos_blocked']
            result = {'normal_gui':True,'cold_start':True,'checkpoint':False,'list_states':list_states,
                'empty_save_no_write':True,'empty_load_restored':True,'eight_character_limit':True,
                'backspace_visible':True,'cancel_restored':True,'read_name_ignored':True,'overwrite_without_extra_prompt':True,
                'other_nine_saves_unchanged':True,'quit_no_restored':True,'f12_roundtrips':toggles,
                'acknowledged_actions':actions,'arrow_acknowledgments':base.sync,'save_dir':str(saves),
                'scope':'正常 GUI 呈現驗收；有界停止，完整施工存退讀與兩次原版退出另驗'}
            (root/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        finally:
            (root/'partial-actions.json').write_text(json.dumps(actions,ensure_ascii=False,indent=2)+'\n')
            if game.poll() is None:
                (root/'stop').write_text('stop\n')
                try:game.wait(timeout=10)
                except subprocess.TimeoutExpired:game.kill();game.wait()
            assert game.returncode == 0
    assert seed.read_bytes() == seed_bytes


if __name__ == '__main__':main()
