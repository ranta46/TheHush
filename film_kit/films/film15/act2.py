"""Act 2 - into the Firefly Wood. The lamp stays on, but now it is one light among a thousand. The Hush comes in; the lights go out around it."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gloamrun_engine as E
from gloamrun_engine import rook, hush, train, keyframes, steps_at, seg, ease, lerp, clamp
import ff
ACT_LEN = 36.0
SHOW = ("far", "rail")
T_STOP, T_IN, T_NEAR = 6.0, 12.0, 21.0
LINES = [
    (0.6, 2.8, "Into the wood. Slow down..."),
    (4.4, 6.6, "Now we are just one more light."),
    (9.0, 11.2, "...Here it comes."),
    (13.2, 15.4, "Look. The lights go out near it."),
    (17.6, 19.8, "...It's looking for the brightest one."),
    (23.0, 25.2, "...It's right above us."),
    (26.4, 28.4, "...Don't move. Not a sound."),
    (31.6, 34.0, "...Please. Just one more minute."),
]
BLINKS = E.auto_blinks(ACT_LEN, seed=152)
def speed(t): return 500 * (1 - ease(seg(t, 0.0, T_STOP)))
_c = {}
def scroll(t):
    k = round(t * 24)
    if k not in _c:
        s = 0.0; dt = 1 / 48
        for i in range(int(t / dt)): s += speed(i * dt) * dt
        _c[k] = s
    return _c[k]
def wx(t): return -scroll(t)
def train_state(t): return train(x=2050, cars=2, lamp=0.75, smoke=0.3 * (1 - ease(seg(t, 0, T_STOP))), dark=0.3)
def rook_state(t):
    pose = steps_at(t, [(0, "pull"), (4.2, "idle"), (8.8, "lean"), (13.0, "point"), (17.4, "down"), (22.8, "flinch"), (26.2, "shh"), (31.4, "down"), (35.0, "shh")])
    face = -1 if 8.8 <= t < 17.4 or 22.8 <= t < 26.2 else 1
    return rook(x=1190, y=E.RAIL - 160, face=face, pose=pose, look={"point": 0.4, "lean": 0.3, "down": -0.2}.get(pose, 0.0),
                eye=1.0 if t < 9 else 0.35, flap=0.0, blink=E.blink_at(t, BLINKS))
def hush_state(t):
    x, y, sc, near = keyframes(t, [(0, 640, 520, 1.1, 0.55), (6.0, 500, 560, 1.0, 0.5), (T_IN, 520, 440, 1.3, 0.75), (17.0, 900, 360, 1.55, 0.9),
                                   (T_NEAR, 1250, 300, 1.8, 1.0), (30.0, 1350, 290, 1.85, 1.0), (36.0, 1300, 300, 1.8, 1.0)])
    return hush(x=x, y=y, sc=sc, near=near, eye=1.5 if t > 9 else 1.2, hand="shh", lean=0.05 * math.sin(t * 1.1))
def draw_back(frame, t, ctx): ff.trees(frame, 300 + wx(t) * 0.6)
def draw_scene(frame, t, ctx):
    hs = hush_state(t)
    ff.draw(frame, t, wx(t) * 0.8, 1.0, dark_at=(hs["x"], hs["y"] + 300 * hs["sc"]) if t > T_IN - 2 else None, dark_r=200 + 260 * ease(seg(t, T_IN - 2, T_NEAR)))
def draw_front(frame, t, ctx):
    hs = hush_state(t)
    for k in range(10):   # a few flies in front of the train too
        x = 700 + k * 190 + 30 * math.sin(t * 1.1 + k); y = 900 + 60 * math.sin(k * 1.7 + t * 0.8)
        d = math.hypot(x - hs["x"], y - hs["y"] - 300 * hs["sc"]); a = min(1.0, max(0.0, (d - 420) / 240)) if t > T_IN else 1.0
        E.add_glow(frame, x, y, 50, ff.COL, 0.8 * a * (0.6 + 0.4 * math.sin(t * 2.5 + k)))
def blackout(t): return 0.35 * ease(seg(t, 8.0, 12.0))
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
    return keyframes(t, [(0, 1190, 760, 1.35), (3.0, 1400, 640, 1.0), (4.4, 1190, 780, 1.4), (7.0, 1280, 700, 1.0), (9.0, 800, 600, 1.15),
                         (13.2, 1000, 640, 1.0), (17.6, 1190, 760, 1.35), (21.0, 1250, 560, 1.05), (23.0, 1190, 760, 1.4), (28.6, 1300, 600, 1.05),
                         (31.6, 1190, 780, 1.45), (36, 1280, 680, 1.0)])
def score(S):
    S.add(S.wind(ACT_LEN, 0.6), 0, 0.3); S.train_rhythm(0, T_STOP, 0.6, 0.1); S.add(S.clack(), T_STOP, 0.5)
    S.play([(81, 1), (86, 1), (88, 2)], 4.6, 0.4, 0.07)
    S.add(S.drone(26.0, 36), 8.0, 0.6); S.add(S.shh(2.4), 9.4, 0.5); S.steps(10.0, 22.0, 1.0, 0.6)
    S.add(S.stinger(), 13.2, 0.35); S.add(S.stinger(), 22.8, 0.45)
    for k in range(12): S.add(S.heartbeat(), 22.5 + k * 1.0, 0.5 if k < 6 else 0.6)
    S.add(S.shh(2.0), 27.0, 0.4)
