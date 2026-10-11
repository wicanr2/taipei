#!/usr/bin/env bash
# #31：正常冷啟動選單來源與切換驗證。
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
orig_dir="${TAIPEI_ORIG:-$project_dir/rs201 模擬台北/模擬台北/RS201}"
test -d "$orig_dir"
test -d "$project_dir/workspace"
test -f "$project_dir/workspace/runs/taipei-preview"
timeout 360s docker run --rm --network none --memory 3g --cpus 2 --pids-limit 128 \
  --user "$(id -u):$(id -g)" --name taipei-startup-menus \
  --mount "type=bind,src=$project_dir/workspace,dst=/workspace" \
  --mount "type=bind,src=$orig_dir,dst=/orig,readonly" \
  -w /workspace -e DISPLAY=:99 -e LIBGL_ALWAYS_SOFTWARE=1 -e GOMAXPROCS=2 \
  -e "TAIPEI_THEME=${TAIPEI_THEME:-original}" \
  sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3 bash -c '
    set -euo pipefail
    mkdir -p /workspace/runs/startup-menus /workspace/runs/xdg
    chmod 700 /workspace/runs/xdg
    rm -f /workspace/runs/startup-menus/*-capture.zip /workspace/runs/startup-menus/capture.zip /workspace/runs/startup-menus/stop /workspace/runs/startup-menus/result.json
    export XDG_RUNTIME_DIR=/workspace/runs/xdg
    Xvfb :99 -screen 0 1280x900x24 -nolisten tcp > /workspace/runs/startup-menus/xvfb.log 2>&1 &
    xvfb_pid=$!
    game_pid=""
    trap '\''if test -n "$game_pid"; then kill "$game_pid" 2>/dev/null || true; fi; kill "$xvfb_pid" 2>/dev/null || true; wait 2>/dev/null || true'\'' EXIT
    for i in {1..50}; do test -S /tmp/.X11-unix/X99 && break; sleep .1; done
    save_dir=$(mktemp -d /workspace/runs/startup-menu-saves.XXXXXX)
    /workspace/runs/taipei-preview -original /orig -saves "$save_dir" -receipts /workspace/runs/startup-menus -mute -steps-per-update 400000 -materials /workspace/prototypes/hd-style -theme "$TAIPEI_THEME" -stop-file /workspace/runs/startup-menus/stop > /workspace/runs/startup-menus/app.log 2>&1 &
    game_pid=$!
    python3 /workspace/tools/startup_menu_playtest.py > /workspace/runs/startup-menus/playtest.log 2>&1
    wait "$game_pid"
  '
