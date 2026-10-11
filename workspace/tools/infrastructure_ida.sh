#!/usr/bin/env bash
# #44：既有唯讀 IDA 資料庫的一次性副本，查窄範圍來源選取。
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
orig_dir="${TAIPEI_ORIG:-$project_dir/rs201 模擬台北/模擬台北/RS201}"
db_dir="$project_dir/workspace/runs/ida-19"
out_dir="$project_dir/workspace/runs/ida-44"
query="${1:-source-selection}"
case "$query" in
  source-selection) address=0x1619a ;;
  bitmap-drawing) address=0x16129 ;;
  *) exit 2 ;;
esac
test -f "$orig_dir/RS201.EXE"
test -f "$db_dir/event-keys.i64"
test -f "$project_dir/workspace/tools/ida_camera_probe.py"
test -d "$project_dir/workspace"
timeout 30s docker run --rm --network none --memory 256m --cpus 1 --pids-limit 32 \
  --user "$(id -u):$(id -g)" \
  --mount "type=bind,src=$project_dir/workspace,dst=/workspace" \
  sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3 bash -c '
    set -euo pipefail
    test -O /workspace/runs
    if test ! -e /workspace/runs/ida-44; then mkdir /workspace/runs/ida-44; fi
    test -d /workspace/runs/ida-44
    test -O /workspace/runs/ida-44
  '
test -d "$out_dir"
timeout 120s docker run --rm --network none --memory 2g --cpus 2 --pids-limit 128 \
  --user "$(id -u):$(id -g)" --name taipei-infrastructure-ida \
  --mount "type=bind,src=$orig_dir,dst=/orig,readonly" \
  --mount "type=bind,src=$db_dir,dst=/db,readonly" \
  --mount "type=bind,src=$out_dir,dst=/work" \
  --mount "type=bind,src=$project_dir/workspace/tools,dst=/tools,readonly" \
  -e "INFRA_QUERY=$query" -e "INFRA_ADDRESS=$address" \
  -w /work sha256:4ac62de83339c215bab10e455cee3a22d9c6efed9fd0d8ed0f068327b83a06ab bash -c '
    set -euo pipefail
    test -O /work
    test ! -e "$INFRA_QUERY.i64"
    test ! -e "$INFRA_QUERY.json"
    sha256sum /db/event-keys.i64 /orig/RS201.EXE > "$INFRA_QUERY-inputs.sha256"
    cp /tools/infrastructure_ida.sh "$INFRA_QUERY-wrapper.sh"
    cp /db/event-keys.i64 "$INFRA_QUERY.i64"
    /opt/ida-pro-9.4/idat -A -L"$INFRA_QUERY.log" -S"/tools/ida_camera_probe.py $INFRA_QUERY $INFRA_ADDRESS" "$INFRA_QUERY.i64" >"$INFRA_QUERY-console.log" 2>&1
    python3 -c '\''import json;from pathlib import Path
import os
s=json.loads(Path(os.environ["INFRA_QUERY"]+".json").read_text())
assert s["schema"]==1 and s["ida_version"]=="9.4"
assert s["input_sha256"]=="798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3"
assert len(s["functions"])==1 and s["functions"][0]["start"]==int(os.environ["INFRA_ADDRESS"],0)
print("verified",s["functions"][0]["original_name"],len(s["functions"][0]["instructions"]),"instructions")'\''
    find /work -user root -o -type d -name "*.md"
  '
