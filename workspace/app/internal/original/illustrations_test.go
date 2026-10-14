package original

import (
	"bytes"
	"image"
	"testing"

	dg "github.com/wicanr2/dosgolem"
	"github.com/wicanr2/taipei/preview/internal/hd"
)

func TestIllustrationObserverABIAndReadOnly(t *testing.T) {
	m := dg.New()
	m.ImageBase = uint32(dg.LoadSeg) * 16
	m.CPU.Seg[dg.CS] = dg.LoadSeg + 0x57c
	m.CPU.Seg[dg.SS], m.CPU.R[dg.SP] = 0x9000, 0x100
	sp := uint32(0x90100)
	for _, ea := range []uint32{0x1605e, 0x160c5, 0x16129, 0x16164, 0x161c3, 0x16210} {
		encoding := "raw"
		if ea == 0x1605e || ea == 0x160c5 {
			encoding = "zero-color-count-candidate"
		}
		if ea == 0x16164 {
			encoding = "iv2"
		}
		source := hd.IllustrationSource{ID: "fixture", Encoding: encoding, Raw: []byte{2, 0, 2, 0, 1, 2, 3, 255}, Pixels: []byte{1, 2, 3, 255}, Width: 2, Height: 2}
		copy(m.Mem[0x80020:], source.Raw)
		m.CPU.IP = uint16(ea - 0x10000 - 0x57c0)
		for off, v := range map[uint32]uint16{4: 10, 6: 20, 8: 0x20, 10: 0x8000} {
			m.Write16(sp+off, v)
		}
		clipped := ea == 0x161c3 || ea == 0x16210
		if clipped {
			for off, v := range map[uint32]uint16{4: 0x20, 6: 0x8000, 8: 1, 10: 0, 12: 1, 14: 2, 16: 10, 18: 20, 20: 7} {
				m.Write16(sp+off, v)
			}
		}
		observer := Illustrations{Sources: []hd.IllustrationSource{source}}
		before := append([]byte(nil), m.Mem...)
		cpu, steps := m.CPU, m.Steps
		observer.Observe(m)
		if !bytes.Equal(before, m.Mem) || cpu != m.CPU || steps != m.Steps {
			t.Fatal("observer changed VM")
		}
		if len(observer.Draws) != 1 || observer.Draws[0].ID != "fixture" {
			t.Fatal(ea, observer.Draws)
		}
		d := observer.Draws[0]
		if clipped && (d.X != 9 || d.Y != 20 || d.Clip != image.Rect(10, 20, 11, 22)) {
			t.Fatal("clipped ABI", d)
		}
		if ea == 0x16210 && (!d.Transparent || d.Key != 7) {
			t.Fatal("actual key lost")
		}
		observer.Observe(m)
		if len(observer.Draws) != 1 {
			t.Fatal("duplicate instance retained")
		}
		m.Mem[0x80024] ^= 1
		observer.Observe(m)
		if observer.Draws[len(observer.Draws)-1].ID != "" {
			t.Fatal("changed source accepted")
		}
	}
	// The original initial offset uses AL*CL, while the row stride is BX.
	// Wide sources at sy=0 remain exact; a nonzero unequal offset falls back.
	wide := hd.IllustrationSource{ID: "wide", Encoding: "raw", Width: 296, Height: 114, Raw: make([]byte, 4+296*114), Pixels: make([]byte, 296*114)}
	copy(wide.Raw, []byte{40, 1, 114, 0})
	copy(m.Mem[0x80020:], wide.Raw)
	m.CPU.IP = 0x161c3 - 0x10000 - 0x57c0
	for off, v := range map[uint32]uint16{4: 0x20, 6: 0x8000, 8: 10, 10: 0, 12: 204, 14: 110, 16: 58, 18: 33} {
		m.Write16(sp+off, v)
	}
	observer := Illustrations{Sources: []hd.IllustrationSource{wide}}
	observer.Observe(m)
	if len(observer.Draws) != 1 || observer.Draws[0].ID != "wide" || observer.Draws[0].X != 48 {
		t.Fatal("valid wide zero-row clip rejected", observer.Draws)
	}
	m.Write16(sp+10, 1)
	observer.Observe(m)
	if observer.Draws[len(observer.Draws)-1].ID != "" {
		t.Fatal("unequal AL*CL offset accepted")
	}
}
