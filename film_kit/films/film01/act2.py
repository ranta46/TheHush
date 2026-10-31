"""Act 2 - Lantern Hill. The Hush eats the lights of the town; its hand reaches for the train; Rook switches tracks."""
import math
import gloamrun_engine as E
from gloamrun_engine import rook, hush, train, keyframes, steps_at, seg, ease, lerp
ACT_LEN = 30.0
SHOW = ("far", "town", "rail")
T_REACH, T_SWITCH = 9.8, 14.0
LINES = [
    (0.3, 2.3, "There! Lantern Hill!"),
    (4.0, 6.2, "No... it's eating the lights!"),
    (9.6, 11.6, "Its hand! Everyone, heads down!"),
    (12.2, 13.9, "Hold on. Switching tracks!"),
    (15.6, 17.4, "Ha! Missed us!"),
    (20.8, 23.0, "This line goes up the hill."),
    (25.4, 28.0, "Lights going out up there too..."),
]
BLINKS = E.auto_blinks(ACT_LEN, seed=102)
def speed(t): return 1500 + 900 * ease(seg(t, T_SWITCH, T_SWITCH + 0.6)) - 700 * ease(seg(t, 19, 23))
_c = {}
def scroll(t):
    k = round(t * 24)
    if k not in _c:
        s = 0.0; dt = 1 / 48
        for i in range(int(t / dt)): s += speed(i * dt) * dt
        _c[k] = s
    return _c[k]
def dark_edge(t):
    if t < 2.0: return None
    return lerp(-10, E.W + 10, ease(seg(t, 2.0, 22.0)))
def train_state(t): return train(x=2050, cars=2, lamp=1.0, smoke=1.0)
def rook_state(t):
    pose = steps_at(t, [(0, "point"), (2.4, "ahead"), (3.8, "flinch"), (6.4, "ahead"), (9.4, "down"), (12.0, "pull"), (14.4, "celebrate"),
                        (17.6, "ahead"), (20.6, "point"), (23.2, "idle"), (25.2, "sad")])
    face = -1 if (3.8 <= t < 9.4 or 25.2 <= t) else 1
    eye = 1.6 if 8.0 < t < 15.0 else 1.0
    return rook(x=1190, y=E.RAIL - 160, face=face, pose=pose, look={"ahead": 0.6, "point": 0.5}.get(pose, 0.0), eye=eye,
                flap=0.7 if pose == "celebrate" else 0.0, lean=0.07 * math.sin(t * 9), blink=E.blink_at(t, BLINKS))
def hush_state(t):
    x, y, sc, near = keyframes(t, [(0, 600, 480, 1.1, 0.5), (6.0, 800, 400, 1.35, 0.9), (10.0, 860, 380, 1.5, 1.0), (14.2, 860, 380, 1.5, 1.0),
                                   (18.0, 380, 560, 0.85, 0.3), (24.0, 520, 500, 1.0, 0.4), (30.0, 700, 450, 1.2, 0.7)])
    return hush(x=x, y=y, sc=sc, near=near, eye=1.0 + 0.6 * near, hand="none" if T_REACH - 0.4 < t < T_SWITCH + 2.4 else "shh", lean=0.05 * math.sin(t * 1.3))
def draw_scene(frame, t, ctx):
    if T_REACH - 0.4 < t < T_SWITCH + 2.4:
        hs = ctx["hush"]; sh = (hs["x"] + 260 * hs["sc"], hs["y"] + 260 * hs["sc"])
        reach = ease(seg(t, T_REACH - 0.4, T_SWITCH - 0.2))
        car = (2050 - 1360, E.RAIL - 200)
        if t < T_SWITCH: tip = (lerp(sh[0], car[0], reach), lerp(sh[1], car[1], reach))
        else:   # the train jumps to the other line: the hand closes on empty air, then pulls back
            back = ease(seg(t, T_SWITCH + 0.6, T_SWITCH + 2.4)); tip = (lerp(car[0] - 120, sh[0], back), lerp(car[1] + 120, sh[1], back))
        E.hush_arm(frame, t, sh, tip, sc=0.9)
    if T_SWITCH - 0.05 < t < T_SWITCH + 0.4:
        E.add_glow(frame, 1500, E.RAIL - 10, 220, (255, 200, 120), 1 - seg(t, T_SWITCH, T_SWITCH + 0.4))
def shake(t):
    if T_SWITCH < t < T_SWITCH + 0.6: return 1.0
    return 0.2
def camera(t):
    return keyframes(t, [(0, 1500, 700, 1.15), (3.8, 1100, 640, 1.05), (7.0, 1280, 720, 1.0), (9.6, 1000, 600, 1.15), (12.0, 1190, 780, 1.45),
                         (14.2, 1280, 720, 1.05), (15.6, 1190, 800, 1.5), (18.0, 1280, 720, 1.0), (21.0, 1500, 680, 1.15), (25.4, 900, 600, 1.15), (30, 1280, 720, 1.0)])
def score(S):
    S.add(S.wind(ACT_LEN), 0, 0.3); S.train_rhythm(0, ACT_LEN, 0.24, 0.15)
    S.chase(0, 9.4, bpm=160, gain=0.14)
    S.add(S.drone(8.0, 36), 4.0, 0.6)
    S.steps(4.0, 14.0, 0.75, 0.5); S.add(S.stinger(), T_REACH, 0.6)
    S.silence_music(10.4, 13.9, 0.8); S.add(S.heartbeat(), 11.0, 0.5); S.add(S.heartbeat(), 12.0, 0.5); S.add(S.heartbeat(), 13.0, 0.55)
    S.add(S.clack(), T_SWITCH, 1.0); S.add(S.clack(), T_SWITCH + 0.12, 0.9); S.add(S.stinger(), T_SWITCH + 0.05, 0.35); S.add(S.whistle(1.2), T_SWITCH + 0.2, 0.8)
    S.chase(T_SWITCH + 0.3, 20.0, bpm=168, gain=0.15)
    S.play([(74, 1), (78, 1), (81, 1)], 15.8, 0.3, 0.1)
    S.add(S.drone(7.0, 38), 23.0, 0.5); S.add(S.shh(1.6), 25.6, 0.4)
