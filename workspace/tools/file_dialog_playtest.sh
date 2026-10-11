#!/usr/bin/env bash
# #38：固定 Docker 的正常檔案／確認視窗來源，不注入原版狀態。
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
orig_dir="${TAIPEI_ORIG:-$project_dir/rs201 模擬台北/模擬台北/RS201}"
test -d "$orig_dir"
test -d "$project_dir/workspace"
test -f "$project_dir/workspace/runs/taipei-preview"
run_name="${TAIPEI_FILE_DIALOG_RUN:-file-dialogs-native}"
case "$run_name" in file-dialogs-native|file-dialogs-native-extra|file-dialogs-native-list|file-dialogs-native-edges|file-dialogs-native-missing) ;; *) exit 2 ;; esac
timeout 900s docker run --rm --network none --memory 3g --cpus 2 --pids-limit 128 \
  --user "$(id -u):$(id -g)" --name taipei-file-dialogs-native \
  --mount "type=bind,src=$project_dir/workspace,dst=/workspace" \
  --mount "type=bind,src=$orig_dir,dst=/orig,readonly" \
  -e DISPLAY=:99 -e LIBGL_ALWAYS_SOFTWARE=1 -e GOMAXPROCS=2 \
  -e "TAIPEI_FILE_DIALOG_RUN=$run_name" -w /workspace \
  sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3 bash -c '
    set -euo pipefail
    run_dir="/workspace/runs/$TAIPEI_FILE_DIALOG_RUN"
    mkdir -p "$run_dir" /workspace/runs/xdg
    test "$(stat -c %u:%g "$run_dir")" = "$(id -u):$(id -g)"
    export XDG_RUNTIME_DIR=/workspace/runs/xdg
    Xvfb :99 -screen 0 1280x900x24 -nolisten tcp > "$run_dir/xvfb.log" 2>&1 &
    xvfb_pid=$!
    trap '\''kill "$xvfb_pid" 2>/dev/null || true; wait 2>/dev/null || true'\'' EXIT
    for i in {1..50}; do test -S /tmp/.X11-unix/X99 && break; sleep .1; done
    for file in file_dialog_playtest.py file_dialog_playtest.sh file_dialog_catalog.py city_menu_playtest.py; do
      test ! -e "$run_dir/$file"
      cp "/workspace/tools/$file" "$run_dir/$file"
    done
    { go version; python3 --version; sha256sum /workspace/runs/taipei-preview /workspace/tools/file_dialog_playtest.py /workspace/tools/file_dialog_playtest.sh /workspace/tools/file_dialog_catalog.py /workspace/tools/city_menu_playtest.py /orig/RS201.EXE /orig/RS201.ROM; } > "$run_dir/program-provenance.txt"
    python3 /workspace/tools/file_dialog_playtest.py > "$run_dir/playtest.log" 2>&1
    find "$run_dir" -user root -o -type d -name "*.md"
  '
