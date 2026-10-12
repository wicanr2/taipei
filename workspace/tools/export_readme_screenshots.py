#!/usr/bin/env python3
"""#53: export only the expressly requested README screenshots and provenance."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import zipfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--run', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
parser.add_argument('--source-commit', required=True)
args = parser.parse_args()
assert re.fullmatch(r'[0-9a-f]{40}', args.source_commit)
assert args.out.parent.is_dir() and args.out.parent.stat().st_uid == os.getuid()
assert not args.out.exists(), 'export to a fresh directory; review before replacing tracked images'


def sha(data):
    return hashlib.sha256(data).hexdigest()


receipt_bytes = (args.run / 'verification.json').read_bytes()
receipt = json.loads(receipt_bytes)
assert receipt['issue'] == 53 and receipt['normal_gui'] and receipt['native_exit_tested']
assert not any(receipt[k] for k in ['checkpoint', 'state_injection', 'long_state_sampling'])
assert sha(Path('/workspace/runs/taipei-preview').read_bytes()) == receipt['binary_sha256']
assert sha(Path('/workspace/app/locales/ui.tsv').read_bytes()) == receipt['catalog_sha256']
langs = ['zh-Hant', 'zh-Hans', 'ja', 'ko', 'en']
expected = {f'{scene}-{lang}.png' for scene in ['city', 'budget'] for lang in langs + ['original']}
expected.update(f'help-{lang}.png' for lang in langs)
assert len(receipt['screenshots']) == len(expected) == 17
assert {shot['file'] for shot in receipt['screenshots']} == expected
validated = []
pngs = {}
for shot in receipt['screenshots']:
    name = shot['file']
    raw = (args.run / 'gui' / (name[:-4] + '-capture.zip')).read_bytes()
    assert sha(raw) == shot['capture_sha256'], name
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        data = z.read('presentation.png')
        native_rgb = subprocess.run(['convert', 'png:-', '-depth', '8', 'rgb:-'], input=z.read('frame.png'),
                                    check=True, stdout=subprocess.PIPE).stdout
        assert sha(native_rgb) == shot['original_rgb_sha256']
        s = json.loads(z.read('status.json'))
        assert sha(z.read('frame-index.bin')) == shot['frame_index_sha256'] == s['frame_index_sha256']
        assert s['hd_enabled'] == (shot['mode'] == 'hd-b')
        assert s['help_panel'] == (shot['scene'] == 'help') and not s['language_panel']
        if s['hd_enabled']:
            assert s['language'] == shot['language'] and not s['language_warning']
        else:
            original = subprocess.run(['convert', 'png:-', '-filter', 'point', '-resize', '1280x800!',
                                       '-depth', '8', 'rgba:-'], input=z.read('frame.png'),
                                      check=True, stdout=subprocess.PIPE).stdout
            shown = subprocess.run(['convert', 'png:-', '-depth', '8', 'rgba:-'], input=data,
                                   check=True, stdout=subprocess.PIPE).stdout
            assert shown == original
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    assert struct.unpack('>II', data[16:24]) == (1280, 800)
    assert sha(data) == shot['png_sha256']
    assert data == (args.run / 'gui' / name).read_bytes()
    pngs[name] = data
    small = {k: v for k, v in shot.items() if k != 'palette'}
    small['palette_sha256'] = sha(bytes(v for rgb in shot['palette'] for v in rgb))
    validated.append(small)
for scene in ['city', 'budget']:
    group = [s for s in validated if s['scene'] == scene]
    assert len({(s['frame_index_sha256'], s['original_rgb_sha256']) for s in group}) == 1

inputs = {name: sha((Path('/orig') / name).read_bytes())
          for name in ['RS201.EXE', 'RS201.ROM', 'RS201A.ROM']}
manifest = {
    'issue': 'https://github.com/wicanr2/taipei/issues/53',
    'use': '依使用者指示，僅於私人儲存庫展示文件截圖；不納入 RRSAL-1.0。',
    'platform': 'Linux amd64，Xvfb 中的實際 GUI', 'captured_at': receipt['captured_at'],
    'source_commit': args.source_commit,
    'binary_sha256': receipt['binary_sha256'], 'catalog_sha256': receipt['catalog_sha256'],
    'original_inputs_sha256': inputs,
    'font_sha256': sha(Path('/workspace/prototypes/hd-style/fonts/NotoSansCJKtc-Regular.otf').read_bytes()),
    'docker_image': 'sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3',
    'dosgolem_base_commit': 'a9714ebdab2ad6b529f81225472680f2b11f2842',
    'dosgolem_patches': '由 workspace/tools/build_preview.sh 套用的七份專案補丁。',
    'patches_sha256': {p.name: sha(p.read_bytes()) for p in sorted(Path('/workspace/tools').glob('dosgolem-*.patch'))},
    'reproduction_tools_sha256': {name: sha((Path('/workspace/tools') / name).read_bytes())
                             for name in ['readme_screenshots.sh', 'readme_screenshots.py']},
    'scenario': '正常新遊戲、第一個城市、預設難度、原版 0 鍵暫停。',
    'rng_seed': '未覆寫；在同一個原版執行個體內切換呈現，不比較亂數規則。',
    'normal_gui': True, 'state_injection': False, 'native_exit_tested': True,
    'comparison': '城市與預算各組的原版色號畫面及可見 RGB 一致；完整色盤的未使用項目可能變化。CPU 步數與時鐘仍前進，此為呈現比較，不能當成相同機器狀態對拍。',
    'limits': ['全部截圖來自 Linux，未做 Windows 或 macOS 真機驗收。',
               '全部圖片 HD 重繪與正式封包尚未完成。',
               '展示範圍限本次城市、預算及 Help 畫面。'],
    'local_receipt': 'workspace/runs/' + args.run.name + '/verification.json',
    'local_receipt_sha256': sha(receipt_bytes),
    'reproduce': 'bash workspace/tools/readme_screenshots.sh 於 Docker 擷取，之後在相同 image 執行 export_readme_screenshots.py --run /workspace/runs/<新擷取目錄> --out <新的輸出目錄> --source-commit <目前產品提交>；執行與掛載範例見 WORKLOG.md 的 #53 記錄。',
    'screenshots': validated,
}
args.out.mkdir(mode=0o755)
for name, data in pngs.items():
    (args.out / name).write_bytes(data)
(args.out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
assert all(p.stat().st_uid == os.getuid() for p in args.out.iterdir())
print(f'Exported {len(pngs)} authorized PNGs, {sum(map(len, pngs.values()))} bytes; all source hashes verified.')
