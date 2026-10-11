// #31：離線固定 Noto 字形參考；不讀取遊戲狀態。
package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/json"
	"flag"
	"fmt"
	"golang.org/x/image/font"
	"golang.org/x/image/font/opentype"
	"golang.org/x/image/font/sfnt"
	"golang.org/x/image/math/fixed"
	"image"
	"image/color"
	"image/draw"
	"image/png"
	"os"
	"path/filepath"
)

func must(e error) {
	if e != nil {
		panic(e)
	}
}
func hash(p []byte) string { return fmt.Sprintf("%x", sha256.Sum256(p)) }
func main() {
	dir := flag.String("materials", "", "固定素材根")
	out := flag.String("out", "", "本機輸出")
	flag.Parse()
	raw, e := os.ReadFile(filepath.Join(*dir, "fonts/NotoSansCJKtc-Regular.otf"))
	must(e)
	if hash(raw) != "dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4" {
		panic("字型失配")
	}
	license, e := os.ReadFile(filepath.Join(*dir, "fonts/LICENSE"))
	must(e)
	if hash(license) != "6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2" {
		panic("授權失配")
	}
	parsed, e := opentype.Parse(raw)
	must(e)
	atlas := image.NewRGBA(image.Rect(0, 0, 384, 192))
	var checks []map[string]any
	groups := []struct {
		text string
		size float64
		w, h int
		c    color.RGBA
	}{{"0123456789-", 28, 24, 28, color.RGBA{255, 255, 255, 255}}, {"每單位萬", 52, 60, 56, color.RGBA{255, 0, 0, 255}}, {"年月萬", 28, 28, 28, color.RGBA{0, 0, 170, 255}}}
	index := 0
	for _, g := range groups {
		face, e := opentype.NewFace(parsed, &opentype.FaceOptions{Size: g.size, DPI: 72, Hinting: font.HintingNone})
		must(e)
		for _, ch := range g.text {
			gi, e := parsed.GlyphIndex(&sfnt.Buffer{}, ch)
			must(e)
			if gi == 0 {
				panic("缺字")
			}
			layer := image.NewRGBA(image.Rect(0, 0, 128, 128))
			d := font.Drawer{Dst: layer, Src: image.NewUniform(g.c), Face: face, Dot: fixed.P(20, 80)}
			d.DrawString(string(ch))
			ink := image.Rectangle{}
			for y := 0; y < 128; y++ {
				for x := 0; x < 128; x++ {
					if layer.RGBAAt(x, y).A != 0 {
						ink = ink.Union(image.Rect(x, y, x+1, y+1))
					}
				}
			}
			if ink.Empty() || ink.Dx() > g.w || ink.Dy() > g.h {
				panic(fmt.Sprintf("墨跡越界 %c %v", ch, ink))
			}
			at := image.Pt(index%6*64+(g.w-ink.Dx())/2, index/6*64+(g.h-ink.Dy())/2)
			target := image.Rectangle{Min: at, Max: at.Add(ink.Size())}
			safe := image.Rect(index%6*64, index/6*64, index%6*64+g.w, index/6*64+g.h)
			draw.Draw(atlas, target, layer, ink.Min, draw.Over)
			checks = append(checks, map[string]any{"index": index, "text": string(ch), "font_size": g.size, "safe": safe, "actual_ink": target, "missing_glyph": false, "clipped": false})
			index++
		}
		must(face.Close())
	}
	var b bytes.Buffer
	must(png.Encode(&b, atlas))
	must(os.MkdirAll(*out, 0755))
	must(os.WriteFile(filepath.Join(*out, "glyphs.png"), b.Bytes(), 0644))
	m := map[string]any{"schema": 1, "font_sha256": hash(raw), "license_sha256": hash(license), "glyphs_sha256": hash(b.Bytes()), "size": []int{384, 192}, "ink_checks": checks}
	p, e := json.MarshalIndent(m, "", "  ")
	must(e)
	p = append(p, '\n')
	must(os.WriteFile(filepath.Join(*out, "manifest.json"), p, 0644))
	fmt.Println("glyphs", hash(b.Bytes()), "manifest", hash(p))
}
