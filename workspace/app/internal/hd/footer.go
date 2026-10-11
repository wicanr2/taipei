package hd

import (
	"bytes"
	"encoding/binary"
	"image"
	"image/draw"
	"os"
	"path/filepath"
	"strings"
)

const footerGlyphSHA = "df2a49313a51d2076e4880bf88cf4fd8a28d722ea49fb98973c05a094107cd7c"

var footerRects = [2]image.Rectangle{image.Rect(7, 175, 231, 193), image.Rect(244, 175, 315, 193)}

type cityFooter struct {
	base        []byte
	digits      [11][]byte
	chinese     [4][]byte
	indices     [2][]byte
	art, glyphs *image.RGBA
	ready       bool
}

func footerCrop(px []byte, r image.Rectangle) []byte {
	b := make([]byte, 0, r.Dx()*r.Dy())
	for y := r.Min.Y; y < r.Max.Y; y++ {
		b = append(b, px[y*320+r.Min.X:y*320+r.Max.X]...)
	}
	return b
}
func loadCityFooter(rom []byte, dir string) *cityFooter {
	u := &cityFooter{base: decodeIconSource(rom)}
	if len(u.base) != 64000 {
		return u
	}
	member := func(i int) []byte {
		a := int(binary.LittleEndian.Uint32(rom[18+16*i:]))
		n := int(binary.LittleEndian.Uint16(rom[22+16*i:]))
		return rom[a : a+n]
	}
	ascii, cjk := member(56), member(57)
	for i, ch := range "0123456789-" {
		at := 6 + (int(ch)-32)*7
		u.digits[i] = append([]byte(nil), ascii[at:at+7]...)
	}
	for i := 0; i < 4; i++ {
		at := 6 + (107+i)*30
		u.chinese[i] = append([]byte(nil), cjk[at:at+28]...)
	}
	for i, r := range footerRects {
		var used [256]bool
		for _, v := range footerCrop(u.base, r) {
			used[v] = true
		}
		used[15] = true
		if i == 0 {
			used[32] = true
		}
		for j, v := range used {
			if v {
				u.indices[i] = append(u.indices[i], byte(j))
			}
		}
	}
	u.art = chromeImage(filepath.Join(dir, "city-chrome-v1/frame.png"), chromeFrameSHA, image.Rect(0, 0, 1280, 800))
	u.glyphs = chromeImage(filepath.Join(dir, "footer-v1/glyphs.png"), footerGlyphSHA, image.Rect(0, 0, 384, 192))
	f, e := os.ReadFile(filepath.Join(dir, "fonts/NotoSansCJKtc-Regular.otf"))
	l, le := os.ReadFile(filepath.Join(dir, "fonts/LICENSE"))
	m, me := os.ReadFile(filepath.Join(dir, "footer-v1/manifest.json"))
	u.ready = e == nil && le == nil && me == nil && digest(f) == menuFontSHA && digest(l) == menuLicenseSHA && digest(m) == "f74c71434954de88e4c9fe6c924091b7f7f64512b651fa60be29087eae5f9650" && u.art != nil && u.glyphs != nil
	return u
}
func footerStamp(px []byte, x, y int, glyph []byte, width, height int, c byte) {
	stride := (width + 7) / 8
	for dy := 0; dy < height; dy++ {
		for dx := 0; dx < width; dx++ {
			if glyph[dy*stride+dx/8]&(128>>uint(dx%8)) != 0 {
				px[(y+dy)*320+x+dx] = c
			}
		}
	}
}
func (u *cityFooter) slots(px, rebuilt []byte, xs []int, y int, negative bool) (string, bool) {
	text := ""
	for _, x := range xs {
		r := image.Rect(x, y, x+5, y+7)
		raw := footerCrop(px, r)
		if bytes.Equal(raw, footerCrop(rebuilt, r)) {
			text += " "
			continue
		}
		matched := -1
		for i, g := range u.digits {
			ok := true
			for dy := 0; dy < 7 && ok; dy++ {
				for dx := 0; dx < 5; dx++ {
					at := (y+dy)*320 + x + dx
					want := rebuilt[at]
					if g[dy]&(128>>uint(dx)) != 0 {
						want = 15
					}
					if px[at] != want {
						ok = false
						break
					}
				}
			}
			if ok {
				if matched >= 0 {
					return "", false
				}
				matched = i
			}
		}
		if matched < 0 {
			return "", false
		}
		text += string("0123456789-"[matched])
		footerStamp(rebuilt, x, y, u.digits[matched], 5, 7, 15)
	}
	numeric := strings.TrimLeft(text, " ")
	if negative {
		numeric = strings.TrimPrefix(numeric, "-")
	}
	if numeric == "" {
		return "", false
	}
	for _, ch := range numeric {
		if ch < '0' || ch > '9' {
			return "", false
		}
	}
	return text, true
}
func (u *cityFooter) decode(px []byte, part int) ([3]string, bool) {
	var values [3]string
	rebuilt := append([]byte(nil), u.base...)
	if part == 0 {
		if bytes.Equal(footerCrop(px, footerRects[0]), footerCrop(u.base, footerRects[0])) {
			return values, true
		}
		for i, x := range []int{19, 35, 51, 103} {
			footerStamp(rebuilt, x, 177, u.chinese[i], 15, 14, 32)
		}
		v, ok := u.slots(px, rebuilt, []int{67, 73, 79, 85, 91, 97}, 181, false)
		if !ok {
			return values, false
		}
		values[0] = v
	} else {
		sets := [][]int{{253, 259, 265, 271, 277}, {289, 295}, {253, 259, 265, 271, 277, 283, 289, 295}}
		for i, xs := range sets {
			y := 176
			if i == 2 {
				y = 184
			}
			v, ok := u.slots(px, rebuilt, xs, y, i == 2)
			if !ok {
				return values, false
			}
			values[i] = v
		}
	}
	return values, bytes.Equal(footerCrop(px, footerRects[part]), footerCrop(rebuilt, footerRects[part]))
}
func (u *cityFooter) glyph(dst *image.RGBA, index, x, y, w, h int) {
	draw.Draw(dst, image.Rect(x*4, y*4, x*4+w, y*4+h), u.glyphs, image.Pt(index%6*64, index/6*64), draw.Over)
}
func (u *cityFooter) numbers(dst *image.RGBA, text string, x, y int) {
	for i, ch := range text {
		if ch == ' ' {
			continue
		}
		index := int(ch - '0')
		if ch == '-' {
			index = 10
		}
		u.glyph(dst, index, x+i*6, y, 24, 28)
	}
}
func (u *cityFooter) paint(dst *image.RGBA, px []byte, pal [256][3]byte) (uint8, [4]string, string) {
	var values [4]string
	mask := uint8(0)
	if u == nil || !u.ready {
		return mask, values, "footer-unavailable"
	}
	expected := []string{"3b4208dbfa57fcac1e09c52c785ec7f0732799de26e6ece81e1a257edd1ce081", "e2ca09da088ea18b2846c73ba9fddd03b32c20511ca0f60429d03356a37f0c1f"}
	for part, r := range footerRects {
		if paletteDigest(u.indices[part], pal) != expected[part] {
			continue
		}
		text, ok := u.decode(px, part)
		if !ok {
			continue
		}
		out := image.Rect(r.Min.X*4, r.Min.Y*4, r.Max.X*4, r.Max.Y*4)
		draw.Draw(dst, out, u.art, out.Min, draw.Src)
		if part == 0 {
			values[0] = text[0]
			if text[0] != "" {
				for i, x := range []int{19, 35, 51, 103} {
					u.glyph(dst, 11+i, x, 177, 60, 56)
				}
				u.numbers(dst, text[0], 67, 181)
			}
		} else {
			copy(values[1:], text[:])
			u.numbers(dst, text[0], 253, 176)
			u.numbers(dst, text[1], 289, 176)
			u.numbers(dst, text[2], 253, 184)
			for i, p := range []image.Point{{283, 176}, {303, 176}, {303, 184}} {
				u.glyph(dst, 15+i, p.X, p.Y, 28, 28)
			}
			// 未確認語意的原版符號，保留原始四倍像素。
			for y := 184; y < 191; y++ {
				for x := 247; x < 254; x++ {
					c := pal[px[y*320+x]]
					for dy := 0; dy < 4; dy++ {
						at := dst.PixOffset(x*4, y*4+dy)
						for dx := 0; dx < 4; dx++ {
							copy(dst.Pix[at+dx*4:at+dx*4+4], []byte{c[0], c[1], c[2], 255})
						}
					}
				}
			}
		}
		mask |= 1 << part
	}
	reason := "footer-source-mismatch"
	if mask > 0 {
		reason = "partial-footer"
	}
	if mask == 3 {
		reason = "matched-footer"
	}
	return mask, values, reason
}
