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

// 026 第一批：只讀完整原版圖塊，呈現不推導連接、施工或動畫規則。
const infrastructureManifestSHA = "720e3d40b253c6a505dbfa43f415cb0752e18ea51150d9888c1ea3f4c7bc7aec"

var infrastructureImages = []int{15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 27, 28, 29, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55}

type infrastructureStats struct {
	Matched  int            `json:"matched"`
	Painted  int            `json:"painted"`
	Fallback int            `json:"fallback"`
	Images   map[int]int    `json:"images,omitempty"`
	Reasons  map[string]int `json:"reasons,omitempty"`
}

type infrastructureTile struct {
	image            int
	indices, weights []byte
	used             []byte
	reason           string
}

type infrastructureSet struct {
	tiles    map[[81]byte]*infrastructureTile
	textures map[string]*image.RGBA
	palette  [256][3]byte
}

func loadInfrastructure(rom []byte, dir string) *infrastructureSet {
	u := &infrastructureSet{tiles: map[[81]byte]*infrastructureTile{}, textures: map[string]*image.RGBA{}}
	if digest(rom) != romSHA {
		return u
	}
	off := int(binary.LittleEndian.Uint32(rom[18+39*16:]))
	n := int(binary.LittleEndian.Uint16(rom[22+39*16:]))
	lib := rom[off : off+n]
	if n != 6527 || binary.LittleEndian.Uint16(lib) != 75 {
		return u
	}
	byImage := map[int]*infrastructureTile{}
	for _, index := range infrastructureImages {
		a := int(binary.LittleEndian.Uint16(lib[2+index*2:]))
		b := int(binary.LittleEndian.Uint16(lib[4+index*2:]))
		if b-a != 85 || binary.LittleEndian.Uint16(lib[a:]) != 9 || binary.LittleEndian.Uint16(lib[a+2:]) != 9 {
			return u
		}
		var source [81]byte
		copy(source[:], lib[a+4:b])
		tile := &infrastructureTile{image: index, reason: "manifest-mismatch"}
		u.tiles[source], byImage[index] = tile, tile
		var used [256]bool
		for _, v := range source {
			used[v] = true
		}
		for i, present := range used {
			if present {
				tile.used = append(tile.used, byte(i))
			}
		}
	}
	root := filepath.Join(dir, "infrastructure-ready-v1")
	raw, err := os.ReadFile(filepath.Join(root, "manifest.json"))
	if err != nil || digest(raw) != infrastructureManifestSHA {
		return u
	}
	var manifest struct {
		Schema           int
		Stage            string
		ROMSHA           string `json:"rom_sha256"`
		GeometryVersion  int    `json:"geometry_version"`
		AsphaltFrequency int    `json:"asphalt_frequency"`
		MaterialSize     int    `json:"material_size"`
		Palette          map[string][3]byte
		Materials        map[string]string
		Sources          []struct {
			Image      int
			SourceSHA  string `json:"source_sha256"`
			IndicesSHA string `json:"indices_sha256"`
			WeightsSHA string `json:"weights_sha256"`
			Used       []byte `json:"used_colors"`
		}
	}
	if json.Unmarshal(raw, &manifest) != nil || manifest.Schema != 1 || manifest.Stage != "normal25" || manifest.ROMSHA != romSHA || manifest.GeometryVersion != 3 || manifest.AsphaltFrequency != 4 || manifest.MaterialSize != materialSize || len(manifest.Sources) != 25 {
		return u
	}
	for key, color := range manifest.Palette {
		index, e := strconv.Atoi(key)
		if e != nil || index < 0 || index > 255 {
			return u
		}
		u.palette[index] = color
	}
	for _, record := range manifest.Sources {
		tile := byImage[record.Image]
		if tile == nil || !bytes.Equal(tile.used, record.Used) {
			return u
		}
		a := int(binary.LittleEndian.Uint16(lib[2+record.Image*2:]))
		if digest(lib[a+4:a+85]) != record.SourceSHA {
			return u
		}
		tile.reason = "geometry-mismatch"
		indices, e := os.ReadFile(filepath.Join(root, fmt.Sprintf("39-%03d-indices.bin", record.Image)))
		if e != nil || len(indices) != 5184 || digest(indices) != record.IndicesSHA {
			continue
		}
		weights, e := os.ReadFile(filepath.Join(root, fmt.Sprintf("39-%03d-weights.bin", record.Image)))
		if e != nil || len(weights) != 5184 || digest(weights) != record.WeightsSHA {
			continue
		}
		valid := true
		for at := 0; at < 5184; at += 4 {
			total := 0
			for j := 0; j < 4; j++ {
				total += int(weights[at+j])
				if weights[at+j] != 0 && !bytes.Contains(tile.used, indices[at+j:at+j+1]) {
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
	for name, want := range manifest.Materials {
		raw, err := os.ReadFile(filepath.Join(dir, name+"-b-v1.png"))
		if err != nil || digest(raw) != want {
			continue
		}
		im, err := png.Decode(bytes.NewReader(raw))
		if err != nil || im.Bounds() != image.Rect(0, 0, materialSize, materialSize) {
			continue
		}
		texture := image.NewRGBA(im.Bounds())
		draw.Draw(texture, texture.Bounds(), im, im.Bounds().Min, draw.Src)
		u.textures[name] = texture
	}
	return u
}

func infrastructureMirror(world int) int {
	i := world % (2 * materialSize)
	if i < 0 {
		i += 2 * materialSize
	}
	if i >= materialSize {
		i = 2*materialSize - 1 - i
	}
	return i
}

func infrastructureMaterial(index byte) (string, int) {
	switch {
	case index == 21:
		return "asphalt", 1000
	case index >= 103 && index <= 107:
		return "forest", 700 + int(index-103)*100
	case index >= 201 && index <= 204:
		return "sand", 940 + int(index-201)*25
	}
	return "", 1000
}

func infrastructureNearest(value int) byte {
	q, r := value/300, value%300
	if r < 0 {
		q--
		r += 300
	}
	if r > 150 || (r == 150 && q%2 != 0) {
		q++
	}
	return byte(max(0, min(255, q)))
}

func (u *infrastructureSet) color(index byte, wx, wy int, original [3]byte) [3]byte {
	asphalt := u.textures["asphalt"]
	at := (infrastructureMirror(wy*4)*materialSize + infrastructureMirror(wx*4)) * 4
	name, factor := infrastructureMaterial(index)
	if name != "" {
		texture := u.textures[name]
		if name != "asphalt" {
			at = (infrastructureMirror(wy)*materialSize + infrastructureMirror(wx)) * 4
		}
		return [3]byte{byte(min(255, int(texture.Pix[at])*factor/1000)), byte(min(255, int(texture.Pix[at+1])*factor/1000)), byte(min(255, int(texture.Pix[at+2])*factor/1000))}
	}
	grain := int(asphalt.Pix[at]) + int(asphalt.Pix[at+1]) + int(asphalt.Pix[at+2]) - 225
	var base [3]int
	if index == 15 {
		base = [3]int{24200, 23900, 22400}
	} else if index == 0 {
		base = [3]int{1500, 2300, 2700}
	} else {
		r, g, b := int(original[0]), int(original[1]), int(original[2])
		if r == g && g == b {
			base = [3]int{r*95 + 1000, g*100 + 1400, b*100 + 2000}
		} else {
			base = [3]int{r*90 + 800, g*90 + 800, b*90 + 800}
		}
	}
	return [3]byte{infrastructureNearest(base[0]*3 + grain*10), infrastructureNearest(base[1]*3 + grain*10), infrastructureNearest(base[2]*3 + grain*10)}
}

func (u *infrastructureSet) paint(dst *image.RGBA, tile *infrastructureTile, pal [256][3]byte, col, row int, origin Origin) string {
	if tile.reason != "" {
		return tile.reason
	}
	if u.textures["asphalt"] == nil {
		return "asphalt-mismatch"
	}
	for _, index := range tile.used {
		if pal[index] != u.palette[index] {
			return "palette-mismatch"
		}
		if name, _ := infrastructureMaterial(index); name != "" && u.textures[name] == nil {
			return name + "-mismatch"
		}
	}
	for y := 0; y < 36; y++ {
		for x := 0; x < 36; x++ {
			at := (y*36 + x) * 4
			var total [3]int
			for j := 0; j < 4; j++ {
				weight := int(tile.weights[at+j])
				if weight == 0 {
					continue
				}
				index := tile.indices[at+j]
				color := u.color(index, (origin.X+col)*36+x, (origin.Y+row)*36+y, pal[index])
				for c, v := range color {
					total[c] += int(v) * weight
				}
			}
			pos := ((136+row*36+y)*1280 + 20 + col*36 + x) * 4
			copy(dst.Pix[pos:pos+4], []byte{byte(total[0] / 255), byte(total[1] / 255), byte(total[2] / 255), 255})
		}
	}
	return "matched-infrastructure"
}
