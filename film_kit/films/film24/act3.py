"""Act 3 - the Hush stands by the mill watching the lantern go round. The wind stops; the light stops; it turns to the train. A big gust: the lantern flies off over the hill and the Hush goes after it. Full steam to Millbrook."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gloamrun_engine as E
from gloamrun_engine import rook, hush, train, keyframes, steps_at, seg, ease, lerp
import mill
ACT_LEN = 34.0
SHOW = ("far", "rail")
_town = {}
T_STILL, T_GUST, T_FLY, T_GO = 4.2, 10.4, 11.4, 12.6
MX, MB, MS = 640, E.RAIL - 40, 1.0
LINES = [
    (0.6, 2.8, "Good. Keep turning, old mill."),
    (4.4, 6.4, "...Oh no. The wind stopped."),
    (7.4, 9.6, "The light stopped. It's turning to us!"),
    (11.0, 12.6, "The wind! Look, it flies!"),
    (13.0, 15.0, "Now. Full steam!"),
    (17.2, 19.4, "It's going after the lantern!"),
    (22.0, 24.2, "Lights ahead! Millbrook!"),
    (28.0, 31.6, "Thank you, old mill. And you, wind."),
]
BLINKS = E.auto_blinks(ACT_LEN, seed=243)
def speed(t): return 1600 * ease(seg(t, T_GO, T_GO + 3.0)) - 900 * ease(seg(t, 26.0, 32.0))
_c = {}
def scroll(t):
    k = round(t * 24)
    if k not in _c:
        s = 0.0; dt = 1 / 48
        for i in range(int(t / dt)): s += speed(i * dt) * dt
        _c[k] = s
    return _c[k]
_a = {}
def ang(t):
    """sail angle: slow turn, stops when the wind stops, then a big gust spins it fast"""
    k = round(t * 48)
    if k not in _a:
        a = 1.4; dt = 1 / 48
        for i in range(k):
            tt = i * dt; w = 0.7 * (1 - ease(seg(tt, T_STILL - 1.0, T_STILL + 0.8))) + 3.5 * ease(seg(tt, T_GUST, T_GUST + 0.8))
            a += w * dt
        _a[k] = a
    return _a[k]
def mx(t): return MX - scroll(t)
def lamp(t): return ease(seg(t, T_GO - 0.4, T_GO + 0.4))
def town_on(t): return t > 20.0
def dark_edge(t): return None if town_on(t) else E.W + 10
def train_state(t): return train(x=2050, cars=2, lamp=lamp(t), smoke=ease(seg(t, T_GO, T_GO + 1)), dark=0.3 * (1 - ease(seg(t, T_GO, T_GO + 1))))
def rook_state(t):
    pose = steps_at(t, [(0, "shh"), (4.2, "flinch"), (7.2, "pull"), (10.8, "point"), (12.8, "spread"), (15.2, "ahead"), (17.0, "point"),
                        (21.8, "point"), (25.0, "celebrate"), (27.6, "idle"), (28.0, "wave"), (32.0, "idle")])
    face = -1 if t < 12.8 or 17.0 <= t < 21.0 or 28.0 <= t < 32.0 else 1
    return rook(x=1190, y=E.RAIL - 160, face=face, pose=pose, look={"ahead": 0.6, "point": 0.5}.get(pose, 0.0),
                eye=0.35 if t < 4.2 else (1.6 if t < T_GO else 1.0), flap=0.7 if pose in ("spread", "celebrate", "wave") else 0.0,
                lean=0.06 * math.sin(t * 9) if T_GO < t < 26 else 0.0, blink=E.blink_at(t, BLINKS))
def fly_pos(t):
    """where the lantern is after it flies off the sail (up and away to the left, over the hill)"""
    k = ease(seg(t, T_FLY, T_FLY + 9.0)); x0, y0 = mill.tip(mx(T_FLY), MB, MS, ang(T_FLY), 0)
    return lerp(x0, -80, k) - scroll(t) * 0.02, lerp(y0, 300, k) - 160 * math.sin(k * math.pi)
def hush_state(t):
    turn = ease(seg(t, T_STILL + 1.0, T_STILL + 4.0)) * (1 - ease(seg(t, T_FLY, T_FLY + 1.5)))
    if t < T_FLY:
        x, y, sc, near = keyframes(t, [(0, 900, 420, 1.35, 0.8), (T_STILL, 860, 430, 1.3, 0.75), (T_FLY, 1000, 380, 1.5, 0.9)])
    else:
        fx, fy = fly_pos(t); k = ease(seg(t, T_FLY, T_FLY + 6))
        x, y, sc, near = lerp(1000, max(160, fx + 200), k), lerp(380, 520, k), lerp(1.5, 0.7, k), lerp(0.9, 0.35, k)
    return hush(x=x, y=y, sc=sc, near=near, eye=1.3 + 0.3 * turn, hand="point" if 7.6 < t < T_FLY else "shh",
                lean=0.06 * math.sin(t * 0.9) - 0.1 * (1 - turn) + 0.1 * turn)
def draw_back(frame, t, ctx):
    mill.far_mills(frame, scroll(t), t * 0.5)
    if t > 19.0:   # Millbrook slides in from the right with its warm windows
        if "s" not in _town: _town["s"] = E.build_town(True)
        lay = E.Image.new("RGBA", (E.W, E.H), (0, 0, 0, 0)); E.scroll_paste(lay, _town["s"], -E.W + (scroll(t) - scroll(19.0)) * 0.45)
        frame.alpha_composite(lay)
    on = t < T_FLY
    mill.mill(frame, mx(t), MB, MS, ang=ang(t), lantern=1.0 if on else 0.0)
    if not on:
        x, y = fly_pos(t); mill.lantern_at(frame, x, y, 1.0 - 0.5 * ease(seg(t, 18.0, 24.0)), 1.0 - 0.4 * ease(seg(t, T_FLY, 20)))
def draw_front(frame, t, ctx):
    if t > 21.0:
        a = ease(seg(t, 21.0, 25.0))
        for k in range(5): E.add_glow(frame, 2100 + k * 120, 820 - 20 * k, 160, E.WINDOW, 0.25 * a)
def blackout(t): return 0.25 * (1 - ease(seg(t, T_STILL, T_GO)))
def shake(t): return 0.15 if T_GO < t < 26 else (0.08 if T_GUST < t < T_GO else 0.0)
def camera(t):
    return keyframes(t, [(0, 1000, 640, 1.0), (2.8, 1190, 760, 1.35), (4.4, 800, 600, 1.0), (7.2, 1000, 600, 1.05), (9.6, 1190, 760, 1.4),
                         (10.6, 800, 600, 1.0), (13.0, 1190, 780, 1.45), (15.2, 1280, 720, 1.0), (17.2, 700, 600, 1.0), (22.0, 1800, 640, 1.15),
                         (25.0, 1190, 760, 1.35), (28.0, 1190, 780, 1.4), (34, 1280, 680, 1.05)])
def score(S):
    S.add(S.wind(T_STILL, 1.0), 0, 0.35); S.add(S.drone(12.0, 36), 0, 0.5)
    for i in range(6): S.add(S.pluck(79 + (i % 3) * 3), 0.3 + i * 0.6, 0.15)
    S.silence_music(T_STILL, T_GUST, 0.8); S.add(S.stinger(), 7.4, 0.5)
    for k in range(4): S.add(S.heartbeat(), 6.0 + k * 1.0, 0.6)
    S.add(S.wind(4.0, 2.5), T_GUST - 0.3, 0.6); S.add(S.bell(88, 1.4), T_FLY, 0.25)
    S.add(S.whistle(1.4), T_GO, 0.8); S.train_rhythm(T_GO, ACT_LEN, 0.28, 0.16); S.chase(T_GO + 0.2, 22.0, bpm=162, gain=0.13)
    S.play([(74, 1), (78, 1), (81, 1), (86, 2)], 22.2, 0.42, 0.13)
    S.play([(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)], 25.2, 0.34, 0.12)
    S.add(S.bell(81), 28.2, 0.25); S.add(S.bell(86), 28.6, 0.2)
