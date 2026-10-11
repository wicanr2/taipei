package hd

import (
	"bytes"
	"encoding/binary"
	"encoding/json"
	"image"
	"image/draw"
	"os"
	"path/filepath"
)

// spec/023：唯讀重建完整來源；不接觸 DOS、輸入緩衝或存檔。
const fileManifestSHA = "6fc74370c334d77b62f2e0d224a80cb967d158da3e632a79aa1e4017636792b6"
const filePaletteSHA = "4103f1e8410a2ee91de3074579ce3062de27f48c1d2c415f46bbd195c50b56df"

var fileBrowserRect = image.Rect(34, 41, 101, 148)
var fileQuitRect = image.Rect(7, 175, 231, 193)

type fileDialogs struct {
	base, question        []byte
	ascii                 [95][7]byte
	reverse               map[[7]byte]byte
	palette               [256][3]byte
	browser, glyphs, quit *image.RGBA
	reason                string
}

func loadFileDialogs(rom []byte, dir string) *fileDialogs {
	u := &fileDialogs{reason: "file-source-mismatch", reverse: map[[7]byte]byte{}}
	if digest(rom) != romSHA {
		return u
	}
	member := func(i int) []byte {
		off := int(binary.LittleEndian.Uint32(rom[18+16*i:]))
		n := int(binary.LittleEndian.Uint16(rom[22+16*i:]))
		return rom[off : off+n]
	}
	raw := member(3)
	if len(raw) != 4812 || binary.LittleEndian.Uint16(raw) != 67 || binary.LittleEndian.Uint16(raw[2:]) != 107 {
		return u
	}
	var decoded []byte
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
		if len(decoded)+count > 7169 {
			return u
		}
		for j := 0; j < count; j++ {
			decoded = append(decoded, value)
		}
	}
	if len(decoded) != 7169 || digest(decoded) != "697dff15cb595e693f514500531196d2be7f415a2b10e9e99a1182da431657c8" {
		return u
	}
	for y := 4; y < 18; y++ {
		for x := 5; x < 62; x++ {
			decoded[y*67+x] = 31
		}
	}
	for row := 0; row < 7; row++ {
		for y := 26 + 11*row; y < 33+11*row; y++ {
			for x := 10; x < 58; x++ {
				decoded[y*67+x] = 136
			}
		}
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
		u.ascii[code-32] = glyph
		u.reverse[glyph] = byte(code)
	}
	city := decodeIconSource(rom)
	if len(city) != 64000 {
		return u
	}
	cjk := member(57)
	for i, index := range []int{188, 301, 55, 302, 51, 49, 50, 167} {
		footerStamp(city, 19+16*i, 177, cjk[6+index*30:6+index*30+28], 15, 14, 32)
	}
	for i, ch := range "?(Y/N)" {
		a := 6 + (int(ch)-32)*7
		footerStamp(city, 153+6*i, 181, font[a:a+7], 5, 7, 32)
	}
	question := footerCrop(city, fileQuitRect)
	if digest(question) != "84b33e447ebeea82ba9517eda9c987bf8a9bf5cec759892974cb66401caaf701" {
		return u
	}
	u.base, u.question = decoded, question
	u.reason = "file-manifest-mismatch"
	base := filepath.Join(dir, "file-dialogs-v1")
	raw, err := os.ReadFile(filepath.Join(base, "manifest.json"))
	if err != nil || digest(raw) != fileManifestSHA {
		return u
	}
	var manifest struct {
		Schema     int
		FontSHA    string `json:"font_sha256"`
		LicenseSHA string `json:"license_sha256"`
		Images     map[string]string
	}
	if json.Unmarshal(raw, &manifest) != nil || manifest.Schema != 1 || manifest.FontSHA != menuFontSHA || manifest.LicenseSHA != menuLicenseSHA {
		return u
	}
	for _, a := range []struct{ name, sha, reason string }{
		{"NotoSansCJKtc-Regular.otf", menuFontSHA, "file-font-mismatch"},
		{"LICENSE", menuLicenseSHA, "file-license-mismatch"},
	} {
		raw, err = os.ReadFile(filepath.Join(dir, "fonts", a.name))
		if err != nil || digest(raw) != a.sha {
			u.reason = a.reason
			return u
		}
	}
	u.reason = "file-palette-resource-mismatch"
	raw, err = os.ReadFile(filepath.Join(base, "palette.json"))
	var palette [][3]byte
	if err != nil || digest(raw) != filePaletteSHA || json.Unmarshal(raw, &palette) != nil || len(palette) != 256 {
		return u
	}
	copy(u.palette[:], palette)
	u.browser = chromeImage(filepath.Join(base, "browser.png"), manifest.Images["browser.png"], image.Rect(0, 0, 268, 428))
	u.glyphs = chromeImage(filepath.Join(base, "glyphs.png"), manifest.Images["glyphs.png"], image.Rect(0, 0, 1024, 832))
	u.quit = chromeImage(filepath.Join(base, "quit-confirm.png"), manifest.Images["quit-confirm.png"], image.Rect(0, 0, 896, 72))
	u.reason = "scene-fallback"
	return u
}

func (u *fileDialogs) decode(px []byte) ([8]string, [8]byte, bool) {
	var texts [8]string
	var colors [8]byte
	if u == nil || len(px) != 64000 || len(u.base) != 7169 {
		return texts, colors, false
	}
	raw := footerCrop(px, fileBrowserRect)
	rebuilt := append([]byte(nil), u.base...)
	red := 0
	for line := 0; line < 8; line++ {
		y, bg := 8, byte(31)
		if line > 0 {
			y, bg = 26+11*(line-1), 136
		} else {
			colors[line] = 15
		}
		for dy := 0; dy < 7; dy++ {
			for dx := 0; dx < 48; dx++ {
				v := raw[(y+dy)*67+10+dx]
				if v == bg {
					continue
				}
				if (line == 0 && v != 15) || (line > 0 && v != 31 && v != 32) || (colors[line] != 0 && colors[line] != v) {
					return texts, colors, false
				}
				colors[line] = v
			}
		}
		if line > 0 && colors[line] == 32 {
			red++
		}
		for column := 0; column < 8; column++ {
			x := 10 + 6*column
			var bits [7]byte
			for dy := 0; dy < 7; dy++ {
				for dx := 0; dx < 5; dx++ {
					if raw[(y+dy)*67+x+dx] == colors[line] {
						bits[dy] |= 1 << uint(4-dx)
					}
				}
			}
			ch, ok := u.reverse[bits]
			if !ok {
				return texts, colors, false
			}
			texts[line] += string(ch)
			for dy, row := range u.ascii[int(ch)-32] {
				for dx := 0; dx < 5; dx++ {
					if row&(1<<uint(4-dx)) != 0 {
						rebuilt[(y+dy)*67+x+dx] = colors[line]
					}
				}
			}
		}
	}
	return texts, colors, red <= 1 && bytes.Equal(raw, rebuilt)
}

func (u *fileDialogs) paint(dst *image.RGBA, px []byte, pal [256][3]byte) (string, [8]string, [8]byte, string, bool) {
	var empty [8]string
	var noColors [8]byte
	if u == nil || len(px) != 64000 || len(u.question) != 4032 {
		return "", empty, noColors, "scene-fallback", false
	}
	text, colors, matched := u.decode(px)
	name, rect := "file-browser", fileBrowserRect
	if !matched {
		if !bytes.Equal(footerCrop(px, fileQuitRect), u.question) {
			return "", empty, noColors, "scene-fallback", false
		}
		name, rect = "quit-confirm", fileQuitRect
		text, colors = empty, noColors
	}
	if u.reason != "scene-fallback" {
		return "", empty, noColors, u.reason, true
	}
	var used [256]bool
	for _, index := range footerCrop(px, rect) {
		used[index] = true
	}
	for index, present := range used {
		if present && pal[index] != u.palette[index] {
			return "", empty, noColors, "file-palette-mismatch", true
		}
	}
	if name == "file-browser" {
		if u.browser == nil {
			return "", empty, noColors, "file-browser-art-mismatch", true
		}
		if u.glyphs == nil {
			return "", empty, noColors, "file-glyph-art-mismatch", true
		}
		out := image.Rect(rect.Min.X*4, rect.Min.Y*4, rect.Max.X*4, rect.Max.Y*4)
		draw.Draw(dst, out, u.browser, image.Point{}, draw.Src)
		for line, value := range text {
			y := 8
			if line > 0 {
				y = 26 + 11*(line-1)
			}
			for column, ch := range value {
				if ch == ' ' {
					continue
				}
				index := int(ch) - 32
				if colors[line] == 32 {
					index += 95
				}
				xx, yy := (44+6*column)*4, (41+y)*4
				draw.Draw(dst, image.Rect(xx, yy, xx+24, yy+28), u.glyphs, image.Pt(index%16*64, index/16*64), draw.Over)
			}
		}
	} else {
		if u.quit == nil {
			return "", empty, noColors, "file-quit-art-mismatch", true
		}
		draw.Draw(dst, image.Rect(rect.Min.X*4, rect.Min.Y*4, rect.Max.X*4, rect.Max.Y*4), u.quit, image.Point{}, draw.Src)
	}
	return name, text, colors, "matched-file-dialog", true
}
