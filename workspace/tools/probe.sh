#!/usr/bin/env bash
# 主機只管理 Docker；建置與原版探針都在容器內。
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
orig_dir="${TAIPEI_ORIG:-$project_dir/rs201 模擬台北/模擬台北/RS201}"
dg_dir="$project_dir/workspace/dosgolem"
image_id=sha256:1a6d4452c65dea36aac2e2d606b01b4a029ec90cc1ae53890540ce6173ea77ac
base_commit=a9714ebdab2ad6b529f81225472680f2b11f2842
test -f "$orig_dir/RS201.EXE"
test -d "$dg_dir/.git"
test -d "$project_dir/workspace/tools"
mkdir -p "$project_dir/workspace/cache" "$project_dir/workspace/runs"
test -O "$project_dir/workspace/cache"
test -O "$project_dir/workspace/runs"
docker image inspect "$image_id" >/dev/null
timeout 180s docker run --rm --network none --memory 3g --cpus 2 --pids-limit 128 \
  --user "$(id -u):$(id -g)" \
  --mount "type=bind,src=$dg_dir,dst=/dg,readonly" \
  --mount "type=bind,src=$project_dir/workspace/tools,dst=/tools,readonly" \
  --mount "type=bind,src=$project_dir/workspace/cache,dst=/cache" \
  --mount "type=bind,src=$project_dir/workspace/runs,dst=/out" \
  --mount "type=bind,src=$orig_dir,dst=/orig,readonly" \
  -e GOCACHE=/cache/go -e GOMODCACHE=/cache/gomod -e GOTOOLCHAIN=local -e GOMAXPROCS=2 \
  --entrypoint bash "$image_id" -c '
    set -euo pipefail
    base_commit="$1"; shift
    exec 9>/cache/probe-build.lock
    flock 9
    stage=/cache/dosgolem-probe-src
    rm -rf "$stage"
    mkdir -p "$stage"
    git -C /dg archive "$base_commit" | tar -x -C "$stage"
    cd "$stage"
    for patch in /tools/dosgolem-bios-irq1.patch /tools/dosgolem-bios-blocking.patch /tools/dosgolem-console-keyboard.patch /tools/dosgolem-probe-trace.patch /tools/dosgolem-bios-caps-lock.patch /tools/dosgolem-audio.patch /tools/dosgolem-system-clock.patch; do
      git apply --check "$patch"
      git apply "$patch"
    done
    printf "%s  /orig/RS201.EXE\n" 798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3 | sha256sum -c -
    go build -p 1 -trimpath -o /out/probe-fixed ./cmd/probe
    { printf "dosgolem_base=%s\n" "$base_commit"; go version; sha256sum /tools/*.patch /out/probe-fixed; } > /out/probe-provenance.txt
    flock -u 9
    exec /out/probe-fixed -exe /orig/RS201.EXE -root /orig -args "/A /D /x" -blocking-bios-keys "$@"
  ' -- "$base_commit" "$@"
