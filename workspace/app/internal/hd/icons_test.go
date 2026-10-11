package hd

import (
	"bytes"
	"image"
	"image/png"
	"os"
	"path/filepath"
	"testing"
)

func TestActualToolIconsAndSelectedBorders(t *testing.T) {
	s, px := load(t, "city-map")
	dir := os.Getenv("TAIPEI_HD_MATERIALS")
	rom, err := os.ReadFile(filepath.Join(os.Getenv("TAIPEI_HD_ORIGINAL"), "RS201.ROM"))
	if err != nil {
		t.Fatal(err)
	}
	raw, err := os.ReadFile(filepath.Join(dir, "city-icons-b-v1.png"))
	if err != nil || digest(raw) != iconsSHA {
		t.Fatal("固定工具圖示失配", err)
	}
	atlas, err := png.Decode(bytes.NewReader(raw))
	if err != nil {
		t.Fatal(err)
	}
	r := New(rom, dir)
	r.chrome = nil // 此測試單獨驗圖示；新外框由 chrome_test 驗完整正常來源。
	origin := Origin{X: 12, Y: 12, Valid: true}
	for _, name := range []string{"city-map", "power-tool", "power-confirm", "uncover-power"} {
		state, frame := load(t, name)
		before := append([]byte(nil), frame...)
		got, stats := r.Render(frame, state.Palette, state.Mode, state.Blocked, true, origin)
		if stats.UIIcons != 14 || stats.UIIconMask != 0x3fff {
			t.Fatal("十四圖示未完整接入", name, stats)
		}
		for i := 0; i < 14; i++ {
			rect := iconRect(i)
			for y := rect.Min.Y - 4; y < rect.Max.Y+4; y++ {
				for x := rect.Min.X - 4; x < rect.Max.X+4; x++ {
					if image.Pt(x, y).In(rect) {
						rr, gg, bb, aa := atlas.At((i%4)*80+x-rect.Min.X, (i/4)*80+y-rect.Min.Y).RGBA()
						gr, g, b, a := got.At(x, y).RGBA()
						if rr != gr || gg != g || bb != b || aa != a {
							t.Fatal("圖示像素不同於固定 atlas", name, i, x, y)
						}
					} else {
						c := state.Palette[frame[(y/4)*320+x/4]]
						at := (y*1280 + x) * 4
						if !bytes.Equal(got.Pix[at:at+4], []byte{c[0], c[1], c[2], 255}) {
							t.Fatal("原版選取外框被改寫", name, i, x, y)
						}
					}
				}
			}
		}
		if !bytes.Equal(before, frame) {
			t.Fatal("原版色號遭改寫", name)
		}
	}
	assertNative := func(got *image.RGBA, frame []byte, palette [256][3]uint8, i int) {
		t.Helper()
		rect := iconRect(i)
		for y := rect.Min.Y; y < rect.Max.Y; y++ {
			for x := rect.Min.X; x < rect.Max.X; x++ {
				c := palette[frame[(y/4)*320+x/4]]
				at := (y*1280 + x) * 4
				if !bytes.Equal(got.Pix[at:at+4], []byte{c[0], c[1], c[2], 255}) {
					t.Fatal("圖示回退保留殘影", i, x, y)
				}
			}
		}
	}
	corrupt := append([]byte(nil), px...)
	corrupt[5*320+274] ^= 1
	got, stats := r.Render(corrupt, s.Palette, s.Mode, false, true, origin)
	if stats.UIIcons != 13 || stats.UIIconMask != 0x3ffe {
		t.Fatal("單圖來源失配未獨立回退", stats)
	}
	assertNative(got, corrupt, s.Palette, 0)
	wrong := s.Palette
	wrong[28][0] ^= 1
	got, stats = r.Render(px, wrong, s.Mode, false, true, origin)
	if stats.UIIcons != 0 || stats.UIReason != "icons-palette-mismatch" || stats.FontLabels != 6 || stats.Painted != 433 {
		t.Fatal("工具色盤未獨立回退", stats)
	}
	assertNative(got, px, wrong, 0)
	for _, broken := range []bool{false, true} {
		tmp := t.TempDir()
		if broken {
			if err := os.WriteFile(filepath.Join(tmp, "city-icons-b-v1.png"), []byte("broken atlas"), 0600); err != nil {
				t.Fatal(err)
			}
		}
		r.icons = loadToolIcons(rom, tmp)
		got, stats = r.Render(px, s.Palette, s.Mode, false, true, origin)
		if stats.UIIcons != 0 || stats.FontLabels != 6 || stats.Painted != 433 {
			t.Fatal("工具素材未獨立回退", stats)
		}
		for i := 0; i < 14; i++ {
			assertNative(got, px, s.Palette, i)
		}
	}
	r.icons = loadToolIcons(rom, dir)
	got, stats = r.Render(px, s.Palette, s.Mode, false, false, origin)
	if stats.UIIcons != 0 || stats.UIIconMask != 0 {
		t.Fatal("切回原版仍有圖示", stats)
	}
	for i := 0; i < 14; i++ {
		assertNative(got, px, s.Palette, i)
	}
	_, stats = r.Render(px, s.Palette, s.Mode, false, true, origin)
	if stats.UIIcons != 14 {
		t.Fatal("返回 HD 未恢復圖示", stats)
	}
}
