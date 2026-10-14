#!/usr/bin/env python3
"""039：回核既有正常開場的原生PNG／色號／發布色盤，非新HD驗收。"""
import argparse
import json
from pathlib import Path
import struct
import subprocess
import zipfile

from full_asset_catalog import ROMS,sha


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();assert not a.out.exists()
    verified=json.loads((a.run/'opening-verification.json').read_text())
    assert verified['normal_gui'] and verified['checkpoint'] is False
    roms={name:Path('/orig',name).read_bytes() for name in ROMS}
    assert all(sha(raw)==ROMS[name][0] for name,raw in roms.items())
    raw=roms['RS201A.ROM'];off,size=struct.unpack_from('<IH',raw,18+3*16);assert size==768
    expand=lambda v:(v>>2)*4|((v>>2)>>4)
    expected=[list(map(expand,raw[off+i:off+i+3])) for i in range(0,768,3)]
    city=json.loads(Path('/workspace/prototypes/hd-style/map-completion-v1/inventory.json').read_text())['palette']
    city=[city[str(i)] for i in range(256)];records=[]
    for name in ['opening-startup.title','opening-art.department_store','opening-intro.traffic','opening-intro.medals']:
        path=a.run/'gui'/(name+'-capture.zip')
        with zipfile.ZipFile(path) as z:
            status=json.loads(z.read('status.json'));pixels=z.read('frame-index.bin');native=z.read('frame.png')
        assert status['original_sha256']=='798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3'
        assert len(pixels)==64000 and sha(pixels)==status['frame_index_sha256']
        palette=status['palette'];assert palette==expected
        decoded=subprocess.check_output(['convert','png:-','-depth','8','rgba:-'],input=native)
        rendered=b''.join(bytes(palette[value]+[255]) for value in pixels)
        assert decoded==rendered,'原生PNG與發布色盤／色號不一致'
        records.append({'capture':str(path.relative_to(a.run)),'capture_sha256':sha(path.read_bytes()),
            'steps':status['steps'],'frame_index_sha256':sha(pixels),'native_png_sha256':sha(native),
            'published_palette_sha256':sha(bytes(c for rgb in palette for c in rgb)),
            'normal_gui_source':True,'new_hd_test':False})
    result={'schema':1,'issue':32,'stage':'DRAFT','source_run':str(a.run),
        'opening_verification_sha256':sha((a.run/'opening-verification.json').read_bytes()),
        'records':records,'published_palette':'ROMA3 VGA6-bit展開',
        'city_to_roma3_differences':[{'index':i,'city':city[i],'roma3':expected[i]} for i in range(256) if city[i]!=expected[i]],
        'input_rom_sha256':{name:sha(raw) for name,raw in roms.items()},
        'tool_sha256':sha(Path(__file__).read_bytes()),'scope':'沿用033已驗正常原版畫面與色盤；非新HD、原版呼叫或平台驗收'}
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('PASS',len(records),'normal published palettes/native PNGs;',sha(a.out.read_bytes()))


if __name__=='__main__':main()
