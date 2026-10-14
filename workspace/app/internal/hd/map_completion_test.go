package hd

import (
	"bytes"
	"image"
	"os"
	"path/filepath"
	"testing"

	"github.com/wicanr2/taipei/preview/internal/i18n"
)

func mapFixture(t *testing.T) ([]byte, string, *Renderer) {
	t.Helper()
	dir, orig := os.Getenv("TAIPEI_HD_MATERIALS"), os.Getenv("TAIPEI_HD_ORIGINAL")
	if dir == "" || orig == "" {
		t.Skip("需要038固定素材與唯讀原版")
	}
	rom, err := os.ReadFile(filepath.Join(orig, "RS201.ROM"))
	if err != nil {
		t.Fatal(err)
	}
	r := New(rom, dir)
	if r.mapComplex.reason != "" || len(r.mapComplex.tiles) != 207 || len(r.mapComplex.atlases) != 13 || r.mapZonesBase.reason != "" || len(r.mapZonesBase.tiles) != 36 || len(r.mapDetail.tiles) != 58 {
		t.Fatal("完整301種來源未載入")
	}
	if r.SetLanguage(i18n.Bundled(), "zh-Hant") != "matched-menu" || r.mapZones.reason != "" {
		t.Fatal("區域字型未就緒", r.mapZones.reason)
	}
	return rom, dir, r
}

func mapFrame(frame []byte, tiles []*publicFacilityTile, col, row int) []byte {
	px := append([]byte(nil), frame...)
	for _, tile := range tiles {
		for dy := 0; dy < 9; dy++ {
			at := (34+(row+tile.row)*9+dy)*320 + 5 + (col+tile.col)*9
			copy(px[at:], tile.source[dy*9:(dy+1)*9])
		}
	}
	return px
}

func TestMapCompletionWholeAtlasesAndFiveLanguageInk(t *testing.T) {
	_, _, r := mapFixture(t)
	s, frame := readFileSample(t, fileSample{Receipt: "/workspace/runs/gui-public-r2/pause-capture.zip", ReceiptSHA: "dd43f31d567124b6f3e006c9f553caca3a2a0a28d3f5002ebe3d1da8f93a38c6"})
	origin := Origin{12, 12, true}
	col, row := 12, 3
	check := func(u *publicFacilitySet, id string, zones bool) {
		px := mapFrame(frame, u.facilities[id], col, row)
		before := append([]byte(nil), px...)
		shown, st := r.Render(px, s.Palette, s.Mode, false, true, origin)
		actual := localeClone(shown)
		got := st.MapCompletion.Complex
		if zones {
			got = st.MapCompletion.Zones
		}
		if got.Facilities[id] != 16 || got.Fallback != 0 || !bytes.Equal(px, before) {
			t.Fatal(id, got)
		}
		atlas := u.atlases[id]
		left, top := 20+col*36, 136+row*36
		for y := 0; y < 144; y++ {
			for x := 0; x < 144; x++ {
				if actual.RGBAAt(left+x, top+y) != atlas.RGBAAt(x, y) {
					t.Fatal("整圖切格失配", id, x, y)
				}
			}
		}
		old := u.reason
		u.reason = "test-disabled"
		base, _ := r.Render(px, s.Palette, s.Mode, false, true, origin)
		u.reason = old
		for y := 0; y < 800; y++ {
			for x := 0; x < 1280; x++ {
				if x >= left && x < left+144 && y >= top && y < top+144 {
					continue
				}
				if actual.RGBAAt(x, y) != base.RGBAAt(x, y) {
					t.Fatal("區外像素變動", id, x, y)
				}
			}
		}
	}
	for _, id := range mapComplexIDs {
		check(r.mapComplex, id, false)
	}
	for _, lang := range i18n.Languages {
		if why := r.SetLanguage(i18n.Bundled(), lang); why != "matched-menu" {
			t.Fatal(lang, why)
		}
		for id, atlas := range r.mapZones.atlases {
			base := r.mapZonesBase.atlases[id]
			ink := 0
			for y := 0; y < 144; y++ {
				for x := 0; x < 144; x++ {
					if atlas.RGBAAt(x, y) != base.RGBAAt(x, y) {
						if !image.Pt(x, y).In(image.Rect(44, 44, 108, 100)) {
							t.Fatal("Noto墨跡越界", lang, id, x, y)
						}
						ink++
					}
				}
			}
			if ink < 40 {
				t.Fatal("區域缺字", lang, id, ink)
			}
			check(r.mapZones, id, true)
		}
	}
	shared := mapFrame(frame, r.mapComplex.facilities["m34-b08"], col, row)
	for source, variants := range r.mapComplex.variants {
		if len(variants) < 2 {
			continue
		}
		tile := variants[0]
		shared[(34+row*9)*320+5+col*9] ^= 128
		if got, why := resolveMapTile(r.mapComplex, source, shared, col+tile.col, row+tile.row); got != nil || why != "neighbors-mismatch" {
			t.Fatal("同源鄰格負對照無效", why)
		}
	}
	for _, gate := range []struct {
		blocked, enabled bool
		origin           Origin
	}{{true, true, origin}, {false, false, origin}, {false, true, Origin{}}} {
		_, st := r.Render(shared, s.Palette, s.Mode, gate.blocked, gate.enabled, gate.origin)
		if st.MapCompletion.Complex.Matched+st.MapCompletion.Zones.Matched+st.MapCompletion.Detail.Matched != 0 {
			t.Fatal("模態／切換／原點閘門失效")
		}
	}
	t.Log("13整圖、15語言區域墨跡／整圖、全部區外、同源反例與場景閘門通過；合成診斷，非正常GUI")
}

func TestMapCompletionSourcePaletteAndResourceFaults(t *testing.T) {
	rom, dir, r := mapFixture(t)
	dst := image.NewRGBA(image.Rect(0, 0, 1280, 800))
	mutated := 0
	registered := func(s [81]byte) bool {
		return r.mapComplex.tiles[s] != nil || r.mapZones.tiles[s] != nil || r.mapDetail.tiles[s] != nil
	}
	for _, u := range []*publicFacilitySet{r.mapComplex, r.mapZones} {
		for source, tile := range u.tiles {
			for i := range source {
				bad := source
				bad[i] ^= 128
				if registered(bad) {
					t.Fatal("來源變異仍辨識", tile.id, i)
				}
				mutated++
			}
			pal := u.palette
			pal[tile.used[0]][0] ^= 1
			before := append([]byte(nil), dst.Pix...)
			if u.paint(dst, tile, pal, 0, 0) != "palette-mismatch" || !bytes.Equal(dst.Pix, before) {
				t.Fatal("已用色盤失配仍繪製", tile.id)
			}
			if r.infrastructure.tiles[source] != nil || r.cityBuildings.tiles[source] != nil || r.publicFacilities.tiles[source] != nil || r.transportFacilities.tiles[source] != nil || r.civicFacilities.tiles[source] != nil || r.nuclearFacility.tiles[source] != nil || r.powerFacility.tiles[source] != nil {
				t.Fatal("與舊家族衝突", tile.id)
			}
		}
	}
	for source, tile := range r.mapDetail.tiles {
		for i := range source {
			bad := source
			bad[i] ^= 128
			if registered(bad) {
				t.Fatal("小格變異仍辨識", tile.image, i)
			}
			mutated++
		}
		pal := r.mapDetail.palette
		pal[tile.used[0]][0] ^= 1
		before := append([]byte(nil), dst.Pix...)
		if r.mapDetail.paint(dst, tile, pal, 0, 0, Origin{12, 12, true}) != "palette-mismatch" || !bytes.Equal(dst.Pix, before) {
			t.Fatal("小格色盤失配仍繪製", tile.image)
		}
	}
	if mutated != 301*81 {
		t.Fatal(mutated)
	}
	for _, sub := range []string{"complex", "zones", "detail"} {
		entries, err := os.ReadDir(filepath.Join(dir, "map-completion-ready-v1", sub))
		if err != nil {
			t.Fatal(err)
		}
		resource := ""
		for _, e := range entries {
			if e.Name() != "manifest.json" {
				resource = e.Name()
				break
			}
		}
		for _, name := range []string{"manifest.json", resource} {
			for _, fault := range []string{"missing", "corrupt"} {
				root := t.TempDir()
				target := filepath.Join(root, "map-completion-ready-v1", sub)
				if err := os.MkdirAll(target, 0700); err != nil {
					t.Fatal(err)
				}
				for _, e := range entries {
					data, err := os.ReadFile(filepath.Join(dir, "map-completion-ready-v1", sub, e.Name()))
					if err != nil {
						t.Fatal(err)
					}
					if e.Name() == name {
						if fault == "missing" {
							continue
						}
						data[len(data)/2] ^= 1
					}
					if err := os.WriteFile(filepath.Join(target, e.Name()), data, 0600); err != nil {
						t.Fatal(err)
					}
				}
				if sub == "detail" {
					bad := loadMapDetail(rom, root)
					if name == "manifest.json" {
						if len(bad.tiles) != 0 {
							t.Fatal("損壞小格manifest被接受")
						}
						continue
					}
					failed := 0
					for _, tile := range bad.tiles {
						if tile.reason != "" {
							failed++
						}
					}
					if failed != 1 {
						t.Fatal("幾何故障未隔離", name, failed)
					}
				} else {
					bad := loadMapAtlases(rom, root, sub == "zones")
					if name == "manifest.json" {
						if bad.reason == "" {
							t.Fatal("損壞atlas manifest被接受")
						}
					} else {
						want := 13
						if sub == "zones" {
							want = 3
						}
						if bad.reason != "" || len(bad.atlases) != want-1 {
							t.Fatal("單圖故障未隔離", name, bad.reason, len(bad.atlases))
						}
					}
				}
			}
		}
	}
	t.Log("24381來源變異、301色盤反例、家族衝突及12個實際資源故障通過")
}
