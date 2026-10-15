package hd

import (
	"encoding/binary"
	"image"
)

// Identical nearest-neighbour pixels, with one expanded row and three copies.
// 042: avoid sixteen tiny RGB copies for every original pixel on every frame.
func expandIndexed4x(dst *image.RGBA, px []byte, pal [256][3]byte) {
	var colours [256]uint64
	for i, rgb := range pal {
		v := uint64(rgb[0]) | uint64(rgb[1])<<8 | uint64(rgb[2])<<16 | uint64(255)<<24
		colours[i] = v | v<<32
	}
	for y := 0; y < 200; y++ {
		at := y * 4 * dst.Stride
		row := dst.Pix[at : at+1280*4]
		for x, index := range px[y*320 : (y+1)*320] {
			v := colours[index]
			binary.LittleEndian.PutUint64(row[x*16:x*16+8], v)
			binary.LittleEndian.PutUint64(row[x*16+8:x*16+16], v)
		}
		for dy := 1; dy < 4; dy++ {
			copy(dst.Pix[at+dy*dst.Stride:at+dy*dst.Stride+len(row)], row)
		}
	}
}
