package main

import (
	"bytes"
	"crypto/sha256"
	"image"
	"testing"

	"github.com/wicanr2/taipei/preview/internal/hd"
)

func TestPresentationCacheNativePixelsPaletteAndOverlay(t *testing.T) {
	px := make([]byte, 64000)
	pal := [256][3]byte{0: {12, 34, 56}, 1: {90, 80, 70}}
	r := hd.New(nil, "")
	var cache presentationCache
	draws := 0
	draw := func() (*image.RGBA, hd.Stats) {
		draws++
		return r.Render(px, pal, 19, false, false, hd.Origin{})
	}
	key := presentationKey{Pixels: sha256.Sum256(px), Palette: pal, Mode: 19}
	first, _ := cache.render(key, draw)
	want := append([]byte(nil), first.Pix...)
	// A frontend overlay must be removed even when the native screen is unchanged.
	first.Pix[0], first.Pix[1] = 255, 255
	second, _ := cache.render(key, draw)
	if draws != 1 || !bytes.Equal(second.Pix, want) {
		t.Fatal("stale frontend overlay or repeated render")
	}
	px[0] = 1
	key.Pixels = sha256.Sum256(px)
	changed, _ := cache.render(key, draw)
	if draws != 2 || changed.Pix[0] != 90 {
		t.Fatal("native pixel change was not rendered")
	}
	pal[1] = [3]byte{1, 2, 3}
	key.Palette = pal
	changed, _ = cache.render(key, draw)
	if draws != 3 || changed.Pix[0] != 1 {
		t.Fatal("palette change was not rendered")
	}
	// A changed source call can reorder HD art without changing the native pixels.
	key.IllustrationRevision++
	cache.render(key, draw)
	key.TextRevision++
	cache.render(key, draw)
	if draws != 5 {
		t.Fatal("native source observation did not invalidate")
	}
}
