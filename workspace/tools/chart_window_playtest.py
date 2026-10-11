"""#48：F4 六入口確認後的正常來源研究；不接正式呈現。"""
import json
import subprocess
import tempfile
import zipfile
from pathlib import Path

import city_menu_playtest as base
from hd_source_audit import scene, sha

console_sync = []


def model():
    with zipfile.ZipFile(base.out/'capture.zip') as z:
        s, frame = json.loads(z.read('status.json')), z.read('frame-index.bin')
    assert len(frame) == 64000 and sha(frame) == s['frame_index_sha256']
    return s, frame


def key(label, value):
    before = base.status()
    base.action(label, value, acknowledge=True)
    assert len(base.status()['key_reads']) == len(before['key_reads'])+1, label


def return_chart(label):
    before = base.status()
    def reads(s):
        return [k for k in s.get('key_reads', []) if k.get('Via')=='int21-AH07' and k.get('Key')==27]
    count = len(reads(before))
    breaks = sum(k.get('kind')=='keyboard' and k.get('scan')==0x81 for k in before['inputs'])
    subprocess.run(['xdotool', 'keydown', 'Escape'], check=True)
    try:
        base.wait_for(lambda s:len(reads(s))>=count+1, label+'-console-read')
    finally:
        subprocess.run(['xdotool', 'keyup', 'Escape'], check=True)
    released = base.wait_for(lambda s:sum(k.get('kind')=='keyboard' and k.get('scan')==0x81
        for k in s.get('inputs', []))>=breaks+1, label+'-release')
    assert len(reads(released))==count+1 and len(released['key_reads'])==len(before['key_reads'])+1
    assert reads(released)[-1]['Word']==0
    console_sync.append({'label':label, 'original_read':reads(released)[-1],
                         'release_steps':released['steps'], 'break_scan':0x81})
    base.capture(label)


def main():
    root = base.root
    assert not (root/'result.json').exists()
    saves = tempfile.mkdtemp(prefix='chart-window-saves.', dir='/workspace/runs')
    samples = []
    raw = Path('/workspace/prototypes/hd-style/city-menu-sources-v1.json').read_bytes()
    assert sha(raw)=='eb98c1def205eb39e533f9646ad9336fafc7268559998e93e3a1ed1c7157f870'
    menu_sources = {s['source_sha256']:s['selection'] for s in json.loads(raw)['states'] if s['id']=='city-f4'}
    assert len(menu_sources)==6
    def selection():
        s, pixels = model()
        raw = b''.join(pixels[(35+y)*320+141:(35+y)*320+209] for y in range(94))
        assert s['dos_blocked'] and sha(raw) in menu_sources
        return menu_sources[sha(raw)], sha(raw)
    with (root/'app.log').open('w') as log:
        game = subprocess.Popen(['/workspace/runs/taipei-preview', '-original', '/orig', '-saves', saves,
            '-receipts', str(root), '-mute', '-steps-per-update', '400000', '-materials',
            '/workspace/prototypes/hd-style', '-theme', 'original', '-stop-file', str(root/'stop')],
            stdout=log, stderr=subprocess.STDOUT)
        try:
            base.wait_for(lambda s:s.get('steps', 0)>=700_000_000, 'intro', progress=True)
            subprocess.run(['xdotool', 'search', '--name', '模擬台北', 'windowfocus'], check=True)
            base.action('intro-space', 'space')
            base.wait_for(lambda s:s.get('steps', 0)>=800_000_000, 'intro-wait')
            base.action('main', 'space')
            base.wait_for(lambda s:s.get('frame_index_sha256')=='5442a8135d36552561f03a46fc443978a76989979e0c25dc016027229b24dda4', 'main-ready')
            key('scenario-choice', 'Right')
            key('scenario-open', 'space')
            for i, value in enumerate(['space', 'space', 'space', '0']):
                key(f'scenario-step-{i}', value)
            paused, frame = model()
            assert scene(paused, frame)
            assert any(f.get('Op')=='read' and f.get('Name', '').lower()=='disa1.dsa' for f in paused['file_ops'])
            base.capture('city-paused')
            names = ['電力供應', '交通密度', '人口密度', '犯罪率', '房價', '污染']
            for index, name in enumerate(names):
                before, _ = model()
                key(f'chart-{index}-menu', 'F4')
                current, _ = selection()
                entered_selection = current
                for step in range((index-current)%6):
                    key(f'chart-{index}-select-{step}', 'Down')
                    actual, _ = selection()
                    assert actual == (current+1)%6
                    current = actual
                chosen, menu_source = selection()
                assert chosen == index
                base.capture(f'chart-{index}-chosen')
                key(f'chart-{index}-open', 'space')
                base.wait_for(lambda s:s.get('dos_blocked') is True, f'chart-{index}-blocked')
                opened, raw = model()
                assert opened['mode']==19 and not opened['dos_exited']
                base.capture(f'chart-{index}-blocked')
                observed = []
                for j in range(2):
                    start = base.status()['steps']
                    base.wait_for(lambda s:s.get('steps', 0)>=start+24_000_000, f'chart-{index}-observe-{j}')
                    s, current = model()
                    assert s['dos_blocked'] and current == raw
                    base.capture(f'chart-{index}-observe-{j}')
                    observed.append({'steps':s['steps'], 'frame_sha256':sha(current)})
                return_chart(f'chart-{index}-return')
                returned, current = model()
                assert scene(returned, current) and returned['map_origin'] == before['map_origin']
                samples.append({'option':index, 'menu_text':name,
                    'actual_menu_selection':chosen, 'entered_menu_selection':entered_selection,
                    'menu_source_sha256':menu_source,
                    'receipt':f'chart-{index}-blocked-capture.zip', 'steps':opened['steps'],
                    'frame_sha256':sha(raw), 'blocked':True, 'observations':observed,
                    'return_receipt':f'chart-{index}-return-capture.zip', 'return_city':True})
            (root/'result.json').write_text(json.dumps({'issue':48, 'normal_gui':True, 'checkpoint':False,
                'scenario':'DISA1.DSA', 'charts':samples, 'arrow_acknowledgments':base.sync,
                'ordinary_acknowledgments':base.ordinary_sync,
                'console_acknowledgments':console_sync,
                'scope':'正常六入口來源及返回研究；有界停止，不代替正常原版退出、HD 或存退讀驗收'},
                ensure_ascii=False, indent=2)+'\n')
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
