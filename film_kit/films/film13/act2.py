"""Act 2 - the water tower. Rook fills the boiler, lets ALL the steam out at once, puts out every light and hides in the cloud."""
import math, random
import gloamrun_engine as E
from gloamrun_engine import rook, hush, train, keyframes, steps_at, seg, ease, lerp, clamp
ACT_LEN = 36.0
SHOW = ("far", "rail")
T_FILL, T_BLOW, T_DARK, T_CREEP = 1.0, 11.6, 15.6, 28.0
TOWER_X = 2330
LINES = [
    (0.4, 2.6, "Fill her up. All of it!"),
    (5.6, 7.8, "Come on, come on..."),
    (9.4, 11.4, "Now. Let it ALL out!"),
    (13.4, 15.4, "Lights off. Hide in the cloud."),
    (19.6, 21.8, "...It can't see us in here."),
    (23.4, 25.6, "...It's right above us."),
    (26.4, 28.4, "...Don't move. Not a sound."),
    (30.6, 33.0, "...Slowly. Out the other side."),
]
BLINKS = E.auto_blinks(ACT_LEN, seed=132)
def speed(t): return 400 * (1 - ease(seg(t, 0.0, 1.0))) + 160 * ease(seg(t, T_CREEP, T_CREEP + 3.0))
_c = {}
def scroll(t):
    k = round(t * 24)
    if k not in _c:
        s = 0.0; dt = 1 / 48
        for i in range(int(t / dt)): s += speed(i * dt) * dt
        _c[k] = s
    return _c[k]
S0 = None
def wx(t): return -(scroll(t) - scroll(1.0))   # world-fixed things move left when the train creeps
def cloud(t): return ease(seg(t, T_BLOW, T_BLOW + 4.0))
def steam(frame, cx, cy, a, t, warm=0.0, spread=1.0):
    for k in range(16):
        ang = k * 2.4; r = (200 + 150 * (k % 3)) * spread
        x = cx + math.cos(ang) * r * 1.5 + math.sin(t * 0.5 + k) * 30; y = cy + math.sin(ang) * r * 0.5 + math.cos(t * 0.4 + k) * 20
        E.add_glow(frame, x, y, int((380 + 60 * (k % 4)) * spread), (205, 212, 222), 0.6 * a)
    if warm > 0: E.add_glow(frame, cx + 200, cy + 40, 420, E.WINDOW, 0.4 * warm * a)
def tower(frame, x):
    d = E.ImageDraw.Draw(frame); wood = (58, 42, 40, 255); dark = (30, 24, 28, 255); y0 = E.RAIL
    for lx in (x - 150, x + 150): d.polygon([(lx - 14, y0 - 380), (lx + 14, y0 - 380), (lx + 24 * (1 if lx > x else -1) + 14, y0), (lx + 24 * (1 if lx > x else -1) - 14, y0)], fill=dark)
    d.line((x - 150, y0 - 200, x + 150, y0 - 200), fill=dark, width=10)
    d.rectangle((x - 200, y0 - 640, x + 200, y0 - 380), fill=wood, outline=E.INK + (255,), width=6)
    for k in range(5): d.line((x - 200, y0 - 600 + k * 50, x + 200, y0 - 600 + k * 50), fill=(40, 30, 30, 255), width=4)
    d.polygon([(x - 230, y0 - 640), (x, y0 - 760), (x + 230, y0 - 640)], fill=dark)
    sp = ease(seg(t_now[0], T_FILL, T_FILL + 1.2)) * (1 - ease(seg(t_now[0], 9.0, 10.0)))
    ex = lerp(x - 130, x - 330, sp); ey = lerp(y0 - 460, y0 - 330, sp)
    d.line((x - 200, y0 - 460, ex, ey), fill=E.IRON + (255,), width=26)
    if sp > 0.6:   # water running into the tender
        for k in range(6): d.line((ex - 10 + k * 4, ey, ex - 10 + k * 4, ey + 60), fill=(140, 190, 230, 200), width=3)
t_now = [0.0]
def lamp(t): return 1.0 - ease(seg(t, T_DARK - 0.4, T_DARK + 0.6))
def train_state(t): return train(x=2050, cars=2, lamp=lamp(t), smoke=0.0 if t > T_BLOW else 0.3, dark=0.6 * ease(seg(t, T_DARK, T_DARK + 1.0)))
def rook_state(t):
    pose = steps_at(t, [(0, "point"), (2.8, "pull"), (5.4, "lean"), (8.6, "idle"), (9.2, "spread"), (11.8, "celebrate"), (13.2, "shh"),
                        (19.4, "down"), (23.2, "flinch"), (26.2, "shh"), (30.4, "ahead")])
    eye = 1.0
    if t > T_DARK: eye = 0.35
    return rook(x=1190, y=E.RAIL - 160, face=-1 if 5.4 <= t < 8.6 or 23.2 <= t < 26.2 else 1, pose=pose,
                look={"ahead": 0.5, "point": 0.5, "lean": 0.3}.get(pose, 0.0), eye=eye,
                flap=0.6 if pose in ("spread", "celebrate") else 0.0, blink=E.blink_at(t, BLINKS))
def hush_state(t):
    x, y, sc, near = keyframes(t, [(0, 640, 480, 1.15, 0.6), (6.0, 720, 440, 1.3, 0.75), (11.0, 820, 400, 1.4, 0.85), (16.0, 900, 380, 1.5, 0.9),
                                   (21.0, 1300, 300, 1.75, 1.0), (28.0, 1350, 300, 1.8, 1.0), (36.0, 1250, 320, 1.75, 1.0)])
    if t > T_CREEP: x += wx(t)
    return hush(x=x, y=y, sc=sc, near=near, eye=1.5 if t > T_DARK else 1.0 + 0.6 * near, hand="shh", lean=0.05 * math.sin(t * 1.1))
def draw_back(frame, t, ctx):
    t_now[0] = t
def draw_scene(frame, t, ctx):
    t_now[0] = t
    tower(frame, TOWER_X + wx(t))
    c = cloud(t)
    if c > 0:
        steam(frame, 1650 + wx(t), 860, c, t, warm=lamp(t), spread=0.5 + 0.8 * c)
    if 1.0 < t < T_BLOW:   # a thin hiss of steam while the boiler fills
        E.add_glow(frame, 1950, 690, 90, (205, 212, 222), 0.4)
def draw_front(frame, t, ctx):
    c = cloud(t)
    if c > 0.3:   # the cloud is in front of the train too, but thin enough to see Rook
        for k in range(6):
            E.add_glow(frame, 900 + k * 260 + wx(t) + math.sin(t * 0.4 + k) * 40, 980 + 30 * math.sin(k), 300, (190, 198, 210), 0.35 * c)
def blackout(t): return 0.5 * ease(seg(t, T_DARK, T_DARK + 1.0))
def draw_overlay(out, t, orient):
    b = blackout(t)
    if b < 0.05: return
    ow, oh = out.size; cx, cy, z = camera(t)
    vw, vh = E.W / z, E.H / z; cx = clamp(cx, vw / 2, E.W - vw / 2); cy = clamp(cy, vh / 2, E.H - vh / 2)
    to = lambda X, Y: ((X - (cx - vw / 2)) / vw * ow, (Y - (cy - vh / 2)) / vh * oh); s = ow / vw
    hs = hush_state(t)
    for sd in (-1, 1):
        px, py = to(hs["x"] + sd * 56 * hs["sc"], hs["y"] - 40 * hs["sc"])
        E.add_glow(out, px, py, 80 * hs["sc"] * s, (120, 255, 190), 0.9 * b)
    rs = rook_state(t); gx, gy = to(rs["x"] + 24 * rs["face"], rs["y"] - 274)
    E.add_glow(out, gx, gy, (60 + 90 * rs["eye"]) * s, (255, 60, 40), 0.9 * b)
def shake(t): return 0.5 if T_BLOW < t < T_BLOW + 1.2 else 0.0
def camera(t):
    return keyframes(t, [(0, 1700, 640, 1.15), (3.0, 1900, 600, 1.3), (5.6, 1190, 780, 1.4), (8.0, 1500, 640, 1.05), (9.4, 1190, 780, 1.45),
                         (11.6, 1500, 680, 1.0), (13.4, 1190, 760, 1.35), (16.0, 1300, 640, 1.05), (19.6, 1190, 740, 1.3),
                         (22.6, 1250, 520, 1.05), (26.2, 1190, 760, 1.4), (29.0, 1280, 640, 1.05), (36, 1300, 680, 1.0)])
def score(S):
    S.add(S.wind(ACT_LEN, 0.8), 0, 0.3); S.add(S.clack(), 0.8, 0.6)
    S.add(S.drone(10.0, 38), 2.0, 0.45); S.steps(4.0, 11.0, 0.9, 0.45)
    S.add(S.wind(8.0, 1.5), 1.2, 0.25)
    S.add(S.heartbeat(), 6.0, 0.4); S.add(S.heartbeat(), 7.2, 0.45); S.add(S.heartbeat(), 8.3, 0.5)
    S.add(S.whistle(2.4), T_BLOW, 0.9); S.add(S.wind(4.0, 2.0), T_BLOW, 0.6); S.add(S.stinger(), T_BLOW + 0.1, 0.4)
    S.add(S.clack(), T_DARK, 0.6); S.add(S.drone(20.0, 34), T_DARK, 0.8)
    S.add(S.shh(2.4), 17.0, 0.5); S.steps(16.5, 21.5, 1.0, 0.7); S.add(S.stinger(), 21.0, 0.45)
    for k in range(10): S.add(S.heartbeat(), 22.0 + k * 1.05, 0.5 if k < 5 else 0.6)
    S.add(S.shh(2.0), 27.0, 0.4); S.train_rhythm(T_CREEP + 1.0, ACT_LEN, 0.7, 0.08)
