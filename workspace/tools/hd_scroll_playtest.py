"""#23：只用視窗按鍵移動原版地圖，原子保存實際呈現。"""
import hashlib
import io
import json
import subprocess
import time
import zipfile
from pathlib import Path

out=Path('/workspace/runs/hd-scroll')
def bundle():
    raw=(out/'capture.zip').read_bytes()
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        s=json.loads(z.read('status.json')); frame=z.read('frame-index.bin')
    assert hashlib.sha256(frame).hexdigest()==s['frame_index_sha256']
    return raw,s,frame
def state():
    try: return bundle()[1]
    except (OSError,zipfile.BadZipFile): return {}
def wait_for(predicate,label):
    deadline=time.monotonic()+120
    while time.monotonic()<deadline:
        s=state()
        if predicate(s): print(label,s['steps'],s.get('hd'),flush=True);return s
        time.sleep(.2)
    raise RuntimeError(f'捲動等待逾時：{label}; steps={state().get("steps")}')
def press(key):
    subprocess.run(['xdotool','keydown',key],check=True);time.sleep(.12)
    subprocess.run(['xdotool','keyup',key],check=True);time.sleep(.12)
def capture(label):
    raw,s,frame=bundle();(out/(label+'-capture.zip')).write_bytes(raw)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        (out/(label+'-presentation.png')).write_bytes(z.read('presentation.png'))
    return s,frame
def action(label,key,count=1):
    if key=='0': subprocess.run(['xdotool','type','0'],check=True)
    else:
        for _ in range(count): press(key)
    after=state().get('steps',0)
    wait_for(lambda s:s.get('steps',0)>=after+24000000,label)
    return capture(label)

wait_for(lambda s:s.get('steps',0)>=700000000,'intro')
subprocess.run(['xdotool','search','--name','模擬台北','windowfocus'],check=True)
press('space');wait_for(lambda s:s.get('steps',0)>=800000000,'intro-wait')
press('space')
wait_for(lambda s:s.get('frame_index_sha256')=='5442a8135d36552561f03a46fc443978a76989979e0c25dc016027229b24dda4','main-menu')
for label in ['city-choice','new-game','difficulty','city-map']: action(label,'space')
action('pause','0');action('map-focus','Tab')
for label,key,count in [
    ('right-10','Right',10),('right-20','Right',10),('right-30','Right',10),('right-40','Right',10),
    ('down-6','Down',6),('down-12','Down',6),('down-18','Down',6),
    ('left-10','Left',10),('left-20','Left',10),('left-30','Left',10),('left-40','Left',10),
    ('up-6','Up',6),('up-12','Up',6),('up-18','Up',6)]: action(label,key,count)
before=state();modal,_=action('file-menu','F2')
assert modal['hd']['Painted']==0,'檔案選單仍被地景覆繪'
restored,_=action('file-cancel','Escape')
assert restored['hd']['Painted']>0,'取消檔案選單後未恢復地景'
reads=len(restored['key_reads']);native,_=action('theme-original','F12')
assert native['hd']['Painted']==0 and len(native['key_reads'])==reads
hd,_=action('theme-hd','F12')
assert hd['hd']['Painted']>0 and len(hd['key_reads'])==reads
(out/'stop').write_text('stop\n')
result={'cold_start':True,'checkpoint':False,'window_input':True,'map_scroll_requested':True,
    'modal_fallback':True,'modal_return':True,'theme_switch_dos_unchanged':True,
    'native_exit':False,'formal_hd':False,
    'scope':'既有 DRAFT 地景原型的正常鍵盤捲動與選單恢復；實際捲動由獨立畫面比對另驗'}
(out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('cold GUI scroll capture completed',flush=True)
