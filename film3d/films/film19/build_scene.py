# GLOAMRUN 3D Film 22 "The Needle" — run INSIDE Blender (hush_lookdev.blend open, scene HUSH).
# Story (no calm start): the moor lamps die and its face rises behind us -> it is faster on the open moor -> Rook's move: he takes the old
# line into the Needle, a rock gorge too narrow for the Hush ("It's too big to come in") -> it stops at the walls, climbs up and walks
# along the rim looking down -> the Bowl, where the gorge opens: it walks down in; lights out by the big rock ('...Don't move.')
# -> it goes back -> surprise: a drop falls on the hot boiler, HISS, it turns -> full steam into the narrow Needle again; it climbs out
# and follows on the rim, but at the end the Needle is a high cliff over Reed Town: it can't climb down. It stands up there (it will be back).
import bpy, bmesh, math, random, os
from mathutils import Vector
OUT = r"C:\Users\81803\TremenFilm\hush\film19"; os.makedirs(OUT, exist_ok=True)
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







# ---------------- world: the night moor, the Needle (a narrow rock gorge through a high plateau), the Bowl, Reed Town by the lake ----------------
from mathutils import Matrix
rr = random.Random(2222)
def ss(a, b, v):
    if b < a: return 1.0 - ss(b, a, v)
    u = min(1.0, max(0.0, (v - a) / (b - a))); return u * u * (3 - 2 * u)
BX, BY = 175.0, 0.0                                              # the Bowl: the gorge opens into a round hollow
def plat(x): return 16.0 + 18.0 * ss(215, 300, x)                # plateau 16 m, the Needle gets deeper (34 m) at the east end
def gh(x, y):
    n = 0.9 * math.sin(x * 0.05 + y * 0.03) + 0.6 * math.sin(x * 0.11 - y * 0.07 + 1.3)
    ay = abs(y)
    m = ss(-2, 6, x) * (1 - ss(318, 324, x)) * (1 - ss(110, 140, ay))                # the rock massif
    g = ss(3.8, 6.2, ay)                                                              # the narrow gorge walls
    b = ss(14, 32, math.hypot(x - BX, y - BY))                                        # the Bowl slopes (walkable)
    wall = min(g, b)
    z = m * plat(x) * wall + (0.4 * n) * (1 - m) + (1.3 * n) * m * wall
    z += 0.25 * n * ss(2.6, 4.0, ay) * m * (1 - wall)                                 # rough gorge floor away from the rails
    z -= 1.4 * ss(22, 32, y) * ss(326, 340, x)                                        # the lake bed by Reed Town
    if ay < 2.6: z = min(z, -0.06)
    return z
GA = O["Ground"]; GA.location = (0, 0, -30.0); GA.scale = (1400, 1000, 1)
rockM = newM("S_RockM", (0.07, 0.068, 0.075), rough=1); grassM = newM("S_Grass", (0.04, 0.055, 0.04), rough=1)
GA.data.materials.clear(); GA.data.materials.append(grassM)
def axis(a, b, step):
    out = []; v = a
    while v <= b + 1e-6: out.append(v); v += step
    return out
xs = axis(-460, -42, 8) + axis(-40, 340, 2.0) + axis(346, 640, 6)
ys = axis(-300, -62, 8) + axis(-60, -8, 2.0) + axis(-7.5, 7.5, 0.5) + axis(8, 60, 2.0) + axis(66, 300, 8)
bm = bmesh.new(); vv = [[bm.verts.new((x, y, gh(x, y))) for y in ys] for x in xs]
for i in range(len(xs) - 1):
    for j in range(len(ys) - 1):
        f = bm.faces.new((vv[i][j], vv[i + 1][j], vv[i + 1][j + 1], vv[i][j + 1]))
        x0, y0 = xs[i], ys[j]
        if x0 < -4 or x0 > 324: f.material_index = 1
GO = mk("S_Ground", bm, rockM, smooth=True); GO.data.materials.append(grassM)
waterM = newM("S_Lake", (0.01, 0.015, 0.03), rough=0.08)
mk("S_Lake", box(), waterM, (480, 120, -0.55), scl=(320, 190, 0.1))
railM = newM("S_RailM", (0.2, 0.2, 0.22), rough=0.4, metal=0.8); tie = newM("S_Tie", (0.05, 0.04, 0.035), rough=1)
postM = newM("S_Post", (0.02, 0.02, 0.025), rough=0.5)
def pboxes(name, mat, items, parent=None):
    bm = bmesh.new()
    for loc, scl, rzz in items:
        g = bmesh.ops.create_cube(bm, size=1.0)["verts"]; bmesh.ops.scale(bm, vec=scl, verts=g)
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(rzz, 3, "Z"), verts=g); bmesh.ops.translate(bm, vec=loc, verts=g)
    return mk(name, bm, mat, parent=parent)
X0, X1 = -330.0, 400.0
pboxes("S_Rails", railM, [(((X0 + X1) / 2, sd * 0.53, 0.03), (X1 - X0, 0.08, 0.06), 0) for sd in (-1, 1)])
pboxes("S_Ties", tie, [((x, 0, -0.02), (0.25, 1.4, 0.06), 0) for x in axis(X0, X1, 2.0)])
pboxes("S_EndStop", newM("S_Red", (0.6, 0.05, 0.03), rough=0.5), [((X0 + 2, 0, 0.4), (0.3, 1.8, 0.5), 0), ((X1, 0, 0.4), (0.3, 1.8, 0.5), 0)])
# the big rock in the Bowl (north of the rails): the train stops in its dark
mk("S_BigRock", sph(1, 10, 8), newM("S_BigRockM", (0.06, 0.058, 0.064), rough=1), (176, 9.5, 2.0), (0.2, 0.1, 0.4), (9, 5, 7))
mk("S_SmallRock", sph(1, 8, 6), rockM, (160, -7, 0.6), (0.3, 0.2, 0.1), (2.2, 1.6, 1.4))
mk("S_SmallRock", sph(1, 8, 6), rockM, (192, 7, 0.6), (0.1, 0.4, 0.3), (2.6, 1.8, 1.6))
RLAMP = []
def lamp(tag, x, y, td, e=55, z=None):
    z = gh(x, y) if z is None else z; mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, y, z + 1.7))
    hm = newM(f"L_{tag}", (1, 0.62, 0.25), emit=8); mk(f"L_{tag}", sph(0.2, 12, 8), hm, (x, y, z + 3.45))
    lo = light(f"L_{tag}L", "POINT", e, (1, 0.6, 0.3), (x, y, z + 3.2)); RLAMP.append((hm, lo, td)); return hm, lo
# the Hush: (t, x, y, dz) ; z = ground + dz
HP_ = [(0, -330, -22, -40), (2.4, -330, -22, -40), (3.4, -330, -22, -14), (4.6, -330, -22, 0), (6, -312, -18, 0),
       (12, -230, -12, 0), (18, -120, -7, 0), (22, -46, -3, 0), (24, -12, 0, 0), (26.6, -11, 0, 0),
       (28.2, 2, -15, 0), (29.6, 14, -16, 0), (40, 140, -17, 0), (42, 152, -19, 0), (44, 163, -17, 0), (47, 170, -17, 0),
       (50, 178, -17, 0), (53, 184, -17, 0), (54.8, 182, -17, 0), (57.8, 162, -17, 0), (58.8, 160, -17, 0), (60.2, 162, -15, 0),
       (62, 170, -12, 0), (64, 188, -11, 0), (66, 200, -13, 0), (68, 209, -17, 0), (70, 224, -16, 0), (74, 270, -15, 0),
       (77, 304, -14, 0), (78.4, 311, -13, 0), (100, 311, -13, 0)]
def h_x(x):
    for (ta, xa, *_), (tb, xb, *_) in zip(HP_[4:10], HP_[5:10]):
        if xa <= x <= xb and xb > xa: return ta + (tb - ta) * (x - xa) / (xb - xa)
    return 999.0
for i, x in enumerate((-300, -285, -270)): lamp(f"B{i}", x, -3.2, 0.2 + i * 0.5)               # the moor lamps behind die first
for i, x in enumerate((-200, -150, -100, -50)): lamp(f"V{i}", x, -3.2, h_x(x) + 0.4)
lamp("G0", 40, 3.0, 31.6); lamp("G1", 100, 3.0, 36.0)                                           # old lamps in the Needle: it eats them from the top
lamp("W0", 164, 4.0, 42.4)                                                                       # the Bowl lamp: it eats it as it steps down
for i, x in enumerate((240, 290)): lamp(f"K{i}", x, 3.0, 999)
for i in range(5): lamp(f"St{i}", 352 + i * 10.0, -4.4, 999, 80)
for i, x in enumerate((328, 338)): lamp(f"Cf{i}", x, -4.4, 999, 120)                          # lamps at the cliff foot
# Reed Town by the lake
houseM = newM("S_HouseM", (0.2, 0.2, 0.22), rough=1); roofM = newM("S_Roof", (0.25, 0.12, 0.09), rough=1)
winM = newM("S_Win", (1, 0.62, 0.25), emit=5)
for i in range(26):
    x = rr.uniform(340, 440); y = rr.choice((rr.uniform(-60, -10), rr.uniform(-60, -10), rr.uniform(8, 20))); w = rr.uniform(3, 6); h = rr.uniform(2.5, 5); z0 = gh(x, y)
    mk("S_House", box(), houseM, (x, y, z0 + h / 2 - 0.5), scl=(w, w, h)); mk("S_Roof", box(), roofM, (x, y, z0 + h - 0.4), scl=(w + 0.4, w + 0.4, 0.3))
    mk("S_Win", box(), winM, (x, y + (w / 2 + 0.02) * (1 if y < 0 else -1), z0 + h * 0.45), scl=(0.6, 0.05, 0.7))
mk("S_Platform", box(), newM("S_Plat", (0.1, 0.09, 0.1), rough=1), (372, -2.6, 0.3), scl=(44, 2.2, 0.6))
# black pines on the moor and by the town; heather rocks on the plateau
pineM = newM("S_Pine", (0.02, 0.035, 0.03), rough=1); trunkM = newM("S_Trunk", (0.04, 0.03, 0.02), rough=1)
pines = []
for i in range(120):
    x = rr.uniform(-450, -20); y = rr.choice((rr.uniform(-120, -10), rr.uniform(10, 120)))
    pines.append((x, y, rr.uniform(6, 12)))
for i in range(40): pines.append((rr.uniform(340, 520), rr.choice((rr.uniform(-140, -66), rr.uniform(-140, -66))), rr.uniform(6, 11)))
bm = bmesh.new(); bt = bmesh.new()
for x, y, h in pines:
    z = gh(x, y)
    g = bmesh.ops.create_cone(bm, cap_ends=True, segments=7, radius1=h * 0.28, radius2=0.0, depth=h)["verts"]; bmesh.ops.translate(bm, vec=(x, y, z + h * 0.5 + 0.8), verts=g)
    g = bmesh.ops.create_cone(bt, cap_ends=True, segments=5, radius1=0.25, radius2=0.2, depth=1.6)["verts"]; bmesh.ops.translate(bt, vec=(x, y, z + 0.6), verts=g)
mk("S_Pines", bm, pineM); mk("S_Trunks", bt, trunkM)
bm = bmesh.new()
for i in range(70):
    x = rr.uniform(10, 310); y = rr.choice((rr.uniform(-100, -9), rr.uniform(9, 100)))
    if math.hypot(x - BX, y - BY) < 34: continue
    s = rr.uniform(1.0, 3.0); g = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=s)["verts"]; bmesh.ops.translate(bm, vec=(x, y, gh(x, y) + s * 0.3), verts=g)
mk("S_Boulders", bm, rockM)
farM = newM("S_FarPeak", (0.1, 0.11, 0.15), rough=1)
for i in range(9):
    mk("S_FarPeak", cyl(1, 0.05, 1, 8), farM, (-420 + i * 120, rr.uniform(330, 380), 30), scl=(rr.uniform(70, 95), 55, rr.uniform(50, 75)))
# the moon in the south-west
EL = math.radians(24.0); AZ = math.radians(35)
moonM = newM("S_Moon", (0.9, 0.9, 0.85), emit=4)
mk("S_Moon", cyl(24, 24, 0.2, 48), moonM, (-800 * math.cos(AZ), -800 * math.sin(AZ), 800 * math.tan(EL)), (math.pi / 2, 0, math.pi / 2 + AZ))
w = sc.world; w.node_tree.nodes["Background"].inputs[0].default_value = (0.016, 0.02, 0.05, 1)
MK = O["MoonKey"]; MK.data.energy = 3.4; MK.data.color = (0.75, 0.82, 1.0); MK.rotation_euler = (0, EL - math.pi / 2, AZ)
try: MK.data.use_shadow = True; MK.data.angle = math.radians(0.6)
except Exception: pass
GORGE = light("T_GorgeFill", "AREA", 260, (0.55, 0.65, 1.0), (1.5, 0, 9.0)); GORGE.data.size = 14     # cold sky light in the Needle (follows the train)
FIREM = newM("T_FireM", (1, 0.35, 0.08), emit=12)
mk("T_Fire", box(), FIREM, (2.45, 0, 0.55), scl=(0.06, 0.5, 0.3), parent=T)
FIRE = light("T_FireGlow", "POINT", 25, (1, 0.45, 0.15), (2.2, 0, 0.7), T)
STEAM = mk("T_Steam", sph(1, 12, 8), newM("T_SteamM", (0.8, 0.82, 0.85), emit=0.8, rough=1), (4.2, 0, 2.0), scl=(0, 0, 0), parent=T)
DROP = mk("T_Drop", sph(0.07, 8, 6), newM("T_DropM", (0.6, 0.75, 1.0), emit=2.0, rough=0.1), (4.2, 0.1, 6.0), parent=T)

# ---------------- the Hush ----------------
H = O["Hush"]; H.scale = (2.4, 2.4, 2.4)
mask_spot = light("T_MaskLight", "SPOT", 9000, (0.7, 0.85, 1.0), (0, 0, 0)); mask_spot.data.spot_size = math.radians(18)
c = mask_spot.constraints.new("TRACK_TO"); c.target = O["H_Mask"]; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
mask_spot.parent = H; mask_spot.location = (2.0, -14, 4.0)

# ---------------- animation ----------------
TK = [(0, -260), (20, -20), (26, 52), (30, 98), (34, 140), (38, 165), (40.4, 173), (41.6, 175), (60.8, 175), (62, 180), (64, 196),
      (66, 218), (70, 266), (74, 318), (78, 352), (81, 368), (82.6, 372), (100, 372)]
def x_at(t):
    for (ta, sa), (tb, sb) in zip(TK, TK[1:]):
        if ta <= t <= tb:
            u = (t - ta) / (tb - ta) if tb > ta else 0; return sa + (sb - sa) * u
    return TK[-1][1]
for f in list(range(1, END + 1, 2)) + [END]:
    key(T, "location", f, Vector((x_at((f - 1) / FPS), 0, 0)))
key(T, "rotation_euler", 1, Vector((0, 0, 0)))
lin(T)
for f in list(range(1, END + 1, 12)) + [END]:                      # the gorge sky light follows the train
    key(GORGE, "location", f, Vector((x_at((f - 1) / FPS) + 1.5, 0, 9.0)))
for t, e in ((0, 0), (20.4, 0), (22.0, 260), (74, 260), (75.5, 0)): GORGE.data.energy = e; GORGE.data.keyframe_insert("energy", frame=F(t))
lin(GORGE)
for hm, lt, td in RLAMP:
    if td > 150: continue
    s = hm.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for t, e in ((0, 8), (td - 0.01, 8), (td + 0.15, 0)): s.default_value = e; s.keyframe_insert("default_value", frame=F(max(t, 0)))
    e0 = lt.data.energy
    for t, e in ((0, e0), (td - 0.01, e0), (td + 0.15, 0)): lt.data.energy = e; lt.data.keyframe_insert("energy", frame=F(max(t, 0)))
for t, x, y, dz in HP_:
    key(H, "location", F(t), Vector((x, y, gh(x, y) + dz))); key(H, "scale", F(t), Vector((2.4, 2.4, 2.4)))
d1 = H.constraints.new("LOCKED_TRACK"); d1.target = T; d1.track_axis = "TRACK_NEGATIVE_Y"; d1.lock_axis = "LOCK_Z"
gm = M("H_Green").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 0), (2.6, 0), (4.0, 60), (41.0, 60), (42.4, 140), (44, 70), (58.6, 70), (59.2, 130), (61, 60), (100, 60)):
    gm.default_value = e; gm.keyframe_insert("default_value", frame=F(t))
# the hiss: a drop from the rock falls on the hot boiler at 58.6 -> a puff of steam
for t, z in ((0, 6.0), (57.9, 6.0), (58.6, 1.7), (58.62, -5)): key(DROP, "location", F(t), z, 2)
for t, s in ((0, 0), (58.6, 0), (59.0, 0.5), (59.8, 0.8), (60.6, 0)): key(STEAM, "scale", F(t), Vector((s, s, s * 1.3)))
for t, z in ((0, 2.0), (58.6, 2.0), (60.6, 3.6)): key(STEAM, "location", F(t), z, 2)
# our lights: put out by Rook at 41.4 ("Lights out."), lit again at 61.2 ("Full steam!")
L0, L1 = 41.4, 61.2
se = M("H_Signal").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 80), (L0, 80), (L0 + 0.6, 3), (L1 - 0.2, 3), (L1 + 0.4, 60), (100, 50)): se.default_value = e; se.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 6), (L0, 6), (L0 + 0.6, 0.3), (L1 - 0.2, 0.3), (L1 + 0.4, 4)): SIGL.data.energy = e; SIGL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 900), (L0, 900), (L0 + 0.4, 0), (L1, 0), (L1 + 0.3, 900)): HL.data.energy = e; HL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 45), (L0, 45), (L0 + 0.6, 16), (L1 - 0.2, 16), (L1 + 0.6, 45)): O["Fill"].data.energy = e; O["Fill"].data.keyframe_insert("energy", frame=F(t))
wi = M("H_Window").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 4), (L0, 4), (L0 + 0.5, 0.0), (L1, 0.0), (L1 + 0.3, 4)): wi.default_value = e; wi.keyframe_insert("default_value", frame=F(t))
fe = FIREM.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 12), (L0, 12), (L0 + 1.0, 1.0), (L1 - 0.2, 1.0), (L1 + 0.2, 20), (100, 14)): fe.default_value = e; fe.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 25), (L0, 25), (L0 + 1.0, 2), (L1 - 0.2, 2), (L1 + 0.2, 40), (100, 30)): FIRE.data.energy = e; FIRE.data.keyframe_insert("energy", frame=F(t))
# Rook head (rz = local direction + 30: 30 ahead, 120 left / north, -150 back, -60 right / south where it walks)
for t, rz_ in ((0, -150), (2.8, -150), (3.2, 30), (5.6, 30), (6.0, -150), (8.4, -150), (8.8, 30), (19.4, 30), (19.8, -150), (27.2, -150),
               (27.6, -60), (34.6, -60), (35.0, 30), (40.6, 30), (41.0, -70), (55.0, -70), (55.4, -110), (58.4, -110), (58.8, 30), (68.6, 30),
               (69.0, -150), (75.2, -150), (75.6, 30), (88.8, 30), (89.4, -120), (100, -120)):
    key(HP, "rotation_euler", F(t), math.radians(rz_), 2)
WUP = [(0.6, 1.3), (5.8, 1.2), (11.2, 1.3), (16.0, 1.2), (24.6, 1.0), (29.4, 0.9), (35.0, 1.1), (59.2, 1.4), (61.0, 1.5), (72.4, 1.3), (81.4, 1.2)]
for sd in (-1, 1):
    wg = O[f"R_Wing{sd}"]; ks = [(0, 0)]
    for t, a in WUP: ks += [(t, 0), (t + 0.3, a), (t + 1.9, a), (t + 2.3, 0)]
    ks += [(41.2, 0), (41.6, -0.6), (55.0, -0.6), (55.4, 0)]
    for t, a in sorted(ks): key(wg, "rotation_euler", F(t), math.radians(sd * 12) + sd * a * 0.6, 1)
for f in range(1, END, 12):
    if F(41.4) <= f <= F(61.2) or f >= F(82.6): continue
    key(R, "location", f, 0.62 + (0.02 if (f // 12) % 2 else 0.0), 2)

# ---------------- cameras (one per shot, bound to markers) ----------------
def cam(name, start_s, loc, look, lens=28, parent=None, world_look=False):
    if parent is None: loc = (loc[0], loc[1], max(loc[2], gh(loc[0], loc[1]) + 2.0))
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_end = 2000
    c = bpy.data.objects.new(name, cd); sc.collection.objects.link(c); c.location = loc
    if parent: c.parent = parent
    if isinstance(look, str): tgt = O[look]
    else:
        tgt = bpy.data.objects.new(name + "_T", None); sc.collection.objects.link(tgt); tgt.location = look; tgt.name = "Cam_T_" + name
        if parent and not world_look: tgt.parent = parent
    k = c.constraints.new("TRACK_TO"); k.target = tgt; k.track_axis = "TRACK_NEGATIVE_Z"; k.up_axis = "UP_Y"
    m = sc.timeline_markers.new(name, frame=F(start_s)); m.camera = c; return c
cam("Cam_01", 0, (2.6, -3.2, 1.8), (0.0, 0, 1.3), 28, T)                          # Rook: the moor lamps went dark
cam("Cam_02", 2.6, (6, 2.2, 3.4), "H_Mask", 55, T)                                 # over the train, back: its face rises on the moor
cam("Cam_03", 5.6, (-150, -95, 30), (-250, 0, 8), 22)                             # high wide: the moor, the train, it behind
cam("Cam_04", 11.0, (-3, -2.2, 2.6), (14, 0, 3.0), 26, T)                         # over Rook: the Needle ahead
cam("Cam_05", 15.0, (-110, -40, 10), (0, 0, 8), 26)                               # wide: the rock wall and the narrow gorge
cam("Cam_06", 19.6, (-4, -3.0, 2.8), "H_Mask", 28, T)                              # from the train: it comes over the moor
cam("Cam_07", 22.4, (30, 2.5, 2.2), (-20, 0, 7), 22)                              # inside the Needle: the train comes in, it stops at the walls
cam("Cam_08", 26.4, (2.4, -2.2, 3.0), (0.6, 0, 1.45), 30, T)                      # Rook in the gorge
cam("Cam_09", 28.6, (-3, 1.5, 1.2), "H_Mask", 26, T)                               # up from the gorge floor: it walks on top
cam("Cam_10", 32.4, (110, 42, 42), (105, -6, 8), 22)                                # high: the train in the slit, it on the rim
cam("Cam_11", 34.8, (8, -1.8, 1.6), (0, 0, 1.4), 26, T)                           # front: Rook, the Bowl ahead
cam("Cam_12", 38.0, (194, -9, 5), (165, 0, 4), 24)                                # in the Bowl: the train comes in, it on the rim
cam("Cam_13", 40.8, (2.6, -2.2, 1.6), (0.5, 0, 1.3), 30, T)                       # Rook: lights out
cam("Cam_14", 44.6, (0.0, 2.2, 0.4), (174, -6, 10), 22, T, world_look=True)                          # low behind Rook: it stands right by us (cold open)
cam("Cam_15", 49.4, (205, 30, 24), (176, -6, 4), 24)                              # high from the north rim: the dark train, it beside
cam("Cam_16", 52.6, (-5, 1.5, 2.4), "H_Mask", 24, T)                               # behind the train: its face
cam("Cam_17", 55.2, (160, 6, 3), (170, -17, 16), 20)                              # in the Bowl: it goes back
cam("Cam_18", 58.2, (7.5, -3.0, 2.8), (4.2, 0, 1.9), 30, T)                       # the drop hits the hot boiler: hiss
cam("Cam_19", 59.8, (2.4, -2.6, 3.0), (0.6, 0, 1.45), 28, T)                      # Rook: it heard us, full steam
cam("Cam_20", 63.2, (6, -3.0, 3.5), (0, 0, 1.5), 24, T)                           # side: full steam into the Needle
cam("Cam_21", 66.4, (250, 60, 70), (215, -6, 12), 28)                             # high: it climbs out on the rim
cam("Cam_22", 70.0, (-3, 1.8, 1.0), "H_Mask", 24, T)                              # back: it on the high rim
cam("Cam_23", 73.6, (345, -12, 3), (318, -6, 22), 20)                               # Reed Town: the train comes out, it on the cliff top
cam("Cam_24", 78.4, (2.4, -3.2, 1.7), (0.6, 0, 1.35), 28, T)                      # Rook at the station
cam("Cam_25", 87.4, (395, -22, 6), (335, -8, 22), 26)                            # the lit station, it on the cliff looking down
sc.camera = O["Cam_01"]
sc.render.resolution_x = 1280; sc.render.resolution_y = 720; sc.render.resolution_percentage = 100
sc.eevee.taa_render_samples = 24
try: sc.eevee.use_raytracing = False
except Exception: pass
sc.render.use_compositing = False; sc.render.use_sequencer = False
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "hush_film19.blend"))
print("film19 built", len(sc.collection.all_objects), "objects; markers", len(sc.timeline_markers))
