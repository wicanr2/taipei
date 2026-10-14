#!/usr/bin/env python3
"""#46：獨立核對核電廠全圖、原始來源、五語系及有效破壞。"""
import argparse
import copy
import json
from pathlib import Path
import subprocess

from chart_locale_check import load, original_pixels, localized_reference
from hd_file_dialogs_check import rgba
from hd_source_audit import sha, cell, scene
from infrastructure_catalog import sources, ROM_SHA

ROOT=Path('/workspace/prototypes/hd-style')
SEALED='05b13ecfc0979b8b4f26e004b195d6068c8202c67cb3ef9ae2836ab9f5cda73a'


def reference():
    raw=(ROOT/'nuclear-ready-v1/manifest.json').read_bytes();assert sha(raw)==SEALED
    m=json.loads(raw);assert (m['stage'],m['tiles'],m['unique_sources'])==('nuclear',36,35)
    rom=Path('/orig/RS201.ROM').read_bytes();assert sha(rom)==m['rom_sha256']==ROM_SHA
    aliases=sources(rom);by_sha={sha(s):s for s in aliases}
    f,=m['facilities'];assert (f['id'],f['size'])==('nuclear',[6,6])
    atlas=rgba(ROOT/'nuclear-ready-v1/nuclear.png',(216,216));assert sha(atlas)==f['rgba_sha256']
    generated=ROOT/'nuclear-v1/nuclear/generated.png';assert sha(generated.read_bytes())==f['generated']['sha256']
    expected=subprocess.run(['convert',str(generated),'-filter','Lanczos','-resize','216x216!',
        '-depth','8','rgba:-'],check=True,stdout=subprocess.PIPE).stdout
    assert expected==atlas and set(atlas[3::4])=={255}
    tiles=[]
    for t in f['tiles']:
        native=by_sha[t['source_sha256']]
        assert aliases[native]==t['sources'] and sorted(set(native))==t['used_colors']
        x,y=t['cell'];assert any(a['member']==38 and a['image']==18+30*y+x for a in aliases[native])
        tiles.append((t['cell'],native))
    assert len(tiles)==36 and len({raw for _,raw in tiles})==35
    return atlas,tiles,m['palette']


def audit(s,frame,shown,atlas,tiles,palette):
    assert sha(frame)==s['frame_index_sha256'] and sha(shown)==s['presentation_sha256']
    assert scene(s,frame) and s['map_origin']=={'X':52,'Y':40,'Valid':True}
    assert not s['help_panel'] and not s['language_panel']
    for (x,y),native in tiles:
        assert cell(frame,77+x*9,70+y*9)==native,('native',x,y)
        assert all(s['palette'][i]==palette[str(i)] for i in set(native))
    if not s['hd_enabled']:
        assert s['hd']['nuclear_facility']['painted']==0 and shown==original_pixels(frame,s['palette'])
        return
    actual=b''.join(shown[((280+y)*1280+308)*4:((280+y)*1280+524)*4] for y in range(216))
    assert actual==atlas,'整座電廠與同源格必須完整符合'
    stats=s['hd']['nuclear_facility']
    assert stats['matched']==stats['painted']==36 and stats['fallback']==0 and stats['facilities']=={'nuclear':36}
    labels=localized_reference(s['language'])
    for x,y,w,h in [(28+i*176,40,136,68) for i in range(6)]+[(1132,704,24,28),(1212,704,48,28),(1212,736,48,28)]:
        assert all(shown[((y+cy)*1280+x)*4:((y+cy)*1280+x+w)*4]==labels[((y+cy)*1280+x)*4:((y+cy)*1280+x+w)*4]
            for cy in range(h)),('localized label',s['language'],x,y)


def check(root):
    report=json.loads((root/'verification.json').read_text())
    assert report['normal_gui'] and report['phase']=='hd' and not report['state_injection'] and not report['checkpoint']
    assert report['native_exit'] and report['original_save_read'] and report['seed_unchanged']
    assert not report['new_nuclear_construction_tested']
    atlas,tiles,palette=reference();receipts=[];baseline=None
    shots=report['screenshots'];assert len(shots)==len({s['file'] for s in shots})==8
    for shot in shots:
        p=root/shot['file'].replace('.png','-capture.zip')
        assert sha(p.read_bytes())==shot['capture_sha256']
        assert sha((root/shot['file']).read_bytes())==shot['png_sha256']
        s,f,shown=load(p);audit(s,f,shown,atlas,tiles,palette)
        receipts.append({'file':p.name,'sha256':sha(p.read_bytes()),'language':s['language'],
            'hd_enabled':s['hd_enabled'],'whole_nuclear_and_labels':True})
        if shot['file']=='nuclear-zh-Hant.png':baseline=s,f,shown
    assert baseline is not None
    controls=[]
    for fault in ['positive','tile','source','reported-count','wrong-language','shared-tile-swap']:
        s,f,shown=copy.deepcopy(baseline[0]),bytearray(baseline[1]),bytearray(baseline[2])
        if fault=='tile':shown[(280*1280+308)*4]^=1
        elif fault=='source':f[70*320+77]^=128
        elif fault=='reported-count':s['hd']['nuclear_facility']['painted']+=1
        elif fault=='wrong-language':s['language']='en'
        elif fault=='shared-tile-swap':
            for y in range(36):
                a=((280+y)*1280+380)*4;b=((280+y)*1280+452)*4
                left,right=bytes(shown[a:a+144]),bytes(shown[b:b+144])
                shown[a:a+144],shown[b:b+144]=right,left
        s['frame_index_sha256'],s['presentation_sha256']=sha(f),sha(shown)
        rejected=False
        try:audit(s,bytes(f),bytes(shown),atlas,tiles,palette)
        except AssertionError:rejected=True
        assert rejected==(fault!='positive'),fault
        controls.append({'fault':fault,'rejected':rejected,'affected_hashes_recomputed':True})
    return {'issue':46,'tiles':36,'unique_sources':35,'receipts':receipts,'controls':controls,
        'scope':'既有電廠正常 GUI，全圖含同源格、五語系標籤及原版整張；區外隔離與資源故障由 Go 測試另驗；新建施工未抽測。'}


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True);a=ap.parse_args()
    p=a.run/'pixel-verification.json';assert not p.exists()
    r=check(a.run);p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
    print('PASS nuclear: 36 tiles, eight GUI frames, six controls')
