// #47：完整政績底圖的可撤回 B／Noto 原型，沒有接入產品。
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

	xdraw "golang.org/x/image/draw"
	"golang.org/x/image/font"
	"golang.org/x/image/font/opentype"
	"golang.org/x/image/font/sfnt"
	"golang.org/x/image/math/fixed"
)

func must(err error) {
	if err != nil {
		panic(err)
	}
}

func read(path string) []byte {
	p, err := os.ReadFile(path)
	must(err)
	return p
}

func digest(p []byte) string { return fmt.Sprintf("%x", sha256.Sum256(p)) }

func load(path string) image.Image {
	f, err := os.Open(path)
	must(err)
	defer f.Close()
	im, err := png.Decode(f)
	must(err)
	return im
}

func save(path string, im image.Image) {
	f, err := os.OpenFile(path, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0600)
	must(err)
	must(png.Encode(f, im))
	must(f.Close())
}

func main() {
	source := flag.String("source", "", "已核對的正常底圖目錄")
	art := flag.String("art", "", "B 插畫原件")
	fontPath := flag.String("font", "", "固定 Noto 字型")
	out := flag.String("out", "", "新的本機原型目錄")
	flag.Parse()
	if _, err := os.Stat(*out); !os.IsNotExist(err) {
		panic("保留既有原型，請指定不存在的輸出")
	}
	raw := read(filepath.Join(*source, "source-index.bin"))
	const sourceSHA = "0040b4374f37464862ae2f89da5bc897ddb7f53d539edd597cf8b2b6ff784ebd"
	if len(raw) != 64000 || digest(raw) != sourceSHA {
		panic("完整原版來源不符")
	}
	artData := read(*art)
	if digest(artData) != "2dbdb09f57fe5324542117b2c00bc2b0d4ded4b24781594920f05663f6ad3284" {
		panic("插畫原件不符")
	}
	fontData := read(*fontPath)
	if digest(fontData) != "dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4" {
		panic("固定 Noto 字型不符")
	}
	original := load(filepath.Join(*source, "source.png"))
	if original.Bounds() != image.Rect(0, 0, 320, 200) {
		panic("原版圖片尺寸不符")
	}
	artImage := load(*art)
	if artImage.Bounds() != image.Rect(0, 0, 1586, 992) {
		panic("插畫尺寸不符")
	}
	parsed, err := opentype.Parse(fontData)
	must(err)
	face, err := opentype.NewFace(parsed, &opentype.FaceOptions{Size: 52, DPI: 72, Hinting: font.HintingNone})
	must(err)
	defer face.Close()
	const title = "您的政績"
	glyphs := map[string]uint16{}
	for _, ch := range title {
		index, err := parsed.GlyphIndex(&sfnt.Buffer{}, ch)
		must(err)
		if index == 0 {
			panic(fmt.Sprintf("Noto 缺字 U+%04X", ch))
		}
		glyphs[string(ch)] = uint16(index)
	}
	canvas := image.NewRGBA(image.Rect(0, 0, 1280, 800))
	xdraw.CatmullRom.Scale(canvas, canvas.Bounds(), artImage, artImage.Bounds(), draw.Src, nil)
	artScaled := image.NewRGBA(canvas.Bounds())
	draw.Draw(artScaled, artScaled.Bounds(), canvas, image.Point{}, draw.Src)
	// 正常來源的藍色字墨矩形是 (128,3)-(191,17)，安全區採完整四字格。
	safe := image.Rect(512, 12, 768, 68)
	bounds, _ := font.BoundString(face, title)
	dot := fixed.P((safe.Min.X+safe.Max.X)/2-(bounds.Min.X+bounds.Max.X).Round()/2,
		(safe.Min.Y+safe.Max.Y)/2-(bounds.Min.Y+bounds.Max.Y).Round()/2)
	mask := image.NewRGBA(canvas.Bounds())
	d := font.Drawer{Dst: mask, Src: image.White, Face: face, Dot: dot}
	d.DrawString(title)
	ink := image.Rectangle{}
	for y := 0; y < 800; y++ {
		for x := 0; x < 1280; x++ {
			if mask.RGBAAt(x, y).A != 0 {
				ink = ink.Union(image.Rect(x, y, x+1, y+1))
			}
		}
	}
	if ink.Empty() || !ink.In(safe) {
		panic(fmt.Sprintf("實際 Noto 字墨裁切 %v %v", ink, safe))
	}
	draw.DrawMask(canvas, canvas.Bounds(), image.NewUniform(color.RGBA{0, 0, 203, 255}),
		image.Point{}, mask, image.Point{}, draw.Over)
	old := image.NewRGBA(canvas.Bounds())
	xdraw.NearestNeighbor.Scale(old, old.Bounds(), original, original.Bounds(), draw.Src, nil)
	comparison := image.NewRGBA(image.Rect(0, 0, 2560, 800))
	draw.Draw(comparison, old.Bounds(), old, image.Point{}, draw.Src)
	draw.Draw(comparison, image.Rect(1280, 0, 2560, 800), canvas, image.Point{}, draw.Src)
	must(os.Mkdir(*out, 0700))
	save(filepath.Join(*out, "art-scaled.png"), artScaled)
	save(filepath.Join(*out, "title-ink.png"), mask)
	save(filepath.Join(*out, "presentation.png"), canvas)
	save(filepath.Join(*out, "comparison.png"), comparison)
	meta, err := json.MarshalIndent(map[string]any{
		"schema": 1, "issue": 47, "stage": "DRAFT", "prototype": true,
		"source_sha256": sourceSHA, "source_check_sha256": digest(read(filepath.Join(*source, "source-check.json"))),
		"art_sha256": digest(artData), "font_sha256": digest(fontData),
		"size": []int{1280, 800}, "title": title, "font_size": 52,
		"glyph_indices": glyphs, "safe_rect": safe, "actual_ink_rect": ink,
		"presentation_rgba_sha256": digest(canvas.Pix),
		"scope":                    "完整已見靜態底圖的可撤回原型，取得政績後的變化、動畫、正式呈現及正常 GUI 尚未完成",
	}, "", "  ")
	must(err)
	must(os.WriteFile(filepath.Join(*out, "manifest.json"), append(meta, '\n'), 0600))
	fmt.Printf("DRAFT ending prototype: %s ink=%v\n", digest(canvas.Pix), ink)
}
