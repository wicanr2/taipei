// Package original holds game-specific, read-only adapters for the verified EXE.
package original

import (
	dg "github.com/wicanr2/dosgolem"
	"github.com/wicanr2/taipei/preview/internal/hd"
)

// Camera observes the original renderer's completion, never a guessed cursor.
// Locations and original operands are indexed in docs/re/006-map-origin.md.
type Camera struct {
	completed hd.Origin
	Draws     uint64
}

func readOrigin(m *dg.Machine) hd.Origin {
	base := m.ImageBase
	if base != uint32(dg.LoadSeg)*16 {
		return hd.Origin{}
	}
	xseg := m.Read16(base + 0x2456e) // IDA seg_3456E; MZ file 2656Eh.
	yseg := m.Read16(base + 0x24570) // IDA seg_34570; MZ file 26570h.
	if xseg != dg.LoadSeg+0x21c8 || yseg != dg.LoadSeg+0x21c8 {
		return hd.Origin{}
	}
	x := int(m.Read16(uint32(xseg)*16 + 0x79c)) // word_3241C.
	y := int(m.Read16(uint32(yseg)*16 + 0x7a0)) // word_32420.
	return hd.Origin{X: x, Y: y, Valid: x <= 76 && y <= 74}
}

// Observe runs before an emulated instruction, without changing that instruction.
func (c *Camera) Observe(m *dg.Machine) {
	if m.CPU.Seg[dg.CS] == dg.LoadSeg+0x634 && m.CPU.IP == 0x280d {
		c.completed = readOrigin(m) // IDA 18B4Dh, after drawing and cursor calls.
		c.Draws++
	}
}

func (c *Camera) Origin(m *dg.Machine) hd.Origin {
	now := readOrigin(m)
	if !c.completed.Valid || !now.Valid || now.X != c.completed.X || now.Y != c.completed.Y {
		return hd.Origin{}
	}
	return now
}
