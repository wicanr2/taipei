// #39：獨立讀取 ROM 與固定參考，不引用產品呈現器。
package main

import (
	"bytes"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"image"
	"image/draw"
	"image/png"
	"os"
	"path/filepath"
	"strings"
)

type budgetFields struct {
	Budget          bool       `json:"budget"`
	BudgetText      [11]string `json:"budget_text"`
	BudgetColors    [11]byte   `json:"budget_colors"`
	BudgetSelection int        `json:"budget_selection"`
	BudgetReason    string     `json:"budget_reason"`
}
type budgetReference struct {
	base       []byte
	ascii      [12][7]byte
	palette    [256][3]byte
	bg, glyphs image.Image
}

var budgetPositions = [11][3]int{
	{93, 29, 3}, {93, 49, 3}, {93, 68, 3}, {93, 85, 3}, {93, 103, 3},
	{168, 49, 8}, {168, 68, 8}, {168, 85, 8}, {168, 103, 8},
	{51, 120, 8}, {168, 120, 8},
}

func readBudgetReference(dir, original string) *budgetReference {
	if dir == "" {
		return nil
	}
	r := &budgetReference{}
	read := func(name, sha string) []byte {
		b, e := os.ReadFile(filepath.Join(dir, name))
		check(e)
		if fileHash(b) != sha {
			panic("預算固定參考失配：" + name)
		}
		return b
	}
	read("budget-v1/manifest.json", "f6a3052430ad3cc1cda5c737fb21ce6c73c13237e191e29cf0c92684553b9933")
	read("fonts/NotoSansCJKtc-Regular.otf", "dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4")
	read("fonts/LICENSE", "6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2")
	check(json.Unmarshal(read("budget-v1/palette.json", "92e63b93ecf043e77d45db64975aecae89116937314f3985972e864cb7f1f37b"), &r.palette))
	for _, p := range []struct {
		name, sha string
		w, h      int
		dst       *image.Image
	}{
		{"panel.png", "24d6607b61504936a798598e29ebd182b7d65e82c2e744218610337693390388", 940, 528, &r.bg},
		{"glyphs.png", "033f1cfa385290c7f1b812faa0170a3e80af2f4de634ef70d8cf1f84f3c4fba1", 288, 56, &r.glyphs},
	} {
		im, e := png.Decode(bytes.NewReader(read("budget-v1/"+p.name, p.sha)))
		check(e)
		if im.Bounds() != image.Rect(0, 0, p.w, p.h) {
			panic("預算參考形狀失配")
		}
		*p.dst = im
	}
	rom, e := os.ReadFile(filepath.Join(original, "RS201.ROM"))
	check(e)
	if fileHash(rom) != "0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29" {
		panic("預算來源 ROM 失配")
	}
	member := func(i int) []byte {
		a := int(binary.LittleEndian.Uint32(rom[18+i*16:]))
		return rom[a : a+int(binary.LittleEndian.Uint16(rom[22+i*16:]))]
	}
	raw := member(2)
	for i := 4; i < len(raw); i++ {
		if raw[i] != 0 {
			r.base = append(r.base, raw[i])
		} else {
			if i+2 >= len(raw) {
				panic("預算 RLE 不完整")
			}
			r.base = append(r.base, bytes.Repeat(raw[i+1:i+2], int(raw[i+2]))...)
			i += 2
		}
	}
	if len(r.base) != 31020 || fileHash(r.base) != "db92d35996a6c8fc112d129ab0a92d1018384495cd38b31d637df468b52c7967" {
		panic("預算背景失配")
	}
	for _, p := range budgetPositions {
		for y := p[1]; y < p[1]+7; y++ {
			copy(r.base[y*235+p[0]:y*235+p[0]+p[2]*6], bytes.Repeat([]byte{3}, p[2]*6))
		}
	}
	for i, ch := range " -0123456789" {
		for y := 0; y < 7; y++ {
			r.ascii[i][y] = member(56)[6+(int(ch)-32)*7+y] >> 3
		}
	}
	return r
}

func (r *budgetReference) compose(px []byte, pal [256][3]byte, mode int, enabled bool, m budgetFields) (*image.RGBA, error) {
	fail := func(why string) (*image.RGBA, error) { return nil, fmt.Errorf("預算：%s", why) }
	empty := !m.Budget && m.BudgetText == [11]string{} && m.BudgetColors == [11]byte{}
	if r == nil {
		if !empty {
			return fail("缺少固定參考或原版 ROM")
		}
		return nil, nil
	}
	raw := fileCrop(px, image.Rect(18, 37, 253, 169))
	rebuilt := append([]byte(nil), r.base...)
	var text [11]string
	var colors [11]byte
	valid, selected, red := true, -1, 0
	for line, p := range budgetPositions {
		ink := map[byte]bool{}
		for y := p[1]; y < p[1]+7; y++ {
			for x := p[0]; x < p[0]+p[2]*6; x++ {
				if v := raw[y*235+x]; v != 3 {
					ink[v] = true
				}
			}
		}
		if len(ink) != 1 || (!ink[0] && !ink[12]) {
			valid = false
		}
		if ink[12] {
			colors[line] = 12
			if line < 5 {
				selected, red = line, red+1
			} else {
				valid = false
			}
		}
		for col := 0; col < p[2]; col++ {
			var bits [7]byte
			for y := 0; y < 7; y++ {
				for x := 0; x < 5; x++ {
					if raw[(p[1]+y)*235+p[0]+col*6+x] == colors[line] {
						bits[y] |= 16 >> uint(x)
					}
				}
			}
			index := -1
			for i, candidate := range r.ascii {
				if candidate == bits {
					index = i
					break
				}
			}
			if index < 0 {
				valid = false
				continue
			}
			text[line] += string(" -0123456789"[index])
			for y, bits := range r.ascii[index] {
				for x := 0; x < 5; x++ {
					if bits&(16>>uint(x)) != 0 {
						rebuilt[(p[1]+y)*235+p[0]+col*6+x] = colors[line]
					}
				}
			}
		}
		number := strings.TrimPrefix(strings.TrimLeft(text[line], " "), "-")
		if number == "" || strings.ContainsAny(number, " -") {
			valid = false
		}
	}
	if !valid || red != 1 || !bytes.Equal(raw, rebuilt) || mode != 19 {
		if !empty {
			return fail("未知來源宣稱覆繪或洩漏欄位")
		}
		return nil, nil
	}
	paletteOK := true
	for _, v := range raw {
		paletteOK = paletteOK && pal[v] == r.palette[v]
	}
	if !enabled || !paletteOK {
		reason := "original"
		if enabled {
			reason = "budget-palette-mismatch"
		}
		if !empty || m.BudgetSelection != -1 || m.BudgetReason != reason {
			return fail("原版主題或色盤失配未完整回退")
		}
		return nil, nil
	}
	if !m.Budget || m.BudgetText != text || m.BudgetColors != colors || m.BudgetSelection != selected || m.BudgetReason != "matched-budget" {
		return fail("完整來源、十一欄或選取中繼資料失配")
	}
	out := image.NewRGBA(image.Rect(0, 0, 940, 528))
	draw.Draw(out, out.Bounds(), r.bg, image.Point{}, draw.Src)
	for i, value := range text {
		p := budgetPositions[i]
		for col, ch := range value {
			index := strings.IndexRune(" -0123456789", ch)
			row := 0
			if colors[i] == 12 {
				row = 28
			}
			x, y := (p[0]+col*6)*4, p[1]*4
			draw.Draw(out, image.Rect(x, y, x+24, y+28), r.glyphs, image.Pt(index*24, row), draw.Over)
		}
	}
	return out, nil
}
