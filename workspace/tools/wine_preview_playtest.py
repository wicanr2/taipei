"""Windows binary 經 Wine 的正常冷啟動與按鍵預檢；不注入狀態。"""
import hashlib
import json
import subprocess
import time
import zipfile
from pathlib import Path

out=Path('/workspace/runs/wine-preview')
def state():
    try:
        with zipfile.ZipFile(out/'capture.zip') as z:
            s=json.loads(z.read('status.json'))
            assert hashlib.sha256(z.read('frame-index.bin')).hexdigest()==s['frame_index_sha256']
            return s
    except (OSError,zipfile.BadZipFile): return {}
def wait_for(pred,label):
    deadline=time.monotonic()+120
    while time.monotonic()<deadline:
        s=state()
        if pred(s): print(label,s['steps'],flush=True); return s
        time.sleep(.2)
    raise RuntimeError(f'Wine GUI 等待逾時：{label}, state={state().get("steps")}')
def space():
    subprocess.run(['xdotool','keydown','space'],check=True)
    time.sleep(.15)
    subprocess.run(['xdotool','keyup','space'],check=True)
def capture(label):
    (out/(label+'-capture.zip')).write_bytes((out/'capture.zip').read_bytes())

wait_for(lambda s:s.get('steps',0)>=700000000,'intro')
subprocess.run(['xdotool','search','--name','模擬台北','windowfocus'],check=True)
space()
wait_for(lambda s:s.get('steps',0)>=800000000,'intro-wait')
space()
wait_for(lambda s:s.get('frame_index_sha256')=='5442a8135d36552561f03a46fc443978a76989979e0c25dc016027229b24dda4','main-menu')
capture('main-menu')
for label in ['city-choice','new-game','difficulty','city-map']:
    before=state()['steps'];space()
    s=wait_for(lambda s:s.get('steps',0)>=before+24000000,label)
    capture(label)
assert s['frame_index_sha256']=='a838e6e26f6af4f62a2fc9a6c945e2671c2b5fa8194d80f01b028791a20fe000'
assert any(k.get('Key')==32 for k in s.get('key_reads',[]))
(out/'stop').write_text('stop\n')
result={'windows_binary':True,'wine':True,'cold_start':True,'checkpoint':False,
        'city_map_sha256':s['frame_index_sha256'],'native_input':True,
        'audio_device':False,'native_machine':False,'package':False,
        'scope':'Windows 研究 binary 的 Wine 冷啟動至城市畫面；非正式封包或真機驗收'}
(out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
