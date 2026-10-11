"""#38：只彙整實際通過結果、正常收據及固定輸入，不代替驗證。"""
import hashlib
import json
import os
import struct
import subprocess
import zipfile
from pathlib import Path

ROOT = Path('/workspace')
RUNS = ROOT/'runs'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert RUNS.stat().st_uid == os.getuid()
    inventory = json.loads((RUNS/'inventory.json').read_text())
    original = Path('/project/rs201 模擬台北')
    for item in inventory['files']:
        path = original/item['path']
        assert path.stat().st_size == item['bytes'] and sha(path) == item['sha256'],path
    assert sha(Path('/project')/inventory['archive']['name']) == inventory['archive']['sha256']
    programs = {}
    for name,platform,machine in [('taipei-preview','Linux amd64 ELF',62),
        ('taipei-preview-windows-amd64.exe','Windows amd64 PE',0x8664),
        ('taipei-preview-macos-amd64','macOS amd64 Mach-O',0x1000007),
        ('taipei-preview-macos-arm64','macOS arm64 Mach-O',0x100000c)]:
        path = RUNS/name
        raw = path.read_bytes()
        if platform.startswith('Linux'):
            assert raw[:6] == b'\x7fELF\x02\x01' and struct.unpack_from('<H',raw,18)[0] == machine
        elif platform.startswith('Windows'):
            off = struct.unpack_from('<I',raw,0x3c)[0]
            assert raw[:2] == b'MZ' and raw[off:off+4] == b'PE\0\0' and struct.unpack_from('<H',raw,off+4)[0] == machine
        else:assert raw[:4] == b'\xcf\xfa\xed\xfe' and struct.unpack_from('<I',raw,4)[0] == machine
        assert (path.stat().st_uid,path.stat().st_gid) == (os.getuid(),os.getgid())
        programs[name] = {'sha256':sha(path),'architecture':platform}
    gui_root = RUNS/'gui-file-dialogs-cold'
    gui = json.loads((gui_root/'result.json').read_text())
    assert gui['cold_start'] and not gui['checkpoint'] and gui['native_exit'] and gui['reload_read'] and gui['construction']['cold_loaded_same']
    assert gui['construction']['money_before_exit'] == gui['construction']['money_after_reload'] and gui['construction']['money_after_reload'].strip() == '79980'
    assert sha(Path(gui['save_dir'])/'ROUND4.SAV') == gui['save_sha256']
    for name in ['quit-native-exit','reload/reload-quit-native-exit']:
        with zipfile.ZipFile(gui_root/(name+'-capture.zip')) as z:assert json.loads(z.read('status.json'))['dos_exited']
    controls = json.loads((RUNS/'file-dialogs-hd/result.json').read_text())
    assert controls['normal_gui'] and not controls['checkpoint'] and controls['empty_save_no_write'] and controls['overwrite_without_extra_prompt'] and controls['other_nine_saves_unchanged']
    assert {r['family'] for r in controls['f12_roundtrips']} == {'file-browser','quit-confirm'}
    negative = json.loads((RUNS/'file-dialogs-negative/result.json').read_text())
    assert len(negative) == 22 and sum(r['positive'] for r in negative) == 4
    assert all(r['python_rejected'] and r['go_rejected'] for r in negative if not r['positive'])
    for name in ['file-dialog-go-tests.log','file-dialog-go-last.log']:
        log = (RUNS/name).read_text()
        assert '\nPASS\n' in log and '--- SKIP' not in log and 'FAIL' not in log
    receipt = gui_root/'quit-file-theme-hd-capture.zip'
    with zipfile.ZipFile(receipt) as z:status = json.loads(z.read('status.json'))
    state = json.loads((RUNS/'file-dialogs-state-audit.json').read_text())
    assert state['state_equal'] and state['same_input'] and state['normal_gui_frame_palette_reads_files_equal']
    assert state['steps'] == status['steps'] and state['render_interval_steps'] == 24_000_000
    assert state['observed_render_frames'] == status['steps']//24_000_000
    assert all(state['file_dialog_families'].get(f,0) > 0 for f in ['file-browser','quit-confirm'])
    assert state['state']['save_sha256']['ROUND4.SAV'] == gui['save_sha256']
    receipts = {str(p.relative_to(ROOT)):sha(p) for folder in ['file-dialogs-hd','gui-file-dialogs-cold'] for p in sorted((RUNS/folder).rglob('*-capture.zip'))}
    source_files = {str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'app').rglob('*.go'))}
    source_files.update({str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'tools').glob('*')) if p.is_file() and p.suffix in ['.py','.sh','.patch']})
    art = ROOT/'prototypes/hd-style'
    references = {str(p.relative_to(art)):sha(p) for p in sorted((art/'file-dialogs-v1').iterdir()) if p.is_file()}
    references.update({name:sha(art/name) for name in ['fonts/NotoSansCJKtc-Regular.otf','fonts/LICENSE','menu-blue-b-v1.png','city-chrome-v1/frame.png']})
    result = {'schema':1,'issue':38,'container_image':'sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3',
        'go_version':subprocess.check_output(['go','version'],text=True).strip(),
        'dosgolem_commit':'a9714ebdab2ad6b529f81225472680f2b11f2842','receipt':str(receipt.relative_to(ROOT)),
        'receipt_sha256':sha(receipt),'command':'bash workspace/tools/file_dialogs_verify.sh',
        'steps_each_side':state['steps'],'render_interval_steps':24_000_000,'observed_render_frames':state['observed_render_frames'],
        'file_dialog_families':state['file_dialog_families'],'state_sha256':state['state_sha256'],
        'phase_elapsed_seconds':state['phase_elapsed_seconds'],'normal_gui_replay_checked':True,'save_sha256':gui['save_sha256'],
        'controlled_condition':'same dosgolem.New state, independent empty writable scratch, unique normal GUI hardware inputs and virtual time; original RNG unchanged; no cross-RNG parity claim',
        'programs':programs,'tools':{name:sha(RUNS/name) for name in ['receipt-check','presentation-audit']},
        'source_files':source_files,'locks':{name:sha(ROOT/'app'/name) for name in ['go.mod','go.sum']},
        'material_references':references,'normal_receipts':receipts,'normal_bundles':len(receipts),
        'negative_cases':18,'positive_cases':4,'normal_native_exits':2,'cold_loaded_funds':79980,
        'original_files':len(inventory['files']),'rar_unchanged':True,'input_inventory_sha256':sha(RUNS/'inventory.json'),
        'scope':'限完整檔案視窗與離開提示及明示抽樣；其他視窗、圖表、圖片、動畫、平台真機及正式封包未完成'}
    (RUNS/'file-dialogs-state-provenance.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['steps_each_side','state_sha256','file_dialog_families','observed_render_frames','normal_bundles','negative_cases','original_files']},ensure_ascii=False))


if __name__ == '__main__':main()
