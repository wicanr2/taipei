"""#31：文字呼叫端的唯讀 IDA 查詢；保留名稱、bytes 與位址基準。"""
import hashlib
import json
import os
from pathlib import Path

import ida_auto
import ida_bytes
import ida_funcs
import ida_kernwin
import ida_loader
import ida_nalt
import ida_segment
import idaapi
import idautils
import idc

ida_auto.auto_wait()
source = Path(os.environ.get('TAIPEI_IDA_EXE', ida_nalt.get_input_file_path()))
raw = source.read_bytes()
assert hashlib.sha256(raw).hexdigest() == '798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3'


def instruction(ea):
    return {'ida_ea': ea, 'file_offset': ida_loader.get_fileregion_offset(ea),
            'bytes': (ida_bytes.get_bytes(ea, ida_bytes.get_item_size(ea)) or b'').hex(),
            'asm': idc.generate_disasm_line(ea, 0)}


strings = []
targets = set(int(value, 0) for value in idc.ARGV[2:])
dseg = ida_segment.get_segm_by_name('dseg')
data_base = ida_segment.get_segm_base(dseg)
query_texts = ['離開', '檔案', '市長', '您的任務', '災難城市', '大台北']
if idc.ARGV[1] == 'endings':
    query_texts += ['\u3000\u3000\u3000恭喜您', '\u3000\u3000全體市民向您', '很抱歉！！您的任務']
if idc.ARGV[1] == 'remaining':
    query_texts += ['民國七十八年', '住宅問題', '得手了', '有圖為證', '民族救星',
                    '如果您不孚', '市長大人', '請輸入數字密碼', '本選項須', '確定離開',
                    'Text0.IS2', '模擬台北', '啊...你是什麼意思']
for text in query_texts:
    data = text.encode('cp950')
    start = 0
    while True:
        off = raw.find(data, start)
        if off < 0:
            break
        start = off+1
        ea = ida_loader.get_fileregion_ea(off)
        refs = []
        for ref in idautils.XrefsTo(ea):
            refs.append(instruction(ref.frm))
            func = ida_funcs.get_func(ref.frm)
            if func:
                targets.add(func.start_ea)
            elif idc.ARGV[1] == 'remaining':
                for indirect in idautils.XrefsTo(ref.frm):
                    refs.append({'via_data_ea': ref.frm, **instruction(indirect.frm)})
                    parent = ida_funcs.get_func(indirect.frm)
                    if parent:
                        targets.add(parent.start_ea)
        strings.append({'text': text, 'code_hex': data.hex(), 'file_offset': off,
                        'ida_ea': ea, 'original_name': idc.get_name(ea), 'xrefs': refs,
                        'evidence': 'confirmed encoded bytes; calls require data-flow review'})

# 16-bit 程式可用 DS 相對立即數取字串位址，沒有 IDA 直接資料 xref。
# 立即數相等只列為線索，完整函式與呼叫端仍須另行資料流審查。
offsets = {record['ida_ea']-data_base for record in strings}
candidates = []
for start in idautils.Functions():
    func = ida_funcs.get_func(start)
    for ea in idautils.Heads(func.start_ea, func.end_ea):
        values = [idc.get_operand_value(ea, op) for op in range(3)
                  if idc.get_operand_type(ea, op) == idc.o_imm]
        if any(value in offsets for value in values):
            targets.add(start)
            candidates.append({'instruction': instruction(ea), 'immediates': values,
                               'evidence': 'hypothesis; immediate equals DS-relative string offset'})

functions = []
unbounded_ranges = []
for target in sorted(targets):
    func = ida_funcs.get_func(target)
    if not func:
        unbounded_ranges.append({'start': target, 'end': target+0xc0,
                                 'evidence': 'unknown function boundary; navigation only',
                                 'instructions': [instruction(ea) for ea in idautils.Heads(target, target+0xc0)]})
        continue
    functions.append({'start': func.start_ea, 'end': func.end_ea,
                      'original_name': idc.get_func_name(func.start_ea),
                      'xrefs': [instruction(ref.frm) for ref in idautils.XrefsTo(func.start_ea)],
                      'instructions': [instruction(ea) for ea in idautils.Heads(func.start_ea, func.end_ea)]})

label = idc.ARGV[1]
assert label.replace('-', '').isalnum()
Path(label+'.json').write_text(json.dumps({
    'schema': 1, 'ida_version': ida_kernwin.get_kernel_version(),
    'input_sha256': hashlib.sha256(raw).hexdigest(),
    'address_space': 'IDA loader linear; raw EXE file offsets labeled separately',
    'data_segment_base': data_base, 'strings': strings, 'candidate_sites': candidates,
    'functions': functions, 'unbounded_ranges': unbounded_ranges,
    'scope': 'text source and call-site evidence; no production text hook or speculative renaming'},
    ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
idaapi.qexit(0)
