"""Act 1 - cold open (the Hush over the steam), then the night run; the Hush comes; the boiler runs dry; a water tower ahead."""
import math
import gloamrun_engine as E
from gloamrun_engine import rook, hush, train, keyframes, steps_at, seg, ease, lerp
ACT_LEN = 34.0
COLD = 3.6
SHOW = ("far", "rail")
LINES = [
    (0.6, 2.8, "...Don't move. Not a sound."),
    (4.2, 6.4, "Evening! Next stop: Brightwater."),
    (9.6, 11.6, "...Do you hear that?"),
    (12.4, 14.4, "It's back. Full steam!"),
    (19.4, 21.6, "It's faster tonight..."),
    (23.4, 25.6, "Oh no. The water is almost gone!"),
    (27.0, 29.0, "No water, no steam."),
    (30.6, 33.4, "There! The old water tower!"),
]
BLINKS = E.auto_blinks(ACT_LEN, seed=131)
def speed(t):
    if t < COLD: return 0.0
    return 600 + 900 * ease(seg(t, 14.0, 16.5)) - 500 * ease(seg(t, 24.0, 30.0))
_c = {}
def scroll(t):
    k = round(t * 24)
    if k not in _c:
        s = 0.0; dt = 1 / 48
        for i in range(int(t / dt)): s += speed(i * dt) * dt
        _c[k] = s
    return _c[k]
def steam(frame, cx, cy, a, t, warm=0.0):
    for k in range(14):
        ang = k * 2.4; r = 260 + 140 * (k % 3)
        x = cx + math.cos(ang) * r * 1.4 + math.sin(t * 0.5 + k) * 30; y = cy + math.sin(ang) * r * 0.45 + math.cos(t * 0.4 + k) * 20
        E.add_glow(frame, x, y, 420 + 60 * (k % 4), (205, 212, 222), 0.55 * a)
    if warm > 0: E.add_glow(frame, cx + 200, cy + 60, 380, E.WINDOW, 0.35 * warm * a)
def tower(frame, x):
    if x < -400 or x > E.W + 400: return
    d = E.ImageDraw.Draw(frame); wood = (58, 42, 40, 255); dark = (30, 24, 28, 255); y0 = E.RAIL
    for lx in (x - 150, x + 150): d.polygon([(lx - 14, y0 - 380), (lx + 14, y0 - 380), (lx + 24 * (1 if lx > x else -1) + 14, y0), (lx + 24 * (1 if lx > x else -1) - 14, y0)], fill=dark)
    d.line((x - 150, y0 - 200, x + 150, y0 - 200), fill=dark, width=10)
    d.rectangle((x - 200, y0 - 640, x + 200, y0 - 380), fill=wood, outline=E.INK + (255,), width=6)
    for k in range(5): d.line((x - 200, y0 - 600 + k * 50, x + 200, y0 - 600 + k * 50), fill=(40, 30, 30, 255), width=4)
    d.polygon([(x - 230, y0 - 640), (x, y0 - 760), (x + 230, y0 - 640)], fill=dark)
    d.rectangle((x - 220, y0 - 470, x - 120, y0 - 450), fill=E.IRON + (255,))
def train_state(t): return train(x=2050, cars=2, lamp=1.0 if t >= COLD else 0.0, smoke=1.0 if t >= COLD else 0.0)
def rook_state(t):
    if t < COLD:
        return rook(x=1190, y=E.RAIL - 160, face=1, pose="shh", eye=0.35, blink=E.blink_at(t, [1.8]))
    pose = steps_at(t, [(COLD, "wave"), (6.6, "idle"), (9.4, "lean"), (12.2, "spread"), (14.6, "ahead"), (19.2, "flinch"),
                        (23.2, "down"), (26.8, "sad"), (30.4, "point"), (33.4, "ahead")])
    face = -1 if (9.4 <= t < 12.2 or 19.2 <= t < 23.0) else 1
    eye = 1.6 if 17.0 < t < 23.0 else 1.0
    return rook(x=1190, y=E.RAIL - 160, face=face, pose=pose, look={"ahead": 0.6, "point": 0.5, "lean": 0.2, "down": -0.3}.get(pose, 0.0), eye=eye,
                flap=0.6 if pose in ("wave", "spread") else 0.0, lean=0.07 * math.sin(t * 9) if t > 15 else 0.0, blink=E.blink_at(t, BLINKS))
def hush_state(t):
    if t < COLD:
        return hush(x=1300, y=330, sc=1.8, near=1.0, eye=1.6, hand="shh", lean=0.04 * math.sin(t))
    x, y, sc, near = keyframes(t, [(COLD, 560, 1500, 0.6, 0.0), (7.0, 560, 900, 0.65, 0.1), (10.0, 560, 640, 0.75, 0.2), (14.0, 480, 600, 0.85, 0.3),
                                   (19.0, 820, 430, 1.3, 0.8), (22.0, 880, 400, 1.4, 0.9), (26.0, 560, 520, 1.0, 0.4), (34.0, 640, 480, 1.15, 0.6)])
    return hush(x=x, y=y, sc=sc, near=near, eye=1.0 + 0.6 * near, hand="shh", lean=0.05 * math.sin(t * 1.3))
def draw_scene(frame, t, ctx):
    if t < COLD:
        steam(frame, 1500, 900, 0.9, t, warm=0.0); return
    if t > 29.0:
        tower(frame, lerp(3200, 2700, ease(seg(t, 29.0, 34.0))))
def blackout(t): return 0.55 if t < COLD else 0.0
def draw_overlay(out, t, orient):
    if t >= COLD: return
    ow, oh = out.size
    for sd in (-1, 1):
        px, py = ow * 0.5 + sd * 70, oh * 0.18
        E.add_glow(out, px, py, 90, (120, 255, 190), 0.9)
def shake(t): return 0.15 if t > 15 else 0.0
def camera(t):
    if t < COLD: return (1300, 620, 1.35 + 0.05 * t)
    return keyframes(t, [(COLD, 1250, 760, 1.3), (8.0, 1280, 720, 1.0), (10.0, 900, 640, 1.1), (12.4, 1190, 800, 1.5),
                         (16, 1280, 720, 1.0), (19.4, 1000, 560, 1.15), (23.2, 1190, 780, 1.45), (29.0, 1280, 720, 1.0), (31.0, 1700, 600, 1.15), (34, 1600, 640, 1.05)])
def score(S):
    S.add(S.drone(COLD, 34), 0, 0.7); S.add(S.heartbeat(), 0.6, 0.5); S.add(S.heartbeat(), 1.7, 0.55); S.add(S.heartbeat(), 2.8, 0.6)
    S.add(S.stinger(), COLD - 0.1, 0.5)
    S.add(S.bell(81), COLD, 0.25); S.add(S.wind(ACT_LEN), 0, 0.3)
    S.train_rhythm(COLD, 14.0, 0.42, 0.15)
    S.play([(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)], 4.4, 0.36, 0.12)
    S.add(S.drone(8.0, 38), 9.0, 0.55); S.add(S.shh(1.8), 10.0, 0.5)
    S.add(S.whistle(1.4), 12.6, 0.7)
    S.train_rhythm(14.0, ACT_LEN, 0.26, 0.16); S.chase(14.2, 24.0, bpm=158, gain=0.14)
    S.steps(17.0, 23.0, 0.8, 0.45); S.add(S.stinger(), 19.2, 0.45)
    S.silence_music(23.0, 29.0, 0.6); S.add(S.drone(7.0, 36), 23.0, 0.5)
    S.play([(74, 1), (78, 1), (81, 1)], 30.8, 0.3, 0.1)
