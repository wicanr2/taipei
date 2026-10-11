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

// 027：只呈現已見火力靜態來源，不推導建物、動畫或供電規則。
const powerFacilityManifestSHA = "bd571fa7a9ca49cbc8de1adde54cf1aa64642db4ff29bf158a567a75ca027c11"

type powerFacilityStats struct {
	Matched  int            `json:"matched"`
	Painted  int            `json:"painted"`
	Fallback int            `json:"fallback"`
	Images   map[int]int    `json:"images,omitempty"`
	Reasons  map[string]int `json:"reasons,omitempty"`
}

type powerFacilityTile struct {
	image, col, row int
	used            []byte
}

type powerFacilitySet struct {
	tiles   map[[81]byte]*powerFacilityTile
	palette [256][3]byte
	atlas   *image.RGBA
	reason  string
}

func loadPowerFacilities(rom []byte, dir string) *powerFacilitySet {
	u := &powerFacilitySet{tiles: map[[81]byte]*powerFacilityTile{}, reason: "manifest-mismatch"}
	if digest(rom) != romSHA {
		return u
	}
	off := int(binary.LittleEndian.Uint32(rom[18+38*16:]))
	n := int(binary.LittleEndian.Uint16(rom[22+38*16:]))
	lib := rom[off : off+n]
	if n != 15662 || binary.LittleEndian.Uint16(lib) != 180 {
		return u
	}
	byImage := map[int]*powerFacilityTile{}
	for row := 0; row < 6; row++ {
		for col := 0; col < 6; col++ {
			index := 12 + row*30 + col
			a := int(binary.LittleEndian.Uint16(lib[2+index*2:]))
			b := int(binary.LittleEndian.Uint16(lib[4+index*2:]))
			if b-a != 85 || binary.LittleEndian.Uint16(lib[a:]) != 9 || binary.LittleEndian.Uint16(lib[a+2:]) != 9 {
				return u
			}
			var source [81]byte
			copy(source[:], lib[a+4:b])
			tile := &powerFacilityTile{image: index, col: col, row: row}
			var used [256]bool
			for _, index := range source {
				used[index] = true
			}
			for i, present := range used {
				if present {
					tile.used = append(tile.used, byte(i))
				}
			}
			u.tiles[source], byImage[index] = tile, tile
		}
	}
	root := filepath.Join(dir, "power-facility-ready-v1")
	raw, err := os.ReadFile(filepath.Join(root, "manifest.json"))
	if err != nil || digest(raw) != powerFacilityManifestSHA {
		return u
	}
	var manifest struct {
		Schema   int
		Stage    string
		ROMSHA   string `json:"rom_sha256"`
		Atlas    string
		AtlasSHA string `json:"atlas_sha256"`
		Size     [2]int `json:"atlas_size"`
		Palette  map[string][3]byte
		Sources  []struct {
			Image     int
			Cell      [2]int
			SourceSHA string `json:"source_sha256"`
			Used      []byte `json:"used_colors"`
		}
	}
	if json.Unmarshal(raw, &manifest) != nil || manifest.Schema != 1 || manifest.Stage != "thermal36" || manifest.ROMSHA != romSHA || manifest.Atlas != "thermal.png" || manifest.Size != [2]int{216, 216} || len(manifest.Sources) != 36 {
		return u
	}
	for key, color := range manifest.Palette {
		index, err := strconv.Atoi(key)
		if err != nil || index < 0 || index > 255 {
			return u
		}
		u.palette[index] = color
	}
	seen := map[int]bool{}
	for _, record := range manifest.Sources {
		tile := byImage[record.Image]
		if tile == nil || seen[record.Image] || record.Cell != [2]int{tile.col, tile.row} || !bytes.Equal(record.Used, tile.used) {
			return u
		}
		seen[record.Image] = true
		a := int(binary.LittleEndian.Uint16(lib[2+record.Image*2:]))
		if digest(lib[a+4:a+85]) != record.SourceSHA {
			return u
		}
	}
	u.reason = "atlas-mismatch"
	raw, err = os.ReadFile(filepath.Join(root, manifest.Atlas))
	if err != nil || digest(raw) != manifest.AtlasSHA {
		return u
	}
	im, err := png.Decode(bytes.NewReader(raw))
	if err != nil || im.Bounds() != image.Rect(0, 0, 216, 216) {
		return u
	}
	atlas := image.NewRGBA(im.Bounds())
	draw.Draw(atlas, atlas.Bounds(), im, im.Bounds().Min, draw.Src)
	for i := 3; i < len(atlas.Pix); i += 4 {
		if atlas.Pix[i] != 255 {
			return u
		}
	}
	u.atlas, u.reason = atlas, ""
	return u
}

func (u *powerFacilitySet) paint(dst *image.RGBA, tile *powerFacilityTile, pal [256][3]byte, col, row int) string {
	if u.reason != "" {
		return u.reason
	}
	for _, index := range tile.used {
		if pal[index] != u.palette[index] {
			return "palette-mismatch"
		}
	}
	draw.Draw(dst, image.Rect(20+col*36, 136+row*36, 56+col*36, 172+row*36), u.atlas, image.Pt(tile.col*36, tile.row*36), draw.Src)
	return "matched-power-facility"
}
