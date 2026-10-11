package hd

import (
	"archive/zip"
	"bytes"
	"encoding/json"
	"image"
	"io"
	"os"
	"path/filepath"
	"testing"
)

type fixture struct {
	Mode    int           `json:"mode"`
	Blocked bool          `json:"dos_blocked"`
	Palette [256][3]uint8 `json:"palette"`
}

func load(t *testing.T, name string) (fixture, []byte) {
	t.Helper()
	dir := os.Getenv("TAIPEI_HD_RECEIPTS")
	if dir == "" {
		t.Skip("需要本機原版單幀收據")
	}
	z, e := zip.OpenReader(filepath.Join(dir, name+"-capture.zip"))
	if e != nil {
		t.Fatal(e)
	}
	defer z.Close()
	var s fixture
	var px []byte
	for _, f := range z.File {
		if f.Name != "frame-index.bin" && f.Name != "status.json" {
			continue
		}
		r, e := f.Open()
		if e != nil {
			t.Fatal(e)
		}
		data, e := io.ReadAll(r)
		r.Close()
		if e != nil {
			t.Fatal(e)
		}
		if f.Name == "status.json" {
			if e = json.Unmarshal(data, &s); e != nil {
				t.Fatal(e)
			}
		} else {
			px = data
		}
	}
	return s, px
}
func TestActualCityAndFallbacks(t *testing.T) {
	s, px := load(t, "city-map")
	orig := os.Getenv("TAIPEI_HD_ORIGINAL")
	dir := os.Getenv("TAIPEI_HD_MATERIALS")
	if orig == "" || dir == "" {
		t.Skip("需要唯讀原版 ROM 與本機材質")
	}
	rom, e := os.ReadFile(filepath.Join(orig, "RS201.ROM"))
	if e != nil {
		t.Fatal(e)
	}
	r := New(rom, dir)
	r.chrome = nil // 此測試保留既有地景邊界檢查；新框架另驗固定來源與區外。
	r.footer = nil // 動態欄位另驗。
	origin := Origin{Valid: true}
	native, _ := r.Render(px, s.Palette, s.Mode, s.Blocked, false, origin)
	base := append([]byte(nil), native.Pix...)
	before := append([]byte(nil), px...)
	painted, stats := r.Render(px, s.Palette, s.Mode, s.Blocked, true, origin)
	if stats.Matched != 434 || stats.Painted != 433 || stats.Fallback != 2 || bytes.Equal(base, painted.Pix) {
		t.Fatalf("unexpected city: %+v", stats)
	}
	if !bytes.Equal(px, before) {
		t.Fatal("original indices mutated")
	}
	for _, invalid := range []Origin{{}, {X: -1, Valid: true}, {Y: 75, Valid: true}} {
		got, st := r.Render(px, s.Palette, s.Mode, false, true, invalid)
		if st.Painted != 0 || !bytes.Equal(base, got.Pix) {
			t.Fatal("unverified origin painted", invalid, st)
		}
	}
	painted, _ = r.Render(px, s.Palette, s.Mode, s.Blocked, true, origin)
	for y := 0; y < 800; y++ {
		for x := 0; x < 1280; x++ {
			if x >= 20 && x < 1064 && y >= 136 && y < 676 {
				continue
			}
			if stats.FontLabels == 6 && inMenu(image.Pt(x, y)) {
				continue
			}
			if inIcons(image.Pt(x, y), stats.UIIconMask) {
				continue
			}
			i := (y*1280 + x) * 4
			if !bytes.Equal(base[i:i+4], painted.Pix[i:i+4]) {
				t.Fatalf("outside-map change %d,%d", x, y)
			}
		}
	}
	// F2 與 023 的完整檔案／離開視窗；其餘模態由年度視窗另驗回退。
	for _, name := range []string{"file-menu", "save-dialog", "quit-confirm"} {
		state, frame := load(t, name)
		im, _ := r.Render(frame, state.Palette, state.Mode, state.Blocked, false, origin)
		want := append([]byte(nil), im.Pix...)
		got, st := r.Render(frame, state.Palette, state.Mode, state.Blocked, true, origin)
		if name == "file-menu" {
			if st.Panel != "city-f2" || st.PanelSelection != 0 || st.PanelReason != "matched-panel" || st.Painted != 0 || st.FontLabels != 0 || st.UIIcons != 0 || bytes.Equal(want, got.Pix) {
				t.Fatal("F2 完整來源未接入", st)
			}
			continue
		}
		expected := "file-browser"
		if name == "quit-confirm" {
			expected = name
		}
		if st.FileDialog != expected || st.FileReason != "matched-file-dialog" || st.Painted != 0 || bytes.Equal(want, got.Pix) {
			t.Fatal("023 完整來源未接入", name, st)
		}
	}
	wrong := s.Palette
	wrong[144][0] ^= 1
	_, st := r.Render(px, wrong, s.Mode, false, true, origin)
	if st.Painted != 0 {
		t.Fatal("palette mismatch painted")
	}
	missing := New(rom, t.TempDir())
	got, st := missing.Render(px, s.Palette, s.Mode, false, true, origin)
	if st.Painted != 0 || !bytes.Equal(base, got.Pix) {
		t.Fatal("withdrawn material painted")
	}
	got, _ = r.Render(px, s.Palette, s.Mode, false, false, origin)
	if !bytes.Equal(base, got.Pix) {
		t.Fatal("toggle retained previous HD pixels")
	}
}

func inMenu(point image.Point) bool {
	for i := range menuLabels {
		if point.In(menuRect(i)) {
			return true
		}
	}
	return false
}

func inIcons(point image.Point, mask uint16) bool {
	for i := 0; i < 14; i++ {
		if mask&(1<<i) != 0 && point.In(iconRect(i)) {
			return true
		}
	}
	return false
}

func TestMirrorMaterialEdges(t *testing.T) {
	for _, at := range []int{materialSize, materialSize * 2, materialSize * 3} {
		if mirror(at-1) != mirror(at) {
			t.Fatal("材質延伸邊緣不連續", at)
		}
	}
	for x := 0; x < 105*36; x++ {
		if at := mirror(x); at < 0 || at >= materialSize {
			t.Fatal("材質索引超界", x, at)
		}
	}
}

func TestActualAnnualBudgetPresentationAndFallback(t *testing.T) {
	dir := os.Getenv("TAIPEI_RUNTIME_RECEIPTS")
	if dir == "" {
		t.Skip("需要正常年度預算視窗收據")
	}
	t.Setenv("TAIPEI_HD_RECEIPTS", dir)
	rom, err := os.ReadFile(filepath.Join(os.Getenv("TAIPEI_HD_ORIGINAL"), "RS201.ROM"))
	if err != nil {
		t.Fatal(err)
	}
	r := New(rom, os.Getenv("TAIPEI_HD_MATERIALS"))
	for _, name := range []string{"running-03", "running-32"} {
		s, px := load(t, name)
		before := append([]byte(nil), px...)
		native, _ := r.Render(px, s.Palette, s.Mode, s.Blocked, false, Origin{X: 12, Y: 12, Valid: true})
		want := append([]byte(nil), native.Pix...)
		got, stats := r.Render(px, s.Palette, s.Mode, s.Blocked, true, Origin{X: 12, Y: 12, Valid: true})
		if stats.Painted != 0 || !stats.Budget || stats.Reason != "matched-budget" || bytes.Equal(want, got.Pix) {
			t.Fatal("年度視窗未接入完整預算呈現", name, stats)
		}
		budget := r.budget
		r.budget = loadBudgetPanel(rom, t.TempDir())
		got, stats = r.Render(px, s.Palette, s.Mode, s.Blocked, true, Origin{X: 12, Y: 12, Valid: true})
		if stats.Budget || stats.Reason != "budget-manifest-mismatch" || !bytes.Equal(want, got.Pix) {
			t.Fatal("年度視窗素材缺失未整幀回退", name, stats)
		}
		r.budget = budget
		if !bytes.Equal(before, px) {
			t.Fatal("年度視窗原版色號被改寫")
		}
	}
}
