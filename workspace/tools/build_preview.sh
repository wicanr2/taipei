#!/usr/bin/env bash
# 原版 GUI 原型。正式交付另走 #9。
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
test -d "$project_dir/workspace/dosgolem/.git"
test -d "$project_dir/workspace/app"
test -d "$project_dir/workspace/tools"
mkdir -p "$project_dir/workspace/cache" "$project_dir/workspace/runs"
test -O "$project_dir/workspace/cache"
test -O "$project_dir/workspace/runs"
network=none
if test "${1:-}" = --download; then network=bridge; shift; fi
test "$#" = 0
timeout 180s docker run --rm --network "$network" --memory 3g --cpus 2 --pids-limit 128 \
  --user "$(id -u):$(id -g)" \
  --mount "type=bind,src=$project_dir/workspace/dosgolem,dst=/dg,readonly" \
  --mount "type=bind,src=$project_dir/workspace/app,dst=/workspace/app,readonly" \
  --mount "type=bind,src=$project_dir/workspace/tools,dst=/tools,readonly" \
  --mount "type=bind,src=$project_dir/workspace/cache,dst=/workspace/cache" \
  --mount "type=bind,src=$project_dir/workspace/runs,dst=/out" \
  -e GOCACHE=/workspace/cache/gui-go -e GOMODCACHE=/workspace/cache/gomod \
  -e GOTOOLCHAIN=local -e GOMAXPROCS=2 -w /workspace/app \
  sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3 bash -c '
    set -euo pipefail
    exec 9>/workspace/cache/probe-build.lock
    flock 9
    stage=/workspace/cache/dosgolem-probe-src
    rm -rf "$stage"
    mkdir -p "$stage"
    git -C /dg archive a9714ebdab2ad6b529f81225472680f2b11f2842 | tar -x -C "$stage"
    for patch in /tools/dosgolem-bios-irq1.patch /tools/dosgolem-bios-blocking.patch /tools/dosgolem-console-keyboard.patch /tools/dosgolem-probe-trace.patch /tools/dosgolem-bios-caps-lock.patch /tools/dosgolem-audio.patch; do
      git -C "$stage" apply --check "$patch"
      git -C "$stage" apply "$patch"
    done
    go mod download
    go mod verify
    go test -mod=readonly -p 1 ./internal/keyboard
    go build -mod=readonly -p 1 -trimpath -o /out/taipei-preview ./cmd/taipei-preview
    { go version; sha256sum go.mod go.sum /tools/*.patch /out/taipei-preview; } > /out/preview-provenance.txt
  '
