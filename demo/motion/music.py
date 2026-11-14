"""Synthesize an original, royalty-free music bed for the demo films (100 BPM).

python3 music.py out.wav <seconds> <style: playful|calm> [whoosh times...]
"""
import sys
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 44100
BPM = 100
BEAT = 60 / BPM
BAR = 4 * BEAT

out, dur, style = sys.argv[1], float(sys.argv[2]), sys.argv[3]
whooshes = [float(x) for x in sys.argv[4:]]
N = int(dur * SR)
t = np.arange(N) / SR
rng = np.random.default_rng(7)


def note(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, fc, order=2):
    return sosfilt(butter(order, fc, 'low', fs=SR, output='sos'), x)


def hp(x, fc, order=2):
    return sosfilt(butter(order, fc, 'high', fs=SR, output='sos'), x)


def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], 'band', fs=SR, output='sos'), x)


def saw(f, tt):
    return 2 * ((f * tt) % 1) - 1


def place(buf, start, sig, gain=1.0):
    i = int(start * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += gain * sig[: j - i]


if style == 'playful':      # SpeechLP: bright, bouncy, C major  I–V–vi–IV
    prog = [[48, 52, 55, 60, 64], [43, 50, 55, 59, 62], [45, 52, 57, 60, 64], [41, 48, 53, 57, 60]]
    pluck_oct, pad_cut, hat_gain, kick_gain = 24, 1800, 0.05, 0.55
else:                       # SpeechTherapist.app: calm, confident, A minor-ish  vi–IV–I–V
    prog = [[45, 52, 57, 60, 64], [41, 48, 53, 57, 60], [48, 52, 55, 60, 64], [43, 50, 55, 59, 62]]
    pluck_oct, pad_cut, hat_gain, kick_gain = 12, 1400, 0.035, 0.45

n_bars = int(np.ceil(dur / BAR))
pad = np.zeros(N); bass = np.zeros(N); pluck = np.zeros(N); drums = np.zeros(N); fx = np.zeros(N)

for b in range(n_bars):
    ch = prog[b % 4]
    t0 = b * BAR
    seg = np.arange(int(BAR * SR) + int(0.3 * SR)) / SR
    env = np.minimum(1, seg / 0.25) * np.exp(-np.maximum(0, seg - BAR) / 0.15)
    # pad: detuned saws on chord tones
    p = np.zeros_like(seg)
    for m in ch[1:]:
        for det in (-0.07, 0, 0.07):
            p += saw(note(m + det), seg)
    place(pad, t0, p * env / 12)
    # bass: eighth-note pulse on the root
    for k in range(8):
        st = k * BEAT / 2
        s2 = np.arange(int(BEAT / 2 * SR)) / SR
        e2 = np.exp(-s2 / 0.18) * np.minimum(1, s2 / 0.005)
        f = note(ch[0] - 12)
        sig = np.tanh(1.6 * (np.sin(2 * np.pi * f * s2) + 0.3 * np.sin(4 * np.pi * f * s2))) * e2
        place(bass, t0 + st, sig, 0.32 if k % 2 == 0 else 0.22)
    # pluck arpeggio (16ths in playful, 8ths in calm)
    step = BEAT / 4 if style == 'playful' else BEAT / 2
    pattern = [1, 2, 3, 4, 3, 2, 4, 3] if style == 'playful' else [1, 3, 2, 4]
    for k in range(int(BAR / step)):
        m = ch[pattern[k % len(pattern)]] + pluck_oct
        s3 = np.arange(int(0.6 * SR)) / SR
        f = note(m)
        sig = (np.sin(2 * np.pi * f * s3) + 0.35 * np.sin(4 * np.pi * f * s3) + 0.12 * np.sin(6 * np.pi * f * s3))
        sig *= np.exp(-s3 / (0.16 if style == 'playful' else 0.32)) * np.minimum(1, s3 / 0.003)
        acc = 1.0 if k % 4 == 0 else 0.7
        place(pluck, t0 + k * step, sig, 0.09 * acc)
    # drums from bar 2 onward (intro is pad + pluck only)
    if b >= 1:
        for k in range(4):
            s4 = np.arange(int(0.4 * SR)) / SR
            f = 45 + 90 * np.exp(-s4 / 0.04)
            kick = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-s4 / 0.16)
            place(drums, t0 + k * BEAT, kick, kick_gain * (1 if k % 2 == 0 else 0.75))
            s5 = np.arange(int(0.08 * SR)) / SR
            hat = hp(rng.standard_normal(len(s5)), 7000) * np.exp(-s5 / 0.02)
            place(drums, t0 + k * BEAT + BEAT / 2, hat, hat_gain)
            if k in (1, 3) and style == 'playful':
                s6 = np.arange(int(0.2 * SR)) / SR
                clap = bp(rng.standard_normal(len(s6)), 900, 3500) * np.exp(-s6 / 0.06)
                place(drums, t0 + k * BEAT, clap, 0.12)

# sidechain-style pump on the pad
beat_phase = (t % BEAT) / BEAT
duck = 1 - 0.45 * np.exp(-beat_phase * 6) * (t > BAR)
pad = lp(pad, pad_cut) * duck
pluck = lp(pluck, 6000)

# whooshes into each scene change
for w in whooshes:
    s7 = np.arange(int(0.7 * SR)) / SR
    nz = rng.standard_normal(len(s7))
    sweep = np.zeros_like(nz)
    for lo, hi, a, b2 in [(300, 900, 0, .35), (900, 2500, .2, .5), (2500, 6000, .35, .7)]:
        m = (s7 >= a) & (s7 < b2)
        sweep += bp(nz, lo, hi) * m
    env = np.sin(np.pi * np.clip(s7 / 0.7, 0, 1)) ** 2
    place(fx, max(0, w - 0.55), lp(sweep, 7000) * env, 0.10)

mix = hp(1.1 * pad + 0.45 * bass + 2.2 * pluck + 0.6 * drums + fx, 70)
# simple stereo: pluck/hats slightly wide via short delays
L = mix + 0.25 * np.roll(pluck, int(0.011 * SR))
R = mix + 0.25 * np.roll(pluck, int(0.017 * SR))
st = np.stack([L, R], 1)
fade = np.minimum(1, t / 1.0) * np.minimum(1, (dur - t) / 1.6)
st *= fade[:, None]
st /= np.max(np.abs(st)) + 1e-9
st *= 0.89
wavfile.write(out, SR, (st * 32767).astype(np.int16))
print('wrote', out, f'{dur:.1f}s')
