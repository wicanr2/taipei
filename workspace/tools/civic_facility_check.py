#!/usr/bin/env python3
"""#57: independently verify actual GUI facility pixels and localized labels."""
import copy
import json
from pathlib import Path
import struct
import subprocess

from chart_locale_check import load, original_pixels, localized_reference
from hd_file_dialogs_check import rgba
from hd_source_audit import sha, cell, scene

ROOT=Path('/workspace/prototypes/hd-style')


def reference():
    proto=ROOT/'civic-facilities-prototype-v1'
    raw=(proto/'manifest.json').read_bytes()
    assert sha(raw)=='248c8ef696f478e90980a00391dffaddadc0abe5b2b93132db57135e13d95bd7'
    m=json.loads(raw)
    rom=Path('/orig/RS201.ROM').read_bytes()
    assert sha(rom)==m['rom_sha256']
    atlas=rgba(proto/'37.png',(288,144))
    assert sha(atlas)==m['atlases']['37']['rgba_sha256']
    for number,case in enumerate(['police','fire']):
        source=ROOT/f'civic-facilities-v1/{case}-generated.png'
        assert sha(source.read_bytes())==m['generated'][case]['sha256']
        expected=subprocess.run(['convert',str(source),'-filter','Lanczos','-resize','144x144!',
                                 '-depth','8','rgba:-'],check=True,stdout=subprocess.PIPE).stdout
        actual=b''.join(atlas[(y*288+number*144)*4:(y*288+number*144+144)*4] for y in range(144))
        assert expected==actual
    off,size=struct.unpack_from('<IH',rom,18+37*16)
    assert size==8354 and struct.unpack_from('<H',rom,off)[0]==96
    tiles={}
    for y in range(4):
        for x in range(8):
            index=y*24+x
            a,b=struct.unpack_from('<HH',rom,off+2+index*2)
            assert b-a==85 and rom[off+a:off+a+4]==b'\x09\x00\x09\x00'
            source=rom[off+a+4:off+b]
            record=next(s for s in m['sources'] if s['image']==index)
            assert sha(source)==record['source_sha256'] and sorted(set(source))==record['used_colors']
            fragment=b''.join(atlas[((y*36+cy)*288+x*36)*4:((y*36+cy)*288+x*36+36)*4] for cy in range(36))
            assert source not in tiles
            tiles[source]=(f'37/{index}',fragment)
    return tiles,m['palette']


def audit(s,frame,shown,tiles,palette):
    assert sha(frame)==s['frame_index_sha256'] and sha(shown)==s['presentation_sha256']
    assert scene(s,frame) and s['map_origin']=={'X':12,'Y':12,'Valid':True}
    assert not s['help_panel'] and not s['language_panel']
    if not s['hd_enabled']:
        assert s['hd']['civic_facilities']['painted']==0 and shown==original_pixels(frame,s['palette'])
        return
    images={}
    for row in range(15):
        for col in range(29):
            raw=cell(frame,5+col*9,34+row*9)
            if raw not in tiles:continue
            key,expected=tiles[raw]
            assert all(s['palette'][i]==palette[str(i)] for i in set(raw))
            actual=b''.join(shown[((136+row*36+y)*1280+20+col*36)*4:((136+row*36+y)*1280+56+col*36)*4] for y in range(36))
            assert actual==expected,('facility pixels',col,row)
            images[key]=images.get(key,0)+1
    stats=s['hd']['civic_facilities']
    assert len(images)==32 and sum(images.values())==32
    assert stats['matched']==stats['painted']==32 and stats['fallback']==0 and stats['images']==images
    labels=localized_reference(s['language'])
    for x,y,w,h in [(28+i*176,40,136,68) for i in range(6)]+[(1132,704,24,28),(1212,704,48,28),(1212,736,48,28)]:
        assert all(shown[((y+cy)*1280+x)*4:((y+cy)*1280+x+w)*4]==labels[((y+cy)*1280+x)*4:((y+cy)*1280+x+w)*4] for cy in range(h)),('localized label',s['language'],x,y)


def main():
    root=Path('/workspace/runs/gui-civic-r1')
    target=root/'pixel-verification.json'
    assert not target.exists()
    tiles,palette=reference()
    receipts=[]
    for label in ['original','zh-Hant','zh-Hans','ja','ko','en']:
        p=root/'gui'/f'city-{label}-capture.zip'
        s,f,shown=load(p)
        audit(s,f,shown,tiles,palette)
        receipts.append({'file':p.name,'sha256':sha(p.read_bytes()),'language':s['language'],
                         'hd_enabled':s['hd_enabled'],'facility_pixels_and_locale_labels':True})
        if s['hd_enabled'] and s['language']=='zh-Hant':baseline=s,f,shown
    assert len(receipts)==6
    controls=[]
    for fault in ['positive','tile','source','reported-count','wrong-language']:
        s,f,shown=copy.deepcopy(baseline[0]),bytearray(baseline[1]),bytearray(baseline[2])
        if fault=='tile':shown[(244*1280+812)*4]^=1
        elif fault=='source':f[61*320+203]^=128
        elif fault=='reported-count':s['hd']['civic_facilities']['painted']+=1
        elif fault=='wrong-language':s['language']='en'
        s['frame_index_sha256'],s['presentation_sha256']=sha(f),sha(shown)
        rejected=False
        try:audit(s,bytes(f),bytes(shown),tiles,palette)
        except AssertionError:rejected=True
        assert rejected==(fault!='positive'),fault
        controls.append({'fault':fault,'rejected':rejected,'affected_hashes_recomputed':True})
    target.write_text(json.dumps({'issue':57,'tiles':32,'receipts':receipts,'controls':controls,
                                 'scope':'HD 設施實際像素與語言標籤，原版整張；區外隔離另由 Go 正常來源測試驗證'},ensure_ascii=False,indent=2)+'\n')
    print('PASS: 32 facility tiles, six GUI frames, five controls')


if __name__=='__main__':main()
