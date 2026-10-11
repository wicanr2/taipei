#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
orig_dir="${TAIPEI_ORIG:-$project_dir/rs201 模擬台北/模擬台北/RS201}"
test -d "$orig_dir"
test -f "$project_dir/workspace/runs/taipei-preview"
run_name="${TAIPEI_GUI_RUN:-gui-cold}"
case "$run_name" in gui-cold|gui-file-dialogs-cold|gui-dos-clock-cold|gui-budget-cold|gui-budget-cold-r2|gui-budget-cold-r3|gui-budget-cold-r4) ;; *) exit 2 ;; esac
# #35：包含逐次讀鍵及兩次正常退出的完整流程，保留有界執行。
batch_seconds=600
# #39 額外包含兩次五列 F12 與數值操作，整批上限按新增步數擴充。
case "$run_name" in gui-budget-cold|gui-budget-cold-r2|gui-budget-cold-r3|gui-budget-cold-r4) batch_seconds=2400 ;; esac
timeout "${batch_seconds}s" docker run --rm --network none --memory 3g --cpus 2 --pids-limit 128 \
  --user "$(id -u):$(id -g)" --name taipei-gui-cold \
  --mount "type=bind,src=$project_dir/workspace,dst=/workspace" \
  --mount "type=bind,src=$orig_dir,dst=/orig,readonly" \
  -w /workspace -e DISPLAY=:99 -e LIBGL_ALWAYS_SOFTWARE=1 -e GOMAXPROCS=2 \
  -e "TAIPEI_THEME=${TAIPEI_THEME:-original}" \
  -e "TAIPEI_GUI_RUN=$run_name" \
  -e "TAIPEI_TEST_BUDGET=${TAIPEI_TEST_BUDGET:-0}" \
  sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3 bash -c '
    set -euo pipefail
    run_dir="/workspace/runs/$TAIPEI_GUI_RUN"
    test ! -e "$run_dir"
    mkdir -p "$run_dir" /workspace/runs/xdg
    test "$(stat -c %u:%g "$run_dir")" = "$(id -u):$(id -g)"
    chmod 700 /workspace/runs/xdg
    cp /workspace/tools/gui_playtest.py /workspace/tools/gui_playtest.sh "$run_dir/"
    if test "$TAIPEI_TEST_BUDGET" = 1; then
      cp /workspace/tools/budget_gui.py /workspace/tools/city_menu_playtest.py /workspace/tools/budget_catalog.py "$run_dir/"
    fi
    { go version; python3 --version; sha256sum /workspace/runs/taipei-preview /orig/RS201.EXE /orig/RS201.ROM "$run_dir"/gui_playtest.*; } > "$run_dir/program-provenance.txt"
    export XDG_RUNTIME_DIR=/workspace/runs/xdg
    Xvfb :99 -screen 0 1280x900x24 -nolisten tcp > "$run_dir/xvfb.log" 2>&1 &
    xvfb_pid=$!
    game_pid=""
    trap '\''if test -n "$game_pid"; then kill "$game_pid" 2>/dev/null || true; fi; kill "$xvfb_pid" 2>/dev/null || true; wait 2>/dev/null || true'\'' EXIT
    for i in {1..50}; do test -S /tmp/.X11-unix/X99 && break; sleep .1; done
    save_dir=$(mktemp -d /workspace/runs/gui-cold-saves.XXXXXX)
    export TAIPEI_TEST_SAVES="$save_dir"
    /workspace/runs/taipei-preview -original /orig -saves "$save_dir" -receipts "$run_dir" -mute -steps-per-update 400000 -materials /workspace/prototypes/hd-style -theme "$TAIPEI_THEME" -stop-file "$run_dir/stop" > "$run_dir/app.log" 2>&1 &
    game_pid=$!
    python3 /workspace/tools/gui_playtest.py > "$run_dir/playtest.log" 2>&1
    wait "$game_pid"
    find /workspace -user root -o -type d -name "*.md"
  '
