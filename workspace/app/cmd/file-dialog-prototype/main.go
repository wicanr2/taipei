// #38：離線檔案視窗原型。固定 Noto 與既有 B 素材，不執行 DOS。
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
	"os"
	"path/filepath"

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
func picture(p, want string) image.Image {
	b := read(p)
	if hash(b) != want {
		panic("固定素材失配")
	}
	im, e := png.Decode(bytes.NewReader(b))
	must(e)
	return im
}
func main() {
	dir := flag.String("materials", "", "本機素材根")
	source := flag.String("source", "", "本機來源 catalog.json")
	sourceSHA := flag.String("source-sha", "", "已審查來源 SHA-256")
	out := flag.String("out", "", "本機原型輸出")
	proofCatalog := flag.String("proof-catalog", "", "可選正常八 W 檔名來源")
	proofSHA := flag.String("proof-sha", "", "八 W 來源 catalog SHA-256")
	proofOut := flag.String("proof-out", "", "可選八 W 原位組合 PNG")
	flag.Parse()
	raw := read(*source)
	if len(*sourceSHA) != 64 || hash(raw) != *sourceSHA {
		panic("來源失配")
	}
	var catalog struct {
		ROMSHA  string                  `json:"rom_sha256"`
		Chinese []struct{ Text string } `json:"chinese_prompt"`
	}
	must(json.Unmarshal(raw, &catalog))
	if catalog.ROMSHA != "0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29" || len(catalog.Chinese) != 8 {
		panic("來源形狀失配")
	}
	fontRaw := read(filepath.Join(*dir, "fonts/NotoSansCJKtc-Regular.otf"))
	license := read(filepath.Join(*dir, "fonts/LICENSE"))
	if hash(fontRaw) != "dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4" || hash(license) != "6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2" {
		panic("字型或授權失配")
	}
	parsed, e := opentype.Parse(fontRaw)
	must(e)
	faces := map[int]font.Face{}
	for _, size := range []int{24, 52} {
		f, e := opentype.NewFace(parsed, &opentype.FaceOptions{Size: float64(size), DPI: 72, Hinting: font.HintingNone})
		must(e)
		faces[size] = f
		defer f.Close()
	}
	atlas := image.NewRGBA(image.Rect(0, 0, 1024, 832))
	var checks []map[string]any
	glyph := func(index int, text string, size, w, h int, fg color.RGBA) {
		ch := []rune(text)
		if len(ch) != 1 {
			panic("單字契約")
		}
		gi, e := parsed.GlyphIndex(&sfnt.Buffer{}, ch[0])
		must(e)
		if gi == 0 {
			panic("缺字")
		}
		layer := image.NewRGBA(image.Rect(0, 0, 128, 128))
		d := font.Drawer{Dst: layer, Src: image.NewUniform(fg), Face: faces[size], Dot: fixed.P(20, 80)}
		d.DrawString(text)
		ink := image.Rectangle{}
		for y := 0; y < 128; y++ {
			for x := 0; x < 128; x++ {
				if layer.RGBAAt(x, y).A != 0 {
					ink = ink.Union(image.Rect(x, y, x+1, y+1))
				}
			}
		}
		if (ink.Empty() && text != " ") || ink.Dx() > w || ink.Dy() > h {
			panic(fmt.Sprintf("墨跡越界 %q %v", text, ink))
		}
		cell := image.Pt(index%16*64, index/16*64)
		at := cell.Add(image.Pt((w-ink.Dx())/2, (h-ink.Dy())/2))
		placed := image.Rectangle{Min: at, Max: at.Add(ink.Size())}
		if !ink.Empty() {
			draw.Draw(atlas, placed, layer, ink.Min, draw.Over)
		}
		checks = append(checks, map[string]any{"index": index, "text": text, "font_size": size, "safe": image.Rectangle{Min: cell, Max: cell.Add(image.Pt(w, h))}, "actual_ink": placed, "missing_glyph": false, "clipped": false})
	}
	for group, fg := range []color.RGBA{{255, 255, 255, 255}, {255, 0, 0, 255}} {
		for code := 32; code <= 126; code++ {
			glyph(group*95+code-32, string(rune(code)), 24, 24, 28, fg)
		}
	}
	for i, g := range catalog.Chinese {
		glyph(190+i, g.Text, 52, 60, 56, color.RGBA{255, 0, 0, 255})
	}
	blue := picture(filepath.Join(*dir, "menu-blue-b-v1.png"), "eeb1aa620c179a7fa0233bdfc9d9ad6abf8719d36f1ad05dc93c84343a164ea9")
	browser := image.NewRGBA(image.Rect(0, 0, 268, 428))
	sb := blue.Bounds()
	border := 8
	xs, ys := []int{0, border, sb.Dx() - border, sb.Dx()}, []int{0, border, sb.Dy() - border, sb.Dy()}
	xd, yd := []int{0, border, 268 - border, 268}, []int{0, border, 428 - border, 428}
	for y := 0; y < 3; y++ {
		for x := 0; x < 3; x++ {
			xdraw.CatmullRom.Scale(browser, image.Rect(xd[x], yd[y], xd[x+1], yd[y+1]), blue, image.Rect(xs[x], ys[y], xs[x+1], ys[y+1]), draw.Src, nil)
		}
	}
	// 保留既有 B 紋理，降低底色亮度，讓白字與紅色選取可辨讀。
	for at := 0; at < len(browser.Pix); at += 4 {
		for c := 0; c < 3; c++ {
			browser.Pix[at+c] /= 5
		}
	}
	draw.Draw(browser, image.Rect(20, 16, 248, 72), image.NewUniform(color.RGBA{9, 19, 37, 255}), image.Point{}, draw.Src)
	chrome := picture(filepath.Join(*dir, "city-chrome-v1/frame.png"), "d3391282c3fde64b60b64fe59ba756537c4bb60b3766a161106e5432b4e396d6")
	prompt := image.NewRGBA(image.Rect(0, 0, 896, 72))
	draw.Draw(prompt, prompt.Bounds(), chrome, image.Pt(28, 700), draw.Src)
	paint := func(index, x, y, w, h int) {
		draw.Draw(prompt, image.Rect(x, y, x+w, y+h), atlas, image.Pt(index%16*64, index/16*64), draw.Over)
	}
	for i := 0; i < 8; i++ {
		paint(190+i, (19+16*i-7)*4, 8, 60, 56)
	}
	for i, ch := range "?(Y/N)" {
		paint(95+int(ch)-32, (153+6*i-7)*4, 24, 24, 28)
	}
	must(os.MkdirAll(*out, 0700))
	images := map[string]string{}
	for name, im := range map[string]image.Image{"glyphs.png": atlas, "browser.png": browser, "quit-confirm.png": prompt} {
		var b bytes.Buffer
		must(png.Encode(&b, im))
		must(os.WriteFile(filepath.Join(*out, name), b.Bytes(), 0600))
		images[name] = hash(b.Bytes())
	}
	manifest := map[string]any{"schema": 1, "font_sha256": hash(fontRaw), "license_sha256": hash(license), "sources_sha256": *sourceSHA, "images": images, "ink_checks": checks, "atlas_size": []int{1024, 832}, "browser_size": []int{268, 428}, "prompt_size": []int{896, 72}}
	b, e := json.MarshalIndent(manifest, "", "  ")
	must(e)
	b = append(b, '\n')
	must(os.WriteFile(filepath.Join(*out, "manifest.json"), b, 0600))
	fmt.Printf("198 字模墨跡；manifest SHA-256 %s\n", hash(b))
	if *proofCatalog != "" {
		proofRaw := read(*proofCatalog)
		if len(*proofSHA) != 64 || hash(proofRaw) != *proofSHA || *proofOut == "" {
			panic("原位比較來源失配")
		}
		var proofs struct {
			Samples []struct {
				Receipt    string
				ReceiptSHA string `json:"receipt_sha256"`
				Source     *struct {
					Rows   []string
					Colors []int
				}
			}
		}
		must(json.Unmarshal(proofRaw, &proofs))
		found := false
		for _, sample := range proofs.Samples {
			if sample.Source == nil || len(sample.Source.Rows) != 8 || sample.Source.Rows[0] != "WWWWWWWW" {
				continue
			}
			if len(sample.Source.Colors) != 8 || hash(read(sample.Receipt)) != sample.ReceiptSHA {
				panic("原位比較收據失配")
			}
			z, e := zip.OpenReader(sample.Receipt)
			must(e)
			var native image.Image
			for _, f := range z.File {
				if f.Name == "frame.png" {
					r, e := f.Open()
					must(e)
					native, e = png.Decode(r)
					must(e)
					must(r.Close())
				}
			}
			must(z.Close())
			if native == nil || native.Bounds() != image.Rect(0, 0, 320, 200) {
				panic("原位比較原版圖片失配")
			}
			preview := image.NewRGBA(image.Rect(0, 0, 1280, 800))
			xdraw.NearestNeighbor.Scale(preview, preview.Bounds(), native, native.Bounds(), draw.Src, nil)
			draw.Draw(preview, image.Rect(136, 164, 404, 592), browser, image.Point{}, draw.Src)
			for line, text := range sample.Source.Rows {
				if len(text) != 8 {
					panic("比較文字列長度失配")
				}
				y := 8
				if line > 0 {
					y = 26 + 11*(line-1)
				}
				for column, ch := range text {
					if ch < 32 || ch > 126 {
						panic("比較字模失配")
					}
					index := int(ch) - 32
					if sample.Source.Colors[line] == 32 {
						index += 95
					}
					xx, yy := (44+6*column)*4, (41+y)*4
					draw.Draw(preview, image.Rect(xx, yy, xx+24, yy+28), atlas, image.Pt(index%16*64, index/16*64), draw.Over)
				}
			}
			var p bytes.Buffer
			must(png.Encode(&p, preview))
			must(os.WriteFile(*proofOut, p.Bytes(), 0600))
			fmt.Printf("八 W 原位比較 %s %s\n", sample.Receipt, hash(p.Bytes()))
			found = true
			break
		}
		if !found {
			panic("沒有已重建的正常八 W 檔名來源")
		}
	}
}
