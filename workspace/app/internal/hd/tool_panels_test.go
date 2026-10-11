package hd

import (
	"bytes"
	"image"
	"io/fs"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestActualToolPanels(t *testing.T) {
	testActualFixedPanels(t, "TAIPEI_TOOL_PANEL_RECEIPTS", "tool-menus-v1", 18, "tool-02", "tool-05", loadToolPanels, func(r *Renderer) **panelSet { return &r.toolPanels })
}

func testActualFixedPanels(t *testing.T, fixtureEnv, folder string, count int, firstID, otherID string, loader func(string) *panelSet, slot func(*Renderer) **panelSet) {
	fixtures := os.Getenv(fixtureEnv)
	dir, orig := os.Getenv("TAIPEI_HD_MATERIALS"), os.Getenv("TAIPEI_HD_ORIGINAL")
	if fixtures == "" || dir == "" || orig == "" {
		t.Skip("需要完整面板正常收據及固定素材：" + fixtureEnv)
	}
	t.Setenv("TAIPEI_HD_RECEIPTS", fixtures)
	rom, err := os.ReadFile(filepath.Join(orig, "RS201.ROM"))
	if err != nil {
		t.Fatal(err)
	}
	r := New(rom, dir)
	panels := *slot(r)
	if panels.reason != "scene-fallback" || len(panels.states) != count {
		t.Fatal(panels.reason)
	}
	paths := []string{}
	err = filepath.WalkDir(fixtures, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if !d.IsDir() && strings.HasSuffix(path, "-capture.zip") {
			rel, e := filepath.Rel(fixtures, path)
			if e != nil {
				return e
			}
			paths = append(paths, strings.TrimSuffix(rel, "-capture.zip"))
		}
		return nil
	})
	if err != nil {
		t.Fatal(err)
	}
	byState := map[string]string{}
	for _, name := range paths {
		_, px := load(t, name)
		for _, state := range panels.states {
			b := state.Native
			var source []byte
			for y := b[1]; y < b[1]+b[3]; y++ {
				source = append(source, px[y*320+b[0]:y*320+b[0]+b[2]]...)
			}
			if digest(source) == state.SourceSHA {
				byState[state.SourceSHA] = name
			}
		}
	}
	if len(byState) != count {
		t.Fatal("正常來源狀態缺少", len(byState))
	}
	for key, state := range panels.states {
		t.Run(state.ID+"/"+byState[key], func(t *testing.T) {
			s, px := load(t, byState[key])
			input := append([]byte(nil), px...)
			a, _ := r.Render(px, s.Palette, s.Mode, s.Blocked, false, Origin{})
			native := append([]byte(nil), a.Pix...)
			a, st := r.Render(px, s.Palette, s.Mode, s.Blocked, true, Origin{})
			if st.Panel != state.ID || st.PanelSelection != state.Selection || st.PanelReason != "matched-panel" || st.Painted != 0 || st.FontLabels != 0 || st.UIIcons != 0 || st.FooterMask != 0 || st.ChromeMask != 0 {
				t.Fatal(st)
			}
			b := state.Native
			box := image.Rect(b[0]*4, b[1]*4, (b[0]+b[2])*4, (b[1]+b[3])*4)
			for y := 0; y < 800; y++ {
				for x := 0; x < 1280; x++ {
					at := (y*1280 + x) * 4
					if image.Pt(x, y).In(box) {
						rr, gg, bb, aa := state.image.At(x-box.Min.X, y-box.Min.Y).RGBA()
						if !bytes.Equal(a.Pix[at:at+4], []byte{byte(rr >> 8), byte(gg >> 8), byte(bb >> 8), byte(aa >> 8)}) {
							t.Fatal("固定面板失配", x, y)
						}
					} else if !bytes.Equal(a.Pix[at:at+4], native[at:at+4]) {
						t.Fatal("區外改變", x, y)
					}
				}
			}
			if !bytes.Equal(input, px) {
				t.Fatal("原色號被改寫")
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
			}{
				{changed, s.Palette, s.Mode, true}, {px, wrong, s.Mode, true}, {px, s.Palette, 3, true}, {px, s.Palette, s.Mode, false},
			} {
				a, _ = r.Render(tc.px, tc.pal, tc.mode, s.Blocked, false, Origin{})
				want := append([]byte(nil), a.Pix...)
				a, st = r.Render(tc.px, tc.pal, tc.mode, s.Blocked, tc.enabled, Origin{})
				if st.Panel != "" || !bytes.Equal(want, a.Pix) {
					t.Fatal("未知來源、色盤或主題未完整回退", st)
				}
			}
		})
	}
	// 真實檔案缺失及竄改不改動原素材，並驗單張故障的範圍。
	names := []string{"fonts/NotoSansCJKtc-Regular.otf", "fonts/LICENSE"}
	entries, err := os.ReadDir(filepath.Join(dir, folder))
	if err != nil {
		t.Fatal(err)
	}
	for _, e := range entries {
		if !e.IsDir() {
			names = append(names, folder+"/"+e.Name())
		}
	}
	var first, other *panelState
	for _, state := range panels.states {
		if state.ID == firstID && state.Selection == 0 {
			first = state
		}
		if state.ID == otherID && state.Selection == 0 {
			other = state
		}
	}
	if first == nil || other == nil {
		t.Fatal("故障隔離正對照缺少", firstID, otherID)
	}
	s, px := load(t, byState[first.SourceSHA])
	a, _ := r.Render(px, s.Palette, s.Mode, s.Blocked, false, Origin{})
	native := append([]byte(nil), a.Pix...)
	for _, target := range []string{folder + "/manifest.json", folder + "/" + first.Image, "fonts/NotoSansCJKtc-Regular.otf", "fonts/LICENSE"} {
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
			old := *slot(r)
			*slot(r) = loader(tmp)
			a, st := r.Render(px, s.Palette, s.Mode, s.Blocked, true, Origin{})
			if st.Panel != "" || !bytes.Equal(a.Pix, native) {
				t.Fatal(target, corrupt, "素材失配未回退", st)
			}
			if target == folder+"/"+first.Image {
				s2, px2 := load(t, byState[other.SourceSHA])
				_, st = r.Render(px2, s2.Palette, s2.Mode, s2.Blocked, true, Origin{})
				if st.Panel != other.ID {
					t.Fatal("單張素材失配影響其他面板", st)
				}
			}
			*slot(r) = old
		}
	}
}
