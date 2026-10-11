"""#46：重讀原子收據與 ROM bytes，核對兩種正常電廠施工來源。"""
import argparse
import json
import os
import struct
import zipfile
from pathlib import Path

from hd_source_audit import MATERIAL,cell,scene,sha
from rom_catalog import png

ROM_SHA='0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29'
COUNTS={34:96,35:96,36:96,37:96,38:180,39:75,40:180,41:180,59:135}


def read_bundle(path):
    with zipfile.ZipFile(path) as z:
        status,frame=json.loads(z.read('status.json')),z.read('frame-index.bin')
    assert len(frame)==64000 and sha(frame)==status['frame_index_sha256']
    return status,frame


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--original',type=Path,required=True)
    parser.add_argument('--receipts',type=Path,required=True)
    parser.add_argument('--case',choices=['thermal','nuclear','all'],default='all')
    parser.add_argument('--before',help='保留的部分流程在 Space 施工前最後一份收據標籤')
    parser.add_argument('--after',help='保留的部分流程移開游標後收據標籤')
    args=parser.parse_args()
    root=args.receipts
    prefix=args.before is not None or args.after is not None
    assert not prefix or (args.before and args.after and args.case!='all')
    target=root/(f'source-check-{args.case}-prefix.json' if prefix else 'source-check.json')
    assert root.stat().st_uid==os.getuid() and not target.exists()
    rom=(args.original/'RS201.ROM').read_bytes()
    assert sha(rom)==ROM_SHA
    aliases={}
    for member,count in COUNTS.items():
        offset,length=struct.unpack_from('<IH',rom,18+member*16)
        lib=rom[offset:offset+length]
        assert struct.unpack_from('<H',lib)[0]==count
        offsets=struct.unpack_from('<'+'H'*count,lib,2)+(length,)
        assert offsets[0]==2+count*2
        for index,(start,end) in enumerate(zip(offsets,offsets[1:])):
            assert end-start==85 and lib[start:start+4]==b'\x09\x00\x09\x00'
            source=lib[start+4:end]
            aliases.setdefault(source,[]).append({'rom':'RS201.ROM','member':member,'image':index,
                'member_offset':start,'file_offset':offset+start,'pixel_file_offset':offset+start+4})
    assert len(aliases)==1049 and sum(map(len,aliases.values()))==1134
    if prefix:
        last,_=read_bundle(root/(args.after+'-capture.zip'))
        result={'issue':46,'normal_gui':True,'checkpoint':False,'actions':[],
            'patterns':[{'label':args.case,'choice':0 if args.case=='thermal' else 1,
                'before_receipt':args.before+'-capture.zip','receipt':args.after+'-capture.zip',
                'origin':last['map_origin']}]}
    else:result=json.loads((root/'result.json').read_text())
    assert result['issue']==46 and result['normal_gui'] and not result['checkpoint']
    expected=['thermal','nuclear'] if args.case=='all' else [args.case]
    assert [p['label'] for p in result['patterns']]==expected
    assert [p['choice'] for p in result['patterns']]==[0 if name=='thermal' else 1 for name in expected]
    for action in result['actions']:
        status,_=read_bundle(root/(action['label']+'-capture.zip'))
        assert status['key_reads'][-1]==action['original_read']
        assert status['steps']==action['steps']
    cases=[]
    for pattern in result['patterns']:
        label=pattern['label']
        menu_label=label+('-choose' if label=='nuclear' else '-submenu')
        menu,menu_frame=read_bundle(root/(menu_label+'-capture.zip'))
        choices={s['source_sha256']:s['selection'] for s in json.loads(Path(
            '/workspace/prototypes/hd-style/tool-menus-v1/manifest.json').read_text())['states'] if s['id']=='tool-11'}
        menu_source=b''.join(menu_frame[y*320+196:y*320+265] for y in range(124,159))
        assert menu['dos_blocked'] and choices[sha(menu_source)]==pattern['choice']
        placed,_=read_bundle(root/(label+'-place-capture.zip'))
        assert placed['key_reads'][-1]['Key']==32
        before,old=read_bundle(root/pattern['before_receipt'])
        after,new=read_bundle(root/pattern['receipt'])
        assert scene(before,old) and scene(after,new)
        assert before['map_origin']==after['map_origin']==pattern['origin']
        assert after['map_origin']['Valid']
        known=[]; unknown=[]
        for row in range(15):
            for col in range(29):
                x,y=5+col*9,34+row*9
                original,current=cell(old,x,y),cell(new,x,y)
                if original==current:continue
                record={'cell':[col,row],'native_xy':[x,y],
                    'before_sha256':sha(original),'after_sha256':sha(current)}
                if current in aliases:
                    record['sources']=aliases[current]
                    record['terrain_only']=set(current)<=MATERIAL
                    known.append(record)
                else:unknown.append(record)
        if not prefix:assert known==pattern['known_changes'] and unknown==pattern['unknown_changes']
        structure=[r for r in known if not r['terrain_only']]
        assert structure
        left,top=[min(r['cell'][axis] for r in structure) for axis in (0,1)]
        right,bottom=[max(r['cell'][axis] for r in structure)+1 for axis in (0,1)]
        used=set(); cells=[]
        for row in range(top,bottom):
            for col in range(left,right):
                source=cell(new,5+col*9,34+row*9)
                assert source in aliases,(pattern['label'],col,row,'複合矩形仍有未知格')
                used.update(source)
                corrupt=bytes([source[0]^128])+source[1:]
                assert corrupt not in aliases
                cells.append({'relative_cell':[col-left,row-top],'source_sha256':sha(source),
                    'sources':aliases[source],'single_pixel_negative_rejected':True})
        native_x,native_y=5+left*9,34+top*9
        width,height=(right-left)*9,(bottom-top)*9
        raster=b''.join(new[y*320+native_x:y*320+native_x+width] for y in range(native_y,native_y+height))
        preview=root/(pattern['label']+'-source.png')
        assert not preview.exists()
        png(preview,width,height,raster,bytes(v for color in after['palette'] for v in color))
        cases.append({'label':pattern['label'],'choice':pattern['choice'],
            'receipt':pattern['receipt'],'receipt_sha256':sha((root/pattern['receipt']).read_bytes()),
            'before_receipt_sha256':sha((root/pattern['before_receipt']).read_bytes()),
            'native_rect':[native_x,native_y,width,height],'cell_bounds':[left,top,right,bottom],
            'origin':after['map_origin'],'composite_source_sha256':sha(raster),'cells':cells,
            'used_palette':{str(index):after['palette'][index] for index in sorted(used)},
            'unknown_changes':unknown,'preview':preview.name,'preview_sha256':sha(preview.read_bytes())})
    evidence={'schema':1,'issue':46,'normal_gui':True,'checkpoint':False,
        'rom_sha256':ROM_SHA,'address_space':'RS201.ROM file offsets; zero-based member/image',
        'tool':'power_facility_source_check.py / Python 3.11.2','cases':cases,
        'acknowledged_actions':len(result['actions']),'prefix_only':prefix,'requested_cases':expected,
        'all_two_cases_complete':not prefix and expected==['thermal','nuclear'],
        'level':'已證實，限 requested_cases 選單選取施工後的完整原版來源；相位及模擬規則未外推',
        'scope':'正常原版來源研究；有界停止，不代表 HD、原版退出或存退讀完成'}
    target.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'actions':evidence['acknowledged_actions'],
        'cases':[{k:p[k] for k in ('label','native_rect','cell_bounds')} for p in cases]},ensure_ascii=False))


if __name__=='__main__':main()
