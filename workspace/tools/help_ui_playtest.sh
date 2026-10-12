#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
orig_dir="${TAIPEI_ORIG:-$project_dir/rs201 模擬台北/模擬台北/RS201}"
test -d "$orig_dir"
test -d "$project_dir/workspace"
test -f "$project_dir/workspace/runs/taipei-preview-help-r1"
run_name="${TAIPEI_HELP_RUN:-help-ui-cold-r1}"
case "$run_name" in help-ui-cold-r1|help-ui-cold-r2|help-ui-cold-r3) ;; *) exit 2 ;; esac
timeout 360s docker run --rm --network none --user "$(id -u):$(id -g)" \
  --memory 3g --cpus 2 --pids-limit 128 --label project=taipei --name "taipei-$run_name" \
  --mount "type=bind,src=$project_dir/workspace,dst=/workspace" \
  --mount "type=bind,src=$orig_dir,dst=/orig,readonly" \
  -e DISPLAY=:99 -e LIBGL_ALWAYS_SOFTWARE=1 -e GOMAXPROCS=2 -e "TAIPEI_HELP_RUN=$run_name" \
  sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3 bash -c '
    set -euo pipefail
    test ! -e "/workspace/runs/$TAIPEI_HELP_RUN"
    test "$(stat -c %u:%g /workspace/runs)" = "$(id -u):$(id -g)"
    Xvfb :99 -screen 0 1280x900x24 -nolisten tcp > /workspace/runs/help-xvfb.log 2>&1 &
    xvfb_pid=$!
    trap '\''kill "$xvfb_pid" 2>/dev/null || true; wait 2>/dev/null || true'\'' EXIT
    for i in {1..50}; do test -S /tmp/.X11-unix/X99 && break; sleep .1; done
    python3 /workspace/tools/help_ui_playtest.py
    find /workspace -user root -o -type d -name "*.md"
  '
