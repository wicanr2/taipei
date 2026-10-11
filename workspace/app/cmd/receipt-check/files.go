// #38：不引用產品呈現器，從原始 ROM 及固定外部圖檔重新核對。
package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"image"
	"image/draw"
	"image/png"
	"os"
	"path/filepath"
)

type fileFields struct {
	FileDialog string    `json:"file_dialog"`
	FileText   [8]string `json:"file_text"`
	FileColors [8]byte   `json:"file_colors"`
	FileReason string    `json:"file_reason"`
}
type fileReference struct {
	base, question   []byte
	ascii            [95][7]byte
	palette          [256][3]byte
	bg, glyphs, quit image.Image
}

func fileHash(raw []byte) string { return fmt.Sprintf("%x", sha256.Sum256(raw)) }
func fileCrop(px []byte, rect image.Rectangle) []byte {
	var result []byte
	for y := rect.Min.Y; y < rect.Max.Y; y++ {
		result = append(result, px[y*320+rect.Min.X:y*320+rect.Max.X]...)
	}
	return result
}
func readFileReference(dir, original string) *fileReference {
	if dir == "" {
		return nil
	}
	r := &fileReference{}
	read := func(name, hash string) []byte {
		raw, e := os.ReadFile(filepath.Join(dir, name))
		check(e)
		if fileHash(raw) != hash {
			panic("檔案視窗固定參考失配：" + name)
		}
		return raw
	}
	read("file-dialogs-v1/manifest.json", "6fc74370c334d77b62f2e0d224a80cb967d158da3e632a79aa1e4017636792b6")
	read("fonts/NotoSansCJKtc-Regular.otf", "dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4")
	read("fonts/LICENSE", "6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2")
	check(json.Unmarshal(read("file-dialogs-v1/palette.json", "4103f1e8410a2ee91de3074579ce3062de27f48c1d2c415f46bbd195c50b56df"), &r.palette))
	for _, p := range []struct {
		name, hash string
		w, h       int
		dst        *image.Image
	}{
		{"browser.png", "222b2939a1f0eae1b7fc15822babd8dc253d5187b5cbb0d07ca5868c1b050754", 268, 428, &r.bg},
		{"glyphs.png", "147840d8a0a343361f4c2165ab21c28d7b3ff3813d065ff17d6ea378eedc2618", 1024, 832, &r.glyphs},
		{"quit-confirm.png", "b0e62043c86b24a4dbf77dffb7b31dfd1f99430b41131bb9916d6cc4f3151d30", 896, 72, &r.quit},
	} {
		im, e := png.Decode(bytes.NewReader(read("file-dialogs-v1/"+p.name, p.hash)))
		check(e)
		if im.Bounds() != image.Rect(0, 0, p.w, p.h) {
			panic("檔案視窗參考形狀不符")
		}
		*p.dst = im
	}
	rom, e := os.ReadFile(filepath.Join(original, "RS201.ROM"))
	check(e)
	if fileHash(rom) != "0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29" {
		panic("檔案視窗來源 ROM 不符")
	}
	member := func(i int) []byte {
		off := int(binary.LittleEndian.Uint32(rom[18+16*i:]))
		n := int(binary.LittleEndian.Uint16(rom[22+16*i:]))
		return rom[off : off+n]
	}
	decode := func(raw []byte, n int) []byte {
		var result []byte
		for at := 4; at < len(raw); at++ {
			if raw[at] != 0 {
				result = append(result, raw[at])
				continue
			}
			if at+2 >= len(raw) {
				panic("RLE 不完整")
			}
			result = append(result, bytes.Repeat(raw[at+1:at+2], int(raw[at+2]))...)
			at += 2
		}
		if len(result) != n {
			panic("RLE 長度不符")
		}
		return result
	}
	r.base = decode(member(3), 7169)
	if fileHash(r.base) != "697dff15cb595e693f514500531196d2be7f415a2b10e9e99a1182da431657c8" {
		panic("ROM3 來源不符")
	}
	for y := 4; y < 18; y++ {
		copy(r.base[y*67+5:y*67+62], bytes.Repeat([]byte{31}, 57))
	}
	for row := 0; row < 7; row++ {
		for y := 26 + 11*row; y < 33+11*row; y++ {
			copy(r.base[y*67+10:y*67+58], bytes.Repeat([]byte{136}, 48))
		}
	}
	font := member(56)
	for i := range r.ascii {
		for y := 0; y < 7; y++ {
			r.ascii[i][y] = font[6+i*7+y] >> 3
		}
	}
	city := decode(member(1), 64000)
	stamp := func(x, y, w, h int, raw []byte) {
		stride := (w + 7) / 8
		for dy := 0; dy < h; dy++ {
			for dx := 0; dx < w; dx++ {
				if raw[dy*stride+dx/8]&(128>>uint(dx%8)) != 0 {
					city[(y+dy)*320+x+dx] = 32
				}
			}
		}
	}
	for i, index := range []int{188, 301, 55, 302, 51, 49, 50, 167} {
		stamp(19+i*16, 177, 15, 14, member(57)[6+index*30:])
	}
	for i, ch := range "?(Y/N)" {
		stamp(153+i*6, 181, 5, 7, font[6+(int(ch)-32)*7:])
	}
	r.question = fileCrop(city, image.Rect(7, 175, 231, 193))
	if fileHash(r.question) != "84b33e447ebeea82ba9517eda9c987bf8a9bf5cec759892974cb66401caaf701" {
		panic("離開提示來源不符")
	}
	return r
}

func (r *fileReference) compose(px []byte, pal [256][3]byte, mode int, enabled bool, m fileFields) (*image.RGBA, image.Rectangle, error) {
	fail := func(message string) (*image.RGBA, image.Rectangle, error) {
		return nil, image.Rectangle{}, fmt.Errorf("檔案視窗：%s", message)
	}
	if r == nil {
		if m.FileDialog != "" {
			return fail("缺少固定參考與原版 ROM")
		}
		return nil, image.Rectangle{}, nil
	}
	var text [8]string
	var colors [8]byte
	box := image.Rect(34, 41, 101, 148)
	raw := fileCrop(px, box)
	rebuilt := append([]byte(nil), r.base...)
	valid, red := true, 0
	for line := 0; line < 8; line++ {
		y, bg := 8, byte(31)
		if line > 0 {
			y, bg = 26+11*(line-1), 136
		} else {
			colors[line] = 15
		}
		for dy := 0; dy < 7; dy++ {
			for dx := 0; dx < 48; dx++ {
				v := raw[(y+dy)*67+10+dx]
				if v == bg {
					continue
				}
				if (line == 0 && v != 15) || (line > 0 && v != 31 && v != 32) || (colors[line] != 0 && colors[line] != v) {
					valid = false
				}
				colors[line] = v
			}
		}
		if line > 0 && colors[line] == 32 {
			red++
		}
		for col := 0; col < 8; col++ {
			var bits [7]byte
			for dy := 0; dy < 7; dy++ {
				for dx := 0; dx < 5; dx++ {
					if raw[(y+dy)*67+10+col*6+dx] == colors[line] {
						bits[dy] |= 16 >> uint(dx)
					}
				}
			}
			match := -1
			for i, glyph := range r.ascii {
				if glyph == bits {
					match = i
					break
				}
			}
			if match < 0 {
				valid = false
				continue
			}
			text[line] += string(rune(match + 32))
			for dy, bits := range r.ascii[match] {
				for dx := 0; dx < 5; dx++ {
					if bits&(16>>uint(dx)) != 0 {
						rebuilt[(y+dy)*67+10+col*6+dx] = colors[line]
					}
				}
			}
		}
	}
	family := "file-browser"
	if !valid || red > 1 || !bytes.Equal(raw, rebuilt) {
		box = image.Rect(7, 175, 231, 193)
		raw = fileCrop(px, box)
		if !bytes.Equal(raw, r.question) {
			family = ""
		} else {
			family = "quit-confirm"
		}
		text, colors = [8]string{}, [8]byte{}
	}
	if family == "" || mode != 19 {
		if m.FileDialog != "" || m.FileText != [8]string{} || m.FileColors != [8]byte{} {
			return fail("未知來源卻宣稱覆繪")
		}
		return nil, image.Rectangle{}, nil
	}
	paletteOK := true
	for _, index := range raw {
		if pal[index] != r.palette[index] {
			paletteOK = false
			break
		}
	}
	if !enabled || !paletteOK {
		reason := "original"
		if enabled {
			reason = "file-palette-mismatch"
		}
		if m.FileDialog != "" || m.FileText != [8]string{} || m.FileColors != [8]byte{} || m.FileReason != reason {
			return fail("關閉主題或色盤失配未回退")
		}
		return nil, image.Rectangle{}, nil
	}
	if m.FileDialog != family || m.FileText != text || m.FileColors != colors || m.FileReason != "matched-file-dialog" {
		return fail("來源、文字或墨色不符")
	}
	ref := r.bg
	if family == "quit-confirm" {
		ref = r.quit
	}
	out := image.NewRGBA(ref.Bounds())
	draw.Draw(out, out.Bounds(), ref, image.Point{}, draw.Src)
	if family == "file-browser" {
		for line, value := range text {
			y := 8
			if line > 0 {
				y = 26 + 11*(line-1)
			}
			for col, ch := range value {
				if ch == ' ' {
					continue
				}
				index := int(ch) - 32
				if colors[line] == 32 {
					index += 95
				}
				x := (10 + col*6) * 4
				draw.Draw(out, image.Rect(x, y*4, x+24, y*4+28), r.glyphs, image.Pt(index%16*64, index/16*64), draw.Over)
			}
		}
	}
	return out, image.Rect(box.Min.X*4, box.Min.Y*4, box.Max.X*4, box.Max.Y*4), nil
}
