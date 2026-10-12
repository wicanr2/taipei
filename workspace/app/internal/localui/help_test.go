package localui

import (
	"image"
	"image/color"
	"image/png"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/wicanr2/taipei/preview/internal/i18n"
	"github.com/wicanr2/taipei/preview/locales"
)

func TestHelpAgainstApprovedReferenceAndCatalogFailures(t *testing.T) {
	dir := os.Getenv("TAIPEI_HD_MATERIALS")
	if dir == "" {
		t.Skip("set TAIPEI_HD_MATERIALS")
	}
	u, err := New(filepath.Join(dir, "fonts"), i18n.Bundled())
	if err != nil {
		t.Fatal(err)
	}
	panel := image.Rect(40, 40, 1240, 760)
	for _, lang := range i18n.Languages {
		got, err := u.Help(lang)
		if err != nil {
			t.Fatal(lang, err)
		}
		f, err := os.Open(filepath.Join(dir, "locale-help-draft-r1", "help-shift-f1-"+lang+".png"))
		if err != nil {
			t.Fatal(err)
		}
		ref, err := png.Decode(f)
		f.Close()
		if err != nil {
			t.Fatal(err)
		}
		for y := 0; y < 800; y++ {
			for x := 0; x < 1280; x++ {
				c := got.RGBAAt(x, y)
				if !image.Pt(x, y).In(panel) {
					if c.A != 0 {
						t.Fatal("help leaked", lang, x, y)
					}
				} else if c != color.RGBAModel.Convert(ref.At(x, y)).(color.RGBA) {
					t.Fatal("help reference mismatch", lang, x, y)
				}
			}
		}
	}
	if _, err := u.Help("unknown"); err == nil {
		t.Fatal("unknown language accepted")
	}
	// Only change TSV data: product code and layout stay untouched.
	lines := strings.Split(string(locales.Bundled), "\n")
	for _, failure := range []string{"missing-key", "missing-glyph", "overflow"} {
		var modified []string
		for _, line := range lines {
			if strings.HasPrefix(line, "help.action.open\t") {
				if failure == "missing-key" {
					continue
				}
				cells := strings.Split(line, "\t")
				if failure == "missing-glyph" {
					cells[5] += "\u0378"
				} else {
					cells[5] = strings.Repeat("W", 200)
				}
				line = strings.Join(cells, "\t")
			}
			modified = append(modified, line)
		}
		c, err := i18n.Parse([]byte(strings.Join(modified, "\n")))
		if err != nil {
			t.Fatal(err)
		}
		reason := map[string]string{
			"missing-key":   "catalog-required:help.action.open",
			"missing-glyph": "font-glyph:U+0378",
			"overflow":      "text-layout:en/help.action.open",
		}[failure]
		if _, err := New(filepath.Join(dir, "fonts"), c); err == nil || err.Error() != reason {
			t.Fatal("help failure reason", failure, err, reason)
		}
	}
}
