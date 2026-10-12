#!/usr/bin/env python3
"""#51 / 032: independent complete-source reconstruction and provenance."""
import hashlib
import json
import re
import struct
import sys
import zipfile
from pathlib import Path

original = Path('/orig')
workspace = Path('/workspace')
rom = (original/'RS201.ROM').read_bytes()
exe = (original/'RS201.EXE').read_bytes()
sha = lambda b: hashlib.sha256(b).hexdigest()
assert sha(rom) == '0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29'
assert sha(exe) == '798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3'

def member(index):
    offset, size = struct.unpack_from('<IH',rom,18+16*index)
    return rom[offset:offset+size]

def decode(index):
    raw=member(index)
    w,h=struct.unpack_from('<HH',raw)
    pixels=bytearray()
    at=4
    while at<len(raw):
        value,count=raw[at],1
        at+=1
        if value==0:
            value,count=raw[at:at+2]
            at+=2
        pixels.extend([value]*count)
    assert len(pixels)==w*h
    return w,h,pixels

ascii_font,chinese,codes=member(56),member(57),member(58)
lookup={}
for i in range(402):
    lookup.setdefault(codes[2+i*2:4+i*2],i)

def stamp(pixels,stride,x,y,glyph,w,h,ink):
    for dy in range(h):
        for dx in range(w):
            if glyph[dy*((w+7)//8)+dx//8] & (128>>(dx%8)):
                pixels[(y+dy)*stride+x+dx]=ink

def receipt(label):
    path=workspace/'runs/interface-locale-cold-r2/gui'/(label+'-capture.zip')
    raw=path.read_bytes()
    with zipfile.ZipFile(path) as z:
        status=json.loads(z.read('status.json'))
        pixels=z.read('frame-index.bin')
    assert sha(pixels)==status['frame_index_sha256']
    return pixels,{'receipt':str(path.relative_to(workspace)),'receipt_sha256':sha(raw),
                   'steps':status['steps'],'frame_index_sha256':sha(pixels)}

def crop(pixels,x,y,w,h):
    return bytes(pixels[(y+dy)*320+x+dx] for dy in range(h) for dx in range(w))

panels=[]
for index,label,slots,bg,ink in [
    (13,'mayor-1',[(46,15,3),(143,15,8),(46,40,3),(143,40,8),(144,65,8),(180,88,3)],9,14),
    (14,'mayor-2',[(x,y,3) for y in [28,47,66,85,104] for x in [81,196]]+[(130,123,3)],1,11),
]:
    w,h,base=decode(index)
    source_sha=sha(base)
    frame,meta=receipt(label)
    actual=crop(frame,18,37,w,h)
    values=[]
    for x,y,count in slots:
        for dy in range(7):
            for dx in range(count*6):base[(y+dy)*w+x+dx]=bg
        text=''
        for col in range(count):
            xx=x+col*6
            mask=bytes(actual[(y+dy)*w+xx+dx]==ink for dy in range(7) for dx in range(5))
            matches=[]
            for char in ' -0123456789':
                offset=6+(ord(char)-32)*7
                glyph=ascii_font[offset:offset+7]
                if mask==bytes(bool(glyph[dy]&(128>>dx)) for dy in range(7) for dx in range(5)):
                    matches.append((char,glyph))
            assert len(matches)==1,(label,x,y,col,matches)
            char,glyph=matches[0]
            text+=char
            stamp(base,w,xx,y,glyph,5,7,ink)
        values.append(text)
    if index==13:
        for col,glyph_index in enumerate([322,None,323]):
            if glyph_index is not None:
                stamp(base,w,144+16*col,108,chinese[6+glyph_index*30:6+(glyph_index+1)*30],15,14,13)
    assert bytes(base)==actual,label
    panels.append({**meta,'member':index,'native':[18,37,w,h],
                   'decoded_sha256':source_sha,'numeric_slots':slots,'values':values,
                   'complete_rebuild_pixel_diff':0,'evidence':'confirmed for this normal GUI receipt'})

frame,meta=receipt('environment-1')
w,h,base=decode(12)
source_sha=sha(base)
for col,glyph_index in enumerate([361,362]):
    stamp(base,w,7+16*col,14,chinese[6+glyph_index*30:6+(glyph_index+1)*30],15,14,12)
assert bytes(base)==crop(frame,54,87,w,h)
panels.append({**meta,'member':12,'native':[54,87,w,h],'decoded_sha256':source_sha,
               'selected':0,'complete_rebuild_pixel_diff':0})

notice_entries=[]
runtime=(workspace/'app/internal/hd/interface_extra.go').read_text()
for key,code in re.findall(r'\{"((?:notice|settings)\.[^"]+)",\s*"([0-9a-f]+)"\}',runtime):
    raw=bytes.fromhex(code)
    offset=exe.find(raw+b'\0',0x25200,0x25a00)
    assert offset>=0,key
    w,h,base=decode(1)
    x=19
    at=0
    while at<len(raw):
        if raw[at]<128:
            char=raw[at]
            stamp(base,w,x,181,ascii_font[6+(char-32)*7:6+(char-31)*7],5,7,32)
            x+=6
            at+=1
        else:
            glyph_index=lookup[raw[at:at+2]]
            stamp(base,w,x,177,chinese[6+glyph_index*30:6+(glyph_index+1)*30],15,14,32)
            x+=16
            at+=2
    assert x<=231,(key,x)
    local=crop(base,7,175,224,18)
    entry={'key':key,'exe_file_offset':offset,'code_hex':code,'source_text':raw.decode('cp950'),
           'complete_left_region_sha256':sha(local),'evidence':'confirmed static EXE bytes and ROM glyph construction; normal triggering varies'}
    if key=='settings.message_speed':
        frame,meta=receipt('environment-0')
        assert local==crop(frame,7,175,224,18)
        entry.update(meta)
        entry['complete_rebuild_pixel_diff']=0
    notice_entries.append(entry)
assert len(notice_entries)==22
disasters=[]
for selected in range(6):
    w,h,base=decode(18)
    decoded_sha=sha(base)
    for option,offset in enumerate([0x25591,0x2559e,0x255ab,0x255b8,0x255c5,0x255d2]):
        raw=exe[offset:exe.index(0,offset)]
        for col in range(6):
            glyph_index=lookup[raw[col*2:col*2+2]]
            stamp(base,w,13+(option//3)*114+col*16,43+(option%3)*31,
                  chinese[6+glyph_index*30:6+(glyph_index+1)*30],15,14,15 if option==selected else 55)
    path=workspace/'runs/interface-locale-cold-r5/gui'/f'disaster-city-{selected}-capture.zip'
    with zipfile.ZipFile(path) as z:
        status=json.loads(z.read('status.json'))
        frame=z.read('frame-index.bin')
    assert bytes(base)==crop(frame,18,37,w,h)
    disasters.append({'receipt':str(path.relative_to(workspace)),'receipt_sha256':sha(path.read_bytes()),
                      'selection':selected,'member':18,'native':[18,37,w,h],
                      'decoded_sha256':decoded_sha,'complete_rebuild_pixel_diff':0})
used={12,13,14,15,32,55}
for index in [1,12,13,14,18]:
    w,h,pixels=decode(index)
    used.update(crop(pixels,7,175,224,18) if index==1 else pixels)
indices=sorted(used)
palette_sha=sha(bytes(c for i in indices for c in status['palette'][i]))
assert palette_sha=='bb592feaa8a51c36b22b702efa4fbed5a793e43a8029526cd6912d915d8a7919'
out=workspace/'runs/interface-source'
out.mkdir(mode=0o700,exist_ok=True)
report={'schema':1,'issue':51,'tool':'Python '+sys.version.split()[0],
        'inputs':{'RS201.EXE':sha(exe),'RS201.ROM':sha(rom)},
        'address_space':'ROM member indices and EXE raw file offsets; native 320x200 coordinates',
        'panels':panels,'notices':notice_entries,'disaster_cities':disasters,
        'used_palette_indices':indices,'used_palette_sha256':palette_sha,
        'scope':'presentation sources; no new rules or timing claims'}
(out/'catalog.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS: complete population/opinion/speed/message reconstruction; six disaster cities; 22 static notices')
