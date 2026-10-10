// #20：實際原版事件的分段連續性研究；不啟動 GUI 或改寫原版。
package main

import (
	"bufio"
	"bytes"
	"crypto/sha256"
	"encoding/binary"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"os"
	"strings"

	a "github.com/wicanr2/dosgolem/audio"
	"github.com/wicanr2/dosgolem/audio/ymfm"
)

func check(e error) {
	if e != nil {
		panic(e)
	}
}
func main() {
	events := flag.String("events", "", "原版 OPL2 事件")
	out := flag.String("out", "", "JSON 收據")
	flag.Parse()
	if *events == "" || *out == "" {
		panic("請指定 -events 與 -out")
	}
	f, e := os.Open(*events)
	check(e)
	defer f.Close()
	r := bufio.NewReader(f)
	var all []a.OPL
	for {
		var step uint64
		var bank, reg, val uint8
		_, e := fmt.Fscan(r, &step, &bank, &reg, &val)
		if e == io.EOF {
			break
		}
		check(e)
		all = append(all, a.OPL{Step: step, Bank: bank, Reg: reg, Value: val})
	}
	const until = uint64(850000001)
	const sps = 11580882.352941177
	render := func(stride uint64) []byte {
		s, e := ymfm.New(48000)
		check(e)
		defer s.Close()
		audio, e := a.New(48000, sps, s)
		check(e)
		var pcm []byte
		at := 0
		for end := stride; ; end += stride {
			if end > until {
				end = until
			}
			next := at
			for next < len(all) && all[next].Step <= end {
				next++
			}
			p, e := audio.Render(end, all[at:next], nil)
			check(e)
			pcm = append(pcm, p...)
			at = next
			if end == until {
				break
			}
		}
		if at != len(all) {
			panic("unconsumed original events")
		}
		return pcm
	}
	pcm := render(193014)
	other := render(10000003)
	if !bytes.Equal(pcm, other) {
		panic("original PCM differs across batch sizes")
	}
	var nonzero, clipped int
	peak := 0
	for i := 0; i < len(pcm); i += 4 {
		v := int(int16(binary.LittleEndian.Uint16(pcm[i:])))
		if v != 0 {
			nonzero++
		}
		if v < 0 {
			v = -v
		}
		if v > peak {
			peak = v
		}
		if v >= 32767 {
			clipped++
		}
	}
	check(os.WriteFile(strings.TrimSuffix(*out, ".json")+".pcm", pcm, 0600))
	meta := map[string]any{"prototype": true, "sample_rate": 48000, "channels": 2, "frames": len(pcm) / 4, "events": len(all), "consumed_events": len(all), "nonzero_frames": nonzero, "peak": peak, "clipped": clipped, "chunk_equal": true, "pcm_sha256": fmt.Sprintf("%x", sha256.Sum256(pcm)), "timing": "hardware-spec approximation", "human_listened": false}
	b, e := json.MarshalIndent(meta, "", "  ")
	check(e)
	check(os.WriteFile(*out, b, 0600))
	fmt.Println(string(b))
}
