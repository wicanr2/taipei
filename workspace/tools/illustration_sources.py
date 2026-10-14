#!/usr/bin/env python3
"""#32／039：完整圖像來源與IV2相位；不執行VM、不推定用途。"""
import argparse
import json
import os
from pathlib import Path
import struct
import subprocess
import zipfile

from full_asset_catalog import ROMS,image,library,sha
from rom_catalog import png


def iv2(raw):
    pixels=bytearray([255])*64000;at=0;position=0;ended=False
    while at+2<=len(raw):
        delta=struct.unpack_from('<H',raw,at)[0];at+=2
        if position+delta>65535:ended=True;break
        position+=delta
        if at>=len(raw):return None
        size=raw[at];at+=1
        if size==0 or at+size>len(raw) or position+size>64000:return None
        pixels[position:position+size]=raw[at:at+size];at+=size;position+=size
    if not ended or at!=len(raw):return None
    points=[i for i,v in enumerate(pixels) if v!=255]
    if not points:return None
    width=max(i%320 for i in points)+1;height=max(i//320 for i in points)+1
    return width,height,b''.join(pixels[y*320:y*320+width] for y in range(height))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    assert not a.out.exists() and a.out.parent.stat().st_uid==os.getuid()
    receipt=Path('/workspace/runs/gui-public-r2/pause-capture.zip')
    with zipfile.ZipFile(receipt) as z:status=json.loads(z.read('status.json'))
    palette=bytes(v for c in status['palette'] for v in c)
    a.out.mkdir();records=[];classifications=[];unique={}
    for name,(expected,count) in ROMS.items():
        rom=Path('/orig',name).read_bytes();assert sha(rom)==expected
        assert struct.unpack_from('<H',rom)[0]==count
        for member in range(count):
            offset,size=struct.unpack_from('<IH',rom,18+member*16);data=rom[offset:offset+size]
            base={'rom':name,'member':member,'offset':offset,'bytes':size,'sha256':sha(data)}
            if (name=='RS201.ROM' and member in [0,56,57,58,60,61,62,63,64,65,66,67,68]) or (name=='RS201A.ROM' and member in [0,3,36,37,39,40,41,42,43,44,45,46,47,48]):
                kind='world-grid' if name=='RS201.ROM' and 60<=member<=66 else 'palette-font-or-audio'
                classifications.append(dict(base,kind=kind,level='既有來源契約；不作獨立插畫重繪',reference='033、009音訊、009字模與原版城市資料；細分證據仍保留原件'))
                continue
            entries=library(data)
            if entries:parts=[(i,relative,decoded) for i,(relative,decoded) in enumerate(entries)]
            else:
                decoded=image(data)
                parts=[(0,0,decoded)] if decoded else []
            if not parts:
                if name=='RS201.ROM' and member in [52,53,54,55]:
                    n=struct.unpack_from('<H',data)[0];assert n==8
                    offsets=list(struct.unpack_from('<'+'H'*n,data,2));assert offsets[0]==18 and offsets==sorted(set(offsets))
                    parts=[]
                    for i,start in enumerate(offsets):
                        raw=data[start:offsets[i+1] if i+1<n else len(data)];decoded=iv2(raw);assert decoded
                        parts.append((i,start,(*decoded,'iv2')))
                elif name=='RS201A.ROM' and member==38:
                    decoded=iv2(data);assert decoded;parts=[(0,0,(*decoded,'iv2'))]
                else:raise AssertionError(('未分類來源',name,member,base))
            for index,relative,(width,height,pixels,encoding) in parts:
                if (width,height)==(9,9):continue
                # 末項以成員長度界定，重複offset保留全部原索引。
                ends=sorted({p[1] for p in parts if p[1]>relative})
                end=ends[0] if ends else len(data);raw=data[relative:end]
                ident=('r' if name=='RS201.ROM' else 'a')+f'{member:02d}-{index:02d}'
                key=(width,height,sha(pixels));canonical=unique.setdefault(key,ident)
                record=dict(base,id=ident,image=index,file_offset=offset+relative,raw_sha256=sha(raw),
                    width=width,height=height,encoding=encoding,pixels_sha256=sha(pixels),canonical=canonical,
                    level='已證實解碼與完整消耗；用途、透明及時序另驗',normal_player_test=False)
                records.append(record)
                if canonical!=ident:continue
                root=a.out/ident;root.mkdir();(root/'source.bin').write_bytes(pixels);(root/'raw.bin').write_bytes(raw)
                png(root/'source.png',width,height,pixels,palette)
                subprocess.run(['convert',str(root/'source.png'),'-filter','point','-resize','400%',
                    '-strip',str(root/'reference.png')],check=True)
                (root/'source.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    result={'schema':1,'issue':32,'stage':'DRAFT','images':records,'non_illustration_members':classifications,
        'sources':len(records),'unique_images':len(unique),'palette_receipt_sha256':sha(receipt.read_bytes()),
        'preview_palette':'正常城市色盤供來源導覽；不宣稱其他場景正式色盤',
        'address_space':'ROM file offsets; zero-based member/image; IV2 destination stride320',
        'tool_sha256':sha(Path(__file__).read_bytes()),'normal_player_test':False}
    (a.out/'inventory.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('DRAFT',len(records),'sources',len(unique),'unique',len(classifications),'non-illustration members',sha((a.out/'inventory.json').read_bytes()))


if __name__=='__main__':main()
