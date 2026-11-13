"""Act 3 - the fireflies all rise at once and fly off over the hill. The Hush turns and follows the big light. Lamp on, full steam to Glowmere."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gloamrun_engine as E
from gloamrun_engine import rook, hush, train, keyframes, steps_at, seg, ease, lerp
import ff
ACT_LEN = 34.0
SHOW = ("far", "town", "rail")
T_RISE, T_GO = 1.0, 15.0
LINES = [
    (0.6, 2.6, "...What's that?"),
    (3.6, 5.8, "They're all going up!"),
    (7.6, 9.8, "Look. It's following them!"),
    (11.4, 13.6, "The biggest light in the wood..."),
    (15.0, 16.8, "Now. Full steam!"),
    (21.0, 23.2, "Lights ahead! Glowmere!"),
    (25.0, 27.2, "Everyone, we made it."),
    (29.4, 32.6, "Thank you, little lights."),
]
BLINKS = E.auto_blinks(ACT_LEN, seed=153)
def speed(t): return 1500 * ease(seg(t, T_GO, T_GO + 3.0)) - 800 * ease(seg(t, 26.0, 32.0))
_c = {}
def scroll(t):
    k = round(t * 24)
    if k not in _c:
        s = 0.0; dt = 1 / 48
        for i in range(int(t / dt)): s += speed(i * dt) * dt
        _c[k] = s
    return _c[k]
def lamp(t): return 0.75 + 0.25 * ease(seg(t, T_GO - 0.6, T_GO + 0.4))
def town_on(t): return t > 19.0
def dark_edge(t): return None if town_on(t) else E.W + 10
def train_state(t): return train(x=2050, cars=2, lamp=lamp(t), smoke=ease(seg(t, T_GO, T_GO + 1)), dark=0.3 * (1 - ease(seg(t, T_GO, T_GO + 1))))
def rook_state(t):
    pose = steps_at(t, [(0, "flinch"), (3.4, "point"), (7.4, "lean"), (11.2, "idle"), (14.8, "spread"), (17.0, "ahead"), (20.8, "point"),
                        (24.8, "celebrate"), (27.6, "idle"), (29.2, "wave"), (33.0, "idle")])
    face = -1 if 3.4 <= t < 11.2 or 29.2 <= t < 33.0 else 1
    return rook(x=1190, y=E.RAIL - 160, face=face, pose=pose, look={"ahead": 0.6, "point": 0.6 if t < 12 else 0.4, "lean": 0.4}.get(pose, 0.0),
                eye=0.35 if t < T_GO - 1 else 1.0, flap=0.7 if pose in ("spread", "celebrate", "wave") else 0.0,
                lean=0.06 * math.sin(t * 9) if T_GO < t < 26 else 0.0, blink=E.blink_at(t, BLINKS))
def swarm(t): return ease(seg(t, T_RISE, 9.0))
def swarm_x(t): return 700 - 500 * ease(seg(t, 6.0, 16.0)) - scroll(t) * 0.8
def hush_state(t):
    x, y, sc, near = keyframes(t, [(0, 1300, 300, 1.8, 1.0), (5.0, 1200, 300, 1.75, 0.95), (9.0, 800, 340, 1.5, 0.8), (14.0, 450, 440, 1.15, 0.6), (22.0, 250, 560, 0.8, 0.4), (34, 200, 600, 0.7, 0.3)])
    x -= scroll(t) * 0.5
    return hush(x=max(x, 140), y=y, sc=sc, near=near, eye=1.3, hand="shh", lean=0.06 * math.sin(t * 0.9) - 0.08 * ease(seg(t, 5, 9)))
def draw_back(frame, t, ctx):
    if t < 20: ff.trees(frame, 300 - scroll(t) * 0.6)
def draw_scene(frame, t, ctx):
    s = swarm(t); sx = swarm_x(t)
    ff.draw(frame, t, -scroll(t) * 0.8, 1.0 - 0.5 * ease(seg(t, 18, 22)), rise=s, rise_x=sx)
    if s > 0.5: E.add_glow(frame, sx, 80, 800, ff.COL, 0.5 * s)
def draw_front(frame, t, ctx):
    if t > 20.0:
        a = ease(seg(t, 20.0, 24.0))
        for k in range(5): E.add_glow(frame, 2100 + k * 120, 820 - 20 * k, 160, E.WINDOW, 0.25 * a)
def blackout(t): return 0.3 * (1 - ease(seg(t, 13.0, 16.0)))
def shake(t): return 0.15 if t > T_GO else 0.0
def camera(t):
    return keyframes(t, [(0, 1190, 760, 1.4), (2.6, 1100, 560, 1.0), (5.8, 900, 480, 1.05), (9.8, 900, 560, 1.0), (11.4, 1190, 760, 1.35),
                         (15.0, 1190, 780, 1.45), (17.0, 1280, 720, 1.0), (21.0, 1800, 640, 1.15), (25.0, 1190, 760, 1.35), (29.2, 1190, 780, 1.4), (34, 1280, 680, 1.05)])
def score(S):
    S.add(S.wind(ACT_LEN, 0.7), 0, 0.3); S.add(S.drone(14.0, 36), 0, 0.5)
    S.play([(81, 1), (86, 1), (88, 1), (93, 2)], 1.6, 0.45, 0.09); S.play([(86, 1), (88, 1), (93, 1)], 5.0, 0.45, 0.08)
    S.steps(6.0, 14.0, 1.1, 0.5); S.add(S.shh(2.0), 9.0, 0.35)
    S.add(S.whistle(1.4), T_GO, 0.8); S.train_rhythm(T_GO, ACT_LEN, 0.28, 0.16); S.chase(T_GO + 0.2, 21.0, bpm=160, gain=0.13)
    S.play([(74, 1), (78, 1), (81, 1), (86, 2)], 21.2, 0.42, 0.13)
    S.play([(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)], 25.2, 0.34, 0.12)
    S.add(S.bell(81), 29.6, 0.25); S.add(S.bell(86), 30.0, 0.2)
