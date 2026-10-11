#!/usr/bin/env bash
# #29：真實冷啟動的框架與十四工具來源。
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
orig_dir="${TAIPEI_ORIG:-$project_dir/rs201 模擬台北/模擬台北/RS201}"
test -d "$orig_dir"
test -d "$project_dir/workspace"
test -f "$project_dir/workspace/runs/taipei-preview"
run_name="${TAIPEI_CHROME_RUN:-city-chrome-gui}"
case "$run_name" in city-chrome-gui|footer-gui) ;; *) exit 2 ;; esac
timeout 480s docker run --rm --network none --memory 3g --cpus 2 --pids-limit 128 \
  --user "$(id -u):$(id -g)" --name taipei-city-chrome \
  --mount "type=bind,src=$project_dir/workspace,dst=/workspace" \
  --mount "type=bind,src=$orig_dir,dst=/orig,readonly" \
  -w /workspace -e DISPLAY=:99 -e LIBGL_ALWAYS_SOFTWARE=1 -e GOMAXPROCS=2 \
  -e "TAIPEI_THEME=${TAIPEI_THEME:-original}" \
  -e "TAIPEI_CHROME_RUN=$run_name" -e "TAIPEI_FOOTER_TIME=${TAIPEI_FOOTER_TIME:-0}" \
  sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3 bash -c '
    set -euo pipefail
    run_dir="/workspace/runs/$TAIPEI_CHROME_RUN"
    mkdir -p "$run_dir"
    mkdir -p /workspace/runs/xdg
    chmod 700 /workspace/runs/xdg
    rm -f "$run_dir"/*-capture.zip "$run_dir/capture.zip" "$run_dir/stop" "$run_dir/result.json"
    export XDG_RUNTIME_DIR=/workspace/runs/xdg
    Xvfb :99 -screen 0 1280x900x24 -nolisten tcp > "$run_dir/xvfb.log" 2>&1 &
    xvfb_pid=$!
    game_pid=""
    trap '\''if test -n "$game_pid"; then kill "$game_pid" 2>/dev/null || true; fi; kill "$xvfb_pid" 2>/dev/null || true; wait 2>/dev/null || true'\'' EXIT
    for i in {1..50}; do test -S /tmp/.X11-unix/X99 && break; sleep .1; done
    save_dir=$(mktemp -d /workspace/runs/chrome-saves.XXXXXX)
    { go version; python3 --version; sha256sum /workspace/runs/taipei-preview /orig/RS201.EXE /orig/RS201.ROM /workspace/prototypes/hd-style/city-chrome-v1/*.png /workspace/prototypes/hd-style/footer-v1/*; } > "$run_dir/program-provenance.txt"
    /workspace/runs/taipei-preview -original /orig -saves "$save_dir" -receipts "$run_dir" -mute -steps-per-update 400000 -materials /workspace/prototypes/hd-style -theme "$TAIPEI_THEME" -stop-file "$run_dir/stop" > "$run_dir/app.log" 2>&1 &
    game_pid=$!
    python3 /workspace/tools/city_chrome_playtest.py > "$run_dir/playtest.log" 2>&1
    wait "$game_pid"
  '
