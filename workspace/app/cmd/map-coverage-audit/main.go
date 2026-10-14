// #62: renderer-only inventory. No DOS VM or game-state injection.
package main

import (
	"archive/zip"
	"bytes"
	"crypto/sha256"
	"encoding/binary"
	"encoding/hex"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"runtime"
	"sort"
	"time"

	"github.com/wicanr2/taipei/preview/internal/hd"
	"github.com/wicanr2/taipei/preview/internal/i18n"
)

func must(err error) {
	if err != nil {
		panic(err)
	}
}
func digest(raw []byte) string { v := sha256.Sum256(raw); return hex.EncodeToString(v[:]) }

type alias struct {
	Member int `json:"member"`
	Image  int `json:"image"`
	Pixel  int `json:"pixel_file_offset"`
}
type record struct {
	SHA              string   `json:"source_sha256"`
	Aliases          []alias  `json:"aliases"`
	SourceKnown      bool     `json:"source_known"`
	Painted          bool     `json:"painted_in_synthetic_context"`
	ChangedPixels    int      `json:"changed_pixels"`
	BlackPlaceholder bool     `json:"all_zero_placeholder"`
	Stats            hd.Stats `json:"stats"`
}

func main() {
	romPath := flag.String("rom", "", "唯讀原版ROM")
	materials := flag.String("materials", "", "現行素材")
	receipt := flag.String("receipt", "", "正常城市原始收據")
	out := flag.String("out", "", "新JSON，不覆寫")
	flag.Parse()
	if *romPath == "" || *materials == "" || *receipt == "" || *out == "" {
		panic("參數不足")
	}
	if _, err := os.Lstat(*out); !os.IsNotExist(err) {
		panic("不覆寫既有收據")
	}
	rom, err := os.ReadFile(*romPath)
	must(err)
	if digest(rom) != "0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29" {
		panic("ROM失配")
	}
	archive, err := os.ReadFile(*receipt)
	must(err)
	z, err := zip.NewReader(bytes.NewReader(archive), int64(len(archive)))
	must(err)
	files := map[string][]byte{}
	for _, f := range z.File {
		if f.Name == "status.json" || f.Name == "frame-index.bin" {
			r, e := f.Open()
			must(e)
			files[f.Name], e = io.ReadAll(r)
			must(e)
			must(r.Close())
		}
	}
	var status struct {
		Mode     int
		Palette  [256][3]byte
		FrameSHA string `json:"frame_index_sha256"`
	}
	must(json.Unmarshal(files["status.json"], &status))
	frame := files["frame-index.bin"]
	if len(frame) != 64000 || digest(frame) != status.FrameSHA {
		panic("正常原件失配")
	}
	r := hd.New(rom, *materials)
	r.SetLanguage(i18n.Bundled(), "zh-Hant")
	origin := hd.Origin{X: 12, Y: 12, Valid: true}
	_, baseline := r.Render(frame, status.Palette, status.Mode, false, true, origin)
	if baseline.Reason != "matched-city" {
		panic("底圖不是完整正常城市: " + baseline.Reason)
	}
	var old [81]byte
	for row := 0; row < 9; row++ {
		copy(old[row*9:], frame[(61+row)*320+203:(61+row)*320+212])
	}
	entries := map[[81]byte][]alias{}
	counts := map[int]int{}
	total := 0
	for _, member := range []int{34, 35, 36, 37, 38, 39, 40, 41, 59} {
		if member >= int(binary.LittleEndian.Uint16(rom)) {
			panic("成員越界")
		}
		h := 18 + member*16
		off := int(binary.LittleEndian.Uint32(rom[h:]))
		n := int(binary.LittleEndian.Uint16(rom[h+4:]))
		if off < 0 || n < 2 || off+n > len(rom) {
			panic("成員形態失配")
		}
		lib := rom[off : off+n]
		count := int(binary.LittleEndian.Uint16(lib))
		counts[member] = count
		if 2+count*2 > len(lib) {
			panic("offset表越界")
		}
		for index := 0; index < count; index++ {
			a := int(binary.LittleEndian.Uint16(lib[2+index*2:]))
			b := len(lib)
			if index+1 < count {
				b = int(binary.LittleEndian.Uint16(lib[4+index*2:]))
			}
			if a < 2+count*2 || b > len(lib) || b-a != 85 || binary.LittleEndian.Uint16(lib[a:]) != 9 || binary.LittleEndian.Uint16(lib[a+2:]) != 9 {
				panic("不是完整9x9來源")
			}
			var source [81]byte
			copy(source[:], lib[a+4:b])
			entries[source] = append(entries[source], alias{member, index, off + a + 4})
			total++
		}
	}
	if total != 1134 || len(entries) != 1049 {
		panic("實際來源數與已盤點版本不符")
	}
	input := append([]byte(nil), frame...)
	records := make([]record, 0, len(entries))
	known, painted, black := 0, 0, 0
	start := time.Now()
	for source, aliases := range entries {
		for row := 0; row < 9; row++ {
			copy(input[(61+row)*320+203:], source[row*9:(row+1)*9])
		}
		shown, stats := r.Render(input, status.Palette, status.Mode, false, true, origin)
		if stats.Reason != "matched-city" {
			panic("合成輸入破壞城市閘門")
		}
		changed := 0
		for y := 0; y < 36; y++ {
			for x := 0; x < 36; x++ {
				c := status.Palette[source[(y/4)*9+x/4]]
				actual := shown.RGBAAt(812+x, 244+y)
				if actual.R != c[0] || actual.G != c[1] || actual.B != c[2] || actual.A != 255 {
					changed++
				}
			}
		}
		isBlack := source == [81]byte{}
		isKnown := stats.Matched == baseline.Matched
		isPainted := stats.Painted == baseline.Painted
		if isKnown {
			known++
		}
		if isPainted {
			painted++
		}
		if isBlack {
			black++
		}
		records = append(records, record{digest(source[:]), aliases, isKnown, isPainted, changed, isBlack, stats})
	}
	sort.Slice(records, func(i, j int) bool {
		a, b := records[i].Aliases[0], records[j].Aliases[0]
		return a.Member < b.Member || a.Member == b.Member && a.Image < b.Image
	})
	for row := 0; row < 9; row++ {
		copy(input[(61+row)*320+203:], old[row*9:(row+1)*9])
	}
	if !bytes.Equal(input, frame) {
		panic("原始副本未回復")
	}
	script, err := os.ReadFile("/workspace/app/cmd/map-coverage-audit/main.go")
	must(err)
	result := map[string]any{"issue": 62, "schema": 1, "rom_sha256": digest(rom), "normal_seed_receipt_sha256": digest(archive),
		"original_frame_sha256": digest(frame), "tool_sha256": digest(script), "go_version": runtime.Version(),
		"synthetic_renderer_input": true, "runs_original_vm": false, "normal_player_test": false,
		"address_space": "RS201.ROM file offsets; zero-based member/image; native 320x200 source cells",
		"counts":        counts, "entries": total, "unique_sources": len(entries), "source_known": known, "painted_without_context": painted,
		"all_zero_placeholders": black, "elapsed_seconds": time.Since(start).Seconds(), "baseline": baseline, "records": records}
	data, err := json.MarshalIndent(result, "", "  ")
	must(err)
	if s, err := os.Stat(filepath.Dir(*out)); err != nil || !s.IsDir() {
		panic("輸出根不存在")
	}
	must(os.WriteFile(*out, append(data, '\n'), 0600))
	fmt.Printf("source inventory: %d entries / %d unique; known %d, painted without context %d, black %d\n", total, len(entries), known, painted, black)
}
