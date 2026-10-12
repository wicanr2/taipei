package main

import (
	"image"
	"image/draw"
	"log"

	"github.com/hajimehoshi/ebiten/v2"
	"github.com/hajimehoshi/ebiten/v2/inpututil"
	"github.com/wicanr2/taipei/preview/internal/i18n"
	"github.com/wicanr2/taipei/preview/internal/localui"
)

func (g *game) openLanguage() {
	// Balance all keys already forwarded before isolating modal input.
	for _, b := range bindings {
		if g.heldScans[b.scan] {
			g.queue(b.scan | 0x80)
		}
	}
	if g.mouseButtons != 0 {
		g.d.PressMouse(0)
		g.mouseButtons = 0
		g.inputs = append(g.inputs, inputEvent{Step: g.m.Steps, Kind: "mouse-button"})
	}
	g.localeOpen = true
	g.localeSelection = i18n.Index(g.language)
	g.rebuildPicker()
	g.inputs = append(g.inputs, inputEvent{Step: g.m.Steps, Kind: "frontend-panel", Text: "language-open"})
}

func (g *game) closeLanguage() {
	g.localeOpen = false
	g.localeFence = true
	g.inputs = append(g.inputs, inputEvent{Step: g.m.Steps, Kind: "frontend-panel", Text: "language-close"})
}

func (g *game) rebuildPicker() {
	var err error
	g.localeOverlay, err = g.localUI.Picker(g.language, g.localeSelection, g.localeWarning)
	if err != nil {
		log.Print(err)
		g.localeOverlay = nil
		g.closeLanguage()
	}
}

func (g *game) chooseLanguage() {
	g.language = i18n.Languages[g.localeSelection]
	g.hdRenderer.SetLanguage(g.catalog, g.language)
	ebiten.SetWindowTitle(g.catalog.Get(g.language, "window.title"))
	g.inputs = append(g.inputs, inputEvent{Step: g.m.Steps, Kind: "language", Text: g.language})
	if err := i18n.SaveSettings(g.settingsPath, g.language); err != nil {
		log.Print(err)
		g.localeWarning = "locale.error.settings"
		g.rebuildPicker()
		return
	}
	g.closeLanguage()
}

// The caller still services stop requests and frame receipts while a frontend
// panel is open. No VM steps, DOS keyboard, text or mouse input occur here.
func (g *game) languageInput() bool {
	if g.localUI == nil {
		return false
	}
	if g.localeFence {
		for _, b := range bindings {
			if ebiten.IsKeyPressed(b.key) {
				return true
			}
		}
		if ebiten.IsKeyPressed(ebiten.KeyF11) || ebiten.IsKeyPressed(ebiten.KeyF12) || ebiten.IsMouseButtonPressed(ebiten.MouseButtonLeft) || ebiten.IsMouseButtonPressed(ebiten.MouseButtonRight) {
			return true
		}
		g.localeFence = false
		// Discard this release frame as well, including text/IME events.
		return true
	}
	if !g.localeOpen {
		if inpututil.IsKeyJustPressed(ebiten.KeyF11) {
			g.openLanguage()
			return true
		}
		return false
	}
	if inpututil.IsKeyJustPressed(ebiten.KeyF11) || inpututil.IsKeyJustPressed(ebiten.KeyEscape) {
		g.closeLanguage()
		return true
	}
	changed := false
	if inpututil.IsKeyJustPressed(ebiten.KeyArrowUp) {
		g.localeSelection = (g.localeSelection + 4) % 5
		changed = true
	}
	if inpututil.IsKeyJustPressed(ebiten.KeyArrowDown) {
		g.localeSelection = (g.localeSelection + 1) % 5
		changed = true
	}
	if changed {
		g.rebuildPicker()
	}
	if inpututil.IsKeyJustPressed(ebiten.KeyEnter) {
		g.chooseLanguage()
		return true
	}
	if inpututil.IsMouseButtonJustPressed(ebiten.MouseButtonLeft) {
		x, y := ebiten.CursorPosition()
		for i := range i18n.Languages {
			if image.Pt(x, y).In(localui.ChoiceRect(i)) {
				g.localeSelection = i
				g.chooseLanguage()
				break
			}
		}
	}
	return true
}

func (g *game) paintLanguage() {
	if g.localeOpen && g.localeOverlay != nil {
		draw.Draw(g.presentation, g.presentation.Bounds(), g.localeOverlay, image.Point{}, draw.Over)
	}
}
