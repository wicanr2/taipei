package main

import (
	"image"
	"image/color"
	"image/draw"
	"path/filepath"
)

// 操作原型而非產品 Help。先展示 F1 衝突的兩個選擇，內容只取 TSV。
func (p *painter) help(src image.Image, lang, variant, out string) map[string]string {
	dst := clone(src)
	panel := image.Rect(40, 40, 1240, 760)
	draw.Draw(dst, panel, image.NewUniform(color.RGBA{45, 51, 58, 255}), image.Point{}, draw.Src)
	p.text(dst, "help.title", lang, image.Rect(80, 48, 1200, 112), 44, 24, color.White)
	menu, open := "help.key.menus.original", "help.key.open.shift"
	if variant == "f1" {
		menu, open = "help.key.menus.remapped", "help.key.open.f1"
	}
	rows := [][2]string{
		{open, "help.action.open"}, {menu, "help.action.menus"},
		{"help.key.focus", "help.action.focus"}, {"help.key.arrows", "help.action.arrows"},
		{"help.key.space", "help.action.space"}, {"help.key.select", "help.action.select"},
		{"help.key.language", "help.action.language"}, {"help.key.theme", "help.action.theme"},
	}
	for i, row := range rows {
		y := 124 + i*68
		if i%2 == 0 {
			draw.Draw(dst, image.Rect(64, y, 1216, y+64), image.NewUniform(color.RGBA{58, 65, 72, 255}), image.Point{}, draw.Src)
		}
		p.text(dst, row[0], lang, image.Rect(72, y, 328, y+64), 27, 18, color.RGBA{238, 213, 139, 255})
		p.text(dst, row[1], lang, image.Rect(344, y, 1208, y+64), 27, 18, color.White)
	}
	p.text(dst, "locale.dismiss", lang, image.Rect(80, 688, 1200, 736), 26, 18, color.White)
	name := "help-" + variant + "-" + lang + ".png"
	return map[string]string{name: save(filepath.Join(out, name), dst)}
}
