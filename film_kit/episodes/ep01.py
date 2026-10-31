"""GLOAMRUN Episode 1 — "The Night Has a Face"
Setup in one line, then the chase. Thrill 70 / surprise 20 / fear 10.
Beats: 0s the Hush's eyes open behind Kesmoor (hook) -> lights go out -> train runs -> the Hush gets close / far / close
-> it grabs the back car -> Rook cuts it loose (surprise) -> total dark, "Don't move" (fear) -> Rook's lamp + whistle, escape.
"""
import math
import gloamrun_engine as E
from gloamrun_engine import rook, hush, train, keyframes, steps_at, seg, ease, clamp, lerp

EP_NO = 1
EP_TITLE = "The Night Has a Face"
SYNOPSIS = "The Hush wakes up behind the town of Kesmoor. Rook, the conductor of the last train, must get his train out before every light goes out."
DUR = 29.5 + E.TITLE_LEN
POSTER_T = 11.0
BG = "night"

LINES = [
    (0.3, 2.4, "Last train! Get on, now!"),
    (2.8, 5.0, "Look behind you. That is the Hush."),
    (6.0, 7.6, "Hold the bar!"),
    (11.0, 12.8, "It's right behind us!"),
    (13.6, 15.6, "It has the back car! Cutting it loose!"),
    (19.4, 21.6, "...Don't move. Don't make a sound."),
    (24.2, 26.6, "NOW! Full steam!"),
    (27.2, 29.3, "It will be back. It always comes back."),
]

T_GO = 6.0          # train starts
T_GRAB = 13.2       # the hand closes on the back car
T_CUT = 14.6        # Rook pulls the pin
T_DARK0, T_DARK1 = 18.2, 23.8   # lights out
BLINKS = E.auto_blinks(DUR - E.TITLE_LEN, seed=EP_NO)

def speed(t):
    """px per second of world scroll"""
    if t < T_GO: return 0.0
    if t < T_DARK0: return 900 * ease(seg(t, T_GO, T_GO + 2.5)) + 500 * ease(seg(t, 9, 11))
    if t < T_DARK1: return lerp(1400, 260, ease(seg(t, T_DARK0, T_DARK0 + 1.2)))
    return 260 + 1600 * ease(seg(t, T_DARK1, T_DARK1 + 1.2))

_cache = {}
def scroll(t):
    k = round(t * 24)
    if k in _cache: return _cache[k]
    s = 0.0; dt = 1 / 48
    for i in range(int(t / dt)): s += speed(i * dt) * dt
    _cache[k] = s; return s

def dark_edge(t):
    """lights of Kesmoor go out from left to right as the Hush rises (and stay out)"""
    if t < 2.4: return None
    return lerp(-10, E.W + 10, ease(seg(t, 2.4, 6.5)))

def train_state(t):
    cars = 2 if t < T_CUT else 1
    return train(x=2050, cars=cars, lamp=0.0 if T_DARK0 + 0.6 < t < T_DARK1 else 1.0, smoke=1.0 if t >= T_GO else 0.4)

def rook_state(t):
    x, y = 1190, E.RAIL - 160
    pose = steps_at(t, [(0, "wave"), (2.6, "point"), (5.2, "idle"), (6.0, "spread"), (8.0, "ahead"), (11.0, "flinch"),
                        (13.4, "pull"), (15.8, "sad"), (17.0, "ahead"), (19.2, "shh"), (24.0, "spread"), (26.8, "idle"), (27.4, "down")])
    face = -1 if (2.6 <= t < 6.0 or 10.8 <= t < 16.0 or 26.8 <= t) else 1
    look = {"ahead": 0.6, "point": 0.4}.get(pose, 0.0)
    eye = 1.0
    if T_DARK0 < t < T_DARK1: eye = 1.6 if t > 23.0 else 0.35
    flap = 0.6 if pose in ("wave", "spread") else 0.0
    lean = 0.08 * math.sin(t * 9) if 8 < t < 18 else 0.0
    if 23.0 < t < 23.6: eye = 1.6
    return rook(x=x, y=y, face=face, pose=pose, look=look, eye=eye, flap=flap, lean=lean, blink=E.blink_at(t, BLINKS))

def hush_state(t):
    # rises behind the town, then chases: close / far / close / in the dark / falls behind
    x, y, sc, near = keyframes(t, [
        (0.0, 880, 760, 0.9, 0.2), (2.6, 880, 520, 1.0, 0.3), (5.5, 900, 420, 1.05, 0.4),
        (8.5, 520, 470, 1.0, 0.3),          # train pulls away
        (11.0, 820, 380, 1.35, 0.9),        # surge: right behind us
        (13.0, 760, 380, 1.45, 1.0),
        (16.5, 420, 470, 1.0, 0.4),         # we lost it a little
        (18.5, 900, 330, 1.6, 1.0),         # it is on top of us in the dark
        (23.8, 980, 320, 1.65, 1.0),
        (26.0, 300, 560, 0.85, 0.3), (29.5, 120, 640, 0.75, 0.2)])
    eye = 1.0 + 0.6 * near
    if T_DARK0 < t < T_DARK1: eye = 1.5
    return hush(x=x, y=y, sc=sc, near=near, eye=eye, hand="shh", lean=0.05 * math.sin(t * 1.3))

def draw_scene(frame, t, ctx):
    ts = ctx["train"]
    # the arm reaches for the back car and takes it
    if 11.8 < t < 17.0:
        hs = ctx["hush"]; sh = (hs["x"] + 260 * hs["sc"], hs["y"] + 260 * hs["sc"])
        car_x = ts["x"] - 860 - 500 if t < T_CUT else ts["x"] - 1360 - (t - T_CUT) * 900
        car_y = E.RAIL - 40 * 0 - (0 if t < T_CUT else 0) + (0 if t < T_CUT else (t - T_CUT) ** 2 * 260)
        reach = ease(seg(t, 11.8, T_GRAB))
        tip = (lerp(sh[0], car_x, reach), lerp(sh[1], car_y - 160, reach))
        if t >= T_CUT:   # the cut car falls back and away with the hand
            lay = E.Image.new("RGBA", (E.W, E.H), (0, 0, 0, 0)); E.draw_car(E.ImageDraw.Draw(lay), car_x, car_y, t * 6)
            E.paste(frame, lay, 0, 0); tip = (car_x, car_y - 160)
        E.hush_arm(frame, t, sh, tip, sc=0.9)
    if T_CUT - 0.05 < t < T_CUT + 0.3:   # spark when the pin comes out
        E.add_glow(frame, ts["x"] - 1110, E.RAIL - 90, 140, (255, 200, 120), 1 - seg(t, T_CUT, T_CUT + 0.3))

def blackout(t):
    if T_DARK0 < t < T_DARK1: return 0.82 * ease(seg(t, T_DARK0, T_DARK0 + 0.5)) * (1 - ease(seg(t, T_DARK1 - 0.4, T_DARK1)))
    return 0.0

def draw_overlay(out, t, orient):
    """in the dark only two things shine: the Hush's eyes and Rook's red lamp (redrawn over the black)"""
    b = blackout(t)
    if b < 0.05: return
    ow, oh = out.size
    cx, cy, z = (camera_v(t) if orient == "v" else camera(t))
    zz = max(1.0, z * 0.85) if orient == "v" else z
    vh = E.H / zz; vw = vh * 9 / 16 if orient == "v" else E.W / z
    cx = clamp(cx, vw / 2, E.W - vw / 2); cy = clamp(cy, vh / 2, E.H - vh / 2)
    to = lambda X, Y: ((X - (cx - vw / 2)) / vw * ow, (Y - (cy - vh / 2)) / vh * oh)
    s = ow / vw
    hs = hush_state(t)
    for sd in (-1, 1):
        px, py = to(hs["x"] + sd * 56 * hs["sc"], hs["y"] - 40 * hs["sc"])
        E.add_glow(out, px, py, 80 * hs["sc"] * s, (120, 255, 190), 0.9 * b)
        r = 10 * hs["sc"] * s; E.ImageDraw.Draw(out).ellipse((px - r, py - r, px + r, py + r), fill=E.PALE + (int(255 * b),))
    # many small eyes all around in the dark
    import random
    rr = random.Random(3)
    for k in range(26):
        X, Y = rr.uniform(200, E.W - 200), rr.uniform(150, E.H - 200); op = b * (0.5 + 0.5 * math.sin(t * 2 + k)) * seg(t, T_DARK0 + 1.0, T_DARK0 + 2.5)
        px, py = to(X, Y)
        for sd in (-1, 1):
            E.ImageDraw.Draw(out).ellipse((px + sd * 9 * s - 4 * s, py - 3 * s, px + sd * 9 * s + 4 * s, py + 3 * s), fill=E.PALE + (int(200 * op),))
    rs = rook_state(t); gx, gy = to(rs["x"] + 24 * rs["face"] * 1.0, rs["y"] - 274)
    E.add_glow(out, gx, gy, (60 + 90 * rs["eye"]) * s, (255, 60, 40), 0.9 * b)

def shake(t):
    if T_GRAB < t < T_GRAB + 0.5: return 1.0 - seg(t, T_GRAB, T_GRAB + 0.5)
    if T_CUT < t < T_CUT + 0.4: return 0.8
    if 24.0 < t < 24.6: return 0.6
    return 0.15 if 8 < t < 18 or t > 24.6 else 0.0

def camera(t):
    return keyframes(t, [(0, 1100, 640, 1.35), (2.6, 1000, 560, 1.05), (5.5, 1100, 600, 1.15), (8.0, 1280, 720, 1.0),
                         (11.0, 1050, 560, 1.15), (13.4, 900, 640, 1.2), (15.8, 1150, 720, 1.25), (18.4, 1100, 560, 1.15),
                         (21.0, 1150, 700, 1.5), (24.0, 1280, 720, 1.0), (27.0, 1190, 800, 1.6), (29.5, 1190, 820, 1.75)])

def camera_v(t):
    # vertical: tall frame = the giant above, Rook below. Keep the empty trestle out.
    return keyframes(t, [(0, 1100, 660, 1.45), (2.6, 1000, 600, 1.3), (5.5, 1080, 620, 1.35), (8.0, 1080, 640, 1.3),
                         (11.0, 1000, 600, 1.35), (13.4, 950, 640, 1.35), (15.8, 1150, 700, 1.5), (18.4, 1050, 600, 1.3),
                         (21.0, 1150, 720, 1.6), (24.0, 1150, 680, 1.35), (27.0, 1190, 780, 1.75), (29.5, 1190, 800, 1.9)])

def score(snd):
    S = snd
    S.add(S.bell(81), 0.0, 0.25); S.add(S.bell(74), 0.35, 0.2)                 # station bell at 0s
    S.add(S.wind(DUR - E.TITLE_LEN), 0, 0.4)
    S.add(S.drone(9.0, 38), 1.5, 0.6)
    S.add(S.shh(1.8), 2.8, 0.5)                                                  # the Hush appears
    S.play([(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)], 2.9, 0.32, 0.13)   # THEME once
    S.add(S.whistle(1.3), T_GO - 0.2, 0.7)
    S.silence_music(T_DARK0, T_DARK1, 0.95)                                      # it eats the sound
    S.train_rhythm(T_GO + 0.6, T_DARK0, 0.30, 0.16)
    S.chase(T_GO + 0.6, T_DARK0 + 0.4, bpm=156, gain=0.14)
    S.add(S.drone(7.5, 36), 10.5, 0.8)
    S.steps(9.5, 17.5, 0.75, 0.45)
    S.add(S.stinger(), T_GRAB, 0.6)                                              # surprise: the hand
    S.add(S.clack(), T_CUT, 0.9); S.add(S.stinger(), T_CUT + 0.05, 0.3)
    S.add(S.drone(5.6, 33), T_DARK0, 0.9)
    for k in range(5): S.add(S.heartbeat(), T_DARK0 + 1.2 + k * 0.95, 0.55)
    S.add(S.shh(2.2), 20.0, 0.45)
    S.add(S.whistle(1.8), 23.9, 0.9)
    S.train_rhythm(24.2, DUR - E.TITLE_LEN - 0.5, 0.24, 0.16)
    S.chase(24.2, 27.0, bpm=168, gain=0.15)
    S.play([(74, 1), (78, 1), (81, 1), (86, 2)], 27.2, 0.3, 0.12)              # small hope
    S.title_music()
