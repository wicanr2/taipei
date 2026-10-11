"""#44：逐段核對正常施工的原子收據；部分結果不當成整批完成。"""
import argparse
import hashlib
import json
import platform
import zipfile
from pathlib import Path

from hd_source_audit import scene
from infrastructure_prototype_check import read_sources

EXE_SHA = '798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3'
STAGES = [
    ('road','road-confirm','road-complete'),
    ('road-corners','road-complete','road-corners-complete'),
    ('road-shore','road-corners-complete','road-shore-complete'),
    ('power','power-confirm','power-complete'),
    ('power-corners','power-complete','power-corners-complete'),
    ('power-road','power-corners-complete','power-road-complete'),
    ('power-shore','power-road-complete','power-shore-complete'),
]


def sha(raw):return hashlib.sha256(raw).hexdigest()


def load(path):
    with zipfile.ZipFile(path) as z:
        s,frame = json.loads(z.read('status.json')),z.read('frame-index.bin')
    assert len(frame)==64000 and sha(frame)==s['frame_index_sha256']
    assert s['original_sha256']==EXE_SHA and scene(s,frame)
    assert s['map_origin']['Valid']
    return s,frame


def grid(frame):
    return {(col,row):b''.join(frame[(34+row*9+y)*320+5+col*9:(34+row*9+y)*320+14+col*9]
        for y in range(9)) for row in range(15) for col in range(29)}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--original',type=Path,required=True)
    ap.add_argument('--receipts',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--require-complete',action='store_true')
    ap.add_argument('--case',choices=['all','shore'],default='all')
    args=ap.parse_args()
    assert not args.out.exists()
    exe,rom=[(args.original/name).read_bytes() for name in ['RS201.EXE','RS201.ROM']]
    assert sha(exe)==EXE_SHA
    _,aliases=read_sources(rom)
    records,missing,observed=[],[],set()
    stages=STAGES if args.case=='all' else [('power-shore','shore-before','shore-complete')]
    for name,before,after in stages:
        paths=[args.receipts/(p+'-capture.zip') for p in [before,after]]
        if not all(p.is_file() for p in paths):missing.append(name);continue
        (a,old),(b,new)=[load(p) for p in paths]
        assert a['map_origin']==b['map_origin'] and a['steps']<b['steps']
        assert len(a['key_reads'])<len(b['key_reads'])
        changes,unknown=[],[]
        ga,gb=grid(old),grid(new)
        for position,pixels in gb.items():
            if pixels in aliases:
                observed.update(ref['image'] for ref in aliases[pixels] if ref['member']==39)
            if ga[position]==pixels:continue
            if pixels not in aliases or ga[position] not in aliases:
                unknown.append({'cell':list(position),'before_known':ga[position] in aliases,
                    'after_known':pixels in aliases,'before_sha256':sha(ga[position]),'after_sha256':sha(pixels)})
                continue
            changes.append({'cell':list(position),'before_sha256':sha(ga[position]),
                'after_sha256':sha(pixels),'before_sources':aliases[ga[position]],'after_sources':aliases[pixels]})
        records.append({'stage':name,'before':paths[0].name,'after':paths[1].name,
            'receipt_sha256':[sha(p.read_bytes()) for p in paths],
            'steps':[a['steps'],b['steps']],'original_reads_added':len(b['key_reads'])-len(a['key_reads']),
            'origin':b['map_origin'],'known_changes':changes,'unknown_changed_cells':unknown})
    assert records
    if args.require_complete:assert not missing,('missing stages',missing)
    result={'schema':1,'issue':44,'inputs':{'RS201.EXE':sha(exe),'RS201.ROM':sha(rom)},
        'tool':f'infrastructure_source_check.py / Python {platform.python_version()}',
        'tool_image':'sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3',
        'address_space':'ROM file offsets and zero-based member/image; native 320x200 cell coordinates',
        'case':args.case,'stages':records,'all_seven_stages_captured':args.case=='all' and not missing,
        'all_requested_stages_captured':not missing,'missing_stages':missing,
        'observed_member39_images':sorted(observed),
        'scope':'正常操作逐段來源及游標等未知變更，研究部分結果不代表正式 HD、存退讀或整批完成'}
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'stages':[r['stage'] for r in records],'known_changes':[len(r['known_changes']) for r in records],
        'missing':missing,'images':sorted(observed)},ensure_ascii=False))


if __name__=='__main__':main()
