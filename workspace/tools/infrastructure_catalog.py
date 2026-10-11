"""#44：九組圖塊、來源別名與正常玩家畫面；不猜施工規則。"""
import argparse
import hashlib
import json
import math
import os
import platform
import struct
import zipfile
from pathlib import Path

from hd_source_audit import cell, scene
from rom_catalog import library, png

ROM_SHA = '0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29'
EXE_SHA = '798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3'
COUNTS = {34:96,35:96,36:96,37:96,38:180,39:75,40:180,41:180,59:135}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def sources(rom):
    assert sha(rom) == ROM_SHA and struct.unpack_from('<H',rom)[0] == 69
    result = {}
    for member,count in COUNTS.items():
        offset,size = struct.unpack_from('<IH',rom,18+member*16)
        parsed = library(rom[offset:offset+size])
        assert parsed and len(parsed[1]) == count
        offsets,images = parsed
        for index,(w,h,pixels) in enumerate(images):
            assert (w,h,len(pixels)) == (9,9,81)
            result.setdefault(pixels,[]).append({'rom':'RS201.ROM','member':member,'image':index,
                'member_offset':offsets[index],'file_offset':offset+offsets[index],
                'pixel_file_offset':offset+offsets[index]+4})
    assert len(result) == 1049 and sum(map(len,result.values())) == 1134
    return result


def sheet(path,tiles,palette,font):
    # 只輸出原始色號的技術圖庫，不作高清美術。沿用已驗 PNG 編碼器。
    columns,pitch,scale = 12,76,6
    rows = math.ceil(len(tiles)/columns)
    width,height = columns*pitch,rows*pitch
    canvas = bytearray(width*height)
    for ordinal,(index,pixels) in enumerate(tiles):
        ox,oy = ordinal%columns*pitch+10,ordinal//columns*pitch+4
        for y in range(9):
            for x in range(9):
                for dy in range(scale):
                    at = (oy+y*scale+dy)*width+ox+x*scale
                    canvas[at:at+scale] = bytes([pixels[y*9+x]])*scale
        for column,ch in enumerate(f'39.{index:03d}'):
            for y in range(7):
                row = font[6+(ord(ch)-32)*7+y] >> 3
                for x in range(5):
                    if row & (16>>x):canvas[(oy+61+y)*width+ox+column*6+x] = 15
    png(path,width,height,bytes(canvas),bytes(v for c in palette for v in c))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--original',type=Path,required=True)
    ap.add_argument('--receipts',type=Path,nargs='+',required=True)
    ap.add_argument('--out',type=Path,required=True)
    args = ap.parse_args()
    assert args.out.parent.is_dir() and args.out.parent.stat().st_uid == os.getuid()
    assert not args.out.exists()
    args.out.mkdir()
    rom,exe = [(args.original/n).read_bytes() for n in ['RS201.ROM','RS201.EXE']]
    assert sha(exe) == EXE_SHA
    aliases = sources(rom)
    observed,records = {},[]
    palette = None
    for root in args.receipts:
        assert root.is_dir()
        for path in sorted(root.rglob('*-capture.zip')):
            with zipfile.ZipFile(path) as z:
                s,frame = json.loads(z.read('status.json')),z.read('frame-index.bin')
            assert len(frame) == 64000 and sha(frame) == s['frame_index_sha256']
            if not scene(s,frame):
                continue
            if palette is None:
                palette = s['palette']
            known,unknown,groups = 0,[],set()
            for y in range(34,169,9):
                for x in range(5,266,9):
                    pixels = cell(frame,x,y)
                    if pixels not in aliases:
                        unknown.append([x,y]);continue
                    known += 1
                    digest = sha(pixels)
                    entry = observed.setdefault(digest,{'sources':aliases[pixels],'indices':sorted(set(pixels)),
                        'examples':[],'cell_count':0})
                    entry['cell_count'] += 1
                    if len(entry['examples']) < 4:
                        entry['examples'].append({'receipt':str(path),'x':x,'y':y})
                    groups.update(a['member'] for a in aliases[pixels])
            records.append({'receipt':str(path),'receipt_sha256':sha(path.read_bytes()),'steps':s['steps'],
                'frame_sha256':sha(frame),'matched_cells':known,'unknown_cells':unknown,'members':sorted(groups)})
    assert palette is not None and records
    target = []
    for pixels,refs in aliases.items():
        for ref in refs:
            if ref['member'] != 39:continue
            target.append({'source':ref,'pixels_sha256':sha(pixels),'pixels_hex':pixels.hex(),
                'indices':sorted(set(pixels)),'aliases':refs,'observed':sha(pixels) in observed})
    target.sort(key=lambda t:t['source']['image'])
    assert len(target) == 75
    negatives = []
    for t in target:
        pixels = bytes.fromhex(t['pixels_hex'])
        corrupted = bytes([255])+pixels[1:]
        assert corrupted not in aliases
        negatives.append({'source_image':t['source']['image'],'corrupt_first_pixel_rejected':True})
    off,size = struct.unpack_from('<IH',rom,18+56*16)
    sheet(args.out/'member39-source.png',[(t['source']['image'],bytes.fromhex(t['pixels_hex'])) for t in target],palette,rom[off:off+size])
    result = {'schema':1,'issue':44,'address_space':'RS201.ROM file offsets; member/image zero-based',
        'tool':f'infrastructure_catalog.py / Python {platform.python_version()}',
        'image':'sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3',
        'inputs':{'RS201.ROM':sha(rom),'RS201.EXE':sha(exe)},'library_counts':COUNTS,
        'source_references':1134,'unique_tiles':len(aliases),'target_member':39,'target':target,
        'normal_samples':records,'observed_tiles':observed,'negative_controls':negatives,'palette':palette,
        'scope':'完整來源及既有正常畫面的原始像素；成員 39 的玩法語意與本批 HD 尚未驗證'}
    (args.out/'catalog.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'normal_city_receipts':len(records),'target_images':len(target),
        'target_observed':sum(t['observed'] for t in target),'unique_observed':len(observed),
        'negative_controls':len(negatives)},ensure_ascii=False))


if __name__ == '__main__':
    main()
