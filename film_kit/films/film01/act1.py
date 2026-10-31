"""Act 1 - the night run. A calm start, then the Hush wakes far behind and comes fast."""
import math
import gloamrun_engine as E
from gloamrun_engine import rook, hush, train, keyframes, steps_at, seg, ease, lerp
ACT_LEN = 30.0
SHOW = ("far", "rail")
LINES = [
    (0.3, 2.6, "Evening! Next stop: Lantern Hill."),
    (3.2, 5.4, "Hold the bar. It's a long night."),
    (9.4, 11.4, "...Do you hear that?"),
    (13.0, 15.0, "Not tonight. Not again."),
    (15.6, 17.4, "Full steam!"),
    (22.4, 24.6, "It's faster than last time!"),
    (26.4, 29.2, "We have to reach Lantern Hill first!"),
]
BLINKS = E.auto_blinks(ACT_LEN, seed=101)
def speed(t): return 600 + 900 * ease(seg(t, 15.4, 18.0))
_c = {}
def scroll(t):
    k = round(t * 24)
    if k not in _c:
        s = 0.0; dt = 1 / 48
        for i in range(int(t / dt)): s += speed(i * dt) * dt
        _c[k] = s
    return _c[k]
def train_state(t): return train(x=2050, cars=2, lamp=1.0, smoke=1.0)
def rook_state(t):
    pose = steps_at(t, [(0, "wave"), (3.0, "idle"), (9.2, "lean"), (12.8, "sad"), (15.4, "spread"), (17.6, "ahead"),
                        (22.2, "flinch"), (26.2, "point"), (29.2, "ahead")])
    face = -1 if (9.2 <= t < 15.2 or 22.2 <= t < 29.0) else 1
    eye = 1.6 if 20.0 < t < 27.0 else 1.0
    return rook(x=1190, y=E.RAIL - 160, face=face, pose=pose, look={"ahead": 0.6, "point": 0.4, "lean": 0.2}.get(pose, 0.0), eye=eye,
                flap=0.6 if pose in ("wave", "spread") else 0.0, lean=0.07 * math.sin(t * 9) if t > 16 else 0.0, blink=E.blink_at(t, BLINKS))
def hush_state(t):
    x, y, sc, near = keyframes(t, [(0, 600, 1700, 0.6, 0.0), (8.0, 600, 1500, 0.6, 0.0), (12.0, 560, 640, 0.75, 0.2), (16.0, 480, 600, 0.85, 0.3),
                                   (20.0, 820, 430, 1.3, 0.8), (24.0, 900, 380, 1.45, 1.0), (27.0, 520, 520, 1.0, 0.4), (30.0, 600, 480, 1.1, 0.5)])
    return hush(x=x, y=y, sc=sc, near=near, eye=1.0 + 0.6 * near, hand="shh", lean=0.05 * math.sin(t * 1.3))
def shake(t): return 0.15 if t > 16 else 0.0
def camera(t):
    return keyframes(t, [(0, 1250, 760, 1.3), (5, 1280, 720, 1.0), (9, 900, 640, 1.1), (12, 650, 600, 1.2), (15.4, 1190, 800, 1.5),
                         (18, 1280, 720, 1.0), (22, 1000, 560, 1.15), (26, 1190, 760, 1.35), (30, 1280, 720, 1.05)])
def score(S):
    S.add(S.bell(81), 0.0, 0.25); S.add(S.bell(74), 0.35, 0.2); S.add(S.wind(ACT_LEN), 0, 0.35)
    S.train_rhythm(0.0, 15.6, 0.42, 0.15)
    S.play([(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)], 3.4, 0.36, 0.12)      # THEME once
    S.add(S.drone(10.0, 38), 8.0, 0.55); S.add(S.shh(1.8), 9.6, 0.5)
    S.add(S.whistle(1.4), 15.3, 0.7)
    S.train_rhythm(15.6, ACT_LEN, 0.26, 0.16); S.chase(15.8, ACT_LEN, bpm=156, gain=0.14)
    S.steps(19.0, 27.0, 0.8, 0.45); S.add(S.stinger(), 20.2, 0.45)
