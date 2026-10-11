"""#46：正常電線施工後接火力施工、切換、捲動及冷讀核對。"""
import json
import os
import zipfile
from pathlib import Path

os.environ.setdefault('TAIPEI_CITY_MENU_RUN',os.environ['TAIPEI_GUI_RUN'])
import city_menu_playtest as base
from infrastructure_playtest import key
from hd_source_audit import cell,MATERIAL,sha
from footer_catalog import source,decode


def model(root):
    with zipfile.ZipFile(root/'capture.zip') as z:
        s,frame=json.loads(z.read('status.json')),z.read('frame-index.bin')
    assert sha(frame)==s['frame_index_sha256']
    return s,frame


def exercise(root):
    base.out=root
    initial,_=model(root)
    origin=initial['map_origin']
    assert origin=={'X':12,'Y':12,'Valid':True}
    assert initial['hd']['infrastructure']['painted']>0
    cursor=[26,1]
    def walk(label,target):
        for axis,values in [(0,('Left','Right')),(1,('Up','Down'))]:
            while cursor[axis]!=target[axis]:
                delta=1 if cursor[axis]<target[axis] else -1
                key(f'power-{label}-{axis}-{cursor[axis]}',values[delta>0])
                cursor[axis]+=delta
    walk('prepare',(16,1))
    key('power-toolbar','Tab')
    for row in range(5):key(f'power-select-row-{row}','Down')
    key('power-submenu','space')
    choices={r['source_sha256']:r['selection'] for r in json.loads(Path(
        '/workspace/prototypes/hd-style/tool-menus-v1/manifest.json').read_text())['states'] if r['id']=='tool-11'}
    _,frame=model(root)
    menu=b''.join(frame[y*320+196:y*320+265] for y in range(124,159))
    selected=choices.get(sha(menu))
    assert selected in (0,1)
    if selected:key('power-thermal-select','Down')
    key('power-confirm','space')
    _,frame=model(root)
    for row in range(3,9):
        for col in range(22,28):
            assert set(cell(frame,5+col*9,34+row*9))<=MATERIAL
    walk('target',(22,3))
    key('power-build','space')
    walk('uncover',(16,3))
    base.capture('power-complete')
    built,frame=model(root)
    assert built['map_origin']==origin and built['hd']['power_facility']['painted']==36
    funds=decode(frame,source(Path('/orig/RS201.ROM').read_bytes()),1)[2]
    assert int(funds)==29980
    cells=[{'world':[origin['X']+col,origin['Y']+row],
        'source_sha256':sha(cell(frame,5+col*9,34+row*9))} for row in range(3,9) for col in range(22,28)]
    def same_world_sources(s,current):
        for record in cells:
            col=record['world'][0]-s['map_origin']['X']
            row=record['world'][1]-s['map_origin']['Y']
            assert 0<=col<29 and 0<=row<15
            assert sha(cell(current,5+col*9,34+row*9))==record['source_sha256']
    cursor_rect=[149,61,54,54]
    def stable_outside_cursor(a,b):
        for y in range(200):
            if 61<=y<115:
                assert a[y*320:y*320+149]==b[y*320:y*320+149]
                assert a[y*320+203:(y+1)*320]==b[y*320+203:(y+1)*320]
            else:assert a[y*320:(y+1)*320]==b[y*320:(y+1)*320]
    idle=[]
    # 原版無呈現重播已重現 r1 的游標差異；不假設固定閃爍週期。
    for sample in range(1):
        step=base.status()['steps']
        base.wait_for(lambda s:s.get('steps',0)>=step+24_000_000,f'power-cursor-idle-{sample}')
        s,current=model(root)
        assert s['key_reads']==built['key_reads']
        assert s['inputs']==built['inputs']
        stable_outside_cursor(frame,current)
        same_world_sources(s,current)
        base.capture(f'power-cursor-idle-{sample}')
        idle.append({'steps':s['steps'],'cursor_changed':current!=frame,'outside_cursor_equal':True})
    toggles=[]
    for name,enabled in [('original',False),('hd',True)]:
        base.action('power-theme-'+name,'F12')
        s,current=model(root)
        stable_outside_cursor(frame,current)
        assert s['key_reads']==built['key_reads']
        assert [i for i in s['inputs'] if i['kind']!='theme']==[i for i in built['inputs'] if i['kind']!='theme']
        assert s['hd_enabled'] is enabled and s['hd']['power_facility']['painted']==(36 if enabled else 0)
        same_world_sources(s,current)
        toggles.append({'enabled':enabled,'original_outside_cursor_unchanged':True,'no_dos_keyboard':True,'only_theme_input':True})
    # 改回已查證的單格電線游標，再走正常邊界捲動。
    key('power-small-cursor-toolbar','Tab')
    for row in range(5):key(f'power-small-cursor-row-{row}','Up')
    key('power-small-cursor-confirm','space')
    scrolls=[]
    for axis,direction,limit in [('X','Right',16),('Y','Down',16)]:
        before,_=model(root)
        base.capture('power-scroll-'+axis+'-before')
        for i in range(limit):
            key(f'power-scroll-{axis}-{i}',direction)
            after,current=model(root)
            if after['map_origin'][axis]!=before['map_origin'][axis]:break
        else:raise AssertionError(('正常捲動未發生',axis))
        assert after['map_origin'][axis]==before['map_origin'][axis]+2
        assert after['map_origin']['Y' if axis=='X' else 'X']==before['map_origin']['Y' if axis=='X' else 'X']
        assert after['hd']['power_facility']['painted']==36
        same_world_sources(after,current)
        base.capture('power-scroll-'+axis+'-after')
        scrolls.append({'axis':axis,'before':before['map_origin'],'after':after['map_origin'],'keys':i+1})
    for axis,direction,limit in [('Y','Up',18),('X','Left',32)]:
        for i in range(limit):
            s,_=model(root)
            if s['map_origin'][axis]==origin[axis]:break
            assert s['map_origin'][axis]==origin[axis]+2
            key(f'power-return-{axis}-{i}',direction)
        else:raise AssertionError(('未返回原點',axis))
    final,current=model(root)
    assert final['map_origin']==origin and final['hd']['power_facility']['painted']==36
    same_world_sources(final,current)
    base.capture('power-before-save')
    result={'issue':46,'normal_gui':True,'checkpoint':False,'cells':cells,'funds':int(funds),
        'f12':toggles,'cursor_rect':cursor_rect,'cursor_idle_control':idle,'scrolls':scrolls,'final_origin':final['map_origin'],
        'scope':'正常火力施工與捲動；完整像素、原版狀態及存退讀由獨立核對'}
    (root/'power-gui.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result


def check_reload(root,first):
    s,frame=model(root)
    original=json.loads((first/'power-gui.json').read_text())
    origin=s['map_origin']
    assert origin['Valid'] and s['hd']['power_facility']['painted']==36
    for record in original['cells']:
        col,row=record['world'][0]-origin['X'],record['world'][1]-origin['Y']
        assert 0<=col<29 and 0<=row<15
        assert sha(cell(frame,5+col*9,34+row*9))==record['source_sha256']
    assert int(decode(frame,source(Path('/orig/RS201.ROM').read_bytes()),1)[2])==original['funds']
    (root/'power-reload.json').write_text(json.dumps({'issue':46,'normal_gui':True,
        'complete_original_cells_equal':36,'funds':original['funds'],'painted':36},ensure_ascii=False,indent=2)+'\n')
