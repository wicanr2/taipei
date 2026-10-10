#!/usr/bin/env bash
# #16：使用本機研究輸入重生離線原型及負對照，不下載或散布素材。
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
orig_dir="${TAIPEI_ORIG:-$project_dir/rs201 模擬台北/模擬台北/RS201}"
test -d "$orig_dir"
test -f "$orig_dir/RS201.ROM"
for rel in workspace/app workspace/cache workspace/runs workspace/prototypes/hd-style workspace/tools; do
  test -d "$project_dir/$rel"
done
timeout 90s docker run --rm --network none --memory 1g --cpus 2 --pids-limit 128 \
  --user "$(id -u):$(id -g)" \
  --mount "type=bind,src=$project_dir/workspace/app,dst=/workspace/app,readonly" \
  --mount "type=bind,src=$project_dir/workspace/cache,dst=/workspace/cache" \
  --mount "type=bind,src=$project_dir/workspace/runs,dst=/workspace/runs,readonly" \
  --mount "type=bind,src=$project_dir/workspace/tools,dst=/workspace/tools,readonly" \
  --mount "type=bind,src=$project_dir/workspace/prototypes/hd-style,dst=/materials" \
  --mount "type=bind,src=$orig_dir,dst=/orig,readonly" \
  -e GOCACHE=/workspace/cache/go -e GOMODCACHE=/workspace/cache/gomod -e GOTOOLCHAIN=local -e GOMAXPROCS=2 \
  -w /workspace/app \
  sha256:1a6d4452c65dea36aac2e2d606b01b4a029ec90cc1ae53890540ce6173ea77ac bash -c '
    set -euo pipefail
    go build -mod=readonly -o /materials/hd-prototype ./cmd/hd-prototype
    python3 /workspace/tools/hd_prototype_check.py
  '
