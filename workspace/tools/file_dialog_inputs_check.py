"""#38：回讀正常探針，核對字集、退格、長度與空清單的實際來源。"""
import argparse
import json
import os
import zipfile
from pathlib import Path

from file_dialog_catalog import decode_browser, references
from full_asset_catalog import sha


def bundle(path):
    with zipfile.ZipFile(path) as z:
        status, frame = json.loads(z.read('status.json')), z.read('frame-index.bin')
    assert len(frame) == 64000 and sha(frame) == status['frame_index_sha256']
    return status, frame


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--original', type=Path, required=True)
    ap.add_argument('--runs', type=Path, required=True)
    ap.add_argument('--catalog', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--missing-run', type=Path)
    args = ap.parse_args()
    assert args.out.parent.stat().st_uid == os.getuid()
    if args.out.exists():
        assert args.out.stat().st_uid == os.getuid()
    refs = references((args.original/'RS201.ROM').read_bytes())
    first, extra = args.runs/'file-dialogs-native', args.runs/'file-dialogs-native-extra'
    samples = []
    previous = ' '*8
    for code in range(33,127):
        root = first if code < 48 else extra
        if code == 48:
            previous = ' '*8  # 第二次從全新 EXE、空白視窗開始。
        label = f'char-{code:02x}'
        path, back = root/(label+'-capture.zip'), root/(label+'-backspace-capture.zip')
        status, frame = bundle(path)
        back_status, back_frame = bundle(back)
        observed, cleared = decode_browser(frame,refs), decode_browser(back_frame,refs)
        assert observed is not None and cleared is not None
        assert status['key_reads'][-1]['Key'] == code
        assert len(back_status['key_reads']) == len(status['key_reads'])+1
        assert back_status['key_reads'][-1]['Word'] == 0x0e08
        alphanumeric = 48 <= code <= 57 or 65 <= code <= 90 or 97 <= code <= 122
        expected = chr(code).upper()+' '*7 if alphanumeric else previous
        assert observed['rows'][0] == expected, (code,observed['rows'][0],expected)
        assert cleared['rows'] == observed['rows'], (code,'最後字元的可見殘留不符')
        previous = cleared['rows'][0]
        samples.append({'input_code':code,'alphanumeric':alphanumeric,'display':observed['rows'][0],
            'after_backspace':cleared['rows'][0], 'receipt':str(path),'receipt_sha256':sha(path.read_bytes()),
            'backspace_receipt':str(back),'backspace_receipt_sha256':sha(back.read_bytes())})
    eight_status,eight_frame = bundle(extra/'length-eight-capture.zip')
    nine_status,nine_frame = bundle(extra/'length-nine-capture.zip')
    assert decode_browser(eight_frame,refs)['rows'][0] == 'ABCDEFGH'
    assert eight_frame == nine_frame and nine_status['key_reads'][-1]['Key'] == ord('I')
    _,cleared_frame = bundle(extra/'clear-eight-8-capture.zip')
    assert decode_browser(cleared_frame,refs)['rows'][0] == 'A       '
    _,pause_frame = bundle(extra/'pause-capture.zip')
    cancel_status,cancel_frame = bundle(extra/'save-empty-cancel-capture.zip')
    empty_status,empty_frame = bundle(extra/'load-empty-confirm-capture.zip')
    assert cancel_frame == empty_frame == pause_frame
    assert not cancel_status['dos_blocked'] and not empty_status['dos_blocked']
    assert not any(f['Name'].upper().endswith('.SAV') and f['Op'] in ['read','write'] for f in empty_status['file_ops'])
    # 按目前使用中的索引驗色盤，保留完整參考供後續 READY 審查。
    catalog = json.loads(args.catalog.read_bytes())
    reference = bundle(args.runs/'gui-cold/save-dialog-capture.zip')[0]['palette']
    for sample in catalog['samples']:
        status,_ = bundle(Path(sample['receipt']))
        assert all(status['palette'][i] == reference[i] for i in sample['palette_indices'])
    list_root = args.runs/'file-dialogs-native-list'
    listed = json.loads((list_root/'result.json').read_bytes())
    names = sorted(p.stem for p in Path(listed['save_dir']).glob('*.SAV'))
    assert len(names) == 10 and all(len(n) == 8 for n in names)
    positions = [0]+list(range(1,10))+[9,9]+list(range(8,-1,-1))+[0,0]
    assert len(listed['list_states']) == len(positions) == 23
    for state,position in zip(listed['list_states'],positions):
        assert state['rows'][0] == names[position]
        visible = state['rows'][1:]
        start = names.index(visible[0])
        assert visible == names[start:start+7]
        assert state['colors'][0] == 15 and state['colors'][1:].count(32) == 1
        selected = state['colors'][1:].index(32)
        assert visible[selected] == names[position]
        assert all(c == (32 if i == selected else 31) for i,c in enumerate(state['colors'][1:]))
    for label in ['load-list-cancel','quit-no']:
        status,frame = bundle(list_root/(label+'-capture.zip'))
        assert frame == pause_frame and not status['dos_blocked']
    seed_sha = listed['seed_sha256']
    assert all(sha(p.read_bytes()) == seed_sha for p in Path(listed['save_dir']).glob('*.SAV'))
    edges_root = args.runs/'file-dialogs-native-edges'
    edges = json.loads((edges_root/'result.json').read_bytes())
    # 前端在私有執行目錄已有兩份 ROM 副本；空白確認只核對 SAV 與 DOS 寫入。
    assert not any(n.upper().endswith('.SAV') for n in edges['empty_save']['files'])
    assert edges['empty_save']['restored']
    assert not any(f['Name'].upper().endswith('.SAV') and f['Op'] in ['create','write']
                   for f in edges['empty_save']['status']['file_ops'])
    overwrite = edges['overwrite']
    assert overwrite['before_sha256'] == seed_sha != overwrite['after_sha256']
    assert overwrite['bytes'] == 93567 and overwrite['restored']
    save_ops = [f for f in overwrite['status']['file_ops'] if f['Name'].upper() == 'ALPHA001.SAV']
    # 固定 dosgolem 的 AH=40h 記在 Wrote，現行前端未匯出；FileOps 沒有 write。
    # 以原版開關檔與落地檔案雜湊、大小、其他檔案不變核對覆寫結果。
    assert any(f['Op'] == 'open' and not f['Failed'] for f in save_ops)
    assert any(f['Op'] == 'close' and not f['Failed'] for f in save_ops)
    for path in Path(edges['save_dir']).glob('*.SAV'):
        assert sha(path.read_bytes()) == (overwrite['after_sha256'] if path.name == 'ALPHA001.SAV' else seed_sha)
    missing = None
    if args.missing_run:
        missing = json.loads((args.missing_run/'result.json').read_bytes())['missing_name']
        assert missing['frame_unchanged'] and missing['browser']['rows'][0] != missing['typed']
        before,_ = bundle(args.missing_run/'load-list-open-capture.zip')
        after,_ = bundle(args.missing_run/'load-unavailable-name-capture.zip')
        new_reads = after['key_reads'][len(before['key_reads']):]
        assert [k['Key'] for k in new_reads] == list(b'MISSING9')
    result = {'normal_characters':94,'alphanumeric_inputs':sum(s['alphanumeric'] for s in samples),
        'punctuation_ignored':sum(not s['alphanumeric'] for s in samples),'lowercase_display_uppercase':True,
        'eight_characters_visible':True,'ninth_read_but_frame_unchanged':True,
        'last_deleted_character_remains_visible':True,'next_character_replaces_visible_residue':True,
        'save_escape_restores_whole_frame':True,'empty_load_confirm_restores_whole_frame':True,
        'catalog_sha256':sha(args.catalog.read_bytes()),'palette_reference':reference,
        'list_states':23,'list_scrolling_and_boundaries':True,'unselected_ink_index':31,
        'list_cancel_and_quit_no_restore_whole_frame':True,
        'empty_save_creates_no_sav':True,'overwrite_without_second_prompt':True,
        'overwritten_sha256':overwrite['after_sha256'], 'load_name_edit_ignored':missing is not None,
        'samples':samples,'scope':'正常來源操作取樣；HD、原版退出與存退讀的正式驗收另驗'}
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['samples','palette_reference']},ensure_ascii=False))


if __name__ == '__main__':
    main()
