// #60: replay recorded normal GUI input; diagnostic evidence, not acceptance.
package main

import (
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sort"

	dg "github.com/wicanr2/dosgolem"
)

func main() {
	if len(os.Args) != 3 {
		panic("status.json output-dir")
	}
	var receipt struct {
		Inputs []struct {
			Step    uint64
			Kind    string
			Scan    byte
			X, Y    int
			Buttons uint16
		}
	}
	raw, err := os.ReadFile(os.Args[1])
	must(err)
	must(json.Unmarshal(raw, &receipt))
	out := os.Args[2]
	if _, err := os.Stat(out); !os.IsNotExist(err) {
		panic("output must be new")
	}
	must(os.Mkdir(out, 0700))
	scratch := filepath.Join(out, "saves")
	must(os.Mkdir(scratch, 0700))
	exe, err := os.ReadFile("/orig/RS201.EXE")
	must(err)
	if fmt.Sprintf("%x", sha256.Sum256(exe)) != "798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3" {
		panic("EXE mismatch")
	}
	m := dg.New()
	must(m.LoadEXE(exe))
	m.SetAdLib(true)
	tail := []byte("/A /D /x")
	base := uint32(dg.PSPSeg) * 16
	m.Write8(base+0x80, byte(len(tail)))
	m.WriteBytes(base+0x81, tail)
	m.Write8(base+0x81+uint32(len(tail)), 13)
	d := dg.NewDOS(m, "/orig")
	d.Install()
	defer d.Close()
	d.Scratch, d.BlockingBIOSKeys = scratch, true
	input := 0
	profile := map[uint32]int{}
	writes := []map[string]any{}
	const start, end = uint64(1_158_000_000), uint64(1_300_000_000)
	for m.Steps < end && !d.Exited && !m.CPU.Halted {
		for input < len(receipt.Inputs) && receipt.Inputs[input].Step == m.Steps {
			e := receipt.Inputs[input]
			switch e.Kind {
			case "keyboard":
				m.QueueScanCodes(e.Scan)
			case "mouse-move":
				d.MoveMouse(e.X, e.Y)
			case "mouse-button":
				d.PressMouse(int(e.Buttons))
			}
			input++
		}
		cs, ip := m.CPU.Seg[dg.CS], m.CPU.IP
		head, tail := m.Read16(0x41a), m.Read16(0x41c)
		must(m.Step())
		if m.Steps < start {
			continue
		}
		if m.Read16(0x41a) != head || m.Read16(0x41c) != tail {
			writes = append(writes, map[string]any{"step": m.Steps, "cs": cs, "ip": ip,
				"head_before": head, "tail_before": tail, "head_after": m.Read16(0x41a), "tail_after": m.Read16(0x41c)})
		}
		if m.Steps%4096 == 0 {
			profile[uint32(cs)*16+uint32(ip)]++
		}
	}
	type point struct {
		Linear uint32
		Count  int
	}
	points := []point{}
	for address, count := range profile {
		points = append(points, point{address, count})
	}
	sort.Slice(points, func(i, j int) bool { return points[i].Count > points[j].Count })
	if len(points) > 40 {
		points = points[:40]
	}
	must(os.WriteFile(filepath.Join(out, "frame-index.bin"), m.Indexed(), 0600))
	must(os.WriteFile(filepath.Join(out, "memory.bin"), m.Mem[:], 0600))
	result := map[string]any{"issue": 60, "diagnostic_replay": true, "normal_gui_acceptance": false,
		"input_sha256": fmt.Sprintf("%x", sha256.Sum256(raw)), "steps": m.Steps,
		"profile_start": start, "profile_end": end, "sample_interval": 4096,
		"address_space": "runtime real-mode linear CS*16+IP; add 0xef00 for the fixed IDA input",
		"buffer_writes": writes, "sampled_pc": points, "key_reads": d.KeyReads,
		"key_waits": d.KeyWaits, "key_polls": d.KeyPolls, "irq1": m.KeyIRQs,
		"registers": m.CPU.R, "segments": m.CPU.Seg, "ip": m.CPU.IP, "inputs_replayed": input}
	encoded, err := json.MarshalIndent(result, "", "  ")
	must(err)
	must(os.WriteFile(filepath.Join(out, "diagnostic.json"), append(encoded, '\n'), 0600))
	fmt.Printf("diagnostic steps=%d, buffer changes=%d, keys=%d\n", m.Steps, len(writes), len(d.KeyReads))
}

func must(err error) {
	if err != nil {
		panic(err)
	}
}
