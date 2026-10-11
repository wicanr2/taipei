package hd

import (
	"bytes"
	"encoding/binary"
	"encoding/json"
	"image"
	"image/draw"
	"os"
	"path/filepath"
	"strings"
)

// 025：完整來源重建與呈現只讀畫布，不接觸原版數值或輸入。
const budgetManifestSHA = "f6a3052430ad3cc1cda5c737fb21ce6c73c13237e191e29cf0c92684553b9933"
const budgetPaletteSHA = "92e63b93ecf043e77d45db64975aecae89116937314f3985972e864cb7f1f37b"
const budgetCharacters = " -0123456789"

var budgetRect = image.Rect(18, 37, 253, 169)
var budgetSlots = [11]struct{ x, y, columns int }{
	{93, 29, 3}, {93, 49, 3}, {93, 68, 3}, {93, 85, 3}, {93, 103, 3},
	{168, 49, 8}, {168, 68, 8}, {168, 85, 8}, {168, 103, 8},
	{51, 120, 8}, {168, 120, 8},
}

type budgetPanel struct {
	base, hint    []byte
	ascii         [95][7]byte
	reverse       map[[7]byte]byte
	palette       [256][3]byte
	panel, glyphs *image.RGBA
	reason        string
}

func loadBudgetPanel(rom []byte, dir string) *budgetPanel {
	u := &budgetPanel{reason: "budget-source-mismatch", reverse: map[[7]byte]byte{}}
	if digest(rom) != romSHA {
		return u
	}
	member := func(i int) []byte {
		off := int(binary.LittleEndian.Uint32(rom[18+16*i:]))
		n := int(binary.LittleEndian.Uint16(rom[22+16*i:]))
		return rom[off : off+n]
	}
	raw := member(2)
	if len(raw) != 10193 || binary.LittleEndian.Uint16(raw) != 235 || binary.LittleEndian.Uint16(raw[2:]) != 132 {
		return u
	}
	var base []byte
	for at := 4; at < len(raw); {
		value, count := raw[at], 1
		at++
		if value == 0 {
			if at+2 > len(raw) {
				return u
			}
			value, count = raw[at], int(raw[at+1])
			at += 2
		}
		if len(base)+count > 31020 {
			return u
		}
		for j := 0; j < count; j++ {
			base = append(base, value)
		}
	}
	if len(base) != 31020 || digest(base) != "db92d35996a6c8fc112d129ab0a92d1018384495cd38b31d637df468b52c7967" {
		return u
	}
	for _, s := range budgetSlots {
		for y := s.y; y < s.y+7; y++ {
			for x := s.x; x < s.x+s.columns*6; x++ {
				base[y*235+x] = 3
			}
		}
	}
	if digest(base) != "28ed84d785657fa26eb5118196c147aa29b1eb97c3b1184829e1ebea6fb1d654" {
		return u
	}
	font := member(56)
	for code := 32; code <= 126; code++ {
		var glyph [7]byte
		for y := 0; y < 7; y++ {
			glyph[y] = font[6+(code-32)*7+y] >> 3
		}
		if _, exists := u.reverse[glyph]; exists {
			return u
		}
		u.ascii[code-32], u.reverse[glyph] = glyph, byte(code)
	}
	u.base = base
	// 此區域沒有動態欄位，與 012 標題不重疊。只用來整幀回退。
	for y := 99; y < 119; y++ {
		u.hint = append(u.hint, base[y*235:y*235+91]...)
	}
	u.reason = "budget-manifest-mismatch"
	root := filepath.Join(dir, "budget-v1")
	raw, err := os.ReadFile(filepath.Join(root, "manifest.json"))
	if err != nil || digest(raw) != budgetManifestSHA {
		return u
	}
	var manifest struct {
		Schema     int
		FontSHA    string `json:"font_sha256"`
		LicenseSHA string `json:"license_sha256"`
		Characters string `json:"atlas_characters"`
		Images     map[string]string
	}
	if json.Unmarshal(raw, &manifest) != nil || manifest.Schema != 1 || manifest.FontSHA != menuFontSHA || manifest.LicenseSHA != menuLicenseSHA || manifest.Characters != budgetCharacters {
		return u
	}
	for _, asset := range []struct{ name, sha, reason string }{
		{"NotoSansCJKtc-Regular.otf", menuFontSHA, "budget-font-mismatch"},
		{"LICENSE", menuLicenseSHA, "budget-license-mismatch"},
	} {
		raw, err = os.ReadFile(filepath.Join(dir, "fonts", asset.name))
		if err != nil || digest(raw) != asset.sha {
			u.reason = asset.reason
			return u
		}
	}
	u.reason = "budget-palette-resource-mismatch"
	raw, err = os.ReadFile(filepath.Join(root, "palette.json"))
	var pal [][3]byte
	if err != nil || digest(raw) != budgetPaletteSHA || json.Unmarshal(raw, &pal) != nil || len(pal) != 256 {
		return u
	}
	copy(u.palette[:], pal)
	u.panel = chromeImage(filepath.Join(root, "panel.png"), manifest.Images["panel.png"], image.Rect(0, 0, 940, 528))
	u.glyphs = chromeImage(filepath.Join(root, "glyphs.png"), manifest.Images["glyphs.png"], image.Rect(0, 0, 288, 56))
	u.reason = "scene-fallback"
	return u
}

func (u *budgetPanel) decode(px []byte) ([11]string, [11]byte, int, bool) {
	var texts [11]string
	var colors [11]byte
	if u == nil || len(px) != 64000 || len(u.base) != 31020 {
		return texts, colors, -1, false
	}
	raw := footerCrop(px, budgetRect)
	rebuilt := append([]byte(nil), u.base...)
	selection := -1
	for i, slot := range budgetSlots {
		ink := byte(255)
		for y := slot.y; y < slot.y+7; y++ {
			for x := slot.x; x < slot.x+slot.columns*6; x++ {
				v := raw[y*235+x]
				if v == 3 {
					continue
				}
				if (v != 0 && v != 12) || (ink != 255 && ink != v) {
					return texts, colors, -1, false
				}
				ink = v
			}
		}
		if ink == 255 || (i >= 5 && ink != 0) {
			return texts, colors, -1, false
		}
		colors[i] = ink
		if i < 5 && ink == 12 {
			if selection != -1 {
				return texts, colors, -1, false
			}
			selection = i
		}
		for col := 0; col < slot.columns; col++ {
			x := slot.x + 6*col
			var bits [7]byte
			for dy := 0; dy < 7; dy++ {
				for dx := 0; dx < 5; dx++ {
					if raw[(slot.y+dy)*235+x+dx] == ink {
						bits[dy] |= 1 << uint(4-dx)
					}
				}
			}
			ch, ok := u.reverse[bits]
			if !ok {
				return texts, colors, -1, false
			}
			texts[i] += string(ch)
			for dy, row := range u.ascii[int(ch)-32] {
				for dx := 0; dx < 5; dx++ {
					if row&(1<<uint(4-dx)) != 0 {
						rebuilt[(slot.y+dy)*235+x+dx] = ink
					}
				}
			}
		}
		number := strings.TrimLeft(texts[i], " ")
		if strings.HasPrefix(number, "-") {
			number = number[1:]
		}
		if number == "" {
			return texts, colors, -1, false
		}
		for _, ch := range number {
			if ch < '0' || ch > '9' {
				return texts, colors, -1, false
			}
		}
	}
	return texts, colors, selection, selection >= 0 && bytes.Equal(raw, rebuilt)
}

func (u *budgetPanel) paint(dst *image.RGBA, px []byte, pal [256][3]byte) (bool, [11]string, [11]byte, int, string, bool) {
	var empty [11]string
	var noColors [11]byte
	texts, colors, selection, matched := u.decode(px)
	if !matched {
		// 兩個不重疊的精確來源只作回退提示，不以部分來源繪製 HD。
		if len(px) == 64000 && (digest(footerCrop(px, image.Rect(18, 38, 117, 60))) == budgetSHA ||
			(u != nil && len(u.hint) == 1820 && bytes.Equal(footerCrop(px, image.Rect(18, 136, 109, 156)), u.hint))) {
			return false, empty, noColors, -1, "budget-source-mismatch", true
		}
		return false, empty, noColors, -1, "scene-fallback", false
	}
	if u.reason != "scene-fallback" {
		return false, empty, noColors, -1, u.reason, true
	}
	var used [256]bool
	for _, index := range footerCrop(px, budgetRect) {
		used[index] = true
	}
	for index, present := range used {
		if present && pal[index] != u.palette[index] {
			return false, empty, noColors, -1, "budget-palette-mismatch", true
		}
	}
	if u.panel == nil || u.glyphs == nil {
		return false, empty, noColors, -1, "budget-art-mismatch", true
	}
	draw.Draw(dst, image.Rect(72, 148, 1012, 676), u.panel, image.Point{}, draw.Src)
	for i, value := range texts {
		slot := budgetSlots[i]
		for col, ch := range value {
			index := strings.IndexByte(budgetCharacters, byte(ch))
			row := 0
			if colors[i] == 12 {
				row = 28
			}
			x, y := (18+slot.x+col*6)*4, (37+slot.y)*4
			draw.Draw(dst, image.Rect(x, y, x+24, y+28), u.glyphs, image.Pt(index*24, row), draw.Over)
		}
	}
	return true, texts, colors, selection, "matched-budget", true
}
