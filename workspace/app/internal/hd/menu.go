package hd

import (
	"image"
	"image/color"
	"image/draw"
	"os"
	"path/filepath"

	"github.com/wicanr2/taipei/preview/internal/i18n"

	"golang.org/x/image/font"
	"golang.org/x/image/font/opentype"
	"golang.org/x/image/font/sfnt"
	"golang.org/x/image/math/fixed"
)

const menuFontSHA = "dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4"
const menuLicenseSHA = "6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2"
const menuPaletteSHA = "1acb802a98b9fb298f4d68b1f4e5a74b0d3bfca88cba6d347795dbafbab63a1e"

var menuKeys = [...]string{"menu.exit", "menu.file", "menu.mayor", "menu.charts", "menu.disasters", "menu.environment"}
var menuLabels = func() (labels [6]string) {
	c := i18n.Bundled()
	for i, key := range menuKeys {
		labels[i] = c.Get(i18n.Default, key)
	}
	return
}()

type menuFont struct {
	labels [6]*image.RGBA
	reason string
}

func menuRect(i int) image.Rectangle {
	return image.Rect(28+i*176, 40, 164+i*176, 108)
}

// 只建置已展示的六個標題；文字來源與完整呈現條件見 spec/013。
func loadMenuFont(dir string) *menuFont {
	return loadMenuFontCatalog(dir, i18n.Bundled(), i18n.Default)
}

func loadMenuFontCatalog(dir string, catalog *i18n.Catalog, language string) *menuFont {
	m := &menuFont{reason: "font-unavailable"}
	if i18n.Index(language) < 0 || catalog.Require(menuKeys[:]...) != nil {
		m.reason = "font-catalog-mismatch"
		return m
	}
	raw, err := os.ReadFile(filepath.Join(dir, "NotoSansCJKtc-Regular.otf"))
	if err != nil {
		return m
	}
	if digest(raw) != menuFontSHA {
		m.reason = "font-mismatch"
		return m
	}
	license, err := os.ReadFile(filepath.Join(dir, "LICENSE"))
	if err != nil || digest(license) != menuLicenseSHA {
		m.reason = "font-license-mismatch"
		return m
	}
	parsed, err := opentype.Parse(raw)
	if err != nil {
		m.reason = "font-format"
		return m
	}
	for i, key := range menuKeys {
		text := catalog.Get(language, key)
		for _, ch := range text {
			glyph, err := parsed.GlyphIndex(&sfnt.Buffer{}, ch)
			if err != nil || glyph == 0 {
				m.reason = "font-missing-glyph"
				return m
			}
		}
		im := image.NewRGBA(image.Rect(0, 0, 136, 68))
		draw.Draw(im, im.Bounds(), image.NewUniform(color.RGBA{170, 170, 170, 255}), image.Point{}, draw.Src)
		matched := false
		for size := 56; size >= 16; size-- {
			face, err := opentype.NewFace(parsed, &opentype.FaceOptions{Size: float64(size), DPI: 72, Hinting: font.HintingNone})
			if err != nil {
				m.reason = "font-face"
				return m
			}
			bounds, _ := font.BoundString(face, text)
			w, h := bounds.Max.X.Ceil()-bounds.Min.X.Floor(), bounds.Max.Y.Ceil()-bounds.Min.Y.Floor()
			dot := fixed.P((136-w)/2-bounds.Min.X.Floor(), (68-h)/2-bounds.Min.Y.Floor())
			if language == i18n.Default {
				dot = fixed.P(12, 54)
			}
			placed := bounds.Add(dot)
			ink := image.Rect(placed.Min.X.Floor(), placed.Min.Y.Floor(), placed.Max.X.Ceil(), placed.Max.Y.Ceil())
			if !ink.In(im.Bounds()) || (language != i18n.Default && (w > 128 || h > 60)) {
				face.Close()
				continue
			}
			d := font.Drawer{Dst: im, Src: image.White, Face: face, Dot: dot}
			d.DrawString(text)
			face.Close()
			matched = true
			break
		}
		if !matched {
			m.reason = "font-layout-mismatch"
			return m
		}
		m.labels[i] = im
	}
	m.reason = "matched-menu"
	return m
}

// SetLanguage only replaces cached presentation labels, never DOS state.
func (r *Renderer) SetLanguage(catalog *i18n.Catalog, language string) string {
	r.menu = loadMenuFontCatalog(r.fontDir, catalog, language)
	r.locale = loadInterfaceLocale(r, catalog, language)
	if r.locale.reason != "" {
		return r.locale.reason
	}
	r.prepareMapZones()
	return r.menu.reason
}

func (m *menuFont) paint(frame *image.RGBA, pal [256][3]uint8) (int, string) {
	if m == nil {
		return 0, "font-unavailable"
	}
	if m.reason != "matched-menu" {
		return 0, m.reason
	}
	var colors []byte
	for _, i := range []byte{15, 21, 27} {
		colors = append(colors, pal[i][:]...)
	}
	if digest(colors) != menuPaletteSHA {
		return 0, "font-palette-mismatch"
	}
	for i, im := range m.labels {
		draw.Draw(frame, menuRect(i), im, image.Point{}, draw.Src)
	}
	return len(m.labels), "matched-menu"
}
