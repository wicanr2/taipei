package main

import (
	"encoding/binary"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"

	dg "github.com/wicanr2/dosgolem"
	"github.com/wicanr2/taipei/preview/internal/hd"
)

// #46: read-only input planning from the exact original sub_1A64C predicate.
// The normal GUI must still navigate and execute the original constructor.
func dumpNuclearSite(m *dg.Machine, exe []byte, out string, origin hd.Origin) {
	proofBytes, e := os.ReadFile("/workspace/runs/ida-46/nuclear-dimensions.json")
	must(e)
	var proof struct {
		InputSHA string `json:"input_sha256"`
		Version  string `json:"ida_version"`
		Data     []struct {
			EA   uint32 `json:"ida_ea"`
			File int    `json:"file_offset"`
		}
	}
	must(json.Unmarshal(proofBytes, &proof))
	if proof.InputSHA != hash(exe) || proof.Version != "9.4" {
		panic("IDA evidence mismatch")
	}
	header := int(binary.LittleEndian.Uint16(exe[8:])) * 16
	slots := map[uint32]uint32{}
	locations := []map[string]any{}
	for _, d := range proof.Data {
		if d.File < header || d.File+4 > len(exe) {
			panic("data file offset")
		}
		address := m.ImageBase + uint32(d.File-header)
		slots[d.EA] = address
		locations = append(locations, map[string]any{"ida_loader_ea": d.EA, "exe_file_offset": d.File,
			"mz_load_offset": d.File - header, "runtime_slot_linear": address})
	}
	for _, ea := range []uint32{0x322be, 0x322d8, 0x322f0, 0x3233c} {
		if slots[ea] == 0 {
			panic("missing data locator")
		}
	}
	width, height := int(m.Read16(slots[0x322f0])), int(m.Read16(slots[0x3233c]))
	if width != 105 || height != 89 || width*height != 0x2481 {
		panic(fmt.Sprintf("unexpected native dimensions %d %d", width, height))
	}
	far := func(slot uint32) uint32 { return uint32(m.Read16(slot)) + uint32(m.Read16(slot+2))*16 }
	a, b := far(slots[0x322be]), far(slots[0x322d8])
	count := uint32(width * height)
	if a == 0 || b == 0 || a+count > uint32(len(m.Mem)) || b+count > uint32(len(m.Mem)) {
		panic("native array bounds")
	}
	types, variants := m.Mem[a:a+count], m.Mem[b:b+count]
	must(os.WriteFile(filepath.Join(out, "dword_322BE.bin"), types, 0600))
	must(os.WriteFile(filepath.Join(out, "dword_322D8.bin"), variants, 0600))
	positions := []map[string]any{}
	for y := 2; y < height-7; y++ {
		for x := 2; x < width-7; x++ {
			ok := true
			for dy := 0; dy < 6 && ok; dy++ {
				for dx := 0; dx < 6; dx++ {
					at := (y+dy)*width + x + dx
					if types[at] != 0 || variants[at] == 0 {
						ok = false
						break
					}
				}
			}
			if !ok {
				continue
			}
			cx, cy := max(0, min(76, (x-8)/2*2)), max(0, min(74, (y-4)/2*2))
			col, row := x-cx, y-cy
			if col < 2 || col > 15 || row < 2 || row > 7 {
				continue
			}
			positions = append(positions, map[string]any{"world": [2]int{x, y}, "camera": [2]int{cx, cy}, "cell": [2]int{col, row}})
		}
	}
	visible := []map[string]any{}
	for y := 0; y < 15; y++ {
		for x := 0; x < 29; x++ {
			at := (origin.Y+y)*width + origin.X + x
			visible = append(visible, map[string]any{"cell": [2]int{x, y}, "world": [2]int{origin.X + x, origin.Y + y},
				"dword_322BE_value": types[at], "dword_322D8_value": variants[at]})
		}
	}
	report := map[string]any{"issue": 46, "read_only": true, "state_injection": false, "checkpoint": false,
		"steps": m.Steps, "origin": origin, "input_sha256": hash(exe), "ida_evidence_sha256": hash(proofBytes),
		"mz_header_bytes": header, "image_base": m.ImageBase, "locators": locations,
		"dimensions": [2]int{width, height}, "allocation_bytes": 0x2481,
		"runtime_dword_322BE_linear": a, "runtime_dword_322D8_linear": b,
		"dword_322BE_sha256": hash(types), "dword_322D8_sha256": hash(variants),
		"predicate":     "IDA sub_1A64C 0x1A64C–0x1A715: each of 6x6 has dword_322BE byte==0 and dword_322D8 byte!=0",
		"visible_cells": visible, "candidates": positions,
		"level": "original instructions confirmed; candidate usability is strong inference until normal GUI construction",
		"scope": "原版EXE及實際GUI輸入重播後唯讀選址；正常方向鍵捲動、原版施工及存讀另驗，不代替玩家路徑"}
	encoded, e := json.MarshalIndent(report, "", "  ")
	must(e)
	must(os.WriteFile(filepath.Join(out, "site-audit.json"), append(encoded, '\n'), 0600))
	fmt.Printf("SITE AUDIT candidates=%d dimensions=%dx%d\n", len(positions), width, height)
}
