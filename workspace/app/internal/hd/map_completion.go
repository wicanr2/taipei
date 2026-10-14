package hd

import (
	"bytes"
	"encoding/json"
	"image"
	"image/color"
	"image/draw"
	"image/png"
	"os"
	"path/filepath"
	"strconv"
)

// 038：來源身份與呈現資料。此層不解讀城市、成長或連接規則。
const mapComplexSHA = "559fb204323da6838a5167b93f3d711cf4f46d962d03a4c111668367b5618489"
const mapZonesSHA = "e2af961d4d73ea89304faf105edbbea6cb6066de326e8705997d3e62520e8fd4"
const mapDetailSHA = "b115c09937401d34bcd1ab65b717fef4a73e9031b7c6da68a4c0983d2b9f5cb7"

var mapComplexIDs = []string{"m34-b08", "m34-b12", "m34-b16", "m34-b20", "m35-b08", "m35-b12", "m35-b16", "m35-b20", "m36-b08", "m36-b12", "m36-b16", "m36-b20", "m37-b08"}
var mapZoneKeys = map[string]string{"m34-b00": "map.zone.residential", "m35-b00": "map.zone.commercial", "m36-b00": "map.zone.industrial"}

type mapCompletionStats struct {
	Complex publicFacilityStats `json:"complex"`
	Zones   publicFacilityStats `json:"zones"`
	Detail  infrastructureStats `json:"detail"`
	Blank   int                 `json:"blank_placeholders"`
}

func loadMapAtlases(rom []byte, dir string, zones bool) *publicFacilitySet {
	ids, kind, seal, total, unique := mapComplexIDs, "complex", mapComplexSHA, 208, 207
	if zones {
		ids, kind, seal, total, unique = []string{"m34-b00", "m35-b00", "m36-b00"}, "zones", mapZonesSHA, 48, 36
	}
	expected := map[string][2]int{}
	for _, id := range ids {
		expected[id] = [2]int{4, 4}
	}
	return loadFacilityAtlases(rom, dir, filepath.Join("map-completion-ready-v1", kind), seal, "map-"+kind, total, unique, expected)
}

func (r *Renderer) prepareMapZones() string {
	base := r.mapZonesBase
	u := *base
	u.atlases = map[string]*image.RGBA{}
	r.mapZones = &u
	if base.reason != "" {
		return base.reason
	}
	if r.locale == nil || r.locale.reason != "" || r.locale.ui == nil {
		u.reason = "map-zone-font"
		return u.reason
	}
	for id, original := range base.atlases {
		atlas := localeClone(original)
		if err := r.locale.ui.DrawCompact(atlas, r.locale.language, mapZoneKeys[id], image.Rect(44, 44, 108, 100), 52, 24, color.White); err != nil {
			u.reason = "map-zone-ink"
			return u.reason
		}
		u.atlases[id] = atlas
	}
	return ""
}

// Identical HD crops need no position guess. Different crops require anchors.
func resolveMapTile(u *publicFacilitySet, source [81]byte, frame []byte, col, row int) (*publicFacilityTile, string) {
	variants := u.variants[source]
	if u.reason == "" && len(variants) > 1 {
		first := variants[0]
		reference := u.atlases[first.id]
		identical := reference != nil
		for _, tile := range variants[1:] {
			atlas := u.atlases[tile.id]
			if atlas == nil {
				identical = false
				break
			}
			for y := 0; y < 36 && identical; y++ {
				a, b := reference.PixOffset(first.col*36, first.row*36+y), atlas.PixOffset(tile.col*36, tile.row*36+y)
				if !bytes.Equal(reference.Pix[a:a+144], atlas.Pix[b:b+144]) {
					identical = false
				}
			}
		}
		if identical {
			return first, ""
		}
	}
	return u.resolve(source, frame, col, row)
}

func loadMapDetail(rom []byte, dir string) *infrastructureSet {
	u := &infrastructureSet{tiles: map[[81]byte]*infrastructureTile{}, textures: map[string]*image.RGBA{}, water: true}
	if digest(rom) != romSHA {
		return u
	}
	root := filepath.Join(dir, "map-completion-ready-v1", "detail")
	raw, err := os.ReadFile(filepath.Join(root, "manifest.json"))
	if err != nil || digest(raw) != mapDetailSHA {
		return u
	}
	var m struct {
		Schema    int
		Stage     string
		ROMSHA    string `json:"rom_sha256"`
		Geometry  int    `json:"geometry_version"`
		Frequency int    `json:"asphalt_frequency"`
		Size      int    `json:"material_size"`
		Palette   map[string][3]byte
		Materials map[string]string
		Sources   []struct {
			ID         string
			SHA        string `json:"source_sha256"`
			IndicesSHA string `json:"indices_sha256"`
			WeightsSHA string `json:"weights_sha256"`
			Used       []byte `json:"used_colors"`
			Sources    []struct {
				Member, Image int
				Pixel         int `json:"pixel_file_offset"`
			}
		}
	}
	if json.Unmarshal(raw, &m) != nil || m.Schema != 1 || m.Stage != "map-detail" || m.ROMSHA != romSHA || m.Geometry != 3 || m.Frequency != 4 || m.Size != materialSize || len(m.Sources) != 58 {
		return u
	}
	for key, value := range m.Palette {
		n, e := strconv.Atoi(key)
		if e != nil || n < 0 || n > 255 {
			return u
		}
		u.palette[n] = value
	}
	for _, record := range m.Sources {
		if len(record.Sources) == 0 || filepath.Base(record.ID) != record.ID {
			return u
		}
		v := record.Sources[0]
		source, ok := publicSource(rom, v.Member, v.Image, v.Pixel)
		if !ok || digest(source[:]) != record.SHA || u.tiles[source] != nil {
			return u
		}
		for _, alias := range record.Sources {
			actual, ok := publicSource(rom, alias.Member, alias.Image, alias.Pixel)
			if !ok || actual != source {
				return u
			}
		}
		used := []byte{}
		for i := 0; i < 256; i++ {
			if bytes.IndexByte(source[:], byte(i)) >= 0 {
				if _, ok := m.Palette[strconv.Itoa(i)]; !ok {
					return u
				}
				used = append(used, byte(i))
			}
		}
		if !bytes.Equal(used, record.Used) {
			return u
		}
		tile := &infrastructureTile{image: v.Member*1000 + v.Image, used: used, reason: "geometry-mismatch"}
		u.tiles[source] = tile
		indices, e := os.ReadFile(filepath.Join(root, record.ID+"-indices.bin"))
		if e != nil || len(indices) != 5184 || digest(indices) != record.IndicesSHA {
			continue
		}
		weights, e := os.ReadFile(filepath.Join(root, record.ID+"-weights.bin"))
		if e != nil || len(weights) != 5184 || digest(weights) != record.WeightsSHA {
			continue
		}
		valid := true
		for at := 0; at < 5184; at += 4 {
			total := 0
			for j := 0; j < 4; j++ {
				total += int(weights[at+j])
				if weights[at+j] != 0 && bytes.IndexByte(used, indices[at+j]) < 0 {
					valid = false
				}
			}
			if total != 255 {
				valid = false
			}
		}
		if valid {
			tile.indices, tile.weights, tile.reason = indices, weights, ""
		}
	}
	for name, want := range m.Materials {
		if name != "asphalt" && name != "water" && name != "sand" && name != "forest" {
			return u
		}
		data, e := os.ReadFile(filepath.Join(dir, name+"-b-v1.png"))
		if e != nil || digest(data) != want {
			continue
		}
		im := decodeOpaqueMapMaterial(data)
		if im != nil {
			u.textures[name] = im
		}
	}
	return u
}

func decodeOpaqueMapMaterial(raw []byte) *image.RGBA {
	im, err := png.Decode(bytes.NewReader(raw))
	if err != nil || im.Bounds() != image.Rect(0, 0, materialSize, materialSize) {
		return nil
	}
	out := image.NewRGBA(im.Bounds())
	draw.Draw(out, out.Bounds(), im, im.Bounds().Min, draw.Src)
	for i := 3; i < len(out.Pix); i += 4 {
		if out.Pix[i] != 255 {
			return nil
		}
	}
	return out
}

func mapAtlasPaint(u *publicFacilitySet, source [81]byte, px []byte, dst *image.RGBA, pal [256][3]byte, col, row int, stats *publicFacilityStats) bool {
	stats.Matched++
	tile, reason := resolveMapTile(u, source, px, col, row)
	if tile != nil {
		reason = u.paint(dst, tile, pal, col, row)
	}
	if stats.Reasons == nil {
		stats.Reasons = map[string]int{}
	}
	stats.Reasons[reason]++
	if reason == u.matchedReason {
		stats.Painted++
		if stats.Facilities == nil {
			stats.Facilities = map[string]int{}
		}
		stats.Facilities[tile.id]++
		return true
	}
	stats.Fallback++
	return false
}

func (r *Renderer) paintMapCompletion(source [81]byte, px []byte, pal [256][3]byte, col, row int, origin Origin, stats *mapCompletionStats) (bool, bool) {
	if source == [81]byte{} {
		stats.Blank++
		return true, false
	}
	if r.mapComplex.tiles[source] != nil {
		return true, mapAtlasPaint(r.mapComplex, source, px, r.frame, pal, col, row, &stats.Complex)
	}
	if r.mapZones.tiles[source] != nil {
		return true, mapAtlasPaint(r.mapZones, source, px, r.frame, pal, col, row, &stats.Zones)
	}
	if tile := r.mapDetail.tiles[source]; tile != nil {
		s := &stats.Detail
		s.Matched++
		reason := r.mapDetail.paint(r.frame, tile, pal, col, row, origin)
		if s.Reasons == nil {
			s.Reasons = map[string]int{}
		}
		s.Reasons[reason]++
		if reason == "matched-infrastructure" {
			s.Painted++
			if s.Images == nil {
				s.Images = map[int]int{}
			}
			s.Images[tile.image]++
			return true, true
		}
		s.Fallback++
		return true, false
	}
	return false, false
}
