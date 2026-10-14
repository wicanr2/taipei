package hd

import (
	"bytes"
	"image"
	"image/color"
	"image/draw"
	"os"
	"path/filepath"
	"testing"

	"github.com/wicanr2/taipei/preview/internal/i18n"
)

func TestIllustrationLayerOcclusionAndFallback(t *testing.T) {
	base := IllustrationSource{ID: "base", Width: 3, Height: 2, Pixels: []byte{1, 2, 3, 4, 5, 6}}
	front := IllustrationSource{ID: "front", Width: 1, Height: 2, Pixels: []byte{7, 8}}
	var pal [256][3]byte
	for i := range pal {
		pal[i] = [3]byte{byte(i), byte(i), byte(i)}
	}
	art := func(w, h int, c color.RGBA) *image.RGBA {
		im := image.NewRGBA(image.Rect(0, 0, w*4, h*4))
		draw.Draw(im, im.Bounds(), image.NewUniform(c), image.Point{}, draw.Src)
		return im
	}
	red, green := color.RGBA{240, 0, 0, 255}, color.RGBA{0, 240, 0, 255}
	s := &illustrationSet{sources: map[string]IllustrationSource{"base": base, "front": front}, palettes: map[string][256][3]byte{"test": pal}, assets: map[string]*illustrationAsset{
		"base":  {ID: "base", variants: []illustrationVariant{{Palette: "test", art: art(3, 2, red)}}},
		"front": {ID: "front", variants: []illustrationVariant{{Palette: "test", art: art(1, 2, green)}}},
	}}
	r := &Renderer{illustrations: s}
	back := IllustrationDraw{ID: "base", Clip: image.Rect(0, 0, 3, 2)}
	top := IllustrationDraw{ID: "front", X: 1, Clip: image.Rect(1, 0, 2, 2)}
	px := make([]byte, 64000)
	copy(px, []byte{1, 7, 3})
	copy(px[320:], []byte{4, 8, 6})
	r.illustrationDraws = []IllustrationDraw{back, top}
	check := func(expected int) *image.RGBA {
		im := image.NewRGBA(image.Rect(0, 0, 1280, 800))
		original := append([]byte(nil), px...)
		stats := r.paintIllustrations(im, px, pal, nil)
		if stats.Painted != expected {
			t.Fatalf("painted=%d expected=%d reasons=%v", stats.Painted, expected, stats.Reasons)
		}
		if !bytes.Equal(original, px) {
			t.Fatal("original pixels mutated")
		}
		return im
	}
	im := check(2)
	if im.RGBAAt(0, 0) != red || im.RGBAAt(4, 0) != green {
		t.Fatal("draw order lost")
	}
	px[2] ^= 1
	im = check(1)
	if im.RGBAAt(0, 0).A != 0 || im.RGBAAt(4, 0) != green {
		t.Fatal("source mismatch leaked older art")
	}
	px[2] ^= 1
	r.illustrationDraws = []IllustrationDraw{back, {Clip: image.Rect(1, 0, 2, 2)}}
	im = check(1)
	if im.RGBAAt(4, 0).A != 0 || im.RGBAAt(0, 0) != red {
		t.Fatal("unknown call did not protect its rectangle")
	}
	r.illustrationDraws = []IllustrationDraw{back, {Clip: image.Rect(0, 0, 320, 200)}}
	check(0)
	r.illustrationDraws = []IllustrationDraw{back, top}
	pal[1][0] ^= 1
	im = check(1)
	if im.RGBAAt(0, 0).A != 0 {
		t.Fatal("unknown palette accepted")
	}
	pal[1][0] ^= 1
	s.assets["front"].variants[0].art = nil
	im = check(1)
	if im.RGBAAt(4, 0).A != 0 {
		t.Fatal("missing foreground asset exposed older art")
	}
	// An opaque raw 255 is owned; only the actual transparent key is skipped.
	front.Pixels = []byte{255, 8}
	v, owns := illustrationOwned(front, top, 1, 0)
	if !owns || v != 255 {
		t.Fatal("opaque raw 255 discarded")
	}
	top.Transparent = true
	top.Key = 255
	if _, owns = illustrationOwned(front, top, 1, 0); owns {
		t.Fatal("transparent key painted")
	}
	top.Key = 8
	if _, owns = illustrationOwned(front, top, 1, 0); !owns {
		t.Fatal("non255 transparent key ignored")
	}
}

func TestIllustrationDecoderBounds(t *testing.T) {
	for _, sample := range []struct {
		raw      []byte
		encoding string
	}{
		{[]byte{1, 0, 1, 0, 0, 7, 0}, "zero-color-count-candidate"},
		{[]byte{1, 0, 1, 0, 7, 8}, "raw"},
		{[]byte{0, 0, 1, 255, 255, 255}, "iv2"},
		{[]byte{0, 0, 1, 7}, "iv2"},
	} {
		if _, _, px := decodeIllustration(sample.raw, sample.encoding); px != nil {
			t.Fatal("malformed stream accepted", sample)
		}
	}
}

func TestIllustrationOriginalSourcesAndSealedAssets(t *testing.T) {
	orig, dir := os.Getenv("TAIPEI_HD_ORIGINAL"), os.Getenv("TAIPEI_HD_MATERIALS")
	if orig == "" || dir == "" {
		t.Skip("requires local original ROMs and READY assets")
	}
	read := func(n string) []byte {
		b, e := os.ReadFile(filepath.Join(orig, n))
		if e != nil {
			t.Fatal(e)
		}
		return b
	}
	exe, rom, romA := read("RS201.EXE"), read("RS201.ROM"), read("RS201A.ROM")
	r := New(rom, dir)
	r.InitTextSources(exe, rom, romA)
	sources := r.InitIllustrations(exe, rom, romA, dir)
	if len(sources) != 209 || r.illustrations.reason != "" || len(r.illustrations.sources) != 197 || len(r.illustrations.assets) != 179 {
		t.Fatal("source coverage", len(sources), r.illustrations.reason)
	}
	for id, a := range r.illustrations.assets {
		for _, v := range a.variants {
			if v.art == nil {
				t.Fatal("missing READY variant", id, v.Palette)
			}
		}
	}
	if len(r.TextImageSources()) != 16 {
		t.Fatal("preview text sources", len(r.TextImageSources()))
	}
	for _, lang := range i18n.Languages {
		r.SetLanguage(i18n.Bundled(), lang)
		if r.locale.reason != "" {
			t.Fatal(lang, r.locale.reason)
		}
		for _, key := range []string{"art.maximum", "art.minimum"} {
			patch := image.NewRGBA(image.Rect(0, 0, 68, 20))
			if err := r.locale.ui.DrawReveal(patch, lang, key, patch.Bounds(), 20, 12, 1, 1, color.RGBA{255, 255, 0, 255}); err != nil {
				t.Fatal(lang, key, err)
			}
			ink := 0
			for i := 3; i < len(patch.Pix); i += 4 {
				if patch.Pix[i] != 0 {
					ink++
				}
			}
			if ink == 0 {
				t.Fatal("preview label has no ink", lang, key)
			}
		}
	}
	// Exercise actual file failures against a private copy of the sealed bundle.
	local := filepath.Join(t.TempDir(), "illustrations-ready-v1")
	if err := os.Mkdir(local, 0700); err != nil {
		t.Fatal(err)
	}
	entries, err := os.ReadDir(filepath.Join(dir, "illustrations-ready-v1"))
	if err != nil {
		t.Fatal(err)
	}
	for _, e := range entries {
		data, err := os.ReadFile(filepath.Join(dir, "illustrations-ready-v1", e.Name()))
		if err != nil {
			t.Fatal(err)
		}
		if err = os.WriteFile(filepath.Join(local, e.Name()), data, 0600); err != nil {
			t.Fatal(err)
		}
	}
	bad := r.illustrations.assets["a04-00"].variants[0].File
	if err = os.Remove(filepath.Join(local, bad)); err != nil {
		t.Fatal(err)
	}
	failed := &Renderer{}
	failed.InitIllustrations(exe, rom, romA, filepath.Dir(local))
	if failed.illustrations.reason != "" || failed.illustrations.assets["a04-00"].variants[0].art != nil || failed.illustrations.assets["a05-00"].variants[1].art == nil {
		t.Fatal("missing art not isolated")
	}
	if err = os.WriteFile(filepath.Join(local, bad), []byte("broken PNG"), 0600); err != nil {
		t.Fatal(err)
	}
	failed.InitIllustrations(exe, rom, romA, filepath.Dir(local))
	if failed.illustrations.reason != "" || failed.illustrations.assets["a04-00"].variants[0].art != nil {
		t.Fatal("modified PNG accepted")
	}
	if err = os.WriteFile(filepath.Join(local, "manifest.json"), []byte("{}"), 0600); err != nil {
		t.Fatal(err)
	}
	if failed.InitIllustrations(exe, rom, romA, filepath.Dir(local)) != nil || failed.illustrations.reason != "illustration-manifest" {
		t.Fatal("unsealed manifest accepted")
	}
	r.InitIllustrations(exe, rom, romA, t.TempDir())
	if r.illustrations.reason != "illustration-manifest" {
		t.Fatal("missing manifest accepted")
	}
	romA = append([]byte(nil), romA...)
	romA[0] ^= 1
	if r.InitIllustrations(exe, rom, romA, dir) != nil {
		t.Fatal("changed original ROM accepted")
	}
	t.Log("209 raw aliases, 197 canonical images, 179 art sources, 537 palette variants, 16 text sources")
}
