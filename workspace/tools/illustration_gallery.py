"""039：正常開場銀行場景的五語系／原版照片與Help抽驗。"""
import hashlib
import json
import subprocess
import zipfile


def verify(status, wait, key, capture, out, root):
    evidence = []

    def language(lang):
        before = status()
        key('F11')
        opened = wait(lambda s: s.get('language_panel') is True, 'art-picker')
        index = ['zh-Hant', 'zh-Hans', 'ja', 'ko', 'en'].index(lang)
        current = ['zh-Hant', 'zh-Hans', 'ja', 'ko', 'en'].index(before['language'])
        for _ in range((index-current) % 5):
            key('Down')
        selected = wait(lambda s: s.get('language_selection') == index, 'art-select-'+lang)
        for field in ['steps', 'registers', 'segments', 'ip', 'ticks', 'key_reads', 'file_ops', 'palette', 'frame_index_sha256']:
            assert opened[field] == selected[field], field
        key('Return')
        return wait(lambda s: s.get('language') == lang and not s.get('language_panel'), 'art-'+lang)

    key('F12')
    wait(lambda s: s.get('hd_enabled') is False, 'art-original')
    capture('illustration-bank-original')
    with zipfile.ZipFile(out/'illustration-bank-original-capture.zip') as z:
        def rgba(data, scale=False):
            args = ['convert', 'png:-']
            if scale:
                args += ['-filter', 'point', '-resize', '1280x800!']
            return subprocess.run(args+['-depth', '8', 'rgba:-'], input=data, stdout=subprocess.PIPE, check=True).stdout
        assert rgba(z.read('frame.png'), True) == rgba(z.read('presentation.png'))
    key('F12')
    wait(lambda s: s.get('hd_enabled') is True, 'art-hd')
    for lang in ['zh-Hant', 'zh-Hans', 'ja', 'ko', 'en']:
        language(lang)
        capture('illustration-bank-'+lang)
        path = out/('illustration-bank-'+lang+'-capture.zip')
        with zipfile.ZipFile(path) as z:
            s = json.loads(z.read('status.json'))
            assert s['language'] == lang and not s.get('language_panel')
            assert 'a17-00' in s['hd']['illustrations']['images'], s['hd']['illustrations']
            assert 'art.bank' in s['hd']['source_image_keys'], s['hd']['source_image_keys']
            evidence.append({'language': lang, 'steps': s['steps'], 'capture_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                             'illustrations': s['hd']['illustrations'], 'frame_index_sha256': s['frame_index_sha256']})
    language('zh-Hant')
    subprocess.run(['xdotool', 'keydown', 'Shift_L'], check=True)
    try:
        key('F1')
    finally:
        subprocess.run(['xdotool', 'keyup', 'Shift_L'], check=True)
    opened = wait(lambda s: s.get('help_panel') is True, 'art-help')
    capture('illustration-help-zh-Hant')
    key('Escape')
    closed = wait(lambda s: s.get('help_panel') is False, 'art-help-close')
    assert opened['key_reads'] == closed['key_reads']
    result = {'issue': 32, 'normal_gui': True, 'checkpoint': False, 'photos': evidence,
              'original_nearest_pixels': True, 'f11_modal_state_unchanged': True, 'help_input_isolation': True,
              'same_state_across_languages': False, 'scope': '正常開場同銀行背景；角色隨原版時間運行，不宣稱五張同狀態'}
    (root/'illustration-gallery.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
