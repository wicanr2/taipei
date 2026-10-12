package hd

import (
	"bytes"
	"encoding/json"
	"fmt"
	"image"
	"image/color"
	"image/draw"
	"image/png"
	"os"
	"path/filepath"

	"github.com/wicanr2/taipei/preview/internal/i18n"
	"github.com/wicanr2/taipei/preview/internal/localui"
	xdraw "golang.org/x/image/draw"
)

// 032: IDs and option indices are semantic; only their TSV values are displayed.
var interfaceOptions = map[string][]string{
	"main":       {"startup.new_game", "startup.disaster_city", "startup.load"},
	"city":       {"city.greater_taipei", "city.taipei", "city.taichung", "city.chiayi", "city.tainan", "city.kaohsiung", "city.hualien"},
	"difficulty": {"difficulty.casual", "difficulty.expert", "difficulty.challenge"},
	"tool-02":    {"tool.road", "tool.metro"},
	"tool-05":    {"tool.police", "tool.fire_station"},
	"tool-09":    {"tool.waste", "tool.sewage"},
	"tool-10":    {"tool.sun_yat_sen", "tool.chiang_kai_shek", "tool.palace_museum", "tool.february_28", "tool.art_museum", "tool.amusement_park", "tool.stadium", "tool.confucius_temple", "tool.zoo", "tool.baseball_dome"},
	"tool-11":    {"tool.thermal_plant", "tool.nuclear_plant"},
	"city-f1":    {"file.return_dos"},
	"city-f2":    {"file.save", "file.load", "file.disaster_city", "file.restart"},
	"city-f3":    {"mayor.budget", "mayor.population", "mayor.opinion"},
	"city-f4":    {"chart.power", "chart.traffic", "chart.population", "chart.crime", "chart.land_value", "chart.pollution"},
	"city-f5":    {"disaster.earthquake", "disaster.fire", "disaster.power_plant", "disaster.typhoon", "disaster.air_crash", "disaster.shipwreck", "disaster.protest", "disaster.blackout", "disaster.enable_all", "disaster.disable_all"},
	"city-f6":    {"environment.message_speed", "environment.game_speed", "environment.difficulty", "environment.speaker", "environment.music"},
}

type localeScene struct {
	ID            string
	Native        [4]int
	Background    string
	Border        int `json:"background_border"`
	Separator     int
	SelectedColor [3]byte `json:"selected_color"`
	OtherColor    [3]byte `json:"other_color"`
	Buttons       []struct {
		Rect [4]int
		Art  string
	}
	Cells []struct {
		X, Y, Option, Button int
		Fit                  []int `json:"fit_ink"`
	}
}

type interfaceLocale struct {
	extra                               *interfaceExtraLocale
	ui                                  *localui.UI
	language, reason                    string
	panels                              map[string]*image.RGBA
	dialog, budget, quit, ending, chart *image.RGBA
	footer                              [5]*image.RGBA
}

func interfaceKeys() []string {
	keys := []string{"startup.title", "difficulty.title", "help.goal", "help.medal", "help.performance", "budget.title", "budget.back", "budget.select", "budget.adjust", "budget.tax", "budget.public_safety", "budget.traffic", "budget.facilities", "budget.power", "budget.tax_revenue", "budget.net_amount", "footer.per_unit", "footer.year", "footer.month", "unit.ten_thousand", "unit.ten_thousand.compact", "file.confirm_exit", "ending.achievement", "chart.minimum", "chart.maximum", "control.escape", "control.up_down", "control.left_right", "unit.percent"}
	for _, options := range interfaceOptions {
		keys = append(keys, options...)
	}
	return append(keys, extraKeys()...)
}

func ValidateInterfaceCatalog(c *i18n.Catalog) error { return c.Require(interfaceKeys()...) }

func localeNative(r [4]int) image.Rectangle {
	return image.Rect(r[0]*4, r[1]*4, (r[0]+r[2])*4, (r[1]+r[3])*4)
}
func localeClone(src image.Image) *image.RGBA {
	dst := image.NewRGBA(src.Bounds())
	draw.Draw(dst, dst.Bounds(), src, src.Bounds().Min, draw.Src)
	return dst
}
func localeScale(dst *image.RGBA, target image.Rectangle, src image.Image, b int) {
	if b == 0 {
		xdraw.CatmullRom.Scale(dst, target, src, src.Bounds(), draw.Src, nil)
		return
	}
	s := src.Bounds()
	xs, ys := []int{s.Min.X, s.Min.X + b, s.Max.X - b, s.Max.X}, []int{s.Min.Y, s.Min.Y + b, s.Max.Y - b, s.Max.Y}
	xd, yd := []int{target.Min.X, target.Min.X + b, target.Max.X - b, target.Max.X}, []int{target.Min.Y, target.Min.Y + b, target.Max.Y - b, target.Max.Y}
	for y := 0; y < 3; y++ {
		for x := 0; x < 3; x++ {
			xdraw.CatmullRom.Scale(dst, image.Rect(xd[x], yd[y], xd[x+1], yd[y+1]), src, image.Rect(xs[x], ys[y], xs[x+1], ys[y+1]), draw.Src, nil)
		}
	}
}

func loadInterfaceLocale(r *Renderer, c *i18n.Catalog, lang string) *interfaceLocale {
	u := &interfaceLocale{language: lang, panels: map[string]*image.RGBA{}}
	if err := u.prepare(r, c); err != nil {
		u.reason = err.Error()
	}
	return u
}

func (u *interfaceLocale) prepare(r *Renderer, c *i18n.Catalog) error {
	if i18n.Index(u.language) < 0 {
		return fmt.Errorf("interface-language")
	}
	if err := ValidateInterfaceCatalog(c); err != nil {
		return err
	}
	var err error
	u.ui, err = localui.New(r.fontDir, c)
	if err != nil {
		return err
	}
	dir := filepath.Dir(r.fontDir)
	readImage := func(path, sha string) (image.Image, error) {
		raw, e := os.ReadFile(filepath.Join(dir, path))
		if e != nil || digest(raw) != sha {
			return nil, fmt.Errorf("interface-art:%s", path)
		}
		im, e := png.Decode(bytes.NewReader(raw))
		return im, e
	}
	for _, input := range []struct {
		path, sha string
		set       *panelSet
	}{
		{"startup-menu-layout-v1.json", "55d977d8da010783bb5a1e0836e6597458dba33a069f83163f0693ff6de264ee", r.panels},
		{"tool-menu-layout-v1.json", "8da4bcab9cdff0e2cb59a208814c7f4589458ad6d9148f6cf6c218cce46fa4ee", r.toolPanels},
		{"city-menu-layout-v1.json", "91dc1347725734638035f0488233945d46db59a173fce8dec3dcc8a5c62f6c64", r.cityPanels},
	} {
		raw, e := os.ReadFile(filepath.Join(dir, input.path))
		if e != nil || digest(raw) != input.sha {
			return fmt.Errorf("interface-layout:%s", input.path)
		}
		var layout struct {
			Schema int
			Arts   map[string]string `json:"art_sha256"`
			Scenes []localeScene
		}
		if json.Unmarshal(raw, &layout) != nil || layout.Schema != 1 {
			return fmt.Errorf("interface-layout-shape")
		}
		arts := map[string]image.Image{}
		for path, sha := range layout.Arts {
			if filepath.Base(path) != path {
				return fmt.Errorf("interface-art-path")
			}
			im, e := readImage(path, sha)
			if e != nil {
				return e
			}
			arts[path] = im
		}
		for _, s := range layout.Scenes {
			keys, ok := interfaceOptions[s.ID]
			if !ok {
				return fmt.Errorf("interface-scene:%s", s.ID)
			}
			bg := arts[s.Background]
			if bg == nil {
				return fmt.Errorf("interface-background:%s", s.ID)
			}
			blank := image.NewRGBA(image.Rect(0, 0, s.Native[2]*4, s.Native[3]*4))
			localeScale(blank, blank.Bounds(), bg, s.Border)
			if s.Separator > 0 {
				b := bg.Bounds()
				xdraw.CatmullRom.Scale(blank, image.Rect(16, s.Separator*4, blank.Bounds().Dx()-16, s.Separator*4+16), bg, image.Rect(16, b.Max.Y-16, b.Max.X-16, b.Max.Y), draw.Src, nil)
			}
			for _, b := range s.Buttons {
				if arts[b.Art] == nil {
					return fmt.Errorf("interface-button")
				}
				localeScale(blank, localeNative(b.Rect), arts[b.Art], 8)
			}
			for selection := range keys {
				im := localeClone(blank)
				for option, key := range keys {
					var safe image.Rectangle
					rowY := im.Bounds().Dy()
					for _, cell := range s.Cells {
						if cell.Option != option {
							continue
						}
						if len(s.Buttons) > 0 {
							index := cell.Button
							if s.ID == "tool-10" {
								index = option
							}
							if index < 0 || index >= len(s.Buttons) {
								return fmt.Errorf("interface-button-index")
							}
							safe = localeNative(s.Buttons[index].Rect).Inset(8)
							break
						}
						if cell.Y*4 < rowY {
							rowY = cell.Y * 4
						}
					}
					if len(s.Buttons) == 0 {
						safe = image.Rect(8, rowY, im.Bounds().Dx()-8, rowY+60)
					}
					fg := color.RGBA{255, 255, 255, 255}
					if option == selection {
						fg = color.RGBA{255, 0, 0, 255}
					}
					if s.ID == "main" || s.ID == "city" || s.ID == "difficulty" {
						a := s.OtherColor
						if option == selection {
							a = s.SelectedColor
						}
						fg = color.RGBA{a[0], a[1], a[2], 255}
					}
					if err := u.ui.DrawText(im, u.language, key, safe, 56, 14, fg); err != nil {
						return err
					}
				}
				if s.ID == "difficulty" {
					if err := u.ui.DrawText(im, u.language, "difficulty.title", localeNative(s.Buttons[0].Rect).Inset(8), 56, 14, color.White); err != nil {
						return err
					}
				}
				if s.ID == "main" {
					var safe image.Rectangle
					for _, cell := range s.Cells {
						if len(cell.Fit) == 4 {
							safe = safe.Union(localeNative([4]int{cell.Fit[0], cell.Fit[1], cell.Fit[2], cell.Fit[3]}))
						}
					}
					if err := u.ui.DrawText(im, u.language, "startup.title", safe, 128, 24, color.RGBA{255, 255, 85, 255}); err != nil {
						return err
					}
				}
				u.panels[fmt.Sprintf("%s/%d", s.ID, selection)] = im
			}
		}
	}
	bg, err := readImage("new-game-panel-b-v1.png", dialogArtSHA)
	if err != nil {
		return err
	}
	u.dialog = localeClone(bg)
	for i, key := range []string{"help.goal", "help.medal", "help.performance"} {
		rect := []image.Rectangle{image.Rect(16, 16, 928, 280), image.Rect(16, 280, 928, 400), image.Rect(16, 400, 928, 512)}[i]
		if err := u.ui.Paragraph(u.dialog, u.language, key, rect, 44, 24, color.White); err != nil {
			return err
		}
	}
	blue, err := readImage("menu-blue-b-v1.png", "eeb1aa620c179a7fa0233bdfc9d9ad6abf8719d36f1ad05dc93c84343a164ea9")
	if err != nil {
		return err
	}
	wood, err := readImage("menu-wood-b-v2.png", "7622ec92b2b8d3dc2f56c7d0bdca489f61aca788617d92ecccceeb41de3ff8f7")
	if err != nil {
		return err
	}
	red, err := readImage("menu-red-b-v1.png", "e01cc0cfc4f5dc064ba0fadd7b7eff7ee35967451bcc1d38313b961e986c432e")
	if err != nil {
		return err
	}
	if err := u.prepareExtras(r, blue, wood, red); err != nil {
		return err
	}
	raw, err := os.ReadFile(filepath.Join(dir, "budget-layout-v1.json"))
	if err != nil || digest(raw) != "f505cd1ca1e70a798d26d4e1caa9f3a3170ca4cb93b88dd0c81e40a8eb5891f0" {
		return fmt.Errorf("interface-budget-layout")
	}
	var budget struct{ Panels [][4]int }
	if json.Unmarshal(raw, &budget) != nil {
		return fmt.Errorf("interface-budget-layout")
	}
	u.budget = image.NewRGBA(image.Rect(0, 0, 940, 528))
	dim := func(rect image.Rectangle, n byte) {
		localeScale(u.budget, rect, blue, 8)
		for y := rect.Min.Y; y < rect.Max.Y; y++ {
			for x := rect.Min.X; x < rect.Max.X; x++ {
				at := u.budget.PixOffset(x, y)
				for c := 0; c < 3; c++ {
					u.budget.Pix[at+c] /= n
				}
			}
		}
	}
	dim(u.budget.Bounds(), 5)
	for _, rect := range budget.Panels {
		dim(localeNative(rect), 3)
	}
	for _, field := range []struct {
		key  string
		rect [4]int
	}{
		{"budget.title", [4]int{3, 3, 88, 16}}, {"control.escape", [4]int{134, 4, 25, 14}}, {"control.up_down", [4]int{166, 4, 28, 14}}, {"control.left_right", [4]int{202, 4, 28, 14}},
		{"budget.back", [4]int{128, 21, 31, 14}}, {"budget.select", [4]int{164, 21, 31, 14}}, {"budget.adjust", [4]int{199, 21, 31, 14}},
		{"budget.tax", [4]int{2, 23, 63, 14}}, {"budget.public_safety", [4]int{2, 41, 63, 14}}, {"budget.traffic", [4]int{2, 59, 63, 14}}, {"budget.facilities", [4]int{2, 77, 63, 14}}, {"budget.power", [4]int{2, 94, 63, 14}},
		{"budget.tax_revenue", [4]int{2, 114, 31, 14}}, {"budget.net_amount", [4]int{122, 114, 31, 14}},
	} {
		if err := u.ui.DrawText(u.budget, u.language, field.key, localeNative(field.rect), 52, 14, color.White); err != nil {
			return err
		}
	}
	for _, p := range [][2]int{{216, 45}, {216, 64}, {216, 81}, {216, 99}, {216, 116}, {100, 116}} {
		if err := u.ui.DrawCompact(u.budget, u.language, "unit.ten_thousand", localeNative([4]int{p[0], p[1], 15, 14}), 48, 14, color.White); err != nil {
			return err
		}
	}
	for _, y := range []int{27, 47, 66, 83, 101} {
		if err := u.ui.DrawCompact(u.budget, u.language, "unit.percent", localeNative([4]int{111, y, 10, 9}), 32, 14, color.White); err != nil {
			return err
		}
	}
	if r.footer != nil && r.footer.art != nil {
		u.quit = image.NewRGBA(image.Rect(0, 0, 896, 72))
		draw.Draw(u.quit, u.quit.Bounds(), r.footer.art, image.Pt(28, 700), draw.Src)
		if err := u.ui.DrawText(u.quit, u.language, "file.confirm_exit", u.quit.Bounds().Inset(8), 48, 14, color.RGBA{255, 0, 0, 255}); err != nil {
			return err
		}
	}
	blank, err := readImage("ending-scene-v1/art-scaled.png", "ac77b0cc8fc8f085d6c09d6e3c9ea3107afbe57494d3ef6417c0cc8ce9250c2c")
	if err != nil {
		return err
	}
	u.ending = localeClone(blank)
	if err := u.ui.DrawCompact(u.ending, u.language, "ending.achievement", image.Rect(512, 12, 768, 68), 52, 14, color.RGBA{0, 0, 203, 255}); err != nil {
		return err
	}
	if r.charts != nil && r.charts.frame != nil {
		u.chart = localeClone(r.charts.frame)
		for _, entry := range []struct {
			key string
			y   int
		}{{"chart.maximum", 22}, {"chart.minimum", 101}} {
			for _, x := range []int{1, 127} {
				rect := image.Rect(x*4, entry.y*4, (x+17)*4, (entry.y+5)*4)
				bg := u.chart.RGBAAt(rect.Min.X, rect.Min.Y)
				draw.Draw(u.chart, rect, image.NewUniform(bg), image.Point{}, draw.Src)
				if err := u.ui.DrawCompact(u.chart, u.language, entry.key, rect, 24, 12, color.RGBA{255, 255, 85, 255}); err != nil {
					return err
				}
			}
		}
	}
	for i, f := range []struct {
		key  string
		w, h int
		ink  color.Color
	}{{"footer.per_unit", 192, 56, color.RGBA{255, 0, 0, 255}}, {"unit.ten_thousand", 64, 56, color.RGBA{255, 0, 0, 255}}, {"footer.year", 24, 28, color.RGBA{0, 0, 170, 255}}, {"footer.month", 48, 28, color.RGBA{0, 0, 170, 255}}, {"unit.ten_thousand.compact", 48, 28, color.RGBA{0, 0, 170, 255}}} {
		im := image.NewRGBA(image.Rect(0, 0, f.w, f.h))
		if err := u.ui.DrawCompact(im, u.language, f.key, im.Bounds(), 48, 12, f.ink); err != nil {
			return err
		}
		u.footer[i] = im
	}
	return nil
}

func (u *interfaceLocale) paint(r *Renderer, dst *image.RGBA, px []byte, pal [256][3]byte, s Stats) (int, string) {
	if u.reason != "" {
		restoreLocaleOriginal(dst, px, pal, dst.Bounds())
		return 0, u.reason
	}
	known := s.PanelReason == "matched-panel" || s.Dialog == "new-game" || s.Budget || s.FileDialog != "" || s.EndingScreen != "" || s.ChartWindow || s.FooterMask != 0
	if !known {
		return 0, "source-fallback"
	}
	if s.PanelReason == "matched-panel" {
		im := u.panels[fmt.Sprintf("%s/%d", s.Panel, s.PanelSelection)]
		if im == nil {
			return 0, "interface-panel-unavailable"
		}
		for _, set := range []*panelSet{r.panels, r.toolPanels, r.cityPanels} {
			for _, state := range set.states {
				if state.ID == s.Panel && state.Selection == s.PanelSelection {
					draw.Draw(dst, localeNative(state.Native), im, image.Point{}, draw.Src)
					return len(interfaceOptions[s.Panel]), "matched-interface"
				}
			}
		}
	}
	if s.Dialog == "new-game" {
		draw.Draw(dst, dialogRect, u.dialog, image.Point{}, draw.Src)
		return 3, "matched-interface"
	}
	if s.Budget {
		draw.Draw(dst, image.Rect(72, 148, 1012, 676), u.budget, image.Point{}, draw.Src)
		for i, value := range s.BudgetText {
			slot := budgetSlots[i]
			for column, ch := range value {
				index := bytes.IndexByte([]byte(budgetCharacters), byte(ch))
				row := 0
				if s.BudgetColors[i] == 12 {
					row = 28
				}
				x, y := (18+slot.x+column*6)*4, (37+slot.y)*4
				draw.Draw(dst, image.Rect(x, y, x+24, y+28), r.budget.glyphs, image.Pt(index*24, row), draw.Over)
			}
		}
		return 25, "matched-interface"
	}
	if s.FileDialog == "quit-confirm" && u.quit != nil {
		draw.Draw(dst, localeNative([4]int{7, 175, 224, 18}), u.quit, image.Point{}, draw.Src)
		return 1, "matched-interface"
	}
	if s.FileDialog == "file-browser" {
		return 0, "preserved-player-filenames"
	}
	if s.EndingScreen != "" {
		draw.Draw(dst, dst.Bounds(), u.ending, image.Point{}, draw.Src)
		return 1, "matched-interface"
	}
	if s.ChartWindow && u.chart != nil {
		for _, y := range []int{22, 101} {
			for _, x := range []int{1, 127} {
				rect := image.Rect(x*4, y*4, (x+17)*4, (y+5)*4)
				draw.Draw(dst, rect.Add(image.Pt(264, 140)), u.chart, rect.Min, draw.Src)
			}
		}
		return 4, "matched-interface"
	}
	return 0, "source-fallback"
}

func (u *interfaceLocale) paintFooter(r *Renderer, dst *image.RGBA, px []byte, pal [256][3]byte, s Stats) int {
	fields := 0
	if s.FooterMask&1 != 0 && s.FooterText[0] != "" {
		rect := footerRects[0]
		out := image.Rect(rect.Min.X*4, rect.Min.Y*4, rect.Max.X*4, rect.Max.Y*4)
		draw.Draw(dst, out, r.footer.art, out.Min, draw.Src)
		r.footer.numbers(dst, s.FooterText[0], 67, 181)
		for i, p := range []image.Point{{76, 708}, {412, 708}} {
			draw.Draw(dst, u.footer[i].Bounds().Add(p), u.footer[i], image.Point{}, draw.Over)
		}
		fields += 2
	}
	if s.FooterMask&2 != 0 {
		rect := footerRects[1]
		out := image.Rect(rect.Min.X*4, rect.Min.Y*4, rect.Max.X*4, rect.Max.Y*4)
		draw.Draw(dst, out, r.footer.art, out.Min, draw.Src)
		r.footer.numbers(dst, s.FooterText[1], 253, 176)
		r.footer.numbers(dst, s.FooterText[2], 289, 176)
		r.footer.numbers(dst, s.FooterText[3], 253, 184)
		for i, p := range []image.Point{{1132, 704}, {1212, 704}, {1212, 736}} {
			im := u.footer[i+2]
			draw.Draw(dst, im.Bounds().Add(p), im, image.Point{}, draw.Over)
		}
		restoreLocaleOriginal(dst, px, pal, image.Rect(988, 736, 1016, 764))
		fields += 3
	}
	return fields
}

func restoreLocaleOriginal(dst *image.RGBA, px []byte, pal [256][3]byte, rect image.Rectangle) {
	for y := rect.Min.Y; y < rect.Max.Y; y++ {
		for x := rect.Min.X; x < rect.Max.X; x++ {
			c := pal[px[(y/4)*320+x/4]]
			dst.SetRGBA(x, y, color.RGBA{c[0], c[1], c[2], 255})
		}
	}
}
