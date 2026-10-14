package hd

import (
	"bytes"
	"encoding/binary"
	"encoding/hex"
	"fmt"
	"image"
	"image/color"
	"image/draw"
	"strings"
)

// Original offsets and call parameters are independent of editable translations.
var remainingTextBindings = []struct {
	offset int
	key    string
}{
	{0x245c4, "legacy.confused"}, {0x24e3c, "legacy.password_prompt"}, {0x24e4f, "legacy.copyright"},
	{0x24e6e, "legacy.password_table1"}, {0x24e87, "legacy.password_table2"},
	{0x24ea0, "legacy.password_table3"}, {0x24eb9, "legacy.password_table4"}, {0x24ed2, "legacy.copyright"},
	{0x2469a, "intro.date"}, {0x246be, "intro.sogo"}, {0x246df, "intro.housing"}, {0x246fe, "intro.thief"},
	{0x24726, "intro.wait"}, {0x24752, "intro.stop"}, {0x24771, "intro.crime"}, {0x247a2, "intro.metro"},
	{0x247c8, "intro.proof"}, {0x247e3, "intro.traffic"}, {0x2486c, "intro.pollution"}, {0x24889, "intro.waiting"},
	{0x248a4, "intro.savior"}, {0x248bb, "intro.you"}, {0x24a24, "ending.congrats"}, {0x24a41, "ending.respect"},
	{0x24a71, "intro.success"}, {0x24a94, "intro.key"}, {0x24ab9, "intro.medals"}, {0x24b0b, "ending.unfinished"},
	{0x24b5f, "intro.failure"}, {0x24b80, "intro.underpass"}, {0x24b9d, "intro.worse"}, {0x24bcd, "letter.mayor"},
	{0x24bd8, "letter.office"}, {0x24be9, "letter.simple"}, {0x24c04, "letter.traffic_housing"}, {0x24c23, "letter.prices_crime"},
	{0x24c42, "letter.environment_fun"}, {0x24c61, "letter.fire_tax"}, {0x24c80, "letter.work_school"},
	{0x24c9f, "letter.easy"}, {0x24cb6, "letter.citizens"}, {0x25494, "file.confirm_exit"},
}

type TextDraw struct {
	Code                  string `json:"source_hex"`
	X, Y, Ink, Background int
	Style                 uint32 `json:"original_ea"`
	Visible               int    `json:"visible_bytes"`
}
type TextImageField struct {
	Rect       image.Rectangle
	Key        string
	Background byte
	Ink        byte
}
type TextImage struct {
	ID            string
	Raw, Pixels   []byte
	Width, Height int
	Transparent   bool
	Fields        []TextImageField
}
type TextImageDraw struct {
	ID     string
	X, Y   int
	Before []byte
	Clip   image.Rectangle
}
type textSources struct {
	keys   map[string]string
	zh     map[uint16][]byte
	ascii  []byte
	images []TextImage
}

func remainingKeys() (out []string) {
	for _, b := range remainingTextBindings {
		out = append(out, b.key)
	}
	return append(out, "art.protest", "art.department_store", "art.pacific", "art.bank", "art.maximum", "art.minimum")
}

// InitTextSources follows spec/033 READY; all inputs stay read-only.
func (r *Renderer) InitTextSources(exe, rom, romA []byte) []TextImage {
	r.textSources, r.textROM = nil, nil
	if digest(exe) != "798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3" || digest(rom) != romSHA || digest(romA) != "5d66f238dce650b8a407986100392ee4b8ac2aa23a033e80a7ca18ed91b3d9b0" {
		return nil
	}
	u := &textSources{keys: map[string]string{}, zh: map[uint16][]byte{}}
	for _, b := range remainingTextBindings {
		end := bytes.IndexByte(exe[b.offset:], 0)
		if end < 0 || end > 512 {
			return nil
		}
		u.keys[hex.EncodeToString(exe[b.offset:b.offset+end])] = b.key
	}
	for _, b := range interfaceNotices {
		u.keys[b.code] = b.key
	}
	member := func(b []byte, i int) []byte {
		o, n := int(binary.LittleEndian.Uint32(b[18+16*i:])), int(binary.LittleEndian.Uint16(b[22+16*i:]))
		return b[o : o+n]
	}
	u.ascii = member(rom, 56)
	zh, codes := member(rom, 57), member(rom, 58)
	for i := 0; i < 402; i++ {
		c := binary.BigEndian.Uint16(codes[2+i*2:])
		if u.zh[c] == nil {
			u.zh[c] = zh[6+i*30 : 6+(i+1)*30]
		}
	}
	// IV2 sparse writes: unsigned offset, byte count, bytes; carry ends the stream.
	raw := member(romA, 38)
	pix := bytes.Repeat([]byte{255}, 320*200)
	at, pos := 0, 0
	for at+2 <= len(raw) {
		delta := int(binary.LittleEndian.Uint16(raw[at:]))
		at += 2
		if pos+delta > 65535 {
			break
		}
		pos += delta
		if at >= len(raw) {
			return nil
		}
		n := int(raw[at])
		at++
		if at+n > len(raw) || pos+n > len(pix) {
			return nil
		}
		copy(pix[pos:pos+n], raw[at:at+n])
		at += n
		pos += n
	}
	if at != len(raw) {
		return nil
	}
	minx, miny, maxx, maxy := 320, 200, 0, 0
	for i, v := range pix {
		if v != 255 {
			x, y := i%320, i/320
			if x < minx {
				minx = x
			}
			if y < miny {
				miny = y
			}
			if x > maxx {
				maxx = x
			}
			if y > maxy {
				maxy = y
			}
		}
	}
	// The sparse stream begins at the caller's origin; retain its empty margins.
	w, h := maxx+1, maxy+1
	small := make([]byte, w*h)
	for y := 0; y < h; y++ {
		copy(small[y*w:(y+1)*w], pix[y*320:y*320+w])
	}
	u.images = append(u.images, TextImage{ID: "small-title", Raw: raw, Pixels: small, Width: w, Height: h, Transparent: true, Fields: []TextImageField{{image.Rect(0, 0, w, h), "startup.title", 255, 14}}})
	for _, index := range []int{6, 10, 15, 16, 17} {
		raw := member(romA, index)
		entries := [][]byte{raw}
		if index == 10 {
			entries = nil
			count := int(binary.LittleEndian.Uint16(raw))
			for i := 0; i < count; i++ {
				o := int(binary.LittleEndian.Uint16(raw[2+i*2:]))
				end := len(raw)
				for j := 0; j < count; j++ {
					p := int(binary.LittleEndian.Uint16(raw[2+j*2:]))
					if p > o && p < end {
						end = p
					}
				}
				entries = append(entries, raw[o:end])
			}
		}
		for imageIndex, data := range entries {
			w, h := int(binary.LittleEndian.Uint16(data)), int(binary.LittleEndian.Uint16(data[2:]))
			pixels := append([]byte(nil), data[4:]...)
			if len(pixels) != w*h {
				pixels = decodeTextRLE(data)
				if len(pixels) != w*h {
					return nil
				}
			}
			im := TextImage{ID: formatTextImageID(index, imageIndex), Raw: data, Pixels: pixels, Width: w, Height: h, Transparent: true}
			switch index {
			case 6:
				im.Fields = []TextImageField{{image.Rect(0, 0, w, h), "startup.title", 255, 14}}
			case 10:
				// Every library phase is retained, including the repeated fourth entry.
				im.Fields = []TextImageField{{image.Rect(108, 2, 149, 35), "art.protest", 101, 15}}
			case 15, 16:
				im.Fields = []TextImageField{{image.Rect(47, 2, 161, 23), "art.department_store", 16, 74}, {image.Rect(6, 22, 34, 37), "art.pacific", 16, 32}, {image.Rect(178, 22, 206, 37), "art.pacific", 16, 32}}
			case 17:
				im.Fields = []TextImageField{{image.Rect(45, 0, 174, 25), "art.bank", pixels[24*w+48], 33}}
			}
			u.images = append(u.images, im)
		}
	}
	r.textSources = u
	r.textROM = rom
	return u.images
}

func formatTextImageID(member, index int) string { return fmt.Sprintf("romA-%d-%d", member, index) }
func decodeTextRLE(raw []byte) (out []byte) {
	w, h := int(binary.LittleEndian.Uint16(raw)), int(binary.LittleEndian.Uint16(raw[2:]))
	for at := 4; at < len(raw); {
		v, n := raw[at], 1
		at++
		if v == 0 {
			if at+2 > len(raw) {
				return nil
			}
			v, n = raw[at], int(raw[at+1])
			at += 2
		}
		if n == 0 || len(out)+n > w*h {
			return nil
		}
		out = append(out, bytes.Repeat([]byte{v}, n)...)
	}
	if len(out) != w*h {
		return nil
	}
	return
}

func (u *textSources) glyphs(raw []byte) (parts [][]byte, width int, ok bool) {
	for at := 0; at < len(raw); {
		if raw[at] < 128 {
			if raw[at] < 32 || raw[at] > 126 {
				return nil, 0, false
			}
			parts = append(parts, raw[at:at+1])
			at++
			width += 6
		} else {
			if at+2 > len(raw) || u.zh[binary.BigEndian.Uint16(raw[at:])] == nil {
				return nil, 0, false
			}
			parts = append(parts, raw[at:at+2])
			at += 2
			width += 16
		}
	}
	return parts, width, true
}

func (r *Renderer) SetTextDraws(texts []TextDraw, images []TextImageDraw) {
	r.textDraws = texts
	r.textImageDraws = images
}

func (r *Renderer) paintTextSources(dst *image.RGBA, px []byte, pal [256][3]byte) (int, string) {
	r.lastTextKeys = nil
	r.lastTextRects = nil
	if r.textSources == nil || r.locale == nil || r.locale.reason != "" {
		return 0, "source-resource-fallback"
	}
	u := r.textSources
	painted := 0
	last := ""
	for _, source := range r.textDraws {
		key := u.keys[source.Code]
		if key == "" {
			continue
		}
		raw, e := hex.DecodeString(source.Code)
		if e != nil {
			continue
		}
		parts, width, ok := u.glyphs(raw)
		if !ok || source.X < 0 || source.Y < 0 || source.X+width > 320 || source.Y+14 > 200 || source.Ink < 0 || source.Ink > 255 {
			continue
		}
		if source.Style != 0x149b8 && source.Style != 0x14a92 && source.Style != 0x14ed2 && source.Style != 0x14d74 {
			continue
		}
		if source.Style != 0x14d74 && !strings.HasPrefix(key, "intro.") && !strings.HasPrefix(key, "letter.") && !strings.HasPrefix(key, "ending.") && !strings.HasPrefix(key, "legacy.") {
			continue
		}
		if source.Style == 0x14d74 && (source.X != 19 || source.Y != 177 || source.Ink != 32) {
			continue
		}
		for _, base := range []byte{0, 31, 21, 12} {
			if source.Style == 0x14d74 && base != 21 || source.Style == 0x14a92 && int(base) != source.Background {
				continue
			}
			fieldWidth := width
			if source.Style == 0x149b8 || source.Style == 0x14ed2 {
				fieldWidth = 320 - source.X
			}
			expected := bytes.Repeat([]byte{base}, fieldWidth*14)
			dx, consumed, visible, leading := 0, 0, 0, 0
			stillLeading := true
			for _, p := range parts {
				if stillLeading && bytes.Equal(p, []byte{0xa1, 0x40}) {
					leading++
				} else {
					stillLeading = false
				}
				typed := source.Style == 0x14ed2 || source.Style == 0x14d74
				show := !typed || consumed+len(p) <= source.Visible
				if show {
					visible++
					g, w, h, dy := []byte(nil), 15, 14, 0
					if len(p) == 1 {
						g = u.ascii[6+(int(p[0])-32)*7 : 6+(int(p[0])-31)*7]
						w, h, dy = 5, 7, 4
					} else {
						g = u.zh[binary.BigEndian.Uint16(p)]
					}
					if source.Style == 0x14ed2 {
						for y := 0; y < h; y++ {
							for x := 0; x < w; x++ {
								expected[(y+dy)*fieldWidth+dx+x] = byte(source.Background)
							}
						}
					}
					stampInterface(expected, fieldWidth, dx, dy, g, w, h, byte(source.Ink))
				}
				consumed += len(p)
				if len(p) == 1 {
					dx += 6
				} else {
					dx += 16
				}
			}
			rect := image.Rect(source.X, source.Y, source.X+fieldWidth, source.Y+14)
			if !bytes.Equal(footerCrop(px, rect), expected) {
				continue
			}
			if source.Style == 0x14d74 {
				frame := decodeIconSource(r.textROM)
				for y := 0; y < 14; y++ {
					copy(frame[(177+y)*320+19:(177+y)*320+19+width], expected[y*width:(y+1)*width])
				}
				if !bytes.Equal(footerCrop(px, footerRects[0]), footerCrop(frame, footerRects[0])) {
					continue
				}
			}
			safe := image.Rect(0, 0, (320-source.X)*4, 56)
			patch := image.NewRGBA(safe)
			c := pal[base]
			draw.Draw(patch, patch.Bounds(), image.NewUniform(color.RGBA{c[0], c[1], c[2], 255}), image.Point{}, draw.Src)
			if source.Style == 0x14a92 {
				safe = image.Rect(0, 0, width*4, 56)
				patch = image.NewRGBA(safe)
				draw.Draw(patch, safe, image.NewUniform(color.RGBA{c[0], c[1], c[2], 255}), image.Point{}, draw.Src)
			}
			position := image.Pt(source.X*4, source.Y*4)
			if source.Style == 0x14d74 {
				if paletteDigest(interfaceExtraIndices, pal) != "bb592feaa8a51c36b22b702efa4fbed5a793e43a8029526cd6912d915d8a7919" {
					continue
				}
				safe = image.Rect(0, 0, 896, 72)
				patch = image.NewRGBA(safe)
				draw.Draw(patch, safe, r.footer.art, image.Pt(28, 700), draw.Src)
				position = image.Pt(28, 700)
				safe = safe.Inset(8)
			}
			denom := len(parts) - leading
			numer := visible - leading
			if denom <= 0 {
				continue
			}
			if numer < 0 {
				numer = 0
			}
			fg := pal[source.Ink]
			if e := r.locale.ui.DrawReveal(patch, r.locale.language, key, safe, 48, 14, numer, denom, color.RGBA{fg[0], fg[1], fg[2], 255}); e != nil {
				continue
			}
			draw.Draw(dst, patch.Bounds().Add(position), patch, image.Point{}, draw.Src)
			r.lastTextRects = append(r.lastTextRects, rect)
			painted++
			r.lastTextKeys = append(r.lastTextKeys, key)
			last = key
			break
		}
	}
	return painted, last
}
