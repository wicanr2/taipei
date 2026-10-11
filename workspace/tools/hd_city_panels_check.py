"""#37：六功能二十九狀態、F12、完整來源／參考／區外獨立核對。"""
import argparse
import json
from pathlib import Path

from hd_panels_check import CITY_MANIFEST_SHA
from hd_scroll_check import audit_bundle, source59


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--receipts', type=Path, required=True)
    args = ap.parse_args()
    sources = source59(Path('/orig'))
    samples, states, by_name = [], set(), {}
    for path in sorted(args.receipts.rglob('*-capture.zip')):
        s, _, _, _, sample = audit_bundle(path, sources)
        panel, selection = s['hd'].get('panel', ''), s['hd'].get('panel_selection', -1)
        if panel.startswith('city-f'):
            states.add((panel, selection))
        name = str(path.relative_to(args.receipts)).removesuffix('-capture.zip')
        by_name[name] = s
        samples.append({**sample, 'receipt': name, 'panel': panel, 'selection': selection})
    expected = {(f'city-f{key}', i) for key, count in enumerate([1,4,3,6,10,5], 1) for i in range(count)}
    assert states == expected, ('缺少二十九種實際高清狀態', states ^ expected)
    for key in range(1, 7):
        opened, off, on = [by_name[f'f{key}/'+label] for label in ['open','theme-original','theme-hd']]
        assert not off['hd_enabled'] and on['hd_enabled']
        assert off['hd'].get('panel', '') == ''
        assert on['hd']['panel'] == f'city-f{key}' and on['hd']['panel_selection'] == 0
        assert opened['frame_index_sha256'] == off['frame_index_sha256'] == on['frame_index_sha256']
        assert opened['key_reads'] == off['key_reads'] == on['key_reads']
        keyboard = lambda s: [i for i in s['inputs'] if i['kind'] == 'keyboard']
        assert keyboard(opened) == keyboard(off) == keyboard(on)
    result = {'manifest_sha256': CITY_MANIFEST_SHA, 'states': sorted(states),
        'f12_menus': list(range(1,7)), 'f12_not_sent_to_dos': True,
        'source_palette_reference_and_outside_equal': True,
        'bundles': len(samples), 'samples': samples,
        'scope': '完整選單及區外；原版控制另由 city_menu_source_check 核對，存退讀及全部 HD 另驗'}
    (args.receipts/'city-panels-verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'samples'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
