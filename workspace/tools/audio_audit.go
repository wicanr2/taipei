// #17：唯讀原版冷啟動，於保存狀態前盤點真正的即時音訊事件。
package main

import (
	"crypto/sha256"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"runtime"

	dg "github.com/wicanr2/dosgolem"
)

func main() {
	root := flag.String("original", "/orig", "唯讀原版目錄")
	tail := flag.String("args", "/A /D /x", "研究啟動參數")
	adlib := flag.Bool("adlib", true, "AdLib 是否存在")
	limit := flag.Uint64("steps", 850000001, "有界指令數")
	scratch := flag.String("scratch", "/out/audio-scratch", "獨立寫入目錄")
	eventPath := flag.String("events", "", "本機原版 OPL 事件序列，不入 Git")
	flag.Parse()
	raw, err := os.ReadFile(filepath.Join(*root, "RS201.EXE")); check(err)
	hash := fmt.Sprintf("%x", sha256.Sum256(raw))
	if hash != "798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3" { panic("輸入雜湊不符") }
	check(os.MkdirAll(*scratch,0700))
	m := dg.New(); check(m.LoadEXE(raw)); m.SetAdLib(*adlib)
	base := uint32(dg.PSPSeg)*16
	m.Write8(base+0x80,byte(len(*tail))); m.WriteBytes(base+0x81,[]byte(*tail)); m.Write8(base+0x81+uint32(len(*tail)),13)
	d := dg.NewDOS(m,*root); d.Install(); defer d.Close()
	d.Scratch=*scratch; d.BlockingBIOSKeys=true
	// 固定啟動基線相同的兩次原生空白鍵，沒有 Stdin 或狀態注入。
	events := []struct{step uint64; scan byte}{{700000000,0x39},{750000000,0xb9},{800000000,0x39},{850000000,0xb9}}
	next:=0
	for m.Steps<*limit && !d.Exited && !m.CPU.Halted {
		for next<len(events) && m.Steps>=events[next].step { m.QueueScanCodes(events[next].scan);next++ }
		check(m.Step())
	}
	ports:=map[uint16]int{}; var audioPorts []map[string]any
	for _,w:=range m.PortLog { ports[w.Port]++; if w.Port==0x42 || w.Port==0x43 || w.Port==0x61 { audioPorts=append(audioPorts,map[string]any{"step":w.Step,"port":w.Port,"value":w.Val}) } }
	regs:=map[uint8]int{}; rhythm,keys:=0,0
	for _,w:=range m.OPL { regs[w.Reg]++; if w.Reg==0xbd && w.Val&0x20!=0 { rhythm++ }; if w.Reg>=0xb0 && w.Reg<=0xb8 && w.Val&0x20!=0 { keys++ } }
	if *eventPath!="" {
		f,e:=os.Create(*eventPath);check(e)
		for _,w:=range m.OPL { _,e=fmt.Fprintf(f,"%d %d %d %d\n",w.Step,w.Bank,w.Reg,w.Val);check(e) }
		check(f.Close())
	}
	check(json.NewEncoder(os.Stdout).Encode(map[string]any{"schema":1,"go":runtime.Version(),"input_sha256":hash,"args":*tail,"adlib":*adlib,"steps":m.Steps,"opl_writes":len(m.OPL),"opl_registers":regs,"opl_key_ons":keys,"rhythm_enables":rhythm,"ports":ports,"audio_port_events":audioPorts,"speaker_changes":len(m.Speaker),"frame_index_sha256":fmt.Sprintf("%x",sha256.Sum256(m.Indexed())),"registers":m.CPU.R,"missing":d.Missing,"unimplemented":d.UnimplementedDetails}))
}
func check(err error){if err!=nil{panic(err)}}
