"""#48／029 READY：只匯出已獨立審查的固定框架及資料筆觸。"""
import argparse
import json
import os
import subprocess
from pathlib import Path

from full_asset_catalog import sha
from hd_file_dialogs_check import rgba


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--materials', type=Path, required=True)
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    assert not args.out.exists() and args.out.parent.stat().st_uid == os.getuid()
    proof = json.loads((args.source/'prototype-check-v2.json').read_bytes())
    repro = json.loads((args.source/'prototype-repro-v2.json').read_bytes())
    assert proof['issue'] == 48 and proof['all_pixels_independently_equal']
    assert proof['data_positions_and_source_colors_preserved'] and proof['generated_data_pixels_accepted'] == 0
    assert repro['byte_equal'] and len(repro['files']) == 42
    for name, expected in repro['files'].items():
        assert sha((args.materials/'chart-windows-v2'/name).read_bytes()) == expected
    raw = (args.source/'source-all-r3.json').read_bytes()
    assert sha(raw) == 'e252c062e832405d3d4a0c65ffbb7a7e694c3c76982b2b366d54b5f12d578f92'
    source = json.loads(raw)
    pal_raw = (args.source/'palette-audit-r1.json').read_bytes()
    assert sha(pal_raw) == '392dc069f4c39632d14c3991c7f2b0e4f11e5dcf6084b397b744f39caad17473'
    palettes = json.loads(pal_raw)
    assert palettes['used_changed'] == [] and len(palettes['palettes']) == 2
    meta = json.loads((args.materials/'chart-windows-v2/0/manifest.json').read_bytes())
    assert proof['charts'][0]['manifest_sha256'] == sha((args.materials/'chart-windows-v2/0/manifest.json').read_bytes())
    complete = rgba(args.materials/'chart-windows-v2/0/presentation.png', (1280,800))
    frame = bytearray(b''.join(complete[((140+y)*1280+264)*4:((140+y)*1280+844)*4] for y in range(508)))
    for y in range(80,436):
        frame[(y*580+80)*4:(y*580+500)*4] = bytes(420*4)
    assert sum(v == 0 for v in frame[3::4]) == 149520
    texture = rgba(args.materials/'city-chrome-gray-v1.png', (944,528))
    grain = bytes(texture[((32+y%464)*944+32+x%880)*4]//8-18+128
                  for y in range(508) for x in range(580))
    args.out.mkdir(mode=0o700)
    subprocess.run(['convert', '-size', '580x508', '-depth', '8', 'rgba:-', '-strip',
                    '-define', 'png:exclude-chunks=date,time', 'PNG32:'+str(args.out/'frame.png')],
                   input=bytes(frame), check=True)
    assert rgba(args.out/'frame.png',(580,508)) == frame
    (args.out/'grain.bin').write_bytes(grain)
    manifest = {'schema':1,'issue':48,'stage':'chart-windows','spec':'029-chart-windows',
        'rom_sha256':source['rom_sha256'],'native':source['native'],'data_local':source['data_local'],
        'source_member':source['members'][0], 'fixed_pixels':9070,'fixed_sha256':source['fixed_sha256'],
        'mode':19,'blocked':True,'palettes':palettes['palettes'],
        'source_check_sha256':sha(raw),'prototype_manifests':[r['manifest_sha256'] for r in proof['charts']],
        'prototype_check_sha256':sha((args.source/'prototype-check-v2.json').read_bytes()),
        'art_sha256':meta['frame_art_sha256'],'font_sha256':meta['font_sha256'],
        'license_sha256':meta['license_sha256'],'font_size':24,'labels':meta['labels'],
        'texture_sha256':meta['texture_sha256'],
        'images':{'frame.png':{'size':[580,508],'sha256':sha((args.out/'frame.png').read_bytes()),'rgba_sha256':sha(frame)}},
        'grain':{'bytes':len(grain),'sha256':sha(grain),'encoding':'red/8-18+128; row-major 580x508'},
        'rights':'原版衍生素材僅留本機；字型 SIL OFL 1.1；未授權公開發布',
        'scope':'固定框架及原版資料像素；不重寫或推定統計公式，未知框架／相位／色盤完整回退'}
    raw = (json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
    (args.out/'manifest.json').write_bytes(raw)
    print(json.dumps({'manifest_sha256':sha(raw),'frame_png_sha256':manifest['images']['frame.png']['sha256'],
        'frame_rgba_sha256':sha(frame),'grain_sha256':sha(grain),'fixed_sha256':source['fixed_sha256']}))


if __name__ == '__main__':
    main()
