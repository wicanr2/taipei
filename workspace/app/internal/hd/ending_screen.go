package hd

import (
	"bytes"
	"encoding/json"
	"image"
	"image/draw"
	"image/png"
	"os"
	"path/filepath"
	"strconv"
)

// 028：只接受正常退出已見的完整靜態底圖，不推導政績或動畫。
const endingManifestSHA = "009fcda9e87d5fcea175ae3112a5a5a610b04833a0d278f2e68b99dd4311ef57"
const endingSourceSHA = "0040b4374f37464862ae2f89da5bc897ddb7f53d539edd597cf8b2b6ff784ebd"
const endingImageSHA = "b37fddad8ea9cc3bbc505af3a3daad1f5cb59e86c213d98d12bbf279da81cfb0"
const endingPixelsSHA = "0147c5c7ad6d909d3c01e2084d879b6a32be68cc3167a6a6ae10210986d3a328"

type endingScreen struct {
	frame   *image.RGBA
	palette [256][3]byte
	used    [256]bool
	reason  string
}

func loadEndingScreen(rom []byte, dir string) *endingScreen {
	u := &endingScreen{reason: "ending-manifest-mismatch"}
	if digest(rom) != romSHA {
		u.reason = "ending-rom-mismatch"
		return u
	}
	root := filepath.Join(dir, "ending-scene-ready-v1")
	raw, err := os.ReadFile(filepath.Join(root, "manifest.json"))
	if err != nil || digest(raw) != endingManifestSHA {
		return u
	}
	var manifest struct {
		Schema     int
		Stage      string
		Size       [2]int
		SourceSize [2]int `json:"source_size"`
		SourceSHA  string `json:"source_sha256"`
		Mode       int
		Blocked    bool
		Palette    map[string][3]byte `json:"used_palette"`
		FontSHA    string             `json:"font_sha256"`
		LicenseSHA string             `json:"license_sha256"`
		Images     map[string]struct {
			SHA       string `json:"sha256"`
			PixelsSHA string `json:"rgba_sha256"`
			Size      [2]int
		}
	}
	if json.Unmarshal(raw, &manifest) != nil || manifest.Schema != 1 || manifest.Stage != "achievement-base" ||
		manifest.Size != [2]int{1280, 800} || manifest.SourceSize != [2]int{320, 200} ||
		manifest.SourceSHA != endingSourceSHA || manifest.Mode != 19 || !manifest.Blocked ||
		len(manifest.Palette) != 23 || len(manifest.Images) != 1 {
		u.reason = "ending-metadata-mismatch"
		return u
	}
	for text, rgb := range manifest.Palette {
		index, err := strconv.Atoi(text)
		if err != nil || index < 0 || index > 255 || u.used[index] {
			u.reason = "ending-metadata-mismatch"
			return u
		}
		u.palette[index], u.used[index] = rgb, true
	}
	font, err := os.ReadFile(filepath.Join(dir, "fonts", "NotoSansCJKtc-Regular.otf"))
	if err != nil || digest(font) != manifest.FontSHA || manifest.FontSHA != "dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4" {
		u.reason = "ending-font-mismatch"
		return u
	}
	license, err := os.ReadFile(filepath.Join(dir, "fonts", "LICENSE"))
	if err != nil || digest(license) != manifest.LicenseSHA || manifest.LicenseSHA != "6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2" {
		u.reason = "ending-license-mismatch"
		return u
	}
	meta := manifest.Images["screen.png"]
	if meta.SHA != endingImageSHA || meta.PixelsSHA != endingPixelsSHA || meta.Size != [2]int{1280, 800} {
		u.reason = "ending-metadata-mismatch"
		return u
	}
	raw, err = os.ReadFile(filepath.Join(root, "screen.png"))
	if err != nil || digest(raw) != endingImageSHA {
		u.reason = "ending-image-mismatch"
		return u
	}
	im, err := png.Decode(bytes.NewReader(raw))
	if err != nil || im.Bounds() != image.Rect(0, 0, 1280, 800) {
		u.reason = "ending-image-shape"
		return u
	}
	u.frame = image.NewRGBA(im.Bounds())
	draw.Draw(u.frame, u.frame.Bounds(), im, image.Point{}, draw.Src)
	if digest(u.frame.Pix) != endingPixelsSHA {
		u.frame = nil
		u.reason = "ending-image-mismatch"
		return u
	}
	for i := 3; i < len(u.frame.Pix); i += 4 {
		if u.frame.Pix[i] != 255 {
			u.frame = nil
			u.reason = "ending-image-shape"
			return u
		}
	}
	u.reason = ""
	return u
}

func endingScreenSource(px []byte) bool {
	return len(px) == 64000 && digest(px) == endingSourceSHA
}

func (u *endingScreen) paint(dst *image.RGBA, pal [256][3]byte, blocked bool) string {
	if !blocked {
		return "ending-unverified-phase"
	}
	if u == nil {
		return "ending-image-mismatch"
	}
	if u.reason != "" {
		return u.reason
	}
	for i, used := range u.used {
		if used && pal[i] != u.palette[i] {
			return "ending-palette-mismatch"
		}
	}
	draw.Draw(dst, dst.Bounds(), u.frame, image.Point{}, draw.Src)
	return "matched-ending-screen"
}
