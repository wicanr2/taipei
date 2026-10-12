#!/usr/bin/env bash
# #4/#20：研究前端跨平台編譯，非正式封包或真機驗收。
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
test -d "$project_dir/workspace/cache/dosgolem-probe-src/audio/ymfm"
test -f "$project_dir/workspace/runs/preview-provenance.txt"
test -d "$project_dir/workspace/app"
target="${1:?請指定 windows 或 macos}"
case "$target" in
  windows) image=sha256:80cda80f47353188794d030f468c37821d8e77a3a078e5b306f12cb0a0953c7d ;;
  macos) image=sha256:d4c50a5cf3cf35164b83fb1531fe66f52b9224e826944363bf1bc4d7ba3c8d0c ;;
  *) exit 2 ;;
esac
timeout 300s docker run --rm --network none --memory 3g --cpus 2 --pids-limit 128 \
  --user "$(id -u):$(id -g)" \
  --mount "type=bind,src=$project_dir/workspace/app,dst=/workspace/app,readonly" \
  --mount "type=bind,src=$project_dir/workspace/cache,dst=/workspace/cache" \
  --mount "type=bind,src=$project_dir/workspace/runs,dst=/out" \
  -e GOCACHE="/workspace/cache/cross-$target" -e GOMODCACHE=/workspace/cache/gomod \
  -e GOTOOLCHAIN=local -e GOMAXPROCS=2 -e CGO_ENABLED=1 -e "TARGET=$target" \
  -w /workspace/app "$image" bash -c '
    set -euo pipefail
    exec 9>/workspace/cache/probe-build.lock
    flock -s 9
    test -O /out
    go mod verify
    mkdir -p /out/locales
    cp locales/ui.tsv /out/locales/ui.tsv
    if test "$TARGET" = windows; then
      export GOOS=windows GOARCH=amd64 CC=x86_64-w64-mingw32-gcc CXX=x86_64-w64-mingw32-g++
      go build -mod=readonly -p 1 -trimpath -o /out/taipei-preview-windows-amd64.exe ./cmd/taipei-preview
      x86_64-w64-mingw32-objdump -p /out/taipei-preview-windows-amd64.exe > /out/preview-windows-pe.txt
    else
      export GOOS=darwin MACOSX_DEPLOYMENT_TARGET=11.0
      for arch in amd64 arm64; do
        triple=x86_64; if test "$arch" = arm64; then triple=aarch64; fi
        export GOARCH="$arch" CC="$triple-apple-darwin24.5-clang" CXX="$triple-apple-darwin24.5-clang++"
        go build -mod=readonly -p 1 -trimpath -o "/out/taipei-preview-macos-$arch" ./cmd/taipei-preview
        x86_64-apple-darwin24.5-otool -L "/out/taipei-preview-macos-$arch" > "/out/preview-macos-$arch-dylibs.txt"
        x86_64-apple-darwin24.5-otool -hv -l "/out/taipei-preview-macos-$arch" > "/out/preview-macos-$arch-load-commands.txt"
      done
    fi
    { go version; go env GOOS GOARCH CC CXX; sha256sum go.mod go.sum locales/ui.tsv;
      if test "$TARGET" = windows; then sha256sum /out/taipei-preview-windows-amd64.exe;
      else sha256sum /out/taipei-preview-macos-amd64 /out/taipei-preview-macos-arm64; fi;
    } > "/out/preview-cross-$TARGET.txt"
  '
