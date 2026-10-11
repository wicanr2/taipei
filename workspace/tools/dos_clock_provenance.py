"""#40：彙整新時鐘產品的正常玩家證據、測試與固定輸入。"""
import hashlib
import json
import os
import re
import struct
import zipfile
from pathlib import Path

ROOT = Path('/workspace')
RUNS = ROOT/'runs'
OUT = RUNS/'dos-clock-source'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_status(path):
    with zipfile.ZipFile(path) as z:
        s, pixels = json.loads(z.read('status.json')), z.read('frame-index.bin')
    assert hashlib.sha256(pixels).hexdigest() == s['frame_index_sha256']
    return s


def main():
    assert OUT.stat().st_uid == os.getuid()
    inventory = json.loads((RUNS/'inventory.json').read_text())
    for item in inventory['files']:
        path = Path('/project/rs201 模擬台北')/item['path']
        assert path.stat().st_size == item['bytes'] and sha(path) == item['sha256'], path
    assert sha(Path('/project')/inventory['archive']['name']) == inventory['archive']['sha256']
    patch = ROOT/'tools/dosgolem-system-clock.patch'
    assert sha(patch) == '2a2f84aaed238fa0a82dea8585e1ce2e1157643241b41666a18e8bbc93bccc42'
    programs = {}
    for name, kind, machine in [('taipei-preview', 'Linux amd64 ELF', 62),
        ('taipei-preview-windows-amd64.exe', 'Windows amd64 PE', 0x8664),
        ('taipei-preview-macos-amd64', 'macOS amd64 Mach-O', 0x1000007),
        ('taipei-preview-macos-arm64', 'macOS arm64 Mach-O', 0x100000c)]:
        path = RUNS/name
        data = path.read_bytes()
        if kind.startswith('Linux'):
            assert data[:6] == b'\x7fELF\x02\x01' and struct.unpack_from('<H', data, 18)[0] == machine
        elif kind.startswith('Windows'):
            off = struct.unpack_from('<I', data, 0x3c)[0]
            assert data[:2] == b'MZ' and data[off:off+4] == b'PE\0\0' and struct.unpack_from('<H', data, off+4)[0] == machine
        else:
            assert data[:4] == b'\xcf\xfa\xed\xfe' and struct.unpack_from('<I', data, 4)[0] == machine
        assert (path.stat().st_uid, path.stat().st_gid) == (os.getuid(), os.getgid())
        assert sha(path) != sha(OUT/'before-build'/name)
        programs[name] = {'architecture': kind, 'sha256': sha(path)}
    tests = {}
    for name in ['dos-go-tests.log', 'hd-go-tests.log']:
        log = (OUT/name).read_text()
        assert '\nPASS\n' in log and '--- FAIL' not in log
        skipped = re.findall(r'^--- SKIP: (.+)$', log, re.M)
        tests[name] = {'passed': len(re.findall(r'^--- PASS:', log, re.M)), 'skipped': skipped, 'sha256': sha(OUT/name)}
        if name == 'hd-go-tests.log':
            assert not skipped
        else:
            for case in ['UsesBIOSTicks', 'Int1ASetAndTimeRegisters', 'InitialOffsetAndDayRemainder', 'MachineAndDOSState']:
                assert '--- PASS: TestDOSSystemClock'+case in log
    budget_root = RUNS/'budget-native-fixed'
    budget = json.loads((budget_root/'result.json').read_text())
    assert budget['normal_gui'] and not budget['checkpoint'] and budget['space_kept_window']
    records = {r['label']: r for r in budget['records']}
    assert [records[f'down-{i}']['budget']['selected_rows'] for i in range(1, 7)] == [[1], [2], [3], [4], [0], [1]]
    assert [records[f'up-{i}']['budget']['selected_rows'] for i in range(1, 7)] == [[0], [4], [3], [2], [1], [0]]
    initial = budget['initial']['percent']
    for row in range(5):
        right = records[f'row-{row}-right']['budget']['percent']
        left = records[f'row-{row}-left']['budget']['percent']
        assert right[row] == initial[row]-1 and left == initial
        assert all(right[i] == initial[i] for i in range(5) if i != row)
    assert records['escape']['budget'] is None and not records['escape']['dos_blocked']
    assert budget['pause_frame_sha256'] == budget['after_escape_frame_sha256']
    assert budget['reopened']['percent'] == initial
    first = load_status(budget_root/'first-open-capture.zip')
    final = load_status(budget_root/'idle-return-capture.zip')
    last_key = load_status(budget_root/'space-capture.zip')
    assert first['pit_divisor'] == 2982 and first['bios_ticks'] < first['ticks']
    assert budget['idle_return'] and budget['idle_return']['after_bios_ticks'] > budget['idle_return']['before_bios_ticks']
    assert final['key_reads'] == last_key['key_reads'] and final['frame_index_sha256'] == budget['pause_frame_sha256']
    catalog_path = RUNS/'budget-source/full-model/catalog.json'
    catalog = json.loads(catalog_path.read_text())
    assert len(catalog['samples']) == 33 and len(catalog['negative_controls']) == 132
    assert {tuple(s['source']['selected_rows']) for s in catalog['samples']} == {(i,) for i in range(5)}
    gui_root = RUNS/'gui-dos-clock-cold'
    gui = json.loads((gui_root/'result.json').read_text())
    assert gui['cold_start'] and not gui['checkpoint'] and gui['native_exit'] and gui['reload_read']
    assert gui['construction']['cold_loaded_same']
    assert gui['construction']['money_before_exit'] == gui['construction']['money_after_reload'] == '   79980'
    assert sha(Path(gui['save_dir'])/'ROUND4.SAV') == gui['save_sha256']
    for name in ['quit-native-exit', 'reload/reload-quit-native-exit']:
        assert load_status(gui_root/(name+'-capture.zip'))['dos_exited']
    gui_receipts = sorted(gui_root.rglob('*-capture.zip'))
    assert len(gui_receipts) == 45
    assert 'same-frame bundles verified: 45' in (OUT/'gui-receipt-check.log').read_text()
    assert '全部正常收據來源、完整呈現與區外像素通過 45' in (OUT/'gui-pixel-check.log').read_text()
    for folder in [budget_root, gui_root]:
        recorded = (folder/'program-provenance.txt').read_text()
        assert programs['taipei-preview']['sha256'] in recorded
    receipts = {str(p.relative_to(ROOT)): sha(p) for folder in [budget_root, gui_root] for p in sorted(folder.rglob('*-capture.zip'))}
    sources = json.loads((OUT/'platform-sources.json').read_text())
    for s in sources:
        assert sha(OUT/'platform'/s['local_file']) == s['sha256']
    result = {'schema': 1, 'issue': 40, 'date': '2026-10-11',
        'dosgolem_base': 'a9714ebdab2ad6b529f81225472680f2b11f2842',
        'patches': {p.name: sha(p) for p in sorted((ROOT/'tools').glob('dosgolem-*.patch'))},
        'image': 'sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3',
        'programs': programs, 'tests': tests, 'platform_sources': sources,
        'source_files': {str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT/'app').rglob('*.go'))},
        'lockfiles': {name: sha(ROOT/'app'/name) for name in ['go.mod', 'go.sum']},
        'normal_receipts': receipts, 'normal_receipts_count': len(receipts), 'normal_native_exits': 2,
        'source_samples': 33, 'source_negative_controls': 132, 'catalog_sha256': sha(catalog_path),
        'normal_budget_first': {k: first[k] for k in ['steps', 'ticks', 'bios_ticks', 'pit_divisor', 'pit_hz']},
        'idle_return': budget['idle_return'], 'last_key_step': last_key['key_reads'][-1]['Step'],
        'save_sha256': gui['save_sha256'], 'save_dir': gui['save_dir'], 'original_files': len(inventory['files']),
        'original_archive_unchanged': True,
        'scope': '限 DOS 時間來源修正及正常抽樣；預算 HD、全部圖片／介面、平台真機與正式封包仍未完成'}
    (OUT/'provenance.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ['normal_receipts_count', 'normal_native_exits', 'source_samples', 'source_negative_controls', 'normal_budget_first', 'idle_return', 'save_sha256']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
