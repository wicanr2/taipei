package original

import (
	"bytes"
	"os"
	"path/filepath"
	"testing"

	dg "github.com/wicanr2/dosgolem"
)

func TestCameraRejectsUnfinishedAndInvalidOrigin(t *testing.T) {
	dir := os.Getenv("TAIPEI_HD_ORIGINAL")
	if dir == "" {
		t.Skip("需要本機原版 EXE")
	}
	raw, err := os.ReadFile(filepath.Join(dir, "RS201.EXE"))
	if err != nil {
		t.Fatal(err)
	}
	m := dg.New()
	if err = m.LoadEXE(raw); err != nil {
		t.Fatal(err)
	}
	var camera Camera
	if camera.Origin(m).Valid {
		t.Fatal("未完成重繪就採用原點")
	}
	m.CPU.Seg[dg.CS], m.CPU.IP = dg.LoadSeg+0x634, 0x280d
	before := append([]byte(nil), m.Mem...)
	regs, segments, ip, flags := m.CPU.R, m.CPU.Seg, m.CPU.IP, m.CPU.Flags
	camera.Observe(m)
	if !camera.Origin(m).Valid {
		t.Fatal("已核對的原始零原點未採用")
	}
	if !bytes.Equal(before, m.Mem) || regs != m.CPU.R || segments != m.CPU.Seg || ip != m.CPU.IP || flags != m.CPU.Flags {
		t.Fatal("原點觀察改變原版狀態")
	}
	xaddr := uint32(dg.LoadSeg+0x21c8)*16 + 0x79c
	m.Write16(xaddr, 2)
	if camera.Origin(m).Valid {
		t.Fatal("捲動未完成卻採用新原點")
	}
	camera.Observe(m)
	if o := camera.Origin(m); !o.Valid || o.X != 2 {
		t.Fatal(o)
	}
	m.Write16(xaddr, 77)
	camera.Observe(m)
	if camera.Origin(m).Valid {
		t.Fatal("接受超界原點")
	}
	m.Write16(xaddr, 0)
	m.Write16(m.ImageBase+0x2456e, 0)
	camera.Observe(m)
	if camera.Origin(m).Valid {
		t.Fatal("接受失配段指標")
	}
}
