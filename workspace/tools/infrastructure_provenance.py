"""#44／026：彙整第一批正式呈現、正常生命周期與狀態證據。"""
import json
import os
import re
import struct
import zipfile
from pathlib import Path

from hd_source_audit import cell,sha

ROOT = Path('/workspace')
RUNS = ROOT/'runs'
OUT = RUNS/'infrastructure-source'
GUI = RUNS/'gui-infrastructure-cold-r2'


def read(path):
    return json.loads(path.read_text())


def bundle(path):
    with zipfile.ZipFile(path) as z:
        s,frame = json.loads(z.read('status.json')),z.read('frame-index.bin')
    assert sha(frame)==s['frame_index_sha256']
    return s,frame


def main():
    assert OUT.stat().st_uid==os.getuid()
    target = OUT/'ready25-provenance.json'
    assert not target.exists()
    inventory = read(RUNS/'inventory.json')
    for item in inventory['files']:
        path = Path('/project/rs201 模擬台北')/item['path']
        assert path.stat().st_size==item['bytes'] and sha(path.read_bytes())==item['sha256']
    assert sha((Path('/project')/inventory['archive']['name']).read_bytes())==inventory['archive']['sha256']
    materials = ROOT/'prototypes/hd-style'
    manifest_path = materials/'infrastructure-ready-v1/manifest.json'
    assert sha(manifest_path.read_bytes())=='720e3d40b253c6a505dbfa43f415cb0752e18ea51150d9888c1ea3f4c7bc7aec'
    manifest = read(manifest_path)
    assert len(manifest['sources'])==25
    for record in manifest['sources']:
        for suffix,key in [('indices','indices_sha256'),('weights','weights_sha256')]:
            path = manifest_path.parent/f'39-{record["image"]:03d}-{suffix}.bin'
            assert path.stat().st_size==5184 and sha(path.read_bytes())==record[key]
    for name,want in manifest['materials'].items():
        assert sha((materials/(name+'-b-v1.png')).read_bytes())==want
    tests = (OUT/'ready25-go-tests-r2.log').read_text()
    regression = (OUT/'ready25-regression.log').read_text()
    for log,count in [(tests,4),(regression,6)]:
        assert '--- FAIL' not in log and '--- SKIP' not in log and '\nPASS\n' in log
        assert len(re.findall(r'^--- PASS:',log,re.M))==count
    negative = read(RUNS/'infrastructure-hd-negative-r1/result.json')
    assert len(negative)==7 and sum(r['positive'] for r in negative)==2 and sum(r['rejected'] for r in negative)==5
    assert all(r['affected_digests_recomputed'] and r['native_png_consistent'] for r in negative)
    gui = read(GUI/'result.json')
    assert gui['cold_start'] and gui['native_exit'] and gui['reload_read'] and not gui['checkpoint']
    assert gui['construction']['cold_loaded_same']
    assert gui['construction']['money_before_exit']==gui['construction']['money_after_reload']
    saved = Path(gui['save_dir'])/'ROUND4.SAV'
    assert saved.stat().st_size==93567 and sha(saved.read_bytes())==gui['save_sha256']
    exits = []
    for label in ['quit-native-exit','reload/reload-quit-native-exit']:
        s,_ = bundle(GUI/(label+'-capture.zip'))
        assert s['dos_exited']
        exits.append({'receipt':label,'steps':s['steps']})
    flow = read(GUI/'infrastructure-gui.json')
    assert flow['normal_gui'] and not flow['checkpoint'] and len(flow['roads'])==4
    assert {s['axis'] for s in flow['scrolls']}=={'X','Y'}
    before,frame = bundle(GUI/'infrastructure-before-save-capture.zip')
    loaded,reloaded = bundle(GUI/'reload/load-accept-capture.zip')
    restored = []
    for col,row in flow['roads']:
        world = (12+col,12+row)
        values = []
        for s,pixels in [(before,frame),(loaded,reloaded)]:
            origin = s['map_origin']
            assert origin['Valid']
            cx,cy = world[0]-origin['X'],world[1]-origin['Y']
            assert 0<=cx<29 and 0<=cy<15
            values.append(cell(pixels,5+cx*9,34+cy*9))
        assert values[0]==values[1]
        assert any(sha(values[0])==r['source_sha256'] for r in manifest['sources'])
        restored.append({'world':world,'source_sha256':sha(values[0]),'cold_loaded_same':True})
    pixels = read(OUT/'ready25-normal-pixels.json')
    receipts = {str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sorted(GUI.rglob('*-capture.zip'))}
    assert len(pixels['samples'])==len(receipts)
    assert pixels['independent_rom_geometry_shader'] and pixels['whole_tiles_and_all_fallback_equal']
    assert len(pixels['normal_scroll_comparisons'])==2 and all(s['same_world_tiles']>=1 for s in pixels['normal_scroll_comparisons'])
    assert f'same-frame bundles verified: {len(receipts)}' in (OUT/'ready25-receipt-check.log').read_text()
    prereg = read(OUT/'ready25-state-preregister.json')
    audit = read(OUT/'ready25-state-audit.json')
    assert sha((ROOT/prereg['audit_program']).read_bytes())==prereg['audit_program_sha256']
    prefix = ROOT/prereg['receipt']
    prefix_status,_ = bundle(prefix)
    assert sha(prefix.read_bytes())==prereg['receipt_sha256']
    assert prefix_status['steps']==prereg['steps']==audit['steps']
    assert audit['state_equal'] and audit['sampled_original_states_equal'] and audit['normal_gui_frame_palette_reads_files_equal']
    assert audit['render_interval_steps']==24_000_000
    assert len(audit['sampled_original_state_sha256'])==audit['observed_render_frames']==audit['steps']//24_000_000
    assert audit['infrastructure_frames'] and any(15<=int(i)<=29 for i in audit['infrastructure_images'])
    assert any(45<=int(i)<=55 for i in audit['infrastructure_images'])
    assert audit['state']['save_sha256']['ROUND4.SAV']==gui['save_sha256']
    programs = {}
    for name,machine in [('taipei-preview',62),('taipei-preview-windows-amd64.exe',0x8664),
        ('taipei-preview-macos-amd64',0x1000007),('taipei-preview-macos-arm64',0x100000c)]:
        path = RUNS/name
        raw = path.read_bytes()
        if name=='taipei-preview':
            assert raw[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',raw,18)[0]==machine
        elif name.endswith('.exe'):
            offset = struct.unpack_from('<I',raw,0x3c)[0]
            assert raw[:2]==b'MZ' and raw[offset:offset+4]==b'PE\0\0' and struct.unpack_from('<H',raw,offset+4)[0]==machine
        else:assert raw[:4]==b'\xcf\xfa\xed\xfe' and struct.unpack_from('<I',raw,4)[0]==machine
        assert (path.stat().st_uid,path.stat().st_gid)==(os.getuid(),os.getgid())
        programs[name] = {'machine':machine,'sha256':sha(raw)}
    assert programs['taipei-preview']['sha256'] in (GUI/'program-provenance.txt').read_text()
    assert programs['taipei-preview']['sha256'] in (OUT/'ready25-clean-rebuild.txt').read_text()
    patches = {p.name:sha(p.read_bytes()) for p in sorted((ROOT/'tools').glob('dosgolem-*.patch'))}
    assert len(patches)==7 and patches==read(RUNS/'dos-clock-source/provenance.json')['patches']
    result = {'schema':1,'issue':44,'stage':'normal25','sources':25,'source_pixel_negatives':2025,
        'real_asset_faults':162,'fixed_world_phase_rasters':16,'new_test_roots':4,'regression_test_roots':6,
        'normal_receipts_count':len(receipts),'normal_receipts':receipts,'normal_native_exits':exits,
        'normal_road_cold_loaded':restored,'normal_scroll_comparisons':pixels['normal_scroll_comparisons'],
        'save_sha256':gui['save_sha256'],'save_dir':gui['save_dir'],'state_sha256':audit['state_sha256'],
        'sampled_original_state_count':len(audit['sampled_original_state_sha256']),
        'state_preregister':prereg,'state_audit_sha256':sha((OUT/'ready25-state-audit.json').read_bytes()),
        'effective_presentation_negatives':5,'presentation_positives':2,'programs':programs,
        'dosgolem_base':'a9714ebdab2ad6b529f81225472680f2b11f2842','patches':patches,
        'image':'sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3',
        'original_files_unchanged':len(inventory['files']),'archive_unchanged':True,
        'scope':'限第一批正常 25 張呈現；其餘候選、全部 HD、真機與正式封包仍未完成'}
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['sources','normal_receipts_count','save_sha256','sampled_original_state_count']},ensure_ascii=False))


if __name__=='__main__':
    main()
