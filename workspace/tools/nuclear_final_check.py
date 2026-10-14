#!/usr/bin/env python3
"""#46：收尾核對來源、四架構、README 與本機輸出衛生。"""
import argparse
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-commit',required=True);a=ap.parse_args()
    repo=Path('/repo');runs=repo/'workspace/runs';root=runs/'gui-nuclear-hd-r1'
    assert re.fullmatch('[0-9a-f]{40}',a.source_commit)
    report=json.loads((root/'verification.json').read_text())
    pixels=json.loads((root/'pixel-verification.json').read_text())
    assert report['phase']=='hd' and report['native_exit'] and report['seed_unchanged']
    assert not report['new_nuclear_construction_tested']
    assert len(pixels['receipts'])==8 and len(pixels['controls'])==6
    assert sha(root/'saves/NUCLEAR.SAV')==report['save_sha256']
    original=json.loads((runs/'inventory.json').read_text())
    for f in original['files']:
        p=repo/'rs201 模擬台北'/f['path'];assert p.stat().st_size==f['bytes'] and sha(p)==f['sha256']
    assert sha(repo/original['archive']['name'])==original['archive']['sha256']
    binary_names=['taipei-preview','taipei-preview-nuclear-r1','taipei-preview-windows-amd64.exe',
        'taipei-preview-macos-amd64','taipei-preview-macos-arm64']
    binaries={name:sha(runs/name) for name in binary_names}
    assert binaries['taipei-preview']==binaries['taipei-preview-nuclear-r1']==report['binary_sha256']
    linux=(runs/'taipei-preview').read_bytes();assert linux[:5]==b'\x7fELF\x02' and struct.unpack_from('<H',linux,18)[0]==62
    win=(runs/'taipei-preview-windows-amd64.exe').read_bytes();off=struct.unpack_from('<I',win,0x3c)[0]
    assert win[:2]==b'MZ' and win[off:off+4]==b'PE\0\0' and struct.unpack_from('<H',win,off+4)[0]==0x8664
    for arch,cpu in [('amd64',0x1000007),('arm64',0x100000c)]:
        raw=(runs/('taipei-preview-macos-'+arch)).read_bytes()
        assert raw[:4]==b'\xcf\xfa\xed\xfe' and struct.unpack_from('<I',raw,4)[0]==cpu
    mpath=repo/'workspace/screenshots/manifest.json';m=json.loads(mpath.read_text())
    images=m['screenshots'];assert len(images)==len({s['file'] for s in images})==60
    readme=(repo/'README.md').read_text();total=0
    for s in images:
        p=mpath.parent/s['file'];raw=p.read_bytes();total+=len(raw)
        assert sha(p)==s['png_sha256'] and raw[:8]==b'\x89PNG\r\n\x1a\n'
        assert struct.unpack_from('>II',raw,16)==(1280,800) and p.stat().st_uid==p.stat().st_gid==1000
        assert 'workspace/screenshots/'+s['file'] in readme
    assert m['nuclear_capture']['binary_sha256']==report['binary_sha256']
    assert m['nuclear_capture']['source_commit']==a.source_commit
    missing=[]
    docs=list(repo.glob('*.md'))+list((repo/'docs').rglob('*.md'))
    for p in docs:
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if target.startswith(('https://','http://','#','mailto:')):continue
            target=target.strip('<>').split('#')[0]
            if target and not (p.parent/target).exists():missing.append([str(p.relative_to(repo)),target])
    assert not missing,missing
    sources=list((repo/'workspace/app').rglob('*.go'))+[repo/'workspace/app/go.mod',repo/'workspace/app/go.sum',repo/'workspace/app/locales/ui.tsv']
    patches=sorted((repo/'workspace/tools').glob('dosgolem-*.patch'));assert len(patches)==7
    for p in sources+patches:
        committed=subprocess.run(['git','-C',str(repo),'show',a.source_commit+':'+str(p.relative_to(repo))],
            check=True,stdout=subprocess.PIPE).stdout
        assert hashlib.sha256(committed).hexdigest()==sha(p),p
    unwanted=subprocess.run(['find',str(repo/'workspace'),'-user','root','-o','-type','d','-name','*.md'],
        check=True,stdout=subprocess.PIPE,text=True).stdout.splitlines()
    assert not unwanted,unwanted[:20]
    out=runs/'nuclear-final-verification.json';assert not out.exists() and runs.stat().st_uid==1000
    result={'issue':46,'source_commit':a.source_commit,'normal_gui_sha256':sha(root/'verification.json'),
        'pixel_verification_sha256':sha(root/'pixel-verification.json'),'save_sha256':report['save_sha256'],
        'original_files':len(original['files']),'archive_unchanged':True,'sources_and_seven_patches_match':True,
        'binaries':binaries,'readme_images':len(images),'image_bytes':total,'manifest_sha256':sha(mpath),
        'links_dimensions_ownership':True,'root_owned_or_md_directories':unwanted,
        'sources':{str(p.relative_to(repo)):sha(p) for p in sources+patches},
        'new_nuclear_construction_tested':False,'platform_native_tested':['Linux amd64'],
        'limits':'正常既有電廠與靜態圖；核能新建、其他相位、完整機器狀態對拍、外平台真機及正式封包未驗。'}
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('PASS nuclear final:',len(images),'README images,',len(original['files']),'original files, four architectures')


if __name__=='__main__':main()
