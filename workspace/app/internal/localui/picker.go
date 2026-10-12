// Package localui draws frontend controls. It has no DOS or game-state access.
package localui

import (
	"crypto/sha256"
	"fmt"
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

type UI struct {
	Catalog *i18n.Catalog
	font    *sfnt.Font
}

func New(dir string, c *i18n.Catalog) (*UI, error) {
	if err := c.Require("locale.title", "locale.hint", "locale.dismiss", "locale.confirm", "locale.error.settings", "locale.error.catalog", "window.title"); err != nil {
		return nil, err
	}
	for _, lang := range i18n.Languages {
		if err := c.Require("locale.name." + lang); err != nil {
			return nil, err
		}
	}
	raw, err := os.ReadFile(filepath.Join(dir, "NotoSansCJKtc-Regular.otf"))
	if err != nil {
		return nil, err
	}
	if fmt.Sprintf("%x", sha256.Sum256(raw)) != "dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4" {
		return nil, fmt.Errorf("font-mismatch")
	}
	license, err := os.ReadFile(filepath.Join(dir, "LICENSE"))
	if err != nil {
		return nil, err
	}
	if fmt.Sprintf("%x", sha256.Sum256(license)) != "6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2" {
		return nil, fmt.Errorf("font-license-mismatch")
	}
	f, err := opentype.Parse(raw)
	if err != nil {
		return nil, err
	}
	for _, text := range c.Texts() {
		for _, r := range text {
			idx, err := f.GlyphIndex(&sfnt.Buffer{}, r)
			if err != nil || idx == 0 {
				return nil, fmt.Errorf("font-glyph:U+%04X", r)
			}
		}
	}
	u := &UI{Catalog: c, font: f}
	// Validate every language and selection before handling player input.
	for _, lang := range i18n.Languages {
		for i := range i18n.Languages {
			if _, err := u.Picker(lang, i, ""); err != nil {
				return nil, err
			}
		}
	}
	return u, nil
}

func ChoiceRect(i int) image.Rectangle { return image.Rect(372, 184+i*82, 908, 254+i*82) }

func (u *UI) text(dst *image.RGBA, lang, key string, rect image.Rectangle, max, min int) error {
	text := u.Catalog.Get(lang, key)
	for size := max; size >= min; size-- {
		face, err := opentype.NewFace(u.font, &opentype.FaceOptions{Size: float64(size), DPI: 72, Hinting: font.HintingNone})
		if err != nil {
			return err
		}
		bounds, _ := font.BoundString(face, text)
		w, h := bounds.Max.X.Ceil()-bounds.Min.X.Floor(), bounds.Max.Y.Ceil()-bounds.Min.Y.Floor()
		if w > rect.Dx()-8 || h > rect.Dy()-8 {
			face.Close()
			continue
		}
		d := font.Drawer{Dst: dst, Src: image.White, Face: face, Dot: fixed.P(rect.Min.X+(rect.Dx()-w)/2-bounds.Min.X.Floor(), rect.Min.Y+(rect.Dy()-h)/2-bounds.Min.Y.Floor())}
		d.DrawString(text)
		return face.Close()
	}
	return fmt.Errorf("text-layout:%s/%s", lang, key)
}

func (u *UI) Picker(lang string, selection int, warning string) (*image.RGBA, error) {
	if i18n.Index(lang) < 0 || selection < 0 || selection >= len(i18n.Languages) {
		return nil, fmt.Errorf("picker-state")
	}
	dst := image.NewRGBA(image.Rect(0, 0, 1280, 800))
	draw.Draw(dst, image.Rect(320, 90, 960, 718), image.NewUniform(color.RGBA{45, 51, 58, 255}), image.Point{}, draw.Src)
	if err := u.text(dst, lang, "locale.title", image.Rect(360, 104, 920, 164), 44, 24); err != nil {
		return nil, err
	}
	for i, name := range i18n.Languages {
		r := ChoiceRect(i)
		bg := color.RGBA{75, 82, 88, 255}
		if i == selection {
			bg = color.RGBA{83, 109, 119, 255}
		}
		draw.Draw(dst, r, image.NewUniform(bg), image.Point{}, draw.Src)
		if err := u.text(dst, lang, "locale.name."+name, r, 36, 24); err != nil {
			return nil, err
		}
	}
	if err := u.text(dst, lang, "locale.confirm", image.Rect(340, 600, 940, 632), 23, 16); err != nil {
		return nil, err
	}
	if err := u.text(dst, lang, "locale.hint", image.Rect(340, 634, 940, 666), 23, 16); err != nil {
		return nil, err
	}
	key := "locale.dismiss"
	if warning != "" {
		key = warning
	}
	if err := u.text(dst, lang, key, image.Rect(340, 670, 940, 706), 23, 16); err != nil {
		return nil, err
	}
	return dst, nil
}
