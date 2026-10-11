package hd

import (
	"archive/zip"
	"bytes"
	"encoding/json"
	"image"
	"image/draw"
	"io"
	"os"
	"path/filepath"
	"testing"
)

type fileSample struct {
	Receipt    string
	ReceiptSHA string `json:"receipt_sha256"`
	Family     string
	Source     *struct {
		Rows   [8]string
		Colors [8]byte
	}
}

func readFileSample(t *testing.T, sample fileSample) (fixture, []byte) {
	t.Helper()
	raw, err := os.ReadFile(sample.Receipt)
	if err != nil {
		t.Fatal(err)
	}
	if digest(raw) != sample.ReceiptSHA {
		t.Fatal("來源收據雜湊不符", sample.Receipt)
	}
	z, err := zip.NewReader(bytes.NewReader(raw), int64(len(raw)))
	if err != nil {
		t.Fatal(err)
	}
	var s fixture
	var px []byte
	for _, f := range z.File {
		if f.Name != "status.json" && f.Name != "frame-index.bin" {
			continue
		}
		r, err := f.Open()
		if err != nil {
			t.Fatal(err)
		}
		data, err := io.ReadAll(r)
		r.Close()
		if err != nil {
			t.Fatal(err)
		}
		if f.Name == "status.json" {
			if err = json.Unmarshal(data, &s); err != nil {
				t.Fatal(err)
			}
		} else {
			px = data
		}
	}
	if len(px) != 64000 {
		t.Fatal("來源畫面長度不符")
	}
	return s, px
}

func fileNative(t *testing.T, r *Renderer, s fixture, px []byte) []byte {
	t.Helper()
	im, st := r.Render(px, s.Palette, s.Mode, s.Blocked, false, Origin{})
	if st.FileDialog != "" || st.FileText != [8]string{} || st.FileColors != [8]byte{} || st.FileReason != "original" {
		t.Fatal(st)
	}
	return append([]byte(nil), im.Pix...)
}

func TestActualFileDialogs(t *testing.T) {
	catalog, dir, orig := os.Getenv("TAIPEI_FILE_DIALOG_CATALOG"), os.Getenv("TAIPEI_HD_MATERIALS"), os.Getenv("TAIPEI_HD_ORIGINAL")
	if catalog == "" || dir == "" || orig == "" {
		t.Skip("需要 023 完整來源 catalog、唯讀原版與固定素材")
	}
	raw, err := os.ReadFile(catalog)
	if err != nil {
		t.Fatal(err)
	}
	if digest(raw) != "e319a23224c21cb6798e88abe107c514b6c072174a093ff02e9edbf7c555922b" {
		t.Fatal("READY catalog 失配")
	}
	var data struct{ Samples []fileSample }
	if err = json.Unmarshal(raw, &data); err != nil {
		t.Fatal(err)
	}
	if len(data.Samples) != 243 {
		t.Fatal("來源數不符", len(data.Samples))
	}
	rom, err := os.ReadFile(filepath.Join(orig, "RS201.ROM"))
	if err != nil {
		t.Fatal(err)
	}
	r := New(rom, dir)
	if r.files.reason != "scene-fallback" || r.files.browser == nil || r.files.glyphs == nil || r.files.quit == nil {
		t.Fatal("正式素材未完整載入", r.files.reason)
	}
	first := map[string]fileSample{}
	var listed *fileSample
	counts := map[string]int{}
	negatives := 0
	for _, sample := range data.Samples {
		s, px := readFileSample(t, sample)
		before := append([]byte(nil), px...)
		native := fileNative(t, r, s, px)
		im, st := r.Render(px, s.Palette, s.Mode, s.Blocked, true, Origin{})
		family, rect := sample.Family, fileBrowserRect
		if family == "browser" {
			family = "file-browser"
		} else {
			rect = fileQuitRect
		}
		if st.FileDialog != family || st.FileReason != "matched-file-dialog" || st.Reason != st.FileReason || st.Painted != 0 || st.FontLabels != 0 || st.UIIcons != 0 || st.ChromeMask != 0 || st.FooterMask != 0 || st.Panel != "" || st.Dialog != "" {
			t.Fatal(sample.Receipt, st)
		}
		if sample.Source != nil {
			if st.FileText != sample.Source.Rows || st.FileColors != sample.Source.Colors {
				t.Fatal("動態文字與獨立 Python 來源不符", sample.Receipt, st)
			}
		} else if st.FileText != [8]string{} || st.FileColors != [8]byte{} {
			t.Fatal("離開提示洩漏舊文字", st)
		}
		if !bytes.Equal(before, px) {
			t.Fatal("改寫原始色號")
		}
		box := image.Rect(rect.Min.X*4, rect.Min.Y*4, rect.Max.X*4, rect.Max.Y*4)
		// 固定參考加上 catalog 的獨立文字結果，核對整框及全畫面區外。
		want := image.NewRGBA(image.Rect(0, 0, 1280, 800))
		copy(want.Pix, native)
		ref := r.files.quit
		if sample.Source != nil {
			ref = r.files.browser
		}
		draw.Draw(want, box, ref, image.Point{}, draw.Src)
		if sample.Source != nil {
			for line, text := range sample.Source.Rows {
				y := 49
				if line > 0 {
					y = 67 + 11*(line-1)
				}
				for column, ch := range text {
					if ch == ' ' {
						continue
					}
					index := int(ch) - 32
					if sample.Source.Colors[line] == 32 {
						index += 95
					}
					x := (44 + column*6) * 4
					draw.Draw(want, image.Rect(x, y*4, x+24, y*4+28), r.files.glyphs, image.Pt(index%16*64, index/16*64), draw.Over)
				}
			}
		}
		if !bytes.Equal(im.Pix, want.Pix) {
			t.Fatal("整框或區外像素不符", sample.Receipt)
		}
		counts[sample.Family]++
		if listed == nil && sample.Source != nil && sample.Source.Colors[1] != 0 && sample.Source.Colors[2] != 0 {
			copy := sample
			listed = &copy
		}
		if _, ok := first[sample.Family]; !ok {
			first[sample.Family] = sample
		}
		for _, point := range []image.Point{rect.Min, rect.Max.Sub(image.Pt(1, 1)), image.Pt(44, 49)} {
			if sample.Source == nil && point == image.Pt(44, 49) {
				point = image.Pt(19, 177)
			}
			changed := append([]byte(nil), px...)
			changed[point.Y*320+point.X] ^= 128
			if _, _, ok := r.files.decode(changed); ok {
				t.Fatal("單像素錯誤來源未拒絕", sample.Receipt, point)
			}
			im, _ = r.Render(changed, s.Palette, s.Mode, s.Blocked, false, Origin{})
			expected := append([]byte(nil), im.Pix...)
			im, st = r.Render(changed, s.Palette, s.Mode, s.Blocked, true, Origin{})
			if st.FileDialog != "" || !bytes.Equal(expected, im.Pix) {
				t.Fatal("單像素失配未整幀回退", sample.Receipt, point, st)
			}
			negatives++
		}
		if !bytes.Equal(native, fileNative(t, r, s, px)) {
			t.Fatal("主題切換殘影", sample.Receipt)
		}
	}
	if counts["browser"] != 238 || counts["quit-confirm"] != 5 || negatives != 729 {
		t.Fatal(counts, negatives)
	}
	if listed == nil {
		t.Fatal("缺少多列清單的正常正對照")
	}
	{
		s, px := readFileSample(t, *listed)
		// 字模與背景均正確，只把兩列設成紅色，必須拒絕不可能的雙選取狀態。
		for row := 0; row < 2; row++ {
			for y := 67 + row*11; y < 74+row*11; y++ {
				for x := 44; x < 92; x++ {
					if px[y*320+x] == 31 {
						px[y*320+x] = 32
					}
				}
			}
		}
		if _, _, ok := r.files.decode(px); ok {
			t.Fatal("兩個紅色選取列未被拒絕")
		}
		native := fileNative(t, r, s, px)
		im, st := r.Render(px, s.Palette, s.Mode, s.Blocked, true, Origin{})
		if st.FileDialog != "" || !bytes.Equal(native, im.Pix) {
			t.Fatal("雙選取狀態未完整回退", st)
		}
	}
	for family, sample := range first {
		s, px := readFileSample(t, sample)
		rect := fileBrowserRect
		if family == "quit-confirm" {
			rect = fileQuitRect
		}
		used := map[byte]bool{}
		for _, v := range footerCrop(px, rect) {
			used[v] = true
		}
		for _, changeUsed := range []bool{true, false} {
			pal := s.Palette
			for i := 0; i < 256; i++ {
				if used[byte(i)] == changeUsed {
					pal[i][0] ^= 1
					break
				}
			}
			im, _ := r.Render(px, pal, s.Mode, s.Blocked, false, Origin{})
			native := append([]byte(nil), im.Pix...)
			im, st := r.Render(px, pal, s.Mode, s.Blocked, true, Origin{})
			if changeUsed {
				if st.FileReason != "file-palette-mismatch" || st.FileDialog != "" || st.FileText != [8]string{} || st.FileColors != [8]byte{} || !bytes.Equal(native, im.Pix) {
					t.Fatal("使用中色盤未回退", family, st)
				}
			} else if st.FileDialog == "" || bytes.Equal(native, im.Pix) {
				t.Fatal("未使用色盤誤拒絕", family, st)
			}
		}
	}
	// 真實素材缺失及內容竄改，單一圖檔故障只影響使用它的視窗。
	names := []string{"fonts/NotoSansCJKtc-Regular.otf", "fonts/LICENSE", "file-dialogs-v1/manifest.json", "file-dialogs-v1/palette.json", "file-dialogs-v1/browser.png", "file-dialogs-v1/glyphs.png", "file-dialogs-v1/quit-confirm.png"}
	for _, target := range names {
		for _, corrupt := range []bool{false, true} {
			tmp := t.TempDir()
			for _, name := range names {
				path := filepath.Join(tmp, name)
				if err = os.MkdirAll(filepath.Dir(path), 0700); err != nil {
					t.Fatal(err)
				}
				if name == target {
					if !corrupt {
						continue
					}
					raw, err = os.ReadFile(filepath.Join(dir, name))
					if err != nil {
						t.Fatal(err)
					}
					raw[len(raw)/2] ^= 1
					if err = os.WriteFile(path, raw, 0600); err != nil {
						t.Fatal(err)
					}
				} else if err = os.Symlink(filepath.Join(dir, name), path); err != nil {
					t.Fatal(err)
				}
			}
			original := r.files
			r.files = loadFileDialogs(rom, tmp)
			for family, sample := range first {
				s, px := readFileSample(t, sample)
				native := fileNative(t, r, s, px)
				im, st := r.Render(px, s.Palette, s.Mode, s.Blocked, true, Origin{})
				unaffected := (family == "browser" && target == "file-dialogs-v1/quit-confirm.png") || (family == "quit-confirm" && (target == "file-dialogs-v1/browser.png" || target == "file-dialogs-v1/glyphs.png"))
				if unaffected {
					if st.FileDialog == "" {
						t.Fatal("素材故障擴散", target, family, st)
					}
				} else if st.FileDialog != "" || st.FileText != [8]string{} || st.FileColors != [8]byte{} || !bytes.Equal(im.Pix, native) {
					t.Fatal("素材故障未完整回退", target, corrupt, family, st)
				}
			}
			if filepath.Dir(target) == "file-dialogs-v1" {
				s, px := load(t, "file-menu")
				_, st := r.Render(px, s.Palette, s.Mode, s.Blocked, true, Origin{})
				if st.Panel != "city-f2" {
					t.Fatal("檔案素材故障影響其他呈現家族", target, st)
				}
			}
			r.files = original
		}
	}
	t.Log("243 完整來源、729 單像素與雙選取負對照、使用／未使用色盤、14 真實資源故障及隔離通過")
}
