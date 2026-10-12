// Package locales carries the fallback catalog from the single TSV source.
package locales

import _ "embed"

//go:embed ui.tsv
var Bundled []byte
