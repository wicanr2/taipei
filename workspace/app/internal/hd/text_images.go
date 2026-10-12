package hd

import (
	"bytes"
	"image"
	"image/color"
	"image/draw"
)

func (r *Renderer) paintTextImages(dst *image.RGBA, px []byte, pal [256][3]byte) (int, string) {
	r.lastImageKeys = nil
	if r.textSources == nil || r.locale == nil || r.locale.reason != "" {
		return 0, ""
	}
	n, last := 0, ""
	seen := map[image.Rectangle]bool{}
	for _, d := range r.textImageDraws {
		for _, s := range r.textSources.images {
			if s.ID != d.ID || len(d.Before) != s.Width*s.Height {
				continue
			}
			for _, field := range s.Fields {
				box := field.Rect
				native := box.Add(image.Pt(d.X, d.Y))
				if !d.Clip.Empty() && !native.In(d.Clip) {
					continue
				}
				if seen[native] || !box.In(image.Rect(0, 0, s.Width, s.Height)) || !native.In(image.Rect(0, 0, 320, 200)) {
					continue
				}
				expected := make([]byte, box.Dx()*box.Dy())
				background := make([]byte, len(expected))
				for y := 0; y < box.Dy(); y++ {
					for x := 0; x < box.Dx(); x++ {
						at := (box.Min.Y+y)*s.Width + box.Min.X + x
						v := s.Pixels[at]
						background[y*box.Dx()+x] = d.Before[at]
						if s.Transparent && v == 255 {
							v = d.Before[at]
						}
						expected[y*box.Dx()+x] = v
					}
				}
				if !bytes.Equal(footerCrop(px, native), expected) {
					continue
				}
				patch := image.NewRGBA(image.Rect(0, 0, box.Dx()*4, box.Dy()*4))
				target := patch.Bounds()
				ink := field.Ink
				for y := 0; y < box.Dy(); y++ {
					for x := 0; x < box.Dx(); x++ {
						v := field.Background
						if field.Key == "startup.title" {
							v = background[y*box.Dx()+x]
							ink = 14
						}
						if field.Key == "art.protest" {
							v = expected[y*box.Dx()+x]
							if v == 15 {
								v = field.Background
							}
						}
						c := pal[v]
						draw.Draw(patch, image.Rect(x*4, y*4, (x+1)*4, (y+1)*4), image.NewUniform(color.RGBA{c[0], c[1], c[2], 255}), image.Point{}, draw.Src)
					}
				}
				if field.Key == "art.protest" {
					fit := imageGreenSafe(s, box, field.Background).Inset(1)
					target = image.Rect((fit.Min.X-box.Min.X)*4, (fit.Min.Y-box.Min.Y)*4, (fit.Max.X-box.Min.X)*4, (fit.Max.Y-box.Min.Y)*4)
				}
				fg := pal[ink]
				if e := r.locale.ui.DrawReveal(patch, r.locale.language, field.Key, target, 112, 12, 1, 1, color.RGBA{fg[0], fg[1], fg[2], 255}); e != nil {
					continue
				}
				draw.Draw(dst, patch.Bounds().Add(image.Pt(native.Min.X*4, native.Min.Y*4)), patch, image.Point{}, draw.Src)
				seen[native] = true
				n++
				r.lastImageKeys = append(r.lastImageKeys, field.Key)
				last = field.Key
			}
		}
	}
	return n, last
}

func imageGreenSafe(s TextImage, box image.Rectangle, green byte) image.Rectangle {
	best := image.Rectangle{}
	for top := box.Min.Y; top < box.Max.Y; top++ {
		valid := make([]bool, box.Dx())
		for i := range valid {
			valid[i] = true
		}
		for bottom := top; bottom < box.Max.Y; bottom++ {
			start := 0
			for x := 0; x <= len(valid); x++ {
				if x < len(valid) {
					v := s.Pixels[bottom*s.Width+box.Min.X+x]
					valid[x] = valid[x] && (v == green || v == 15)
				}
				if x == len(valid) || !valid[x] {
					candidate := image.Rect(box.Min.X+start, top, box.Min.X+x, bottom+1)
					if candidate.Dx()*candidate.Dy() > best.Dx()*best.Dy() {
						best = candidate
					}
					start = x + 1
				}
			}
		}
	}
	return best
}
