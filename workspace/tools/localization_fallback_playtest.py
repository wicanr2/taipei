"""#49/#52: missing translation falls back to the bundled TSV in the real GUI."""
import hashlib
import io
import json
import os
import subprocess
import time
import zipfile
from pathlib import Path

root=Path('/workspace/runs')/os.environ['TAIPEI_INTERFACE_RUN']
root.mkdir(mode=0o700)
saves,out=root/'saves',root/'gui'
saves.mkdir();out.mkdir()
catalog=root/'missing-opening-key.tsv'
catalog.write_bytes(b'\n'.join(line for line in Path('/workspace/app/locales/ui.tsv').read_bytes().splitlines()
                             if not line.startswith(b'intro.date\t'))+b'\n')
def status():
    try:
        raw=(out/'capture.zip').read_bytes()
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            s=json.loads(z.read('status.json'))
            assert hashlib.sha256(z.read('frame-index.bin')).hexdigest()==s['frame_index_sha256']
            return s,raw
    except (FileNotFoundError,zipfile.BadZipFile):return {},b''
def wait(check):
    end=time.monotonic()+90
    while time.monotonic()<end:
        s,raw=status()
        if check(s):return s,raw
        time.sleep(.1)
    raise RuntimeError(status()[0])
def key(name):
    subprocess.run(['xdotool','keydown',name],check=True);time.sleep(.15)
    subprocess.run(['xdotool','keyup',name],check=True)
log=(out/'app.log').open('w')
binary=Path('/workspace/runs/taipei-preview')
p=subprocess.Popen([str(binary),'-original','/orig','-saves',str(saves),'-receipts',str(out),
                    '-mute','-steps-per-update','400000','-theme','hd-b','-language','en',
                    '-materials','/workspace/prototypes/hd-style','-catalog',str(catalog),
                    '-stop-file',str(out/'stop')],stdout=log,stderr=subprocess.STDOUT)
try:
    first,_=wait(lambda s:'intro.date' in (s.get('hd',{}).get('source_text_keys') or []))
    assert first['catalog_source']=='bundled-tsv'
    assert first['language_warning']=='locale.error.catalog'
    subprocess.run(['xdotool','search','--onlyvisible','--pid',str(p.pid),'windowfocus'],check=True)
    key('F11')
    opened,raw=wait(lambda s:s.get('language_panel') is True)
    (out/'fallback-capture.zip').write_bytes(raw)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:(out/'fallback.png').write_bytes(z.read('presentation.png'))
    assert opened['language_warning']=='locale.error.catalog'
    assert opened['hd']['source_text_fields']>0
    key('Down')
    selected,_=wait(lambda s:s.get('language_selection')==0)
    for field in ['steps','frame_index_sha256','source_text','key_reads','file_ops']:
        assert opened[field]==selected[field],field
    key('Escape')
    wait(lambda s:s.get('language_panel') is False)
finally:
    (out/'stop').write_text('stop\n')
    try:assert p.wait(timeout=10)==0
    finally:
        if p.poll() is None:p.kill();p.wait()
        log.close()
(root/'fallback-verification.json').write_text(json.dumps({'issue':49,'normal_gui':True,
    'checkpoint':False,'missing_required_key':'intro.date','bundled_fallback':True,
    'visible_localized_warning':True,'original_input_unchanged_in_picker':True,
    'native_exit_tested':False,'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest()},indent=2)+'\n')
print('PASS: missing required translation, bundled fallback and visible GUI warning',flush=True)
