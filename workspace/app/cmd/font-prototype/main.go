// #18：實際原版文字的離線字型比較，沒有接入遊戲文字路徑。
package main

import (
	"crypto/sha256"
	"encoding/json"
	"flag"
	"fmt"
	"image"
	"image/color"
	"image/draw"
	"image/png"
	"os"
	"path/filepath"

	"golang.org/x/image/font"
	"golang.org/x/image/font/opentype"
	"golang.org/x/image/font/sfnt"
	"golang.org/x/image/math/fixed"
)

func check(err error) {
	if err != nil {
		panic(err)
	}
}
func read(p string) []byte { b, err := os.ReadFile(p); check(err); return b }
func save(p string, im image.Image) {
	f, err := os.Create(p)
	check(err)
	check(png.Encode(f, im))
	check(f.Close())
}

func main() {
	input := flag.String("input", "", "1280×800 B 材質原型")
	fontPath := flag.String("font", "", "NotoSansCJKtc-Regular.otf")
	out := flag.String("out", "", "本機比較輸出目錄")
	flag.Parse()
	f, err := os.Open(*input)
	check(err)
	src, err := png.Decode(f)
	check(err)
	check(f.Close())
	if src.Bounds() != image.Rect(0, 0, 1280, 800) {
		panic("畫面必須為 1280×800")
	}
	fontData := read(*fontPath)
	parsed, err := opentype.Parse(fontData)
	check(err)
	face, err := opentype.NewFace(parsed, &opentype.FaceOptions{Size: 56, DPI: 72, Hinting: font.HintingNone})
	check(err)
	defer face.Close()
	hd := image.NewRGBA(src.Bounds())
	draw.Draw(hd, hd.Bounds(), src, image.Point{}, draw.Src)
	var labels []map[string]any
	for i, text := range []string{"離開", "檔案", "市長", "圖表", "災難", "環境"} {
		for _, r := range text {
			idx, e := parsed.GlyphIndex(&sfnt.Buffer{}, r)
			check(e)
			if idx == 0 {
				panic(fmt.Sprintf("缺字 U+%04X", r))
			}
		}
		// 沿用原版文字區及原生 F1–F6 標示，只替換中文字墨跡。
		rect := image.Rect(28+i*176, 40, 164+i*176, 108)
		draw.Draw(hd, rect, image.NewUniform(color.RGBA{170, 170, 170, 255}), image.Point{}, draw.Src)
		bounds, _ := font.BoundString(face, text)
		placed := bounds.Add(fixed.P(rect.Min.X+12, rect.Min.Y+54))
		ink := image.Rect(placed.Min.X.Floor(), placed.Min.Y.Floor(), placed.Max.X.Ceil(), placed.Max.Y.Ceil())
		if !ink.In(rect) {
			panic(fmt.Sprintf("文字裁切 %s %v %v", text, ink, rect))
		}
		d := font.Drawer{Dst: hd, Src: image.White, Face: face, Dot: fixed.P(rect.Min.X+12, rect.Min.Y+54)}
		d.DrawString(text)
		labels = append(labels, map[string]any{"text": text, "safe_rect": rect, "ink_rect": ink})
	}
	check(os.MkdirAll(*out, 0700))
	save(filepath.Join(*out, "pixel-font.png"), src)
	save(filepath.Join(*out, "noto-font.png"), hd)
	// 以原尺寸並列頂部文字區；下方文字仍保持原版，避免冒充全字型替換。
	board := image.NewRGBA(image.Rect(0, 0, 1280, 288))
	draw.Draw(board, image.Rect(0, 0, 1280, 144), src, image.Point{}, draw.Src)
	draw.Draw(board, image.Rect(0, 144, 1280, 288), hd, image.Point{}, draw.Src)
	save(filepath.Join(*out, "comparison-fonts.png"), board)
	meta := map[string]any{"prototype": true, "font_sha256": fmt.Sprintf("%x", sha256.Sum256(fontData)), "size_px": 56, "labels": labels, "missing_glyphs": []string{}, "scope": "只比較六個已核對的主選單中文字；未驗全部文字、讀檔及動態繪字"}
	data, err := json.MarshalIndent(meta, "", "  ")
	check(err)
	check(os.WriteFile(filepath.Join(*out, "receipt.json"), data, 0600))
}
