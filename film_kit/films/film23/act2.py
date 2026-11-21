"""Act 2 - lights off, stop at the old signal box. Rook turns every lamp on the quarry line green. The Hush comes, stands right over the dark train, then sees the green lamps."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gloamrun_engine as E
from gloamrun_engine import rook, hush, train, keyframes, steps_at, seg, ease, lerp, clamp
import sig
ACT_LEN = 36.0
SHOW = ("far", "rail")
T_STOP, T_GREEN = 4.0, 7.4
LINES = [
    (0.6, 2.8, "Lights off. Stop at the box."),
    (4.0, 6.2, "Every signal on the quarry line..."),
    (7.4, 9.4, "...Green!"),
    (11.0, 13.2, "...Here it comes."),
    (15.6, 17.8, "...It's right above us."),
    (19.4, 21.6, "...Don't move. Not a sound."),
    (25.0, 27.2, "It sees the green lights..."),
    (29.6, 32.8, "Yes. Follow them. Far, far away."),
]
BLINKS = E.auto_blinks(ACT_LEN, seed=232)
def speed(t): return 700 * (1 - ease(seg(t, 0.0, T_STOP)))
_c = {}
def scroll(t):
    k = round(t * 24)
    if k not in _c:
        s = 0.0; dt = 1 / 48
        for i in range(int(t / dt)): s += speed(i * dt) * dt
        _c[k] = s
    return _c[k]
def wx(t): return -scroll(t) + scroll(ACT_LEN)
def train_state(t): return train(x=2050, cars=2, lamp=1.0 - ease(seg(t, 0.4, 1.2)), smoke=0.3 * (1 - ease(seg(t, 0, T_STOP))), dark=0.3 * ease(seg(t, 0.4, 1.2)))
def rook_state(t):
    pose = steps_at(t, [(0, "pull"), (3.8, "lean"), (7.2, "pull"), (9.6, "point"), (10.8, "down"), (15.4, "flinch"), (19.2, "shh"), (24.8, "lean"), (29.4, "shh"), (33.0, "down")])
    face = -1 if 9.6 <= t < 15.4 or 24.8 <= t < 29.4 else 1
    return rook(x=1190, y=E.RAIL - 160, face=face, pose=pose, look={"point": 0.5, "lean": 0.3, "down": -0.2}.get(pose, 0.0),
                eye=1.0 if t < 10.8 else 0.35, blink=E.blink_at(t, BLINKS))
def green_on(t): return sig.N * ease(seg(t, T_GREEN - 0.6, T_GREEN + 2.4))
def hush_state(t):
    x, y, sc, near = keyframes(t, [(0, 200, 640, 0.7, 0.3), (8.0, 260, 620, 0.75, 0.35), (12.0, 600, 470, 1.25, 0.7), (15.0, 1200, 300, 1.8, 1.0),
                                   (24.0, 1300, 290, 1.85, 1.0), (28.0, 1250, 300, 1.8, 1.0), (36.0, 1000, 380, 1.5, 0.85)])
    return hush(x=x, y=y, sc=sc, near=near, eye=1.5 if t > 11 else 1.2, hand="shh",
                lean=0.05 * math.sin(t * 1.1) - 0.1 * ease(seg(t, 24.5, 28.0)))
def draw_back(frame, t, ctx):
    sig.box(frame, 560 + wx(t) * 0.0 + scroll(ACT_LEN) - scroll(t), E.RAIL - 40, lit=0.0)
    sig.far_line(frame, t, on=green_on(t))
def draw_scene(frame, t, ctx):
    sig.post(frame, 2420 + scroll(ACT_LEN) - scroll(t), E.RAIL, 1.0, red=1.0 - ease(seg(t, T_GREEN - 0.4, T_GREEN + 0.4)))
def blackout(t): return 0.3 * ease(seg(t, 9.0, 12.0))
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
def shake(t): return 0.0
def camera(t):
    return keyframes(t, [(0, 1190, 760, 1.35), (3.0, 1300, 700, 1.0), (4.0, 1190, 780, 1.4), (7.2, 800, 720, 1.0), (10.8, 700, 640, 1.0),
                         (13.2, 1000, 640, 1.0), (15.6, 1250, 560, 1.05), (19.4, 1190, 760, 1.4), (24.6, 1100, 640, 1.0), (27.2, 900, 700, 1.0),
                         (29.6, 1190, 780, 1.4), (36, 1000, 660, 1.0)])
def score(S):
    S.add(S.wind(ACT_LEN, 0.6), 0, 0.3); S.train_rhythm(0, T_STOP, 0.6, 0.1); S.add(S.clack(), T_STOP, 0.5)
    S.add(S.clack(), T_GREEN - 0.3, 0.7); S.add(S.thump(), T_GREEN - 0.3, 0.4)
    for i in range(sig.N): S.add(S.pluck(81 + (i % 5) * 2), T_GREEN - 0.5 + i * 0.3, 0.25)
    S.add(S.drone(26.0, 36), 9.0, 0.6); S.add(S.shh(2.4), 10.0, 0.5); S.steps(10.0, 15.5, 1.0, 0.6)
    S.add(S.stinger(), 15.6, 0.45)
    for k in range(10): S.add(S.heartbeat(), 16.0 + k * 1.0, 0.5 if k < 5 else 0.6)
    S.add(S.shh(2.0), 20.0, 0.4); S.steps(29.0, 36.0, 1.2, 0.45)
