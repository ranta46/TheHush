"""Act 3 - the end of the line. The train stops in the dark; the Hush is right above; it points at you. Then a song from the sky."""
import math, random
import gloamrun_engine as E
from gloamrun_engine import rook, hush, train, keyframes, steps_at, seg, ease, lerp, clamp
ACT_LEN = 32.0
SHOW = ("far", "rail")
T_DARK0 = 6.0
LINES = [
    (0.4, 2.6, "End of the line? It can't be."),
    (3.6, 5.8, "...Lamps off. Everyone, quiet."),
    (9.2, 11.4, "...It's right above us. Don't breathe."),
    (16.6, 18.8, "...It's pointing at you."),
    (21.2, 23.2, "...Stay still. Please."),
    (26.0, 28.2, "...That song. I know that song."),
    (29.4, 31.6, "Old friend! Down here!"),
]
BLINKS = E.auto_blinks(ACT_LEN, seed=103)
def speed(t): return 800 * (1 - ease(seg(t, 0.0, 3.5)))
_c = {}
def scroll(t):
    k = round(t * 24)
    if k not in _c:
        s = 0.0; dt = 1 / 48
        for i in range(int(t / dt)): s += speed(i * dt) * dt
        _c[k] = s
    return _c[k]
def train_state(t): return train(x=2050, cars=2, lamp=1.0 - ease(seg(t, 4.0, 5.2)), smoke=0.4 * (1 - seg(t, 3, 6)))
def blue(t): return ease(seg(t, 25.0, 31.5))
def rook_state(t):
    pose = steps_at(t, [(0, "sad"), (3.4, "shh"), (8.8, "down"), (16.4, "flinch"), (19.0, "shh"), (25.8, "lean"), (29.2, "wave")])
    eye = 1.0
    if T_DARK0 < t < 25.5: eye = 0.35
    if t >= 29.2: eye = 1.6
    face = -1 if 16.4 <= t < 19.0 else 1
    return rook(x=1190, y=E.RAIL - 160, face=face, pose=pose, look=0.5 if pose == "lean" else 0.0, eye=eye,
                flap=0.7 if pose == "wave" else 0.0, blink=E.blink_at(t, BLINKS))
def hush_state(t):
    x, y, sc, near = keyframes(t, [(0, 600, 560, 1.0, 0.4), (6.0, 900, 380, 1.4, 0.9), (9.0, 1250, 300, 1.75, 1.0), (16.0, 1250, 300, 1.8, 1.0),
                                   (22.0, 1150, 320, 1.7, 1.0), (27.0, 900, 420, 1.4, 0.8), (32.0, 760, 480, 1.25, 0.7)])
    hand = "point" if 15.6 < t < 20.4 else "shh"
    return hush(x=x, y=y, sc=sc, near=near, eye=1.5, hand=hand, point_dir=1, lean=0.04 * math.sin(t * 1.1))
def blackout(t):
    if t < T_DARK0: return 0.0
    return 0.84 * ease(seg(t, T_DARK0, T_DARK0 + 0.8)) - 0.4 * blue(t)
def draw_overlay(out, t, orient):
    b = blackout(t)
    if b < 0.05: return
    ow, oh = out.size; cx, cy, z = camera(t)
    vw, vh = E.W / z, E.H / z; cx = clamp(cx, vw / 2, E.W - vw / 2); cy = clamp(cy, vh / 2, E.H - vh / 2)
    to = lambda X, Y: ((X - (cx - vw / 2)) / vw * ow, (Y - (cy - vh / 2)) / vh * oh); s = ow / vw
    hs = hush_state(t)
    for sd in (-1, 1):
        px, py = to(hs["x"] + sd * 56 * hs["sc"], hs["y"] - 40 * hs["sc"])
        E.add_glow(out, px, py, 80 * hs["sc"] * s, (120, 255, 190), 0.9 * b)
        r = 10 * hs["sc"] * s; E.ImageDraw.Draw(out).ellipse((px - r, py - r, px + r, py + r), fill=E.PALE + (int(255 * b),))
    rr = random.Random(7)
    for k in range(30):
        X, Y = rr.uniform(150, E.W - 150), rr.uniform(150, E.H - 220)
        op = b * (0.5 + 0.5 * math.sin(t * 2 + k)) * seg(t, T_DARK0 + 2.0, T_DARK0 + 4.0)
        px, py = to(X, Y)
        for sd in (-1, 1):
            E.ImageDraw.Draw(out).ellipse((px + sd * 9 * s - 4 * s, py - 3 * s, px + sd * 9 * s + 4 * s, py + 3 * s), fill=E.PALE + (int(200 * op),))
    rs = rook_state(t); gx, gy = to(rs["x"] + 24 * rs["face"], rs["y"] - 274)
    E.add_glow(out, gx, gy, (60 + 90 * rs["eye"]) * s, (255, 60, 40), 0.9 * b)
def draw_front(frame, t, ctx):
    bl = blue(t)
    if bl > 0.02:   # the Long Back's blue spots, far up in the clouds
        for k in range(9):
            E.add_glow(frame, 1700 + k * 90, 140 + abs(k - 4) ** 1.5 * 10 + math.sin(t + k) * 6, 70, E.WHALE_SPOT, 0.55 * bl)
def shake(t): return 0.35 if 9.0 < t < 9.6 else 0.0
def camera(t):
    return keyframes(t, [(0, 1280, 720, 1.05), (3.4, 1190, 780, 1.45), (6.2, 1190, 760, 1.3), (9.0, 1220, 560, 1.05), (13.0, 1220, 520, 1.15),
                         (16.4, 1190, 700, 1.4), (19.0, 1250, 560, 1.1), (24.0, 1200, 640, 1.2), (26.0, 1600, 420, 1.15), (29.2, 1190, 760, 1.4), (32, 1300, 600, 1.05)])
def score(S):
    S.add(S.wind(ACT_LEN, 0.8), 0, 0.3); S.train_rhythm(0, 3.4, 0.5, 0.12)
    S.add(S.clack(), 3.6, 0.7); S.add(S.drone(20.0, 34), 5.0, 0.8)
    S.add(S.shh(2.4), 6.5, 0.5); S.steps(6.5, 9.5, 1.0, 0.7); S.add(S.stinger(), 9.0, 0.4)
    for k in range(13): S.add(S.heartbeat(), 10.0 + k * 1.05, 0.5 if k < 6 else 0.6)
    S.add(S.stinger(), 15.8, 0.35); S.add(S.shh(2.0), 21.0, 0.4)
    S.add(S.whale(3.2), 25.2, 0.7); S.add(S.whale(3.0), 28.6, 0.8)
    S.play([(74, 1), (78, 1), (81, 2)], 29.6, 0.4, 0.11)
