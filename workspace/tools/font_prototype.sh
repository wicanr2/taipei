#!/usr/bin/env bash
# #18：只重生字型比較，不接正式繪字路徑。
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
for rel in workspace/app workspace/cache workspace/tools workspace/prototypes/hd-style; do
  test -d "$project_dir/$rel"
done
font_dir="$project_dir/workspace/prototypes/hd-style/fonts"
mkdir -p "$font_dir"
test -O "$font_dir"
if test "${1:-}" = --download; then
  shift
  timeout 180s docker run --rm --network bridge --memory 512m --cpus 1 --pids-limit 64 \
    --user "$(id -u):$(id -g)" \
    --mount "type=bind,src=$font_dir,dst=/fonts" \
    --mount "type=bind,src=$project_dir/workspace/tools,dst=/tools,readonly" \
    python:3.13-slim python /tools/font_source.py
fi
test "$#" = 0
test -f "$font_dir/NotoSansCJKtc-Regular.otf"
test -f "$font_dir/LICENSE"
test -f "$project_dir/workspace/prototypes/hd-style/composed-v1/hd-b-1280x800.png"
timeout 60s docker run --rm --network none --memory 1g --cpus 2 --pids-limit 128 \
  --user "$(id -u):$(id -g)" \
  --mount "type=bind,src=$project_dir/workspace/app,dst=/workspace/app,readonly" \
  --mount "type=bind,src=$project_dir/workspace/cache,dst=/workspace/cache" \
  --mount "type=bind,src=$project_dir/workspace/prototypes/hd-style,dst=/materials" \
  -e GOCACHE=/workspace/cache/go -e GOMODCACHE=/workspace/cache/gomod -e GOTOOLCHAIN=local -e GOMAXPROCS=2 \
  -w /workspace/app \
  sha256:1a6d4452c65dea36aac2e2d606b01b4a029ec90cc1ae53890540ce6173ea77ac bash -c '
    set -euo pipefail
    printf "%s  /materials/fonts/NotoSansCJKtc-Regular.otf\n" dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4 | sha256sum -c -
    printf "%s  /materials/fonts/LICENSE\n" 6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2 | sha256sum -c -
    go run -mod=readonly ./cmd/font-prototype -input /materials/composed-v1/hd-b-1280x800.png -font /materials/fonts/NotoSansCJKtc-Regular.otf -out /materials/font-comparison
  '
