// #49：五語系文字及語言面板可撤回原型，尚未接入產品。
package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/csv"
	"encoding/json"
	"flag"
	"fmt"
	"image"
	"image/color"
	"image/draw"
	"image/png"
	"io"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
	"unicode"
	"unicode/utf8"

	"golang.org/x/image/font"
	"golang.org/x/image/font/opentype"
	"golang.org/x/image/font/sfnt"
	"golang.org/x/image/math/fixed"
)

var languages = []string{"zh-Hant", "zh-Hans", "ja", "ko", "en"}
var menuKeys = []string{"menu.exit", "menu.file", "menu.mayor", "menu.charts", "menu.disasters", "menu.environment"}
var placeholder = regexp.MustCompile(`\{[a-zA-Z][a-zA-Z0-9_]*\}`)

func check(err error) {
	if err != nil {
		panic(err)
	}
}
func read(path string) []byte { b, err := os.ReadFile(path); check(err); return b }
func digest(b []byte) string  { return fmt.Sprintf("%x", sha256.Sum256(b)) }

type catalog map[string]map[string]string

func loadCatalog(data []byte) catalog {
	if !utf8.Valid(data) || bytes.HasPrefix(data, []byte{0xef, 0xbb, 0xbf}) {
		panic("catalog must be UTF-8 without BOM")
	}
	r := csv.NewReader(bytes.NewReader(data))
	r.Comma = '\t'
	r.FieldsPerRecord = 6
	header, err := r.Read()
	check(err)
	if strings.Join(header, "\t") != "key\t"+strings.Join(languages, "\t") {
		panic("invalid catalog columns")
	}
	result := catalog{}
	for {
		row, err := r.Read()
		if err == io.EOF {
			break
		}
		check(err)
		if !regexp.MustCompile(`^[a-zA-Z][a-zA-Z0-9_.-]*$`).MatchString(row[0]) {
			panic("invalid key: " + row[0])
		}
		if _, ok := result[row[0]]; ok {
			panic("duplicate key: " + row[0])
		}
		result[row[0]] = map[string]string{}
		var expected string
		for i, lang := range languages {
			text := row[i+1]
			if strings.TrimSpace(text) == "" {
				panic("missing translation: " + row[0] + "/" + lang)
			}
			for _, c := range text {
				if unicode.IsControl(c) {
					panic("control character: " + row[0])
				}
			}
			matches := placeholder.FindAllString(text, -1)
			sort.Strings(matches)
			signature := strings.Join(matches, " ")
			if i == 0 {
				expected = signature
			} else if signature != expected {
				panic("placeholder mismatch: " + row[0])
			}
			result[row[0]][lang] = text
		}
	}
	return result
}

type placement struct {
	Key       string          `json:"key"`
	Locale    string          `json:"locale"`
	Size      int             `json:"size_px"`
	Rect      image.Rectangle `json:"safe_rect"`
	Ink       image.Rectangle `json:"actual_ink_rect"`
	InkPixels int             `json:"ink_pixels"`
}

type painter struct {
	font       *sfnt.Font
	catalog    catalog
	placements []placement
}

func (p *painter) text(dst *image.RGBA, key, lang string, rect image.Rectangle, maxSize, minSize int, c color.Color) {
	text, ok := p.catalog[key][lang]
	if !ok {
		panic("missing key: " + key + "/" + lang)
	}
	for size := maxSize; size >= minSize; size-- {
		face, err := opentype.NewFace(p.font, &opentype.FaceOptions{Size: float64(size), DPI: 72, Hinting: font.HintingNone})
		check(err)
		bounds, _ := font.BoundString(face, text)
		w, h := bounds.Max.X.Ceil()-bounds.Min.X.Floor(), bounds.Max.Y.Ceil()-bounds.Min.Y.Floor()
		if w > rect.Dx()-8 || h > rect.Dy()-8 {
			check(face.Close())
			continue
		}
		dot := fixed.P(rect.Min.X+(rect.Dx()-w)/2-bounds.Min.X.Floor(), rect.Min.Y+(rect.Dy()-h)/2-bounds.Min.Y.Floor())
		mask := image.NewRGBA(dst.Bounds())
		d := font.Drawer{Dst: mask, Src: image.White, Face: face, Dot: dot}
		d.DrawString(text)
		check(face.Close())
		ink := image.Rectangle{}
		count := 0
		for y := rect.Min.Y - 4; y < rect.Max.Y+4; y++ {
			for x := rect.Min.X - 4; x < rect.Max.X+4; x++ {
				if mask.RGBAAt(x, y).A > 0 {
					q := image.Rect(x, y, x+1, y+1)
					if count == 0 {
						ink = q
					} else {
						ink = ink.Union(q)
					}
					count++
				}
			}
		}
		if count == 0 || !ink.In(rect) {
			panic(fmt.Sprintf("invalid ink %s/%s %v", key, lang, ink))
		}
		draw.DrawMask(dst, dst.Bounds(), image.NewUniform(c), image.Point{}, mask, image.Point{}, draw.Over)
		p.placements = append(p.placements, placement{key, lang, size, rect, ink, count})
		return
	}
	panic("text does not fit: " + key + "/" + lang)
}

func clone(src image.Image) *image.RGBA {
	dst := image.NewRGBA(src.Bounds())
	draw.Draw(dst, dst.Bounds(), src, src.Bounds().Min, draw.Src)
	return dst
}
func save(path string, src image.Image) string {
	var b bytes.Buffer
	check(png.Encode(&b, src))
	check(os.WriteFile(path, b.Bytes(), 0600))
	return digest(b.Bytes())
}

func main() {
	input := flag.String("input", "", "1280×800 正常 HD 收據")
	fontPath := flag.String("font", "", "固定 Noto OTF")
	catalogPath := flag.String("catalog", "", "DRAFT UTF-8 TSV")
	out := flag.String("out", "", "不存在的本機原型輸出目錄")
	flag.Parse()
	if *out == "" {
		panic("out required")
	}
	check(os.Mkdir(*out, 0700)) // 拒絕覆寫前件。
	srcData, fontData, catalogData := read(*input), read(*fontPath), read(*catalogPath)
	src, err := png.Decode(bytes.NewReader(srcData))
	check(err)
	if src.Bounds() != image.Rect(0, 0, 1280, 800) {
		panic("expected 1280x800")
	}
	if digest(fontData) != "dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4" {
		panic("font mismatch")
	}
	parsed, err := opentype.Parse(fontData)
	check(err)
	catalog := loadCatalog(catalogData)
	unique := map[rune]bool{}
	for key, cols := range catalog {
		for lang, text := range cols {
			for _, r := range text {
				idx, err := parsed.GlyphIndex(&sfnt.Buffer{}, r)
				check(err)
				if idx == 0 {
					panic(fmt.Sprintf("missing glyph %s/%s U+%04X", key, lang, r))
				}
				unique[r] = true
			}
		}
	}
	p := painter{font: parsed, catalog: catalog}
	files := map[string]string{}
	board := image.NewRGBA(image.Rect(0, 0, 1280, 5*176))
	gray := image.NewUniform(color.RGBA{170, 170, 170, 255})
	for li, lang := range languages {
		dst := clone(src)
		for i, key := range menuKeys {
			r := image.Rect(28+i*176, 40, 164+i*176, 108)
			draw.Draw(dst, r, gray, image.Point{}, draw.Src)
			p.text(dst, key, lang, r, 56, 16, color.White)
		}
		// 原型只改六標題；逐像素檢查其他區域與真實收據相同。
		for y := 0; y < 800; y++ {
			for x := 0; x < 1280; x++ {
				inside := false
				for i := range menuKeys {
					if image.Pt(x, y).In(image.Rect(28+i*176, 40, 164+i*176, 108)) {
						inside = true
						break
					}
				}
				if !inside && dst.RGBAAt(x, y) != color.RGBAModel.Convert(src.At(x, y)).(color.RGBA) {
					panic("out-of-region change")
				}
			}
		}
		name := "city-" + lang + ".png"
		files[name] = save(filepath.Join(*out, name), dst)
		y := li * 176
		draw.Draw(board, image.Rect(0, y, 1280, y+176), image.NewUniform(color.RGBA{38, 43, 49, 255}), image.Point{}, draw.Src)
		p.text(board, "locale.name."+lang, "zh-Hant", image.Rect(0, y, 1280, y+40), 28, 16, color.White)
		draw.Draw(board, image.Rect(0, y+40, 1280, y+176), dst, image.Point{}, draw.Src)
	}
	files["five-languages.png"] = save(filepath.Join(*out, "five-languages.png"), board)
	// 只示意 F11 面板，不改遊戲或按鍵。操作方式尚待使用者決定。
	picker := clone(src)
	draw.Draw(picker, image.Rect(320, 90, 960, 718), image.NewUniform(color.RGBA{45, 51, 58, 255}), image.Point{}, draw.Src)
	p.text(picker, "locale.title", "zh-Hant", image.Rect(360, 104, 920, 164), 44, 24, color.White)
	for i, lang := range languages {
		r := image.Rect(372, 184+i*82, 908, 254+i*82)
		bg := color.RGBA{75, 82, 88, 255}
		if i == 0 {
			bg = color.RGBA{83, 109, 119, 255}
		}
		draw.Draw(picker, r, image.NewUniform(bg), image.Point{}, draw.Src)
		p.text(picker, "locale.name."+lang, "zh-Hant", r, 36, 24, color.White)
	}
	p.text(picker, "locale.hint", "zh-Hant", image.Rect(340, 614, 940, 656), 26, 16, color.White)
	p.text(picker, "locale.dismiss", "zh-Hant", image.Rect(340, 660, 940, 702), 24, 16, color.White)
	files["language-picker-draft.png"] = save(filepath.Join(*out, "language-picker-draft.png"), picker)
	receipt := map[string]any{"issue": 49, "status": "DRAFT", "product_connected": false, "input_sha256": digest(srcData), "font_sha256": digest(fontData), "catalog_sha256": digest(catalogData), "locales": languages, "keys": len(catalog), "glyphs_checked": len(unique), "missing_glyphs": []string{}, "placements": p.placements, "files": files, "out_of_region_equal": true}
	b, err := json.MarshalIndent(receipt, "", "  ")
	check(err)
	check(os.WriteFile(filepath.Join(*out, "receipt.json"), b, 0600))
	fmt.Printf("DRAFT: %d keys, %d locales, %d glyphs; %d placements fit; product not connected\n", len(catalog), len(languages), len(unique), len(p.placements))
}
