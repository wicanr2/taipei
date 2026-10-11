#!/usr/bin/env bash
# #40：只驗目前固定七補丁與實際呈現素材；正常 GUI 收據另由既有入口生成。
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
orig_dir="${TAIPEI_ORIG:-$project_dir/rs201 模擬台北/模擬台北/RS201}"
test -d "$orig_dir"
test -d "$project_dir/workspace/cache/dosgolem-probe-src"
test -d "$project_dir/workspace/runs/dos-clock-source"
timeout 240s docker run --rm --network none --memory 3g --cpus 2 --pids-limit 128 \
  --user "$(id -u):$(id -g)" \
  --mount "type=bind,src=$project_dir/workspace,dst=/workspace" \
  --mount "type=bind,src=$orig_dir,dst=/orig,readonly" \
  -e GOCACHE=/workspace/cache/gui-go -e GOMODCACHE=/workspace/cache/gomod \
  -e GOTOOLCHAIN=local -e GOPROXY=off -e GOMAXPROCS=2 \
  -e TAIPEI_HD_RECEIPTS=/workspace/runs/gui-cold \
  -e TAIPEI_HD_MATERIALS=/workspace/prototypes/hd-style -e TAIPEI_HD_ORIGINAL=/orig \
  -e TAIPEI_TOOL_PANEL_RECEIPTS=/workspace/runs/tool-submenus-native \
  -e TAIPEI_PANEL_RECEIPTS=/workspace/runs/startup-menus \
  -e TAIPEI_CHROME_RECEIPTS=/workspace/runs/city-chrome-native \
  -e TAIPEI_RUNTIME_RECEIPTS=/workspace/runs/hd-runtime \
  -e TAIPEI_CITY_PANEL_RECEIPTS=/workspace/runs/city-menus-native \
  -e TAIPEI_FILE_DIALOG_CATALOG=/workspace/runs/file-dialog-source-ready/catalog.json \
  -w /workspace sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3 bash -c '
    set -euo pipefail
    out=/workspace/runs/dos-clock-source
    test "$(stat -c %u:%g "$out")" = "$(id -u):$(id -g)"
    exec 9>/workspace/cache/probe-build.lock
    flock -s 9
    cd /workspace/cache/dosgolem-probe-src
    test -f internal/dos/system_clock_test.go
    go test -mod=readonly -count=1 -p 1 -v ./internal/dos ./internal/state ./oracle ./cmd/probe > "$out/dos-go-tests.log" 2>&1
    go build -mod=readonly -p 1 -trimpath -o "$out/probe-system-clock" ./cmd/probe
    cd /workspace/app
    go test -mod=readonly -count=1 -p 1 -v ./internal/hd ./internal/keyboard ./internal/original > "$out/hd-go-tests.log" 2>&1
    if grep -q -- "--- SKIP" "$out/hd-go-tests.log"; then exit 1; fi
    { go version; sha256sum /workspace/tools/dosgolem-*.patch /workspace/runs/taipei-preview "$out/probe-system-clock" /workspace/cache/dosgolem-probe-src/internal/dos/dos.go /workspace/cache/dosgolem-probe-src/internal/dos/system_clock_test.go; } > "$out/verified-build.txt"
    find /workspace -user root -o -type d -name "*.md"
    tail -6 "$out/dos-go-tests.log"
    tail -6 "$out/hd-go-tests.log"
  '
