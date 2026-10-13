#!/usr/bin/env python3
"""#56: normalize reviewed B illustrations once, preserving the 4x4 atlas seams."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import zipfile

from hd_file_dialogs_check import rgba
from infrastructure_prototype import png
from infrastructure_catalog import sources, sha, ROM_SHA
from hd_source_audit import cell

GENERATED = {
    34: 'd78aa437d01672c90d707377065302ef3e628a500631e38bb5a05803ece8d65d',
    35: '755deffd3c801f17cd7f6d1f66377f1d95283c8cffc36d9b4e7a4e27986a6ccb',
    36: '79e6ac2fb736c8f481a8068659158de31f81f98d2641e670fb5448f64a87512c',
}
SOURCE_SHA = '764054313fa809c6ab1e686a325751eb5fade49ada81fd99fabd569f6cac6272'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--original', type=Path, required=True)
    ap.add_argument('--inputs', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--stage', choices=['DRAFT', 'disaster48'], default='DRAFT')
    args = ap.parse_args()
    assert not args.out.exists() and args.out.parent.stat().st_uid == os.getuid()
    raw = (args.inputs/'sources.json').read_bytes()
    assert sha(raw) == SOURCE_SHA
    proof = json.loads(raw)
    rom = (args.original/'RS201.ROM').read_bytes()
    assert sha(rom) == ROM_SHA
    aliases = sources(rom)
    receipt = Path(proof['receipt'])
    assert sha(receipt.read_bytes()) == proof['receipt_sha256']
    with zipfile.ZipFile(receipt) as z:
        frame = z.read('frame-index.bin')
        base = z.read('presentation.png')
    assert sha(frame) == proof['frame_index_sha256']
    args.out.mkdir()
    records, palette, fragments, atlases = [], {}, {}, {}
    for building in proof['buildings']:
        member = building['member']
        generated = args.inputs/f'{member}-generated.png'
        assert sha(generated.read_bytes()) == GENERATED[member]
        atlas = subprocess.run(['convert', str(generated), '-filter', 'Lanczos', '-resize', '144x144!',
                                '-depth', '8', 'rgba:-'], check=True, stdout=subprocess.PIPE).stdout
        assert len(atlas) == 144*144*4 and set(atlas[3::4]) == {255}
        encoded = png(atlas, 144, 144)
        (args.out/f'{member}.png').write_bytes(encoded)
        atlases[str(member)] = {'file': f'{member}.png', 'sha256': sha(encoded),
                                 'rgba_sha256': sha(atlas), 'generated_sha256': GENERATED[member]}
        palette.update(building['used_palette'])
        native = bytearray(144*144*4)
        for tile in building['tiles']:
            col, row = tile['cell']
            source = next(raw for raw in aliases if sha(raw) == tile['source_sha256'])
            assert aliases[source] == tile['sources']
            fragment = b''.join(atlas[((row*36+y)*144+col*36)*4:((row*36+y)*144+col*36+36)*4] for y in range(36))
            assert source not in fragments
            fragments[source] = fragment
            records.append(tile)
            for y in range(36):
                for x in range(36):
                    at = ((row*36+y)*144+col*36+x)*4
                    native[at:at+4] = bytes(building['used_palette'][str(source[(y//4)*9+x//4])]+[255])
        if args.stage == 'DRAFT':
            comparison = b''.join(native[y*576:(y+1)*576]+atlas[y*576:(y+1)*576] for y in range(144))
            (args.out/f'{member}-comparison.png').write_bytes(png(comparison, 288, 144))
    if args.stage == 'DRAFT':
        # Technical atlas assembly on the frozen pre-task GUI frame, not new game art.
        base_path = args.out/'base.png'
        base_path.write_bytes(base)
        shown = bytearray(rgba(base_path, (1280, 800)))
        for row in range(15):
            for col in range(29):
                fragment = fragments.get(cell(frame, 5+col*9, 34+row*9))
                if fragment is None:
                    continue
                for y in range(36):
                    at = ((136+row*36+y)*1280+20+col*36)*4
                    shown[at:at+144] = fragment[y*144:(y+1)*144]
        (args.out/'city-candidate.png').write_bytes(png(shown, 1280, 800))
    manifest = {'schema': 1, 'stage': args.stage, 'issue': 56, 'rom_sha256': ROM_SHA,
                'atlas_size': [144, 144], 'source_proof_sha256': SOURCE_SHA,
                'image_processing': 'ImageMagick 6.9.11 Lanczos 1254->144, RGBA8; fixed standard-library PNG',
                'palette': palette, 'atlases': atlases, 'sources': records}
    (args.out/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    print('48 tiles; manifest SHA-256', sha((args.out/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
