// #46 DRAFT: replay actual GUI input from EXE, then continue native city/save UI.
package main

import (
	"archive/zip"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strconv"
	"strings"

	dg "github.com/wicanr2/dosgolem"
	"github.com/wicanr2/taipei/preview/internal/hd"
	"github.com/wicanr2/taipei/preview/internal/i18n"
	"github.com/wicanr2/taipei/preview/internal/keyboard"
	"github.com/wicanr2/taipei/preview/internal/original"
)

func must(err error) {
	if err != nil {
		panic(err)
	}
}
func hash(p []byte) string { return fmt.Sprintf("%x", sha256.Sum256(p)) }
func normalized(v any) string {
	b, e := json.Marshal(v)
	must(e)
	var x any
	must(json.Unmarshal(b, &x))
	b, e = json.Marshal(x)
	must(e)
	return string(b)
}

func main() {
	if len(os.Args) != 3 && len(os.Args) != 4 {
		panic("GUI-capture.zip new-output-dir [inspect]")
	}
	z, e := zip.OpenReader(os.Args[1])
	must(e)
	defer z.Close()
	var captured struct {
		Steps    uint64
		FrameSHA string `json:"frame_index_sha256"`
		Palette  [256][3]byte
		Mode     int
		Blocked  bool            `json:"dos_blocked"`
		Origin   hd.Origin       `json:"map_origin"`
		Reads    json.RawMessage `json:"key_reads"`
		Files    json.RawMessage `json:"file_ops"`
		Inputs   []struct {
			Step    uint64
			Kind    string
			Scan    byte
			X, Y    int
			Buttons uint16
		}
	}
	var capturedFrame []byte
	for _, f := range z.File {
		if f.Name == "frame-index.bin" {
			rd, e := f.Open()
			must(e)
			capturedFrame, e = io.ReadAll(rd)
			must(e)
			must(rd.Close())
		}
		if f.Name == "status.json" {
			r, e := f.Open()
			must(e)
			b, e := io.ReadAll(r)
			must(e)
			must(r.Close())
			must(json.Unmarshal(b, &captured))
		}
	}
	if captured.Steps == 0 {
		panic("missing receipt")
	}
	inputBytes, e := os.ReadFile(os.Args[1])
	must(e)
	if hash(inputBytes) != "110d7b85a6148743f876f8e41298b9157c460a833f24c9fb062ec31c3ced6534" {
		panic("unregistered GUI prefix")
	}
	rom, e := os.ReadFile("/orig/RS201.ROM")
	must(e)
	r := hd.New(rom, "/workspace/prototypes/hd-style")
	if why := r.SetLanguage(i18n.Bundled(), "zh-Hant"); why != "matched-menu" {
		panic("renderer setup: " + why)
	}
	_, checked := r.Render(capturedFrame, captured.Palette, captured.Mode, captured.Blocked, true, captured.Origin)
	if checked.FooterMask&2 == 0 || strings.TrimSpace(checked.FooterText[3]) != "98428" {
		panic(fmt.Sprintf("captured original footer setup failed: %+v", checked))
	}
	if len(os.Args) == 4 {
		if os.Args[3] != "inspect" {
			panic("unknown mode")
		}
		b, e := json.MarshalIndent(checked, "", "  ")
		must(e)
		fmt.Println(string(b))
		return
	}
	out := os.Args[2]
	if _, e := os.Stat(out); !os.IsNotExist(e) {
		panic("output must be new")
	}
	must(os.Mkdir(out, 0700))
	scratch := filepath.Join(out, "saves")
	must(os.Mkdir(scratch, 0700))
	exe, e := os.ReadFile("/orig/RS201.EXE")
	must(e)
	if hash(exe) != "798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3" {
		panic("EXE mismatch")
	}
	m := dg.New()
	must(m.LoadEXE(exe))
	m.SetAdLib(true)
	tail := []byte("/A /D /x")
	psp := uint32(dg.PSPSeg) * 16
	m.Write8(psp+0x80, byte(len(tail)))
	m.WriteBytes(psp+0x81, tail)
	m.Write8(psp+0x81+uint32(len(tail)), 13)
	d := dg.NewDOS(m, "/orig")
	d.Install()
	defer d.Close()
	d.Scratch = scratch
	d.BlockingBIOSKeys = true
	var camera original.Camera
	step := func() {
		camera.Observe(m)
		must(m.Step())
		if m.CPU.Halted && !d.Exited {
			panic("CPU halted")
		}
	}
	next := 0
	var mods keyboard.Modifiers
	progress := uint64(1000000000)
	for m.Steps < captured.Steps {
		for next < len(captured.Inputs) && m.Steps >= captured.Inputs[next].Step {
			ev := captured.Inputs[next]
			switch ev.Kind {
			case "keyboard":
				m.QueueScanCodes(ev.Scan)
				mods.Feed(ev.Scan)
			case "mouse-move":
				d.MoveMouse(ev.X, ev.Y)
			case "mouse-button":
				d.PressMouse(int(ev.Buttons))
			case "text":
				// Text metadata is followed by the actual Stroke scan codes.
				paired := false
				for j := next + 1; j < len(captured.Inputs) && captured.Inputs[j].Step == ev.Step; j++ {
					paired = paired || captured.Inputs[j].Kind == "keyboard"
				}
				if !paired {
					panic("text event lacks recorded scan codes")
				}
			default:
				panic("unsupported input kind: " + ev.Kind)
			}
			next++
		}
		step()
		if m.Steps >= progress {
			fmt.Fprintf(os.Stderr, "replay %d/%d\n", m.Steps, captured.Steps)
			progress += 1000000000
		}
	}
	if hash(m.Indexed()) != captured.FrameSHA || m.Palette() != captured.Palette || normalized(d.KeyReads) != normalized(captured.Reads) || normalized(d.FileOps) != normalized(captured.Files) {
		panic("replay endpoint differs from GUI")
	}
	prefixProof, e := json.MarshalIndent(map[string]any{"prefix_steps": captured.Steps, "frame_palette_reads_files_equal": true, "receipt_sha256": hash(inputBytes), "origin": camera.Origin(m)}, "", "  ")
	must(e)
	must(os.WriteFile(filepath.Join(out, "prefix-verification.json"), append(prefixProof, '\n'), 0600))
	stats := func() hd.Stats {
		_, s := r.Render(m.Indexed(), m.Palette(), int(m.VideoMode()), d.Blocked, true, camera.Origin(m))
		return s
	}
	run := func(n uint64) {
		end := m.Steps + n
		for m.Steps < end && !d.Exited {
			step()
		}
	}
	events := []map[string]any{}
	queue := func(scan byte) {
		events = append(events, map[string]any{"step": m.Steps, "kind": "keyboard", "scan": scan})
		m.QueueScanCodes(scan)
		mods.Feed(scan)
	}
	key := func(scan byte) {
		before := len(d.KeyReads)
		queue(scan)
		run(2000000)
		queue(scan + 128)
		end := m.Steps + 120000000
		for len(d.KeyReads) == before && m.Steps < end && !d.Exited {
			step()
		}
		if len(d.KeyReads) != before+1 {
			panic(fmt.Sprintf("native key not consumed exactly once: %x", scan))
		}
		run(2000000)
	}
	wait := func(label string, pred func(hd.Stats) bool) {
		end := m.Steps + 120000000
		for m.Steps < end {
			if pred(stats()) {
				return
			}
			run(400000)
		}
		panic("native UI wait failed: " + label)
	}
	city := func(s hd.Stats) bool {
		return !d.Blocked && !s.Budget && s.Panel == "" && s.FileDialog == "" && s.Reason == "matched-city" && s.FooterMask&2 != 0
	}
	save := func(name string) []byte {
		key(0x3c)
		wait("file menu", func(s hd.Stats) bool { return s.Panel == "city-f2" })
		for stats().PanelSelection != 0 {
			key(0x50)
		}
		key(0x39)
		wait("save browser", func(s hd.Stats) bool { return s.FileDialog == "file-browser" })
		for len(strings.TrimSpace(stats().FileText[0])) > 0 {
			key(0x0e)
		}
		for _, ch := range name {
			if ch < '0' || ch > '9' {
				panic("numeric save name only")
			}
			scan := byte(ch - '0' + 1)
			if ch == '0' {
				scan = 0x0b
			}
			key(scan)
		}
		key(0x39)
		wait("saved city", city)
		data, e := os.ReadFile(filepath.Join(scratch, name+".SAV"))
		must(e)
		if len(data) != 93567 {
			panic("save length")
		}
		return data
	}
	key(0x0b)
	wait("prefix city paused", city)
	prefixSave := save("0000")
	key(0x04)
	wait("city resumed", city)
	samples := []map[string]any{}
	funded := false
	finalFunds := 0
	for i := 0; i < 250; i++ {
		run(24000000)
		s := stats()
		if city(s) {
			money, e := strconv.Atoi(stringTrim(s.FooterText[3]))
			must(e)
			finalFunds = money
			samples = append(samples, map[string]any{"steps": m.Steps, "footer": s.FooterText, "funds": money, "frame_sha256": hash(m.Indexed())})
			if money >= 102000 {
				funded = true
				break
			}
		}
		if i%25 == 0 {
			fmt.Fprintf(os.Stderr, "continue sample=%d steps=%d funds=%d\n", i, m.Steps, finalFunds)
		}
	}
	// Preserve legitimate progress even if the bounded continuation remains below cost.
	key(0x0b)
	wait("paused city", city)
	data := save("0001")
	path := filepath.Join(scratch, "0001.SAV")
	key(0x3b)
	wait("quit menu", func(s hd.Stats) bool { return s.Panel == "city-f1" })
	for stats().PanelSelection != 0 {
		key(0x50)
	}
	key(0x39)
	wait("quit confirmation", func(s hd.Stats) bool { return s.FileDialog == "quit-confirm" })
	codes, ok := keyboard.Stroke('Y', mods)
	if !ok {
		panic("Y stroke")
	}
	for _, scan := range codes {
		queue(scan)
	}
	run(2000000)
	wait("ending", func(s hd.Stats) bool { return s.EndingScreen == "achievement-base" })
	key(0x39)
	run(120000000)
	if !d.Exited {
		panic("no native DOS exit")
	}
	receipt, e := os.ReadFile(os.Args[1])
	must(e)
	report := map[string]any{"issue": 46, "from_exe": true, "checkpoint": false, "state_injection": false,
		"gui_acceptance": false, "prefix_receipt_sha256": hash(receipt), "prefix_steps": captured.Steps,
		"prefix_native_save_sha256":              hash(prefixSave),
		"prefix_frame_palette_reads_files_equal": true, "funded": funded, "target_funds": 102000,
		"funds": finalFunds, "steps": m.Steps, "samples": samples, "native_inputs": events, "key_reads": d.KeyReads,
		"file_ops": d.FileOps, "native_exit": d.Exited, "save_file": path, "save_sha256": hash(data),
		"scope": "重播實際 GUI 輸入後續跑原版城市、原版鍵盤存檔及退出；GUI 冷讀／核能施工另驗"}
	b, e := json.MarshalIndent(report, "", "  ")
	must(e)
	must(os.WriteFile(filepath.Join(out, "result.json"), append(b, '\n'), 0600))
	fmt.Printf("DONE funds=%d funded=%t SAV=%s\n", finalFunds, funded, hash(data))
}

func stringTrim(s string) string {
	return strings.TrimSpace(s)
}
