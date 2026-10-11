"""#31：五工具十八狀態、F12、原版循環及完整面板／區外核對。"""
import argparse
import json
from pathlib import Path
from hd_scroll_check import audit_bundle, source59
from hd_panels_check import TOOL_MANIFEST_SHA


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--receipts', type=Path, required=True)
    args = ap.parse_args(); sources = source59(Path('/orig'))
    samples, states, by_name = [], set(), {}
    for path in sorted(args.receipts.glob('*-capture.zip')):
        s, _, _, _, sample = audit_bundle(path, sources)
        panel = s['hd'].get('panel', ''); selection = s['hd'].get('panel_selection', -1)
        if panel.startswith('tool-'): states.add((panel, selection))
        name = path.name.removesuffix('-capture.zip'); by_name[name] = (panel, selection, s)
        samples.append({**sample, 'panel': panel, 'selection': selection})
    expected = {(f'tool-{tool:02d}', i) for tool, n in [(2,2),(5,2),(9,2),(10,10),(11,2)] for i in range(n)}
    assert states == expected, ('缺少十八個實際高清狀態', states ^ expected)
    for tool in [2, 5, 9, 10, 11]:
        prefix = f'tool-{tool:02d}'
        panel, selection, opened = by_name[prefix+'-open']
        assert (panel, selection) == (prefix, 0)
        _, _, off = by_name[prefix+'-theme-original']
        on_panel, on_selection, on = by_name[prefix+'-theme-hd']
        assert not off['hd_enabled'] and on['hd_enabled'] and on_panel == prefix and on_selection == 0
        assert opened['frame_index_sha256'] == off['frame_index_sha256'] == on['frame_index_sha256']
        assert (opened.get('key_reads') or []) == (off.get('key_reads') or []) == (on.get('key_reads') or [])
        for direction in ['left', 'right', 'escape']:
            _, _, s = by_name[prefix+'-'+direction]
            assert s['dos_blocked']
        if tool == 10:
            for i in range(1, 11): assert by_name[prefix+f'-down-{i}'][:2] == (prefix, i % 10)
            assert by_name[prefix+'-right'][:2] == (prefix, 0)
            for label in ['up-wrap', 'left', 'escape']: assert by_name[prefix+'-'+label][:2] == (prefix, 9)
        else:
            for label, selected in [('down',1),('down-boundary',0),('up',1),('up-boundary',0),('left',0),('right',0),('escape',0)]:
                assert by_name[prefix+'-'+label][:2] == (prefix, selected)
        for label in ['confirm', 'return-toolbar']:
            assert not by_name[prefix+'-'+label][2]['dos_blocked']
    result = {'manifest_sha256': TOOL_MANIFEST_SHA, 'states': sorted(states), 'f12_tools': [2,5,9,10,11],
              'source_palette_reference_and_outside_equal': True, 'original_navigation_verified': True,
              'bundles': len(samples), 'samples': samples}
    (args.receipts/'tool-panels-verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'samples'}, ensure_ascii=False))


if __name__ == '__main__': main()
