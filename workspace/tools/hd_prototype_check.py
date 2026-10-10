"""離線原型的真實圖塊失配與素材撤除負對照。"""
import hashlib
import json
import subprocess
from pathlib import Path

root = Path('/materials')
frame = Path('/workspace/runs/gui-cold/city-map-frame.png')
indices = frame.with_name('city-map-frame-index.bin')
assert frame.is_file() and indices.is_file()

def render(label, raw, materials):
    out = root / label
    subprocess.run([str(root/'hd-prototype'), '-frame', str(frame), '-indices', str(raw),
                    '-rom', '/orig/RS201.ROM', '-materials', str(materials), '-out', str(out)], check=True)
    return out, json.loads((out/'receipt.json').read_text())

baseline, normal = render('composed-v1', indices, root)
empty = root/'empty-materials'
empty.mkdir(exist_ok=True)
assert not any(empty.iterdir())
withdrawn, missing = render('negative-missing-materials', indices, empty)
assert missing['painted_cells'] == 0 and missing['fallback_cells'] == 435
assert missing['changed_hd_pixels'] == 0
assert (withdrawn/'hd-b-1280x800.png').read_bytes() == (withdrawn/'original-1280x800.png').read_bytes()

# 從確實覆繪的第一格挑一個色號，破壞完整來源匹配。
cell = normal['cells'][0]
raw = bytearray(indices.read_bytes())
at = cell['y']*320 + cell['x']
raw[at] = 255
corrupt = root/'negative-mismatch-indices.bin'
corrupt.write_bytes(raw)
mismatched, mismatch = render('negative-source-mismatch', corrupt, root)
assert mismatch['painted_cells'] == normal['painted_cells']-1
assert mismatch['matched_cells'] == normal['matched_cells']-1
assert mismatch['fallback_cells'] == normal['fallback_cells']+1
assert all(r['outside_differences'] == 0 for r in [normal, missing, mismatch])
result = {'prototype': True, 'negative_missing_materials': True, 'negative_source_mismatch': True,
          'normal_painted_cells': normal['painted_cells'], 'normal_fallback_cells': normal['fallback_cells'],
          'native_indices_sha256': hashlib.sha256(indices.read_bytes()).hexdigest(),
          'negative_control_only': '失配色號僅用於離線負對照，未送入原版機器'}
(root/'negative-controls.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result))
