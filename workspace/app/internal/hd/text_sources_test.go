package hd

import (
	"bytes"
	"encoding/hex"
	"encoding/json"
	"image"
	"image/color"
	"image/draw"
	"image/png"
	"os"
	"path/filepath"
	"testing"

	"github.com/wicanr2/taipei/preview/internal/i18n"
)

func TestRemainingTextSourcesWithOriginalFrames(t *testing.T) {
	root, orig, materials := os.Getenv("TAIPEI_LOCALE_WORKSPACE"), os.Getenv("TAIPEI_HD_ORIGINAL"), os.Getenv("TAIPEI_HD_MATERIALS")
	if root == "" || orig == "" || materials == "" {
		t.Skip("requires original source receipts and fixed Noto materials")
	}
	read := func(p string) []byte {
		b, e := os.ReadFile(p)
		if e != nil {
			t.Fatal(e)
		}
		return b
	}
	exe, rom, romA := read(filepath.Join(orig, "RS201.EXE")), read(filepath.Join(orig, "RS201.ROM")), read(filepath.Join(orig, "RS201A.ROM"))
	r := New(rom, materials)
	images := r.InitTextSources(exe, rom, romA)
	if len(images) != 9 {
		t.Fatalf("image sources=%d", len(images))
	}
	var audit struct {
		Calls []struct {
			Code                  string
			X, Y, Ink, Background int
			EA                    uint32
		}
		Events []struct {
			Label   string
			Palette [256][3]byte
		}
	}
	dir := filepath.Join(root, "runs/localization-source-intro-r2")
	if e := json.Unmarshal(read(filepath.Join(dir, "audit.json")), &audit); e != nil {
		t.Fatal(e)
	}
	var check struct {
		Results []struct {
			File    string
			Call    int
			Matches []struct{ Characters int }
		}
	}
	if e := json.Unmarshal(read(filepath.Join(dir, "source-check.json")), &check); e != nil {
		t.Fatal(e)
	}
	pals := map[string][256][3]byte{}
	for _, e := range audit.Events {
		pals[e.Label] = e.Palette
	}
	rawImage := func(px []byte, pal [256][3]byte) *image.RGBA {
		out := image.NewRGBA(image.Rect(0, 0, 1280, 800))
		for i, v := range px {
			c := pal[v]
			draw.Draw(out, image.Rect((i%320)*4, (i/320)*4, (i%320+1)*4, (i/320+1)*4), image.NewUniform(color.RGBA{c[0], c[1], c[2], 255}), image.Point{}, draw.Src)
		}
		return out
	}
	gallery := os.Getenv("TAIPEI_TEXT_GALLERY")
	if gallery != "" {
		if e := os.Mkdir(gallery, 0700); e != nil {
			t.Fatal(e)
		}
	}
	for _, lang := range i18n.Languages {
		r.SetLanguage(i18n.Bundled(), lang)
		if r.locale.reason != "" {
			t.Fatal(lang, r.locale.reason)
		}
		verified := 0
		for _, c := range check.Results {
			if len(c.Matches) == 0 {
				t.Fatal("unverified original fixture", c.File)
			}
			call := audit.Calls[c.Call]
			parts, _, ok := r.textSources.glyphs(mustDecodeText(t, call.Code))
			if !ok {
				t.Fatal(call.Code)
			}
			count := c.Matches[len(c.Matches)-1].Characters
			visible := 0
			for _, p := range parts[:count] {
				visible += len(p)
			}
			d := TextDraw{Code: call.Code, X: call.X, Y: call.Y, Ink: call.Ink, Background: call.Background, Style: call.EA, Visible: visible}
			px := read(filepath.Join(dir, c.File))
			before := append([]byte(nil), px...)
			pal := pals[c.File[:len(c.File)-4]]
			r.SetTextDraws([]TextDraw{d}, nil)
			out := rawImage(px, pal)
			if n, key := r.paintTextSources(out, px, pal); n != 1 {
				t.Fatalf("%s %s count=%d key=%s", lang, c.File, n, key)
			}
			if !bytes.Equal(before, px) {
				t.Fatal("original pixels modified")
			}
			broken := append([]byte(nil), px...)
			broken[call.Y*320+call.X] ^= 1
			if n, _ := r.paintTextSources(rawImage(broken, pal), broken, pal); n != 0 {
				t.Fatal("corrupt original accepted", c.File)
			}
			verified++
		}
		t.Log(lang, "original phases", verified)
		cityDir := filepath.Join(root, "runs/localization-source-city-r2")
		var cityAudit struct {
			Calls []struct {
				Code                  string
				X, Y, Ink, Background int
				EA                    uint32
			}
			Events []struct {
				Label   string
				Palette [256][3]byte
			}
		}
		var cityCheck struct {
			Results []struct {
				File    string
				Call    int
				Matches []struct{ Characters int }
			}
		}
		if e := json.Unmarshal(read(filepath.Join(cityDir, "audit.json")), &cityAudit); e != nil {
			t.Fatal(e)
		}
		if e := json.Unmarshal(read(filepath.Join(cityDir, "source-check.json")), &cityCheck); e != nil {
			t.Fatal(e)
		}
		cityPals := map[string][256][3]byte{}
		for _, e := range cityAudit.Events {
			cityPals[e.Label] = e.Palette
		}
		messages := 0
		for _, c := range cityCheck.Results {
			call := cityAudit.Calls[c.Call]
			if call.EA != 0x14d74 {
				continue
			}
			if len(c.Matches) == 0 {
				t.Fatal("unverified message", c.File)
			}
			parts, _, ok := r.textSources.glyphs(mustDecodeText(t, call.Code))
			if !ok {
				t.Fatal(call.Code)
			}
			visible := 0
			for _, p := range parts[:c.Matches[len(c.Matches)-1].Characters] {
				visible += len(p)
			}
			d := TextDraw{Code: call.Code, X: call.X, Y: call.Y, Ink: call.Ink, Background: 21, Style: call.EA, Visible: visible}
			px := read(filepath.Join(cityDir, c.File))
			pal := cityPals[c.File[:len(c.File)-4]]
			r.SetTextDraws([]TextDraw{d}, nil)
			if n, key := r.paintTextSources(rawImage(px, pal), px, pal); n != 1 {
				t.Fatalf("%s %s message count=%d %s", lang, c.File, n, key)
			}
			messages++
		}
		t.Log(lang, "original message phases", messages)
		// Static call parameters from IDA sub_12128/sub_12420; source-composed,
		// not a claim that a real city reached the winning ending.
		for _, ending := range []struct{ offset, x, y int }{{0x24a24, 0, 164}, {0x24a41, 0, 180}, {0x24b0b, 32, 32}} {
			end := bytes.IndexByte(exe[ending.offset:], 0)
			raw := exe[ending.offset : ending.offset+end]
			parts, _, ok := r.textSources.glyphs(raw)
			if !ok {
				t.Fatal("ending source glyph")
			}
			px := make([]byte, 64000)
			x := ending.x
			for _, p := range parts {
				if len(p) == 2 {
					stampInterface(px, 320, x, ending.y, r.textSources.zh[uint16(p[0])<<8|uint16(p[1])], 15, 14, 15)
					x += 16
				} else {
					stampInterface(px, 320, x, ending.y+4, r.textSources.ascii[6+(int(p[0])-32)*7:6+(int(p[0])-31)*7], 5, 7, 15)
					x += 6
				}
			}
			r.SetTextDraws([]TextDraw{{Code: hex.EncodeToString(raw), X: ending.x, Y: ending.y, Ink: 15, Style: 0x149b8, Visible: len(raw)}}, nil)
			if n, key := r.paintTextSources(rawImage(px, audit.Events[0].Palette), px, audit.Events[0].Palette); n != 1 {
				t.Fatal("ending source not translated", lang, key)
			}
		}
		// Source-composed image fixtures verify every ROM library phase and text fit.
		for _, s := range images {
			px := bytes.Repeat([]byte{31}, 64000)
			bg := bytes.Repeat([]byte{31}, s.Width*s.Height)
			for y := 0; y < s.Height; y++ {
				for x := 0; x < s.Width; x++ {
					v := s.Pixels[y*s.Width+x]
					if v != 255 {
						px[(y+1)*320+x+1] = v
					}
				}
			}
			pal := audit.Events[0].Palette
			r.SetTextDraws(nil, []TextImageDraw{{ID: s.ID, X: 1, Y: 1, Before: bg}})
			out := rawImage(px, pal)
			n, _ := r.paintTextImages(out, px, pal)
			if n != len(s.Fields) {
				t.Fatalf("%s %s image fields=%d want=%d", lang, s.ID, n, len(s.Fields))
			}
			if gallery != "" {
				writeTextPNG(t, filepath.Join(gallery, lang+"-"+s.ID+".png"), out)
			}
			for _, field := range s.Fields {
				broken := append([]byte(nil), px...)
				broken[(field.Rect.Min.Y+1)*320+field.Rect.Min.X+1] ^= 1
				if n, _ := r.paintTextImages(rawImage(broken, pal), broken, pal); n != len(s.Fields)-1 {
					t.Fatal("occluded image text field accepted", s.ID, n)
				}
			}
			if len(s.Fields) == 1 {
				clipped := s.Fields[0].Rect.Add(image.Pt(1, 1))
				clipped.Min.X++
				r.SetTextDraws(nil, []TextImageDraw{{ID: s.ID, X: 1, Y: 1, Before: bg, Clip: clipped}})
				if n, _ := r.paintTextImages(rawImage(px, pal), px, pal); n != 0 {
					t.Fatal("cropped text field translated", s.ID)
				}
			}
		}
		// All ten rows of the real completed letter, keeping the original layout.
		px := read(filepath.Join(dir, "call-034-full.bin"))
		pal := pals["call-034-full"]
		var draws []TextDraw
		for _, c := range audit.Calls {
			if c.EA == 0x14ed2 {
				draws = append(draws, TextDraw{Code: c.Code, X: c.X, Y: c.Y, Ink: c.Ink, Background: c.Background, Style: c.EA, Visible: len(c.Code) / 2})
			}
		}
		r.SetTextDraws(draws, nil)
		out := rawImage(px, pal)
		if n, _ := r.paintTextSources(out, px, pal); n != 10 {
			t.Fatalf("%s complete letter rows=%d", lang, n)
		}
		shown, stats := r.Render(px, pal, 19, false, true, Origin{})
		if stats.SourceText != 10 || !bytes.Equal(shown.Pix, out.Pix) {
			t.Fatal("production Render differs from reviewed letter prototype", lang, stats.SourceText)
		}
		shown, stats = r.Render(px, pal, 19, false, false, Origin{})
		if stats.SourceText != 0 || stats.SourceImages != 0 || !bytes.Equal(shown.Pix, rawImage(px, pal).Pix) {
			t.Fatal("F12 changed original presentation", lang)
		}
		r.SetTextDraws([]TextDraw{{Code: "deadbeef", X: 0, Y: 0, Ink: 15, Style: 0x149b8}}, nil)
		if n, _ := r.paintTextSources(rawImage(px, pal), px, pal); n != 0 {
			t.Fatal("unknown source translated")
		}
		if gallery != "" {
			writeTextPNG(t, filepath.Join(gallery, lang+"-letter.png"), out)
		}
	}
	corrupt := append([]byte(nil), romA...)
	corrupt[0] ^= 1
	if r.InitTextSources(exe, rom, corrupt) != nil || r.textSources != nil {
		t.Fatal("mismatched original resource accepted")
	}
}

func mustDecodeText(t *testing.T, s string) []byte {
	t.Helper()
	b, e := hex.DecodeString(s)
	if e != nil {
		t.Fatal(e)
	}
	return b
}
func writeTextPNG(t *testing.T, p string, im image.Image) {
	t.Helper()
	f, e := os.Create(p)
	if e != nil {
		t.Fatal(e)
	}
	if e = png.Encode(f, im); e != nil {
		t.Fatal(e)
	}
	if e = f.Close(); e != nil {
		t.Fatal(e)
	}
}
