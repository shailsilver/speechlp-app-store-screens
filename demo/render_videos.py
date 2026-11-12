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
TAB_BAR = 2532                     # no tab bar any more: content runs to the bottom


# ---------------------------------------------------------------- helpers
def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def lerp(a, b, t):
    return a + (b - a) * t


# The app no longer has the Learn / Practice tab bar: kids stay on the learning path.
# Screenshots were taken with the old tab bar, so it is removed here.
CUT = 2085                         # everything below this (tab bar + icons) is removed
PATH_SCREENS = {78, 83}            # learning-path maps: crop to above the bar, fill screen
GAME_SCREENS = {80, 81, 82, 84}    # game cards: extend the sky down over the bar
PATH_K = SRC_H / CUT               # zoom factor for path screens
PATH_X0 = (SRC_W - SRC_W / PATH_K) / 2


def path_pt(x, y):
    """Map a point from the original path screenshot into the cleaned (cropped) version."""
    return ((x - PATH_X0) * PATH_K, y * PATH_K)


CUR = ROOT / "demo" / "assets" / "current"


def compose_report():
    """Post Game Report laid out as a phone screen (report table + SLP notes stacked)."""
    rep = Image.open(CUR / "post-game-report.png").convert("RGB")
    out = Image.new("RGB", (SRC_W, SRC_H), "white")
    left = rep.crop((0, 0, 1000, 1357))
    left = left.resize((SRC_W, round(1357 * SRC_W / 1000)), Image.LANCZOS)
    out.paste(left, (0, 60))
    y = 60 + left.height + 10
    for box in [(1055, 5, 1970, 195), (1055, 200, 1970, 510), (1090, 545, 1920, 595)]:
        c = rep.crop(box)
        w = SRC_W - 40
        c = c.resize((w, round(c.height * w / c.width)), Image.LANCZOS)
        out.paste(c, (20, y))
        y += c.height + 10
    return out


@lru_cache(maxsize=None)
def src(n):
    if n == "report":
        return compose_report()
    if isinstance(n, str):
        im = Image.open(CUR / f"{n}.png").convert("RGB")
        # fit to phone aspect: scale to width, crop/pad height
        h = round(im.height * SRC_W / im.width)
        im = im.resize((SRC_W, h), Image.LANCZOS)
        if h >= SRC_H:
            off = (h - SRC_H) // 2
            return im.crop((0, off, SRC_W, off + SRC_H))
        canvas = Image.new("RGB", (SRC_W, SRC_H), im.getpixel((5, h - 5)))
        canvas.paste(im, (0, (SRC_H - h) // 2))
        return canvas
    im = Image.open(ROOT / f"IMG_65{n}.png").convert("RGB")
    if n in PATH_SCREENS:
        orig = im
        im = im.crop((PATH_X0, 0, SRC_W - PATH_X0, CUT)).resize((SRC_W, SRC_H), Image.LANCZOS)
        # put the status bar + menu buttons back at their real size, feathered into the map
        band_h, fe = 250, 40
        mask = Image.new("L", (SRC_W, band_h), 255)
        mask.paste(Image.linear_gradient("L").rotate(180).resize((SRC_W, fe)), (0, band_h - fe))
        im.paste(orig.crop((0, 0, SRC_W, band_h)), (0, 0), mask)
    elif n in GAME_SCREENS:
        row = im.crop((0, CUT - 4, SRC_W, CUT - 2)).resize((1, 1), Image.BOX).getpixel((0, 0))
        fill = Image.new("RGB", (SRC_W, SRC_H - CUT))
        d = ImageDraw.Draw(fill)
        for y in range(fill.height):
            t = y / fill.height
            d.line([(0, y), (SRC_W, y)], fill=tuple(round(lerp(c, min(255, c + 18), t)) for c in row))
        im.paste(fill, (0, CUT))
        # soften the join
        band = im.crop((0, CUT - 40, SRC_W, CUT + 40)).filter(ImageFilter.GaussianBlur(10))
        im.paste(band.crop((0, 20, SRC_W, 60)), (0, CUT - 20))
    return im


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
        d.text((x, 420), ch, font=fe, fill=(255, 255, 255, 190))
        x += fe.getlength(ch) + sp
    size = 92
    while font(size).getlength("speechtherapist.app") > W - 100:
        size -= 2
    center("speechtherapist.app", font(size), 640 - 140)
    fp, fm = font(150), font(52)
    pw = fp.getlength("$20") + fm.getlength("/month")
    x = (W - pw) / 2
    d.text((x, 600), "$20", font=fp, fill="white")
    d.text((x + fp.getlength("$20") + 6, 678), "/month", font=fm, fill=(255, 255, 255, 210))
    # real SLP dashboard screenshot
    dash = Image.open(CUR / "slp-dashboard.png").convert("RGB")
    dw = W - 110
    dash = dash.resize((dw, round(dash.height * dw / dash.width)), Image.LANCZOS)
    m = Image.new("L", dash.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, dash.width - 1, dash.height - 1), radius=26, fill=255)
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).rounded_rectangle((55, 820, 55 + dw, 820 + dash.height + 20), radius=30, fill=120)
    card.paste((10, 10, 40), (0, 0), sh.filter(ImageFilter.GaussianBlur(24)))
    card.paste(dash, (55, 800), m)
    fl = font(50)
    items = ["Sign up today", "Add your students", "Invite caregivers to connect"]
    block = max(fl.getlength(it) for it in items) + 70
    x0 = (W - block) / 2
    y = 800 + round(612 * (W - 110) / 952) + 60
    for it in items:
        cx, cy, R, r = x0 + 24, y + 30, 26, 11
        pts = [(cx + (R if k % 2 == 0 else r) * math.sin(math.pi * k / 5),
                cy - (R if k % 2 == 0 else r) * math.cos(math.pi * k / 5)) for k in range(10)]
        d.polygon(pts, fill=(255, 213, 74))
        d.text((x0 + 70, y), it, font=fl, fill="white")
        y += 96
    return card


def draw_pulse(frame, sx, sy, t):
    """Listening rings radiating from the mic button (source coords)."""
    x, y = PHONE_X + sx * S, PHONE_Y + sy * S
    ov = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for k in range(3):
        q = ((t / 1.2) + k / 3) % 1
        r = 40 + 90 * q
        d.ellipse((x - r, y - r, x + r, y + r), outline=(255, 255, 255, int(200 * (1 - q))), width=5)
    frame.alpha_composite(ov)


def slide_up(base, sheet_name, dur, out=False):
    """A bottom sheet (e.g. 'Words in this game') slides up over a dimmed screen."""
    B = screen_static(base)
    sh = Image.open(CUR / f"{sheet_name}.png").convert("RGB")
    sh = sh.resize((SCR_W, round(sh.height * SCR_W / sh.width)), Image.LANCZOS)
    dark = Image.blend(B, Image.new("RGB", B.size, (0, 0, 0)), 0.45)

    def fn(t):
        k = ease(t / dur) if dur else 1
        if out:
            k = 1 - k
        img = Image.blend(B, dark, k)
        img.paste(sh, (0, SCR_H - round(sh.height * k)))
        return img
    return Clip(dur, fn)


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


def render(name, colors, clips, captions, taps, end_card=None, promo=True, subdir="", pulses=()):
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
            for (ps, pe, px, py) in pulses:
                if ps <= t <= pe:
                    draw_pulse(frame, px, py, t - ps)
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
# Current app: kids stay on the learning path (no Learn / Practice tabs).
# Tap targets are in 1170x2532 source coordinates.
K = SRC_W / 560                                  # report screenshots are 560 px wide
LEVEL_PLAY = (455 * K, 1125 * K)                 # "LEVEL 2 ▶" button on the path
LESSON_PIN = (313 * K, 595 * K)                  # lesson marker above level 2
MIC = (280 * K, 958 * K)                         # mic button on the say-the-word screen
START_GAME = (585, 1865)
CHOOSE_SOUNDS = {80: (585, 512), 84: (585, 597)}
CENTER = (SRC_W / 2, SRC_H / 2)

END = ("SpeechLP", "Learn from certified speech pathologists", 2.6)


def video_tour():
    P2, P17, WORD, REP = "path-level-2", "path-level-17", "game-say-the-word", "report"
    clips = [
        hold(P2, 3.0, 1.3, 1.0, (585, 1300), CENTER),                       # 0.0
        hold(P2, 1.0),                                                      # 3.0 tap Level ▶ @3.1
        crossfade(lambda: screen_static(P2), lambda: screen_static(WORD), 0.6),  # 4.0
        hold(WORD, 4.4, 1.0, 1.06, CENTER, (585, 1700)),                    # 4.6 mic pulse
        crossfade(lambda: zoomed(WORD, 1.06, 585, 1700), lambda: screen_static(REP), 0.6),  # 9.0
        hold(REP, 4.4, 1.0, 1.25, (585, 900), (585, 1500)),                 # 9.6
        crossfade(lambda: zoomed(REP, 1.25, 585, 1500), lambda: screen_static(P17), 0.6),  # 14.0
        hold(P17, 3.4, 1.0, 1.15, CENTER, (585, 1000)),                     # 14.6 -> 18.0
    ]
    captions = [
        (0.0, 3.9, "Level up through guided learning paths", None),
        (4.4, 8.9, "Say the word on the screen!", "Practice target sounds out loud"),
        (9.4, 13.9, "Track Their Progress", "A Post Game Report after each game"),
        (14.4, 18.0, "Keep climbing, level by level", None),
    ]
    taps = [(3.1, *LEVEL_PLAY)]
    pulses = [(5.0, 8.9, *MIC)]
    render("01-app-tour", ("#4A5FC1", "#2C3E8C"), clips, captions, taps, END, pulses=pulses)


def video_lessons():
    P2 = "path-level-2"
    clips = [
        hold(P2, 2.2, 1.0, 1.0),                                            # 0.0 tap pin @1.2
        hold(P2, 0.8, 1.0, 1.3, CENTER, LESSON_PIN),                        # 2.2
        crossfade(lambda: zoomed(P2, 1.3, *LESSON_PIN), lambda: screen_static(79), 0.6),  # 3.0
        hold(79, 2.4),                                                      # 3.6
        hold(79, 3.0, 1.0, 1.9, CENTER, (585, 400)),                        # 6.0 zoom on SLP
        hold(79, 1.0, 1.9, 1.0, (585, 400), CENTER),                        # 9.0
        slide_up(79, "words-in-this-game", 0.6),                            # 10.0
        Clip(3.4, slide_up(79, "words-in-this-game", 0).fn),                # 10.6 -> 14.0
    ]
    captions = [
        (0.0, 2.9, "Level up through guided learning paths", "Tap a lesson to start"),
        (3.4, 9.9, "SLP-Guided Video Lessons", "Learn from certified speech pathologists"),
        (10.2, 14.0, "Hear every word first", "Target sound highlighted"),
    ]
    taps = [(1.2, *LESSON_PIN)]
    render("02-slp-lessons", ("#D94FAD", "#9B2FAF"), clips, captions, taps, END)


def video_games():
    games = [
        (80, "Beary Hungry", "Feed the bear — say it right!"),
        (81, "Baby Talk", "Say it right — make it pass!"),
        (82, "Chicken Little", "Say it right — make it pass!"),
        (84, "Pilot Penguin", "Play with your chosen sounds."),
    ]
    WORD = "game-say-the-word"
    clips, captions, t = [], [], 0.0
    for i, (n, title, sub) in enumerate(games):
        if i:
            clips.append(swipe(games[i - 1][0], n, 0.5))
            t += 0.5
        clips.append(hold(n, 2.4))
        captions.append((t, t + 2.3, title, sub))
        t += 2.4
    # Pilot Penguin: choose sounds, start, play
    clips.append(hold(84, 2.0))                     # tap Choose sounds, then Start Game
    captions.append((t, t + 1.9, "Choose the sounds to practice", None))
    taps = [(t + 0.1, *CHOOSE_SOUNDS[84]), (t + 1.1, *START_GAME)]
    t += 2.0
    clips.append(crossfade(lambda: screen_static(84), lambda: screen_static(WORD), 0.6))
    clips.append(hold(WORD, 3.6, 1.0, 1.06, CENTER, (585, 1700)))
    captions.append((t + 0.3, t + 4.2, "Say the word on the screen!", None))
    pulses = [(t + 0.8, t + 4.2, *MIC)]
    t += 4.2
    clips.append(crossfade(lambda: zoomed(WORD, 1.06, 585, 1700), lambda: screen_static(86), 0.6))
    clips.append(hold(86, 2.8, 1.0, 1.1))
    captions.append((t + 0.3, t + 3.4, "Games They'll Actually Want to Play", None))
    render("03-practice-games", ("#E8973E", "#C0631E"), clips, captions, taps, END, pulses=pulses)


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
