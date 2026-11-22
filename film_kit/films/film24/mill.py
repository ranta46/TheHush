"""windmills for film 24 (The Windmills): far mill silhouettes, and the big old mill with turning sails and a lantern"""
import math
import gloamrun_engine as E
WOOD = (34, 28, 38, 255); SAIL = (52, 44, 54, 255); LAMP = (255, 214, 130)

def tip(x, base, sc, ang, k=0):
    """centre of sail k's tip (where the lantern hangs)"""
    hx, hy = x, base - 560 * sc; a = ang + k * math.pi / 2; r = 330 * sc
    return hx + r * math.cos(a), hy + r * math.sin(a)

def mill(frame, x, base, sc=1.0, ang=0.0, lantern=0.0, lamp_k=0):
    if x < -500 * sc or x > E.W + 500 * sc: return
    d = E.ImageDraw.Draw(frame)
    d.polygon([(x - 120 * sc, base), (x - 70 * sc, base - 520 * sc), (x + 70 * sc, base - 520 * sc), (x + 120 * sc, base)], fill=WOOD)
    d.polygon([(x - 95 * sc, base - 515 * sc), (x, base - 620 * sc), (x + 95 * sc, base - 515 * sc)], fill=(24, 20, 30, 255))
    d.rectangle((x - 26 * sc, base - 120 * sc, x + 26 * sc, base), fill=(16, 13, 22, 255))
    hx, hy = x, base - 560 * sc
    for k in range(4):
        a = ang + k * math.pi / 2; ca, sa = math.cos(a), math.sin(a); px, py = -sa, ca
        d.line((hx, hy, hx + 360 * sc * ca, hy + 360 * sc * sa), fill=WOOD, width=max(2, int(12 * sc)))
        r0, r1, w = 90 * sc, 350 * sc, 46 * sc
        d.polygon([(hx + r0 * ca, hy + r0 * sa), (hx + r1 * ca, hy + r1 * sa), (hx + r1 * ca + w * px, hy + r1 * sa + w * py),
                   (hx + r0 * ca + w * px, hy + r0 * sa + w * py)], fill=SAIL)
    d.ellipse((hx - 22 * sc, hy - 22 * sc, hx + 22 * sc, hy + 22 * sc), fill=(20, 16, 26, 255))
    if lantern > 0.02:
        lx, ly = tip(x, base, sc, ang, lamp_k)
        d.ellipse((lx - 16 * sc, ly - 16 * sc, lx + 16 * sc, ly + 16 * sc), fill=E.mix((60, 50, 40), LAMP, lantern) + (255,))
        E.add_glow(frame, lx, ly, 220 * sc, LAMP, 0.6 * lantern); E.add_glow(frame, lx, ly, 50 * sc, (255, 250, 230), 0.9 * lantern)

def lantern_at(frame, x, y, a=1.0, sc=1.0):
    d = E.ImageDraw.Draw(frame)
    d.ellipse((x - 16 * sc, y - 16 * sc, x + 16 * sc, y + 16 * sc), fill=E.mix((60, 50, 40), LAMP, a) + (255,))
    E.add_glow(frame, x, y, 220 * sc, LAMP, 0.6 * a); E.add_glow(frame, x, y, 50 * sc, (255, 250, 230), 0.9 * a)

def far_mills(frame, off, t, lit=0.0):
    """a row of small far mills (scroll with off). lit = their little window lamps"""
    for k in range(7):
        x = (k * 520 - off * 0.3) % 3640 - 300
        mill(frame, x, E.RAIL - 60, 0.32, ang=t * 0.6 + k)
        if lit > 0.02: E.add_glow(frame, x, E.RAIL - 60 - 110, 40, LAMP, 0.6 * lit)
