#!/usr/bin/env python3
"""#52: EXE source coverage, independent of the presentation implementation."""
import argparse
import csv
import hashlib
import json
import re
import unicodedata
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--original', type=Path, required=True)
p.add_argument('--catalog', type=Path, required=True)
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
raw = (a.original / 'RS201.EXE').read_bytes()
assert hashlib.sha256(raw).hexdigest() == '798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3'
rows = list(csv.DictReader(a.catalog.open(), delimiter='\t'))
normalize = lambda s: ''.join(c for c in unicodedata.normalize('NFKC', s) if c.isalnum())
lookup = {}
for row in rows:
    for language in ['zh-Hant', 'zh-Hans', 'ja', 'ko', 'en']:
        assert row[language].strip(), (row['key'], language)
    lookup.setdefault(normalize(row['zh-Hant']), []).append(row['key'])
records = []
at = 0x245c4
while at < 0x259a0:
    end = raw.find(b'\0', at, 0x259a0)
    if end < 0:
        break
    try:
        text = raw[at:end].decode('cp950')
    except UnicodeDecodeError:
        text = ''
    if text and all(c.isprintable() or c == '\u3000' for c in text) and re.search('[\u3400-\u9fff]', text):
        records.append({'exe_file_offset': hex(at), 'source_hex': raw[at:end].hex(),
                        'original': text, 'keys': lookup.get(normalize(text), []),
                        'execution': 'unknown usage' if at == 0x245c4 else
                        'password branch not exercised with /x' if 0x24e3c <= at <= 0x24ed2 else
                        'source coverage; player-path evidence recorded by family'})
    at = end + 1
missing = [r for r in records if not r['keys']]
images=[]
rom_hashes={}
for name,want in [('RS201.ROM','0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29'),
                  ('RS201A.ROM','5d66f238dce650b8a407986100392ee4b8ac2aa23a033e80a7ca18ed91b3d9b0')]:
    data=(a.original/name).read_bytes()
    rom_hashes[name]=hashlib.sha256(data).hexdigest()
    assert rom_hashes[name]==want
    if name!='RS201A.ROM':continue
    for member in [6,10,15,16,17,38]:
        off=int.from_bytes(data[18+16*member:22+16*member],'little')
        size=int.from_bytes(data[22+16*member:24+16*member],'little')
        part=data[off:off+size]
        entries=[part]
        if member==10:
            count=int.from_bytes(part[:2],'little')
            offsets=[int.from_bytes(part[2+i*2:4+i*2],'little') for i in range(count)]
            entries=[part[start:min([v for v in offsets if v>start]+[len(part)])] for start in offsets]
        for index,entry in enumerate(entries):
            images.append({'file':name,'member':member,'entry':index,'bytes':len(entry),
                           'source_sha256':hashlib.sha256(entry).hexdigest(),
                           'format':'IV2' if member==38 else 'raw/RLE original image',
                           'evidence':'confirmed source bytes; call contracts and field bounds in spec/033'})
result = {'issue': 52, 'exe_sha256': hashlib.sha256(raw).hexdigest(),
          'rom_sha256':rom_hashes,'image_sources':images,
          'catalog_sha256': hashlib.sha256(a.catalog.read_bytes()).hexdigest(),
          'catalog_keys': len(rows), 'readable_chinese_sources': len(records),
          'unmapped': len(missing), 'sources': records,
          'image_text': {'ROMA 6': 'startup.title', 'ROMA 38 (IV2)': 'startup.title',
                         'ROMA 10 (four entries)': 'art.protest',
                         'ROMA 15,16': ['art.department_store', 'art.pacific'],
                         'ROMA 17': 'art.bank'},
          'retained_art': ['SOGO and other brand emblems', 'unreadable certificate ornament'],
          'limitations': ['Source coverage is separate from execution coverage.',
                          'Password flow and unknown-usage source are not player-path claims.']}
assert len(records) == 146, len(records)
assert len(images)==9,len(images)
assert not missing, missing
a.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: result[k] for k in ['catalog_keys', 'readable_chinese_sources', 'unmapped', 'catalog_sha256']}))
