package hd

import (
	"bytes"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"image"
	"image/draw"
	"image/png"
	"os"
	"path/filepath"
	"strconv"
)

// 034: exact observed source tiles only; construction and growth stay in DOS.
const cityBuildingsManifestSHA = "7dc484798f0d65962d35db56a33ac3153c7f65fb105daef3a28351018d6030e2"

type cityBuildingStats struct {
	Matched  int            `json:"matched"`
	Painted  int            `json:"painted"`
	Fallback int            `json:"fallback"`
	Images   map[string]int `json:"images,omitempty"`
	Reasons  map[string]int `json:"reasons,omitempty"`
}

type cityBuildingTile struct {
	member, image, col, row int
	used                    []byte
}

type cityBuildingSet struct {
	tiles   map[[81]byte]*cityBuildingTile
	palette [256][3]byte
	atlases map[int]*image.RGBA
	reason  string
}

func loadCityBuildings(rom []byte, dir string) *cityBuildingSet {
	u := &cityBuildingSet{tiles: map[[81]byte]*cityBuildingTile{}, atlases: map[int]*image.RGBA{}, reason: "manifest-mismatch"}
	if digest(rom) != romSHA {
		return u
	}
	byID := map[string]*cityBuildingTile{}
	for _, member := range []int{34, 35, 36} {
		off := int(binary.LittleEndian.Uint32(rom[18+member*16:]))
		n := int(binary.LittleEndian.Uint16(rom[22+member*16:]))
		lib := rom[off : off+n]
		if n != 8354 || binary.LittleEndian.Uint16(lib) != 96 {
			return u
		}
		for row := 0; row < 4; row++ {
			for col := 0; col < 4; col++ {
				index := 4 + row*24 + col
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
				tile := &cityBuildingTile{member: member, image: index, col: col, row: row}
				for i := 0; i < 256; i++ {
					if bytes.Contains(source[:], []byte{byte(i)}) {
						tile.used = append(tile.used, byte(i))
					}
				}
				u.tiles[source], byID[fmt.Sprintf("%d/%d", member, index)] = tile, tile
			}
		}
	}
	root := filepath.Join(dir, "disaster-buildings-ready-v1")
	raw, err := os.ReadFile(filepath.Join(root, "manifest.json"))
	if err != nil || digest(raw) != cityBuildingsManifestSHA {
		return u
	}
	var manifest struct {
		Schema    int
		Stage     string
		ROMSHA    string `json:"rom_sha256"`
		AtlasSize [2]int `json:"atlas_size"`
		Palette   map[string][3]byte
		Atlases   map[string]struct {
			File string
			SHA  string `json:"sha256"`
		}
		Sources []struct {
			Member    int
			Image     int
			Cell      [2]int
			SourceSHA string `json:"source_sha256"`
			Used      []byte `json:"used_colors"`
		}
	}
	if json.Unmarshal(raw, &manifest) != nil || manifest.Schema != 1 || manifest.Stage != "disaster48" || manifest.ROMSHA != romSHA || manifest.AtlasSize != [2]int{144, 144} || len(manifest.Sources) != 48 || len(manifest.Atlases) != 3 {
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
	for _, record := range manifest.Sources {
		id := fmt.Sprintf("%d/%d", record.Member, record.Image)
		tile := byID[id]
		if tile == nil || seen[id] || record.Cell != [2]int{tile.col, tile.row} || !bytes.Equal(record.Used, tile.used) {
			return u
		}
		seen[id] = true
		off := int(binary.LittleEndian.Uint32(rom[18+record.Member*16:]))
		a := int(binary.LittleEndian.Uint16(rom[off+2+record.Image*2:]))
		if digest(rom[off+a+4:off+a+85]) != record.SourceSHA {
			return u
		}
	}
	for _, member := range []int{34, 35, 36} {
		asset, ok := manifest.Atlases[strconv.Itoa(member)]
		if !ok || asset.File != fmt.Sprintf("%d.png", member) {
			return u
		}
		raw, err := os.ReadFile(filepath.Join(root, asset.File))
		if err != nil || digest(raw) != asset.SHA {
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
			u.atlases[member] = atlas
		}
	}
	u.reason = ""
	return u
}

func (u *cityBuildingSet) paint(dst *image.RGBA, tile *cityBuildingTile, pal [256][3]byte, col, row int) string {
	if u.reason != "" {
		return u.reason
	}
	atlas := u.atlases[tile.member]
	if atlas == nil {
		return "atlas-mismatch"
	}
	for _, index := range tile.used {
		if pal[index] != u.palette[index] {
			return "palette-mismatch"
		}
	}
	draw.Draw(dst, image.Rect(20+col*36, 136+row*36, 56+col*36, 172+row*36), atlas, image.Pt(tile.col*36, tile.row*36), draw.Src)
	return "matched-city-building"
}
