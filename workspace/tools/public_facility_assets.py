#!/usr/bin/env python3
"""#58: build independently sealed atlases from complete normal sources and B art."""
import argparse
import json
import os
from pathlib import Path
import subprocess

from infrastructure_catalog import sources, sha, ROM_SHA
from infrastructure_prototype import png


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--inputs',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--stage',choices=['DRAFT','public','nuclear','transport'],default='DRAFT')
    ap.add_argument('--count',type=int,default=12)
    ap.add_argument('--issue',type=int,default=58)
    a=ap.parse_args()
    assert not a.out.exists() and a.out.parent.stat().st_uid==os.getuid()
    rom=Path('/orig/RS201.ROM').read_bytes();assert sha(rom)==ROM_SHA
    aliases=sources(rom)
    roots=sorted(p.parent for p in a.inputs.glob('*/source.json'))
    assert len(roots)==a.count,'明列的批次來源取得後才組成清單'
    a.out.mkdir()
    facilities=[];palette={};source_occurrences={}
    for root in roots:
        proof=json.loads((root/'source.json').read_text())
        case=proof['id'];assert root.name==case
        w,h=proof['size'];width,height=w*36,h*36
        generated=root/'generated.png';generation=json.loads((root/'generation.json').read_text())
        assert sha(generated.read_bytes())==generation['sha256']
        assert sha((root/'prompt.txt').read_bytes())==generation['prompt_sha256']
        raw=subprocess.run(['convert',str(generated),'-filter','Lanczos','-resize',f'{width}x{height}!',
                            '-depth','8','rgba:-'],check=True,stdout=subprocess.PIPE).stdout
        assert len(raw)==width*height*4 and set(raw[3::4])=={255}
        encoded=png(raw,width,height);(a.out/(case+'.png')).write_bytes(encoded)
        native=bytearray(width*height*4)
        for tile in proof['tiles']:
            pixels=next(s for s in aliases if sha(s)==tile['source_sha256'])
            assert aliases[pixels]==tile['sources'] and sorted(set(pixels))==tile['used_colors']
            source_occurrences.setdefault(sha(pixels),[]).append([case,tile['cell']])
            x,y=tile['cell']
            for dy in range(36):
                for dx in range(36):
                    at=((y*36+dy)*width+x*36+dx)*4
                    native[at:at+4]=bytes(proof['used_palette'][str(pixels[(dy//4)*9+dx//4])]+[255])
        for key,color in proof['used_palette'].items():
            assert key not in palette or palette[key]==color
            palette[key]=color
        if a.stage=='DRAFT':
            comparison=b''.join(native[y*width*4:(y+1)*width*4]+raw[y*width*4:(y+1)*width*4] for y in range(height))
            (a.out/(case+'-comparison.png')).write_bytes(png(comparison,width*2,height))
        facilities.append({'id':case,'size':[w,h],'atlas':case+'.png','sha256':sha(encoded),'rgba_sha256':sha(raw),
            'source_proof_sha256':sha((root/'source.json').read_bytes()),'generated':generation,'tiles':proof['tiles']})
    manifest={'schema':1,'stage':a.stage,'issue':46 if a.stage=='nuclear' else a.issue,'rom_sha256':ROM_SHA,'palette':palette,
        'facilities':facilities,'tiles':sum(len(f['tiles']) for f in facilities),
        'unique_sources':len(source_occurrences),
        'shared_sources':[v for v in source_occurrences.values() if len(v)>1],
        'image_processing':'ImageMagick 6.9.11 Lanczos whole-image -> 4x; fixed RGBA8 PNG, no per-tile resampling'}
    (a.out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(a.stage,'facilities',len(facilities),'tiles',manifest['tiles'],'unique',len(source_occurrences),
          'manifest',sha((a.out/'manifest.json').read_bytes()))


if __name__=='__main__':main()
