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

func powerFacilityFixture(t *testing.T) ([]byte, string, *powerFacilitySet) {
	t.Helper()
	dir, orig := os.Getenv("TAIPEI_HD_MATERIALS"), os.Getenv("TAIPEI_HD_ORIGINAL")
	if dir == "" || orig == "" {
		t.Skip("需要 027 本機固定插畫與唯讀 ROM")
	}
	rom, err := os.ReadFile(filepath.Join(orig, "RS201.ROM"))
	if err != nil {
		t.Fatal(err)
	}
	u := loadPowerFacilities(rom, dir)
	if len(u.tiles) != 36 || u.reason != "" || u.atlas == nil {
		t.Fatal("火力 36 格固定素材未載入", len(u.tiles), u.reason)
	}
	return rom, dir, u
}

func TestPowerFacilityCompleteAndPartialAtlas(t *testing.T) {
	_, dir, u := powerFacilityFixture(t)
	// 直接採 READY 前已獨立重組的完整原型，避免用呈現器生成期望值。
	ref := infrastructurePNG(t, filepath.Join(dir, "power-facility-v2", "thermal-hd.png"))
	dst := image.NewRGBA(image.Rect(0, 0, 1280, 800))
	for i := range dst.Pix {
		dst.Pix[i] = byte(i % 251)
	}
	want := image.NewRGBA(dst.Bounds())
	copy(want.Pix, dst.Pix)
	draw.Draw(want, image.Rect(128, 208, 344, 424), ref, image.Point{}, draw.Src)
	negative := 0
	for source, tile := range u.tiles {
		if why := u.paint(dst, tile, u.palette, tile.col+3, tile.row+2); why != "matched-power-facility" {
			t.Fatal(tile.image, why)
		}
		for at := range source {
			changed := source
			changed[at] ^= 128
			if u.tiles[changed] != nil {
				t.Fatal("來源失配仍辨識", tile.image, at)
			}
			negative++
		}
	}
	if negative != 2916 || !bytes.Equal(dst.Pix, want.Pix) {
		t.Fatal("完整 6×6 原型、全部區外或逐像素反例失敗", negative)
	}
	for _, tile := range u.tiles {
		// 移至另一個視窗格，代表完整複合建物僅部分可見。
		partial := image.NewRGBA(dst.Bounds())
		want := image.NewRGBA(dst.Bounds())
		draw.Draw(want, image.Rect(20, 136, 56, 172), ref, image.Pt(tile.col*36, tile.row*36), draw.Src)
		if u.paint(partial, tile, u.palette, 0, 0) != "matched-power-facility" || !bytes.Equal(partial.Pix, want.Pix) {
			t.Fatal("單格／區外與完整原型不符", tile.image)
		}
	}
	t.Log("36 格完整／部分重組、全部區外及 2916 項來源失配通過")
}

func TestPowerFacilityPalette(t *testing.T) {
	_, _, u := powerFacilityFixture(t)
	dst := image.NewRGBA(image.Rect(0, 0, 1280, 800))
	for source, tile := range u.tiles {
		var used [256]bool
		for _, index := range source {
			used[index] = true
		}
		for _, index := range tile.used {
			pal := u.palette
			pal[index][0] ^= 1
			before := append([]byte(nil), dst.Pix...)
			if u.paint(dst, tile, pal, 0, 0) != "palette-mismatch" || !bytes.Equal(before, dst.Pix) {
				t.Fatal("已用色盤失配未原位回退", tile.image, index)
			}
		}
		pal := u.palette
		for index, present := range used {
			if !present {
				pal[index][0] ^= 1
			}
		}
		if u.paint(dst, tile, pal, 0, 0) != "matched-power-facility" {
			t.Fatal("未用色盤誤拒絕", tile.image)
		}
	}
}

func TestPowerFacilityActualLoaderFaults(t *testing.T) {
	rom, dir, _ := powerFacilityFixture(t)
	root := filepath.Join(dir, "power-facility-ready-v1")
	manifest, err := os.ReadFile(filepath.Join(root, "manifest.json"))
	if err != nil {
		t.Fatal(err)
	}
	atlas, err := os.ReadFile(filepath.Join(root, "thermal.png"))
	if err != nil {
		t.Fatal(err)
	}
	for _, fault := range []string{"missing-manifest", "invalid-manifest", "wrong-stage", "missing-atlas", "corrupt-atlas"} {
		t.Run(fault, func(t *testing.T) {
			dir := t.TempDir()
			root := filepath.Join(dir, "power-facility-ready-v1")
			if err := os.Mkdir(root, 0700); err != nil {
				t.Fatal(err)
			}
			m, a := append([]byte(nil), manifest...), append([]byte(nil), atlas...)
			if fault == "invalid-manifest" {
				m[0] ^= 1
			}
			if fault == "wrong-stage" {
				var fields map[string]any
				if json.Unmarshal(m, &fields) != nil {
					t.Fatal("固定 manifest 解析失敗")
				}
				fields["stage"] = "DRAFT"
				m, _ = json.Marshal(fields)
			}
			if fault == "corrupt-atlas" {
				a[len(a)/2] ^= 1
			}
			if fault != "missing-manifest" {
				if err := os.WriteFile(filepath.Join(root, "manifest.json"), m, 0600); err != nil {
					t.Fatal(err)
				}
			}
			if fault != "missing-atlas" {
				if err := os.WriteFile(filepath.Join(root, "thermal.png"), a, 0600); err != nil {
					t.Fatal(err)
				}
			}
			u := loadPowerFacilities(rom, dir)
			if len(u.tiles) != 36 || u.atlas != nil || u.reason == "" {
				t.Fatal("實際資源故障未保留已知來源及拒絕原因", len(u.tiles), u.reason)
			}
			dst := image.NewRGBA(image.Rect(0, 0, 1280, 800))
			for _, tile := range u.tiles {
				if u.paint(dst, tile, u.palette, 0, 0) == "matched-power-facility" {
					t.Fatal("資源故障仍覆繪", tile.image)
				}
			}
			if !bytes.Equal(dst.Pix, make([]byte, len(dst.Pix))) {
				t.Fatal("資源故障改動原位或區外")
			}
		})
	}
}
