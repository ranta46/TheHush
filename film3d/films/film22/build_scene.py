# GLOAMRUN 3D Film 27 "The Storm" — run INSIDE Blender (hush_lookdev.blend open, scene HUSH).
# Story (no calm start): the heath lamps die and its face rises behind us -> by 8 s it is right at the last car (Rook flinches) -> full steam
# -> a dry storm ahead; the first lightning hits the heath and the Hush STOPS and turns to eat the light -> Rook's move: lights out, and the
# train moves ONLY while the lightning flashes (it is busy eating the light), and stands still and dark between ("We go only when it
# flashes.") -> no flash for a long time; it walks right up beside the dark train ('...Don't move.') -> surprise: the lightning hits the old
# iron signal right behind it; it bends down to eat the fire -> 'Lights on! Full steam!' to Stone Town. It stands far behind (it will be back).
import bpy, bmesh, math, random, os
from mathutils import Vector
OUT = r"C:\Users\81803\TremenFilm\hush\film22"; os.makedirs(OUT, exist_ok=True)
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
# ---------------- world: the open stone heath, a dry storm, the old iron signal, Stone Town ----------------
from mathutils import Matrix
rr = random.Random(2727)
def ss(a, b, v):
    if b < a: return 1.0 - ss(b, a, v)
    u = min(1.0, max(0.0, (v - a) / (b - a))); return u * u * (3 - 2 * u)
def gh(x, y):
    n = 0.9 * math.sin(x * 0.05 + y * 0.03) + 0.6 * math.sin(x * 0.11 - y * 0.07 + 1.3)
    ay = abs(y)
    z = 0.45 * n * ss(4, 16, ay) + 6.0 * ss(45, 170, ay) * (0.55 + 0.45 * math.sin(x * 0.012 + 0.8))
    z = max(z, 30.0 * ss(240, 330, ay) * (0.8 + 0.2 * math.sin(x * 0.02)))
    if ay < 2.6: z = min(z, -0.06)
    return z
GA = O["Ground"]; GA.location = (0, 0, -30.0); GA.scale = (1400, 1000, 1)
grassM = newM("S_Heath", (0.05, 0.042, 0.035), rough=1)
GA.data.materials.clear(); GA.data.materials.append(grassM)
def axis(a, b, step):
    out = []; v = a
    while v <= b + 1e-6: out.append(v); v += step
    return out
xs = axis(-460, -42, 8) + axis(-40, 140, 2.5) + axis(144, 520, 4) + axis(528, 700, 8)
ys = axis(-340, -62, 8) + axis(-60, -8, 2.5) + axis(-7.5, 7.5, 0.5) + axis(8, 60, 2.5) + axis(64, 340, 6)
bm = bmesh.new(); vv = [[bm.verts.new((x, y, gh(x, y))) for y in ys] for x in xs]
for i in range(len(xs) - 1):
    for j in range(len(ys) - 1):
        bm.faces.new((vv[i][j], vv[i + 1][j], vv[i + 1][j + 1], vv[i][j + 1]))
GO = mk("S_Ground", bm, grassM, smooth=True)
railM = newM("S_RailM", (0.2, 0.2, 0.22), rough=0.4, metal=0.8); tie = newM("S_Tie", (0.05, 0.04, 0.035), rough=1)
postM = newM("S_Post", (0.02, 0.02, 0.025), rough=0.5)
def pboxes(name, mat, items, parent=None):
    bm = bmesh.new()
    for loc, scl, rzz in items:
        g = bmesh.ops.create_cube(bm, size=1.0)["verts"]; bmesh.ops.scale(bm, vec=scl, verts=g)
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(rzz, 3, "Z"), verts=g); bmesh.ops.translate(bm, vec=loc, verts=g)
    return mk(name, bm, mat, parent=parent)
X0, X1 = -330.0, 398.0
pboxes("S_Rails", railM, [(((X0 + X1) / 2, sd * 0.53, 0.03), (X1 - X0, 0.08, 0.06), 0) for sd in (-1, 1)])
pboxes("S_Ties", tie, [((x, 0, -0.02), (0.25, 1.4, 0.06), 0) for x in axis(X0, X1, 2.0)])
pboxes("S_EndStop", newM("S_Red", (0.6, 0.05, 0.03), rough=0.5), [((X0 + 2, 0, 0.4), (0.3, 1.8, 0.5), 0), ((X1 - 1, 0, 0.4), (0.3, 1.8, 0.5), 0)])
# standing stones on the heath + an old stone ring north of the line
stoneM = newM("S_StoneM", (0.16, 0.155, 0.15), rough=0.95)
items = []
for i in range(90):
    x = rr.uniform(-420, 330); y = rr.choice((-1, 1)) * rr.uniform(10, 160)
    h = rr.uniform(1.8, 4.6); items.append(((x, y, gh(x, y) + h / 2 - 0.3), (rr.uniform(0.7, 1.4), rr.uniform(0.5, 1.0), h), rr.uniform(0, 3)))
for k in range(13):
    a = k / 13 * 2 * math.pi; x = 30 + 15 * math.cos(a); y = 40 + 15 * math.sin(a); h = rr.uniform(3.0, 4.4)
    items.append(((x, y, gh(x, y) + h / 2 - 0.3), (1.3, 0.8, h), a))
pboxes("S_Stones", stoneM, items)
# the old iron signal by the line (the lightning will hit it)
SPX, SPY = 64.0, -16.0
ironM = newM("S_Iron", (0.06, 0.06, 0.065), rough=0.5, metal=0.7)
mk("S_SignalPost", cyl(0.18, 0.12, 9.0, 10), ironM, (SPX, SPY, gh(SPX, SPY) + 4.5))
mk("S_SignalArm", box(), ironM, (SPX + 0.9, SPY, gh(SPX, SPY) + 8.2), scl=(1.9, 0.12, 0.35))
FIRE2M = newM("S_PostFireM", (1, 0.45, 0.12), emit=0)
PFIRE = mk("S_PostFire", sph(0.7, 12, 8), FIRE2M, (SPX, SPY, gh(SPX, SPY) + 9.2))
RLAMP = []
def lamp(tag, x, y, td, e=55, z=None):
    z = gh(x, y) if z is None else z; mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, y, z + 1.7))
    hm = newM(f"L_{tag}", (1, 0.62, 0.25), emit=8); mk(f"L_{tag}", sph(0.2, 12, 8), hm, (x, y, z + 3.45))
    lo = light(f"L_{tag}L", "POINT", e, (1, 0.6, 0.3), (x, y, z + 3.2)); RLAMP.append((hm, lo, td)); return hm, lo
PF = light("S_PostFireL", "POINT", 0, (1, 0.5, 0.15), (SPX, SPY, gh(SPX, SPY) + 9.6))
# the Hush: (t, x, y, dz) ; z = ground + dz
HP_ = [(0, -268, -6, -40), (2.4, -268, -6, -40), (3.4, -268, -6, -16), (4.4, -266, -6, 0), (8.0, -185, -3, 0), (9.4, -167, -3, 0),
       (14, -112, -5, 0), (19, -45, -6, 0), (20.0, -40, -6, 0), (22.4, -40, -6, 0), (26.4, -8, -8, 0), (27.8, -5, -8, 0),
       (31.0, 12, -10, 0), (32.8, 14, -10, 0), (35.5, 32, -12, 0), (37.4, 34, -12, 0), (40.0, 48, -11, 0), (41.6, 50, -11, 0),
       (45.0, 72, -9, 0), (48.0, 74, -8.5, 0), (52.8, 73, -9, 0), (54.4, 73, -9, 0), (55.8, 74, -9, 0), (57.0, 72, -10, 0),
       (58.0, 68, -13, -4), (59.0, 67, -13.5, -6), (64.5, 67, -13.5, -6), (66, 69, -12, 0), (68, 90, -8, 0), (72, 130, -6, 0),
       (76, 165, -6, 0), (80, 195, -6, 0), (84, 215, -6, 0), (86, 220, -6, 0), (100, 220, -6, 0)]
def h_x(x):
    for (ta, xa, *_), (tb, xb, *_) in zip(HP_[3:8], HP_[4:8]):
        if xa <= x <= xb and xb > xa: return ta + (tb - ta) * (x - xa) / (xb - xa)
    return 999.0
for i, x in enumerate((-300, -285, -270)): lamp(f"B{i}", x, -3.2, 0.2 + i * 0.5)               # the heath lamps behind die first
for i, x in enumerate((-140, -100, -60)): lamp(f"V{i}", x, -3.2, h_x(x) + 0.4)
for i, x in enumerate((250, 300)): lamp(f"K{i}", x, 3.2, 999, 55)
for i in range(5): lamp(f"St{i}", 345 + i * 11.0, 3.4, 999, 80)
# Stone Town
houseM = newM("S_HouseM", (0.2, 0.2, 0.22), rough=1); roofM = newM("S_Roof", (0.25, 0.12, 0.09), rough=1)
winM = newM("S_Win", (1, 0.62, 0.25), emit=5)
for i in range(34):
    x = rr.uniform(320, 450); y = rr.choice((-1, 1)) * rr.uniform(9, 55); w = rr.uniform(3, 6); h = rr.uniform(2.5, 5); z0 = gh(x, y)
    mk("S_House", box(), houseM, (x, y, z0 + h / 2 - 0.5), scl=(w, w, h)); mk("S_Roof", box(), roofM, (x, y, z0 + h - 0.4), scl=(w + 0.4, w + 0.4, 0.3))
    mk("S_Win", box(), winM, (x, y - (w / 2 + 0.02) * (1 if y > 0 else -1), z0 + h * 0.45), scl=(0.6, 0.05, 0.7))
mk("S_Platform", box(), newM("S_Plat", (0.1, 0.09, 0.1), rough=1), (370, 1.9, 0.3), scl=(60, 1.6, 0.6))
# far hills
farM = newM("S_FarPeak", (0.1, 0.11, 0.15), rough=1)
for i in range(9):
    mk("S_FarPeak", cyl(1, 0.05, 1, 8), farM, (rr.uniform(600, 760), -420 + i * 110, 20), scl=(70, rr.uniform(70, 95), rr.uniform(40, 70)))
# the moon low in the south-west, the storm clouds over the heath (no shadows from clouds)
EL = math.radians(22.0); AZ = math.radians(35)
moonM = newM("S_Moon", (0.9, 0.9, 0.85), emit=4)
mk("S_Moon", cyl(24, 24, 0.2, 48), moonM, (-800 * math.cos(AZ), -800 * math.sin(AZ), 800 * math.tan(EL)), (math.pi / 2, 0, math.pi / 2 + AZ))
cloudM = newM("S_CloudM", (0.03, 0.033, 0.045), rough=1)
cn = cloudM.node_tree.nodes["Principled BSDF"]; cn.inputs["Emission Color"].default_value = (0.55, 0.6, 0.85, 1)
CLOUDS = []
for i in range(46):
    x = rr.uniform(-250, 480); y = rr.uniform(-60, 320) if rr.random() < 0.7 else rr.uniform(-300, -60)
    if x < -120 and y < 0: continue                                       # keep the moon side open
    c = mk("S_Cloud", sph(1, 14, 8), cloudM, (x, y, rr.uniform(75, 105)), scl=(rr.uniform(35, 70), rr.uniform(25, 50), rr.uniform(6, 12)), smooth=True)
    c.visible_shadow = False; CLOUDS.append(c)
w = sc.world; BG = w.node_tree.nodes["Background"].inputs[0]; BG.default_value = (0.016, 0.02, 0.05, 1)
MK = O["MoonKey"]; MK.data.energy = 3.0; MK.data.color = (0.75, 0.82, 1.0); MK.rotation_euler = (0, EL - math.pi / 2, AZ)
try: MK.data.use_shadow = True; MK.data.angle = math.radians(0.6)
except Exception: pass
FLASH = light("S_Flash", "SUN", 0, (0.8, 0.85, 1.0), (0, 0, 100)); FLASH.rotation_euler = (math.radians(18), 0, math.radians(200))
FIREM = newM("T_FireM", (1, 0.35, 0.08), emit=12)
mk("T_Fire", box(), FIREM, (2.45, 0, 0.55), scl=(0.06, 0.5, 0.3), parent=T)
FIRE = light("T_FireGlow", "POINT", 25, (1, 0.45, 0.15), (2.2, 0, 0.7), T)
# lightning: (t0, x, y, strength, sub-flashes)
STRIKES = [(17.4, 420, 130, 0.5, 1), (20.0, -50, -150, 1.0, 2), (26.5, 60, 190, 1.0, 3), (31.0, 140, -170, 1.0, 3), (35.5, 20, 210, 1.0, 3),
           (40.0, 190, 160, 1.0, 2), (52.8, 230, -190, 0.7, 2), (56.6, SPX, SPY, 1.6, 3), (66.0, -150, 230, 0.4, 1), (75.0, -260, -210, 0.3, 1)]
boltM = []
def bolt(i, x, y, ztop, zbot, th):
    m = newM(f"S_BoltM{i}", (0.75, 0.82, 1.0), emit=0); bm = bmesh.new(); r2 = random.Random(100 + i)
    pts = [Vector((x, y, ztop))]; n = 9
    for k in range(1, n + 1):
        u = k / n; j = 0 if k == n else 1
        pts.append(Vector((x + j * r2.uniform(-1, 1) * (ztop - zbot) * 0.06, y + j * r2.uniform(-1, 1) * (ztop - zbot) * 0.06, ztop + (zbot - ztop) * u)))
    segs = list(zip(pts, pts[1:]))
    a = pts[3]; segs.append((a, a + Vector((r2.uniform(-1, 1) * 14, r2.uniform(-1, 1) * 14, -(ztop - zbot) * 0.22))))
    for p, q in segs:
        d = q - p; g = bmesh.ops.create_cube(bm, size=1.0)["verts"]; bmesh.ops.scale(bm, vec=(th, th, d.length), verts=g)
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix(), verts=g)
        bmesh.ops.translate(bm, vec=(p + q) / 2, verts=g)
    o = mk(f"S_Bolt{i}", bm, m); o.visible_shadow = False; boltM.append((o, m)); return o
for i, (t0, x, y, s, n) in enumerate(STRIKES):
    zb = gh(x, y) + 9.2 if i == 7 else gh(x, y)
    bolt(i, x, y, 95, zb, 0.45 if i == 7 else 1.3)
PAT = [1.0, 0.35, 0.9, 0.25, 0.12, 0.7, 0.45, 0.25, 0.15, 0.08, 0.04, 0.0]
def lvl(i, f):
    t0, x, y, s, n = STRIKES[i]; v = 0.0
    for k in range(n):
        j = f - F(t0 + k * 0.75)
        if 0 <= j < len(PAT): v = max(v, PAT[j])
    return s * v
KF = set([1, END])
for t0, x, y, s, n in STRIKES:
    for k in range(n):
        for j in range(-1, len(PAT) + 1): KF.add(F(t0 + k * 0.75) + j)
KF = sorted(f for f in KF if 1 <= f <= END)
cl = cn.inputs["Emission Strength"]
for f in KF:
    L = min(2.0, sum(lvl(i, f) for i in range(len(STRIKES))))
    FLASH.data.energy = 2.2 * L; FLASH.data.keyframe_insert("energy", frame=f)
    BG.default_value = (0.016 + 0.05 * L, 0.02 + 0.055 * L, 0.05 + 0.09 * L, 1); BG.keyframe_insert("default_value", frame=f)
    cl.default_value = 0.7 * L; cl.keyframe_insert("default_value", frame=f)
    for i, (o, m) in enumerate(boltM):
        li = lvl(i, f); e = m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
        e.default_value = 60 * li; e.keyframe_insert("default_value", frame=f)
        o.hide_render = li < 0.03; o.keyframe_insert("hide_render", frame=f)
        o.hide_viewport = False
# the struck signal burns (56.7) and the Hush eats the fire (59 -> 64.5)
fs2 = FIRE2M.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e, pe in ((0, 0, 0), (56.65, 0, 0), (56.8, 30, 900), (59.0, 22, 600), (62.0, 10, 250), (64.5, 0, 0), (100, 0, 0)):
    fs2.default_value = e; fs2.keyframe_insert("default_value", frame=F(t)); PF.data.energy = pe; PF.data.keyframe_insert("energy", frame=F(t))

# ---------------- the Hush ----------------
H = O["Hush"]; H.scale = (2.4, 2.4, 2.4)
mask_spot = light("T_MaskLight", "SPOT", 9000, (0.7, 0.85, 1.0), (0, 0, 0)); mask_spot.data.spot_size = math.radians(18)
c = mask_spot.constraints.new("TRACK_TO"); c.target = O["H_Mask"]; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
mask_spot.parent = H; mask_spot.location = (2.0, -14, 4.0)

# ---------------- animation ----------------
TK = [(0, -262), (4.6, -212), (8, -172), (9.6, -152), (14, -90), (19.6, -20), (22.6, 8), (24.6, 18), (25.4, 20),
      (26.5, 20), (27.0, 22), (28.2, 34), (28.8, 36), (31.0, 36), (31.5, 38), (32.7, 50), (33.3, 52),
      (35.5, 52), (36.0, 54), (37.2, 64), (37.6, 65), (40.0, 65), (40.4, 67), (41.4, 75), (41.8, 76),
      (52.8, 76), (53.3, 78), (54.0, 84), (54.4, 85), (59.8, 85), (61, 90), (62.6, 104), (64, 122), (66, 150), (70, 205),
      (76, 290), (80, 345), (83, 378), (84.6, 386), (100, 386)]
def ip(K, t):
    for (ta, sa), (tb, sb) in zip(K, K[1:]):
        if ta <= t <= tb:
            u = (t - ta) / (tb - ta) if tb > ta else 0; return sa + (sb - sa) * u
    return K[-1][1] if t > K[0][0] else K[0][1]
def tpos(t):
    return Vector((ip(TK, t), 0, 0))
LOOKW = [(20.0, 22.4, 1), (26.5, 28.6, 2), (31.0, 33.0, 3), (35.5, 37.5, 4), (40.0, 41.6, 5), (52.8, 54.6, 6), (56.6, 65.0, 7)]
HT = empty("V_HushLook"); hv = None
for f in range(1, END + 1):
    t = (f - 1) / FPS; p = tpos(t)
    key(T, "location", f, p)
    want = p
    for a, b, i in LOOKW:
        if a <= t < b: want = Vector((STRIKES[i][1], STRIKES[i][2], 3))
    if 25.4 <= t < 52.8 and want is p and not (44.0 <= t < 49.0):
        want = p + Vector((14 * math.sin(0.9 * t), 10 * math.cos(0.7 * t), 0))
    hv = Vector(want) if hv is None else hv + (Vector(want) - hv) * 0.16
    key(HT, "location", f, hv)
lin(T); lin(HT)
for hm, lt, td in RLAMP:
    if td > 150: continue
    s = hm.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for t, e in ((0, 8), (td - 0.01, 8), (td + 0.15, 0)): s.default_value = e; s.keyframe_insert("default_value", frame=F(max(t, 0)))
    e0 = lt.data.energy
    for t, e in ((0, e0), (td - 0.01, e0), (td + 0.15, 0)): lt.data.energy = e; lt.data.keyframe_insert("energy", frame=F(max(t, 0)))
for t, x, y, dz in HP_:
    key(H, "location", F(t), Vector((x, y, gh(x, y) + dz))); key(H, "scale", F(t), Vector((2.4, 2.4, 2.4)))
d1 = H.constraints.new("LOCKED_TRACK"); d1.target = HT; d1.track_axis = "TRACK_NEGATIVE_Y"; d1.lock_axis = "LOCK_Z"
gm = M("H_Green").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
gk = [(0, 0), (2.6, 0), (4.0, 60), (7.4, 60), (8.0, 140), (9.6, 70)]
for a, b, i in LOOKW: gk += [(a + 0.1, 70), (a + 0.4, 150), (b - 0.3, 150), (b, 70)]
gk += [(100, 60)]
for t, e in gk: gm.default_value = e; gm.keyframe_insert("default_value", frame=F(t))
# our lights: put out by Rook at 23.4 ("Lights out."), lit again at 59.8 ("Lights on! Full steam!")
L0, L1 = 23.4, 59.8
se = M("H_Signal").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 80), (L0, 80), (L0 + 0.6, 3), (L1 - 0.2, 3), (L1 + 0.4, 60), (100, 50)): se.default_value = e; se.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 6), (L0, 6), (L0 + 0.6, 0.3), (L1 - 0.2, 0.3), (L1 + 0.4, 4)): SIGL.data.energy = e; SIGL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 900), (L0, 900), (L0 + 0.4, 0), (L1, 0), (L1 + 0.3, 900)): HL.data.energy = e; HL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 45), (L0, 45), (L0 + 0.6, 22), (L1 - 0.2, 22), (L1 + 0.6, 45)): O["Fill"].data.energy = e; O["Fill"].data.keyframe_insert("energy", frame=F(t))
wi = M("H_Window").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 4), (L0, 4), (L0 + 0.5, 0.0), (L1, 0.0), (L1 + 0.3, 4)): wi.default_value = e; wi.keyframe_insert("default_value", frame=F(t))
fe = FIREM.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 12), (L0, 12), (L0 + 1.0, 1.0), (L1 - 0.2, 1.0), (L1 + 0.2, 20), (100, 14)): fe.default_value = e; fe.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 25), (L0, 25), (L0 + 1.0, 2), (L1 - 0.2, 2), (L1 + 0.2, 40), (100, 30)): FIRE.data.energy = e; FIRE.data.keyframe_insert("energy", frame=F(t))
# Rook head (rz = local direction + 30: 30 ahead, 120 left, -150 back, -60 right). The Hush comes up on the right (-y).
for t, rz_ in ((0, -150), (3.0, -150), (3.4, 30), (5.0, 30), (5.4, -150), (9.8, -150), (10.2, 30), (19.8, 30), (20.2, -150), (41.2, -150),
               (41.8, -60), (59.2, -60), (59.6, 30), (68.0, 30), (68.4, -150), (73.6, -150), (74.0, 30), (87.6, 30), (88.2, -150), (100, -150)):
    key(HP, "rotation_euler", F(t), math.radians(rz_), 2)
WUP = [(0.6, 1.3), (10.4, 1.2), (16.6, 1.0), (21.0, 1.2), (57.8, 1.4), (59.8, 1.5), (69.0, 1.2), (76.4, 1.3)]
for sd in (-1, 1):
    wg = O[f"R_Wing{sd}"]; ks = [(0, 0)]
    for t, a in WUP: ks += [(t, 0), (t + 0.3, a), (t + 1.6, a), (t + 1.9, 0)]
    ks += [(7.9, 0), (8.05, 1.7), (9.4, 1.6), (9.8, 0)]                          # flinch: it's at the last car
    ks += [(25.7, 0), (26.1, -0.6), (57.3, -0.6), (57.7, 0)]                     # small and still in the dark
    for t, a in sorted(ks): key(wg, "rotation_euler", F(t), math.radians(sd * 12) + sd * a * 0.6, 1)
for f in range(1, END, 12):
    if F(7.6) <= f <= F(8.8) or F(23.0) <= f <= F(59.8) or f >= F(84.6): continue
    key(R, "location", f, 0.62 + (0.02 if (f // 12) % 2 else 0.0), 2)
for t, z in ((7.6, 0.62), (8.05, 0.76), (8.4, 0.6), (8.8, 0.62)): key(R, "location", F(t), z, 2)

# ---------------- cameras (one per shot, bound to markers) ----------------
def cam(name, start_s, loc, look, lens=28, parent=None, world_look=False, free=False):
    if parent is None and not free: loc = (loc[0], loc[1], max(loc[2], gh(loc[0], loc[1]) + 2.0))
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_end = 2000; cd.clip_start = 0.05
    c = bpy.data.objects.new(name, cd); sc.collection.objects.link(c); c.location = loc
    if parent: c.parent = parent
    if isinstance(look, str): tgt = O[look]
    else:
        tgt = bpy.data.objects.new(name + "_T", None); sc.collection.objects.link(tgt); tgt.location = look; tgt.name = "Cam_T_" + name
        if parent and not world_look: tgt.parent = parent
    k = c.constraints.new("TRACK_TO"); k.target = tgt; k.track_axis = "TRACK_NEGATIVE_Z"; k.up_axis = "UP_Y"
    m = sc.timeline_markers.new(name, frame=F(start_s)); m.camera = c; return c
cam("Cam_01", 0, (2.6, -3.2, 1.8), (0.0, 0, 1.3), 28, T)                          # Rook: the heath lamps went dark
cam("Cam_02", 2.6, (6, 2.2, 3.4), "H_Mask", 55, T)                                 # over the train, back: its face rises
cam("Cam_03", 5.0, (-8, -34, 3), (-12, 0, 10), 18, T)                             # side wide: it catches up, right behind the last car
cam("Cam_03b", 7.8, (3.0, -1.5, 0.8), (-4, 0, 7), 16, T)                          # low on Rook: it is at the last car (flinch)
cam("Cam_04", 10.2, (-95, -45, 16), (-125, 0, 4), 24)                            # high wide: full steam, it behind
cam("Cam_05", 14.0, (-40, -24, 6), (-85, 0, 8), 24)                               # it walks after us, the lamps die
cam("Cam_06", 16.4, (-3, -2.2, 2.6), (14, 0.6, 4.0), 30, T)                       # over Rook: the storm ahead, a far flash
cam("Cam_07", 19.0, (-75, -45, 7), (-40, -6, 14), 22)                             # the first lightning: it stops and turns to the light
cam("Cam_08", 21.0, (2.4, -1.7, 1.5), (0.6, 0, 1.3), 26, T)                       # Rook: it eats the lightning
cam("Cam_08b", 23.2, (2.2, 2.4, 1.2), (0.6, 0, 1.3), 26, T)                       # Rook: lights out, we go only when it flashes
cam("Cam_09", 25.8, (45, -48, 16), (20, 10, 10), 22)                              # wide: flash -> the dark train runs, it looks away
cam("Cam_10", 29.4, (58, 4, 2.0), "H_Mask", 30, None, free=True)                # in front of the dark train: it searches behind us
cam("Cam_11", 32.8, (55, 45, 10), (40, -5, 8), 20)                                # flash, go! dark, stop.
cam("Cam_12", 34.4, (2.6, -1.7, 1.4), (0.6, 0, 1.35), 24, T)                      # Rook counts the flashes
cam("Cam_13", 37.4, (20, 60, 30), (60, -5, 4), 24)                                # high: it walks closer in the dark
cam("Cam_14", 41.4, (88, 14, 2.4), (72, -6, 9), 20)                               # no flash: it comes right up beside the dark train
cam("Cam_15", 44.4, (94, 8, 2.5), (75, -5, 12.5), 20, None, free=True)               # low by the train, up at its face (cold open)
cam("Cam_16", 48.4, (2.2, 2.4, 1.2), (0.6, 0, 1.3), 26, T)                        # Rook in the dark, it right behind him
cam("Cam_17", 51.2, (40, 40, 30), (76, -5, 4), 26)                                # high: come on, storm... a flash, we creep on
cam("Cam_18", 55.0, (40, -40, 7), (66, -12, 10), 22)                             # the lightning hits the old signal behind it
cam("Cam_19", 58.4, (2.6, -1.7, 1.4), (0.6, 0, 1.35), 24, T)                      # Rook: lights on, full steam
cam("Cam_20", 60.6, (30, -50, 8), (72, -8, 8), 22)                              # we run, it bends down to eat the fire
cam("Cam_21", 64.6, (150, 45, 28), (190, 0, 4), 26)                               # high: the train on the heath
cam("Cam_22", 68.6, (6, -3.0, 3.5), (0, 0, 1.5), 24, T)                           # side: keep the fire hot
cam("Cam_23", 72.6, (320, -22, 10), (230, 0, 8), 22)                              # front: the train comes, it far behind
cam("Cam_24", 76.2, (-3, -2.2, 2.6), (14, 0, 2.0), 26, T)                         # over Rook: Stone Town ahead
cam("Cam_25", 80.6, (2.4, -3.2, 1.7), (0.6, 0, 1.35), 28, T)                      # Rook at the station
cam("Cam_26", 85.4, (420, 26, 18), (330, -10, 14), 26)                            # the lit station, it far behind on the heath
sc.camera = O["Cam_01"]
sc.render.resolution_x = 1280; sc.render.resolution_y = 720; sc.render.resolution_percentage = 100
sc.eevee.taa_render_samples = 24
try: sc.eevee.use_raytracing = False
except Exception: pass
sc.render.use_compositing = False; sc.render.use_sequencer = False
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "hush_film22.blend"))
print("film22 built", len(sc.collection.all_objects), "objects; markers", len(sc.timeline_markers))
