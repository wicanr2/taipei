package hd

import (
	"bytes"
	"image"
	"image/draw"
	"image/png"
	"os"
	"path/filepath"
	"testing"
)

func TestActualNotoMenuMatchesSelectedReference(t *testing.T) {
	s, px := load(t, "city-map")
	dir := os.Getenv("TAIPEI_HD_MATERIALS")
	rom, err := os.ReadFile(filepath.Join(os.Getenv("TAIPEI_HD_ORIGINAL"), "RS201.ROM"))
	if err != nil {
		t.Fatal(err)
	}
	reference, err := os.ReadFile(filepath.Join(dir, "font-comparison", "noto-font.png"))
	if err != nil || digest(reference) != "feefbf252a77ab01322c72654a2c6d8b7cb42118494949604f194c20d4f331da" {
		t.Fatal("已展示字型參考圖失配", err)
	}
	im, err := png.Decode(bytes.NewReader(reference))
	if err != nil || im.Bounds() != image.Rect(0, 0, 1280, 800) {
		t.Fatal("字型參考圖格式不符", err)
	}
	want := image.NewRGBA(im.Bounds())
	draw.Draw(want, want.Bounds(), im, image.Point{}, draw.Src)
	r := New(rom, dir)
	r.chrome = nil // 六標題原有測試單獨覆字；框架內的 Noto 與缺字型另驗。
	origin := Origin{X: 12, Y: 12, Valid: true}
	before := append([]byte(nil), px...)
	got, stats := r.Render(px, s.Palette, s.Mode, s.Blocked, true, origin)
	if stats.FontLabels != 6 || stats.FontReason != "matched-menu" {
		t.Fatal("六個 Noto 標題未接入", stats)
	}
	for i, text := range menuLabels {
		rect := menuRect(i)
		ink := image.Rectangle{}
		for y := rect.Min.Y; y < rect.Max.Y; y++ {
			at := (y*1280 + rect.Min.X) * 4
			end := at + rect.Dx()*4
			if !bytes.Equal(got.Pix[at:end], want.Pix[at:end]) {
				t.Fatal("動態標題不同於已展示原型", text, y)
			}
			for x := rect.Min.X; x < rect.Max.X; x++ {
				if got.RGBAAt(x, y).R != 170 {
					ink = ink.Union(image.Rect(x, y, x+1, y+1))
				}
			}
		}
		if ink.Empty() || !ink.In(rect) {
			t.Fatal("實際墨跡不在安全矩形", text, ink, rect)
		}
	}
	if !bytes.Equal(before, px) {
		t.Fatal("Noto 覆繪改寫了原版色號")
	}

	assertNativeLabels := func(got *image.RGBA, pal [256][3]uint8) {
		t.Helper()
		for i := range menuLabels {
			rect := menuRect(i)
			for y := rect.Min.Y; y < rect.Max.Y; y++ {
				for x := rect.Min.X; x < rect.Max.X; x++ {
					c := pal[px[(y/4)*320+x/4]]
					at := (y*1280 + x) * 4
					if !bytes.Equal(got.Pix[at:at+4], []byte{c[0], c[1], c[2], 255}) {
						t.Fatal("字型回退保留了覆繪殘影", x, y)
					}
				}
			}
		}
	}
	valid := r.menu
	for _, reason := range []string{"font-unavailable", "font-mismatch", "font-license-mismatch"} {
		t.Run(reason, func(t *testing.T) {
			tmp := t.TempDir()
			if reason == "font-mismatch" {
				if err := os.WriteFile(filepath.Join(tmp, "NotoSansCJKtc-Regular.otf"), []byte("broken font"), 0600); err != nil {
					t.Fatal(err)
				}
			}
			if reason == "font-license-mismatch" {
				if err := os.Symlink(filepath.Join(dir, "fonts", "NotoSansCJKtc-Regular.otf"), filepath.Join(tmp, "NotoSansCJKtc-Regular.otf")); err != nil {
					t.Fatal(err)
				}
				if err := os.WriteFile(filepath.Join(tmp, "LICENSE"), []byte("broken license"), 0600); err != nil {
					t.Fatal(err)
				}
			}
			r.menu = loadMenuFont(tmp)
			got, stats := r.Render(px, s.Palette, s.Mode, false, true, origin)
			if stats.FontLabels != 0 || stats.FontReason != reason || stats.Painted != 433 {
				t.Fatal("字型失配未獨立回退", stats)
			}
			assertNativeLabels(got, s.Palette)
		})
	}
	r.menu = valid
	wrong := s.Palette
	wrong[15][0] ^= 1
	got, stats = r.Render(px, wrong, s.Mode, false, true, origin)
	if stats.FontLabels != 0 || stats.FontReason != "font-palette-mismatch" || stats.Painted != 433 {
		t.Fatal("文字色盤失配未獨立回退", stats)
	}
	assertNativeLabels(got, wrong)
	got, stats = r.Render(px, s.Palette, s.Mode, false, false, origin)
	if stats.FontLabels != 0 {
		t.Fatal("原版主題仍覆繪字型", stats)
	}
	assertNativeLabels(got, s.Palette)
	_, stats = r.Render(px, s.Palette, s.Mode, false, true, origin)
	if stats.FontLabels != 6 {
		t.Fatal("恢復 HD 後未重畫文字", stats)
	}
}
