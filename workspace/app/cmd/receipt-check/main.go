// #21：獨立解碼 GUI 單幀收據，逐像素核對 PNG、色號與同幀色盤。
package main

import (
	"archive/zip"
	"bytes"
	"crypto/sha256"
	"encoding/json"
	"flag"
	"fmt"
	"image"
	"image/png"
	"io"
	"math/bits"
	"os"
	"path/filepath"
	"strings"
)

func check(e error) {
	if e != nil {
		panic(e)
	}
}

type panelReference struct {
	ID             string `json:"id"`
	Selection      int    `json:"selection"`
	Native         [4]int `json:"native"`
	SourceSHA      string `json:"source_sha256"`
	PaletteIndices []int  `json:"palette_indices"`
	PaletteSHA     string `json:"palette_sha256"`
	Image          string `json:"image"`
	ImageSHA       string `json:"image_sha256"`
	decoded        image.Image
}

func readPanels(path string) []panelReference {
	if path == "" {
		return nil
	}
	raw, err := os.ReadFile(path)
	check(err)
	if fmt.Sprintf("%x", sha256.Sum256(raw)) != "daeb0a0b440bce18b792cae3b89bcacc98b78e19ae05ab5a7e19f86c6cc3384d" {
		panic("啟動面板 manifest 失配")
	}
	var data struct {
		Schema int
		States []panelReference
	}
	check(json.Unmarshal(raw, &data))
	if data.Schema != 1 || len(data.States) != 13 {
		panic("啟動面板數量失配")
	}
	for i := range data.States {
		s := &data.States[i]
		raw, err = os.ReadFile(filepath.Join(filepath.Dir(path), s.Image))
		check(err)
		if fmt.Sprintf("%x", sha256.Sum256(raw)) != s.ImageSHA {
			panic("啟動面板參考失配")
		}
		s.decoded, err = png.Decode(bytes.NewReader(raw))
		check(err)
		if s.decoded.Bounds() != image.Rect(0, 0, s.Native[2]*4, s.Native[3]*4) {
			panic("啟動面板參考尺寸失配")
		}
	}
	return data.States
}

func main() {
	dir := flag.String("dir", "", "GUI 收據目錄")
	fontReference := flag.String("font-reference", "", "含 Noto 標題時須提供已展示的固定參考圖")
	uiReference := flag.String("ui-reference", "", "含工具圖示時須提供固定 HD atlas")
	dialogReference := flag.String("dialog-reference", "", "含說明視窗時須提供固定 Noto 面板參考")
	panelManifest := flag.String("panel-manifest", "", "啟動選單固定面板與完整來源 manifest")
	chromeDir := flag.String("chrome-reference", "", "城市框架及外框固定參考目錄")
	flag.Parse()
	panels := readPanels(*panelManifest)
	chrome := readChrome(*chromeDir)
	if *dir == "" {
		panic("請指定 -dir")
	}
	var reference image.Image
	var icons image.Image
	var dialog image.Image
	if *dialogReference != "" {
		raw, err := os.ReadFile(*dialogReference)
		check(err)
		if fmt.Sprintf("%x", sha256.Sum256(raw)) != "6bfa6faeffd0950d31af1a5bb9da84aa71af4a34dc36dae374d3d387b1e6c7e9" {
			panic("說明視窗參考雜湊失配")
		}
		dialog, err = png.Decode(bytes.NewReader(raw))
		check(err)
		if dialog.Bounds() != image.Rect(0, 0, 944, 528) {
			panic("說明視窗參考尺寸不符")
		}
	}
	if *uiReference != "" {
		raw, err := os.ReadFile(*uiReference)
		check(err)
		if fmt.Sprintf("%x", sha256.Sum256(raw)) != "9ad97735f45cab2c968e23d8f1d6924c6b1937854fa4cda1c1c7a5ee90a089ab" {
			panic("工具圖示參考雜湊失配")
		}
		icons, err = png.Decode(bytes.NewReader(raw))
		check(err)
		if icons.Bounds() != image.Rect(0, 0, 320, 320) {
			panic("工具圖示參考尺寸不符")
		}
	}
	if *fontReference != "" {
		raw, err := os.ReadFile(*fontReference)
		check(err)
		if fmt.Sprintf("%x", sha256.Sum256(raw)) != "feefbf252a77ab01322c72654a2c6d8b7cb42118494949604f194c20d4f331da" {
			panic("已展示字型參考雜湊失配")
		}
		reference, err = png.Decode(bytes.NewReader(raw))
		check(err)
		if reference.Bounds() != image.Rect(0, 0, 1280, 800) {
			panic("字型參考圖尺寸不符")
		}
	}
	count := 0
	check(filepath.WalkDir(*dir, func(path string, d os.DirEntry, e error) error {
		if e != nil {
			return e
		}
		if d.IsDir() || !strings.HasSuffix(d.Name(), "-capture.zip") {
			return nil
		}
		z, e := zip.OpenReader(path)
		if e != nil {
			return e
		}
		defer z.Close()
		files := map[string][]byte{}
		for _, f := range z.File {
			r, e := f.Open()
			if e != nil {
				return e
			}
			p, e := io.ReadAll(r)
			r.Close()
			if e != nil {
				return e
			}
			files[f.Name] = p
		}
		var s struct {
			Mode            int          `json:"mode"`
			Enabled         bool         `json:"hd_enabled"`
			SHA             string       `json:"frame_index_sha256"`
			Palette         [256][3]byte `json:"palette"`
			PresentationSHA string       `json:"presentation_sha256"`
			HD              struct {
				chromeFields
				Painted        int
				FontLabels     int    `json:"font_labels"`
				FontReason     string `json:"font_reason"`
				UIIcons        int    `json:"ui_icons"`
				UIIconMask     uint16 `json:"ui_icon_mask"`
				UIReason       string `json:"ui_reason"`
				Dialog         string `json:"dialog"`
				DialogReason   string `json:"dialog_reason"`
				Panel          string `json:"panel"`
				PanelSelection int    `json:"panel_selection"`
				PanelReason    string `json:"panel_reason"`
			}
		}
		if e = json.Unmarshal(files["status.json"], &s); e != nil {
			return e
		}
		if e = chrome.validate(s.HD.chromeFields); e != nil {
			return fmt.Errorf("%s: %w", path, e)
		}
		if s.HD.FontLabels != 0 && (s.HD.FontLabels != 6 || s.HD.FontReason != "matched-menu" || reference == nil) {
			return fmt.Errorf("%s: Noto labels require six matched labels and the selected reference", path)
		}
		if s.HD.UIIconMask>>14 != 0 || bits.OnesCount16(s.HD.UIIconMask) != s.HD.UIIcons ||
			(s.HD.UIIcons != 0 && (s.HD.UIReason != "matched-icons" || icons == nil)) {
			return fmt.Errorf("%s: tool icons require a valid mask and fixed atlas", path)
		}
		px := files["frame-index.bin"]
		if len(px) != 64000 || fmt.Sprintf("%x", sha256.Sum256(px)) != s.SHA {
			return fmt.Errorf("%s: index digest mismatch", path)
		}
		var panel *panelReference
		if s.Enabled && s.Mode == 19 {
			for i := range panels {
				p := &panels[i]
				x, y, w, h := p.Native[0], p.Native[1], p.Native[2], p.Native[3]
				var box, colors []byte
				for row := y; row < y+h; row++ {
					box = append(box, px[row*320+x:row*320+x+w]...)
				}
				for _, index := range p.PaletteIndices {
					colors = append(colors, s.Palette[index][:]...)
				}
				if fmt.Sprintf("%x", sha256.Sum256(box)) == p.SourceSHA && fmt.Sprintf("%x", sha256.Sum256(colors)) == p.PaletteSHA {
					panel = p
					break
				}
			}
		}
		if s.HD.Panel != "" || panel != nil {
			if panel == nil || s.HD.Panel != panel.ID || s.HD.PanelSelection != panel.Selection || s.HD.PanelReason != "matched-panel" || s.HD.Painted != 0 || s.HD.FontLabels != 0 || s.HD.UIIcons != 0 || s.HD.Dialog != "" {
				return fmt.Errorf("%s: panel source, palette or metadata mismatch", path)
			}
		}
		if s.HD.Dialog != "" {
			if s.HD.Dialog != "new-game" || s.HD.DialogReason != "matched-dialog" || dialog == nil || !s.Enabled || s.Mode != 19 || s.HD.Painted != 0 || s.HD.FontLabels != 0 || s.HD.UIIcons != 0 {
				return fmt.Errorf("%s: invalid dialog metadata or missing reference", path)
			}
			var box, colors []byte
			for y := 37; y < 169; y++ {
				box = append(box, px[y*320+18:y*320+254]...)
			}
			for _, i := range []int{15, 16, 20, 23, 27, 134} {
				colors = append(colors, s.Palette[i][:]...)
			}
			if fmt.Sprintf("%x", sha256.Sum256(box)) != "a6299b68e4e28c3309bcbf10f2e562c4a9be7fb7d2a43f8a4bc79e69a77ccc8b" || fmt.Sprintf("%x", sha256.Sum256(colors)) != "701e28d343effaf04f5e2b535626a87a3b18e4a1c2fcdc10cbb2a6939714e4de" {
				return fmt.Errorf("%s: dialog source or palette mismatch", path)
			}
		}
		im, e := png.Decode(bytes.NewReader(files["frame.png"]))
		if e != nil {
			return e
		}
		if im.Bounds().Dx() != 320 || im.Bounds().Dy() != 200 {
			return fmt.Errorf("%s: PNG dimensions", path)
		}
		for y := 0; y < 200; y++ {
			for x := 0; x < 320; x++ {
				r, g, b, a := im.At(x, y).RGBA()
				c := s.Palette[px[y*320+x]]
				if byte(r>>8) != c[0] || byte(g>>8) != c[1] || byte(b>>8) != c[2] || a != 65535 {
					return fmt.Errorf("%s: PNG differs at %d,%d", path, x, y)
				}
			}
		}
		if s.PresentationSHA != "" {
			presented, e := png.Decode(bytes.NewReader(files["presentation.png"]))
			if e != nil {
				return e
			}
			if presented.Bounds().Dx() != 1280 || presented.Bounds().Dy() != 800 {
				return fmt.Errorf("%s: presentation dimensions", path)
			}
			pixels := make([]byte, 1280*800*4)
			for y := 0; y < 800; y++ {
				for x := 0; x < 1280; x++ {
					r, g, b, a := presented.At(x, y).RGBA()
					at := (y*1280 + x) * 4
					copy(pixels[at:at+4], []byte{byte(r >> 8), byte(g >> 8), byte(b >> 8), byte(a >> 8)})
					fontPixel := false
					if s.HD.FontLabels == 6 && y >= 40 && y < 108 {
						for i := 0; i < 6; i++ {
							fontPixel = fontPixel || (x >= 28+i*176 && x < 164+i*176)
						}
					}
					icon := -1
					if x >= 1092 && y >= 20 && y < 676 {
						for i := 0; i < 14; i++ {
							left, top := (274+23*(i%2))*4, (5+24*(i/2))*4
							if s.HD.UIIconMask&(1<<i) != 0 && x >= left && x < left+80 && y >= top && y < top+80 {
								icon = i
								break
							}
						}
					}
					chromeImage, cx, cy := chrome.pixel(s.HD.chromeFields, px, x, y)
					if panel != nil && x >= panel.Native[0]*4 && x < (panel.Native[0]+panel.Native[2])*4 && y >= panel.Native[1]*4 && y < (panel.Native[1]+panel.Native[3])*4 {
						rr, gg, bb, aa := panel.decoded.At(x-panel.Native[0]*4, y-panel.Native[1]*4).RGBA()
						if r != rr || g != gg || b != bb || a != aa {
							return fmt.Errorf("%s: panel pixels differ at %d,%d", path, x, y)
						}
					} else if s.HD.Dialog == "new-game" && x >= 72 && x < 1016 && y >= 148 && y < 676 {
						rr, gg, bb, aa := dialog.At(x-72, y-148).RGBA()
						if r != rr || g != gg || b != bb || a != aa {
							return fmt.Errorf("%s: dialog pixels differ at %d,%d", path, x, y)
						}
					} else if chromeImage != nil {
						rr, gg, bb, aa := chromeImage.At(cx, cy).RGBA()
						if r != rr || g != gg || b != bb || a != aa {
							return fmt.Errorf("%s: 城市框架像素失配 %d,%d", path, x, y)
						}
					} else if icon >= 0 {
						xx := x - (274+23*(icon%2))*4 + (icon%4)*80
						yy := y - (5+24*(icon/2))*4 + (icon/4)*80
						rr, gg, bb, aa := icons.At(xx, yy).RGBA()
						if r != rr || g != gg || b != bb || a != aa {
							return fmt.Errorf("%s: tool icon pixels differ at %d,%d", path, x, y)
						}
					} else if fontPixel {
						rr, gg, bb, aa := reference.At(x, y).RGBA()
						if r != rr || g != gg || b != bb || a != aa {
							return fmt.Errorf("%s: Noto pixels differ from selected reference at %d,%d", path, x, y)
						}
					} else if s.HD.Painted == 0 || x < 20 || x >= 1064 || y < 136 || y >= 676 {
						c := s.Palette[px[(y/4)*320+x/4]]
						if byte(r>>8) != c[0] || byte(g>>8) != c[1] || byte(b>>8) != c[2] || a != 65535 {
							return fmt.Errorf("%s: presentation changed native pixel at %d,%d", path, x, y)
						}
					}
				}
			}
			if fmt.Sprintf("%x", sha256.Sum256(pixels)) != s.PresentationSHA {
				return fmt.Errorf("%s: presentation digest mismatch", path)
			}
		}
		count++
		return nil
	}))
	if count == 0 {
		panic("未找到單幀收據")
	}
	fmt.Printf("same-frame bundles verified: %d\n", count)
}
