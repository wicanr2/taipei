// #24：從正常 GUI 收據重播鍵盤輸入，核對呈現層沒有改動原版狀態。
package main

import (
	"archive/zip"
	"bytes"
	"crypto/sha256"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"os"
	"path/filepath"

	dg "github.com/wicanr2/dosgolem"
	"github.com/wicanr2/taipei/preview/internal/hd"
	"github.com/wicanr2/taipei/preview/internal/original"
)

func must(err error) {
	if err != nil {
		panic(err)
	}
}
func hash(p []byte) string { return fmt.Sprintf("%x", sha256.Sum256(p)) }

func main() {
	root := flag.String("original", "/orig", "唯讀原版目錄")
	materials := flag.String("materials", "", "本機材質")
	receipt := flag.String("receipt", "", "正常 GUI 的原子收據")
	out := flag.String("out", "", "狀態對照輸出")
	requireBudget := flag.Bool("require-budget", false, "要求重播實際經過年度視窗回退")
	requireFont := flag.Bool("require-font", false, "要求重播實際經過 Noto 標題覆繪")
	requireIcons := flag.Bool("require-icons", false, "要求重播實際經過十四個工具圖示覆繪")
	requireDialog := flag.Bool("require-dialog", false, "要求重播實際經過完整說明視窗覆繪")
	requirePanels := flag.Bool("require-panels", false, "要求重播實際經過十三種啟動選單狀態")
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
	found := false
	for _, f := range z.File {
		if f.Name != "status.json" {
			continue
		}
		r, err := f.Open()
		must(err)
		p, err := io.ReadAll(r)
		must(err)
		must(r.Close())
		must(json.Unmarshal(p, &capture))
		found = true
	}
	if !found || capture.Steps == 0 {
		panic("缺少 GUI 輸入收據")
	}
	raw, err := os.ReadFile(filepath.Join(*root, "RS201.EXE"))
	must(err)
	if hash(raw) != "798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3" {
		panic("EXE 不符")
	}
	rom, err := os.ReadFile(filepath.Join(*root, "RS201.ROM"))
	must(err)
	var draws, painted, fontFrames, iconFrames, dialogFrames uint64
	reasons := map[string]uint64{}
	panelStates := map[string]uint64{}
	run := func(present bool) []byte {
		m := dg.New()
		must(m.LoadEXE(raw))
		m.SetAdLib(true)
		tail := []byte("/A /D /x")
		base := uint32(dg.PSPSeg) * 16
		m.Write8(base+0x80, byte(len(tail)))
		m.WriteBytes(base+0x81, tail)
		m.Write8(base+0x81+uint32(len(tail)), 13)
		d := dg.NewDOS(m, *root)
		d.Install()
		defer d.Close()
		d.BlockingBIOSKeys = true
		var camera original.Camera
		var renderer *hd.Renderer
		if present {
			renderer = hd.New(rom, *materials)
		}
		next := 0
		refresh := uint64(400000)
		for m.Steps < capture.Steps {
			for next < len(capture.Inputs) && m.Steps >= capture.Inputs[next].Step {
				event := capture.Inputs[next]
				if event.Kind == "keyboard" {
					m.QueueScanCodes(event.Scan)
				}
				next++
			}
			if present {
				camera.Observe(m)
			}
			must(m.Step())
			if present && m.Steps >= refresh {
				_, stats := renderer.Render(m.Indexed(), m.Palette(), int(m.VideoMode()), d.Blocked, true, camera.Origin(m))
				reasons[stats.Reason]++
				if stats.Panel != "" {
					panelStates[fmt.Sprintf("%s/%d", stats.Panel, stats.PanelSelection)]++
				}
				if stats.Dialog == "new-game" {
					dialogFrames++
				}
				if stats.FontLabels > 0 {
					fontFrames++
				}
				if stats.UIIcons == 14 {
					iconFrames++
				}
				if stats.Painted > 0 {
					painted++
				}
				refresh += 400000
			}
		}
		if present {
			draws = camera.Draws
		}
		state, err := json.Marshal(map[string]any{
			"memory_sha256": hash(m.Mem), "frame_sha256": hash(m.Indexed()), "palette": m.Palette(),
			"registers": m.CPU.R, "segments": m.CPU.Seg, "ip": m.CPU.IP, "flags": m.CPU.Flags,
			"steps": m.Steps, "ticks": m.Ticks, "ports": m.Ports, "opl_regs": m.OPLRegs(0),
			"key_reads": d.KeyReads, "dos_blocked": d.Blocked, "dos_exited": d.Exited,
		})
		must(err)
		return state
	}
	baseline := run(false)
	presented := run(true)
	if !bytes.Equal(baseline, presented) {
		panic("原點觀察或 HD 呈現改變原版狀態")
	}
	if draws < 2 || painted == 0 {
		panic("重播未經過地圖重繪與 HD 呈現")
	}
	if *requireBudget && reasons["budget-window"] == 0 {
		panic("重播未實際經過年度視窗回退")
	}
	if *requireFont && fontFrames == 0 {
		panic("重播未實際經過 Noto 標題覆繪")
	}
	if *requireIcons && iconFrames == 0 {
		panic("重播未實際經過十四個工具圖示覆繪")
	}
	if *requireDialog && dialogFrames == 0 {
		panic("重播未實際經過完整說明視窗覆繪")
	}
	if *requirePanels && len(panelStates) != 13 {
		panic("重播未實際經過十三種啟動選單狀態")
	}
	result, err := json.MarshalIndent(map[string]any{
		"input_sha256": hash(raw), "steps": capture.Steps, "same_input": true, "state_equal": true,
		"state_sha256": hash(baseline), "state": json.RawMessage(baseline), "map_draws": draws, "hd_frames": painted,
		"hd_reasons": reasons, "font_frames": fontFrames,
		"icon_frames":   iconFrames,
		"dialog_frames": dialogFrames,
		"panel_states":  panelStates,
		"scope":         "同一正常 GUI 冷啟動鍵盤收據，固定 dosgolem 初始狀態與虛擬時間；只驗呈現層不改原版狀態，非正式 HD 驗收",
	}, "", "  ")
	must(err)
	must(os.WriteFile(*out, append(result, '\n'), 0600))
	fmt.Printf("presentation state equal: %s; draws=%d hd_frames=%d\n", hash(baseline), draws, painted)
}
