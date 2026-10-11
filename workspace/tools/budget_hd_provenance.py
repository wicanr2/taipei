"""#39：核對修正版正常操作、逐點原版狀態及本機交付前證據。"""
import json
import os
import re
import struct
from pathlib import Path

from dos_clock_provenance import load_status, sha

ROOT = Path('/workspace')
RUNS = ROOT/'runs'
OUT = RUNS/'budget-source'


def read(path):
    return json.loads(path.read_text())


def main():
    assert OUT.stat().st_uid == os.getuid()
    target = OUT/'hd-provenance-r4.json'
    assert not target.exists()
    inventory = read(RUNS/'inventory.json')
    for item in inventory['files']:
        path = Path('/project/rs201 模擬台北')/item['path']
        assert path.stat().st_size == item['bytes'] and sha(path) == item['sha256']
    assert sha(Path('/project')/inventory['archive']['name']) == inventory['archive']['sha256']
    patches = {p.name:sha(p) for p in sorted((ROOT/'tools').glob('dosgolem-*.patch'))}
    assert patches == read(RUNS/'dos-clock-source/provenance.json')['patches'] and len(patches) == 7
    programs = {}
    for name,machine in [('taipei-preview',62),('taipei-preview-windows-amd64.exe',0x8664),
        ('taipei-preview-macos-amd64',0x1000007),('taipei-preview-macos-arm64',0x100000c)]:
        path = RUNS/name
        raw = path.read_bytes()
        if name == 'taipei-preview':
            assert raw[:6] == b'\x7fELF\x02\x01' and struct.unpack_from('<H',raw,18)[0] == machine
        elif name.endswith('.exe'):
            offset = struct.unpack_from('<I',raw,0x3c)[0]
            assert raw[:2] == b'MZ' and raw[offset:offset+4] == b'PE\0\0' and struct.unpack_from('<H',raw,offset+4)[0] == machine
        else:
            assert raw[:4] == b'\xcf\xfa\xed\xfe' and struct.unpack_from('<I',raw,4)[0] == machine
        assert (path.stat().st_uid,path.stat().st_gid) == (os.getuid(),os.getgid())
        assert sha(path) != sha(OUT/'before-hd-build'/name)
        programs[name] = {'machine':machine,'sha256':sha(path)}
    linux = programs['taipei-preview']['sha256']
    assert linux == sha(OUT/'taipei-preview-r2') == '66e8e18ec202cf3cf22a3fe4893947adfb368425c47ba127177b6b8696dcc9c1'
    log = (OUT/'hd-integration-tests-r2.log').read_text()
    assert '--- FAIL' not in log and '--- SKIP' not in log and '\nPASS\n' in log
    assert '--- PASS: TestActualBudgetPanel' in log and '233 有效來源負對照' in log
    gui_root,scenario_root = RUNS/'gui-budget-cold-r4',RUNS/'budget-hd-scenario-r2'
    gui = read(gui_root/'result.json')
    assert gui['cold_start'] and not gui['checkpoint'] and gui['native_exit'] and gui['reload_read']
    assert gui['construction']['cold_loaded_same']
    assert gui['construction']['money_before_exit'] == gui['construction']['money_after_reload'] == '   79980'
    saved = Path(gui['save_dir'])/'ROUND4.SAV'
    assert saved.stat().st_size == 93567 and sha(saved) == gui['save_sha256']
    for label in ['quit-native-exit','reload/reload-quit-native-exit']:
        assert load_status(gui_root/(label+'-capture.zip'))['dos_exited']
    for root,adjust in [(gui_root,True),(gui_root/'reload',False)]:
        budget = read(root/'budget-gui.json')
        assert budget['normal_gui'] and budget['adjust'] is adjust
        assert budget['initial']['percent'] == ([10,100,100,100,100] if adjust else [9,99,100,100,100])
        assert budget['reopened']['percent'] == [9,99,100,100,100]
        assert {t['row'] for t in budget['f12_five_rows']} == set(range(5))
        assert all(t['frame_unchanged'] and t['no_dos_keyboard'] for t in budget['f12_five_rows'])
        assert all(a['original_read']['Step'] <= a['steps'] for a in budget['actions'])
        if adjust:
            actions = {a['label']:a for a in budget['actions']}
            for row in range(5):
                s = load_status(root/(f'budget-row-{row}-decrease-capture.zip'))
                assert int(s['hd']['budget_text'][row]) == budget['initial']['percent'][row]-1
                assert actions[f'row-{row}-restore']['original_read']
    scenario = read(scenario_root/'result.json')
    assert scenario['normal_gui'] and not scenario['checkpoint']
    assert [int(f['text']) for f in scenario['final_budget']['fields'][5:9]] == [2200,1778,6019,20247]
    assert len(scenario['records']) == 9
    for root in [gui_root,scenario_root]:
        assert linux in (root/'program-provenance.txt').read_text()
    receipts = {str(p.relative_to(ROOT)):sha(p) for root in [gui_root,scenario_root] for p in sorted(root.rglob('*-capture.zip'))}
    assert len(receipts) > 100
    for name,root in [('cold',gui_root),('scenario',scenario_root)]:
        count = len(list(root.rglob('*-capture.zip')))
        revision = 'r4' if name == 'cold' else 'r2'
        assert f'same-frame bundles verified: {count}' in (OUT/f'{name}-receipt-check-{revision}.log').read_text()
        assert f'全部正常收據來源、完整呈現與區外像素通過 {count}' in (OUT/f'{name}-pixels-{revision}.log').read_text()
    negative = read(RUNS/'budget-hd-negative-r2/result.json')
    assert len(negative) == 15 and sum(n['positive'] for n in negative) == 2
    assert sum(n['python_rejected'] and n['go_rejected'] for n in negative) == 13
    assert all(n['native_png_consistent'] and n['affected_digests_recomputed'] for n in negative)
    net = read(OUT/'negative-net-source.json')
    assert net['python_full_source_and_presentation'] and net['go'] == 'same-frame bundles verified: 1'
    assert int(net['texts'][-1]) == -1 and net['texts'] == net['hd_texts']
    assert sha(Path(net['receipt'])) == net['receipt_sha256']
    audit = read(OUT/'state-audit-r4.json')
    prereg = read(OUT/'state-preregister-r4.json')
    assert sha(ROOT/prereg['audit_program']) == prereg['audit_program_sha256']
    receipt = gui_root/'quit-file-theme-hd-capture.zip'
    normal = load_status(receipt)
    assert sha(receipt) == prereg['receipt_sha256'] and normal['steps'] == audit['steps'] == prereg['steps']
    assert audit['render_interval_steps'] == 24_000_000
    assert audit['observed_render_frames'] == len(audit['sampled_original_state_sha256']) == normal['steps']//24_000_000
    assert audit['state_equal'] and audit['sampled_original_states_equal'] and audit['normal_gui_frame_palette_reads_files_equal']
    assert set(audit['budget_hd_rows']) == {str(i) for i in range(5)}
    assert audit['file_dialog_families']['file-browser'] and audit['file_dialog_families']['quit-confirm']
    state = audit['state']
    assert state['frame_sha256'] == normal['frame_index_sha256'] and state['palette'] == normal['palette']
    assert state['key_reads'] == normal['key_reads'] and state['file_ops'] == normal['file_ops']
    assert state['save_sha256'].get('ROUND4.SAV') == gui['save_sha256']
    result = {'schema':1,'issue':39,'programs':programs,'patches':patches,
        'dosgolem_base':'a9714ebdab2ad6b529f81225472680f2b11f2842',
        'image':'sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3',
        'test_roots_passed':len(re.findall(r'^--- PASS:',log,re.M)),'test_skips':0,
        'source_samples':43,'source_negative_controls':233,'real_asset_faults':12,
        'normal_receipts':receipts,'normal_receipts_count':len(receipts),'normal_native_exits':2,
        'budget_setting_before_save_and_cold_loaded':[9,99,100,100,100],
        'save_sha256':gui['save_sha256'],'save_dir':gui['save_dir'],
        'sampled_original_state_count':len(audit['sampled_original_state_sha256']),
        'state_audit_sha256':sha(OUT/'state-audit-r4.json'),'state_preregister':prereg,
        'effective_presentation_negatives':13,'presentation_positives':2,
        'normal_negative_net_source':net,
        'source_files':{str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'app').rglob('*.go'))},
        'tool_files':{p.name:sha(p) for p in sorted((ROOT/'tools').glob('*budget*')) if p.is_file()},
        'lockfiles':{name:sha(ROOT/'app'/name) for name in ['go.mod','go.sum']},
        'original_files_unchanged':len(inventory['files']),'archive_unchanged':True,
        'scope':'限完整預算呈現及已抽樣路徑；極值規則、其他全部圖片／介面、真機與正式封包未完成'}
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['normal_receipts_count','normal_native_exits','save_sha256',
        'sampled_original_state_count','effective_presentation_negatives','test_roots_passed']},ensure_ascii=False))


if __name__ == '__main__':
    main()
