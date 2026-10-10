#!/usr/bin/env python3
"""原版操作診斷，從檢查點續跑，只產生探索收據。"""
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

out=Path('/workspace/runs/gui-explore')
end=time.monotonic()+30
while not (out/'status.json').exists():
    if time.monotonic()>end:
        raise RuntimeError('diagnostic GUI startup timeout')
    time.sleep(.1)
subprocess.run(['xdotool','search','--name','模擬台北','windowfocus'],check=True)
actions=[('file-menu','F2'),('save-dialog','space'),('save-name','type:taipei'),('save-accept','space')]
if os.environ.get('TAIPEI_ACTIONS'):
    actions=[tuple(item.split(':',1)) for item in os.environ['TAIPEI_ACTIONS'].split(',')]
for name,key in actions:
    if key.startswith('type:'):
        subprocess.run(['xdotool','type','--delay','150',key[5:]],check=True)
    else:
        subprocess.run(['xdotool','keydown',key],check=True)
        time.sleep(.15)
        subprocess.run(['xdotool','keyup',key],check=True)
    time.sleep(3)
    for ext in ['frame.png','status.json']:
        shutil.copyfile(out/ext,out/(name+'-'+ext))
(out/'stop').write_text('stop\n')
