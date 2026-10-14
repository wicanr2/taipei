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

func publicFixture(t *testing.T) ([]byte, string, *publicFacilitySet) {
	t.Helper()
	dir, orig := os.Getenv("TAIPEI_HD_MATERIALS"), os.Getenv("TAIPEI_HD_ORIGINAL")
	if dir == "" || orig == "" {
		t.Skip("需要 036 素材與唯讀 ROM")
	}
	rom, err := os.ReadFile(filepath.Join(orig, "RS201.ROM"))
	if err != nil {
		t.Fatal(err)
	}
	u := loadPublicFacilities(rom, dir)
	if len(u.tiles) != 391 || len(u.atlases) != 12 || u.reason != "" {
		t.Fatal("391 種來源／十二項設施未載入", u.reason)
	}
	return rom, dir, u
}

func TestPublicFacilitiesAssemblyAndFallback(t *testing.T) {
	rom, dir, u := publicFixture(t)
	for id, tiles := range u.facilities {
		dst := image.NewRGBA(image.Rect(0, 0, 1280, 800))
		for i := range dst.Pix {
			dst.Pix[i] = byte(i % 251)
		}
		want := image.NewRGBA(dst.Bounds())
		copy(want.Pix, dst.Pix)
		ref := infrastructurePNG(t, filepath.Join(dir, "public-facilities-prototype-v2", id+".png"))
		draw.Draw(want, image.Rect(92, 208, 92+ref.Bounds().Dx(), 208+ref.Bounds().Dy()), ref, image.Point{}, draw.Src)
		for _, tile := range tiles {
			if u.paint(dst, tile, u.palette, tile.col+2, tile.row+2) != "matched-public-facility" {
				t.Fatal(id, tile.col, tile.row)
			}
		}
		if !bytes.Equal(dst.Pix, want.Pix) {
			t.Fatal("完整設施或區外不符", id)
		}
		pal := u.palette
		pal[tiles[0].used[0]][0] ^= 1
		before := append([]byte(nil), dst.Pix...)
		if u.paint(dst, tiles[0], pal, 0, 0) != "palette-mismatch" || !bytes.Equal(before, dst.Pix) {
			t.Fatal("失配色盤覆繪", id)
		}
	}
	used := [256]bool{}
	for source := range u.tiles {
		for _, color := range source {
			used[color] = true
		}
	}
	invalid := 0
	for invalid < 256 && used[invalid] {
		invalid++
	}
	if invalid == 256 {
		t.Fatal("固定測例需未用色號")
	}
	for source := range u.tiles {
		bad := source
		bad[40] = byte(invalid)
		if u.tiles[bad] != nil {
			t.Fatal("失配來源仍辨識")
		}
	}
	names := []string{"manifest.json"}
	for id := range u.facilities {
		names = append(names, id+".png")
	}
	for _, name := range names {
		for _, fault := range []string{"missing", "corrupt"} {
			t.Run(name+"-"+fault, func(t *testing.T) {
				root := t.TempDir()
				target := filepath.Join(root, "public-facilities-ready-v2")
				if err := os.Mkdir(target, 0700); err != nil {
					t.Fatal(err)
				}
				for _, f := range names {
					data, err := os.ReadFile(filepath.Join(dir, "public-facilities-ready-v2", f))
					if err != nil {
						t.Fatal(err)
					}
					if f == name {
						if fault == "missing" {
							continue
						}
						data[len(data)/2] ^= 1
					}
					if err := os.WriteFile(filepath.Join(target, f), data, 0600); err != nil {
						t.Fatal(err)
					}
				}
				broken := loadPublicFacilities(rom, root)
				dst := image.NewRGBA(image.Rect(0, 0, 1280, 800))
				for id, tiles := range u.facilities {
					before := append([]byte(nil), dst.Pix...)
					matched := broken.paint(dst, tiles[0], broken.palette, 0, 0) == "matched-public-facility"
					shouldPaint := name != "manifest.json" && name != id+".png"
					if matched != shouldPaint || (!shouldPaint && !bytes.Equal(before, dst.Pix)) {
						t.Fatal("素材故障未隔離", id)
					}
				}
			})
		}
	}
}

func TestPublicFacilityArchiveBoundaries(t *testing.T) {
	rom, _, _ := publicFixture(t)
	for _, v := range []struct {
		member, index, pixel int
		sha                  string
	}{
		{40, 0, 587115, "b050228d1ab1c21cc0f993646cf67e3007f9468768e27d47b1ead5bf12c69361"},
		{40, 179, 602330, "fe9c33e425063fb6df2e91851cc0b33f7faeaa0efa8d00c7ecc062a180d1b4c6"},
		{41, 0, 602777, "e417d2979b57d0cdc635192e6f378855ccaa26df23b54d85cf0f5c47687740b6"},
		{41, 179, 617992, "d2661c97205d69e6f082a0f051c3534f2a2dc45ba01665e80a89cd88fd9e1cc0"},
	} {
		pixels, ok := publicSource(rom, v.member, v.index, v.pixel)
		if !ok || digest(pixels[:]) != v.sha {
			t.Fatal("實際 archive 首末格不符", v.member, v.index)
		}
		if _, ok := publicSource(rom, v.member, v.index, v.pixel+1); ok {
			t.Fatal("失配偏移被接受")
		}
	}
	for _, v := range [][2]int{{-1, 0}, {69, 0}, {40, -1}, {40, 180}} {
		if _, ok := publicSource(rom, v[0], v[1], 587115); ok {
			t.Fatal("archive 越界被接受", v)
		}
	}
}

func publicProof(t *testing.T, dir, root, id string) (fileSample, [2]int) {
	t.Helper()
	raw, err := os.ReadFile(filepath.Join(dir, "public-facilities-prototype-v2", "manifest.json"))
	if err != nil {
		t.Fatal(err)
	}
	if digest(raw) != "8a90556b3065244377ae9cfbc414389b76fb71150c618623a06a05116caf5428" {
		t.Fatal("固定原型失配")
	}
	var manifest struct {
		Facilities []struct {
			ID       string
			Size     [2]int
			ProofSHA string `json:"source_proof_sha256"`
		}
	}
	if err := json.Unmarshal(raw, &manifest); err != nil {
		t.Fatal(err)
	}
	for _, f := range manifest.Facilities {
		if f.ID == id {
			raw, err := os.ReadFile(filepath.Join(dir, "public-facilities-v1", id, "source.json"))
			if err != nil {
				t.Fatal(err)
			}
			if digest(raw) != f.ProofSHA {
				t.Fatal("來源證明失配", id)
			}
			var proof struct {
				Receipt string
				SHA     string `json:"receipt_sha256"`
			}
			if err := json.Unmarshal(raw, &proof); err != nil {
				t.Fatal(err)
			}
			return fileSample{Receipt: filepath.Join(root, filepath.Base(filepath.Dir(proof.Receipt)), filepath.Base(proof.Receipt)), ReceiptSHA: proof.SHA}, f.Size
		}
	}
	t.Fatal("未知來源", id)
	return fileSample{}, [2]int{}
}

func TestPublicFacilitiesNormalSources(t *testing.T) {
	rom, dir, u := publicFixture(t)
	root := os.Getenv("TAIPEI_PUBLIC_RECEIPTS")
	if root == "" {
		t.Fatal("需要正常施工來源")
	}
	for id := range u.facilities {
		sample, size := publicProof(t, dir, root, id)
		s, px := readFileSample(t, sample)
		before := append([]byte(nil), px...)
		pal := s.Palette
		r := New(rom, dir)
		shown, stats := r.Render(px, pal, s.Mode, false, true, Origin{X: 12, Y: 12, Valid: true})
		if stats.PublicFacilities.Painted != size[0]*size[1] || stats.PublicFacilities.Fallback != 0 || !bytes.Equal(before, px) || pal != s.Palette {
			t.Fatal("正常施工未完整覆繪或原版變動", id, stats.PublicFacilities)
		}
		fallback := New(rom, dir)
		fallback.publicFacilities.reason = "test-disabled"
		baseline, _ := fallback.Render(px, pal, s.Mode, false, true, Origin{X: 12, Y: 12, Valid: true})
		for y := 0; y < 800; y++ {
			for x := 0; x < 1280; x++ {
				if x >= 812 && x < 812+size[0]*36 && y >= 244 && y < 244+size[1]*36 {
					continue
				}
				if shown.RGBAAt(x, y) != baseline.RGBAAt(x, y) {
					t.Fatal("設施區外變動", id, x, y)
				}
			}
		}
		for _, gate := range []struct {
			blocked, enabled bool
			origin           Origin
		}{
			{false, false, Origin{X: 12, Y: 12, Valid: true}}, {true, true, Origin{X: 12, Y: 12, Valid: true}}, {false, true, Origin{}},
		} {
			_, stats := r.Render(px, pal, s.Mode, gate.blocked, gate.enabled, gate.origin)
			if stats.PublicFacilities.Matched != 0 {
				t.Fatal("場景未隔離", id)
			}
		}
	}
}

func TestPublicFacilitiesSharedSourceContext(t *testing.T) {
	_, dir, u := publicFixture(t)
	root := os.Getenv("TAIPEI_PUBLIC_RECEIPTS")
	sample, _ := publicProof(t, dir, root, "stadium")
	_, frame := readFileSample(t, sample)
	var source [81]byte
	for raw, variants := range u.variants {
		if len(variants) > 1 {
			source = raw
		}
	}
	if digest(source[:]) != "c7d8532244e8a14fdac66ea1fe533c46c6b474c66dce4ba20873aafab738c5be" || len(u.variants[source]) != 2 {
		t.Fatal("共用來源不符")
	}
	for _, col := range []int{3, 4} {
		tile, reason := u.resolve(source, frame, 22+col, 3)
		if tile == nil || tile.id != "stadium" || tile.col != col || tile.row != 0 || reason != "" {
			t.Fatal("正常共用格定位失敗", col, reason)
		}
	}
	put := func(dst []byte, col, row int, source [81]byte) {
		for y := 0; y < 9; y++ {
			copy(dst[(34+row*9+y)*320+5+col*9:], source[y*9:(y+1)*9])
		}
	}
	cropped := make([]byte, 64000)
	for _, tile := range u.facilities["stadium"] {
		if tile.col >= 3 {
			put(cropped, tile.col-3, tile.row, tile.source)
		}
	}
	for col := 0; col < 2; col++ {
		tile, reason := u.resolve(source, cropped, col, 0)
		if tile == nil || tile.col != col+3 || reason != "" {
			t.Fatal("裁切共用格定位失敗", col, reason)
		}
	}
	missing := make([]byte, 64000)
	put(missing, 0, 0, source)
	if tile, _ := u.resolve(source, missing, 0, 0); tile != nil {
		t.Fatal("沒有可用鄰圖仍覆繪")
	}
	damaged := append([]byte(nil), frame...)
	damaged[(34+3*9+4)*320+5+24*9+4] ^= 128
	for _, col := range []int{25, 26} {
		if tile, _ := u.resolve(source, damaged, col, 3); tile != nil {
			t.Fatal("錯誤鄰圖仍覆繪")
		}
	}
}
