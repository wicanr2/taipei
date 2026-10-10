"""#24：唯讀查詢原版捲動函式與資料交叉參照，保留原始定位。"""
import hashlib
import json
import struct
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

def instruction(ea):
    return {"ida_ea": ea, "file_offset": ida_loader.get_fileregion_offset(ea),
            "bytes": (ida_bytes.get_bytes(ea, ida_bytes.get_item_size(ea)) or b"").hex(),
            "asm": idc.generate_disasm_line(ea, 0)}

targets = [int(s, 0) for s in idc.ARGV[2:]]
functions = []
for target in targets:
    f = ida_funcs.get_func(target)
    if f:
        functions.append({"start": f.start_ea, "end": f.end_ea,
                          "original_name": idc.get_func_name(f.start_ea),
                          "xrefs": [{"ea": x.frm, "type": x.type} for x in idautils.XrefsTo(f.start_ea)],
                          "instructions": [instruction(ea) for ea in idautils.Heads(f.start_ea, f.end_ea)]})
source = Path(ida_nalt.get_input_file_path())
raw = source.read_bytes()
header_bytes = struct.unpack_from("<H", raw, 8)[0] * 16
reloc_count = struct.unpack_from("<H", raw, 6)[0]
reloc_offset = struct.unpack_from("<H", raw, 24)[0]
relocations = {seg * 16 + off for off, seg in struct.iter_unpack("<HH", raw[reloc_offset:reloc_offset+reloc_count*4])}
data = []
for ea in [0x34522, 0x31acf, 0x31ad1, 0x3456e, 0x34570, 0x3241c, 0x32420]:
    file_offset = ida_loader.get_fileregion_offset(ea)
    data.append({"ida_ea": ea, "file_offset": file_offset,
                 "raw_file_word": struct.unpack_from("<H", raw, file_offset)[0],
                 "mz_relocation": file_offset-header_bytes in relocations,
                 "original_name": idc.get_name(ea),
                 "bytes": (ida_bytes.get_bytes(ea, 12) or b"").hex(),
                 "xrefs": [instruction(x.frm) for x in idautils.XrefsTo(ea)]})
label = idc.ARGV[1]
assert label.replace("-", "").isalnum()
Path("/work/" + label + ".json").write_text(json.dumps({
    "schema": 1, "ida_version": ida_kernwin.get_kernel_version(),
    "input_sha256": hashlib.sha256(raw).hexdigest(),
    "mz_header_bytes": header_bytes, "mz_relocation_count": reloc_count,
    "address_space": "IDA loader linear; file offsets labeled separately",
    "functions": functions, "data": data}, indent=2))
idaapi.qexit(0)
