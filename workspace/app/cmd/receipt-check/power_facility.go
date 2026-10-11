package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"image"
	"image/png"
	"os"
	"path/filepath"
	"reflect"
)

type powerCounts struct {
	Matched  int            `json:"matched"`
	Painted  int            `json:"painted"`
	Fallback int            `json:"fallback"`
	Images   map[int]int    `json:"images"`
	Reasons  map[string]int `json:"reasons"`
}

type powerFields struct {
	PowerFacility powerCounts `json:"power_facility"`
}

type powerSource struct {
	index int
	cell  image.Point
}

type powerReference struct {
	sources map[[81]byte]powerSource
	otherHD map[[81]byte]bool
	palette map[string][3]byte
	atlas   image.Image
}

type powerPixels struct {
	atlas    image.Image
	cells    map[int]image.Point
	native   *image.RGBA
	fallback map[int]bool
}

func powerSHA(p []byte) string { return fmt.Sprintf("%x", sha256.Sum256(p)) }

func readPowerReference(dir, original string) *powerReference {
	if dir == "" {
		return nil
	}
	rom, err := os.ReadFile(filepath.Join(original, "RS201.ROM"))
	check(err)
	if powerSHA(rom) != "0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29" {
		panic("火力參考 ROM 失配")
	}
	raw, err := os.ReadFile(filepath.Join(dir, "power-facility-ready-v1", "manifest.json"))
	check(err)
	if powerSHA(raw) != "bd571fa7a9ca49cbc8de1adde54cf1aa64642db4ff29bf158a567a75ca027c11" {
		panic("火力參考 manifest 失配")
	}
	var manifest struct {
		Palette map[string][3]byte
		Sources []struct {
			Image int
			Cell  [2]int
			SHA   string `json:"source_sha256"`
		}
	}
	check(json.Unmarshal(raw, &manifest))
	r := &powerReference{sources: map[[81]byte]powerSource{}, otherHD: map[[81]byte]bool{}, palette: manifest.Palette}
	for _, member := range []int{39, 59} {
		offset := int(binary.LittleEndian.Uint32(rom[18+member*16:]))
		count := int(binary.LittleEndian.Uint16(rom[offset:]))
		for index := 0; index < count; index++ {
			if member == 39 && !((index >= 15 && index <= 25) || (index >= 27 && index <= 29) || (index >= 45 && index <= 55)) {
				continue
			}
			start := offset + int(binary.LittleEndian.Uint16(rom[offset+2+index*2:]))
			var key [81]byte
			copy(key[:], rom[start+4:start+85])
			valid := true
			if member == 59 {
				for _, i := range key {
					if !((i >= 103 && i <= 107) || (i >= 144 && i <= 147) || (i >= 201 && i <= 204)) {
						valid = false
					}
				}
			}
			if valid {
				r.otherHD[key] = true
			}
		}
	}
	off := int(binary.LittleEndian.Uint32(rom[626:]))
	length := int(binary.LittleEndian.Uint16(rom[630:]))
	lib := rom[off : off+length]
	if length != 15662 || binary.LittleEndian.Uint16(lib) != 180 || len(manifest.Sources) != 36 {
		panic("火力參考圖庫形態失配")
	}
	for _, v := range manifest.Sources {
		col, row := v.Cell[0], v.Cell[1]
		if col < 0 || col > 5 || row < 0 || row > 5 || v.Image != 12+row*30+col {
			panic("火力參考來源順序失配")
		}
		at := int(binary.LittleEndian.Uint16(lib[2+v.Image*2:]))
		end := int(binary.LittleEndian.Uint16(lib[4+v.Image*2:]))
		if end-at != 85 || !bytes.Equal(lib[at:at+4], []byte{9, 0, 9, 0}) || powerSHA(lib[at+4:end]) != v.SHA {
			panic("火力參考來源 bytes 失配")
		}
		var key [81]byte
		copy(key[:], lib[at+4:end])
		r.sources[key] = powerSource{v.Image, image.Pt(col*36, row*36)}
	}
	// 採 READY 前完整原型，獨立於產品載入的 atlas 檔。
	raw, err = os.ReadFile(filepath.Join(dir, "power-facility-v2", "thermal-hd.png"))
	check(err)
	if powerSHA(raw) != "ceb6c9a9dfe64330c4004c6492b6c0997fc84a2f8881688d506c44e481de8dc2" {
		panic("火力 READY 前參考圖失配")
	}
	r.atlas, err = png.Decode(bytes.NewReader(raw))
	check(err)
	if r.atlas.Bounds() != image.Rect(0, 0, 216, 216) || len(r.sources) != 36 {
		panic("火力參考完整圖形態失配")
	}
	return r
}

func powerRect(px []byte, x, y, w, h int) []byte {
	out := make([]byte, 0, w*h)
	for row := y; row < y+h; row++ {
		out = append(out, px[row*320+x:row*320+x+w]...)
	}
	return out
}

func (r *powerReference) audit(px []byte, pal [256][3]byte, mode int, enabled, blocked, originValid bool, ox, oy int, fields powerFields) (*powerPixels, error) {
	reported := fields.PowerFacility
	if r == nil {
		if reported.Matched != 0 || reported.Painted != 0 || reported.Fallback != 0 || len(reported.Images) != 0 || len(reported.Reasons) != 0 {
			return nil, fmt.Errorf("火力收據需要固定獨立參考")
		}
		return nil, nil
	}
	active := enabled && !blocked && mode == 19 && originValid && ox >= 0 && ox <= 76 && oy >= 0 && oy <= 74
	colors := []byte{}
	for i := 0; i < 256; i++ {
		if (i >= 103 && i <= 107) || (i >= 144 && i <= 147) || (i >= 201 && i <= 204) {
			colors = append(colors, pal[i][:]...)
		}
	}
	active = active && powerSHA(colors) == "9bd7a6f66fe9e1da47ea3360ffbd0e114616d466034ff8b999529ae38afe6b0b" && powerSHA(powerRect(px, 0, 0, 270, 33)) == "b9b27e2010b2d581cb55c349b5944492ea0077104e15126236fc50b859b51eda"
	active = active && powerSHA(powerRect(px, 18, 38, 99, 22)) != "a93af2ea621191dc51663f84eee9ebc40672d149d585a1458b9edf3c60e872bb" && powerSHA(powerRect(px, 18, 136, 91, 20)) != "01fcb11eb506fd99ea6679b5162d18c3f9a0268800f147657407d7734018ba8c"
	expected := powerCounts{Images: map[int]int{}, Reasons: map[string]int{}}
	pixels := &powerPixels{atlas: r.atlas, cells: map[int]image.Point{}, native: image.NewRGBA(image.Rect(0, 0, 1280, 800)), fallback: map[int]bool{}}
	if active {
		for row := 0; row < 15; row++ {
			for col := 0; col < 29; col++ {
				var key [81]byte
				copy(key[:], powerRect(px, 5+col*9, 34+row*9, 9, 9))
				v, found := r.sources[key]
				if !found {
					if !r.otherHD[key] {
						pixels.fallback[row*29+col] = true
					}
					continue
				}
				expected.Matched++
				valid := true
				for _, index := range key {
					if pal[index] != r.palette[fmt.Sprint(index)] {
						valid = false
					}
				}
				if valid {
					expected.Painted++
					expected.Images[v.index]++
					expected.Reasons["matched-power-facility"]++
					pixels.cells[row*29+col] = v.cell
				} else {
					pixels.fallback[row*29+col] = true
					expected.Fallback++
					expected.Reasons["palette-mismatch"]++
				}
			}
		}
	}
	for grid := range pixels.fallback {
		col, row := grid%29, grid/29
		for y := 0; y < 36; y++ {
			for x := 0; x < 36; x++ {
				color := pal[px[(34+row*9+y/4)*320+5+col*9+x/4]]
				at := ((136+row*36+y)*1280 + 20 + col*36 + x) * 4
				copy(pixels.native.Pix[at:at+4], []byte{color[0], color[1], color[2], 255})
			}
		}
	}
	if reported.Images == nil {
		reported.Images = map[int]int{}
	}
	if reported.Reasons == nil {
		reported.Reasons = map[string]int{}
	}
	if !reflect.DeepEqual(reported, expected) {
		return nil, fmt.Errorf("火力統計與獨立來源不符：%v / %v", reported, expected)
	}
	return pixels, nil
}

func (p *powerPixels) pixel(x, y int) (image.Image, int, int) {
	if p == nil || x < 20 || x >= 1064 || y < 136 || y >= 676 {
		return nil, 0, 0
	}
	x, y = x-20, y-136
	if p.fallback[(y/36)*29+x/36] {
		return p.native, x + 20, y + 136
	}
	if v, found := p.cells[(y/36)*29+x/36]; found {
		return p.atlas, v.X + x%36, v.Y + y%36
	}
	return nil, 0, 0
}
