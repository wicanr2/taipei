package hd

import (
	"bytes"
	"image"
	"image/png"
	"os"
	"path/filepath"
	"testing"
)

func TestActualNewGameDialog(t *testing.T) {
	s, px := load(t, "new-game")
	dir, orig := os.Getenv("TAIPEI_HD_MATERIALS"), os.Getenv("TAIPEI_HD_ORIGINAL")
	if dir == "" || orig == "" {
		t.Skip("需要本機完整來源與素材")
	}
	rom, err := os.ReadFile(filepath.Join(orig, "RS201.ROM"))
	if err != nil {
		t.Fatal(err)
	}
	r := New(rom, dir)
	if r.dialog.reason != "matched-dialog" {
		t.Fatal(r.dialog.reason)
	}
	native, _ := r.Render(px, s.Palette, s.Mode, s.Blocked, false, Origin{})
	base, input := append([]byte(nil), native.Pix...), append([]byte(nil), px...)
	got, st := r.Render(px, s.Palette, s.Mode, s.Blocked, true, Origin{})
	if st.Dialog != "new-game" || st.Painted != 0 || st.FontLabels != 0 || st.UIIcons != 0 || bytes.Equal(base, got.Pix) {
		t.Fatal("正常阻塞視窗未獨立覆繪", st)
	}
	for y := 0; y < 800; y++ {
		for x := 0; x < 1280; x++ {
			if image.Pt(x, y).In(dialogRect) {
				continue
			}
			at := (y*1280 + x) * 4
			if !bytes.Equal(base[at:at+4], got.Pix[at:at+4]) {
				t.Fatal("區外像素改變", x, y)
			}
		}
	}
	// 此匯出供人工逐字審查及固定參考封存；正式核對器另驗來源與參考雜湊。
	if path := os.Getenv("TAIPEI_DIALOG_EXPORT"); path != "" {
		f, e := os.Create(path)
		if e != nil {
			t.Fatal(e)
		}
		e = png.Encode(f, r.dialog.image)
		f.Close()
		if e != nil {
			t.Fatal(e)
		}
	}
	changed := append([]byte(nil), px...)
	changed[37*320+18] ^= 1
	for _, tc := range []struct {
		name    string
		frame   []byte
		palette [256][3]byte
		mode    int
		enabled bool
	}{
		{"source", changed, s.Palette, s.Mode, true},
		{"original", px, s.Palette, s.Mode, false},
		{"mode", px, s.Palette, 3, true},
	} {
		a, _ := r.Render(tc.frame, tc.palette, tc.mode, s.Blocked, false, Origin{})
		want := append([]byte(nil), a.Pix...)
		a, st := r.Render(tc.frame, tc.palette, tc.mode, s.Blocked, tc.enabled, Origin{})
		if st.Dialog != "" || !bytes.Equal(want, a.Pix) {
			t.Fatal(tc.name, st)
		}
	}
	wrong := s.Palette
	wrong[134][0] ^= 1
	a, _ := r.Render(px, wrong, s.Mode, s.Blocked, false, Origin{})
	want := append([]byte(nil), a.Pix...)
	a, st = r.Render(px, wrong, s.Mode, s.Blocked, true, Origin{})
	if st.Dialog != "" || st.DialogReason != "dialog-palette-mismatch" || !bytes.Equal(want, a.Pix) {
		t.Fatal(st)
	}
	unused := s.Palette
	unused[232][0] ^= 1
	_, st = r.Render(px, unused, s.Mode, s.Blocked, true, Origin{})
	if st.Dialog != "new-game" {
		t.Fatal("未使用色盤影響來源", st)
	}
	for _, filename := range []string{"new-game-panel-b-v1.png", "new-game-text-v1.json", "fonts/NotoSansCJKtc-Regular.otf", "fonts/LICENSE"} {
		for _, corrupt := range []bool{false, true} {
			tmp := t.TempDir()
			if e := os.Mkdir(filepath.Join(tmp, "fonts"), 0700); e != nil {
				t.Fatal(e)
			}
			for _, name := range []string{"new-game-panel-b-v1.png", "new-game-text-v1.json", "fonts/NotoSansCJKtc-Regular.otf", "fonts/LICENSE"} {
				p, e := os.ReadFile(filepath.Join(dir, name))
				if e != nil {
					t.Fatal(e)
				}
				if name == filename {
					if !corrupt {
						continue
					}
					p[len(p)/2] ^= 1
				}
				if e = os.WriteFile(filepath.Join(tmp, name), p, 0600); e != nil {
					t.Fatal(e)
				}
			}
			r.dialog = loadNewGameDialog(tmp)
			a, st = r.Render(px, s.Palette, s.Mode, s.Blocked, true, Origin{})
			if st.Dialog != "" || !bytes.Equal(base, a.Pix) {
				t.Fatal(filename, corrupt, st)
			}
		}
	}
	r.dialog = loadNewGameDialog(dir)
	a, st = r.Render(px, s.Palette, s.Mode, s.Blocked, true, Origin{})
	if st.Dialog != "new-game" {
		t.Fatal(st)
	}
	a, _ = r.Render(px, s.Palette, s.Mode, s.Blocked, false, Origin{})
	if !bytes.Equal(base, a.Pix) {
		t.Fatal("F12 關閉殘留")
	}
	closed, frame := load(t, "difficulty")
	a, _ = r.Render(frame, closed.Palette, closed.Mode, closed.Blocked, false, Origin{})
	want = append([]byte(nil), a.Pix...)
	a, st = r.Render(frame, closed.Palette, closed.Mode, closed.Blocked, true, Origin{})
	if st.Dialog != "" || !bytes.Equal(want, a.Pix) {
		t.Fatal("關閉視窗殘留", st)
	}
	if !bytes.Equal(input, px) {
		t.Fatal("原版色號改寫")
	}
}
