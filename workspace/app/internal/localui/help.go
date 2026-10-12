package localui

import (
	"fmt"
	"image"
	"image/color"
	"image/draw"

	"github.com/wicanr2/taipei/preview/internal/i18n"
)

var helpRows = [][2]string{
	{"help.key.open.shift", "help.action.open"},
	{"help.key.menus.original", "help.action.menus"},
	{"help.key.focus", "help.action.focus"},
	{"help.key.arrows", "help.action.arrows"},
	{"help.key.space", "help.action.space"},
	{"help.key.select", "help.action.select"},
	{"help.key.language", "help.action.language"},
	{"help.key.theme", "help.action.theme"},
}

func helpKeys() []string {
	keys := []string{"help.title", "locale.dismiss"}
	for _, row := range helpRows {
		keys = append(keys, row[:]...)
	}
	return keys
}

// Help follows the approved 031 prototype. Pixels outside the panel are clear.
func (u *UI) Help(lang string) (*image.RGBA, error) {
	if i18n.Index(lang) < 0 {
		return nil, fmt.Errorf("help-language")
	}
	dst := image.NewRGBA(image.Rect(0, 0, 1280, 800))
	draw.Draw(dst, image.Rect(40, 40, 1240, 760), image.NewUniform(color.RGBA{45, 51, 58, 255}), image.Point{}, draw.Src)
	if err := u.text(dst, lang, "help.title", image.Rect(80, 48, 1200, 112), 44, 24); err != nil {
		return nil, err
	}
	for i, row := range helpRows {
		y := 124 + i*68
		if i%2 == 0 {
			draw.Draw(dst, image.Rect(64, y, 1216, y+64), image.NewUniform(color.RGBA{58, 65, 72, 255}), image.Point{}, draw.Src)
		}
		if err := u.textColor(dst, lang, row[0], image.Rect(72, y, 328, y+64), 27, 18, color.RGBA{238, 213, 139, 255}); err != nil {
			return nil, err
		}
		if err := u.text(dst, lang, row[1], image.Rect(344, y, 1208, y+64), 27, 18); err != nil {
			return nil, err
		}
	}
	if err := u.text(dst, lang, "locale.dismiss", image.Rect(80, 688, 1200, 736), 26, 18); err != nil {
		return nil, err
	}
	return dst, nil
}
