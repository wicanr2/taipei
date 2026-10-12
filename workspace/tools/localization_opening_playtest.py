"""#52: actual cold-start GUI text sources; invoked by interface playtest."""
import json
import subprocess
import time
import zipfile


def verify(status, wait, key, capture, out, root):
    seen, images, partial = set(), set(), False
    end = time.monotonic() + 420
    while time.monotonic() < end:
        s = status()
        h = s.get('hd', {})
        for text in (h.get('source_text_keys') or []):
          if text not in seen:
            seen.add(text)
            capture('opening-' + text)
            print('original source text', text, s['steps'], flush=True)
        for picture in (h.get('source_image_keys') or []):
          if picture not in images:
            images.add(picture)
            capture('opening-' + picture)
            print('original source picture', picture, s['steps'], flush=True)
        candidates = [d for d in (s.get('source_text') or [])
                      if d['original_ea'] == 0x14ed2 and 0 < d['visible_bytes'] < len(d['source_hex']) // 2]
        if not partial and candidates and h.get('source_text_fields', 0):
            subprocess.run(['xdotool', 'search', '--name', '模擬台北', 'windowfocus'], check=True)
            key('F11')
            opened = wait(lambda x: x.get('language_panel') is True, 'opening-picker')
            for _ in range(3):
                key('Down')
            selected = wait(lambda x: x.get('language_selection') == 3, 'opening-korean-selection')
            for field in ['steps', 'registers', 'segments', 'ip', 'ticks', 'key_reads',
                          'frame_index_sha256', 'palette', 'source_text']:
                assert opened[field] == selected[field], field
            key('F12')
            off = wait(lambda x: x.get('hd_enabled') is False, 'opening-original')
            assert off['source_text'] == opened['source_text']
            assert off['frame_index_sha256'] == opened['frame_index_sha256']
            with zipfile.ZipFile(out / 'capture.zip') as z:
                native, shown = z.read('frame.png'), z.read('presentation.png')
            for crop in ['320x800+0+0', '320x800+960+0']:
                def rgba(data, scale):
                    args = ['convert', 'png:-']
                    if scale:
                        args += ['-filter', 'point', '-resize', '1280x800!']
                    return subprocess.run(args + ['-crop', crop, '+repage', '-depth', '8', 'rgba:-'],
                                          input=data, stdout=subprocess.PIPE, check=True).stdout
                assert rgba(native, True) == rgba(shown, False)
            capture('opening-partial-original-picker')
            key('F12')
            wait(lambda x: x.get('hd_enabled') is True, 'opening-hd')
            key('Return')
            wait(lambda x: x.get('language') == 'ko' and not x.get('language_panel'), 'opening-korean')
            capture('opening-partial-korean')
            partial = True
        if s.get('dos_blocked') and s.get('steps', 0) > 1_850_000_000:
            break
        time.sleep(.1)
    else:
        raise RuntimeError('opening sources timed out: ' + str(status().get('hd')))
    assert partial, 'no normal GUI typewriter language switch'
    assert {'art.department_store', 'art.bank', 'art.protest', 'startup.title'} <= images, images
    assert {'intro.date', 'intro.sogo', 'intro.metro', 'intro.pollution', 'letter.citizens'} <= seen, seen
    for _ in range(3):
        if status().get('hd', {}).get('panel') == 'main':
            break
        before = status()['steps']
        key('space')
        wait(lambda x: x.get('hd', {}).get('panel') == 'main' or
             x.get('steps', 0) > before + 24_000_000, 'opening-continue')
        time.sleep(1)
    wait(lambda x: x.get('hd', {}).get('panel') == 'main', 'opening-main')
    result = {'normal_gui': True, 'checkpoint': False, 'text_keys': sorted(seen),
              'image_keys': sorted(images), 'mid_typewriter_language_switch': partial,
              'f12_original_unobscured_pixels': True, 'long_state_sampling': False}
    (root / 'opening-verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
