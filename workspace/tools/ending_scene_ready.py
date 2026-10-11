"""#47／028 READY：只複製已審查完整底圖及固定來源契約。"""
import argparse
import json
import os
from pathlib import Path

from full_asset_catalog import sha


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--materials', type=Path, required=True)
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    assert not args.out.exists() and args.out.parent.stat().st_uid == os.getuid()
    source_raw = (args.source/'source-check.json').read_bytes()
    source = json.loads(source_raw)
    proof = json.loads((args.source/'prototype-check-v1.json').read_text())
    repro = json.loads((args.source/'reproducibility.json').read_text())
    assert repro['source_and_prototype_byte_equal'] and len(repro['files']) == 8
    for path, digest in repro['files'].items():
        assert sha(Path(path).read_bytes()) == digest
    root = args.materials/'ending-scene-v1'
    proto_raw = (root/'manifest.json').read_bytes()
    proto = json.loads(proto_raw)
    assert proto['stage'] == 'DRAFT' and proto['prototype']
    assert proof['manifest_sha256'] == sha(proto_raw) == 'a86c26d3d8731d0d59042d7f461e3cf9468c32f431e127ecae5e1d421d357e41'
    assert proto['source_check_sha256'] == sha(source_raw)
    assert proof['outside_ink_equal'] and proof['comparison_complete_equal']
    assert proof['source_aliases'] == len(source['sources']) == 2
    assert proof['normal_receipts'] == 4 and proof['complete_rgba_pixels'] == 1024000
    screen = (root/'presentation.png').read_bytes()
    assert sha(screen) == 'b37fddad8ea9cc3bbc505af3a3daad1f5cb59e86c213d98d12bbf279da81cfb0'
    assert proto['source_sha256'] == source['source_sha256'] == '0040b4374f37464862ae2f89da5bc897ddb7f53d539edd597cf8b2b6ff784ebd'
    assert proto['font_sha256'] == sha((args.materials/'fonts/NotoSansCJKtc-Regular.otf').read_bytes())
    license_sha = sha((args.materials/'fonts/LICENSE').read_bytes())
    assert license_sha == '6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2'
    manifest = {
        'schema': 1, 'issue': 47, 'stage': 'achievement-base', 'spec': '028-ending-achievement-base',
        'size': [1280, 800], 'source_size': [320, 200], 'mode': 19, 'blocked': True,
        'source_sha256': source['source_sha256'], 'source_check_sha256': sha(source_raw),
        'source_aliases': [{k: v for k, v in item.items() if k != 'encoding'} for item in source['sources']],
        'used_palette': source['used_palette'], 'prototype_manifest_sha256': sha(proto_raw),
        'art_sha256': proto['art_sha256'], 'font_sha256': proto['font_sha256'], 'license_sha256': license_sha,
        'title': proto['title'], 'font_size': proto['font_size'],
        'safe_rect': proto['safe_rect'], 'actual_ink_rect': proto['actual_ink_rect'],
        'images': {'screen.png': {'sha256': sha(screen), 'size': [1280, 800],
                                  'rgba_sha256': proof['presentation_rgba_sha256']}},
        'rights': '原版衍生素材僅留本機；字型 SIL OFL 1.1；本批未授權公開發布',
        'scope': '只處理已見完整靜態底圖；其他政績、圖案及文字變化與動畫維持原版',
    }
    args.out.mkdir()
    (args.out/'screen.png').write_bytes(screen)
    raw = (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True)+'\n').encode()
    (args.out/'manifest.json').write_bytes(raw)
    print(json.dumps({'manifest_sha256': sha(raw), 'screen_sha256': sha(screen)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
