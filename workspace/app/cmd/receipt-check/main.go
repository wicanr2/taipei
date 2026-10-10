// #21：獨立解碼 GUI 單幀收據，逐像素核對 PNG、色號與同幀色盤。
package main

import (
	"archive/zip"
	"bytes"
	"crypto/sha256"
	"encoding/json"
	"flag"
	"fmt"
	"image/png"
	"io"
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
	flag.Parse()
	if *dir == "" {
		panic("請指定 -dir")
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
			HD              struct{ Painted int }
		}
		if e = json.Unmarshal(files["status.json"], &s); e != nil {
			return e
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
					if s.HD.Painted == 0 || x < 20 || x >= 1064 || y < 136 || y >= 676 {
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
