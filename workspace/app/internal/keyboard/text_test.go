package keyboard

import (
	dg "github.com/wicanr2/dosgolem"
	"testing"
)

// 驗送達 BIOS 的文字，涵蓋同幀批次順序、大小寫、標點與修飾狀態恢復。
func TestOrderedTextReachesHardwareBIOS(t *testing.T) {
	for _, mods := range []Modifiers{{}, {LeftShift: true}, {RightShift: true}, {CapsLock: true}, {LeftShift: true, CapsLock: true}} {
		t.Run(string(rune('0'+boolInt(mods.LeftShift)+2*boolInt(mods.RightShift)+4*boolInt(mods.CapsLock))), func(t *testing.T) {
			m := dg.New()
			if err := m.LoadCOM([]byte{0xeb, 0xfe}); err != nil {
				t.Fatal(err)
			}
			d := dg.NewDOS(m, t.TempDir())
			d.Install()
			defer d.Close()
			m.CPU.SetFlags(dg.IF)
			m.KeyEvery = 20
			m.SetNextKey(0)
			if mods.LeftShift {
				m.QueueScanCodes(0x2a)
			}
			if mods.RightShift {
				m.QueueScanCodes(0x36)
			}
			if mods.CapsLock {
				m.QueueScanCodes(0x3a, 0xba)
			}
			const text = "round2A!"
			for _, ch := range text {
				codes, ok := Stroke(ch, mods)
				if !ok {
					t.Fatal(ch)
				}
				m.QueueScanCodes(codes...)
			}
			for i := 0; i < 3000; i++ {
				if err := m.Step(); err != nil {
					t.Fatal(err)
				}
			}
			var got []byte
			for {
				w, ok := m.PopKey()
				if !ok {
					break
				}
				got = append(got, byte(w))
			}
			if string(got) != text {
				t.Fatalf("BIOS read %q, want %q", got, text)
			}
			var want byte
			if mods.LeftShift {
				want |= 2
			}
			if mods.RightShift {
				want |= 1
			}
			if mods.CapsLock {
				want |= 64
			}
			if flags := m.Read8(0x417); flags&67 != want {
				t.Fatalf("modifier flags %x, want %x", flags, want)
			}
		})
	}
}
func boolInt(v bool) int {
	if v {
		return 1
	}
	return 0
}

func TestUnknownTextDoesNotProducePartialStroke(t *testing.T) {
	if codes, ok := Stroke('台', Modifiers{}); ok || len(codes) != 0 {
		t.Fatal("unsupported Unicode must not emit bytes")
	}
}

// 同一次前端更新可同時看到 Shift 按下、放開及大寫文字。
// 收集器須依已排入的通斷碼重建狀態，不能沿用過早的 Shift 狀態。
func TestCompressedShiftTransitionsReachBIOS(t *testing.T) {
	m := dg.New()
	if err := m.LoadCOM([]byte{0xeb, 0xfe}); err != nil {
		t.Fatal(err)
	}
	d := dg.NewDOS(m, t.TempDir())
	d.Install()
	defer d.Close()
	m.CPU.SetFlags(dg.IF)
	m.KeyEvery = 20
	m.SetNextKey(0)
	var mods Modifiers
	queue := func(codes ...byte) {
		m.QueueScanCodes(codes...)
		for _, scan := range codes {
			mods.Feed(scan)
		}
	}
	queue(0x2a, 0xaa)
	codes, ok := Stroke('Y', mods)
	if !ok {
		t.Fatal("uppercase Y unsupported")
	}
	queue(codes...)
	for i := 0; i < 1000; i++ {
		if err := m.Step(); err != nil {
			t.Fatal(err)
		}
	}
	w, ok := m.PopKey()
	if !ok || byte(w) != 'Y' {
		t.Fatalf("BIOS read %#x, want uppercase Y", w)
	}
	if mods.LeftShift || m.Read8(0x417)&3 != 0 {
		t.Fatal("temporary Shift was not released")
	}
}
