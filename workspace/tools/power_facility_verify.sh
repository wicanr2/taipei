#!/usr/bin/env bash
# #46：正常火力收據與有效負對照。狀態重播另先登記唯一輸入。
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
orig_dir="${TAIPEI_ORIG:-$project_dir/rs201 模擬台北/模擬台北/RS201}"
mode="${1:?請指定 normal 或 negative}"
case "$mode" in normal|negative) ;; *) exit 2 ;; esac
test -d "$orig_dir"
test -d "$project_dir/workspace"
test -f "$project_dir/workspace/runs/receipt-check"
timeout 900s docker run --rm --network none --user "$(id -u):$(id -g)" \
  --memory 2g --cpus 1 --pids-limit 128 --name "taipei-power-verify-$mode" \
  --mount "type=bind,src=$project_dir/workspace,dst=/workspace" \
  --mount "type=bind,src=$orig_dir,dst=/orig,readonly" \
  -w /workspace -e "TAIPEI_POWER_VERIFY_MODE=$mode" \
  sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3 bash -c '
    set -euo pipefail
    root=/workspace/runs/gui-power-facility-cold-r3
    output=/workspace/runs/power-facility-thermal-native
    test "$(stat -c %u:%g "$output")" = "$(id -u):$(id -g)"
    if test "$TAIPEI_POWER_VERIFY_MODE" = negative; then
      test -f /workspace/runs/gui-power-facility-cold-r1/power-complete-capture.zip
      python3 /workspace/tools/hd_power_facility_negative.py --receipt /workspace/runs/gui-power-facility-cold-r1/power-complete-capture.zip \
        --out /workspace/runs/power-facility-hd-negative-r1
    else
      test -f "$root/power-complete-capture.zip"
      test -f "$root/result.json"
      test ! -e "$output/hd-receipts-r1.json"
      test ! -e "$output/hd-receipt-check-r1.log"
      python3 /workspace/tools/hd_power_facility_check.py --receipts "$root" --out "$output/hd-receipts-r1.json"
      materials=/workspace/prototypes/hd-style
      /workspace/runs/receipt-check -dir "$root" -original /orig \
        -power-reference "$materials" -budget-reference "$materials" -file-reference "$materials" \
        -panel-manifest "$materials/startup-menus-v1/manifest.json" \
        -tool-panel-manifest "$materials/tool-menus-v1/manifest.json" \
        -city-panel-manifest "$materials/city-menus-v1/manifest.json" \
        -font-reference "$materials/font-comparison/noto-font.png" \
        -ui-reference "$materials/city-icons-b-v1.png" \
        -dialog-reference "$materials/new-game-noto-reference-v1.png" \
        -chrome-reference "$materials/city-chrome-v1" -footer-reference "$materials" \
        > "$output/hd-receipt-check-r1.log"
    fi
    find /workspace -user root -o -type d -name "*.md"
  '
