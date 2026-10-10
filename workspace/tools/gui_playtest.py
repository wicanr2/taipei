#!/usr/bin/env python3
"""#4：Xvfb 內用真實視窗事件走冷啟動，不注入遊戲狀態。"""
import json
import hashlib
import os
import shutil
import subprocess
import time
from pathlib import Path

out=Path('/workspace/runs/gui-cold')
def status():
    try:
        return json.loads((out/'status.json').read_text())
    except (OSError,json.JSONDecodeError):
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
    raise RuntimeError(f'GUI 等待逾時：{label}; steps={s.get("steps")}; last_keys={s.get("key_reads",[])[-3:]}')

def keypress(key):
    subprocess.run(['xdotool','keydown',key],check=True)
    time.sleep(.15)
    subprocess.run(['xdotool','keyup',key],check=True)

def space():
    keypress('space')

def capture(label):
    for name in ['frame.png','frame-index.bin','status.json']:
        shutil.copyfile(out/name,out/(label+'-'+name))

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
for name in ['frame.png','status.json']:
    shutil.copyfile(out/name,out/('main-menu-'+name))
before=status().get('steps',0)
space()
wait_for(lambda s:s.get('steps',0)>=before+24_000_000,'city-choice')
for name in ['frame.png','status.json']:
    shutil.copyfile(out/name,out/('city-choice-'+name))
subprocess.run(['import','-window','root',str(out/'window.png')],check=True)
for stage in ['new-game','difficulty','city-map']:
    before=status().get('steps',0)
    space()
    wait_for(lambda s:s.get('steps',0)>=before+24_000_000,stage)
    capture(stage)
for label,key in [('cursor-right','Right'),
                  ('file-menu','F2'),('save-dialog','space'),('save-name','type:round3'),
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
for name in ['status.json','stop']:
    (out/name).unlink(missing_ok=True)
with (out/'app.log').open('w') as log:
    p=subprocess.Popen(['/workspace/runs/taipei-preview','-original','/orig','-saves',str(save_dir),
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
        native_exit('reload-quit')
        assert p.wait(timeout=10)==0
        (first_out/'result.json').write_text(json.dumps({'cold_start':True,'checkpoint':False,'native_exit':True,'reload_read':True,'save_sha256':saved_sha,'save_dir':str(save_dir)},indent=2))
        print('GUI cold save / native exit / cold reload passed',flush=True)
    finally:
        if p.poll() is None:
            (out/'stop').write_text('stop\n')
            try:p.wait(timeout=10)
            except subprocess.TimeoutExpired:p.kill();p.wait()
