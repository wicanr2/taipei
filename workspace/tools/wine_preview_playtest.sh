#!/usr/bin/env bash
# #9：Windows 研究 binary 的 Wine 冷啟動預檢，非正式封包或真機驗收。
set -euo pipefail
if test "${1:-}" != --inside; then
  project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
  orig_dir="${TAIPEI_ORIG:-$project_dir/rs201 模擬台北/模擬台北/RS201}"
  test -d "$orig_dir"
  test -f "$project_dir/workspace/runs/taipei-preview-windows-amd64.exe"
  timeout 240s docker run --rm --network none --memory 3g --cpus 2 --pids-limit 128 \
    --user "$(id -u):$(id -g)" --name taipei-wine-preview \
    --mount "type=bind,src=$project_dir/workspace,dst=/workspace" \
    --mount "type=bind,src=$orig_dir,dst=/orig,readonly" \
    -e DISPLAY=:99 -e LIBGL_ALWAYS_SOFTWARE=1 -e GOMAXPROCS=2 \
    --entrypoint bash sha256:c047a6a259a1fc9a90babf7c937310fa9df4b3465bf75f3fcaad1bc640099c2f \
    /workspace/tools/wine_preview_playtest.sh --inside
  exit
fi
out=/workspace/runs/wine-preview
mkdir -p "$out/home" "$out/saves"
test -O "$out"
export HOME="$out/home" WINEPREFIX="$out/prefix" WINEDEBUG=-all
rm -f "$out/stop" "$out/capture.zip" "$out/result.json"
Xvfb :99 -screen 0 1280x900x24 -nolisten tcp > "$out/xvfb.log" 2>&1 &
xvfb_pid=$!; game_pid=""
trap 'if test -n "$game_pid"; then kill "$game_pid" 2>/dev/null || true; fi; wineserver -k 2>/dev/null || true; kill "$xvfb_pid" 2>/dev/null || true; wait 2>/dev/null || true' EXIT
for _ in {1..50}; do test -S /tmp/.X11-unix/X99 && break; sleep .1; done
wine /workspace/runs/taipei-preview-windows-amd64.exe \
  -original 'Z:\orig' -saves 'Z:\workspace\runs\wine-preview\saves' \
  -receipts 'Z:\workspace\runs\wine-preview' -stop-file 'Z:\workspace\runs\wine-preview\stop' \
  -mute -steps-per-update 400000 > "$out/app.log" 2>&1 &
game_pid=$!
python3 /workspace/tools/wine_preview_playtest.py
wait "$game_pid"
game_pid=""
