// #31：正常輸入的唯讀文字來源與字模繪製研究，不接入產品呈現。
package main

import (
	"archive/zip"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"os"
	"path/filepath"

	dg "github.com/wicanr2/dosgolem"
)

func must(err error) {
	if err != nil {
		panic(err)
	}
}

func hash(data []byte) string { return fmt.Sprintf("%x", sha256.Sum256(data)) }

type textCall struct {
	Step      uint64 `json:"step"`
	X, Y      uint16
	Color     uint16 `json:"color"`
	Pointer   uint32 `json:"runtime_pointer"`
	Bytes     string `json:"bytes_hex"`
	Return    uint32 `json:"runtime_return"`
	Completed bool   `json:"completed"`
}

type glyphCall struct {
	Step       uint64 `json:"step"`
	Kind       string `json:"kind"`
	X, Y       uint16
	Color      byte   `json:"color"`
	Pointer    uint32 `json:"runtime_glyph_pointer"`
	Buffer     uint32 `json:"runtime_buffer_base"`
	Bytes      string `json:"glyph_bytes_hex"`
	Before     string `json:"before_hex"`
	After      string `json:"after_hex"`
	Return     uint32 `json:"runtime_return"`
	Completed  bool   `json:"completed"`
	ParentText int    `json:"parent_text_call"`
	Width      int    `json:"width"`
	Height     int    `json:"height"`
}

func main() {
	root := flag.String("original", "/orig", "唯讀原版目錄")
	receipt := flag.String("receipt", "", "正常 GUI 輸入收據")
	out := flag.String("out", "", "本機研究 JSON")
	expected := flag.String("expected-state", "", "既有同輸入原版狀態 SHA-256")
	flag.Parse()
	z, err := zip.OpenReader(*receipt)
	must(err)
	defer z.Close()
	var capture struct {
		Steps  uint64
		Inputs []struct {
			Step uint64
			Kind string
			Scan byte
		}
	}
	for _, file := range z.File {
		if file.Name == "status.json" {
			r, err := file.Open()
			must(err)
			raw, err := io.ReadAll(r)
			must(err)
			must(r.Close())
			must(json.Unmarshal(raw, &capture))
		}
	}
	if capture.Steps == 0 || *out == "" {
		panic("缺少正常 GUI 收據或輸出路徑")
	}
	raw, err := os.ReadFile(filepath.Join(*root, "RS201.EXE"))
	must(err)
	if hash(raw) != "798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3" {
		panic("EXE 不符")
	}
	m := dg.New()
	must(m.LoadEXE(raw))
	m.SetAdLib(true)
	tail := []byte("/A /D /x")
	base := uint32(dg.PSPSeg) * 16
	m.Write8(base+0x80, byte(len(tail)))
	m.WriteBytes(base+0x81, tail)
	m.Write8(base+0x81+uint32(len(tail)), 13)
	dos := dg.NewDOS(m, *root)
	dos.Install()
	defer dos.Close()
	dos.BlockingBIOSKeys = true
	texts := []textCall{}
	glyphs := []glyphCall{}
	activeText, activeGlyph := -1, -1
	read := func(address uint32, size int) []byte {
		if uint64(address)+uint64(size) > uint64(len(m.Mem)) {
			panic("觀察地址超界")
		}
		return append([]byte(nil), m.Mem[int(address):int(address)+size]...)
	}
	region := func(g glyphCall) []byte {
		if int(g.X)+g.Width > 320 || int(g.Y)+g.Height > 200 {
			panic("字模研究出現未確認的裁切座標")
		}
		pixels := make([]byte, 0, g.Width*g.Height)
		for row := 0; row < g.Height; row++ {
			pixels = append(pixels, read(g.Buffer+uint32((int(g.Y)+row)*320+int(g.X)), g.Width)...)
		}
		return pixels
	}
	next := 0
	for m.Steps < capture.Steps {
		for next < len(capture.Inputs) && m.Steps >= capture.Inputs[next].Step {
			event := capture.Inputs[next]
			if event.Kind == "keyboard" {
				m.QueueScanCodes(event.Scan)
			}
			next++
		}
		pc := uint32(m.CPU.Seg[dg.CS])*16 + uint32(m.CPU.IP)
		if activeGlyph >= 0 && pc == glyphs[activeGlyph].Return {
			g := &glyphs[activeGlyph]
			before, err := hex.DecodeString(g.Before)
			must(err)
			data, err := hex.DecodeString(g.Bytes)
			must(err)
			after := region(*g)
			for y := 0; y < g.Height; y++ {
				for x := 0; x < g.Width; x++ {
					var ink bool
					if g.Kind == "chinese" {
						ink = data[y*2+x/8]&(1<<uint(7-x%8)) != 0
					} else {
						ink = data[y]&(1<<uint(7-x)) != 0
					}
					want := before[y*g.Width+x]
					if ink {
						want = g.Color
					}
					if after[y*g.Width+x] != want {
						panic(fmt.Sprintf("字模繪製不符，step=%d xy=%d,%d", g.Step, x, y))
					}
				}
			}
			g.After, g.Completed = hex.EncodeToString(after), true
			activeGlyph = -1
		}
		if activeText >= 0 && pc == texts[activeText].Return {
			texts[activeText].Completed = true
			activeText = -1
		}
		if m.ImageBase != uint32(dg.LoadSeg)*16 {
			panic("未知載入基址")
		}
		ea := pc - m.ImageBase + 0x10000
		if ea == 0x143da || ea == 0x15a99 || ea == 0x15bce {
			stack := uint32(m.CPU.Seg[dg.SS])*16 + uint32(m.CPU.R[dg.SP])
			arg := func(offset uint32) uint16 { return m.Read16(stack + offset) }
			pointer := uint32(arg(10))*16 + uint32(arg(8))
			ret := uint32(arg(2))*16 + uint32(arg(0))
			if ea == 0x143da {
				if activeText >= 0 || len(texts) >= 8192 {
					panic("未確認的文字巢狀或數量")
				}
				data := read(pointer, 512)
				end := 0
				for end < len(data) && data[end] != 0 {
					end++
				}
				if end == len(data) {
					panic("文字沒有有界結尾")
				}
				texts = append(texts, textCall{Step: m.Steps, X: arg(4), Y: arg(6), Color: arg(12),
					Pointer: pointer, Bytes: hex.EncodeToString(data[:end]), Return: ret})
				activeText = len(texts) - 1
			} else {
				if activeGlyph >= 0 || len(glyphs) >= 65536 {
					panic("未確認的字模巢狀或數量")
				}
				g := glyphCall{Step: m.Steps, Kind: "ascii", X: arg(4), Y: arg(6), Color: byte(arg(12)),
					Pointer: pointer, Return: ret, ParentText: activeText, Width: 5, Height: 7}
				count := 7
				if ea == 0x15a99 {
					g.Kind, g.Width, g.Height, count = "chinese", 15, 14, 30
				}
				if m.CPU.Seg[dg.DS] != dg.LoadSeg+0x2243 {
					panic("字模繪製的 DS 不符固定來源")
				}
				data := uint32(m.CPU.Seg[dg.DS])*16 + 0xde4
				g.Buffer = uint32(m.Read16(data+2)) * 16 // 原版忽略 pointer 的 offset，重算 DI。
				g.Bytes = hex.EncodeToString(read(pointer, count))
				g.Before = hex.EncodeToString(region(g))
				glyphs = append(glyphs, g)
				activeGlyph = len(glyphs) - 1
			}
		}
		must(m.Step())
	}
	state, err := json.Marshal(map[string]any{
		"memory_sha256": hash(m.Mem), "frame_sha256": hash(m.Indexed()), "palette": m.Palette(),
		"registers": m.CPU.R, "segments": m.CPU.Seg, "ip": m.CPU.IP, "flags": m.CPU.Flags,
		"steps": m.Steps, "ticks": m.Ticks, "ports": m.Ports, "opl_regs": m.OPLRegs(0),
		"key_reads": dos.KeyReads, "dos_blocked": dos.Blocked, "dos_exited": dos.Exited,
	})
	must(err)
	if len(texts) == 0 || len(glyphs) == 0 || (*expected != "" && hash(state) != *expected) {
		panic("缺少實際文字或原版狀態不符既有基線")
	}
	result, err := json.MarshalIndent(map[string]any{
		"schema": 1, "input_sha256": hash(raw), "steps": m.Steps,
		"scope":         "read-only normal-input text/glyph call evidence; no HD text implementation",
		"address_space": "runtime physical addresses; IDA targets 143DAh,15A99h,15BCEh are loader linear",
		"state_sha256":  hash(state), "expected_state_sha256": *expected,
		"text_calls": texts, "glyph_calls": glyphs,
	}, "", "  ")
	must(err)
	must(os.WriteFile(*out, append(result, '\n'), 0600))
	fmt.Printf("text calls=%d glyphs=%d state=%s\n", len(texts), len(glyphs), hash(state))
}
