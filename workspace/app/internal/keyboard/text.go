// Package keyboard 將前端有序 ASCII 文字轉為原生 set 1 通斷碼。
package keyboard

import "strings"

type Modifiers struct {
	LeftShift, RightShift, CapsLock bool
	CapsHeld                        bool
}

// Feed 追蹤實際排入 IRQ1 的狀態，避免用較晚讀到的主機鍵盤狀態解釋舊文字事件。
func (m *Modifiers) Feed(scan byte) {
	switch scan {
	case 0x2a:
		m.LeftShift = true
	case 0xaa:
		m.LeftShift = false
	case 0x36:
		m.RightShift = true
	case 0xb6:
		m.RightShift = false
	case 0x3a:
		if !m.CapsHeld {
			m.CapsLock = !m.CapsLock
		}
		m.CapsHeld = true
	case 0xba:
		m.CapsHeld = false
	}
}

// PrintableScan 判斷本前端以文字事件處理的實體鍵。
func PrintableScan(scan byte) bool {
	return scan >= 0x02 && scan <= 0x0d || scan >= 0x10 && scan <= 0x1b ||
		scan >= 0x1e && scan <= 0x29 || scan == 0x2b ||
		scan >= 0x2c && scan <= 0x35 || scan == 0x39
}

// Stroke 的輸出仍經 QueueScanCodes、IRQ1 與 BIOS，沒有文字注入捷徑。
func Stroke(ch rune, mods Modifiers) ([]byte, bool) {
	var scan byte
	shift := false
	letter := ch >= 'a' && ch <= 'z' || ch >= 'A' && ch <= 'Z'
	if letter {
		shift = ch >= 'A' && ch <= 'Z'
		if shift {
			ch += 'a' - 'A'
		}
		for _, row := range []struct {
			text  string
			first byte
		}{{"qwertyuiop", 0x10}, {"asdfghjkl", 0x1e}, {"zxcvbnm", 0x2c}} {
			if i := strings.IndexRune(row.text, ch); i >= 0 {
				scan = row.first + byte(i)
				break
			}
		}
		shift = shift != mods.CapsLock
	} else {
		plain := "1234567890-=qwertyuiop[]asdfghjkl;'`\\zxcvbnm,./ "
		upper := "!@#$%^&*()_+QWERTYUIOP{}ASDFGHJKL:\"~|ZXCVBNM<>? "
		scans := []byte{2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 57}
		i := strings.IndexRune(plain, ch)
		if i < 0 {
			i = strings.IndexRune(upper, ch)
			shift = true
		}
		if i < 0 {
			return nil, false
		}
		scan = scans[i]
	}
	var codes []byte
	held := mods.LeftShift || mods.RightShift
	if !shift {
		if mods.LeftShift {
			codes = append(codes, 0xaa)
		}
		if mods.RightShift {
			codes = append(codes, 0xb6)
		}
	} else if !held {
		codes = append(codes, 0x2a)
	}
	codes = append(codes, scan, scan|0x80)
	if !shift {
		if mods.LeftShift {
			codes = append(codes, 0x2a)
		}
		if mods.RightShift {
			codes = append(codes, 0x36)
		}
	} else if !held {
		codes = append(codes, 0xaa)
	}
	return codes, true
}
