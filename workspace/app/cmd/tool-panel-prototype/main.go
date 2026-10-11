// #31：五工具子選單的離線 B 素材與 Noto 組合，不執行 DOS。
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
	"strings"

	xdraw "golang.org/x/image/draw"
	"golang.org/x/image/font"
	"golang.org/x/image/font/opentype"
	"golang.org/x/image/font/sfnt"
	"golang.org/x/image/math/fixed"
)

const fontSHA = "dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4"
const licenseSHA = "6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2"

type scene struct {
	ID         string
	Native     [4]int
	Background string
	Border     int `json:"background_border"`
	Buttons    []struct {
		Rect [4]int
		Art  string
	}
	Cells []struct {
		Text                string
		X, Y, Option, Index int
		Size                float64
	}
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

func must(err error) {
	if err != nil {
		panic(err)
	}
}
func hash(b []byte) string          { return fmt.Sprintf("%x", sha256.Sum256(b)) }
func read(p string) []byte          { b, e := os.ReadFile(p); must(e); return b }
func rect(r [4]int) image.Rectangle { return image.Rect(r[0]*4, r[1]*4, (r[0]+r[2])*4, (r[1]+r[3])*4) }
func alphaBounds(im *image.RGBA) image.Rectangle {
	b := image.Rectangle{}
	for y := 0; y < im.Bounds().Dy(); y++ {
		for x := 0; x < im.Bounds().Dx(); x++ {
			if im.Pix[im.PixOffset(x, y)+3] > 0 {
				b = b.Union(image.Rect(x, y, x+1, y+1))
			}
		}
	}
	return b
}
func scale(dst *image.RGBA, target image.Rectangle, src image.Image, border int) {
	s := src.Bounds()
	xs, ys := []int{0, border, s.Dx() - border, s.Dx()}, []int{0, border, s.Dy() - border, s.Dy()}
	xd, yd := []int{target.Min.X, target.Min.X + border, target.Max.X - border, target.Max.X}, []int{target.Min.Y, target.Min.Y + border, target.Max.Y - border, target.Max.Y}
	for y := 0; y < 3; y++ {
		for x := 0; x < 3; x++ {
			xdraw.CatmullRom.Scale(dst, image.Rect(xd[x], yd[y], xd[x+1], yd[y+1]), src, image.Rect(xs[x], ys[y], xs[x+1], ys[y+1]), draw.Src, nil)
		}
	}
}
func main() {
	dir := flag.String("materials", "", "本機素材根")
	out := flag.String("out", "", "本機完整面板輸出")
	layoutSHA := flag.String("layout-sha", "", "已審查版面 SHA-256")
	sourcesSHA := flag.String("sources-sha", "", "已審查來源 SHA-256")
	flag.Parse()
	if *dir == "" || *out == "" || len(*layoutSHA) != 64 || len(*sourcesSHA) != 64 {
		panic("需指定素材、輸出及兩項已審查 SHA-256")
	}
	layoutRaw := read(filepath.Join(*dir, "tool-menu-layout-v1.json"))
	sourceRaw := read(filepath.Join(*dir, "tool-menu-sources-v1.json"))
	if hash(layoutRaw) != *layoutSHA || hash(sourceRaw) != *sourcesSHA {
		panic("來源或版面失配")
	}
	var layout struct {
		Schema int
		Arts   map[string]string `json:"art_sha256"`
		Scenes []scene
	}
	var catalog struct {
		Schema    int
		LayoutSHA string `json:"layout_sha256"`
		ROMSHA    string `json:"rom_sha256"`
		States    []source
	}
	must(json.Unmarshal(layoutRaw, &layout))
	must(json.Unmarshal(sourceRaw, &catalog))
	if layout.Schema != 1 || len(layout.Scenes) != 5 || catalog.Schema != 1 || len(catalog.States) != 18 || catalog.LayoutSHA != *layoutSHA || catalog.ROMSHA != "0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29" {
		panic("來源形狀失配")
	}
	raw := read(filepath.Join(*dir, "fonts", "NotoSansCJKtc-Regular.otf"))
	if hash(raw) != fontSHA || hash(read(filepath.Join(*dir, "fonts", "LICENSE"))) != licenseSHA {
		panic("字型或授權失配")
	}
	parsed, e := opentype.Parse(raw)
	must(e)
	face, e := opentype.NewFace(parsed, &opentype.FaceOptions{Size: 52, DPI: 72, Hinting: font.HintingNone})
	must(e)
	defer face.Close()
	arts := map[string]image.Image{}
	for name, want := range layout.Arts {
		if filepath.Base(name) != name {
			panic("素材路徑越界")
		}
		b := read(filepath.Join(*dir, name))
		if hash(b) != want {
			panic("B 素材失配")
		}
		im, e := png.Decode(bytes.NewReader(b))
		must(e)
		arts[name] = im
	}
	scenes := map[string]scene{}
	for _, s := range layout.Scenes {
		scenes[s.ID] = s
	}
	must(os.MkdirAll(*out, 0700))
	var inks []map[string]any
	for i := range catalog.States {
		r := &catalog.States[i]
		s, ok := scenes[r.ID]
		if !ok || s.Native != r.Native {
			panic("來源與版面矩形失配")
		}
		im := image.NewRGBA(image.Rect(0, 0, s.Native[2]*4, s.Native[3]*4))
		scale(im, im.Bounds(), arts[s.Background], s.Border)
		for _, b := range s.Buttons {
			scale(im, rect(b.Rect), arts[b.Art], 8)
		}
		for ci, c := range s.Cells {
			if c.Size != 52 {
				panic("字型大小失配")
			}
			if strings.TrimSpace(c.Text) == "" {
				continue
			}
			for _, ch := range c.Text {
				g, e := parsed.GlyphIndex(&sfnt.Buffer{}, ch)
				must(e)
				if g == 0 {
					panic("缺字")
				}
			}
			fg := color.RGBA{255, 255, 255, 255}
			if c.Option == r.Selection {
				fg = color.RGBA{255, 0, 0, 255}
			}
			mask := image.NewRGBA(image.Rect(0, 0, 64, 64))
			dot := fixed.P(4, 50)
			bounds, _ := font.BoundString(face, c.Text)
			placed := bounds.Add(dot)
			declared := image.Rect(placed.Min.X.Floor(), placed.Min.Y.Floor(), placed.Max.X.Ceil(), placed.Max.Y.Ceil())
			if !declared.In(mask.Bounds()) {
				panic("字形理論墨跡越界")
			}
			d := font.Drawer{Dst: mask, Src: image.NewUniform(fg), Face: face, Dot: dot}
			d.DrawString(c.Text)
			actual := alphaBounds(mask)
			at := image.Pt(c.X*4, c.Y*4)
			if actual.Empty() || !actual.In(declared) || !actual.Add(at).In(im.Bounds().Inset(4)) {
				panic(fmt.Sprintf("實際墨跡越界 %s %d", s.ID, ci))
			}
			if len(s.Buttons) > 0 && !actual.Add(at).In(rect(s.Buttons[c.Option].Rect).Inset(4)) {
				panic("按鈕文字越界")
			}
			draw.Draw(im, image.Rect(at.X, at.Y, at.X+64, at.Y+64), mask, image.Point{}, draw.Over)
			inks = append(inks, map[string]any{"id": s.ID, "selection": r.Selection, "cell": ci, "index": c.Index, "actual_ink": actual.Add(at), "contained": true})
		}
		r.Image = fmt.Sprintf("%s-%d.png", r.ID, r.Selection)
		var b bytes.Buffer
		must(png.Encode(&b, im))
		r.ImageSHA = hash(b.Bytes())
		must(os.WriteFile(filepath.Join(*out, r.Image), b.Bytes(), 0600))
	}
	manifest := map[string]any{"schema": 1, "font_sha256": fontSHA, "license_sha256": licenseSHA, "layout_sha256": *layoutSHA, "sources_sha256": *sourcesSHA, "states": catalog.States}
	b, e := json.MarshalIndent(manifest, "", "  ")
	must(e)
	b = append(b, '\n')
	must(os.WriteFile(filepath.Join(*out, "manifest.json"), b, 0600))
	v, e := json.MarshalIndent(map[string]any{"font_sha256": fontSHA, "states": 18, "all_ink_contained": true, "samples": inks}, "", "  ")
	must(e)
	must(os.WriteFile(filepath.Join(*out, "ink-verification.json"), append(v, '\n'), 0600))
	fmt.Printf("十八個子選單面板；%d 項實際墨跡；manifest SHA-256 %s\n", len(inks), hash(b))
}
