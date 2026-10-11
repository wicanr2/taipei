#!/usr/bin/env bash
# #37：只讀正常 GUI 收據，獨立核對像素、控制、有效負對照及原版狀態。
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
orig_dir="${TAIPEI_ORIG:-$project_dir/rs201 模擬台北/模擬台北/RS201}"
test -d "$project_dir/workspace"
test -d "$orig_dir"
test -f "$project_dir/workspace/runs/city-menus-hd/result.json"
test -f "$project_dir/workspace/runs/gui-cold/result.json"
timeout 900s docker run --rm --network none --memory 3g --cpus 2 --pids-limit 128 \
  --user "$(id -u):$(id -g)" --name taipei-city-panels-verify \
  --mount "type=bind,src=$project_dir/workspace,dst=/workspace" \
  --mount "type=bind,src=$orig_dir,dst=/orig,readonly" \
  -e GOMAXPROCS=2 -w /workspace \
  sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3 bash -c '
    set -euo pipefail
    test -O /workspace/runs
    art=/workspace/prototypes/hd-style
    menus=/workspace/runs/city-menus-hd
    python3 /workspace/tools/city_menu_source_check.py --receipts "$menus" \
      --sources "$art/city-menu-sources-v1.json" --out "$menus/controls-verification.json"
    python3 /workspace/tools/hd_city_panels_check.py --receipts "$menus"
    for dir in "$menus" /workspace/runs/gui-cold; do
      /workspace/runs/receipt-check -dir "$dir" \
        -font-reference "$art/font-comparison/noto-font.png" \
        -ui-reference "$art/city-icons-b-v1.png" \
        -dialog-reference "$art/new-game-noto-reference-v1.png" \
        -panel-manifest "$art/startup-menus-v1/manifest.json" \
        -tool-panel-manifest "$art/tool-menus-v1/manifest.json" \
        -city-panel-manifest "$art/city-menus-v1/manifest.json" \
        -chrome-reference "$art/city-chrome-v1" -footer-reference "$art"
    done
    for key in 1 5; do
      python3 /workspace/tools/hd_tool_panels_negative.py --family city \
        --receipt "$menus/f$key/open-capture.zip" --out "/workspace/runs/city-panels-negative/f$key"
    done
    python3 /workspace/tools/hd_font_check.py --original /orig --materials "$art" --receipts /workspace/runs/gui-cold
    python3 /workspace/tools/hd_icons_check.py --original /orig --materials "$art" --receipts /workspace/runs/gui-cold
    test ! -e /workspace/runs/city-panels-state-audit.json
    /workspace/runs/presentation-audit -original /orig -materials "$art" \
      -receipt "$menus/f6/escape-capture.zip" -render-interval-steps 24000000 \
      -require-dialog -require-font -require-icons -require-chrome -require-footer \
      -require-city-panels -out /workspace/runs/city-panels-state-audit.json
    find /workspace -user root -o -type d -name "*.md"
  '
