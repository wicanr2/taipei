"""#19：新 image／UID 組合的最小 IDAPython 輸出探針。"""
import hashlib
import json
from pathlib import Path
import ida_auto
import ida_ida
import ida_kernwin
import ida_nalt
import ida_segment
import idaapi
import idautils

ida_auto.auto_wait()
source = Path(ida_nalt.get_input_file_path())
segments = []
for ea in idautils.Segments():
    s = ida_segment.getseg(ea)
    segments.append({'start':s.start_ea,'end':s.end_ea,'base':ida_segment.get_segm_base(s),
                     'name':ida_segment.get_segm_name(s),'bitness':s.bitness})
data = {'schema':1,'ida_version':ida_kernwin.get_kernel_version(),
        'input_name':source.name,'input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'address_space':'IDA loader linear addresses; segment bases listed separately',
        'min_ea':ida_ida.inf_get_min_ea(),'max_ea':ida_ida.inf_get_max_ea(),
        'functions':len(list(idautils.Functions())),'segments':segments}
Path('/work/probe.json').write_text(json.dumps(data,indent=2))
idaapi.qexit(0)
