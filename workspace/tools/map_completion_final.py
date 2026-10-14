#!/usr/bin/env python3
"""038：正常驗收、原版不變、編譯來源、四架構、文件與交付衛生。"""
import argparse
import json
from pathlib import Path
import re
import struct
import subprocess

from infrastructure_catalog import sha


def digest(path):return sha(path.read_bytes())


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-commit',required=True)
    ap.add_argument('--run',default='gui-map-r4');a=ap.parse_args()
    assert re.fullmatch('[0-9a-f]{40}',a.source_commit)
    repo=Path('/repo');runs=repo/'workspace/runs';root=runs/a.run
    report=json.loads((root/'verification.json').read_text());pixels=json.loads((root/'pixel-verification.json').read_text())
    assert report['native_exit_tested'] and report['normal_gui'] and not report['state_injection']
    assert pixels['baseline_save_identical'] and len(pixels['screenshots'])==42 and pixels['effective_pixel_negative_controls']==42
    saved=root/'saves/MAPHD.SAV';assert digest(saved)==report['final_save_sha256']==pixels['original_save_sha256']
    original=json.loads((runs/'inventory.json').read_text())
    for record in original['files']:
        path=repo/'rs201 模擬台北'/record['path']
        assert path.stat().st_size==record['bytes'] and digest(path)==record['sha256']
    assert digest(repo/original['archive']['name'])==original['archive']['sha256']
    names=['taipei-preview','taipei-preview-map-r2','taipei-preview-windows-amd64.exe','taipei-preview-macos-amd64','taipei-preview-macos-arm64']
    binaries={n:digest(runs/n) for n in names}
    assert binaries['taipei-preview']==binaries['taipei-preview-map-r2']==report['binary_sha256']
    linux=(runs/'taipei-preview').read_bytes();assert linux[:5]==b'\x7fELF\x02' and struct.unpack_from('<H',linux,18)[0]==62
    windows=(runs/names[2]).read_bytes();off=struct.unpack_from('<I',windows,0x3c)[0]
    assert windows[:2]==b'MZ' and windows[off:off+4]==b'PE\0\0' and struct.unpack_from('<H',windows,off+4)[0]==0x8664
    for name,cpu in zip(names[3:],[0x1000007,0x100000c]):
        raw=(runs/name).read_bytes();assert raw[:4]==b'\xcf\xfa\xed\xfe' and struct.unpack_from('<I',raw,4)[0]==cpu
    assets=repo/'workspace/prototypes/hd-style/map-completion-ready-v1';repro=assets.parent/'map-completion-ready-repro-v1'
    asset_files=[p.relative_to(assets) for p in assets.rglob('*') if p.is_file()];assert len(asset_files)==136
    assert digest(assets/'manifest.json')=='be04e87136b05e09c3eb92402eea6173280687c9323fdf97cef77c2c8dd10a10'
    for path in asset_files:assert (assets/path).read_bytes()==(repro/path).read_bytes()
    screenshots=repo/'workspace/screenshots';manifest=json.loads((screenshots/'manifest.json').read_text())
    images=manifest['screenshots'];assert len(images)==len({s['file'] for s in images})==84
    assert manifest['map_capture']['source_commit']==a.source_commit and manifest['map_capture']['binary_sha256']==report['binary_sha256']
    readme=(repo/'README.md').read_text();total=0
    for record in images:
        path=screenshots/record['file'];raw=path.read_bytes();total+=len(raw)
        assert sha(raw)==record['png_sha256'] and raw[:8]==b'\x89PNG\r\n\x1a\n'
        assert struct.unpack_from('>II',raw,16)==(1280,800) and path.stat().st_uid==path.stat().st_gid==1000
        assert 'workspace/screenshots/'+record['file'] in readme
    sources=list((repo/'workspace/app').rglob('*.go'))+[repo/'workspace/app/go.mod',repo/'workspace/app/go.sum',repo/'workspace/app/locales/ui.tsv']
    patches=sorted((repo/'workspace/tools').glob('dosgolem-*.patch'));assert len(patches)==7
    for path in sources+patches:
        raw=subprocess.check_output(['git','-C',str(repo),'show',a.source_commit+':'+str(path.relative_to(repo))])
        assert sha(raw)==digest(path),path
    missing=[]
    for path in list(repo.glob('*.md'))+list((repo/'docs').rglob('*.md')):
        for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
            if target.startswith(('https://','http://','#','mailto:')):continue
            target=target.strip('<>').split('#')[0]
            if target and not (path.parent/target).exists():missing.append([str(path.relative_to(repo)),target])
    assert not missing,missing
    unwanted=subprocess.check_output(['find',str(repo/'workspace'),'-user','root','-o','-type','d','-name','*.md'],text=True).splitlines();assert not unwanted,unwanted[:20]
    out=runs/'map-completion-final.json';assert not out.exists() and runs.stat().st_uid==1000
    result={'schema':1,'issue':62,'source_commit':a.source_commit,'normal_gui_sha256':digest(root/'verification.json'),
        'pixel_verification_sha256':digest(root/'pixel-verification.json'),'save_sha256':digest(saved),
        'original_files_unchanged':len(original['files']),'archive_unchanged':True,'binaries':binaries,
        'sources_and_seven_patches_match':True,'reproduced_assets':len(asset_files),'readme_images':len(images),
        'readme_image_bytes':total,'readme_manifest_sha256':digest(screenshots/'manifest.json'),
        'links_dimensions_ownership':True,'root_owned_or_md_directories':unwanted,'tool_sha256':digest(Path(__file__)),
        'platform_native_tested':['Linux amd64'],'limits':pixels['scope']+'；未做人耳或Windows／macOS真機，正式封包另驗。'}
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('PASS: 35 original files, four architectures, 136 assets, 84 screenshots, commit sources, links and ownership',digest(out))


if __name__=='__main__':main()
