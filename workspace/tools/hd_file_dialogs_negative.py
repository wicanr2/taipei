"""#38：重算色號、原版 PNG 及呈現雜湊的有效負對照。"""
import argparse
import json
import os
import subprocess
import zipfile
from pathlib import Path

from hd_chrome_negative import png
from hd_scroll_check import audit_bundle, source59
from hd_source_audit import sha


def check(directory):
    art = Path('/workspace/prototypes/hd-style')
    return subprocess.run(['/workspace/runs/receipt-check','-dir',str(directory),
        '-file-reference',str(art),'-original','/orig'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--browser',type=Path,required=True)
    ap.add_argument('--quit',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args = ap.parse_args()
    assert args.out.parent.is_dir() and args.out.parent.stat().st_uid == os.getuid() and not args.out.exists()
    args.out.mkdir()
    sources = source59(Path('/orig'))
    results = []
    for family,receipt in [('browser',args.browser),('quit',args.quit)]:
        s,frame,_,rgba,_ = audit_bundle(receipt,sources)
        assert s['hd']['file_dialog'] == ('file-browser' if family == 'browser' else 'quit-confirm')
        if family == 'browser':assert s['hd']['file_text'][0].strip()
        with zipfile.ZipFile(receipt) as z:files = {n:z.read(n) for n in z.namelist()}
        cases = ['positive','unused-palette-positive','source-border','source-glyph','used-palette',
                 'background-pixel','glyph-pixel','outside-pixel','metadata-family','metadata-text','metadata-color']
        for case in cases:
            changed = dict(files)
            status = json.loads(files['status.json'])
            native,pixels = bytearray(frame),bytearray(rgba)
            if case == 'source-border':
                x,y = (34,41) if family == 'browser' else (7,175)
                native[y*320+x] ^= 128
            elif case == 'source-glyph':
                x,y = (44,49) if family == 'browser' else (19,177)
                native[y*320+x] ^= 128
            elif case == 'used-palette':
                index = frame[41*320+34] if family == 'browser' else frame[175*320+7]
                status['palette'][index][0] ^= 1
            elif case == 'unused-palette-positive':
                index = next(i for i in range(256) if i not in set(frame))
                status['palette'][index][0] ^= 1
            elif case in ['background-pixel','glyph-pixel','outside-pixel']:
                if case == 'outside-pixel':x,y = 10,690
                elif case == 'background-pixel':x,y = (140,168) if family == 'browser' else (28,700)
                else:
                    # 選固定 atlas 中實際有 alpha 的字形墨跡，不以空白矩形冒充字形負對照。
                    from hd_file_dialogs_check import references
                    atlas = references()[2]['glyphs.png']
                    if family == 'browser':
                        code = ord(s['hd']['file_text'][0][0])-32
                        gx,gy,w,h = code % 16*64,code//16*64,24,28
                        dx,dy = next((dx,dy) for dy in range(h) for dx in range(w) if atlas[((gy+dy)*1024+gx+dx)*4+3])
                        x,y = 44*4+dx,49*4+dy
                    else:
                        gx,gy = 190 % 16*64,190//16*64
                        dx,dy = next((dx,dy) for dy in range(56) for dx in range(60) if atlas[((gy+dy)*1024+gx+dx)*4+3])
                        x,y = 19*4+dx,177*4+dy
                pixels[(y*1280+x)*4] ^= 127
            elif case == 'metadata-family':status['hd']['file_dialog'] = ''
            elif case == 'metadata-text':status['hd']['file_text'][0] = 'XXXXXXXX'
            elif case == 'metadata-color':status['hd']['file_colors'][0] ^= 1
            status['frame_index_sha256'] = sha(native)
            status['presentation_sha256'] = sha(pixels)
            changed.update({'frame-index.bin':native,
                'frame.png':png(bytes(v for i in native for v in status['palette'][i]+[255]),320,200),
                'presentation.png':png(pixels,1280,800),'status.json':json.dumps(status).encode()})
            directory = args.out/(family+'-'+case)
            directory.mkdir()
            path = directory/'checked-capture.zip'
            with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_STORED) as z:
                for name,raw in changed.items():z.writestr(name,raw)
            error = ''
            try:audit_bundle(path,sources)
            except AssertionError as e:error = str(e) or 'AssertionError'
            run = check(directory)
            positive = case.endswith('positive')
            assert bool(error) is not positive and (run.returncode != 0) is not positive,(family,case,error,run.stdout[:500])
            results.append({'family':family,'case':case,'positive':positive,'python_rejected':bool(error),
                'go_rejected':run.returncode != 0,'python_error':error,'go_output':run.stdout[:500],
                'native_png_consistent':True,'affected_digests_recomputed':True})
    (args.out/'result.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'cases':len(results),'positive':sum(r['positive'] for r in results),
        'both_checkers_rejected':sum(r['python_rejected'] and r['go_rejected'] for r in results)},ensure_ascii=False))


if __name__ == '__main__':main()
