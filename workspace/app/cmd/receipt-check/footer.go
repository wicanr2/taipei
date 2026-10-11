// #31：以固定外部 atlas 與收據字串獨立組合參考；來源另由 Python 重算。
package main

import (
	"bytes"
	"crypto/sha256"
	"fmt"
	"image"
	"image/draw"
	"image/png"
	"os"
	"path/filepath"
	"strings"
)

type footerFields struct {
	FooterMask   uint8     `json:"footer_mask"`
	FooterText   [4]string `json:"footer_text"`
	FooterReason string    `json:"footer_reason"`
}
type footerReference struct{ bg, glyphs *image.RGBA }

func readFooter(dir string) *footerReference {
	if dir == "" {
		return nil
	}
	r := &footerReference{}
	for _, a := range []struct {
		name, sha string
		shape     image.Rectangle
		dst       **image.RGBA
	}{
		{"city-chrome-v1/frame.png", "d3391282c3fde64b60b64fe59ba756537c4bb60b3766a161106e5432b4e396d6", image.Rect(0, 0, 1280, 800), &r.bg},
		{"footer-v1/glyphs.png", "df2a49313a51d2076e4880bf88cf4fd8a28d722ea49fb98973c05a094107cd7c", image.Rect(0, 0, 384, 192), &r.glyphs},
	} {
		want := a.sha
		raw, e := os.ReadFile(filepath.Join(dir, a.name))
		check(e)
		if fmt.Sprintf("%x", sha256.Sum256(raw)) != want {
			panic("底部固定參考失配")
		}
		im, e := png.Decode(bytes.NewReader(raw))
		check(e)
		if im.Bounds() != a.shape {
			panic("底部參考尺寸失配")
		}
		*a.dst = image.NewRGBA(a.shape)
		draw.Draw(*a.dst, a.shape, im, a.shape.Min, draw.Src)
	}
	return r
}
func (r *footerReference) compose(m footerFields) (*image.RGBA, error) {
	if m.FooterMask > 3 {
		return nil, fmt.Errorf("底部遮罩越界")
	}
	if m.FooterMask == 0 {
		return nil, nil
	}
	if r == nil {
		return nil, fmt.Errorf("缺少底部固定參考")
	}
	reason := "partial-footer"
	if m.FooterMask == 3 {
		reason = "matched-footer"
	}
	if m.FooterReason != reason {
		return nil, fmt.Errorf("底部原因失配")
	}
	dst := image.NewRGBA(r.bg.Bounds())
	draw.Draw(dst, dst.Bounds(), r.bg, image.Point{}, draw.Src)
	glyph := func(index, x, y, w, h int) {
		draw.Draw(dst, image.Rect(x*4, y*4, x*4+w, y*4+h), r.glyphs, image.Pt(index%6*64, index/6*64), draw.Over)
	}
	digits := func(s string, n, x, y int, negative bool) error {
		if len(s) != n {
			return fmt.Errorf("底部字串長度不符")
		}
		numeric := strings.TrimLeft(s, " ")
		if negative {
			numeric = strings.TrimPrefix(numeric, "-")
		}
		if numeric == "" {
			return fmt.Errorf("空數字")
		}
		for _, ch := range numeric {
			if ch < '0' || ch > '9' {
				return fmt.Errorf("未知底部字元")
			}
		}
		for i, ch := range s {
			if ch == ' ' {
				continue
			}
			index := int(ch - '0')
			if ch == '-' {
				index = 10
			}
			glyph(index, x+i*6, y, 24, 28)
		}
		return nil
	}
	if m.FooterMask&1 != 0 && m.FooterText[0] != "" {
		for i, x := range []int{19, 35, 51, 103} {
			glyph(11+i, x, 177, 60, 56)
		}
		if e := digits(m.FooterText[0], 6, 67, 181, false); e != nil {
			return nil, e
		}
	}
	if m.FooterMask&2 != 0 {
		for _, d := range []struct {
			s        string
			n, x, y  int
			negative bool
		}{{m.FooterText[1], 5, 253, 176, false}, {m.FooterText[2], 2, 289, 176, false}, {m.FooterText[3], 8, 253, 184, true}} {
			if e := digits(d.s, d.n, d.x, d.y, d.negative); e != nil {
				return nil, e
			}
		}
		for i, p := range []image.Point{{283, 176}, {303, 176}, {303, 184}} {
			glyph(15+i, p.X, p.Y, 28, 28)
		}
	}
	return dst, nil
}
func footerPoint(m footerFields, x, y int) bool {
	x /= 4
	y /= 4
	return (m.FooterMask&1 != 0 && x >= 7 && x < 231 && y >= 175 && y < 193) || (m.FooterMask&2 != 0 && x >= 244 && x < 315 && y >= 175 && y < 193 && !(x >= 247 && x < 254 && y >= 184 && y < 191))
}
