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
func main() {
	dir := flag.String("dir", "", "GUI 收據目錄")
	fontReference := flag.String("font-reference", "", "含 Noto 標題時須提供已展示的固定參考圖")
	uiReference := flag.String("ui-reference", "", "含工具圖示時須提供固定 HD atlas")
	flag.Parse()
	if *dir == "" {
		panic("請指定 -dir")
	}
	var reference image.Image
	var icons image.Image
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
			SHA             string       `json:"frame_index_sha256"`
			Palette         [256][3]byte `json:"palette"`
			PresentationSHA string       `json:"presentation_sha256"`
			HD              struct {
				Painted    int
				FontLabels int    `json:"font_labels"`
				FontReason string `json:"font_reason"`
				UIIcons    int    `json:"ui_icons"`
				UIIconMask uint16 `json:"ui_icon_mask"`
				UIReason   string `json:"ui_reason"`
			}
		}
		if e = json.Unmarshal(files["status.json"], &s); e != nil {
			return e
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
							left, top := (273+24*(i%2))*4, (5+24*(i/2))*4
							if s.HD.UIIconMask&(1<<i) != 0 && x >= left && x < left+80 && y >= top && y < top+80 {
								icon = i
								break
							}
						}
					}
					if icon >= 0 {
						xx := x - (273+24*(icon%2))*4 + (icon%4)*80
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
