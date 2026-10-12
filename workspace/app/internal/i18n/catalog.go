// Package i18n owns display text and frontend settings, never DOS identifiers.
package i18n

import (
	"bytes"
	"crypto/sha256"
	"encoding/csv"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
	"unicode"
	"unicode/utf8"

	"github.com/wicanr2/taipei/preview/locales"
)

const Default = "zh-Hant"

var Languages = [...]string{"zh-Hant", "zh-Hans", "ja", "ko", "en"}
var keyPattern = regexp.MustCompile(`^[a-zA-Z][a-zA-Z0-9_.-]*$`)
var placeholders = regexp.MustCompile(`\{[a-zA-Z][a-zA-Z0-9_]*\}`)

type Catalog struct {
	rows   map[string][5]string
	SHA    string
	Source string
}

func Index(language string) int {
	for i, lang := range Languages {
		if lang == language {
			return i
		}
	}
	return -1
}

func Parse(raw []byte) (*Catalog, error) {
	if !utf8.Valid(raw) || bytes.HasPrefix(raw, []byte{0xef, 0xbb, 0xbf}) {
		return nil, fmt.Errorf("catalog-utf8")
	}
	r := csv.NewReader(bytes.NewReader(raw))
	r.Comma = '\t'
	r.FieldsPerRecord = 6
	header, err := r.Read()
	if err != nil {
		return nil, err
	}
	if strings.Join(header, "\t") != "key\t"+strings.Join(Languages[:], "\t") {
		return nil, fmt.Errorf("catalog-header")
	}
	c := &Catalog{rows: map[string][5]string{}, SHA: fmt.Sprintf("%x", sha256.Sum256(raw))}
	for {
		row, err := r.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			return nil, err
		}
		key := row[0]
		if !keyPattern.MatchString(key) {
			return nil, fmt.Errorf("catalog-key:%s", key)
		}
		if _, ok := c.rows[key]; ok {
			return nil, fmt.Errorf("catalog-duplicate:%s", key)
		}
		var cols [5]string
		var signature string
		for i, text := range row[1:] {
			if strings.TrimSpace(text) == "" {
				return nil, fmt.Errorf("catalog-missing:%s/%s", key, Languages[i])
			}
			for _, ch := range text {
				if unicode.IsControl(ch) {
					return nil, fmt.Errorf("catalog-control:%s", key)
				}
			}
			p := placeholders.FindAllString(text, -1)
			sort.Strings(p)
			s := strings.Join(p, " ")
			if i == 0 {
				signature = s
			} else if s != signature {
				return nil, fmt.Errorf("catalog-placeholder:%s", key)
			}
			cols[i] = text
		}
		c.rows[key] = cols
	}
	if len(c.rows) == 0 {
		return nil, fmt.Errorf("catalog-empty")
	}
	return c, nil
}

func Bundled() *Catalog {
	c, err := Parse(locales.Bundled)
	if err != nil {
		panic(err)
	}
	c.Source = "bundled-tsv"
	return c
}

// An external catalog allows editing text without recompilation. Invalid input
// falls back to the same TSV bundled at build time, with a caller-visible error.
func Load(path string) (*Catalog, error) {
	if path == "" {
		exe, err := os.Executable()
		if err != nil {
			return Bundled(), err
		}
		path = filepath.Join(filepath.Dir(exe), "locales", "ui.tsv")
	}
	raw, err := os.ReadFile(path)
	if err == nil {
		var c *Catalog
		c, err = Parse(raw)
		if err == nil {
			c.Source = "external-tsv"
			return c, nil
		}
	}
	return Bundled(), err
}

func (c *Catalog) Get(language, key string) string {
	row, ok := c.rows[key]
	if !ok {
		return key
	}
	i := Index(language)
	if i < 0 || row[i] == "" {
		return row[0]
	}
	return row[i]
}

func (c *Catalog) Require(keys ...string) error {
	for _, key := range keys {
		if _, ok := c.rows[key]; !ok {
			return fmt.Errorf("catalog-required:%s", key)
		}
	}
	return nil
}

func (c *Catalog) Texts() []string {
	var result []string
	for _, row := range c.rows {
		result = append(result, row[:]...)
	}
	return result
}
