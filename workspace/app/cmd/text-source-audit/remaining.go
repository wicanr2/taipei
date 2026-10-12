package main

import (
	"archive/zip"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"image"
	"image/color"
	"image/png"
	"io"
	"os"
	"path/filepath"

	dg "github.com/wicanr2/dosgolem"
)

// Research only. It observes real calls without changing the emulated program.
func remainingAudit(root, receipt, out string, limit uint64) {
	if out == "" {
		panic("missing output directory")
	}
	must(os.Mkdir(out, 0700))
	raw, err := os.ReadFile(filepath.Join(root, "RS201.EXE"))
	must(err)
	if hash(raw) != "798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3" {
		panic("EXE mismatch")
	}
	m := dg.New()
	must(m.LoadEXE(raw))
	m.SetAdLib(true)
	tail := []byte("/A /D /x")
	base := uint32(dg.PSPSeg) * 16
	m.Write8(base+0x80, byte(len(tail)))
	m.WriteBytes(base+0x81, tail)
	m.Write8(base+0x81+uint32(len(tail)), 13)
	d := dg.NewDOS(m, root)
	d.Install()
	defer d.Close()
	d.BlockingBIOSKeys = true
	var replay struct {
		Inputs []struct {
			Step uint64
			Kind string
			Scan byte
		}
	}
	if receipt != "" {
		z, err := zip.OpenReader(receipt)
		must(err)
		defer z.Close()
		for _, f := range z.File {
			if f.Name == "status.json" {
				r, e := f.Open()
				must(e)
				b, e := io.ReadAll(r)
				must(e)
				must(r.Close())
				must(json.Unmarshal(b, &replay))
			}
		}
	}
	type call struct {
		Step                  uint64
		EA                    uint32
		X, Y, Ink, Background uint16
		Pointer               uint32
		Code                  string
		Return                uint32
		End                   uint64
	}
	var calls []call
	var events []map[string]any
	active := -1
	snap := func(label string) {
		px := append([]byte(nil), m.Indexed()...)
		pal := m.Palette()
		must(os.WriteFile(filepath.Join(out, label+".bin"), px, 0600))
		im := image.NewRGBA(image.Rect(0, 0, 320, 200))
		for i, v := range px {
			c := pal[v]
			im.SetRGBA(i%320, i/320, color.RGBA{c[0], c[1], c[2], 255})
		}
		f, e := os.Create(filepath.Join(out, label+".png"))
		must(e)
		must(png.Encode(f, im))
		must(f.Close())
		events = append(events, map[string]any{"step": m.Steps, "label": label, "frame_sha256": hash(px), "palette": pal})
	}
	next := 0
	for m.Steps < limit && !d.Exited && !m.CPU.Halted {
		for next < len(replay.Inputs) && replay.Inputs[next].Step <= m.Steps {
			e := replay.Inputs[next]
			if e.Kind == "keyboard" {
				m.QueueScanCodes(e.Scan)
			}
			next++
		}
		pc := uint32(m.CPU.Seg[dg.CS])*16 + uint32(m.CPU.IP)
		ea := pc - m.ImageBase + 0x10000
		if active >= 0 && pc == calls[active].Return {
			calls[active].End = m.Steps
			snap(fmt.Sprintf("call-%03d-full", active))
			active = -1
		}
		if ea == 0x149b8 || ea == 0x14a92 || ea == 0x14ed2 || ea == 0x14d74 || ea == 0x143da || ea == 0x160c5 || ea == 0x16164 {
			sp := uint32(m.CPU.Seg[dg.SS])*16 + uint32(m.CPU.R[dg.SP])
			arg := func(n uint32) uint16 { return m.Read16(sp + n) }
			ptr := uint32(arg(10))*16 + uint32(arg(8))
			b := []byte{}
			if ea == 0x160c5 || ea == 0x16164 {
				b = append(b, m.Mem[ptr:ptr+128]...)
			}
			for at := uint32(0); at < 512 && ptr+at < uint32(len(m.Mem)); at++ {
				if ea == 0x160c5 || ea == 0x16164 {
					break
				}
				v := m.Read8(ptr + at)
				if v == 0 {
					break
				}
				b = append(b, v)
			}
			c := call{Step: m.Steps, EA: ea, X: arg(4), Y: arg(6), Ink: arg(12), Background: arg(14), Pointer: ptr, Code: hex.EncodeToString(b), Return: uint32(arg(2))*16 + uint32(arg(0))}
			if ea == 0x14d74 {
				c.Background = 21
			}
			calls = append(calls, c)
			active = len(calls) - 1
			snap(fmt.Sprintf("call-%03d-before", active))
			fmt.Printf("call %d EA=%x xy=%d,%d code=%s\n", active, ea, c.X, c.Y, c.Code)
		}
		if (ea == 0x14fe6 || ea == 0x14e97) && active >= 0 {
			snap(fmt.Sprintf("call-%03d-phase-%d", active, m.Steps))
		}
		must(m.Step())
		if d.Blocked && next == len(replay.Inputs) {
			break
		}
	}
	snap("final")
	b, err := json.MarshalIndent(map[string]any{"schema": 1, "input_sha256": hash(raw), "tool": "dosgolem; read-only instruction observer", "address_space": "EA: IDA loader linear; Pointer and Return: runtime physical", "steps": m.Steps, "calls": calls, "events": events, "key_reads": d.KeyReads, "file_ops": d.FileOps, "dos_blocked": d.Blocked, "dos_exited": d.Exited}, "", "  ")
	must(err)
	must(os.WriteFile(filepath.Join(out, "audit.json"), append(b, '\n'), 0600))
	fmt.Printf("observed %d calls, %d frames, %d steps\n", len(calls), len(events), m.Steps)
}
