"""#46／027：獨立重讀 ROM、插畫與全部切片，核對完整離線原型。"""
import argparse
import json
import os
import struct
import subprocess
import zipfile
from pathlib import Path

from hd_file_dialogs_check import rgba
from hd_source_audit import sha


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--original',type=Path,required=True)
    parser.add_argument('--prototype',type=Path,required=True)
    parser.add_argument('--illustration',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    assert args.out.parent.is_dir() and args.out.parent.stat().st_uid==os.getuid() and not args.out.exists()
    rom=(args.original/'RS201.ROM').read_bytes()
    assert sha(rom)=='0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29'
    manifest=json.loads((args.prototype/'manifest.json').read_text())
    assert manifest['rom_sha256']==sha(rom) and manifest['stage']=='DRAFT'
    assert sha(args.illustration.read_bytes())==manifest['illustration_sha256']=='16642276a2ba54203e2b745525e65ba92106698fc9ac9b1151720f621211aa2c'
    assert len(manifest['cases'])==1 and manifest['cases'][0]['label']=='thermal'
    case=manifest['cases'][0]
    assert case['native_size']==[54,54] and case['hd_size']==[216,216]
    assert len(case['cells'])==len(case['fragments'])==36
    source_receipt=Path(case['source_receipt'])
    assert sha(source_receipt.read_bytes())==case['source_receipt_sha256']
    with zipfile.ZipFile(source_receipt) as z:
        status,frame=json.loads(z.read('status.json')),z.read('frame-index.bin')
    assert len(frame)==64000 and sha(frame)==status['frame_index_sha256']
    original=rgba(args.prototype/'thermal-native4x.png',(216,216))
    full=rgba(args.prototype/'thermal-hd.png',(216,216))
    reduced=subprocess.run(['convert',str(args.illustration),'-filter','Lanczos','-resize','216x216!',
        '-depth','8','rgba:-'],check=True,stdout=subprocess.PIPE).stdout
    assert full==reduced and set(full[3::4])=={255}
    aliases={}
    for member,count in {34:96,35:96,36:96,37:96,38:180,39:75,40:180,41:180,59:135}.items():
        start,length=struct.unpack_from('<IH',rom,18+member*16)
        assert struct.unpack_from('<H',rom,start)[0]==count
        offsets=struct.unpack_from('<'+'H'*count,rom,start+2)+(length,)
        for index in range(count):
            at,end=start+offsets[index],start+offsets[index+1]
            assert end-at==85 and rom[at:at+4]==b'\x09\x00\x09\x00'
            aliases.setdefault(rom[at+4:end],[]).append((member,index,at,at+4,offsets[index]))
    reconstructed=bytearray(216*216*4)
    indices=bytearray(54*54)
    checked=set()
    negative=0
    for record in case['fragments']:
        col,row=record['relative_cell']
        assert 0<=col<6 and 0<=row<6 and (col,row) not in checked
        checked.add((col,row))
        source=(args.prototype/record['source_file']).read_bytes()
        assert len(source)==81 and sha(source)==record['source_sha256']
        actual=[(r['member'],r['image'],r['file_offset'],r['pixel_file_offset'],r['member_offset']) for r in record['sources']]
        assert actual==aliases[source]==[(38,12+row*30+col,actual[0][2],actual[0][3],actual[0][4])]
        for at in range(81):
            changed=bytearray(source);changed[at]^=128
            assert bytes(changed) not in aliases
            negative+=1
        for y in range(9):indices[(row*9+y)*54+col*9:(row*9+y)*54+col*9+9]=source[y*9:y*9+9]
        path=args.prototype/record['image_file']
        assert sha(path.read_bytes())==record['image_sha256']
        fragment=rgba(path,(36,36))
        for y in range(36):
            at=((row*36+y)*216+col*36)*4
            reconstructed[at:at+144]=fragment[y*144:(y+1)*144]
    assert reconstructed==full and sha(indices)==case['source_sha256']=='791fbfe53259ca39fe6dbd91ba4e2fa36009b7bc43d61e31b3d498b816dca558'
    for y in range(216):
        for x in range(216):
            color=status['palette'][indices[(y//4)*54+x//4]]+[255]
            assert original[(y*216+x)*4:(y*216+x+1)*4]==bytes(color)
    comparison=rgba(args.prototype/'thermal-comparison.png',(432,216))
    assert comparison==b''.join(original[y*864:(y+1)*864]+full[y*864:(y+1)*864] for y in range(216))
    for name,digest in case['files'].items():assert sha((args.prototype/name).read_bytes())==digest
    result={'schema':1,'issue':46,'prototype_manifest_sha256':sha((args.prototype/'manifest.json').read_bytes()),
        'rom_sha256':sha(rom),'source_receipt_sha256':case['source_receipt_sha256'],
        'full_source_sha256':sha(indices),'illustration_sha256':manifest['illustration_sha256'],
        'fragments':36,'source_pixel_negatives':negative,'full_image_rgba_sha256':sha(full),
        'full_reassembly_equal':True,'original_rgba_equal':True,'comparison_equal':True,
        'tool':'Python 3.11.2 / ImageMagick 6.9.11-60','scope':'離線來源／切片／重組核對；美術構圖另經目視審查，不代替正常 HD 玩家驗收'}
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
