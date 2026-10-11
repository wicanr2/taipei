#!/usr/bin/env bash
# #37：正常城市六功能入口來源，固定 image 與有界程序。
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
orig_dir="${TAIPEI_ORIG:-$project_dir/rs201 模擬台北/模擬台北/RS201}"
test -d "$orig_dir"
test -d "$project_dir/workspace"
test -f "$project_dir/workspace/runs/taipei-preview"
run_name="${TAIPEI_CITY_MENU_RUN:-city-menus-native}"
case "$run_name" in city-menus-native|city-menus-hd|city-menus-native-extra) ;; *) exit 2 ;; esac
timeout 900s docker run --rm --network none --memory 3g --cpus 2 --pids-limit 128 \
  --user "$(id -u):$(id -g)" --name taipei-city-menus \
  --mount "type=bind,src=$project_dir/workspace,dst=/workspace" \
  --mount "type=bind,src=$orig_dir,dst=/orig,readonly" \
  -w /workspace -e DISPLAY=:99 -e LIBGL_ALWAYS_SOFTWARE=1 -e GOMAXPROCS=2 \
  -e "TAIPEI_THEME=${TAIPEI_THEME:-original}" -e "TAIPEI_CITY_MENU_RUN=$run_name" \
  -e "TAIPEI_CITY_MENU_ONLY=${TAIPEI_CITY_MENU_ONLY:-all}" \
  sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3 bash -c '
    set -euo pipefail
    run_dir="/workspace/runs/$TAIPEI_CITY_MENU_RUN"
    mkdir -p "$run_dir" /workspace/runs/xdg
    test "$(stat -c %u:%g "$run_dir")" = "$(id -u):$(id -g)"
    chmod 700 /workspace/runs/xdg
    export XDG_RUNTIME_DIR=/workspace/runs/xdg
    Xvfb :99 -screen 0 1280x900x24 -nolisten tcp > "$run_dir/xvfb.log" 2>&1 &
    xvfb_pid=$!
    trap '\''kill "$xvfb_pid" 2>/dev/null || true; wait 2>/dev/null || true'\'' EXIT
    for i in {1..50}; do test -S /tmp/.X11-unix/X99 && break; sleep .1; done
    { go version; python3 --version; sha256sum /workspace/runs/taipei-preview /orig/RS201.EXE /orig/RS201.ROM; } > "$run_dir/program-provenance.txt"
    python3 /workspace/tools/city_menu_playtest.py > "$run_dir/playtest.log" 2>&1
    find "$run_dir" -user root -o -type d -name "*.md"
  '
