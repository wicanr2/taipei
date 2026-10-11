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
	"strings"
	"time"

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
	requireBudgetHD := flag.Bool("require-budget-hd", false, "要求完整預算 HD，並逐抽樣點比對原版狀態")
	requireInfrastructure := flag.Bool("require-infrastructure", false, "要求道路與電線 HD，逐抽樣點比對原版狀態")
	requireFont := flag.Bool("require-font", false, "要求重播實際經過 Noto 標題覆繪")
	requireIcons := flag.Bool("require-icons", false, "要求重播實際經過十四個工具圖示覆繪")
	requireDialog := flag.Bool("require-dialog", false, "要求重播實際經過完整說明視窗覆繪")
	requirePanels := flag.Bool("require-panels", false, "要求重播實際經過十三種啟動選單狀態")
	requireChrome := flag.Bool("require-chrome", false, "要求實際經過完整城市框架及十四外框")
	requireFooter := flag.Bool("require-footer", false, "要求實際經過完整底部動態欄位")
	requireTools := flag.Bool("require-tool-panels", false, "要求實際經過十八種工具子選單狀態")
	requireCity := flag.Bool("require-city-panels", false, "要求實際經過二十九種城市功能選單狀態")
	requireFiles := flag.Bool("require-file-dialogs", false, "要求實際經過檔案視窗與離開提示兩家族")
	renderInterval := flag.Uint64("render-interval-steps", 400000, "HD 抽樣間距，400000 的正整數倍，最多 24000000")
	flag.Parse()
	sampleStates := *requireBudgetHD || *requireInfrastructure
	if *renderInterval == 0 || *renderInterval%400000 != 0 || *renderInterval > 24000000 {
		panic("HD 抽樣間距須為 400000 的正整數倍，最多 24000000")
	}
	z, err := zip.OpenReader(*receipt)
	must(err)
	defer z.Close()
	var capture struct {
		Steps    uint64
		FrameSHA string          `json:"frame_index_sha256"`
		Palette  [256][3]byte    `json:"palette"`
		KeyReads json.RawMessage `json:"key_reads"`
		FileOps  json.RawMessage `json:"file_ops"`
		Inputs   []struct {
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
	var chromeFrames uint64
	var footerFrames uint64
	reasons := map[string]uint64{}
	panelStates := map[string]uint64{}
	toolStates := map[string]uint64{}
	cityStates := map[string]uint64{}
	fileFamilies := map[string]uint64{}
	budgetRows := map[int]uint64{}
	infrastructureImages := map[int]uint64{}
	var infrastructureFrames uint64
	var checkpoints []string
	durations := map[string]float64{}
	var observedFrames uint64
	run := func(present bool) []byte {
		phase := "baseline"
		if present {
			phase = "presented"
		}
		started := time.Now()
		fmt.Fprintf(os.Stderr, "%s start: steps=%d render_interval_steps=%d\n", phase, capture.Steps, *renderInterval)
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
		// 真實獨立暫存層，讓兩側實際存檔，不使用沒有 Scratch 的模擬寫入。
		scratch, err := os.MkdirTemp("", "taipei-presentation-audit-")
		must(err)
		defer os.RemoveAll(scratch)
		d.Scratch = scratch
		d.BlockingBIOSKeys = true
		var camera original.Camera
		var renderer *hd.Renderer
		if present {
			renderer = hd.New(rom, *materials)
		}
		next := 0
		point := 0
		snapshot := func() []byte {
			saveHashes := map[string]string{}
			entries, err := os.ReadDir(scratch)
			must(err)
			for _, entry := range entries {
				if !entry.IsDir() && strings.EqualFold(filepath.Ext(entry.Name()), ".sav") {
					data, err := os.ReadFile(filepath.Join(scratch, entry.Name()))
					must(err)
					saveHashes[entry.Name()] = hash(data)
				}
			}
			state, err := json.Marshal(map[string]any{
				"memory_sha256": hash(m.Mem), "frame_sha256": hash(m.Indexed()), "palette": m.Palette(),
				"registers": m.CPU.R, "segments": m.CPU.Seg, "ip": m.CPU.IP, "flags": m.CPU.Flags,
				"steps": m.Steps, "ticks": m.Ticks, "ports": m.Ports, "opl_regs": m.OPLRegs(0),
				"key_reads": d.KeyReads, "dos_blocked": d.Blocked, "dos_exited": d.Exited,
				"file_ops": d.FileOps, "writes": d.Wrote, "save_sha256": saveHashes,
			})
			must(err)
			return state
		}
		refresh := *renderInterval
		progress := uint64(1000000000)
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
			if m.Steps >= progress {
				fmt.Fprintf(os.Stderr, "%s progress: steps=%d/%d elapsed_seconds=%.1f\n", phase, m.Steps, capture.Steps, time.Since(started).Seconds())
				progress += 1000000000
			}
			if m.Steps >= refresh {
				if present {
					observedFrames++
					_, stats := renderer.Render(m.Indexed(), m.Palette(), int(m.VideoMode()), d.Blocked, true, camera.Origin(m))
					reasons[stats.Reason]++
					if stats.Infrastructure.Painted > 0 {
						infrastructureFrames++
						for index, count := range stats.Infrastructure.Images {
							infrastructureImages[index] += uint64(count)
						}
					}
					if stats.Budget {
						budgetRows[stats.BudgetSelection]++
					}
					if stats.FileDialog != "" {
						fileFamilies[stats.FileDialog]++
					}
					if stats.Panel != "" {
						states := panelStates
						if strings.HasPrefix(stats.Panel, "tool-") {
							states = toolStates
						} else if strings.HasPrefix(stats.Panel, "city-f") {
							states = cityStates
						}
						states[fmt.Sprintf("%s/%d", stats.Panel, stats.PanelSelection)]++
					}
					if stats.Dialog == "new-game" {
						dialogFrames++
					}
					if stats.FontLabels > 0 {
						fontFrames++
					}
					if stats.FooterMask == 3 {
						footerFrames++
					}
					if stats.UIIcons == 14 {
						iconFrames++
					}
					if stats.ChromeParts == 6 && stats.ChromeRings == 14 {
						chromeFrames++
					}
					if stats.Painted > 0 {
						painted++
					}
				}
				if sampleStates {
					stateSHA := hash(snapshot())
					if !present {
						checkpoints = append(checkpoints, stateSHA)
					} else if point >= len(checkpoints) || checkpoints[point] != stateSHA {
						panic(fmt.Sprintf("HD 抽樣點 %d、步數 %d 的原版狀態不符", point, m.Steps))
					}
					point++
				}
				refresh += *renderInterval
			}
		}
		if present {
			draws = camera.Draws
		}
		if *requireFiles || sampleStates {
			normalize := func(v any) string {
				raw, err := json.Marshal(v)
				must(err)
				var decoded any
				must(json.Unmarshal(raw, &decoded))
				raw, err = json.Marshal(decoded)
				must(err)
				return string(raw)
			}
			if hash(m.Indexed()) != capture.FrameSHA || m.Palette() != capture.Palette || normalize(d.KeyReads) != normalize(capture.KeyReads) || normalize(d.FileOps) != normalize(capture.FileOps) {
				panic("檔案視窗重播未到達正常 GUI 收據的原版狀態")
			}
		}
		if sampleStates && point != len(checkpoints) {
			panic("兩側原版狀態抽樣點數不符")
		}
		state := snapshot()
		durations[phase] = time.Since(started).Seconds()
		fmt.Fprintf(os.Stderr, "%s done: steps=%d elapsed_seconds=%.1f\n", phase, m.Steps, durations[phase])
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
	if *requireBudgetHD && (reasons["matched-budget"] == 0 || len(checkpoints) == 0 || len(budgetRows) != 5) {
		panic("重播缺少完整預算 HD 五列或原版狀態抽樣")
	}
	if *requireInfrastructure {
		road, power := false, false
		for index := range infrastructureImages {
			road = road || (index >= 15 && index <= 29)
			power = power || (index >= 45 && index <= 55)
		}
		if !road || !power || infrastructureFrames == 0 || len(checkpoints) == 0 {
			panic("重播缺少正常道路／電線 HD 或逐點原版狀態抽樣")
		}
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
	if *requireChrome && chromeFrames == 0 {
		panic("重播未實際經過完整城市框架")
	}
	if *requireFooter && footerFrames == 0 {
		panic("重播未經過完整底部欄位")
	}
	if *requireTools && len(toolStates) != 18 {
		panic("重播未經過十八種工具子選單狀態")
	}
	if *requireCity && len(cityStates) != 29 {
		panic("重播未經過二十九種城市功能選單狀態")
	}
	if *requireFiles && (fileFamilies["file-browser"] == 0 || fileFamilies["quit-confirm"] == 0) {
		panic("重播未實際經過檔案與離開提示兩家族")
	}
	result, err := json.MarshalIndent(map[string]any{
		"input_sha256": hash(raw), "steps": capture.Steps, "same_input": true, "state_equal": true,
		"state_sha256": hash(baseline), "state": json.RawMessage(baseline), "map_draws": draws, "hd_frames": painted,
		"hd_reasons": reasons, "font_frames": fontFrames,
		"icon_frames":                                iconFrames,
		"chrome_frames":                              chromeFrames,
		"footer_frames":                              footerFrames,
		"dialog_frames":                              dialogFrames,
		"panel_states":                               panelStates,
		"tool_panel_states":                          toolStates,
		"city_panel_states":                          cityStates,
		"file_dialog_families":                       fileFamilies,
		"budget_hd_rows":                             budgetRows,
		"infrastructure_images":                      infrastructureImages,
		"infrastructure_frames":                      infrastructureFrames,
		"sampled_original_state_sha256":              checkpoints,
		"sampled_original_states_equal":              sampleStates,
		"normal_gui_frame_palette_reads_files_equal": *requireFiles || sampleStates,
		"render_interval_steps":                      *renderInterval,
		"observed_render_frames":                     observedFrames,
		"phase_elapsed_seconds":                      durations,
		"scope":                                      "同一正常 GUI 冷啟動鍵盤收據，固定 dosgolem 初始狀態與虛擬時間；完整執行兩側原版步數，HD 按明示間距抽樣，只驗該重播的呈現層不改原版狀態，非逐幀或全部 HD 驗收",
	}, "", "  ")
	must(err)
	must(os.WriteFile(*out, append(result, '\n'), 0600))
	fmt.Printf("presentation state equal: %s; draws=%d hd_frames=%d\n", hash(baseline), draws, painted)
}
