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

// 036: only the two complete, normally constructed environmental facilities.
const publicFacilitiesManifestSHA = "07319733ab01743a8e2e30cec7e6e042554b35982bf342ba556f21d84c2892e1"

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
}

type publicFacilitySet struct {
	tiles   map[[81]byte]*publicFacilityTile
	palette [256][3]byte
	atlases map[string]*image.RGBA
	reason  string
}

func loadPublicFacilities(rom []byte, dir string) *publicFacilitySet {
	u := &publicFacilitySet{tiles: map[[81]byte]*publicFacilityTile{}, atlases: map[string]*image.RGBA{}, reason: "manifest-mismatch"}
	if digest(rom) != romSHA {
		return u
	}
	off := int(binary.LittleEndian.Uint32(rom[18+37*16:]))
	n := int(binary.LittleEndian.Uint16(rom[22+37*16:]))
	lib := rom[off : off+n]
	if n != 8354 || binary.LittleEndian.Uint16(lib) != 96 {
		return u
	}
	byID := map[string]map[[2]int]*publicFacilityTile{}
	for _, definition := range []struct {
		id    string
		start int
	}{{"waste", 12}, {"sewage", 16}} {
		byID[definition.id] = map[[2]int]*publicFacilityTile{}
		for row := 0; row < 4; row++ {
			for col := 0; col < 4; col++ {
				index := definition.start + row*24 + col
				a := int(binary.LittleEndian.Uint16(lib[2+index*2:]))
				b := int(binary.LittleEndian.Uint16(lib[4+index*2:]))
				if b-a != 85 || binary.LittleEndian.Uint16(lib[a:]) != 9 || binary.LittleEndian.Uint16(lib[a+2:]) != 9 {
					return u
				}
				var source [81]byte
				copy(source[:], lib[a+4:b])
				if u.tiles[source] != nil {
					return u
				}
				tile := &publicFacilityTile{id: definition.id, col: col, row: row, image: index, pixel: off + a + 4, sourceSHA: digest(source[:])}
				for i := 0; i < 256; i++ {
					if bytes.Contains(source[:], []byte{byte(i)}) {
						tile.used = append(tile.used, byte(i))
					}
				}
				u.tiles[source], byID[definition.id][[2]int{col, row}] = tile, tile
			}
		}
	}
	root := filepath.Join(dir, "public-facilities-ready-v1")
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
	if json.Unmarshal(raw, &manifest) != nil || manifest.Schema != 1 || manifest.Stage != "public" || manifest.ROMSHA != romSHA || manifest.Tiles != 32 || manifest.UniqueSources != 32 || len(manifest.Facilities) != 2 {
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
		if byID[facility.ID] == nil || seen[facility.ID] || facility.Size != [2]int{4, 4} || facility.Atlas != facility.ID+".png" || len(facility.Tiles) != 16 {
			return u
		}
		seen[facility.ID] = true
		cells := map[[2]int]bool{}
		for _, record := range facility.Tiles {
			tile := byID[facility.ID][record.Cell]
			if tile == nil || cells[record.Cell] || record.SourceSHA != tile.sourceSHA || !bytes.Equal(record.Used, tile.used) || len(record.Sources) != 1 {
				return u
			}
			cells[record.Cell] = true
			source := record.Sources[0]
			if source.Member != 37 || source.Image != tile.image || source.Pixel != tile.pixel {
				return u
			}
		}
		raw, err := os.ReadFile(filepath.Join(root, facility.Atlas))
		if err != nil || digest(raw) != facility.SHA {
			continue
		}
		im, err := png.Decode(bytes.NewReader(raw))
		if err != nil || im.Bounds() != image.Rect(0, 0, 144, 144) {
			continue
		}
		atlas := image.NewRGBA(im.Bounds())
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
	u.reason = ""
	return u
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
