#!/usr/bin/env python3
"""041 / #63：正常 GUI 錄影剪輯、原版實際錄音配樂、成片技術檢查。"""
import argparse
from array import array
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import wave


def run(args, **kwargs):
    return subprocess.run([str(x) for x in args], check=True, **kwargs)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))


def audio_check(wav):
    with wave.open(str(wav),'rb') as f:
        assert f.getsampwidth()==2 and f.getnchannels()==2 and f.getframerate()==48000
        frames=f.getnframes();samples=array('h',f.readframes(frames))
    peak=max(abs(v) for v in samples); nonzero=sum(v!=0 for v in samples)
    rms=math.sqrt(sum(v*v for v in samples)/len(samples)); dc=sum(samples)/len(samples)
    clipping=sum(abs(v)>=32767 for v in samples)
    # 以 100 ms 的 RMS 視窗找長靜音；保留實際安靜處，不憑非零樣本宣稱全曲正常。
    windows=[]
    for i in range(0,len(samples),9600):
        chunk=samples[i:i+9600]
        windows.append(math.sqrt(sum(v*v for v in chunk)/len(chunk)))
    silence=[];start=None
    for i, rms_window in enumerate(windows+[float('inf')]):
        if rms_window<3 and start is None:start=i
        elif rms_window>=3 and start is not None:
            if i-start>=5:silence.append({'start':round(start*.1,3),'duration':round((i-start)*.1,3)})
            start=None
    assert peak>128 and nonzero>48000 and rms>20
    assert clipping==0 and abs(dc)<100
    return {'file':wav.name,'sha256':sha(wav),'sample_rate':48000,'channels':2,'duration':frames/48000,
            'peak_s16':peak,'peak_dbfs':20*math.log10(peak/32768),'rms_s16':rms,'dc_s16':dc,
            'nonzero_samples':nonzero,'clipped_samples':clipping,'silence_windows':silence,
            'silence_threshold_rms_s16':3,'silence_min_seconds':.5,'human_listening':False}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();r=a.run;out=a.out
    assert r.is_dir() and out.parent.is_dir() and not out.exists()
    assert out.parent.stat().st_uid==os.getuid()
    report=json.loads((r/'capture-result.json').read_text());assert report['normal_gui'] and report['all_five_locales']==['zh-Hant','zh-Hans','ja','ko','en']
    assert sha(r/'session.mkv')==report['session_sha256']
    out.mkdir();build=r/'edit';assert not build.exists();build.mkdir()
    font=Path('/bundle/materials/fonts/NotoSansCJKtc-Regular.otf');assert font.is_file()
    events=report['events']
    def when(label):
        return next(e['video_time'] for e in events if e['label']==label)
    # 第一份本作影片。從本作城市草綠介面取色，採格線、黑體、實機剪輯。
    histogram=subprocess.check_output(['convert',str(r/'city-hd.png'),'-resize','100x100','-colors','8','-depth','8','-format','%c','histogram:info:-'],text=True)
    (out/'theme.json').write_text(json.dumps({'name':'城市草綠與圖格','background':'#18352a','accent':'#b9cd65','text':'#f5f1dc',
        'font_sha256':sha(font),'source':'city-hd.png','histogram':histogram,'first_project_promo':True,
        'differences_from_reference_template':['本作草綠色而非奇幻紫金','城市圖格母題','Noto黑體','實際操作錄影為主']},ensure_ascii=False,indent=2)+'\n')
    geometry=[]
    def card(name, lines):
        path=build/(name+'.png')
        args=['convert','-size','1280x800','gradient:#244f3d-#0d211a','-stroke','#365b45','-strokewidth','1']
        for x in range(0,1280,80):args+=['-draw',f'line {x},0 {x},800']
        for y in range(0,800,80):args+=['-draw',f'line 0,{y} 1280,{y}']
        args+=['-stroke','none','-fill','#b9cd65','-draw','rectangle 88,130 100,670']
        for text,size,y,color in lines:
            wh=subprocess.check_output(['convert','-font',str(font),'-pointsize',str(size),'label:'+text,'-format','%w %h','info:'],text=True).split()
            w,h=map(int,wh);assert w<=1080 and 0<=y and y+h<=760
            geometry.append({'card':name,'text':text,'x':140,'y':y,'width':w,'height':h,'safe':[120,100,1080,660]})
            args+=['-font',str(font),'-pointsize',str(size),'-fill',color,'-gravity','NorthWest','-annotate',f'+140+{y}',text]
        run(args+[path]);return path
    intro=card('title',[('模擬台北',92,180,'#f5f1dc'),('dosgolem 重新打包 · HD 版本',40,330,'#b9cd65'),
                        ('1280 × 800  |  遊戲中即時切換',32,440,'#f5f1dc'),('本機完整版 · 實際遊玩錄影',28,570,'#b9cd65')])
    controls=card('switches',[('同一座城市，切換觀看方式',54,180,'#f5f1dc'),('F12  原版／HD',44,320,'#b9cd65'),
                            ('F11  繁中／簡中／日文／韓文／英文',32,430,'#f5f1dc'),('本片配樂取自本次遊戲開場實際錄音',26,570,'#b9cd65')])
    ending=card('ending',[('把城市交還給玩家',64,200,'#f5f1dc'),('Windows · Linux · macOS',38,350,'#b9cd65'),
                          ('完整版含原版遊戲與 HD 素材',32,460,'#f5f1dc'),(report['version'],26,580,'#b9cd65')])
    timeline=[];segments=[];position=0
    def add(name, seconds, start=None, image=None, kind='gameplay'):
        nonlocal position
        part=build/(f'{len(segments):02d}-{name}.mp4')
        cmd=['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-n']
        if image:cmd+=['-loop','1','-framerate','30','-i',str(image)]
        else:cmd+=['-ss',str(max(0,start)),'-i',str(r/'session.mkv')]
        cmd+=['-t',str(seconds),'-an','-r','30','-vf','setsar=1,format=yuv420p','-c:v','libx264','-preset','veryfast','-crf','19','-threads','2',part]
        run(cmd)
        timeline.append({'name':name,'start':round(position,3),'duration':seconds,'source_start':start,'kind':kind,
                         'source':'session.mkv' if not image else image.name})
        segments.append(part);position+=seconds
    add('title',4,image=intro,kind='card')
    add('opening',6,start=when('opening-hd-return')+4,kind='opening')
    # 完整正常施工輸入，不加速。長走路剪去中段，以實際游標及施工收尾呈現。
    add('choose-road',6,start=when('gameplay-start'),kind='gameplay')
    add('construction',10,start=when('road-place')-3,kind='gameplay')
    add('city-scroll',10,start=when('gameplay-end')-10,kind='gameplay')
    add('switches',4,image=controls,kind='card')
    add('F12-original-HD',12,start=when('city-original')-1,kind='theme-switch')
    add('traditional-chinese',4,start=when('locale-zh-Hant'),kind='locale-reading')
    for lang in ['zh-Hans','ja','ko','en']:
        start=when('picker-'+lang)-.5;end=when('locale-'+lang)+3.5
        add('F11-'+lang,round(end-start,3),start=start,kind='locale-switch')
    add('Help',4,start=when('help-en'),kind='help-reading')
    add('ending',4,image=ending,kind='card')
    (build/'concat.txt').write_text(''.join("file '"+str(p)+"'\n" for p in segments))
    run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-n','-f','concat','-safe','0','-i',build/'concat.txt','-c','copy',build/'silent.mp4'])
    duration=float(probe(build/'silent.mp4')['format']['duration'])
    # 本次原版 OPL 播放的未加速開場錄音，保留原樣 WAV；剪輯配樂另製，明列交叉淡化循環。
    music_start=3;music_duration=min(60,when('skip-opening')-music_start-2)
    assert music_duration>=40
    run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-n','-ss',str(music_start),'-i',r/'session.mkv','-t',str(music_duration),
         '-vn','-ar','48000','-ac','2','-c:a','pcm_s16le',out/'original-game-music.wav'])
    source_audio=audio_check(out/'original-game-music.wav')
    assert not source_audio['silence_windows'], '開場配樂有長靜音，須回查來源'
    # 兩段真實錄音交叉淡化，不以短音軌截斷成片。
    music_length=source_audio['duration']
    assert duration<=music_length*2-.8
    run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-n','-i',build/'silent.mp4',
         '-i',out/'original-game-music.wav','-i',out/'original-game-music.wav',
         '-filter_complex',f'[1:a][2:a]acrossfade=d=0.8:c1=tri:c2=tri,atrim=duration={duration},volume=2,afade=t=in:st=0:d=1,afade=t=out:st={duration-2}:d=2[a]',
         '-map','0:v','-map','[a]','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-movflags','+faststart',
         out/('Taipei-'+report['version']+'-promo.mp4')])
    movie=out/('Taipei-'+report['version']+'-promo.mp4');info=probe(movie)
    video=next(s for s in info['streams'] if s['codec_type']=='video');audio=next(s for s in info['streams'] if s['codec_type']=='audio')
    assert video['codec_name']=='h264' and video['width']==1280 and video['height']==800 and video['r_frame_rate']=='30/1'
    assert audio['codec_name']=='aac' and int(audio['sample_rate'])==48000 and audio['channels']==2
    assert abs(float(video['duration'])-float(audio['duration']))<.1
    (out/'ffprobe.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n')
    run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-n','-i',movie,'-vn','-c:a','pcm_s16le',build/'final-audio.wav'])
    final_audio=audio_check(build/'final-audio.wav')
    assert all(s['start']<1.1 or s['start']+s['duration']>duration-2.1 for s in final_audio['silence_windows'])
    # 全片解碼，並輸出黑畫面與靜止檢測。選單閱讀、字卡與暫停城市的靜止是預期內容。
    check=run(['ffmpeg','-nostdin','-hide_banner','-loglevel','info','-i',movie,'-vf',
               'blackdetect=d=0.1:pic_th=0.98:pix_th=0.05,freezedetect=n=-50dB:d=3',
               '-af','astats=metadata=0:reset=0','-threads','2','-f','null','-'],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
    (out/'decode-audio-black-freeze.log').write_text(check.stderr)
    assert 'black_start:' not in check.stderr
    # 頻譜及波形便於人工複核，技術訊號不冒充人耳驗收。
    run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-n','-i',out/'original-game-music.wav',
         '-lavfi','showspectrumpic=s=1280x480:legend=1','-frames:v','1',out/'music-spectrum.png'])
    sample_names=['opening','construction','city-scroll','F12-original-HD','traditional-chinese','F11-zh-Hans','F11-ja','F11-ko','F11-en','Help']
    samples=[]
    for name in sample_names:
        item=next(t for t in timeline if t['name']==name)
        # F12 各抽一張，語系使用選擇後的實際文字畫面。
        times=[item['start']+2,item['start']+8] if name=='F12-original-HD' else [item['start']+item['duration']-1]
        for j,t in enumerate(times):
            file=out/(name+('-'+str(j) if len(times)>1 else '')+'.png')
            run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-n','-ss',str(t),'-i',movie,'-frames:v','1','-threads','1',file])
            samples.append({'file':file.name,'time':round(t,3),'sha256':sha(file)})
    run(['montage',*[out/s['file'] for s in samples],'-thumbnail','384x240','-tile','3x','-geometry','+8+8','-background','#18352a',out/'contact-sheet.png'])
    rights={'schema':1,'distribution':'local-only; no public upload authorized','version':report['version'],
            'video_source':'actual packaged Linux GUI X11 capture, normal original EXE via dosgolem; approved HD presentation',
            'music_source':'same packaged original game live OPL output via fixed upstream YMFM, recorded from isolated PulseAudio monitor',
            'music_edit':{'source_session_sha256':report['session_sha256'],'source_start_seconds':music_start,
                          'source_duration_seconds':music_duration,'crossfade_loop_seconds':.8,'looped':True,
                          'synchronized_gameplay_audio':False,'gain':2,'tempo_change':False},
            'original_game_sha256':'798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3',
            'music_public_distribution_rights':'not established; local only',
            'native_windows_macos_audio_tested':False,'human_listening':False}
    (out/'rights.json').write_text(json.dumps(rights,ensure_ascii=False,indent=2)+'\n')
    for source in ['capture-result.json','full-package-check.json','events.json']:
        shutil.copyfile(r/source,out/source)
    result={'schema':1,'issue':63,'version':report['version'],'movie':movie.name,'sha256':sha(movie),'bytes':movie.stat().st_size,
            'duration':duration,'timeline':timeline,'source_audio':source_audio,'final_audio':final_audio,
            'full_decode_passed':True,'black_intervals':[],'freeze_events':re.findall(r'freeze_(?:start|end|duration): [0-9.]+',check.stderr),
            'freeze_policy':'paused city, native budget/Help reading and title cards intentionally hold; actual operations retained',
            'text_geometry':geometry,'sample_frames':samples,'human_visual_review_pending':True,
            'tool_sha256':sha(Path(__file__).read_bytes()),'original_packages_unchanged':True}
    (out/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    files=[{'file':str(p.relative_to(out)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(out.iterdir()) if p.is_file()]
    (out/'SHA256SUMS.json').write_text(json.dumps({'schema':1,'version':report['version'],'local_only':True,'files':files},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'PASS':True,'movie':str(movie),'duration':duration,'sha256':sha(movie),
                      'original_music_rms':source_audio['rms_s16'],'final_peak':final_audio['peak_dbfs'],'human_listening':False},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
