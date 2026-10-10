// 原版 GUI 研究原型，契約見 docs/spec/005-frontend-preview.md。
package main

import (
	"bytes"
	"compress/gzip"
	"crypto/sha256"
	"encoding/binary"
	"encoding/json"
	"flag"
	"fmt"
	"image"
	"image/png"
	"io"
	"log"
	"os"
	"path/filepath"

	"github.com/hajimehoshi/ebiten/v2"
	"github.com/hajimehoshi/ebiten/v2/inpututil"
	dg "github.com/wicanr2/dosgolem"
	"github.com/wicanr2/taipei/preview/internal/keyboard"
)

const originalSHA = "798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3"

type binding struct {
	key  ebiten.Key
	scan byte
}

var bindings = []binding{
	{ebiten.KeyEscape, 0x01}, {ebiten.Key1, 0x02}, {ebiten.Key2, 0x03}, {ebiten.Key3, 0x04},
	{ebiten.Key4, 0x05}, {ebiten.Key5, 0x06}, {ebiten.Key6, 0x07}, {ebiten.Key7, 0x08},
	{ebiten.Key8, 0x09}, {ebiten.Key9, 0x0a}, {ebiten.Key0, 0x0b},
	{ebiten.KeyMinus, 0x0c}, {ebiten.KeyEqual, 0x0d}, {ebiten.KeyBackspace, 0x0e}, {ebiten.KeyTab, 0x0f},
	{ebiten.KeyQ, 0x10}, {ebiten.KeyW, 0x11}, {ebiten.KeyE, 0x12}, {ebiten.KeyR, 0x13},
	{ebiten.KeyT, 0x14}, {ebiten.KeyY, 0x15}, {ebiten.KeyU, 0x16}, {ebiten.KeyI, 0x17},
	{ebiten.KeyO, 0x18}, {ebiten.KeyP, 0x19}, {ebiten.KeyBracketLeft, 0x1a}, {ebiten.KeyBracketRight, 0x1b},
	{ebiten.KeyEnter, 0x1c}, {ebiten.KeyControlLeft, 0x1d},
	{ebiten.KeyA, 0x1e}, {ebiten.KeyS, 0x1f}, {ebiten.KeyD, 0x20}, {ebiten.KeyF, 0x21},
	{ebiten.KeyG, 0x22}, {ebiten.KeyH, 0x23}, {ebiten.KeyJ, 0x24}, {ebiten.KeyK, 0x25}, {ebiten.KeyL, 0x26},
	{ebiten.KeySemicolon, 0x27}, {ebiten.KeyQuote, 0x28}, {ebiten.KeyBackquote, 0x29},
	{ebiten.KeyShiftLeft, 0x2a}, {ebiten.KeyBackslash, 0x2b},
	{ebiten.KeyZ, 0x2c}, {ebiten.KeyX, 0x2d}, {ebiten.KeyC, 0x2e}, {ebiten.KeyV, 0x2f},
	{ebiten.KeyB, 0x30}, {ebiten.KeyN, 0x31}, {ebiten.KeyM, 0x32},
	{ebiten.KeyComma, 0x33}, {ebiten.KeyPeriod, 0x34}, {ebiten.KeySlash, 0x35}, {ebiten.KeyShiftRight, 0x36},
	{ebiten.KeyAltLeft, 0x38}, {ebiten.KeySpace, 0x39}, {ebiten.KeyCapsLock, 0x3a},
	{ebiten.KeyF1, 0x3b}, {ebiten.KeyF2, 0x3c}, {ebiten.KeyF3, 0x3d}, {ebiten.KeyF4, 0x3e},
	{ebiten.KeyF5, 0x3f}, {ebiten.KeyF6, 0x40}, {ebiten.KeyF7, 0x41}, {ebiten.KeyF8, 0x42},
	{ebiten.KeyF9, 0x43}, {ebiten.KeyF10, 0x44},
	{ebiten.KeyHome, 0x47}, {ebiten.KeyArrowUp, 0x48}, {ebiten.KeyPageUp, 0x49},
	{ebiten.KeyArrowLeft, 0x4b}, {ebiten.KeyArrowRight, 0x4d},
	{ebiten.KeyEnd, 0x4f}, {ebiten.KeyArrowDown, 0x50}, {ebiten.KeyPageDown, 0x51},
	{ebiten.KeyInsert, 0x52}, {ebiten.KeyDelete, 0x53},
}

type game struct {
	m            *dg.Machine
	d            *dg.DOS
	frame        *ebiten.Image
	rgba         *image.RGBA
	out          string
	stopFile     string
	perUpdate    uint64
	frames       uint64
	mouseButtons uint16
	inputs       []inputEvent
	textMods     keyboard.Modifiers
	keyStacks    []map[string]any
}

type inputEvent struct {
	Step    uint64 `json:"step"`
	Kind    string `json:"kind"`
	Scan    byte   `json:"scan,omitempty"`
	X       int    `json:"x,omitempty"`
	Y       int    `json:"y,omitempty"`
	Buttons uint16 `json:"buttons,omitempty"`
	Text    string `json:"text,omitempty"`
}

func (g *game) Update() error {
	if g.stopFile != "" {
		if _, err := os.Stat(g.stopFile); err == nil {
			return ebiten.Termination
		}
	}
	shortcut := ebiten.IsKeyPressed(ebiten.KeyControlLeft) || ebiten.IsKeyPressed(ebiten.KeyAltLeft)
	// 修飾鍵先送，讓有序文字能按相同的 BIOS 修飾狀態轉換。
	for _, b := range bindings {
		if b.scan != 0x2a && b.scan != 0x36 && b.scan != 0x3a && b.scan != 0x1d && b.scan != 0x38 {
			continue
		}
		if inpututil.IsKeyJustPressed(b.key) {
			g.queue(b.scan)
		}
		if inpututil.IsKeyJustReleased(b.key) {
			g.queue(b.scan | 0x80)
		}
	}
	if !shortcut {
		for _, ch := range ebiten.AppendInputChars(nil) {
			g.inputs = append(g.inputs, inputEvent{Step: g.m.Steps, Kind: "text", Text: string(ch)})
			if codes, ok := keyboard.Stroke(ch, g.textMods); ok {
				g.queue(codes...)
			} else {
				log.Printf("研究前端尚不支援文字 U+%04X", ch)
			}
		}
	}
	for _, b := range bindings {
		if b.scan == 0x2a || b.scan == 0x36 || b.scan == 0x3a || b.scan == 0x1d || b.scan == 0x38 {
			continue
		}
		if keyboard.PrintableScan(b.scan) && !shortcut {
			continue
		}
		if inpututil.IsKeyJustPressed(b.key) {
			g.queue(b.scan)
		}
		if inpututil.IsKeyJustReleased(b.key) {
			g.queue(b.scan | 0x80)
		}
	}
	x, y := ebiten.CursorPosition()
	if x >= 0 && y >= 0 && x < 320 && y < 200 {
		if uint16(x) != g.d.Mouse.X || uint16(y) != g.d.Mouse.Y {
			g.d.MoveMouse(x, y)
			g.inputs = append(g.inputs, inputEvent{Step: g.m.Steps, Kind: "mouse-move", X: x, Y: y})
		}
	}
	var buttons uint16
	if ebiten.IsMouseButtonPressed(ebiten.MouseButtonLeft) {
		buttons |= 1
	}
	if ebiten.IsMouseButtonPressed(ebiten.MouseButtonRight) {
		buttons |= 2
	}
	if buttons != g.mouseButtons {
		g.d.PressMouse(int(buttons))
		g.inputs = append(g.inputs, inputEvent{Step: g.m.Steps, Kind: "mouse-button", Buttons: buttons})
		g.mouseButtons = buttons
	}
	end := g.m.Steps + g.perUpdate
	for g.m.Steps < end && !g.d.Exited && !g.m.CPU.Halted {
		if err := g.m.Step(); err != nil {
			return err
		}
	}
	g.refresh()
	g.frames++
	if g.frames%60 == 0 {
		if err := g.receipt(); err != nil {
			return err
		}
	}
	if g.d.Exited || g.m.CPU.Halted {
		return ebiten.Termination
	}
	return nil
}

func (g *game) queue(codes ...byte) {
	g.m.QueueScanCodes(codes...)
	for _, scan := range codes {
		g.textMods.Feed(scan)
		g.inputs = append(g.inputs, inputEvent{Step: g.m.Steps, Kind: "keyboard", Scan: scan})
	}
}

func (g *game) refresh() {
	pal := g.m.Palette()
	px := g.m.Indexed()
	for i, p := range px {
		if i >= 320*200 {
			break
		}
		j := i * 4
		g.rgba.Pix[j] = pal[p][0]
		g.rgba.Pix[j+1] = pal[p][1]
		g.rgba.Pix[j+2] = pal[p][2]
		g.rgba.Pix[j+3] = 255
	}
	g.frame.WritePixels(g.rgba.Pix)
}
func (g *game) Draw(screen *ebiten.Image)  { screen.DrawImage(g.frame, nil) }
func (g *game) Layout(int, int) (int, int) { return 320, 200 }

func atomic(path string, data []byte) error {
	tmp := path + ".tmp"
	if err := os.WriteFile(tmp, data, 0600); err != nil {
		return err
	}
	return os.Rename(tmp, path)
}
func (g *game) receipt() error {
	if g.out == "" {
		return nil
	}
	b, err := json.MarshalIndent(map[string]any{
		"inputs":             g.inputs,
		"frame_index_sha256": fmt.Sprintf("%x", sha256.Sum256(g.m.Indexed())),
		"steps":              g.m.Steps, "frames": g.frames, "mode": g.m.VideoMode(), "registers": g.m.CPU.R,
		"segments": g.m.CPU.Seg, "ip": g.m.CPU.IP, "ticks": g.m.Ticks,
		"key_reads": g.d.KeyReads, "key_waits": g.d.KeyWaits, "irq1": g.m.KeyIRQs,
		"key_stacks":  g.keyStacks,
		"mouse_polls": len(g.d.Mouse.Polls), "mouse_calls": g.d.Mouse.Calls, "file_ops": g.d.FileOps,
		"missing": g.d.Missing, "unimplemented": g.d.UnimplementedDetails,
		"dos_exited":      g.d.Exited,
		"dos_blocked":     g.d.Blocked,
		"original_sha256": originalSHA, "prototype": true,
	}, "", "  ")
	if err != nil {
		return err
	}
	if err = atomic(filepath.Join(g.out, "frame-index.bin"), g.m.Indexed()); err != nil {
		return err
	}
	if err = atomic(filepath.Join(g.out, "status.json"), b); err != nil {
		return err
	}
	var buf bytes.Buffer
	if err = png.Encode(&buf, g.rgba); err != nil {
		return err
	}
	return atomic(filepath.Join(g.out, "frame.png"), buf.Bytes())
}

// 與 dosgolem internal/state 的兩段 gzip/gob 相同，只供診斷續跑。
func loadCheckpoint(path string, m *dg.Machine, d *dg.DOS) error {
	f, err := os.Open(path)
	if err != nil {
		return err
	}
	defer f.Close()
	z, err := gzip.NewReader(f)
	if err != nil {
		return err
	}
	defer z.Close()
	for _, load := range []func(io.Reader) error{m.LoadState, d.LoadState} {
		var n uint64
		if err = binary.Read(z, binary.LittleEndian, &n); err != nil {
			return err
		}
		r := io.LimitReader(z, int64(n))
		if err = load(r); err != nil {
			return err
		}
		if _, err = io.Copy(io.Discard, r); err != nil {
			return err
		}
	}
	return nil
}

func main() {
	orig := flag.String("original", "", "原版 RS201.EXE 所在目錄")
	saves := flag.String("saves", "", "獨立可寫存檔目錄")
	out := flag.String("receipts", "", "研究收據目錄")
	checkpoint := flag.String("checkpoint", "", "診斷快照；正式冷啟動不使用")
	stopFile := flag.String("stop-file", "", "研究驗證的正常結束請求檔")
	steps := flag.Uint64("steps-per-update", 400000, "每次更新的固定指令數")
	traceKeyStack := flag.Bool("trace-key-stack", false, "診斷 INT16 讀鍵前的原始堆疊，不改原版狀態")
	flag.Parse()
	if *orig == "" || *saves == "" || *out == "" {
		log.Fatal("請指定 -original、-saves、-receipts")
	}
	if *steps == 0 {
		log.Fatal("每次更新指令數必須大於零")
	}
	raw, err := os.ReadFile(filepath.Join(*orig, "RS201.EXE"))
	if err != nil {
		log.Fatal(err)
	}
	if fmt.Sprintf("%x", sha256.Sum256(raw)) != originalSHA {
		log.Fatal("原版 EXE 雜湊不符，請使用已盤點的版本")
	}
	for _, p := range []string{*saves, *out} {
		if err = os.MkdirAll(p, 0700); err != nil {
			log.Fatal(err)
		}
	}
	m := dg.New()
	if err = m.LoadEXE(raw); err != nil {
		log.Fatal(err)
	}
	tail := []byte("/A /D /x")
	base := uint32(dg.PSPSeg) * 16
	m.Write8(base+0x80, byte(len(tail)))
	m.WriteBytes(base+0x81, tail)
	m.Write8(base+0x81+uint32(len(tail)), 13)
	d := dg.NewDOS(m, *orig)
	d.Install()
	defer d.Close()
	if *checkpoint != "" {
		if err = loadCheckpoint(*checkpoint, m, d); err != nil {
			log.Fatal(err)
		}
	}
	d.Root = *orig
	d.Scratch = *saves
	d.BlockingBIOSKeys = true
	g := &game{m: m, d: d, frame: ebiten.NewImage(320, 200), rgba: image.NewRGBA(image.Rect(0, 0, 320, 200)), out: *out, stopFile: *stopFile, perUpdate: *steps}
	g.textMods.CapsLock = m.Read8(0x417)&64 != 0
	g.textMods.LeftShift = m.Read8(0x417)&2 != 0
	g.textMods.RightShift = m.Read8(0x417)&1 != 0
	g.textMods.CapsHeld = m.Read8(0x418)&64 != 0
	if *traceKeyStack {
		previous := m.CPU.IntHook
		m.CPU.IntHook = func(c *dg.CPU, n uint8) bool {
			if n == 0x16 && c.R[dg.AX]>>8 == 0 {
				if _, ok := m.PeekKey(); ok {
					words := make([]uint16, 12)
					for i := range words {
						address := uint32(c.Seg[dg.SS])*16 + uint32(c.R[dg.SP]+uint16(i*2))
						words[i] = m.Read16(address & 0xfffff)
					}
					dsbase := uint32(c.Seg[dg.DS]) * 16
					focusBase := uint32(m.Read16(dsbase+0x20f2)) * 16
					g.keyStacks = append(g.keyStacks, map[string]any{"step": m.Steps, "cs": c.Seg[dg.CS], "ip": c.IP, "ss": c.Seg[dg.SS], "sp": c.R[dg.SP], "ds": c.Seg[dg.DS], "es": c.Seg[dg.ES], "words": words,
						"focus_segment": focusBase / 16, "focus": m.Read8(focusBase + 0x4a), "cursor_x": m.Read16(focusBase + 0x4f), "cursor_y": m.Read16(focusBase + 0x51), "tool_cursor": m.Read8(dsbase + 0xe3c), "tool_committed": m.Read8(dsbase + 0xe3e)})
				}
			}
			return previous(c, n)
		}
	}
	ebiten.SetWindowTitle("模擬台北：原版整合研究原型")
	ebiten.SetWindowSize(1280, 800)
	ebiten.SetWindowResizingMode(ebiten.WindowResizingModeEnabled)
	if err = ebiten.RunGame(g); err != nil {
		log.Print(err)
	}
	g.refresh()
	if err = g.receipt(); err != nil {
		log.Print(err)
	}
}
