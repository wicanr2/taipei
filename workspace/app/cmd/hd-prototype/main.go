// 離線比較原型，契約見 docs/spec/008-hd-material-prototype.md。
package main

import (
	"crypto/sha256"
	"encoding/binary"
	"encoding/json"
	"flag"
	"fmt"
	"image"
	"image/color"
	"image/png"
	"os"
	"path/filepath"
)

func check(err error) {
	if err != nil {
		panic(err)
	}
}
func read(p string) []byte { b, e := os.ReadFile(p); check(e); return b }
func pngRead(p string) image.Image {
	f, e := os.Open(p)
	check(e)
	defer f.Close()
	im, e := png.Decode(f)
	check(e)
	return im
}
func pngWrite(p string, im image.Image) {
	f, e := os.Create(p)
	check(e)
	check(png.Encode(f, im))
	check(f.Close())
}
func digest(b []byte) string { return fmt.Sprintf("%x", sha256.Sum256(b)) }

func main() {
	frame := flag.String("frame", "", "原版 PNG")
	indices := flag.String("indices", "", "原版色號")
	romPath := flag.String("rom", "", "唯讀 RS201.ROM")
	materials := flag.String("materials", "", "本機材質目錄")
	out := flag.String("out", "", "輸出目錄")
	flag.Parse()
	if *frame == "" || *indices == "" || *romPath == "" || *materials == "" || *out == "" {
		panic("請指定全部輸入與輸出")
	}
	rgb := pngRead(*frame)
	px := read(*indices)
	rom := read(*romPath)
	if rgb.Bounds().Dx() != 320 || rgb.Bounds().Dy() != 200 || len(px) != 64000 {
		panic("原版畫面形狀不符")
	}
	if digest(rom) != "0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29" {
		panic("ROM 雜湊不符")
	}
	u16 := func(b []byte) int { return int(binary.LittleEndian.Uint16(b)) }
	member := 59
	rec := 8 + member*16
	off := int(binary.LittleEndian.Uint32(rom[rec+10:]))
	n := u16(rom[rec+14:])
	lib := rom[off : off+n]
	count := u16(lib)
	sources := map[string][]int{}
	for i := 0; i < count; i++ {
		a := u16(lib[2+i*2:])
		z := len(lib)
		if i+1 < count {
			z = u16(lib[4+i*2:])
		}
		b := lib[a:z]
		if u16(b) != 9 || u16(b[2:]) != 9 || len(b) != 85 {
			panic("圖庫形狀不符")
		}
		key := string(b[4:])
		sources[key] = append(sources[key], i)
	}
	textures := map[string]image.Image{}
	textureHashes := map[string]string{}
	for _, name := range []string{"water", "sand", "forest"} {
		p := filepath.Join(*materials, name+"-b-v1.png")
		if _, e := os.Stat(p); e == nil {
			textures[name] = pngRead(p)
			textureHashes[name] = digest(read(p))
		}
	}
	native := image.NewRGBA(image.Rect(0, 0, 1280, 800))
	hd := image.NewRGBA(native.Bounds())
	for y := 0; y < 800; y++ {
		for x := 0; x < 1280; x++ {
			c := rgb.At(x/4, y/4)
			native.Set(x, y, c)
			hd.Set(x, y, c)
		}
	}
	hits, painted, fallback := 0, 0, 0
	var cells []map[string]any
	counts := map[string]int{}
	for y := 34; y+9 <= 169; y += 9 {
		for x := 5; x+9 <= 266; x += 9 {
			b := make([]byte, 0, 81)
			for row := 0; row < 9; row++ {
				b = append(b, px[(y+row)*320+x:(y+row)*320+x+9]...)
			}
			ids, ok := sources[string(b)]
			if !ok {
				fallback++
				continue
			}
			hits++
			known := true
			for _, c := range b {
				if material(c) == "" || textures[material(c)] == nil {
					known = false
					break
				}
			}
			if !known {
				fallback++
				continue
			}
			for dy := 0; dy < 36; dy++ {
				for dx := 0; dx < 36; dx++ {
					index := b[(dy/4)*9+dx/4]
					name := material(index)
					tex := textures[name]
					if tex == nil {
						continue
					}
					xx, yy := x*4+dx, y*4+dy
					bounds := tex.Bounds()
					c := tex.At(bounds.Min.X+(xx-20)%bounds.Dx(), bounds.Min.Y+(yy-136)%bounds.Dy())
					r, g, bl, _ := c.RGBA()
					shade := 1.0
					switch name {
					case "water":
						shade = 0.95 + float64(index-144)*0.025
					case "sand":
						shade = 0.94 + float64(index-201)*0.025
					case "forest":
						shade = 0.70 + float64(index-103)*0.10
					}
					scale := func(v uint32) uint8 {
						f := float64(v>>8) * shade
						if f > 255 {
							f = 255
						}
						return uint8(f)
					}
					hd.SetRGBA(xx, yy, color.RGBA{scale(r), scale(g), scale(bl), 255})
					counts[name]++
				}
			}
			painted++
			cells = append(cells, map[string]any{"x": x, "y": y, "member": member, "source_indices": ids, "sha256": digest(b)})
		}
	}
	outsideDifferences := 0
	changed := 0
	for y := 0; y < 800; y++ {
		for x := 0; x < 1280; x++ {
			if hd.RGBAAt(x, y) != native.RGBAAt(x, y) {
				changed++
				if x < 20 || x >= 1064 || y < 136 || y >= 676 {
					outsideDifferences++
				}
			}
		}
	}
	if outsideDifferences != 0 {
		panic("區域外像素改變")
	}
	check(os.MkdirAll(*out, 0700))
	pngWrite(filepath.Join(*out, "original-1280x800.png"), native)
	pngWrite(filepath.Join(*out, "hd-b-1280x800.png"), hd)
	meta := map[string]any{"prototype": true, "original_frame_sha256": digest(read(*frame)), "original_indices_sha256": digest(px), "rom_sha256": digest(rom), "material_sha256": textureHashes, "matched_cells": hits, "painted_cells": painted, "fallback_cells": fallback, "changed_hd_pixels": changed, "outside_differences": outsideDifferences, "material_pixels": counts, "cells": cells}
	data, e := json.MarshalIndent(meta, "", "  ")
	check(e)
	check(os.WriteFile(filepath.Join(*out, "receipt.json"), data, 0600))
	fmt.Printf("matched=%d painted=%d fallback=%d outside-differences=%d\n", hits, painted, fallback, outsideDifferences)
}

func material(index byte) string {
	switch {
	case index >= 144 && index <= 147:
		return "water"
	case index >= 201 && index <= 204:
		return "sand"
	case index >= 103 && index <= 107:
		return "forest"
	}
	return ""
}
