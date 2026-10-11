"""#44：正常道路與電線十字施工來源，不注入城市或座標。"""
import hashlib
import json
import os
import subprocess
import tempfile
import zipfile
from pathlib import Path

import city_menu_playtest as base
from hd_source_audit import cell, MATERIAL
from infrastructure_catalog import sources

out = base.root
base.out = out
actions = []


def frame():
    with zipfile.ZipFile(out/'capture.zip') as z:
        return z.read('frame-index.bin')


def key(label,value):
    before = base.status()
    if value == 'Tab':
        # 004 已證實 0F09h；與既有工具子選單探針的 Tab 同步相同。
        reads = sum(k.get('Word') == 0x0f09 for k in before.get('key_reads') or [])
        breaks = sum(k.get('kind') == 'keyboard' and k.get('scan') == 0x8f for k in before.get('inputs',[]))
        subprocess.run(['xdotool','keydown','Tab'],check=True)
        try:
            base.wait_for(lambda s:sum(k.get('Word') == 0x0f09 for k in s.get('key_reads') or []) >= reads+1,label+'-read')
        finally:
            subprocess.run(['xdotool','keyup','Tab'],check=True)
        base.wait_for(lambda s:sum(k.get('kind') == 'keyboard' and k.get('scan') == 0x8f for k in s.get('inputs',[])) >= breaks+1,label+'-release')
        base.capture(label)
    else:
        base.action(label,value,acknowledge=True)
    after = base.status()
    assert len(after['key_reads']) == len(before['key_reads'])+1,(label,'按鍵未恰讀一次')
    actions.append({'label':label,'key':value,'steps':after['steps'],'original_read':after['key_reads'][-1]})


def dry_center(prefer):
    pixels = frame()
    candidates = []
    for row in range(2,13):
        # 移開游標還需向右三格；停在 28 以內，避免意外捲動。
        for col in range(2,26):
            if all(set(cell(pixels,5+(col+dx)*9,34+(row+dy)*9)) <= MATERIAL
                and not set(cell(pixels,5+(col+dx)*9,34+(row+dy)*9)) & set(range(144,148))
                for dy in range(-2,3) for dx in range(-2,3)):
                candidates.append((col,row))
    assert candidates,'沒有完整可見的 5×5 已知陸地，停止研究，不猜底圖'
    return min(candidates,key=lambda p:abs(p[0]-prefer[0])+abs(p[1]-prefer[1]))


def main():
    rom = Path('/orig/RS201.ROM').read_bytes()
    aliases = sources(rom)
    saves = tempfile.mkdtemp(prefix='infrastructure-saves.',dir='/workspace/runs')
    patterns = []
    variants = []
    with (out/'app.log').open('w') as log:
        game = subprocess.Popen(['/workspace/runs/taipei-preview','-original','/orig','-saves',saves,
            '-receipts',str(out),'-mute','-steps-per-update','400000','-materials','/workspace/prototypes/hd-style',
            '-theme','original','-stop-file',str(out/'stop')],stdout=log,stderr=subprocess.STDOUT)
        try:
            base.cold_city()
            key('road-tool','Down')
            key('road-submenu','space')
            manifest = json.loads(Path('/workspace/prototypes/hd-style/tool-menus-v1/manifest.json').read_text())
            choices = {s['source_sha256']:s['selection'] for s in manifest['states'] if s['id']=='tool-02'}
            def selection():
                return choices.get(hashlib.sha256(b''.join(frame()[y*320+228:y*320+265] for y in range(29,64))).hexdigest())
            assert selection() in (0,1),'未抵達已證實的公路／捷運子選單'
            if selection() != 0:key('choose-road','Down')
            assert selection()==0
            key('road-confirm','space')
            cursor = [0,0]
            def walk(label,position):
                for axis,values in [(0,('Left','Right')),(1,('Up','Down'))]:
                    while cursor[axis] != position[axis]:
                        direction = 1 if cursor[axis] < position[axis] else -1
                        key(f'{label}-{axis}-{cursor[axis]}',values[direction>0])
                        cursor[axis] += direction
            def cross(label,center):
                before = frame()
                locations = [(0,0),(1,0),(2,0),(-1,0),(-2,0),(0,1),(0,2),(0,-1),(0,-2)]
                for i,(dx,dy) in enumerate(locations):
                    position = (center[0]+dx,center[1]+dy)
                    walk(f'{label}-move-{i}',position)
                    key(f'{label}-place-{i}','space')
                walk(label+'-uncover',(center[0]+3,center[1]-2))
                after = frame()
                cells = []
                for dx,dy in locations:
                    x,y = 5+(center[0]+dx)*9,34+(center[1]+dy)*9
                    old,new = cell(before,x,y),cell(after,x,y)
                    assert old != new and new in aliases,(label,x,y,'施工未形成完整已知圖塊')
                    cells.append({'native_xy':[x,y],'before_sha256':hashlib.sha256(old).hexdigest(),
                        'after_sha256':hashlib.sha256(new).hexdigest(),'sources':aliases[new]})
                patterns.append({'tool':label,'center_cell':center,'cells':cells,'receipt':label+'-complete-capture.zip'})
                base.capture(label+'-complete')
            def patch(label,locations,uncover):
                before = frame()
                for i,position in enumerate(locations):
                    walk(f'{label}-move-{i}',position)
                    key(f'{label}-place-{i}','space')
                walk(label+'-uncover',uncover)
                after = frame()
                cells = []
                for col,row in locations:
                    x,y = 5+col*9,34+row*9
                    old,new = cell(before,x,y),cell(after,x,y)
                    assert new in aliases,(label,x,y,'操作後不是完整已知來源，停止研究')
                    cells.append({'cell':[col,row],'before_sha256':hashlib.sha256(old).hexdigest(),
                        'after_sha256':hashlib.sha256(new).hexdigest(),'changed':old!=new,'sources':aliases[new]})
                # 水面操作可能被原版拒絕，照實記錄；不把按鍵視為施工成功。
                variants.append({'label':label,'cells':cells,'receipt':label+'-complete-capture.zip'})
                base.capture(label+'-complete')
            road_center = dry_center((24,5))
            cross('road',road_center)
            if os.environ.get('TAIPEI_INFRASTRUCTURE_VARIANTS') == '1':
                x,y = road_center
                patch('road-corners',[(x-1,y-1),(x+1,y-1),(x+1,y+1),(x-1,y+1)],(x+3,y-2))
                patch('road-shore',[(x-d,y) for d in range(3,9)],(x+3,y-2))
            key('power-toolbar','Tab')
            key('power-row','Up')
            key('power-column','Right')
            key('power-confirm','space')
            power_center = dry_center((road_center[0]-6,road_center[1]+4))
            cross('power',power_center)
            if os.environ.get('TAIPEI_INFRASTRUCTURE_VARIANTS') == '1':
                x,y = power_center
                patch('power-corners',[(x-1,y-1),(x+1,y-1),(x+1,y+1),(x-1,y+1)],(x+3,y-2))
                rx,ry = road_center
                patch('power-road',[(rx+d,ry-1) for d in range(-2,3)],(rx+3,ry-2))
                patch('power-shore',[(x-d,y) for d in range(3,7)],(x+3,y-2))
            (out/'result.json').write_text(json.dumps({'normal_gui':True,'checkpoint':False,'patterns':patterns,
                'variants':variants,
                'actions':actions,'arrow_acknowledgments':base.sync,'ordinary_acknowledgments':base.ordinary_sync,
                'save_dir':saves,'scope':'正常施工來源；有界研究停止，不當作存退讀或原版退出'},ensure_ascii=False,indent=2)+'\n')
        finally:
            if game.poll() is None:
                (out/'stop').write_text('stop\n')
                try:game.wait(timeout=10)
                except subprocess.TimeoutExpired:game.kill();game.wait()
            assert game.returncode == 0,game.returncode


if __name__=='__main__':
    main()
