package hd

import (
	"bytes"
	"fmt"
	"image"
	"image/draw"
	"os"
	"path/filepath"
	"testing"
)

func cityBuildingFixture(t *testing.T) ([]byte, string, *cityBuildingSet) {
	t.Helper()
	dir, orig := os.Getenv("TAIPEI_HD_MATERIALS"), os.Getenv("TAIPEI_HD_ORIGINAL")
	if dir == "" || orig == "" {
		t.Skip("需要 034 固定原型與唯讀 ROM")
	}
	rom, err := os.ReadFile(filepath.Join(orig, "RS201.ROM"))
	if err != nil {
		t.Fatal(err)
	}
	u := loadCityBuildings(rom, dir)
	if len(u.tiles) != 48 || len(u.atlases) != 3 || u.reason != "" {
		t.Fatal("48 格固定素材未載入", len(u.tiles), len(u.atlases), u.reason)
	}
	return rom, dir, u
}

func TestCityBuildingsAtlasAndSources(t *testing.T) {
	_, dir, u := cityBuildingFixture(t)
	dst := image.NewRGBA(image.Rect(0, 0, 1280, 800))
	for i := range dst.Pix {
		dst.Pix[i] = byte(i % 251)
	}
	want := image.NewRGBA(dst.Bounds())
	copy(want.Pix, dst.Pix)
	for _, member := range []int{34, 35, 36} {
		ref := infrastructurePNG(t, filepath.Join(dir, "disaster-buildings-prototype-v1", fmt.Sprintf("%d.png", member)))
		x := 20 + (member-34)*6*36
		draw.Draw(want, image.Rect(x, 172, x+144, 316), ref, image.Point{}, draw.Src)
	}
	negatives := 0
	for source, tile := range u.tiles {
		if u.paint(dst, tile, u.palette, (tile.member-34)*6+tile.col, tile.row+1) != "matched-city-building" {
			t.Fatal(tile.member, tile.image)
		}
		for i := range source {
			changed := source
			changed[i] ^= 128
			if u.tiles[changed] != nil {
				t.Fatal("來源失配仍辨識", tile.member, tile.image, i)
			}
			negatives++
		}
		bad := u.palette
		bad[tile.used[0]][0] ^= 1
		before := append([]byte(nil), dst.Pix...)
		if u.paint(dst, tile, bad, 0, 0) != "palette-mismatch" || !bytes.Equal(before, dst.Pix) {
			t.Fatal("已用色失配未回退")
		}
		unused := u.palette
		for i := 0; i < 256; i++ {
			if !bytes.Contains(source[:], []byte{byte(i)}) {
				unused[i][0] ^= 1
			}
		}
		if u.paint(dst, tile, unused, (tile.member-34)*6+tile.col, tile.row+1) != "matched-city-building" {
			t.Fatal("未用色誤拒絕")
		}
	}
	if negatives != 3888 || !bytes.Equal(dst.Pix, want.Pix) {
		t.Fatal("完整三圖重組、區外或來源反例失敗", negatives)
	}
	t.Log("48 格、三個完整 atlas、全部區外、3888 項來源失配及已用／未用色盤通過")
}

func TestCityBuildingsActualLoaderFaults(t *testing.T) {
	rom, dir, _ := cityBuildingFixture(t)
	files := map[string][]byte{}
	for _, name := range []string{"manifest.json", "34.png", "35.png", "36.png"} {
		raw, err := os.ReadFile(filepath.Join(dir, "disaster-buildings-ready-v1", name))
		if err != nil {
			t.Fatal(err)
		}
		files[name] = raw
	}
	for _, name := range []string{"manifest.json", "34.png", "35.png", "36.png"} {
		for _, fault := range []string{"missing", "corrupt"} {
			t.Run(name+"-"+fault, func(t *testing.T) {
				temp := t.TempDir()
				root := filepath.Join(temp, "disaster-buildings-ready-v1")
				if err := os.Mkdir(root, 0700); err != nil {
					t.Fatal(err)
				}
				for file, raw := range files {
					data := append([]byte(nil), raw...)
					if file == name {
						if fault == "missing" {
							continue
						}
						data[len(data)/2] ^= 1
					}
					if err := os.WriteFile(filepath.Join(root, file), data, 0600); err != nil {
						t.Fatal(err)
					}
				}
				u := loadCityBuildings(rom, temp)
				painted := 0
				for _, tile := range u.tiles {
					dst := image.NewRGBA(image.Rect(0, 0, 1280, 800))
					why := u.paint(dst, tile, u.palette, 0, 0)
					shouldPaint := name != "manifest.json" && name != fmt.Sprintf("%d.png", tile.member)
					if (why == "matched-city-building") != shouldPaint {
						t.Fatal("資源故障未按成員隔離", tile.member, why)
					}
					if shouldPaint {
						painted++
					} else if !bytes.Equal(dst.Pix, make([]byte, len(dst.Pix))) {
						t.Fatal("故障覆繪原位或區外")
					}
				}
				if (name == "manifest.json" && painted != 0) || (name != "manifest.json" && painted != 32) {
					t.Fatal("其他成員被錯誤牽連", painted)
				}
			})
		}
	}
}

func TestCityBuildingsSceneAndOriginalIsolation(t *testing.T) {
	rom, dir, _ := cityBuildingFixture(t)
	root := os.Getenv("TAIPEI_BUILDING_RECEIPTS")
	if root == "" {
		t.Fatal("需要正常 DISA1 來源")
	}
	s, px := readFileSample(t, fileSample{Receipt: filepath.Join(root, "city-paused-capture.zip"), ReceiptSHA: "9a0587a7e0c2f8d3b966cb1a2d2add381b508fbca6c277406b1920a65b7094f9"})
	original := append([]byte(nil), px...)
	palette := s.Palette
	r := New(rom, dir)
	_, st := r.Render(px, palette, s.Mode, false, true, Origin{X: 6, Y: 22, Valid: true})
	if st.CityBuildings.Painted == 0 || st.CityBuildings.Fallback != 0 || !bytes.Equal(px, original) || palette != s.Palette {
		t.Fatal("正常來源未繪或改寫原版", st.CityBuildings)
	}
	for _, test := range []struct {
		blocked, enabled bool
		origin           Origin
	}{{false, false, Origin{X: 6, Y: 22, Valid: true}}, {true, true, Origin{X: 6, Y: 22, Valid: true}}, {false, true, Origin{}}} {
		_, st := r.Render(px, palette, s.Mode, test.blocked, test.enabled, test.origin)
		if st.CityBuildings.Matched != 0 || st.CityBuildings.Painted != 0 {
			t.Fatal("原版、阻塞或原點失配仍畫建物", st.CityBuildings)
		}
	}
}
