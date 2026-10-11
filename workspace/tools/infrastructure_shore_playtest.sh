#!/usr/bin/env bash
# #44：僅補岸邊缺段，沿用原 binary、image 與遊戲速度。
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
orig_dir="${TAIPEI_ORIG:-$project_dir/rs201 模擬台北/模擬台北/RS201}"
test -d "$project_dir/workspace"
test -d "$orig_dir"
test -f "$project_dir/workspace/runs/taipei-preview"
timeout 1200s docker run --rm --network none --user "$(id -u):$(id -g)" \
  --memory 3g --cpus 2 --pids-limit 128 --name taipei-infrastructure-shore \
  --mount "type=bind,src=$project_dir/workspace,dst=/workspace" \
  --mount "type=bind,src=$orig_dir,dst=/orig,readonly" \
  -w /workspace -e DISPLAY=:99 -e LIBGL_ALWAYS_SOFTWARE=1 -e GOMAXPROCS=2 \
  -e TAIPEI_CITY_MENU_RUN=infrastructure-shore-native \
  sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3 bash -c '
    set -euo pipefail
    out=/workspace/runs/infrastructure-shore-native
    test ! -e "$out"
    test "$(stat -c %u:%g /workspace/runs)" = "$(id -u):$(id -g)"
    mkdir -p "$out" /workspace/runs/xdg
    chmod 700 /workspace/runs/xdg
    export XDG_RUNTIME_DIR=/workspace/runs/xdg
    cp /workspace/tools/infrastructure_shore_playtest.* /workspace/tools/infrastructure_playtest.py /workspace/tools/city_menu_playtest.py "$out/"
    { go version; python3 --version; sha256sum /workspace/runs/taipei-preview /orig/RS201.EXE /orig/RS201.ROM; } > "$out/program-provenance.txt"
    Xvfb :99 -screen 0 1280x900x24 -nolisten tcp > "$out/xvfb.log" 2>&1 &
    xvfb_pid=$!
    trap '\''kill "$xvfb_pid" 2>/dev/null || true; wait 2>/dev/null || true'\'' EXIT
    for i in {1..50}; do test -S /tmp/.X11-unix/X99 && break; sleep .1; done
    python3 /workspace/tools/infrastructure_shore_playtest.py > "$out/playtest.log" 2>&1
    find /workspace -user root -o -type d -name "*.md"
  '
