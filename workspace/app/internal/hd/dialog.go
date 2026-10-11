package hd

import (
	"bytes"
	"encoding/json"
	"image"
	"image/draw"
	"image/png"
	"os"
	"path/filepath"

	"golang.org/x/image/font"
	"golang.org/x/image/font/opentype"
	"golang.org/x/image/font/sfnt"
	"golang.org/x/image/math/fixed"
)

const dialogSourceSHA = "a6299b68e4e28c3309bcbf10f2e562c4a9be7fb7d2a43f8a4bc79e69a77ccc8b"
const dialogPaletteSHA = "701e28d343effaf04f5e2b535626a87a3b18e4a1c2fcdc10cbb2a6939714e4de"
const dialogArtSHA = "87a25f1552c42d5f4cc77c1d49c07f69d02d103c6f154feb43d57bc1445558e5"
const dialogTextSHA = "2fbe3ae36cccf679965f33ac1a8d8d49ea866e913baaeb7dda119b3fa1794a71"

var dialogRect = image.Rect(72, 148, 1016, 676)

type newGameDialog struct {
	image  *image.RGBA
	reason string
}

// 原文資料與原版衍生圖片只留本機；契約及固定來源見 spec/017。
func loadNewGameDialog(dir string) *newGameDialog {
	d := &newGameDialog{reason: "dialog-art-unavailable"}
	art, err := os.ReadFile(filepath.Join(dir, "new-game-panel-b-v1.png"))
	if err != nil {
		return d
	}
	if digest(art) != dialogArtSHA {
		d.reason = "dialog-art-mismatch"
		return d
	}
	bg, err := png.Decode(bytes.NewReader(art))
	if err != nil || bg.Bounds() != image.Rect(0, 0, 944, 528) {
		d.reason = "dialog-art-shape"
		return d
	}
	raw, err := os.ReadFile(filepath.Join(dir, "new-game-text-v1.json"))
	if err != nil || digest(raw) != dialogTextSHA {
		d.reason = "dialog-text-mismatch"
		return d
	}
	var data struct {
		Schema int
		Cells  []struct {
			X, Y, Size int
			Text       string
		}
	}
	if json.Unmarshal(raw, &data) != nil || data.Schema != 1 || len(data.Cells) != 90 {
		d.reason = "dialog-text-format"
		return d
	}
	raw, err = os.ReadFile(filepath.Join(dir, "fonts", "NotoSansCJKtc-Regular.otf"))
	if err != nil || digest(raw) != menuFontSHA {
		d.reason = "dialog-font-mismatch"
		return d
	}
	license, err := os.ReadFile(filepath.Join(dir, "fonts", "LICENSE"))
	if err != nil || digest(license) != menuLicenseSHA {
		d.reason = "dialog-license-mismatch"
		return d
	}
	parsed, err := opentype.Parse(raw)
	if err != nil {
		d.reason = "dialog-font-format"
		return d
	}
	faces := map[int]font.Face{}
	defer func() {
		for _, face := range faces {
			face.Close()
		}
	}()
	im := image.NewRGBA(bg.Bounds())
	draw.Draw(im, im.Bounds(), bg, image.Point{}, draw.Src)
	for _, cell := range data.Cells {
		for _, ch := range cell.Text {
			glyph, e := parsed.GlyphIndex(&sfnt.Buffer{}, ch)
			if e != nil || glyph == 0 {
				d.reason = "dialog-missing-glyph"
				return d
			}
		}
		if cell.Size != 56 && cell.Size != 28 {
			d.reason = "dialog-font-size"
			return d
		}
		face := faces[cell.Size]
		if face == nil {
			face, err = opentype.NewFace(parsed, &opentype.FaceOptions{Size: float64(cell.Size), DPI: 72, Hinting: font.HintingNone})
			if err != nil {
				d.reason = "dialog-font-face"
				return d
			}
			faces[cell.Size] = face
		}
		dot := fixed.P(cell.X*4+4, cell.Y*4+50)
		bounds, _ := font.BoundString(face, cell.Text)
		placed := bounds.Add(dot)
		ink := image.Rect(placed.Min.X.Floor(), placed.Min.Y.Floor(), placed.Max.X.Ceil(), placed.Max.Y.Ceil())
		cellRect := image.Rect(cell.X*4, cell.Y*4, cell.X*4+64, cell.Y*4+64)
		if !ink.In(cellRect) || !ink.In(image.Rect(16, 16, 928, 512)) {
			d.reason = "dialog-text-layout"
			return d
		}
		painter := font.Drawer{Dst: im, Src: image.White, Face: face, Dot: dot}
		painter.DrawString(cell.Text)
	}
	d.image, d.reason = im, "matched-dialog"
	return d
}

func dialogSource(px []byte) bool {
	if len(px) != 64000 {
		return false
	}
	box := make([]byte, 0, 236*132)
	for y := 37; y < 169; y++ {
		box = append(box, px[y*320+18:y*320+254]...)
	}
	return digest(box) == dialogSourceSHA
}

func (d *newGameDialog) paint(frame *image.RGBA, pal [256][3]uint8) string {
	if d == nil {
		return "dialog-unavailable"
	}
	if d.reason != "matched-dialog" {
		return d.reason
	}
	var colors []byte
	for _, i := range []int{15, 16, 20, 23, 27, 134} {
		colors = append(colors, pal[i][:]...)
	}
	if digest(colors) != dialogPaletteSHA {
		return "dialog-palette-mismatch"
	}
	draw.Draw(frame, dialogRect, d.image, image.Point{}, draw.Src)
	return "matched-dialog"
}
