package hd

import (
	"bytes"
	"encoding/binary"
	"encoding/json"
	"image"
	"image/draw"
	"image/png"
	"os"
	"path/filepath"
)

// 039: sources are decoded from the original ROMs; assets own no VM pointer.
type IllustrationSource struct {
	ID, Encoding  string
	Raw, Pixels   []byte
	Width, Height int
}
type IllustrationDraw struct {
	ID          string `json:"id"`
	X, Y        int
	Clip        image.Rectangle
	Transparent bool
	Key         byte
	EA          uint32 `json:"ida_loader_linear"`
}
type illustrationStats struct {
	Painted int            `json:"painted"`
	Images  []string       `json:"images"`
	Reasons map[string]int `json:"reasons"`
}
type illustrationVariant struct {
	Palette, File, SHA string
	art                *image.RGBA
}
type illustrationAsset struct {
	ID       string
	Variants []struct {
		Palette, File string
		SHA           string `json:"sha256"`
	}
	Fields []struct {
		Rect            [4]int
		Key             string
		Background, Ink byte
	}
	variants []illustrationVariant
}
type illustrationSet struct {
	sources  map[string]IllustrationSource
	assets   map[string]*illustrationAsset
	palettes map[string][256][3]byte
	reason   string
}

const illustrationManifestSHA = "545b4f94b6454debc0de5110bab646d5e68ae19dfa126f700361cd12d9d276af"

func decodeIllustration(raw []byte, encoding string) (w, h int, pixels []byte) {
	if encoding == "iv2" {
		canvas := bytes.Repeat([]byte{255}, 64000)
		at, pos, ended := 0, 0, false
		for at+2 <= len(raw) {
			delta := int(binary.LittleEndian.Uint16(raw[at:]))
			at += 2
			if pos+delta > 65535 {
				ended = true
				break
			}
			pos += delta
			if at >= len(raw) {
				return 0, 0, nil
			}
			n := int(raw[at])
			at++
			if n == 0 || at+n > len(raw) || pos+n > len(canvas) || bytes.IndexByte(raw[at:at+n], 255) >= 0 {
				return 0, 0, nil
			}
			copy(canvas[pos:pos+n], raw[at:at+n])
			at += n
			pos += n
		}
		if !ended || at != len(raw) {
			return 0, 0, nil
		}
		for i, v := range canvas {
			if v != 255 {
				w = max(w, i%320+1)
				h = max(h, i/320+1)
			}
		}
		if w == 0 || h == 0 {
			return 0, 0, nil
		}
		for y := 0; y < h; y++ {
			pixels = append(pixels, canvas[y*320:y*320+w]...)
		}
		return
	}
	if len(raw) < 4 {
		return 0, 0, nil
	}
	w, h = int(binary.LittleEndian.Uint16(raw)), int(binary.LittleEndian.Uint16(raw[2:]))
	if w <= 0 || h <= 0 || w > 320 || h > 200 {
		return 0, 0, nil
	}
	if encoding == "raw" {
		if len(raw) != 4+w*h {
			return 0, 0, nil
		}
		return w, h, append([]byte(nil), raw[4:]...)
	}
	if encoding != "zero-color-count-candidate" {
		return 0, 0, nil
	}
	for at := 4; at < len(raw); {
		v, n := raw[at], 1
		at++
		if v == 0 {
			if at+2 > len(raw) {
				return 0, 0, nil
			}
			v, n = raw[at], int(raw[at+1])
			at += 2
		}
		if n == 0 || len(pixels)+n > w*h {
			return 0, 0, nil
		}
		pixels = append(pixels, bytes.Repeat([]byte{v}, n)...)
	}
	if len(pixels) != w*h {
		return 0, 0, nil
	}
	return
}

// InitIllustrations accepts only the sealed READY bundle and original inputs.
func (r *Renderer) InitIllustrations(exe, rom, romA []byte, dir string) (sources []IllustrationSource) {
	s := &illustrationSet{sources: map[string]IllustrationSource{}, assets: map[string]*illustrationAsset{}, reason: "illustration-input"}
	r.illustrations = s
	if digest(exe) != "798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3" || digest(rom) != romSHA || digest(romA) != "5d66f238dce650b8a407986100392ee4b8ac2aa23a033e80a7ca18ed91b3d9b0" {
		return nil
	}
	root := filepath.Join(dir, "illustrations-ready-v1")
	raw, err := os.ReadFile(filepath.Join(root, "manifest.json"))
	s.reason = "illustration-manifest"
	if err != nil || digest(raw) != illustrationManifestSHA {
		return nil
	}
	var manifest struct {
		Stage   string
		Sources []struct {
			ID, Canonical, ROM, Encoding string
			Offset                       int `json:"file_offset"`
			End, Width, Height           int
			RawSHA                       string `json:"raw_sha256"`
			PixelSHA                     string `json:"pixels_sha256"`
		}
		Palettes map[string][256][3]byte
		Images   []*illustrationAsset
	}
	if json.Unmarshal(raw, &manifest) != nil || manifest.Stage != "READY" || len(manifest.Sources) != 209 || len(manifest.Images) != 179 || len(manifest.Palettes) != 3 {
		return nil
	}
	roms := map[string][]byte{"RS201.ROM": rom, "RS201A.ROM": romA}
	for _, entry := range manifest.Sources {
		data := roms[entry.ROM]
		if entry.Offset < 0 || entry.End <= entry.Offset || entry.End > len(data) {
			return nil
		}
		original := data[entry.Offset:entry.End]
		w, h, pixels := decodeIllustration(original, entry.Encoding)
		if digest(original) != entry.RawSHA || w != entry.Width || h != entry.Height || digest(pixels) != entry.PixelSHA {
			return nil
		}
		im := IllustrationSource{entry.Canonical, entry.Encoding, original, pixels, w, h}
		sources = append(sources, im)
		if _, ok := s.sources[im.ID]; !ok {
			s.sources[im.ID] = im
		}
	}
	if len(s.sources) != 197 {
		return nil
	}
	s.palettes = manifest.Palettes
	for _, entry := range manifest.Images {
		source, ok := s.sources[entry.ID]
		if !ok || s.assets[entry.ID] != nil || len(entry.Variants) != 3 {
			return nil
		}
		for _, variant := range entry.Variants {
			v := illustrationVariant{Palette: variant.Palette, File: variant.File, SHA: variant.SHA}
			if filepath.Base(v.File) != v.File {
				return nil
			}
			data, e := os.ReadFile(filepath.Join(root, v.File))
			if e == nil && digest(data) == v.SHA {
				im, e := png.Decode(bytes.NewReader(data))
				if e == nil && im.Bounds() == image.Rect(0, 0, source.Width*4, source.Height*4) {
					v.art = image.NewRGBA(im.Bounds())
					draw.Draw(v.art, v.art.Bounds(), im, image.Point{}, draw.Src)
					for i := 3; i < len(v.art.Pix); i += 4 {
						if v.art.Pix[i] != 255 {
							v.art = nil
							break
						}
					}
				}
			}
			entry.variants = append(entry.variants, v)
		}
		s.assets[entry.ID] = entry
		if len(entry.Fields) > 0 && r.textSources != nil {
			im := TextImage{ID: source.ID, Raw: source.Raw, Pixels: source.Pixels, Width: source.Width, Height: source.Height, Transparent: true}
			for _, f := range entry.Fields {
				im.Fields = append(im.Fields, TextImageField{image.Rect(f.Rect[0], f.Rect[1], f.Rect[2], f.Rect[3]), f.Key, f.Background, f.Ink})
			}
			r.textSources.images = append(r.textSources.images, im)
		}
	}
	s.reason = ""
	return
}

func (r *Renderer) TextImageSources() []TextImage {
	if r.textSources == nil {
		return nil
	}
	return r.textSources.images
}
func (r *Renderer) SetIllustrationDraws(draws []IllustrationDraw) { r.illustrationDraws = draws }

func illustrationOwned(s IllustrationSource, d IllustrationDraw, x, y int) (byte, bool) {
	if !image.Pt(x, y).In(d.Clip) || x < d.X || y < d.Y || x >= d.X+s.Width || y >= d.Y+s.Height {
		return 0, false
	}
	v := s.Pixels[(y-d.Y)*s.Width+x-d.X]
	return v, !d.Transparent || v != d.Key
}

func (r *Renderer) paintIllustrations(dst *image.RGBA, px []byte, pal [256][3]byte, fields []preparedImageField) illustrationStats {
	r.illustrationRects = nil
	stats := illustrationStats{Reasons: map[string]int{}}
	s := r.illustrations
	if s == nil {
		stats.Reasons["illustration-uninitialized"]++
		return stats
	}
	if s.reason != "" {
		stats.Reasons[s.reason]++
		return stats
	}
	var occluded, text [64000]bool
	for _, rect := range r.lastTextRects {
		for y := rect.Min.Y; y < rect.Max.Y; y++ {
			for x := rect.Min.X; x < rect.Max.X; x++ {
				if x >= 0 && x < 320 && y >= 0 && y < 200 {
					occluded[y*320+x] = true
				}
			}
		}
	}
	for _, field := range fields {
		for y := field.native.Min.Y; y < field.native.Max.Y; y++ {
			for x := field.native.Min.X; x < field.native.Max.X; x++ {
				text[y*320+x] = true
			}
		}
	}
	for i := len(r.illustrationDraws) - 1; i >= 0; i-- {
		d := r.illustrationDraws[i]
		source, known := s.sources[d.ID]
		box := d.Clip.Intersect(image.Rect(0, 0, 320, 200))
		if known {
			box = box.Intersect(image.Rect(d.X, d.Y, d.X+source.Width, d.Y+source.Height))
		}
		if box.Empty() {
			continue
		}
		if !known {
			for y := box.Min.Y; y < box.Max.Y; y++ {
				for x := box.Min.X; x < box.Max.X; x++ {
					occluded[y*320+x] = true
				}
			}
			continue
		}
		matched, colours := true, map[byte]bool{}
		for y := box.Min.Y; y < box.Max.Y && matched; y++ {
			for x := box.Min.X; x < box.Max.X; x++ {
				v, owns := illustrationOwned(source, d, x, y)
				if !owns || occluded[y*320+x] || text[y*320+x] {
					continue
				}
				if px[y*320+x] != v {
					matched = false
					break
				}
				colours[v] = true
			}
		}
		asset := s.assets[source.ID]
		var art *image.RGBA
		reason := "illustration-source"
		if matched && len(colours) >= 2 && asset != nil {
			bound := source.ID == "a15-00" || source.ID == "a16-00" || source.ID == "a17-00" || len(asset.Fields) > 0 || len(source.ID) >= 4 && source.ID[:4] == "a10-"
			textReady := !bound || r.textSources != nil && r.locale != nil && r.locale.reason == ""
			for _, im := range r.TextImageSources() {
				if !bytes.Equal(im.Raw, source.Raw) {
					continue
				}
				for _, f := range im.Fields {
					native := f.Rect.Add(image.Pt(d.X, d.Y))
					found := false
					for _, ready := range fields {
						if ready.native == native && ready.key == f.Key {
							found = true
							break
						}
					}
					if !found {
						textReady = false
					}
				}
			}
			reason = "illustration-text"
			if textReady {
				reason = "illustration-palette"
				used := map[byte]bool{}
				for y := box.Min.Y; y < box.Max.Y; y++ {
					for x := box.Min.X; x < box.Max.X; x++ {
						if v, ok := illustrationOwned(source, d, x, y); ok {
							used[v] = true
						}
					}
				}
				for _, v := range asset.variants {
					palette, ok := s.palettes[v.Palette]
					if !ok {
						continue
					}
					compatible := true
					for index := range used {
						if pal[index] != palette[index] {
							compatible = false
							break
						}
					}
					if compatible {
						art = v.art
						reason = "illustration-asset"
						if art != nil {
							reason = "matched-illustration"
							break
						}
					}
				}
			}
		}
		// Existing UI remains above older pictures. Validated title fields are
		// transparent to the art layer; their Noto text is painted afterwards.
		title := source.ID == "a06-00" || source.ID == "a38-00"
		if art != nil {
			r.illustrationRects = append(r.illustrationRects, box)
			stats.Painted++
			stats.Images = append(stats.Images, source.ID)
		}
		if asset != nil {
			stats.Reasons[reason]++
		}
		for y := box.Min.Y; y < box.Max.Y; y++ {
			for x := box.Min.X; x < box.Max.X; x++ {
				_, owns := illustrationOwned(source, d, x, y)
				if !owns || occluded[y*320+x] {
					continue
				}
				if art != nil {
					for dy := 0; dy < 4; dy++ {
						at := ((y*4+dy)*1280 + x*4) * 4
						from := (((y-d.Y)*4+dy)*source.Width*4 + (x-d.X)*4) * 4
						copy(dst.Pix[at:at+16], art.Pix[from:from+16])
					}
				}
				if !(title && text[y*320+x]) {
					occluded[y*320+x] = true
				}
			}
		}
	}
	return stats
}
