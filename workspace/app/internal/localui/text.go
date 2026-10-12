package localui

import (
	"fmt"
	"image"
	"image/color"
	"strings"
	"unicode"

	"golang.org/x/image/font"
	"golang.org/x/image/font/opentype"
)

// DrawText paints one TSV key inside a bounded, centered field.
func (u *UI) DrawText(dst *image.RGBA, lang, key string, safe image.Rectangle, max, min int, ink color.Color) error {
	if safe.Empty() || !safe.In(dst.Bounds()) {
		return fmt.Errorf("text-safe:%s", key)
	}
	if err := u.Catalog.Require(key); err != nil {
		return err
	}
	return u.textColor(dst, lang, key, safe, max, min, ink)
}

// DrawCompact is for the original 5–7 pixel unit fields at four times scale.
func (u *UI) DrawCompact(dst *image.RGBA, lang, key string, safe image.Rectangle, max, min int, ink color.Color) error {
	if safe.Empty() || !safe.In(dst.Bounds()) {
		return fmt.Errorf("text-safe:%s", key)
	}
	if err := u.Catalog.Require(key); err != nil {
		return err
	}
	return u.drawValuePadding(dst, u.Catalog.Get(lang, key), lang+"/"+key, safe, max, min, ink, 1)
}

// Paragraph keeps the original content and bounds both line width and total height.
func (u *UI) Paragraph(dst *image.RGBA, lang, key string, safe image.Rectangle, max, min int, ink color.Color) error {
	if safe.Empty() || !safe.In(dst.Bounds()) {
		return fmt.Errorf("text-safe:%s", key)
	}
	if err := u.Catalog.Require(key); err != nil {
		return err
	}
	text := u.Catalog.Get(lang, key)
	for size := max; size >= min; size-- {
		face, err := opentype.NewFace(u.font, &opentype.FaceOptions{Size: float64(size), DPI: 72, Hinting: font.HintingNone})
		if err != nil {
			return err
		}
		var lines []string
		remaining := []rune(text)
		valid := true
		for len(remaining) > 0 {
			end, space := 0, -1
			for i := 1; i <= len(remaining); i++ {
				b, _ := font.BoundString(face, string(remaining[:i]))
				if b.Max.X.Ceil()-b.Min.X.Floor() > safe.Dx()-8 {
					break
				}
				end = i
				if unicode.IsSpace(remaining[i-1]) {
					space = i - 1
				}
			}
			if end == 0 {
				valid = false
				break
			}
			if end < len(remaining) && !unicode.Is(unicode.Han, remaining[end-1]) && !unicode.Is(unicode.Hiragana, remaining[end-1]) && !unicode.Is(unicode.Katakana, remaining[end-1]) {
				if space < 1 {
					valid = false
					break
				}
				end = space
			}
			lines = append(lines, strings.TrimSpace(string(remaining[:end])))
			remaining = []rune(strings.TrimLeftFunc(string(remaining[end:]), unicode.IsSpace))
		}
		face.Close()
		lineHeight := (size*135 + 99) / 100
		if !valid || len(lines)*lineHeight > safe.Dy()-8 {
			continue
		}
		for i, line := range lines {
			r := image.Rect(safe.Min.X, safe.Min.Y+4+i*lineHeight, safe.Max.X, safe.Min.Y+4+(i+1)*lineHeight)
			if err := u.drawValue(dst, line, lang+"/"+key, r, size, size, ink); err != nil {
				return err
			}
		}
		return nil
	}
	return fmt.Errorf("paragraph-layout:%s/%s", lang, key)
}
