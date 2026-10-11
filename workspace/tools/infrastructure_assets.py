"""#44／026：從已核對 v5 固定第一批 25 張的本機呈現資產。"""
import argparse
import hashlib
import json
import os
import struct
from pathlib import Path

ROM_SHA = '0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29'
PROTOTYPE_SHA = 'c9ea6457c10fc9dec5c755177e940eb0461e26282a74f5a58977456a2c90794c'
IMAGES = list(range(15,26))+list(range(27,30))+list(range(45,56))


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rom',type=Path,required=True)
    ap.add_argument('--prototype',type=Path,required=True)
    ap.add_argument('--catalog',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args = ap.parse_args()
    rom = args.rom.read_bytes()
    assert sha(rom)==ROM_SHA
    raw = (args.prototype/'manifest.json').read_bytes()
    assert sha(raw)==PROTOTYPE_SHA
    prototype = json.loads(raw)
    catalog = json.loads(args.catalog.read_bytes())
    assert prototype['geometry_version']==3 and prototype['asphalt_frequency']==4
    records = {r['image']:r for r in prototype['candidate_images']}
    off,n = struct.unpack_from('<IH',rom,18+39*16)
    lib = rom[off:off+n]
    assert struct.unpack_from('<H',lib)[0]==75 and len(lib)==6527
    assets,sources,colors = {},[],set()
    for index in IMAGES:
        start = struct.unpack_from('<H',lib,2+index*2)[0]
        end = struct.unpack_from('<H',lib,4+index*2)[0] if index<74 else len(lib)
        tile = lib[start:end]
        assert len(tile)==85 and tile[:4]==b'\x09\0\x09\0'
        pixels = tile[4:]
        source,record = catalog['target'][index],records[index]
        assert source['observed'] and source['pixels_hex']==pixels.hex()
        assert sha(pixels)==source['pixels_sha256']==record['source_sha256']
        assert source['aliases']==record['aliases']
        names = [f'39-{index:03d}-{suffix}.bin' for suffix in ['indices','weights']]
        for name,key in zip(names,['index_bytes','weight_bytes']):
            data = (args.prototype/name).read_bytes()
            assert len(data)==5184 and sha(data)==record[key]
            assets[name] = data
        assert all(sum(assets[names[1]][at:at+4])==255 for at in range(0,5184,4))
        assert all(w==0 or i in pixels for i,w in zip(assets[names[0]],assets[names[1]]))
        used = sorted(set(pixels))
        assert not {240,241}.intersection(used)
        colors.update(used)
        sources.append({'image':index,'source_sha256':sha(pixels),'aliases':source['aliases'],
            'indices_sha256':record['index_bytes'],'weights_sha256':record['weight_bytes'],
            'used_colors':used})
    manifest = {'schema':1,'stage':'normal25','rom_sha256':ROM_SHA,
        'geometry_version':3,'asphalt_frequency':4,'material_size':1254,
        'prototype_manifest_sha256':PROTOTYPE_SHA,'sources':sources,
        'palette':{str(i):catalog['palette'][i] for i in sorted(colors)},
        'materials':{k:v for k,v in prototype['materials'].items() if k!='water'},
        'shader':'integer per-mille; nearest-even /300; blend /255',
        'scope':'已見正常來源的 25 張；其他候選仍不進產品'}
    assert not args.out.exists() and args.out.parent.stat().st_uid==os.getuid()
    args.out.mkdir()
    for name,data in assets.items():
        (args.out/name).write_bytes(data)
    raw = (json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode()
    (args.out/'manifest.json').write_bytes(raw)
    print(json.dumps({'sources':len(sources),'files':len(assets)+1,
        'manifest_sha256':sha(raw),'used_colors':sorted(colors)},ensure_ascii=False))


if __name__=='__main__':
    main()
