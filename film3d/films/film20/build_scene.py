# GLOAMRUN 3D Film 25 "The Glass Roof" — run INSIDE Blender (hush_lookdev.blend open, scene HUSH).
# Story (no calm start): the yard lamps die and its face rises behind us -> by 8 s it is right at the last car (Rook flinches) -> full steam
# -> Rook's move: he runs the train into the old engine shed and the doors close behind ("Walls hide us"), lights out -> it comes, eats the
# shed lamps and bends down to look in through the glass roof ('...Don't move.') -> it goes -> surprise: its heavy steps shake a loose pane
# off the roof, CRASH inside -> it comes back to the window -> 'Out the back door! Full steam!' the train bursts out of the back doors and
# runs to Ember Town. It stands far behind on the line (it will be back).
import bpy, bmesh, math, random, os
from mathutils import Vector
OUT = r"C:\Users\81803\TremenFilm\hush\film20"; os.makedirs(OUT, exist_ok=True)
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





# ---------------- world: the dark rail yard by the woods, the old engine shed with a glass roof, the line to Ember Town ----------------
from mathutils import Matrix
rr = random.Random(2525)
def ss(a, b, v):
    if b < a: return 1.0 - ss(b, a, v)
    u = min(1.0, max(0.0, (v - a) / (b - a))); return u * u * (3 - 2 * u)
SX0, SX1, SW = 40.0, 60.0, 2.3                                   # the shed: x 40..60, walls at y = +-2.3, eaves 3.0 m, ridge 4.2 m
def gh(x, y):
    n = 0.9 * math.sin(x * 0.05 + y * 0.03) + 0.6 * math.sin(x * 0.11 - y * 0.07 + 1.3)
    ay = abs(y)
    hills = 7.0 * ss(25, 110, ay) * (0.55 + 0.45 * math.sin(x * 0.012 + 0.8))
    yard = 1.0 - (ss(-30, 0, x) * (1 - ss(100, 130, x)) * (1 - ss(16, 30, ay)))       # the flat yard round the shed
    z = (0.45 * n + hills) * yard
    z += 3.0 * ss(30, 70, y) * ss(160, 200, x) * (1 - ss(240, 280, x))                 # a low hill north of the line
    if ay < 2.6: z = min(z, -0.06)
    return z
GA = O["Ground"]; GA.location = (0, 0, -30.0); GA.scale = (1400, 1000, 1)
grassM = newM("S_Grass", (0.035, 0.05, 0.035), rough=1); yardM = newM("S_Yard", (0.05, 0.048, 0.05), rough=1)
GA.data.materials.clear(); GA.data.materials.append(grassM)
def axis(a, b, step):
    out = []; v = a
    while v <= b + 1e-6: out.append(v); v += step
    return out
xs = axis(-460, -42, 8) + axis(-40, 400, 2.5) + axis(406, 640, 8)
ys = axis(-300, -62, 8) + axis(-60, -8, 2.5) + axis(-7.5, 7.5, 0.5) + axis(8, 60, 2.5) + axis(66, 300, 8)
bm = bmesh.new(); vv = [[bm.verts.new((x, y, gh(x, y))) for y in ys] for x in xs]
for i in range(len(xs) - 1):
    for j in range(len(ys) - 1):
        f = bm.faces.new((vv[i][j], vv[i + 1][j], vv[i + 1][j + 1], vv[i][j + 1]))
        if -20 < xs[i] < 110 and abs(ys[j]) < 20: f.material_index = 1
GO = mk("S_Ground", bm, grassM, smooth=True); GO.data.materials.append(yardM)
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
# yard sidings with a few old wagons and a coal heap
pboxes("S_Rails2", railM, [((-5 + 0, sd * 0.53 + yy, 0.03), (110, 0.08, 0.06), 0) for yy in (-7.0, 7.0) for sd in (-1, 1)])
wagM = newM("S_Wagon", (0.09, 0.05, 0.04), rough=0.9)
pboxes("S_Wagons", wagM, [((x, 7.0, 0.75), (4.2, 1.2, 1.2), 0) for x in (-30, -25, -20, 70, 75)] + [((x, -7.0, 0.75), (4.2, 1.2, 1.2), 0) for x in (-48, 8, 13)])
mk("S_Coal", sph(1, 10, 6), newM("S_CoalM", (0.012, 0.012, 0.014), rough=0.7), (22, 9.5, 0.0), scl=(4, 2.2, 1.6))
mk("S_TowerTank", cyl(1.3, 1.3, 1.8, 16), newM("S_TankM", (0.1, 0.07, 0.05), rough=0.8), (25, -5.0, 4.2))
pboxes("S_TowerLegs", postM, [((25 + dx, -5.0 + dy, 1.65), (0.15, 0.15, 3.3), 0) for dx in (-0.9, 0.9) for dy in (-0.9, 0.9)])
# ---- the old engine shed: brick walls, wooden doors at both ends, south roof all glass (iron bars), north roof iron ----
brickM = newM("S_Brick", (0.16, 0.07, 0.05), rough=0.95); woodM = newM("S_Door", (0.12, 0.08, 0.05), rough=0.9)
ironM = newM("S_Iron", (0.06, 0.065, 0.07), rough=0.6, metal=0.5); floorM = newM("S_Floor", (0.045, 0.043, 0.045), rough=1)
glassM = newM("S_Glass", (0.55, 0.7, 0.8), rough=0.05)
gb = glassM.node_tree.nodes["Principled BSDF"]; gb.inputs["Alpha"].default_value = 0.10
try: glassM.surface_render_method = "DITHERED"
except Exception:
    try: glassM.blend_method = "HASHED"
    except Exception: pass
SL = math.atan2(1.2, SW)                                           # roof slope angle
pboxes("S_ShedWalls", brickM, [(((SX0 + SX1) / 2, sd * SW, 1.5), (SX1 - SX0, 0.2, 3.0), 0) for sd in (-1, 1)])
mk("S_ShedFloor", box(), floorM, ((SX0 + SX1) / 2, 0, -0.05), scl=(SX1 - SX0, 2 * SW, 0.04))
for xg in (SX0, SX1):                                              # gables above the doors
    bm = bmesh.new(); vs = [bm.verts.new((xg + dx, y, z)) for dx in (-0.1, 0.1) for (y, z) in ((-SW - 0.1, 3.0), (SW + 0.1, 3.0), (0, 4.25))]
    bm.faces.new(vs[0:3]); bm.faces.new(vs[3:6][::-1])
    for a, b2 in ((0, 1), (1, 2), (2, 0)): bm.faces.new((vs[a], vs[b2], vs[b2 + 3], vs[a + 3]))
    mk("S_Gable", bm, brickM)
    pboxes("S_DoorPosts", brickM, [((xg, sd * (SW + 0.05), 1.5), (0.35, 0.35, 3.0), 0) for sd in (-1, 1)])
RL = math.hypot(1.2, SW) + 0.25
mk("S_RoofN", box(), ironM, ((SX0 + SX1) / 2, SW / 2, 3.62), (-SL, 0, 0), ((SX1 - SX0) + 0.6, RL, 0.08))
PANES = []
for k in range(16):                                                # 16 glass panes on the south slope
    xc = SX0 + 0.625 + k * 1.25
    p = mk(f"S_Pane{k}", box(), glassM, (xc, -SW / 2, 3.62), (SL, 0, 0), (1.2, RL - 0.1, 0.03)); p.visible_shadow = False; PANES.append(p)
bars = [((SX0 + k * 1.25, 0, 0), (0.07, RL, 0.09)) for k in range(17)] + [(((SX0 + SX1) / 2, d, 0), ((SX1 - SX0), 0.07, 0.09)) for d in (-RL / 2, 0, RL / 2)]
bm = bmesh.new()
for loc, scl in bars:
    g = bmesh.ops.create_cube(bm, size=1.0)["verts"]; bmesh.ops.scale(bm, vec=scl, verts=g); bmesh.ops.translate(bm, vec=loc, verts=g)
bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(SL, 3, "X"), verts=bm.verts)
bmesh.ops.translate(bm, vec=(0, -SW / 2, 3.66), verts=bm.verts); mk("S_RoofBars", bm, ironM)
pboxes("S_Ridge", ironM, [(((SX0 + SX1) / 2, 0, 4.22), (SX1 - SX0 + 0.6, 0.25, 0.12), 0)])
DOORS = {}
def door(tag, xh, yh, sgn):
    piv = empty(f"S_Hinge{tag}", (xh, yh, 0)); lf = mk(f"S_Door{tag}", box(), woodM, (0, -sgn * 1.12, 1.5), scl=(0.12, 2.22, 2.95), parent=piv)
    mk(f"S_DoorBand{tag}", box(), ironM, (0.07, -sgn * 1.12, 1.5), scl=(0.03, 2.1, 0.12), parent=piv); DOORS[tag] = piv; return piv
door("F1", SX0, SW, 1); door("F2", SX0, -SW, -1); door("B1", SX1, SW, 1); door("B2", SX1, -SW, -1)
FALL = PANES[11]                                                    # the loose pane (beside the cab)
fallM = newM("S_GlassFall", (0.7, 0.85, 1.0), emit=0.6, rough=0.05)
fallM.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.45
try: fallM.surface_render_method = "DITHERED"
except Exception: pass
FALL.data.materials[0] = fallM
fb = fallM.node_tree.nodes["Principled BSDF"]
for t_, a_, e_ in ((0, 0.10, 0.0), (57.6, 0.10, 0.0), (58.0, 0.45, 0.6)):
    fb.inputs["Alpha"].default_value = a_; fb.inputs["Alpha"].keyframe_insert("default_value", frame=F(t_))
    fb.inputs["Emission Strength"].default_value = e_; fb.inputs["Emission Strength"].keyframe_insert("default_value", frame=F(t_))
SHARDS = [mk("S_Shard", box(), fallM, (FALL.location.x + rr.uniform(-0.3, 0.3), -1.25, 0.03), (0, 0, rr.uniform(0, 3)), (0, 0, 0)) for i in range(10)]
for s_ in SHARDS: s_.visible_shadow = False
RLAMP = []
def light(name, typ, energy, col, loc, parent=None, size=1.0, shadow=False):
    d = bpy.data.lights.new(name, typ); d.energy = energy; d.color = col
    if typ == "AREA": d.size = size
    if typ == "SPOT": d.spot_size = math.radians(55)
    try: d.use_shadow = shadow
    except Exception: pass
    o = bpy.data.objects.new(name, d); sc.collection.objects.link(o); o.location = loc; o.parent = parent; return o
def lamp(tag, x, y, td, e=55, z=None):
    z = gh(x, y) if z is None else z; mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, y, z + 1.7))
    hm = newM(f"L_{tag}", (1, 0.62, 0.25), emit=8); mk(f"L_{tag}", sph(0.2, 12, 8), hm, (x, y, z + 3.45))
    lo = light(f"L_{tag}L", "POINT", e, (1, 0.6, 0.3), (x, y, z + 3.2)); RLAMP.append((hm, lo, td)); return hm, lo
# the Hush: (t, x, y, dz) ; z = ground + dz   (dz < 0 = it bends down into its smoke to look in)
HP_ = [(0, -268, -6, -40), (2.4, -268, -6, -40), (3.4, -268, -6, -16), (4.4, -266, -6, 0), (8.0, -185, -3, 0), (9.4, -167, -3, 0),
       (14, -112, -5, 0), (19, -52, -6, 0), (22.6, -12, -6, 0), (26, 24, -8, 0), (29, 33, -11, 0), (33, 40, -14, 0), (37, 46, -14, -2),
       (40, 50, -13, -5), (42, 52, -12.5, -7), (48, 53, -12.5, -7), (50, 53.5, -12.5, -7), (53.5, 50, -13, -4), (56, 44, -15, 0),
       (57.6, 40, -16, 0), (59.6, 42, -15, 0), (61.6, 49, -13, -4), (63, 52, -13, -3), (64.4, 58, -14, 0), (66, 66, -15, 0),
       (70, 96, -12, 0), (76, 150, -10, 0), (80, 190, -10, 0), (84, 214, -12, 0), (86, 220, -14, 0), (100, 220, -14, 0)]
def h_x(x):
    for (ta, xa, *_), (tb, xb, *_) in zip(HP_[3:12], HP_[4:12]):
        if xa <= x <= xb and xb > xa: return ta + (tb - ta) * (x - xa) / (xb - xa)
    return 999.0
for i, x in enumerate((-300, -285, -270)): lamp(f"B{i}", x, -3.2, 0.2 + i * 0.5)               # the yard lamps behind die first
for i, x in enumerate((-140, -100, -60, -20)): lamp(f"V{i}", x, -3.2, h_x(x) + 0.4)
lamp("D0", 37.5, -3.4, 28.4, 70)                                                                  # the shed lamps: it eats them
lamp("D1", 62.5, -3.4, 41.0, 70)
for i, x in enumerate((140, 220)): lamp(f"K{i}", x, -3.2, 999)
for i in range(5): lamp(f"St{i}", 316 + i * 10.0, -3.4, 999, 80)
INL = light("S_ShedLampL", "POINT", 22, (1, 0.6, 0.3), (47, 0, 3.2)); INM = newM("L_ShedLamp", (1, 0.62, 0.25), emit=8)
mk("L_ShedLamp", sph(0.14, 10, 6), INM, (47, 0, 3.4)); mk("S_LampWire", cyl(0.01, 0.01, 0.8, 4), postM, (47, 0, 3.8))
ROOFMOON = light("S_RoofMoon", "AREA", 70, (0.55, 0.65, 1.0), ((SX0 + SX1) / 2, -0.6, 3.5))
ROOFMOON.data.shape = "RECTANGLE"; ROOFMOON.data.size = SX1 - SX0; ROOFMOON.data.size_y = 3.0
# Ember Town
houseM = newM("S_HouseM", (0.2, 0.2, 0.22), rough=1); roofM = newM("S_Roof", (0.25, 0.12, 0.09), rough=1)
winM = newM("S_Win", (1, 0.62, 0.25), emit=5)
for i in range(28):
    x = rr.uniform(300, 420); y = rr.choice((rr.uniform(-60, -9), rr.uniform(-60, -9), rr.uniform(8, 30))); w = rr.uniform(3, 6); h = rr.uniform(2.5, 5); z0 = gh(x, y)
    mk("S_House", box(), houseM, (x, y, z0 + h / 2 - 0.5), scl=(w, w, h)); mk("S_Roof", box(), roofM, (x, y, z0 + h - 0.4), scl=(w + 0.4, w + 0.4, 0.3))
    mk("S_Win", box(), winM, (x, y + (w / 2 + 0.02) * (1 if y < 0 else -1), z0 + h * 0.45), scl=(0.6, 0.05, 0.7))
mk("S_Platform", box(), newM("S_Plat", (0.1, 0.09, 0.1), rough=1), (336, -1.9, 0.3), scl=(44, 1.6, 0.6))
# black pines along the woods
pineM = newM("S_Pine", (0.02, 0.035, 0.03), rough=1); trunkM = newM("S_Trunk", (0.04, 0.03, 0.02), rough=1)
pines = []
for i in range(220):
    x = rr.uniform(-460, 520); y = rr.choice((rr.uniform(-160, -24), rr.uniform(24, 160)))
    if 290 < x < 430 and abs(y) < 70: continue
    pines.append((x, y, rr.uniform(6, 12)))
for i in range(60):
    x = rr.uniform(-330, -40); y = rr.choice((rr.uniform(-22, -12), rr.uniform(12, 22))); pines.append((x, y, rr.uniform(5, 10)))
bm = bmesh.new(); bt = bmesh.new()
for x, y, h in pines:
    z = gh(x, y)
    g = bmesh.ops.create_cone(bm, cap_ends=True, segments=7, radius1=h * 0.28, radius2=0.0, depth=h)["verts"]; bmesh.ops.translate(bm, vec=(x, y, z + h * 0.5 + 0.8), verts=g)
    g = bmesh.ops.create_cone(bt, cap_ends=True, segments=5, radius1=0.25, radius2=0.2, depth=1.6)["verts"]; bmesh.ops.translate(bt, vec=(x, y, z + 0.6), verts=g)
mk("S_Pines", bm, pineM); mk("S_Trunks", bt, trunkM)
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
FIREM = newM("T_FireM", (1, 0.35, 0.08), emit=12)
mk("T_Fire", box(), FIREM, (2.45, 0, 0.55), scl=(0.06, 0.5, 0.3), parent=T)
FIRE = light("T_FireGlow", "POINT", 25, (1, 0.45, 0.15), (2.2, 0, 0.7), T)

# ---------------- the Hush ----------------
H = O["Hush"]; H.scale = (2.4, 2.4, 2.4)
mask_spot = light("T_MaskLight", "SPOT", 9000, (0.7, 0.85, 1.0), (0, 0, 0)); mask_spot.data.spot_size = math.radians(18)
c = mask_spot.constraints.new("TRACK_TO"); c.target = O["H_Mask"]; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
mask_spot.parent = H; mask_spot.location = (2.0, -14, 4.0)

# ---------------- animation ----------------
TK = [(0, -262), (4.6, -212), (8, -172), (9.6, -152), (19, -2), (22.6, 44), (24.6, 52), (25.4, 53), (62.2, 53), (63.4, 60), (64.4, 72),
      (66, 92), (70, 148), (76, 232), (80, 290), (83, 326), (84.6, 336), (100, 336)]
def x_at(t):
    for (ta, sa), (tb, sb) in zip(TK, TK[1:]):
        if ta <= t <= tb:
            u = (t - ta) / (tb - ta) if tb > ta else 0; return sa + (sb - sa) * u
    return TK[-1][1]
for f in list(range(1, END + 1, 2)) + [END]:
    key(T, "location", f, Vector((x_at((f - 1) / FPS), 0, 0)))
key(T, "rotation_euler", 1, Vector((0, 0, 0)))
lin(T)
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
for t, e in ((0, 0), (2.6, 0), (4.0, 60), (7.4, 60), (8.0, 140), (9.6, 70), (41.0, 70), (42.4, 140), (46, 80), (59.0, 80), (59.6, 140), (61.6, 70), (100, 60)):
    gm.default_value = e; gm.keyframe_insert("default_value", frame=F(t))
# doors: front pair closes behind the train, back pair bursts open
OPEN = math.radians(92)
for tag, sgn in (("F1", -1), ("F2", 1)):
    for t, a in ((0, OPEN), (22.8, OPEN), (24.0, 0.0), (100, 0.0)): key(DOORS[tag], "rotation_euler", F(t), sgn * a, 2)
for tag, sgn in (("B1", 1), ("B2", -1)):
    for t, a in ((0, 0.0), (62.3, 0.0), (62.8, OPEN * 1.1), (63.2, OPEN), (100, OPEN)): key(DOORS[tag], "rotation_euler", F(t), sgn * a, 2)
# the loose pane: its steps shake it (57.4-58.0), it slides and falls in (58.0-58.85), shatters on the floor beside the cab
fx = FALL.location.x
for t, loc, rx in ((0, (fx, -SW / 2, 3.62), SL), (57.4, (fx, -SW / 2, 3.62), SL), (57.7, (fx, -SW / 2 + 0.05, 3.60), SL + 0.04),
                   (58.0, (fx, -SW / 2 + 0.2, 3.50), SL + 0.15), (58.85, (fx + 0.1, -1.25, 0.08), 0.3)):
    key(FALL, "location", F(t), Vector(loc)); key(FALL, "rotation_euler", F(t), rx, 0)
for t, s in ((0, 1.0), (58.84, 1.0), (58.9, 0.0)): key(FALL, "scale", F(t), Vector((1.2 * s, (RL - 0.1) * s, 0.03 * s)))
for s_ in SHARDS:
    a = rr.uniform(0, 2 * math.pi); r_ = rr.uniform(0.3, 1.0); end = (s_.location.x + r_ * math.cos(a), -1.25 + 0.5 * r_ * math.sin(a), 0.03)
    sz = (rr.uniform(0.12, 0.3), rr.uniform(0.1, 0.25), 0.02)
    key(s_, "scale", F(0), Vector((0, 0, 0))); key(s_, "scale", F(58.86), Vector((0, 0, 0))); key(s_, "scale", F(58.9), Vector(sz))
    key(s_, "location", F(58.9), Vector((s_.location.x, -1.25, 0.06))); key(s_, "location", F(59.3), Vector(end))
# our lights: put out by Rook at 25.6 ("Lights out."), lit again at 62.0 ("Full steam!")
L0, L1 = 25.6, 62.0
se = M("H_Signal").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 80), (L0, 80), (L0 + 0.6, 3), (L1 - 0.2, 3), (L1 + 0.4, 60), (100, 50)): se.default_value = e; se.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 6), (L0, 6), (L0 + 0.6, 0.3), (L1 - 0.2, 0.3), (L1 + 0.4, 4)): SIGL.data.energy = e; SIGL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 900), (L0, 900), (L0 + 0.4, 0), (L1, 0), (L1 + 0.3, 900)): HL.data.energy = e; HL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 45), (L0, 45), (L0 + 0.6, 16), (L1 - 0.2, 16), (L1 + 0.6, 45)): O["Fill"].data.energy = e; O["Fill"].data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 22), (L0, 22), (L0 + 0.4, 0)): INL.data.energy = e; INL.data.keyframe_insert("energy", frame=F(t))
ie = INM.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 8), (L0, 8), (L0 + 0.4, 0)): ie.default_value = e; ie.keyframe_insert("default_value", frame=F(t))
wi = M("H_Window").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 4), (L0, 4), (L0 + 0.5, 0.0), (L1, 0.0), (L1 + 0.3, 4)): wi.default_value = e; wi.keyframe_insert("default_value", frame=F(t))
fe = FIREM.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 12), (L0, 12), (L0 + 1.0, 1.0), (L1 - 0.2, 1.0), (L1 + 0.2, 20), (100, 14)): fe.default_value = e; fe.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 25), (L0, 25), (L0 + 1.0, 2), (L1 - 0.2, 2), (L1 + 0.2, 40), (100, 30)): FIRE.data.energy = e; FIRE.data.keyframe_insert("energy", frame=F(t))
# Rook head (rz = local direction + 30: 30 ahead, 120 left / north, -150 back, -60 right / south where it is)
for t, rz_ in ((0, -150), (3.0, -150), (3.4, 30), (5.0, 30), (5.4, -150), (9.8, -150), (10.2, 30), (19.8, 30), (20.2, -150), (24.4, -150),
               (24.8, 30), (28.6, 30), (29.0, -60), (54.6, -60), (55.0, -150), (57.8, -150), (58.2, -80), (61.4, -80), (61.8, 30), (68.0, 30),
               (68.4, -150), (73.6, -150), (74.0, 30), (88.8, 30), (89.4, -120), (100, -120)):
    key(HP, "rotation_euler", F(t), math.radians(rz_), 2)
WUP = [(0.6, 1.3), (10.4, 1.2), (16.6, 1.3), (21.0, 1.2), (24.6, 1.0), (59.4, 1.4), (61.6, 1.5), (70.4, 1.2), (78.2, 1.3)]
for sd in (-1, 1):
    wg = O[f"R_Wing{sd}"]; ks = [(0, 0)]
    for t, a in WUP: ks += [(t, 0), (t + 0.3, a), (t + 1.9, a), (t + 2.3, 0)]
    ks += [(7.9, 0), (8.05, 1.7), (9.4, 1.6), (9.8, 0)]                          # flinch: it's at the last car
    ks += [(26.9, 0), (27.3, -0.6), (59.0, -0.6), (59.4, 0)]                     # small and still in the dark
    for t, a in sorted(ks): key(wg, "rotation_euler", F(t), math.radians(sd * 12) + sd * a * 0.6, 1)
for f in range(1, END, 12):
    if F(7.6) <= f <= F(8.8) or F(25.4) <= f <= F(62.2) or f >= F(84.6): continue
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
cam("Cam_01", 0, (2.6, -3.2, 1.8), (0.0, 0, 1.3), 28, T)                          # Rook: the yard lamps went dark
cam("Cam_02", 2.6, (6, 2.2, 3.4), "H_Mask", 55, T)                                 # over the train, back: its face rises
cam("Cam_03", 5.0, (-8, -34, 3), (-12, 0, 10), 18, T)                             # side wide: it catches up, right behind the last car
cam("Cam_03b", 7.8, (3.0, -1.5, 0.8), (-4, 0, 7), 16, T)                          # low on Rook: it is at the last car (flinch)
cam("Cam_04", 10.2, (-95, -45, 16), (-125, 0, 4), 24)                            # high wide: full steam, it behind
cam("Cam_05", 14.0, (-40, -24, 6), (-85, 0, 8), 24)                               # it walks after us, the lamps die
cam("Cam_06", 16.4, (-3, -2.2, 2.6), (14, 0, 2.0), 34, T)                         # over Rook: the old shed ahead
cam("Cam_07", 19.4, (30, -12, 4), (46, 0, 2), 24)                                 # the yard: the train runs in, the doors close
cam("Cam_08", 24.2, (55.8, -1.6, 1.6), (53.4, 0, 1.3), 22, None, free=True)       # inside: Rook, lights out
cam("Cam_09", 27.4, (10, 20, 14), (40, -8, 9), 24)                                # outside: it comes to the shed, eats the lamp
cam("Cam_10", 32.4, (80, 24, 26), (48, -8, 6), 24)                                # high: it walks along the little shed
cam("Cam_11", 36.4, (48.5, 1.7, 0.6), (50, -6, 9), 18, None, free=True)           # inside, up: the glass roof, its shape passes
cam("Cam_12", 41.0, (51.5, 1.6, 0.4), "H_Mask", 20, None, free=True)              # inside, up: its face at the glass (cold open)
cam("Cam_13", 48.4, (2.4, -1.9, 1.5), (0.6, 0, 1.3), 30, T)                       # Rook in the dark
cam("Cam_14", 51.6, (64, 26, 22), (50, -8, 8), 22)                                # high from the north: it bent over the dark shed
cam("Cam_15", 54.6, (16, -40, 4), (46, -10, 10), 24)                              # it straightens and goes
cam("Cam_16", 57.8, (56.8, -2.0, 0.4), (54.4, -1.0, 1.2), 20, None, free=True)    # inside: the pane slides and falls, CRASH
cam("Cam_17", 59.2, (52.0, 1.2, 0.5), "H_Mask", 20, None, free=True)              # inside, up: it is back at the glass
cam("Cam_18", 60.9, (2.6, -1.7, 1.4), (0.6, 0, 1.35), 24, T)                      # Rook: out the back door
cam("Cam_19", 62.2, (74, -5, 1.4), (61, 0, 1.4), 24)                              # the back doors burst open
cam("Cam_20", 66.4, (112, -52, 30), (80, 0, 4), 24)                               # high: we run, it comes after
cam("Cam_21", 70.0, (6, -3.0, 3.5), (0, 0, 1.5), 24, T)                           # side: keep the fire hot
cam("Cam_22", 74.0, (250, -20, 4), (200, 0, 8), 22)                               # the line: the train passes, it far behind
cam("Cam_23", 78.0, (-3, -2.2, 2.6), (14, 0, 2.0), 26, T)                         # over Rook: Ember Town ahead
cam("Cam_24", 82.4, (2.4, -3.2, 1.7), (0.6, 0, 1.35), 28, T)                      # Rook at the station
cam("Cam_25", 87.4, (362, -22, 6), (280, -8, 14), 26)                             # the lit station, it far behind on the line
sc.camera = O["Cam_01"]
sc.render.resolution_x = 1280; sc.render.resolution_y = 720; sc.render.resolution_percentage = 100
sc.eevee.taa_render_samples = 24
try: sc.eevee.use_raytracing = False
except Exception: pass
sc.render.use_compositing = False; sc.render.use_sequencer = False
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "hush_film20.blend"))
print("film20 built", len(sc.collection.all_objects), "objects; markers", len(sc.timeline_markers))
