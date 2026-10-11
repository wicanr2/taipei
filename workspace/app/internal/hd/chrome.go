package hd

import (
	"bytes"
	"image"
	"image/draw"
	"image/png"
	"os"
	"path/filepath"
)

const chromeFrameSHA = "d3391282c3fde64b60b64fe59ba756537c4bb60b3766a161106e5432b4e396d6"
const chromeRingsSHA = "8b4c017f525d6b947e7fc446132cef79af053f1916e6d36ea6a8b2d746cc9fc0"
const chromeTopSHA = "8e292a6de746cfe2d55f3d3c1db3856f3b247c23512e471b2cbfd4f35272fa76"

type chromePart struct {
	points     []int
	indices    []byte
	paletteSHA string
}
type cityChrome struct {
	base         []byte
	parts        []chromePart
	frame, rings *image.RGBA
	fontOK       bool
	iconIndices  []byte
}

// 固定原版幾何與動態排除範圍；完整來源契約見 spec/019。
func chromePartPoints() [][]int {
	parts := make([][]int, 6)
	for y := 0; y < 200; y++ {
		for x := 0; x < 320; x++ {
			part := -1
			switch {
			case x < 270 && y < 34:
				part = 0
			case x < 5 && y >= 34 && y < 169:
				part = 1
			case x >= 266 && x < 270 && y >= 34 && y < 169:
				part = 2
			case x < 270 && y >= 169 && y < 174:
				part = 3
			case x >= 270 && y < 174:
				slot := false
				for i := 0; i < 14; i++ {
					xx, yy := 273+23*(i%2), 4+24*(i/2)
					if x >= xx && x < xx+22 && y >= yy && y < yy+22 {
						slot = true
						break
					}
				}
				if !slot {
					part = 4
				}
			case y >= 174:
				dynamic := y >= 175 && y < 193 && ((x >= 7 && x < 231) || (x >= 244 && x < 315))
				if !dynamic {
					part = 5
				}
			}
			if part >= 0 {
				parts[part] = append(parts[part], y*320+x)
			}
		}
	}
	return parts
}
func chromeImage(path, want string, shape image.Rectangle) *image.RGBA {
	raw, e := os.ReadFile(path)
	if e != nil || digest(raw) != want {
		return nil
	}
	im, e := png.Decode(bytes.NewReader(raw))
	if e != nil || im.Bounds() != shape {
		return nil
	}
	cache := image.NewRGBA(shape)
	draw.Draw(cache, shape, im, shape.Min, draw.Src)
	return cache
}
func loadCityChrome(rom []byte, dir string) *cityChrome {
	u := &cityChrome{base: decodeIconSource(rom)}
	if u.base == nil {
		return u
	}
	palettes := []string{"812a09c150893419cfdbd5735fdc7ae1894d9269cb700b13aaec67c3145796bd", "72cc9a45a3dcc4f0b4203eb8dfff2aa331815a7b9e440b8f5f5c059743efe3ee", "de9cb1deaf78560bcbe58d5aa914357cc0deb3ac7109aa1f693e73b859e55961", "f18f4072f4d8deb4093618b7a70d385a8ad93db3b1a48db90d198b135e44e73f", "31c580975a1bf0e9163b077268235237dfc0dc5bf6dd464aa6e77c1d06eb6a57", "69fb4bfd6e40e197712e5ba31a22c8b338a0cf947c4818f4831a586423fb46b0"}
	for i, points := range chromePartPoints() {
		var used [256]bool
		for _, at := range points {
			used[u.base[at]] = true
		}
		if i == 0 {
			used[15] = true
		}
		p := chromePart{points: points, paletteSHA: palettes[i]}
		for j, v := range used {
			if v {
				p.indices = append(p.indices, byte(j))
			}
		}
		u.parts = append(u.parts, p)
	}
	var used [256]bool
	for i := 0; i < 14; i++ {
		r := iconRect(i)
		x, y := r.Min.X/4, r.Min.Y/4
		for yy := 0; yy < 20; yy++ {
			for xx := 0; xx < 20; xx++ {
				used[u.base[(y+yy)*320+x+xx]] = true
			}
		}
	}
	for i, v := range used {
		if v {
			u.iconIndices = append(u.iconIndices, byte(i))
		}
	}
	u.frame = chromeImage(filepath.Join(dir, "city-chrome-v1/frame.png"), chromeFrameSHA, image.Rect(0, 0, 1280, 800))
	u.rings = chromeImage(filepath.Join(dir, "city-chrome-v1/rings.png"), chromeRingsSHA, image.Rect(0, 0, 264, 88))
	f, e := os.ReadFile(filepath.Join(dir, "fonts/NotoSansCJKtc-Regular.otf"))
	l, le := os.ReadFile(filepath.Join(dir, "fonts/LICENSE"))
	u.fontOK = e == nil && le == nil && digest(f) == menuFontSHA && digest(l) == menuLicenseSHA
	return u
}
func paletteDigest(indices []byte, palette [256][3]uint8) string {
	var raw []byte
	for _, i := range indices {
		raw = append(raw, palette[i][:]...)
	}
	return digest(raw)
}
func (u *cityChrome) paint(dst *image.RGBA, pixels []byte, palette [256][3]uint8) (int, uint8, int, uint16, string) {
	if u == nil || u.base == nil {
		return 0, 0, 0, 0, "chrome-unavailable"
	}
	parts, mask, rings, ringMask := 0, uint8(0), 0, uint16(0)
	if u.frame != nil {
		for i, p := range u.parts {
			if i == 0 && !u.fontOK {
				continue
			}
			if paletteDigest(p.indices, palette) != p.paletteSHA {
				continue
			}
			matched := true
			if i == 0 {
				raw := make([]byte, 0, len(p.points))
				for _, at := range p.points {
					raw = append(raw, pixels[at])
				}
				matched = digest(raw) == chromeTopSHA
			} else {
				for _, at := range p.points {
					if pixels[at] != u.base[at] {
						matched = false
						break
					}
				}
			}
			if !matched {
				continue
			}
			for _, at := range p.points {
				x, y := at%320*4, at/320*4
				for yy := y; yy < y+4; yy++ {
					a, b := dst.PixOffset(x, yy), u.frame.PixOffset(x, yy)
					copy(dst.Pix[a:a+16], u.frame.Pix[b:b+16])
				}
			}
			parts++
			mask |= 1 << i
		}
	}
	if u.rings != nil && paletteDigest(u.iconIndices, palette) == iconsPaletteSHA {
		for i := 0; i < 14; i++ {
			x, y := 273+23*(i%2), 4+24*(i/2)
			index := pixels[y*320+x]
			variant := -1
			switch index {
			case 15:
				variant = 0
			case 32:
				variant = 1
			case 186:
				variant = 2
			}
			if variant < 0 {
				continue
			}
			rgb := [][3]byte{{255, 255, 255}, {255, 0, 0}, {182, 0, 182}}[variant]
			if palette[index] != rgb {
				continue
			}
			matched := true
			for yy := 0; yy < 22 && matched; yy++ {
				for xx := 0; xx < 22; xx++ {
					at := (y+yy)*320 + x + xx
					want := u.base[at]
					if yy == 0 || yy == 21 || xx == 0 || xx == 21 {
						want = index
					}
					if pixels[at] != want {
						matched = false
						break
					}
				}
			}
			if !matched {
				continue
			}
			for yy := 0; yy < 22; yy++ {
				for xx := 0; xx < 22; xx++ {
					if xx > 0 && xx < 21 && yy > 0 && yy < 21 {
						continue
					}
					for dy := 0; dy < 4; dy++ {
						a, b := dst.PixOffset((x+xx)*4, (y+yy)*4+dy), u.rings.PixOffset(variant*88+xx*4, yy*4+dy)
						copy(dst.Pix[a:a+16], u.rings.Pix[b:b+16])
					}
				}
			}
			rings++
			ringMask |= 1 << i
		}
	}
	reason := "chrome-unavailable"
	if parts > 0 || rings > 0 {
		reason = "partial-chrome"
	}
	if parts == 6 && rings == 14 {
		reason = "matched-chrome"
	}
	return parts, mask, rings, ringMask, reason
}
