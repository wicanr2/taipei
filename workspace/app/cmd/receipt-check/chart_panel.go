package main

import (
	"bytes"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"image"
	"image/color"
	"image/draw"
	"image/png"
	"os"
	"path/filepath"
)

type chartFields struct {
	ChartWindow bool   `json:"chart_window"`
	ChartReason string `json:"chart_reason"`
	ChartData   string `json:"chart_data_sha256"`
}

type chartReference struct {
	base     []byte
	proto    *image.RGBA
	texture  image.Image
	palettes [2][256][3]byte
}

func readChartReference(dir, original string) *chartReference {
	if dir == "" {
		return nil
	}
	rom, err := os.ReadFile(filepath.Join(original, "RS201.ROM"))
	check(err)
	if powerSHA(rom) != "0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29" {
		panic("圖表唯讀 ROM 不符")
	}
	offset := int(binary.LittleEndian.Uint32(rom[18+4*16:]))
	size := int(binary.LittleEndian.Uint16(rom[22+4*16:]))
	if offset != 27667 || size != 9294 {
		panic("圖表原始成員定位不符")
	}
	raw := rom[offset : offset+size]
	if !bytes.Equal(raw[:4], []byte{145, 0, 127, 0}) {
		panic("圖表原始尺寸不符")
	}
	r := &chartReference{}
	for at := 4; at < len(raw); {
		value, count := raw[at], 1
		at++
		if value == 0 {
			if at+2 > len(raw) || raw[at+1] == 0 {
				panic("圖表原始串流不完整")
			}
			value, count = raw[at], int(raw[at+1])
			at += 2
		}
		r.base = append(r.base, bytes.Repeat([]byte{value}, count)...)
		if len(r.base) > 145*127 {
			panic("圖表原始串流越界")
		}
	}
	if len(r.base) != 145*127 || powerSHA(r.base) != "c3b7fa8fdc7246e48cd051d375cf36566c3f01c69e33f7eb9ac4bcd1c2ffc961" {
		panic("圖表完整解碼不符")
	}
	raw, err = os.ReadFile(filepath.Join(dir, "chart-windows-v2", "0", "manifest.json"))
	check(err)
	if powerSHA(raw) != "511ffcec3a1a125b6ca4878e8d384624e2772f9500c47c7e6db1a2abce0ebd45" {
		panic("圖表 READY 前 manifest 不符")
	}
	for _, item := range []struct{ path, expected string }{
		{"chart-windows-v2/0/presentation.png", ""},
		{"city-chrome-gray-v1.png", "6532e1daf962bb4abeed7a4c0a186a0ee9b606d4273d6d8ee5fce46e462efd37"},
	} {
		raw, err = os.ReadFile(filepath.Join(dir, item.path))
		check(err)
		if item.expected != "" && powerSHA(raw) != item.expected {
			panic("圖表固定參考圖不符")
		}
		im, err := png.Decode(bytes.NewReader(raw))
		check(err)
		if item.expected == "" {
			if im.Bounds() != image.Rect(0, 0, 1280, 800) {
				panic("圖表完整原型尺寸不符")
			}
			r.proto = image.NewRGBA(im.Bounds())
			draw.Draw(r.proto, r.proto.Bounds(), im, image.Point{}, draw.Src)
			if powerSHA(r.proto.Pix) != "ebd0d2a0c4fc73278db2f23e391a94dcf51f6c5d57903c87fc8bc6f9c7015d4f" {
				panic("圖表完整原型 RGBA 不符")
			}
		} else {
			if im.Bounds() != image.Rect(0, 0, 944, 528) {
				panic("圖表筆觸參考尺寸不符")
			}
			r.texture = im
		}
	}
	raw, err = os.ReadFile(filepath.Join(dir, "..", "..", "runs", "chart-windows-native", "palette-audit-r1.json"))
	check(err)
	if powerSHA(raw) != "392dc069f4c39632d14c3991c7f2b0e4f11e5dcf6084b397b744f39caad17473" {
		panic("圖表正常原版色盤證據不符")
	}
	var p struct {
		Palettes []struct{ RGB [256][3]byte }
	}
	check(json.Unmarshal(raw, &p))
	if len(p.Palettes) != 2 {
		panic("圖表正常色盤數量不符")
	}
	for i := range r.palettes {
		r.palettes[i] = p.Palettes[i].RGB
	}
	return r
}

func (r *chartReference) audit(px []byte, pal [256][3]byte, mode int, enabled, blocked bool, h chartFields) (image.Image, error) {
	if r == nil {
		if h.ChartWindow {
			return nil, fmt.Errorf("圖表 HD 缺 -chart-reference")
		}
		return nil, nil
	}
	known, paletteOK := true, true
	var data []byte
	for y := 0; y < 127; y++ {
		for x := 0; x < 145; x++ {
			v := px[(35+y)*320+66+x]
			if x >= 20 && x < 125 && y >= 20 && y < 109 {
				data = append(data, v)
			} else if v != r.base[y*145+x] {
				known = false
			}
			if pal[v] != r.palettes[0][v] && pal[v] != r.palettes[1][v] {
				paletteOK = false
			}
		}
	}
	wantReason := "scene-fallback"
	if !enabled {
		wantReason = "original"
	} else if known && mode == 19 {
		if !blocked {
			wantReason = "chart-unverified-phase"
		} else if !paletteOK {
			wantReason = "chart-palette-mismatch"
		} else {
			wantReason = "matched-chart-window"
		}
	}
	if h.ChartReason != wantReason {
		return nil, fmt.Errorf("圖表原因不符 %q，期望 %q", h.ChartReason, wantReason)
	}
	if !known || mode != 19 || !enabled || !blocked || !paletteOK {
		if h.ChartWindow || h.ChartData != "" {
			return nil, fmt.Errorf("圖表失配仍回報 HD 或資料")
		}
		return nil, nil
	}
	if !h.ChartWindow || h.ChartData != powerSHA(data) {
		return nil, fmt.Errorf("圖表家族或原資料雜湊不符")
	}
	want := image.NewRGBA(image.Rect(0, 0, 1280, 800))
	for at, v := range px {
		rgb := pal[v]
		for dy := 0; dy < 4; dy++ {
			for dx := 0; dx < 4; dx++ {
				want.SetRGBA(at%320*4+dx, at/320*4+dy, color.RGBA{rgb[0], rgb[1], rgb[2], 255})
			}
		}
	}
	draw.Draw(want, image.Rect(264, 140, 844, 648), r.proto, image.Pt(264, 140), draw.Src)
	for y := 80; y < 436; y++ {
		for x := 80; x < 500; x++ {
			rgb := pal[px[(35+y/4)*320+66+x/4]]
			rr, _, _, _ := r.texture.At(32+x%880, 32+y%464).RGBA()
			grain := int(rr>>8)/8 - 18
			var c [3]byte
			for i, v := range rgb {
				value := int(v) + grain
				if value < 0 {
					value = 0
				} else if value > 255 {
					value = 255
				}
				c[i] = byte(value)
			}
			want.SetRGBA(264+x, 140+y, color.RGBA{c[0], c[1], c[2], 255})
		}
	}
	return want, nil
}
