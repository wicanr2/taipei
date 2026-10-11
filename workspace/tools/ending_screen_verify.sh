#!/usr/bin/env bash
# #47：正常政績收據與有效負對照；原版狀態另先登記唯一輸入。
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
orig_dir="${TAIPEI_ORIG:-$project_dir/rs201 模擬台北/模擬台北/RS201}"
mode="${1:?請指定 normal 或 negative}"
case "$mode" in normal|negative) ;; *) exit 2 ;; esac
test -d "$orig_dir"
test -d "$project_dir/workspace"
test -f "$project_dir/workspace/runs/receipt-check-ending-r1"
timeout 900s docker run --rm --network none --user "$(id -u):$(id -g)" \
  --memory 2g --cpus 1 --pids-limit 128 --name "taipei-ending-verify-$mode" \
  --mount "type=bind,src=$project_dir/workspace,dst=/workspace" \
  --mount "type=bind,src=$orig_dir,dst=/orig,readonly" \
  -w /workspace -e "TAIPEI_ENDING_VERIFY_MODE=$mode" \
  sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3 bash -c '
    set -euo pipefail
    root=/workspace/runs/gui-ending-scene-cold-r1
    output=/workspace/runs/ending-scene-native
    materials=/workspace/prototypes/hd-style
    test "$(stat -c %u:%g "$output")" = "$(id -u):$(id -g)"
    if test "$TAIPEI_ENDING_VERIFY_MODE" = negative; then
      test -f "$root/quit-score-capture.zip"
      python3 /workspace/tools/hd_ending_screen_negative.py --receipt "$root/quit-score-capture.zip" \
        --out /workspace/runs/ending-scene-hd-negative-r1
    else
      test -f "$root/result.json"
      test -f "$root/ending-gui.json"
      test ! -e "$output/normal-receipts-r1.json"
      test ! -e "$output/normal-go-check-r1.log"
      python3 /workspace/tools/hd_ending_screen_check.py --receipts "$root" --out "$output/normal-receipts-r1.json"
      /workspace/runs/receipt-check-ending-r1 -dir "$root" -original /orig \
        -ending-reference "$materials" -power-reference "$materials" \
        -budget-reference "$materials" -file-reference "$materials" \
        -panel-manifest "$materials/startup-menus-v1/manifest.json" \
        -tool-panel-manifest "$materials/tool-menus-v1/manifest.json" \
        -city-panel-manifest "$materials/city-menus-v1/manifest.json" \
        -font-reference "$materials/font-comparison/noto-font.png" \
        -ui-reference "$materials/city-icons-b-v1.png" \
        -dialog-reference "$materials/new-game-noto-reference-v1.png" \
        -chrome-reference "$materials/city-chrome-v1" -footer-reference "$materials" \
        > "$output/normal-go-check-r1.log"
    fi
    find /workspace -user root -o -type d -name "*.md"
  '
