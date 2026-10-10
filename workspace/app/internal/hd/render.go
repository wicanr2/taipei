// Package hd is the discardable live prototype described by spec/010.
// It owns only presentation pixels and never imports the DOS executor.
package hd

import (
	"crypto/sha256"
	"encoding/binary"
	"fmt"
	"image"
	"image/png"
	"os"
	"path/filepath"
)

const romSHA = "0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29"
const uiSHA = "b9b27e2010b2d581cb55c349b5944492ea0077104e15126236fc50b859b51eda"
const paletteSHA = "9bd7a6f66fe9e1da47ea3360ffbd0e114616d466034ff8b999529ae38afe6b0b"

var materials = map[string]string{
	"water":  "c5946a794cb44daea5e1492ecd880a0e2bb42e9ebe6da62e472a651abfa26015",
	"sand":   "90c23e56f9c8a116fbe8cc7d8b2c1a494eb7044d3ff57c3ff28a60f5b911717f",
	"forest": "0bb1f136ce10e014e27626ab11dc5f3c18431fdcb9c6ab8fbd063b478e8644f7",
}

type Stats struct {
	Reason                     string `json:"reason"`
	Matched, Painted, Fallback int
}
type Renderer struct {
	frame   *image.RGBA
	sources map[string]bool
	shades  map[byte][]byte
	reason  string
}

func digest(p []byte) string { return fmt.Sprintf("%x", sha256.Sum256(p)) }
func New(rom []byte, dir string) *Renderer {
	r := &Renderer{frame: image.NewRGBA(image.Rect(0, 0, 1280, 800)), sources: map[string]bool{}, shades: map[byte][]byte{}}
	if digest(rom) != romSHA {
		r.reason = "rom-mismatch"
		return r
	}
	u16 := func(p []byte) int { return int(binary.LittleEndian.Uint16(p)) }
	rec := 8 + 59*16
	off := int(binary.LittleEndian.Uint32(rom[rec+10:]))
	n := u16(rom[rec+14:])
	lib := rom[off : off+n]
	if u16(lib) != 135 {
		r.reason = "library-shape"
		return r
	}
	for i := 0; i < 135; i++ {
		a := u16(lib[2+i*2:])
		z := len(lib)
		if i+1 < 135 {
			z = u16(lib[4+i*2:])
		}
		if a < 272 || a >= z || z > len(lib) {
			r.reason = "library-offset"
			return r
		}
		b := lib[a:z]
		if len(b) != 85 || u16(b) != 9 || u16(b[2:]) != 9 {
			r.reason = "tile-shape"
			return r
		}
		r.sources[string(b[4:])] = true
	}
	for name, want := range materials {
		p, e := os.ReadFile(filepath.Join(dir, name+"-b-v1.png"))
		if e != nil || digest(p) != want {
			continue
		}
		f, e := os.Open(filepath.Join(dir, name+"-b-v1.png"))
		if e != nil {
			continue
		}
		im, e := png.Decode(f)
		f.Close()
		if e != nil || im.Bounds() != image.Rect(0, 0, 1254, 1254) {
			continue
		}
		for index := 0; index < 256; index++ {
			if material(byte(index)) != name {
				continue
			}
			cache := make([]byte, 1044*540*4)
			for y := 0; y < 540; y++ {
				for x := 0; x < 1044; x++ {
					rr, g, b, _ := im.At(x, y).RGBA()
					at := (y*1044 + x) * 4
					for j, v := range []uint32{rr, g, b} {
						value := float64(v>>8) * shade(byte(index))
						if value > 255 {
							value = 255
						}
						cache[at+j] = byte(value)
					}
					cache[at+3] = 255
				}
			}
			r.shades[byte(index)] = cache
		}
	}
	return r
}

func (r *Renderer) Render(px []byte, pal [256][3]uint8, mode int, blocked, enabled bool) (*image.RGBA, Stats) {
	stats := Stats{Fallback: 435, Reason: "original"}
	if len(px) != 64000 {
		clear(r.frame.Pix)
		stats.Reason = "frame-shape"
		return r.frame, stats
	}
	for y := 0; y < 200; y++ {
		for x := 0; x < 320; x++ {
			c := pal[px[y*320+x]]
			for dy := 0; dy < 4; dy++ {
				at := ((y*4+dy)*1280 + x*4) * 4
				for dx := 0; dx < 4; dx++ {
					copy(r.frame.Pix[at+dx*4:at+dx*4+3], c[:])
					r.frame.Pix[at+dx*4+3] = 255
				}
			}
		}
	}
	if !enabled {
		return r.frame, stats
	}
	if r.reason != "" {
		stats.Reason = r.reason
		return r.frame, stats
	}
	if mode != 19 {
		stats.Reason = "video-mode"
		return r.frame, stats
	}
	if blocked {
		stats.Reason = "blocking-input"
		return r.frame, stats
	}
	var colors []byte
	for i := 0; i < 256; i++ {
		if material(byte(i)) != "" {
			colors = append(colors, pal[i][:]...)
		}
	}
	if digest(colors) != paletteSHA {
		stats.Reason = "palette-mismatch"
		return r.frame, stats
	}
	top := make([]byte, 0, 270*33)
	for y := 0; y < 33; y++ {
		top = append(top, px[y*320:y*320+270]...)
	}
	if digest(top) != uiSHA {
		stats.Reason = "scene-mismatch"
		return r.frame, stats
	}
	stats.Reason = "matched-city"
	for y := 34; y < 169; y += 9 {
		for x := 5; x < 266; x += 9 {
			var tile [81]byte
			for row := 0; row < 9; row++ {
				copy(tile[row*9:(row+1)*9], px[(y+row)*320+x:(y+row)*320+x+9])
			}
			if !r.sources[string(tile[:])] {
				continue
			}
			stats.Matched++
			known := true
			for _, index := range tile {
				if r.shades[index] == nil {
					known = false
					break
				}
			}
			if !known {
				continue
			}
			for row := 0; row < 9; row++ {
				for col := 0; col < 9; col++ {
					cache := r.shades[tile[row*9+col]]
					for dy := 0; dy < 4; dy++ {
						xx, yy := (x+col)*4, (y+row)*4+dy
						at := (yy*1280 + xx) * 4
						src := ((yy-136)*1044 + xx - 20) * 4
						copy(r.frame.Pix[at:at+16], cache[src:src+16])
					}
				}
			}
			stats.Painted++
			stats.Fallback--
		}
	}
	return r.frame, stats
}
func material(index byte) string {
	switch {
	case index >= 103 && index <= 107:
		return "forest"
	case index >= 144 && index <= 147:
		return "water"
	case index >= 201 && index <= 204:
		return "sand"
	}
	return ""
}
func shade(index byte) float64 {
	switch material(index) {
	case "water":
		return .95 + float64(index-144)*.025
	case "sand":
		return .94 + float64(index-201)*.025
	case "forest":
		return .70 + float64(index-103)*.10
	}
	return 1
}
