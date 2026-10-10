#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
orig_dir="${TAIPEI_ORIG:-$project_dir/rs201 模擬台北/模擬台北/RS201}"
test -d "$orig_dir"
test -f "$project_dir/workspace/runs/taipei-preview"
timeout 300s docker run --rm --network none --memory 3g --cpus 2 --pids-limit 128 \
  --user "$(id -u):$(id -g)" --name taipei-gui-cold \
  --mount "type=bind,src=$project_dir/workspace,dst=/workspace" \
  --mount "type=bind,src=$orig_dir,dst=/orig,readonly" \
  -w /workspace -e DISPLAY=:99 -e LIBGL_ALWAYS_SOFTWARE=1 -e GOMAXPROCS=2 \
  -e "TAIPEI_THEME=${TAIPEI_THEME:-original}" \
  sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3 bash -c '
    set -euo pipefail
    mkdir -p /workspace/runs/gui-cold /workspace/runs/gui-saves /workspace/runs/xdg
    chmod 700 /workspace/runs/xdg
    # 移除前一次的命名收據，避免不同主題的舊擷取混入本次驗證。
    rm -f /workspace/runs/gui-cold/*-capture.zip /workspace/runs/gui-cold/reload/*-capture.zip
    rm -f /workspace/runs/gui-cold/status.json /workspace/runs/gui-cold/capture.zip /workspace/runs/gui-cold/stop /workspace/runs/gui-cold/result.json
    export XDG_RUNTIME_DIR=/workspace/runs/xdg
    Xvfb :99 -screen 0 1280x900x24 -nolisten tcp > /workspace/runs/gui-cold/xvfb.log 2>&1 &
    xvfb_pid=$!
    game_pid=""
    trap '\''if test -n "$game_pid"; then kill "$game_pid" 2>/dev/null || true; fi; kill "$xvfb_pid" 2>/dev/null || true; wait 2>/dev/null || true'\'' EXIT
    for i in {1..50}; do test -S /tmp/.X11-unix/X99 && break; sleep .1; done
    save_dir=$(mktemp -d /workspace/runs/gui-cold-saves.XXXXXX)
    export TAIPEI_TEST_SAVES="$save_dir"
    /workspace/runs/taipei-preview -original /orig -saves "$save_dir" -receipts /workspace/runs/gui-cold -mute -steps-per-update 400000 -materials /workspace/prototypes/hd-style -theme "$TAIPEI_THEME" -stop-file /workspace/runs/gui-cold/stop > /workspace/runs/gui-cold/app.log 2>&1 &
    game_pid=$!
    python3 /workspace/tools/gui_playtest.py > /workspace/runs/gui-cold/playtest.log 2>&1
    wait "$game_pid"
  '
