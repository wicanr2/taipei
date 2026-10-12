package hd

import (
	"bytes"
	"fmt"
	"image"
	"image/color"
	"image/png"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/wicanr2/taipei/preview/internal/i18n"
	"github.com/wicanr2/taipei/preview/locales"
)

// Actual original receipts exercise the existing recognizers, not synthetic flags.
func TestInterfaceLocalesWithOriginalReceipts(t *testing.T) {
	root, dir, orig := os.Getenv("TAIPEI_LOCALE_WORKSPACE"), os.Getenv("TAIPEI_HD_MATERIALS"), os.Getenv("TAIPEI_HD_ORIGINAL")
	if root == "" || dir == "" || orig == "" {
		t.Skip("需要本機原版收據、唯讀 ROM 與固定素材")
	}
	rom, err := os.ReadFile(filepath.Join(orig, "RS201.ROM"))
	if err != nil {
		t.Fatal(err)
	}
	r := New(rom, dir)
	paths := []string{}
	for _, sub := range []string{"startup-menus-native", "tool-submenus-native", "city-menus-native", "gui-budget-cold-r4", "chart-windows-native-r3", "gui-ending-scene-cold-r1", "interface-locale-cold-r2/gui", "interface-locale-cold-r5/gui"} {
		err := filepath.WalkDir(filepath.Join(root, "runs", sub), func(path string, d os.DirEntry, err error) error {
			if err != nil {
				return err
			}
			if !d.IsDir() && strings.HasSuffix(path, "-capture.zip") {
				paths = append(paths, path)
			}
			return nil
		})
		if err != nil {
			t.Fatal(err)
		}
	}
	for _, lang := range i18n.Languages {
		t.Run(lang, func(t *testing.T) {
			if reason := r.SetLanguage(i18n.Bundled(), lang); reason != "matched-menu" {
				t.Fatal("載入失敗", reason)
			}
			if r.locale.reason != "" || len(r.locale.panels) != 60 {
				t.Fatal(r.locale.reason, len(r.locale.panels))
			}
			redInk := 0
			for i := 0; i < len(r.locale.panels["main/0"].Pix); i += 4 {
				p := r.locale.panels["main/0"].Pix[i : i+4]
				if bytes.Equal(p, []byte{255, 0, 0, 255}) {
					redInk++
				}
			}
			if redInk < 20 {
				t.Fatal("主選單選取色未沿用固定版面", redInk)
			}
			seen := map[string]bool{}
			for _, path := range paths {
				raw, e := os.ReadFile(path)
				if e != nil {
					t.Fatal(e)
				}
				s, px := readFileSample(t, fileSample{Receipt: path, ReceiptSHA: digest(raw)})
				before := append([]byte(nil), px...)
				translated, st := r.Render(px, s.Palette, s.Mode, s.Blocked, true, Origin{X: 12, Y: 12, Valid: true})
				if strings.Contains(path, "interface-locale-cold-r2/gui") {
					wanted := map[string]string{"mayor-1-capture.zip": "population", "mayor-2-capture.zip": "opinion", "environment-0-capture.zip": "settings.message_speed", "environment-1-capture.zip": "speed"}[filepath.Base(path)]
					if wanted != "" && st.InterfacePanel != wanted {
						t.Fatal("正常來源未接入", path, wanted, st)
					}
				}
				if !bytes.Equal(before, px) {
					t.Fatal("覆寫原版色號", path)
				}
				if st.LocalizedFields == 0 {
					continue
				}
				id := st.Panel
				if st.InterfacePanel != "" {
					id = st.InterfacePanel
				}
				if id == "" {
					id = fmt.Sprintf("dialog-%s-budget-%t-file-%s-chart-%t-ending-%s-footer-%d", st.Dialog, st.Budget, st.FileDialog, st.ChartWindow, st.EndingScreen, st.FooterMask)
				}
				if st.Panel != "" {
					id += fmt.Sprint("-", st.PanelSelection)
				}
				if st.LocaleReason != "matched-interface" {
					t.Fatal(path, st.LocaleReason)
				}
				// Compare all original budget values against the same HD numeric atlas.
				got := append([]byte(nil), translated.Pix...)
				active := r.locale
				r.locale = nil
				base, old := r.Render(px, s.Palette, s.Mode, s.Blocked, true, Origin{X: 12, Y: 12, Valid: true})
				r.locale = active
				if st.Budget {
					if st.BudgetText != old.BudgetText || st.BudgetColors != old.BudgetColors {
						t.Fatal("預算解析變動")
					}
					for _, slot := range budgetSlots {
						box := image.Rect((18+slot.x)*4, (37+slot.y)*4, (18+slot.x+slot.columns*6)*4, (37+slot.y)*4+28)
						for y := box.Min.Y; y < box.Max.Y; y++ {
							a, b := (y*1280+box.Min.X)*4, (y*1280+box.Max.X)*4
							if !bytes.Equal(got[a:b], base.Pix[a:b]) {
								t.Fatal("翻譯侵犯預算數字", lang, path, box, y)
							}
						}
					}
				}
				if st.InterfacePanel == "population" || st.InterfacePanel == "opinion" {
					slots := populationSlots
					if st.InterfacePanel == "opinion" {
						slots = opinionSlots
					}
					for _, slot := range slots {
						box := image.Rect((18+slot[0])*4, (37+slot[1])*4, (18+slot[0]+slot[2]*6)*4, (37+slot[1]+7)*4)
						for y := box.Min.Y; y < box.Max.Y; y++ {
							for x := box.Min.X; x < box.Max.X; x++ {
								c := s.Palette[px[(y/4)*320+x/4]]
								at := (y*1280 + x) * 4
								if !bytes.Equal(got[at:at+4], []byte{c[0], c[1], c[2], 255}) {
									t.Fatal("人口／民意數字被翻譯改寫", lang, box, x, y)
								}
							}
						}
					}
				}
				if !seen[id] && os.Getenv("TAIPEI_LOCALE_GALLERY") != "" && (st.InterfacePanel != "" || st.Budget || st.Dialog != "" || st.Panel == "main") {
					f, e := os.Create(filepath.Join(os.Getenv("TAIPEI_LOCALE_GALLERY"), lang+"-"+id+".png"))
					if e != nil {
						t.Fatal(e)
					}
					e = png.Encode(f, &image.RGBA{Pix: got, Stride: 1280 * 4, Rect: image.Rect(0, 0, 1280, 800)})
					f.Close()
					if e != nil {
						t.Fatal(e)
					}
				}
				seen[id] = true
			}
			for scene, options := range interfaceOptions {
				for selection := range options {
					if !seen[fmt.Sprintf("%s-%d", scene, selection)] {
						t.Fatal("缺少來源狀態", scene, selection)
					}
				}
			}
			t.Log("原版來源狀態", len(seen))
		})
	}
	// A valid TSV with a missing required field or oversized translation must fail visibly.
	t.Setenv("TAIPEI_HD_RECEIPTS", filepath.Join(root, "runs/startup-menus-native"))
	s, px := load(t, "main-0")
	for _, bad := range []string{
		strings.Replace(string(locales.Bundled), "startup.new_game\t", "missing.new_game\t", 1),
		strings.Replace(string(locales.Bundled), "New game", strings.Repeat("Oversized", 200), 1),
	} {
		c, e := i18n.Parse([]byte(bad))
		if e != nil {
			t.Fatal(e)
		}
		r.SetLanguage(c, "en")
		if r.locale.reason == "" {
			t.Fatal("不完整或溢位翻譯未拒絕")
		}
		got, st := r.Render(px, s.Palette, s.Mode, s.Blocked, true, Origin{})
		copyGot := append([]byte(nil), got.Pix...)
		want, _ := r.Render(px, s.Palette, s.Mode, s.Blocked, false, Origin{})
		if st.LocalizedFields != 0 || !bytes.Equal(copyGot, want.Pix) {
			t.Fatal("失敗留下部分翻譯", st)
		}
	}
}

func TestInterfaceExtraSourceIsolation(t *testing.T) {
	root, dir, orig := os.Getenv("TAIPEI_LOCALE_WORKSPACE"), os.Getenv("TAIPEI_HD_MATERIALS"), os.Getenv("TAIPEI_HD_ORIGINAL")
	if root == "" || dir == "" || orig == "" {
		t.Skip("需要固定本機來源")
	}
	rom, e := os.ReadFile(filepath.Join(orig, "RS201.ROM"))
	if e != nil {
		t.Fatal(e)
	}
	r := New(rom, dir)
	if why := r.SetLanguage(i18n.Bundled(), "en"); why != "matched-menu" {
		t.Fatal(why)
	}
	for _, tc := range []struct {
		name, id string
		box      image.Rectangle
	}{
		{"mayor-1", "population", image.Rect(18, 37, 253, 169)},
		{"mayor-2", "opinion", image.Rect(18, 37, 253, 169)},
		{"environment-0", "settings.message_speed", footerRects[0]},
		{"environment-1", "speed", image.Rect(54, 87, 219, 128)},
	} {
		path := filepath.Join(root, "runs/interface-locale-cold-r2/gui", tc.name+"-capture.zip")
		raw, e := os.ReadFile(path)
		if e != nil {
			t.Fatal(e)
		}
		s, px := readFileSample(t, fileSample{Receipt: path, ReceiptSHA: digest(raw)})
		_, st := r.Render(px, s.Palette, s.Mode, s.Blocked, true, Origin{})
		if st.InterfacePanel != tc.id {
			t.Fatal("正對照失敗", tc.id, st)
		}
		unused := s.Palette
		unused[232][0] ^= 1
		_, st = r.Render(px, unused, s.Mode, s.Blocked, true, Origin{})
		if st.InterfacePanel != tc.id {
			t.Fatal("未用色盤改動不應使來源失配", tc.id)
		}
		for _, point := range []image.Point{tc.box.Min, tc.box.Max.Sub(image.Pt(1, 1)), tc.box.Min.Add(image.Pt(6, 6))} {
			bad := append([]byte(nil), px...)
			bad[point.Y*320+point.X] ^= 255
			got, st := r.Render(bad, s.Palette, s.Mode, s.Blocked, true, Origin{})
			if st.InterfacePanel == tc.id {
				t.Fatal("損壞來源仍被翻譯", tc.id, point)
			}
			assertNativeBox(t, got, bad, s.Palette, tc.box)
		}
		pal := s.Palette
		pal[15][0] ^= 1
		got, st := r.Render(px, pal, s.Mode, s.Blocked, true, Origin{})
		if st.InterfacePanel != "" {
			t.Fatal("失配色盤仍覆繪", tc.id)
		}
		assertNativeBox(t, got, px, pal, tc.box)
		got, st = r.Render(px, s.Palette, s.Mode, s.Blocked, false, Origin{})
		if st.LocalizedFields != 0 || st.InterfacePanel != "" {
			t.Fatal("F12 原版仍翻譯")
		}
		assertNativeBox(t, got, px, s.Palette, image.Rect(0, 0, 320, 200))
	}
}

func assertNativeBox(t *testing.T, got *image.RGBA, px []byte, pal [256][3]byte, box image.Rectangle) {
	t.Helper()
	for y := box.Min.Y * 4; y < box.Max.Y*4; y++ {
		for x := box.Min.X * 4; x < box.Max.X*4; x++ {
			c := pal[px[(y/4)*320+x/4]]
			if got.RGBAAt(x, y) != (color.RGBA{c[0], c[1], c[2], 255}) {
				t.Fatal("來源失配留下局部覆繪", box, x, y)
			}
		}
	}
}
