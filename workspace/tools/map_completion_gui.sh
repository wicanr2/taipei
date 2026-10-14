#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
original_dir="$project_dir/rs201 模擬台北/模擬台北/RS201"
seed1="$project_dir/workspace/runs/power-scenario-scan-r1/city-1/saves"
seed2="$project_dir/workspace/runs/power-scenario-scan-r2/city-2/saves"
for dir in "$original_dir" "$project_dir/workspace" "$project_dir/workspace/runs" "$seed1" "$seed2"; do test -d "$dir"; done
for dir in "$seed1" "$seed2"; do test -f "$dir/FUND.SAV"; done
run_name="${TAIPEI_CITY_MENU_RUN:-gui-map-r1}"
timeout 1800s docker run --rm --network none --label project=taipei --name "taipei-$run_name" \
  --user "$(id -u):$(id -g)" --memory 3g --cpus 2 --pids-limit 128 \
  --mount "type=bind,src=$project_dir/workspace,dst=/workspace,readonly" \
  --mount "type=bind,src=$project_dir/workspace/runs,dst=/workspace/runs" \
  --mount "type=bind,src=$seed1,dst=/workspace/runs/power-scenario-scan-r1/city-1/saves,readonly" \
  --mount "type=bind,src=$seed2,dst=/workspace/runs/power-scenario-scan-r2/city-2/saves,readonly" \
  --mount "type=bind,src=$seed1,dst=/seed1,readonly" \
  --mount "type=bind,src=$seed2,dst=/seed2,readonly" \
  --mount "type=bind,src=$original_dir,dst=/orig,readonly" \
  -e DISPLAY=:99 -e LIBGL_ALWAYS_SOFTWARE=1 -e PYTHONDONTWRITEBYTECODE=1 \
  -e "TAIPEI_CITY_MENU_RUN=$run_name" -e "TAIPEI_MAP_PHASE=${TAIPEI_MAP_PHASE:-hd}" \
  -e "TAIPEI_MAP_BINARY=${TAIPEI_MAP_BINARY:-taipei-preview-map-r2}" \
  -e "TAIPEI_MAP_RECEIPT_UPDATES=${TAIPEI_MAP_RECEIPT_UPDATES:-1}" \
  sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3 bash -c '
    set -euo pipefail
    test "$(stat -c %u:%g /workspace/runs)" = 1000:1000
    Xvfb :99 -screen 0 1280x900x24 -nolisten tcp > "/workspace/runs/$TAIPEI_CITY_MENU_RUN-xvfb.log" 2>&1 & xp=$!
    trap '\''code=$?; trap - EXIT; kill "$xp" 2>/dev/null || true; wait "$xp" 2>/dev/null || true; exit "$code"'\'' EXIT
    for i in {1..50}; do test -S /tmp/.X11-unix/X99 && break; sleep .1; done
    driver_log="/workspace/runs/$TAIPEI_CITY_MENU_RUN-driver.log"
    if python3 /workspace/tools/map_completion_gui.py > "$driver_log" 2>&1; then tail -n 5 "$driver_log";
    else code=$?; tail -n 25 "$driver_log"; exit "$code"; fi
    find "/workspace/runs/$TAIPEI_CITY_MENU_RUN" -user root -o -type d -name "*.md"
  '
