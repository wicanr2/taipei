#!/usr/bin/env bash
# 041 / #63：正式封包唯讀，正常 GUI 與實際音訊錄影。
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
version="${1:?完整版號}"
run_name="${2:?工作目錄名稱}"
[[ "$version" =~ ^v\.[0-9]+\.[0-9]+\.[0-9]+-[0-9]{8}$ ]]
[[ "$run_name" =~ ^promo-v\.[0-9]+\.[0-9]+\.[0-9]+-[0-9]{8}(-r[0-9]+)?$ ]]
test "$#" = 2
dist="$project_dir/dist-all/$version"
bundle="$dist/smoke/unpacked/封包 測試 linux/Taipei-$version-linux-amd64"
for d in "$bundle" "$dist" "$project_dir/workspace/runs" "$project_dir/workspace/tools"; do test -d "$d"; done
test -f "$project_dir/workspace/runs/inventory.json"
test ! -e "$project_dir/workspace/runs/$run_name"
cpu_args=()
if test -n "${TAIPEI_PROMO_CPUSET:-}"; then
  [[ "$TAIPEI_PROMO_CPUSET" =~ ^[0-9,-]+$ ]]
  cpu_args+=(--cpuset-cpus "$TAIPEI_PROMO_CPUSET")
fi
timeout 1200s docker run --rm --pull never --network none --memory 4g --cpus 4 --pids-limit 192 \
  "${cpu_args[@]}" \
  --user "$(id -u):$(id -g)" --label project=taipei --name "taipei-$run_name" \
  --mount "type=bind,src=$bundle,dst=/bundle,readonly" \
  --mount "type=bind,src=$dist,dst=/dist,readonly" \
  --mount "type=bind,src=$project_dir/workspace/runs,dst=/runs" \
  --mount "type=bind,src=$project_dir/workspace/tools,dst=/tools,readonly" \
  -e DISPLAY=:99 -e LIBGL_ALWAYS_SOFTWARE=1 -e GOMAXPROCS=2 -e LP_NUM_THREADS=2 \
  -e PYTHONDONTWRITEBYTECODE=1 -e "TAIPEI_PROMO_RUN=$run_name" \
  -e "TAIPEI_AUDIO_PROBE=${TAIPEI_AUDIO_PROBE:-}" \
  -e "TAIPEI_PROBE_BINARY=${TAIPEI_PROBE_BINARY:-}" \
  -e "TAIPEI_AUDIO_NO_PERIODIC=${TAIPEI_AUDIO_NO_PERIODIC:-}" \
  --entrypoint bash sha256:d831720f8dfa388af8ad175fa8adeae8f2814dd4637be1e3db6a43274b26f36c -c '
    set -euo pipefail
    test "$(stat -c %u:%g /runs)" = "$(id -u):$(id -g)"
    out="/runs/$TAIPEI_PROMO_RUN"; mkdir "$out"; mkdir "$out/xdg" "$out/cache"
    chmod 700 "$out/xdg"
    export XDG_RUNTIME_DIR="$out/xdg" XDG_CACHE_HOME="$out/cache"
    export PULSE_SERVER="unix:$out/xdg/pulse-native" PULSE_SINK=taipei_promo ALSA_CONFIG_PATH="$out/alsa.conf"
    printf '\''pcm.!default { type pulse server "%s" }\nctl.!default { type pulse server "%s" }\n'\'' "$PULSE_SERVER" "$PULSE_SERVER" > "$ALSA_CONFIG_PATH"
    Xvfb :99 -screen 0 1280x800x24 -nolisten tcp > "$out/xvfb.log" 2>&1 & xvfb_pid=$!
    pulse_pid=""
    trap '\''test -z "$pulse_pid" || kill "$pulse_pid" 2>/dev/null || true; kill "$xvfb_pid" 2>/dev/null || true; wait 2>/dev/null || true'\'' EXIT
    for i in {1..50}; do test -S /tmp/.X11-unix/X99 && break; sleep .1; done
    pulseaudio -n --daemonize=no --exit-idle-time=-1 -L "module-null-sink sink_name=taipei_promo rate=48000 channels=2" -L "module-native-protocol-unix socket=$out/xdg/pulse-native auth-anonymous=1" > "$out/pulse.log" 2>&1 & pulse_pid=$!
    for i in {1..50}; do pactl info >/dev/null 2>&1 && break; sleep .1; done
    pactl info > "$out/device.txt"
    probe_args=(); test -z "$TAIPEI_AUDIO_PROBE" || probe_args+=(--audio-probe)
    python3 /tools/promo_capture.py --out "$out" "${probe_args[@]}"
    find "$out" -user root -o -type d -name "*.md"
  '
