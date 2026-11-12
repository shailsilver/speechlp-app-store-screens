"""Render SpeechLP demo walkthrough videos from the app screenshots.

Usage: python3 demo/render_videos.py [tour|lessons|games|all]
Output: demo/videos/*.mp4 (886x1920, 30fps — App Store iPhone preview size)
"""
import math
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "demo" / "videos"
FONT = ROOT / "demo" / "assets" / "FunnelDisplay-Bold.ttf"

W, H, FPS = 886, 1920, 30
SRC_W, SRC_H = 1170, 2532          # screenshot size
SCR_W = 600                        # on-canvas screen width
SCR_H = round(SCR_W * SRC_H / SRC_W)
BEZEL = 16
PHONE_X = (W - SCR_W) // 2
PHONE_Y = 470
S = SCR_W / SRC_W                  # source -> screen scale

TOP_BAR = 110                      # status bar height (source px)
TAB_BAR = 2150                     # tab bar starts (source px)


# ---------------------------------------------------------------- helpers
def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def lerp(a, b, t):
    return a + (b - a) * t


@lru_cache(maxsize=None)
def src(n):
    return Image.open(ROOT / f"IMG_65{n}.png").convert("RGB")


@lru_cache(maxsize=None)
def screen_static(n):
    return src(n).resize((SCR_W, SCR_H), Image.LANCZOS)


def zoomed(n, z, cx, cy):
    """Screen-size view of screenshot n, zoomed z× around source point (cx, cy)."""
    if z <= 1.001:
        return screen_static(n)
    cw, ch = SRC_W / z, SRC_H / z
    x0 = min(max(cx - cw / 2, 0), SRC_W - cw)
    y0 = min(max(cy - ch / 2, 0), SRC_H - ch)
    return src(n).resize((SCR_W, SCR_H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))


def font(size):
    return ImageFont.truetype(str(FONT), size)


def gradient(c1, c2):
    g = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(g)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(round(lerp(a, b, t)) for a, b in zip(c1, c2)))
    return g


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


@lru_cache(maxsize=None)
def background(c1, c2):
    bg = gradient(hexrgb(c1), hexrgb(c2))
    # soft glow behind the phone
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse((60, 600, W - 60, 1700), fill=70)
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    bg.paste((255, 255, 255), (0, 0), glow)
    # phone shadow + bezel
    shadow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shadow).rounded_rectangle(
        (PHONE_X - BEZEL, PHONE_Y - BEZEL + 30, PHONE_X + SCR_W + BEZEL, PHONE_Y + SCR_H + BEZEL + 30),
        radius=90, fill=150)
    shadow = shadow.filter(ImageFilter.GaussianBlur(40))
    bg.paste((10, 10, 30), (0, 0), shadow)
    ImageDraw.Draw(bg).rounded_rectangle(
        (PHONE_X - BEZEL, PHONE_Y - BEZEL, PHONE_X + SCR_W + BEZEL, PHONE_Y + SCR_H + BEZEL),
        radius=88, fill=(17, 17, 22))
    return bg


@lru_cache(maxsize=None)
def screen_mask():
    m = Image.new("L", (SCR_W, SCR_H), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, SCR_W - 1, SCR_H - 1), radius=74, fill=255)
    return m


def wrap(text, f, maxw):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if f.getlength(trial) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


@lru_cache(maxsize=None)
def caption_layer(title, sub):
    """RGBA layer with the headline (and optional sub line) centred in the top area."""
    layer = Image.new("RGBA", (W, PHONE_Y - 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    size = 78
    while True:
        f = font(size)
        lines = wrap(title, f, W - 110)
        if len(lines) <= 2 or size <= 56:
            break
        size -= 4
    fs = font(38)
    lh = size * 1.08
    total = lh * len(lines) + (60 if sub else 0)
    y = (layer.height - total) / 2 + 10
    for ln in lines:
        x = (W - f.getlength(ln)) / 2
        d.text((x + 2, y + 4), ln, font=f, fill=(0, 0, 0, 70))
        d.text((x, y), ln, font=f, fill="white")
        y += lh
    if sub:
        y += 14
        x = (W - fs.getlength(sub)) / 2
        d.text((x, y), sub, font=fs, fill=(255, 255, 255, 215))
    return layer


def draw_tap(frame, sx, sy, p):
    """Tap indicator at source point (sx, sy), progress p in 0..1."""
    if not 0 <= p <= 1:
        return
    x = PHONE_X + sx * S
    y = PHONE_Y + sy * S
    ov = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    # finger dot: grows in, presses, fades
    dot_a = int(200 * (ease(p / 0.15) if p < 0.15 else (1 - ease((p - 0.55) / 0.45))))
    r = 34 * (0.85 if 0.2 < p < 0.4 else 1.0)
    d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, max(dot_a, 0)),
              outline=(80, 70, 200, max(dot_a, 0)), width=4)
    # ripple ring
    if p > 0.25:
        q = (p - 0.25) / 0.75
        rr = 34 + 90 * ease(q)
        a = int(230 * (1 - q))
        d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=(255, 255, 255, a), width=6)
    frame.alpha_composite(ov)


@lru_cache(maxsize=None)
def end_card_img(c1, c2, title, sub):
    card = gradient(hexrgb(c1), hexrgb(c2)).convert("RGBA")
    d = ImageDraw.Draw(card)
    f1, f2 = font(140), font(48)
    d.text(((W - f1.getlength(title)) / 2, 780), title, font=f1, fill="white")
    for j, ln in enumerate(wrap(sub, f2, W - 140)):
        d.text(((W - f2.getlength(ln)) / 2, 980 + j * 62), ln, font=f2, fill=(255, 255, 255, 230))
    return card


@lru_cache(maxsize=None)
def promo_card_img():
    """speechtherapist.app pricing card (for SLPs)."""
    card = gradient(hexrgb("#4A5FC1"), hexrgb("#2C3E8C")).convert("RGBA")
    d = ImageDraw.Draw(card)

    def center(text, f, y, fill="white"):
        d.text(((W - f.getlength(text)) / 2, y), text, font=f, fill=fill)

    fe = font(34)
    eyebrow = "FOR SPEECH THERAPISTS"
    # letter-spaced eyebrow
    sp = 8
    wdt = sum(fe.getlength(ch) for ch in eyebrow) + sp * (len(eyebrow) - 1)
    x = (W - wdt) / 2
    for ch in eyebrow:
        d.text((x, 560), ch, font=fe, fill=(255, 255, 255, 190))
        x += fe.getlength(ch) + sp
    size = 92
    while font(size).getlength("speechtherapist.app") > W - 100:
        size -= 2
    center("speechtherapist.app", font(size), 640)
    fp, fm = font(150), font(52)
    pw = fp.getlength("$20") + fm.getlength("/month")
    x = (W - pw) / 2
    d.text((x, 790), "$20", font=fp, fill="white")
    d.text((x + fp.getlength("$20") + 6, 868), "/month", font=fm, fill=(255, 255, 255, 210))
    fl = font(50)
    items = ["Sign up today", "Add your students", "Invite caregivers to connect"]
    block = max(fl.getlength(it) for it in items) + 70
    x0 = (W - block) / 2
    y = 1050
    for it in items:
        cx, cy, R, r = x0 + 24, y + 30, 26, 11
        pts = [(cx + (R if k % 2 == 0 else r) * math.sin(math.pi * k / 5),
                cy - (R if k % 2 == 0 else r) * math.cos(math.pi * k / 5)) for k in range(10)]
        d.polygon(pts, fill=(255, 213, 74))
        d.text((x0 + 70, y), it, font=fl, fill="white")
        y += 96
    return card


# ------------------------------------------------------- timeline engine
class Clip:
    """A segment of screen content: fn(local_t) -> screen image."""

    def __init__(self, dur, fn):
        self.dur, self.fn = dur, fn


def hold(n, dur, z0=1.0, z1=1.0, c0=(SRC_W / 2, SRC_H / 2), c1=None):
    c1 = c1 or c0

    def fn(t):
        k = ease(t / dur) if dur else 1
        return zoomed(n, lerp(z0, z1, k), lerp(c0[0], c1[0], k), lerp(c0[1], c1[1], k))
    return Clip(dur, fn)


def crossfade(a_img_fn, b_img_fn, dur):
    return Clip(dur, lambda t: Image.blend(a_img_fn(), b_img_fn(), ease(t / dur)))


def swipe(a, b, dur, keep_bars=True, direction=-1):
    """Horizontal carousel swipe from screenshot a to b (bars stay fixed)."""
    A, B = screen_static(a), screen_static(b)
    top, bot = round(TOP_BAR * S), round(TAB_BAR * S)

    def fn(t):
        k = ease(t / dur)
        off = round(SCR_W * k) * direction
        out = A.copy()
        out.paste((255, 255, 255), (0, top, SCR_W, bot))
        out.paste(A.crop((0, top, SCR_W, bot)), (off, top))
        out.paste(B.crop((0, top, SCR_W, bot)), (off - direction * SCR_W, top))
        if keep_bars:
            out.paste(A.crop((0, bot, SCR_W, SCR_H)), (0, bot))
            out.paste(A.crop((0, 0, SCR_W, top)), (0, 0))
        return out
    return Clip(dur, fn)


def vscroll(a, b, dur):
    """Vertical scroll: map of a moves down, map of b arrives from above (scrolling up the
    path). Only the map area between the baked-in top buttons and the tab bar scrolls;
    the top band crossfades and the tab bar stays fixed."""
    A, B = screen_static(a), screen_static(b)
    top, bot = round(240 * S), round(TAB_BAR * S)
    h = bot - top
    strip = Image.new("RGB", (SCR_W, 2 * h))
    strip.paste(B.crop((0, top, SCR_W, bot)), (0, 0))
    strip.paste(A.crop((0, top, SCR_W, bot)), (0, h))
    # feather the join so the two maps blend instead of meeting at a hard line
    fe = 50
    ramp = Image.linear_gradient("L").resize((SCR_W, fe))
    strip.paste(A.crop((0, top, SCR_W, top + fe)), (0, h - fe), ramp)
    At, Bt = A.crop((0, 0, SCR_W, top)), B.crop((0, 0, SCR_W, top))

    def fn(t):
        k = ease(t / dur)
        off = round(h * k)
        out = A.copy()
        out.paste(strip.crop((0, h - off, SCR_W, 2 * h - off)), (0, top))
        out.paste(Image.blend(At, Bt, k), (0, 0))
        return out
    return Clip(dur, fn)


def render(name, colors, clips, captions, taps, end_card=None, promo=True, subdir=""):
    """
    clips:    list of Clip, played back to back
    captions: list of (start, end, title, sub)
    taps:     list of (start, src_x, src_y) — each tap lasts 0.9s
    end_card: (title, sub, dur) shown full-screen after the clips
    """
    out_dir = OUT / subdir
    out_dir.mkdir(parents=True, exist_ok=True)
    total = sum(c.dur for c in clips)
    PROMO_DUR = 4.0
    end_dur = (end_card[2] if end_card else 0) + (PROMO_DUR if promo else 0)
    n_frames = round((total + end_dur) * FPS)
    bg = background(*colors)
    path = out_dir / f"{name}.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
           "-shortest", "-c:v", "libx264", "-preset", "slow", "-crf", "18",
           "-pix_fmt", "yuv420p", "-profile:v", "high", "-c:a", "aac", "-b:a", "128k",
           "-movflags", "+faststart", str(path)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    for i in range(n_frames):
        t = i / FPS
        if t < total:
            # which clip
            acc = 0
            for c in clips:
                if t < acc + c.dur or c is clips[-1]:
                    scr = c.fn(min(t - acc, c.dur))
                    break
                acc += c.dur
            frame = bg.copy().convert("RGBA")
            frame.paste(scr, (PHONE_X, PHONE_Y), screen_mask())
            # captions with fade
            for (s, e, title, sub) in captions:
                if s - 0.3 <= t <= e + 0.3:
                    a = min(ease((t - s + 0.3) / 0.4), ease((e + 0.3 - t) / 0.4))
                    lay = caption_layer(title, sub)
                    if a < 1:
                        lay = lay.copy()
                        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
                    dy = int((1 - a) * 18)
                    frame.alpha_composite(lay, (0, 10 + dy))
            for (s, sx, sy) in taps:
                draw_tap(frame, sx, sy, (t - s) / 0.9)
            # fade in from brand colour at start
            if t < 0.4:
                frame = Image.blend(Image.new("RGBA", (W, H), hexrgb(colors[0]) + (255,)),
                                    frame, ease(t / 0.4))
            last = frame
        else:
            te = t - total
            card = end_card_img(colors[0], colors[1], end_card[0], end_card[1])
            if te < end_card[2]:
                frame = Image.blend(last, card, ease(te / 0.6))
            else:
                frame = Image.blend(card, promo_card_img(), ease((te - end_card[2]) / 0.6))
        proc.stdin.write(frame.convert("RGB").tobytes())
    proc.stdin.close()
    proc.wait()
    print(f"wrote {path} ({total + end_dur:.1f}s)")
    return path


# --------------------------------------------------------------- videos
# Tap targets in source (1170x2532) coordinates
LEARN_TAB = (292, 2300)
PRACTICE_TAB = (878, 2300)
PENGUIN_PIN = (410, 985)
START_GAME = (585, 1865)
CHOOSE_SOUNDS = {80: (585, 512), 84: (585, 597), 85: (585, 595)}
CENTER = (SRC_W / 2, SRC_H / 2)

END = ("SpeechLP", "Learn from certified speech pathologists", 2.6)


def video_tour():
    clips = [
        hold(78, 3.0, 1.35, 1.0, PENGUIN_PIN, CENTER),            # 0.0
        vscroll(78, 83, 1.0),                                     # 3.0
        hold(83, 2.4),                                            # 4.0
        hold(83, 1.0),                                            # 6.4 tap Practice
        crossfade(lambda: screen_static(83), lambda: screen_static(80), 0.5),  # 7.4
        hold(80, 1.4),                                            # 7.9
        swipe(80, 81, 0.5), hold(81, 1.1),                        # 9.3
        swipe(81, 82, 0.5), hold(82, 1.1),                        # 10.9
        swipe(82, 85, 0.5), hold(85, 1.1),                        # 12.5
        swipe(85, 84, 0.5), hold(84, 2.2),                        # 14.1 (tap choose sounds @14.9)
        hold(84, 1.2),                                            # 16.8 tap start @16.9
        crossfade(lambda: screen_static(84), lambda: zoomed(86, 1.12, 585, 1100), 0.6),  # 18.0
        hold(86, 3.4, 1.12, 1.0, (585, 1100), CENTER),            # 18.6 -> 22.0
    ]
    captions = [
        (0.0, 6.6, "Level up through guided learning paths", None),
        (7.2, 14.5, "Games They'll Actually Want to Play", "Swipe to pick a game"),
        (14.7, 16.9, "Choose the sounds to practice", None),
        (17.1, 22.0, "Say it right — make it pass!", None),
    ]
    taps = [(6.5, *PRACTICE_TAB), (14.9, *CHOOSE_SOUNDS[84]), (16.9, *START_GAME)]
    render("01-app-tour", ("#4A5FC1", "#2C3E8C"), clips, captions, taps, END)


def video_lessons():
    clips = [
        hold(78, 2.6, 1.0, 1.0),                                  # 0.0  tap Learn @0.6
        hold(78, 1.6, 1.0, 1.4, CENTER, PENGUIN_PIN),             # 2.6  tap pin @3.4
        crossfade(lambda: zoomed(78, 1.4, *PENGUIN_PIN), lambda: screen_static(79), 0.6),  # 4.2
        hold(79, 2.6),                                            # 4.8
        hold(79, 3.4, 1.0, 1.9, CENTER, (585, 400)),              # 7.4 -> 10.8 zoom on SLP
        hold(79, 2.0, 1.9, 1.0, (585, 400), CENTER),              # 10.8 -> 12.8
    ]
    captions = [
        (0.0, 4.2, "Level up through guided learning paths", "Tap a lesson to start"),
        (4.6, 12.8, "SLP-Guided Video Lessons", "Learn from certified speech pathologists"),
    ]
    taps = [(0.7, *LEARN_TAB), (1.7, *PENGUIN_PIN)]
    render("02-slp-lessons", ("#D94FAD", "#9B2FAF"), clips, captions, taps, END)


def video_games():
    games = [
        (80, "Beary Hungry", "Feed the bear — say it right!"),
        (81, "Baby Talk", "Say it right — make it pass!"),
        (82, "Chicken Little", "Say it right — make it pass!"),
        (84, "Pilot Penguin", "Play with your chosen sounds."),
        (85, "Sentence", "Say a sentence with the chosen word."),
    ]
    clips, captions, t = [], [], 0.0
    card_c = (585, 1350)
    for i, (n, title, sub) in enumerate(games):
        if i:
            clips.append(swipe(games[i - 1][0], n, 0.5))
            t += 0.5
        clips.append(hold(n, 2.6))
        captions.append((t, t + 2.6 - 0.1, title, sub))
        t += 2.6
    clips.append(crossfade(lambda: screen_static(85), lambda: screen_static(86), 0.6))
    clips.append(hold(86, 3.0, 1.0, 1.1))
    captions.append((t + 0.3, t + 3.6, "Games They'll Actually Want to Play", None))
    taps = [(t - 1.2, *START_GAME)]
    render("03-practice-games", ("#E8973E", "#C0631E"), clips, captions, taps, END)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    _render = render
    for key, fn in [("tour", video_tour), ("lessons", video_lessons), ("games", video_games)]:
        if which in (key, "all"):
            # with speechtherapist.app end card (podcast / social / web)
            render = _render
            fn()
            # App Store-safe version without external pricing
            render = lambda *a, **k: _render(*a, **k, promo=False, subdir="app-store")
            fn()
