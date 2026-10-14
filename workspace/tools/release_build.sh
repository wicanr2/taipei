#!/usr/bin/env bash
# 040／#9：從不可變tag乾淨重建四架構；所有工作負載在既有Docker image。
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
version="${1:?請指定完整版號及同名tag}"
[[ "$version" =~ ^v\.[0-9]+\.[0-9]+\.[0-9]+-[0-9]{8}$ ]]
test "$#" = 1
git -C "$project_dir" rev-parse --verify "$version^{commit}" >/dev/null
test -d "$project_dir/workspace/cache"
test -d "$project_dir/workspace/runs"
test -d "$project_dir/workspace/dosgolem/.git"
test ! -e "$project_dir/workspace/runs/release-$version"
test ! -e "$project_dir/workspace/cache/release-source-$version"
timeout 240s docker run --rm --network none --memory 3g --cpus 2 --pids-limit 128 \
  --user "$(id -u):$(id -g)" --label project=taipei \
  --mount "type=bind,src=$project_dir,dst=/repo,readonly" \
  --mount "type=bind,src=$project_dir/workspace/cache,dst=/workspace/cache" \
  --mount "type=bind,src=$project_dir/workspace/runs,dst=/workspace/runs" \
  -e "TAIPEI_RELEASE_VERSION=$version" -e GOCACHE=/workspace/cache/gui-go \
  -e GOMODCACHE=/workspace/cache/gomod -e GOTOOLCHAIN=local -e GOMAXPROCS=2 \
  sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3 bash -c '
    set -euo pipefail
    test "$(stat -c %u:%g /workspace/cache)" = "$(id -u):$(id -g)"
    stage="/workspace/cache/release-source-$TAIPEI_RELEASE_VERSION"
    out="/workspace/runs/release-$TAIPEI_RELEASE_VERSION"
    mkdir -p "$stage" "$out"
    git -C /repo archive "$TAIPEI_RELEASE_VERSION" workspace/app workspace/tools LICENSE | tar -xf - -C "$stage"
    engine="$stage/workspace/cache/dosgolem-probe-src"
    mkdir -p "$engine"
    git -C /repo/workspace/dosgolem archive a9714ebdab2ad6b529f81225472680f2b11f2842 | tar -xf - -C "$engine"
    for name in bios-irq1 bios-blocking console-keyboard probe-trace bios-caps-lock audio system-clock; do
      patch="$stage/workspace/tools/dosgolem-$name.patch"
      git -C "$engine" apply --check "$patch"
      git -C "$engine" apply "$patch"
    done
    cd "$stage/workspace/app"
    go mod verify
    go build -mod=readonly -p 1 -trimpath -ldflags "-X main.version=$TAIPEI_RELEASE_VERSION" -o "$out/taipei-linux-amd64" ./cmd/taipei-preview
    go build -mod=readonly -p 1 -trimpath -o "$out/package-resources" ./cmd/package-resources
    git -C /repo rev-parse "$TAIPEI_RELEASE_VERSION^{commit}" > "$out/source-commit.txt"
    go version -m "$out/taipei-linux-amd64" > "$out/linux-go-build.txt"
    ldd "$out/taipei-linux-amd64" > "$out/linux-dependencies.txt"
    Xvfb :91 -screen 0 1280x900x24 -nolisten tcp > "$out/version-xvfb.log" 2>&1 &
    xvfb_pid=$!; trap '\''kill "$xvfb_pid" 2>/dev/null || true; wait 2>/dev/null || true'\'' EXIT
    for i in {1..50}; do test -S /tmp/.X11-unix/X91 && break; sleep .1; done
    DISPLAY=:91 "$out/taipei-linux-amd64" -version > "$out/version-linux.txt"
    test "$(cat "$out/version-linux.txt")" = "$TAIPEI_RELEASE_VERSION"
  '
test -d "$project_dir/workspace/cache/release-source-$version"
test -d "$project_dir/workspace/runs/release-$version"
for target in windows macos; do
  if test "$target" = windows; then
    image=sha256:80cda80f47353188794d030f468c37821d8e77a3a078e5b306f12cb0a0953c7d
  else
    image=sha256:d4c50a5cf3cf35164b83fb1531fe66f52b9224e826944363bf1bc4d7ba3c8d0c
  fi
  timeout 300s docker run --rm --network none --memory 3g --cpus 2 --pids-limit 128 \
    --user "$(id -u):$(id -g)" --label project=taipei \
    --mount "type=bind,src=$project_dir/workspace/cache/release-source-$version,dst=/release-src,readonly" \
    --mount "type=bind,src=$project_dir/workspace/cache,dst=/workspace/cache" \
    --mount "type=bind,src=$project_dir/workspace/runs/release-$version,dst=/out" \
    -e "TAIPEI_RELEASE_VERSION=$version" -e "TAIPEI_RELEASE_TARGET=$target" \
    -e "GOCACHE=/workspace/cache/cross-$target" -e GOMODCACHE=/workspace/cache/gomod \
    -e GOTOOLCHAIN=local -e GOMAXPROCS=2 -e CGO_ENABLED=1 -w /release-src/workspace/app \
    "$image" bash -c '
      set -euo pipefail
      go mod verify
      if test "$TAIPEI_RELEASE_TARGET" = windows; then
        export GOOS=windows GOARCH=amd64 CC=x86_64-w64-mingw32-gcc CXX=x86_64-w64-mingw32-g++
        go build -mod=readonly -p 1 -trimpath -ldflags "-X main.version=$TAIPEI_RELEASE_VERSION" -o /out/taipei-windows-amd64.exe ./cmd/taipei-preview
        x86_64-w64-mingw32-objdump -p /out/taipei-windows-amd64.exe > /out/windows-pe.txt
      else
        export GOOS=darwin MACOSX_DEPLOYMENT_TARGET=11.0
        for arch in amd64 arm64; do
          triple=x86_64; if test "$arch" = arm64; then triple=aarch64; fi
          export GOARCH="$arch" CC="$triple-apple-darwin24.5-clang" CXX="$triple-apple-darwin24.5-clang++"
          go build -mod=readonly -p 1 -trimpath -ldflags "-X main.version=$TAIPEI_RELEASE_VERSION" -o "/out/taipei-macos-$arch" ./cmd/taipei-preview
          x86_64-apple-darwin24.5-otool -L "/out/taipei-macos-$arch" > "/out/macos-$arch-dependencies.txt"
          x86_64-apple-darwin24.5-otool -hv -l "/out/taipei-macos-$arch" > "/out/macos-$arch-load-commands.txt"
        done
        x86_64-apple-darwin24.5-lipo -create /out/taipei-macos-amd64 /out/taipei-macos-arm64 -output /out/taipei-macos-universal
        x86_64-apple-darwin24.5-lipo -info /out/taipei-macos-universal > /out/macos-universal-architectures.txt
      fi
    '
done
