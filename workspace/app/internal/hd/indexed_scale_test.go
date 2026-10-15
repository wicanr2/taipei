package hd

import (
	"bytes"
	"image"
	"testing"
)

func TestIndexedScaleAllColoursMatchesReference(t *testing.T) {
	px := make([]byte, 64000)
	var pal [256][3]byte
	for i := range pal {
		pal[i] = [3]byte{byte(i), byte(i * 19), byte(255 - i)}
	}
	for i := range px {
		px[i] = byte(i*37 + i/320)
	}
	want, got := image.NewRGBA(image.Rect(0, 0, 1280, 800)), image.NewRGBA(image.Rect(0, 0, 1280, 800))
	for y := 0; y < 800; y++ {
		for x := 0; x < 1280; x++ {
			c := pal[px[(y/4)*320+x/4]]
			at := y*want.Stride + x*4
			copy(want.Pix[at:at+3], c[:])
			want.Pix[at+3] = 255
		}
	}
	expandIndexed4x(got, px, pal)
	if !bytes.Equal(got.Pix, want.Pix) {
		t.Fatal("nearest-neighbour expansion changed pixels")
	}
}
