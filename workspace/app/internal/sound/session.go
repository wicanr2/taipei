// Package sound connects original hardware events to the host player.
// Contract: docs/spec/009-opl2-audio.md. No game rules live here.
package sound

import (
	"crypto/sha256"
	"encoding/binary"
	"fmt"
	"hash"
	"time"

	ebaudio "github.com/hajimehoshi/ebiten/v2/audio"
	dg "github.com/wicanr2/dosgolem"
	a "github.com/wicanr2/dosgolem/audio"
	"github.com/wicanr2/dosgolem/audio/ymfm"
)

type Session struct {
	stream                          *a.Stream
	synth                           *ymfm.Synth
	ring                            *a.Ring
	player                          *ebaudio.Player
	context                         *ebaudio.Context
	pcmHash                         hash.Hash
	muted, closed                   bool
	frames, nonzero, events, rhythm uint64
	peak                            int
}

func New(muted bool) (*Session, error) {
	synth, e := ymfm.New(48000)
	if e != nil {
		return nil, e
	}
	stream, e := a.New(48000, a.StepsPerSecond(), synth)
	if e != nil {
		synth.Close()
		return nil, e
	}
	s := &Session{stream: stream, synth: synth, muted: muted, pcmHash: sha256.New()}
	if muted {
		return s, nil
	}
	s.ring, e = a.NewRing(48000)
	if e != nil {
		s.Close()
		return nil, e
	}
	s.context = ebaudio.NewContext(48000)
	s.player, e = s.context.NewPlayer(s.ring)
	if e != nil {
		s.Close()
		return nil, e
	}
	s.player.SetBufferSize(100 * time.Millisecond)
	s.player.Play()
	return s, nil
}

// Wait for the device and leave room for a complete VM update. Device startup
// or suspension must not make the VM produce an unbounded audio backlog.
func (s *Session) CanAdvance(steps uint64) bool {
	if s.muted {
		return true
	}
	if s.closed || !s.context.IsReady() {
		return false
	}
	frames := int(float64(steps)*48000/a.StepsPerSecond()) + 2
	stats := s.ring.Stats()
	return stats.Capacity-stats.Buffered >= frames*4
}
func (s *Session) Submit(m *dg.Machine) error {
	s.events += uint64(len(m.OPL))
	for _, e := range m.OPL {
		if e.Reg == 0xbd && e.Val&0x20 != 0 {
			s.rhythm++
		}
	}
	pcm, e := s.stream.Drain(m)
	if e != nil {
		return e
	}
	s.frames += uint64(len(pcm) / 4)
	s.pcmHash.Write(pcm)
	for i := 0; i < len(pcm); i += 4 {
		v := int(int16(binary.LittleEndian.Uint16(pcm[i:])))
		if v != 0 {
			s.nonzero++
		}
		if v < 0 {
			v = -v
		}
		if v > s.peak {
			s.peak = v
		}
	}
	if s.ring != nil {
		return s.ring.Push(pcm)
	}
	return nil
}
func (s *Session) Close() {
	if s.closed {
		return
	}
	s.closed = true
	if s.ring != nil {
		s.ring.Close()
	}
	if s.player != nil {
		s.player.Close()
	}
	if s.synth != nil {
		s.synth.Close()
	}
}
func (s *Session) Stats() map[string]any {
	result := map[string]any{"muted": s.muted, "closed": s.closed, "sample_rate": 48000, "frames": s.frames, "nonzero_frames": s.nonzero, "opl_events": s.events, "rhythm_enables": s.rhythm, "peak": s.peak, "pcm_sha256": fmt.Sprintf("%x", s.pcmHash.Sum(nil)), "timing": "hardware-spec approximation"}
	if s.ring != nil {
		result["ring"] = s.ring.Stats()
		result["device_ready"] = s.context.IsReady()
	}
	return result
}
