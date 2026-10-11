"""#39：窄範圍預算輸入證據，保留原始名稱、bytes 與位址。"""
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
source = Path(ida_nalt.get_input_file_path())
digest = hashlib.sha256(source.read_bytes()).hexdigest()
assert digest == '798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3'


def instruction(ea):
    return {'ida_ea': ea, 'file_offset': ida_loader.get_fileregion_offset(ea),
            'bytes': (ida_bytes.get_bytes(ea, ida_bytes.get_item_size(ea)) or b'').hex(),
            'asm': idc.generate_disasm_line(ea, 0)}


functions = []
unclassified = []
for target in [int(s, 0) for s in idc.ARGV[2:]]:
    f = ida_funcs.get_func(target)
    if f is None:
        unclassified.append({'ida_ea': target, 'evidence': 'unknown; no IDA function boundary',
                             'window': [instruction(ea) for ea in idautils.Heads(max(idc.get_segm_start(target), target-24), target+48)]})
        continue
    functions.append({'target': target, 'start': f.start_ea, 'end': f.end_ea,
                      'original_name': idc.get_func_name(f.start_ea),
                      'xrefs': [instruction(x.frm) for x in idautils.XrefsTo(f.start_ea)],
                      'instructions': [instruction(ea) for ea in idautils.Heads(f.start_ea, f.end_ea)]})
label = idc.ARGV[1]
assert label.replace('-', '').isalnum()
Path(label+'.json').write_text(json.dumps({
    'schema': 1, 'ida_version': ida_kernwin.get_kernel_version(), 'input_sha256': digest,
    'address_space': 'IDA loader linear addresses; raw EXE file offsets separately labeled',
    'functions': functions, 'unclassified_targets': unclassified,
    'scope': '原始指令及交叉參照；未附未分級推測名稱'}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
idaapi.qexit(0)
