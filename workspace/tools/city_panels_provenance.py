"""#37：彙整本批實際輸入、程式、工具、收據與交付限制，不含原版素材。"""
import hashlib
import json
import os
import struct
import subprocess
import zipfile
from pathlib import Path

ROOT = Path('/workspace')
RUNS = ROOT/'runs'
PROJECT = Path('/project')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert RUNS.stat().st_uid == os.getuid()
    inventory = json.loads((RUNS/'inventory.json').read_text())
    original = PROJECT/'rs201 模擬台北'
    for item in inventory['files']:
        path = original/item['path']
        assert path.stat().st_size == item['bytes'] and sha(path) == item['sha256'], path
    archive = PROJECT/inventory['archive']['name']
    assert sha(archive) == inventory['archive']['sha256']
    programs = {}
    for name, platform, machine in [('taipei-preview', 'Linux amd64 ELF', 62),
            ('taipei-preview-windows-amd64.exe', 'Windows amd64 PE', 0x8664),
            ('taipei-preview-macos-amd64', 'macOS amd64 Mach-O', 0x1000007),
            ('taipei-preview-macos-arm64', 'macOS arm64 Mach-O', 0x100000c)]:
        path = RUNS/name
        raw = path.read_bytes()
        if platform.startswith('Linux'):
            assert raw[:6] == b'\x7fELF\x02\x01' and struct.unpack_from('<H', raw, 18)[0] == machine
        elif platform.startswith('Windows'):
            offset = struct.unpack_from('<I', raw, 0x3c)[0]
            assert raw[:2] == b'MZ' and raw[offset:offset+4] == b'PE\0\0'
            assert struct.unpack_from('<H', raw, offset+4)[0] == machine
        else:
            assert raw[:4] == b'\xcf\xfa\xed\xfe' and struct.unpack_from('<I', raw, 4)[0] == machine
        assert (path.stat().st_uid, path.stat().st_gid) == (os.getuid(), os.getgid())
        programs[name] = {'sha256': sha(path), 'architecture': platform}
    receipt = RUNS/'city-menus-hd/f6/escape-capture.zip'
    with zipfile.ZipFile(receipt) as z:
        status = json.loads(z.read('status.json'))
    state = json.loads((RUNS/'city-panels-state-audit.json').read_text())
    assert state['state_equal'] and state['same_input'] and len(state['city_panel_states']) == 29
    assert state['steps'] == status['steps'] and state['render_interval_steps'] == 24_000_000
    assert state['observed_render_frames'] == status['steps']//24_000_000
    controls = json.loads((RUNS/'city-menus-hd/controls-verification.json').read_text())
    visual = json.loads((RUNS/'city-menus-hd/city-panels-verification.json').read_text())
    assert len(controls['acknowledged_actions']) == 82 and len(visual['states']) == 29
    negatives = [json.loads((RUNS/f'city-panels-negative/f{key}/result.json').read_text()) for key in [1,5]]
    assert all(len(cases) == 7 and all(c['source_checker_rejected'] and c['pixel_checker_rejected'] for c in cases) for cases in negatives)
    gui = json.loads((RUNS/'gui-cold/result.json').read_text())
    assert gui['cold_start'] and not gui['checkpoint'] and gui['native_exit'] and gui['reload_read']
    assert gui['construction']['cold_loaded_same']
    assert sha(Path(gui['save_dir'])/'ROUND4.SAV') == gui['save_sha256'] == '8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad'
    for name in ['quit-native-exit', 'reload/reload-quit-native-exit']:
        with zipfile.ZipFile(RUNS/'gui-cold'/(name+'-capture.zip')) as z:
            assert json.loads(z.read('status.json'))['dos_exited'], name
    for name in ['uncover-power', 'reload/load-accept']:
        with zipfile.ZipFile(RUNS/'gui-cold'/(name+'-capture.zip')) as z:
            assert json.loads(z.read('status.json'))['hd']['footer_text'][-1].strip() == '79980', name
    receipts = {str(p.relative_to(ROOT)): sha(p) for folder in ['city-menus-hd','gui-cold'] for p in sorted((RUNS/folder).rglob('*-capture.zip'))}
    source_files = {str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT/'app').rglob('*.go'))}
    source_files.update({str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT/'tools').glob('*')) if p.is_file() and p.suffix in ['.py','.sh','.patch']})
    art = ROOT/'prototypes/hd-style'
    references = {str(p.relative_to(art)): sha(p) for p in sorted(art.rglob('*')) if p.is_file() and (p.name in ['manifest.json','LICENSE','NotoSansCJKtc-Regular.otf'] or p.suffix == '.png')}
    result = {'schema': 1, 'container_image': 'sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3',
        'go_version': subprocess.check_output(['go','version'], text=True).strip(),
        'dosgolem_commit': 'a9714ebdab2ad6b529f81225472680f2b11f2842',
        'controlled_condition': 'same dosgolem.New initial state, same unique normal hardware input and virtual time; original RNG unchanged; no cross-RNG parity claim',
        'receipt': str(receipt.relative_to(ROOT)), 'receipt_sha256': sha(receipt),
        'steps_each_side': status['steps'], 'render_interval_steps': 24_000_000,
        'outer_timeout_seconds': 900, 'state_sha256': state['state_sha256'],
        'observed_render_frames': state['observed_render_frames'],
        'phase_elapsed_seconds': state['phase_elapsed_seconds'],
        'command': 'bash workspace/tools/city_panels_verify.sh',
        'original_files': len(inventory['files']), 'original_bytes': sum(i['bytes'] for i in inventory['files']),
        'input_inventory_sha256': sha(RUNS/'inventory.json'),
        'original': {name: sha(original/'模擬台北/RS201'/name) for name in ['RS201.EXE','RS201.ROM','RS201A.ROM']},
        'rar_unchanged': True, 'programs': programs,
        'audit_binary_sha256': sha(RUNS/'presentation-audit'),
        'pixel_checker_sha256': sha(RUNS/'receipt-check'),
        'source_files': source_files,
        'locks': {name: sha(ROOT/'app'/name) for name in ['go.mod','go.sum']},
        'material_references': references, 'normal_receipts': receipts,
        'normal_hd_bundles': visual['bundles'], 'negative_cases': 14,
        'gui_result': gui, 'normal_native_exits': 2, 'cold_loaded_funds': 79980,
        'scope': '六功能完整下拉面板二十九選取及明示抽樣；其餘視窗、圖片、場景、動畫、平台真機與正式封包未完成'}
    (RUNS/'city-panels-state-provenance.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ['steps_each_side','state_sha256','observed_render_frames','normal_hd_bundles','negative_cases','original_files','rar_unchanged']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
