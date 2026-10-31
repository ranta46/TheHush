"""GLOAMRUN engine — shared, CANONICAL drawing/rendering code for every Gloamrun short.
DO NOT change character geometry, colors or proportions here: they are the canon
(see CANON.md and the character bible page). Episodes import this module and only supply timelines.

Characters (canon, derived from the VR ride "Gloamrun · Line 01 · The Last Train"):
  ROOK      — brass clockwork crow, conductor of the last train. Royal-blue coat, white shirt, red tie,
              conductor cap (blue, red band, black brim, gold badge), steel beak, RIGHT eye = red signal lamp
              in a steel ring, LEFT eye = white with black pupil, gold wind-up key on his back that always turns.
              He talks (simple English captions, label "ROOK · CONDUCTOR").
  THE HUSH  — giant of the night. White bone mask, black slanted eye sockets with pale green pupils,
              a small third eye on the forehead, a black vertical slit mouth, one long finger always at its lips.
              Body and hood of black smoke with a green rim glow, small pale eyes inside the smoke.
              It never speaks. Where it passes, every light and every sound goes out. It cannot fly.

Episode module contract (see episodes/ep01.py):
  EP_NO:int, EP_TITLE:str, SYNOPSIS:str, DUR:float (story 18-35s + TITLE_LEN 3.5s end card)
  LINES: [(t0, t1, "simple English")]   Rook's spoken lines (the only words in the story)
  BG: "night" | "dawn"                    sky
  scroll(t)        -> world scroll in px (drives parallax + rails + wheels). 0 = stopped.
  dark_edge(t)     -> optional: screen x (2x canvas) left of which all town lights are OUT (the Hush passed). None = all lit.
  train_state(t)   -> dict for draw_train or None
  rook_state(t)    -> dict for draw_rook (build with rook(...))
  hush_state(t)    -> dict for draw_hush or None (build with hush(...))
  draw_scene(frame, t, ctx)  -> optional extras drawn after the train, before Rook
  draw_front(frame, t, ctx)  -> optional extras drawn last
  camera(t) -> (cx, cy, zoom) ; camera_v(t) optional framing for 9:16
  score(snd) -> soundtrack via gloamrun_sound
All on-screen text must be SIMPLE ENGLISH (check_english).
"""
import math, random, subprocess, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 2560, 1440
FPS = 24
RAIL = 1060                # rail top (train wheels sit here)
TITLE_LEN = 3.5
SIZES = {"h": (1280, 720), "v": (1080, 1920)}
FONT_BLACK = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
FONT_MED = "/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc"
FONT_SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Black.ttc"

# ---------------------------------------------------------------- palette (canon)
NIGHT_TOP, NIGHT_MID, NIGHT_LOW = (6, 7, 22), (20, 20, 58), (58, 40, 84)
DAWN_TOP, DAWN_MID, DAWN_LOW = (60, 70, 130), (190, 130, 150), (255, 196, 140)
INK = (14, 12, 20)
BRASS = (224, 167, 62); BRASS_D = (150, 104, 30)
COAT = (42, 82, 200); COAT_D = (24, 46, 120)
SHIRT = (246, 240, 228); TIE = (216, 55, 44); STEEL = (154, 162, 174); SIGNAL = (255, 58, 40)
BONE = (244, 239, 228); BONE_D = (196, 188, 176); SMOKE = (16, 13, 24); RIM = (77, 255, 173); PALE = (157, 255, 207)
TRAIN_RED = (122, 31, 26); IRON = (29, 26, 30); WINDOW = (255, 196, 110)
WHALE = (34, 56, 74); WHALE_SPOT = (127, 232, 255); WHALE_EYE = (255, 242, 192)

# ---------------------------------------------------------------- math helpers
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def lerp(a, b, t): return a + (b - a) * t
def ease(t): t = clamp(t); return t * t * (3 - 2 * t)
def ease_out(t): t = clamp(t); return 1 - (1 - t) ** 3
def ease_in(t): t = clamp(t); return t ** 3
def seg(t, a, b): return clamp((t - a) / (b - a))
def mix(c1, c2, t): return tuple(int(lerp(a, b, clamp(t))) for a, b in zip(c1, c2))

def keyframes(t, keys):
    """keys: [(t, v1, v2, ...)] eased interpolation -> tuple"""
    for k0, k1 in zip(keys, keys[1:]):
        if k0[0] <= t <= k1[0]:
            k = ease(seg(t, k0[0], k1[0]))
            return tuple(lerp(a, b, k) for a, b in zip(k0[1:], k1[1:]))
    return tuple(keys[-1][1:]) if t > keys[-1][0] else tuple(keys[0][1:])

def steps_at(t, keys):
    """keys [(t, value)] -> last value whose time <= t (for pose names etc.)"""
    v = keys[0][1]
    for k, val in keys:
        if t >= k: v = val
    return v

def blink_at(t, times, dur=0.14):
    for b in times:
        if b <= t < b + dur: return math.sin((t - b) / dur * math.pi)
    return 0.0

def auto_blinks(dur, seed=1):
    r = random.Random(seed); t = 1.2; out = []
    while t < dur: out.append(t); t += r.uniform(2.6, 4.0)
    return out

def paste(dst, src, x, y):
    x, y = int(round(x)), int(round(y)); sw, sh = src.size
    sx0, sy0 = max(0, -x), max(0, -y); dx0, dy0 = max(0, x), max(0, y)
    w = min(sw - sx0, dst.width - dx0); h = min(sh - sy0, dst.height - dy0)
    if w <= 0 or h <= 0: return
    dst.alpha_composite(src, (dx0, dy0), (sx0, sy0, sx0 + w, sy0 + h))

_glow_base = None; _glow_cache = {}
def glow(radius, color, alpha):
    global _glow_base
    if _glow_base is None:
        n = 256; yy, xx = np.mgrid[0:n, 0:n]
        d = np.sqrt((xx - n / 2 + .5) ** 2 + (yy - n / 2 + .5) ** 2) / (n / 2)
        _glow_base = np.clip(1 - d, 0, 1) ** 2.2
    r = max(4, int(radius // 4 * 4)); a = int(clamp(alpha) * 20) / 20; key = (r, color, a)
    if key not in _glow_cache:
        s = r * 2
        m = Image.fromarray((_glow_base * 255 * a).astype(np.uint8)).resize((s, s), Image.BILINEAR)
        im = Image.new("RGBA", (s, s), color + (0,)); im.putalpha(m)
        if len(_glow_cache) > 500: _glow_cache.clear()
        _glow_cache[key] = im
    return _glow_cache[key]

def add_glow(dst, x, y, radius, color, alpha):
    if alpha <= 0.01 or radius < 4: return
    g = glow(radius, color, alpha); paste(dst, g, x - g.width / 2, y - g.height / 2)

def rot(px, py, cx, cy, a):
    c, s = math.cos(a), math.sin(a); dx, dy = px - cx, py - cy
    return cx + dx * c - dy * s, cy + dx * s + dy * c

# ---------------------------------------------------------------- world: sky + parallax layers
def build_sky(kind="night", seed=7):
    yy = np.linspace(0, 1, H)[:, None]
    if kind == "dawn": top, mid, low = map(np.array, (DAWN_TOP, DAWN_MID, DAWN_LOW))
    else: top, mid, low = map(np.array, (NIGHT_TOP, NIGHT_MID, NIGHT_LOW))
    t1 = np.clip(yy / 0.55, 0, 1); t2 = np.clip((yy - 0.55) / 0.25, 0, 1)
    col = top + (mid - top) * t1 + (low - mid) * t2
    sky = Image.fromarray(np.repeat(col[:, None, :], W, axis=1).astype(np.uint8), "RGB").convert("RGBA")
    if kind == "night":
        # the moon is always low and big: it backlights the Hush
        add_glow(sky, 1280, 470, 760, (150, 160, 255), 0.30)
        d = ImageDraw.Draw(sky); d.ellipse((1080, 270, 1480, 670), fill=(236, 232, 214, 255))
        for cx, cy, r in ((1180, 390, 40), (1360, 520, 55), (1250, 560, 25)):
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(214, 208, 190, 255))
    else:
        add_glow(sky, 1700, 1000, 900, (255, 210, 150), 0.55)
    return sky

def base_stars(seed=11, n=260):
    r = random.Random(seed)
    return [dict(x=r.uniform(0, W), y=r.uniform(0, 820), s=r.uniform(1.8, 4.2), ph=r.uniform(0, 6.28), sp=r.uniform(1, 3)) for _ in range(n)]

def draw_stars(img, t, stars, alpha=1.0):
    if alpha <= 0.02: return
    d = ImageDraw.Draw(img)
    for s in stars:
        b = 0.55 + 0.45 * math.sin(t * s["sp"] + s["ph"]); rr = s["s"] * (0.7 + 0.3 * b)
        d.ellipse((s["x"] - rr, s["y"] - rr, s["x"] + rr, s["y"] + rr), fill=(220, 225, 255, int(255 * alpha * (0.35 + 0.6 * b))))

STRIP = W * 2
def _strip(): return Image.new("RGBA", (STRIP, H), (0, 0, 0, 0))

def build_far(seed=5, kind="night"):
    """rock spires of Gloamrun and the Needle — very far, moves slowly"""
    im = _strip(); d = ImageDraw.Draw(im); r = random.Random(seed)
    col = (26, 22, 52, 255) if kind == "night" else (120, 86, 120, 255)
    x = 0
    while x < STRIP:
        w = r.randint(60, 160); h = r.randint(260, 620); top = RAIL - 120 - h
        d.polygon([(x, RAIL), (x + w * 0.3, top + 40), (x + w * 0.5, top), (x + w * 0.7, top + 50), (x + w, RAIL)], fill=col)
        x += w + r.randint(40, 220)
    # the Needle (a landmark: thin spire with a red light on top)
    nx = 1500; d.polygon([(nx - 70, RAIL), (nx - 10, 140), (nx + 10, 140), (nx + 70, RAIL)], fill=col)
    return im

def build_town(lit=True, seed=9, kind="night"):
    """Kesmoor: steep roofs, chimneys, warm windows. Two versions (lit / dark) — the Hush puts lights out."""
    im = _strip(); d = ImageDraw.Draw(im); r = random.Random(seed)
    base = (34, 26, 50, 255) if kind == "night" else (90, 62, 86, 255)
    x = -30
    while x < STRIP:
        w = r.randint(150, 280); h = r.randint(140, 340); top = RAIL - 40 - h; peak = top - r.randint(70, 150)
        d.rectangle((x, top, x + w, RAIL), fill=base)
        d.polygon([(x - 12, top + 4), (x + w / 2, peak), (x + w + 12, top + 4)], fill=base)
        if r.random() < 0.6:
            cx = x + r.randint(20, w - 50); d.rectangle((cx, peak + 40, cx + 26, top), fill=base)
        for wy in range(top + 30, RAIL - 60, 70):
            for wx in range(x + 26, x + w - 40, 64):
                if r.random() < 0.45:
                    c = (255, 196, 110, 255) if lit else (20, 16, 30, 255)
                    d.rectangle((wx, wy, wx + 24, wy + 34), fill=c)
        x += w + r.randint(0, 30)
    if lit:
        g = im.filter(ImageFilter.GaussianBlur(10)); g = Image.blend(Image.new("RGBA", im.size, (0, 0, 0, 0)), g, 0.9)
        im = Image.alpha_composite(g, im)
    return im

def build_trestle(kind="night"):
    """the rail line: track + ties + trestle legs; tile width 160"""
    im = _strip(); d = ImageDraw.Draw(im)
    wood = (40, 30, 34, 255) if kind == "night" else (80, 56, 52, 255)
    for x in range(0, STRIP, 320):
        d.polygon([(x, RAIL + 30), (x + 40, RAIL + 30), (x + 140, H), (x + 100, H)], fill=wood)
        d.polygon([(x + 280, RAIL + 30), (x + 320, RAIL + 30), (x + 220, H), (x + 180, H)], fill=wood)
        d.line((x + 20, RAIL + 160, x + 300, RAIL + 160), fill=wood, width=12)
    for x in range(0, STRIP, 40): d.rectangle((x, RAIL + 8, x + 22, RAIL + 30), fill=(54, 42, 44, 255))
    d.rectangle((0, RAIL - 2, STRIP, RAIL + 10), fill=(120, 120, 132, 255))
    return im

def scroll_paste(dst, strip, offset):
    o = int(offset) % STRIP
    paste(dst, strip, -o, 0)
    if o > STRIP - W: paste(dst, strip, STRIP - o, 0)

# ---------------------------------------------------------------- the train (canon colors)
TRAIN_DEFAULT = dict(x=1500, y=RAIL, cars=2, lamp=1.0, smoke=1.0, dark=0.0)
def train(**kw): st = dict(TRAIN_DEFAULT); st.update(kw); return st

def draw_car(d, x, y, wheel_a):
    d.rectangle((x - 230, y - 150, x + 230, y - 40), fill=TRAIN_RED + (255,), outline=INK + (255,), width=6)
    d.rectangle((x - 236, y - 160, x + 236, y - 146), fill=BRASS + (255,))
    d.rectangle((x - 240, y - 46, x + 240, y - 26), fill=IRON + (255,))
    for wx in (x - 150, x + 150): _wheel(d, wx, y - 34, 34, wheel_a)

def _wheel(d, cx, cy, r, a):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=IRON + (255,), outline=(70, 64, 70, 255), width=5)
    for k in range(3):
        aa = a + k * math.pi / 3
        d.line((cx - r * .8 * math.cos(aa), cy - r * .8 * math.sin(aa), cx + r * .8 * math.cos(aa), cy + r * .8 * math.sin(aa)), fill=(70, 64, 70, 255), width=4)

def draw_train(frame, t, st, scroll=0.0):
    """side view, facing RIGHT. x = front of the locomotive. Cars trail to the left."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    x, y = st["x"], st["y"]; wa = scroll / 34.0
    # locomotive
    d.rectangle((x - 560, y - 300, x - 330, y - 40), fill=TRAIN_RED + (255,), outline=INK + (255,), width=6)       # cab
    d.rectangle((x - 590, y - 320, x - 300, y - 296), fill=IRON + (255,))
    d.rectangle((x - 520, y - 260, x - 380, y - 180), fill=WINDOW + (255,))
    d.rounded_rectangle((x - 340, y - 230, x - 20, y - 60), radius=80, fill=TRAIN_RED + (255,), outline=INK + (255,), width=6)  # boiler
    for bx in (x - 280, x - 180, x - 80): d.rectangle((bx, y - 232, bx + 14, y - 58), fill=BRASS + (255,))
    d.rectangle((x - 120, y - 330, x - 70, y - 230), fill=IRON + (255,)); d.rectangle((x - 132, y - 344, x - 58, y - 326), fill=IRON + (255,))
    d.rectangle((x - 600, y - 46, x + 10, y - 26), fill=IRON + (255,))
    d.polygon([(x - 10, y - 60), (x + 50, y - 26), (x - 10, y - 26)], fill=IRON + (255,))  # cow-catcher
    for wx, r in ((x - 470, 54), (x - 300, 54), (x - 120, 40)): _wheel(d, wx, y - r + 6, r, wa)
    d.ellipse((x - 34, y - 170, x + 4, y - 130), fill=(255, 242, 208, 255))
    for i in range(st.get("cars", 2)):
        draw_car(d, x - 860 - i * 500, y, wa + i)
    if st.get("dark", 0) > 0:
        a = lay.getchannel("A"); dk = Image.new("RGBA", (W, H), (4, 3, 8, 255)); dk.putalpha(a.point(lambda q: int(q * st["dark"] * 0.8)))
        lay.alpha_composite(dk)
    paste(frame, lay, 0, 0)
    lamp = st.get("lamp", 1.0)
    if lamp > 0.02:
        beam = Image.new("RGBA", (900, 400), (0, 0, 0, 0)); bd = ImageDraw.Draw(beam)
        bd.polygon([(0, 200), (900, 40), (900, 360)], fill=(255, 236, 190, int(60 * lamp)))
        paste(frame, beam.filter(ImageFilter.GaussianBlur(18)), x - 10, y - 350)
        add_glow(frame, x - 15, y - 150, 120, (255, 236, 190), 0.8 * lamp)
        add_glow(frame, x - 450, y - 220, 160, WINDOW, 0.45 * lamp)
    sm = st.get("smoke", 1.0)
    if sm > 0.02:
        for k in range(7):
            ph = (t * 1.3 + k / 7) % 1.0
            sx = x - 95 - ph * (420 + scroll * 0.0) - ph * 160; sy = y - 350 - ph * 220
            add_glow(frame, sx, sy, 50 + ph * 150, (120, 110, 130), 0.35 * sm * (1 - ph))
    add_glow(frame, x - 95, y - 350, 70, (255, 122, 58), 0.7)

def car_seat(st, i=0):
    """where Rook stands on top of car i (0 = first car behind the loco)"""
    return st["x"] - 860 - i * 500, st["y"] - 160

def loco_roof(st):
    return st["x"] - 445, st["y"] - 320

# ---------------------------------------------------------------- ROOK (canon — do not modify)
ROOK_DEFAULT = dict(sc=1.0, x=1280, y=RAIL - 160, face=1, pose="idle", look=0.0, tilt=0.0, lean=0.0,
                    eye=1.0, blink=0.0, beak=0.0, flap=0.0, fly=0.0)
POSES = {"idle": (0, 0), "wave": (0.2, 2.4), "point": (0.3, 1.5), "ahead": (0, 0), "sad": (-0.2, -0.2),
         "lean": (-0.5, 0.6), "pull": (0.9, 0.9), "flinch": (2.0, 2.0), "spread": (1.5, 1.5),
         "celebrate": (1.7, 1.7), "down": (0, 0), "shh": (0.2, 2.6)}
# pose -> (left wing raise, right wing raise) in radians. "shh": right wingtip to the beak.

def rook(**kw):
    st = dict(ROOK_DEFAULT); st.update(kw); return st

def draw_rook(frame, t, st):
    """Rook, the conductor. x,y = feet. face = 1 (looks right) / -1 (looks left). 1.0 sc = 300 px tall."""
    sc = st["sc"]; S = int(700 * max(1.0, sc)); lay = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    ax, ay = S / 2, S - 70 * max(1.0, sc)
    P = lambda x, y: (ax + x * sc, ay + y * sc)
    pose = st["pose"]; lw0, rw0 = POSES.get(pose, (0, 0))
    flap = math.sin(t * 16) * 0.45 * st.get("flap", 0)
    ink = INK + (255,); w = max(2, int(5 * sc))
    # wind-up key (always turning) sticks out of his back: seen behind the body, opposite the face
    spin = t * 2.2; kw = abs(math.cos(spin)); kx = -st["face"] * 86
    x_a, x_b = sorted((P(kx * 0.6, 0)[0], P(kx, 0)[0])); d.rectangle((x_a, P(0, -138)[1], x_b, P(0, -126)[1]), fill=BRASS + (255,), outline=ink)
    for sd in (-1, 1):
        cx, cy = P(kx + (-st["face"]) * 20, -132 + sd * 24 * max(.45, kw)); r = 24 * sc
        d.ellipse((cx - r * .8, cy - r * max(.45, kw), cx + r * .8, cy + r * max(.45, kw)), outline=BRASS + (255,), width=max(3, int(10 * sc)))
    # tail: three short gold feathers peeking out behind, low
    for k in (-1, 0, 1):
        d.polygon([P(-10 + k * 14, -70), P(-26 + k * 30, -22), P(-8 + k * 30, -22), P(10 + k * 14, -70)], fill=BRASS_D + (255,), outline=ink)
    # legs
    for sd in (-1, 1):
        d.line((*P(sd * 22, -50), *P(sd * 22, 0)), fill=BRASS + (255,), width=max(3, int(9 * sc)))
        d.line((*P(sd * 22, 0), *P(sd * 22 + 22 * st["face"], 4)), fill=BRASS + (255,), width=max(3, int(8 * sc)))
    # body: blue coat egg, white shirt front, red tie, six gold buttons
    d.ellipse((*P(-72, -200), *P(72, -40)), fill=COAT + (255,), outline=ink, width=w)
    d.ellipse((*P(-34, -190), *P(34, -70)), fill=SHIRT + (255,), outline=ink, width=max(2, int(3 * sc)))
    d.polygon([P(-10, -186), P(10, -186), P(0, -132)], fill=TIE + (255,), outline=ink)
    for by in (-170, -142, -114):
        for bx in (-50, 50): d.ellipse((*P(bx - 6, by - 6), *P(bx + 6, by + 6)), fill=BRASS + (255,))
    def wing(sd, a):
        """coat-blue sleeve wing with a gold feather tip (canon)"""
        sx, sy = P(sd * 58, -166); phi = 0.12 + a; ln = 128 * sc
        ux, uy = sd * math.sin(phi), math.cos(phi); nx, ny = -uy * sd, ux * sd
        prof = [(0, 13), (0.25, 26), (0.55, 28), (0.8, 20), (1.0, 0)]
        side1 = [(sx + ux * ln * f + nx * w_ * sc, sy + uy * ln * f + ny * w_ * sc) for f, w_ in prof]
        side2 = [(sx + ux * ln * f - nx * w_ * sc * 0.55, sy + uy * ln * f - ny * w_ * sc * 0.55) for f, w_ in prof]
        poly = side1 + side2[::-1]
        d.polygon(poly, fill=COAT + (255,), outline=ink)
        g1 = [(sx + ux * ln * f + nx * w_ * sc, sy + uy * ln * f + ny * w_ * sc) for f, w_ in prof[2:]]
        g2 = [(sx + ux * ln * f - nx * w_ * sc * 0.55, sy + uy * ln * f - ny * w_ * sc * 0.55) for f, w_ in prof[2:]]
        d.polygon(g1 + g2[::-1], fill=BRASS + (255,), outline=ink)
        mx, my = sx + ux * ln * 0.55, sy + uy * ln * 0.55
        d.line((mx + nx * 28 * sc, my + ny * 28 * sc, mx - nx * 15 * sc, my - ny * 15 * sc), fill=ink, width=max(2, int(4 * sc)))
    for sd, base in ((-1, lw0), (1, rw0)):
        if pose == "shh" and sd > 0: continue          # right wing is drawn at the beak below
        wing(sd, max(-0.15, base + flap))
    # head (gold), turned by look (-1..1) + face
    look = clamp(st.get("look", 0) + 0.35 * st["face"], -1, 1)
    hx, hy = 0, -262; hr = 62
    head = Image.new("RGBA", (S, S), (0, 0, 0, 0)); h = ImageDraw.Draw(head)
    H_ = lambda x, y: (ax + (hx + x) * sc, ay + (hy + y) * sc)
    h.ellipse((*H_(-hr, -hr), *H_(hr, hr)), fill=BRASS + (255,), outline=ink, width=w)
    h.ellipse((*H_(-hr + 10, -hr + 8), *H_(-10, -10)), fill=(245, 200, 110, 255))
    ex = look * 26
    # LEFT eye: white with black pupil (viewer's left), RIGHT eye: red signal lamp in steel ring
    lx_, rx_ = ex - 24, ex + 24
    bl = st.get("blink", 0)
    eh = 15 * (1 - bl) + 2
    h.ellipse((*H_(lx_ - 15, -12 - eh), *H_(lx_ + 15, -12 + eh)), fill=SHIRT + (255,), outline=ink, width=max(2, int(3 * sc)))
    if bl < 0.5: h.ellipse((*H_(lx_ - 6 + look * 4, -18), *H_(lx_ + 6 + look * 4, -6)), fill=(17, 17, 17, 255))
    e = st.get("eye", 1.0)
    h.ellipse((*H_(rx_ - 19, -31), *H_(rx_ + 19, 7)), fill=STEEL + (255,), outline=ink, width=max(2, int(3 * sc)))
    h.ellipse((*H_(rx_ - 12, -24), *H_(rx_ + 12, 0)), fill=mix((90, 20, 16), SIGNAL, clamp(e)) + (255,))
    # beak (dark steel crow beak), points the way he looks; opens when he talks
    bo = clamp(st.get("beak", 0)) * 16; bx = ex * 1.1; dirx = 1 if look >= 0 else -1
    tip = H_(bx + dirx * (36 + 74 * abs(look)), 22 + 30 * (1 - abs(look)))
    up = [H_(bx - 22, -4 - bo * .4), H_(bx + 22, -4 - bo * .4), tip]
    if bo > 1: h.polygon([H_(bx - 18, 12), H_(bx + 18, 12), (tip[0] - dirx * 8 * sc, tip[1] + bo * sc)], fill=(70, 74, 84, 255), outline=ink)
    h.polygon(up, fill=(118, 126, 140, 255), outline=ink)
    h.line([H_(bx - 6, -2 - bo * .4), (tip[0] - (tip[0] - H_(bx, 0)[0]) * 0.25, tip[1] - (tip[1] - H_(0, 0)[1]) * 0.25)], fill=(200, 206, 216, 255), width=max(2, int(4 * sc)))
    # conductor cap: blue, red band, black brim, gold badge
    h.polygon([H_(-60, -48), H_(60, -48), H_(66, -96), H_(-66, -96)], fill=COAT + (255,), outline=ink)
    h.rectangle((*H_(-62, -66), *H_(62, -50)), fill=TIE + (255,))
    h.polygon([H_(-60 + ex * .5, -48), H_(70 + ex * 1.2, -42), H_(64 + ex * 1.2, -32), H_(-56 + ex * .5, -40)], fill=(17, 17, 17, 255))
    h.ellipse((*H_(-10 + ex * .4, -90), *H_(10 + ex * .4, -70)), fill=BRASS + (255,), outline=ink)
    tilt = st.get("tilt", 0)
    if pose == "down": tilt += 0.25
    if pose == "sad": tilt += 0.15
    if abs(tilt) > 0.01: head = head.rotate(-math.degrees(tilt), resample=Image.BICUBIC, center=H_(0, 0))
    lay.alpha_composite(head)
    if pose == "shh":   # right wingtip held up to the beak (copying the Hush, as a joke or a warning)
        d2 = ImageDraw.Draw(lay); sx, sy = P(60, -168); tx, ty = H_(bx + 4, 4)
        nx, ny = -(ty - sy), (tx - sx); L = math.hypot(nx, ny) or 1; nx, ny = nx / L * 20 * sc, ny / L * 20 * sc
        d2.polygon([(sx + nx, sy + ny), (sx - nx, sy - ny), (tx - nx * .3, ty - ny * .3), (tx, ty)], fill=COAT + (255,), outline=ink)
        for k in range(3):
            fx_, fy_ = lerp(sx, tx, 0.7 + k * 0.1), lerp(sy, ty, 0.7 + k * 0.1)
            d2.polygon([(fx_ + nx * .6, fy_ + ny * .6), (fx_ + nx * 1.6, fy_ + ny * 1.6 - 10 * sc), (fx_, fy_ - 4 * sc)], fill=BRASS + (255,), outline=ink)
    lean = st.get("lean", 0) + (0.12 if pose == "pull" else 0) + (-0.1 if pose == "flinch" else 0)
    if abs(lean) > 0.005: lay = lay.rotate(-math.degrees(lean) * st["face"], resample=Image.BICUBIC, center=(ax, ay))
    if st["face"] < 0: lay = lay.transpose(Image.FLIP_LEFT_RIGHT)
    X, Y = st["x"], st["y"] - st.get("fly", 0)
    if pose in ("celebrate", "wave") or st.get("flap", 0) > 0.1: Y -= abs(math.sin(t * 8)) * 8 * st.get("flap", 0.5)
    paste(frame, lay, X - ax, Y - ay)
    # signal-lamp glow (brighter in danger / in the dark)
    gx = X + (rx_ * sc if st["face"] > 0 else -rx_ * sc); gy = Y + (hy - 12) * sc
    add_glow(frame, gx, gy, (50 + 90 * e) * sc, (255, 70, 40), 0.25 + 0.45 * clamp(e / 1.6))

# ---------------------------------------------------------------- THE HUSH (canon — do not modify)
HUSH_DEFAULT = dict(sc=1.0, x=900, y=520, hand="shh", eye=1.0, near=0.0, sink=0.0, lean=0.0, point_dir=1)
HANDS = ("shh", "point", "none")
def hush(**kw): st = dict(HUSH_DEFAULT); st.update(kw); return st

def _rim(lay, poly, color, width, blur):
    r = Image.new("RGBA", lay.size, (0, 0, 0, 0)); ImageDraw.Draw(r).line(poly + [poly[0]], fill=color + (255,), width=width, joint="curve")
    return r.filter(ImageFilter.GaussianBlur(blur))

def draw_hush(frame, t, st):
    """The Hush. (x,y) = center of the mask. sc 1.0 = mask 300 px tall; the robe falls far below the frame."""
    Q = 0.5   # drawn at half resolution then scaled up (soft smoke, much faster)
    sc = st["sc"] * Q; x0, y0 = st["x"], st["y"] + st.get("sink", 0)
    S = int(2200 * sc) + 4; lay = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    ax, ay = S / 2, S * 0.28
    P = lambda x, y: (ax + x * sc, ay + y * sc)
    wob = lambda k, a: math.sin(t * 2.1 + k * 1.7) * a
    near = st.get("near", 0)
    # robe: tall smoke cone with ragged edges
    robe = []
    for i in range(24):
        f = i / 23; yy = 120 + f * 1500; ww = 220 + f * 520
        robe.append(P(-ww + wob(i, 18), yy))
    for i in range(23, -1, -1):
        f = i / 23; yy = 120 + f * 1500; ww = 220 + f * 520
        robe.append(P(ww + wob(i + 9, 18), yy))
    shoulders = [P(-330 + wob(1, 8), 200), P(-300, 120), P(-200, 60), P(0, 40), P(200, 60), P(300, 120), P(330 + wob(2, 8), 200)]
    hood = [P(a, b) for a, b in [(-170, 120), (-200, 0), (-180, -150), (-110, -250), (0, -285), (110, -250), (180, -150), (200, 0), (170, 120)]]
    add_glow(lay, ax, ay - 20 * sc, 700 * sc, (60, 200, 140), 0.18 + 0.2 * near)                 # halo
    d.polygon(robe, fill=SMOKE + (255,)); d.polygon(shoulders + [P(330, 260), P(-330, 260)], fill=SMOKE + (255,)); d.polygon(hood, fill=SMOKE + (255,))
    rimw = max(3, int(10 * sc)); f = 0.75 + 0.25 * math.sin(t * 3)
    rl = Image.new("RGBA", lay.size, (0, 0, 0, 0)); rd_ = ImageDraw.Draw(rl); rc = mix(SMOKE, RIM, 0.75 * f + 0.25 * near) + (255,)
    for poly in (robe, hood, shoulders): rd_.line(poly + [poly[0]], fill=rc, width=rimw, joint="curve")
    lay.alpha_composite(rl.filter(ImageFilter.GaussianBlur(6 * sc)))
    d = ImageDraw.Draw(lay)
    d.polygon(robe, fill=SMOKE + (230,)); d.polygon(hood, fill=SMOKE + (235,))
    # small pale eyes inside the smoke (they blink slowly)
    r = random.Random(5)
    for k in range(34):
        ex, ey = r.uniform(-1, 1), r.uniform(260, 1300); wdt = 220 + (ey - 120) / 1500 * 520
        ex *= wdt * 0.8; op = 0.5 + 0.5 * math.sin(t * r.uniform(0.6, 1.4) + k)
        if op > 0.25:
            for s_ in (-1, 1):
                cx, cy = P(ex + s_ * 12, ey); rr = 5 * sc
                d.ellipse((cx - rr, cy - rr * .7, cx + rr, cy + rr * .7), fill=PALE + (int(220 * op),))
    # mask: white bone oval
    d.ellipse((*P(-140, -190), *P(140, 190)), fill=BONE + (255,), outline=(120, 112, 104, 255), width=max(2, int(4 * sc)))
    d.ellipse((*P(-120, -175), *P(40, 60)), fill=(252, 249, 242, 255))
    d.ellipse((*P(-140, -190), *P(140, 190)), outline=(120, 112, 104, 255), width=max(2, int(4 * sc)))
    # eye sockets (black, slanted) + pale green pupils + third eye
    eg = st.get("eye", 1.0)
    for sd in (-1, 1):
        cx, cy = P(sd * 56, -40)
        pts = []
        for i in range(20):
            a = i / 20 * math.tau; px, py = math.cos(a) * 44 * sc, math.sin(a) * 22 * sc
            pts.append(rot(cx + px, cy + py, cx, cy, sd * 0.28))
        d.polygon(pts, fill=(0, 0, 0, 255))
        d.ellipse((cx - 10 * sc, cy - 10 * sc, cx + 10 * sc, cy + 10 * sc), fill=PALE + (255,))
    tx, ty = P(0, -118); d.ellipse((tx - 7 * sc, ty - 7 * sc, tx + 7 * sc, ty + 7 * sc), fill=PALE + (255,))
    d.polygon([P(-5, 60), P(5, 60), P(4, 150), P(-4, 150)], fill=(0, 0, 0, 255))     # slit mouth
    # the hand: one long finger always at its lips ("shh"), or pointing
    hand = st.get("hand", "shh")
    if hand == "shh":
        d.ellipse((*P(-60, 170), *P(70, 260)), fill=BONE + (255,), outline=BONE_D + (255,), width=max(2, int(3 * sc)))
        d.rounded_rectangle((*P(-16, 20), *P(14, 200)), radius=14 * sc, fill=BONE + (255,), outline=BONE_D + (255,), width=max(2, int(3 * sc)))
        d.ellipse((*P(-18, 110), *P(16, 140)), fill=BONE + (255,))
        d.ellipse((*P(-10, 18), *P(8, 46)), fill=(42, 34, 40, 255))
    elif hand == "point":
        pd = st.get("point_dir", 1)
        d.ellipse((*P(-70 + 120 * pd, 200), *P(70 + 120 * pd, 290)), fill=BONE + (255,), outline=BONE_D + (255,), width=max(2, int(3 * sc)))
        bx0 = 120 * pd + 60 * pd; tipx = 120 * pd + 360 * pd
        d.polygon([P(bx0, 222), P(tipx, 234), P(tipx, 250), P(bx0, 266)], fill=BONE + (255,), outline=BONE_D + (255,))
        kx = (bx0 + tipx) / 2; d.ellipse((*P(kx - 22, 222), *P(kx + 22, 266)), fill=BONE + (255,), outline=BONE_D + (255,))
        tx_, ty_ = P(tipx, 242); d.ellipse((tx_ - 12 * sc, ty_ - 9 * sc, tx_ + 12 * sc, ty_ + 9 * sc), fill=(42, 34, 40, 255))
        for k in range(3):   # the other fingers stay curled
            cx_, cy_ = P(120 * pd + (20 + k * 26) * pd, 290); d.ellipse((cx_ - 16 * sc, cy_ - 14 * sc, cx_ + 16 * sc, cy_ + 14 * sc), fill=BONE + (255,), outline=BONE_D + (255,))
    lean = st.get("lean", 0)
    if abs(lean) > 0.1: lay = lay.rotate(-math.degrees(lean), resample=Image.BILINEAR, center=(ax, ay + 600 * sc))
    else: x0 += lean * 220 * st["sc"]
    lay = lay.resize((int(S / Q), int(S / Q)), Image.BILINEAR); ax, ay = ax / Q, ay / Q; sc = st["sc"]
    paste(frame, lay, x0 - ax, y0 - ay)
    for sd in (-1, 1):   # pupil glow
        cx, cy = x0 + sd * 56 * sc, y0 - 40 * sc
        add_glow(frame, cx, cy, 70 * sc * (0.6 + 0.6 * eg), (120, 255, 190), 0.55 * clamp(eg))

def hush_arm(frame, t, a, b, sc=1.0):
    """long bone arm from a (shoulder) to b (claw), drawn over everything near it"""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    mx, my = (a[0] + b[0]) / 2, min(a[1], b[1]) - 180 * sc
    pts = [(lerp(lerp(a[0], mx, k), lerp(mx, b[0], k), k), lerp(lerp(a[1], my, k), lerp(my, b[1], k), k)) for k in [i / 30 for i in range(31)]]
    d.line(pts, fill=BONE + (255,), width=int(46 * sc), joint="curve")
    for u in (0.42, 0.66):
        px, py = pts[int(u * 30)]; d.ellipse((px - 30 * sc, py - 30 * sc, px + 30 * sc, py + 30 * sc), fill=BONE + (255,))
    for f in range(4):
        ang = math.pi / 2 + (f - 1.5) * 0.45
        d.line((b[0], b[1], b[0] + math.cos(ang) * 90 * sc, b[1] + math.sin(ang) * 90 * sc), fill=BONE + (255,), width=int(18 * sc))
        d.ellipse((b[0] + math.cos(ang) * 90 * sc - 9 * sc, b[1] + math.sin(ang) * 90 * sc - 9 * sc,
                   b[0] + math.cos(ang) * 90 * sc + 9 * sc, b[1] + math.sin(ang) * 90 * sc + 9 * sc), fill=(42, 34, 40, 255))
    d.ellipse((b[0] - 50 * sc, b[1] - 34 * sc, b[0] + 50 * sc, b[1] + 34 * sc), fill=BONE + (255,))
    paste(frame, lay, 0, 0)

# ---------------------------------------------------------------- THE LONG BACK (canon)
def draw_longback(frame, t, x, y, sc=1.0):
    """the sky whale, old friend of Rook. (x,y) = center of the back"""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    fin = math.sin(t * 0.9) * 0.2
    for sd in (-1, 1):
        d.polygon([(x + sd * 300 * sc, y + 40 * sc), (x + sd * 1100 * sc, y + (60 + 160 * fin * sd) * sc), (x + sd * 400 * sc, y + 140 * sc)], fill=WHALE + (255,))
    tl = math.sin(t * 0.9 + 1) * 60 * sc
    d.polygon([(x - 1400 * sc, y + 150 * sc), (x - 1850 * sc, y - 60 * sc + tl), (x - 1720 * sc, y + 150 * sc), (x - 1850 * sc, y + 360 * sc - tl)], fill=WHALE + (255,))
    d.ellipse((x - 1500 * sc, y - 120 * sc, x + 900 * sc, y + 420 * sc), fill=WHALE + (255,))
    d.ellipse((x - 1300 * sc, y + 120 * sc, x + 760 * sc, y + 420 * sc), fill=(106, 127, 140, 255))
    for k in range(14):
        sx = x - 1250 * sc + k * 150 * sc; sy = y - 80 * sc + abs(k - 7) ** 1.6 * 4 * sc
        d.ellipse((sx - 14 * sc, sy - 10 * sc, sx + 14 * sc, sy + 10 * sc), fill=WHALE_SPOT + (255,))
    d.ellipse((x + 640 * sc, y + 60 * sc, x + 700 * sc, y + 110 * sc), fill=WHALE_EYE + (255,))
    paste(frame, lay, 0, 0)
    for k in range(0, 14, 2):
        add_glow(frame, x - 1250 * sc + k * 150 * sc, y - 80 * sc, 50 * sc, WHALE_SPOT, 0.4)

# ---------------------------------------------------------------- text
def font(p, size): return ImageFont.truetype(p, size, index=0)
ALLOWED_PUNCT = set("’‘“”…—–·©")
def check_english(txt):
    """Canon rule (森さん, 2026-09-28): every on-screen word is simple English. No Japanese or other scripts."""
    bad = [c for c in str(txt) if ord(c) > 0x7E and c not in ALLOWED_PUNCT]
    if bad: raise ValueError(f"on-screen text must be simple English (ASCII). Found {''.join(bad)!r} in {txt!r}")
    return txt

def text_center(img, y, txt, f, color, alpha, spacing=0):
    check_english(txt)
    if alpha <= 0.01: return
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if spacing:
        widths = [d.textlength(ch, font=f) for ch in txt]; x = (img.width - (sum(widths) + spacing * (len(txt) - 1))) / 2
        for ch, w_ in zip(txt, widths): d.text((x, y), ch, font=f, fill=color + (int(255 * alpha),)); x += w_ + spacing
    else:
        w_ = d.textlength(txt, font=f); d.text(((img.width - w_) / 2, y), txt, font=f, fill=color + (int(255 * alpha),))
    img.alpha_composite(lay)

def draw_line(img, t, lines, orient):
    """Rook's spoken line: small brass label + white text on a soft dark band (like the ride's radio caption)."""
    ow, oh = img.size; v = orient == "v"
    for t0, t1, txt in lines:
        if t0 <= t < t1:
            a = ease(seg(t, t0, t0 + 0.15)) * (1 - ease(seg(t, t1 - 0.2, t1)))
            f = font(FONT_BLACK, 60 if v else 40); fl = font(FONT_MED, 30 if v else 22)
            y = int(oh * (0.74 if v else 0.80))
            band = Image.new("RGBA", (ow, (170 if v else 120)), (0, 0, 0, 0)); bd = ImageDraw.Draw(band)
            bd.rectangle((0, 0, ow, band.height), fill=(6, 5, 14, int(150 * a)))
            img.alpha_composite(band.filter(ImageFilter.GaussianBlur(16)), (0, y - (34 if v else 22)))
            text_center(img, y - (20 if v else 14), "ROOK · CONDUCTOR", fl, BRASS, a, spacing=3)
            # wrap if needed
            d = ImageDraw.Draw(img); words = txt.split(); rows = [""]
            for wd in words:
                test = (rows[-1] + " " + wd).strip()
                if d.textlength(test, font=f) > ow - 90: rows.append(wd)
                else: rows[-1] = test
            for i, row in enumerate(rows): text_center(img, y + 22 + i * (74 if v else 50), row, f, (246, 242, 236), a)

def speaking(t, lines):
    for t0, t1, _ in lines:
        if t0 <= t < t1 - 0.15: return 0.5 + 0.5 * math.sin((t - t0) * 22)
    return 0.0

# ---------------------------------------------------------------- end card
def draw_hush_eyes(img, cx, cy, sc, a):
    for sd in (-1, 1):
        add_glow(img, cx + sd * 56 * sc, cy, 60 * sc, (120, 255, 190), 0.6 * a)
        ImageDraw.Draw(img).ellipse((cx + sd * 56 * sc - 8 * sc, cy - 8 * sc, cx + sd * 56 * sc + 8 * sc, cy + 8 * sc), fill=PALE + (int(255 * a),))

def title_card(t, t0, ep_no, ep_title, orient="h", note=None):
    ow, oh = SIZES[orient]; v = orient == "v"
    img = Image.new("RGBA", (ow, oh), (8, 7, 20, 255)); k = (t - t0) * (7.0 / TITLE_LEN)
    add_glow(img, ow / 2, oh * (0.30 if v else 0.30), (520 if v else 360), (120, 130, 255), 0.25)
    draw_hush_eyes(img, ow / 2, oh * (0.20 if v else 0.17), 1.6 if v else 1.1, ease(seg(k, 0.0, 1.0)) * (1 - ease(seg(k, 4.5, 6.0))))
    a_r = ease(seg(k, 0.3, 1.1))
    if a_r > 0:
        tmp = Image.new("RGBA", (ow, oh), (0, 0, 0, 0))
        draw_rook(tmp, t, rook(sc=1.1 if v else 0.7, x=ow / 2, y=(oh * 0.47 if v else oh * 0.52), pose="wave" if k < 3.5 else "idle",
                               flap=0.4 if k < 3.5 else 0, look=-0.35, blink=blink_at(k, [2.4, 5.0])))
        if a_r < 1: tmp.putalpha(tmp.getchannel("A").point(lambda q: int(q * a_r)))
        img.alpha_composite(tmp)
    y0 = int(oh * (0.52 if v else 0.58))
    text_center(img, y0, "GLOAMRUN", font(FONT_SERIF, 150 if v else 104), BRASS, ease(seg(k, 0.6, 1.6)), spacing=14 if v else 10)
    text_center(img, y0 + (200 if v else 136), f"EPISODE {ep_no}", font(FONT_MED, 46 if v else 32), (230, 210, 180), ease(seg(k, 1.2, 2.1)), spacing=4)
    f_ep = font(FONT_BLACK, 62 if v else 42)
    if ImageDraw.Draw(img).textlength(ep_title, font=f_ep) > ow - 80: f_ep = font(FONT_BLACK, 46 if v else 32)
    text_center(img, y0 + (270 if v else 184), ep_title, f_ep, (246, 242, 236), ease(seg(k, 2.0, 3.0)))
    tbc = note or "To be continued"
    text_center(img, oh - (240 if v else 64), tbc, font(FONT_MED, 40 if v else 26), BRASS, ease(seg(k, 3.0, 3.8)) * (1 - ease(seg(k, 6.3, 6.9))))
    text_center(img, oh - (150 if v else 30), "© 2026 Mori. Original work.", font(FONT_MED, 26 if v else 16), (150, 140, 170), ease(seg(k, 3.0, 3.8)))
    out = ease(seg(k, 6.5, 7.0))
    if out > 0: img.alpha_composite(Image.new("RGBA", (ow, oh), (0, 0, 0, int(255 * out))))
    return img

# ---------------------------------------------------------------- render
def build_vignette(ow, oh, power=150):
    yy, xx = np.mgrid[0:oh, 0:ow]
    d = np.sqrt(((xx - ow / 2) / (ow / 2)) ** 2 + ((yy - oh / 2) / (oh / 2)) ** 2)
    a = np.clip((d - 0.7) / 0.8, 0, 1) ** 1.5 * power
    v = np.zeros((oh, ow, 4), np.uint8); v[..., 3] = a.astype(np.uint8)
    return Image.fromarray(v, "RGBA")

class Renderer:
    def __init__(self, ep, orient="h"):
        self.ep = ep; self.orient = orient; self.ow, self.oh = SIZES[orient]
        kind = getattr(ep, "BG", "night")
        self.sky = {"night": build_sky("night"), "dawn": build_sky("dawn")}
        self.layers = {k: dict(far=build_far(kind=k), lit=build_town(True, kind=k), dark=build_town(False, kind=k), tr=build_trestle(k)) for k in ("night", "dawn")}
        self.stars = base_stars(); self.vig = build_vignette(self.ow, self.oh); self.story_end = ep.DUR - TITLE_LEN
        self.lines = getattr(ep, "LINES", [])

    def world(self, t):
        ep = self.ep
        dawn = ep.dawn(t) if hasattr(ep, "dawn") else (1.0 if getattr(ep, "BG", "night") == "dawn" else 0.0)
        fr = self.sky["night"].copy() if dawn < 1 else self.sky["dawn"].copy()
        if 0 < dawn < 1: fr = Image.blend(fr, self.sky["dawn"], dawn)
        draw_stars(fr, t, self.stars, 1 - dawn)
        L = self.layers["night" if dawn < 0.5 else "dawn"]
        sx = ep.scroll(t) if hasattr(ep, "scroll") else 0.0
        show = getattr(ep, "SHOW", ("far", "town", "rail"))
        if "far" in show: scroll_paste(fr, L["far"], sx * 0.12)
        hs = ep.hush_state(t) if hasattr(ep, "hush_state") else None
        ctx = dict(scroll=sx, hush=hs, dawn=dawn)
        if hasattr(ep, "draw_back"): ep.draw_back(fr, t, ctx)
        if hs: draw_hush(fr, t, hs)
        if "town" in show:
            edge = ep.dark_edge(t) if hasattr(ep, "dark_edge") else None
            if edge is None: scroll_paste(fr, L["lit"], sx * 0.45)
            else:
                town = Image.new("RGBA", (W, H), (0, 0, 0, 0)); scroll_paste(town, L["dark"], sx * 0.45)
                lit = Image.new("RGBA", (W, H), (0, 0, 0, 0)); scroll_paste(lit, L["lit"], sx * 0.45)
                e = int(clamp(edge, -1, W + 1)) if edge >= 0 else 0
                if e < W: town.alpha_composite(lit.crop((max(0, e), 0, W, H)), (max(0, e), 0))
                fr.alpha_composite(town)
        if "rail" in show: scroll_paste(fr, L["tr"], sx)
        ts = ep.train_state(t) if hasattr(ep, "train_state") else None
        ctx["train"] = ts
        if ts: draw_train(fr, t, ts, sx)
        if hasattr(ep, "draw_scene"): ep.draw_scene(fr, t, ctx)
        rs = ep.rook_state(t); ctx["rook"] = rs
        if rs and rs.get("x", -9999) > -400:
            rs = dict(rs); rs["beak"] = max(rs.get("beak", 0), speaking(t, self.lines)); draw_rook(fr, t, rs)
        if hasattr(ep, "draw_front"): ep.draw_front(fr, t, ctx)
        return fr, ctx

    def frame(self, t):
        ep = self.ep; ow, oh = self.ow, self.oh
        if t >= self.story_end:
            return title_card(t, self.story_end, ep.EP_NO, ep.EP_TITLE, self.orient, getattr(ep, "END_NOTE", None)).convert("RGB")
        fr, ctx = self.world(t)
        if self.orient == "v" and hasattr(ep, "camera_v"): cx, cy, z = ep.camera_v(t)
        else: cx, cy, z = ep.camera(t)
        sh = ep.shake(t) if hasattr(ep, "shake") else 0.0
        cx += math.sin(t * 0.7) * 6 + math.sin(t * 37) * 14 * sh; cy += math.sin(t * 0.53) * 5 + math.cos(t * 41) * 12 * sh
        if self.orient == "v":
            zv = max(1.0, z * 0.85); vh = H / zv; vw = vh * 9 / 16
        else: vw, vh = W / z, H / z
        cx = clamp(cx, vw / 2, W - vw / 2); cy = clamp(cy, vh / 2, H - vh / 2)
        out = fr.crop((int(cx - vw / 2), int(cy - vh / 2), int(cx + vw / 2), int(cy + vh / 2))).resize((ow, oh), Image.LANCZOS)
        out.alpha_composite(self.vig)
        dark = ep.blackout(t) if hasattr(ep, "blackout") else 0.0     # lights-out moments
        if dark > 0.01: out.alpha_composite(Image.new("RGBA", (ow, oh), (0, 0, 0, int(240 * clamp(dark)))))
        if hasattr(ep, "draw_overlay"): ep.draw_overlay(out, t, self.orient)
        draw_line(out, t, self.lines, self.orient)
        fa = ease(seg(t, self.story_end - 0.5, self.story_end))
        if fa > 0.005: out.alpha_composite(Image.new("RGBA", (ow, oh), (0, 0, 0, int(255 * clamp(fa)))))
        return out.convert("RGB")

def render_range(ep, path, lo, hi, orient="h"):
    rd = Renderer(ep, orient)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{rd.ow}x{rd.oh}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    for i in range(lo, hi): p.stdin.write(rd.frame(i / FPS).tobytes())
    p.stdin.close(); p.wait()

def preview(ep, times, outdir, orient="v"):
    rd = Renderer(ep, orient); os.makedirs(outdir, exist_ok=True); fs = []
    for t in times:
        f = os.path.join(outdir, f"prev_{orient}_{t:05.1f}.png"); rd.frame(t).save(f); fs.append(f)
    tw, th = (270, 480) if orient == "v" else (640, 360); cols = 4 if orient == "v" else 2
    sheet = Image.new("RGB", (tw * cols, th * ((len(fs) + cols - 1) // cols)))
    for i, f in enumerate(fs): sheet.paste(Image.open(f).resize((tw, th)), ((i % cols) * tw, (i // cols) * th))
    out = os.path.join(outdir, f"sheet_{orient}.png"); sheet.save(out); return out
