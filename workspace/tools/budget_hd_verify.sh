#!/usr/bin/env bash
# #39/#42/#43：核對已保存的新正常收據，不覆寫前件、不替代真機或封包。
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
orig_dir="${TAIPEI_ORIG:-$project_dir/rs201 模擬台北/模擬台北/RS201}"
mode="${1:?請指定 scenario、cold 或 provenance}"
case "$mode" in scenario|cold|provenance) ;; *) exit 2 ;; esac
test -d "$orig_dir"
test -d "$project_dir/workspace/runs/budget-source"
test -f "$project_dir/workspace/runs/receipt-check"
timeout 600s docker run --rm --network none --memory 2g --cpus 1 --pids-limit 128 \
  --user "$(id -u):$(id -g)" \
  --mount "type=bind,src=$project_dir,dst=/project,readonly" \
  --mount "type=bind,src=$project_dir/workspace,dst=/workspace" \
  --mount "type=bind,src=$orig_dir,dst=/orig,readonly" \
  -e "TAIPEI_BUDGET_VERIFY_MODE=$mode" -w /workspace \
  sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3 bash -c '
    set -euo pipefail
    out=/workspace/runs/budget-source
    test "$(stat -c %u:%g "$out")" = "$(id -u):$(id -g)"
    if test "$TAIPEI_BUDGET_VERIFY_MODE" = provenance; then
      python3 /workspace/tools/budget_hd_provenance.py
    else
      if test "$TAIPEI_BUDGET_VERIFY_MODE" = cold; then
        root=/workspace/runs/gui-budget-cold-r4
        name=cold
        revision=r4
        extra=--require-five-rows
      else
        root=/workspace/runs/budget-hd-scenario-r2
        name=scenario
        revision=r2
        extra=--require-nonzero
      fi
      test -f "$root/result.json"
      test -f /workspace/prototypes/hd-style/tool-menus-v1/manifest.json
      test ! -e "$out/$name-budget-$revision.json"
      python3 /workspace/tools/hd_budget_check.py --receipts "$root" --out "$out/$name-budget-$revision.json" "$extra"
      /workspace/runs/receipt-check -dir "$root" -budget-reference /workspace/prototypes/hd-style -original /orig \
        -file-reference /workspace/prototypes/hd-style \
        -panel-manifest /workspace/prototypes/hd-style/startup-menus-v1/manifest.json \
        -tool-panel-manifest /workspace/prototypes/hd-style/tool-menus-v1/manifest.json \
        -city-panel-manifest /workspace/prototypes/hd-style/city-menus-v1/manifest.json \
        -font-reference /workspace/prototypes/hd-style/font-comparison/noto-font.png \
        -ui-reference /workspace/prototypes/hd-style/city-icons-b-v1.png \
        -dialog-reference /workspace/prototypes/hd-style/new-game-noto-reference-v1.png \
        -chrome-reference /workspace/prototypes/hd-style/city-chrome-v1 \
        -footer-reference /workspace/prototypes/hd-style > "$out/$name-receipt-check-$revision.log"
      python3 - "$root" > "$out/$name-pixels-$revision.log" <<'\''PY'\''
import sys
from pathlib import Path
sys.path.insert(0,"/workspace/tools")
from hd_scroll_check import audit_bundle, source59
root=Path(sys.argv[1])
sources=source59(Path("/orig"))
receipts=sorted(root.rglob("*-capture.zip"))
assert receipts
for path in receipts: audit_bundle(path,sources)
print("全部正常收據來源、完整呈現與區外像素通過",len(receipts))
PY
      cat "$out/$name-receipt-check-$revision.log" "$out/$name-pixels-$revision.log"
      if test "$TAIPEI_BUDGET_VERIFY_MODE" = cold; then
        python3 /workspace/tools/hd_budget_negative.py --receipt "$root/budget-row-1-theme-hd-capture.zip" \
          --out /workspace/runs/budget-hd-negative-r2 > "$out/negative-r2.log"
        cat "$out/negative-r2.log"
      fi
    fi
    find /workspace -user root -o -type d -name "*.md"
  '
