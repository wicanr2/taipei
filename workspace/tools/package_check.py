#!/usr/bin/env python3
"""040：檢查並解開實際三包，重跑正式材料載入器與缺件反例。"""
import argparse
import json
import os
from pathlib import Path, PurePosixPath
import stat
import struct
import subprocess
import tarfile
import zipfile

from full_asset_catalog import sha


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dist', type=Path, required=True)
    ap.add_argument('--build', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    index_raw = (a.dist/'SHA256SUMS.json').read_bytes()
    index = json.loads(index_raw)
    assert a.dist.name == index['version']
    assert not a.out.exists() and a.out.parent.stat().st_uid == os.getuid()
    a.out.mkdir()
    records = []
    for package in index['packages']:
        archive = a.dist/package['file']
        assert archive.stat().st_size == package['bytes'] and sha(archive.read_bytes()) == package['sha256']
        files, modes = {}, {}
        if archive.name.endswith('.zip'):
            with zipfile.ZipFile(archive) as z:
                assert z.testzip() is None
                for entry in z.infolist():
                    assert not entry.is_dir() and entry.filename not in files
                    if not entry.filename.isascii():
                        assert entry.flag_bits & 0x800
                    mode = entry.external_attr >> 16
                    assert stat.S_ISREG(mode)
                    files[entry.filename], modes[entry.filename] = z.read(entry), stat.S_IMODE(mode)
        else:
            with tarfile.open(archive, 'r:gz') as tar:
                for entry in tar.getmembers():
                    assert entry.isfile() and entry.name not in files and entry.uid == entry.gid == 1000
                    files[entry.name], modes[entry.name] = tar.extractfile(entry).read(), entry.mode
        for name in files:
            path = PurePosixPath(name)
            assert not path.is_absolute() and '..' not in path.parts and '\\' not in name and ':' not in name
            assert path.parts[0] == package['root']
        prefix = package['root']+'/'
        manifest_raw = files[prefix+'manifest.json']
        assert sha(manifest_raw) == package['manifest_sha256']
        manifest = json.loads(manifest_raw)
        assert manifest['version'] == index['version'] and manifest['source_commit'] == index['source_commit']
        assert manifest['platform'] == package['platform'] and manifest['architecture'] == package['architecture']
        expected = {prefix+r['file'] for r in manifest['files']} | {prefix+'manifest.json'}
        assert set(files) == expected
        for r in manifest['files']:
            name = prefix+r['file']
            assert len(files[name]) == r['bytes'] and sha(files[name]) == r['sha256'] and modes[name] == int(r['mode'], 8)
        assert files[prefix+'VERSION'].decode() == index['version']+'\n'
        platform = package['platform']
        binary = files[prefix+('Taipei.exe' if platform == 'windows' else 'Taipei')]
        if platform == 'linux':
            assert binary[:5] == b'\x7fELF\x02' and struct.unpack_from('<H',binary,18)[0] == 62
        elif platform == 'windows':
            offset = struct.unpack_from('<I',binary,60)[0]
            assert binary[:2] == b'MZ' and binary[offset:offset+4] == b'PE\0\0' and struct.unpack_from('<H',binary,offset+4)[0] == 0x8664
            assert files[prefix+'README.txt'].startswith(b'\xef\xbb\xbf')
            assert b'\n' not in files[prefix+'README.txt'].replace(b'\r\n',b'')
            batch = files[prefix+'Start.cmd']
            batch.decode('ascii')
            assert batch.startswith(b'@echo off\r\n') and b'\n' not in batch.replace(b'\r\n',b'')
        else:
            assert binary[:4] == b'\xca\xfe\xba\xbe' and struct.unpack_from('>I',binary,4)[0] == 2
            slices = {}
            for i in range(2):
                cpu, subtype, off, size, alignment = struct.unpack_from('>IIIII',binary,8+20*i)
                assert cpu not in slices and off+size <= len(binary)
                slices[cpu] = binary[off:off+size]
            assert set(slices) == {0x1000007,0x100000c}
            for cpu, arch in [(0x1000007,'amd64'),(0x100000c,'arm64')]:
                assert slices[cpu] == (a.build/('taipei-macos-'+arch)).read_bytes()
        assert index['version'].encode() in binary
        destination = a.out/('封包 測試 '+platform)
        destination.mkdir()
        for name, data in files.items():
            path = destination/name
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(data)
            path.chmod(modes[name])
        root = destination/package['root']
        resource = subprocess.check_output([str(a.build/'package-resources'),'-root',str(root)],text=True)
        counts = json.loads(resource)
        assert counts['illustrations'] == 179 and counts['languages'] == 5
        if platform != 'windows':
            launcher = root/manifest['launcher']
            subprocess.run(['sh','-n',str(launcher)],check=True)
            assert subprocess.check_output([str(launcher),'-version'],text=True).strip() == index['version']
        records.append({'platform':platform,'archive_sha256':package['sha256'],'unpacked_root':str(root),
                        'files_verified':len(files),'resources':counts,'manifest_sha256':sha(manifest_raw),
                        'native_execution':False,'scope':'archive, header, full content, actual resource loaders; GUI handled separately'})
        print('PASS package',platform,len(files),'files',flush=True)
    # Remove a real sealed illustration in the unpacked Linux package. The
    # same production resource auditor must reject its missing palette variant.
    root = Path(records[0]['unpacked_root'])
    art = root/'materials/illustrations-ready-v1'
    manifest = json.loads((art/'manifest.json').read_text())
    image = next(r for r in manifest['images'] if r['id'] == 'a04-00')['variants'][0]['file']
    path = art/image
    backup = path.with_suffix('.removed')
    path.rename(backup)
    try:
        result = subprocess.run([str(a.build/'package-resources'),'-root',str(root)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        assert result.returncode != 0 and b'illustration a04-00' in result.stderr
    finally:
        backup.rename(path)
    result = {'schema':1,'version':index['version'],'source_commit':index['source_commit'],
              'index_sha256':sha(index_raw),'packages':records,'missing_sealed_art_rejected':True,
              'tool_sha256':sha(Path(__file__).read_bytes()),'native_macOS_tested':False}
    (a.out/'package-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('PASS three packages and effective missing-art control;',sha((a.out/'package-verification.json').read_bytes()))


if __name__ == '__main__':
    main()
