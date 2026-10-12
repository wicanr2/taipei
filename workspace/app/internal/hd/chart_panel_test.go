package hd

import (
	"bytes"
	"fmt"
	"image"
	"image/draw"
	"os"
	"path/filepath"
	"testing"
)

func chartFixture(t *testing.T) ([]byte, string, *Renderer) {
	t.Helper()
	dir, orig := os.Getenv("TAIPEI_HD_MATERIALS"), os.Getenv("TAIPEI_HD_ORIGINAL")
	if dir == "" || orig == "" || os.Getenv("TAIPEI_CHART_RECEIPTS") == "" {
		t.Skip("需要 029 本機正式素材、原版與六入口收據")
	}
	rom, err := os.ReadFile(filepath.Join(orig, "RS201.ROM"))
	if err != nil {
		t.Fatal(err)
	}
	r := New(rom, dir)
	if r.charts == nil || r.charts.reason != "" || r.charts.frame == nil {
		t.Fatal("正式圖表素材未載入", r.charts)
	}
	return rom, dir, r
}

func chartReceipt(t *testing.T, index int) (fixture, []byte) {
	t.Helper()
	t.Setenv("TAIPEI_HD_RECEIPTS", os.Getenv("TAIPEI_CHART_RECEIPTS"))
	return load(t, fmt.Sprintf("chart-%d-blocked", index))
}

func chartReference(t *testing.T, dir string, index int) *image.RGBA {
	t.Helper()
	im := infrastructurePNG(t, filepath.Join(dir, "chart-windows-v2", fmt.Sprint(index), "presentation.png"))
	r := image.NewRGBA(im.Bounds())
	draw.Draw(r, r.Bounds(), im, image.Point{}, draw.Src)
	return r
}

func TestChartWindowsCompleteAndPhase(t *testing.T) {
	_, dir, r := chartFixture(t)
	for index := 0; index < 6; index++ {
		s, px := chartReceipt(t, index)
		before := append([]byte(nil), px...)
		palBefore := s.Palette
		ref := chartReference(t, dir, index)
		checkHD := func() {
			t.Helper()
			got, st := r.Render(px, s.Palette, 19, true, true, Origin{})
			if !st.ChartWindow || st.Reason != "matched-chart-window" || st.ChartDataSHA == "" || !bytes.Equal(got.Pix, ref.Pix) {
				t.Fatal("六圖完整固定原型不符", index, st)
			}
			if st.Painted != 0 || st.EndingScreen != "" || st.Panel != "" || st.FileDialog != "" || st.Budget || st.FontLabels != 0 || st.UIIcons != 0 || st.ChromeMask != 0 || st.FooterMask != 0 {
				t.Fatal("圖表混入其他家族", st)
			}
		}
		checkHD()
		native, _ := r.Render(px, s.Palette, 19, true, false, Origin{})
		want := append([]byte(nil), native.Pix...)
		checkHD()
		for _, c := range []struct {
			mode    int
			blocked bool
			enabled bool
			reason  string
		}{{3, true, true, "video-mode"}, {19, false, true, "chart-unverified-phase"}, {19, true, false, "original"}} {
			got, st := r.Render(px, s.Palette, c.mode, c.blocked, c.enabled, Origin{})
			if st.ChartWindow || st.Reason != c.reason || !bytes.Equal(got.Pix, want) {
				t.Fatal("模式、相位或 F12 未完整回退", index, st)
			}
			checkHD()
		}
		if !bytes.Equal(px, before) || s.Palette != palBefore {
			t.Fatal("呈現改動原版資料或色盤")
		}
	}
}

func TestChartWindowsSourcePaletteAndData(t *testing.T) {
	_, dir, r := chartFixture(t)
	s, px := chartReceipt(t, 1)
	ref := chartReference(t, dir, 1)
	for _, p := range []image.Point{{0, 0}, {144, 126}, {1, 22}, {127, 101}, {19, 20}, {125, 108}} {
		changed := append([]byte(nil), px...)
		changed[(35+p.Y)*320+66+p.X] ^= 128
		native, _ := r.Render(changed, s.Palette, 19, true, false, Origin{})
		want := append([]byte(nil), native.Pix...)
		got, st := r.Render(changed, s.Palette, 19, true, true, Origin{})
		if st.ChartWindow || !bytes.Equal(got.Pix, want) {
			t.Fatal("固定框架來源失配仍覆繪", p, st)
		}
	}
	var used [256]bool
	for y := 0; y < 127; y++ {
		for x := 0; x < 145; x++ {
			used[px[(35+y)*320+66+x]] = true
		}
	}
	for index, yes := range used {
		if !yes {
			continue
		}
		pal := s.Palette
		pal[index][0] ^= 1
		native, _ := r.Render(px, pal, 19, true, false, Origin{})
		want := append([]byte(nil), native.Pix...)
		got, st := r.Render(px, pal, 19, true, true, Origin{})
		if st.ChartWindow || st.ChartReason != "chart-palette-mismatch" || !bytes.Equal(got.Pix, want) {
			t.Fatal("已用色盤失配未完整回退", index, st)
		}
	}
	pal := s.Palette
	pal[232] = [3]byte{1, 2, 3}
	got, st := r.Render(px, pal, 19, true, true, Origin{})
	// 未用於圖框的色盤可改變區外，因此只比較圖框；區外必須仍跟隨本幀原版。
	if !st.ChartWindow {
		t.Fatal("未用色盤被誤拒絕", st)
	}
	for y := 140; y < 648; y++ {
		if !bytes.Equal(got.Pix[(y*1280+264)*4:(y*1280+844)*4], ref.Pix[(y*1280+264)*4:(y*1280+844)*4]) {
			t.Fatal("未用色盤改變圖框")
		}
	}
	// 任一原色號只依其原版 RGB 原位顯示，不猜統計類別。
	changed := append([]byte(nil), px...)
	changed[55*320+86] = 232
	got, st = r.Render(changed, s.Palette, 19, true, true, Origin{})
	if !st.ChartWindow {
		t.Fatal("原版資料格未接受正常色盤值", st)
	}
	for y := 0; y < 800; y++ {
		for x := 0; x < 1280; x++ {
			at := (y*1280 + x) * 4
			if x >= 344 && x < 348 && y >= 220 && y < 224 {
				grain := int(r.charts.grain[(y-140)*580+x-264]) - 128
				for c := 0; c < 3; c++ {
					if got.Pix[at+c] != chartClamp(int(s.Palette[232][c])+grain) {
						t.Fatal("資料格色號、位置或筆觸不符")
					}
				}
			} else if !bytes.Equal(got.Pix[at:at+4], ref.Pix[at:at+4]) {
				t.Fatal("單格資料更新波及區外", x, y)
			}
		}
	}
	got, st = r.Render(changed, pal, 19, true, true, Origin{})
	if st.ChartWindow || st.ChartReason != "chart-palette-mismatch" {
		t.Fatal("新使用的失配色盤未拒絕", st)
	}
}

func TestChartWindowsActualLoaderFaults(t *testing.T) {
	rom, dir, r := chartFixture(t)
	s, px := chartReceipt(t, 0)
	native, _ := r.Render(px, s.Palette, 19, true, false, Origin{})
	want := append([]byte(nil), native.Pix...)
	for _, c := range []struct {
		name, path, reason string
		change             []byte
	}{
		{"missing-manifest", "chart-windows-ready-v1/manifest.json", "chart-manifest-mismatch", nil},
		{"corrupt-manifest", "chart-windows-ready-v1/manifest.json", "chart-manifest-mismatch", []byte("{")},
		{"wrong-stage", "chart-windows-ready-v1/manifest.json", "chart-manifest-mismatch", []byte(`{"stage":"all-statistics"}`)},
		{"missing-frame", "chart-windows-ready-v1/frame.png", "chart-image-mismatch", nil},
		{"corrupt-frame", "chart-windows-ready-v1/frame.png", "chart-image-mismatch", []byte("PNG")},
		{"missing-grain", "chart-windows-ready-v1/grain.bin", "chart-grain-mismatch", nil},
		{"corrupt-grain", "chart-windows-ready-v1/grain.bin", "chart-grain-mismatch", []byte("grain")},
		{"missing-font", "fonts/NotoSansCJKtc-Regular.otf", "chart-font-mismatch", nil},
		{"corrupt-font", "fonts/NotoSansCJKtc-Regular.otf", "chart-font-mismatch", []byte("OTF")},
		{"missing-license", "fonts/LICENSE", "chart-license-mismatch", nil},
		{"corrupt-license", "fonts/LICENSE", "chart-license-mismatch", []byte("OFL")},
	} {
		t.Run(c.name, func(t *testing.T) {
			root := t.TempDir()
			for _, name := range []string{"fonts", "chart-windows-ready-v1"} {
				if err := os.Mkdir(filepath.Join(root, name), 0700); err != nil {
					t.Fatal(err)
				}
			}
			for _, name := range []string{"fonts/NotoSansCJKtc-Regular.otf", "fonts/LICENSE", "chart-windows-ready-v1/manifest.json", "chart-windows-ready-v1/frame.png", "chart-windows-ready-v1/grain.bin"} {
				if name == c.path {
					if c.change != nil {
						if err := os.WriteFile(filepath.Join(root, name), c.change, 0600); err != nil {
							t.Fatal(err)
						}
					}
				} else if err := os.Symlink(filepath.Join(dir, name), filepath.Join(root, name)); err != nil {
					t.Fatal(err)
				}
			}
			r.charts = loadChartWindows(rom, root)
			got, st := r.Render(px, s.Palette, 19, true, true, Origin{})
			if r.charts.reason != c.reason || st.ChartReason != c.reason || st.ChartWindow || !bytes.Equal(got.Pix, want) {
				t.Fatal("真實載入故障未完整回退", st)
			}
		})
	}
	if loadChartWindows([]byte("bad ROM"), dir).reason != "chart-rom-mismatch" {
		t.Fatal("錯 ROM 未拒絕")
	}
}

func TestChartWindowsOtherFamilyIsolation(t *testing.T) {
	_, _, r := chartFixture(t)
	s, px := load(t, "city-map")
	before, st := r.Render(px, s.Palette, s.Mode, s.Blocked, true, Origin{X: 12, Y: 12, Valid: true})
	want := append([]byte(nil), before.Pix...)
	if st.Reason != "matched-city" {
		t.Fatal("城市正對照不符", st)
	}
	r.charts = &chartWindows{base: r.charts.base, reason: "chart-image-mismatch"}
	got, st := r.Render(px, s.Palette, s.Mode, s.Blocked, true, Origin{X: 12, Y: 12, Valid: true})
	if st.ChartWindow || st.Reason != "matched-city" || !bytes.Equal(got.Pix, want) {
		t.Fatal("圖表故障影響城市", st)
	}
}
