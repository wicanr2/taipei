package hd

import (
	"bytes"
	"encoding/binary"
	"image"
	"image/draw"
	"image/png"
	"os"
	"path/filepath"
)

const iconsSHA = "9ad97735f45cab2c968e23d8f1d6924c6b1937854fa4cda1c1c7a5ee90a089ab"
const iconsSourceSHA = "a35e8372b6dbd661444299f3241ad36634291b1c6657e6feacf8189c53e04dd7"
const iconsPaletteSHA = "39592c7fa30a9605b79cc18217f320484e16e3d301c6c8a2a4e992951b32a759"

type toolIcons struct {
	sources [14][400]byte
	atlas   image.Image
	reason  string
	indices []byte
}

func iconRect(i int) image.Rectangle {
	x, y := (274+23*(i%2))*4, (5+24*(i/2))*4
	return image.Rect(x, y, x+80, y+80)
}

// 固定 ROM 成員 1 的介面底圖；完整來源與位址空間見 spec/016。
func decodeIconSource(rom []byte) []byte {
	if digest(rom) != romSHA {
		return nil
	}
	record := 8 + 16
	off := int(binary.LittleEndian.Uint32(rom[record+10:]))
	n := int(binary.LittleEndian.Uint16(rom[record+14:]))
	if off != 1888 || n != 10774 || off+n > len(rom) {
		return nil
	}
	raw := rom[off : off+n]
	if binary.LittleEndian.Uint16(raw) != 320 || binary.LittleEndian.Uint16(raw[2:]) != 200 {
		return nil
	}
	pixels := make([]byte, 0, 64000)
	for at := 4; at < len(raw); {
		value := raw[at]
		at++
		count := 1
		if value == 0 {
			if at+2 > len(raw) {
				return nil
			}
			value, count = raw[at], int(raw[at+1])
			at += 2
		}
		if len(pixels)+count > 64000 {
			return nil
		}
		for j := 0; j < count; j++ {
			pixels = append(pixels, value)
		}
	}
	if len(pixels) != 64000 || digest(pixels) != iconsSourceSHA {
		return nil
	}
	return pixels
}

func loadToolIcons(rom []byte, dir string) *toolIcons {
	u := &toolIcons{reason: "icons-unavailable"}
	source := decodeIconSource(rom)
	if source == nil {
		u.reason = "icons-source-mismatch"
		return u
	}
	raw, err := os.ReadFile(filepath.Join(dir, "city-icons-b-v1.png"))
	if err != nil {
		return u
	}
	if digest(raw) != iconsSHA {
		u.reason = "icons-mismatch"
		return u
	}
	u.atlas, err = png.Decode(bytes.NewReader(raw))
	if err != nil || u.atlas.Bounds() != image.Rect(0, 0, 320, 320) {
		u.reason = "icons-shape"
		return u
	}
	for i := range u.sources {
		rect := iconRect(i)
		x, y := rect.Min.X/4, rect.Min.Y/4
		for row := 0; row < 20; row++ {
			copy(u.sources[i][row*20:(row+1)*20], source[(y+row)*320+x:(y+row)*320+x+20])
		}
	}
	var used [256]bool
	for _, source := range u.sources {
		for _, index := range source {
			used[index] = true
		}
	}
	for index, present := range used {
		if present {
			u.indices = append(u.indices, byte(index))
		}
	}
	u.reason = "matched-icons"
	return u
}

func (u *toolIcons) paint(dst *image.RGBA, pixels []byte, palette [256][3]uint8) (int, uint16, string) {
	if u == nil {
		return 0, 0, "icons-unavailable"
	}
	if u.reason != "matched-icons" {
		return 0, 0, u.reason
	}
	colors := make([]byte, 0, len(u.indices)*3)
	for _, index := range u.indices {
		rgb := palette[index]
		colors = append(colors, rgb[:]...)
	}
	if digest(colors) != iconsPaletteSHA {
		return 0, 0, "icons-palette-mismatch"
	}
	count, mask := 0, uint16(0)
	for i, source := range u.sources {
		rect := iconRect(i)
		x, y := rect.Min.X/4, rect.Min.Y/4
		matched := true
		for row := 0; row < 20; row++ {
			if !bytes.Equal(source[row*20:(row+1)*20], pixels[(y+row)*320+x:(y+row)*320+x+20]) {
				matched = false
				break
			}
		}
		if !matched {
			continue
		}
		draw.Draw(dst, rect, u.atlas, image.Pt((i%4)*80, (i/4)*80), draw.Src)
		count++
		mask |= 1 << i
	}
	return count, mask, "matched-icons"
}
