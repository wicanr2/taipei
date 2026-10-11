"""#47：直接解已見完整政績底圖，核對正常兩次退出及色盤。"""
import argparse
import collections
import hashlib
import json
import os
import platform
import struct
import zipfile
from pathlib import Path

from rom_catalog import png

ROMS = {
    'RS201.ROM': ('0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29', 69, 23),
    'RS201A.ROM': ('5d66f238dce650b8a407986100392ee4b8ac2aa23a033e80a7ca18ed91b3d9b0', 49, 1),
}
SOURCE_SHA = '0040b4374f37464862ae2f89da5bc897ddb7f53d539edd597cf8b2b6ff784ebd'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def decode_member(data, file_offset):
    assert data[:4] == struct.pack('<HH', 320, 200)
    output = bytearray()
    at = 4
    runs = []
    literals = 0
    while at < len(data):
        value = data[at]
        start = at
        at += 1
        if value:
            output.append(value)
            literals += 1
        else:
            assert at + 2 <= len(data)
            value, count = data[at:at+2]
            at += 2
            assert count > 0
            runs.append({'file_offset': file_offset+start, 'output_offset': len(output),
                         'value': value, 'count': count})
            output.extend(bytes([value])*count)
        assert len(output) <= 64000
    assert at == len(data) and len(output) == 64000
    assert sha(output) == SOURCE_SHA
    return bytes(output), {'literal_count': literals, 'runs': runs}


def bundle(path):
    with zipfile.ZipFile(path) as z:
        status = json.loads(z.read('status.json'))
        pixels = z.read('frame-index.bin')
    assert len(pixels) == 64000 and sha(pixels) == status['frame_index_sha256']
    return status, pixels


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--original', type=Path, required=True)
    ap.add_argument('--receipts', type=Path, nargs='+', required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    assert not args.out.exists() and args.out.parent.stat().st_uid == os.getuid()
    sources = []
    frame = None
    for name, (digest, count, member) in ROMS.items():
        raw = (args.original/name).read_bytes()
        assert sha(raw) == digest
        # 固定版本目錄項採 16 bytes，定位基準是 ROM 檔案偏移。
        assert len(raw) >= 16+count*16
        offset, size = struct.unpack_from('<IH', raw, 18+member*16)
        assert offset >= 16+count*16 and offset+size <= len(raw)
        pixels, encoding = decode_member(raw[offset:offset+size], offset)
        assert frame is None or pixels == frame
        frame = pixels
        sources.append({'rom': name, 'rom_sha256': digest, 'member': member,
                        'file_offset': offset, 'length': size,
                        'member_sha256': sha(raw[offset:offset+size]), 'encoding': encoding})
    receipts = []
    palette = None
    colors = sorted(set(frame))
    for root in args.receipts:
        result = json.loads((root/'result.json').read_text())
        assert result['cold_start'] and not result['checkpoint']
        assert result['native_exit'] and result['reload_read']
        for prefix, subdir in [('', root), ('reload-', root/'reload')]:
            score_path = subdir/(prefix+'quit-score-capture.zip')
            exit_path = subdir/(prefix+'quit-native-exit-capture.zip')
            status, actual = bundle(score_path)
            exited, _ = bundle(exit_path)
            assert actual == frame and status['mode'] == 0x13
            assert status['dos_blocked'] and not status['dos_exited']
            assert exited['dos_exited'] and exited['mode'] == 3
            assert exited['steps'] > status['steps']
            used = {str(c): status['palette'][c] for c in colors}
            assert palette is None or used == palette
            palette = used
            receipts.append({'receipt': str(score_path), 'receipt_sha256': sha(score_path.read_bytes()),
                             'steps': status['steps'], 'frame_sha256': sha(actual),
                             'key_reads': len(status['key_reads']),
                             'exit_receipt': str(exit_path), 'exit_steps': exited['steps']})
    assert len(receipts) >= 4
    result = {'schema': 1, 'issue': 47, 'stage': 'DRAFT',
              'evidence': '已證實，限正常退出的完整靜態底圖、已用色盤及阻塞輸入相位',
              'address_space': 'ROM file offsets; zero-based member indices',
              'tool': 'ending_scene_source_check.py / Python '+platform.python_version(),
              'source_size': [320, 200], 'source_sha256': SOURCE_SHA,
              'sources': sources, 'used_palette': palette,
              'pixel_counts': dict(collections.Counter(frame)), 'receipts': receipts,
              'title': {'text': '您的政績', 'evidence': '已證實，正常原版畫面人工辨讀；不推定 EXE 繪字呼叫'},
              'unknown': ['取得政績後的圖案或文字變化', '其他評分及動畫相位', '原版內部評分規則']}
    args.out.mkdir()
    assert args.out.stat().st_uid == os.getuid()
    (args.out/'source-index.bin').write_bytes(frame)
    first, _ = bundle(Path(receipts[0]['receipt']))
    png(args.out/'source.png', 320, 200, frame, bytes(c for rgb in first['palette'] for c in rgb))
    (args.out/'source-check.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'receipts': len(receipts), 'aliases': len(sources),
                      'colors': len(colors), 'source_sha256': SOURCE_SHA}))


if __name__ == '__main__':
    main()
