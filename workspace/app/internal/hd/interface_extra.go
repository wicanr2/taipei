package hd

import (
	"bytes"
	"encoding/binary"
	"encoding/hex"
	"fmt"
	"image"
	"image/color"
	"image/draw"
)

// 032: original source bytes stay separate from editable presentation text.
var interfaceNotices = []struct{ key, code string }{
	{"notice.no_funds", "b3f8a769a5abaaf8a141b867b64fa4a3b0f7a149"},
	{"notice.challenge_disasters", "ac44bed4afc5a141a861c3f8b54caa6bc3f6b3aca149"},
	{"notice.start_only", "a5bbbfefb6b5b6b7a662b943c0b8b67da96caec9b35da977a149"},
	{"notice.population_goal", "aea5b3dfb17aa448a466a477b946a4ada451b855a448a149a149"},
	{"settings.message_speed", "b054aea7b374abd7bdd5bee328302d3929"},
	{"settings.speaker_on", "b3e2a57ab67db1d2"}, {"settings.speaker_off", "b3e2a57ac3f6b3ac"},
	{"settings.sound_off", "adb5aec4c3f6b3ac"}, {"settings.sound_on", "adb5aec4b67db1d2"},
	{"notice.earthquake", "a661be5fa149a149a661be5fa149a149a149"},
	{"notice.fire", "a470a4dfa149a140a4f5a861a149a149"},
	{"notice.nuclear", "a7b9a446a149aed6afe0b971bc74a861c5dca149"},
	{"notice.thermal", "a46ab6d5a4a3a7aea141a4f5a44fb971bc74c37aacb5a149"},
	{"notice.typhoon", "bbe4adb7ab49c5a7a5bba5aba149"},
	{"notice.air_crash", "a5bba5aba457aac5b56fa5cdaac5c3f8a8c6a5f3a149"},
	{"notice.shipwreck", "a5bba5aba57eaefca141b56fa5cdb2eec3f8a149"},
	{"notice.shipwreck_cost", "b2eec3f8b5bdabe1b342b27ab64fa440a6cab855a149"},
	{"notice.protest", "b9efa5abac46a4a3baa1aabab873b2b3a8aba457b5f3c059a149"},
	{"notice.blackout", "a5bba5aba65da8d1b971a4a3a8aca141b0b1b971a149"},
	{"notice.fire_stations", "aef8a8beb6a4b94cabd7afcaa546a149"},
	{"notice.power_budget", "b971bc74b977bae2c459adaba4a3a8aca149"},
	{"notice.power_supply", "b971b7bda8d1c0b3a4a3a8aca141bdd0abd8b971bc74a149"},
}

type interfaceField struct {
	key  string
	rect [4]int
}

var populationFields = []interfaceField{
	{"population.annual", [4]int{70, 7, 66, 18}}, {"population.people", [4]int{194, 7, 18, 18}},
	{"population.annual", [4]int{70, 32, 66, 18}}, {"population.people", [4]int{194, 32, 18, 18}},
	{"population.change", [4]int{46, 57, 66, 18}}, {"population.people", [4]int{195, 57, 18, 18}},
	{"population.growth", [4]int{46, 80, 66, 18}}, {"population.level", [4]int{46, 106, 66, 18}},
}
var opinionFields = []interfaceField{
	{"opinion.title", [4]int{42, 1, 147, 18}},
	{"opinion.traffic", [4]int{2, 20, 66, 17}}, {"opinion.environment", [4]int{125, 20, 66, 17}},
	{"opinion.housing", [4]int{2, 39, 66, 17}}, {"opinion.recreation", [4]int{125, 39, 66, 17}},
	{"opinion.prices", [4]int{2, 58, 66, 17}}, {"opinion.fire", [4]int{125, 58, 66, 17}},
	{"opinion.crime", [4]int{2, 77, 66, 17}}, {"opinion.tax", [4]int{125, 77, 66, 17}},
	{"opinion.education", [4]int{2, 96, 66, 17}}, {"opinion.unemployment", [4]int{125, 96, 66, 17}},
	{"opinion.total", [4]int{65, 114, 63, 17}},
}
var rankKeys = []string{"population.village", "population.town", "population.city", "population.metropolis", "population.megalopolis"}
var rankGlyphs = [][]int{{322, -1, 323}, {324, -1, 325}, {215, -1, 2}, {176, -1, 326}, {91, 176, 326}}
var speedKeys = []string{"speed.sleep", "speed.walk", "speed.jog", "speed.run"}
var disasterCityKeys = []string{"disaster_city.taipei", "disaster_city.taichung", "disaster_city.chiayi", "disaster_city.tainan", "disaster_city.kaohsiung", "disaster_city.hualien"}
var disasterCityCodes = []string{"a861c3f8a15da578a55fa15e", "a861c3f8a15da578a4a4a15e", "a861c3f8a15db9c5b871a15e", "a861c3f8a15da578ab6ea15e", "a861c3f8a15db0aab6afa15e", "a861c3f8a15daae1bdaca15e"}
var interfaceExtraIndices = []byte{0, 1, 9, 11, 12, 13, 14, 15, 16, 20, 21, 22, 23, 25, 27, 32, 34, 38, 55, 79, 120, 123, 124, 125, 138, 159, 161, 162, 163, 187, 192, 194, 196, 202, 203, 204, 205, 210, 213}
var populationSlots = [][3]int{{46, 15, 3}, {143, 15, 8}, {46, 40, 3}, {143, 40, 8}, {144, 65, 8}, {180, 88, 3}}
var opinionSlots = func() (out [][3]int) {
	for _, y := range []int{28, 47, 66, 85, 104} {
		for _, x := range []int{81, 196} {
			out = append(out, [3]int{x, y, 3})
		}
	}
	return append(out, [3]int{130, 123, 3})
}()

type interfaceSources struct {
	disaster            [6][]byte
	population, opinion []byte
	ranks               [5][]byte
	speed               [4][]byte
	notices             map[string]string
	ascii               []byte
}
type interfaceExtraLocale struct {
	disaster            [6]*image.RGBA
	population, opinion *image.RGBA
	ranks               [5]*image.RGBA
	speed               [4]*image.RGBA
	notices             map[string]*image.RGBA
}

func extraKeys() (out []string) {
	for _, group := range [][]interfaceField{populationFields, opinionFields} {
		for _, f := range group {
			out = append(out, f.key)
		}
	}
	out = append(out, rankKeys...)
	out = append(out, speedKeys...)
	out = append(out, disasterCityKeys...)
	for _, n := range interfaceNotices {
		out = append(out, n.key)
	}
	return
}

func decodeInterfaceMember(rom []byte, member, w, h int) []byte {
	off, n := int(binary.LittleEndian.Uint32(rom[18+16*member:])), int(binary.LittleEndian.Uint16(rom[22+16*member:]))
	raw := rom[off : off+n]
	if len(raw) < 4 || int(binary.LittleEndian.Uint16(raw)) != w || int(binary.LittleEndian.Uint16(raw[2:])) != h {
		return nil
	}
	out := make([]byte, 0, w*h)
	for at := 4; at < len(raw); {
		v, count := raw[at], 1
		at++
		if v == 0 {
			if at+2 > len(raw) {
				return nil
			}
			v, count = raw[at], int(raw[at+1])
			at += 2
		}
		if len(out)+count > w*h {
			return nil
		}
		for i := 0; i < count; i++ {
			out = append(out, v)
		}
	}
	if len(out) != w*h {
		return nil
	}
	return out
}

func loadInterfaceSources(rom []byte) *interfaceSources {
	u := &interfaceSources{notices: map[string]string{}}
	if digest(rom) != romSHA {
		return u
	}
	mem := func(i int) []byte {
		off, n := int(binary.LittleEndian.Uint32(rom[18+16*i:])), int(binary.LittleEndian.Uint16(rom[22+16*i:]))
		return rom[off : off+n]
	}
	u.population = decodeInterfaceMember(rom, 13, 235, 132)
	u.opinion = decodeInterfaceMember(rom, 14, 235, 132)
	if digest(u.population) != "9e700aade5641d18fe5e21215a88e621c1a3a955d47d6bc5930d8eb18c9fab19" || digest(u.opinion) != "a1be5c63d2cb40a50027866805e0f7c3b80a611f16aed1abc3f2346c02f5b8c6" {
		u.population = nil
		u.opinion = nil
		return u
	}
	u.ascii = mem(56)
	zh, codes := mem(57), mem(58)
	for i, indices := range rankGlyphs {
		u.ranks[i] = make([]byte, 48*14)
		for at := range u.ranks[i] {
			u.ranks[i][at] = 9
		}
		for col, index := range indices {
			if index < 0 {
				continue
			}
			stampInterface(u.ranks[i], 48, col*16, 0, zh[6+index*30:6+(index+1)*30], 15, 14, 13)
		}
	}
	base := decodeInterfaceMember(rom, 12, 165, 41)
	if digest(base) != "ebc0873bab68422d2bae28af7e1fa2734a8cb04aaa4aecf7c71e4a7676f4ed78" {
		return u
	}
	for selected := range speedKeys {
		u.speed[selected] = append([]byte(nil), base...)
		indices := [][]int{{361, 362}, {363, 364}, {365, 366}, {367, 366}}[selected]
		for col, index := range indices {
			stampInterface(u.speed[selected], 165, 7+selected*40+col*16, 14, zh[6+index*30:6+(index+1)*30], 15, 14, 12)
		}
	}
	lookup := map[uint16]int{}
	for i := 0; i < 402; i++ {
		c := binary.BigEndian.Uint16(codes[2+i*2:])
		if _, ok := lookup[c]; !ok {
			lookup[c] = i
		}
	}
	disasterBase := decodeInterfaceMember(rom, 18, 236, 132)
	if digest(disasterBase) != "bb31340f9990e90edba6eaa575966b8dd29ed72ba014357cd1dd1825ace5667a" {
		return u
	}
	for selection := range disasterCityKeys {
		frame := append([]byte(nil), disasterBase...)
		for option, code := range disasterCityCodes {
			raw, _ := hex.DecodeString(code)
			ink := byte(55)
			if option == selection {
				ink = 15
			}
			for col := 0; col < 6; col++ {
				index := lookup[binary.BigEndian.Uint16(raw[col*2:])]
				stampInterface(frame, 236, 13+(option/3)*114+col*16, 43+(option%3)*31, zh[6+index*30:6+(index+1)*30], 15, 14, ink)
			}
		}
		u.disaster[selection] = frame
	}
	for _, notice := range interfaceNotices {
		raw, _ := hex.DecodeString(notice.code)
		frame := decodeIconSource(rom)
		x := 19
		for at := 0; at < len(raw); {
			if raw[at] < 128 {
				code := int(raw[at])
				if code < 32 || code > 126 {
					return u
				}
				stampInterface(frame, 320, x, 181, u.ascii[6+(code-32)*7:6+(code-31)*7], 5, 7, 32)
				x += 6
				at++
				continue
			}
			if at+2 > len(raw) {
				return u
			}
			code := binary.BigEndian.Uint16(raw[at:])
			index, ok := lookup[code]
			if !ok {
				return u
			}
			stampInterface(frame, 320, x, 177, zh[6+index*30:6+(index+1)*30], 15, 14, 32)
			x += 16
			at += 2
		}
		u.notices[string(footerCrop(frame, footerRects[0]))] = notice.key
	}
	return u
}

func stampInterface(dst []byte, stride, x, y int, glyph []byte, w, h int, ink byte) {
	for dy := 0; dy < h; dy++ {
		for dx := 0; dx < w; dx++ {
			if glyph[dy*((w+7)/8)+dx/8]&(128>>uint(dx%8)) != 0 {
				dst[(y+dy)*stride+x+dx] = ink
			}
		}
	}
}

// Full panel reconstruction admits only original digits, sign, spaces and known rank glyphs.
func (u *interfaceSources) panel(px []byte, population bool) (int, bool) {
	base, slots, bg, ink := u.opinion, opinionSlots, byte(1), byte(11)
	if population {
		base, slots, bg, ink = u.population, populationSlots, 9, 14
	}
	if len(base) != 235*132 {
		return -1, false
	}
	raw := footerCrop(px, image.Rect(18, 37, 253, 169))
	rebuilt := append([]byte(nil), base...)
	for _, s := range slots {
		for dy := 0; dy < 7; dy++ {
			for dx := 0; dx < s[2]*6; dx++ {
				rebuilt[(s[1]+dy)*235+s[0]+dx] = bg
			}
		}
		for col := 0; col < s[2]; col++ {
			x := s[0] + col*6
			found := false
			for _, ch := range " -0123456789" {
				g := u.ascii[6+(int(ch)-32)*7 : 6+(int(ch)-31)*7]
				match := true
				for dy := 0; dy < 7 && match; dy++ {
					for dx := 0; dx < 5; dx++ {
						want := bg
						if g[dy]&(128>>uint(dx)) != 0 {
							want = ink
						}
						if raw[(s[1]+dy)*235+x+dx] != want {
							match = false
							break
						}
					}
				}
				if match {
					stampInterface(rebuilt, 235, x, s[1], g, 5, 7, ink)
					found = true
					break
				}
			}
			if !found {
				return -1, false
			}
		}
	}
	rank := -1
	if population {
		for i, source := range u.ranks {
			match := true
			for y := 0; y < 14; y++ {
				if !bytes.Equal(raw[(108+y)*235+144:(108+y)*235+192], source[y*48:(y+1)*48]) {
					match = false
					break
				}
			}
			if match {
				rank = i
				break
			}
		}
		if rank < 0 {
			return -1, false
		}
		for y := 0; y < 14; y++ {
			copy(rebuilt[(108+y)*235+144:(108+y)*235+192], u.ranks[rank][y*48:(y+1)*48])
		}
	}
	return rank, bytes.Equal(raw, rebuilt)
}

func (u *interfaceLocale) prepareExtras(r *Renderer, blue, wood, red image.Image) error {
	if r.extra == nil || len(r.extra.population) != 31020 || len(r.extra.opinion) != 31020 || len(r.extra.notices) != len(interfaceNotices) {
		return fmt.Errorf("interface-source-resource")
	}
	u.extra = &interfaceExtraLocale{notices: map[string]*image.RGBA{}}
	for selection := range disasterCityKeys {
		patch := image.NewRGBA(image.Rect(0, 0, 944, 528))
		localeScale(patch, patch.Bounds(), wood, 0)
		title := localeNative([4]int{49, 9, 142, 22})
		localeScale(patch, title, red, 8)
		if e := u.ui.DrawText(patch, u.language, "startup.disaster_city", title.Inset(8), 52, 14, color.White); e != nil {
			return e
		}
		for option, key := range disasterCityKeys {
			box := localeNative([4]int{9 + (option/3)*114, 39 + (option%3)*31, 106, 22})
			localeScale(patch, box, red, 8)
			fg := color.Color(color.RGBA{255, 0, 0, 255})
			if option == selection {
				fg = color.White
			}
			if e := u.ui.DrawText(patch, u.language, key, box.Inset(8), 52, 14, fg); e != nil {
				return e
			}
		}
		u.extra.disaster[selection] = patch
	}
	for i, group := range [][]interfaceField{populationFields, opinionFields} {
		patch := image.NewRGBA(image.Rect(0, 0, 940, 528))
		for _, f := range group {
			box := localeNative(f.rect)
			localeScale(patch, box, blue, 0)
			if e := u.ui.DrawText(patch, u.language, f.key, box, 52, 14, color.White); e != nil {
				return e
			}
		}
		if i == 0 {
			u.extra.population = patch
		} else {
			u.extra.opinion = patch
		}
	}
	for i, key := range rankKeys {
		patch := image.NewRGBA(image.Rect(0, 0, 192, 72))
		localeScale(patch, patch.Bounds(), blue, 0)
		if e := u.ui.DrawText(patch, u.language, key, patch.Bounds(), 52, 14, color.RGBA{255, 85, 255, 255}); e != nil {
			return e
		}
		u.extra.ranks[i] = patch
	}
	for selection := range speedKeys {
		patch := image.NewRGBA(image.Rect(0, 0, 660, 164))
		localeScale(patch, patch.Bounds(), blue, 8)
		for option, key := range speedKeys {
			fg := color.Color(color.White)
			if option == selection {
				fg = color.RGBA{255, 85, 85, 255}
			}
			if e := u.ui.DrawText(patch, u.language, key, image.Rect((5+option*40)*4, 40, (39+option*40)*4, 124), 52, 14, fg); e != nil {
				return e
			}
		}
		u.extra.speed[selection] = patch
	}
	if r.footer == nil || r.footer.art == nil {
		return fmt.Errorf("interface-footer-resource")
	}
	for _, notice := range interfaceNotices {
		patch := image.NewRGBA(image.Rect(0, 0, 896, 72))
		draw.Draw(patch, patch.Bounds(), r.footer.art, image.Pt(28, 700), draw.Src)
		if e := u.ui.DrawText(patch, u.language, notice.key, patch.Bounds().Inset(8), 48, 14, color.RGBA{255, 0, 0, 255}); e != nil {
			return e
		}
		u.extra.notices[notice.key] = patch
	}
	return nil
}

func (u *interfaceLocale) paintExtras(r *Renderer, dst *image.RGBA, px []byte, pal [256][3]byte) (int, string) {
	if r.extra == nil || u.extra == nil || paletteDigest(interfaceExtraIndices, pal) != "bb592feaa8a51c36b22b702efa4fbed5a793e43a8029526cd6912d915d8a7919" {
		return 0, ""
	}
	disaster := footerCrop(px, image.Rect(18, 37, 254, 169))
	for selection, source := range r.extra.disaster {
		if len(source) > 0 && bytes.Equal(disaster, source) {
			draw.Draw(dst, image.Rect(72, 148, 1016, 676), u.extra.disaster[selection], image.Point{}, draw.Src)
			return 7, fmt.Sprintf("disaster-city-%d", selection)
		}
	}
	for i, group := range [][]interfaceField{populationFields, opinionFields} {
		rank, matched := r.extra.panel(px, i == 0)
		if !matched {
			continue
		}
		patch, id := u.extra.opinion, "opinion"
		if i == 0 {
			patch, id = u.extra.population, "population"
		}
		for _, f := range group {
			box := localeNative(f.rect)
			draw.Draw(dst, box.Add(image.Pt(72, 148)), patch, box.Min, draw.Over)
		}
		fields := len(group)
		if i == 0 {
			draw.Draw(dst, image.Rect(648, 572, 840, 644), u.extra.ranks[rank], image.Point{}, draw.Src)
			fields++
		}
		return fields, id
	}
	raw := footerCrop(px, image.Rect(54, 87, 219, 128))
	for selection, source := range r.extra.speed {
		if len(source) > 0 && bytes.Equal(raw, source) {
			draw.Draw(dst, image.Rect(216, 348, 876, 512), u.extra.speed[selection], image.Point{}, draw.Src)
			return 4, "speed"
		}
	}
	key := r.extra.notices[string(footerCrop(px, footerRects[0]))]
	if patch := u.extra.notices[key]; patch != nil {
		draw.Draw(dst, image.Rect(28, 700, 924, 772), patch, image.Point{}, draw.Src)
		return 1, key
	}
	return 0, ""
}
