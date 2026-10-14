package hd

import (
	"bytes"
	"encoding/json"
	"image"
	"image/draw"
	"os"
	"path/filepath"
	"testing"
)

func transportFixture(t *testing.T) ([]byte, string, *publicFacilitySet) {
	t.Helper()
	dir, orig := os.Getenv("TAIPEI_HD_MATERIALS"), os.Getenv("TAIPEI_HD_ORIGINAL")
	if dir == "" || orig == "" {
		t.Skip("需要 037 素材與唯讀原版")
	}
	rom, err := os.ReadFile(filepath.Join(orig, "RS201.ROM"))
	if err != nil {
		t.Fatal(err)
	}
	u := loadTransportFacilities(rom, dir)
	if u.reason != "" || len(u.tiles) != 72 || len(u.atlases) != 2 {
		t.Fatal("72 種來源／兩 atlas 未載入", u.reason)
	}
	return rom, dir, u
}

func TestTransportFacilitiesNormalSourcesAndIsolation(t *testing.T) {
	rom, dir, u := transportFixture(t)
	root := os.Getenv("TAIPEI_TRANSPORT_RECEIPTS")
	if root == "" {
		t.Fatal("需要正常 GUI 來源")
	}
	for _, sample := range []struct {
		id, proofSHA string
		col, row     int
	}{
		{"port", "0c0616fe918189c68e35846fd916f786090806c49fc882dab87c561f46c6d70d", 22, 3},
		{"airport", "61aeb6803546ef6edb48c81e38a109d41aece97e078247c7aa901aca04434327", 11, 5},
	} {
		raw, err := os.ReadFile(filepath.Join(dir, "transport-v1", sample.id, "source.json"))
		if err != nil || digest(raw) != sample.proofSHA {
			t.Fatal("固定來源證明失配", sample.id, err)
		}
		var proof struct {
			Receipt string
			SHA     string `json:"receipt_sha256"`
			Origin  Origin
		}
		if err := json.Unmarshal(raw, &proof); err != nil {
			t.Fatal(err)
		}
		receipt := filepath.Join(root, filepath.Base(filepath.Dir(proof.Receipt)), filepath.Base(proof.Receipt))
		s, px := readFileSample(t, fileSample{Receipt: receipt, ReceiptSHA: proof.SHA})
		before := append([]byte(nil), px...)
		r := New(rom, dir)
		shown, stats := r.Render(px, s.Palette, s.Mode, false, true, proof.Origin)
		if stats.TransportFacilities.Painted != 36 || stats.TransportFacilities.Fallback != 0 || !bytes.Equal(px, before) {
			t.Fatal("正常完整來源未覆繪或原版變動", sample.id, stats.TransportFacilities)
		}
		im := infrastructurePNG(t, filepath.Join(dir, "transport-prototype-v1", sample.id+".png"))
		ref := image.NewRGBA(im.Bounds())
		draw.Draw(ref, ref.Bounds(), im, im.Bounds().Min, draw.Src)
		left, top := 20+sample.col*36, 136+sample.row*36
		for y := 0; y < 216; y++ {
			for x := 0; x < 216; x++ {
				if shown.RGBAAt(left+x, top+y) != ref.RGBAAt(x, y) {
					t.Fatal("完整圖與固定候選不符", sample.id, x, y)
				}
			}
		}
		fallback := New(rom, dir)
		fallback.transportFacilities.reason = "test-disabled"
		baseline, _ := fallback.Render(px, s.Palette, s.Mode, false, true, proof.Origin)
		for y := 0; y < 800; y++ {
			for x := 0; x < 1280; x++ {
				if x >= left && x < left+216 && y >= top && y < top+216 {
					continue
				}
				if shown.RGBAAt(x, y) != baseline.RGBAAt(x, y) {
					t.Fatal("設施區外變動", sample.id, x, y)
				}
			}
		}
		for _, gate := range []struct {
			blocked, enabled bool
			origin           Origin
		}{
			{false, false, proof.Origin}, {true, true, proof.Origin}, {false, true, Origin{}},
		} {
			_, st := r.Render(px, s.Palette, s.Mode, gate.blocked, gate.enabled, gate.origin)
			if st.TransportFacilities.Matched != 0 {
				t.Fatal("場景未隔離", sample.id)
			}
		}
		for source := range u.tiles {
			if r.nuclearFacility.tiles[source] != nil || r.publicFacilities.tiles[source] != nil || r.powerFacility.tiles[source] != nil || r.civicFacilities.tiles[source] != nil || r.cityBuildings.tiles[source] != nil || r.infrastructure.tiles[source] != nil {
				t.Fatal("運輸設施與其他家族來源衝突", sample.id)
			}
		}
	}
}

func TestTransportFacilitiesSourcesPaletteAndActualFaults(t *testing.T) {
	rom, dir, u := transportFixture(t)
	dst := image.NewRGBA(image.Rect(0, 0, 1280, 800))
	for source, tile := range u.tiles {
		for i := range source {
			bad := source
			bad[i] ^= 128
			if u.tiles[bad] != nil {
				t.Fatal("來源失配仍辨識", tile.id, i)
			}
		}
		pal := u.palette
		pal[tile.used[0]][0] ^= 1
		before := append([]byte(nil), dst.Pix...)
		if u.paint(dst, tile, pal, 0, 0) != "palette-mismatch" || !bytes.Equal(dst.Pix, before) {
			t.Fatal("已用色盤失配仍覆繪", tile.id)
		}
		unused := u.palette
		for i := 0; i < 256; i++ {
			if !bytes.Contains(source[:], []byte{byte(i)}) {
				unused[i][0] ^= 1
			}
		}
		if u.paint(dst, tile, unused, tile.col, tile.row) != "matched-transport-facility" {
			t.Fatal("未用色盤誤拒絕", tile.id)
		}
	}
	for _, name := range []string{"manifest.json", "airport.png", "port.png"} {
		for _, fault := range []string{"missing", "corrupt"} {
			root := t.TempDir()
			target := filepath.Join(root, "transport-ready-v1")
			if err := os.Mkdir(target, 0700); err != nil {
				t.Fatal(err)
			}
			for _, n := range []string{"manifest.json", "airport.png", "port.png"} {
				data, err := os.ReadFile(filepath.Join(dir, "transport-ready-v1", n))
				if err != nil {
					t.Fatal(err)
				}
				if n == name {
					if fault == "missing" {
						continue
					}
					data[len(data)/2] ^= 1
				}
				if err := os.WriteFile(filepath.Join(target, n), data, 0600); err != nil {
					t.Fatal(err)
				}
			}
			broken := loadTransportFacilities(rom, root)
			for id, tiles := range u.facilities {
				before := append([]byte(nil), dst.Pix...)
				painted := broken.paint(dst, tiles[0], u.palette, 0, 0) == "matched-transport-facility"
				want := name != "manifest.json" && name != id+".png"
				if painted != want || (!want && !bytes.Equal(before, dst.Pix)) {
					t.Fatal("素材故障未隔離", name, fault, id)
				}
			}
		}
	}
}
