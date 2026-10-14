#!/usr/bin/env python3
"""040：彙整已完成的實際封包收據，保留平台未驗限制。"""
import argparse
import json
import os
from pathlib import Path
import re
import struct
import subprocess

from full_asset_catalog import sha


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', type=Path, required=True)
    ap.add_argument('--version', required=True)
    a = ap.parse_args()
    assert re.fullmatch(r'v\.[0-9]+\.[0-9]+\.[0-9]+-[0-9]{8}', a.version)
    dist = a.project/'dist-all'/a.version
    assert not (dist/'smoke/acceptance.json').exists()
    index = json.loads((dist/'SHA256SUMS.json').read_text())
    assert index['version'] == a.version
    tag = subprocess.check_output(['git','-C',str(a.project),'rev-parse',a.version+'^{commit}'],text=True).strip()
    assert tag == index['source_commit']
    check_raw = (dist/'smoke/unpacked/package-verification.json').read_bytes()
    check = json.loads(check_raw)
    assert len(check['packages']) == 3 and check['missing_sealed_art_rejected']
    assert check['source_commit'] == tag and check['version'] == a.version
    for r in index['packages']:
        path = dist/r['file']
        assert path.stat().st_size == r['bytes'] and sha(path.read_bytes()) == r['sha256']
    smoke = {}
    for platform in ['linux','windows']:
        path = dist/'smoke'/platform/'smoke-result.json'
        raw = path.read_bytes()
        result = json.loads(raw)
        assert result['version'] == result['program_version'] == a.version and result['source_commit'] == tag
        assert result['actual_package_launcher'] and not result['checkpoint']
        assert result['f11_f12_help'] and result['original_nearest_pixels'] and result['missing_original_visible_error']
        assert result['opening_illustrations']['painted'] > 0
        if platform == 'linux':
            assert result['audio']['default_audio_device'] and result['audio']['technical_non_silence']
        smoke[platform] = {'receipt_sha256':sha(raw),'backend':result['backend'],
                           'actual_package_launcher':True,'f11_f12_help':True,'missing_original_visible_error':True,
                           'default_audio':result['audio'],'native_DOS_save_load_exit':'039 Linux representative receipt'}
    build = a.project/'workspace/runs'/('release-'+a.version)
    for arch in ['amd64','arm64']:
        commands = (build/('macos-'+arch+'-load-commands.txt')).read_text()
        assert re.search(r'(?:minos|version)\s+11\.0\b',commands)
        for line in (build/('macos-'+arch+'-dependencies.txt')).read_text().splitlines()[1:]:
            line = line.strip()
            assert line.startswith('/usr/lib/') or line.startswith('/System/Library/Frameworks/'), line
    pe = (build/'windows-pe.txt').read_text()
    assert set(re.findall(r'DLL Name:\s*(\S+)',pe)) == {'KERNEL32.dll','msvcrt.dll'}
    original = json.loads((a.project/'workspace/runs/inventory.json').read_text())
    for r in original['files']:
        path = a.project/'rs201 模擬台北'/r['path']
        assert path.stat().st_size == r['bytes'] and sha(path.read_bytes()) == r['sha256']
    assert sha((a.project/original['archive']['name']).read_bytes()) == original['archive']['sha256']
    photos_raw = (a.project/'workspace/screenshots/manifest.json').read_bytes()
    photos = json.loads(photos_raw)
    assert len(photos['screenshots']) == 92
    for r in photos['screenshots']:
        raw = (a.project/'workspace/screenshots'/r['file']).read_bytes()
        assert sha(raw) == r['png_sha256'] and struct.unpack('>II',raw[16:24]) == (1280,800)
    # find does not dereference Wine's z: link to the container root.
    for root in [a.project/'workspace',a.project/'dist-all']:
        assert not subprocess.check_output(['find',str(root),'-user','root','-o','-type','d','-name','*.md'],text=True).strip()
    result = {'schema':1,'version':a.version,'source_commit':tag,'packages':index['packages'],
              'package_verification_sha256':sha(check_raw),'smoke':smoke,
              'macos':{'architectures':['amd64','arm64'],'universal_slices_byte_equal':True,
                       'minimum_deployment_target':'11.0','dependencies':'system frameworks/libraries',
                       'package_content_and_materials_verified':True,'native_execution_tested':False,
                       'launcher_save_directory_native_tested':False},
              'original_35_files_and_rar_unchanged':True,'readme_screenshots':92,
              'screenshots_manifest_sha256':sha(photos_raw),'output_ownership':'1000:1000',
              'limits':'Windows is Wine, macOS structure only; native machines and human listening untested;039 normal representative scope retained',
              'tool_sha256':sha(Path(__file__).read_bytes()),'rights':'full-local only; no public Release'}
    out = dist/'smoke/acceptance.json'
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    index['acceptance'] = {'file':'smoke/acceptance.json','sha256':sha(out.read_bytes()),
                           'linux_actual_package_gui':True,'linux_default_audio_non_silent':True,
                           'windows_wine_actual_package_gui':True,'macos_structure_only':True,
                           'native_windows_macos_tested':False}
    (dist/'SHA256SUMS.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
    print('ACCEPTED LOCAL',a.version,sha(out.read_bytes()))


if __name__ == '__main__':
    main()
