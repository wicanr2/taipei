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
	"strconv"
)

// 036 v2: twelve complete, normally constructed facilities; presentation only.
const publicFacilitiesManifestSHA = "cbbb76d9a14f71f540e310a073492c5b43f58b6a13ff3f99c081d55064ed1f32"

type publicFacilityStats struct {
	Matched    int            `json:"matched"`
	Painted    int            `json:"painted"`
	Fallback   int            `json:"fallback"`
	Facilities map[string]int `json:"facilities,omitempty"`
	Reasons    map[string]int `json:"reasons,omitempty"`
}

type publicFacilityTile struct {
	id        string
	col, row  int
	image     int
	pixel     int
	sourceSHA string
	used      []byte
	source    [81]byte
}

type publicFacilitySet struct {
	tiles      map[[81]byte]*publicFacilityTile
	variants   map[[81]byte][]*publicFacilityTile
	facilities map[string][]*publicFacilityTile
	palette    [256][3]byte
	atlases    map[string]*image.RGBA
	reason     string
}

// Read each alias through the actual ROM archive table, never a guessed stride.
func publicSource(rom []byte, member, index, pixel int) ([81]byte, bool) {
	var source [81]byte
	if len(rom) < 2 || member < 0 || member >= int(binary.LittleEndian.Uint16(rom)) {
		return source, false
	}
	header := 18 + member*16
	if header+6 > len(rom) {
		return source, false
	}
	off := int(binary.LittleEndian.Uint32(rom[header:]))
	n := int(binary.LittleEndian.Uint16(rom[header+4:]))
	if n < 4 || off < 0 || off+n > len(rom) {
		return source, false
	}
	lib := rom[off : off+n]
	count := int(binary.LittleEndian.Uint16(lib))
	if index < 0 || index >= count || 2+count*2 > len(lib) {
		return source, false
	}
	a := int(binary.LittleEndian.Uint16(lib[2+index*2:]))
	b := len(lib)
	if index+1 < count {
		b = int(binary.LittleEndian.Uint16(lib[4+index*2:]))
	}
	if a < 2+count*2 || b > len(lib) || b-a != 85 || pixel != off+a+4 || binary.LittleEndian.Uint16(lib[a:]) != 9 || binary.LittleEndian.Uint16(lib[a+2:]) != 9 {
		return source, false
	}
	copy(source[:], lib[a+4:b])
	return source, true
}

func loadPublicFacilities(rom []byte, dir string) *publicFacilitySet {
	u := &publicFacilitySet{tiles: map[[81]byte]*publicFacilityTile{}, variants: map[[81]byte][]*publicFacilityTile{}, facilities: map[string][]*publicFacilityTile{}, atlases: map[string]*image.RGBA{}, reason: "manifest-mismatch"}
	if digest(rom) != romSHA {
		return u
	}
	root := filepath.Join(dir, "public-facilities-ready-v2")
	raw, err := os.ReadFile(filepath.Join(root, "manifest.json"))
	if err != nil || digest(raw) != publicFacilitiesManifestSHA {
		return u
	}
	var manifest struct {
		Schema        int
		Stage         string
		ROMSHA        string `json:"rom_sha256"`
		Tiles         int
		UniqueSources int `json:"unique_sources"`
		Palette       map[string][3]byte
		Facilities    []struct {
			ID    string
			Size  [2]int
			Atlas string
			SHA   string `json:"sha256"`
			Tiles []struct {
				Cell      [2]int
				SourceSHA string `json:"source_sha256"`
				Used      []byte `json:"used_colors"`
				Sources   []struct {
					Member int
					Image  int
					Pixel  int `json:"pixel_file_offset"`
				}
			}
		}
	}
	expected := map[string][2]int{"waste": {4, 4}, "sewage": {4, 4}}
	for _, id := range []string{"sun-yat-sen", "chiang-kai-shek", "palace-museum", "february-28", "art-museum", "amusement-park", "stadium", "confucius-temple", "zoo", "baseball-dome"} {
		expected[id] = [2]int{6, 6}
	}
	if json.Unmarshal(raw, &manifest) != nil || manifest.Schema != 1 || manifest.Stage != "public" || manifest.ROMSHA != romSHA || manifest.Tiles != 392 || manifest.UniqueSources != 391 || len(manifest.Facilities) != len(expected) {
		return u
	}
	for key, color := range manifest.Palette {
		index, err := strconv.Atoi(key)
		if err != nil || index < 0 || index > 255 {
			return u
		}
		u.palette[index] = color
	}
	seen := map[string]bool{}
	for _, facility := range manifest.Facilities {
		size, ok := expected[facility.ID]
		if !ok || seen[facility.ID] || facility.Size != size || facility.Atlas != facility.ID+".png" || len(facility.Tiles) != size[0]*size[1] {
			return u
		}
		seen[facility.ID] = true
		cells := map[[2]int]bool{}
		for _, record := range facility.Tiles {
			x, y := record.Cell[0], record.Cell[1]
			if x < 0 || x >= size[0] || y < 0 || y >= size[1] || cells[record.Cell] || len(record.Sources) == 0 {
				return u
			}
			cells[record.Cell] = true
			first := record.Sources[0]
			source, ok := publicSource(rom, first.Member, first.Image, first.Pixel)
			if !ok || digest(source[:]) != record.SourceSHA {
				return u
			}
			for _, alias := range record.Sources {
				same, ok := publicSource(rom, alias.Member, alias.Image, alias.Pixel)
				if !ok || same != source {
					return u
				}
			}
			tile := &publicFacilityTile{id: facility.ID, col: x, row: y, image: first.Image, pixel: first.Pixel, sourceSHA: record.SourceSHA, source: source}
			for i := 0; i < 256; i++ {
				if bytes.Contains(source[:], []byte{byte(i)}) {
					if _, ok := manifest.Palette[strconv.Itoa(i)]; !ok {
						return u
					}
					tile.used = append(tile.used, byte(i))
				}
			}
			if !bytes.Equal(tile.used, record.Used) {
				return u
			}
			if u.tiles[source] == nil {
				u.tiles[source] = tile
			}
			u.variants[source] = append(u.variants[source], tile)
			u.facilities[facility.ID] = append(u.facilities[facility.ID], tile)
		}
		raw, err := os.ReadFile(filepath.Join(root, facility.Atlas))
		if err != nil || digest(raw) != facility.SHA {
			continue
		}
		im, err := png.Decode(bytes.NewReader(raw))
		bounds := image.Rect(0, 0, size[0]*36, size[1]*36)
		if err != nil || im.Bounds() != bounds {
			continue
		}
		atlas := image.NewRGBA(bounds)
		draw.Draw(atlas, atlas.Bounds(), im, im.Bounds().Min, draw.Src)
		opaque := true
		for i := 3; i < len(atlas.Pix); i += 4 {
			if atlas.Pix[i] != 255 {
				opaque = false
				break
			}
		}
		if opaque {
			u.atlases[facility.ID] = atlas
		}
	}
	if len(u.tiles) != manifest.UniqueSources {
		return u
	}
	u.reason = ""
	return u
}

// A shared original tile is positioned only by exact visible unique neighbors.
func (u *publicFacilitySet) resolve(source [81]byte, frame []byte, col, row int) (*publicFacilityTile, string) {
	if len(u.variants[source]) <= 1 {
		return u.tiles[source], ""
	}
	if u.reason != "" {
		return nil, u.reason
	}
	if len(frame) != 320*200 {
		return nil, "source-ambiguous"
	}
	var chosen *publicFacilityTile
	for _, candidate := range u.variants[source] {
		anchors, valid := 0, true
		for _, neighbor := range u.facilities[candidate.id] {
			if len(u.variants[neighbor.source]) != 1 {
				continue
			}
			x, y := col+neighbor.col-candidate.col, row+neighbor.row-candidate.row
			if x < 0 || x >= 29 || y < 0 || y >= 15 {
				continue
			}
			anchors++
			var actual [81]byte
			for dy := 0; dy < 9; dy++ {
				copy(actual[dy*9:], frame[(34+y*9+dy)*320+5+x*9:(34+y*9+dy)*320+14+x*9])
			}
			if actual != neighbor.source {
				valid = false
				break
			}
		}
		if valid && anchors > 0 {
			if chosen != nil {
				return nil, "source-ambiguous"
			}
			chosen = candidate
		}
	}
	if chosen == nil {
		return nil, "neighbors-mismatch"
	}
	return chosen, ""
}

func (u *publicFacilitySet) paint(dst *image.RGBA, tile *publicFacilityTile, pal [256][3]byte, col, row int) string {
	if u.reason != "" {
		return u.reason
	}
	atlas := u.atlases[tile.id]
	if atlas == nil {
		return "atlas-mismatch"
	}
	for _, index := range tile.used {
		if pal[index] != u.palette[index] {
			return "palette-mismatch"
		}
	}
	draw.Draw(dst, image.Rect(20+col*36, 136+row*36, 56+col*36, 172+row*36), atlas, image.Pt(tile.col*36, tile.row*36), draw.Src)
	return "matched-public-facility"
}
