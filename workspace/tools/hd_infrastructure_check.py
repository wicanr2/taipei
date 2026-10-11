"""#44／026：獨立以 ROM、整數幾何與 Fraction 色彩核對正式 GUI 圖塊。"""
import argparse
import functools
import json
from pathlib import Path

from hd_file_dialogs_check import rgba
from hd_source_audit import cell, scene
from infrastructure_prototype_check import read_sources, sha, tile_image

IMAGES = list(range(15,26))+list(range(27,30))+list(range(45,56))


@functools.lru_cache(maxsize=1)
def references():
    root = Path('/workspace/prototypes/hd-style')
    raw = (root/'infrastructure-ready-v1/manifest.json').read_bytes()
    assert sha(raw)=='720e3d40b253c6a505dbfa43f415cb0752e18ea51150d9888c1ea3f4c7bc7aec'
    manifest = json.loads(raw)
    tiles,aliases = read_sources(Path('/orig/RS201.ROM').read_bytes())
    assert [r['image'] for r in manifest['sources']]==IMAGES
    for record in manifest['sources']:
        source = tiles[record['image']]
        assert record['source_sha256']==sha(source) and record['aliases']==aliases[source]
        assert record['used_colors']==sorted(set(source))
        for suffix,key in [('indices','indices_sha256'),('weights','weights_sha256')]:
            assert sha((root/'infrastructure-ready-v1'/f'39-{record["image"]:03d}-{suffix}.bin').read_bytes())==record[key]
    materials = {}
    for name,want in manifest['materials'].items():
        path = root/(name+'-b-v1.png')
        assert sha(path.read_bytes())==want
        materials[name] = rgba(path,(1254,1254))
    return {tiles[i]:i for i in IMAGES},manifest,materials


@functools.lru_cache(maxsize=4096)
def expected_tile(source,world,palette):
    return bytes(tile_image(source,world,palette,references()[2],3,4))


def audit_infrastructure(s,frame,pixels):
    if 'infrastructure' not in s['hd']:
        return set()
    sources,manifest,_ = references()
    origin = s.get('map_origin') or {}
    active = (s['hd_enabled'] and scene(s,frame) and origin.get('Valid')
        and 0<=origin['X']<=76 and 0<=origin['Y']<=74)
    matched,painted,images,reasons = 0,set(),{},{}
    palette = tuple(tuple(c) for c in s['palette'])
    for row in range(15):
        for col in range(29):
            x,y = 5+col*9,34+row*9
            source = cell(frame,x,y)
            if not active or source not in sources:continue
            matched += 1
            if any(list(palette[i])!=manifest['palette'][str(i)] for i in set(source)):
                reason = 'palette-mismatch'
                expected = b''.join(b''.join(bytes(palette[i]+(255,))*4 for i in source[r*9:(r+1)*9])*4 for r in range(9))
            else:
                reason = 'matched-infrastructure'
                expected = expected_tile(source,((origin['X']+col)*36,(origin['Y']+row)*36),palette)
                painted.add((x,y))
                key = str(sources[source])
                images[key] = images.get(key,0)+1
            reasons[reason] = reasons.get(reason,0)+1
            for dy in range(36):
                at = ((y*4+dy)*1280+x*4)*4
                assert pixels[at:at+144]==expected[dy*144:(dy+1)*144],(col,row,'正式道路電線整格像素失配')
    reported = s['hd']['infrastructure']
    assert reported['matched']==matched and reported['painted']==len(painted) and reported['fallback']==matched-len(painted)
    assert reported.get('images',{})==images and reported.get('reasons',{})==reasons
    return painted


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--receipts',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args = ap.parse_args()
    from hd_scroll_check import audit_bundle,source59
    sources = source59(Path('/orig'))
    records = []
    for path in sorted(args.receipts.rglob('*-capture.zip')):
        s,_,_,_,_ = audit_bundle(path,sources)
        h = s['hd'].get('infrastructure')
        assert h is not None,'不是接入後正式收據'
        records.append({'receipt':str(path.relative_to(args.receipts)),'steps':s['steps'],
            'theme':s['hd_enabled'],'origin':s.get('map_origin'),'infrastructure':h})
    assert records and any(r['infrastructure']['painted'] for r in records)
    scrolls = []
    if (args.receipts/'infrastructure-gui.json').exists():
        for axis in ['X','Y']:
            pairs = []
            for phase in ['before','after']:
                s,frame,_,pixels,_ = audit_bundle(args.receipts/f'infrastructure-scroll-{axis}-{phase}-capture.zip',sources)
                origin = s['map_origin']
                assert s['hd_enabled'] and origin['Valid']
                tiles = {}
                for row in range(15):
                    for col in range(29):
                        source = cell(frame,5+col*9,34+row*9)
                        if source not in references()[0]:continue
                        x,y = 20+col*36,136+row*36
                        tile = b''.join(pixels[((y+dy)*1280+x)*4:((y+dy)*1280+x+36)*4] for dy in range(36))
                        tiles[(origin['X']+col,origin['Y']+row)] = (source,tile)
                pairs.append((s,tiles))
            a,b = pairs
            assert b[0]['map_origin'][axis]-a[0]['map_origin'][axis]==2
            common = sorted(set(a[1])&set(b[1]))
            assert common,'正常捲動沒有可比的同世界高清格'
            for world in common:
                assert a[1][world]==b[1][world],(axis,world,'相同世界來源或高清像素漂移')
            scrolls.append({'axis':axis,'same_world_tiles':len(common),'sources_and_full_hd_tiles_equal':True,
                'world_cells':common})
    assert not args.out.exists()
    args.out.write_text(json.dumps({'samples':records,'independent_rom_geometry_shader':True,
        'whole_tiles_and_all_fallback_equal':True,'normal_scroll_comparisons':scrolls,
        'scope':'正式 GUI 呈現與同世界捲動；完整生命周期與原版狀態另核對'},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'receipts':len(records),'painted_receipts':sum(bool(r['infrastructure']['painted']) for r in records),
        'normal_scroll_axes':len(scrolls)},ensure_ascii=False))


if __name__=='__main__':
    main()
