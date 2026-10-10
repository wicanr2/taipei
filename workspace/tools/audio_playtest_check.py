"""獨立檢查播放器 monitor 擷取；技術驗證不冒充人耳確認。"""
import array
import hashlib
import json
import math
import wave
import zipfile
from pathlib import Path

root=Path('/workspace/runs/audio-device')
with wave.open(str(root/'playback.wav')) as w:
    rate=w.getframerate();channels=w.getnchannels();width=w.getsampwidth();frames=w.getnframes()
    assert (rate,channels,width)==(48000,2,2)
    pcm=w.readframes(frames)
samples=array.array('h',pcm)
nonzero=sum(v!=0 for v in samples)
peak=max(abs(v) for v in samples)
rms=math.sqrt(sum(v*v for v in samples)/len(samples))
assert frames>=48000*14 and nonzero>48000, '實際播放器 monitor 沒有足夠音訊'
with zipfile.ZipFile(root/'capture.zip') as z:
    state=json.loads(z.read('status.json'))
audio=state['audio']
assert audio['muted'] is False and audio['closed'] is True
assert audio['nonzero_frames']>48000 and audio['opl_events']>100
assert audio['ring']['RejectedBytes']==0 and audio['ring']['Closed'] is True
result={'cold_gui':True,'checkpoint':False,'player_monitor_captured':True,
        'sample_rate':rate,'channels':channels,'frames':frames,'nonzero_samples':nonzero,
        'peak':peak,'rms':rms,'wav_sha256':hashlib.sha256((root/'playback.wav').read_bytes()).hexdigest(),
        'audio':audio,'human_listened':False,'native_exit':False,
        'scope':'原版冷啟動、實際播放器與正常關閉；完整原版退出另由 gui_playtest.sh 驗證'}
(root/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['player_monitor_captured','frames','nonzero_samples','peak','rms','human_listened']}))
