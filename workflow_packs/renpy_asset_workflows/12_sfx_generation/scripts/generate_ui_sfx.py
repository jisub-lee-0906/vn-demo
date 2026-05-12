#!/usr/bin/env python3
"""Generate tiny procedural WAV SFX prototypes for VN UI/testing.
No external dependencies. Convert with ffmpeg, e.g.:
  ffmpeg -y -i ui_click.wav -c:a libvorbis ui_click.ogg
"""
from pathlib import Path
import wave, struct, math, random

OUT = Path(__file__).resolve().parents[1] / 'generated_wav'
OUT.mkdir(parents=True, exist_ok=True)
SR = 44100

def write_wav(path, samples):
    samples = [max(-1.0, min(1.0, s)) for s in samples]
    with wave.open(str(path), 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        for s in samples:
            w.writeframes(struct.pack('<h', int(s * 32767)))

def sine(freq, dur, amp=0.35, decay=4.0):
    n = int(SR * dur)
    return [amp * math.sin(2*math.pi*freq*i/SR) * math.exp(-decay*i/n) for i in range(n)]

def click():
    a = sine(1400, 0.055, 0.22, 7.0)
    b = sine(2300, 0.035, 0.10, 8.0)
    n = max(len(a), len(b))
    return [(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0) for i in range(n)]

def confirm():
    return sine(880, 0.08, 0.18, 3.0) + sine(1320, 0.11, 0.16, 3.5)

def cancel():
    return sine(520, 0.08, 0.18, 3.0) + sine(330, 0.12, 0.16, 4.0)

def shimmer():
    n = int(SR * 0.9)
    out = []
    for i in range(n):
        t = i/SR
        env = math.exp(-2.4*t)
        sig = 0.08*math.sin(2*math.pi*(900+500*t)*t) + 0.06*math.sin(2*math.pi*(1600+700*t)*t)
        sig += random.uniform(-0.02, 0.02) * env
        out.append(sig * env)
    return out

write_wav(OUT/'ui_click.wav', click())
write_wav(OUT/'ui_confirm.wav', confirm())
write_wav(OUT/'ui_cancel.wav', cancel())
write_wav(OUT/'magic_shimmer_proto.wav', shimmer())
print(f'wrote WAV prototypes under {OUT}')
