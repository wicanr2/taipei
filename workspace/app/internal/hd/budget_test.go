package hd

import (
	"bytes"
	"encoding/json"
	"image"
	"image/draw"
	"image/png"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

type budgetSample struct {
	Receipt    string
	ReceiptSHA string `json:"receipt_sha256"`
	Source     struct {
		Fields []struct {
			Text                 string
			X, Y, Columns, Color int
		}
		Selection []int `json:"selected_rows"`
	}
}

func budgetFixture(t *testing.T, s budgetSample) (fixture, []byte) {
	t.Helper()
	if !filepath.IsAbs(s.Receipt) {
		s.Receipt = filepath.Join(os.Getenv("TAIPEI_BUDGET_WORKSPACE"), s.Receipt)
	}
	return readFileSample(t, fileSample{Receipt: s.Receipt, ReceiptSHA: s.ReceiptSHA})
}

func TestActualBudgetPanel(t *testing.T) {
	catalog, dir, orig := os.Getenv("TAIPEI_BUDGET_CATALOG"), os.Getenv("TAIPEI_HD_MATERIALS"), os.Getenv("TAIPEI_HD_ORIGINAL")
	if catalog == "" || dir == "" || orig == "" {
		t.Skip("需要 025 固定完整來源、唯讀原版及本機素材")
	}
	raw, err := os.ReadFile(catalog)
	if err != nil || digest(raw) != "63efc60609d200351746801f9b8d8a6a8764318b33bf05dfe78551f372fc7a2f" {
		t.Fatal("READY catalog 失配", err)
	}
	var data struct{ Samples []budgetSample }
	if err = json.Unmarshal(raw, &data); err != nil || len(data.Samples) != 43 {
		t.Fatal(err, len(data.Samples))
	}
	rom, err := os.ReadFile(filepath.Join(orig, "RS201.ROM"))
	if err != nil {
		t.Fatal(err)
	}
	r := New(rom, dir)
	if r.budget.reason != "scene-fallback" || r.budget.panel == nil || r.budget.glyphs == nil {
		t.Fatal("預算正式素材缺失", r.budget.reason)
	}
	readPNG := func(name, sha string) image.Image {
		t.Helper()
		b, e := os.ReadFile(filepath.Join(dir, "budget-v1", name))
		if e != nil || digest(b) != sha {
			t.Fatal(name, e)
		}
		im, e := png.Decode(bytes.NewReader(b))
		if e != nil {
			t.Fatal(e)
		}
		return im
	}
	panel := readPNG("panel.png", "24d6607b61504936a798598e29ebd182b7d65e82c2e744218610337693390388")
	glyphs := readPNG("glyphs.png", "033f1cfa385290c7f1b812faa0170a3e80af2f4de634ef70d8cf1f84f3c4fba1")
	native := func(s fixture, px []byte) []byte {
		t.Helper()
		im, st := r.Render(px, s.Palette, s.Mode, s.Blocked, false, Origin{})
		if st.Budget || st.BudgetText != [11]string{} || st.BudgetColors != [11]byte{} || st.BudgetSelection != -1 || st.BudgetReason != "original" {
			t.Fatal("原版主題洩漏預算欄位", st)
		}
		return append([]byte(nil), im.Pix...)
	}
	fallback := func(s fixture, px []byte) {
		t.Helper()
		want := native(s, px)
		im, st := r.Render(px, s.Palette, s.Mode, s.Blocked, true, Origin{Valid: true})
		if st.Budget || st.BudgetText != [11]string{} || st.BudgetColors != [11]byte{} || st.BudgetSelection != -1 || !bytes.Equal(want, im.Pix) {
			t.Fatal("預算失配未整幀回退", st)
		}
	}
	negativeCount := 0
	for _, sample := range data.Samples {
		s, px := budgetFixture(t, sample)
		before := append([]byte(nil), px...)
		base := native(s, px)
		im, st := r.Render(px, s.Palette, s.Mode, s.Blocked, true, Origin{})
		if !st.Budget || st.BudgetReason != "matched-budget" || st.Reason != st.BudgetReason || len(sample.Source.Selection) != 1 || st.BudgetSelection != sample.Source.Selection[0] || st.Painted != 0 || st.FileDialog != "" || st.FontLabels != 0 || st.UIIcons != 0 || st.ChromeMask != 0 || st.FooterMask != 0 || st.Panel != "" || st.Dialog != "" {
			t.Fatal(sample.Receipt, st)
		}
		want := image.NewRGBA(image.Rect(0, 0, 1280, 800))
		copy(want.Pix, base)
		draw.Draw(want, image.Rect(72, 148, 1012, 676), panel, image.Point{}, draw.Src)
		if len(sample.Source.Fields) != 11 {
			t.Fatal("獨立欄位數不符")
		}
		for i, field := range sample.Source.Fields {
			if st.BudgetText[i] != field.Text || int(st.BudgetColors[i]) != field.Color {
				t.Fatal("原字串或顏色與 Python 獨立來源不符", sample.Receipt, i, st)
			}
			for col, ch := range field.Text {
				index := strings.IndexRune(" -0123456789", ch)
				row := 0
				if field.Color == 12 {
					row = 28
				}
				x, y := (18+field.X+col*6)*4, (37+field.Y)*4
				draw.Draw(want, image.Rect(x, y, x+24, y+28), glyphs, image.Pt(index*24, row), draw.Over)
			}
		}
		if !bytes.Equal(im.Pix, want.Pix) || bytes.Equal(im.Pix, base) || !bytes.Equal(before, px) {
			t.Fatal("完整呈現、全部區外或原版輸入不符", sample.Receipt)
		}
		if !bytes.Equal(base, native(s, px)) {
			t.Fatal("切回原版殘影")
		}
		for _, point := range []image.Point{{18, 37}, {252, 168}, {111, 66}, {228, 157}, {35, 45}} {
			changed := append([]byte(nil), px...)
			changed[point.Y*320+point.X] ^= 128
			if _, _, _, ok := r.budget.decode(changed); ok {
				t.Fatal("單像素來源未拒絕", sample.Receipt, point)
			}
			fallback(s, changed)
			negativeCount++
		}
	}
	// 六張升 READY 前固定的原位原型直接比對，避免只驗與實作同寫的公式。
	raw, err = os.ReadFile(filepath.Join(dir, "budget-v1/manifest.json"))
	if err != nil || digest(raw) != budgetManifestSHA {
		t.Fatal(err)
	}
	var manifest struct {
		Proofs []struct {
			Receipt    string
			ReceiptSHA string `json:"receipt_sha256"`
			Image      string
			ImageSHA   string `json:"image_sha256"`
		}
	}
	if err = json.Unmarshal(raw, &manifest); err != nil || len(manifest.Proofs) != 6 {
		t.Fatal(err)
	}
	for _, proof := range manifest.Proofs {
		s, px := budgetFixture(t, budgetSample{Receipt: proof.Receipt, ReceiptSHA: proof.ReceiptSHA})
		im, st := r.Render(px, s.Palette, s.Mode, s.Blocked, true, Origin{})
		ref := readPNG(proof.Image, proof.ImageSHA)
		for y := 0; y < 800; y++ {
			for x := 0; x < 1280; x++ {
				a, b, c, d := im.At(x, y).RGBA()
				e, f, g, h := ref.At(x, y).RGBA()
				if a != e || b != f || c != g || d != h {
					t.Fatal("固定原型像素失配", proof.Image, x, y, st)
				}
			}
		}
		for _, kind := range []string{"none", "double", "cost"} {
			changed := append([]byte(nil), px...)
			for i, slot := range budgetSlots {
				if (kind == "none" && i < 5) || (kind == "double" && i < 5) || (kind == "cost" && i == 5) {
					color := byte(0)
					if kind != "none" {
						color = 12
						if kind == "double" && i > 1 {
							color = 0
						}
					}
					for y := 37 + slot.y; y < 44+slot.y; y++ {
						for x := 18 + slot.x; x < 18+slot.x+slot.columns*6; x++ {
							if changed[y*320+x] != 3 {
								changed[y*320+x] = color
							}
						}
					}
				}
			}
			fallback(s, changed)
			negativeCount++
		}
	}
	s, px := budgetFixture(t, data.Samples[0])
	used := map[byte]bool{}
	for _, v := range footerCrop(px, budgetRect) {
		used[v] = true
	}
	for _, changeUsed := range []bool{true, false} {
		changed := s
		for i := 0; i < 256; i++ {
			if used[byte(i)] == changeUsed {
				changed.Palette[i][0] ^= 1
				break
			}
		}
		if changeUsed {
			fallback(changed, px)
		} else if _, st := r.Render(px, changed.Palette, s.Mode, s.Blocked, true, Origin{}); !st.Budget {
			t.Fatal("未用色盤錯誤拒絕", st)
		}
	}
	names := []string{"fonts/NotoSansCJKtc-Regular.otf", "fonts/LICENSE", "budget-v1/manifest.json", "budget-v1/palette.json", "budget-v1/panel.png", "budget-v1/glyphs.png"}
	for _, target := range names {
		for _, corrupt := range []bool{false, true} {
			tmp := t.TempDir()
			for _, name := range names {
				path := filepath.Join(tmp, name)
				if err = os.MkdirAll(filepath.Dir(path), 0700); err != nil {
					t.Fatal(err)
				}
				if name != target {
					err = os.Symlink(filepath.Join(dir, name), path)
				} else if corrupt {
					raw, err = os.ReadFile(filepath.Join(dir, name))
					if err == nil {
						raw[len(raw)/2] ^= 1
						err = os.WriteFile(path, raw, 0600)
					}
				}
				if err != nil {
					t.Fatal(err)
				}
			}
			original := r.budget
			r.budget = loadBudgetPanel(rom, tmp)
			fallback(s, px)
			brother, frame := load(t, "file-menu")
			if _, st := r.Render(frame, brother.Palette, brother.Mode, brother.Blocked, true, Origin{}); st.Panel != "city-f2" {
				t.Fatal("預算資源故障影響功能選單", target, st)
			}
			r.budget = original
		}
	}
	if negativeCount != 233 {
		t.Fatal(negativeCount)
	}
	t.Log("43 完整來源、六張固定原型、233 有效來源負對照、使用／未用色盤與十二實際素材故障及隔離通過")
}
