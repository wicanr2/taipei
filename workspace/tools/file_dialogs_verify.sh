#!/usr/bin/env bash
# #38：正常收據、有效負對照、存退讀與呈現無副作用的整批驗證。
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
orig_dir="${TAIPEI_ORIG:-$project_dir/rs201 模擬台北/模擬台北/RS201}"
test -d "$orig_dir"
test -d "$project_dir/workspace"
test -f "$project_dir/workspace/runs/gui-file-dialogs-cold/result.json"
test -f "$project_dir/workspace/runs/file-dialogs-hd/result.json"
test -f "$project_dir/workspace/runs/file-dialogs-negative/result.json"
timeout 900s docker run --rm --network none --memory 3g --cpus 2 --pids-limit 128 \
  --user "$(id -u):$(id -g)" --name taipei-file-dialogs-verify \
  --mount "type=bind,src=$project_dir,dst=/project,readonly" \
  --mount "type=bind,src=$project_dir/workspace,dst=/workspace" \
  --mount "type=bind,src=$orig_dir,dst=/orig,readonly" \
  -e GOMAXPROCS=2 -e PYTHONPATH=/workspace/tools -w /workspace \
  sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3 bash -c '
    set -euo pipefail
    test -O /workspace/runs
    art=/workspace/prototypes/hd-style
    gui=/workspace/runs/gui-file-dialogs-cold
    for dir in /workspace/runs/file-dialogs-hd "$gui"; do
      python3 /workspace/tools/hd_file_dialogs_check.py --receipts "$dir" --out "$dir/files-verification.json"
      /workspace/runs/receipt-check -dir "$dir" -original /orig -file-reference "$art" \
        -font-reference "$art/font-comparison/noto-font.png" -ui-reference "$art/city-icons-b-v1.png" \
        -dialog-reference "$art/new-game-noto-reference-v1.png" \
        -panel-manifest "$art/startup-menus-v1/manifest.json" \
        -tool-panel-manifest "$art/tool-menus-v1/manifest.json" \
        -city-panel-manifest "$art/city-menus-v1/manifest.json" \
        -chrome-reference "$art/city-chrome-v1" -footer-reference "$art"
    done
    python3 - <<'\''PY'\''
from pathlib import Path
from hd_scroll_check import audit_bundle,source59
sources=source59(Path("/orig"))
paths=[p for folder in ["file-dialogs-hd","gui-file-dialogs-cold"] for p in sorted((Path("/workspace/runs")/folder).rglob("*-capture.zip"))]
for path in paths:audit_bundle(path,sources)
print("全部正常收據來源與像素通過：",len(paths),flush=True)
PY
    python3 /workspace/tools/hd_font_check.py --original /orig --materials "$art" --receipts "$gui"
    python3 /workspace/tools/hd_icons_check.py --original /orig --materials "$art" --receipts "$gui"
    python3 /workspace/tools/hd_footer_check.py --receipts "$gui"
    test ! -e /workspace/runs/file-dialogs-state-audit.json
    /workspace/runs/presentation-audit -original /orig -materials "$art" \
      -receipt "$gui/quit-file-theme-hd-capture.zip" -render-interval-steps 24000000 \
      -require-file-dialogs -require-dialog -require-font -require-icons -require-chrome -require-footer \
      -out /workspace/runs/file-dialogs-state-audit.json
    python3 /workspace/tools/file_dialogs_provenance.py
    find /workspace -user root -o -type d -name "*.md"
  '
