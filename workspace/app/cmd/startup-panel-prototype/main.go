// #31：可丟棄的離線面板原型；不接入 DOS 執行路徑。
package main

import (
	"bytes"
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

	xdraw "golang.org/x/image/draw"
	"golang.org/x/image/font"
	"golang.org/x/image/font/opentype"
	"golang.org/x/image/font/sfnt"
	"golang.org/x/image/math/fixed"
)

const fontSHA = "dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4"
const licenseSHA = "6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2"
const layoutSHA = "55d977d8da010783bb5a1e0836e6597458dba33a069f83163f0693ff6de264ee"
const sourcesSHA = "cbe20400432e71d7ed21bba29d2fb2ae8c5d118d24842b8f2ed98d9c867f3ab6"

type cell struct {
	Text                 string
	X, Y, Option, Button int
	Size                 float64
	Color                [3]byte
	FitInk               []int `json:"fit_ink"`
}
type scene struct {
	ID            string
	Native        [4]int
	Background    string
	Border        int `json:"background_border"`
	Separator     int
	SelectedColor [3]byte `json:"selected_color"`
	OtherColor    [3]byte `json:"other_color"`
	Buttons       []struct {
		Rect [4]int
		Art  string
	}
	Cells []cell
}
type source struct {
	ID         string `json:"id"`
	Selection  int    `json:"selection"`
	Native     [4]int `json:"native"`
	SourceSHA  string `json:"source_sha256"`
	Indices    []int  `json:"palette_indices"`
	PaletteSHA string `json:"palette_sha256"`
	Image      string `json:"image"`
	ImageSHA   string `json:"image_sha256"`
}

func must(e error) {
	if e != nil {
		panic(e)
	}
}
func hash(p []byte) string    { return fmt.Sprintf("%x", sha256.Sum256(p)) }
func read(path string) []byte { p, e := os.ReadFile(path); must(e); return p }
func alphaBounds(im *image.RGBA) image.Rectangle {
	box := image.Rectangle{}
	for y := im.Bounds().Min.Y; y < im.Bounds().Max.Y; y++ {
		for x := im.Bounds().Min.X; x < im.Bounds().Max.X; x++ {
			if im.Pix[im.PixOffset(x, y)+3] != 0 {
				box = box.Union(image.Rect(x, y, x+1, y+1))
			}
		}
	}
	if box.Empty() {
		panic("字形沒有實際墨跡")
	}
	return box
}
func nativeRect(r [4]int) image.Rectangle {
	return image.Rect(r[0]*4, r[1]*4, (r[0]+r[2])*4, (r[1]+r[3])*4)
}
func scale(dst *image.RGBA, target image.Rectangle, src image.Image, border int) {
	if border == 0 {
		xdraw.CatmullRom.Scale(dst, target, src, src.Bounds(), draw.Src, nil)
		return
	}
	s := src.Bounds()
	xs, ys := []int{s.Min.X, s.Min.X + border, s.Max.X - border, s.Max.X}, []int{s.Min.Y, s.Min.Y + border, s.Max.Y - border, s.Max.Y}
	xd, yd := []int{target.Min.X, target.Min.X + border, target.Max.X - border, target.Max.X}, []int{target.Min.Y, target.Min.Y + border, target.Max.Y - border, target.Max.Y}
	for y := 0; y < 3; y++ {
		for x := 0; x < 3; x++ {
			xdraw.CatmullRom.Scale(dst, image.Rect(xd[x], yd[y], xd[x+1], yd[y+1]), src, image.Rect(xs[x], ys[y], xs[x+1], ys[y+1]), draw.Src, nil)
		}
	}
}
func main() {
	dir := flag.String("materials", "", "本機固定素材目錄")
	out := flag.String("out", "", "本機離線面板輸出目錄")
	flag.Parse()
	if *dir == "" || *out == "" {
		panic("請指定素材與輸出")
	}
	layoutRaw := read(filepath.Join(*dir, "startup-menu-layout-v1.json"))
	if hash(layoutRaw) != layoutSHA {
		panic("轉錄與幾何資料失配")
	}
	var layout struct {
		Schema int
		Arts   map[string]string `json:"art_sha256"`
		Scenes []scene
	}
	must(json.Unmarshal(layoutRaw, &layout))
	if layout.Schema != 1 || len(layout.Scenes) != 3 {
		panic("版面形狀失配")
	}
	sourceRaw := read(filepath.Join(*dir, "startup-menu-sources-v1.json"))
	if hash(sourceRaw) != sourcesSHA {
		panic("已審查來源雜湊失配")
	}
	var catalog struct {
		Schema    int
		LayoutSHA string `json:"layout_sha256"`
		ROMSHA    string `json:"rom_sha256"`
		States    []source
	}
	must(json.Unmarshal(sourceRaw, &catalog))
	if catalog.Schema != 1 || catalog.LayoutSHA != layoutSHA || catalog.ROMSHA != "0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29" || len(catalog.States) != 13 {
		panic("來源審查資料失配")
	}
	raw := read(filepath.Join(*dir, "fonts", "NotoSansCJKtc-Regular.otf"))
	if hash(raw) != fontSHA {
		panic("Noto 字型失配")
	}
	if hash(read(filepath.Join(*dir, "fonts", "LICENSE"))) != licenseSHA {
		panic("字型授權失配")
	}
	parsed, e := opentype.Parse(raw)
	must(e)
	faces := map[float64]font.Face{}
	defer func() {
		for _, f := range faces {
			f.Close()
		}
	}()
	faceFor := func(size float64) font.Face {
		if faces[size] == nil {
			f, e := opentype.NewFace(parsed, &opentype.FaceOptions{Size: size, DPI: 72, Hinting: font.HintingNone})
			must(e)
			faces[size] = f
		}
		return faces[size]
	}
	arts := map[string]image.Image{}
	for name, want := range layout.Arts {
		if filepath.Base(name) != name {
			panic("資產路徑越界")
		}
		p := read(filepath.Join(*dir, name))
		if hash(p) != want {
			panic("B 素材失配: " + name)
		}
		im, e := png.Decode(bytes.NewReader(p))
		must(e)
		arts[name] = im
	}
	byID := map[string]scene{}
	for _, s := range layout.Scenes {
		byID[s.ID] = s
	}
	must(os.MkdirAll(*out, 0700))
	var inks []map[string]any
	for i := range catalog.States {
		r := &catalog.States[i]
		s, ok := byID[r.ID]
		if !ok || s.Native != r.Native {
			panic("場景幾何不同於來源")
		}
		im := image.NewRGBA(image.Rect(0, 0, s.Native[2]*4, s.Native[3]*4))
		scale(im, im.Bounds(), arts[s.Background], s.Border)
		if s.Separator > 0 {
			bg := arts[s.Background]
			b := bg.Bounds()
			xdraw.CatmullRom.Scale(im, image.Rect(16, s.Separator*4, im.Bounds().Dx()-16, s.Separator*4+16), bg, image.Rect(16, b.Max.Y-16, b.Max.X-16, b.Max.Y), draw.Src, nil)
		}
		for _, b := range s.Buttons {
			scale(im, nativeRect(b.Rect), arts[b.Art], 8)
		}
		for ci, c := range s.Cells {
			for _, ch := range c.Text {
				glyph, e := parsed.GlyphIndex(&sfnt.Buffer{}, ch)
				must(e)
				if glyph == 0 {
					panic("缺字")
				}
			}
			fg := c.Color
			if fg == [3]byte{} {
				fg = [3]byte{255, 255, 255}
			}
			if c.Option >= 0 {
				fg = s.OtherColor
				if c.Option == r.Selection {
					fg = s.SelectedColor
				}
			}
			paint := image.NewUniform(color.RGBA{fg[0], fg[1], fg[2], 255})
			face := faceFor(c.Size)
			var ink image.Rectangle
			var actual image.Rectangle
			if len(c.FitInk) == 4 {
				probe := image.NewRGBA(image.Rect(0, 0, 640, 640))
				dot := fixed.P(32, 550)
				bounds, _ := font.BoundString(face, c.Text)
				placed := bounds.Add(dot)
				from := image.Rect(placed.Min.X.Floor(), placed.Min.Y.Floor(), placed.Max.X.Ceil(), placed.Max.Y.Ceil())
				if !from.In(probe.Bounds()) {
					panic("大字原始墨跡越界")
				}
				p := font.Drawer{Dst: probe, Src: paint, Face: face, Dot: dot}
				p.DrawString(c.Text)
				if !alphaBounds(probe).In(from) {
					panic("字型邊界裁掉實際墨跡")
				}
				ink = nativeRect([4]int{c.FitInk[0], c.FitInk[1], c.FitInk[2], c.FitInk[3]})
				if !ink.In(im.Bounds().Inset(16)) {
					panic("標題墨跡越界")
				}
				xdraw.CatmullRom.Scale(im, ink, probe, from, draw.Over, nil)
				mask := image.NewRGBA(im.Bounds())
				xdraw.CatmullRom.Scale(mask, ink, probe, from, draw.Over, nil)
				actual = alphaBounds(mask)
			} else {
				dot := fixed.P(c.X*4+4, c.Y*4+50)
				bounds, _ := font.BoundString(face, c.Text)
				placed := bounds.Add(dot)
				ink = image.Rect(placed.Min.X.Floor(), placed.Min.Y.Floor(), placed.Max.X.Ceil(), placed.Max.Y.Ceil())
				if c.Button < 0 || c.Button >= len(s.Buttons) || !ink.In(nativeRect(s.Buttons[c.Button].Rect).Inset(8)) || !ink.In(image.Rect(c.X*4, c.Y*4, c.X*4+64, c.Y*4+64)) {
					panic(fmt.Sprintf("文字墨跡越界: %s %d", s.ID, ci))
				}
				p := font.Drawer{Dst: im, Src: paint, Face: face, Dot: dot}
				p.DrawString(c.Text)
				mask := image.NewRGBA(image.Rect(0, 0, 64, 64))
				p = font.Drawer{Dst: mask, Src: paint, Face: face, Dot: fixed.P(4, 50)}
				p.DrawString(c.Text)
				actual = alphaBounds(mask).Add(image.Pt(c.X*4, c.Y*4))
			}
			if !actual.In(ink) {
				panic("實際墨跡超出已核對邊界")
			}
			inks = append(inks, map[string]any{"scene": r.ID, "selection": r.Selection, "cell": ci, "ink": ink, "actual_ink": actual, "contained": true})
		}
		r.Image = fmt.Sprintf("startup-%s-%d.png", r.ID, r.Selection)
		var pngBytes bytes.Buffer
		must(png.Encode(&pngBytes, im))
		r.ImageSHA = hash(pngBytes.Bytes())
		must(os.WriteFile(filepath.Join(*out, r.Image), pngBytes.Bytes(), 0600))
	}
	manifest := map[string]any{"schema": 1, "font_sha256": fontSHA, "license_sha256": licenseSHA, "layout_sha256": layoutSHA, "sources_sha256": hash(sourceRaw), "states": catalog.States}
	p, e := json.MarshalIndent(manifest, "", "  ")
	must(e)
	p = append(p, '\n')
	must(os.WriteFile(filepath.Join(*out, "manifest.json"), p, 0600))
	v, e := json.MarshalIndent(map[string]any{"font_sha256": fontSHA, "states": 13, "all_ink_contained": true, "samples": inks}, "", "  ")
	must(e)
	must(os.WriteFile(filepath.Join(*out, "ink-verification.json"), append(v, '\n'), 0600))
	fmt.Printf("十三個離線選取狀態已重生；manifest SHA-256 %s\n", hash(p))
}
