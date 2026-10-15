package original

import (
	"bytes"
	"encoding/hex"
	"image"

	dg "github.com/wicanr2/dosgolem"
	"github.com/wicanr2/taipei/preview/internal/hd"
)

// Text observes the original call contract indexed in spec/033. It never writes
// the VM, handles keys, or reads translated strings.
type Text struct {
	Revision uint64 // Presentation invalidation only; never written to the DOS VM.
	Draws    []hd.TextDraw
	Images   []hd.TextImageDraw
	Sources  []hd.TextImage
	active   int
	start    uint16
}

// ImageMetadata excludes captured pixels from the lightweight status receipt.
func (t *Text) ImageMetadata() (out []map[string]any) {
	for _, d := range t.Images {
		out = append(out, map[string]any{"id": d.ID, "x": d.X, "y": d.Y, "clip": d.Clip})
	}
	return
}

func (t *Text) Observe(m *dg.Machine) {
	if m.CPU.Seg[dg.CS] != dg.LoadSeg+0x421 && m.CPU.Seg[dg.CS] != dg.LoadSeg+0x57c {
		return
	}
	if m.ImageBase != uint32(dg.LoadSeg)*16 {
		return
	}
	pc := uint32(m.CPU.Seg[dg.CS])*16 + uint32(m.CPU.IP)
	ea := pc - m.ImageBase + 0x10000
	if ea == 0x14e97 || ea == 0x14fe6 {
		t.Revision++
		if t.active >= 0 && t.active < len(t.Draws) {
			d := &t.Draws[t.active]
			if (ea == 0x14e97 && d.Style == 0x14d74) || (ea == 0x14fe6 && d.Style == 0x14ed2) {
				bp := uint32(m.CPU.Seg[dg.SS])*16 + uint32(m.CPU.R[dg.BP])
				n := int(uint16(m.Read16(bp+10) - t.start))
				if n <= len(d.Code)/2 {
					d.Visible = n
				}
			}
		}
		return
	}
	if ea != 0x149b8 && ea != 0x14a92 && ea != 0x14ed2 && ea != 0x14d74 && ea != 0x160c5 && ea != 0x16164 && ea != 0x1605e && ea != 0x16129 && ea != 0x16210 {
		return
	}
	t.Revision++
	sp := uint32(m.CPU.Seg[dg.SS])*16 + uint32(m.CPU.R[dg.SP])
	arg := func(n uint32) uint16 { return m.Read16(sp + n) }
	x, y := int(arg(4)), int(arg(6))
	ptr := uint32(arg(10))*16 + uint32(arg(8))
	if ea == 0x160c5 || ea == 0x16164 || ea == 0x1605e || ea == 0x16129 || ea == 0x16210 {
		clip := image.Rect(0, 0, 320, 200)
		sx, sy, cw, ch := 0, 0, 0, 0
		if ea == 0x16210 {
			ptr = uint32(arg(6))*16 + uint32(arg(4))
			sx, sy, cw, ch = int(arg(8)), int(arg(10)), int(arg(12)), int(arg(14))
			dx, dy := int(arg(16)), int(arg(18))
			clip = image.Rect(dx, dy, dx+cw, dy+ch)
			if cw <= 0 || ch <= 0 || !clip.In(image.Rect(0, 0, 320, 200)) || arg(20) != 255 {
				return
			}
			x, y = dx-sx, dy-sy
		}
		for _, s := range t.Sources {
			if ptr+uint32(len(s.Raw)) > uint32(len(m.Mem)) || !bytes.Equal(m.Mem[ptr:ptr+uint32(len(s.Raw))], s.Raw) {
				continue
			}
			if ea == 0x16210 && (sx+cw > s.Width || sy+ch > s.Height) {
				return
			}
			if ea != 0x16210 && (x < 0 || y < 0 || x+s.Width > 320 || y+s.Height > 200) {
				return
			}
			buffer := uint32(m.Read16(m.ImageBase+0x23216)) * 16
			if buffer+64000 > uint32(len(m.Mem)) {
				return
			}
			before := make([]byte, s.Width*s.Height)
			for row := 0; row < s.Height; row++ {
				if y+row < 0 || y+row >= 200 {
					continue
				}
				left, right := max(0, x), min(320, x+s.Width)
				if left < right {
					copy(before[row*s.Width+left-x:row*s.Width+right-x], m.Mem[buffer+uint32((y+row)*320+left):buffer+uint32((y+row)*320+right)])
				}
			}
			next := t.Images[:0]
			for _, d := range t.Images {
				if d.ID == s.ID && d.X == x && d.Y == y && len(d.Before) == len(before) {
					// Repeated transparent draws may already contain this title.
					// Keep the clean background only if the entire prior composite matches.
					same := true
					for i, v := range s.Pixels {
						if s.Transparent && v == 255 {
							v = d.Before[i]
						}
						if before[i] != v {
							same = false
							break
						}
					}
					if same {
						before = d.Before
					}
				}
				if d.ID != s.ID {
					next = append(next, d)
				}
			}
			t.Images = append(next, hd.TextImageDraw{ID: s.ID, X: x, Y: y, Before: before, Clip: clip})
			return
		}
		return
	}
	if ptr >= uint32(len(m.Mem)) {
		return
	}
	end := ptr
	for end < ptr+512 && end < uint32(len(m.Mem)) && m.Mem[end] != 0 {
		end++
	}
	if end == ptr+512 || end >= uint32(len(m.Mem)) {
		return
	}
	code := hex.EncodeToString(m.Mem[ptr:end])
	next := t.Draws[:0]
	for _, d := range t.Draws {
		if d.X != x || d.Y != y {
			next = append(next, d)
		}
	}
	t.Draws = next
	if len(t.Draws) >= 64 {
		t.Draws = t.Draws[len(t.Draws)-63:]
	}
	visible := int(end - ptr)
	if ea == 0x14d74 || ea == 0x14ed2 {
		visible = 0
	}
	background := int(arg(14))
	if ea == 0x14d74 {
		background = 21
	}
	t.Draws = append(t.Draws, hd.TextDraw{Code: code, X: x, Y: y, Ink: int(arg(12)), Background: background, Style: ea, Visible: visible})
	t.active = len(t.Draws) - 1
	t.start = arg(8)
}
