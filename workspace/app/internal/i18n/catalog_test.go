package i18n

import (
	"bytes"
	"os"
	"path/filepath"
	"testing"

	"github.com/wicanr2/taipei/preview/locales"
)

func TestExternalEditsAndFallback(t *testing.T) {
	path := filepath.Join(t.TempDir(), "ui.tsv")
	raw := bytes.Replace(locales.Bundled, []byte("\tExit\n"), []byte("\tLeave city\n"), 1)
	if err := os.WriteFile(path, raw, 0600); err != nil {
		t.Fatal(err)
	}
	c, err := Load(path)
	if err != nil || c.Source != "external-tsv" || c.Get("en", "menu.exit") != "Leave city" {
		t.Fatal(c, err)
	}
	if err := os.WriteFile(path, []byte{0xff}, 0600); err != nil {
		t.Fatal(err)
	}
	c, err = Load(path)
	if err == nil || c.Source != "bundled-tsv" || c.Get("en", "menu.exit") != "Exit" {
		t.Fatal(c, err)
	}
	if c.Get("invalid", "menu.exit") != "離開" || c.Get("en", "unknown.key") != "unknown.key" {
		t.Fatal("catalog-only fallback failed")
	}
}

func TestMalformedCatalogs(t *testing.T) {
	lines := bytes.Split(locales.Bundled, []byte{'\n'})
	cases := map[string][]byte{
		"duplicate":   append(append([]byte{}, locales.Bundled...), append(lines[1], '\n')...),
		"missing":     bytes.Replace(locales.Bundled, []byte("\tExit\n"), []byte("\t\n"), 1),
		"columns":     bytes.Replace(locales.Bundled, []byte("\tExit\n"), []byte("\n"), 1),
		"placeholder": bytes.Replace(locales.Bundled, []byte("\tExit\n"), []byte("\tExit {name}\n"), 1),
		"utf8":        {0xff},
		"control":     bytes.Replace(locales.Bundled, []byte("\tExit\n"), []byte("\tEx\x01it\n"), 1),
	}
	for name, raw := range cases {
		t.Run(name, func(t *testing.T) {
			if _, err := Parse(raw); err == nil {
				t.Fatal("malformed catalog accepted")
			}
		})
	}
}

func TestFrontendSettingsDoNotTouchSave(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, "frontend-settings.json")
	save := filepath.Join(dir, "CITY.SAV")
	original := []byte{0, 1, 2, 0xff}
	if err := os.WriteFile(save, original, 0600); err != nil {
		t.Fatal(err)
	}
	if language, err := ReadSettings(path); err != nil || language != Default {
		t.Fatal(language, err)
	}
	for _, language := range Languages {
		if err := SaveSettings(path, language); err != nil {
			t.Fatal(err)
		}
		if got, err := ReadSettings(path); err != nil || got != language {
			t.Fatal(got, err)
		}
	}
	if err := SaveSettings(path, "../../bad"); err == nil {
		t.Fatal("invalid language accepted")
	}
	if err := SaveSettings(filepath.Join(dir, "missing", "settings.json"), "ja"); err == nil {
		t.Fatal("write failure hidden")
	}
	if err := os.WriteFile(path, []byte(`{"schema":1,"language":"invalid"}`), 0600); err != nil {
		t.Fatal(err)
	}
	if got, err := ReadSettings(path); err == nil || got != Default {
		t.Fatal(got, err)
	}
	got, err := os.ReadFile(save)
	if err != nil || !bytes.Equal(got, original) {
		t.Fatal("SAV modified", err)
	}
	entries, err := os.ReadDir(dir)
	if err != nil || len(entries) != 2 {
		t.Fatal("temporary settings leaked", entries, err)
	}
}
