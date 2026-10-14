// 039 DRAFT：正常EXE入口、唯讀繪圖呼叫與返回像素；不是產品覆繪。
package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/binary"
	"encoding/json"
	"flag"
	"fmt"
	"image"
	"os"
	"path/filepath"
	"runtime"
	"sort"

	dg "github.com/wicanr2/dosgolem"
)

func must(err error) {
	if err != nil {
		panic(err)
	}
}
func hash(raw []byte) string { return fmt.Sprintf("%x", sha256.Sum256(raw)) }

type source struct {
	ID, Canonical, ROM, Encoding string
	Member, Image, Width, Height int
	Offset                       int    `json:"file_offset"`
	RawSHA                       string `json:"raw_sha256"`
	PixelSHA                     string `json:"pixels_sha256"`
	raw, pixels                  []byte
}

type draw struct {
	Label, Sample                    string
	ID, Encoding                     string
	Step, End                        uint64
	EA                               uint32 `json:"ida_loader_linear"`
	Pointer, Return, Buffer          uint32
	X, Y                             int
	Clip                             [4]int
	Transparent                      bool
	Key                              byte
	BeforeSHA, ExpectedSHA, AfterSHA string
	Matched                          bool
	PaletteSHA                       string
	source                           *source
	rect                             image.Rectangle
	expected                         []byte
	before, after                    []byte
}

func main() {
	original := flag.String("original", "/orig", "唯讀原版")
	inputs := flag.String("inputs", "", "DRAFT完整來源目錄")
	out := flag.String("out", "", "新的本機輸出目錄")
	limit := flag.Uint64("steps", 800000000, "正常入口觀察上限")
	flag.Parse()
	if *inputs == "" || *out == "" || *limit == 0 {
		panic("參數不足")
	}
	if _, e := os.Lstat(*out); !os.IsNotExist(e) {
		panic("不覆寫原件")
	}
	indexRaw, err := os.ReadFile(filepath.Join(*inputs, "inventory.json"))
	must(err)
	var index struct {
		Stage  string
		Images []source
	}
	must(json.Unmarshal(indexRaw, &index))
	if index.Stage != "DRAFT" || len(index.Images) != 209 {
		panic("來源形態失配")
	}
	roms := map[string][]byte{}
	for name, want := range map[string]string{"RS201.ROM": "0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29", "RS201A.ROM": "5d66f238dce650b8a407986100392ee4b8ac2aa23a033e80a7ca18ed91b3d9b0"} {
		rom, e := os.ReadFile(filepath.Join(*original, name))
		must(e)
		if hash(rom) != want {
			panic("ROM失配")
		}
		roms[name] = rom
	}
	for i := range index.Images {
		s := &index.Images[i]
		rom := roms[s.ROM]
		h := 18 + s.Member*16
		off := int(binary.LittleEndian.Uint32(rom[h:]))
		n := int(binary.LittleEndian.Uint16(rom[h+4:]))
		end := off + n
		for _, other := range index.Images {
			if other.ROM == s.ROM && other.Member == s.Member && other.Offset > s.Offset && other.Offset < end {
				end = other.Offset
			}
		}
		if s.Offset < off || s.Offset >= end || end > len(rom) {
			panic("原始定位越界")
		}
		s.raw = rom[s.Offset:end]
		if hash(s.raw) != s.RawSHA {
			panic("原始bytes失配")
		}
		s.pixels, err = os.ReadFile(filepath.Join(*inputs, s.Canonical, "source.bin"))
		must(err)
		if len(s.pixels) != s.Width*s.Height || hash(s.pixels) != s.PixelSHA {
			panic("解碼來源失配")
		}
	}
	exe, err := os.ReadFile(filepath.Join(*original, "RS201.EXE"))
	must(err)
	if hash(exe) != "798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3" {
		panic("EXE失配")
	}
	m := dg.New()
	must(m.LoadEXE(exe))
	m.SetAdLib(true)
	tail := []byte("/A /D /x")
	psp := uint32(dg.PSPSeg) * 16
	m.Write8(psp+0x80, byte(len(tail)))
	m.WriteBytes(psp+0x81, tail)
	m.Write8(psp+0x81+uint32(len(tail)), 13)
	dos := dg.NewDOS(m, *original)
	dos.Install()
	defer dos.Close()
	dos.BlockingBIOSKeys = true
	must(os.Mkdir(*out, 0700))
	records := []draw{}
	var active *draw
	counts := map[string]int{}
	seen := map[string]bool{}
	firstArea := map[string]int{}
	largest := map[string]draw{}
	palettes := map[string][256][3]byte{}
	paletteEvents := []map[string]any{}
	nextPalette := uint64(0)
	lastPalette := ""
	export := func(d draw, sample string) {
		d.Label = fmt.Sprintf("call-%03d", len(records))
		d.Sample = sample
		must(os.WriteFile(filepath.Join(*out, d.Label+"-before.bin"), d.before, 0600))
		must(os.WriteFile(filepath.Join(*out, d.Label+"-after.bin"), d.after, 0600))
		records = append(records, d)
	}
	region := func(buffer uint32, rect image.Rectangle) []byte {
		if buffer+64000 > uint32(len(m.Mem)) || !rect.In(image.Rect(0, 0, 320, 200)) {
			panic("原版緩衝越界")
		}
		result := make([]byte, 0, rect.Dx()*rect.Dy())
		for y := rect.Min.Y; y < rect.Max.Y; y++ {
			at := buffer + uint32(y*320+rect.Min.X)
			result = append(result, m.Mem[at:at+uint32(rect.Dx())]...)
		}
		return result
	}
	for m.Steps < *limit && !dos.Exited && !m.CPU.Halted {
		if m.Steps >= nextPalette {
			nextPalette = m.Steps + 500000
			palette := m.Palette()
			data, e := json.Marshal(palette)
			must(e)
			key := hash(data)
			if key != lastPalette {
				palettes[key] = palette
				paletteEvents = append(paletteEvents, map[string]any{"step": m.Steps, "palette_sha256": key, "frame_index_sha256": hash(m.Indexed())})
				lastPalette = key
			}
		}
		pc := uint32(m.CPU.Seg[dg.CS])*16 + uint32(m.CPU.IP)
		if active != nil && pc == active.Return {
			after := region(active.Buffer, active.rect)
			active.End = m.Steps
			active.AfterSHA = hash(after)
			active.Matched = bytes.Equal(after, active.expected)
			active.after = after
			if !active.Matched {
				panic(fmt.Sprintf("原版完整返回像素失配 %s EA%x", active.ID, active.EA))
			}
			counts[active.ID]++
			key := fmt.Sprintf("%s/%x/%t", active.ID, active.EA, active.Transparent)
			if !seen[key] {
				seen[key] = true
				firstArea[key] = active.rect.Dx() * active.rect.Dy()
				export(*active, "first")
				fmt.Printf("CONFIRMED %s EA%x xy%d,%d clip%v opaque=%t step=%d\n", active.ID, active.EA, active.X, active.Y, active.Clip, !active.Transparent, m.Steps)
			}
			if prior, ok := largest[key]; !ok || active.rect.Dx()*active.rect.Dy() > prior.rect.Dx()*prior.rect.Dy() {
				largest[key] = *active
			}
			active = nil
		}
		if m.ImageBase != uint32(dg.LoadSeg)*16 {
			panic("未知原版基址")
		}
		ea := pc - m.ImageBase + 0x10000
		if ea == 0x1605e || ea == 0x160c5 || ea == 0x16129 || ea == 0x16164 || ea == 0x161c3 || ea == 0x16210 {
			if active != nil {
				panic("未知繪圖巢狀")
			}
			sp := uint32(m.CPU.Seg[dg.SS])*16 + uint32(m.CPU.R[dg.SP])
			arg := func(n uint32) uint16 { return m.Read16(sp + n) }
			x, y := int(arg(4)), int(arg(6))
			ptr := uint32(arg(10))*16 + uint32(arg(8))
			clip := image.Rect(0, 0, 320, 200)
			transparent := ea == 0x1605e || ea == 0x160c5 || ea == 0x16164
			key := byte(255)
			if ea == 0x161c3 || ea == 0x16210 {
				ptr = uint32(arg(6))*16 + uint32(arg(4))
				sx, sy, w, h, dx, dy := int(arg(8)), int(arg(10)), int(arg(12)), int(arg(14)), int(arg(16)), int(arg(18))
				clip = image.Rect(dx, dy, dx+w, dy+h)
				x, y = dx-sx, dy-sy
				transparent = ea == 0x16210
				key = byte(arg(20))
			}
			for i := range index.Images {
				s := &index.Images[i]
				if ptr+uint32(len(s.raw)) > uint32(len(m.Mem)) || !bytes.Equal(m.Mem[ptr:ptr+uint32(len(s.raw))], s.raw) {
					continue
				}
				if s.Encoding == "iv2" && ea != 0x16164 {
					panic("IV2呼叫契約不同")
				}
				rect := image.Rect(x, y, x+s.Width, y+s.Height).Intersect(clip)
				if rect.Empty() || !rect.In(image.Rect(0, 0, 320, 200)) {
					panic("未確認繪圖裁切")
				}
				buffer := uint32(m.Read16(m.ImageBase+0x23216)) * 16
				before := region(buffer, rect)
				expected := append([]byte(nil), before...)
				for dy := rect.Min.Y; dy < rect.Max.Y; dy++ {
					for dx := rect.Min.X; dx < rect.Max.X; dx++ {
						v := s.pixels[(dy-y)*s.Width+dx-x]
						if transparent && v == key {
							continue
						}
						expected[(dy-rect.Min.Y)*rect.Dx()+dx-rect.Min.X] = v
					}
				}
				palette := m.Palette()
				palRaw, _ := json.Marshal(palette)
				palSHA := hash(palRaw)
				palettes[palSHA] = palette
				active = &draw{ID: s.ID, Encoding: s.Encoding, Step: m.Steps, EA: ea, Pointer: ptr, Return: uint32(arg(2))*16 + uint32(arg(0)), Buffer: buffer,
					X: x, Y: y, Clip: [4]int{rect.Min.X, rect.Min.Y, rect.Dx(), rect.Dy()}, Transparent: transparent, Key: key,
					BeforeSHA: hash(before), ExpectedSHA: hash(expected), PaletteSHA: palSHA, source: s, rect: rect, expected: expected, before: before}
				break
			}
		}
		must(m.Step())
		if dos.Blocked {
			break
		}
	}
	keys := make([]string, 0, len(largest))
	for key := range largest {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	for _, key := range keys {
		d := largest[key]
		if d.rect.Dx()*d.rect.Dy() > firstArea[key] {
			export(d, "largest-visible")
		}
	}
	tool, err := os.ReadFile("/workspace/app/cmd/illustration-source-audit/main.go")
	must(err)
	result := map[string]any{"schema": 1, "issue": 32, "stage": "DRAFT", "exe_sha256": hash(exe), "inventory_sha256": hash(indexRaw),
		"tool_sha256": hash(tool), "go_version": runtime.Version(), "steps": m.Steps, "limit": *limit, "calls": records, "call_counts": counts, "palettes": palettes, "palette_events": paletteEvents,
		"normal_exe_entry": true, "state_injection": false, "checkpoint": false, "normal_gui": false, "native_exit_tested": dos.Exited, "dos_blocked": dos.Blocked,
		"address_space": "EA=IDA loader linear; Pointer/Return/Buffer=runtime physical; input file offsets only in source inventory",
		"scope":         "原版無輸入正常前段的唯讀呼叫與完整後緩衝驗證；不是HD接入、正常GUI或發布畫面收據"}
	data, err := json.MarshalIndent(result, "", "  ")
	must(err)
	must(os.WriteFile(filepath.Join(*out, "audit.json"), append(data, '\n'), 0600))
	fmt.Printf("DRAFT: %d source/call contracts, %d steps, blocked=%t\n", len(records), m.Steps, dos.Blocked)
}
