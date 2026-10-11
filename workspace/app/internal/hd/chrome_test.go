package hd

import (
	"bytes"
	"image"
	"image/png"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestActualChromeAllToolStatesAndFallbacks(t *testing.T) {
	receipts := os.Getenv("TAIPEI_CHROME_RECEIPTS")
	if receipts == "" {
		t.Skip("需要正常十四工具收據")
	}
	t.Setenv("TAIPEI_HD_RECEIPTS", receipts)
	rom, e := os.ReadFile(filepath.Join(os.Getenv("TAIPEI_HD_ORIGINAL"), "RS201.ROM"))
	if e != nil {
		t.Fatal(e)
	}
	dir := os.Getenv("TAIPEI_HD_MATERIALS")
	r := New(rom, dir)
	origin := Origin{X: 12, Y: 12, Valid: true}
	paths, e := filepath.Glob(filepath.Join(receipts, "*-capture.zip"))
	if e != nil {
		t.Fatal(e)
	}
	states := map[[2]int]bool{}
	cityModals := map[string]bool{}
	toolModals := map[string]bool{}
	for _, path := range paths {
		name := strings.TrimSuffix(filepath.Base(path), "-capture.zip")
		s, px := load(t, name)
		before := append([]byte(nil), px...)
		native, _ := r.Render(px, s.Palette, s.Mode, s.Blocked, false, origin)
		base := append([]byte(nil), native.Pix...)
		got, st := r.Render(px, s.Palette, s.Mode, s.Blocked, true, origin)
		if st.Reason == "matched-city" {
			if st.ChromeParts != 6 || st.ChromeMask != 63 || st.ChromeRings != 14 || st.ChromeRingMask != 0x3fff || st.UIIcons != 14 {
				t.Fatal(name, st)
			}
			for _, p := range r.chrome.parts {
				for _, at := range p.points {
					x, y := at%320*4, at/320*4
					for yy := y; yy < y+4; yy++ {
						for xx := x; xx < x+4; xx++ {
							a, b, c, d := got.At(xx, yy).RGBA()
							aa, bb, cc, dd := r.chrome.frame.At(xx, yy).RGBA()
							if a != aa || b != bb || c != cc || d != dd {
								t.Fatal("框架參考失配", name, xx, yy)
							}
						}
					}
				}
			}
			for i := 0; i < 14; i++ {
				x, y := 273+23*(i%2), 4+24*(i/2)
				value := int(px[y*320+x])
				v := map[int]int{15: 0, 32: 1, 186: 2}[value]
				states[[2]int{i, value}] = true
				for yy := 0; yy < 88; yy++ {
					for xx := 0; xx < 88; xx++ {
						if xx >= 4 && xx < 84 && yy >= 4 && yy < 84 {
							continue
						}
						a, b, c, d := got.At(x*4+xx, y*4+yy).RGBA()
						aa, bb, cc, dd := r.chrome.rings.At(v*88+xx, yy).RGBA()
						if a != aa || b != bb || c != cc || d != dd {
							t.Fatal("外框參考失配", name, i, xx, yy)
						}
					}
				}
			}
		} else if s.Blocked && strings.HasPrefix(st.Panel, "tool-") {
			// 021 已接入五種完整面板；其像素及區外由工具面板測試驗證。
			toolModals[st.Panel] = true
			if st.ChromeParts != 0 || st.ChromeRings != 0 {
				t.Fatal("工具面板仍疊加城市框架", name, st)
			}
		} else if s.Blocked && strings.HasPrefix(st.Panel, "city-f") {
			// 022 已接入六功能面板，像素及區外由城市面板測試驗證。
			cityModals[st.Panel] = true
			if st.ChromeParts != 0 || st.ChromeRings != 0 {
				t.Fatal("城市面板仍疊加城市框架", name, st)
			}
		} else if s.Blocked && st.Panel == "" && st.Dialog == "" {
			if st.ChromeParts != 0 || st.ChromeRings != 0 || !bytes.Equal(base, got.Pix) {
				t.Fatal("未知視窗未整幀回退", name, st)
			}
		}
		if !bytes.Equal(px, before) {
			t.Fatal("色號遭改寫", name)
		}
	}
	if len(states) != 42 || !cityModals["city-f2"] || len(toolModals) != 5 {
		t.Fatal("缺完整正常來源", len(states), cityModals, len(toolModals))
	}
	s, px := load(t, "city-map")
	bad := append([]byte(nil), px...)
	bad[34*320] ^= 1
	got, st := r.Render(bad, s.Palette, s.Mode, false, true, origin)
	if st.ChromeMask != 61 || st.ChromeRings != 14 {
		t.Fatal("單部分來源未獨立回退", st)
	}
	if c := got.RGBAAt(0, 136); c.R != s.Palette[bad[34*320]][0] {
		t.Fatal("未知來源仍覆繪")
	}
	pal := s.Palette
	pal[162][0] ^= 1
	_, st = r.Render(px, pal, s.Mode, false, true, origin)
	if st.ChromeMask&16 != 0 {
		t.Fatal("底板色盤失配仍覆繪", st)
	}
	for _, name := range []string{"city-chrome-v1/frame.png", "city-chrome-v1/rings.png"} {
		temp := t.TempDir()
		if e := os.MkdirAll(filepath.Join(temp, "city-chrome-v1"), 0755); e != nil {
			t.Fatal(e)
		}
		for _, n := range []string{"city-chrome-v1/frame.png", "city-chrome-v1/rings.png"} {
			raw, e := os.ReadFile(filepath.Join(dir, n))
			if e != nil {
				t.Fatal(e)
			}
			if e = os.WriteFile(filepath.Join(temp, n), raw, 0600); e != nil {
				t.Fatal(e)
			}
		}
		u := loadCityChrome(rom, temp)
		if u.fontOK {
			t.Fatal("缺字型仍接受頂框")
		}
		dst := image.NewRGBA(image.Rect(0, 0, 1280, 800))
		_, mask, _, rings, _ := u.paint(dst, px, s.Palette)
		if mask != 62 || rings != 0x3fff {
			t.Fatal("缺字型未只回退頂框", mask, rings)
		}
		for _, corrupt := range []bool{false, true} {
			if corrupt {
				if e := os.WriteFile(filepath.Join(temp, name), []byte("broken image"), 0600); e != nil {
					t.Fatal(e)
				}
			} else {
				if e := os.Remove(filepath.Join(temp, name)); e != nil {
					t.Fatal(e)
				}
			}
			u = loadCityChrome(rom, temp)
			_, mask, _, rings, _ = u.paint(dst, px, s.Palette)
			if strings.Contains(name, "frame") && mask != 0 || strings.Contains(name, "rings") && rings != 0 {
				t.Fatal("缺檔或失配素材仍被接受", name, mask, rings)
			}
		}
	}
	bad = append([]byte(nil), px...)
	bad[4*320+273] ^= 1
	_, st = r.Render(bad, s.Palette, s.Mode, false, true, origin)
	if st.ChromeMask != 63 || st.ChromeRingMask != 0x3ffe || st.UIIcons != 14 {
		t.Fatal("未知外框來源未獨立回退", st)
	}
	for _, name := range []string{"NotoSansCJKtc-Regular.otf", "LICENSE"} {
		temp := t.TempDir()
		if e = os.MkdirAll(filepath.Join(temp, "city-chrome-v1"), 0755); e != nil {
			t.Fatal(e)
		}
		if e = os.MkdirAll(filepath.Join(temp, "fonts"), 0755); e != nil {
			t.Fatal(e)
		}
		for _, n := range []string{"city-chrome-v1/frame.png", "city-chrome-v1/rings.png", "fonts/NotoSansCJKtc-Regular.otf", "fonts/LICENSE"} {
			raw, e := os.ReadFile(filepath.Join(dir, n))
			if e != nil {
				t.Fatal(e)
			}
			if e = os.WriteFile(filepath.Join(temp, n), raw, 0600); e != nil {
				t.Fatal(e)
			}
		}
		if !loadCityChrome(rom, temp).fontOK {
			t.Fatal("正對照字型未被接受")
		}
		if e = os.WriteFile(filepath.Join(temp, "fonts", name), []byte("wrong font or license"), 0600); e != nil {
			t.Fatal(e)
		}
		u := loadCityChrome(rom, temp)
		_, mask, _, rings, _ := u.paint(image.NewRGBA(image.Rect(0, 0, 1280, 800)), px, s.Palette)
		if u.fontOK || mask != 62 || rings != 0x3fff {
			t.Fatal("字型或授權失配未獨立回退", name, mask, rings)
		}
	}
	temp := filepath.Join(t.TempDir(), "wrong-shape.png")
	var raw bytes.Buffer
	if e = png.Encode(&raw, image.NewRGBA(image.Rect(0, 0, 1, 1))); e != nil {
		t.Fatal(e)
	}
	if e = os.WriteFile(temp, raw.Bytes(), 0600); e != nil {
		t.Fatal(e)
	}
	if chromeImage(temp, digest(raw.Bytes()), image.Rect(0, 0, 1280, 800)) != nil {
		t.Fatal("錯誤形狀被接受")
	}
}
