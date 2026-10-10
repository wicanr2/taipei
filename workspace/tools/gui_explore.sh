#!/usr/bin/env bash
# 快照只供操作診斷，不能當作正常玩家路徑驗收。
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
orig_dir="${TAIPEI_ORIG:-$project_dir/rs201 模擬台北/模擬台北/RS201}"
test -d "$orig_dir"
test -f "$project_dir/workspace/runs/taipei-preview"
test -f "$project_dir/workspace/runs/city-native.state"
timeout 120s docker run --rm --network none --memory 3g --cpus 2 --pids-limit 128 \
  --user "$(id -u):$(id -g)" --name taipei-gui-explore \
  --mount "type=bind,src=$project_dir/workspace,dst=/workspace" \
  --mount "type=bind,src=$orig_dir,dst=/orig,readonly" \
  -w /workspace -e DISPLAY=:99 -e LIBGL_ALWAYS_SOFTWARE=1 -e GOMAXPROCS=2 \
  -e "TAIPEI_ACTIONS=${TAIPEI_ACTIONS:-}" \
  sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3 bash -c '
    set -euo pipefail
    mkdir -p /workspace/runs/gui-explore /workspace/runs/gui-saves /workspace/runs/xdg
    chmod 700 /workspace/runs/xdg
    export XDG_RUNTIME_DIR=/workspace/runs/xdg
    rm -f /workspace/runs/gui-explore/status.json /workspace/runs/gui-explore/stop
    Xvfb :99 -screen 0 1280x900x24 -nolisten tcp > /workspace/runs/gui-explore/xvfb.log 2>&1 &
    xvfb_pid=$!
    game_pid=""
    trap '\''if test -n "$game_pid"; then kill "$game_pid" 2>/dev/null || true; fi; kill "$xvfb_pid" 2>/dev/null || true; wait 2>/dev/null || true'\'' EXIT
    for i in {1..50}; do test -S /tmp/.X11-unix/X99 && break; sleep .1; done
    /workspace/runs/taipei-preview -original /orig -saves /workspace/runs/gui-saves -receipts /workspace/runs/gui-explore -checkpoint /workspace/runs/city-native.state -stop-file /workspace/runs/gui-explore/stop > /workspace/runs/gui-explore/app.log 2>&1 &
    game_pid=$!
    python3 /workspace/tools/gui_explore.py > /workspace/runs/gui-explore/playtest.log 2>&1
    wait "$game_pid"
  '
