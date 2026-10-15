package main

import (
	"image"

	"github.com/wicanr2/taipei/preview/internal/hd"
)

// 042: every input to the native/HD base presentation participates in the key.
// Frontend panels are painted afterwards into a separate reusable buffer.
type presentationKey struct {
	Pixels                             [32]byte
	Palette                            [256][3]byte
	Mode                               int
	Blocked, HD                        bool
	Language                           string
	Origin                             hd.Origin
	TextRevision, IllustrationRevision uint64
}

type presentationCache struct {
	key          presentationKey
	valid        bool
	base, output *image.RGBA
	stats        hd.Stats
}

func (c *presentationCache) render(key presentationKey, draw func() (*image.RGBA, hd.Stats)) (*image.RGBA, hd.Stats) {
	if !c.valid || key != c.key {
		src, stats := draw()
		if c.base == nil || c.base.Bounds() != src.Bounds() {
			c.base = image.NewRGBA(src.Bounds())
			c.output = image.NewRGBA(src.Bounds())
		}
		copy(c.base.Pix, src.Pix)
		c.stats, c.key, c.valid = stats, key, true
	}
	// The caller may paint Help or language UI. Never retain those pixels.
	copy(c.output.Pix, c.base.Pix)
	return c.output, c.stats
}
