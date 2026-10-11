// #39：完整預算離線原型，不能由產品入口呼叫。
package main

import (
	"archive/zip"
	"bytes"
	"crypto/sha256"
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
	"strconv"
	"strings"

	xdraw "golang.org/x/image/draw"
	"golang.org/x/image/font"
	"golang.org/x/image/font/opentype"
	"golang.org/x/image/font/sfnt"
	"golang.org/x/image/math/fixed"
)

func must(e error) {
	if e != nil {
		panic(e)
	}
}
func hash(b []byte) string { return fmt.Sprintf("%x", sha256.Sum256(b)) }
func read(p string) []byte { b, e := os.ReadFile(p); must(e); return b }
func fixedInput(p, want string) []byte {
	b := read(p)
	if len(want) != 64 || hash(b) != want {
		panic("輸入雜湊失配：" + p)
	}
	return b
}
func pngBytes(im image.Image) []byte { var b bytes.Buffer; must(png.Encode(&b, im)); return b.Bytes() }

type cell struct {
	Text             string
	X, Y, W, H, Size int
}
type layout struct {
	Schema     int      `json:"schema"`
	ROMSHA     string   `json:"rom_sha256"`
	DecodedSHA string   `json:"decoded_sha256"`
	Cells      []cell   `json:"cells"`
	Panels     [][4]int `json:"panels"`
}
type field struct {
	Text                 string
	X, Y, Columns, Color int
}
type sample struct {
	Receipt    string
	ReceiptSHA string                   `json:"receipt_sha256"`
	Source     struct{ Fields []field } `json:"source"`
}

func main() {
	dir := flag.String("materials", "", "本機固定素材根")
	source := flag.String("source", "", "完整來源 catalog")
	sourceSHA := flag.String("source-sha", "", "來源 SHA-256")
	annotation := flag.String("layout", "", "本機烘製文字與原位轉錄")
	layoutSHA := flag.String("layout-sha", "", "轉錄 SHA-256")
	out := flag.String("out", "", "本機離線原型輸出")
	flag.Parse()
	sourceRaw := fixedInput(*source, *sourceSHA)
	var catalog struct {
		ROMSHA  string `json:"rom_sha256"`
		Native  []int
		Samples []sample
	}
	must(json.Unmarshal(sourceRaw, &catalog))
	if catalog.ROMSHA != "0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29" || len(catalog.Native) != 4 || fmt.Sprint(catalog.Native) != "[18 37 235 132]" || len(catalog.Samples) == 0 {
		panic("來源形狀失配")
	}
	layoutRaw := fixedInput(*annotation, *layoutSHA)
	var content layout
	must(json.Unmarshal(layoutRaw, &content))
	if content.Schema != 1 || content.ROMSHA != catalog.ROMSHA || content.DecodedSHA != "db92d35996a6c8fc112d129ab0a92d1018384495cd38b31d637df468b52c7967" || len(content.Cells) == 0 {
		panic("轉錄來源失配")
	}
	fontRaw := fixedInput(filepath.Join(*dir, "fonts/NotoSansCJKtc-Regular.otf"), "dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4")
	license := fixedInput(filepath.Join(*dir, "fonts/LICENSE"), "6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2")
	blueRaw := fixedInput(filepath.Join(*dir, "menu-blue-b-v1.png"), "eeb1aa620c179a7fa0233bdfc9d9ad6abf8719d36f1ad05dc93c84343a164ea9")
	blue, e := png.Decode(bytes.NewReader(blueRaw))
	must(e)
	parsed, e := opentype.Parse(fontRaw)
	must(e)
	faces := map[int]font.Face{}
	face := func(size int) font.Face {
		if f := faces[size]; f != nil {
			return f
		}
		f, e := opentype.NewFace(parsed, &opentype.FaceOptions{Size: float64(size), DPI: 72, Hinting: font.HintingNone})
		must(e)
		faces[size] = f
		return f
	}
	defer func() {
		for _, f := range faces {
			must(f.Close())
		}
	}()
	var checks []map[string]any
	inkGlyph := func(text string, size, w, h int, fg color.RGBA) (*image.RGBA, image.Rectangle) {
		runes := []rune(text)
		if len(runes) != 1 {
			panic("單字契約")
		}
		gi, e := parsed.GlyphIndex(&sfnt.Buffer{}, runes[0])
		must(e)
		if gi == 0 {
			panic("Noto 缺字")
		}
		layer := image.NewRGBA(image.Rect(0, 0, 160, 160))
		d := font.Drawer{Dst: layer, Src: image.NewUniform(fg), Face: face(size), Dot: fixed.P(32, 96)}
		d.DrawString(text)
		ink := image.Rectangle{}
		for y := 0; y < 160; y++ {
			for x := 0; x < 160; x++ {
				if layer.RGBAAt(x, y).A != 0 {
					ink = ink.Union(image.Rect(x, y, x+1, y+1))
				}
			}
		}
		if (ink.Empty() && text != " ") || ink.Dx() > w || ink.Dy() > h {
			panic(fmt.Sprintf("墨跡越界 %q %v / %dx%d", text, ink, w, h))
		}
		return layer, ink
	}
	panel := image.NewRGBA(image.Rect(0, 0, 940, 528))
	staticInk := image.NewRGBA(panel.Bounds())
	paintPanel := func(dst image.Rectangle, dim uint8) {
		if !dst.In(panel.Bounds()) || dst.Empty() {
			panic("面板越界")
		}
		sb := blue.Bounds()
		b := 8
		xs, ys := []int{0, b, sb.Dx() - b, sb.Dx()}, []int{0, b, sb.Dy() - b, sb.Dy()}
		xd, yd := []int{dst.Min.X, dst.Min.X + b, dst.Max.X - b, dst.Max.X}, []int{dst.Min.Y, dst.Min.Y + b, dst.Max.Y - b, dst.Max.Y}
		for y := 0; y < 3; y++ {
			for x := 0; x < 3; x++ {
				xdraw.CatmullRom.Scale(panel, image.Rect(xd[x], yd[y], xd[x+1], yd[y+1]), blue, image.Rect(xs[x], ys[y], xs[x+1], ys[y+1]), draw.Src, nil)
			}
		}
		for y := dst.Min.Y; y < dst.Max.Y; y++ {
			for x := dst.Min.X; x < dst.Max.X; x++ {
				at := panel.PixOffset(x, y)
				for c := 0; c < 3; c++ {
					panel.Pix[at+c] /= dim
				}
			}
		}
	}
	paintPanel(panel.Bounds(), 5)
	for _, p := range content.Panels {
		paintPanel(image.Rect(p[0]*4, p[1]*4, (p[0]+p[2])*4, (p[1]+p[3])*4), 3)
	}
	for i, c := range content.Cells {
		layer, ink := inkGlyph(c.Text, c.Size, c.W*4, c.H*4, color.RGBA{255, 255, 255, 255})
		safe := image.Rect(c.X*4, c.Y*4, (c.X+c.W)*4, (c.Y+c.H)*4)
		if !safe.In(panel.Bounds()) {
			panic("靜態文字越界")
		}
		at := safe.Min.Add(image.Pt((safe.Dx()-ink.Dx())/2, (safe.Dy()-ink.Dy())/2))
		placed := image.Rectangle{Min: at, Max: at.Add(ink.Size())}
		draw.Draw(panel, placed, layer, ink.Min, draw.Over)
		draw.Draw(staticInk, placed, layer, ink.Min, draw.Over)
		checks = append(checks, map[string]any{"kind": "static", "index": i, "text": c.Text, "font_size": c.Size, "safe": safe, "actual_ink": placed, "missing_glyph": false, "clipped": false})
	}
	const chars = " -0123456789"
	atlas := image.NewRGBA(image.Rect(0, 0, 24*len(chars), 56))
	for group, fg := range []color.RGBA{{255, 255, 255, 255}, {255, 0, 0, 255}} {
		for i, ch := range chars {
			layer, ink := inkGlyph(string(ch), 32, 24, 28, fg)
			safe := image.Rect(i*24, group*28, (i+1)*24, (group+1)*28)
			at := safe.Min.Add(image.Pt((24-ink.Dx())/2, (28-ink.Dy())/2))
			placed := image.Rectangle{Min: at, Max: at.Add(ink.Size())}
			if !ink.Empty() {
				draw.Draw(atlas, placed, layer, ink.Min, draw.Over)
			}
			checks = append(checks, map[string]any{"kind": "number", "index": group*len(chars) + i, "text": string(ch), "font_size": 32, "safe": safe, "actual_ink": placed, "missing_glyph": false, "clipped": false})
		}
	}
	must(os.MkdirAll(*out, 0700))
	images := map[string]string{}
	for name, im := range map[string]image.Image{"panel.png": panel, "static-ink.png": staticInk, "glyphs.png": atlas} {
		b := pngBytes(im)
		must(os.WriteFile(filepath.Join(*out, name), b, 0600))
		images[name] = hash(b)
	}
	var proofs []map[string]any
	selected := map[int]bool{}
	nonzeroProof := false
	for _, s := range catalog.Samples {
		row := -1
		for i, f := range s.Source.Fields {
			if i < 5 && f.Color == 12 {
				row = i
			}
		}
		nonzero := false
		for i, f := range s.Source.Fields {
			if i >= 5 {
				value, err := strconv.ParseInt(strings.TrimSpace(f.Text), 10, 32)
				must(err)
				nonzero = nonzero || value != 0
			}
		}
		extra := row >= 0 && selected[row] && nonzero && !nonzeroProof
		if row < 0 || (selected[row] && !extra) {
			continue
		}
		selected[row] = true
		nonzeroProof = nonzeroProof || nonzero
		zr, e := zip.NewReader(bytes.NewReader(fixedInput(s.Receipt, s.ReceiptSHA)), int64(len(read(s.Receipt))))
		must(e)
		var native image.Image
		for _, f := range zr.File {
			if f.Name == "frame.png" {
				r, e := f.Open()
				must(e)
				raw, e := io.ReadAll(r)
				must(e)
				must(r.Close())
				native, e = png.Decode(bytes.NewReader(raw))
				must(e)
			}
		}
		if native == nil || native.Bounds() != image.Rect(0, 0, 320, 200) {
			panic("原始畫面失配")
		}
		preview := image.NewRGBA(image.Rect(0, 0, 1280, 800))
		xdraw.NearestNeighbor.Scale(preview, preview.Bounds(), native, native.Bounds(), draw.Src, nil)
		draw.Draw(preview, image.Rect(72, 148, 1012, 676), panel, image.Point{}, draw.Src)
		for _, f := range s.Source.Fields {
			if len(f.Text) != f.Columns || (f.Color != 0 && f.Color != 12) {
				panic("動態欄位失配")
			}
			for col, ch := range f.Text {
				index := bytes.IndexByte([]byte(chars), byte(ch))
				if index < 0 {
					panic("未知數字字形")
				}
				y := 0
				if f.Color == 12 {
					y = 28
				}
				x := (18 + f.X + col*6) * 4
				yy := (37 + f.Y) * 4
				draw.Draw(preview, image.Rect(x, yy, x+24, yy+28), atlas, image.Pt(index*24, y), draw.Over)
			}
		}
		name := fmt.Sprintf("proof-row-%d.png", row)
		if extra {
			name = "proof-nonzero.png"
		}
		b := pngBytes(preview)
		must(os.WriteFile(filepath.Join(*out, name), b, 0600))
		images[name] = hash(b)
		proofs = append(proofs, map[string]any{"selection": row, "receipt": s.Receipt, "receipt_sha256": s.ReceiptSHA, "image": name, "image_sha256": hash(b), "nonzero_amounts": nonzero})
	}
	if len(selected) != 5 {
		panic("缺少五列正常來源")
	}
	manifest := map[string]any{"schema": 1, "sources_sha256": *sourceSHA, "layout_sha256": *layoutSHA, "font_sha256": hash(fontRaw), "license_sha256": hash(license), "art_sha256": hash(blueRaw), "native": catalog.Native, "images": images, "atlas_characters": chars, "atlas_size": []int{atlas.Bounds().Dx(), 56}, "ink_checks": checks, "proofs": proofs, "scope": "離線原型，不是正式產品 HD 收據"}
	b, e := json.MarshalIndent(manifest, "", "  ")
	must(e)
	b = append(b, '\n')
	must(os.WriteFile(filepath.Join(*out, "manifest.json"), b, 0600))
	fmt.Printf("%d 實際墨跡；%d 正常來源原位原型；非零金額=%v；manifest %s\n", len(checks), len(proofs), nonzeroProof, hash(b))
}
