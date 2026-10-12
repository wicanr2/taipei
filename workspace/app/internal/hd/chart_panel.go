package hd

import (
	"bytes"
	"encoding/binary"
	"encoding/json"
	"image"
	"image/color"
	"image/draw"
	"image/png"
	"os"
	"path/filepath"
)

// 029：只呈現原版已計算的圖表色號，不推定選項或統計語意。
const chartManifestSHA = "9a0cc44ee54ea2b2681c6e578a00ac532be32b9d88780cc9c90579fe4766226e"
const chartFrameSHA = "7b70c2e5b3dcc83fbd063c5a6829b050b003d4caa1fcfc64ddd8344091775d9b"
const chartPixelsSHA = "6e39dcf7dc0a8cbf58d1be91e46da10e7f2c7588fef8b44c502b3f6081b68d59"
const chartGrainSHA = "17c0fe2195ee6961533c16ae3b52d46c01045470b8874ddb5dbd46eb77fb142b"
const chartFixedSHA = "592ce98b127d88a073f2b4b25bf38bc077283cd60518210948a669da0678f487"

type chartWindows struct {
	base     []byte
	frame    *image.RGBA
	grain    []byte
	palettes [2][256][3]byte
	reason   string
}

func chartBase(rom []byte) []byte {
	if digest(rom) != romSHA {
		return nil
	}
	offset := int(binary.LittleEndian.Uint32(rom[18+4*16:]))
	size := int(binary.LittleEndian.Uint16(rom[22+4*16:]))
	if offset != 27667 || size != 9294 {
		return nil
	}
	raw := rom[offset : offset+size]
	if !bytes.Equal(raw[:4], []byte{145, 0, 127, 0}) {
		return nil
	}
	var out []byte
	for at := 4; at < len(raw); {
		value, count := raw[at], 1
		at++
		if value == 0 {
			if at+2 > len(raw) || raw[at+1] == 0 {
				return nil
			}
			value, count = raw[at], int(raw[at+1])
			at += 2
		}
		out = append(out, bytes.Repeat([]byte{value}, count)...)
		if len(out) > 145*127 {
			return nil
		}
	}
	if len(out) != 145*127 || digest(out) != "c3b7fa8fdc7246e48cd051d375cf36566c3f01c69e33f7eb9ac4bcd1c2ffc961" {
		return nil
	}
	return out
}

func chartData(x, y int) bool { return x >= 20 && x < 125 && y >= 20 && y < 109 }

func loadChartWindows(rom []byte, dir string) *chartWindows {
	u := &chartWindows{base: chartBase(rom), reason: "chart-manifest-mismatch"}
	if u.base == nil {
		u.reason = "chart-rom-mismatch"
		return u
	}
	root := filepath.Join(dir, "chart-windows-ready-v1")
	raw, err := os.ReadFile(filepath.Join(root, "manifest.json"))
	if err != nil || digest(raw) != chartManifestSHA {
		return u
	}
	var m struct {
		Schema      int
		Stage       string
		Native      [4]int
		Data        [4]int `json:"data_local"`
		FixedPixels int    `json:"fixed_pixels"`
		FixedSHA    string `json:"fixed_sha256"`
		ROM         string `json:"rom_sha256"`
		Mode        int
		Blocked     bool
		Font        string `json:"font_sha256"`
		License     string `json:"license_sha256"`
		Palettes    []struct {
			SHA string `json:"sha256"`
			RGB [256][3]byte
		}
		Grain struct {
			Bytes int
			SHA   string `json:"sha256"`
		}
		Images map[string]struct {
			Size   [2]int
			SHA    string `json:"sha256"`
			Pixels string `json:"rgba_sha256"`
		}
	}
	if json.Unmarshal(raw, &m) != nil || m.Schema != 1 || m.Stage != "chart-windows" || m.ROM != romSHA ||
		m.Native != [4]int{66, 35, 145, 127} || m.Data != [4]int{20, 20, 105, 89} ||
		m.FixedPixels != 9070 || m.FixedSHA != chartFixedSHA || m.Mode != 19 || !m.Blocked ||
		len(m.Palettes) != 2 || len(m.Images) != 1 || m.Grain.Bytes != 580*508 || m.Grain.SHA != chartGrainSHA {
		u.reason = "chart-metadata-mismatch"
		return u
	}
	for i, p := range m.Palettes {
		var values []byte
		for _, rgb := range p.RGB {
			values = append(values, rgb[:]...)
		}
		if digest(values) != p.SHA {
			u.reason = "chart-metadata-mismatch"
			return u
		}
		u.palettes[i] = p.RGB
	}
	for _, item := range []struct{ path, expected, actual, reason string }{
		{"fonts/NotoSansCJKtc-Regular.otf", "dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4", m.Font, "chart-font-mismatch"},
		{"fonts/LICENSE", "6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2", m.License, "chart-license-mismatch"},
	} {
		data, err := os.ReadFile(filepath.Join(dir, item.path))
		if err != nil || item.actual != item.expected || digest(data) != item.expected {
			u.reason = item.reason
			return u
		}
	}
	meta := m.Images["frame.png"]
	if meta.Size != [2]int{580, 508} || meta.SHA != chartFrameSHA || meta.Pixels != chartPixelsSHA {
		u.reason = "chart-metadata-mismatch"
		return u
	}
	raw, err = os.ReadFile(filepath.Join(root, "frame.png"))
	if err != nil || digest(raw) != chartFrameSHA {
		u.reason = "chart-image-mismatch"
		return u
	}
	im, err := png.Decode(bytes.NewReader(raw))
	if err != nil || im.Bounds() != image.Rect(0, 0, 580, 508) {
		u.reason = "chart-image-shape"
		return u
	}
	u.frame = image.NewRGBA(im.Bounds())
	draw.Draw(u.frame, u.frame.Bounds(), im, image.Point{}, draw.Src)
	if digest(u.frame.Pix) != chartPixelsSHA {
		u.reason = "chart-image-mismatch"
		return u
	}
	for y := 0; y < 508; y++ {
		for x := 0; x < 580; x++ {
			c := u.frame.RGBAAt(x, y)
			if chartData(x/4, y/4) && c != (color.RGBA{}) || !chartData(x/4, y/4) && c.A != 255 {
				u.reason = "chart-image-shape"
				return u
			}
		}
	}
	u.grain, err = os.ReadFile(filepath.Join(root, "grain.bin"))
	if err != nil || len(u.grain) != 580*508 || digest(u.grain) != chartGrainSHA {
		u.reason = "chart-grain-mismatch"
		return u
	}
	u.reason = ""
	return u
}

func (u *chartWindows) source(px []byte) bool {
	if u == nil || len(u.base) != 145*127 || len(px) != 64000 {
		return false
	}
	for y := 0; y < 127; y++ {
		for x := 0; x < 145; x++ {
			if !chartData(x, y) && px[(35+y)*320+66+x] != u.base[y*145+x] {
				return false
			}
		}
	}
	return true
}

func chartClamp(v int) byte {
	if v < 0 {
		return 0
	}
	if v > 255 {
		return 255
	}
	return byte(v)
}

func (u *chartWindows) paint(dst *image.RGBA, px []byte, pal [256][3]byte, blocked bool) (string, string) {
	if !blocked {
		return "chart-unverified-phase", ""
	}
	if u.reason != "" {
		return u.reason, ""
	}
	var used [256]bool
	var data []byte
	for y := 0; y < 127; y++ {
		for x := 0; x < 145; x++ {
			v := px[(35+y)*320+66+x]
			used[v] = true
			if chartData(x, y) {
				data = append(data, v)
			}
		}
	}
	for i, yes := range used {
		if yes && pal[i] != u.palettes[0][i] && pal[i] != u.palettes[1][i] {
			return "chart-palette-mismatch", ""
		}
	}
	draw.Draw(dst, image.Rect(264, 140, 844, 648), u.frame, image.Point{}, draw.Over)
	for y := 80; y < 436; y++ {
		for x := 80; x < 500; x++ {
			v := px[(35+y/4)*320+66+x/4]
			rgb := pal[v]
			grain := int(u.grain[y*580+x]) - 128
			at := ((140+y)*1280 + 264 + x) * 4
			for c := 0; c < 3; c++ {
				dst.Pix[at+c] = chartClamp(int(rgb[c]) + grain)
			}
			dst.Pix[at+3] = 255
		}
	}
	return "matched-chart-window", digest(data)
}
