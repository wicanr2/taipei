package hd

import (
	"bytes"
	"encoding/json"
	"image"
	"image/draw"
	"os"
	"path/filepath"
	"testing"
)

func nuclearFixture(t *testing.T) ([]byte, string, *publicFacilitySet, fileSample) {
	t.Helper()
	dir, orig, root := os.Getenv("TAIPEI_HD_MATERIALS"), os.Getenv("TAIPEI_HD_ORIGINAL"), os.Getenv("TAIPEI_NUCLEAR_RECEIPTS")
	if dir == "" || orig == "" || root == "" {
		t.Skip("需要 027 核能素材、原版與正常 GUI 收據")
	}
	rom, err := os.ReadFile(filepath.Join(orig, "RS201.ROM"))
	if err != nil {
		t.Fatal(err)
	}
	u := loadNuclearFacility(rom, dir)
	if u.reason != "" || len(u.tiles) != 35 || len(u.atlases) != 1 || len(u.facilities["nuclear"]) != 36 {
		t.Fatal("核能 36 格／35 種來源未載入", u.reason)
	}
	raw, err := os.ReadFile(filepath.Join(dir, "nuclear-v1", "nuclear", "source.json"))
	if err != nil || digest(raw) != "274c1057a1aa545dcda0104c6958ba6b4a23da04295c0ac3cf7fcff70fa8f0f6" {
		t.Fatal("正常核能來源證明失配", err)
	}
	var proof struct {
		SHA string `json:"receipt_sha256"`
	}
	if err := json.Unmarshal(raw, &proof); err != nil {
		t.Fatal(err)
	}
	return rom, dir, u, fileSample{Receipt: filepath.Join(root, "existing-nuclear-capture.zip"), ReceiptSHA: proof.SHA}
}

func TestNuclearFacilityNormalSourceAndIsolation(t *testing.T) {
	rom, dir, u, sample := nuclearFixture(t)
	s, px := readFileSample(t, sample)
	before := append([]byte(nil), px...)
	r := New(rom, dir)
	shown, stats := r.Render(px, s.Palette, s.Mode, false, true, Origin{X: 52, Y: 40, Valid: true})
	if stats.NuclearFacility.Painted != 36 || stats.NuclearFacility.Fallback != 0 || !bytes.Equal(px, before) {
		t.Fatal("正常來源未完整呈現或原版變動", stats.NuclearFacility)
	}
	im := infrastructurePNG(t, filepath.Join(dir, "nuclear-prototype-v1", "nuclear.png"))
	ref := image.NewRGBA(im.Bounds())
	draw.Draw(ref, ref.Bounds(), im, im.Bounds().Min, draw.Src)
	for y := 0; y < 216; y++ {
		for x := 0; x < 216; x++ {
			if shown.RGBAAt(308+x, 280+y) != ref.RGBAAt(x, y) {
				t.Fatal("完整核能與固定候選不符", x, y)
			}
		}
	}
	fallback := New(rom, dir)
	fallback.nuclearFacility.reason = "test-disabled"
	baseline, _ := fallback.Render(px, s.Palette, s.Mode, false, true, Origin{X: 52, Y: 40, Valid: true})
	for y := 0; y < 800; y++ {
		for x := 0; x < 1280; x++ {
			if x >= 308 && x < 524 && y >= 280 && y < 496 {
				continue
			}
			if shown.RGBAAt(x, y) != baseline.RGBAAt(x, y) {
				t.Fatal("核能區外變動", x, y)
			}
		}
	}
	for _, gate := range []struct {
		blocked, enabled bool
		origin           Origin
	}{
		{false, false, Origin{X: 52, Y: 40, Valid: true}}, {true, true, Origin{X: 52, Y: 40, Valid: true}}, {false, true, Origin{}},
	} {
		_, st := r.Render(px, s.Palette, s.Mode, gate.blocked, gate.enabled, gate.origin)
		if st.NuclearFacility.Matched != 0 {
			t.Fatal("核能場景未隔離", st.NuclearFacility)
		}
	}
	for source := range u.tiles {
		for _, family := range []map[[81]byte]*publicFacilityTile{r.publicFacilities.tiles} {
			if family[source] != nil {
				t.Fatal("核能與公共設施來源衝突")
			}
		}
		if r.powerFacility.tiles[source] != nil || r.civicFacilities.tiles[source] != nil || r.cityBuildings.tiles[source] != nil || r.infrastructure.tiles[source] != nil {
			t.Fatal("核能與既有家族來源衝突")
		}
	}
}

func TestNuclearFacilitySharedAndCropped(t *testing.T) {
	_, _, u, sample := nuclearFixture(t)
	_, frame := readFileSample(t, sample)
	var source [81]byte
	for raw, variants := range u.variants {
		if len(variants) > 1 {
			source = raw
		}
	}
	if len(u.variants[source]) != 2 {
		t.Fatal("同源數量不符")
	}
	for _, col := range []int{2, 4} {
		tile, reason := u.resolve(source, frame, 8+col, 4)
		if tile == nil || tile.col != col || tile.row != 0 || reason != "" {
			t.Fatal("原位同源定位失敗", col, reason)
		}
	}
	put := func(dst []byte, col, row int, raw [81]byte) {
		for y := 0; y < 9; y++ {
			copy(dst[(34+row*9+y)*320+5+col*9:], raw[y*9:(y+1)*9])
		}
	}
	cropped := make([]byte, 64000)
	for _, tile := range u.facilities["nuclear"] {
		if tile.col >= 3 {
			put(cropped, tile.col-3, tile.row, tile.source)
		}
	}
	tile, reason := u.resolve(source, cropped, 1, 0)
	if tile == nil || tile.col != 4 || reason != "" {
		t.Fatal("裁切同源定位失敗", reason)
	}
	missing := make([]byte, 64000)
	put(missing, 0, 0, source)
	if tile, _ := u.resolve(source, missing, 0, 0); tile != nil {
		t.Fatal("缺少完整鄰圖仍覆繪")
	}
	damaged := append([]byte(nil), frame...)
	damaged[71*320+78] ^= 128
	for _, col := range []int{10, 12} {
		if tile, _ := u.resolve(source, damaged, col, 4); tile != nil {
			t.Fatal("鄰圖失配仍覆繪")
		}
	}
}

func TestNuclearFacilityPaletteSourcesAndResources(t *testing.T) {
	rom, dir, u, _ := nuclearFixture(t)
	dst := image.NewRGBA(image.Rect(0, 0, 1280, 800))
	tile := u.facilities["nuclear"][0]
	for source := range u.tiles {
		for i := range source {
			bad := source
			bad[i] ^= 128
			if u.tiles[bad] != nil {
				t.Fatal("失配來源仍辨識", i)
			}
		}
	}
	for _, color := range tile.used {
		pal := u.palette
		pal[color][0] ^= 1
		before := append([]byte(nil), dst.Pix...)
		if u.paint(dst, tile, pal, 0, 0) != "palette-mismatch" || !bytes.Equal(dst.Pix, before) {
			t.Fatal("失配色盤覆繪")
		}
	}
	used := [256]bool{}
	for source := range u.tiles {
		for _, c := range source {
			used[c] = true
		}
	}
	pal := u.palette
	unused := 0
	for used[unused] {
		unused++
	}
	pal[unused][0] ^= 1
	if u.paint(dst, tile, pal, 0, 0) != "matched-nuclear-facility" {
		t.Fatal("未用色盤誤拒絕")
	}
	ref := image.NewRGBA(dst.Bounds())
	draw.Draw(ref, image.Rect(20, 136, 56, 172), u.atlases["nuclear"], image.Point{}, draw.Src)
	if !bytes.Equal(dst.Pix, ref.Pix) {
		t.Fatal("單格繪製或區外不符")
	}
	for _, name := range []string{"manifest.json", "nuclear.png"} {
		for _, fault := range []string{"missing", "corrupt"} {
			root := t.TempDir()
			target := filepath.Join(root, "nuclear-ready-v1")
			if err := os.Mkdir(target, 0700); err != nil {
				t.Fatal(err)
			}
			for _, n := range []string{"manifest.json", "nuclear.png"} {
				data, err := os.ReadFile(filepath.Join(dir, "nuclear-ready-v1", n))
				if err != nil {
					t.Fatal(err)
				}
				if n == name {
					if fault == "missing" {
						continue
					}
					data[len(data)/2] ^= 1
				}
				if err := os.WriteFile(filepath.Join(target, n), data, 0600); err != nil {
					t.Fatal(err)
				}
			}
			broken := loadNuclearFacility(rom, root)
			before := append([]byte(nil), dst.Pix...)
			if broken.paint(dst, tile, u.palette, 0, 0) == "matched-nuclear-facility" || !bytes.Equal(dst.Pix, before) {
				t.Fatal("真實素材故障未回退", name, fault)
			}
		}
	}
}
