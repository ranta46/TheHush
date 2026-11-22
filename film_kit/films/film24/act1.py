"""Act 1 - cold open (the Hush close to Rook), then already in danger: the windmill lamps went out, it is close behind; the old mill ahead."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gloamrun_engine as E
from gloamrun_engine import rook, hush, train, keyframes, steps_at, seg, ease, lerp
import mill
ACT_LEN = 34.0
COLD = 3.6
SHOW = ("far", "rail")
LINES = [
    (0.6, 2.8, "...It's right behind us. Shh."),
    (4.0, 6.2, "The mill lamps went out. It's here!"),
    (7.4, 9.6, "Hold on, everyone. Full steam!"),
    (11.2, 13.4, "It walks over the fields so fast."),
    (15.6, 17.8, "...It's at the last car!"),
    (20.4, 22.6, "Look. The old mill on the hill."),
    (24.8, 27.0, "I still have the spare lantern."),
    (29.4, 32.6, "Then let's give it a light to watch."),
]
BLINKS = E.auto_blinks(ACT_LEN, seed=241)
def speed(t):
    if t < COLD: return 0.0
    return 900 + 700 * ease(seg(t, 7.4, 9.6)) - 600 * ease(seg(t, 24.0, 31.0))
_c = {}
def scroll(t):
    k = round(t * 24)
    if k not in _c:
        s = 0.0; dt = 1 / 48
        for i in range(int(t / dt)): s += speed(i * dt) * dt
        _c[k] = s
    return _c[k]
def train_state(t): return train(x=2050, cars=2, lamp=0.0 if t < COLD else 1.0, smoke=1.0 if t >= COLD else 0.0)
def rook_state(t):
    if t < COLD:
        return rook(x=1190, y=E.RAIL - 160, face=-1, pose="shh", eye=0.35, blink=E.blink_at(t, [1.8]))
    pose = steps_at(t, [(COLD, "flinch"), (6.6, "pull"), (10.0, "lean"), (13.6, "pull"), (15.4, "flinch"), (18.4, "idle"),
                        (20.2, "point"), (24.6, "ahead"), (28.0, "down"), (29.2, "spread"), (33.0, "idle")])
    face = -1 if (10.0 <= t < 13.6 or 15.4 <= t < 18.4) else 1
    eye = 1.6 if 15.0 < t < 19.0 else 1.0
    return rook(x=1190, y=E.RAIL - 160, face=face, pose=pose, look={"ahead": 0.6, "point": 0.5, "lean": 0.2, "down": -0.3}.get(pose, 0.0), eye=eye,
                flap=0.6 if pose == "spread" else 0.0, lean=0.07 * math.sin(t * 9) if 7.4 < t < 24 else 0.0, blink=E.blink_at(t, BLINKS))
def hush_state(t):
    if t < COLD:
        return hush(x=1450, y=330, sc=1.8, near=1.0, eye=1.6, hand="shh", lean=0.04 * math.sin(t))
    x, y, sc, near = keyframes(t, [(COLD, 520, 620, 0.9, 0.4), (7.0, 500, 600, 0.95, 0.45), (11.0, 620, 480, 1.2, 0.7), (15.0, 720, 400, 1.45, 0.9),
                                   (18.0, 740, 400, 1.45, 0.9), (22.0, 440, 560, 1.0, 0.5), (28.0, 360, 600, 0.9, 0.4), (34.0, 420, 580, 0.95, 0.45)])
    return hush(x=x, y=y, sc=sc, near=near, eye=1.0 + 0.6 * near, hand="point" if 15.6 < t < 18.0 else "shh", lean=0.05 * math.sin(t * 1.3))
def draw_back(frame, t, ctx):
    if t < COLD:
        mill.mill(frame, 300, E.RAIL - 40, 0.8, ang=t * 0.3); return
    mill.far_mills(frame, scroll(t), t, lit=0.0)
    if t > 19.0:   # the old mill on the hill comes into view
        mill.mill(frame, lerp(2700, 1700, ease(seg(t, 19.0, 32.0))), E.RAIL - 80, 0.75, ang=t * 0.5)
def blackout(t): return 0.5 if t < COLD else 0.0
def draw_overlay(out, t, orient):
    if t >= COLD: return
    ow, oh = out.size
    for sd in (-1, 1): E.add_glow(out, ow * 0.62 + sd * 70, oh * 0.16, 90, (120, 255, 190), 0.9)
def shake(t): return 0.15 if 7.4 < t < 24 else 0.0
def camera(t):
    if t < COLD: return (1350, 640, 1.3 + 0.05 * t)
    return keyframes(t, [(COLD, 1190, 780, 1.4), (7.0, 1280, 720, 1.0), (11.0, 900, 620, 1.1), (13.6, 1190, 780, 1.45), (15.4, 950, 600, 1.15),
                         (18.6, 1280, 720, 1.0), (20.4, 1500, 680, 1.0), (24.8, 1190, 780, 1.4), (28.0, 1300, 700, 1.05), (34, 1100, 700, 1.05)])
def score(S):
    S.add(S.drone(COLD, 34), 0, 0.7); S.add(S.heartbeat(), 0.6, 0.5); S.add(S.heartbeat(), 1.7, 0.55); S.add(S.heartbeat(), 2.8, 0.6)
    S.add(S.stinger(), COLD - 0.1, 0.5); S.add(S.wind(ACT_LEN, 1.2), 0, 0.35)
    S.add(S.whistle(1.2), 7.4, 0.7)
    S.train_rhythm(COLD, ACT_LEN, 0.3, 0.16); S.chase(COLD + 0.2, 24.0, bpm=160, gain=0.14)
    S.steps(10.0, 19.0, 0.8, 0.5); S.add(S.stinger(), 15.6, 0.45)
    S.silence_music(24.0, 29.0, 0.5); S.add(S.drone(6.0, 36), 24.0, 0.5)
    S.play([(74, 1), (77, 1), (81, 1), (86, 1)], 29.6, 0.3, 0.1)
