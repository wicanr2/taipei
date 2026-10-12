package localui

import (
	"bytes"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/wicanr2/taipei/preview/internal/i18n"
	"github.com/wicanr2/taipei/preview/locales"
)

func TestRealPickerLanguagesAndResourceFailures(t *testing.T) {
	dir := os.Getenv("TAIPEI_HD_MATERIALS")
	if dir == "" {
		t.Skip("set TAIPEI_HD_MATERIALS")
	}
	dir = filepath.Join(dir, "fonts")
	u, err := New(dir, i18n.Bundled())
	if err != nil {
		t.Fatal(err)
	}
	for _, language := range i18n.Languages {
		for _, warning := range []string{"", "locale.error.settings", "locale.error.catalog"} {
			im, err := u.Picker(language, 4, warning)
			if err != nil {
				t.Fatal(language, warning, err)
			}
			ink := 0
			for y := 0; y < 800; y++ {
				for x := 0; x < 1280; x++ {
					c := im.RGBAAt(x, y)
					if c.A != 0 && (x < 320 || x >= 960 || y < 90 || y >= 718) {
						t.Fatal("overlay leaked", x, y)
					}
					if c.R > 200 && c.G > 200 && c.B > 200 {
						ink++
					}
				}
			}
			if ink < 1000 {
				t.Fatal("missing picker ink", language, warning, ink)
			}
		}
	}
	missing := bytes.Replace(locales.Bundled, []byte("\tExit\n"), []byte("\tExit \u0378\n"), 1)
	c, err := i18n.Parse(missing)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := New(dir, c); err == nil || !strings.Contains(err.Error(), "font-glyph") {
		t.Fatal("missing glyph not rejected", err)
	}
	if _, err := New(t.TempDir(), i18n.Bundled()); err == nil {
		t.Fatal("missing font accepted")
	}
	badLicense := t.TempDir()
	if err := os.Symlink(filepath.Join(dir, "NotoSansCJKtc-Regular.otf"), filepath.Join(badLicense, "NotoSansCJKtc-Regular.otf")); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(badLicense, "LICENSE"), []byte("invalid"), 0600); err != nil {
		t.Fatal(err)
	}
	if _, err := New(badLicense, i18n.Bundled()); err == nil || err.Error() != "font-license-mismatch" {
		t.Fatal("bad license accepted", err)
	}
}
