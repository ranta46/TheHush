# GLOAMRUN 3D Film 19 "The Long Shadow" — run INSIDE Blender (hush_lookdev.blend open, scene HUSH).
# Story (no calm start): the lamps behind die and its face rises over the west ridge at once, the big low moon behind it ->
# on the open salt flat there is nowhere to hide and it is faster -> Rook's move: the low moon throws the Hush's long shadow far
# ahead along the line, so he puts out every light and the fire, lets it come close and keeps the dark train INSIDE its own
# shadow, at its walking speed ("It looks for lights, not at its feet") -> it stops; we stop, right in front of it ('Don't move')
# -> surprise: the old lamp at the salt works flickers on by itself; it steps aside to it and its shadow slides off us: we are in
# the moonlight -> it turns back and sees us. Lights on, full steam to Salt Town; it follows (it will be back).
import bpy, bmesh, math, random, os
from mathutils import Vector
OUT = r"C:\Users\81803\TremenFilm\hush\film16"; os.makedirs(OUT, exist_ok=True)
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




# ---------------- world: the west ridge, the salt flat, the salt works, Salt Town ----------------
from mathutils import Matrix
rr = random.Random(1919)
X0 = -240.0                                    # the line runs straight east along y = 0 (x -240 .. 560)
def ss(a, b, v):
    u = min(1.0, max(0.0, (v - a) / (b - a))); return u * u * (3 - 2 * u)
def pose(s): return (-150.0 + s, 0.0, 0.0)
def gh(x, y):
    n = 0.9 * math.sin(x * 0.045 + y * 0.03) + 0.6 * math.sin(x * 0.09 - y * 0.06 + 1.3)
    d = abs(y); up = ss(110, 200, d) * (14 + 4 * n)
    back = 24.0 * math.exp(-((x + 300.0) / 30.0) ** 2)                # the ridge in the west (it comes over it)
    east = ss(600, 680, x) * 12
    return up + back + east - 0.02
GA = O["Ground"]; GA.location = (0, 0, -40.0); GA.scale = (1400, 1000, 1)
saltM = newM("S_Salt", (0.30, 0.31, 0.35), rough=0.95); rockM = newM("S_RockM", (0.08, 0.08, 0.09), rough=1)
GA.data.materials.clear(); GA.data.materials.append(rockM)
def axis(a, b, step):
    out = []; v = a
    while v <= b: out.append(v); v += step
    return out
xs = axis(-440, -346, 6) + axis(-340, -202, 2.0) + axis(-198, 560, 4.0) + axis(566, 700, 6)
ys = axis(-246, -132, 6) + axis(-126, 126, 4.0) + axis(132, 246, 6)
bm = bmesh.new(); vv = [[bm.verts.new((x, y, gh(x, y))) for y in ys] for x in xs]
for i in range(len(xs) - 1):
    for j in range(len(ys) - 1):
        f = bm.faces.new((vv[i][j], vv[i + 1][j], vv[i + 1][j + 1], vv[i][j + 1]))
        if vv[i][j].co.z > 3.0: f.material_index = 1
GO = mk("S_SaltGround", bm, saltM, smooth=True); GO.data.materials.append(rockM)
# the salt crust: raised white ridges in a broken honeycomb near the line
crustM = newM("S_Crust", (0.5, 0.51, 0.55), rough=0.9)
bm = bmesh.new(); nr = 0
CS = 7.0
for i in range(-30, 92):
    for j in range(-11, 12):
        cx = i * CS * 0.866 * 1.0; cy = j * CS + (CS / 2 if i % 2 else 0)
        cx += rr.uniform(-1.2, 1.2); cy += rr.uniform(-1.2, 1.2)
        if cx < -205 or cx > 430 or abs(cy) < 2.4: continue
        for k in range(3):
            if rr.random() < 0.25: continue
            a = k * math.pi / 3 + rr.uniform(-0.25, 0.25); L = CS * 0.58 * rr.uniform(0.8, 1.15)
            px = cx + 0.5 * L * math.cos(a); py = cy + 0.5 * L * math.sin(a)
            if abs(py) < 2.2: continue
            g = bmesh.ops.create_cube(bm, size=1.0)["verts"]; bmesh.ops.scale(bm, vec=(L, 0.22, 0.08), verts=g)
            bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(a, 3, "Z"), verts=g)
            bmesh.ops.translate(bm, vec=(px, py, gh(px, py) + 0.02), verts=g); nr += 1
mk("S_CrustRidges", bm, crustM)
print("ridges", nr)
railM = newM("S_RailM", (0.2, 0.2, 0.22), rough=0.4, metal=0.8); tie = newM("S_Tie", (0.05, 0.04, 0.035), rough=1)
postM = newM("S_Post", (0.02, 0.02, 0.025), rough=0.5)
def pboxes(name, mat, items, parent=None):
    bm = bmesh.new()
    for loc, scl, rz in items:
        g = bmesh.ops.create_cube(bm, size=1.0)["verts"]; bmesh.ops.scale(bm, vec=scl, verts=g)
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(rz, 3, "Z"), verts=g); bmesh.ops.translate(bm, vec=loc, verts=g)
    return mk(name, bm, mat, parent=parent)
rails, ties = [], []
for i in range(int((560 - X0) / 2)):
    x = X0 + i * 2 + 1
    for yy in (-0.53, 0.53): rails.append(((x, yy, 0.03), (2.03, 0.08, 0.06), 0.0))
    ties.append(((x, 0, 0.01), (0.25, 1.4, 0.06), 0.0))
pboxes("S_Rails", railM, rails); pboxes("S_Ties", tie, ties)
pboxes("S_EndStop", newM("S_Red", (0.6, 0.05, 0.03), rough=0.5), [((X0 + 2, 0, 0.45), (0.3, 1.8, 0.5), 0), ((558, 0, 0.45), (0.3, 1.8, 0.5), 0)])
# old telegraph poles along the line (they give the flat its size)
poles = []
for x in axis(-230, 540, 22):
    poles.append(((x, -6.0, 3.0), (0.16, 0.16, 6.0), 0)); poles.append(((x, -6.0, 5.6), (0.1, 1.6, 0.1), 0))
pboxes("S_Poles", postM, poles)
# lamps along the line (die in a wave as it passes), the old salt works lamp (dark, it flickers on by itself), Salt Town
RLAMP = []
def lamp(tag, x, y, td, e=55):
    z = max(gh(x, y), 0.0); mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, y, z + 1.7))
    hm = newM(f"L_{tag}", (1, 0.62, 0.25), emit=8); mk(f"L_{tag}", sph(0.2, 12, 8), hm, (x, y, z + 3.45))
    lo = light(f"L_{tag}L", "POINT", e, (1, 0.6, 0.3), (x, y, z + 3.2)); RLAMP.append((hm, lo, td)); return hm, lo
HP_ = [(0, -300, 0, -40), (2.4, -300, 0, -40), (3.4, -300, 0, -14), (4.6, -300, 0, 0), (5.4, -296, 0, 0), (6, -285, 0, 0),
       (10, -218, 0, 0), (14, -150, 0, 0), (18, -82, 0, 0), (20, -48, 0, 0), (24, 18, 0, 0), (27, 70, 0, 0), (33, 106, 0, 0),
       (39, 142, 0, 0), (42, 160, 0, 0), (55.4, 160, 0, 0), (56.4, 162, 6, 0), (57.4, 164, 12, 0), (58.2, 165, 16, 0),
       (59.0, 165, 16, -0.4), (60.2, 166, 15, -0.4), (61, 168, 13, 0), (64, 190, 8, 0), (70, 252, 2, 0), (76, 304, 0, 0), (82, 356, 0, 0),
       (88, 404, -6, 0), (94, 440, -14, 0), (100, 462, -20, 0)]
def h_time(x):
    for (ta, xa, *_), (tb, xb, *_) in zip(HP_[4:], HP_[5:]):
        if xa <= x <= xb and xb > xa: return ta + (tb - ta) * (x - xa) / (xb - xa)
    return 999.0
for i, x in enumerate((-225, -205, -185, -165)): lamp(f"B{i}", x, -3.2, 0.2 + i * 0.5)        # the lamps behind die first
for i, x in enumerate((-130, -100, -70, -40, -10, 20)): lamp(f"V{i}", x, -3.2, h_time(x) + 0.4)
WLM, WLL = lamp("Works", 236, 40, 999, 140)                                                       # the old salt works lamp
for i, x in enumerate((430, 455, 480)): lamp(f"E{i}", x, -3.2, 999)
for i in range(5): lamp(f"St{i}", 512 + i * 9.0, 3.4, 999, 80)
# the salt works: white heaps, an old shed, a chimney
heapM = newM("S_Heap", (0.55, 0.56, 0.6), rough=0.9); shedM = newM("S_Shed", (0.08, 0.07, 0.07), rough=1)
bm = bmesh.new()
for k in range(9):
    hx = 210 + (k % 5) * 13 + rr.uniform(-2, 2); hy = 52 + (k // 5) * 14 + rr.uniform(-2, 2); h = rr.uniform(5, 9)
    g = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12, radius1=h * 0.9, radius2=0.3, depth=h)["verts"]
    bmesh.ops.translate(bm, vec=(hx, hy, h / 2), verts=g)
mk("S_Heaps", bm, heapM, smooth=True)
mk("S_Shed", box(), shedM, (246, 47, 2.0), scl=(10, 5, 4)); mk("S_ShedRoof", box(), newM("S_Roof", (0.25, 0.12, 0.09), rough=1), (246, 47, 4.2), (0.12, 0, 0), scl=(10.6, 5.6, 0.3))
mk("S_Chimney", cyl(0.9, 0.7, 14, 10), shedM, (254, 52, 7))
# far peaks, Salt Town (white houses, lit windows), the platform
farM = newM("S_FarPeak", (0.1, 0.11, 0.15), rough=1)
for i in range(10):
    hx = -340 + i * 105
    mk("S_FarPeak", cyl(1, 0.05, 1, 8), farM, (hx, rr.uniform(270, 310), 10), scl=(rr.uniform(55, 75), 45, rr.uniform(35, 60)))
    mk("S_FarPeak", cyl(1, 0.05, 1, 8), farM, (hx + 50, -rr.uniform(290, 330), 0), scl=(rr.uniform(55, 75), 45, rr.uniform(35, 55)))
houseM = newM("S_HouseM", (0.2, 0.2, 0.22), rough=1); roofM = M("S_Roof")
winM = newM("S_Win", (1, 0.62, 0.25), emit=5)
for i in range(28):
    x = rr.uniform(470, 560); y = rr.choice((rr.uniform(12, 50), rr.uniform(-50, -12))); w = rr.uniform(3, 6); h = rr.uniform(2.5, 5)
    z0 = gh(x, y); sd = 1 if y > 0 else -1
    mk("S_House", box(), houseM, (x, y, z0 + h / 2 - 0.5), scl=(w, w, h)); mk("S_Roof", box(), roofM, (x, y, z0 + h - 0.4), scl=(w + 0.4, w + 0.4, 0.3))
    mk("S_Win", box(), winM, (x, y - sd * (w / 2 + 0.02), z0 + h * 0.45), scl=(0.6, 0.05, 0.7))
mk("S_Platform", box(), newM("S_Plat", (0.1, 0.09, 0.1), rough=1), (530, 2.4, 0.0), scl=(40, 2.2, 0.6))
mk("S_TownHeap", cyl(6, 0.3, 7, 12), heapM, (500, 26, 3.5))
# the big low moon in the west (behind the Hush): it throws the long shadow east along the line
EL = math.radians(13.0)
moonM = newM("S_Moon", (0.9, 0.9, 0.85), emit=4)
mk("S_Moon", cyl(26, 26, 0.2, 48), moonM, (-760, -22, 760 * math.tan(EL)), (math.pi / 2, 0, math.pi / 2))
w = sc.world; w.node_tree.nodes["Background"].inputs[0].default_value = (0.014, 0.018, 0.045, 1)
MK = O["MoonKey"]; MK.data.energy = 3.4; MK.data.color = (0.75, 0.82, 1.0); MK.rotation_euler = (0, EL - math.pi / 2, 0)
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
SK = [(0, 0), (4, 44), (8, 90), (12, 136), (16, 182), (20, 226), (22, 236), (24, 243), (27, 250), (33, 286), (39, 322), (42, 340),
      (43.2, 345), (59.9, 345), (62, 352), (64, 366), (66, 386), (70, 432), (74, 482), (78, 532), (82, 580), (86, 622), (90, 660),
      (93, 678), (95, 684), (96.5, 685), (100, 685)]
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
# the old salt works lamp: dark, flickers on by itself (55.0-55.8), it goes to it, then it is eaten (59.2)
ws = WLM.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, k in ((0, 0), (54.9, 0), (55.0, 1), (55.15, 0), (55.3, 1), (55.4, 0.2), (55.6, 1), (59.1, 1), (59.3, 0), (100, 0)):
    ws.default_value = 9 * k; ws.keyframe_insert("default_value", frame=F(t)); WLL.data.energy = 160 * k; WLL.data.keyframe_insert("energy", frame=F(t))
for t, (x, y, dz) in [(p[0], p[1:]) for p in HP_]:
    key(H, "location", F(t), Vector((x, y, gh(x, y) + dz))); key(H, "scale", F(t), Vector((2.4, 2.4, 2.4)))
# where it looks: far ahead along the flat for lights (22-55), then at the salt works lamp, then back down at us
SEARCH = empty("S_Search", (420, 0, 20))
for t, p in ((0, (420, 0, 20)), (22, (420, 0, 20)), (26, (420, 70, 20)), (31, (420, -80, 20)), (36, (420, 50, 20)), (41, (420, -40, 20)),
             (44, (420, 30, 20)), (48, (420, -20, 20)), (54.8, (420, 10, 20)), (55.6, (236, 40, 4)), (58.6, (236, 40, 4)), (100, (236, 40, 4))):
    key(SEARCH, "location", F(t), Vector(p))
d1 = H.constraints.new("LOCKED_TRACK"); d1.target = T; d1.track_axis = "TRACK_NEGATIVE_Y"; d1.lock_axis = "LOCK_Z"
d2 = H.constraints.new("LOCKED_TRACK"); d2.target = SEARCH; d2.track_axis = "TRACK_NEGATIVE_Y"; d2.lock_axis = "LOCK_Z"
for t, v in ((0, 0.0), (21.0, 0.0), (23.0, 1.0), (58.8, 1.0), (59.6, 0.0)):
    d2.influence = v; d2.keyframe_insert("influence", frame=F(t))
gm = M("H_Green").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 0), (2.6, 0), (4.0, 60), (59.0, 60), (59.4, 140), (60.6, 80), (100, 60)):
    gm.default_value = e; gm.keyframe_insert("default_value", frame=F(t))
# our lights: out at 21.2 ("Lights off! Into its shadow!"), back on at 60.2 ("It sees us! Lights on! Full steam!")
L0, L1 = 21.2, 60.2
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
for t, rz in ((0, -150), (2.4, -150), (2.9, 30), (6.0, 30), (6.4, -150), (8.8, -150), (9.2, 30), (12.0, 30), (12.4, -150), (14.0, -150),
              (14.4, 30), (24.0, 30), (24.4, -150), (27.0, -150), (27.4, 30), (40.0, 30), (40.4, -150), (54.8, -150),
              (55.2, 100), (57.8, 100), (58.2, -150), (59.8, -150), (60.2, 30), (66.0, 30), (66.4, -150), (69.6, -150), (70.0, 30), (100, 30)):
    key(HP, "rotation_euler", F(t), math.radians(rz), 2)
for sd in (-1, 1):
    wg = O[f"R_Wing{sd}"]
    for t, a in ((0, 0), (0.6, 0), (0.9, 1.3), (1.3, 0.4), (1.7, 1.3), (2.6, 0), (6.0, 0), (6.3, 1.2), (8.2, 1.2), (8.6, 0),
                 (12.0, 0), (12.3, 1.2), (14.2, 1.2), (14.6, 0), (16.4, 0), (16.7, 1.0), (18.6, 1.0), (19.0, 0), (21.0, 0), (21.3, 1.4), (23.2, 1.4), (23.6, -0.6),
                 (56.2, -0.6), (56.6, 0.5), (58.6, 0.5), (59.0, -0.6), (59.6, -0.6), (59.9, 1.5), (62.4, 1.5), (62.8, 0), (76.6, 0), (76.9, 1.3),
                 (78.8, 1.3), (79.2, 0), (88.4, 0), (88.7, 1.0), (90.8, 1.0), (91.2, 0)):
        key(wg, "rotation_euler", F(t), math.radians(sd * 12) + sd * a * 0.6, 1)
for f in range(1, END, 12):
    if F(21.0) <= f <= F(60.4) or f >= F(95.0): continue
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
cam("Cam_01", 0, (2.6, -3.2, 1.8), (0.0, 0, 1.3), 28, T)                          # Rook: the lamps are going out behind us
cam("Cam_02", 2.6, (6, 2.2, 3.4), "H_Mask", 60, T)                                 # over the train, back: its face rises over the ridge, the moon
cam("Cam_03", 6.0, (-60, -85, 32), (-150, 0, 8), 22)                              # high wide: the flat, the train and the Hush behind
cam("Cam_04", 10.0, (-4, 3.0, 2.8), "H_Mask", 28, T)                               # from the train: it is gaining
cam("Cam_05", 13.0, (14, -5, 1.4), (0, 0, 1.6), 30, T)                            # front: nowhere to hide on the flat
cam("Cam_06", 16.2, (-30, -75, 45), (-30, 0, 0), 22)                              # high: its long shadow on the salt, reaching for us
cam("Cam_07", 20.0, (-3, -1.5, 2.8), (8, 0, 1), 26, T)                            # behind Rook: lights off!
cam("Cam_08", 23.0, (118, -30, 2.5), (60, 0, 8), 22)                              # low ahead: it comes, the dark train slides into its shadow
cam("Cam_09", 27.0, (150, -95, 50), (105, 0, 3), 24)                              # high side: the shadow band over the dark train
cam("Cam_10", 30.4, (2.4, -2.6, 3.0), (0.6, 0, 1.45), 30, T)                      # Rook: slow now, same speed as it
cam("Cam_11", 33.6, (3.5, 1.6, 0.8), "H_Mask", 22, T)                              # low from the front of the train: it walks right behind us
cam("Cam_12", 36.4, (300, 35, 22), (160, 0, 8), 30)                               # far ahead looking back: the moon, the Hush, its shadow, us
cam("Cam_13", 40.2, (2.4, -2.6, 3.0), (0.6, 0, 1.45), 30, T)                      # Rook: it stopped. Stop!
cam("Cam_14", 42.8, (185, -42, 4), "H_Mask", 30)                                  # side low: it stands still, looking far
cam("Cam_15", 45.6, (203, 1.4, 1.2), "H_Mask", 20)                                # low in front of the train: it towers over us
cam("Cam_16", 49.6, (2.6, -2.2, 0.75), (-4.0, 0.4, 3.6), 18, T)                   # low beside Rook: its face right over us (cold open)
cam("Cam_17", 54.6, (214, 22, 2.4), (236, 40, 3.5), 32)                            # the old salt works lamp flickers on by itself
cam("Cam_18", 55.8, (150, -80, 34), (180, 6, 3), 26)                              # high: it steps aside, its shadow slides off us
cam("Cam_19", 58.4, (2.4, -2.6, 3.0), (0.6, 0, 1.45), 28, T)                      # Rook in the moonlight: it sees us!
cam("Cam_20", 62.4, (6, 8, 9), (0, 0, 1), 28, T)                                  # side: full steam over the salt
cam("Cam_21", 66.0, (-4, 3.0, 3.2), "H_Mask", 30, T)                               # back: it follows
cam("Cam_22", 70.0, (330, -40, 6), (280, 0, 4), 24)                               # wide low: the train races past the poles, it behind
cam("Cam_23", 76.2, (-3, -1.5, 2.8), (8, 0, 1), 26, T)                            # behind Rook: faster
cam("Cam_24", 80.0, (420, -30, 4), (370, 0, 10), 24)                              # low: it walks after us over the flat
cam("Cam_25", 84.0, (-20, -14, 8), (30, 0, 2), 24, T)                             # Salt Town ahead
cam("Cam_26", 88.0, (2.4, -3.2, 1.7), (0.6, 0, 1.35), 28, T)                      # Rook at the station
sc.camera = O["Cam_01"]
sc.render.resolution_x = 1280; sc.render.resolution_y = 720; sc.render.resolution_percentage = 100
sc.eevee.taa_render_samples = 24
try: sc.eevee.use_raytracing = False
except Exception: pass
sc.render.use_compositing = False; sc.render.use_sequencer = False
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "hush_film16.blend"))
print("film16 built", len(sc.collection.all_objects), "objects; markers", len(sc.timeline_markers))
