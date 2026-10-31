"""Act 4 - the Long Back. The sky whale comes down; the train rides up on its back. The Hush can't fly. Dawn; Rook flies."""
import math
import gloamrun_engine as E
from gloamrun_engine import rook, hush, train, keyframes, steps_at, seg, ease, lerp
ACT_LEN = 34.0
SHOW = ("far", "rail")
LIFT = 380
LINES = [
    (1.0, 3.0, "...Look up."),
    (4.6, 6.8, "Old friend! Everyone, hold the bar!"),
    (11.0, 13.0, "Up we go!"),
    (15.4, 17.6, "It can't fly. It can only watch."),
    (20.6, 22.8, "Look. The sky is getting light."),
    (24.6, 26.6, "Light means wings!"),
    (29.0, 31.8, "Next stop: wherever the light is."),
]
BLINKS = E.auto_blinks(ACT_LEN, seed=104)
def lift(t): return LIFT * ease(seg(t, 10.0, 21.0))
def scroll(t):
    global SHOW
    SHOW = ("far", "rail") if t < 10.5 else ("far",)
    return 0.0
def dawn(t): return ease(seg(t, 17.0, 27.0))
def whale_xy(t):
    x = lerp(4300, 1420, ease(seg(t, 1.5, 9.5))); y = E.RAIL + 125 - lift(t) + 10 * math.sin(t * 0.8)
    return x, y
def blackout(t): return 0.44 * (1 - ease(seg(t, 0.0, 6.0)))
def draw_back(frame, t, ctx):
    x, y = whale_xy(t); E.draw_longback(frame, t, x, y, sc=0.85)
def train_state(t):
    _, wy = whale_xy(t); y = E.RAIL if t < 10.0 else min(E.RAIL, wy - 125 + E.RAIL - E.RAIL)
    return train(x=2050, y=y, cars=2, lamp=0.4 + 0.6 * ease(seg(t, 3.0, 5.0)), smoke=0.6)
def rook_state(t):
    ty = train_state(t)["y"]
    pose = steps_at(t, [(0, "lean"), (4.4, "wave"), (7.2, "ahead"), (10.8, "celebrate"), (13.2, "idle"), (15.2, "point"), (18.0, "idle"),
                        (20.4, "ahead"), (24.4, "spread"), (27.0, "celebrate"), (28.8, "wave"), (32.0, "idle")])
    fly = ease(seg(t, 24.8, 27.5))
    face = -1 if 15.2 <= t < 18.0 else 1
    return rook(x=1190 + 60 * fly, y=ty - 160 - 140 * fly + 18 * math.sin(t * 3) * fly, face=face, pose=pose,
                look={"lean": 0.7, "ahead": 0.5}.get(pose, 0.0), eye=1.6 if t < 8 else 1.0,
                flap=1.0 if fly > 0.05 else (0.7 if pose in ("wave", "celebrate") else 0.0), fly=fly, blink=E.blink_at(t, BLINKS))
def hush_state(t):
    x, y, sc, near = keyframes(t, [(0, 760, 480, 1.25, 0.7), (6.0, 820, 470, 1.35, 0.8), (12.0, 760, 480, 1.3, 0.8), (18.0, 660, 480, 1.2, 0.6), (34, 560, 480, 1.1, 0.4)])
    return hush(x=x, y=y + 1.25 * lift(t), sc=sc, near=near, eye=1.0 + 0.6 * near, hand="shh", sink=700 * ease(seg(t, 21.0, 31.0)), lean=0.04 * math.sin(t))
def draw_scene(frame, t, ctx):
    if False:   # it reaches up for the train once, and cannot follow
        hs = ctx["hush"]; sh = (hs["x"] + 260 * hs["sc"], hs["y"] + 260 * hs["sc"])
        up = math.sin(math.pi * seg(t, 12.0, 16.5)); ty = ctx["train"]["y"]
        E.hush_arm(frame, t, sh, (lerp(sh[0], 1100, up), lerp(sh[1], ty + 260, up)), sc=0.9)
def shake(t): return 0.25 if 9.5 < t < 11.0 else 0.0
def camera(t):
    return keyframes(t, [(0, 1600, 520, 1.1), (3.0, 1280, 720, 1.0), (6.0, 1300, 760, 1.25), (10.0, 1280, 720, 1.0), (14.0, 1200, 640, 1.15),
                         (18.0, 1250, 560, 1.2), (22.0, 1250, 560, 1.3), (25.0, 1220, 500, 1.4), (28.5, 1250, 520, 1.3), (34, 1280, 600, 1.1)])
def score(S):
    S.add(S.wind(ACT_LEN, 0.7), 0, 0.3); S.add(S.whale(3.4), 0.6, 0.85); S.add(S.whale(3.0), 8.5, 0.8)
    S.add(S.drone(8.0, 38), 9.0, 0.4); S.add(S.whistle(1.6), 10.6, 0.7)
    S.play([(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)], 11.0, 0.32, 0.12, transpose=0)
    S.add(S.stinger(), 12.2, 0.3); S.add(S.shh(2.0), 15.6, 0.35)
    S.play([(74, 1), (78, 1), (81, 1), (86, 2)], 20.6, 0.45, 0.13)
    S.play([(74, 1), (78, 1), (81, 1), (86, 1), (85, 1), (83, 1), (81, 2)], 25.0, 0.34, 0.13)
    S.add(S.whale(3.6), 27.5, 0.7)
    S.play([(74, 1), (78, 1), (81, 1), (86, 3)], 29.2, 0.5, 0.14)
