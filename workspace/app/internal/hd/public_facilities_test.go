package hd

import (
	"bytes"
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
	if len(u.tiles) != 32 || len(u.atlases) != 2 || u.reason != "" {
		t.Fatal("32 張來源未載入", u.reason)
	}
	return rom, dir, u
}

func TestPublicFacilitiesAssemblyAndFallback(t *testing.T) {
	rom, dir, u := publicFixture(t)
	dst := image.NewRGBA(image.Rect(0, 0, 1280, 800))
	for i := range dst.Pix {
		dst.Pix[i] = byte(i % 251)
	}
	want := image.NewRGBA(dst.Bounds())
	copy(want.Pix, dst.Pix)
	for n, id := range []string{"waste", "sewage"} {
		ref := infrastructurePNG(t, filepath.Join(dir, "public-facilities-prototype-v1", id+".png"))
		draw.Draw(want, image.Rect(20+n*144, 172, 164+n*144, 316), ref, image.Point{}, draw.Src)
	}
	for source, tile := range u.tiles {
		col := tile.col
		if tile.id == "sewage" {
			col += 4
		}
		if u.paint(dst, tile, u.palette, col, tile.row+1) != "matched-public-facility" {
			t.Fatal(tile.id, tile.image)
		}
		for i := range source {
			bad := source
			bad[i] ^= 128
			if u.tiles[bad] != nil {
				t.Fatal("失配來源仍辨識", tile.id, tile.image, i)
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
		t.Fatal("兩完整設施或區外像素不符")
	}
	for _, name := range []string{"manifest.json", "waste.png", "sewage.png"} {
		for _, fault := range []string{"missing", "corrupt"} {
			t.Run(name+"-"+fault, func(t *testing.T) {
				root := t.TempDir()
				target := filepath.Join(root, "public-facilities-ready-v1")
				if err := os.Mkdir(target, 0700); err != nil {
					t.Fatal(err)
				}
				for _, f := range []string{"manifest.json", "waste.png", "sewage.png"} {
					data, err := os.ReadFile(filepath.Join(dir, "public-facilities-ready-v1", f))
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
				for _, tile := range broken.tiles {
					before := append([]byte(nil), dst.Pix...)
					matched := broken.paint(dst, tile, broken.palette, 0, 0) == "matched-public-facility"
					shouldPaint := name != "manifest.json" && name != tile.id+".png"
					if matched != shouldPaint || (!shouldPaint && !bytes.Equal(before, dst.Pix)) {
						t.Fatal("素材回退或設施隔離失效", tile.id)
					}
				}
			})
		}
	}
}

func TestPublicFacilitiesNormalSources(t *testing.T) {
	rom, dir, _ := publicFixture(t)
	root := os.Getenv("TAIPEI_PUBLIC_RECEIPTS")
	if root == "" {
		t.Fatal("需要兩份正常施工來源")
	}
	for _, sample := range []fileSample{
		{Receipt: filepath.Join(root, "public-native-r1", "waste-complete-capture.zip"), ReceiptSHA: "fff767a9311d274877d0a2482014a196e3775c986780d8341641990a8cef625a"},
		{Receipt: filepath.Join(root, "public-native-r5", "sewage-complete-capture.zip"), ReceiptSHA: "a0019433d39b9304550678cd3285c465fb0042a4997ea973f6232e94ce518928"},
	} {
		s, px := readFileSample(t, sample)
		before := append([]byte(nil), px...)
		pal := s.Palette
		r := New(rom, dir)
		shown, stats := r.Render(px, pal, s.Mode, false, true, Origin{X: 12, Y: 12, Valid: true})
		if stats.PublicFacilities.Painted != 16 || stats.PublicFacilities.Fallback != 0 || !bytes.Equal(px, before) || pal != s.Palette {
			t.Fatal("正常施工未覆繪或改寫原版", stats.PublicFacilities)
		}
		fallback := New(rom, dir)
		fallback.publicFacilities.reason = "test-disabled"
		baseline, _ := fallback.Render(px, pal, s.Mode, false, true, Origin{X: 12, Y: 12, Valid: true})
		for y := 0; y < 800; y++ {
			for x := 0; x < 1280; x++ {
				if x >= 812 && x < 956 && y >= 244 && y < 388 {
					continue
				}
				if shown.RGBAAt(x, y) != baseline.RGBAAt(x, y) {
					t.Fatal("改寫設施區外", x, y)
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
				t.Fatal("原版、阻塞或原點未知仍覆繪")
			}
		}
	}
}
