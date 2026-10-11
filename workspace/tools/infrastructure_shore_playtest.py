"""#44：只補正常電線岸邊來源，不重跑已完成道路／十字批次。"""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

import infrastructure_playtest as infra
from hd_source_audit import MATERIAL,cell
from infrastructure_catalog import sources

base=infra.base
out=base.root


def main():
    aliases=sources(Path('/orig/RS201.ROM').read_bytes())
    saves=tempfile.mkdtemp(prefix='infrastructure-shore-saves.',dir='/workspace/runs')
    with (out/'app.log').open('w') as log:
        game=subprocess.Popen(['/workspace/runs/taipei-preview','-original','/orig','-saves',saves,
            '-receipts',str(out),'-mute','-steps-per-update','400000','-materials','/workspace/prototypes/hd-style',
            '-theme','original','-stop-file',str(out/'stop')],stdout=log,stderr=subprocess.STDOUT)
        try:
            base.cold_city()
            before=infra.frame()
            # 原岸邊探針已證實 (23,10) 為陸地，向左延伸至 (19,10)。
            # 新一次仍核對實際底圖，不能因前件相同就跳過。
            start=cell(before,5+23*9,34+10*9)
            assert set(start)<=MATERIAL and not set(start)&set(range(144,148))
            base.capture('shore-before')
            infra.key('power-column','Right')
            infra.key('power-confirm','space')
            for col in range(23):infra.key(f'shore-right-{col}','Right')
            for row in range(10):infra.key(f'shore-down-{row}','Down')
            for col in range(23,18,-1):
                if col!=23:infra.key(f'shore-left-{col}','Left')
                infra.key(f'shore-place-{col}','space')
            # 兩列距離避開原生游標及邊框，不捲動。
            infra.key('shore-uncover-1','Down')
            infra.key('shore-uncover-2','Down')
            base.capture('shore-complete')
            after=infra.frame()
            cells=[]
            for col in range(23,18,-1):
                old,new=cell(before,5+col*9,124),cell(after,5+col*9,124)
                assert old in aliases and new in aliases,(col,'岸邊不是完整來源，停止研究')
                cells.append({'cell':[col,10],'before_sha256':hashlib.sha256(old).hexdigest(),
                    'after_sha256':hashlib.sha256(new).hexdigest(),'changed':old!=new,
                    'before_sources':aliases[old],'after_sources':aliases[new]})
            (out/'result.json').write_text(json.dumps({'normal_gui':True,'checkpoint':False,'cells':cells,
                'actions':infra.actions,'arrow_acknowledgments':base.sync,'ordinary_acknowledgments':base.ordinary_sync,
                'save_dir':saves,'scope':'只補電線岸邊正常來源，原版拒絕施工亦照實記錄；研究停止不代替存退讀'},ensure_ascii=False,indent=2)+'\n')
        finally:
            if game.poll() is None:
                (out/'stop').write_text('stop\n')
                try:game.wait(timeout=10)
                except subprocess.TimeoutExpired:game.kill();game.wait()
            assert game.returncode==0,game.returncode


if __name__=='__main__':main()
