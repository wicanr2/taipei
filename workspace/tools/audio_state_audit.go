// #17：原版 EXE 相同步數與輸入，有／無消費音訊的機器狀態比較。
package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"

	dg "github.com/wicanr2/dosgolem"
	a "github.com/wicanr2/dosgolem/audio"
	"github.com/wicanr2/dosgolem/audio/ymfm"
)

func must(e error) {
	if e != nil {
		panic(e)
	}
}
func hash(p []byte) string { return fmt.Sprintf("%x", sha256.Sum256(p)) }
func main() {
	root := flag.String("original", "/orig", "唯讀原版目錄")
	out := flag.String("out", "/out/audio-state-audit.json", "比較收據")
	flag.Parse()
	raw, e := os.ReadFile(filepath.Join(*root, "RS201.EXE"))
	must(e)
	if hash(raw) != "798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3" {
		panic("原版 EXE 不符")
	}
	run := func(consume bool) []byte {
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
		var stream *a.Stream
		if consume {
			synth, e := ymfm.New(48000)
			must(e)
			defer synth.Close()
			stream, e = a.New(48000, a.StepsPerSecond(), synth)
			must(e)
		}
		events := []struct {
			step uint64
			scan byte
		}{{700000000, 0x39}, {750000000, 0xb9}, {800000000, 0x39}, {850000000, 0xb9}}
		next := 0
		drainAt := uint64(193014)
		for m.Steps < 850000001 {
			for next < len(events) && m.Steps >= events[next].step {
				m.QueueScanCodes(events[next].scan)
				next++
			}
			must(m.Step())
			if consume && m.Steps >= drainAt {
				_, e := stream.Drain(m)
				must(e)
				drainAt += 193014
			}
		}
		if consume {
			_, e := stream.Drain(m)
			must(e)
		}
		state := map[string]any{"memory_sha256": hash(m.Mem), "frame_sha256": hash(m.Indexed()), "palette": m.Palette(), "registers": m.CPU.R, "segments": m.CPU.Seg, "ip": m.CPU.IP, "flags": m.CPU.Flags, "steps": m.Steps, "ticks": m.Ticks, "ports": m.Ports, "opl_regs": m.OPLRegs(0), "key_reads": d.KeyReads}
		p, e := json.Marshal(state)
		must(e)
		return p
	}
	baseline := run(false)
	consumed := run(true)
	if !bytes.Equal(baseline, consumed) {
		panic("音訊消費改變原版機器狀態")
	}
	result := map[string]any{"input_sha256": hash(raw), "steps": 850000001, "initial_adlib_present": true, "same_input": true, "state_equal": true, "state_sha256": hash(baseline), "state": json.RawMessage(baseline), "scope": "原版冷啟動至主選單；存退讀另由正常 GUI 驗證"}
	b, e := json.MarshalIndent(result, "", "  ")
	must(e)
	must(os.WriteFile(*out, append(b, '\n'), 0600))
	fmt.Println("original state equal with audio consumption:", hash(baseline))
}
