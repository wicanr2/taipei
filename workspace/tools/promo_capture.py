#!/usr/bin/env python3
"""041：三實包遊戲檔回核，以及正式 Linux 正常玩家路徑錄影。"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import tarfile
import time
import zipfile

from hd_source_audit import cell, MATERIAL, scene
from promo_render import audio_check

LANGS = ['zh-Hant', 'zh-Hans', 'ja', 'ko', 'en']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def package_check(out):
    inventory = json.loads(Path('/runs/inventory.json').read_text())
    expected = {Path(f['path']).name: f for f in inventory['files'] if f['path'].startswith('模擬台北/RS201/')}
    assert len(expected) == 23
    index = json.loads(Path('/dist/SHA256SUMS.json').read_text())
    results = []
    for p in index['packages']:
        archive = Path('/dist')/p['file']
        assert sha(archive.read_bytes()) == p['sha256']
        if archive.suffix == '.zip':
            with zipfile.ZipFile(archive) as z:
                actual = {n.split('/original/', 1)[1]: z.read(n) for n in z.namelist() if '/original/' in n and not n.endswith('/')}
        else:
            with tarfile.open(archive, 'r:gz') as t:
                actual = {m.name.split('/original/', 1)[1]: t.extractfile(m).read() for m in t.getmembers() if m.isfile() and '/original/' in m.name}
        assert set(actual) == set(expected)
        files = []
        for name, raw in sorted(actual.items()):
            assert len(raw) == expected[name]['bytes'] and sha(raw) == expected[name]['sha256'], name
            assert (Path('/bundle/original')/name).read_bytes() == raw
            files.append({'file':name, 'bytes':len(raw), 'sha256':sha(raw)})
        results.append({'file':p['file'], 'sha256':p['sha256'], 'platform':p['platform'], 'game_files':files,
                        'full_game_included':True, 'external_game_import_needed':False})
    (out/'full-package-check.json').write_text(json.dumps({'schema':1, 'version':index['version'], 'packages':results}, ensure_ascii=False, indent=2)+'\n')
    print('PASS 三平台實包包含相同的 23 個原版遊戲檔', flush=True)


def audio_probe(out):
    """#64：預設收據頻率，音訊單獨擷取；兩個正常冷啟動負載。"""
    results=[]
    for theme in ['hd-b','original']:
        root=out/theme;root.mkdir()
        env=os.environ.copy();env['XDG_DATA_HOME']=str(root/'user-data')
        log=(root/'app.log').open('wb')
        if env.get('TAIPEI_PROBE_BINARY'):
            command=[env['TAIPEI_PROBE_BINARY'],'-original','/bundle/original','-saves',str(root/'saves'),
                     '-receipts',str(root/'user-data/taipei-dosgolem/receipts'),'-materials','/bundle/materials','-catalog','/bundle/locales/ui.tsv',
                     '-theme',theme,'-stop-file',str(root/'stop')]
            env['TAIPEI_CPU_PROFILE']=str(root/'cpu.pprof')
        else:
            command=['/bundle/start.sh','-theme',theme,'-stop-file',str(root/'stop')]
        game=subprocess.Popen(command,env=env,stdout=log,stderr=subprocess.STDOUT)
        path=root/'user-data/taipei-dosgolem/receipts/capture.zip'
        def status():
            try:
                with zipfile.ZipFile(path) as z:return json.loads(z.read('status.json'))
            except (FileNotFoundError,zipfile.BadZipFile):return {}
        try:
            deadline=time.monotonic()+20
            while time.monotonic()<deadline:
                w=subprocess.run(['xdotool','search','--onlyvisible','--pid',str(game.pid)],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True)
                if w.returncode==0:break
                time.sleep(.1)
            assert w.returncode==0
            window=w.stdout.split()[-1]
            subprocess.run(['xdotool','windowmove',window,'0','0','windowfocus','--sync',window],check=True,timeout=10)
            assert subprocess.check_output(['xdotool','getwindowfocus'],text=True).strip()==window
            deadline=time.monotonic()+20
            if env.get('TAIPEI_AUDIO_NO_PERIODIC'):
                while time.monotonic()<deadline:
                    w=subprocess.run(['xdotool','search','--onlyvisible','--name','模擬台北'],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
                    if w.returncode==0:break
                    time.sleep(.1)
                assert w.returncode==0
            else:
                while not status().get('steps') and time.monotonic()<deadline:time.sleep(.1)
                assert status().get('steps')
            time.sleep(3);before=status();start=time.monotonic()
            subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-n','-f','pulse','-i','taipei_promo.monitor',
                            '-t','20','-ar','48000','-ac','2','-c:a','pcm_s16le',str(root/'playback.wav')],check=True,timeout=30,env=env)
            elapsed=time.monotonic()-start
            (root/'stop').write_text('stop\n');assert game.wait(timeout=15)==0
            after=status()
            if env.get('TAIPEI_AUDIO_NO_PERIODIC'):
                before={'steps':0,'audio':{'frames':0,'ring':{'SilentBytes':0}}}
            results.append({'theme':theme,'elapsed':elapsed,'before':before['audio'],'after':after['audio'],
                'step_delta':after['steps']-before['steps'],'audio_seconds_delta':(after['audio']['frames']-before['audio']['frames'])/48000,
                'silent_seconds_delta':(after['audio']['ring']['SilentBytes']-before['audio']['ring']['SilentBytes'])/192000,
                'recorded_audio_sha256':sha((root/'playback.wav').read_bytes()),'periodic_receipts':not bool(env.get('TAIPEI_AUDIO_NO_PERIODIC')),
                'window_focus_confirmed':True,'recorded_wave':audio_check(root/'playback.wav'),
                'counter_window':'before is latest periodic snapshot; after is exact graceful final; WAV duration is the recording window'})
            print(json.dumps(results[-1],ensure_ascii=False),flush=True)
        finally:
            (root/'stop').write_text('stop\n')
            try:game.wait(timeout=15)
            except subprocess.TimeoutExpired:game.kill();game.wait()
            log.close()
    (out/'audio-probe.json').write_text(json.dumps({'schema':1,'issue':64,'default_receipt_frequency':True,'video_capture':False,
        'cpu_affinity':sorted(os.sched_getaffinity(0)),'results':results},ensure_ascii=False,indent=2)+'\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--audio-probe', action='store_true')
    a = ap.parse_args(); out = a.out
    assert out.stat().st_uid == os.getuid() and not (out/'capture-result.json').exists()
    if a.audio_probe:
        audio_probe(out);return
    package_check(out)
    bundle = Path('/bundle'); manifest = json.loads((bundle/'manifest.json').read_text())
    env = os.environ.copy(); env['XDG_DATA_HOME'] = str(out/'user-data')
    receipts = out/'user-data/taipei-dosgolem/receipts'
    events = []; shots = []; recorder = None; recording_start = None
    log = (out/'app.log').open('wb')
    command = [str(bundle/'start.sh'), '-stop-file', str(out/'stop')]
    game = subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT)

    def current():
        try:
            raw = (receipts/'capture.zip').read_bytes()
            with zipfile.ZipFile(io.BytesIO(raw)) as z:
                s = json.loads(z.read('status.json')); frame = z.read('frame-index.bin')
                assert sha(frame) == s['frame_index_sha256']
            return s, raw, frame
        except (FileNotFoundError, zipfile.BadZipFile):
            return {}, None, None

    def mark(label, **extra):
        s, raw, frame = current()
        e = {'label':label, 'video_time':round(time.monotonic()-recording_start, 3) if recording_start else None,
             'steps':s.get('steps'), 'language':s.get('language'), 'hd_enabled':s.get('hd_enabled'),
             'map_origin':s.get('map_origin'), 'frame_index_sha256':s.get('frame_index_sha256'), **extra}
        events.append(e); (out/'events.json').write_text(json.dumps(events, ensure_ascii=False, indent=2)+'\n')
        print('EVENT', label, e['video_time'], e['steps'], flush=True)
        return e

    def wait(pred, label, seconds=120):
        end = time.monotonic()+seconds
        while time.monotonic()<end:
            s, raw, frame = current()
            if pred(s):
                print('PASS', label, s.get('steps'), flush=True)
                return s
            if game.poll() is not None:
                raise RuntimeError(label+': game exited; '+(out/'app.log').read_text(errors='replace')[-1000:])
            time.sleep(.08)
        raise RuntimeError(label+': '+str(current()[0].get('hd')))

    def front(key):
        subprocess.run(['xdotool','keydown',key], check=True); time.sleep(.12)
        subprocess.run(['xdotool','keyup',key], check=True)

    def native(key, label):
        before = current()[0]
        ascii_keys = {'space':(32,0x39),'Tab':(9,0x0f),'Escape':(27,1),'0':(48,0x0b)}
        scan = {'Left':0x4b,'Right':0x4d,'Up':0x48,'Down':0x50, **{f'F{i}':0x3a+i for i in range(1,7)}}.get(key)
        if key in ascii_keys:
            code, scan = ascii_keys[key]; matches = lambda k:k.get('Key')==code
        else:
            assert scan is not None
            matches = lambda k:k.get('Word')==scan<<8
        count = sum(matches(k) for k in before.get('key_reads',[]))
        breaks = sum(k.get('kind')=='keyboard' and k.get('scan')==scan+128 for k in before.get('inputs',[]))
        front(key)
        after = wait(lambda s:sum(matches(k) for k in s.get('key_reads',[]))==count+1 and
                     sum(k.get('kind')=='keyboard' and k.get('scan')==scan+128 for k in s.get('inputs',[]))>breaks,
                     label)
        mark(label, key=key, original_read=next(k for k in reversed(after['key_reads']) if matches(k)))
        return after

    def shot(label):
        s, raw, frame = current(); (out/(label+'-capture.zip')).write_bytes(raw)
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            (out/(label+'.png')).write_bytes(z.read('presentation.png'))
        shots.append({'label':label, 'capture_sha256':sha(raw), 'language':s['language'], 'hd_enabled':s['hd_enabled']})
        mark(label); return s, frame

    try:
        wait(lambda s:s.get('steps',0)>0, 'cold-start')
        ids = subprocess.check_output(['xdotool','search','--onlyvisible','--name','模擬台北'], text=True).split()
        window = ids[-1]
        subprocess.run(['xdotool','windowmove',window,'0','0','windowfocus',window], check=True)
        video_log = (out/'record.log').open('wb')
        recording_start = time.monotonic()
        recording_command = ['ffmpeg','-nostdin','-hide_banner','-loglevel','warning','-n',
            '-thread_queue_size','512','-f','x11grab','-framerate','30','-video_size','1280x800','-draw_mouse','0','-i',':99+0,0',
            '-thread_queue_size','512','-f','pulse','-i','taipei_promo.monitor',
            '-map','0:v','-map','1:a','-c:v','libx264','-preset','ultrafast','-crf','18','-threads','2',
            '-pix_fmt','yuv420p','-af','aresample=async=1:first_pts=0','-ar','48000','-ac','2','-c:a','pcm_s16le',str(out/'session.mkv')]
        recorder = subprocess.Popen(recording_command, env=env, stdout=video_log, stderr=subprocess.STDOUT)
        mark('recording-start')
        wait(lambda s:s.get('hd',{}).get('illustrations',{}).get('painted',0)>0, 'opening-art',180)
        shot('opening-hd'); time.sleep(4)
        front('F12'); wait(lambda s:s.get('hd_enabled') is False,'opening-original');shot('opening-original');time.sleep(4)
        front('F12'); wait(lambda s:s.get('hd_enabled') is True,'opening-hd-return');mark('opening-hd-return')
        wait(lambda s:s.get('steps',0)>=700_000_000, 'intro',180)
        front('space'); mark('skip-opening')
        wait(lambda s:s.get('steps',0)>=800_000_000, 'intro-wait',90)
        front('space');wait(lambda s:s.get('hd',{}).get('panel')=='main','main');shot('main-hd')
        native('Right','scenario-choice');native('space','scenario-open');native('space','scenario-city')
        native('space','instructions');native('space','city-start')
        wait(lambda s:s.get('hd',{}).get('font_labels')==6,'city-ready')
        native('0','pause')
        initial, frame = shot('city-hd')
        assert any(f.get('Op')=='read' and f.get('Name','').lower()=='disa1.dsa' for f in initial['file_ops'])
        assert scene(initial, frame)
        mark('gameplay-start');time.sleep(2)
        # 原生工具列從 0 開始，Down 選公路／捷運。遊標與施工均由 DOS 處理。
        native('Down','road-tool');native('space','road-submenu')
        wait(lambda s:s.get('hd',{}).get('panel')=='tool-02','road-menu-ready');time.sleep(2)
        native('space','road-confirm')
        # DISA1 的完整已知陸地，選離左上最近的 5×5 地景，避免猜測畫面。
        frame = current()[2]
        candidates = [(x,y) for y in range(2,13) for x in range(2,26)
                      if all(set(cell(frame,5+(x+dx)*9,34+(y+dy)*9))<=MATERIAL and
                             not set(cell(frame,5+(x+dx)*9,34+(y+dy)*9)) & set(range(144,148))
                             for dy in range(-2,3) for dx in range(-2,3))]
        assert candidates, 'DISA1 沒有完整已知施工陸地'
        target = min(candidates,key=lambda p:p[0]+p[1]);cursor=[0,0]
        for axis, names in [(0,('Left','Right')),(1,('Up','Down'))]:
            while cursor[axis]!=target[axis]:
                d=1 if cursor[axis]<target[axis] else -1
                native(names[d>0], 'road-walk');cursor[axis]+=d
        before = current()[0];old_budget=int(before['hd']['footer_text'][3])
        native('space','road-place')
        native('Right','uncover-road');native('Right','uncover-road-2')
        placed, frame = shot('road-constructed')
        assert int(placed['hd']['footer_text'][3])<old_budget, '原版未扣施工費'
        mark('construction-verified',before_budget=old_budget,after_budget=int(placed['hd']['footer_text'][3]),cell=list(target))
        time.sleep(4)
        # Tab 回工具列，再選工具零；正常方向鍵捲動到新區域。
        native('Tab','toolbar-return');native('Up','bulldozer-tool');native('space','map-cursor')
        for i in range(32): native('Right','city-pan-'+str(i))
        wait(lambda s:s.get('map_origin',{}).get('X',0)>initial['map_origin']['X'],'city-scrolled')
        shot('city-scrolled');mark('gameplay-end');time.sleep(3)
        before = current()[0]
        front('F12');wait(lambda s:s.get('hd_enabled') is False,'city-original');original,_=shot('city-original')
        assert before['frame_index_sha256']==original['frame_index_sha256'] and before['key_reads']==original['key_reads']
        time.sleep(5)
        front('F12');wait(lambda s:s.get('hd_enabled') is True,'city-HD-return');shot('city-HD-return');time.sleep(5)
        # 預算資訊在五語系有足夠可讀文字，展示真實選單及原版數值。
        native('F3','budget-menu');wait(lambda s:s.get('hd',{}).get('panel')=='city-f3','budget-menu-ready')
        for _ in range((0-current()[0]['hd']['panel_selection'])%3): native('Down','budget-select')
        native('space','budget-open');wait(lambda s:s.get('hd',{}).get('budget') is True,'budget-ready')
        shot('locale-zh-Hant');time.sleep(4)
        for lang in LANGS[1:]:
            before=current()[0];front('F11');opened=wait(lambda s:s.get('language_panel') is True,'F11-picker')
            mark('picker-'+lang);time.sleep(1)
            front('Down');wait(lambda s:s.get('language_selection')==LANGS.index(lang),'locale-choice')
            front('Return');after=wait(lambda s:s.get('language')==lang and not s.get('language_panel'),'locale-'+lang)
            assert after['frame_index_sha256']==before['frame_index_sha256']
            assert after['key_reads']==before['key_reads']
            shot('locale-'+lang);time.sleep(4)
        native('Escape','budget-close')
        # 影片尾聲回城市，保持英文選擇，展示前端 Help。
        subprocess.run(['xdotool','keydown','Shift_L'],check=True)
        try:front('F1')
        finally:subprocess.run(['xdotool','keyup','Shift_L'],check=True)
        wait(lambda s:s.get('help_panel') is True,'help');shot('help-en');time.sleep(4)
        front('Escape');wait(lambda s:s.get('help_panel') is False,'help-close')
        shot('final-city');time.sleep(3)
        final=current()[0];mark('recording-end')
        recorder.send_signal(signal.SIGINT);assert recorder.wait(timeout=20) in (0,255);video_log.close();recorder=None
        result={'schema':1,'issue':63,'version':manifest['version'],'source_commit':manifest['source_commit'],
            'binary_sha256':sha((bundle/'Taipei').read_bytes()),'normal_gui':True,'checkpoint':False,'state_injection':False,
            'scenario':'DISA1.DSA','actual_package_launcher':True,'default_unmuted_timing':True,
            'cpu_affinity':sorted(os.sched_getaffinity(0)),
            'construction_verified_by_native_cost':True,'native_dos_exit_tested':False,
            'all_five_locales':LANGS,'f12_original_hd_same_native_frame':True,
            'audio':final['audio'],'events':events,'screenshots':shots,'recording_command':recording_command,
            'session_sha256':sha((out/'session.mkv').read_bytes()),'tool_sha256':sha(Path(__file__).read_bytes())}
        (out/'capture-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        print('PASS 正式封包遊玩、施工、捲動、F12、F11 五語系與音訊擷取',flush=True)
    finally:
        if recorder and recorder.poll() is None:
            recorder.send_signal(signal.SIGINT)
            try:recorder.wait(timeout=10)
            except subprocess.TimeoutExpired:recorder.kill();recorder.wait()
        if game.poll() is None:
            (out/'stop').write_text('stop\n')
            try:game.wait(timeout=15)
            except subprocess.TimeoutExpired:game.kill();game.wait()
        log.close()


if __name__=='__main__':
    main()
