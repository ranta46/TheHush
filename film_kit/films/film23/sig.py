"""signals for film 23 (The Green Lamps): near signal posts, the signal box, and the far quarry line of green lamps"""
import math
import gloamrun_engine as E
RED = (255, 70, 50); GREEN = (90, 255, 140)
POST = (24, 22, 30, 255); HEAD = (12, 11, 16, 255)

def post(frame, x, base, sc=1.0, red=0.0, green=0.0):
    """one signal post. red/green 0..1 = lamp brightness"""
    if x < -200 or x > E.W + 200: return
    d = E.ImageDraw.Draw(frame); h = 520 * sc; w = 14 * sc
    d.rectangle((x - w, base - h, x + w, base), fill=POST)
    d.rectangle((x - 60 * sc, base - 30 * sc, x + 60 * sc, base), fill=POST)
    hx0, hy0 = x - 46 * sc, base - h - 170 * sc
    d.rounded_rectangle((hx0, hy0, x + 46 * sc, base - h + 10 * sc), radius=int(20 * sc), fill=HEAD)
    ry, gy = hy0 + 48 * sc, hy0 + 128 * sc
    for yy, k, col in ((ry, red, RED), (gy, green, GREEN)):
        c = E.mix((40, 36, 44), col, k)
        d.ellipse((x - 26 * sc, yy - 26 * sc, x + 26 * sc, yy + 26 * sc), fill=c + (255,))
        if k > 0.02:
            E.add_glow(frame, x, yy, 170 * sc, col, 0.7 * k); E.add_glow(frame, x, yy, 40 * sc, (255, 255, 235), 0.8 * k)

def box(frame, x, base, lit=0.0):
    """the old signal box (a small hut on legs with a long window)"""
    d = E.ImageDraw.Draw(frame)
    d.rectangle((x - 200, base - 300, x + 200, base), fill=(30, 26, 34, 255))
    d.rectangle((x - 230, base - 560, x + 230, base - 300), fill=(44, 36, 40, 255), outline=(14, 12, 20, 255), width=6)
    d.polygon([(x - 270, base - 560), (x, base - 680), (x + 270, base - 560)], fill=(20, 18, 26, 255))
    d.rectangle((x - 190, base - 520, x + 190, base - 400), fill=E.mix((18, 16, 26), E.WINDOW, lit) + (255,))
    for k in range(5): d.rectangle((x - 190 + k * 95, base - 520, x - 184 + k * 95, base - 400), fill=(14, 12, 20, 255))
    if lit > 0.02: E.add_glow(frame, x, base - 460, 260, E.WINDOW, 0.4 * lit)

# the quarry line: lamps climbing away up the hill to the left (far = smaller)
N = 10
def far_pos(i, ox=0.0):
    k = i / (N - 1)
    return E.lerp(1150, -60, k) + ox * (1 - 0.7 * k), E.lerp(1000, 640, k), E.lerp(0.55, 0.16, k)

def far_line(frame, t, on=1.0, eaten=-1.0, ox=0.0):
    """on 0..N = how many lamps are lit (they light one by one); eaten = lamps with index < eaten are dark (the Hush ate them)"""
    d = E.ImageDraw.Draw(frame)
    pts = [far_pos(i, ox) for i in range(N)]
    d.line([(x, y + 6) for x, y, s in pts], fill=(40, 36, 46, 255), width=5)
    for i, (x, y, s) in enumerate(pts):
        k = E.clamp(on - i) * (0.0 if i < eaten else 1.0) * (0.85 + 0.15 * math.sin(t * 3 + i))
        post(frame, x, y, s, red=0.0, green=k)
