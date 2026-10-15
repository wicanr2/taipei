package original

import (
	"bytes"
	"image"

	dg "github.com/wicanr2/dosgolem"
	"github.com/wicanr2/taipei/preview/internal/hd"
)

// Illustrations observes six original blitters. Unknown calls protect older
// pictures; neither this observer nor the renderer can write original memory.
type Illustrations struct {
	Revision uint64 // Presentation invalidation only; never written to the DOS VM.
	Sources  []hd.IllustrationSource
	Draws    []hd.IllustrationDraw
}

func (t *Illustrations) Observe(m *dg.Machine) {
	if len(t.Sources) == 0 || m.ImageBase != uint32(dg.LoadSeg)*16 || m.CPU.Seg[dg.CS] != dg.LoadSeg+0x57c {
		return
	}
	ea := uint32(m.CPU.Seg[dg.CS])*16 + uint32(m.CPU.IP) - m.ImageBase + 0x10000
	if ea != 0x1605e && ea != 0x160c5 && ea != 0x16129 && ea != 0x16164 && ea != 0x161c3 && ea != 0x16210 {
		return
	}
	t.Revision++
	sp := uint32(m.CPU.Seg[dg.SS])*16 + uint32(m.CPU.R[dg.SP])
	if sp+22 > uint32(len(m.Mem)) {
		return
	}
	arg := func(n uint32) uint16 { return m.Read16(sp + n) }
	d := hd.IllustrationDraw{X: int(arg(4)), Y: int(arg(6)), EA: ea, Key: 255,
		Clip: image.Rect(0, 0, 320, 200), Transparent: ea == 0x1605e || ea == 0x160c5 || ea == 0x16164}
	ptr := uint32(arg(10))*16 + uint32(arg(8))
	sx, sy, w, h := 0, 0, 0, 0
	clipped := ea == 0x161c3 || ea == 0x16210
	if clipped {
		ptr = uint32(arg(6))*16 + uint32(arg(4))
		sx, sy, w, h = int(arg(8)), int(arg(10)), int(arg(12)), int(arg(14))
		dx, dy := int(arg(16)), int(arg(18))
		d.X, d.Y = dx-sx, dy-sy
		d.Clip = image.Rect(dx, dy, dx+w, dy+h)
		d.Transparent, d.Key = ea == 0x16210, byte(arg(20))
	}
	if d.Clip.Empty() || !d.Clip.In(image.Rect(0, 0, 320, 200)) {
		d.Clip = image.Rect(0, 0, 320, 200)
		t.append(d)
		return
	}
	for _, s := range t.Sources {
		compatible := s.Encoding == "iv2" && ea == 0x16164 || s.Encoding == "raw" && (ea == 0x16129 || clipped) || s.Encoding == "zero-color-count-candidate" && (ea == 0x1605e || ea == 0x160c5)
		if !compatible || ptr+uint32(len(s.Raw)) > uint32(len(m.Mem)) || !bytes.Equal(m.Mem[ptr:ptr+uint32(len(s.Raw))], s.Raw) {
			continue
		}
		// 161C3 multiplies AL by CL for the initial row offset, then uses
		// the full 16-bit width as its row stride. A wide source with sy=0
		// is therefore valid; require the actual multiplication to agree.
		if clipped && (sx+w > s.Width || sy+h > s.Height || ea == 0x161c3 && (s.Width&255)*(sy&255) != s.Width*sy) {
			break
		}
		if !clipped && (d.X+s.Width > 320 || d.Y+s.Height > 200) {
			break
		}
		d.ID = s.ID
		if !clipped {
			d.Clip = image.Rect(d.X, d.Y, d.X+s.Width, d.Y+s.Height)
		}
		t.append(d)
		return
	}
	// Safe raw/RLE dimensions protect only their destination. IV2 has no
	// width/height header, so an unknown IV2 call is a full-screen barrier.
	if !clipped && ea != 0x16164 && ptr+4 <= uint32(len(m.Mem)) {
		w, h := int(m.Read16(ptr)), int(m.Read16(ptr+2))
		box := image.Rect(d.X, d.Y, d.X+w, d.Y+h)
		if w > 0 && h > 0 && w <= 320 && h <= 200 && box.In(image.Rect(0, 0, 320, 200)) {
			d.Clip = box
		}
	}
	t.append(d)
}

func (t *Illustrations) append(d hd.IllustrationDraw) {
	next := t.Draws[:0]
	for _, prior := range t.Draws {
		if prior != d {
			next = append(next, prior)
		}
	}
	if len(next) >= 8192 {
		next = next[len(next)-8191:]
	}
	t.Draws = append(next, d)
}
