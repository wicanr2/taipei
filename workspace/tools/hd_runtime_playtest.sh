#!/usr/bin/env bash
# #25：原版城市持續運行的有界 GUI 抽樣，限現有 HD DRAFT。
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
orig_dir="${TAIPEI_ORIG:-$project_dir/rs201 模擬台北/模擬台北/RS201}"
test -d "$orig_dir"
test -d "$project_dir/workspace/prototypes/hd-style"
test -f "$project_dir/workspace/runs/taipei-preview"
timeout 420s docker run --rm --network none --memory 3g --cpus 2 --pids-limit 128 \
  --user "$(id -u):$(id -g)" --name taipei-hd-runtime \
  --mount "type=bind,src=$project_dir/workspace,dst=/workspace" \
  --mount "type=bind,src=$orig_dir,dst=/orig,readonly" \
  -e DISPLAY=:99 -e LIBGL_ALWAYS_SOFTWARE=1 -e GOMAXPROCS=2 \
  sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3 bash -c '
    set -euo pipefail
    out=/workspace/runs/hd-runtime
    mkdir -p "$out/xdg" "$out/saves"
    test -O "$out"
    chmod 700 "$out/xdg"
    export XDG_RUNTIME_DIR="$out/xdg"
    rm -f "$out/capture.zip" "$out/stop" "$out/result.json" "$out/"*-capture.zip
    Xvfb :99 -screen 0 1280x900x24 -nolisten tcp > "$out/xvfb.log" 2>&1 &
    xvfb_pid=$!; game_pid=""
    trap '\''if test -n "$game_pid"; then kill "$game_pid" 2>/dev/null || true; fi; kill "$xvfb_pid" 2>/dev/null || true; wait 2>/dev/null || true'\'' EXIT
    for _ in {1..50}; do test -S /tmp/.X11-unix/X99 && break; sleep .1; done
    /workspace/runs/taipei-preview -original /orig -saves "$out/saves" -receipts "$out" \
      -mute -steps-per-update 400000 -theme hd-b -materials /workspace/prototypes/hd-style \
      -stop-file "$out/stop" > "$out/app.log" 2>&1 &
    game_pid=$!
    python3 /workspace/tools/hd_runtime_playtest.py > "$out/playtest.log" 2>&1
    wait "$game_pid"
  '
