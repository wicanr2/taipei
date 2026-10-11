// #29：城市框架固定參考逐像素核對。來源獨立重算另見 hd_chrome_check.py。
package main

import (
	"bytes"
	"crypto/sha256"
	"fmt"
	"image"
	"image/png"
	"math/bits"
	"os"
	"path/filepath"
)

type chromeFields struct {
	ChromeParts    int    `json:"chrome_parts"`
	ChromeMask     uint8  `json:"chrome_mask"`
	ChromeRings    int    `json:"chrome_rings"`
	ChromeRingMask uint16 `json:"chrome_ring_mask"`
	ChromeReason   string `json:"chrome_reason"`
}
type chromeReference struct {
	frame, rings image.Image
	part         [64000]int8
	ring         [64000]int8
}

func readChrome(dir string) *chromeReference {
	if dir == "" {
		return nil
	}
	r := &chromeReference{}
	for i := range r.part {
		r.part[i] = -1
		r.ring[i] = -1
	}
	for _, a := range []struct {
		name, sha string
		shape     image.Rectangle
		dst       *image.Image
	}{
		{"frame.png", "d3391282c3fde64b60b64fe59ba756537c4bb60b3766a161106e5432b4e396d6", image.Rect(0, 0, 1280, 800), &r.frame},
		{"rings.png", "8b4c017f525d6b947e7fc446132cef79af053f1916e6d36ea6a8b2d746cc9fc0", image.Rect(0, 0, 264, 88), &r.rings},
	} {
		raw, e := os.ReadFile(filepath.Join(dir, a.name))
		check(e)
		if fmt.Sprintf("%x", sha256.Sum256(raw)) != a.sha {
			panic("城市框架參考失配")
		}
		im, e := png.Decode(bytes.NewReader(raw))
		check(e)
		if im.Bounds() != a.shape {
			panic("城市框架參考尺寸失配")
		}
		*a.dst = im
	}
	for y := 0; y < 200; y++ {
		for x := 0; x < 320; x++ {
			p := int8(-1)
			switch {
			case x < 270 && y < 34:
				p = 0
			case x < 5 && y >= 34 && y < 169:
				p = 1
			case x >= 266 && x < 270 && y >= 34 && y < 169:
				p = 2
			case x < 270 && y >= 169 && y < 174:
				p = 3
			case x >= 270 && y < 174:
				p = 4
			case y >= 174:
				if !(y >= 175 && y < 193 && ((x >= 7 && x < 231) || (x >= 244 && x < 315))) {
					p = 5
				}
			}
			r.part[y*320+x] = p
		}
	}
	for i := 0; i < 14; i++ {
		x, y := 273+23*(i%2), 4+24*(i/2)
		for yy := 0; yy < 22; yy++ {
			for xx := 0; xx < 22; xx++ {
				at := (y+yy)*320 + x + xx
				r.part[at] = -1
				if xx == 0 || xx == 21 || yy == 0 || yy == 21 {
					r.ring[at] = int8(i)
				}
			}
		}
	}
	return r
}
func (r *chromeReference) validate(m chromeFields) error {
	if m.ChromeMask>>6 != 0 || m.ChromeRingMask>>14 != 0 || bits.OnesCount8(m.ChromeMask) != m.ChromeParts || bits.OnesCount16(m.ChromeRingMask) != m.ChromeRings {
		return fmt.Errorf("城市框架遮罩及數量不符")
	}
	if m.ChromeMask != 0 || m.ChromeRingMask != 0 {
		if r == nil {
			return fmt.Errorf("缺少城市框架固定參考")
		}
		want := "partial-chrome"
		if m.ChromeParts == 6 && m.ChromeRings == 14 {
			want = "matched-chrome"
		}
		if m.ChromeReason != want {
			return fmt.Errorf("城市框架原因不符")
		}
	}
	return nil
}
func (r *chromeReference) pixel(m chromeFields, px []byte, x, y int) (image.Image, int, int) {
	if r == nil {
		return nil, 0, 0
	}
	at := (y/4)*320 + x/4
	p := r.part[at]
	if p >= 0 && m.ChromeMask&(1<<p) != 0 {
		return r.frame, x, y
	}
	i := r.ring[at]
	if i >= 0 && m.ChromeRingMask&(1<<i) != 0 {
		xx, yy := 273+23*(int(i)%2), 4+24*(int(i)/2)
		v := -1
		switch px[yy*320+xx] {
		case 15:
			v = 0
		case 32:
			v = 1
		case 186:
			v = 2
		}
		if v >= 0 {
			return r.rings, v*88 + x - xx*4, y - yy*4
		}
	}
	return nil, 0, 0
}
