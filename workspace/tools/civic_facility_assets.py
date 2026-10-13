#!/usr/bin/env python3
"""#57: resize whole reviewed paintings once, then assemble a shared 8x4 atlas."""
import argparse
import json
import os
from pathlib import Path
import subprocess

from infrastructure_catalog import sha, ROM_SHA, sources
from infrastructure_prototype import png

SOURCE_SHA = '212cb5c2c92fcfc36a254205586a38bb7e668dc8f3595a28e0ed0d770dbadc45'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--stage',choices=['DRAFT','civic32'],default='DRAFT')
    args = ap.parse_args()
    assert not args.out.exists() and args.out.parent.stat().st_uid == os.getuid()
    root = Path('/workspace/prototypes/hd-style/civic-facilities-v1')
    source = (root/'sources.json').read_bytes()
    assert sha(source) == SOURCE_SHA
    proof = json.loads(source)
    generated = json.loads((root/'generation.json').read_text())
    rom = Path('/orig/RS201.ROM').read_bytes()
    assert sha(rom) == ROM_SHA
    aliases = sources(rom)
    atlas, records, palette, art = bytearray(288*144*4), [], {}, {}
    args.out.mkdir()
    for number, building in enumerate(proof['buildings']):
        case = building['id']
        path = root/f'{case}-generated.png'
        assert sha(path.read_bytes()) == generated[case]['sha256']
        raw = subprocess.run(['convert',str(path),'-filter','Lanczos','-resize','144x144!',
                              '-depth','8','rgba:-'],check=True,stdout=subprocess.PIPE).stdout
        assert len(raw)==144*144*4 and set(raw[3::4]) == {255}
        art[case] = generated[case]
        native = bytearray(144*144*4)
        for tile in building['tiles']:
            x,y = tile['cell']
            pixels = next(k for k in aliases if sha(k)==tile['source_sha256'])
            assert aliases[pixels] == tile['sources']
            records.append(dict(tile,cell=[number*4+x,y]))
            for cy in range(36):
                for cx in range(36):
                    at = ((y*36+cy)*144+x*36+cx)*4
                    native[at:at+4]=bytes(building['used_palette'][str(pixels[(cy//4)*9+cx//4])]+[255])
        palette.update(building['used_palette'])
        for y in range(144):
            at=(y*288+number*144)*4
            atlas[at:at+576]=raw[y*576:(y+1)*576]
        if args.stage=='DRAFT':
            comparison=b''.join(native[y*576:(y+1)*576]+raw[y*576:(y+1)*576] for y in range(144))
            (args.out/f'{case}-comparison.png').write_bytes(png(comparison,288,144))
    encoded=png(atlas,288,144)
    (args.out/'37.png').write_bytes(encoded)
    manifest={'schema':1,'stage':args.stage,'issue':57,'rom_sha256':ROM_SHA,'atlas_size':[288,144],
              'source_proof_sha256':SOURCE_SHA,'image_processing':'ImageMagick 6.9.11 Lanczos 1254->144 RGBA8, then side-by-side; fixed PNG',
              'palette':palette,'atlases':{'37':{'file':'37.png','sha256':sha(encoded),'rgba_sha256':sha(atlas)}},
              'generated':art,'sources':records}
    (args.out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(args.stage,sha((args.out/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
