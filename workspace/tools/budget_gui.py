"""#39：共用正常冷啟動流程中的預算調整、F12 與冷讀設定核對。"""
import hashlib
import json
import os
import zipfile
from pathlib import Path

os.environ.setdefault('TAIPEI_CITY_MENU_RUN',os.environ.get('TAIPEI_GUI_RUN','gui-budget-cold'))
import city_menu_playtest as base
from budget_catalog import crop, decode_budget, references


def exercise(root, adjust):
    base.out = root
    refs = references(Path('/orig/RS201.ROM').read_bytes())
    raw = Path('/workspace/prototypes/hd-style/city-menus-v1/manifest.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == '699c3ed0baed752327667f3d50cc9b0ee45b0124407338eb4f41be94d6239fc5'
    choices = {s['source_sha256']:s['selection'] for s in json.loads(raw)['states'] if s['id'] == 'city-f3'}
    actions, toggles = [], []

    def model():
        with zipfile.ZipFile(root/'capture.zip') as z:
            s,frame = json.loads(z.read('status.json')),z.read('frame-index.bin')
        return s,frame,decode_budget(frame,refs)

    def key(label,value):
        before = base.status()
        base.action('budget-'+label,value,acknowledge=True)
        s,_,decoded = model()
        assert len(s['key_reads']) == len(before['key_reads'])+1
        if decoded:
            assert s['hd']['budget'] and s['hd']['budget_text'] == [f['text'] for f in decoded['fields']]
        actions.append({'label':label,'key':value,'steps':s['steps'],'original_read':s['key_reads'][-1]})
        return decoded

    def open_panel(label):
        key(label+'-menu','F3')
        for i in range(3):
            selection = choices.get(hashlib.sha256(crop(model()[1],(97,35,68,49))).hexdigest())
            assert selection is not None
            if selection == 0:break
            key(f'{label}-choose-{i}','Down')
        else:raise AssertionError('未抵達正常預算選項')
        result = key(label+'-open','space')
        assert result is not None
        return result

    initial = open_panel('initial')
    assert initial['percent'] == ([10,100,100,100,100] if adjust else [9,99,100,100,100])
    for row in range(5):
        before,frame,decoded = model()
        assert decoded['selected_rows'] == [row]
        for suffix,enabled in [('original',False),('hd',True)]:
            base.action(f'budget-row-{row}-theme-{suffix}','F12')
            s,current,_ = model()
            keyboard = lambda value:[k for k in value['inputs'] if k['kind'] == 'keyboard']
            assert current == frame and s['key_reads'] == before['key_reads'] and keyboard(s) == keyboard(before)
            assert s['hd_enabled'] is enabled and s['hd']['budget'] is enabled
            assert s['hd']['budget_text'] == (before['hd']['budget_text'] if enabled else ['']*11)
        toggles.append({'row':row,'frame_unchanged':True,'no_dos_keyboard':True})
        if adjust:
            changed = key(f'row-{row}-decrease','Right')
            assert changed['percent'][row] == initial['percent'][row]-1
            restored = key(f'row-{row}-restore','Left')
            assert restored['percent'] == initial['percent']
        key(f'row-{row}-down','Down')
    if adjust:
        key('tax-decrease','Right')
        key('safety-select','Down')
        modified = key('safety-decrease','Right')
        assert modified['percent'] == [9,99,100,100,100]
    assert key('escape','Escape') is None
    reopened = open_panel('reopen')
    assert reopened['percent'] == [9,99,100,100,100]
    assert key('enter','Return') is not None
    assert key('return','Escape') is None
    result = {'normal_gui':True,'adjust':adjust,'initial':initial,'reopened':reopened,
        'f12_five_rows':toggles,'actions':actions,'ordinary_acknowledgments':base.ordinary_sync,
        'arrow_acknowledgments':base.sync,'scope':'正常 F3 預算操作與 F12；呼叫者另驗存檔及原版退出'}
    (root/'budget-gui.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result
