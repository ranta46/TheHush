"""fireflies for film 15 (world-space small glows)"""
import math, random
import gloamrun_engine as E
_R = random.Random(15)
FLIES = [(_R.uniform(-600, 4200), _R.uniform(380, 1040), _R.uniform(0, 6.28), _R.uniform(0.6, 1.4)) for _ in range(90)]
COL = (230, 255, 140)
def draw(frame, t, ox=0.0, a=1.0, dark_at=None, dark_r=520, rise=0.0, rise_x=None):
    """ox = world shift; dark_at = (x,y) where the Hush eats the light; rise 0..1 = the swarm flies up toward rise_x"""
    if a <= 0: return
    for (x, y, ph, s) in FLIES:
        X = x + ox + 26 * math.sin(t * 0.9 * s + ph); Y = y + 18 * math.cos(t * 1.3 * s + ph)
        if rise > 0:
            tx = rise_x if rise_x is not None else X
            X = X + (tx + 300 * math.sin(ph * 3) - X) * rise; Y = Y + (-200 + 140 * math.sin(ph * 5) - Y) * rise
        if X < -100 or X > E.W + 100: continue
        k = a * (0.55 + 0.45 * math.sin(t * 2.2 * s + ph * 2))
        if dark_at is not None:
            d = math.hypot(X - dark_at[0], Y - dark_at[1]); k *= min(1.0, max(0.0, (d - dark_r) / 240))
        if k > 0.03:
            E.add_glow(frame, X, Y, 60 * s, COL, 0.7 * k); E.add_glow(frame, X, Y, 14 * s, (255, 255, 220), 1.0 * k)
def trees(frame, ox=0.0):
    d = E.ImageDraw.Draw(frame)
    for i in range(14):
        x = -400 + i * 330 + ox + (i * 97 % 120)
        if x < -300 or x > E.W + 300: continue
        h = 620 + (i * 53 % 220); y0 = E.RAIL - 40
        d.rectangle((x - 18, y0 - h * 0.45, x + 18, y0), fill=(20, 18, 26, 255))
        d.polygon([(x - 170, y0 - h * 0.35), (x, y0 - h), (x + 170, y0 - h * 0.35)], fill=(16, 22, 28, 255))
        d.polygon([(x - 130, y0 - h * 0.6), (x, y0 - h * 1.08), (x + 130, y0 - h * 0.6)], fill=(18, 26, 30, 255))
