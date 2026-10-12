package localui

import (
	"image"
	"image/color"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/wicanr2/taipei/preview/internal/i18n"
	"github.com/wicanr2/taipei/preview/locales"
)

func TestRevealKeepsFinalLayoutAndBounds(t *testing.T) {
	dir := os.Getenv("TAIPEI_HD_MATERIALS")
	if dir == "" {
		t.Skip("requires fixed Noto font")
	}
	u, err := New(filepath.Join(dir, "fonts"), i18n.Bundled())
	if err != nil {
		t.Fatal(err)
	}
	safe := image.Rect(76, 644, 1272, 700)
	for _, lang := range i18n.Languages {
		frames := make([]*image.RGBA, 3)
		counts := make([]int, 3)
		for phase := 0; phase <= 2; phase++ {
			im := image.NewRGBA(image.Rect(0, 0, 1280, 800))
			if err := u.DrawReveal(im, lang, "intro.date", safe, 48, 14, phase, 2, color.White); err != nil {
				t.Fatal(err)
			}
			frames[phase] = im
			for y := 0; y < 800; y++ {
				for x := 0; x < 1280; x++ {
					if im.RGBAAt(x, y).A != 0 {
						counts[phase]++
						if !image.Pt(x, y).In(safe) {
							t.Fatal("ink escaped safe field", lang, x, y)
						}
					}
				}
			}
		}
		if counts[0] != 0 || counts[1] == 0 || counts[2] <= counts[1] {
			t.Fatal("missing reveal ink", lang, counts)
		}
		for y := safe.Min.Y; y < safe.Max.Y; y++ {
			for x := safe.Min.X; x < safe.Max.X; x++ {
				if frames[1].RGBAAt(x, y).A > frames[2].RGBAAt(x, y).A {
					t.Fatal("prefix moved when completed", lang, x, y)
				}
			}
		}
	}
	// A long external translation must preserve the original instead of clipping.
	lines := strings.Split(string(locales.Bundled), "\n")
	for i, line := range lines {
		if strings.HasPrefix(line, "intro.date\t") {
			columns := strings.Split(line, "\t")
			columns[5] = strings.Repeat("W", 1000)
			lines[i] = strings.Join(columns, "\t")
		}
	}
	c, err := i18n.Parse([]byte(strings.Join(lines, "\n")))
	if err != nil {
		t.Fatal(err)
	}
	u, err = New(filepath.Join(dir, "fonts"), c)
	if err != nil {
		t.Fatal(err)
	}
	im := image.NewRGBA(image.Rect(0, 0, 1280, 800))
	if err = u.DrawReveal(im, "en", "intro.date", safe, 48, 14, 1, 1, color.White); err == nil {
		t.Fatal("oversized text accepted")
	}
	for _, v := range im.Pix {
		if v != 0 {
			t.Fatal("failed layout partially painted")
		}
	}
}
