"""#37：獨立核對正常選取來源、循環、跨選單、取消與逐次讀鍵。"""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

SOURCE_SHA = 'eb98c1def205eb39e533f9646ad9336fafc7268559998e93e3a1ed1c7157f870'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    with zipfile.ZipFile(path) as z:
        s, frame = json.loads(z.read('status.json')), z.read('frame-index.bin')
    assert len(frame) == 64000 and sha(frame) == s['frame_index_sha256'], path
    return s, frame


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--receipts', type=Path, nargs='+', required=True)
    ap.add_argument('--sources', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    raw = args.sources.read_bytes(); assert sha(raw) == SOURCE_SHA
    data = json.loads(raw); assert len(data['states']) == 29
    sources = {(s['id'], s['selection']): s for s in data['states']}
    counts = [1, 4, 3, 6, 10, 5]
    samples, acks = [], []

    def source(s, frame, key, selected):
        ref = sources[f'city-f{key}', selected]
        x, y, w, h = ref['native']
        pixels = b''.join(frame[yy*320+x:yy*320+x+w] for yy in range(y, y+h))
        colors = bytes(v for i in ref['palette_indices'] for v in s['palette'][i])
        assert sha(pixels) == ref['source_sha256'] and sha(colors) == ref['palette_sha256']
        assert s['dos_blocked']

    def ack(before, after, word, scan, label):
        reads = lambda s: sum(k.get('Word') == word for k in s.get('key_reads', []))
        breaks = lambda s: sum(k.get('kind') == 'keyboard' and k.get('scan') == scan+128 for k in s.get('inputs', []))
        assert reads(after) == reads(before)+1 and breaks(after) == breaks(before)+1, label
        assert after['steps'] > before['steps']
        acks.append({'label': label, 'word': word, 'before_step': before['steps'], 'release_step': after['steps']})

    for key, count in enumerate(counts, 1):
        directory = next(root/f'f{key}' for root in args.receipts if (root/f'f{key}/result.json').is_file())
        pause, baseline = read(directory/'pause-capture.zip')
        before = pause
        actions = [('open', key, 0, 0x3a+key, 0)]
        actions += [(f'down-{i:02d}', key, i % count, 0x50, 0) for i in range(1, count+1)]
        actions += [(f'up-{i:02d}', key, -i % count, 0x48, 0) for i in range(1, count+1)]
        actions += [('left', key-1 if key > 1 else 6, 0, 0x4b, 0),
                    ('right', key, 0, 0x4d, 0), ('escape', 0, 0, 1, 27)]
        for label, target, selected, scan, ascii_code in actions:
            path = directory/(label+'-capture.zip')
            s, frame = read(path)
            ack(before, s, (scan << 8) | ascii_code, scan, f'f{key}/{label}')
            if target:
                source(s, frame, target, selected)
            else:
                assert not s['dos_blocked'] and frame == baseline
            samples.append({'receipt': str(path), 'key': key, 'label': label,
                            'target': target, 'selection': selected, 'steps': s['steps']})
            before = s
        result = json.loads((directory/'result.json').read_text())
        assert result['normal_gui'] and not result['checkpoint']
        assert result['last_status']['frame_index_sha256'] == pause['frame_index_sha256']
    assert len(acks) == 82
    result = {'sources_sha256': SOURCE_SHA, 'menus': 6, 'states': 29,
              'normal_bundles': sum(len(list(root.rglob('*-capture.zip'))) for root in args.receipts),
              'acknowledged_actions': acks, 'samples': samples,
              'original_cycles_and_cross_menu_wrap_verified': True,
              'escape_restored_original_map': 6,
              'scope': '原版正常來源及控制；不證明 HD 或原版退出完成'}
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['samples', 'acknowledged_actions']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
