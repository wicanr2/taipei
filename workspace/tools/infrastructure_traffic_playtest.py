"""#44：正常災難城市恢復模擬，觀察完整道路圖像的實際相位。"""
import json
import os
import subprocess
import tempfile
import zipfile
from pathlib import Path

import city_menu_playtest as base
from hd_source_audit import cell,scene,sha
from infrastructure_prototype_check import read_sources


def main():
    root = base.root
    mode = os.environ.get('TAIPEI_TRAFFIC_MODE','running')
    assert mode in ('running','density')
    assert not (root/'result.json').exists()
    tiles,_ = read_sources(Path('/orig/RS201.ROM').read_bytes())
    images = {source:i for i,source in tiles.items()}
    def model():
        with zipfile.ZipFile(root/'capture.zip') as z:
            s,frame = json.loads(z.read('status.json')),z.read('frame-index.bin')
        assert sha(frame)==s['frame_index_sha256']
        return s,frame
    def key(label,value):
        before = base.status()
        base.action(label,value,acknowledge=True)
        assert len(base.status()['key_reads'])==len(before['key_reads'])+1
    saves = tempfile.mkdtemp(prefix='infrastructure-traffic-saves.',dir='/workspace/runs')
    with (root/'app.log').open('w') as log:
        game = subprocess.Popen(['/workspace/runs/taipei-preview','-original','/orig','-saves',saves,
            '-receipts',str(root),'-mute','-steps-per-update','400000','-materials',
            '/workspace/prototypes/hd-style','-theme','original','-stop-file',str(root/'stop')],
            stdout=log,stderr=subprocess.STDOUT)
        try:
            base.wait_for(lambda s:s.get('steps',0)>=700_000_000,'intro',progress=True)
            subprocess.run(['xdotool','search','--name','模擬台北','windowfocus'],check=True)
            base.action('intro-space','space')
            base.wait_for(lambda s:s.get('steps',0)>=800_000_000,'intro-wait')
            base.action('main','space')
            base.wait_for(lambda s:s.get('frame_index_sha256')=='5442a8135d36552561f03a46fc443978a76989979e0c25dc016027229b24dda4','main-ready')
            key('scenario-choice','Right')
            key('scenario-open','space')
            for i,value in enumerate(['space','space','space','0']):key(f'scenario-step-{i}',value)
            paused,frame = model()
            assert scene(paused,frame) and any(f.get('Name','').lower()=='disa1.dsa' and f.get('Op')=='read' for f in paused['file_ops'])
            base.capture('traffic-paused')
            if mode=='density':
                key('traffic-menu','F4')
                key('traffic-density-select','Down')
                key('traffic-density-open','space')
            else:key('traffic-resume','1')
            samples = []
            observed = set()
            for i in range(8 if mode=='density' else 30):
                before = base.status()['steps']
                base.wait_for(lambda s:s.get('steps',0)>=before+24_000_000,f'traffic-{i:02d}')
                s,frame = model()
                label = f'traffic-{i:02d}'
                base.capture(label)
                current = []
                if s['mode']==19 and not s['dos_blocked'] and s['map_origin']['Valid']:
                    for row in range(15):
                        for col in range(29):
                            source = cell(frame,5+col*9,34+row*9)
                            if source in images:
                                current.append({'cell':[col,row],'image':images[source],'source_sha256':sha(source)})
                                observed.add(images[source])
                samples.append({'receipt':label+'-capture.zip','steps':s['steps'],'scene_valid':scene(s,frame),
                    'origin':s['map_origin'],'member39':current})
                # 已知年度視窗只記錄；不把模態畫面當作交通相位。
            (root/'result.json').write_text(json.dumps({'normal_gui':True,'checkpoint':False,
                'mode':mode,'observed_member39':sorted(observed),'samples':samples,
                'ordinary_acknowledgments':base.ordinary_sync,'arrow_acknowledgments':base.sync,
                'scope':'正常災難城市恢復或 F4 交通密度入口的來源研究；有界停止，非正常退出或交通 HD 驗收'},ensure_ascii=False,indent=2)+'\n')
        finally:
            if game.poll() is None:
                (root/'stop').write_text('stop\n')
                try:game.wait(timeout=10)
                except subprocess.TimeoutExpired:game.kill();game.wait()
            assert game.returncode==0,game.returncode


if __name__=='__main__':
    main()
