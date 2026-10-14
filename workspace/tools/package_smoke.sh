#!/usr/bin/env bash
# 040：只在既有隔離音訊／Wine image執行實際封包啟動器。
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
version="${1:?請指定完整版號}"
platform="${2:?請指定linux或windows}"
[[ "$version" =~ ^v\.[0-9]+\.[0-9]+\.[0-9]+-[0-9]{8}$ ]]
test "$#" = 2
case "$platform" in
  linux) target=linux-amd64; image=sha256:d831720f8dfa388af8ad175fa8adeae8f2814dd4637be1e3db6a43274b26f36c ;;
  windows) target=windows-amd64; image=sha256:c047a6a259a1fc9a90babf7c937310fa9df4b3465bf75f3fcaad1bc640099c2f ;;
  *) exit 2 ;;
esac
dist="$project_dir/dist-all/$version"
bundle="$dist/smoke/unpacked/封包 測試 $platform/Taipei-$version-$target"
test -d "$bundle"
test -d "$dist/smoke"
test -d "$project_dir/workspace/tools"
test ! -e "$dist/smoke/$platform"
timeout 240s docker run --rm --network none --memory 3g --cpus 2 --pids-limit 128 \
  --user "$(id -u):$(id -g)" --label project=taipei \
  --mount "type=bind,src=$bundle,dst=/bundle,readonly" \
  --mount "type=bind,src=$dist/smoke,dst=/smoke" \
  --mount "type=bind,src=$project_dir/workspace/tools,dst=/tools,readonly" \
  -e DISPLAY=:99 -e LIBGL_ALWAYS_SOFTWARE=1 -e GOMAXPROCS=2 -e "TAIPEI_SMOKE_PLATFORM=$platform" \
  --entrypoint bash "$image" -c '
    set -euo pipefail
    out="/smoke/$TAIPEI_SMOKE_PLATFORM"
    mkdir "$out"
    test "$(stat -c %u:%g "$out")" = "$(id -u):$(id -g)"
    Xvfb :99 -screen 0 1600x1000x24 -nolisten tcp > "$out/xvfb.log" 2>&1 &
    xvfb_pid=$!;pulse_pid=""
    trap '\''if test -n "$pulse_pid"; then kill "$pulse_pid" 2>/dev/null || true; fi; if test "$TAIPEI_SMOKE_PLATFORM" = windows; then wineserver -k 2>/dev/null || true; fi; kill "$xvfb_pid" 2>/dev/null || true; wait 2>/dev/null || true'\'' EXIT
    for i in {1..50}; do test -S /tmp/.X11-unix/X99 && break; sleep .1; done
    mkdir -p "$out/cache" "$out/xdg"
    chmod 700 "$out/xdg"
    export XDG_CACHE_HOME="$out/cache" XDG_RUNTIME_DIR="$out/xdg"
    if test "$TAIPEI_SMOKE_PLATFORM" = linux; then
      export PULSE_SERVER="unix:$out/xdg/pulse-native" PULSE_SINK=taipei_package ALSA_CONFIG_PATH="$out/alsa.conf"
      printf '\''pcm.!default { type pulse server "%s" }\nctl.!default { type pulse server "%s" }\n'\'' "$PULSE_SERVER" "$PULSE_SERVER" > "$ALSA_CONFIG_PATH"
      pulseaudio -n --daemonize=no --exit-idle-time=-1 -L "module-null-sink sink_name=taipei_package rate=48000 channels=2" -L "module-native-protocol-unix socket=$out/xdg/pulse-native auth-anonymous=1" > "$out/pulse.log" 2>&1 &
      pulse_pid=$!
      for i in {1..50}; do pactl info >/dev/null 2>&1 && break; sleep .1; done
      pactl info > "$out/device.txt"
    else
      export WINEPREFIX="$out/prefix" WINEDEBUG=-all WINEDLLOVERRIDES="mscoree,mshtml="
      wineboot -u > "$out/wineboot.log" 2>&1
    fi
    python3 /tools/package_smoke.py --platform "$TAIPEI_SMOKE_PLATFORM" --out "$out"
  '
