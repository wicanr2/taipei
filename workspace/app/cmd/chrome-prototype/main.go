// #29：城市框架離線原型，來源與幾何由 spec/019 審查。
package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/json"
	"flag"
	"fmt"
	xdraw "golang.org/x/image/draw"
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
func read(p string) []byte { b, e := os.ReadFile(p); must(e); return b }
func save(p string, im image.Image) string {
	var b bytes.Buffer
	must(png.Encode(&b, im))
	must(os.WriteFile(p, b.Bytes(), 0644))
	return hash(b.Bytes())
}
func scaled(dst *image.RGBA, r image.Rectangle, src image.Image, b int) {
	s := src.Bounds()
	xs, ys := []int{0, b, s.Dx() - b, s.Dx()}, []int{0, b, s.Dy() - b, s.Dy()}
	xd, yd := []int{r.Min.X, r.Min.X + b, r.Max.X - b, r.Max.X}, []int{r.Min.Y, r.Min.Y + b, r.Max.Y - b, r.Max.Y}
	for y := 0; y < 3; y++ {
		for x := 0; x < 3; x++ {
			xdraw.CatmullRom.Scale(dst, image.Rect(xd[x], yd[y], xd[x+1], yd[y+1]), src, image.Rect(xs[x], ys[y], xs[x+1], ys[y+1]), draw.Src, nil)
		}
	}
}
func bounds(im *image.RGBA) image.Rectangle {
	r := image.Rectangle{}
	for y := 0; y < im.Bounds().Dy(); y++ {
		for x := 0; x < im.Bounds().Dx(); x++ {
			if im.Pix[im.PixOffset(x, y)+3] > 0 {
				r = r.Union(image.Rect(x, y, x+1, y+1))
			}
		}
	}
	if r.Empty() {
		panic("空白墨跡")
	}
	return r
}
func main() {
	dir := flag.String("materials", "", "本機素材")
	out := flag.String("out", "", "本機原型")
	flag.Parse()
	if *dir == "" || *out == "" {
		panic("缺少路徑")
	}
	must(os.MkdirAll(*out, 0755))
	artHashes := map[string]string{
		"city-chrome-gray-v1.png":       "6532e1daf962bb4abeed7a4c0a186a0ee9b606d4273d6d8ee5fce46e462efd37",
		"city-chrome-lime-v1.png":       "73948266299d3a892614da7f13a5ca67cdd097867348f16c5b0539a4440c83c7",
		"city-chrome-pillar-v1.png":     "6cb9632af1cae98aad40736659bc14d1db8cf69dbd6d4e3711b8f5e48f331fbd",
		"font-comparison/noto-font.png": "feefbf252a77ab01322c72654a2c6d8b7cb42118494949604f194c20d4f331da",
	}
	arts := map[string]image.Image{}
	for name, want := range artHashes {
		raw := read(filepath.Join(*dir, name))
		if hash(raw) != want {
			panic(name + " 失配")
		}
		im, e := png.Decode(bytes.NewReader(raw))
		must(e)
		arts[name] = im
	}
	fontRaw := read(filepath.Join(*dir, "fonts/NotoSansCJKtc-Regular.otf"))
	if hash(fontRaw) != "dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4" {
		panic("字型失配")
	}
	if hash(read(filepath.Join(*dir, "fonts/LICENSE"))) != "6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2" {
		panic("字型授權失配")
	}
	parsed, e := opentype.Parse(fontRaw)
	must(e)
	face, e := opentype.NewFace(parsed, &opentype.FaceOptions{Size: 28, DPI: 72, Hinting: font.HintingNone})
	must(e)
	defer face.Close()
	frame := image.NewRGBA(image.Rect(0, 0, 1280, 800))
	gray, lime, pillar := arts["city-chrome-gray-v1.png"], arts["city-chrome-lime-v1.png"], arts["city-chrome-pillar-v1.png"]
	// 地圖、底部動態欄位及工具內部不屬於本批；執行時依審查遮罩取像素。
	scaled(frame, image.Rect(0, 0, 1080, 696), gray, 16)
	scaled(frame, image.Rect(0, 0, 1080, 136), gray, 12)
	for i := 0; i < 7; i++ {
		r := image.Rect(-4+176*i, 20, 28+176*i, 124)
		draw.Draw(frame, r, pillar, image.Point{}, draw.Over)
	}
	var inkChecks []map[string]any
	for i := 0; i < 6; i++ {
		r := image.Rect(28+176*i, 40, 164+176*i, 108)
		draw.Draw(frame, r, arts["font-comparison/noto-font.png"], r.Min, draw.Src)
		text := fmt.Sprintf("F%d", i+1)
		for _, ch := range text {
			g, e := parsed.GlyphIndex(&sfnt.Buffer{}, ch)
			must(e)
			if g == 0 {
				panic("缺字")
			}
		}
		glyph := image.NewRGBA(image.Rect(0, 0, 96, 48))
		d := font.Drawer{Dst: glyph, Src: image.NewUniform(color.RGBA{255, 247, 0, 255}), Face: face, Dot: fixed.P(4, 36)}
		d.DrawString(text)
		ink := bounds(glyph)
		safe := image.Rect(72+176*i, 4, 148+176*i, 36)
		if ink.Dx() > safe.Dx() || ink.Dy() > safe.Dy() {
			panic("F 鍵裁切")
		}
		at := image.Pt(safe.Min.X+(safe.Dx()-ink.Dx())/2, safe.Min.Y+(safe.Dy()-ink.Dy())/2)
		target := image.Rectangle{Min: at, Max: at.Add(ink.Size())}
		draw.Draw(frame, safe, image.NewUniform(color.RGBA{65, 65, 0, 255}), image.Point{}, draw.Src)
		draw.Draw(frame, target, glyph, ink.Min, draw.Over)
		inkChecks = append(inkChecks, map[string]any{"text": text, "safe": safe, "actual_ink": target, "missing_glyph": false, "clipped": false})
	}
	scaled(frame, image.Rect(1080, 0, 1280, 696), lime, 8)
	scaled(frame, image.Rect(0, 696, 1280, 800), gray, 8)
	ringAtlas := image.NewRGBA(image.Rect(0, 0, 264, 88))
	colors := [][3]byte{{255, 255, 255}, {255, 0, 0}, {182, 0, 182}}
	for i, c := range colors {
		for y := 0; y < 88; y++ {
			for x := 0; x < 88; x++ {
				if x >= 4 && x < 84 && y >= 4 && y < 84 {
					continue
				}
				distance := min(x, y, 87-x, 87-y)
				shade := []float64{0.70, 1.0, 0.88, 0.62}[distance]
				ringAtlas.SetRGBA(i*88+x, y, color.RGBA{byte(float64(c[0]) * shade), byte(float64(c[1]) * shade), byte(float64(c[2]) * shade), 255})
			}
		}
	}
	frameSHA := save(filepath.Join(*out, "frame.png"), frame)
	ringSHA := save(filepath.Join(*out, "rings.png"), ringAtlas)
	manifest := map[string]any{"schema": 1, "scope": "019 城市框架與十四外框；不包含動態底部文字或工具子選單", "frame_sha256": frameSHA, "rings_sha256": ringSHA, "frame_size": []int{1280, 800}, "rings_size": []int{264, 88}, "art_sha256": artHashes, "font_sha256": hash(fontRaw), "font_size_fkeys": 28, "ink_checks": inkChecks}
	raw, e := json.MarshalIndent(manifest, "", "  ")
	must(e)
	raw = append(raw, '\n')
	must(os.WriteFile(filepath.Join(*out, "manifest.json"), raw, 0644))
	fmt.Printf("frame %s\nrings %s\nmanifest %s\n", frameSHA, ringSHA, hash(raw))
}
