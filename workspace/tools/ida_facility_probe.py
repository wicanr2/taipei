"""#60: read-only IDA query for the sampled normal construction stall."""
import hashlib
import json
import os
from pathlib import Path

import ida_auto
import ida_bytes
import ida_funcs
import ida_loader
import ida_nalt
import idaapi
import idautils
import idc

ida_auto.auto_wait()
raw=Path('/orig/RS201.EXE').read_bytes()
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(raw)=='798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3'


def ins(ea):
    return {'ida_ea':ea,'file_offset':ida_loader.get_fileregion_offset(ea),
            'bytes':(ida_bytes.get_bytes(ea,ida_bytes.get_item_size(ea)) or b'').hex(),
            'asm':idc.generate_disasm_line(ea,0)}


targets={int(s,16) for s in os.environ.get('TAIPEI_IDA_TARGETS','24fb9,24fc2').split(',')}
output=os.environ.get('TAIPEI_IDA_OUTPUT','stall.json')
assert Path(output).name==output and output.endswith('.json')
functions=[]
parents=set()
for address in sorted(targets):
    f=ida_funcs.get_func(address)
    if f:
        functions.append({'sampled_ida_ea':address,'original_name':idc.get_func_name(f.start_ea),
            'start':f.start_ea,'end':f.end_ea,
            'instructions':[ins(ea) for ea in idautils.Heads(f.start_ea,f.end_ea)],
            'xrefs':[{'from':x.frm,'to':x.to,'type':x.type} for x in idautils.XrefsTo(f.start_ea)]})
        for x in idautils.XrefsTo(f.start_ea):
            parent=ida_funcs.get_func(x.frm)
            if parent:parents.add(parent.start_ea)
    else:
        functions.append({'sampled_ida_ea':address,'original_name':None,
            'instructions':[ins(ea) for ea in idautils.Heads(address-48,address+48)]})
for address in sorted(parents):
    f=ida_funcs.get_func(address)
    functions.append({'original_name':idc.get_func_name(address),'start':address,'end':f.end_ea,
        'instructions':[ins(ea) for ea in idautils.Heads(address,f.end_ea)]})
report={'schema':1,'issue':60,'ida_version':idaapi.get_kernel_version(),'input':'RS201.EXE',
        'input_sha256':sha(raw),'database_input_sha256':ida_nalt.retrieve_input_file_sha256().hex(),
        'address_space':'IDA linear image base 0x10000; dosgolem CS*16+IP + 0xEF00 per fixed input mapping 004',
        'mapping_level':'已證實，固定版本映射；函式語意待審查','functions':functions}
Path('/work',output).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
idc.qexit(0)
