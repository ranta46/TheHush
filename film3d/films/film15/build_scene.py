# GLOAMRUN 3D Film 18 "The Wheat Sea" — run INSIDE Blender (hush_lookdev.blend open, scene HUSH).
# Story (no calm start): the lamps behind die and its face rises over the ridge at once -> it is faster over the downs ->
# Rook's move: he puts out every light and the fire and runs the dark train into the tall wheat field (the wheat is taller than the
# train); the Hush searches the field; the train moves ONLY when the wind blows, so the moving wheat hides it, and stops when the
# wind stops -> the wind dies and it stands right over the dark train ('Don't move') -> surprise: the old whistle peeps by itself
# (a little puff of steam); it looks down at us -> lights on, full steam out of the wheat to Harvest Town; it follows (it will be back).
import bpy, bmesh, math, random, os
from mathutils import Vector
OUT = r"C:\Users\81803\TremenFilm\hush\film15"; os.makedirs(OUT, exist_ok=True)
sc = bpy.data.scenes["HUSH"]; bpy.context.window.scene = sc; O = bpy.data.objects
FPS = 24; END = 2400; sc.render.fps = FPS; sc.frame_start = 1; sc.frame_end = END
F = lambda s: int(round(s * FPS)) + 1
def M(name):
    return bpy.data.materials[name]
def newM(name, col, emit=0.0, rough=0.6, metal=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF"); b.inputs["Base Color"].default_value = (*col, 1)
    b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    b.inputs["Emission Color"].default_value = (*col, 1); b.inputs["Emission Strength"].default_value = emit; return m
def mk(name, bm, mat, loc=(0, 0, 0), rot=(0, 0, 0), scl=(1, 1, 1), parent=None, smooth=False):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    if smooth:
        for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); me.materials.append(mat)
    o.location = loc; o.rotation_euler = rot; o.scale = scl
    if parent: o.parent = parent
    return o
def box():
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); return bm
def cyl(r1, r2, d, seg=16):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r1, radius2=r2, depth=d); return bm
def sph(r=1.0, s=16, v=10):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=s, v_segments=v, radius=r); return bm
def empty(name, loc=(0, 0, 0), parent=None):
    e = O.get(name) or bpy.data.objects.new(name, None)
    if e.name not in sc.collection.objects: sc.collection.objects.link(e)
    e.location = loc; e.parent = parent; return e
def key(o, path, frame, val, idx=-1):
    if idx >= 0:
        getattr(o, path)[idx] = val; o.keyframe_insert(path, index=idx, frame=frame)
    else:
        setattr(o, path, val); o.keyframe_insert(path, frame=frame)
def lin(o):
    ad = o.animation_data
    if not ad or not ad.action: return
    try:
        fcs = ad.action.layers[0].strips[0].channelbag(ad.action_slot).fcurves
    except Exception:
        fcs = getattr(ad.action, "fcurves", [])
    for fc in fcs:
        for kp in fc.keyframe_points: kp.interpolation = "LINEAR"

# ---------------- clean previous build ----------------

# ---------------- clean previous build ----------------
for o in list(bpy.data.objects):
    if o.name.startswith(("S_", "L_", "Cam_", "T_", "V_", "Peek")): bpy.data.objects.remove(o, do_unlink=True)
for o in list(sc.collection.all_objects):
    if o.animation_data: o.animation_data_clear()
sc.timeline_markers.clear()
for n in ("HCam", "MoonDisc", "MaskLight", "WarmRim", "SignalGlow"):
    if n in O: bpy.data.objects.remove(O[n], do_unlink=True)
GA = O["Ground"]; GA.scale = (1200, 1000, 1); GA.location = (150, 100, -0.5)
for o in list(bpy.data.objects):
    if o.name.startswith("Rail"): o.hide_render = True; o.hide_viewport = True

# ---------------- train group ----------------
T = empty("Train")
for n in ("Car", "CarTrim", "Cab", "CabWin", "Boiler", "Stack", "Lamp", "Rook") + tuple(o.name for o in sc.collection.all_objects if o.name.startswith("Wheel")):
    o = O[n]; o.parent = T
def light(name, typ, energy, col, loc, parent=None, size=1.0, shadow=False):
    d = bpy.data.lights.new(name, typ); d.energy = energy; d.color = col
    if typ == "AREA": d.size = size
    if typ == "SPOT": d.spot_size = math.radians(55)
    try: d.use_shadow = shadow
    except Exception: pass
    o = bpy.data.objects.new(name, d); sc.collection.objects.link(o); o.location = loc; o.parent = parent; return o
HL = light("T_HeadBeam", "SPOT", 900, (1, 0.85, 0.6), (5.1, 0, 0.9), T); HL.rotation_euler = (0, math.radians(90 + 6), 0)
O["Fill"].parent = T; O["Fill"].location = (1.6, -2.4, 2.4); O["Fill"].data.energy = 45
SIGL = light("T_SignalGlow", "POINT", 4, (1, 0.08, 0.04), (0.7, -0.5, 1.7), T)
R = O["Rook"]; R.location = (0.6, 0, 0.62); R.rotation_euler = (0, 0, math.radians(58))
HP = empty("R_HeadPivot", (0, -0.02, 0.98), R)
for n in ("R_Head", "R_Beak", "R_EyeL", "R_PupL", "R_EyeR", "R_Ring", "R_Hat", "R_Band", "R_Brim", "R_Badge"):
    o = O[n]; o.parent = HP; o.location = o.location - Vector((0, -0.02, 0.98))
for n in ("R_KeyLoop-1", "R_KeyLoop1"):
    o = O[n]; key(o, "rotation_euler", 1, 0.0, 0); key(o, "rotation_euler", END, math.radians(-360 * 40), 0); lin(o)



# ---------------- world: the downs, the wheat sea, Harvest Town ----------------
from mathutils import Matrix
rr = random.Random(1818)
X0 = -230.0                                    # the line runs straight east along y = 0 (x -230 .. 480)
WA, WB = 60.0, 300.0                           # the wheat field along the line
WY = 1.75                                      # wheat starts this far from the line centre (gap for the train)
WH = 2.5                                       # wheat height (the train is lower)
def ss(a, b, v):
    u = min(1.0, max(0.0, (v - a) / (b - a))); return u * u * (3 - 2 * u)
def pose(s): return (-150.0 + s, 0.0, 0.0)
def gh(x, y):
    n = 0.9 * math.sin(x * 0.045 + y * 0.03) + 0.6 * math.sin(x * 0.09 - y * 0.06 + 1.3)
    d = abs(y); up = ss(6, 70, d) * (4 + 2 * n) + ss(90, 180, d) * 16 + 0.3 * n * ss(8, 20, d)
    back = 24.0 * math.exp(-((x + 285.0) / 30.0) ** 2)               # the ridge at the back of the downs
    return up + back - 0.02
def wheat_in(x, y): return WA <= x <= WB and WY <= abs(y) <= 95
GA = O["Ground"]; GA.location = (0, 0, -40.0); GA.scale = (1400, 1000, 1)
grassM = newM("S_Grass", (0.04, 0.06, 0.04), rough=1); rockM = newM("S_RockM", (0.09, 0.09, 0.1), rough=1)
GA.data.materials.clear(); GA.data.materials.append(rockM)
def axis(a, b, step):
    out = []; v = a
    while v <= b: out.append(v); v += step
    return out
xs = axis(-420, -332, 6) + axis(-330, 490, 2.0) + axis(496, 600, 6)
ys = axis(-220, -122, 6) + axis(-120, 120, 2.0) + axis(126, 240, 6)
bm = bmesh.new(); vv = [[bm.verts.new((x, y, gh(x, y))) for y in ys] for x in xs]
for i in range(len(xs) - 1):
    for j in range(len(ys) - 1):
        f = bm.faces.new((vv[i][j], vv[i + 1][j], vv[i + 1][j + 1], vv[i][j + 1]))
        if abs(vv[i][j].co.z - vv[i + 1][j + 1].co.z) > 2.0: f.material_index = 1
GO = mk("S_DownsGround", bm, grassM, smooth=True); GO.data.materials.append(rockM)
# the wheat: a golden top surface (two strips beside the line) + stalk clumps at the edges and along the line, all waving in the wind
wheatM = newM("S_Wheat", (0.46, 0.32, 0.1), emit=0.06, rough=0.9)
wheat2 = newM("S_Wheat2", (0.56, 0.4, 0.13), emit=0.08, rough=0.9)
WAVE = []
def wavemod(o):
    m = o.modifiers.new("Wind", "WAVE"); m.use_x = True; m.use_y = True; m.use_cyclic = True
    m.start_position_x = WA - 60; m.start_position_y = -140; m.width = 7.0; m.narrowness = 1.2; m.speed = 0.22
    m.height = 0.0; m.time_offset = 0; WAVE.append(m); return m
for sd in (-1, 1):
    wys = [sd * WY] + [sd * v for v in axis(2.0, 96, 1.0)]
    wxs = axis(WA, WB, 1.0)
    bm = bmesh.new(); grid = []
    for x in wxs:
        row = []
        for k, y in enumerate(wys):
            edge = x <= WA + 0.01 or x >= WB - 0.01 or k == 0 or k == len(wys) - 1
            h = 0.0 if edge else WH + 0.18 * math.sin(x * 0.7 + y * 0.9) + 0.1 * math.sin(x * 2.3 - y * 1.7)
            row.append(bm.verts.new((x, y, gh(x, y) + h)))
        grid.append(row)
    for i in range(len(wxs) - 1):
        for j in range(len(wys) - 1):
            q = (grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1])
            bm.faces.new(q if sd > 0 else q[::-1])
    o = mk(f"S_WheatTop{sd}", bm, wheatM, smooth=True); wavemod(o)
bm = bmesh.new()
def stalk(x, y, h):
    g = bmesh.ops.create_cone(bm, cap_ends=False, cap_tris=False, segments=5, radius1=0.16, radius2=0.05, depth=h)["verts"]
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(rr.uniform(-0.12, 0.12), 3, "X") @ Matrix.Rotation(rr.uniform(-0.12, 0.12), 3, "Y"), verts=g)
    bmesh.ops.translate(bm, vec=(x, y, gh(x, y) + h / 2), verts=g)
n = 0
x = WA
while x <= WB:                                                            # along the line, both sides (what the cameras near the train see)
    for sd in (-1, 1):
        for k in range(3):
            y = sd * rr.uniform(WY, WY + 2.6); stalk(x + rr.uniform(-0.25, 0.25), y, WH + rr.uniform(-0.15, 0.25)); n += 1
    x += 0.55
for y in axis(-95, 95, 0.5):                                              # the field edges
    if abs(y) < WY: continue
    for xe in (WA, WB):
        for k in range(2): stalk(xe + rr.uniform(0, 1.4) * (1 if xe == WA else -1), y + rr.uniform(-0.2, 0.2), WH + rr.uniform(-0.2, 0.2)); n += 1
for i in range(5000):                                                     # heads sticking out of the top
    x = rr.uniform(WA + 1, WB - 1); y = rr.choice((-1, 1)) * rr.uniform(WY + 0.4, 60)
    stalk(x, y, WH + rr.uniform(0.15, 0.45)); n += 1
ST = mk("S_WheatStalks", bm, wheat2); wavemod(ST)
print("stalks", n)
railM = newM("S_RailM", (0.2, 0.2, 0.22), rough=0.4, metal=0.8); tie = newM("S_Tie", (0.05, 0.04, 0.035), rough=1)
postM = newM("S_Post", (0.02, 0.02, 0.025), rough=0.5)
def pboxes(name, mat, items, parent=None):
    bm = bmesh.new()
    for loc, scl, rz in items:
        g = bmesh.ops.create_cube(bm, size=1.0)["verts"]; bmesh.ops.scale(bm, vec=scl, verts=g)
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(rz, 3, "Z"), verts=g); bmesh.ops.translate(bm, vec=loc, verts=g)
    return mk(name, bm, mat, parent=parent)
rails, ties = [], []
for i in range(int((480 - X0) / 2)):
    x = X0 + i * 2 + 1
    for yy in (-0.53, 0.53): rails.append(((x, yy, 0.03), (2.03, 0.08, 0.06), 0.0))
    ties.append(((x, 0, 0.01), (0.25, 1.4, 0.06), 0.0))
pboxes("S_Rails", railM, rails); pboxes("S_Ties", tie, ties)
pboxes("S_EndStop", newM("S_Red", (0.6, 0.05, 0.03), rough=0.5), [((X0 + 2, 0, 0.45), (0.3, 1.8, 0.5), 0), ((478, 0, 0.45), (0.3, 1.8, 0.5), 0)])
# lamps along the line (die in a wave as it passes), lamps past the field, Harvest Town
RLAMP = []
def lamp(tag, x, y, td, e=55):
    z = max(gh(x, y), 0.0); mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, y, z + 1.7))
    hm = newM(f"L_{tag}", (1, 0.62, 0.25), emit=8); mk(f"L_{tag}", sph(0.2, 12, 8), hm, (x, y, z + 3.45))
    RLAMP.append((hm, light(f"L_{tag}L", "POINT", e, (1, 0.6, 0.3), (x, y, z + 3.2)), td))
HX = [(6, -268), (10, -205), (14, -140), (18, -75), (22, -15), (26, 30), (30, 56)]
def h_time(x):
    for (ta, xa), (tb, xb) in zip(HX, HX[1:]):
        if xa <= x <= xb: return ta + (tb - ta) * (x - xa) / (xb - xa)
    return 34.0
for i, x in enumerate((-215, -195, -175, -158)): lamp(f"B{i}", x, -3.2, 0.2 + i * 0.55)       # the lamps behind die first
for i, x in enumerate((-130, -100, -70, -40, -10, 20, 48)): lamp(f"V{i}", x, -3.2, h_time(x) - 0.6)
for i, x in enumerate((340, 370, 400, 418)): lamp(f"E{i}", x, -3.2, 999)
for i in range(5): lamp(f"St{i}", 436 + i * 9.0, 3.4, 999, 80)
treeM = newM("S_Pine", (0.02, 0.035, 0.025), rough=1); bm = bmesh.new()
for i in range(200):
    x = rr.uniform(-320, 470); y = rr.uniform(-170, 170)
    if abs(y) < 12 or (WA - 6 < x < WB + 6 and abs(y) < 100): continue
    z0 = gh(x, y); h = rr.uniform(5, 10)
    g = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=7, radius1=h * 0.28, radius2=0.0, depth=h)["verts"]
    bmesh.ops.translate(bm, vec=(x, y, z0 + h / 2 + 0.6), verts=g)
mk("S_Pines", bm, treeM)
rocks, walls = [], []
for i in range(40):
    x = rr.uniform(-300, 460); y = rr.uniform(-140, 140)
    if abs(y) < 8 or (WA - 4 < x < WB + 4 and abs(y) < 98): continue
    s = rr.uniform(0.6, 1.8); rocks.append(((x, y, gh(x, y) + s * 0.3), (s * 1.4, s, s * 0.9), rr.uniform(0, 3)))
for k in range(14):                                                      # old stone walls on the downs
    y0 = rr.choice((-1, 1)) * rr.uniform(14, 70); x0 = rr.choice((rr.uniform(-280, 40), rr.uniform(310, 400))); a = rr.uniform(-0.4, 0.4)
    for j in range(12):
        x = x0 + j * 2.0 * math.cos(a); y = y0 + j * 2.0 * math.sin(a)
        if abs(y) < 8 or (WA - 4 < x < WB + 4): continue
        walls.append(((x, y, gh(x, y) + 0.35), (2.1, 0.5, 0.8), a))
pboxes("S_Rocks", rockM, rocks + walls)
farM = newM("S_FarPeak", (0.1, 0.11, 0.15), rough=1)
for i in range(9):
    hx = -320 + i * 100
    mk("S_FarPeak", cyl(1, 0.05, 1, 8), farM, (hx, rr.uniform(270, 310), 10), scl=(rr.uniform(55, 75), 45, rr.uniform(40, 65)))
    mk("S_FarPeak", cyl(1, 0.05, 1, 8), farM, (hx + 50, -rr.uniform(290, 330), 0), scl=(rr.uniform(55, 75), 45, rr.uniform(40, 60)))
houseM = newM("S_HouseM", (0.075, 0.07, 0.078), rough=1); roofM = newM("S_Roof", (0.25, 0.12, 0.09), rough=1)
winM = newM("S_Win", (1, 0.62, 0.25), emit=5)
for i in range(26):
    x = rr.uniform(400, 480); y = rr.choice((rr.uniform(12, 50), rr.uniform(-50, -12))); w = rr.uniform(3, 6); h = rr.uniform(2.5, 5)
    z0 = gh(x, y); sd = 1 if y > 0 else -1
    mk("S_House", box(), houseM, (x, y, z0 + h / 2 - 0.5), scl=(w, w, h)); mk("S_Roof", box(), roofM, (x, y, z0 + h - 0.4), scl=(w + 0.4, w + 0.4, 0.3))
    mk("S_Win", box(), winM, (x, y - sd * (w / 2 + 0.02), z0 + h * 0.45), scl=(0.6, 0.05, 0.7))
mk("S_Platform", box(), newM("S_Plat", (0.1, 0.09, 0.1), rough=1), (454, 2.4, 0.0), scl=(40, 2.2, 0.6))
# the old windmill of Harvest Town (still), and sheaves on the platform
millM = newM("S_Mill", (0.13, 0.11, 0.1), rough=1); sailM = newM("S_Sail", (0.3, 0.27, 0.22), rough=1)
mz = gh(462, 22)
mk("S_Mill", cyl(3.0, 2.0, 12, 10), millM, (462, 22, mz + 6))
mk("S_MillCap", cyl(2.3, 0.2, 2.4, 10), roofM, (462, 22, mz + 13.2))
for k in range(4):
    a = k * math.pi / 2 + 0.4
    mk("S_MillSail", box(), sailM, (462 + 4.2 * math.cos(a), 19.6, mz + 10.5 + 4.2 * math.sin(a)), (0, -a, 0), scl=(8.0, 0.15, 1.4))
mk("S_MillWin", box(), winM, (462, 19.9, mz + 4), scl=(0.8, 0.1, 1.0))
bm = bmesh.new()
for i in range(8):
    g = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=0.45, radius2=0.2, depth=1.3)["verts"]
    bmesh.ops.translate(bm, vec=(440 + i * 4.3, 3.0, 0.95), verts=g)
mk("S_Sheaves", bm, wheat2)
moonM = newM("S_Moon", (0.9, 0.88, 0.8), emit=3)
mk("S_Moon", cyl(9, 9, 0.2, 48), moonM, (150, -380, 110), (math.pi / 2, 0, 0.0))
w = sc.world; w.node_tree.nodes["Background"].inputs[0].default_value = (0.014, 0.018, 0.045, 1)
O["MoonKey"].data.energy = 3.6
FIREM = newM("T_FireM", (1, 0.35, 0.08), emit=12)
mk("T_Fire", box(), FIREM, (2.45, 0, 0.55), scl=(0.06, 0.5, 0.3), parent=T)
FIRE = light("T_FireGlow", "POINT", 25, (1, 0.45, 0.15), (2.2, 0, 0.7), T)
# the little puff of steam when the old whistle peeps by itself (55.6)
SX = 4.6                                                                  # stack (train-local x)
PUFF = mk("T_Puff", sph(0.3, 12, 8), newM("T_PuffM", (0.8, 0.82, 0.85), emit=0.4, rough=1), (SX - 0.9, 0, 2.0), parent=T)

# ---------------- the Hush ----------------
H = O["Hush"]; H.scale = (2.4, 2.4, 2.4)
mask_spot = light("T_MaskLight", "SPOT", 9000, (0.7, 0.85, 1.0), (0, 0, 0)); mask_spot.data.spot_size = math.radians(18)
c = mask_spot.constraints.new("TRACK_TO"); c.target = O["H_Mask"]; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
mask_spot.parent = H; mask_spot.location = (2.0, -14, 4.0)


# ---------------- animation ----------------
SK = [(0, 0), (4, 44), (8, 90), (12, 135), (16, 178), (20, 212), (22, 228), (24, 238), (36, 238), (40, 246), (42.6, 246), (45.2, 252),
      (59.9, 252), (62, 260), (64, 274), (66, 294), (70, 340), (74, 390), (78, 440), (82, 490), (86, 538), (90, 580), (93, 600),
      (95, 606), (96.5, 607), (100, 607)]
def s_at(t):
    for (ta, sa), (tb, sb) in zip(SK, SK[1:]):
        if ta <= t <= tb:
            u = (t - ta) / (tb - ta) if tb > ta else 0; return sa + (sb - sa) * u
    return SK[-1][1]
def tx(t): return pose(s_at(t))[0]
for f in range(1, END + 1, 4):
    x, y, h = pose(s_at((f - 1) / FPS)); key(T, "location", f, Vector((x, y, 0.0))); key(T, "rotation_euler", f, h, 2)
x, y, h = pose(s_at(100)); key(T, "location", END, Vector((x, y, 0.0))); key(T, "rotation_euler", END, h, 2)
lin(T)
for hm, lt, td in RLAMP:
    if td > 150: continue
    s = hm.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for t, e in ((0, 8), (td - 0.01, 8), (td + 0.15, 0)): s.default_value = e; s.keyframe_insert("default_value", frame=F(max(t, 0)))
    e0 = lt.data.energy
    for t, e in ((0, e0), (td - 0.01, e0), (td + 0.15, 0)): lt.data.energy = e; lt.data.keyframe_insert("energy", frame=F(max(t, 0)))
# the wind: soft all the time, two gusts (36.0-40.4, 42.6-45.2) when the train creeps, dead still in the fear (45.6-60), wind after
GUST = [(0, 0.12), (35.6, 0.12), (36.2, 0.55), (40.0, 0.55), (40.6, 0.03), (42.4, 0.03), (42.9, 0.5), (44.9, 0.5), (45.5, 0.0),
        (60.0, 0.0), (61.0, 0.2), (100, 0.2)]
for m in WAVE:
    for t, v in GUST: m.height = v; m.keyframe_insert("height", frame=F(t))
    m.time_offset = 0
# the puff: the old whistle peeps by itself (55.6)
PUFF.scale = (0.01, 0.01, 0.01); PUFF.keyframe_insert("scale", frame=1); PUFF.keyframe_insert("scale", frame=F(55.5))
for t, s, z in ((55.5, 0.01, 2.0), (55.9, 0.9, 2.5), (56.8, 1.5, 3.3), (57.6, 0.01, 3.9)):
    PUFF.scale = (s, s, s); PUFF.keyframe_insert("scale", frame=F(t)); PUFF.location.z = z; PUFF.keyframe_insert("location", index=2, frame=F(t))

# the Hush: rises over the back ridge (2.4-4.6), comes over the downs faster than us, reaches the wheat (30) and searches the field,
# looking all round (it does not see the dark train in the waving wheat); it stands right beside the dark train (46-55.6); the whistle
# peeps, it looks down at us; lights on, we run; it follows.
HP_ = [(0, -280, -10, -40), (2.4, -280, -10, -40), (3.4, -280, -10, -14), (4.6, -280, -10, 0), (5.4, -278, -10, 0), (6, -268, -12, 0),
       (10, -205, -16, 0), (14, -140, -18, 0), (18, -75, -18, 0), (22, -15, -18, 0), (26, 30, -18, 0), (30, 56, -17, 0),
       (34, 70, -16, 0), (38, 80, -14, 0), (42, 90, -12.5, 0), (46, 99, -10.5, 0), (55.6, 100, -10, 0), (56.4, 100, -9.6, -0.4), (58, 100, -9.6, -0.4),
       (60, 102, -10, 0), (64, 130, -14, 0), (70, 185, -18, 0), (76, 240, -20, 0), (82, 300, -22, 0), (88, 352, -24, 0), (94, 400, -24, 0),
       (100, 435, -24, 0)]
for t, x, y, dz in HP_:
    key(H, "location", F(t), Vector((x, y, gh(x, y) + dz))); key(H, "scale", F(t), Vector((2.4, 2.4, 2.4)))
SEARCH = empty("S_Search", (80, 30, 2))
for t, p in ((0, (80, 30, 2)), (26, (90, 30, 2)), (31, (150, -30, 2)), (36, (70, 50, 2)), (41, (140, 20, 2)), (46, (130, -25, 2)),
             (51, (95, -40, 2)), (55.6, (150, 5, 2)), (100, (150, 5, 2))):
    key(SEARCH, "location", F(t), Vector(p))
d1 = H.constraints.new("LOCKED_TRACK"); d1.target = T; d1.track_axis = "TRACK_NEGATIVE_Y"; d1.lock_axis = "LOCK_Z"
d2 = H.constraints.new("LOCKED_TRACK"); d2.target = SEARCH; d2.track_axis = "TRACK_NEGATIVE_Y"; d2.lock_axis = "LOCK_Z"
for t, v in ((0, 0.0), (24.0, 0.0), (27.0, 1.0), (55.6, 1.0), (56.3, 0.0)):
    d2.influence = v; d2.keyframe_insert("influence", frame=F(t))
gm = M("H_Green").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 0), (2.6, 0), (4.0, 60), (55.6, 60), (56.0, 140), (57.2, 80), (100, 60)):
    gm.default_value = e; gm.keyframe_insert("default_value", frame=F(t))
# our lights: out at 20.6 ("Lights off. Into the wheat!"), back on at 60.2 ("It heard us! Lights on! Full steam!")
L0, L1 = 20.6, 60.2
se = M("H_Signal").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 80), (L0 - 0.2, 80), (L0 + 0.8, 3), (L1 - 0.2, 3), (L1 + 0.4, 60), (100, 50)): se.default_value = e; se.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 6), (L0 - 0.2, 6), (L0 + 0.8, 0.3), (L1 - 0.2, 0.3), (L1 + 0.4, 4)): SIGL.data.energy = e; SIGL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 900), (L0 - 0.2, 900), (L0, 0), (L1, 0), (L1 + 0.3, 900)): HL.data.energy = e; HL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 45), (L0 - 0.2, 45), (L0 + 0.4, 18), (L1 - 0.2, 18), (L1 + 0.6, 45)): O["Fill"].data.energy = e; O["Fill"].data.keyframe_insert("energy", frame=F(t))
wi = M("H_Window").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 4), (L0 - 0.1, 4), (L0 + 0.2, 0.0), (L1, 0.0), (L1 + 0.3, 4)): wi.default_value = e; wi.keyframe_insert("default_value", frame=F(t))
fe = FIREM.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 12), (L0 - 0.2, 12), (L0 + 0.1, 0), (L1 - 0.2, 0), (L1 + 0.2, 20), (100, 14)): fe.default_value = e; fe.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 25), (L0 - 0.2, 25), (L0 + 0.1, 0), (L1 - 0.2, 0), (L1 + 0.2, 40), (100, 30)): FIRE.data.energy = e; FIRE.data.keyframe_insert("energy", frame=F(t))
# Rook head (rz = local direction + 30: 30 ahead, 120 left / north, -150 back, -60 right / south)
for t, rz in ((0, -150), (2.4, -150), (2.9, 30), (6.0, 30), (6.4, -150), (8.8, -150), (9.2, 30), (12.0, 30), (12.4, -150), (15.0, -150),
              (15.4, 30), (24.0, 30), (24.4, -120), (30.4, -120), (30.8, 30), (41.0, 30), (41.4, -80), (55.4, -80),
              (55.8, 30), (58.8, 30), (59.2, -80), (59.8, -80), (60.2, 30), (66.0, 30), (66.4, -150), (69.6, -150), (70.0, 30), (100, 30)):
    key(HP, "rotation_euler", F(t), math.radians(rz), 2)
for sd in (-1, 1):
    wg = O[f"R_Wing{sd}"]
    for t, a in ((0, 0), (0.6, 0), (0.9, 1.3), (1.3, 0.4), (1.7, 1.3), (2.6, 0), (6.0, 0), (6.3, 1.2), (8.2, 1.2), (8.6, 0),
                 (12.0, 0), (12.3, 1.2), (14.2, 1.2), (14.6, 0), (18.0, 0), (18.3, 1.4), (20.4, 1.4), (20.9, -0.6), (56.2, -0.6),
                 (56.6, 0.5), (58.6, 0.5), (59.0, -0.6), (59.6, -0.6), (59.9, 1.5), (62.4, 1.5), (62.8, 0), (76.6, 0), (76.9, 1.3),
                 (78.8, 1.3), (79.2, 0), (88.4, 0), (88.7, 1.0), (90.8, 1.0), (91.2, 0)):
        key(wg, "rotation_euler", F(t), math.radians(sd * 12) + sd * a * 0.6, 1)
for f in range(1, END, 12):
    if F(20.4) <= f <= F(60.4) or f >= F(95.0): continue
    key(R, "location", f, 0.62 + (0.02 if (f // 12) % 2 else 0.0), 2)

# ---------------- cameras (one per shot, bound to markers) ----------------
def cam(name, start_s, loc, look, lens=28, parent=None, world_look=False):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_end = 2000
    c = bpy.data.objects.new(name, cd); sc.collection.objects.link(c); c.location = loc
    if parent: c.parent = parent
    if isinstance(look, str): tgt = O[look]
    else:
        tgt = bpy.data.objects.new(name + "_T", None); sc.collection.objects.link(tgt); tgt.location = look; tgt.name = "Cam_T_" + name
        if parent and not world_look: tgt.parent = parent
    k = c.constraints.new("TRACK_TO"); k.target = tgt; k.track_axis = "TRACK_NEGATIVE_Z"; k.up_axis = "UP_Y"
    m = sc.timeline_markers.new(name, frame=F(start_s)); m.camera = c; return c
cam("Cam_01", 0, (2.6, -3.2, 1.8), (0.0, 0, 1.3), 28, T)                          # Rook: the lamps went out behind us
cam("Cam_02", 3.0, (6, 2.2, 3.4), "H_Mask", 70, T)                                 # over the train, back: its face rises over the ridge
cam("Cam_03", 6.0, (-40, -70, 30), (-150, 0, 8), 22)                              # high wide: the downs, the train and the Hush behind
cam("Cam_04", 10.0, (-4, 3.0, 2.8), "H_Mask", 28, T)                               # from the train: it is gaining
cam("Cam_05", 15.0, (14, -5, 1.4), (0, 0, 1.6), 30, T)                            # front: the train runs, the wheat ahead
cam("Cam_06", 17.6, (-3, -1.5, 2.8), (8, 0, 1), 26, T)                            # behind Rook: the wheat field! lights off
cam("Cam_07", 20.6, (76, -16, 2.0), (58, 0, 1.6), 26)                             # low at the field edge: the dark train goes into the wheat
cam("Cam_08", 23.4, (2.4, -2.6, 3.0), (0.6, 0, 1.45), 30, T)                      # over the wheat: Rook down low in it
cam("Cam_09", 27.0, (30, -70, 28), (80, -5, 2), 24)                               # high wide: the wheat sea, the dark line, the Hush at the edge
cam("Cam_10", 30.4, (2.4, -2.6, 3.0), (0.6, 0, 1.45), 30, T)                      # Rook: when the wind blows, we move
cam("Cam_11", 33.6, (90, -1.2, 3.0), "H_Mask", 24)                                # over the wheat tops: it wades into the field
cam("Cam_12", 35.8, (125, -45, 16), (95, 0, 1), 26)                               # high side: the wind waves, the dark train creeps
cam("Cam_13", 40.2, (2.4, -2.6, 3.0), (0.6, 0, 1.45), 30, T)                      # Rook: stop, wait for the wind
cam("Cam_14", 42.4, (125, -38, 6), "H_Mask", 30)                                  # it searches the field (the second gust)
cam("Cam_15", 45.6, (109, 0.9, 1.3), "H_Mask", 20)                                # low behind the train between the wheat: it towers over us
cam("Cam_16", 49.6, (0.2, 1.5, 0.9), "H_Mask", 20, T)                             # low behind Rook: its face right over us (cold open)
cam("Cam_17", 53.4, (7.5, -3.5, 3.4), (SX - 0.9, 0, 2.2), 32, T)                  # the whistle peeps: a little puff
cam("Cam_18", 56.4, (114, 18, 14), "H_Mask", 45)                                  # its face turns down to us
cam("Cam_19", 59.0, (2.4, -2.6, 3.0), (0.6, 0, 1.45), 28, T)                      # Rook: it heard us! lights on! full steam!
cam("Cam_20", 62.4, (8, -9, 3.2), (0, 0, 1.4), 26, T)                             # side: full steam through the wheat
cam("Cam_21", 66.0, (-4, 3.0, 3.2), "H_Mask", 30, T)                               # back: it follows through the wheat
cam("Cam_22", 70.0, (330, -40, 12), (285, 0, 1), 24)                              # wide: the end of the field, the train bursts out
cam("Cam_23", 76.2, (-3, -1.5, 2.8), (8, 0, 1), 26, T)                            # behind Rook: out of the wheat
cam("Cam_24", 80.0, (360, -30, 4), (300, -15, 8), 24)                             # low: it comes out of the wheat behind us
cam("Cam_25", 84.0, (-20, -14, 8), (30, 0, 2), 24, T)                             # Harvest Town ahead
cam("Cam_26", 88.0, (2.4, -3.2, 1.7), (0.6, 0, 1.35), 28, T)                      # Rook at the station
sc.camera = O["Cam_01"]
sc.render.resolution_x = 1280; sc.render.resolution_y = 720; sc.render.resolution_percentage = 100
sc.eevee.taa_render_samples = 24
try: sc.eevee.use_raytracing = False
except Exception: pass
sc.render.use_compositing = False; sc.render.use_sequencer = False
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "hush_film15.blend"))
print("film15 built", len(sc.collection.all_objects), "objects; markers", len(sc.timeline_markers))
