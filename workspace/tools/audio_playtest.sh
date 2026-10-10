#!/usr/bin/env bash
# #17：冷啟動 GUI 經真實播放器輸出至隔離 PulseAudio，再擷取 monitor。
set -euo pipefail
if test "${1:-}" != --inside; then
  project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
  orig_dir="${TAIPEI_ORIG:-$project_dir/rs201 模擬台北/模擬台北/RS201}"
  test -d "$orig_dir"
  test -f "$project_dir/workspace/runs/taipei-preview"
  timeout 120s docker run --rm --network none --memory 3g --cpus 2 --pids-limit 128 \
    --user "$(id -u):$(id -g)" --name taipei-audio-device \
    --mount "type=bind,src=$project_dir/workspace,dst=/workspace" \
    --mount "type=bind,src=$orig_dir,dst=/orig,readonly" \
    -e DISPLAY=:99 -e LIBGL_ALWAYS_SOFTWARE=1 -e GOMAXPROCS=2 \
    --entrypoint bash sha256:d831720f8dfa388af8ad175fa8adeae8f2814dd4637be1e3db6a43274b26f36c \
    /workspace/tools/audio_playtest.sh --inside
  exit
fi
out=/workspace/runs/audio-device
mkdir -p "$out/xdg" "$out/saves"
test -O "$out"
chmod 700 "$out/xdg"
rm -f "$out/stop" "$out/status.json" "$out/capture.zip"
export XDG_RUNTIME_DIR="$out/xdg"
export PULSE_SERVER="unix:$out/xdg/pulse-native"
export PULSE_SINK=taipei_audio
export ALSA_CONFIG_PATH="$out/alsa.conf"
cat > "$ALSA_CONFIG_PATH" <<EOF
pcm.!default { type pulse server "$PULSE_SERVER" }
ctl.!default { type pulse server "$PULSE_SERVER" }
EOF
Xvfb :99 -screen 0 1280x900x24 -nolisten tcp > "$out/xvfb.log" 2>&1 &
xvfb_pid=$!
pulse_pid="";game_pid=""
trap 'if test -n "$game_pid"; then kill "$game_pid" 2>/dev/null || true; fi; if test -n "$pulse_pid"; then kill "$pulse_pid" 2>/dev/null || true; fi; kill "$xvfb_pid" 2>/dev/null || true; wait 2>/dev/null || true' EXIT
pulseaudio -n --daemonize=no --exit-idle-time=-1 \
  -L "module-null-sink sink_name=taipei_audio rate=48000 channels=2" \
  -L "module-native-protocol-unix socket=$out/xdg/pulse-native auth-anonymous=1" \
  > "$out/pulse.log" 2>&1 &
pulse_pid=$!
for _ in {1..50}; do if pactl info >/dev/null 2>&1 && test -S /tmp/.X11-unix/X99; then break; fi; sleep .1; done
pactl info > "$out/device.txt"
/workspace/runs/taipei-preview -original /orig -saves "$out/saves" \
  -receipts "$out" -stop-file "$out/stop" \
  > "$out/app.log" 2>&1 &
game_pid=$!
# 刻意延後焦點，覆蓋播放器尚未開始持續取樣的啟動條件。
sleep 3
kill -0 "$game_pid"
timeout 10s xdotool search --sync --onlyvisible --name '模擬台北' windowfocus
ffmpeg -nostdin -hide_banner -loglevel error -y -threads 1 -f pulse \
  -i taipei_audio.monitor -t 15 -ac 2 -ar 48000 "$out/playback.wav"
printf 'stop\n' > "$out/stop"
wait "$game_pid"
game_pid=""
python3 /workspace/tools/audio_playtest_check.py
