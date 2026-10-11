#!/usr/bin/env bash
# #38：正常 GUI 與獨立 Python／Go 整框核對，保留既有收據。
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
orig_dir="${TAIPEI_ORIG:-$project_dir/rs201 模擬台北/模擬台北/RS201}"
test -d "$orig_dir"
test -d "$project_dir/workspace"
test -f "$project_dir/workspace/runs/taipei-preview"
test -f "$project_dir/workspace/runs/receipt-check"
timeout 900s docker run --rm --network none --memory 3g --cpus 2 --pids-limit 128 \
  --user "$(id -u):$(id -g)" --name taipei-file-dialogs-hd \
  --mount "type=bind,src=$project_dir/workspace,dst=/workspace" \
  --mount "type=bind,src=$orig_dir,dst=/orig,readonly" \
  -e DISPLAY=:99 -e LIBGL_ALWAYS_SOFTWARE=1 -e GOMAXPROCS=2 -w /workspace \
  sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3 bash -c '
    set -euo pipefail
    run_dir=/workspace/runs/file-dialogs-hd
    test ! -e "$run_dir"
    mkdir "$run_dir"
    test "$(stat -c %u:%g "$run_dir")" = "$(id -u):$(id -g)"
    test -d /workspace/runs/xdg
    export XDG_RUNTIME_DIR=/workspace/runs/xdg
    Xvfb :99 -screen 0 1280x900x24 -nolisten tcp > "$run_dir/xvfb.log" 2>&1 &
    xvfb_pid=$!
    trap '\''kill "$xvfb_pid" 2>/dev/null || true; wait 2>/dev/null || true'\'' EXIT
    for i in {1..50}; do test -S /tmp/.X11-unix/X99 && break; sleep .1; done
    for file in file_dialog_hd_playtest.py file_dialog_hd_playtest.sh file_dialog_catalog.py city_menu_playtest.py hd_file_dialogs_check.py hd_scroll_check.py; do
      cp "/workspace/tools/$file" "$run_dir/$file"
    done
    { go version; python3 --version; sha256sum /workspace/runs/taipei-preview /workspace/runs/receipt-check /orig/RS201.EXE /orig/RS201.ROM "$run_dir"/*.py "$run_dir"/*.sh; } > "$run_dir/program-provenance.txt"
    python3 /workspace/tools/file_dialog_hd_playtest.py > "$run_dir/playtest.log" 2>&1
    python3 /workspace/tools/hd_file_dialogs_check.py --receipts "$run_dir" --out "$run_dir/files-verification.json" > "$run_dir/files-check.log"
    /workspace/runs/receipt-check -dir "$run_dir" -file-reference /workspace/prototypes/hd-style -original /orig \
      -panel-manifest /workspace/prototypes/hd-style/startup-menus-v1/manifest.json \
      -city-panel-manifest /workspace/prototypes/hd-style/city-menus-v1/manifest.json \
      -font-reference /workspace/prototypes/hd-style/font-comparison/noto-font.png \
      -ui-reference /workspace/prototypes/hd-style/city-icons-b-v1.png \
      -dialog-reference /workspace/prototypes/hd-style/new-game-noto-reference-v1.png \
      -chrome-reference /workspace/prototypes/hd-style/city-chrome-v1 \
      -footer-reference /workspace/prototypes/hd-style > "$run_dir/receipt-check.log"
    find /workspace -user root -o -type d -name "*.md"
  '
