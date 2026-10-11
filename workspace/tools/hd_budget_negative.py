"""#39：重生 PNG 及雜湊後，核對 Go／Python 皆拒絕有效破壞。"""
import argparse
import json
import os
import subprocess
import zipfile
from pathlib import Path

from hd_chrome_negative import png
from hd_scroll_check import audit_bundle, source59
from hd_budget_check import references
from hd_file_dialogs_check import rgba as read_rgba
from hd_source_audit import sha


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--receipt',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args = ap.parse_args()
    assert args.out.parent.is_dir() and args.out.parent.stat().st_uid == os.getuid() and not args.out.exists()
    args.out.mkdir()
    sources = source59(Path('/orig'))
    s,frame,_,rgba,_ = audit_bundle(args.receipt,sources)
    assert s['hd']['budget']
    refs,manifest,pictures,_ = references()
    with zipfile.ZipFile(args.receipt) as z: files = {n:z.read(n) for n in z.namelist()}
    from budget_catalog import decode_budget
    model = decode_budget(frame,refs)
    field = model['fields'][0]
    col,ch = next((i,ch) for i,ch in enumerate(field['text']) if ch != ' ')
    ix,iy = manifest['atlas_characters'].index(ch)*24,28 if field['color'] == 12 else 0
    dx,dy = next((dx,dy) for dy in range(28) for dx in range(24)
        if pictures['glyphs.png'][((iy+dy)*288+ix+dx)*4+3])
    numeric_xy = ((18+field['x']+col*6)*4+dx,(37+field['y'])*4+dy)
    ink_path = Path('/workspace/prototypes/hd-style/budget-v1/static-ink.png')
    assert sha(ink_path.read_bytes()) == manifest['images']['static-ink.png']
    static_alpha = read_rgba(ink_path,(940,528))
    static_xy = next((72+x,148+y) for y in range(528) for x in range(940)
        if static_alpha[(y*940+x)*4+3])
    cases = ['positive','unused-palette-positive','source-border','source-number','source-title','used-palette',
        'background-pixel','number-ink','static-ink','outside-pixel',
        'metadata-flag','metadata-text','metadata-color','metadata-selection','metadata-reason']
    result = []
    for case in cases:
        changed = dict(files)
        status = json.loads(files['status.json'])
        native,pixels = bytearray(frame),bytearray(rgba)
        if case in ('source-border','source-number','source-title'):
            x,y = {'source-border':(18,37),'source-number':(111,66),'source-title':(35,45)}[case]
            native[y*320+x] ^= 128
        elif case == 'used-palette':status['palette'][frame[37*320+18]][0] ^= 1
        elif case == 'unused-palette-positive':
            index = next(i for i in range(256) if i not in set(frame))
            status['palette'][index][0] ^= 1
        elif case in ('background-pixel','number-ink','static-ink','outside-pixel'):
            x,y = {'background-pixel':(72,148),'number-ink':numeric_xy,
                'static-ink':static_xy,'outside-pixel':(10,690)}[case]
            pixels[(y*1280+x)*4] ^= 127
        elif case == 'metadata-flag':status['hd']['budget'] = False
        elif case == 'metadata-text':status['hd']['budget_text'][0] = '999'
        elif case == 'metadata-color':status['hd']['budget_colors'][0] ^= 1
        elif case == 'metadata-selection':status['hd']['budget_selection'] = 9
        elif case == 'metadata-reason':status['hd']['budget_reason'] = 'original'
        status['frame_index_sha256'] = sha(native)
        status['presentation_sha256'] = sha(pixels)
        changed.update({'frame-index.bin':native,
            'frame.png':png(bytes(v for i in native for v in status['palette'][i]+[255]),320,200),
            'presentation.png':png(pixels,1280,800),'status.json':json.dumps(status).encode()})
        directory = args.out/case
        directory.mkdir()
        path = directory/'checked-capture.zip'
        with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_STORED) as z:
            for name,raw in changed.items():z.writestr(name,raw)
        error = ''
        try:audit_bundle(path,sources)
        except AssertionError as e:error = str(e) or 'AssertionError'
        run = subprocess.run(['/workspace/runs/receipt-check','-dir',str(directory),
            '-budget-reference','/workspace/prototypes/hd-style','-original','/orig'],
            stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        positive = case.endswith('positive')
        assert bool(error) is not positive and (run.returncode != 0) is not positive,(case,error,run.stdout[:600])
        result.append({'case':case,'positive':positive,'python_rejected':bool(error),
            'go_rejected':run.returncode != 0,'python_error':error,'go_output':run.stdout[:500],
            'native_png_consistent':True,'affected_digests_recomputed':True})
    (args.out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'cases':len(result),'positive':sum(r['positive'] for r in result),
        'both_checkers_rejected':sum(r['python_rejected'] and r['go_rejected'] for r in result)},ensure_ascii=False))


if __name__ == '__main__':
    main()
