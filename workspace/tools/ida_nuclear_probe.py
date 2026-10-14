"""#46：保留原名與 bytes，窄查正常 Space 施工的檢查與直接呼叫。"""
import hashlib
import json
import os
from pathlib import Path
import ida_auto
import ida_bytes
import ida_funcs
import ida_loader
import ida_nalt
import ida_xref
import idaapi
import idautils
import idc

ida_auto.auto_wait()
sha=lambda p:hashlib.sha256(p).hexdigest()
raw=Path('/orig/RS201.EXE').read_bytes()
assert sha(raw)=='798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3'
assert ida_nalt.retrieve_input_file_sha256().hex()==sha(raw)
targets={int(x,16) for x in os.environ.get('TAIPEI_IDA_TARGETS','16ff4').split(',')}
assert len(targets)<=8
result=[]
for ea in sorted(targets):
    f=ida_funcs.get_func(ea); assert f is not None
    instructions=[]; calls=[]
    for address in idautils.Heads(f.start_ea,f.end_ea):
        line=idc.generate_disasm_line(address,0)
        instructions.append({'ida_ea':address,'file_offset':ida_loader.get_fileregion_offset(address),
            'bytes':(ida_bytes.get_bytes(address,ida_bytes.get_item_size(address)) or b'').hex(),'asm':line})
        if idc.print_insn_mnem(address).lower() in ['call','callf']:
            calls.extend({'from':address,'to':x.to,'name':idc.get_func_name(x.to),'xref_type':x.type}
                for x in idautils.XrefsFrom(address) if x.iscode)
    result.append({'requested_ida_ea':ea,'original_name':idc.get_func_name(f.start_ea),
        'start':f.start_ea,'end':f.end_ea,'instructions':instructions,'calls':calls})
out=os.environ.get('TAIPEI_IDA_OUTPUT','nuclear-build.json'); assert Path(out).name==out
data=[]
for value in filter(None,os.environ.get('TAIPEI_IDA_DATA','').split(',')):
    address=int(value,16); writes=[]; refs=list(idautils.XrefsTo(address))
    for x in refs:
        if x.type!=ida_xref.dr_W:continue
        writes.append({'ida_ea':x.frm,'original_function':idc.get_func_name(x.frm),
            'instructions':[{'ida_ea':a,'bytes':(ida_bytes.get_bytes(a,ida_bytes.get_item_size(a)) or b'').hex(),
                'asm':idc.generate_disasm_line(a,0)} for a in idautils.Heads(x.frm-24,x.frm+24)]})
    data.append({'ida_ea':address,'original_name':idc.get_name(address),
        'file_offset':ida_loader.get_fileregion_offset(address),'bytes':(ida_bytes.get_bytes(address,16) or b'').hex(),
        'direct_xref_count':len(refs),'direct_writes':writes})
report={'schema':1,'issue':46,'input':'RS201.EXE','input_sha256':sha(raw),
    'ida_version':idaapi.get_kernel_version(),'tool_sha256':sha(Path(__file__).read_bytes()),
    'address_space':'IDA loader linear base 0x10000; file offsets separately stated',
    'level':'unknown; original instructions only, no semantic rename','functions':result,'data':data}
Path('/work',out).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
idc.qexit(0)
