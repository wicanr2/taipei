package main

import (
	"bytes"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"image"
	"image/png"
	"os"
	"path/filepath"
	"strconv"
)

type endingFields struct {
	EndingScreen string `json:"ending_screen"`
	EndingReason string `json:"ending_reason"`
	HDReason     string `json:"reason"`
}

type endingReference struct {
	source  []byte
	palette map[int][3]byte
	image   image.Image
}

func readEndingReference(dir, original string) *endingReference {
	if dir == "" {
		return nil
	}
	protoRaw, err := os.ReadFile(filepath.Join(dir, "ending-scene-v1", "manifest.json"))
	check(err)
	if powerSHA(protoRaw) != "a86c26d3d8731d0d59042d7f461e3cf9468c32f431e127ecae5e1d421d357e41" {
		panic("政績 READY 前原型 manifest 不符")
	}
	var proto struct {
		SourceCheckSHA string `json:"source_check_sha256"`
	}
	check(json.Unmarshal(protoRaw, &proto))
	raw, err := os.ReadFile(filepath.Join(dir, "..", "..", "runs", "ending-scene-native", "source-check.json"))
	check(err)
	if powerSHA(raw) != proto.SourceCheckSHA {
		panic("政績原版證據失配")
	}
	var source struct {
		Palette map[string][3]byte `json:"used_palette"`
	}
	check(json.Unmarshal(raw, &source))
	rom, err := os.ReadFile(filepath.Join(original, "RS201.ROM"))
	check(err)
	if powerSHA(rom) != "0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29" {
		panic("政績唯讀 ROM 不符")
	}
	offset := int(binary.LittleEndian.Uint32(rom[18+23*16:]))
	size := int(binary.LittleEndian.Uint16(rom[22+23*16:]))
	if offset != 193647 || size != 17587 {
		panic("政績原版成員定位不符")
	}
	data := rom[offset : offset+size]
	if !bytes.Equal(data[:4], []byte{64, 1, 200, 0}) {
		panic("政績原版尺寸不符")
	}
	ref := &endingReference{palette: map[int][3]byte{}}
	for at := 4; at < len(data); {
		value, count := data[at], 1
		at++
		if value == 0 {
			if at+2 > len(data) || data[at+1] == 0 {
				panic("政績原版串流不完整")
			}
			value, count = data[at], int(data[at+1])
			at += 2
		}
		ref.source = append(ref.source, bytes.Repeat([]byte{value}, count)...)
		if len(ref.source) > 64000 {
			panic("政績原版串流越界")
		}
	}
	if len(ref.source) != 64000 || powerSHA(ref.source) != "0040b4374f37464862ae2f89da5bc897ddb7f53d539edd597cf8b2b6ff784ebd" || len(source.Palette) != 23 {
		panic("政績完整來源不符")
	}
	for text, rgb := range source.Palette {
		i, err := strconv.Atoi(text)
		check(err)
		if i < 0 || i > 255 {
			panic("政績色盤索引越界")
		}
		ref.palette[i] = rgb
	}
	raw, err = os.ReadFile(filepath.Join(dir, "ending-scene-v1", "presentation.png"))
	check(err)
	if powerSHA(raw) != "b37fddad8ea9cc3bbc505af3a3daad1f5cb59e86c213d98d12bbf279da81cfb0" {
		panic("政績完整獨立原型不符")
	}
	ref.image, err = png.Decode(bytes.NewReader(raw))
	check(err)
	if ref.image.Bounds() != image.Rect(0, 0, 1280, 800) {
		panic("政績獨立原型尺寸不符")
	}
	return ref
}

func (r *endingReference) audit(px []byte, pal [256][3]byte, mode int, enabled, blocked bool, h endingFields) (image.Image, error) {
	if r == nil {
		if h.EndingScreen != "" {
			return nil, fmt.Errorf("政績 HD 缺 -ending-reference")
		}
		return nil, nil
	}
	known := bytes.Equal(px, r.source)
	active := known && mode == 19 && enabled && blocked
	paletteOK := true
	for i, rgb := range r.palette {
		paletteOK = paletteOK && pal[i] == rgb
	}
	wantReason := "scene-fallback"
	if !enabled {
		wantReason = "original"
	} else if known && mode == 19 {
		if !blocked {
			wantReason = "ending-unverified-phase"
		} else if !paletteOK {
			wantReason = "ending-palette-mismatch"
		} else {
			wantReason = "matched-ending-screen"
		}
	}
	if h.EndingReason != wantReason {
		return nil, fmt.Errorf("政績拒絕原因不符：%q，期望 %q", h.EndingReason, wantReason)
	}
	if active && paletteOK {
		if h.EndingScreen != "achievement-base" || h.HDReason != "matched-ending-screen" {
			return nil, fmt.Errorf("政績完整家族或統計不符")
		}
		return r.image, nil
	}
	if h.EndingScreen != "" {
		return nil, fmt.Errorf("未確認政績來源或相位仍回報 HD")
	}
	return nil, nil
}
