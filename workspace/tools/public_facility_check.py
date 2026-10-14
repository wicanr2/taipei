#!/usr/bin/env python3
"""#58: verify v1/v2 facilities against sealed prototypes, ROM and AI originals."""
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
PROTOTYPES={'environment':('v1','36654f6fcfcc76dcc095fafde7a58c575bd5f4bfcdeeaf44b6c94912e526ae87',32,32),
            'public':('v2','8a90556b3065244377ae9cfbc414389b76fb71150c618623a06a05116caf5428',392,391),
            'transport':('transport','3ad256026ebfa478fbe0da48e1053131079c5d4b10787b5320f8f388546094cd',72,72)}


def reference(scope):
    version,sealed,total,unique=PROTOTYPES[scope]
    proto=ROOT/('transport-prototype-v1' if scope=='transport' else 'public-facilities-prototype-'+version)
    raw=(proto/'manifest.json').read_bytes();assert sha(raw)==sealed
    m=json.loads(raw);rom=Path('/orig/RS201.ROM').read_bytes()
    assert sha(rom)==m['rom_sha256'] and (m['tiles'],m['unique_sources'])==(total,unique)
    aliases=sources(rom);by_sha={sha(s):s for s in aliases};facilities={};seen=[]
    for facility in m['facilities']:
        case=facility['id'];w,h=facility['size'];width,height=w*36,h*36
        atlas=rgba(proto/f'{case}.png',(width,height))
        assert sha(atlas)==facility['rgba_sha256']
        source=ROOT/('transport-v1' if scope=='transport' else 'public-facilities-v1')/case/'generated.png'
        assert sha(source.read_bytes())==facility['generated']['sha256']
        expected=subprocess.run(['convert',str(source),'-filter','Lanczos','-resize',f'{width}x{height}!',
                                 '-depth','8','rgba:-'],check=True,stdout=subprocess.PIPE).stdout
        assert expected==atlas
        tiles=[]
        for record in facility['tiles']:
            native=by_sha[record['source_sha256']]
            assert aliases[native]==record['sources'] and sorted(set(native))==record['used_colors']
            tiles.append((record['cell'],native));seen.append(sha(native))
        assert len(tiles)==w*h
        facilities[case]={'size':(width,height),'atlas':atlas,'tiles':tiles}
    assert len(seen)==total and len(set(seen))==unique
    return facilities,m['palette']


def audit(s,frame,shown,facilities,palette,case):
    transport=case in ['port','airport']
    origin={'X':36,'Y':24,'Valid':True} if case=='airport' else {'X':32,'Y':68,'Valid':True} if case=='port' else {'X':12,'Y':12,'Valid':True}
    left,top=(11,5) if transport else (22,3)
    dx,dy=(416,316) if transport else (812,244)
    field='transport_facilities' if transport else 'public_facilities'
    assert sha(frame)==s['frame_index_sha256'] and sha(shown)==s['presentation_sha256']
    assert scene(s,frame) and s['map_origin']==origin
    assert not s['help_panel'] and not s['language_panel']
    if not s['hd_enabled']:
        assert s['hd'][field]['painted']==0 and shown==original_pixels(frame,s['palette'])
        return
    facility=facilities[case];width,height=facility['size'];count=len(facility['tiles'])
    for (x,y),native in facility['tiles']:
        assert cell(frame,5+(left+x)*9,34+(top+y)*9)==native,('native facility',case,x,y)
        assert all(s['palette'][i]==palette[str(i)] for i in set(native))
    actual=b''.join(shown[((dy+y)*1280+dx)*4:((dy+y)*1280+dx+width)*4] for y in range(height))
    assert actual==facility['atlas'],('whole facility including shared sources',case)
    stats=s['hd'][field]
    assert stats['matched']==stats['painted']==count and stats['fallback']==0 and stats['facilities']=={case:count}
    labels=localized_reference(s['language'])
    for x,y,w,h in [(28+i*176,40,136,68) for i in range(6)]+[(1132,704,24,28),(1212,704,48,28),(1212,736,48,28)]:
        assert all(shown[((y+cy)*1280+x)*4:((y+cy)*1280+x+w)*4]==labels[((y+cy)*1280+x)*4:((y+cy)*1280+x+w)*4] for cy in range(h)),('localized label',s['language'],x,y)


def check(root,scope='environment'):
    report=json.loads((root/'verification.json').read_text())
    assert report['normal_gui'] and not report['state_injection'] and not report['checkpoint']
    assert report['native_exit_tested'] and report['original_save_read'] and report['save_unchanged_after_read']
    transport=scope=='transport'
    first='airport' if transport else 'waste'
    second='port' if transport else 'stadium' if scope=='public' else 'sewage'
    assert [c['id'] for c in report['cases']]==[first,second]
    if transport:assert report['seed_unchanged'] and not report['new_construction_tested']
    facilities,palette=reference(scope);receipts=[];baseline=None
    shots=report['screenshots'];assert len(shots)==len({s['file'] for s in shots})==(12 if transport else 8)
    expected=({first+'-'+lang+'.png' for lang in ['original','zh-Hant','zh-Hans','ja','ko','en']} if transport else {'waste-original.png','waste-zh-Hant.png'})|{second+'-'+lang+'.png' for lang in ['original','zh-Hant','zh-Hans','ja','ko','en']}
    assert {s['file'] for s in shots}==expected
    for shot in shots:
        case=shot['file'].split('-')[0]
        p=root/shot['file'].replace('.png','-capture.zip')
        assert sha(p.read_bytes())==shot['capture_sha256']
        assert sha((root/shot['file']).read_bytes())==shot['png_sha256']
        s,f,shown=load(p);audit(s,f,shown,facilities,palette,case)
        receipts.append({'file':p.name,'sha256':sha(p.read_bytes()),'language':s['language'],
                         'hd_enabled':s['hd_enabled'],'case':case,'facility_pixels_and_locale_labels':True})
        if case==second and s['hd_enabled'] and s['language']=='zh-Hant':baseline=s,f,shown
    assert baseline is not None
    controls=[]
    faults=['positive','tile','source','reported-count','wrong-language']+(['shared-tile-swap'] if scope=='public' else [])
    for fault in faults:
        s,f,shown=copy.deepcopy(baseline[0]),bytearray(baseline[1]),bytearray(baseline[2])
        if fault=='tile':shown[((316 if transport else 244)*1280+(416 if transport else 812))*4]^=1
        elif fault=='source':f[(79 if transport else 61)*320+(104 if transport else 203)]^=128
        elif fault=='reported-count':s['hd']['transport_facilities' if transport else 'public_facilities']['painted']+=1
        elif fault=='wrong-language':s['language']='en'
        elif fault=='shared-tile-swap':
            for y in range(36):
                a=((244+y)*1280+920)*4;b=((244+y)*1280+956)*4
                left,right=bytes(shown[a:a+144]),bytes(shown[b:b+144])
                shown[a:a+144],shown[b:b+144]=right,left
        s['frame_index_sha256'],s['presentation_sha256']=sha(f),sha(shown)
        rejected=False
        try:audit(s,bytes(f),bytes(shown),facilities,palette,second)
        except AssertionError:rejected=True
        assert rejected==(fault!='positive'),fault
        controls.append({'fault':fault,'rejected':rejected,'affected_hashes_recomputed':True})
    return {'issue':61 if transport else 58,'tiles':PROTOTYPES[scope][2],'receipts':receipts,'controls':controls,
            'scope':'整批固定原型與來源；GUI 兩項既有設施完整圖、五語系標籤及原版整張；區外隔離由 Go 正常來源測試驗證' if transport else '整批固定原型與來源；GUI 兩項完整圖、五語系標籤及原版整張；區外隔離由 Go 正常來源測試驗證'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True)
    ap.add_argument('--scope',choices=PROTOTYPES,default='environment');a=ap.parse_args()
    target=a.run/'pixel-verification.json';assert not target.exists()
    report=check(a.run,a.scope)
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('PASS:',report['tiles'],'tiles,',len(report['receipts']),'GUI frames,',len(report['controls']),'controls')


if __name__=='__main__':main()
