"""Act 1 - cold open (the Hush among the fireflies), then the night run; the Hush comes; the lamp is stuck on; the Firefly Wood ahead."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gloamrun_engine as E
from gloamrun_engine import rook, hush, train, keyframes, steps_at, seg, ease, lerp
import ff
ACT_LEN = 34.0
COLD = 3.6
SHOW = ("far", "rail")
LINES = [
    (0.6, 2.8, "...Don't move. Not a sound."),
    (4.2, 6.4, "Evening! Next stop: Glowmere."),
    (9.6, 11.6, "...Do you hear that?"),
    (12.4, 14.4, "It's back. Lights off!"),
    (17.0, 19.2, "The lamp won't go out!"),
    (21.0, 23.2, "It can see us from miles away."),
    (26.4, 28.6, "Where do you hide one light?"),
    (30.4, 33.4, "...With a thousand others!"),
]
BLINKS = E.auto_blinks(ACT_LEN, seed=151)
def speed(t):
    if t < COLD: return 0.0
    return 600 + 900 * ease(seg(t, 14.0, 16.5)) - 300 * ease(seg(t, 26.0, 31.0))
_c = {}
def scroll(t):
    k = round(t * 24)
    if k not in _c:
        s = 0.0; dt = 1 / 48
        for i in range(int(t / dt)): s += speed(i * dt) * dt
        _c[k] = s
    return _c[k]
def train_state(t): return train(x=2050, cars=2, lamp=0.0 if t < COLD else (1.0 - 0.35 * abs(math.sin(t * 20)) * ease(seg(t, 14.6, 16.0)) * (1 - ease(seg(t, 19, 20)))), smoke=1.0 if t >= COLD else 0.0)
def rook_state(t):
    if t < COLD:
        return rook(x=1190, y=E.RAIL - 160, face=1, pose="shh", eye=0.35, blink=E.blink_at(t, [1.8]))
    pose = steps_at(t, [(COLD, "wave"), (6.6, "idle"), (9.4, "lean"), (12.2, "spread"), (14.6, "pull"), (16.8, "flinch"),
                        (20.8, "down"), (24.0, "lean"), (26.2, "idle"), (30.2, "point"), (33.4, "ahead")])
    face = -1 if (9.4 <= t < 12.2 or 20.8 <= t < 24.0) else 1
    eye = 1.6 if 16.0 < t < 23.0 else 1.0
    return rook(x=1190, y=E.RAIL - 160, face=face, pose=pose, look={"ahead": 0.6, "point": 0.5, "lean": 0.2, "down": -0.3}.get(pose, 0.0), eye=eye,
                flap=0.6 if pose in ("wave", "spread") else 0.0, lean=0.07 * math.sin(t * 9) if t > 15 else 0.0, blink=E.blink_at(t, BLINKS))
def hush_state(t):
    if t < COLD:
        return hush(x=1300, y=330, sc=1.8, near=1.0, eye=1.6, hand="shh", lean=0.04 * math.sin(t))
    x, y, sc, near = keyframes(t, [(COLD, 560, 1500, 0.6, 0.0), (7.0, 560, 900, 0.65, 0.1), (10.0, 560, 640, 0.75, 0.2), (14.0, 480, 600, 0.85, 0.3),
                                   (19.0, 820, 430, 1.3, 0.8), (22.0, 880, 400, 1.4, 0.9), (26.0, 600, 500, 1.05, 0.45), (34.0, 660, 470, 1.15, 0.6)])
    return hush(x=x, y=y, sc=sc, near=near, eye=1.0 + 0.6 * near, hand="point" if 20.0 < t < 23.0 else "shh", lean=0.05 * math.sin(t * 1.3))
def draw_scene(frame, t, ctx):
    if t < COLD:
        ff.trees(frame, 0); ff.draw(frame, t, 0, 1.0, dark_at=(1300, 600), dark_r=380); return
    if t > 28.0:
        a = ease(seg(t, 28.0, 32.0)); ox = lerp(1600, 600, ease(seg(t, 28.0, 34.0)))
        ff.trees(frame, ox + 600); ff.draw(frame, t, ox, a)
def blackout(t): return 0.55 if t < COLD else 0.0
def draw_overlay(out, t, orient):
    if t >= COLD: return
    ow, oh = out.size
    for sd in (-1, 1):
        E.add_glow(out, ow * 0.5 + sd * 70, oh * 0.18, 90, (120, 255, 190), 0.9)
def shake(t): return 0.15 if t > 15 else 0.0
def camera(t):
    if t < COLD: return (1300, 620, 1.35 + 0.05 * t)
    return keyframes(t, [(COLD, 1250, 760, 1.3), (8.0, 1280, 720, 1.0), (10.0, 900, 640, 1.1), (12.4, 1190, 800, 1.5),
                         (15, 1700, 640, 1.2), (17.0, 1190, 780, 1.45), (20.6, 1000, 560, 1.1), (24.0, 1280, 720, 1.0), (26.4, 1190, 780, 1.4), (30.0, 1600, 640, 1.05), (34, 1500, 660, 1.0)])
def score(S):
    S.add(S.drone(COLD, 34), 0, 0.7); S.add(S.heartbeat(), 0.6, 0.5); S.add(S.heartbeat(), 1.7, 0.55); S.add(S.heartbeat(), 2.8, 0.6)
    S.add(S.stinger(), COLD - 0.1, 0.5)
    S.add(S.bell(81), COLD, 0.25); S.add(S.wind(ACT_LEN), 0, 0.3)
    S.train_rhythm(COLD, 14.0, 0.42, 0.15)
    S.play([(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)], 4.4, 0.36, 0.12)
    S.add(S.drone(8.0, 38), 9.0, 0.55); S.add(S.shh(1.8), 10.0, 0.5)
    S.add(S.clack(), 15.0, 0.6); S.add(S.clack(), 15.8, 0.6)
    S.train_rhythm(14.0, ACT_LEN, 0.26, 0.16); S.chase(14.2, 25.0, bpm=158, gain=0.14)
    S.steps(17.0, 23.0, 0.8, 0.45); S.add(S.stinger(), 20.8, 0.45)
    S.silence_music(25.0, 30.0, 0.6); S.add(S.drone(5.0, 36), 25.0, 0.5)
    S.play([(74, 1), (78, 1), (81, 1), (86, 1)], 30.6, 0.3, 0.1)
