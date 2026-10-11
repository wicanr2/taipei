#!/usr/bin/env python3
"""#4：Xvfb 內用真實視窗事件走冷啟動，不注入遊戲狀態。"""
import json
import hashlib
import os
import shutil
import subprocess
import time
import zipfile
from pathlib import Path

out=Path('/workspace/runs/gui-cold')
def status():
    try:
        with zipfile.ZipFile(out/'capture.zip') as z:
            s=json.loads(z.read('status.json'))
            assert hashlib.sha256(z.read('frame-index.bin')).hexdigest()==s['frame_index_sha256']
            return s
    except (OSError,json.JSONDecodeError,zipfile.BadZipFile):
        return {}

def wait_for(predicate, label, seconds=120):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        s=status()
        if predicate(s):
            print(label,s.get('steps'),s.get('frame_index_sha256'),flush=True)
            return s
        time.sleep(.2)
    s=status()
    raise RuntimeError(f'GUI 等待逾時：{label}; steps={s.get("steps")}; last_keys={(s.get("key_reads") or [])[-3:]}')

def keypress(key):
    subprocess.run(['xdotool','keydown',key],check=True)
    time.sleep(.15)
    subprocess.run(['xdotool','keyup',key],check=True)

def space():
    keypress('space')

def capture(label):
    raw=(out/'capture.zip').read_bytes()
    (out/(label+'-capture.zip')).write_bytes(raw)
    import io
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        for name in ['frame.png','frame-index.bin','status.json','presentation.png']:
            (out/(label+'-'+name)).write_bytes(z.read(name))

def action(label,key):
    before=status().get('steps',0)
    if key.startswith('type:'):
        subprocess.run(['xdotool','type','--delay','150',key[5:]],check=True)
    else:
        keypress(key)
    wait_for(lambda s:s.get('steps',0)>=before+24_000_000,label)
    capture(label)

def native_exit(label):
    action(label+'-menu','F1')
    action(label+'-select','Down')
    action(label+'-confirm','space')
    subprocess.run(['xdotool','type','--delay','150','Y'],check=True)
    # 原版先播離開動畫，再於政績畫面透過 AH=07h 等最後一個鍵。
    # 只等原版控制流，不跳過動畫，也不以固定睡眠猜測完成時間。
    wait_for(lambda s: s.get('dos_blocked') is True and
             any(k.get('Via')=='int21-AH07' and k.get('Key')==89
                 for k in s.get('key_reads',[])), label+'-score')
    capture(label+'-score')
    space()
    wait_for(lambda s:s.get('dos_exited') is True,label+'-native-exit')
    capture(label+'-native-exit')

wait_for(lambda s:s.get('steps',0)>=700_000_000,'intro')
subprocess.run(['xdotool','search','--name','模擬台北','windowfocus'],check=True)
space()
wait_for(lambda s:s.get('steps',0)>=800_000_000,'intro-wait')
space()
wait_for(lambda s:s.get('frame_index_sha256')=='5442a8135d36552561f03a46fc443978a76989979e0c25dc016027229b24dda4','main-menu')
capture('main-menu')
before=status().get('steps',0)
space()
wait_for(lambda s:s.get('steps',0)>=before+24_000_000,'city-choice')
capture('city-choice')
subprocess.run(['import','-window','root',str(out/'window.png')],check=True)
for stage in ['new-game','difficulty','city-map']:
    before=status().get('steps',0)
    space()
    wait_for(lambda s:s.get('steps',0)>=before+24_000_000,stage)
    capture(stage)
    if stage=='new-game' and os.environ.get('TAIPEI_THEME')=='hd-b':
        before_dialog=status()
        assert before_dialog['hd']['dialog']=='new-game', '完整說明視窗未覆繪'
        reads=before_dialog.get('key_reads',[])
        for label,enabled in [('new-game-theme-original',False),('new-game-theme-hd',True)]:
            action(label,'F12')
            current=status()
            assert current['hd_enabled'] is enabled
            assert current['hd']['dialog']==('new-game' if enabled else '')
            assert current['frame_index_sha256']==before_dialog['frame_index_sha256'], '切換改動原版視窗'
            assert current.get('key_reads',[])==reads, '視窗切換流入 DOS'
# 新城市初始焦點是工具列。第 2 項是每單位 20 萬的電線。
# 方向鍵、空白鍵與施工均由原版處理，不注入游標或城市資料。
action('pause','type:0')
if os.environ.get('TAIPEI_THEME')=='hd-b':
    assert status()['hd']['Painted']>400, 'HD 城市未覆繪'
    key_reads=len(status().get('key_reads',[]))
    action('theme-original','F12')
    assert status()['hd_enabled'] is False and status()['hd']['Painted']==0
    assert len(status().get('key_reads',[]))==key_reads, '主題快捷鍵流入 DOS'
    action('theme-hd','F12')
    assert status()['hd_enabled'] is True and status()['hd']['Painted']>400
    assert len(status().get('key_reads',[]))==key_reads, '主題快捷鍵流入 DOS'
for label,key in [('power-tool','Right'),('power-confirm','space')]:
    action(label,key)
# #34：以原子收據確認原版讀鍵及前端 release，避免負載下漏掉短脈衝。
movement_sync=[]
for index in range(25):
    before=status()
    reads=sum(k.get('Word')==0x4d00 for k in before.get('key_reads',[]))
    breaks=sum(k.get('kind')=='keyboard' and k.get('scan')==0xcd for k in before.get('inputs',[]))
    subprocess.run(['xdotool','keydown','Right'],check=True)
    try:
        pressed=wait_for(lambda s:sum(k.get('Word')==0x4d00 for k in s.get('key_reads',[]))>=reads+1,f'land-right-{index+1:02d}-read')
    finally:
        subprocess.run(['xdotool','keyup','Right'],check=True)
    released=wait_for(lambda s:sum(k.get('kind')=='keyboard' and k.get('scan')==0xcd for k in s.get('inputs',[]))>=breaks+1,f'land-right-{index+1:02d}-release')
    assert sum(k.get('Word')==0x4d00 for k in released.get('key_reads',[]))==reads+1,'連續 Right 重複送達'
    movement_sync.append({'index':index+1,'press_receipt_step':pressed['steps'],'release_receipt_step':released['steps'],'original_reads_before':reads,'original_reads_after':reads+1,'breaks_before':breaks,'breaks_after':breaks+1})
(out/'movement-sync.json').write_text(json.dumps(movement_sync,indent=2)+'\n')
action('land-down','Down')
capture('before-build')
action('place-power','space')
action('uncover-power','Right')
cell=(230,43)
def tile(frame, xy):
    data=Path(frame).read_bytes()
    assert len(data)==64000
    x,y=xy
    return b''.join(data[(y+row)*320+x:(y+row)*320+x+9] for row in range(9))
base_tile=tile(out/'city-map-frame-index.bin',cell)
built_tile=tile(out/'uncover-power-frame-index.bin',cell)
assert built_tile!=base_tile, '原版施工未改變目標圖塊'
assert len(set(built_tile))>1, '施工結果只有空白色塊'
for label,key in [('file-menu','F2'),('save-dialog','space'),('save-name','type:round3'),
                  ('backspace','BackSpace'),('rename','type:4'),('save-accept','space')]:
    action(label,key)
save_dir=Path(os.environ['TAIPEI_TEST_SAVES'])
save=save_dir/'ROUND4.SAV'
assert save.is_file() and save.stat().st_size==93567, '原版存檔尚未產生'
saved_sha=hashlib.sha256(save.read_bytes()).hexdigest()
(out/'saved-file.json').write_text(json.dumps({'path':str(save),'size':save.stat().st_size,'sha256':saved_sha},indent=2))
native_exit('quit')

# 全新 EXE 冷啟動，再由原版主選單讀取同一存檔，沒有載入機器快照。
first_out=out
out=first_out/'reload'
out.mkdir(exist_ok=True)
for name in ['status.json','capture.zip','stop']:
    (out/name).unlink(missing_ok=True)
with (out/'app.log').open('w') as log:
    p=subprocess.Popen(['/workspace/runs/taipei-preview','-original','/orig','-saves',str(save_dir),
                        '-mute','-steps-per-update','400000',
                        '-materials','/workspace/prototypes/hd-style','-theme',os.environ.get('TAIPEI_THEME','original'),
                        '-receipts',str(out),'-stop-file',str(out/'stop')],stdout=log,stderr=subprocess.STDOUT)
    try:
        wait_for(lambda s:s.get('steps',0)>=700_000_000,'reload-intro')
        subprocess.run(['xdotool','search','--name','模擬台北','windowfocus'],check=True)
        space()
        wait_for(lambda s:s.get('steps',0)>=800_000_000,'reload-intro-wait')
        space()
        wait_for(lambda s:s.get('frame_index_sha256')=='5442a8135d36552561f03a46fc443978a76989979e0c25dc016027229b24dda4','reload-main-menu')
        for label,key in [('load-choice-1','Right'),('load-choice-2','Right'),('load-dialog','space'),
                          ('load-name','type:round4'),('load-accept','space')]:
            action(label,key)
        assert any(f.get('Op')=='read' and f.get('Name','').upper()=='ROUND4.SAV' for f in status().get('file_ops',[])), '未見原版讀取存檔'
        assert hashlib.sha256(save.read_bytes()).hexdigest()==saved_sha, '讀檔改寫了來源存檔'
        loaded_tile=tile(out/'load-accept-frame-index.bin',cell)
        assert loaded_tile==built_tile, '冷啟動讀檔未恢復施工圖塊'
        native_exit('reload-quit')
        assert p.wait(timeout=10)==0
        (first_out/'result.json').write_text(json.dumps({'cold_start':True,'checkpoint':False,'native_exit':True,'reload_read':True,'new_game_dialog_f12_roundtrip':os.environ.get('TAIPEI_THEME')=='hd-b','save_sha256':saved_sha,'save_dir':str(save_dir), 'construction':{'native_xy':cell,'before_sha256':hashlib.sha256(base_tile).hexdigest(),'after_sha256':hashlib.sha256(built_tile).hexdigest(),'cold_loaded_same':True}},indent=2))
        print('GUI cold construction / save / native exit / cold reload passed',flush=True)
    finally:
        if p.poll() is None:
            (out/'stop').write_text('stop\n')
            try:p.wait(timeout=10)
            except subprocess.TimeoutExpired:p.kill();p.wait()
