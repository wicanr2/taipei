package hd

import (
	"bytes"
	"image"
	"image/draw"
	"os"
	"path/filepath"
	"testing"
)

func civicFixture(t *testing.T) ([]byte, string, *civicFacilitySet) {
	t.Helper()
	dir, orig := os.Getenv("TAIPEI_HD_MATERIALS"), os.Getenv("TAIPEI_HD_ORIGINAL")
	if dir == "" || orig == "" {
		t.Skip("需要 035 素材與唯讀 ROM")
	}
	rom, err := os.ReadFile(filepath.Join(orig, "RS201.ROM"))
	if err != nil {
		t.Fatal(err)
	}
	u := loadCivicFacilities(rom, dir)
	if len(u.tiles) != 32 || len(u.atlases) != 1 || u.reason != "" {
		t.Fatal("32 張固定來源未載入", u.reason)
	}
	return rom, dir, u
}

func TestCivicFacilitiesAtlasAndFallback(t *testing.T) {
	rom, dir, u := civicFixture(t)
	dst := image.NewRGBA(image.Rect(0, 0, 1280, 800))
	for i := range dst.Pix {
		dst.Pix[i] = byte(i % 251)
	}
	want := image.NewRGBA(dst.Bounds())
	copy(want.Pix, dst.Pix)
	ref := infrastructurePNG(t, filepath.Join(dir, "civic-facilities-prototype-v1", "37.png"))
	draw.Draw(want, image.Rect(20, 172, 308, 316), ref, image.Point{}, draw.Src)
	for source, tile := range u.tiles {
		if u.paint(dst, tile, u.palette, tile.col, tile.row+1) != "matched-civic-facility" {
			t.Fatal(tile.image)
		}
		for i := range source {
			bad := source
			bad[i] ^= 128
			if u.tiles[bad] != nil {
				t.Fatal("失配來源仍辨識", tile.image, i)
			}
		}
		pal := u.palette
		pal[tile.used[0]][0] ^= 1
		before := append([]byte(nil), dst.Pix...)
		if u.paint(dst, tile, pal, 0, 0) != "palette-mismatch" || !bytes.Equal(dst.Pix, before) {
			t.Fatal("失配色盤覆繪")
		}
	}
	if !bytes.Equal(dst.Pix, want.Pix) {
		t.Fatal("兩完整建物或區外像素不符")
	}
	for _, name := range []string{"manifest.json", "37.png"} {
		for _, fault := range []string{"missing", "corrupt"} {
			t.Run(name+"-"+fault, func(t *testing.T) {
				root := t.TempDir()
				target := filepath.Join(root, "civic-facilities-ready-v1")
				if err := os.Mkdir(target, 0700); err != nil {
					t.Fatal(err)
				}
				for _, f := range []string{"manifest.json", "37.png"} {
					data, err := os.ReadFile(filepath.Join(dir, "civic-facilities-ready-v1", f))
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
				broken := loadCivicFacilities(rom, root)
				for _, tile := range broken.tiles {
					before := append([]byte(nil), dst.Pix...)
					if broken.paint(dst, tile, broken.palette, 0, 0) == "matched-civic-facility" || !bytes.Equal(before, dst.Pix) {
						t.Fatal("失配資源仍覆繪")
					}
				}
			})
		}
	}
}

func TestCivicFacilitiesNormalSourceIsolation(t *testing.T) {
	rom, dir, _ := civicFixture(t)
	root := os.Getenv("TAIPEI_CIVIC_RECEIPTS")
	if root == "" {
		t.Fatal("需要兩份正常施工來源")
	}
	for _, sample := range []fileSample{
		{Receipt: filepath.Join(root, "civic-police-native-r1", "police-complete-capture.zip"), ReceiptSHA: "7b1668234598de52e7677c63f1ee1ebd988564401dcf3ea9f6586fa969f9a265"},
		{Receipt: filepath.Join(root, "civic-fire-native-r1", "fire-complete-capture.zip"), ReceiptSHA: "3066c6e5c2b32647fafaf4da7c0d6e1b6a9efb9edae511720837eb3e279970a7"},
	} {
		s, px := readFileSample(t, sample)
		before := append([]byte(nil), px...)
		pal := s.Palette
		r := New(rom, dir)
		shown, stats := r.Render(px, pal, s.Mode, false, true, Origin{X: 12, Y: 12, Valid: true})
		if stats.CivicFacilities.Painted != 16 || stats.CivicFacilities.Fallback != 0 || !bytes.Equal(px, before) || pal != s.Palette {
			t.Fatal("正常施工未覆繪或改寫原版", stats.CivicFacilities)
		}
		fallback := New(rom, dir)
		fallback.civicFacilities.reason = "test-disabled"
		baseline, _ := fallback.Render(px, pal, s.Mode, false, true, Origin{X: 12, Y: 12, Valid: true})
		for y := 0; y < 800; y++ {
			for x := 0; x < 1280; x++ {
				if x >= 812 && x < 956 && y >= 244 && y < 388 {
					continue
				}
				if shown.RGBAAt(x, y) != baseline.RGBAAt(x, y) {
					t.Fatal("改寫建物區外", x, y)
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
			if stats.CivicFacilities.Matched != 0 {
				t.Fatal("原版、阻塞或原點未知仍覆繪")
			}
		}
	}
}
