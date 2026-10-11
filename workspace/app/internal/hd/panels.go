package hd

import (
	"bytes"
	"encoding/json"
	"image"
	"image/draw"
	"image/png"
	"os"
	"path/filepath"
)

// spec/018：完整正常來源及固定 Noto 面板。原文與衍生素材僅留本機。
const panelManifestSHA = "daeb0a0b440bce18b792cae3b89bcacc98b78e19ae05ab5a7e19f86c6cc3384d"
const toolPanelManifestSHA = "288687aa21460d01aa87dd24060c5bbd3ff50035bf26bab5c821d23688f2543e"
const cityPanelManifestSHA = "699c3ed0baed752327667f3d50cc9b0ee45b0124407338eb4f41be94d6239fc5"

type panelState struct {
	ID             string `json:"id"`
	Selection      int    `json:"selection"`
	Native         [4]int `json:"native"`
	SourceSHA      string `json:"source_sha256"`
	PaletteIndices []int  `json:"palette_indices"`
	PaletteSHA     string `json:"palette_sha256"`
	Image          string `json:"image"`
	ImageSHA       string `json:"image_sha256"`
	image          image.Image
	reason         string
}

type panelSet struct {
	states map[string]*panelState
	boxes  [][4]int
	reason string
}

func loadPanels(dir string) *panelSet {
	return loadPanelSet(dir, "startup-menus-v1", panelManifestSHA, 13)
}

// spec/021：十八個已審查的正常工具子選單，與啟動選單分開載入。
func loadToolPanels(dir string) *panelSet {
	return loadPanelSet(dir, "tool-menus-v1", toolPanelManifestSHA, 18)
}

// spec/022：六功能下拉面板的二十九種完整來源。
func loadCityPanels(dir string) *panelSet {
	return loadPanelSet(dir, "city-menus-v1", cityPanelManifestSHA, 29)
}

func loadPanelSet(dir, folder, manifestSHA string, count int) *panelSet {
	p := &panelSet{reason: "panel-manifest-mismatch", states: map[string]*panelState{}}
	base := filepath.Join(dir, folder)
	raw, err := os.ReadFile(filepath.Join(base, "manifest.json"))
	if err != nil || digest(raw) != manifestSHA {
		return p
	}
	var data struct {
		Schema     int
		FontSHA    string `json:"font_sha256"`
		LicenseSHA string `json:"license_sha256"`
		States     []panelState
	}
	if json.Unmarshal(raw, &data) != nil || data.Schema != 1 || len(data.States) != count || data.FontSHA != menuFontSHA || data.LicenseSHA != menuLicenseSHA {
		return p
	}
	for _, item := range []struct{ name, sha, reason string }{
		{"NotoSansCJKtc-Regular.otf", menuFontSHA, "panel-font-mismatch"},
		{"LICENSE", menuLicenseSHA, "panel-license-mismatch"},
	} {
		raw, err = os.ReadFile(filepath.Join(dir, "fonts", item.name))
		if err != nil || digest(raw) != item.sha {
			p.reason = item.reason
			return p
		}
	}
	seen := map[[4]int]bool{}
	for i := range data.States {
		s := &data.States[i]
		x, y, w, h := s.Native[0], s.Native[1], s.Native[2], s.Native[3]
		if x < 0 || y < 0 || w <= 0 || h <= 0 || x+w > 320 || y+h > 200 || filepath.Base(s.Image) != s.Image {
			return p
		}
		if !seen[s.Native] {
			p.boxes = append(p.boxes, s.Native)
			seen[s.Native] = true
		}
		p.states[s.SourceSHA] = s
		s.reason = "panel-art-mismatch"
		raw, err = os.ReadFile(filepath.Join(base, s.Image))
		if err != nil || digest(raw) != s.ImageSHA {
			continue
		}
		s.image, err = png.Decode(bytes.NewReader(raw))
		if err != nil || s.image.Bounds() != image.Rect(0, 0, w*4, h*4) {
			s.image = nil
			s.reason = "panel-art-shape"
			continue
		}
		s.reason = "matched-panel"
	}
	p.reason = "scene-fallback"
	return p
}

func (p *panelSet) paint(frame *image.RGBA, px []byte, pal [256][3]uint8) (string, int, string) {
	if p == nil {
		return "", -1, "panel-unavailable"
	}
	if p.reason != "scene-fallback" {
		return "", -1, p.reason
	}
	for _, b := range p.boxes {
		var source []byte
		for y := b[1]; y < b[1]+b[3]; y++ {
			source = append(source, px[y*320+b[0]:y*320+b[0]+b[2]]...)
		}
		s := p.states[digest(source)]
		if s == nil {
			continue
		}
		var colors []byte
		for _, index := range s.PaletteIndices {
			colors = append(colors, pal[index][:]...)
		}
		if digest(colors) != s.PaletteSHA {
			return "", -1, "panel-palette-mismatch"
		}
		if s.image == nil {
			return "", -1, s.reason
		}
		draw.Draw(frame, image.Rect(b[0]*4, b[1]*4, (b[0]+b[2])*4, (b[1]+b[3])*4), s.image, image.Point{}, draw.Src)
		return s.ID, s.Selection, "matched-panel"
	}
	return "", -1, "scene-fallback"
}
