"""#46：正常施工火力／核能電廠，保留完整來源與未知格。"""
import hashlib
import json
import os
import subprocess
import tempfile
import zipfile
from pathlib import Path

import city_menu_playtest as base
from hd_source_audit import MATERIAL,cell,scene,sha
from infrastructure_catalog import sources


def main():
    out=base.root
    case=os.environ.get('TAIPEI_POWER_FACILITY_CASE','thermal')
    assert case in ('thermal','nuclear')
    aliases=sources(Path('/orig/RS201.ROM').read_bytes())
    choices={s['source_sha256']:s['selection'] for s in json.loads(
        Path('/workspace/prototypes/hd-style/tool-menus-v1/manifest.json').read_text())['states']
        if s['id']=='tool-11'}
    assert len(choices)==2
    actions=[]
    patterns=[]
    cursor=[0,0]

    def model():
        with zipfile.ZipFile(out/'capture.zip') as z:
            status,frame=json.loads(z.read('status.json')),z.read('frame-index.bin')
        assert sha(frame)==status['frame_index_sha256']
        return status,frame

    def key(label,value):
        before=base.status()
        if value=='Tab':
            reads=sum(k.get('Word')==0x0f09 for k in before.get('key_reads') or [])
            releases=sum(k.get('kind')=='keyboard' and k.get('scan')==0x8f for k in before.get('inputs',[]))
            subprocess.run(['xdotool','keydown','Tab'],check=True)
            try:
                base.wait_for(lambda s:sum(k.get('Word')==0x0f09 for k in s.get('key_reads') or [])>=reads+1,label+'-read')
            finally:subprocess.run(['xdotool','keyup','Tab'],check=True)
            base.wait_for(lambda s:sum(k.get('kind')=='keyboard' and k.get('scan')==0x8f for k in s.get('inputs',[]))>=releases+1,label+'-release')
            base.capture(label)
        else:base.action(label,value,acknowledge=True)
        after=base.status()
        assert len(after['key_reads'])==len(before['key_reads'])+1,(label,'原版未恰讀一次')
        actions.append({'label':label,'key':value,'steps':after['steps'],'original_read':after['key_reads'][-1]})

    def walk(label,target):
        for axis,keys in [(0,('Left','Right')),(1,('Up','Down'))]:
            while cursor[axis]!=target[axis]:
                direction=1 if cursor[axis]<target[axis] else -1
                key(f'{label}-{axis}-{cursor[axis]}',keys[direction>0])
                cursor[axis]+=direction

    def select(label,wanted):
        key(label+'-submenu','space')
        def selection():
            status,frame=model()
            assert status['dos_blocked']
            source=b''.join(frame[y*320+196:y*320+265] for y in range(124,159))
            return choices.get(hashlib.sha256(source).hexdigest())
        current=selection()
        assert current in (0,1),(label,'不是 021 已確認完整電廠選單')
        if current!=wanted:key(label+'-choose','Down')
        assert selection()==wanted
        key(label+'-confirm','space')
        assert not base.status()['dos_blocked']

    def build(label,target,uncover):
        before,original=model()
        assert scene(before,original)
        base.capture(label+'-before')
        walk(label+'-target',target)
        key(label+'-place','space')
        walk(label+'-uncover',uncover)
        after,frame=model()
        assert scene(after,frame)
        assert before['map_origin']==after['map_origin'],'研究走位意外捲動，停止而不猜座標'
        base.capture(label+'-complete')
        changed=[]
        unknown=[]
        for row in range(15):
            for col in range(29):
                x,y=5+col*9,34+row*9
                old,new=cell(original,x,y),cell(frame,x,y)
                if old==new:continue
                record={'cell':[col,row],'native_xy':[x,y],'before_sha256':sha(old),'after_sha256':sha(new)}
                if new in aliases:
                    record['sources']=aliases[new]
                    record['terrain_only']=set(new)<=MATERIAL
                    changed.append(record)
                else:unknown.append(record)
        assert any(not r['terrain_only'] for r in changed),(label,'尚未看到完整已知非地景來源')
        patterns.append({'label':label,'choice':0 if label=='thermal' else 1,'target_key_position':target,
            'uncover_key_position':uncover,'origin':after['map_origin'],
            'before_receipt':label+'-before-capture.zip','receipt':label+'-complete-capture.zip',
            'known_changes':changed,'unknown_changes':unknown,'steps':after['steps']})

    saves=tempfile.mkdtemp(prefix='power-facility-saves.',dir='/workspace/runs')
    with (out/'app.log').open('w') as log:
        game=subprocess.Popen(['/workspace/runs/taipei-preview','-original','/orig','-saves',saves,
            '-receipts',str(out),'-mute','-steps-per-update','400000','-materials',
            '/workspace/prototypes/hd-style','-theme','original','-stop-file',str(out/'stop')],
            stdout=log,stderr=subprocess.STDOUT)
        try:
            base.cold_city()
            key('plant-column','Right')
            for row in range(5):key(f'plant-row-{row+1}','Down')
            select(case,0 if case=='thermal' else 1)
            # 首次原版實見電廠為 6×6；24 次 Right 會提早捲動。
            # 本批在已見完整陸地 (22..27,3..8) 施工，不變更原版邊界。
            build(case,(22,3),(16,3))
            (out/'result.json').write_text(json.dumps({'issue':46,'normal_gui':True,'checkpoint':False,
                'case':case,'patterns':patterns,'actions':actions,'arrow_acknowledgments':base.sync,
                'ordinary_acknowledgments':base.ordinary_sync,'save_dir':saves,
                'scope':'原版正常施工的完整來源研究；有界停止，非存退讀或原版退出驗收'},ensure_ascii=False,indent=2)+'\n')
        finally:
            if game.poll() is None:
                (out/'stop').write_text('stop\n')
                try:game.wait(timeout=10)
                except subprocess.TimeoutExpired:game.kill();game.wait()
            assert game.returncode==0,game.returncode


if __name__=='__main__':main()
