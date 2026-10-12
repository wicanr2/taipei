// #48：只供來源及美術審查的可撤回圖表原型，不接產品。
package main

import (
	"archive/zip"
	"bytes"
	"crypto/sha256"
	"encoding/binary"
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
func digest(p []byte) string  { return fmt.Sprintf("%x", sha256.Sum256(p)) }
func read(path string) []byte { p, err := os.ReadFile(path); must(err); return p }
func save(path string, im image.Image) {
	f, err := os.OpenFile(path, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0600)
	must(err)
	must(png.Encode(f, im))
	must(f.Close())
}
func clamp(v int) uint8 {
	if v < 0 {
		return 0
	}
	if v > 255 {
		return 255
	}
	return uint8(v)
}

func abs(v int) int {
	if v < 0 {
		return -v
	}
	return v
}

func main() {
	original := flag.String("original", "/orig", "唯讀原版")
	receipt := flag.String("receipt", "", "真實正常圖表原子收據")
	materials := flag.String("materials", "", "既有 B 素材與固定字型")
	frameArt := flag.String("frame-art", "", "可選固定灰框插畫，僅使用原版灰色框架遮罩")
	out := flag.String("out", "", "不存在的新原型目錄")
	flag.Parse()
	if _, err := os.Stat(*out); !os.IsNotExist(err) {
		panic("保留原型，輸出必須不存在")
	}
	rom := read(filepath.Join(*original, "RS201.ROM"))
	if digest(rom) != "0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29" {
		panic("ROM 不符")
	}
	offset := int(binary.LittleEndian.Uint32(rom[18+4*16:]))
	size := int(binary.LittleEndian.Uint16(rom[22+4*16:]))
	compressed := rom[offset : offset+size]
	if binary.LittleEndian.Uint16(compressed) != 145 || binary.LittleEndian.Uint16(compressed[2:]) != 127 {
		panic("原始圖框尺寸不符")
	}
	base := []byte{}
	for at := 4; at < len(compressed); {
		value := compressed[at]
		at++
		if value != 0 {
			base = append(base, value)
			continue
		}
		if at+2 > len(compressed) || compressed[at+1] == 0 {
			panic("來源壓縮串流不符")
		}
		value, count := compressed[at], int(compressed[at+1])
		at += 2
		for j := 0; j < count; j++ {
			base = append(base, value)
		}
	}
	if len(base) != 145*127 || digest(base) != "c3b7fa8fdc7246e48cd051d375cf36566c3f01c69e33f7eb9ac4bcd1c2ffc961" {
		panic("完整圖框不符")
	}
	receiptData := read(*receipt)
	z, err := zip.NewReader(bytes.NewReader(receiptData), int64(len(receiptData)))
	must(err)
	files := map[string][]byte{}
	for _, f := range z.File {
		if f.Name == "status.json" || f.Name == "frame-index.bin" {
			r, err := f.Open()
			must(err)
			files[f.Name], err = io.ReadAll(r)
			must(err)
			must(r.Close())
		}
	}
	var status struct {
		Mode     int
		Blocked  bool   `json:"dos_blocked"`
		Exited   bool   `json:"dos_exited"`
		FrameSHA string `json:"frame_index_sha256"`
		Palette  [256][3]byte
	}
	must(json.Unmarshal(files["status.json"], &status))
	pixels := files["frame-index.bin"]
	if len(pixels) != 64000 || digest(pixels) != status.FrameSHA || status.Mode != 19 || !status.Blocked || status.Exited {
		panic("不是已見正常等待輸入圖表")
	}
	const nx, ny, w, h = 66, 35, 145, 127
	dataRect := image.Rect(20, 20, 125, 109)
	roi, data := []byte{}, []byte{}
	for y := 0; y < h; y++ {
		for x := 0; x < w; x++ {
			v := pixels[(ny+y)*320+nx+x]
			roi = append(roi, v)
			if image.Pt(x, y).In(dataRect) {
				data = append(data, v)
			} else if v != base[y*w+x] {
				panic("完整固定框架不符")
			}
		}
	}
	textureData := read(filepath.Join(*materials, "city-chrome-gray-v1.png"))
	if digest(textureData) != "6532e1daf962bb4abeed7a4c0a186a0ee9b606d4273d6d8ee5fce46e462efd37" {
		panic("既有 B 筆觸不符")
	}
	texture, err := png.Decode(bytes.NewReader(textureData))
	must(err)
	if texture.Bounds() != image.Rect(0, 0, 944, 528) {
		panic("B 筆觸尺寸不符")
	}
	frameSHA := ""
	var frameImage *image.RGBA
	if *frameArt != "" {
		raw := read(*frameArt)
		frameSHA = digest(raw)
		if frameSHA != "109e7da267bed6a0b9dcb9baa0872bb3b5f1b0e1fa0ab1e8b532a82d99f41738" {
			panic("灰框插畫不符")
		}
		im, err := png.Decode(bytes.NewReader(raw))
		must(err)
		if im.Bounds() != image.Rect(0, 0, 1341, 1173) {
			panic("灰框插畫尺寸不符")
		}
		frameImage = image.NewRGBA(image.Rect(0, 0, w*4, h*4))
		xdraw.CatmullRom.Scale(frameImage, frameImage.Bounds(), im, im.Bounds(), draw.Src, nil)
	}
	fontData := read(filepath.Join(*materials, "fonts", "NotoSansCJKtc-Regular.otf"))
	license := read(filepath.Join(*materials, "fonts", "LICENSE"))
	if digest(fontData) != "dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4" || digest(license) != "6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2" {
		panic("字型或授權不符")
	}
	parsed, err := opentype.Parse(fontData)
	must(err)
	face, err := opentype.NewFace(parsed, &opentype.FaceOptions{Size: 24, DPI: 72, Hinting: font.HintingNone})
	must(err)
	defer face.Close()
	glyphs := map[string]uint16{}
	for _, ch := range "MAXIN" {
		i, err := parsed.GlyphIndex(&sfnt.Buffer{}, ch)
		must(err)
		if i == 0 {
			panic("Noto 缺字")
		}
		glyphs[string(ch)] = uint16(i)
	}
	canvas := image.NewRGBA(image.Rect(0, 0, 1280, 800))
	native := image.NewRGBA(image.Rect(0, 0, 320, 200))
	for at, v := range pixels {
		c := status.Palette[v]
		native.SetRGBA(at%320, at/320, color.RGBA{c[0], c[1], c[2], 255})
		for dy := 0; dy < 4; dy++ {
			for dx := 0; dx < 4; dx++ {
				canvas.SetRGBA((at%320)*4+dx, (at/320)*4+dy, color.RGBA{c[0], c[1], c[2], 255})
			}
		}
	}
	old := image.NewRGBA(canvas.Bounds())
	draw.Draw(old, old.Bounds(), canvas, image.Point{}, draw.Src)
	framePixels, frameLeakFallback := 0, 0
	for y := 0; y < h*4; y++ {
		for x := 0; x < w*4; x++ {
			source := roi[(y/4)*w+x/4]
			rgb := status.Palette[source]
			tr, _, _, _ := texture.At(32+x%880, 32+y%464).RGBA()
			grain := int(tr>>8)/8 - 18
			amount := 0
			if image.Pt(x/4, y/4).In(dataRect) {
				amount = grain
			} else if source >= 20 && source <= 27 && rgb[0] == rgb[1] && rgb[1] == rgb[2] {
				amount = grain * 2
			} else if frameImage != nil {
				amount = grain
			}
			if frameImage != nil && !image.Pt(x/4, y/4).In(dataRect) && rgb[0] == rgb[1] && rgb[1] == rgb[2] {
				c := frameImage.RGBAAt(x, y)
				if c.A == 255 && abs(int(c.R)-int(c.G)) <= 8 && abs(int(c.G)-int(c.B)) <= 8 && abs(int(c.R)-int(c.B)) <= 8 {
					canvas.SetRGBA(nx*4+x, ny*4+y, c)
					framePixels++
					continue
				}
				// 生成圖的地圖或色階可能跨過灰框邊界，該像素改用已知筆觸。
				frameLeakFallback++
			}
			canvas.SetRGBA(nx*4+x, ny*4+y, color.RGBA{clamp(int(rgb[0]) + amount), clamp(int(rgb[1]) + amount), clamp(int(rgb[2]) + amount), 255})
		}
	}
	mask := image.NewRGBA(canvas.Bounds())
	labels := []map[string]any{}
	for _, entry := range []struct {
		text string
		y    int
	}{{"MAX", 22}, {"MIN", 101}} {
		for _, x := range []int{1, 127} {
			for dy := 0; dy < 5; dy++ {
				for dx := 0; dx < 17; dx++ {
					v := roi[(entry.y+dy)*w+x+dx]
					if v != 14 && v != 129 {
						panic("嵌入文字底板不是已見來源")
					}
				}
			}
			safe := image.Rect((nx+x)*4, (ny+entry.y)*4, (nx+x+17)*4, (ny+entry.y+5)*4)
			bg := status.Palette[129]
			draw.Draw(canvas, safe, image.NewUniform(color.RGBA{bg[0], bg[1], bg[2], 255}), image.Point{}, draw.Src)
			bounds, _ := font.BoundString(face, entry.text)
			dot := fixed.P((safe.Min.X+safe.Max.X)/2-(bounds.Min.X+bounds.Max.X).Round()/2, (safe.Min.Y+safe.Max.Y)/2-(bounds.Min.Y+bounds.Max.Y).Round()/2)
			part := image.NewRGBA(canvas.Bounds())
			d := font.Drawer{Dst: part, Src: image.White, Face: face, Dot: dot}
			d.DrawString(entry.text)
			ink := image.Rectangle{}
			count := 0
			for y := 0; y < 800; y++ {
				for x := 0; x < 1280; x++ {
					if part.RGBAAt(x, y).A != 0 {
						ink = ink.Union(image.Rect(x, y, x+1, y+1))
						count++
					}
				}
			}
			if ink.Empty() || !ink.In(safe) {
				panic(fmt.Sprintf("Noto 墨跡裁切 %v %v", ink, safe))
			}
			draw.Draw(mask, mask.Bounds(), part, image.Point{}, draw.Over)
			labels = append(labels, map[string]any{"text": entry.text, "safe_rect": safe, "actual_ink_rect": ink, "ink_pixels": count})
		}
	}
	beforeText := image.NewRGBA(canvas.Bounds())
	draw.Draw(beforeText, beforeText.Bounds(), canvas, image.Point{}, draw.Src)
	rgb := status.Palette[14]
	draw.DrawMask(canvas, canvas.Bounds(), image.NewUniform(color.RGBA{rgb[0], rgb[1], rgb[2], 255}), image.Point{}, mask, image.Point{}, draw.Over)
	comparison := image.NewRGBA(image.Rect(0, 0, 2560, 800))
	draw.Draw(comparison, old.Bounds(), old, image.Point{}, draw.Src)
	draw.Draw(comparison, image.Rect(1280, 0, 2560, 800), canvas, image.Point{}, draw.Src)
	must(os.Mkdir(*out, 0700))
	if frameImage != nil {
		save(filepath.Join(*out, "frame-art-scaled.png"), frameImage)
	}
	save(filepath.Join(*out, "source.png"), native)
	save(filepath.Join(*out, "before-text.png"), beforeText)
	save(filepath.Join(*out, "text-ink.png"), mask)
	save(filepath.Join(*out, "presentation.png"), canvas)
	save(filepath.Join(*out, "comparison.png"), comparison)
	meta, err := json.MarshalIndent(map[string]any{"schema": 1, "issue": 48, "stage": "DRAFT", "prototype": true, "rom_sha256": digest(rom), "receipt_sha256": digest(receiptData), "source_frame_sha256": digest(pixels), "source_window_sha256": digest(roi), "source_data_sha256": digest(data), "native": []int{nx, ny, w, h}, "data_local": []int{20, 20, 105, 89}, "texture_sha256": digest(textureData), "font_sha256": digest(fontData), "license_sha256": digest(license), "font_size": 24, "glyph_indices": glyphs, "labels": labels, "size": []int{1280, 800}, "presentation_rgba_sha256": digest(canvas.Pix), "scope": "來源及 B／Noto 原型；不接產品，不推定統計語意。圖框外保持原版四倍像素，資料保留每個原始色號位置與色盤類別"}, "", "  ")
	must(err)
	var extra map[string]any
	must(json.Unmarshal(meta, &extra))
	extra["frame_art_sha256"] = frameSHA
	if frameImage != nil {
		extra["frame_art_scaled_png_sha256"] = digest(read(filepath.Join(*out, "frame-art-scaled.png")))
		extra["frame_art_scaled_rgba_sha256"] = digest(frameImage.Pix)
	}
	extra["frame_art_gray_pixels"] = framePixels
	extra["frame_art_colored_pixel_fallback"] = frameLeakFallback
	extra["generated_data_pixels_accepted"] = 0
	meta, err = json.MarshalIndent(extra, "", "  ")
	must(err)
	must(os.WriteFile(filepath.Join(*out, "manifest.json"), append(meta, '\n'), 0600))
	fmt.Println("DRAFT chart prototype", digest(canvas.Pix))
}
