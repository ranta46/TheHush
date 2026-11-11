"""Act 3 - out of the cloud. The Hush stays, searching the steam. The train creeps away dark, then Brightwater is still lit."""
import math
import gloamrun_engine as E
from gloamrun_engine import rook, hush, train, keyframes, steps_at, seg, ease, lerp
ACT_LEN = 32.0
SHOW = ("far", "town", "rail")
LINES = [
    (0.6, 2.8, "...We're out. Easy... easy..."),
    (5.0, 7.2, "Look. It's still in the steam."),
    (9.4, 11.4, "It's looking for us in there."),
    (14.0, 15.8, "Now. Full steam!"),
    (19.6, 21.8, "Lights ahead! Brightwater!"),
    (23.4, 25.6, "Still lit. Everyone, we made it."),
    (28.0, 31.2, "Thank you, old tower."),
]
BLINKS = E.auto_blinks(ACT_LEN, seed=133)
def speed(t): return 160 + 300 * ease(seg(t, 4.0, 9.0)) + 1100 * ease(seg(t, 14.0, 17.0)) - 700 * ease(seg(t, 24.0, 30.0))
_c = {}
def scroll(t):
    k = round(t * 24)
    if k not in _c:
        s = 0.0; dt = 1 / 48
        for i in range(int(t / dt)): s += speed(i * dt) * dt
        _c[k] = s
    return _c[k]
def lamp(t): return ease(seg(t, 13.6, 14.6))
def town_on(t): return t > 17.5
def dark_edge(t): return None if town_on(t) else E.W + 10
def train_state(t): return train(x=2050, cars=2, lamp=lamp(t), smoke=lamp(t), dark=0.6 * (1 - lamp(t)))
def rook_state(t):
    pose = steps_at(t, [(0, "shh"), (4.8, "point"), (9.2, "lean"), (12.0, "idle"), (13.8, "spread"), (16.4, "ahead"), (19.4, "point"),
                        (23.2, "celebrate"), (26.0, "idle"), (27.8, "wave"), (31.4, "idle")])
    face = -1 if 4.8 <= t < 12.0 or 27.8 <= t < 31.4 else 1
    eye = 0.35 if t < 13.8 else 1.0
    return rook(x=1190, y=E.RAIL - 160, face=face, pose=pose, look={"ahead": 0.6, "point": 0.4, "lean": 0.3}.get(pose, 0.0), eye=eye,
                flap=0.7 if pose in ("spread", "celebrate", "wave") else 0.0, lean=0.06 * math.sin(t * 9) if t > 15 else 0.0, blink=E.blink_at(t, BLINKS))
def cloud_x(t): return 1350 - scroll(t) * 0.9
def hush_state(t):
    x = cloud_x(t) - 100 + 120 * math.sin(t * 0.5)
    y, sc, near = 330 + 30 * math.sin(t * 0.7), 1.6, 0.7
    if t > 14: sc = lerp(1.6, 0.9, ease(seg(t, 14, 22))); y = lerp(330, 520, ease(seg(t, 14, 22)))
    x = max(x, 300 + 40 * math.sin(t))
    return hush(x=x, y=y, sc=sc, near=near, eye=1.3, hand="shh", lean=0.06 * math.sin(t * 0.9))
def draw_scene(frame, t, ctx):
    cx = cloud_x(t); fade = 1 - ease(seg(t, 8.0, 18.0))   # the Hush eats the light in the cloud; the steam goes grey and thin
    for k in range(12):
        ang = k * 2.4; r = 300 + 150 * (k % 3)
        E.add_glow(frame, cx + math.cos(ang) * r * 1.5 + math.sin(t * 0.5 + k) * 40, 860 + math.sin(ang) * r * 0.5, 420, (205, 212, 222), 0.5 * (0.4 + 0.6 * fade))
def draw_front(frame, t, ctx):
    if t > 18.0:
        a = ease(seg(t, 18.0, 22.0))
        for k in range(5): E.add_glow(frame, 2100 + k * 120, 820 - 20 * k, 160, E.WINDOW, 0.25 * a)
def blackout(t): return 0.4 * (1 - ease(seg(t, 13.0, 15.0)))
def shake(t): return 0.15 if t > 15 else 0.0
def camera(t):
    return keyframes(t, [(0, 1190, 760, 1.4), (3.0, 1280, 720, 1.0), (5.0, 900, 620, 1.15), (9.4, 800, 600, 1.2), (12.0, 1280, 720, 1.0),
                         (14.0, 1190, 780, 1.45), (16.4, 1280, 720, 1.0), (19.6, 1800, 640, 1.15), (23.4, 1190, 760, 1.35), (27.8, 1190, 780, 1.4), (32, 1280, 680, 1.05)])
def score(S):
    S.add(S.wind(ACT_LEN, 0.7), 0, 0.3); S.train_rhythm(0, 14.0, 0.7, 0.08); S.add(S.drone(13.0, 36), 0, 0.5)
    S.add(S.shh(2.0), 6.0, 0.35); S.add(S.shh(1.2), 10.0, 0.3)
    S.add(S.whistle(1.4), 14.0, 0.8); S.train_rhythm(14.0, ACT_LEN, 0.28, 0.16); S.chase(14.2, 19.5, bpm=160, gain=0.13)
    S.play([(74, 1), (78, 1), (81, 1), (86, 2)], 19.8, 0.42, 0.13)
    S.play([(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)], 23.6, 0.34, 0.12)
    S.add(S.bell(81), 28.0, 0.25); S.add(S.bell(86), 28.4, 0.2)
