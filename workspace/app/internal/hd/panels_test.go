package hd

import (
	"bytes"
	"fmt"
	"image"
	"os"
	"path/filepath"
	"testing"
)

func TestActualStartupPanels(t *testing.T) {
	fixtures := os.Getenv("TAIPEI_PANEL_RECEIPTS")
	dir, orig := os.Getenv("TAIPEI_HD_MATERIALS"), os.Getenv("TAIPEI_HD_ORIGINAL")
	if fixtures == "" || dir == "" || orig == "" {
		t.Skip("需要十三種正常 GUI 收據及本機素材")
	}
	t.Setenv("TAIPEI_HD_RECEIPTS", fixtures)
	rom, err := os.ReadFile(filepath.Join(orig, "RS201.ROM"))
	if err != nil {
		t.Fatal(err)
	}
	r := New(rom, dir)
	if r.panels.reason != "scene-fallback" || len(r.panels.states) != 13 {
		t.Fatal(r.panels.reason)
	}
	for _, scene := range []struct {
		id, prefix string
		n          int
	}{{"main", "main", 3}, {"city", "city-left", 7}, {"difficulty", "difficulty", 3}} {
		for sel := 0; sel < scene.n; sel++ {
			t.Run(fmt.Sprintf("%s/%d", scene.id, sel), func(t *testing.T) {
				s, px := load(t, fmt.Sprintf("%s-%d", scene.prefix, sel))
				input := append([]byte(nil), px...)
				a, _ := r.Render(px, s.Palette, s.Mode, s.Blocked, false, Origin{})
				native := append([]byte(nil), a.Pix...)
				a, st := r.Render(px, s.Palette, s.Mode, s.Blocked, true, Origin{})
				if st.Panel != scene.id || st.PanelSelection != sel || st.PanelReason != "matched-panel" || st.Painted != 0 || st.FontLabels != 0 || st.UIIcons != 0 || st.Dialog != "" {
					t.Fatal(st)
				}
				var state *panelState
				for _, p := range r.panels.states {
					if p.ID == scene.id && p.Selection == sel {
						state = p
					}
				}
				b := state.Native
				box := image.Rect(b[0]*4, b[1]*4, (b[0]+b[2])*4, (b[1]+b[3])*4)
				for y := 0; y < 800; y++ {
					for x := 0; x < 1280; x++ {
						at := (y*1280 + x) * 4
						if image.Pt(x, y).In(box) {
							rr, gg, bb, aa := state.image.At(x-box.Min.X, y-box.Min.Y).RGBA()
							if !bytes.Equal(a.Pix[at:at+4], []byte{byte(rr >> 8), byte(gg >> 8), byte(bb >> 8), byte(aa >> 8)}) {
								t.Fatal("面板像素失配", x, y)
							}
						} else if !bytes.Equal(native[at:at+4], a.Pix[at:at+4]) {
							t.Fatal("區外改變", x, y)
						}
					}
				}
				if !bytes.Equal(input, px) {
					t.Fatal("原始色號改寫")
				}
				changed := append([]byte(nil), px...)
				changed[b[1]*320+b[0]] ^= 1
				wrong := s.Palette
				wrong[state.PaletteIndices[0]][0] ^= 1
				for _, tc := range []struct {
					px      []byte
					pal     [256][3]byte
					mode    int
					enabled bool
				}{{changed, s.Palette, s.Mode, true}, {px, wrong, s.Mode, true}, {px, s.Palette, 3, true}, {px, s.Palette, s.Mode, false}} {
					a, _ = r.Render(tc.px, tc.pal, tc.mode, s.Blocked, false, Origin{})
					want := append([]byte(nil), a.Pix...)
					a, st = r.Render(tc.px, tc.pal, tc.mode, s.Blocked, tc.enabled, Origin{})
					if st.Panel != "" || !bytes.Equal(want, a.Pix) {
						t.Fatal("失配或切換未完整回退", st)
					}
				}
			})
		}
	}
	// 撤除或損毀必要輸入，使用獨立目錄，不改動原素材。
	base := filepath.Join(dir, "startup-menus-v1")
	entries, err := os.ReadDir(base)
	if err != nil {
		t.Fatal(err)
	}
	names := []string{"fonts/NotoSansCJKtc-Regular.otf", "fonts/LICENSE"}
	for _, entry := range entries {
		if !entry.IsDir() {
			names = append(names, "startup-menus-v1/"+entry.Name())
		}
	}
	s, px := load(t, "main-0")
	a, _ := r.Render(px, s.Palette, s.Mode, s.Blocked, false, Origin{})
	native := append([]byte(nil), a.Pix...)
	for _, target := range []string{"startup-menus-v1/manifest.json", "startup-menus-v1/startup-main-0.png", "fonts/NotoSansCJKtc-Regular.otf", "fonts/LICENSE"} {
		for _, corrupt := range []bool{false, true} {
			tmp := t.TempDir()
			for _, name := range names {
				path := filepath.Join(tmp, name)
				if err := os.MkdirAll(filepath.Dir(path), 0700); err != nil {
					t.Fatal(err)
				}
				if name == target {
					if !corrupt {
						continue
					}
					raw, err := os.ReadFile(filepath.Join(dir, name))
					if err != nil {
						t.Fatal(err)
					}
					raw[len(raw)/2] ^= 1
					if err = os.WriteFile(path, raw, 0600); err != nil {
						t.Fatal(err)
					}
				} else if err := os.Symlink(filepath.Join(dir, name), path); err != nil {
					t.Fatal(err)
				}
			}
			old := r.panels
			r.panels = loadPanels(tmp)
			a, st := r.Render(px, s.Palette, s.Mode, s.Blocked, true, Origin{})
			if st.Panel != "" || !bytes.Equal(native, a.Pix) {
				t.Fatal(target, corrupt, st)
			}
			if target == "startup-menus-v1/startup-main-0.png" {
				other, frame := load(t, "city-left-0")
				_, st = r.Render(frame, other.Palette, other.Mode, other.Blocked, true, Origin{})
				if st.Panel != "city" {
					t.Fatal("單張缺失影響其他已驗面板", st)
				}
			}
			r.panels = old
		}
	}
}
