#!/usr/bin/env bash
# #24：從既有唯讀 .i64 複本重生窄範圍地圖原點證據。
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
orig_dir="${TAIPEI_ORIG:-$project_dir/rs201 模擬台北/模擬台北/RS201}"
db_dir="$project_dir/workspace/runs/ida-19"
out_dir="$project_dir/workspace/runs/ida-24"
test -f "$orig_dir/RS201.EXE"
test -f "$db_dir/event-keys.i64"
test -f "$project_dir/workspace/tools/ida_camera_probe.py"
mkdir -p "$out_dir"
test -O "$out_dir"
timeout 120s docker run --rm --network none --memory 2g --cpus 2 --pids-limit 128 \
  --user "$(id -u):$(id -g)" \
  --mount "type=bind,src=$orig_dir,dst=/orig,readonly" \
  --mount "type=bind,src=$db_dir,dst=/db,readonly" \
  --mount "type=bind,src=$out_dir,dst=/work" \
  --mount "type=bind,src=$project_dir/workspace/tools,dst=/tools,readonly" \
  -w /work sha256:4ac62de83339c215bab10e455cee3a22d9c6efed9fd0d8ed0f068327b83a06ab bash -c '
    set -euo pipefail
    test -O /work
    cp /db/event-keys.i64 camera.i64
    /opt/ida-pro-9.4/idat -A -Lcamera.log -S"/tools/ida_camera_probe.py camera 0x1850a" camera.i64 >console.log 2>&1
    /opt/ida-pro-9.4/idat -A -Ldraw.log -S"/tools/ida_camera_probe.py draw 0x18594 0x28da6" camera.i64 >draw-console.log 2>&1
    python3 -c '\''import json;from pathlib import Path
for name in ["camera","draw"]:
    s=json.loads(Path(name+".json").read_text())
    assert s["schema"]==1 and s["ida_version"]=="9.4"
    assert s["input_sha256"]=="798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3"
    assert s["functions"] and s["mz_header_bytes"]==8192 and s["mz_relocation_count"]==2018
    for d in s["data"]:
        if d["ida_ea"] in [0x3456e,0x34570]:assert d["mz_relocation"] and d["raw_file_word"]==0x21c8
    print(name,"verified",len(s["functions"]),"functions")'\''
  '
