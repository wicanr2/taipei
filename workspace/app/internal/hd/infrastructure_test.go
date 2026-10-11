package hd

import (
	"bytes"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"image"
	"image/draw"
	"image/png"
	"os"
	"path/filepath"
	"testing"
)

func infrastructureFixture(t *testing.T) ([]byte, string, *infrastructureSet, [256][3]byte) {
	t.Helper()
	dir, orig := os.Getenv("TAIPEI_HD_MATERIALS"), os.Getenv("TAIPEI_HD_ORIGINAL")
	if dir == "" || orig == "" {
		t.Skip("需要 026 本機固定資產與唯讀 ROM")
	}
	rom, err := os.ReadFile(filepath.Join(orig, "RS201.ROM"))
	if err != nil {
		t.Fatal(err)
	}
	u := loadInfrastructure(rom, dir)
	if len(u.tiles) != 25 || len(u.textures) != 3 {
		t.Fatal("第一批來源或固定材質未載入", len(u.tiles), len(u.textures))
	}
	for _, tile := range u.tiles {
		if tile.reason != "" {
			t.Fatal(tile.image, tile.reason)
		}
	}
	return rom, dir, u, u.palette
}

func infrastructurePNG(t *testing.T, path string) image.Image {
	t.Helper()
	f, err := os.Open(path)
	if err != nil {
		t.Fatal(err)
	}
	defer f.Close()
	im, err := png.Decode(f)
	if err != nil {
		t.Fatal(err)
	}
	return im
}

func TestInfrastructureReadySourcesAndPixels(t *testing.T) {
	_, dir, u, pal := infrastructureFixture(t)
	negative := 0
	for source, tile := range u.tiles {
		dst := image.NewRGBA(image.Rect(0, 0, 1280, 800))
		for i := range dst.Pix {
			dst.Pix[i] = byte(i % 251)
		}
		want := image.NewRGBA(dst.Bounds())
		copy(want.Pix, dst.Pix)
		ref := infrastructurePNG(t, filepath.Join(dir, "infrastructure-v5", fmt.Sprintf("39-%03d.png", tile.image)))
		draw.Draw(want, image.Rect(20, 136, 56, 172), ref, image.Point{}, draw.Src)
		if why := u.paint(dst, tile, pal, 0, 0, Origin{Valid: true}); why != "matched-infrastructure" || !bytes.Equal(dst.Pix, want.Pix) {
			t.Fatal("整格或全部區外與 READY 前 v5 不符", tile.image, why)
		}
		for i := range source {
			changed := source
			changed[i] ^= 128
			if u.tiles[changed] != nil {
				t.Fatal("單像素失配仍識別", tile.image, i)
			}
			negative++
		}
		// 真正用色才是此來源的色盤閘門。
		var used [256]bool
		for _, i := range source {
			used[i] = true
		}
		for _, i := range tile.used {
			changed := pal
			changed[i][0] ^= 1
			before := append([]byte(nil), dst.Pix...)
			if why := u.paint(dst, tile, changed, 0, 0, Origin{Valid: true}); why != "palette-mismatch" || !bytes.Equal(before, dst.Pix) {
				t.Fatal("已用色失配沒有整格回退", tile.image, i, why)
			}
		}
		changed := pal
		for i, present := range used {
			if !present {
				changed[i][0] ^= 1
			}
		}
		if why := u.paint(dst, tile, changed, 0, 0, Origin{Valid: true}); why != "matched-infrastructure" || !bytes.Equal(dst.Pix, want.Pix) {
			t.Fatal("未用色變化誤拒絕", tile.image, why)
		}
	}
	if negative != 2025 {
		t.Fatal(negative)
	}
	t.Log("25 張完整固定原型、全部區外及 2025 項來源負對照、逐已用色與全部未用色通過")
}

func TestInfrastructureNormalReceipts(t *testing.T) {
	rom, dir, _, _ := infrastructureFixture(t)
	root := filepath.Join(dir, "infrastructure-v5-expanded")
	raw, err := os.ReadFile(filepath.Join(root, "manifest.json"))
	if err != nil || digest(raw) != "b59376311fafe2265bc7a2208c4426b20d33c35cafa4dcf989261794354ee32b" {
		t.Fatal("固定正常原位比較失配", err)
	}
	var m struct {
		Proofs []struct {
			Receipt    string
			ReceiptSHA string `json:"receipt_sha256"`
			PNG        string
			Origin     Origin
			Painted    []json.RawMessage
		}
	}
	if json.Unmarshal(raw, &m) != nil || len(m.Proofs) != 7 {
		t.Fatal("七種原位比較缺少")
	}
	r := New(rom, dir)
	r.sources = map[string]bool{}
	r.menu, r.icons, r.chrome, r.footer = nil, nil, nil, nil
	total := 0
	for _, p := range m.Proofs {
		s, px := readFileSample(t, fileSample{Receipt: p.Receipt, ReceiptSHA: p.ReceiptSHA})
		before := append([]byte(nil), px...)
		palBefore := s.Palette
		im, st := r.Render(px, s.Palette, s.Mode, s.Blocked, true, p.Origin)
		want := image.NewRGBA(im.Bounds())
		draw.Draw(want, want.Bounds(), infrastructurePNG(t, filepath.Join(root, p.PNG)), image.Point{}, draw.Src)
		if st.Infrastructure.Painted != len(p.Painted) || st.Infrastructure.Fallback != 0 || st.Matched != len(p.Painted) || st.Painted != len(p.Painted) || st.Fallback != 435-len(p.Painted) || !bytes.Equal(want.Pix, im.Pix) {
			t.Fatal("正常原位完整來源、計數或全部區外不符", p.PNG, st)
		}
		if !bytes.Equal(before, px) || s.Palette != palBefore {
			t.Fatal("改寫原版輸入")
		}
		total += st.Infrastructure.Painted
		native, st := r.Render(px, s.Palette, s.Mode, s.Blocked, false, p.Origin)
		if st.Infrastructure.Matched != 0 || st.Infrastructure.Painted != 0 || st.Infrastructure.Images != nil || st.Infrastructure.Reasons != nil {
			t.Fatal("原版主題殘留家族收據", st)
		}
		base := append([]byte(nil), native.Pix...)
		for _, o := range []Origin{{}, {X: -1, Valid: true}, {Y: 75, Valid: true}} {
			im, st = r.Render(px, s.Palette, s.Mode, false, true, o)
			if st.Infrastructure.Matched != 0 || !bytes.Equal(base, im.Pix) {
				t.Fatal("原點失配仍畫入", st)
			}
		}
		im, st = r.Render(px, s.Palette, s.Mode, true, true, p.Origin)
		if st.Infrastructure.Matched != 0 || !bytes.Equal(base, im.Pix) {
			t.Fatal("阻塞場景仍畫入", st)
		}
	}
	if total != 140 {
		t.Fatal(total)
	}
	t.Log("七張正常原位、140 格、完整 1280×800、切換與原點／場景回退通過")
}

func TestInfrastructureActualAssetFaults(t *testing.T) {
	rom, dir, complete, pal := infrastructureFixture(t)
	names := []string{"infrastructure-ready-v1/manifest.json", "asphalt-b-v1.png", "sand-b-v1.png", "forest-b-v1.png"}
	for _, i := range infrastructureImages {
		for _, suffix := range []string{"indices", "weights"} {
			names = append(names, fmt.Sprintf("infrastructure-ready-v1/39-%03d-%s.bin", i, suffix))
		}
	}
	cases := 0
	for _, target := range names {
		for _, fault := range []string{"missing", "corrupt", "length"} {
			tmp := t.TempDir()
			for _, name := range names {
				path := filepath.Join(tmp, name)
				if err := os.MkdirAll(filepath.Dir(path), 0700); err != nil {
					t.Fatal(err)
				}
				var err error
				if name != target {
					err = os.Symlink(filepath.Join(dir, name), path)
				} else if fault != "missing" {
					var raw []byte
					raw, err = os.ReadFile(filepath.Join(dir, name))
					if err == nil {
						if fault == "corrupt" {
							raw[len(raw)/2] ^= 1
						} else {
							raw = raw[:len(raw)-1]
						}
						err = os.WriteFile(path, raw, 0600)
					}
				}
				if err != nil {
					t.Fatal(err)
				}
			}
			broken := loadInfrastructure(rom, tmp)
			for _, tile := range broken.tiles {
				shouldFail := target == names[0] || target == names[1]
				for _, index := range tile.used {
					name, _ := infrastructureMaterial(index)
					shouldFail = shouldFail || target == name+"-b-v1.png"
				}
				for _, suffix := range []string{"indices", "weights"} {
					shouldFail = shouldFail || target == fmt.Sprintf("infrastructure-ready-v1/39-%03d-%s.bin", tile.image, suffix)
				}
				dst := image.NewRGBA(image.Rect(0, 0, 1280, 800))
				before := append([]byte(nil), dst.Pix...)
				why := broken.paint(dst, tile, pal, 0, 0, Origin{Valid: true})
				if (why != "matched-infrastructure") != shouldFail || (shouldFail && !bytes.Equal(before, dst.Pix)) {
					t.Fatal("實際資產故障或其他來源隔離不符", target, fault, tile.image, shouldFail, why)
				}
			}
			cases++
		}
	}
	if cases != 162 {
		t.Fatal(cases)
	}
	// 其餘 50 張原始來源不列入第一批，包含 18 張候選。
	off := int(binary.LittleEndian.Uint32(rom[18+39*16:]))
	for i := 0; i < 75; i++ {
		a := int(binary.LittleEndian.Uint16(rom[off+2+i*2:]))
		var source [81]byte
		copy(source[:], rom[off+a+4:off+a+85])
		_, known := complete.tiles[source]
		want := false
		for _, selected := range infrastructureImages {
			want = want || i == selected
		}
		if known != want {
			t.Fatal("候選與正式來源混用", i)
		}
	}
	t.Log("162 項實際資產撤除／損壞／長度錯及逐來源隔離通過；其餘 50 張回退")
}

func TestInfrastructureWorldPhase(t *testing.T) {
	_, dir, u, pal := infrastructureFixture(t)
	for _, index := range []int{15, 25, 45, 55} {
		var tile *infrastructureTile
		for _, candidate := range u.tiles {
			if candidate.image == index {
				tile = candidate
			}
		}
		for number, world := range [][2]int{{0, 0}, {1250, 1250}, {-40, -40}, {1260, -1260}} {
			want := infrastructurePNG(t, filepath.Join(dir, "infrastructure-v5", fmt.Sprintf("phase-39-%03d-%d.png", index, number)))
			for y := 0; y < 36; y++ {
				for x := 0; x < 36; x++ {
					at := (y*36 + x) * 4
					var total [3]int
					for j := 0; j < 4; j++ {
						if tile.weights[at+j] == 0 {
							continue
						}
						index := tile.indices[at+j]
						c := u.color(index, world[0]+x, world[1]+y, pal[index])
						for k, v := range c {
							total[k] += int(v) * int(tile.weights[at+j])
						}
					}
					r, g, b, a := want.At(x, y).RGBA()
					if total[0]/255 != int(r>>8) || total[1]/255 != int(g>>8) || total[2]/255 != int(b>>8) || a != 65535 {
						t.Fatal("固定世界相位與獨立原型不符", index, world, x, y)
					}
				}
			}
		}
	}
	for i := -5016; i <= 5016; i++ {
		if v := infrastructureMirror(i); v < 0 || v >= 1254 {
			t.Fatal(i, v)
		}
	}
	t.Log("16 張固定世界材質測圖與正負鏡像邊界通過")
}
