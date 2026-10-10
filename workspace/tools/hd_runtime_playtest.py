"""#25：由實際視窗操作原版城市，按固定虛擬步數抽樣時間推進。"""
import hashlib
import io
import json
import subprocess
import time
import zipfile
from pathlib import Path

out=Path('/workspace/runs/hd-runtime')
def bundle():
    raw=(out/'capture.zip').read_bytes()
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        s=json.loads(z.read('status.json'));frame=z.read('frame-index.bin')
    assert hashlib.sha256(frame).hexdigest()==s['frame_index_sha256']
    return raw,s,frame
def state():
    try:return bundle()[1]
    except (OSError,zipfile.BadZipFile):return {}
def wait_for(predicate,label):
    deadline=time.monotonic()+120
    while time.monotonic()<deadline:
        s=state()
        if predicate(s):print(label,s['steps'],s.get('hd'),flush=True);return s
        time.sleep(.2)
    raise RuntimeError(f'持續運行等待逾時：{label}; steps={state().get("steps")}')
def press(key):
    subprocess.run(['xdotool','keydown',key],check=True);time.sleep(.15)
    subprocess.run(['xdotool','keyup',key],check=True)
def capture(label):
    raw,s,frame=bundle();(out/(label+'-capture.zip')).write_bytes(raw)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        (out/(label+'-presentation.png')).write_bytes(z.read('presentation.png'))
        (out/(label+'-frame.png')).write_bytes(z.read('frame.png'))
    return s,frame
def action(label,key):
    if key in ['1','2','3']:subprocess.run(['xdotool','type',key],check=True)
    else:press(key)
    after=state().get('steps',0)
    wait_for(lambda s:s.get('steps',0)>=after+24000000,label)
    return capture(label)

wait_for(lambda s:s.get('steps',0)>=700000000,'intro')
subprocess.run(['xdotool','search','--name','模擬台北','windowfocus'],check=True)
press('space');wait_for(lambda s:s.get('steps',0)>=800000000,'intro-wait')
press('space')
wait_for(lambda s:s.get('frame_index_sha256')=='5442a8135d36552561f03a46fc443978a76989979e0c25dc016027229b24dda4','main-menu')
for label in ['city-choice','new-game','difficulty','city-map']:action(label,'space')
started,_=action('native-speed-3','3')
for i in range(1,61):
    target=started['steps']+i*24000000
    wait_for(lambda s:s.get('steps',0)>=target,f'running-{i:02d}')
    capture(f'running-{i:02d}')
(out/'stop').write_text('stop\n')
result={'cold_start':True,'checkpoint':False,'window_input':True,'native_speed_key':'3',
        'pause_key_sent':False,'sample_interval_steps':24000000,'scheduled_samples':60,
        'native_exit':False,'formal_hd':False,
        'scope':'原版速度操作後的正常持續運行；日期推進與 HD 像素由獨立核對另驗'}
(out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('cold GUI runtime capture completed',flush=True)
