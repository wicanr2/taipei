#!/usr/bin/env python3
"""040：鎖定原版、現行runtime材料、四架構與實際連結元件授權。"""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess

from full_asset_catalog import sha

FILES = ['water-b-v1.png', 'sand-b-v1.png', 'forest-b-v1.png', 'asphalt-b-v1.png',
         'industrial-paint-b-v1.png', 'city-icons-b-v1.png', 'new-game-panel-b-v1.png',
         'new-game-text-v1.json', 'menu-blue-b-v1.png', 'menu-wood-b-v2.png', 'menu-red-b-v1.png',
         'startup-menu-layout-v1.json', 'tool-menu-layout-v1.json', 'city-menu-layout-v1.json',
         'budget-layout-v1.json', 'ending-scene-v1/art-scaled.png']
FOLDERS = ['fonts', 'city-chrome-v1', 'footer-v1', 'startup-menus-v1', 'tool-menus-v1',
           'city-menus-v1', 'file-dialogs-v1', 'budget-v1', 'infrastructure-ready-v1',
           'power-facility-ready-v1', 'nuclear-ready-v1', 'transport-ready-v1',
           'civic-facilities-ready-v1', 'public-facilities-ready-v2', 'disaster-buildings-ready-v1',
           'map-completion-ready-v1', 'ending-scene-ready-v1', 'chart-windows-ready-v1', 'illustrations-ready-v1']
BINARIES = ['taipei-linux-amd64', 'taipei-windows-amd64.exe', 'taipei-macos-amd64',
            'taipei-macos-arm64', 'taipei-macos-universal']


def runtime_material_paths(root):
    paths = {root/n for n in FILES}
    # These three sealed layouts declare the runtime background/button paths.
    # Follow their asset table, not unrelated source/prototype metadata.
    for name in ['startup-menu-layout-v1.json', 'tool-menu-layout-v1.json', 'city-menu-layout-v1.json']:
        layout = json.loads((root/name).read_text())
        for filename, expected in layout['art_sha256'].items():
            path = Path(filename)
            assert not path.is_absolute() and '..' not in path.parts
            assert sha((root/path).read_bytes()) == expected
            paths.add(root/path)
    for name in FOLDERS:
        assert (root/name).is_dir()
        paths.update(p for p in (root/name).rglob('*') if p.is_file())
    assert all(p.is_file() and not p.is_symlink() for p in paths)
    return sorted(paths)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', type=Path, required=True)
    ap.add_argument('--build', type=Path, required=True)
    ap.add_argument('--version', required=True)
    a = ap.parse_args()
    assert re.fullmatch(r'v\.[0-9]+\.[0-9]+\.[0-9]+-[0-9]{8}', a.version)
    assert a.build.stat().st_uid == os.getuid() and not (a.build/'inputs.json').exists()
    commit = (a.build/'source-commit.txt').read_text().strip()
    assert subprocess.check_output(['git', '-C', str(a.project), 'rev-parse', a.version+'^{commit}'], text=True).strip() == commit
    source = a.project/'workspace/cache'/('release-source-'+a.version)
    inventory_raw = (a.project/'workspace/runs/inventory.json').read_bytes()
    assert sha(inventory_raw) == 'b9f1a573e3656d800354740edfe3707c80ce520abc9a140b12e5ce54e4e37084'
    inventory = json.loads(inventory_raw)
    root = a.project/'rs201 模擬台北'
    original = []
    for r in inventory['files']:
        path = root/r['path']
        assert path.is_file() and path.stat().st_size == r['bytes'] and sha(path.read_bytes()) == r['sha256']
        if r['path'].startswith('模擬台北/RS201/'):
            original.append({'file': path.name, 'bytes': r['bytes'], 'sha256': r['sha256']})
    assert len(inventory['files']) == 35 and len(original) == 23
    rar = a.project/inventory['archive']['name']
    assert rar.stat().st_size == inventory['archive']['bytes'] and sha(rar.read_bytes()) == inventory['archive']['sha256']
    material_root = a.project/'workspace/prototypes/hd-style'
    paths = runtime_material_paths(material_root)
    materials = [{'file': str(p.relative_to(material_root)), 'bytes': p.stat().st_size, 'sha256': sha(p.read_bytes()),
                  'rights': 'Noto OFL-1.1' if p.relative_to(material_root).parts[0] == 'fonts' else 'local-only original-derived HD'} for p in sorted(paths)]
    binaries, modules = [], {}
    for name in BINARIES:
        path = a.build/name
        data = path.read_bytes()
        assert a.version.encode() in data, ('missing program version', name)
        binaries.append({'file': name, 'bytes': len(data), 'sha256': sha(data)})
        if name.endswith('universal'):
            continue
        metadata = subprocess.check_output(['go', 'version', '-m', str(path)], text=True)
        (a.build/(name+'-go-build.txt')).write_text(metadata)
        for line in metadata.splitlines():
            fields = line.split()
            if fields and fields[0] == 'dep':
                modules[fields[1]] = {'path': fields[1], 'version': fields[2], 'sum': fields[3] if len(fields) > 3 else None}
    notices = a.build/'third-party'
    notices.mkdir()
    licenses = []

    def copy_license(path, filename, component):
        data = path.read_bytes()
        target = notices/filename
        target.write_bytes(data)
        licenses.append({'file': filename, 'component': component, 'sha256': sha(data), 'bytes': len(data)})

    for module in sorted(modules):
        info = modules[module]
        module_root = a.project/'workspace/cache/gomod'/(module+'@'+info['version'])
        if module == 'github.com/wicanr2/dosgolem':
            module_root = source/'workspace/cache/dosgolem-probe-src'
        candidates = sorted(p for p in module_root.glob('LICENSE*') if p.is_file())
        assert candidates, ('missing linked component license', module)
        safe = module.replace('/', '_')+'@'+info['version']
        for i, path in enumerate(candidates):
            copy_license(path, safe+('-'+str(i) if i else '')+'.txt', module)
        if module == 'github.com/wicanr2/dosgolem':
            copy_license(module_root/'audio/ymfm/LICENSE', 'YMFM-LICENSE.txt', 'YMFM')
        if module == 'github.com/hajimehoshi/ebiten/v2':
            # Preserve original GLFW wrapper copyright/license headers too.
            headers = set()
            for p in (module_root/'internal/glfw').glob('*.go'):
                header = p.read_text().split('package ', 1)[0]
                if 'Copyright' in header or 'SPDX-FileCopyrightText' in header:
                    headers.add(header)
            data = '\n'.join(sorted(headers)).encode()
            assert data
            path = notices/'Ebitengine-GLFW-NOTICES.txt'
            path.write_bytes(data)
            licenses.append({'file': path.name, 'component': 'Ebitengine GLFW', 'sha256': sha(data), 'bytes': len(data)})
    copy_license(material_root/'fonts/LICENSE', 'Noto-OFL-1.1.txt', 'Noto Sans CJK TC Regular Sans2.004')
    result = {'schema': 1, 'version': a.version, 'source_commit': commit,
              'dosgolem_commit': 'a9714ebdab2ad6b529f81225472680f2b11f2842',
              'original_inventory_sha256': sha(inventory_raw), 'original_tree_files_verified': 35,
              'original_archive_sha256': inventory['archive']['sha256'], 'original': original,
              'materials': materials, 'binaries': binaries, 'modules': list(modules.values()), 'licenses': licenses,
              'catalog_sha256': sha((source/'workspace/app/locales/ui.tsv').read_bytes()),
              'tool_sha256': sha(Path(__file__).read_bytes()), 'rights': 'full-local only; no public Release'}
    (a.build/'inputs.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print('LOCKED', len(original), 'original files;', len(materials), 'runtime materials;', len(modules), 'linked modules;', sha((a.build/'inputs.json').read_bytes()))


if __name__ == '__main__':
    main()
