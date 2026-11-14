# GLOAMRUN 3D Film 16 "The Falls" — run INSIDE Blender (hush_lookdev.blend open, scene HUSH).
# Story: the river valley -> the lamps behind die and its face rises over the ridge -> it is faster and closes in -> Rook's move:
# the old falls pour over the line under a rock ledge; he puts out every light and the fire and creeps the dark train in BEHIND
# the falling water: the roar hides the sound and the water hides the train -> it stands at the pool right in front of the
# water ('Don't move') -> surprise: it pushes its face to the water, the cold water hits its mask and it pulls back and goes
# down the river -> lights on, out the far side, full steam to Falls Town; it turns back and follows (it will come again).
import bpy, bmesh, math, random, os
from mathutils import Vector
OUT = r"C:\Users\81803\TremenFilm\hush\film13"; os.makedirs(OUT, exist_ok=True)
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


# ---------------- world: the river valley, the old falls over the line under the rock ledge, the pool, Falls Town ----------------
from mathutils import Matrix
rr = random.Random(1616)
X0 = -175.0                                    # the line runs straight east along y = 0 (x -175 .. 480)
FA0, FA1 = 150.0, 186.0                        # the falls: water pours off the ledge in front of the line
FC = (FA0 + FA1) / 2
def ss(a, b, v):
    u = min(1.0, max(0.0, (v - a) / (b - a))); return u * u * (3 - 2 * u)
def pose(s): return (-150.0 + s, 0.0, 0.0)
def gh(x, y):
    n = 0.9 * math.sin(x * 0.045 + y * 0.03) + 0.6 * math.sin(x * 0.09 - y * 0.06 + 1.3)
    if y > 0:                                                        # north: the cliff along the line, highest at the falls
        top = 16.0 + 12.0 * math.exp(-((x - FC) / 60.0) ** 2) + 2.5 * n
        up = ss(4.5, 8.0, y) * top + ss(8, 40, y) * 8.0
    else:                                                            # south: the wide valley floor, hills far away
        d = -y; up = ss(70, 160, d) * (14 + 3 * n) + 0.4 * n * ss(10, 30, d)
        if FA0 - 6 < x < FA1 + 6 and 4 < d < 18: up = -1.2              # the pool under the falls
    back = 22.0 * math.exp(-((x + 255.0) / 28.0) ** 2)               # the ridge at the back of the valley
    t = ss(375.0, 410.0, x)
    return up * (1 - t) + back - 0.02
GA = O["Ground"]; GA.location = (0, 0, -60.0); GA.scale = (1400, 1000, 1)
grassM = newM("S_Grass", (0.035, 0.05, 0.04), rough=1); rockM = newM("S_RockM", (0.09, 0.09, 0.1), rough=1)
GA.data.materials.clear(); GA.data.materials.append(rockM)
def axis(a, b, step):
    out = []; v = a
    while v <= b: out.append(v); v += step
    return out
xs = axis(-400, -302, 6) + axis(-300, 490, 2.0) + axis(496, 600, 6)
ys = axis(-220, -122, 6) + axis(-120, 120, 2.0) + axis(126, 240, 6)
bm = bmesh.new(); vv = [[bm.verts.new((x, y, gh(x, y))) for y in ys] for x in xs]
for i in range(len(xs) - 1):
    for j in range(len(ys) - 1):
        f = bm.faces.new((vv[i][j], vv[i + 1][j], vv[i + 1][j + 1], vv[i][j + 1]))
        if abs(vv[i][j].co.z - vv[i + 1][j + 1].co.z) > 2.0: f.material_index = 1
GO = mk("S_ValleyGround", bm, grassM, smooth=True); GO.data.materials.append(rockM)
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
# the rock ledge over the line and the falling water in front of it (south side)
mk("S_Ledge", box(), rockM, (FC, 1.0, 10.8), scl=(FA1 - FA0 + 12, 12.0, 2.6))
mk("S_LedgeL", box(), rockM, (FA0 - 7, 1.0, 5.0), scl=(4, 12, 10.5)); mk("S_LedgeR", box(), rockM, (FA1 + 7, 1.0, 5.0), scl=(4, 12, 10.5))
mk("S_TopRiver", box(), newM("S_TopWater", (0.12, 0.2, 0.3), emit=0.25, rough=0.1), (FC, 8, 12.2), scl=(FA1 - FA0 - 4, 14, 0.3))
WM = bpy.data.materials.get("S_FallWater") or bpy.data.materials.new("S_FallWater"); WM.use_nodes = True
nt = WM.node_tree; nt.nodes.clear()
outn = nt.nodes.new("ShaderNodeOutputMaterial"); bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping"); wv = nt.nodes.new("ShaderNodeTexWave")
cr = nt.nodes.new("ShaderNodeValToRGB")
wv.wave_type = "BANDS"; wv.bands_direction = "Z"; wv.inputs["Scale"].default_value = 1.6; wv.inputs["Distortion"].default_value = 6.0
wv.inputs["Detail"].default_value = 3.0
nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], wv.inputs["Vector"])
nt.links.new(wv.outputs["Fac"], cr.inputs["Fac"])
cr.color_ramp.elements[0].position = 0.3; cr.color_ramp.elements[0].color = (0.25, 0.4, 0.55, 1)
cr.color_ramp.elements[1].position = 0.9; cr.color_ramp.elements[1].color = (0.8, 0.9, 1.0, 1)
nt.links.new(cr.outputs["Color"], bs.inputs["Base Color"]); nt.links.new(cr.outputs["Color"], bs.inputs["Emission Color"])
bs.inputs["Emission Strength"].default_value = 0.35; bs.inputs["Alpha"].default_value = 0.38; bs.inputs["Roughness"].default_value = 0.2
nt.links.new(bs.outputs["BSDF"], outn.inputs["Surface"])
try: WM.surface_render_method = "DITHERED"
except Exception: pass
try: WM.blend_method = "HASHED"
except Exception: pass
mp.inputs["Location"].default_value = (0, 0, 0); mp.inputs["Location"].keyframe_insert("default_value", frame=1)
mp.inputs["Location"].default_value = (0, 0, 260.0); mp.inputs["Location"].keyframe_insert("default_value", frame=END)
try:
    for fc in WM.node_tree.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
except Exception: pass
bmw = bmesh.new(); bmesh.ops.create_grid(bmw, x_segments=1, y_segments=1, size=0.5)
CUR = mk("S_Falls", bmw, WM, (FC, -3.6, 4.9), (math.pi / 2, 0, 0), (FA1 - FA0 - 2, 12.4, 1))
poolM = newM("S_Pool", (0.04, 0.07, 0.11), emit=0.15, rough=0.05)
mk("S_PoolWater", box(), poolM, (FC, -11, -0.7), scl=(FA1 - FA0 + 14, 14, 0.2))
mk("S_River", box(), poolM, (FC, -110, -0.65), scl=(14, 186, 0.2))
SPRAYM = newM("S_Spray", (0.75, 0.85, 0.95), emit=1.2, rough=0.5)
spr = []
for i in range(26):
    x = rr.uniform(FA0 + 1, FA1 - 1); spr.append(((x, rr.uniform(-6.5, -4.5), rr.uniform(-0.4, 0.6)), (rr.uniform(1.4, 2.6), 1.2, 0.8), rr.uniform(0, 3)))
pboxes("S_SprayFoam", SPRAYM, spr)
# the splash on its mask (55.4 - 56.6)
for i in range(8):
    o = mk(f"S_Splash{i}", sph(1, 12, 8), SPRAYM, scl=(0.01, 0.01, 0.01), smooth=True)
    a = i * 0.785; c0 = Vector((FC + 2, -9.5, 8.5)); c1 = c0 + Vector((math.cos(a) * 3.5, -1.5 - 1.5 * abs(math.sin(a)), math.sin(a) * 3.0))
    for t, p, s in ((0, c0, 0.01), (55.3, c0, 0.01), (55.6, c0, 0.7), (56.6, c1, 0.5), (57.2, c1 - Vector((0, 0, 3)), 0.01), (100, c1, 0.01)):
        key(o, "location", F(t), p); key(o, "scale", F(t), Vector((s, s, s)))
    lin(o)
# lamps along the line (die in a wave as it comes), lamps past the falls, Falls Town station
RLAMP = []
def lamp(tag, x, y, td, e=55):
    z = max(gh(x, y), 0.0); mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, y, z + 1.7))
    hm = newM(f"L_{tag}", (1, 0.62, 0.25), emit=8); mk(f"L_{tag}", sph(0.2, 12, 8), hm, (x, y, z + 3.45))
    RLAMP.append((hm, light(f"L_{tag}L", "POINT", e, (1, 0.6, 0.3), (x, y, z + 3.2)), td))
HX = [(10, -262), (14, -205), (18, -140), (22, -70), (26, -10), (30, 50), (34, 100), (38, 135)]
def h_time(x):
    for (ta, xa), (tb, xb) in zip(HX, HX[1:]):
        if xa <= x <= xb: return ta + (tb - ta) * (x - xa) / (xb - xa)
    return 38.0
for i, x in enumerate((-140, -110, -80, -50, -20, 10, 40, 70, 100, 130)): lamp(f"V{i}", x, -3.2, h_time(x) - 0.6)
for i, x in enumerate((215, 255, 295, 335, 375)): lamp(f"E{i}", x, -3.2, 999)
for i in range(5): lamp(f"St{i}", 436 + i * 9.0, 3.4, 999, 80)
treeM = newM("S_Pine", (0.02, 0.035, 0.025), rough=1); bm = bmesh.new()
for i in range(420):
    x = rr.uniform(-300, 470); y = rr.uniform(-160, 160)
    if abs(y) < 9 or (FA0 - 20 < x < FA1 + 20 and -24 < y < 14) or (FC - 12 < x < FC + 12 and y < 0): continue
    z0 = gh(x, y); h = rr.uniform(5, 10)
    g = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=7, radius1=h * 0.28, radius2=0.0, depth=h)["verts"]
    bmesh.ops.translate(bm, vec=(x, y, z0 + h / 2 + 0.6), verts=g)
mk("S_Pines", bm, treeM)
rocks = []
for i in range(60):
    x = rr.uniform(-280, 460); y = rr.uniform(-140, 140)
    if abs(y) < 8 or (FC - 12 < x < FC + 12 and y < 0): continue
    s = rr.uniform(0.8, 2.4); rocks.append(((x, y, gh(x, y) + s * 0.3), (s * 1.4, s, s * 0.9), rr.uniform(0, 3)))
pboxes("S_Rocks", rockM, rocks)
farM = newM("S_FarPeak", (0.1, 0.11, 0.15), rough=1)
for i in range(9):
    hx = -320 + i * 100
    mk("S_FarPeak", cyl(1, 0.05, 1, 8), farM, (hx, rr.uniform(260, 300), 10), scl=(rr.uniform(55, 75), 45, rr.uniform(60, 90)))
    mk("S_FarPeak", cyl(1, 0.05, 1, 8), farM, (hx + 50, -rr.uniform(280, 320), 0), scl=(rr.uniform(55, 75), 45, rr.uniform(50, 80)))
houseM = newM("S_HouseM", (0.075, 0.07, 0.078), rough=1); roofM = newM("S_Roof", (0.25, 0.12, 0.09), rough=1)
winM = newM("S_Win", (1, 0.62, 0.25), emit=5)
for i in range(26):
    x = rr.uniform(400, 480); y = rr.choice((rr.uniform(12, 50), rr.uniform(-50, -12))); w = rr.uniform(3, 6); h = rr.uniform(2.5, 5)
    z0 = gh(x, y); sd = 1 if y > 0 else -1
    mk("S_House", box(), houseM, (x, y, z0 + h / 2 - 0.5), scl=(w, w, h)); mk("S_Roof", box(), roofM, (x, y, z0 + h - 0.4), scl=(w + 0.4, w + 0.4, 0.3))
    mk("S_Win", box(), winM, (x, y - sd * (w / 2 + 0.02), z0 + h * 0.45), scl=(0.6, 0.05, 0.7))
mk("S_Platform", box(), newM("S_Plat", (0.1, 0.09, 0.1), rough=1), (454, 2.4, 0.0), scl=(40, 2.2, 0.6))
moonM = newM("S_Moon", (0.9, 0.88, 0.8), emit=3)
mk("S_Moon", cyl(9, 9, 0.2, 48), moonM, (170, -380, 110), (math.pi / 2, 0, 0.0))
w = sc.world; w.node_tree.nodes["Background"].inputs[0].default_value = (0.014, 0.018, 0.045, 1)
O["MoonKey"].data.energy = 3.4
FIREM = newM("T_FireM", (1, 0.35, 0.08), emit=12)
mk("T_Fire", box(), FIREM, (2.45, 0, 0.55), scl=(0.06, 0.5, 0.3), parent=T)
FIRE = light("T_FireGlow", "POINT", 25, (1, 0.45, 0.15), (2.2, 0, 0.7), T)
FALLGLOW = light("S_FallsGlow", "AREA", 400, (0.6, 0.75, 1.0), (FC, -14, 9), size=30); FALLGLOW.rotation_euler = (math.radians(-80), 0, 0)

# ---------------- the Hush ----------------
H = O["Hush"]; H.scale = (2.4, 2.4, 2.4)
mask_spot = light("T_MaskLight", "SPOT", 9000, (0.7, 0.85, 1.0), (0, 0, 0)); mask_spot.data.spot_size = math.radians(18)
c = mask_spot.constraints.new("TRACK_TO"); c.target = O["H_Mask"]; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
mask_spot.parent = H; mask_spot.location = (2.0, -14, 4.0)

# ---------------- animation ----------------
SK = [(0, 0), (5, 25), (10, 55), (14, 90), (18, 130), (22, 172), (26, 215), (30, 262), (33.4, 296), (36, 312), (38.4, 318),
      (62.4, 318), (63.4, 320), (66, 340), (70, 380), (76, 440), (82, 500), (88, 560), (92, 590), (95, 603), (96.5, 604), (100, 604)]
def s_at(t):
    for (ta, sa), (tb, sb) in zip(SK, SK[1:]):
        if ta <= t <= tb:
            u = (t - ta) / (tb - ta) if tb > ta else 0; return sa + (sb - sa) * u
    return SK[-1][1]
for f in range(1, END + 1, 4):
    x, y, h = pose(s_at((f - 1) / FPS)); key(T, "location", f, Vector((x, y, 0.0))); key(T, "rotation_euler", f, h, 2)
x, y, h = pose(s_at(100)); key(T, "location", END, Vector((x, y, 0.0))); key(T, "rotation_euler", END, h, 2)
lin(T)
for hm, lt, td in RLAMP:
    if td > 150: continue
    s = hm.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for t, e in ((0, 8), (td - 0.01, 8), (td + 0.15, 0)): s.default_value = e; s.keyframe_insert("default_value", frame=F(t))
    e0 = lt.data.energy
    for t, e in ((0, e0), (td - 0.01, e0), (td + 0.15, 0)): lt.data.energy = e; lt.data.keyframe_insert("energy", frame=F(t))
# the Hush: rises over the back ridge (5.4-8), comes down the valley faster than us, reaches the pool (42), stands right in front
# of the water (44.6-55.3), the water hits its mask (55.4), it pulls back (56.6) and walks off down the river (58-70),
# then turns back and follows far behind.
HP_ = [(0, -280, -10, -40), (5.4, -280, -10, -40), (6.6, -280, -10, -14), (8.0, -280, -10, 0), (9.0, -280, -10, 0), (10, -262, -12, 0),
       (14, -205, -16, 0), (18, -140, -18, 0), (22, -70, -18, 0), (26, -10, -18, 0), (30, 50, -18, 0), (34, 100, -20, 0), (38, 135, -22, 0),
       (42, 158, -24, 0), (44.6, FC, -21, 0), (48.0, FC + 1, -16, 0), (55.3, FC + 2, -14.5, 0), (55.8, FC + 2, -17, 1.0),
       (56.6, FC + 1, -20, 0.5), (58, FC - 2, -32, 0), (62, FC - 6, -60, 0), (66, FC - 8, -88, 0), (70, FC - 6, -105, 0),
       (74, 215, -92, 0), (80, 280, -64, 0), (86, 340, -44, 0), (92, 395, -34, 0), (100, 450, -28, 0)]
for t, x, y, dz in HP_:
    key(H, "location", F(t), Vector((x, y, gh(x, y) + dz))); key(H, "scale", F(t), Vector((2.4, 2.4, 2.4)))
FEED = empty("S_Feed", (FC, -3.6, 5))
for t, x, y, z in ((0, FC, -3.6, 5), (55.3, FC, -3.6, 5), (56.0, FC - 6, -200, 0), (100, FC - 6, -200, 0)):
    key(FEED, "location", F(t), Vector((x, y, z)))
d1 = H.constraints.new("LOCKED_TRACK"); d1.target = T; d1.track_axis = "TRACK_NEGATIVE_Y"; d1.lock_axis = "LOCK_Z"
d2 = H.constraints.new("LOCKED_TRACK"); d2.target = FEED; d2.track_axis = "TRACK_NEGATIVE_Y"; d2.lock_axis = "LOCK_Z"
for t, v in ((0, 0.0), (36.0, 0.0), (38.0, 1.0), (71.0, 1.0), (73.0, 0.0)):
    d2.influence = v; d2.keyframe_insert("influence", frame=F(t))
gm = M("H_Green").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 0), (5.2, 0), (7.0, 60), (55.3, 60), (55.6, 140), (56.6, 25), (60, 60), (100, 60)):
    gm.default_value = e; gm.keyframe_insert("default_value", frame=F(t))
# our lights: out at 33.4 ("Lights off. Fire out. Not a sound."), back on at 62.2 ("It's going down the river. Lights on!")
L0, L1 = 33.4, 62.8
se = M("H_Signal").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 40), (9, 40), (10, 80), (L0 - 0.2, 80), (L0 + 0.8, 3), (L1 - 0.2, 3), (L1 + 0.4, 60), (100, 50)): se.default_value = e; se.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 4), (10, 6), (L0 - 0.2, 6), (L0 + 0.8, 0.3), (L1 - 0.2, 0.3), (L1 + 0.4, 4)): SIGL.data.energy = e; SIGL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 900), (L0 - 0.2, 900), (L0, 0), (L1, 0), (L1 + 0.3, 900)): HL.data.energy = e; HL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 45), (L0 - 0.2, 45), (L0 + 0.4, 18), (L1 - 0.2, 18), (L1 + 0.6, 45)): O["Fill"].data.energy = e; O["Fill"].data.keyframe_insert("energy", frame=F(t))
wi = M("H_Window").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 4), (L0 - 0.1, 4), (L0 + 0.2, 0.0), (L1, 0.0), (L1 + 0.3, 4)): wi.default_value = e; wi.keyframe_insert("default_value", frame=F(t))
fe = FIREM.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 12), (L0 - 0.2, 12), (L0 + 0.1, 0), (L1 - 0.2, 0), (L1 + 0.2, 20), (100, 14)): fe.default_value = e; fe.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 25), (L0 - 0.2, 25), (L0 + 0.1, 0), (L1 - 0.2, 0), (L1 + 0.2, 40), (100, 30)): FIRE.data.energy = e; FIRE.data.keyframe_insert("energy", frame=F(t))
# Rook head (rz = local direction + 30: 30 ahead, 120 left / the cliff, -150 back, -60 right / the water and the valley)
for t, rz in ((0, 30), (5.0, 30), (5.6, -150), (9.8, -150), (10.4, 30), (13.0, 30), (13.6, -150), (16.6, -150), (17.2, 30), (22.4, 30),
              (23.0, 40), (26.4, 40), (27.0, 30), (29.0, 30), (29.6, -150), (33.0, -150), (33.6, 30), (38.6, 30), (39.2, -60), (55.0, -60),
              (55.4, -80), (60.8, -80), (61.4, 30), (72.6, 30), (73.2, -150), (77.4, -150), (78.0, 30), (100, 30)):
    key(HP, "rotation_euler", F(t), math.radians(rz), 2)
for sd in (-1, 1):
    wg = O[f"R_Wing{sd}"]
    for t, a in ((0, 0), (1.0, 0), (1.3, 1.2), (1.6, 0.3), (1.9, 1.2), (2.3, 0), (10.3, 0), (10.6, 1.3), (12.6, 1.3), (13.0, 0),
                 (16.8, 0), (17.1, 1.2), (19.2, 1.2), (19.6, 0), (23.0, 0), (23.3, 0.8), (25.2, 0.8), (25.6, 0),
                 (33.2, 0), (33.5, 1.3), (34.8, 1.3), (35.2, -0.6), (58.4, -0.6), (58.8, 1.2), (60.6, 1.2), (61.0, -0.6), (62.0, -0.6),
                 (62.3, 1.5), (65.0, 1.5), (65.4, 0), (76.0, 0), (76.3, 1.3), (78.2, 1.3), (78.6, 0), (90.4, 0), (90.7, 1.0), (92.8, 1.0), (93.2, 0)):
        key(wg, "rotation_euler", F(t), math.radians(sd * 12) + sd * a * 0.6, 1)
for f in range(1, END, 12):
    if F(33.6) <= f <= F(63.0) or f >= F(96.0): continue
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
cam("Cam_01", 0, (3.0, -11, 2.6), (1.0, 0, 1.6), 26, T)                           # wide side: the train in the river valley
cam("Cam_02", 5.0, (6, 2.2, 3.4), "H_Mask", 90, T)                                 # over the train, back: the lamps die, its face over the ridge
cam("Cam_03", 9.8, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)                        # Rook: it's coming down the valley
cam("Cam_04", 12.8, (-20, -40, 28), (-130, -10, 8), 24)                          # high wide: the valley, the train and the Hush behind
cam("Cam_05", 17.0, (-4, 3.0, 2.8), "H_Mask", 28, T)                               # from the train: it is faster
cam("Cam_06", 20.4, (14, -5, 1.4), (0, 0, 1.6), 30, T)                            # front: the train runs along the cliff
cam("Cam_07", 22.6, (1.2, -0.6, 2.2), (FC, -3.6, 7), 26, T, True)                 # behind Rook: the old falls ahead
cam("Cam_08", 26.6, (FC + 34, -46, 10), (FC - 6, -2, 5), 28)                       # wide: the falls over the line, the train comes
cam("Cam_09", 29.6, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)                       # Rook: lights off, fire out
cam("Cam_10", 34.6, (FC - 4, -30, 3), (FC - 14, 0, 2), 26)                        # the dark train creeps in behind the water
cam("Cam_11", 38.4, (2.4, -2.6, 1.5), (0.6, 0, 1.45), 30, T)                      # Rook behind the water: it can't hear us
cam("Cam_12", 41.6, (FC + 40, -70, 22), "H_Mask", 30)                            # wide: it reaches the pool
cam("Cam_13", 44.4, (FC - 2, 1.6, 1.6), "H_Mask", 24)                             # from behind the water: its shape through the falls
cam("Cam_14", 47.2, (2.4, -2.6, 1.5), (0.6, 0, 1.45), 30, T)                      # Rook in the dark
cam("Cam_15", 49.2, (FC + 1, 1.8, 0.4), (FC + 2, -14, 9), 20)                    # low behind Rook: its face right at the water (cold open)
cam("Cam_16", 52.6, (2.4, -2.6, 1.5), (0.6, 0, 1.45), 30, T)                      # Rook: hold on
cam("Cam_17", 54.6, (FC - 26, -26, 6), "H_Mask", 35)                              # side: its face at the water, the splash
cam("Cam_18", 57.6, (FC + 20, -12, 14), "H_Mask", 30)                             # it walks off down the river
cam("Cam_19", 60.8, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)                       # Rook: lights on!
cam("Cam_20", 63.4, (FA1 + 18, -16, 3), (FA1 - 2, 0, 1.5), 28)                             # the train comes out of the falls, lights on
cam("Cam_21", 67.6, (8, -9, 3), (0, 0, 1.4), 26, T)                               # side: full steam
cam("Cam_22", 72.6, (-4, -3.0, 2.6), "H_Mask", 30, T)                              # back: it turns and follows
cam("Cam_23", 78.6, (330, -110, 40), (260, -30, 0), 22)                           # wide: it follows far behind
cam("Cam_24", 85.6, (-20, -14, 8), (30, 0, 2), 24, T)                             # Falls Town ahead
cam("Cam_25", 90.2, (2.4, -3.2, 1.7), (0.6, 0, 1.35), 28, T)                      # Rook at the station
sc.camera = O["Cam_01"]
sc.render.resolution_x = 1280; sc.render.resolution_y = 720; sc.render.resolution_percentage = 100
sc.eevee.taa_render_samples = 24
try: sc.eevee.use_raytracing = False
except Exception: pass
sc.render.use_compositing = False; sc.render.use_sequencer = False
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "hush_film13.blend"))
print("film13 built", len(sc.collection.all_objects), "objects; markers", len(sc.timeline_markers))
