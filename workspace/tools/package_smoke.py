#!/usr/bin/env python3
"""040：實際解包啟動器、B開場、F11/F12/Help及使用者目錄抽驗。"""
import argparse
import io
import json
import os
from pathlib import Path, PureWindowsPath
import shutil
import subprocess
import time
import wave
import zipfile
from array import array

from full_asset_catalog import sha


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--platform', choices=['linux', 'windows'], required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--bundle', type=Path, default=Path('/封包 測試'))
    a = ap.parse_args()
    a.out.mkdir(exist_ok=True)
    assert a.out.stat().st_uid == os.getuid() and not (a.out/'smoke-result.json').exists()
    bundle = a.bundle
    manifest = json.loads((bundle/'manifest.json').read_text())
    assert manifest['platform'] == a.platform
    version = (bundle/'VERSION').read_text().strip()
    env = os.environ.copy()
    if a.platform == 'linux':
        env['XDG_DATA_HOME'] = str(a.out/'使用者 資料')
        user_root = Path(env['XDG_DATA_HOME'])/'taipei-dosgolem'
        command = [str(bundle/'start.sh'), '-stop-file', str(a.out/'stop')]
        version_command = [str(bundle/'Taipei'), '-version']
    else:
        local = subprocess.check_output(['wine','cmd','/d','/c','echo','%LOCALAPPDATA%'],env=env,text=True,stderr=subprocess.DEVNULL).strip()
        path = PureWindowsPath(local)
        assert path.drive.upper() == 'C:'
        # Wine paths are case insensitive; resolve each actual POSIX component.
        actual = Path(env['WINEPREFIX'])/'drive_c'
        for part in path.parts[1:]:
            matches = [p for p in actual.iterdir() if p.name.casefold() == part.casefold()]
            assert len(matches) == 1, (actual, part)
            actual = matches[0]
        user_root = actual/'TaipeiDosgolem'
        stop = 'Z:'+str(a.out/'stop').replace('/','\\')
        batch = 'Z:'+str(bundle/'Start.cmd').replace('/','\\')
        command = ['wine','cmd','/d','/c','call',batch,'-mute','-steps-per-update','400000','-stop-file',stop]
        version_command = ['wine',str(bundle/'Taipei.exe'),'-version']
    got_version = subprocess.check_output(version_command,env=env,text=True,stderr=subprocess.DEVNULL).strip()
    assert got_version == version
    log = (a.out/'app.log').open('wb')
    process = subprocess.Popen(command,env=env,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL)
    receipts = user_root/'receipts'

    def current():
        try:
            raw = (receipts/'capture.zip').read_bytes()
            with zipfile.ZipFile(io.BytesIO(raw)) as z:
                s = json.loads(z.read('status.json'))
                assert sha(z.read('frame-index.bin')) == s['frame_index_sha256']
            return s,raw
        except (FileNotFoundError,zipfile.BadZipFile):
            return {},None

    def wait(predicate, label, seconds=60):
        end = time.monotonic()+seconds
        while time.monotonic() < end:
            s,raw = current()
            if predicate(s):
                print('PASS',label,s.get('steps'),flush=True)
                return s,raw
            if process.poll() is not None:
                raise RuntimeError('application exited during '+label+': '+(a.out/'app.log').read_text(errors='replace')[-1500:])
            time.sleep(.1)
        raise RuntimeError(label+' timeout: '+str(current()[0].get('hd')))

    def key(name):
        subprocess.run(['xdotool','keydown',name],check=True)
        time.sleep(.12)
        subprocess.run(['xdotool','keyup',name],check=True)

    def capture(name,raw):
        (a.out/(name+'-capture.zip')).write_bytes(raw)
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            (a.out/(name+'.png')).write_bytes(z.read('presentation.png'))

    audio = None
    try:
        first,raw = wait(lambda s:s.get('hd',{}).get('illustrations',{}).get('painted',0)>0,'packaged-B-opening',150)
        assert first['version'] == version and first['prototype'] is False and first['hd_enabled']
        assert first['original_sha256'] == '798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3'
        assert first['original_root'].replace('\\','/').lower().endswith(str(bundle/'original').lower())
        capture('opening',raw)
        windows = subprocess.check_output(['xdotool','search','--onlyvisible','--name','模擬台北'],text=True).split()
        assert windows
        window = windows[-1]
        subprocess.run(['xdotool','windowfocus',window],check=True)
        if a.platform == 'linux':
            wav = a.out/'playback.wav'
            subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-threads','1','-f','pulse',
                            '-i','taipei_package.monitor','-t','5','-ac','2','-ar','48000','-c:a','pcm_s16le',str(wav)],check=True,timeout=15,env=env)
            with wave.open(str(wav),'rb') as f:
                assert f.getsampwidth() == 2 and f.getnchannels() == 2 and f.getframerate() == 48000
                samples = array('h',f.readframes(f.getnframes()))
            peak = max(abs(v) for v in samples)
            nonzero = sum(v != 0 for v in samples)
            assert peak > 128 and nonzero > 1000, (peak,nonzero)
            audio = {'default_audio_device':True,'technical_non_silence':True,'peak':peak,'nonzero_samples':nonzero,
                     'wav_sha256':sha(wav.read_bytes()),'human_listening':False}
        key('F11')
        wait(lambda s:s.get('language_panel') is True,'packaged-F11')
        for _ in range(4):
            key('Down')
        wait(lambda s:s.get('language_selection') == 4,'packaged-English-selection')
        key('Return')
        english,raw = wait(lambda s:s.get('language') == 'en' and not s.get('language_panel'),'packaged-English')
        settings = user_root/'saves/frontend-settings.json'
        assert json.loads(settings.read_text())['language'] == 'en'
        if a.platform == 'windows':
            assert english['save_root'].replace('\\','/').lower().endswith('/taipeidosgolem/saves')
        else:
            assert english['save_root'] == str(user_root/'saves')
        subprocess.run(['xdotool','keydown','Shift_L'],check=True)
        try:
            key('F1')
        finally:
            subprocess.run(['xdotool','keyup','Shift_L'],check=True)
        opened,raw = wait(lambda s:s.get('help_panel') is True,'packaged-Help')
        capture('help-en',raw)
        subprocess.run(['import','-window',window,str(a.out/'x11-window.png')],check=True,timeout=10)
        key('Escape')
        wait(lambda s:s.get('help_panel') is False,'packaged-Help-close')
        key('F12')
        original,raw = wait(lambda s:s.get('hd_enabled') is False,'packaged-original')
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            def rgba(data,scale=False):
                args = ['convert','png:-']
                if scale:
                    args += ['-filter','point','-resize','1280x800!']
                return subprocess.check_output(args+['-depth','8','rgba:-'],input=data)
            assert rgba(z.read('frame.png'),True) == rgba(z.read('presentation.png'))
        capture('original',raw)
        key('F12')
        wait(lambda s:s.get('hd_enabled') is True,'packaged-HD-return')
        (a.out/'stop').write_text('stop\n')
        assert process.wait(timeout=15) == 0
    finally:
        if process.poll() is None:
            (a.out/'stop').write_text('stop\n')
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill();process.wait()
        log.close()
    # Exercise visible missing-data guard through the actual launcher bytes.
    missing = a.out/'missing-original'
    missing.mkdir()
    launcher = manifest['launcher']
    shutil.copy2(bundle/launcher,missing/launcher)
    shutil.copy2(bundle/'VERSION',missing/'VERSION')
    if a.platform == 'linux':
        error = subprocess.run([str(missing/launcher)],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=10)
        assert error.returncode == 1 and b'Missing original game data' in error.stderr
    else:
        missing_batch = 'Z:'+str(missing/launcher).replace('/','\\')
        error = subprocess.run(['wine','cmd','/d','/c',missing_batch],env=env,input=b'\r\n',stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=20)
        assert error.returncode == 1 and b'missing original game data' in error.stdout
    result = {'schema':1,'version':version,'platform':a.platform,'backend':'Linux Xvfb' if a.platform == 'linux' else 'Wine Xvfb',
              'actual_package_launcher':True,'checkpoint':False,'source_commit':manifest['source_commit'],
              'opening_illustrations':first['hd']['illustrations'],'language_settings_written':str(settings),
              'f11_f12_help':True,'original_nearest_pixels':True,'missing_original_visible_error':True,
              'program_version':got_version,'audio':audio,'normal_native_DOS_exit_tested':False,
              'scope':'actual packaged cold start and frontend/path checks; complete native save/load/DOS exit uses039 Linux receipts',
              'tool_sha256':sha(Path(__file__).read_bytes())}
    (a.out/'smoke-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('PASS packaged',a.platform,version,sha((a.out/'smoke-result.json').read_bytes()))


if __name__ == '__main__':
    main()
