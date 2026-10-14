#!/usr/bin/env python3
"""040：由固定輸入建立三平台full-local封包；不覆寫已存在版本。"""
import argparse
import gzip
import io
import json
import os
from pathlib import Path
import re
import tarfile
import zipfile

from full_asset_catalog import sha


def shell_launcher(platform, originals):
    user = '${XDG_DATA_HOME:-${HOME:?}/.local/share}/taipei-dosgolem' if platform == 'linux' else '${HOME:?}/Library/Application Support/Taipei dosgolem'
    alert = 'printf "%s\\n" "Missing original game data: $data_name" >&2'
    if platform == 'macos':
        alert += '\n    /usr/bin/osascript -e \'display alert "Taipei: missing original game data"\' >/dev/null 2>&1 || true'
    return f'''#!/bin/sh
set -eu
base_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
if [ "${{1:-}}" = -version ] || [ "${{1:-}}" = --version ]; then
  cat "$base_dir/VERSION"
  exit 0
fi
for data_name in {' '.join(originals)}; do
  if [ ! -f "$base_dir/original/$data_name" ]; then
    {alert}
    exit 1
  fi
done
taipei_user_root="{user}"
mkdir -p "$taipei_user_root/saves" "$taipei_user_root/receipts"
exec "$base_dir/Taipei" -original "$base_dir/original" -saves "$taipei_user_root/saves" -receipts "$taipei_user_root/receipts" -materials "$base_dir/materials" -catalog "$base_dir/locales/ui.tsv" -theme hd-b "$@"
'''.encode()


def windows_launcher(originals):
    checks = ''.join('if not exist "%~dp0original\\'+name+'" goto missing\n' for name in originals)
    data = r'''@echo off
setlocal
if "%~1"=="-version" goto version
if "%~1"=="--version" goto version
'''+checks+r'''if defined LOCALAPPDATA (
  set "taipei_user_root=%LOCALAPPDATA%\TaipeiDosgolem"
) else (
  set "taipei_user_root=%USERPROFILE%\AppData\Local\TaipeiDosgolem"
)
if not exist "%taipei_user_root%\saves" mkdir "%taipei_user_root%\saves"
if not exist "%taipei_user_root%\receipts" mkdir "%taipei_user_root%\receipts"
"%~dp0Taipei.exe" -original "%~dp0original" -saves "%taipei_user_root%\saves" -receipts "%taipei_user_root%\receipts" -materials "%~dp0materials" -catalog "%~dp0locales\ui.tsv" -theme hd-b %*
set "taipei_exit=%ERRORLEVEL%"
if not "%taipei_exit%"=="0" pause
exit /b %taipei_exit%
:version
type "%~dp0VERSION"
exit /b 0
:missing
echo Taipei: missing original game data. Restore the original folder.
pause
exit /b 1
'''
    return data.replace('\n', '\r\n').encode('ascii')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', type=Path, required=True)
    ap.add_argument('--build', type=Path, required=True)
    ap.add_argument('--dist', type=Path, required=True)
    a = ap.parse_args()
    inputs_raw = (a.build/'inputs.json').read_bytes()
    lock = json.loads(inputs_raw)
    version = lock['version']
    assert re.fullmatch(r'v\.[0-9]+\.[0-9]+\.[0-9]+-[0-9]{8}', version)
    assert a.dist.name == version and not a.dist.exists() and a.dist.parent.stat().st_uid == os.getuid()
    source = a.project/'workspace/cache'/('release-source-'+version)
    originals = a.project/'rs201 模擬台北/模擬台北/RS201'
    material_root = a.project/'workspace/prototypes/hd-style'
    a.dist.mkdir()
    (a.dist/'full-local').mkdir()
    (a.dist/'smoke').mkdir()
    packages = []
    for target, platform, arch, binary, launcher in [
        ('linux-amd64', 'linux', 'amd64', 'taipei-linux-amd64', 'start.sh'),
        ('windows-amd64', 'windows', 'amd64', 'taipei-windows-amd64.exe', 'Start.cmd'),
        ('macos-universal', 'macos', 'amd64+arm64', 'taipei-macos-universal', 'start.command')]:
        payload = {}

        def add(name, raw, mode=0o644, rights='project RRSAL-1.0'):
            assert name not in payload and not Path(name).is_absolute() and '..' not in Path(name).parts
            payload[name] = (raw, mode, rights)

        def add_locked(name, path, record, mode=0o444, rights='local-only original'):
            raw = path.read_bytes()
            assert len(raw) == record['bytes'] and sha(raw) == record['sha256'], name
            add(name, raw, mode, rights)

        record = next(r for r in lock['binaries'] if r['file'] == binary)
        add_locked('Taipei.exe' if platform == 'windows' else 'Taipei', a.build/binary, record, 0o755, 'project and linked third-party code')
        for r in lock['original']:
            add_locked('original/'+r['file'], originals/r['file'], r)
        for r in lock['materials']:
            add_locked('materials/'+r['file'], material_root/r['file'], r, rights=r['rights'])
        for r in lock['licenses']:
            add_locked('third-party/'+r['file'], a.build/'third-party'/r['file'], r, 0o644, 'third-party license')
        add('LICENSE', (source/'LICENSE').read_bytes())
        catalog = (source/'workspace/app/locales/ui.tsv').read_bytes()
        assert sha(catalog) == lock['catalog_sha256']
        add('locales/ui.tsv', catalog)
        add('VERSION', (version+'\n').encode())
        names = [r['file'] for r in lock['original']]
        add(launcher, windows_launcher(names) if platform == 'windows' else shell_launcher(platform, names), 0o755)
        save_path = {'linux':'${XDG_DATA_HOME:-$HOME/.local/share}/taipei-dosgolem/',
                     'windows':'%LOCALAPPDATA%\\TaipeiDosgolem\\',
                     'macos':'$HOME/Library/Application Support/Taipei dosgolem/'}[platform]
        readme = f'''模擬台北 dosgolem 與 HD 呈現
版本：{version}
平台：{target}
來源提交：{lock['source_commit']}

執行 {launcher}。請先完整解壓縮，保留 original、materials 及 locales 目錄。
預設為1280×800 HD，使用Noto高清黑體。
F11：繁中／簡中／日文／韓文／英文。F12：原版／HD。Shift+F1：Help。
原版F1仍為離開；原版程式負責規則與存檔。
存檔／語言設定在 {save_path}saves，診斷收據在 receipts，與遊戲資料分開。

這是只留本機的完整版。原版與原作衍生HD的公開散布權未取得，不上傳或公開發布。
自有程式依LICENSE的RRSAL-1.0；Noto及實際連結元件授權見third-party。
Linux正常GUI與原版存退讀已抽驗；Windows另以Wine預檢。
macOS兩架構與啟動結構已核對，Windows／macOS真機與音訊人耳未驗。
本包無簽章／公證；來源、逐檔雜湊及平台限制見manifest.json。
未逐項試玩所有事件／成功結局。必要資料缺少時，請還原本包資料。
'''
        add('README.txt', readme.replace('\n','\r\n').encode('utf-8-sig') if platform == 'windows' else readme.encode())
        manifest = {'schema':1, 'version':version, 'source_commit':lock['source_commit'], 'platform':platform, 'architecture':arch,
                    'launcher':launcher, 'user_data':save_path, 'dosgolem_commit':lock['dosgolem_commit'],
                    'inputs_sha256':sha(inputs_raw), 'rights':'full-local only; no public Release',
                    'source_normal_gui':'039 Linux representative gameplay verified',
                    'package_validation':'see dist-all version smoke/acceptance.json',
                    'native_platform_limits':'Windows and macOS native machines untested',
                    'files':[{'file':name, 'bytes':len(raw), 'sha256':sha(raw), 'mode':oct(mode), 'rights':rights}
                             for name,(raw,mode,rights) in sorted(payload.items())]}
        add('manifest.json', (json.dumps(manifest, ensure_ascii=False, indent=2)+'\n').encode())
        root = 'Taipei-'+version+'-'+target
        filename = root+'-full-local'+('.tar.gz' if platform == 'linux' else '.zip')
        path = a.dist/'full-local'/filename
        if platform == 'linux':
            with path.open('wb') as output, gzip.GzipFile(fileobj=output, mode='wb', filename='', mtime=0) as gz, tarfile.open(fileobj=gz, mode='w') as tar:
                for name,(raw,mode,_) in sorted(payload.items()):
                    info = tarfile.TarInfo(root+'/'+name)
                    info.size,info.mode,info.uid,info.gid,info.mtime = len(raw),mode,1000,1000,0
                    tar.addfile(info, io.BytesIO(raw))
        else:
            with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
                for name,(raw,mode,_) in sorted(payload.items()):
                    info = zipfile.ZipInfo(root+'/'+name, (1980,1,1,0,0,0))
                    info.create_system,info.external_attr,info.compress_type = 3,(0o100000|mode)<<16,zipfile.ZIP_DEFLATED
                    z.writestr(info,raw,compresslevel=9)
        packages.append({'file':'full-local/'+filename,'bytes':path.stat().st_size,'sha256':sha(path.read_bytes()),
                         'platform':platform,'architecture':arch,'root':root,'manifest_sha256':sha(payload['manifest.json'][0])})
        print('PACKED', target, path.stat().st_size, sha(path.read_bytes()), flush=True)
    result = {'schema':1,'version':version,'source_commit':lock['source_commit'],'inputs_sha256':sha(inputs_raw),
              'packages':packages,'rights':'full-local only; no public Release','tool_sha256':sha(Path(__file__).read_bytes())}
    (a.dist/'SHA256SUMS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')


if __name__ == '__main__':
    main()
