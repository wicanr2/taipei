#!/usr/bin/env python3
"""唯讀盤點使用者已解壓的原版；輸出只含 metadata，不複製素材。"""
import argparse
import hashlib
import json
import platform
import struct
from pathlib import Path


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def inventory(source, archive):
    source = source.resolve(strict=True)
    if not source.is_dir() or not archive.is_file():
        raise ValueError("需要解壓目錄及原始 RAR")
    records = []
    for path in sorted(source.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"來源含符號連結：{path}")
        if not path.is_file():
            continue
        record = {"path": path.relative_to(source).as_posix(),
                  "bytes": path.stat().st_size, "sha256": sha256(path)}
        if path.name.lower() in ("rs201.exe", "rs201a.exe"):
            raw = path.read_bytes()
            if raw[:2] != b"MZ" or len(raw) < 28:
                raise ValueError("原版啟動檔不是有效 MZ")
            words = struct.unpack_from("<14H", raw)
            record["mz"] = {"header_bytes": words[4] * 16,
                            "relocations": words[3],
                            "entry_cs_ip": f"{words[11]:04X}:{words[10]:04X}",
                            "initial_ss_sp": f"{words[7]:04X}:{words[8]:04X}",
                            "address_space": "MZ header relative segments, not runtime or IDA addresses"}
            runtime = b"MS Run-Time Library - Copyright (c) 1990, Microsoft Corp"
            record["runtime_signature"] = {"found": runtime in raw,
                "file_offset": raw.find(runtime), "compiler_version": "unknown"}
        records.append(record)
    return {"schema": 1, "python": platform.python_version(),
            "source": str(source), "archive": {"name": archive.name,
            "bytes": archive.stat().st_size, "sha256": sha256(archive)},
            "files": records, "file_count": len(records),
            "total_bytes": sum(r["bytes"] for r in records)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = inventory(args.source, args.archive)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"{result['file_count']} files, {result['total_bytes']} bytes")
    print("archive sha256:", result["archive"]["sha256"])
    for record in result["files"]:
        if "mz" in record:
            print(record["path"], record["sha256"], record["mz"])


if __name__ == "__main__":
    main()
