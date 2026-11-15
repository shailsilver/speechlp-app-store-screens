"""Cut voiceover lines from the raw recordings (via Whisper word timestamps) and
place them on each film's timeline.

python3 voiceover.py <vo_dir_with r304.wav,r305.wav,r304.json,r305.json> <out_dir>
Writes <out_dir>/vo_lp.wav, vo_st.wav, vo_docs.wav (44.1 kHz mono, film length).
"""
import json
import re
import sys
import numpy as np
from scipy.io import wavfile

VO, OUT = sys.argv[1], sys.argv[2]
SR = 44100


def load(name):
    import subprocess
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', f'{VO}/{name}.wav', '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'],
                         capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    words = [w for s in json.load(open(f'{VO}/{name}.json')) for w in s['words']]
    for w in words:
        w['norm'] = re.sub(r'[^a-z0-9]', '', w['word'].lower())
    return x, words


REC = {n: load(n) for n in ['r304', 'r305']}


def find(rec, phrase, after=0.0, occurrence=1):
    """Return (start, end) of the phrase's words in recording `rec`, searching after `after` s."""
    words = REC[rec][1]
    target = [re.sub(r'[^a-z0-9]', '', t.lower()) for t in phrase.split()]
    hits = 0
    for i in range(len(words) - len(target) + 1):
        if words[i]['start'] < after:
            continue
        if all(words[i + k]['norm'] == target[k] for k in range(len(target))):
            hits += 1
            if hits == occurrence:
                return words[i]['start'], words[i + len(target) - 1]['end']
    raise ValueError(f'not found: {phrase} in {rec}')


def clip(rec, first, last, after=0.0, occurrence=1, pad_in=0.10, pad_out=0.28, tighten=0.35):
    """Audio from the first word of `first` to the last word of `last`, internal pauses tightened."""
    s0, _ = find(rec, first, after, occurrence)
    _, e1 = find(rec, last, s0)
    x = REC[rec][0]
    a = x[max(0, int((s0 - pad_in) * SR)): int((e1 + pad_out) * SR)].copy()
    # tighten pauses longer than `tighten` seconds (keeps natural rhythm, removes dead air)
    hop = int(0.02 * SR)
    env = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a) - hop, hop)])
    thr = max(np.percentile(env, 15) * 2.5, 10 ** (-42 / 20))
    quiet = env < thr
    keep = np.ones(len(a), bool)
    i = 0
    while i < len(quiet):
        if quiet[i]:
            j = i
            while j < len(quiet) and quiet[j]:
                j += 1
            run = (j - i) * 0.02
            if run > tighten and i > 0 and j < len(quiet):
                cut = run - tighten
                mid = (i + j) / 2 * hop
                keep[int(mid - cut * SR / 2): int(mid + cut * SR / 2)] = False
            i = j
        else:
            i += 1
    a = a[keep]
    f = int(0.012 * SR)                                    # tiny fades, no clicks
    a[:f] *= np.linspace(0, 1, f); a[-f:] *= np.linspace(1, 0, f)
    return a


def build(name, dur, cues):
    track = np.zeros(int(dur * SR), np.float32)
    t_prev = 0.0
    for at, a in cues:
        at = max(at, t_prev + 0.25)
        i = int(at * SR); j = min(len(track), i + len(a))
        track[i:j] += a[: j - i]
        t_prev = at + len(a) / SR
        print(f'  {name}: {at:6.2f}-{t_prev:6.2f}')
    if t_prev > dur - 0.6:
        print(f'  WARNING {name}: voice runs to {t_prev:.2f}s (film {dur}s)')
    wavfile.write(f'{OUT}/vo_{name}.wav', SR, (np.clip(track, -1, 1) * 32767).astype(np.int16))


# ---- Film 1: SpeechLP (70.0s) — recording 304, second take of the opening line
take2 = find('r304', 'Speech practice your child', 0, 2)[0] - 0.05
build('lp', 70.0, [
    (0.6,  clip('r304', 'Speech practice', 'want to play', after=take2)),
    (5.0,  clip('r304', 'This is', 'pathologists')),
    (10.0, clip('r304', 'A guided', 'by level')),
    (17.0, clip('r304', 'Age -based', 'consonant')),
    (22.6, clip('r304', 'Certified SLPs', 'they play')),
    (30.0, clip('r304', '7 speaking', 'hungry bear')),
    (40.4, clip('r304', 'Kids say', 'the match')),
    (46.4, clip('r304', 'Their friends', 'they practice')),
    (51.0, clip('r304', 'and every pack', 'to collect')),
    (58.0, clip('r304', 'Every word is', 'SLPs')),
    (64.4, clip('r304', 'Speech LP on', 'the web')),
])

# ---- Film 2: SpeechTherapist.app home practice (46.0s) — recording 305, second "Now you'll know"
nyk2 = find('r305', "Now you'll know", 0, 2)[0] - 0.05
build('st', 46.0, [
    (0.5,  clip('r305', 'What happens', 'sessions')),
    (2.4,  clip('r305', "Now you'll", 'know', after=nyk2)),
    (5.2,  clip('r305', 'SpeechTherapist .app the', 'to SpeechLP')),
    (10.2, clip('r305', 'Share a', 'instantly')),
    (16.0, clip('r305', 'Choose target', 'SpeechLP app')),
    (23.0, clip('r305', 'Then see', 'each sound')),
    (30.6, clip('r305', 'And decide', 'next')),
    (34.0, clip('r305', 'Privacy built', 'any audio')),
    (39.0, clip('r305', '$20 a seat', 'free plan', after=40)),
    (42.6, clip('r305', 'SpeechTherapist .app', 'SpeechTherapist .app', after=50)),
])

# ---- Film 3: SpeechTherapist.app documentation (60.4s) — recording 305 second half
build('docs', 60.4, [
    (0.6,  clip('r305', 'Spend less', 'treating')),
    (5.2,  clip('r305', 'One app', 'schools')),
    (10.0, clip('r305', 'Record or', 'typing')),
    (15.4, clip('r305', 'Your soap', 'sign off')),
    (25.0, clip('r305', 'You always', 'final say')),
    (29.4, clip('r305', 'Clinical insights', 'next session')),
    (34.4, clip('r305', 'Evaluations', 'lesson plans')),
    (40.2, clip('r305', 'And for schools', 'funding reports')),
    (46.2, clip('r305', 'Invite caregivers', 'either setting')),
    (53.2, clip('r305', 'Documentation included', 'per month', after=100)),
    (57.4, clip('r305', 'SpeechTherapist .app', 'SpeechTherapist .app', after=108)),
])
