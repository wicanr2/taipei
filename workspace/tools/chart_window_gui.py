"""#48：正常存退讀路徑內逐一開六圖表、F12、等待及返回。"""
import json
from pathlib import Path

import city_menu_playtest as base
from chart_window_playtest import model, key, return_chart, console_sync
from chart_window_source_check import crop, NATIVE, DATA
from full_asset_catalog import sha
from hd_source_audit import scene


def exercise(out):
    base.out = out
    raw = Path('/workspace/prototypes/hd-style/city-menu-sources-v1.json').read_bytes()
    assert sha(raw) == 'eb98c1def205eb39e533f9646ad9336fafc7268559998e93e3a1ed1c7157f870'
    sources = {s['source_sha256']:s['selection'] for s in json.loads(raw)['states'] if s['id']=='city-f4'}
    before, city = model()
    assert scene(before,city) and before['hd_enabled']
    records = []
    def selection():
        s, frame = model()
        value = sha(crop(frame,320,(141,35,68,94)))
        assert s['dos_blocked'] and value in sources
        return sources[value], value
    for target in range(6):
        prefix = f'chart-{target}'
        key(prefix+'-menu','F4')
        current, _ = selection()
        for step in range((target-current)%6):
            key(prefix+f'-select-{step}','Down')
            actual, _ = selection()
            assert actual == (current+1)%6
            current = actual
        actual, menu_sha = selection()
        assert actual == target
        base.capture(prefix+'-chosen')
        key(prefix+'-open','space')
        base.wait_for(lambda s:s['dos_blocked'],prefix+'-blocked')
        s, frame = model()
        assert s['mode']==19 and s['hd']['chart_window'] and s['hd']['chart_reason']=='matched-chart-window'
        data_sha = sha(crop(crop(frame,320,NATIVE),145,DATA))
        assert s['hd']['chart_data_sha256']==data_sha
        base.capture(prefix+'-blocked')
        for suffix,enabled in [('original',False),('hd',True)]:
            base.action(prefix+'-theme-'+suffix,'F12')
            after, pixels = model()
            assert after['hd_enabled'] is enabled and after['hd']['chart_window'] is enabled
            assert after['dos_blocked'] and pixels == frame and after['key_reads']==s['key_reads']
            assert [i for i in after['inputs'] if i['kind']!='theme'] == [i for i in s['inputs'] if i['kind']!='theme']
        for observation in range(2):
            start = base.status()['steps']
            base.wait_for(lambda s:s['steps']>=start+24_000_000,prefix+f'-observe-{observation}')
            after, pixels = model()
            assert after['hd']['chart_window'] and after['dos_blocked'] and pixels==frame
            base.capture(prefix+f'-observe-{observation}')
        return_chart(prefix+'-return')
        returned, pixels = model()
        assert scene(returned,pixels) and pixels==city and returned['map_origin']==before['map_origin']
        assert not returned['hd']['chart_window'] and returned['hd']['reason']=='matched-city'
        records.append({'selection':actual,'menu_source_sha256':menu_sha,'data_sha256':data_sha,
            'f12_roundtrip':True,'theme_only_input':True,'console_escape':True,'complete_city_restored':True})
    (out/'chart-gui.json').write_text(json.dumps({'issue':48,'normal_gui':True,'checkpoint':False,
        'charts':records,'console_acknowledgments':console_sync,
        'scope':'六個實際入口、F12、無輸入及返回；存退讀由外層正常路徑驗證'},
        ensure_ascii=False,indent=2)+'\n')
