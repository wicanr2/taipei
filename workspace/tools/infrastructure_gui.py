"""#44：接在正常施工／存退讀流程中的道路、切換與雙向捲動。"""
import hashlib
import json
import os
import zipfile
from pathlib import Path

os.environ.setdefault('TAIPEI_CITY_MENU_RUN',os.environ['TAIPEI_GUI_RUN'])
import city_menu_playtest as base
from infrastructure_playtest import key
from hd_source_audit import cell,MATERIAL


def exercise(root):
    base.out = root
    def model():
        with zipfile.ZipFile(root/'capture.zip') as z:
            s,frame = json.loads(z.read('status.json')),z.read('frame-index.bin')
        assert hashlib.sha256(frame).hexdigest()==s['frame_index_sha256']
        return s,frame
    initial,_ = model()
    origin = initial['map_origin']
    assert origin=={'X':12,'Y':12,'Valid':True}
    assert initial['hd']['infrastructure']['painted']>0,'前段正常電線未接高清'
    # 前段已完成正常電線施工，游標在 (26,1)，工具列選電線。
    for label,value in [('toolbar','Tab'),('first-tool','Left'),('road-row','Down'),
                        ('road-menu','space'),('road-confirm','space')]:
        key('infrastructure-'+label,value)
    cursor = [26,1]
    def walk(label,target):
        for axis,values in [(0,('Left','Right')),(1,('Up','Down'))]:
            while cursor[axis]!=target[axis]:
                delta = 1 if cursor[axis]<target[axis] else -1
                key(f'infrastructure-{label}-{axis}-{cursor[axis]}',values[delta>0])
                cursor[axis]+=delta
    _,before = model()
    positions = [(26,5),(25,5),(25,6),(24,6)]
    for col,row in positions:
        source = cell(before,5+col*9,34+row*9)
        assert set(source)<=MATERIAL and not set(source)&set(range(144,148)),'目標不是已確認陸地'
    for i,p in enumerate(positions):
        walk(f'road-move-{i}',p)
        key(f'infrastructure-road-build-{i}','space')
    walk('road-uncover',(26,4))
    base.capture('infrastructure-road-complete')
    built,frame = model()
    assert built['hd']['infrastructure']['painted']>=5
    toggles = []
    for suffix,enabled in [('original',False),('hd',True)]:
        base.action('infrastructure-road-theme-'+suffix,'F12')
        current,now = model()
        assert now==frame and current['key_reads']==built['key_reads']
        assert [i for i in current['inputs'] if i['kind']=='keyboard']==[i for i in built['inputs'] if i['kind']=='keyboard']
        assert current['hd_enabled'] is enabled
        assert current['hd']['infrastructure']['painted']==(built['hd']['infrastructure']['painted'] if enabled else 0)
        toggles.append({'theme':enabled,'original_frame_unchanged':True,'no_dos_keyboard':True})
    scrolls = []
    for axis,direction,bound in [('X','Right',10),('Y','Down',16)]:
        old,_ = model()
        base.capture('infrastructure-scroll-'+axis+'-before')
        for i in range(bound):
            key(f'infrastructure-scroll-{axis}-{i}',direction)
            current,_ = model()
            if current['map_origin']['Valid'] and current['map_origin'][axis]>old['map_origin'][axis]:
                break
        else:raise AssertionError(('正常捲動未達原點變更',axis))
        # 006 的原版 sub_1850A 每次捲動兩格。
        assert current['map_origin'][axis]==old['map_origin'][axis]+2
        other = 'Y' if axis=='X' else 'X'
        assert current['map_origin'][other]==old['map_origin'][other]
        assert current['hd']['infrastructure']['painted']>=4
        base.capture('infrastructure-scroll-'+axis+'-after')
        scrolls.append({'axis':axis,'before':old['map_origin'],'after':current['map_origin'],
            'keys':i+1,'normal_original_keys':True})
    # 原電線位於世界 y=13。垂直捲動後用正常 Up 回原視窗，讓存退讀可直接核對它。
    for i in range(17):
        current,_ = model()
        if current['map_origin']['Y']==origin['Y']:break
        assert current['map_origin']['Y']==origin['Y']+2
        key(f'infrastructure-return-up-{i}','Up')
    else:raise AssertionError('正常 Up 未返回原垂直視窗')
    base.capture('infrastructure-scroll-return')
    base.action('infrastructure-scrolled-theme-original','F12')
    assert not model()[0]['hd_enabled']
    base.action('infrastructure-scrolled-theme-hd','F12')
    final,_ = model()
    assert final['hd_enabled'] and final['hd']['infrastructure']['painted']>=5
    result = {'normal_gui':True,'checkpoint':False,'roads':positions,'f12':toggles,
        'scrolls':scrolls,'final_origin':final['map_origin'],
        'scope':'正常施工與捲動輸入；完整像素、同世界位置及存退讀由外部核對'}
    (root/'infrastructure-gui.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result
