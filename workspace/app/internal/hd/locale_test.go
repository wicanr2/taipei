package hd

import (
	"image/color"
	"image/png"
	"os"
	"path/filepath"
	"testing"

	"github.com/wicanr2/taipei/preview/internal/i18n"
)

func TestFiveLocaleLabelsAgainstDiscardableReference(t *testing.T) {
	dir := os.Getenv("TAIPEI_HD_MATERIALS")
	if dir == "" {
		t.Skip("set TAIPEI_HD_MATERIALS")
	}
	c := i18n.Bundled()
	for _, language := range i18n.Languages {
		m := loadMenuFontCatalog(filepath.Join(dir, "fonts"), c, language)
		if m.reason != "matched-menu" {
			t.Fatal(language, m.reason)
		}
		path := filepath.Join(dir, "locale-draft-r1", "city-"+language+".png")
		if language == i18n.Default {
			path = filepath.Join(dir, "font-comparison", "noto-font.png")
		}
		f, err := os.Open(path)
		if err != nil {
			t.Fatal(err)
		}
		ref, err := png.Decode(f)
		f.Close()
		if err != nil {
			t.Fatal(err)
		}
		for i, im := range m.labels {
			rect := menuRect(i)
			for y := 0; y < 68; y++ {
				for x := 0; x < 136; x++ {
					if im.RGBAAt(x, y) != color.RGBAModel.Convert(ref.At(rect.Min.X+x, rect.Min.Y+y)).(color.RGBA) {
						t.Fatal(language, i, x, y)
					}
				}
			}
		}
	}
	broken := []byte("key\tzh-Hant\tzh-Hans\tja\tko\ten\nmenu.exit\tx\tx\tx\tx\tx\n")
	partial, err := i18n.Parse(broken)
	if err != nil {
		t.Fatal(err)
	}
	if got := loadMenuFontCatalog(filepath.Join(dir, "fonts"), partial, "en"); got.reason != "font-catalog-mismatch" {
		t.Fatal(got.reason)
	}
}
