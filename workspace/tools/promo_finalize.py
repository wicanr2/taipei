#!/usr/bin/env python3
"""041：重用已完成且已解碼通過的影片，收尾縮圖與來源清單。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil

from promo_render import audio_check, contact_sheet, probe, run, sha


def main():
    ap=argparse.ArgumentParser()
    for name in ['run','opening-run','work','out']:ap.add_argument('--'+name,type=Path,required=True)
    a=ap.parse_args();out=a.out;work=a.work
    assert out.is_dir() and out.stat().st_uid==os.getuid() and not (out/'verification.json').exists()
    os.environ['MAGICK_THREAD_LIMIT']='1';os.environ['OMP_NUM_THREADS']='1'
    report=json.loads((a.run/'capture-result.json').read_text())
    assert report['capture_prefix_validated'] and sha(a.run/'session.mkv')==report['session_sha256']
    movie=out/('Taipei-'+report['version']+'-promo.mp4');info=probe(movie)
    old=json.loads((out/'ffprobe.json').read_text());assert info['format']['size']==old['format']['size']
    v=next(s for s in info['streams'] if s['codec_type']=='video');audio=next(s for s in info['streams'] if s['codec_type']=='audio')
    assert (v['codec_name'],v['width'],v['height'],v['r_frame_rate'])==('h264',1280,800,'30/1')
    assert audio['codec_name']=='aac' and audio['channels']==2 and audio['sample_rate']=='48000'
    assert abs(float(v['duration'])-float(audio['duration']))<.1
    duration=float(v['duration'])
    log=(out/'decode-audio-black-freeze.log').read_text()
    assert 'black_start:' not in log and 'video:' in log and 'audio:' in log and 'Overall' in log
    source_audio=audio_check(out/'original-game-music.wav');final_audio=audio_check(work/'final-audio.wav')
    assert not source_audio['silence_windows']
    assert all(s['start']<1.1 or s['start']+s['duration']>duration-2.1 for s in final_audio['silence_windows'])
    events=report['events'];opening_events=json.loads((a.opening_run/'events.json').read_text())
    def when(label,opening=False):return next(e['video_time'] for e in (opening_events if opening else events) if e['label']==label)
    timeline=[];position=0
    for part in sorted(work.glob('[0-9][0-9]-*.mp4')):
        name=part.stem[3:];seconds=float(probe(part)['format']['duration']);speed=1;start=None;kind='card';source=part.name
        if name=='opening':start=when('opening-hd-return',True)+4;kind='opening';source='opening/session.mkv'
        elif name=='city-explore':start=when('gameplay-start');speed=(when('gameplay-end')-start)/14;kind='gameplay-navigation-edit';source='session.mkv'
        elif name=='F12-original-HD':start=when('city-original')-1;kind='theme-switch';source='session.mkv'
        elif name=='traditional-chinese':start=when('locale-zh-Hant');kind='locale-reading';source='session.mkv'
        elif name.startswith('F11-picker-'):
            lang=name[len('F11-picker-'):];start=when('picker-'+lang)-.3;speed=max(1,(when('locale-'+lang)-start)/3);kind='locale-picker-edit';source='session.mkv'
        elif name.startswith('F11-'):start=when('locale-'+name[4:]);kind='locale-reading';source='session.mkv'
        if source=='session.mkv':assert start+seconds*speed<=report['last_valid_video_time']+.1
        timeline.append({'name':name,'start':round(position,3),'duration':seconds,'source_start':start,'speed':speed,'kind':kind,'source':source,'part_sha256':sha(part)})
        position+=seconds
    assert abs(position-duration)<.1 and len(timeline)==15
    sample_names=['opening','city-explore','F12-original-HD-0','F12-original-HD-1','traditional-chinese','F11-zh-Hans','F11-ja','F11-ko','F11-en']
    samples=[]
    for name in sample_names:
        if name.startswith('F12-original-HD-'):
            t=next(t for t in timeline if t['name']=='F12-original-HD');at=t['start']+(2 if name.endswith('-0') else 8)
        else:
            t=next(t for t in timeline if t['name']==name);at=t['start']+t['duration']-1
        path=out/(name+'.png');assert path.is_file()
        samples.append({'file':path.name,'time':at,'sha256':sha(path)})
    contact_sheet([out/s['file'] for s in samples],out/'contact-sheet.png')
    for name,at in [('title',2),('ending',duration-2)]:
        path=out/(name+'.png')
        run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-n','-ss',str(at),'-i',movie,'-frames:v','1','-threads','1',path])
        samples.append({'file':path.name,'time':at,'sha256':sha(path)})
    rights={'schema':1,'distribution':'local-only; no public upload authorized','version':report['version'],
        'video_source':'actual packaged Linux GUI, normal original EXE via dosgolem; host-muted city gameplay, no custom step rate or injected state',
        'music_source':'same formal package, unmuted normal opening; isolated PulseAudio monitor of fixed upstream YMFM original OPL output',
        'music_edit':{'source_session_sha256':sha(a.opening_run/'session.mkv'),'source_start_seconds':3,'source_duration_seconds':source_audio['duration'],
                      'crossfade_loop_seconds':.8,'looped':True,'synchronized_gameplay_audio':False,'gain':2,'tempo_change':False},
        'video_edit':'actual gameplay cuts; navigation and picker timing listed per shot; no invented gameplay frames',
        'opening_capture':{'run':str(a.opening_run),'completed_flow':False,'scope':'valid opening/audio only; later empty-land script assumption failed and is excluded'},
        'gameplay_capture':{'run':str(a.run),'raw_flow_completed':False,'required_prefix_validated':True,'unused_tail':report['unused_tail'],
                            'capturing_driver_limit':report['capturing_driver_limit']},
        'original_game_sha256':'798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3',
        'music_public_distribution_rights':'not established; local only','native_windows_macos_audio_tested':False,'human_listening':False}
    (out/'rights.json').write_text(json.dumps(rights,ensure_ascii=False,indent=2)+'\n')
    for name in ['capture-result.json','full-package-check.json','events.json']:shutil.copyfile(a.run/name,out/name)
    result={'schema':1,'issue':63,'version':report['version'],'movie':movie.name,'sha256':sha(movie),'bytes':movie.stat().st_size,'duration':duration,
        'timeline':timeline,'source_audio':source_audio,'final_audio':final_audio,'full_decode_passed':True,'full_decode_reused':True,
        'decode_log_sha256':sha(out/'decode-audio-black-freeze.log'),'black_intervals':[],
        'freeze_events':re.findall(r'freeze_(?:start|end|duration): [0-9.]+',log),
        'freeze_policy':'title cards, paused original/HD city and five-locale budget reading intentionally hold; navigation retains real input movement',
        'sample_frames':samples,'human_visual_review_pending':True,'human_listening':False,'original_packages_unchanged':True,
        'render_tool_sha256':sha(work/'executed-render.py'),'finalizer_tool_sha256':sha(Path(__file__))}
    (out/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    files=[{'file':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(out.iterdir()) if p.is_file()]
    (out/'SHA256SUMS.json').write_text(json.dumps({'schema':1,'version':report['version'],'local_only':True,'files':files},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'PASS':True,'movie':str(movie),'duration':duration,'sha256':sha(movie),'audio_peak_dbfs':final_audio['peak_dbfs']},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
