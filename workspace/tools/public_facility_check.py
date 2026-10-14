#!/usr/bin/env python3
"""#58: verify facilities against sealed prototypes, ROM and generated originals."""
import argparse
import copy
import json
from pathlib import Path
import subprocess

from chart_locale_check import load, original_pixels, localized_reference
from hd_file_dialogs_check import rgba
from hd_source_audit import sha, cell, scene
from infrastructure_catalog import sources

ROOT=Path('/workspace/prototypes/hd-style')


def reference():
    proto=ROOT/'public-facilities-prototype-v1'
    raw=(proto/'manifest.json').read_bytes()
    assert sha(raw)=='36654f6fcfcc76dcc095fafde7a58c575bd5f4bfcdeeaf44b6c94912e526ae87'
    m=json.loads(raw)
    rom=Path('/orig/RS201.ROM').read_bytes()
    assert sha(rom)==m['rom_sha256'] and m['unique_sources']==m['tiles']==32
    aliases=sources(rom);tiles={}
    for facility in m['facilities']:
        case=facility['id'];assert case in ['waste','sewage']
        atlas=rgba(proto/f'{case}.png',(144,144))
        assert sha(atlas)==facility['rgba_sha256']
        source=ROOT/f'public-facilities-v1/{case}/generated.png'
        assert sha(source.read_bytes())==facility['generated']['sha256']
        expected=subprocess.run(['convert',str(source),'-filter','Lanczos','-resize','144x144!',
                                 '-depth','8','rgba:-'],check=True,stdout=subprocess.PIPE).stdout
        assert expected==atlas
        for record in facility['tiles']:
            native=next(s for s in aliases if sha(s)==record['source_sha256'])
            assert aliases[native]==record['sources'] and sorted(set(native))==record['used_colors']
            x,y=record['cell']
            fragment=b''.join(atlas[((y*36+cy)*144+x*36)*4:((y*36+cy)*144+x*36+36)*4] for cy in range(36))
            assert native not in tiles
            tiles[native]=(case,fragment)
    return tiles,m['palette']


def audit(s,frame,shown,tiles,palette,case):
    assert sha(frame)==s['frame_index_sha256'] and sha(shown)==s['presentation_sha256']
    assert scene(s,frame) and s['map_origin']=={'X':12,'Y':12,'Valid':True}
    assert not s['help_panel'] and not s['language_panel']
    if not s['hd_enabled']:
        assert s['hd']['public_facilities']['painted']==0 and shown==original_pixels(frame,s['palette'])
        return
    facilities={}
    for row in range(15):
        for col in range(29):
            raw=cell(frame,5+col*9,34+row*9)
            if raw not in tiles:continue
            key,expected=tiles[raw]
            assert all(s['palette'][i]==palette[str(i)] for i in set(raw))
            actual=b''.join(shown[((136+row*36+y)*1280+20+col*36)*4:((136+row*36+y)*1280+56+col*36)*4] for y in range(36))
            assert actual==expected,('facility pixels',key,col,row)
            facilities[key]=facilities.get(key,0)+1
    stats=s['hd']['public_facilities']
    assert facilities=={case:16}
    assert stats['matched']==stats['painted']==16 and stats['fallback']==0 and stats['facilities']==facilities
    labels=localized_reference(s['language'])
    for x,y,w,h in [(28+i*176,40,136,68) for i in range(6)]+[(1132,704,24,28),(1212,704,48,28),(1212,736,48,28)]:
        assert all(shown[((y+cy)*1280+x)*4:((y+cy)*1280+x+w)*4]==labels[((y+cy)*1280+x)*4:((y+cy)*1280+x+w)*4] for cy in range(h)),('localized label',s['language'],x,y)


def check(root):
    report=json.loads((root/'verification.json').read_text())
    assert report['normal_gui'] and not report['state_injection'] and not report['checkpoint']
    assert report['native_exit_tested'] and report['original_save_read'] and report['save_unchanged_after_read']
    assert [c['id'] for c in report['cases']]==['waste','sewage']
    tiles,palette=reference();receipts=[];baseline=None
    assert len(report['screenshots'])==8
    for shot in report['screenshots']:
        case=shot['file'].split('-')[0]
        p=root/shot['file'].replace('.png','-capture.zip')
        assert sha(p.read_bytes())==shot['capture_sha256']
        assert sha((root/shot['file']).read_bytes())==shot['png_sha256']
        s,f,shown=load(p);audit(s,f,shown,tiles,palette,case)
        receipts.append({'file':p.name,'sha256':sha(p.read_bytes()),'language':s['language'],
                         'hd_enabled':s['hd_enabled'],'case':case,'facility_pixels_and_locale_labels':True})
        if case=='sewage' and s['hd_enabled'] and s['language']=='zh-Hant':baseline=s,f,shown
    assert baseline is not None
    controls=[]
    for fault in ['positive','tile','source','reported-count','wrong-language']:
        s,f,shown=copy.deepcopy(baseline[0]),bytearray(baseline[1]),bytearray(baseline[2])
        if fault=='tile':shown[(244*1280+812)*4]^=1
        elif fault=='source':f[61*320+203]^=128
        elif fault=='reported-count':s['hd']['public_facilities']['painted']+=1
        elif fault=='wrong-language':s['language']='en'
        s['frame_index_sha256'],s['presentation_sha256']=sha(f),sha(shown)
        rejected=False
        try:audit(s,bytes(f),bytes(shown),tiles,palette,'sewage')
        except AssertionError:rejected=True
        assert rejected==(fault!='positive'),fault
        controls.append({'fault':fault,'rejected':rejected,'affected_hashes_recomputed':True})
    return {'issue':58,'tiles':32,'receipts':receipts,'controls':controls,
            'scope':'兩設施實際像素與五語系標籤，原版整張；區外隔離由 Go 正常來源測試驗證'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True);a=ap.parse_args()
    target=a.run/'pixel-verification.json';assert not target.exists()
    report=check(a.run)
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('PASS: 32 facility tiles, eight GUI frames, five controls')


if __name__=='__main__':main()
