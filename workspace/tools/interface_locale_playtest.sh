#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
orig_dir="${TAIPEI_ORIG:-$project_dir/rs201 模擬台北/模擬台北/RS201}"
test -d "$orig_dir"
test -d "$project_dir/workspace"
test -f "$project_dir/workspace/runs/taipei-preview"
run_name="${TAIPEI_INTERFACE_RUN:-interface-locale-cold-r1}"
case "$run_name" in interface-locale-cold-r[1-9]|interface-locale-cold-r[1-9][0-9]) ;; *) exit 2 ;; esac
timeout 900s docker run --rm --network none --user "$(id -u):$(id -g)" \
  --memory 3g --cpus 2 --pids-limit 128 --label project=taipei --name "taipei-$run_name" \
  --mount "type=bind,src=$project_dir/workspace,dst=/workspace" \
  --mount "type=bind,src=$orig_dir,dst=/orig,readonly" \
  -e DISPLAY=:99 -e LIBGL_ALWAYS_SOFTWARE=1 -e GOMAXPROCS=2 -e "TAIPEI_INTERFACE_RUN=$run_name" \
  -e "TAIPEI_INTERFACE_BINARY=${TAIPEI_INTERFACE_BINARY:-/workspace/runs/taipei-preview}" \
  -e "TAIPEI_INTERFACE_QUICK=${TAIPEI_INTERFACE_QUICK:-0}" \
  -e "TAIPEI_INTERFACE_PHASE=${TAIPEI_INTERFACE_PHASE:-all}" \
  -e "TAIPEI_INTERFACE_SOURCE_ONLY=${TAIPEI_INTERFACE_SOURCE_ONLY:-}" \
  -e "TAIPEI_INTERFACE_OPENING=${TAIPEI_INTERFACE_OPENING:-0}" \
  -e "TAIPEI_INTERFACE_FALLBACK=${TAIPEI_INTERFACE_FALLBACK:-0}" \
  sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3 bash -c '
    set -euo pipefail
    test ! -e "/workspace/runs/$TAIPEI_INTERFACE_RUN"
    test "$(stat -c %u:%g /workspace/runs)" = "$(id -u):$(id -g)"
    Xvfb :99 -screen 0 1280x900x24 -nolisten tcp > /workspace/runs/interface-xvfb.log 2>&1 &
    xvfb_pid=$!
    trap '\''kill "$xvfb_pid" 2>/dev/null || true; wait 2>/dev/null || true'\'' EXIT
    for i in {1..50}; do test -S /tmp/.X11-unix/X99 && break; sleep .1; done
    if test "$TAIPEI_INTERFACE_FALLBACK" = 1; then
      python3 /workspace/tools/localization_fallback_playtest.py
    else
      python3 /workspace/tools/interface_locale_playtest.py
    fi
    find /workspace -user root -o -type d -name "*.md"
  '
