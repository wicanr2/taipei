"""#19：只匯出 INT33、INT16 與 IVT 33h 附近的原始定位及呼叫者。"""
import hashlib
import json
from pathlib import Path
import ida_auto
import ida_bytes
import ida_funcs
import ida_kernwin
import ida_loader
import ida_nalt
import idaapi
import idautils
import idc

ida_auto.auto_wait()
sites=[]
for seg in idautils.Segments():
    for ea in idautils.Heads(seg,idc.get_segm_end(seg)):
        if not ida_bytes.is_code(ida_bytes.get_full_flags(ea)):continue
        interrupt=idc.print_insn_mnem(ea).lower()=='int' and idc.get_operand_value(ea,0) in (0x16,0x33)
        vector=any(idc.get_operand_value(ea,i) in (0xcc,0xce) for i in range(2))
        if not (interrupt or vector):continue
        fun=ida_funcs.get_func(ea)
        start=max(idc.get_segm_start(ea),ea-40)
        end=min(idc.get_segm_end(ea),ea+70)
        window=[]
        for at in idautils.Heads(start,end):
            n=ida_bytes.get_item_size(at)
            window.append({'ida_ea':at,'file_offset':ida_loader.get_fileregion_offset(at),
                           'bytes':(ida_bytes.get_bytes(at,n) or b'').hex(),
                           'asm':idc.generate_disasm_line(at,0)})
        sites.append({'ida_ea':ea,'function_ea':fun.start_ea if fun else None,
                      'original_name':idc.get_func_name(ea),'trigger':'interrupt' if interrupt else 'operand_candidate',
                      'xrefs_to_function':[{'ida_ea':x.frm,'type':x.type} for x in idautils.XrefsTo(fun.start_ea)] if fun else [],
                      'window':window,'inference':'unknown'})
label=idc.ARGV[1] if len(idc.ARGV)>1 else 'input-sites'
assert label.replace('-','').isalnum()
targets=[int(s,0) for s in idc.ARGV[2:]] or [167554,161314]
functions=[]
for target in targets:
    f=ida_funcs.get_func(target)
    if not f:continue
    lines=[]
    for ea in idautils.Heads(f.start_ea,f.end_ea):
        lines.append({'ida_ea':ea,'file_offset':ida_loader.get_fileregion_offset(ea),
                      'bytes':(ida_bytes.get_bytes(ea,ida_bytes.get_item_size(ea)) or b'').hex(),
                      'asm':idc.generate_disasm_line(ea,0)})
    functions.append({'target':target,'start':f.start_ea,'end':f.end_ea,
                      'original_name':idc.get_func_name(f.start_ea),'instructions':lines,
                      'xrefs_to_function':[{'ida_ea':x.frm,'type':x.type} for x in idautils.XrefsTo(f.start_ea)]})
source=Path(ida_nalt.get_input_file_path())
data={'schema':1,'ida_version':ida_kernwin.get_kernel_version(),
      'input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
      'address_space':'IDA loader linear addresses; file offsets labeled separately','sites':sites,'functions':functions}
Path('/work/'+label+'.json').write_text(json.dumps(data,indent=2))
idaapi.qexit(0)
