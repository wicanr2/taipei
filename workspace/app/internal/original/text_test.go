package original

import (
	"bytes"
	"encoding/hex"
	"os"
	"path/filepath"
	"testing"

	dg "github.com/wicanr2/dosgolem"
	"github.com/wicanr2/taipei/preview/internal/hd"
)

func TestTextObserverReadOnlyAndOriginalProgress(t *testing.T) {
	dir := os.Getenv("TAIPEI_HD_ORIGINAL")
	if dir == "" {
		t.Skip("requires local original EXE")
	}
	raw, err := os.ReadFile(filepath.Join(dir, "RS201.EXE"))
	if err != nil {
		t.Fatal(err)
	}
	m := dg.New()
	if err = m.LoadEXE(raw); err != nil {
		t.Fatal(err)
	}
	m.CPU.Seg[dg.CS], m.CPU.IP = dg.LoadSeg+0x421, 0xb64
	m.CPU.Seg[dg.SS], m.CPU.R[dg.SP] = 0x9000, 0x100
	sp := uint32(0x90100)
	for off, value := range map[uint32]uint16{4: 19, 6: 177, 8: 0x20, 10: 0x8000, 12: 32, 14: 0} {
		m.Write16(sp+off, value)
	}
	code := []byte{0xa4, 0x40, 0xa4, 0x42}
	copy(m.Mem[0x80020:], append(code, 0))
	var observer Text
	check := func() {
		before := append([]byte(nil), m.Mem...)
		regs, segs, ip, flags, steps := m.CPU.R, m.CPU.Seg, m.CPU.IP, m.CPU.Flags, m.Steps
		observer.Observe(m)
		if !bytes.Equal(before, m.Mem) || regs != m.CPU.R || segs != m.CPU.Seg || ip != m.CPU.IP || flags != m.CPU.Flags || steps != m.Steps {
			t.Fatal("observer changed DOS state")
		}
	}
	check()
	if len(observer.Draws) != 1 || observer.Draws[0].Code != hex.EncodeToString(code) || observer.Draws[0].Visible != 0 {
		t.Fatal(observer.Draws)
	}
	m.CPU.IP = 0xc87 // runtime EA 14E97h, after original publish
	m.CPU.R[dg.BP] = 0x200
	m.Write16(0x9020a, 0x22)
	check()
	if observer.Draws[0].Visible != 2 {
		t.Fatal(observer.Draws)
	}
	m.Write16(0x9020a, 0xffff)
	check()
	if observer.Draws[0].Visible != 2 {
		t.Fatal("accepted out-of-range progress")
	}
	// Image background is copied from the original off-screen buffer, not VRAM.
	source := hd.TextImage{ID: "test", Raw: []byte{1, 2, 3}, Pixels: []byte{14, 255, 255, 14}, Transparent: true, Width: 2, Height: 2}
	observer.Sources = []hd.TextImage{source}
	copy(m.Mem[0x80020:], source.Raw)
	m.CPU.Seg[dg.CS], m.CPU.IP = dg.LoadSeg+0x57c, 0x905
	m.Write16(sp+4, 1)
	m.Write16(sp+6, 2)
	m.Write16(m.ImageBase+0x23216, 0x7000)
	copy(m.Mem[0x70000+641:], []byte{7, 8})
	copy(m.Mem[0x70000+961:], []byte{9, 10})
	check()
	if len(observer.Images) != 1 || !bytes.Equal(observer.Images[0].Before, []byte{7, 8, 9, 10}) {
		t.Fatal(observer.Images)
	}
	copy(m.Mem[0x70000+641:], []byte{14, 8})
	copy(m.Mem[0x70000+961:], []byte{9, 14})
	check()
	if !bytes.Equal(observer.Images[0].Before, []byte{7, 8, 9, 10}) {
		t.Fatal("repeated transparent draw lost clean background")
	}
	m.Mem[0x70000+641] = 99
	if observer.Images[0].Before[0] != 7 {
		t.Fatal("background aliases DOS memory")
	}
	// Cropped raw drawing keeps the original source origin and actual visible clip.
	m.CPU.IP = 0xa50
	for off, value := range map[uint32]uint16{4: 0x20, 6: 0x8000, 8: 1, 10: 0, 12: 1, 14: 2, 16: 58, 18: 30, 20: 255} {
		m.Write16(sp+off, value)
	}
	check()
	d := observer.Images[0]
	if d.X != 57 || d.Y != 30 || d.Clip.Min.X != 58 || d.Clip.Dx() != 1 || d.Clip.Dy() != 2 {
		t.Fatal(d)
	}
}
