#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
original_dir="$project_dir/rs201 模擬台北/模擬台北/RS201"
mode="${1:-gui}"
[[ "$mode" == source || "$mode" == gui ]]
for dir in "$original_dir" "$project_dir/workspace" "$project_dir/workspace/tools" \
  "$project_dir/workspace/app" "$project_dir/workspace/prototypes"; do test -d "$dir"; done
timeout 1500s docker run --rm --network none --label project=taipei --name "taipei-civic-$mode" \
  --user "$(id -u):$(id -g)" --memory 3g --cpus 2 --pids-limit 128 \
  --mount "type=bind,src=$project_dir/workspace,dst=/workspace" \
  --mount "type=bind,src=$project_dir/workspace/tools,dst=/workspace/tools,readonly" \
  --mount "type=bind,src=$project_dir/workspace/app,dst=/workspace/app,readonly" \
  --mount "type=bind,src=$project_dir/workspace/prototypes,dst=/workspace/prototypes,readonly" \
  --mount "type=bind,src=$original_dir,dst=/orig,readonly" \
  -e DISPLAY=:99 -e LIBGL_ALWAYS_SOFTWARE=1 -e GOMAXPROCS=2 -e PYTHONDONTWRITEBYTECODE=1 \
  -e "TAIPEI_CIVIC_MODE=$mode" -e "TAIPEI_CITY_MENU_RUN=${TAIPEI_CITY_MENU_RUN:-gui-civic-r1}" \
  sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3 bash -c '
    set -euo pipefail
    test "$(stat -c %u:%g /workspace/runs)" = "1000:1000"
    Xvfb :99 -screen 0 1280x900x24 -nolisten tcp > /workspace/runs/civic-xvfb.log 2>&1 &
    xvfb_pid=$!
    trap '\''kill "$xvfb_pid" 2>/dev/null || true; wait 2>/dev/null || true'\'' EXIT
    for i in {1..50}; do test -S /tmp/.X11-unix/X99 && break; sleep .1; done
    if test "$TAIPEI_CIVIC_MODE" = source; then
      for kind in police fire; do
        TAIPEI_CITY_MENU_RUN="civic-$kind-native-r1" TAIPEI_CIVIC_CASE="$kind" python3 /workspace/tools/civic_facility_playtest.py
      done
    else
      python3 /workspace/tools/civic_facility_gui.py
    fi
    find /workspace/runs -user root -o -type d -name "*.md"
  '
