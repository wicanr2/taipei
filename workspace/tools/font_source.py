"""#18：下載固定版本字型及授權，雜湊驗證後才更新本機檔案。"""
import hashlib
import json
import urllib.request
from pathlib import Path

root = Path('/fonts')
base = 'https://raw.githubusercontent.com/notofonts/noto-cjk/Sans2.004/'
files = {
    'NotoSansCJKtc-Regular.otf': ('Sans/OTF/TraditionalChinese/NotoSansCJKtc-Regular.otf', 'dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4'),
    'LICENSE': ('LICENSE', '6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2'),
}
meta = {}
for name, (remote, expected) in files.items():
    dest = root/name
    if not dest.is_file() or hashlib.sha256(dest.read_bytes()).hexdigest() != expected:
        with urllib.request.urlopen(base+remote, timeout=60) as response:
            data = response.read()
        assert hashlib.sha256(data).hexdigest() == expected, f'來源雜湊不符：{name}'
        temporary = dest.with_suffix(dest.suffix+'.tmp')
        temporary.write_bytes(data)
        temporary.replace(dest)
    meta[name] = {'url':base+remote, 'sha256':expected, 'bytes':dest.stat().st_size}
(root/'source.json').write_text(json.dumps(meta, indent=2))
print(json.dumps(meta))
