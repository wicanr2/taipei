package hd

import (
	"bytes"
	"image"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestActualFooterSourcesAndFallback(t *testing.T) {
	receipts := os.Getenv("TAIPEI_CHROME_RECEIPTS")
	if receipts == "" {
		t.Skip("需要正常十四工具來源")
	}
	t.Setenv("TAIPEI_HD_RECEIPTS", receipts)
	rom, e := os.ReadFile(filepath.Join(os.Getenv("TAIPEI_HD_ORIGINAL"), "RS201.ROM"))
	if e != nil {
		t.Fatal(e)
	}
	dir := os.Getenv("TAIPEI_HD_MATERIALS")
	u := loadCityFooter(rom, dir)
	if !u.ready {
		t.Fatal("固定資源未載入")
	}
	paths, e := filepath.Glob(filepath.Join(receipts, "*-capture.zip"))
	if e != nil {
		t.Fatal(e)
	}
	costs := map[string]bool{}
	matched := 0
	for _, p := range paths {
		s, px := load(t, strings.TrimSuffix(filepath.Base(p), "-capture.zip"))
		before := append([]byte(nil), px...)
		for part := 0; part < 2; part++ {
			v, ok := u.decode(px, part)
			if !ok {
				continue
			}
			matched++
			if part == 0 {
				costs[strings.TrimSpace(v[0])] = true
			}
			// 任一背景／墨跡破壞不得仍匹配原欄位，另一欄保持可辨識。
			bad := append([]byte(nil), px...)
			r := footerRects[part]
			bad[r.Min.Y*320+r.Min.X] ^= 128
			if _, ok := u.decode(bad, part); ok {
				t.Fatal("破壞完整來源仍匹配", p, part)
			}
		}
		if !bytes.Equal(before, px) {
			t.Fatal("來源遭改寫")
		}
		_ = s
	}
	if matched < 100 || len(costs) < 10 {
		t.Fatal("正常來源不足", matched, len(costs))
	}
	s, px := load(t, "confirm-13")
	dst := image.NewRGBA(image.Rect(0, 0, 1280, 800))
	mask, values, _ := u.paint(dst, px, s.Palette)
	if mask != 3 || strings.TrimSpace(values[0]) != "100000" {
		t.Fatal(mask, values)
	}
	pal := s.Palette
	pal[32][0] ^= 1
	mask, _, _ = u.paint(dst, px, pal)
	if mask != 2 {
		t.Fatal("紅色失配未只回退左欄", mask)
	}
	pal = s.Palette
	pal[1][0] ^= 1
	mask, _, _ = u.paint(dst, px, pal)
	if mask != 1 {
		t.Fatal("藍色失配未只回退右欄", mask)
	}
	bad := append([]byte(nil), px...)
	bad[177*320+19] ^= 128
	mask, _, _ = u.paint(dst, bad, s.Palette)
	if mask != 2 {
		t.Fatal("左欄來源失配未獨立回退", mask)
	}
	for _, missing := range []string{"fonts/NotoSansCJKtc-Regular.otf", "fonts/LICENSE", "footer-v1/glyphs.png", "footer-v1/manifest.json", "city-chrome-v1/frame.png"} {
		temp := t.TempDir()
		for _, name := range []string{"fonts/NotoSansCJKtc-Regular.otf", "fonts/LICENSE", "footer-v1/glyphs.png", "footer-v1/manifest.json", "city-chrome-v1/frame.png"} {
			if name == missing {
				continue
			}
			raw, e := os.ReadFile(filepath.Join(dir, name))
			if e != nil {
				t.Fatal(e)
			}
			if e = os.MkdirAll(filepath.Dir(filepath.Join(temp, name)), 0755); e != nil {
				t.Fatal(e)
			}
			if e = os.WriteFile(filepath.Join(temp, name), raw, 0600); e != nil {
				t.Fatal(e)
			}
		}
		absent := loadCityFooter(rom, temp)
		sentinel := bytes.Repeat([]byte{17}, len(dst.Pix))
		copy(dst.Pix, sentinel)
		mask, _, _ = absent.paint(dst, px, s.Palette)
		if mask != 0 || !bytes.Equal(dst.Pix, sentinel) {
			t.Fatal("缺素材未完整回退", missing)
		}
		if e = os.MkdirAll(filepath.Dir(filepath.Join(temp, missing)), 0755); e != nil {
			t.Fatal(e)
		}
		if e = os.WriteFile(filepath.Join(temp, missing), []byte("wrong"), 0600); e != nil {
			t.Fatal(e)
		}
		if loadCityFooter(rom, temp).ready {
			t.Fatal("竄改固定資源仍可用", missing)
		}
	}
	// 六位縮短為兩位時仍從固定背景重繪，不保留舊墨跡。
	_, long := load(t, "confirm-13")
	_, short := load(t, "confirm-00")
	fresh := image.NewRGBA(dst.Bounds())
	u.paint(dst, long, s.Palette)
	u.paint(dst, short, s.Palette)
	u.paint(fresh, short, s.Palette)
	for _, r := range footerRects {
		for y := r.Min.Y * 4; y < r.Max.Y*4; y++ {
			a := dst.PixOffset(r.Min.X*4, y)
			n := r.Dx() * 16
			if !bytes.Equal(dst.Pix[a:a+n], fresh.Pix[a:a+n]) {
				t.Fatal("縮短數字殘影")
			}
		}
	}
}
