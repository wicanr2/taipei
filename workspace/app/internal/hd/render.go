// Package hd is the discardable live prototype described by spec/010.
// It owns only presentation pixels and never imports the DOS executor.
package hd

import (
	"crypto/sha256"
	"encoding/binary"
	"fmt"
	"image"
	"image/png"
	"os"
	"path/filepath"
)

const romSHA = "0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29"
const uiSHA = "b9b27e2010b2d581cb55c349b5944492ea0077104e15126236fc50b859b51eda"
const paletteSHA = "9bd7a6f66fe9e1da47ea3360ffbd0e114616d466034ff8b999529ae38afe6b0b"
const budgetSHA = "a93af2ea621191dc51663f84eee9ebc40672d149d585a1458b9edf3c60e872bb"

var materials = map[string]string{
	"water":  "c5946a794cb44daea5e1492ecd880a0e2bb42e9ebe6da62e472a651abfa26015",
	"sand":   "90c23e56f9c8a116fbe8cc7d8b2c1a494eb7044d3ff57c3ff28a60f5b911717f",
	"forest": "0bb1f136ce10e014e27626ab11dc5f3c18431fdcb9c6ab8fbd063b478e8644f7",
}

type Stats struct {
	Illustrations              illustrationStats   `json:"illustrations"`
	SourceText                 int                 `json:"source_text_fields"`
	SourceImages               int                 `json:"source_image_fields"`
	SourceTextKey              string              `json:"source_text_key"`
	SourceImageKey             string              `json:"source_image_key"`
	SourceTextKeys             []string            `json:"source_text_keys"`
	SourceImageKeys            []string            `json:"source_image_keys"`
	InterfacePanel             string              `json:"interface_panel"`
	LocalizedFields            int                 `json:"localized_fields"`
	LocaleReason               string              `json:"locale_reason"`
	ChartWindow                bool                `json:"chart_window"`
	ChartReason                string              `json:"chart_reason"`
	ChartDataSHA               string              `json:"chart_data_sha256"`
	EndingScreen               string              `json:"ending_screen"`
	EndingReason               string              `json:"ending_reason"`
	PowerFacility              powerFacilityStats  `json:"power_facility"`
	NuclearFacility            publicFacilityStats `json:"nuclear_facility"`
	TransportFacilities        publicFacilityStats `json:"transport_facilities"`
	CivicFacilities            civicFacilityStats  `json:"civic_facilities"`
	PublicFacilities           publicFacilityStats `json:"public_facilities"`
	CityBuildings              cityBuildingStats   `json:"city_buildings"`
	Infrastructure             infrastructureStats `json:"infrastructure"`
	MapCompletion              mapCompletionStats  `json:"map_completion"`
	Budget                     bool                `json:"budget"`
	BudgetText                 [11]string          `json:"budget_text"`
	BudgetColors               [11]byte            `json:"budget_colors"`
	BudgetSelection            int                 `json:"budget_selection"`
	BudgetReason               string              `json:"budget_reason"`
	FileDialog                 string              `json:"file_dialog"`
	FileText                   [8]string           `json:"file_text"`
	FileColors                 [8]byte             `json:"file_colors"`
	FileReason                 string              `json:"file_reason"`
	FooterMask                 uint8               `json:"footer_mask"`
	FooterText                 [4]string           `json:"footer_text"`
	FooterReason               string              `json:"footer_reason"`
	ChromeParts                int                 `json:"chrome_parts"`
	ChromeMask                 uint8               `json:"chrome_mask"`
	ChromeRings                int                 `json:"chrome_rings"`
	ChromeRingMask             uint16              `json:"chrome_ring_mask"`
	ChromeReason               string              `json:"chrome_reason"`
	Reason                     string              `json:"reason"`
	Matched, Painted, Fallback int
	FontLabels                 int    `json:"font_labels"`
	FontReason                 string `json:"font_reason"`
	UIIcons                    int    `json:"ui_icons"`
	UIIconMask                 uint16 `json:"ui_icon_mask"`
	UIReason                   string `json:"ui_reason"`
	Dialog                     string `json:"dialog"`
	DialogReason               string `json:"dialog_reason"`
	Panel                      string `json:"panel"`
	PanelSelection             int    `json:"panel_selection"`
	PanelReason                string `json:"panel_reason"`
}

// Origin is the verified tile origin of a completed original map draw.
type Origin struct {
	X, Y  int
	Valid bool
}

const materialSize = 1254

type Renderer struct {
	illustrations       *illustrationSet
	illustrationDraws   []IllustrationDraw
	lastTextRects       []image.Rectangle
	imageUnderlays      map[image.Rectangle]*image.RGBA
	illustrationRects   []image.Rectangle
	lastTextKeys        []string
	lastImageKeys       []string
	textSources         *textSources
	textDraws           []TextDraw
	textImageDraws      []TextImageDraw
	textROM             []byte
	extra               *interfaceSources
	locale              *interfaceLocale
	fontDir             string
	charts              *chartWindows
	ending              *endingScreen
	powerFacility       *powerFacilitySet
	nuclearFacility     *publicFacilitySet
	transportFacilities *publicFacilitySet
	civicFacilities     *civicFacilitySet
	publicFacilities    *publicFacilitySet
	cityBuildings       *cityBuildingSet
	mapComplex          *publicFacilitySet
	mapZonesBase        *publicFacilitySet
	mapZones            *publicFacilitySet
	mapDetail           *infrastructureSet
	infrastructure      *infrastructureSet
	budget              *budgetPanel
	files               *fileDialogs
	footer              *cityFooter
	chrome              *cityChrome
	frame               *image.RGBA
	sources             map[string]bool
	shades              map[byte][]byte
	reason              string
	menu                *menuFont
	icons               *toolIcons
	dialog              *newGameDialog
	panels              *panelSet
	toolPanels          *panelSet
	cityPanels          *panelSet
}

func digest(p []byte) string { return fmt.Sprintf("%x", sha256.Sum256(p)) }
func New(rom []byte, dir string) *Renderer {
	r := &Renderer{fontDir: filepath.Join(dir, "fonts"), frame: image.NewRGBA(image.Rect(0, 0, 1280, 800)), sources: map[string]bool{}, shades: map[byte][]byte{}}
	if digest(rom) != romSHA {
		r.reason = "rom-mismatch"
		return r
	}
	u16 := func(p []byte) int { return int(binary.LittleEndian.Uint16(p)) }
	rec := 8 + 59*16
	off := int(binary.LittleEndian.Uint32(rom[rec+10:]))
	n := u16(rom[rec+14:])
	lib := rom[off : off+n]
	if u16(lib) != 135 {
		r.reason = "library-shape"
		return r
	}
	for i := 0; i < 135; i++ {
		a := u16(lib[2+i*2:])
		z := len(lib)
		if i+1 < 135 {
			z = u16(lib[4+i*2:])
		}
		if a < 272 || a >= z || z > len(lib) {
			r.reason = "library-offset"
			return r
		}
		b := lib[a:z]
		if len(b) != 85 || u16(b) != 9 || u16(b[2:]) != 9 {
			r.reason = "tile-shape"
			return r
		}
		r.sources[string(b[4:])] = true
	}
	r.menu = loadMenuFont(filepath.Join(dir, "fonts"))
	r.icons = loadToolIcons(rom, dir)
	r.dialog = loadNewGameDialog(dir)
	r.panels = loadPanels(dir)
	r.toolPanels = loadToolPanels(dir)
	r.cityPanels = loadCityPanels(dir)
	r.chrome = loadCityChrome(rom, dir)
	r.footer = loadCityFooter(rom, dir)
	r.files = loadFileDialogs(rom, dir)
	r.budget = loadBudgetPanel(rom, dir)
	r.infrastructure = loadInfrastructure(rom, dir)
	r.powerFacility = loadPowerFacilities(rom, dir)
	r.nuclearFacility = loadNuclearFacility(rom, dir)
	r.transportFacilities = loadTransportFacilities(rom, dir)
	r.civicFacilities = loadCivicFacilities(rom, dir)
	r.publicFacilities = loadPublicFacilities(rom, dir)
	r.cityBuildings = loadCityBuildings(rom, dir)
	r.mapComplex = loadMapAtlases(rom, dir, false)
	r.mapZonesBase = loadMapAtlases(rom, dir, true)
	zones := *r.mapZonesBase
	if zones.reason == "" {
		zones.reason = "map-zone-font"
	}
	r.mapZones = &zones
	r.mapDetail = loadMapDetail(rom, dir)
	r.ending = loadEndingScreen(rom, dir)
	r.charts = loadChartWindows(rom, dir)
	r.extra = loadInterfaceSources(rom)
	for name, want := range materials {
		p, e := os.ReadFile(filepath.Join(dir, name+"-b-v1.png"))
		if e != nil || digest(p) != want {
			continue
		}
		f, e := os.Open(filepath.Join(dir, name+"-b-v1.png"))
		if e != nil {
			continue
		}
		im, e := png.Decode(f)
		f.Close()
		if e != nil || im.Bounds() != image.Rect(0, 0, 1254, 1254) {
			continue
		}
		for index := 0; index < 256; index++ {
			if material(byte(index)) != name {
				continue
			}
			cache := make([]byte, materialSize*materialSize*4)
			for y := 0; y < materialSize; y++ {
				for x := 0; x < materialSize; x++ {
					rr, g, b, _ := im.At(x, y).RGBA()
					at := (y*materialSize + x) * 4
					for j, v := range []uint32{rr, g, b} {
						value := float64(v>>8) * shade(byte(index))
						if value > 255 {
							value = 255
						}
						cache[at+j] = byte(value)
					}
					cache[at+3] = 255
				}
			}
			r.shades[byte(index)] = cache
		}
	}
	return r
}

func (r *Renderer) Render(px []byte, pal [256][3]uint8, mode int, blocked, enabled bool, origin Origin) (result *image.RGBA, stats Stats) {
	stats = Stats{Fallback: 435, Reason: "original", FontReason: "scene-fallback", UIReason: "scene-fallback", DialogReason: "scene-fallback", PanelSelection: -1, PanelReason: "scene-fallback", ChromeReason: "scene-fallback", FileReason: "scene-fallback"}
	defer func() {
		if r.locale != nil && enabled && mode == 19 && len(px) == 64000 && result != nil {
			stats.LocalizedFields, stats.LocaleReason = r.locale.paint(r, result, px, pal, stats)
			if r.locale.reason == "" {
				extra, id := r.locale.paintExtras(r, result, px, pal)
				stats.LocalizedFields += extra
				stats.InterfacePanel = id
				top := footerCrop(px, image.Rect(0, 0, 270, 33))
				if digest(top) == uiSHA {
					stats.FontLabels, stats.FontReason = r.menu.paint(result, pal)
				}
				stats.FooterMask, stats.FooterText, stats.FooterReason = r.footer.paint(result, px, pal)
				stats.LocalizedFields += r.locale.paintFooter(r, result, px, pal, stats)
				if stats.LocalizedFields > 0 {
					stats.LocaleReason = "matched-interface"
				}
				stats.SourceText, stats.SourceTextKey = r.paintTextSources(result, px, pal)
				r.imageUnderlays = nil
				if r.illustrations != nil && r.illustrations.reason == "" {
					fields := r.prepareTextImageFields(px, pal)
					for _, f := range fields {
						for y := 0; y < f.background.Bounds().Dy(); y++ {
							at := ((f.native.Min.Y*4+y)*1280 + f.native.Min.X*4) * 4
							from := y * f.background.Stride
							copy(result.Pix[at:at+f.background.Stride], f.background.Pix[from:from+f.background.Stride])
						}
					}
					stats.Illustrations = r.paintIllustrations(result, px, pal, fields)
					r.imageUnderlays = map[image.Rectangle]*image.RGBA{}
					for _, f := range fields {
						for _, box := range r.illustrationRects {
							if !f.native.Overlaps(box) {
								continue
							}
							patch := image.NewRGBA(f.background.Bounds())
							for y := 0; y < patch.Bounds().Dy(); y++ {
								at := ((f.native.Min.Y*4+y)*1280 + f.native.Min.X*4) * 4
								copy(patch.Pix[y*patch.Stride:(y+1)*patch.Stride], result.Pix[at:at+patch.Stride])
							}
							r.imageUnderlays[f.native] = patch
							break
						}
					}
				}
				stats.SourceImages, stats.SourceImageKey = r.paintTextImages(result, px, pal)
				stats.SourceTextKeys, stats.SourceImageKeys = r.lastTextKeys, r.lastImageKeys
				stats.LocalizedFields += stats.SourceText + stats.SourceImages
				if stats.SourceText+stats.SourceImages > 0 {
					stats.LocaleReason = "matched-interface"
				}
			}
		}
	}()
	stats.BudgetSelection, stats.BudgetReason = -1, "scene-fallback"
	stats.EndingReason = "scene-fallback"
	stats.ChartReason = "scene-fallback"
	if len(px) != 64000 {
		clear(r.frame.Pix)
		stats.Reason = "frame-shape"
		return r.frame, stats
	}
	for y := 0; y < 200; y++ {
		for x := 0; x < 320; x++ {
			c := pal[px[y*320+x]]
			for dy := 0; dy < 4; dy++ {
				at := ((y*4+dy)*1280 + x*4) * 4
				for dx := 0; dx < 4; dx++ {
					copy(r.frame.Pix[at+dx*4:at+dx*4+3], c[:])
					r.frame.Pix[at+dx*4+3] = 255
				}
			}
		}
	}
	if !enabled {
		stats.ChartReason = "original"
		stats.EndingReason = "original"
		stats.BudgetReason = "original"
		stats.FileReason = "original"
		stats.FontReason = "original"
		stats.UIReason = "original"
		stats.DialogReason = "original"
		stats.PanelReason = "original"
		stats.ChromeReason = "original"
		return r.frame, stats
	}
	if r.reason != "" {
		stats.Reason = r.reason
		return r.frame, stats
	}
	if mode != 19 {
		stats.Reason = "video-mode"
		return r.frame, stats
	}
	if endingScreenSource(px) {
		stats.EndingReason = r.ending.paint(r.frame, pal, blocked)
		stats.Reason = stats.EndingReason
		if stats.EndingReason == "matched-ending-screen" {
			stats.EndingScreen = "achievement-base"
		}
		return r.frame, stats
	}
	if r.charts.source(px) {
		stats.ChartReason, stats.ChartDataSHA = r.charts.paint(r.frame, px, pal, blocked)
		stats.ChartWindow = stats.ChartReason == "matched-chart-window"
		stats.Reason = stats.ChartReason
		return r.frame, stats
	}
	stats.Panel, stats.PanelSelection, stats.PanelReason = r.panels.paint(r.frame, px, pal)
	if stats.PanelReason != "scene-fallback" {
		// 匹配選單或已知素材失配時，均不再疊加城市覆繪。
		stats.Reason = stats.PanelReason
		if stats.PanelReason == "matched-panel" || stats.PanelReason == "panel-art-mismatch" || stats.PanelReason == "panel-art-shape" || stats.PanelReason == "panel-palette-mismatch" {
			return r.frame, stats
		}
	}
	// 此完整來源是等待原版輸入的說明面板，與城市地景條件獨立。
	if dialogSource(px) {
		stats.DialogReason = r.dialog.paint(r.frame, pal)
		stats.Reason = stats.DialogReason
		if stats.DialogReason == "matched-dialog" {
			stats.Dialog = "new-game"
		}
		return r.frame, stats
	}
	// 工具子選單等待 BIOS 輸入，完整來源須先於阻塞回退判斷。
	id, selection, reason := r.toolPanels.paint(r.frame, px, pal)
	if reason != "scene-fallback" {
		stats.Panel, stats.PanelSelection, stats.PanelReason = id, selection, reason
		stats.Reason = reason
		if reason == "matched-panel" || reason == "panel-art-mismatch" || reason == "panel-art-shape" || reason == "panel-palette-mismatch" {
			return r.frame, stats
		}
	}
	id, selection, reason = r.cityPanels.paint(r.frame, px, pal)
	if reason != "scene-fallback" {
		stats.Panel, stats.PanelSelection, stats.PanelReason = id, selection, reason
		stats.Reason = reason
		if reason == "matched-panel" || reason == "panel-art-mismatch" || reason == "panel-art-shape" || reason == "panel-palette-mismatch" {
			return r.frame, stats
		}
	}
	if file, text, colors, why, known := r.files.paint(r.frame, px, pal); known {
		stats.FileDialog, stats.FileText, stats.FileColors, stats.FileReason = file, text, colors, why
		stats.Reason = why
		return r.frame, stats
	}
	if painted, text, colors, selection, why, known := r.budget.paint(r.frame, px, pal); known {
		stats.Budget, stats.BudgetText, stats.BudgetColors = painted, text, colors
		stats.BudgetSelection, stats.BudgetReason = selection, why
		stats.Reason = why
		return r.frame, stats
	}
	if blocked {
		stats.Reason = "blocking-input"
		return r.frame, stats
	}
	var colors []byte
	for i := 0; i < 256; i++ {
		if material(byte(i)) != "" {
			colors = append(colors, pal[i][:]...)
		}
	}
	if digest(colors) != paletteSHA {
		stats.Reason = "palette-mismatch"
		return r.frame, stats
	}
	top := make([]byte, 0, 270*33)
	for y := 0; y < 33; y++ {
		top = append(top, px[y*320:y*320+270]...)
	}
	if digest(top) != uiSHA {
		stats.Reason = "scene-mismatch"
		return r.frame, stats
	}
	// Annual budget receipts have a visible panel while BIOS blocked is false.
	// The actual title pixels are indexed in spec/012; retain the entire frame.
	budget := make([]byte, 0, 99*22)
	for y := 38; y < 60; y++ {
		budget = append(budget, px[y*320+18:y*320+117]...)
	}
	if digest(budget) == budgetSHA {
		stats.Reason = "budget-window"
		return r.frame, stats
	}
	if !origin.Valid || origin.X < 0 || origin.X > 76 || origin.Y < 0 || origin.Y > 74 {
		stats.Reason = "origin-unverified"
		return r.frame, stats
	}
	stats.Reason = "matched-city"
	for y := 34; y < 169; y += 9 {
		for x := 5; x < 266; x += 9 {
			var tile [81]byte
			for row := 0; row < 9; row++ {
				copy(tile[row*9:(row+1)*9], px[(y+row)*320+x:(y+row)*320+x+9])
			}
			if candidate := r.infrastructure.tiles[tile]; candidate != nil {
				stats.Matched++
				stats.Infrastructure.Matched++
				reason := r.infrastructure.paint(r.frame, candidate, pal, (x-5)/9, (y-34)/9, origin)
				if stats.Infrastructure.Reasons == nil {
					stats.Infrastructure.Reasons = map[string]int{}
				}
				stats.Infrastructure.Reasons[reason]++
				if reason == "matched-infrastructure" {
					stats.Painted++
					stats.Fallback--
					stats.Infrastructure.Painted++
					if stats.Infrastructure.Images == nil {
						stats.Infrastructure.Images = map[int]int{}
					}
					stats.Infrastructure.Images[candidate.image]++
				} else {
					stats.Infrastructure.Fallback++
				}
				continue
			}
			if candidate := r.powerFacility.tiles[tile]; candidate != nil {
				stats.Matched++
				stats.PowerFacility.Matched++
				reason := r.powerFacility.paint(r.frame, candidate, pal, (x-5)/9, (y-34)/9)
				if stats.PowerFacility.Reasons == nil {
					stats.PowerFacility.Reasons = map[string]int{}
				}
				stats.PowerFacility.Reasons[reason]++
				if reason == "matched-power-facility" {
					stats.Painted++
					stats.Fallback--
					stats.PowerFacility.Painted++
					if stats.PowerFacility.Images == nil {
						stats.PowerFacility.Images = map[int]int{}
					}
					stats.PowerFacility.Images[candidate.image]++
				} else {
					stats.PowerFacility.Fallback++
				}
				continue
			}
			if candidate := r.nuclearFacility.tiles[tile]; candidate != nil {
				stats.Matched++
				stats.NuclearFacility.Matched++
				candidate, reason := r.nuclearFacility.resolve(tile, px, (x-5)/9, (y-34)/9)
				if candidate != nil {
					reason = r.nuclearFacility.paint(r.frame, candidate, pal, (x-5)/9, (y-34)/9)
				}
				if stats.NuclearFacility.Reasons == nil {
					stats.NuclearFacility.Reasons = map[string]int{}
				}
				stats.NuclearFacility.Reasons[reason]++
				if reason == "matched-nuclear-facility" {
					stats.Painted++
					stats.Fallback--
					stats.NuclearFacility.Painted++
					if stats.NuclearFacility.Facilities == nil {
						stats.NuclearFacility.Facilities = map[string]int{}
					}
					stats.NuclearFacility.Facilities[candidate.id]++
				} else {
					stats.NuclearFacility.Fallback++
				}
				continue
			}
			if candidate := r.transportFacilities.tiles[tile]; candidate != nil {
				stats.Matched++
				stats.TransportFacilities.Matched++
				reason := r.transportFacilities.paint(r.frame, candidate, pal, (x-5)/9, (y-34)/9)
				if stats.TransportFacilities.Reasons == nil {
					stats.TransportFacilities.Reasons = map[string]int{}
				}
				stats.TransportFacilities.Reasons[reason]++
				if reason == "matched-transport-facility" {
					stats.Painted++
					stats.Fallback--
					stats.TransportFacilities.Painted++
					if stats.TransportFacilities.Facilities == nil {
						stats.TransportFacilities.Facilities = map[string]int{}
					}
					stats.TransportFacilities.Facilities[candidate.id]++
				} else {
					stats.TransportFacilities.Fallback++
				}
				continue
			}
			if candidate := r.civicFacilities.tiles[tile]; candidate != nil {
				stats.Matched++
				stats.CivicFacilities.Matched++
				reason := r.civicFacilities.paint(r.frame, candidate, pal, (x-5)/9, (y-34)/9)
				if stats.CivicFacilities.Reasons == nil {
					stats.CivicFacilities.Reasons = map[string]int{}
				}
				stats.CivicFacilities.Reasons[reason]++
				if reason == "matched-civic-facility" {
					stats.Painted++
					stats.Fallback--
					stats.CivicFacilities.Painted++
					if stats.CivicFacilities.Images == nil {
						stats.CivicFacilities.Images = map[string]int{}
					}
					stats.CivicFacilities.Images[fmt.Sprintf("%d/%d", candidate.member, candidate.image)]++
				} else {
					stats.CivicFacilities.Fallback++
				}
				continue
			}
			if candidate := r.publicFacilities.tiles[tile]; candidate != nil {
				stats.Matched++
				stats.PublicFacilities.Matched++
				candidate, reason := r.publicFacilities.resolve(tile, px, (x-5)/9, (y-34)/9)
				if candidate != nil {
					reason = r.publicFacilities.paint(r.frame, candidate, pal, (x-5)/9, (y-34)/9)
				}
				if stats.PublicFacilities.Reasons == nil {
					stats.PublicFacilities.Reasons = map[string]int{}
				}
				stats.PublicFacilities.Reasons[reason]++
				if reason == "matched-public-facility" {
					stats.Painted++
					stats.Fallback--
					stats.PublicFacilities.Painted++
					if stats.PublicFacilities.Facilities == nil {
						stats.PublicFacilities.Facilities = map[string]int{}
					}
					stats.PublicFacilities.Facilities[candidate.id]++
				} else {
					stats.PublicFacilities.Fallback++
				}
				continue
			}
			if candidate := r.cityBuildings.tiles[tile]; candidate != nil {
				stats.Matched++
				stats.CityBuildings.Matched++
				reason := r.cityBuildings.paint(r.frame, candidate, pal, (x-5)/9, (y-34)/9)
				if stats.CityBuildings.Reasons == nil {
					stats.CityBuildings.Reasons = map[string]int{}
				}
				stats.CityBuildings.Reasons[reason]++
				if reason == "matched-city-building" {
					stats.Painted++
					stats.Fallback--
					stats.CityBuildings.Painted++
					if stats.CityBuildings.Images == nil {
						stats.CityBuildings.Images = map[string]int{}
					}
					stats.CityBuildings.Images[fmt.Sprintf("%d/%d", candidate.member, candidate.image)]++
				} else {
					stats.CityBuildings.Fallback++
				}
				continue
			}
			if known, painted := r.paintMapCompletion(tile, px, pal, (x-5)/9, (y-34)/9, origin, &stats.MapCompletion); known {
				stats.Matched++
				if painted {
					stats.Painted++
					stats.Fallback--
				}
				continue
			}
			if !r.sources[string(tile[:])] {
				continue
			}
			stats.Matched++
			known := true
			for _, index := range tile {
				if r.shades[index] == nil {
					known = false
					break
				}
			}
			if !known {
				continue
			}
			for row := 0; row < 9; row++ {
				for col := 0; col < 9; col++ {
					cache := r.shades[tile[row*9+col]]
					for dy := 0; dy < 4; dy++ {
						xx, yy := (x+col)*4, (y+row)*4+dy
						at := (yy*1280 + xx) * 4
						wy := mirror(origin.Y*36 + yy - 136)
						for dx := 0; dx < 4; dx++ {
							wx := mirror(origin.X*36 + xx - 20 + dx)
							src := (wy*materialSize + wx) * 4
							copy(r.frame.Pix[at+dx*4:at+dx*4+4], cache[src:src+4])
						}
					}
				}
			}
			stats.Painted++
			stats.Fallback--
		}
	}
	stats.ChromeParts, stats.ChromeMask, stats.ChromeRings, stats.ChromeRingMask, stats.ChromeReason = r.chrome.paint(r.frame, px, pal)
	stats.FontLabels, stats.FontReason = r.menu.paint(r.frame, pal)
	stats.UIIcons, stats.UIIconMask, stats.UIReason = r.icons.paint(r.frame, px, pal)
	stats.FooterMask, stats.FooterText, stats.FooterReason = r.footer.paint(r.frame, px, pal)
	return r.frame, stats
}
func mirror(world int) int {
	i := world % (2 * materialSize)
	if i >= materialSize {
		i = 2*materialSize - 1 - i
	}
	return i
}
func material(index byte) string {
	switch {
	case index >= 103 && index <= 107:
		return "forest"
	case index >= 144 && index <= 147:
		return "water"
	case index >= 201 && index <= 204:
		return "sand"
	}
	return ""
}
func shade(index byte) float64 {
	switch material(index) {
	case "water":
		return .95 + float64(index-144)*.025
	case "sand":
		return .94 + float64(index-201)*.025
	case "forest":
		return .70 + float64(index-103)*.10
	}
	return 1
}
