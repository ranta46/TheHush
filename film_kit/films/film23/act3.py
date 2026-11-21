"""Act 3 - the Hush walks away up the quarry line, eating the green lamps one by one. The lever slips: the home signal turns on. It turns. Full steam on the home line; it is too far up the hill. Ashby."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gloamrun_engine as E
from gloamrun_engine import rook, hush, train, keyframes, steps_at, seg, ease, lerp
import sig
ACT_LEN = 34.0
SHOW = ("far", "town", "rail")
T_SLIP, T_GO = 4.4, 11.0
LINES = [
    (0.6, 2.8, "Slowly now. Points to the home line."),
    (4.2, 6.0, "...Oh no. The lever!"),
    (7.2, 9.4, "Our signal is on. It's turning!"),
    (11.0, 12.8, "Now. Full steam!"),
    (16.6, 18.8, "It's too far up the quarry line!"),
    (21.0, 23.2, "Lights ahead! Ashby!"),
    (25.0, 27.2, "Everyone, we made it."),
    (29.4, 32.6, "Never trust a green light at night."),
]
BLINKS = E.auto_blinks(ACT_LEN, seed=233)
def speed(t): return 1600 * ease(seg(t, T_GO, T_GO + 3.0)) - 900 * ease(seg(t, 26.0, 32.0))
_c = {}
def scroll(t):
    k = round(t * 24)
    if k not in _c:
        s = 0.0; dt = 1 / 48
        for i in range(int(t / dt)): s += speed(i * dt) * dt
        _c[k] = s
    return _c[k]
def lamp(t): return ease(seg(t, T_GO - 0.4, T_GO + 0.4))
def town_on(t): return t > 19.0
def dark_edge(t): return None if town_on(t) else E.W + 10
def train_state(t): return train(x=2050, cars=2, lamp=lamp(t), smoke=ease(seg(t, T_GO, T_GO + 1)), dark=0.3 * (1 - ease(seg(t, T_GO, T_GO + 1))))
def rook_state(t):
    pose = steps_at(t, [(0, "pull"), (4.0, "flinch"), (7.0, "point"), (10.8, "spread"), (13.0, "ahead"), (16.4, "point"),
                        (20.8, "point"), (24.8, "celebrate"), (27.6, "idle"), (29.2, "wave"), (33.0, "idle")])
    face = -1 if 7.0 <= t < 10.8 or 16.4 <= t < 20.8 or 29.2 <= t < 33.0 else 1
    return rook(x=1190, y=E.RAIL - 160, face=face, pose=pose, look={"ahead": 0.6, "point": 0.5, "lean": 0.4}.get(pose, 0.0),
                eye=0.35 if t < 4.0 else (1.6 if t < T_GO else 1.0), flap=0.7 if pose in ("spread", "celebrate", "wave") else 0.0,
                lean=0.06 * math.sin(t * 9) if T_GO < t < 26 else 0.0, blink=E.blink_at(t, BLINKS))
def hush_state(t):
    x, y, sc, near = keyframes(t, [(0, 1000, 380, 1.5, 0.85), (6.0, 520, 470, 0.95, 0.55), (11.0, 500, 470, 0.95, 0.6), (20.0, 340, 420, 0.65, 0.35), (34, 300, 420, 0.6, 0.3)])
    turn = ease(seg(t, T_SLIP + 1.5, T_SLIP + 4.0))
    return hush(x=max(220, x - scroll(t) * 0.04), y=y, sc=sc, near=near, eye=1.3 + 0.3 * turn, hand="point" if 8.0 < t < 11.0 else "shh",
                lean=0.06 * math.sin(t * 0.9) - 0.1 * (1 - turn) + 0.12 * turn * (1 - ease(seg(t, 18, 22))))
def draw_back(frame, t, ctx):
    eaten = sig.N * ease(seg(t, 0.0, 5.5)) * 0.6 + sig.N * 0.4 * ease(seg(t, T_GO, 22.0))
    sig.far_line(frame, t, on=sig.N, eaten=eaten, ox=-scroll(t) * 0.04)
def draw_scene(frame, t, ctx):
    g = ease(seg(t, T_SLIP, T_SLIP + 0.3))
    sig.post(frame, 2420 - scroll(t), E.RAIL, 1.0, red=0.0, green=g)
def draw_front(frame, t, ctx):
    if t > 20.0:
        a = ease(seg(t, 20.0, 24.0))
        for k in range(5): E.add_glow(frame, 2100 + k * 120, 820 - 20 * k, 160, E.WINDOW, 0.25 * a)
def blackout(t): return 0.25 * (1 - ease(seg(t, T_SLIP, T_GO)))
def shake(t): return 0.15 if T_GO < t < 26 else 0.0
def camera(t):
    return keyframes(t, [(0, 1190, 760, 1.35), (2.8, 900, 640, 1.0), (4.2, 1900, 760, 1.3), (6.0, 1190, 760, 1.35), (7.2, 800, 640, 1.0),
                         (11.0, 1190, 780, 1.45), (13.0, 1280, 720, 1.0), (16.6, 700, 600, 1.0), (21.0, 1800, 640, 1.15), (25.0, 1190, 760, 1.35),
                         (29.2, 1190, 780, 1.4), (34, 1280, 680, 1.05)])
def score(S):
    S.add(S.wind(ACT_LEN, 0.7), 0, 0.3); S.add(S.drone(11.0, 36), 0, 0.5); S.steps(0.0, 6.0, 1.2, 0.4)
    S.add(S.clack(), T_SLIP, 0.9); S.add(S.thump(), T_SLIP, 0.6); S.add(S.bell(86, 1.2), T_SLIP + 0.1, 0.3)
    S.add(S.stinger(), T_SLIP + 2.6, 0.5)
    for k in range(4): S.add(S.heartbeat(), 6.0 + k * 1.1, 0.6)
    S.add(S.whistle(1.4), T_GO, 0.8); S.train_rhythm(T_GO, ACT_LEN, 0.28, 0.16); S.chase(T_GO + 0.2, 21.0, bpm=162, gain=0.13)
    S.play([(74, 1), (78, 1), (81, 1), (86, 2)], 21.2, 0.42, 0.13)
    S.play([(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)], 25.2, 0.34, 0.12)
    S.add(S.bell(81), 29.6, 0.25); S.add(S.bell(86), 30.0, 0.2)
