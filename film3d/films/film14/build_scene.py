# GLOAMRUN 3D Film 17 "The Sky Lanterns" — run INSIDE Blender (hush_lookdev.blend open, scene HUSH).
# Story (no calm start): the lamps behind die and its face rises over the ridge at once -> it is faster over the high meadow ->
# Rook's move: the wagon is full of festival lanterns for Lantern Town; he stops, lights them all and lets them go, puts out every
# light and the fire; the Hush can't fly, it turns to the thousand little lights going up and walks under them -> it stands right
# over the dark train looking up ('Don't move') -> surprise: one lantern comes back down and lands on our stack; it looks down at
# us -> lights on, full steam over the old stone viaduct to Lantern Town; it follows (it will come again).
import bpy, bmesh, math, random, os
from mathutils import Vector
OUT = r"C:\Users\81803\TremenFilm\hush\film14"; os.makedirs(OUT, exist_ok=True)
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


# ---------------- world: the high meadow, the lantern wagon, the old stone viaduct, Lantern Town ----------------
from mathutils import Matrix
rr = random.Random(1717)
X0 = -230.0                                    # the line runs straight east along y = 0 (x -230 .. 480)
MX = 94.0                                      # where the train stops on the meadow and lets the lanterns go
VA, VB = 298.0, 382.0                          # the old stone viaduct over the river valley
def ss(a, b, v):
    u = min(1.0, max(0.0, (v - a) / (b - a))); return u * u * (3 - 2 * u)
def pose(s): return (-150.0 + s, 0.0, 0.0)
def gh(x, y):
    n = 0.9 * math.sin(x * 0.045 + y * 0.03) + 0.6 * math.sin(x * 0.09 - y * 0.06 + 1.3)
    d = abs(y); up = ss(6, 70, d) * (7 + 3 * n) + ss(90, 180, d) * 18 + 0.3 * n * ss(8, 20, d)
    back = 24.0 * math.exp(-((x + 285.0) / 30.0) ** 2)               # the ridge at the back of the meadow
    vd = math.exp(-((x - (VA + VB) / 2) / 30.0) ** 4)               # the river valley under the viaduct
    return (up + back) * (1 - 0.8 * vd) - 34.0 * vd - 0.02
GA = O["Ground"]; GA.location = (0, 0, -70.0); GA.scale = (1400, 1000, 1)
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
GO = mk("S_MeadowGround", bm, grassM, smooth=True); GO.data.materials.append(rockM)
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
# the old stone viaduct: deck, low walls, piers with arches down to the river
stoneM = newM("S_Stone", (0.16, 0.14, 0.13), rough=1)
pb = [(((VA + VB) / 2, 0, -0.45), (VB - VA + 8, 3.2, 0.8), 0)]
for sd in (-1, 1): pb.append((((VA + VB) / 2, sd * 1.5, 0.35), (VB - VA + 8, 0.25, 0.8), 0))
x = VA
while x <= VB + 0.1:
    z0 = gh(x, 0); h = -0.8 - z0
    if h > 0.5: pb.append(((x, 0, z0 + h / 2), (2.6, 3.2, h), 0))
    x += 10.5
pboxes("S_Viaduct", stoneM, pb)
mk("S_RiverWater", box(), newM("S_Water", (0.04, 0.07, 0.11), emit=0.12, rough=0.05), ((VA + VB) / 2, 0, gh((VA + VB) / 2, 0) + 0.6), scl=(14, 500, 0.2))
# lamps along the line (die in a wave), lamps past the viaduct, Lantern Town
RLAMP = []
def lamp(tag, x, y, td, e=55):
    z = max(gh(x, y), 0.0); mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, y, z + 1.7))
    hm = newM(f"L_{tag}", (1, 0.62, 0.25), emit=8); mk(f"L_{tag}", sph(0.2, 12, 8), hm, (x, y, z + 3.45))
    RLAMP.append((hm, light(f"L_{tag}L", "POINT", e, (1, 0.6, 0.3), (x, y, z + 3.2)), td))
HX = [(6, -268), (10, -200), (14, -130), (18, -60), (22, 0), (26, 40), (30, 62), (34, 76)]
def h_time(x):
    for (ta, xa), (tb, xb) in zip(HX, HX[1:]):
        if xa <= x <= xb: return ta + (tb - ta) * (x - xa) / (xb - xa)
    return 34.0
for i, x in enumerate((-215, -195, -175, -158)): lamp(f"B{i}", x, -3.2, 0.2 + i * 0.55)       # the lamps behind die first
for i, x in enumerate((-130, -100, -70, -40, -10, 20, 50, 75)): lamp(f"V{i}", x, -3.2, h_time(x) - 0.6)
for i, x in enumerate((400, 418)): lamp(f"E{i}", x, -3.2, 999)
for i in range(5): lamp(f"St{i}", 436 + i * 9.0, 3.4, 999, 80)
treeM = newM("S_Pine", (0.02, 0.035, 0.025), rough=1); bm = bmesh.new()
for i in range(260):
    x = rr.uniform(-320, 470); y = rr.uniform(-170, 170)
    if abs(y) < 12 or (MX - 40 < x < MX + 30 and abs(y) < 40) or (VA - 10 < x < VB + 10 and abs(y) < 20): continue
    z0 = gh(x, y); h = rr.uniform(5, 10)
    g = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=7, radius1=h * 0.28, radius2=0.0, depth=h)["verts"]
    bmesh.ops.translate(bm, vec=(x, y, z0 + h / 2 + 0.6), verts=g)
mk("S_Pines", bm, treeM)
rocks, walls = [], []
for i in range(50):
    x = rr.uniform(-300, 460); y = rr.uniform(-140, 140)
    if abs(y) < 8: continue
    s = rr.uniform(0.6, 1.8); rocks.append(((x, y, gh(x, y) + s * 0.3), (s * 1.4, s, s * 0.9), rr.uniform(0, 3)))
for k in range(14):                                                      # old stone walls across the meadow
    y0 = rr.choice((-1, 1)) * rr.uniform(14, 70); x0 = rr.uniform(-280, 260); a = rr.uniform(-0.4, 0.4)
    for j in range(12):
        x = x0 + j * 2.0 * math.cos(a); y = y0 + j * 2.0 * math.sin(a)
        if abs(y) < 8 or VA - 20 < x < VB + 20: continue
        walls.append(((x, y, gh(x, y) + 0.35), (2.1, 0.5, 0.8), a))
pboxes("S_Rocks", rockM, rocks + walls)
farM = newM("S_FarPeak", (0.1, 0.11, 0.15), rough=1)
for i in range(9):
    hx = -320 + i * 100
    mk("S_FarPeak", cyl(1, 0.05, 1, 8), farM, (hx, rr.uniform(270, 310), 10), scl=(rr.uniform(55, 75), 45, rr.uniform(50, 80)))
    mk("S_FarPeak", cyl(1, 0.05, 1, 8), farM, (hx + 50, -rr.uniform(290, 330), 0), scl=(rr.uniform(55, 75), 45, rr.uniform(45, 70)))
houseM = newM("S_HouseM", (0.075, 0.07, 0.078), rough=1); roofM = newM("S_Roof", (0.25, 0.12, 0.09), rough=1)
winM = newM("S_Win", (1, 0.62, 0.25), emit=5)
for i in range(26):
    x = rr.uniform(400, 480); y = rr.choice((rr.uniform(12, 50), rr.uniform(-50, -12))); w = rr.uniform(3, 6); h = rr.uniform(2.5, 5)
    z0 = gh(x, y); sd = 1 if y > 0 else -1
    mk("S_House", box(), houseM, (x, y, z0 + h / 2 - 0.5), scl=(w, w, h)); mk("S_Roof", box(), roofM, (x, y, z0 + h - 0.4), scl=(w + 0.4, w + 0.4, 0.3))
    mk("S_Win", box(), winM, (x, y - sd * (w / 2 + 0.02), z0 + h * 0.45), scl=(0.6, 0.05, 0.7))
mk("S_Platform", box(), newM("S_Plat", (0.1, 0.09, 0.1), rough=1), (454, 2.4, 0.0), scl=(40, 2.2, 0.6))
TLM = newM("S_TownLan", (1, 0.3, 0.12), emit=9); bm = bmesh.new()             # strings of little lanterns over the platform
for i in range(40):
    x = 436 + i * 0.95; z = 3.4 - 0.5 * math.sin((i % 10) / 9 * math.pi)
    g = bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=6, radius=0.16)["verts"]; bmesh.ops.translate(bm, vec=(x, 3.4, z), verts=g)
mk("S_TownLanterns", bm, TLM)
moonM = newM("S_Moon", (0.9, 0.88, 0.8), emit=3)
mk("S_Moon", cyl(9, 9, 0.2, 48), moonM, (150, -380, 110), (math.pi / 2, 0, 0.0))
w = sc.world; w.node_tree.nodes["Background"].inputs[0].default_value = (0.014, 0.018, 0.045, 1)
O["MoonKey"].data.energy = 3.4
FIREM = newM("T_FireM", (1, 0.35, 0.08), emit=12)
mk("T_Fire", box(), FIREM, (2.45, 0, 0.55), scl=(0.06, 0.5, 0.3), parent=T)
FIRE = light("T_FireGlow", "POINT", 25, (1, 0.45, 0.15), (2.2, 0, 0.7), T)
# the lantern wagon behind the car (festival lanterns for Lantern Town)
woodM = newM("T_Wood", (0.16, 0.08, 0.04), rough=0.9)
mk("T_Wagon", box(), woodM, (-1.85, 0, 0.36), scl=(2.0, 0.95, 0.42), parent=T)
for sd in (-1, 1): mk("T_WagonSide", box(), woodM, (-1.85, sd * 0.47, 0.68), scl=(2.0, 0.06, 0.28), parent=T)
mk("T_Coupling", box(), postM, (-0.72, 0, 0.3), scl=(0.3, 0.12, 0.08), parent=T)
for k in range(4):
    wh = mk("T_WagonWheel", cyl(0.2, 0.2, 0.08, 14), postM, (-2.45 + (k // 2) * 1.2, (k % 2 - 0.5) * 1.0, 0.2), (math.pi / 2, 0, 0), parent=T)
PAPER = newM("T_Paper", (0.85, 0.6, 0.35), rough=0.8)
def lanmesh(r=1.0):
    return cyl(0.22 * r, 0.3 * r, 0.75 * r, 12)
bm = bmesh.new()
for k in range(10):
    g = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=10, radius1=0.17, radius2=0.22, depth=0.5)["verts"]
    bmesh.ops.translate(bm, vec=(-2.6 + (k % 5) * 0.37, -0.2 + (k // 5) * 0.4, 0.8), verts=g)
CRATES = mk("T_Crates", bm, PAPER, parent=T)

# ---------------- the Hush ----------------
H = O["Hush"]; H.scale = (2.4, 2.4, 2.4)
mask_spot = light("T_MaskLight", "SPOT", 9000, (0.7, 0.85, 1.0), (0, 0, 0)); mask_spot.data.spot_size = math.radians(18)
c = mask_spot.constraints.new("TRACK_TO"); c.target = O["H_Mask"]; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
mask_spot.parent = H; mask_spot.location = (2.0, -14, 4.0)

# ---------------- animation ----------------
SK = [(0, 0), (4, 44), (8, 90), (12, 135), (16, 178), (20, 216), (22, 234), (23.6, 244), (59.9, 244), (62, 252), (64, 266), (66, 286),
      (70, 332), (74, 382), (78, 432), (82, 482), (86, 530), (90, 572), (93, 596), (95, 604), (96.5, 605), (100, 605)]
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
# the lanterns: appear in the wagon (23.6), light up (24.4-26), go up one by one (26-36) and drift north on the wind
for o in (CRATES,):
    o.hide_render = False; o.keyframe_insert("hide_render", frame=1); o.hide_render = True; o.keyframe_insert("hide_render", frame=F(23.6))
LM = [newM(f"S_LanM{k}", (1, 0.28, 0.04), emit=0) for k in range(3)]   # warm gold (was blown white at emit 9)
for k, m in enumerate(LM):
    s = m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for t, e in ((0, 0), (24.4 + k * 0.5, 0), (24.9 + k * 0.5, 1.2)): s.default_value = e; s.keyframe_insert("default_value", frame=F(t))
WX = MX - 1.85                                                           # wagon centre (world) while stopped
LC = empty("S_LanternC", (WX, 0, 1))
for t, p in ((0, (WX, 0, 1)), (26, (WX, 0, 1.5)), (36, (WX - 1, 6, 16)), (46, (WX - 2, 12, 30)), (56, (WX - 4, 20, 42)),
             (70, (WX - 8, 34, 56)), (100, (WX - 16, 60, 80))):
    key(LC, "location", F(t), Vector(p))
lin(LC)
NL = 56
for i in range(NL):
    o = mk(f"S_Lan{i}", lanmesh(rr.uniform(0.9, 1.2)), LM[i % 3])
    p0 = Vector((WX + rr.uniform(-0.8, 0.8), rr.uniform(-0.3, 0.3), 0.9))
    tb = 26.0 + i * 0.18 + rr.uniform(0, 0.1); vz = rr.uniform(1.7, 2.6); zc = rr.uniform(30, 75)
    dx, dy = rr.uniform(-0.35, 0.25), rr.uniform(0.35, 0.9)
    o.hide_render = True; o.keyframe_insert("hide_render", frame=1); o.hide_render = False; o.keyframe_insert("hide_render", frame=F(23.6))
    key(o, "location", 1, p0); key(o, "location", F(tb), p0)
    t = tb
    while t < 100:
        t = min(100.0, t + 2.0); dt = t - tb
        z = p0.z + min(zc, vz * dt * (0.6 + 0.4 * min(1, dt / 4))); key(o, "location", F(t), p0 + Vector((dx * dt, dy * dt, z - p0.z)))
    o.rotation_euler = (rr.uniform(-0.1, 0.1), rr.uniform(-0.1, 0.1), 0)
    lin(o)
LGLOW = light("S_LanternGlow", "POINT", 0, (1, 0.6, 0.3), (0, 0, 0)); LGLOW.parent = LC; LGLOW.location = (0, 0, 2)
LGLOW.data.shadow_soft_size = 4.0
for t, e in ((0, 0), (24.4, 0), (26.0, 875), (46, 1400), (70, 1400), (90, 700)): LGLOW.data.energy = e; LGLOW.data.keyframe_insert("energy", frame=F(t))
# the one that comes back: rises with the others, drifts down and lands on the stack (55.4), rides it, blows off (63)
LB = mk("S_LanBack", lanmesh(1.1), LM[0])
LB.hide_render = True; LB.keyframe_insert("hide_render", frame=1); LB.hide_render = False; LB.keyframe_insert("hide_render", frame=F(23.6))
SX = 4.6                                                                 # stack (train-local x)
pts = [(0, (WX, 0, 0.9)), (26.1, (WX, 0, 0.9)), (32, (WX - 0.5, 3, 11)), (38, (WX - 1, 6, 20)), (44, (WX + 1, 7, 24)),
       (48, (WX + 3, 5, 18)), (51, (MX + 3.5, 2.5, 10)), (53.6, (MX + SX, 0.6, 4.0)), (55.4, (MX + SX, 0, 2.15))]
for k in range(10): t = 55.4 + k * 0.5; pts.append((t, (tx(t) + SX, 0, 2.15)))
t63 = 63.4; xb = tx(t63)
pts += [(t63, (xb + SX - 0.5, 0.3, 2.6)), (64.6, (xb, 1.5, 5)), (66, (xb - 6, 3, 10)), (70, (xb - 12, 6, 22)), (100, (xb - 30, 30, 60))]
for t, p in pts: key(LB, "location", F(t), Vector(p))
lin(LB)
BG = light("S_BackGlow", "POINT", 0, (1, 0.6, 0.3), (0, 0, 0)); cl = BG.constraints.new("COPY_LOCATION"); cl.target = LB
for t, e in ((0, 0), (24.4, 0), (24.9, 25), (50, 25), (55.4, 90), (63, 90), (68, 20)): BG.data.energy = e; BG.data.keyframe_insert("energy", frame=F(t))
# the Hush: rises over the back ridge (2.4-4.6), comes over the meadow faster than us, turns to the lanterns (30), walks under them
# and stands right over the dark train looking up (46-55.4); the lantern lands on the stack, it looks down at us; it follows.
HP_ = [(0, -280, -10, -40), (2.4, -280, -10, -40), (3.4, -280, -10, -14), (4.6, -280, -10, 0), (5.4, -278, -10, 0), (6, -268, -12, 0),
       (10, -200, -16, 0), (14, -130, -18, 0), (18, -60, -18, 0), (22, 0, -18, 0), (26, 40, -18, 0), (30, 62, -18, 0), (34, 76, -17, 0),
       (38, 85, -15, 0), (42, 91, -13.5, 0), (46, 95, -12.5, 0), (55.4, 96, -12, 0), (56.4, 96, -11.5, -0.4), (58, 96, -11.5, -0.4),
       (60, 98, -12, 0), (64, 132, -16, 0), (70, 190, -20, 0), (76, 250, -24, 0), (82, 310, -28, 0), (88, 362, -30, 0), (94, 412, -28, 0),
       (100, 450, -26, 0)]
for t, x, y, dz in HP_:
    key(H, "location", F(t), Vector((x, y, gh(x, y) + dz))); key(H, "scale", F(t), Vector((2.4, 2.4, 2.4)))
d1 = H.constraints.new("LOCKED_TRACK"); d1.target = T; d1.track_axis = "TRACK_NEGATIVE_Y"; d1.lock_axis = "LOCK_Z"
d2 = H.constraints.new("LOCKED_TRACK"); d2.target = LC; d2.track_axis = "TRACK_NEGATIVE_Y"; d2.lock_axis = "LOCK_Z"
for t, v in ((0, 0.0), (28.0, 0.0), (31.0, 1.0), (55.4, 1.0), (56.2, 0.0)):
    d2.influence = v; d2.keyframe_insert("influence", frame=F(t))
gm = M("H_Green").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 0), (2.6, 0), (4.0, 60), (55.4, 60), (55.8, 140), (57.0, 80), (100, 60)):
    gm.default_value = e; gm.keyframe_insert("default_value", frame=F(t))
# our lights: out at 30.8 ("Lights off. Not a sound."), back on at 60.0 ("It sees us! Lights on! Full steam!")
L0, L1 = 30.8, 60.2
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
# Rook head (rz = local direction + 30: 30 ahead, 120 left / north, -150 back / the wagon, -60 right / south)
for t, rz in ((0, -150), (2.4, -150), (2.9, 30), (6.0, 30), (6.4, -150), (8.8, -150), (9.2, 30), (12.2, 30), (12.6, -150), (15.0, -150),
              (15.4, 30), (18.0, 30), (18.4, -150), (29.4, -150), (29.8, 30), (33.0, 30), (33.4, 120), (39.0, 120), (39.4, -60), (55.2, -60),
              (55.6, 30), (58.8, 30), (59.2, -60), (59.8, -60), (60.2, 30), (66.0, 30), (66.4, -150), (69.6, -150), (70.0, 30), (100, 30)):
    key(HP, "rotation_euler", F(t), math.radians(rz), 2)
for sd in (-1, 1):
    wg = O[f"R_Wing{sd}"]
    for t, a in ((0, 0), (0.6, 0), (0.9, 1.3), (1.3, 0.4), (1.7, 1.3), (2.6, 0), (6.0, 0), (6.3, 1.2), (8.2, 1.2), (8.6, 0),
                 (12.4, 0), (12.7, 1.2), (14.6, 1.2), (15.0, 0), (18.4, 0), (18.7, 0.8), (20.6, 0.8), (21.0, 0), (23.8, 0), (24.1, 1.4),
                 (26.0, 1.4), (26.4, 0), (30.0, 0), (30.3, 1.3), (31.4, 1.3), (31.8, -0.6), (56.4, -0.6), (56.8, 0.5), (58.6, 0.5), (59.0, -0.6),
                 (59.6, -0.6), (59.9, 1.5), (62.4, 1.5), (62.8, 0), (76.6, 0), (76.9, 1.3), (78.8, 1.3), (79.2, 0), (88.4, 0), (88.7, 1.0),
                 (90.8, 1.0), (91.2, 0)):
        key(wg, "rotation_euler", F(t), math.radians(sd * 12) + sd * a * 0.6, 1)
for f in range(1, END, 12):
    if F(23.4) <= f <= F(60.4) or f >= F(95.0): continue
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
cam("Cam_03", 6.0, (-40, -70, 30), (-150, 0, 8), 22)                              # high wide: the meadow, the train and the Hush behind
cam("Cam_04", 10.0, (-4, 3.0, 2.8), "H_Mask", 28, T)                               # from the train: it is gaining
cam("Cam_05", 15.0, (14, -5, 1.4), (0, 0, 1.6), 30, T)                            # front: the train runs over the meadow
cam("Cam_06", 17.6, (1.4, -2.8, 2.0), (-1.2, 0, 0.9), 26, T)                      # Rook turns to the lantern wagon
cam("Cam_07", 21.6, (-1.0, -3.2, 2.0), (-1.7, 0, 1.0), 28, T)                     # the wagon: light them all, let them go
cam("Cam_08", 26.6, (MX + 20, -28, 3), (MX - 4, 4, 12), 24)                       # wide low: the lanterns go up from the train
cam("Cam_09", 29.6, (2.4, -2.6, 1.5), (0.6, 0, 1.45), 30, T)                      # Rook: lights off
cam("Cam_10", 33.0, (MX - 60, -80, 40), (MX - 20, 0, 15), 24)                     # high wide: the dark train, the lanterns, the Hush coming
cam("Cam_11", 36.2, (-0.6, -1.8, 1.2), (WX, 8, 22), 24, T, True)                  # low behind Rook: the lanterns high in the sky
cam("Cam_12", 39.6, (MX - 30, 30, 8), "H_Mask", 28)                               # the Hush under the lanterns, looking up
cam("Cam_13", 43.6, (2.4, -2.6, 1.5), (0.6, 0, 1.45), 30, T)                      # Rook in the dark
cam("Cam_14", 45.6, (MX + 6, 6, 1.2), "H_Mask", 20)                               # low behind the train: it towers over us
cam("Cam_15", 49.6, (0.2, 1.5, 0.9), "H_Mask", 20, T)                             # low behind Rook: its face right over us (cold open)
cam("Cam_16", 53.2, (MX + 24, 18, 6), (MX + 3, -2, 5), 28)                        # side: one lantern comes down onto the stack
cam("Cam_17", 56.0, (MX + 8, 20, 14), "H_Mask", 45)                               # its face turns down to us
cam("Cam_18", 59.0, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)                       # Rook: lights on! full steam!
cam("Cam_19", 62.4, (8, -9, 3), (0, 0, 1.4), 26, T)                               # side: full steam, the lantern blows off
cam("Cam_20", 66.0, (-4, 3.0, 2.6), "H_Mask", 30, T)                               # back: it follows
cam("Cam_21", 70.0, (400, -90, 30), (330, 0, -4), 24)                             # wide: the old stone viaduct, the train comes
cam("Cam_22", 76.2, (-3, -1.5, 2.8), (8, 0, 1), 26, T)                            # behind Rook: over the old bridge
cam("Cam_23", 79.4, (350, -50, -14), (335, 0, -2), 22)                            # low under the viaduct: the train above, it in the valley
cam("Cam_24", 84.0, (-20, -14, 8), (30, 0, 2), 24, T)                             # Lantern Town ahead
cam("Cam_25", 88.0, (2.4, -3.2, 1.7), (0.6, 0, 1.35), 28, T)                      # Rook at the station
sc.camera = O["Cam_01"]
sc.render.resolution_x = 1280; sc.render.resolution_y = 720; sc.render.resolution_percentage = 100
sc.eevee.taa_render_samples = 24
try: sc.eevee.use_raytracing = False
except Exception: pass
sc.render.use_compositing = False; sc.render.use_sequencer = False
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "hush_film14.blend"))
print("film14 built", len(sc.collection.all_objects), "objects; markers", len(sc.timeline_markers))
