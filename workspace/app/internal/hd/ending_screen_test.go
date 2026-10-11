package hd

import (
	"bytes"
	"encoding/binary"
	"image"
	"image/draw"
	"os"
	"path/filepath"
	"testing"
)

func endingFixture(t *testing.T) ([]byte, string, []byte, *Renderer) {
	t.Helper()
	dir, orig := os.Getenv("TAIPEI_HD_MATERIALS"), os.Getenv("TAIPEI_HD_ORIGINAL")
	if dir == "" || orig == "" {
		t.Skip("需要 028 本機固定底圖及唯讀 ROM")
	}
	rom, err := os.ReadFile(filepath.Join(orig, "RS201.ROM"))
	if err != nil {
		t.Fatal(err)
	}
	offset := int(binary.LittleEndian.Uint32(rom[18+23*16:]))
	size := int(binary.LittleEndian.Uint16(rom[22+23*16:]))
	data := rom[offset : offset+size]
	if offset != 193647 || size != 17587 || !bytes.Equal(data[:4], []byte{64, 1, 200, 0}) {
		t.Fatal("已見底圖成員定位不符")
	}
	var px []byte
	for at := 4; at < len(data); {
		value := data[at]
		at++
		count := 1
		if value == 0 {
			if at+2 > len(data) {
				t.Fatal("原版底圖串流不完整")
			}
			value, count = data[at], int(data[at+1])
			at += 2
		}
		px = append(px, bytes.Repeat([]byte{value}, count)...)
	}
	if len(px) != 64000 || digest(px) != "0040b4374f37464862ae2f89da5bc897ddb7f53d539edd597cf8b2b6ff784ebd" {
		t.Fatal("原版底圖完整來源不符")
	}
	r := New(rom, dir)
	if r.ending == nil || r.ending.reason != "" || r.ending.frame == nil {
		t.Fatal("正式固定政績素材未載入", r.ending)
	}
	return rom, dir, px, r
}

func endingReference(t *testing.T, dir string) *image.RGBA {
	t.Helper()
	im := infrastructurePNG(t, filepath.Join(dir, "ending-scene-v1", "presentation.png"))
	ref := image.NewRGBA(im.Bounds())
	draw.Draw(ref, ref.Bounds(), im, image.Point{}, draw.Src)
	return ref
}

func TestEndingScreenCompleteAndRoundtrip(t *testing.T) {
	_, dir, px, r := endingFixture(t)
	ref := endingReference(t, dir)
	before := append([]byte(nil), px...)
	pal := r.ending.palette
	checkHD := func() {
		t.Helper()
		got, stats := r.Render(px, pal, 19, true, true, Origin{})
		if !bytes.Equal(got.Pix, ref.Pix) || stats.EndingScreen != "achievement-base" || stats.Reason != "matched-ending-screen" {
			t.Fatal("完整原型像素或家族不符", stats)
		}
		if stats.Painted != 0 || stats.PowerFacility.Painted != 0 || stats.Infrastructure.Painted != 0 || stats.Panel != "" || stats.FileDialog != "" {
			t.Fatal("完整底圖混入其他家族", stats)
		}
	}
	checkHD()
	got, stats := r.Render(px, pal, 19, true, false, Origin{})
	if stats.EndingScreen != "" || stats.EndingReason != "original" || bytes.Equal(got.Pix, ref.Pix) {
		t.Fatal("F12 原版回退不符", stats)
	}
	native := append([]byte(nil), got.Pix...)
	checkHD()
	for _, c := range []struct {
		mode    int
		blocked bool
		reason  string
	}{{3, true, "video-mode"}, {19, false, "ending-unverified-phase"}} {
		got, stats := r.Render(px, pal, c.mode, c.blocked, true, Origin{})
		if !bytes.Equal(got.Pix, native) || stats.EndingScreen != "" || stats.Reason != c.reason {
			t.Fatal("模式或未確認相位殘留 HD", stats)
		}
		checkHD()
	}
	for _, at := range []int{0, 3*320 + 128, 70*320 + 48, 120*320 + 160, 63999} {
		changed := append([]byte(nil), px...)
		changed[at] ^= 128
		original, _ := r.Render(changed, pal, 19, true, false, Origin{})
		want := append([]byte(nil), original.Pix...)
		got, stats := r.Render(changed, pal, 19, true, true, Origin{})
		if stats.EndingScreen != "" || !bytes.Equal(got.Pix, want) {
			t.Fatal("來源單點失配未完整回退", at, stats)
		}
		checkHD()
	}
	if !bytes.Equal(before, px) {
		t.Fatal("呈現器寫入原版來源")
	}
}

func TestEndingScreenUsedPalette(t *testing.T) {
	_, dir, px, r := endingFixture(t)
	ref := endingReference(t, dir)
	checked := 0
	for index, used := range r.ending.used {
		if !used {
			continue
		}
		pal := r.ending.palette
		pal[index][0] ^= 1
		original, _ := r.Render(px, pal, 19, true, false, Origin{})
		want := append([]byte(nil), original.Pix...)
		got, stats := r.Render(px, pal, 19, true, true, Origin{})
		if stats.EndingScreen != "" || stats.EndingReason != "ending-palette-mismatch" || !bytes.Equal(got.Pix, want) {
			t.Fatal("已用色盤失配未完整回退", index, stats)
		}
		checked++
	}
	if checked != 23 || r.ending.used[0] {
		t.Fatal("已用色盤形態不符", checked)
	}
	pal := r.ending.palette
	pal[0] = [3]byte{1, 2, 3}
	got, stats := r.Render(px, pal, 19, true, true, Origin{})
	if !bytes.Equal(got.Pix, ref.Pix) || stats.EndingScreen != "achievement-base" {
		t.Fatal("未用色盤誤拒絕", stats)
	}
}

func TestEndingScreenActualLoaderFaults(t *testing.T) {
	rom, dir, px, r := endingFixture(t)
	pal := r.ending.palette
	original, _ := r.Render(px, pal, 19, true, false, Origin{})
	want := append([]byte(nil), original.Pix...)
	for _, c := range []struct {
		name, path, reason string
		change             []byte
	}{
		{"missing-manifest", "ending-scene-ready-v1/manifest.json", "ending-manifest-mismatch", nil},
		{"corrupt-manifest", "ending-scene-ready-v1/manifest.json", "ending-manifest-mismatch", []byte("{")},
		{"wrong-stage", "ending-scene-ready-v1/manifest.json", "ending-manifest-mismatch", []byte(`{"schema":1,"stage":"all-achievements"}`)},
		{"missing-image", "ending-scene-ready-v1/screen.png", "ending-image-mismatch", nil},
		{"corrupt-image", "ending-scene-ready-v1/screen.png", "ending-image-mismatch", []byte("PNG")},
		{"missing-font", "fonts/NotoSansCJKtc-Regular.otf", "ending-font-mismatch", nil},
		{"corrupt-font", "fonts/NotoSansCJKtc-Regular.otf", "ending-font-mismatch", []byte("OTF")},
		{"missing-license", "fonts/LICENSE", "ending-license-mismatch", nil},
		{"corrupt-license", "fonts/LICENSE", "ending-license-mismatch", []byte("OFL")},
	} {
		t.Run(c.name, func(t *testing.T) {
			root := t.TempDir()
			for _, subdir := range []string{"fonts", "ending-scene-ready-v1"} {
				if err := os.Mkdir(filepath.Join(root, subdir), 0700); err != nil {
					t.Fatal(err)
				}
			}
			for _, name := range []string{"fonts/NotoSansCJKtc-Regular.otf", "fonts/LICENSE", "ending-scene-ready-v1/manifest.json", "ending-scene-ready-v1/screen.png"} {
				if name == c.path {
					if c.change != nil {
						if err := os.WriteFile(filepath.Join(root, name), c.change, 0600); err != nil {
							t.Fatal(err)
						}
					}
					continue
				}
				if err := os.Symlink(filepath.Join(dir, name), filepath.Join(root, name)); err != nil {
					t.Fatal(err)
				}
			}
			r.ending = loadEndingScreen(rom, root)
			got, stats := r.Render(px, pal, 19, true, true, Origin{})
			if r.ending.reason != c.reason || stats.EndingReason != c.reason || stats.EndingScreen != "" || !bytes.Equal(got.Pix, want) {
				t.Fatal("實際載入故障未完整回退", stats)
			}
		})
	}
	if u := loadEndingScreen([]byte("wrong ROM"), dir); u.reason != "ending-rom-mismatch" {
		t.Fatal("錯 ROM 未拒絕", u.reason)
	}
}

func TestEndingScreenOtherFamilyIsolation(t *testing.T) {
	_, _, _, r := endingFixture(t)
	s, px := load(t, "city-map")
	before, stats := r.Render(px, s.Palette, s.Mode, s.Blocked, true, Origin{X: 12, Y: 12, Valid: true})
	want := append([]byte(nil), before.Pix...)
	if stats.Reason != "matched-city" {
		t.Fatal("城市正對照未命中", stats)
	}
	r.ending = &endingScreen{reason: "ending-image-mismatch"}
	got, stats := r.Render(px, s.Palette, s.Mode, s.Blocked, true, Origin{X: 12, Y: 12, Valid: true})
	if !bytes.Equal(got.Pix, want) || stats.EndingScreen != "" || stats.Reason != "matched-city" {
		t.Fatal("政績素材故障影響城市家族", stats)
	}
}
