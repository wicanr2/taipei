#!/usr/bin/env bash
# #46：核能施工前的正常原版財政來源，不修改存檔。
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
orig_dir="${TAIPEI_ORIG:-$project_dir/rs201 模擬台北/模擬台北/RS201}"
test -d "$orig_dir"
test -d "$project_dir/workspace/runs"
test -f "$project_dir/workspace/runs/taipei-preview"
run_name="${TAIPEI_POWER_FUNDING_RUN:-power-facility-funding-native}"
[[ "$run_name" =~ ^power-facility-funding-native(-r[0-9]+)?$ ]]
timeout 3600s docker run --rm --network none --user "$(id -u):$(id -g)" \
  --memory 3g --cpus 2 --pids-limit 128 --name taipei-power-funding-native \
  --mount "type=bind,src=$project_dir/workspace,dst=/workspace" \
  --mount "type=bind,src=$orig_dir,dst=/orig,readonly" \
  -w /workspace -e DISPLAY=:99 -e LIBGL_ALWAYS_SOFTWARE=1 -e GOMAXPROCS=2 \
  -e "TAIPEI_CITY_MENU_RUN=$run_name" \
  -e "TAIPEI_POWER_MANAGED_BUDGET=${TAIPEI_POWER_MANAGED_BUDGET:-0}" \
  sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3 bash -c '
    set -euo pipefail
    out="/workspace/runs/$TAIPEI_CITY_MENU_RUN"
    test ! -e "$out"
    test "$(stat -c %u:%g /workspace/runs)" = "$(id -u):$(id -g)"
    mkdir "$out"
    export XDG_RUNTIME_DIR=/workspace/runs/xdg
    test -d "$XDG_RUNTIME_DIR"
    cp /workspace/tools/power_funding_playtest.* /workspace/tools/city_menu_playtest.py "$out/"
    { go version; python3 --version; sha256sum /workspace/runs/taipei-preview /orig/RS201.EXE /orig/RS201.ROM; } > "$out/program-provenance.txt"
    Xvfb :99 -screen 0 1280x900x24 -nolisten tcp > "$out/xvfb.log" 2>&1 &
    xvfb_pid=$!
    trap '\''kill "$xvfb_pid" 2>/dev/null || true; wait 2>/dev/null || true'\'' EXIT
    for i in {1..50}; do test -S /tmp/.X11-unix/X99 && break; sleep .1; done
    PYTHONPATH=/workspace/tools python3 "$out/power_funding_playtest.py" > "$out/playtest.log" 2>&1
    find /workspace -user root -o -type d -name "*.md"
  '
