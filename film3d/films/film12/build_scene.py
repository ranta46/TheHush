# GLOAMRUN 3D Film 14 "The Snow Pass" — run INSIDE Blender (hush_lookdev.blend open, scene HUSH).
# Builds the set + animation + cameras on top of the approved 3D Rook / the Hush / train, then saves
# C:\Users\81803\TremenFilm\hush\film12\hush_film12.blend.  24 fps, 2400 frames (100 s).
# Story: the snowy valley -> the valley lamps die and its face rises over the ridge behind -> it is faster uphill and closes in
# -> Rook's move: under the heavy snow at the top of the pass he blows one long whistle; the snow comes down behind the train and
# closes the pass ("Bring it down!") -> it climbs over the ridge -> lights off, the dark train hides in the old snow shed on the
# ledge -> it stands on the slope right by the shed ('Don't move') -> surprise: the snow under its own heavy feet gives way and it
# slides down the mountain -> lights on, full steam to Pine Town; it climbs back up and follows (it will come again).
import bpy, bmesh, math, random, os
from mathutils import Vector
OUT = r"C:\Users\81803\TremenFilm\hush\film12"; os.makedirs(OUT, exist_ok=True)
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


# ---------------- world: the snowy valley, the pass and its cut, the ledge with the old snow shed, Pine Town ----------------
from mathutils import Matrix
rr = random.Random(1414)
X0 = -175.0                                   # the line runs straight east along y = 0 (x -175 .. 480)
PASS_X, CUT0, CUT1 = 75.0, 45.0, 105.0         # the pass ridge and its narrow cut
SHED0, SHED1 = 140.0, 176.0                    # the old snow shed on the ledge
def ss(a, b, v):
    u = min(1.0, max(0.0, (v - a) / (b - a))); return u * u * (3 - 2 * u)
def pose(s): return (-150.0 + s, 0.0, 0.0)
def gh(x, y):
    ay = abs(y); d = max(0.0, ay - 6.0); wall = ss(6.0, 13.0, ay)
    R = 30.0 * math.exp(-((x - PASS_X) / 28.0) ** 2)                 # the pass ridge (cut through at |y| < 6)
    back = 22.0 * math.exp(-((x + 255.0) / 28.0) ** 2)               # the ridge at the back of the valley
    n = 0.9 * math.sin(x * 0.045 + y * 0.03) + 0.6 * math.sin(x * 0.09 - y * 0.06 + 1.3)
    up = wall * (R + min(40.0, 0.35 * d + 0.002 * d * d) + n * ss(0, 20, d)) + back
    if y < 0:                                                         # past the pass the south side drops away under the ledge
        b = ss(85.0, 115.0, x) * (1.0 - ss(380.0, 410.0, x))
        drop = -min(45.0, 1.1 * max(0.0, -y - 8.0)) + n * ss(0, 20, d) * 0.5
        up = up * (1 - b) + drop * b
    t = ss(375.0, 410.0, x)                                           # Pine Town: flat
    return up * (1 - t) - 0.02
GA = O["Ground"]; GA.location = (0, 0, -60.0); GA.scale = (1400, 1000, 1)
snowM = newM("S_Snow", (0.55, 0.6, 0.7), rough=0.9); rockM = newM("S_RockM", (0.1, 0.1, 0.11), rough=1)
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
        if abs(vv[i][j].co.z - vv[i + 1][j + 1].co.z) > 2.4: f.material_index = 1   # steep rock faces
GO = mk("S_SnowGround", bm, snowM, smooth=True); GO.data.materials.append(rockM)
railM = newM("S_RailM", (0.2, 0.2, 0.22), rough=0.4, metal=0.8); tie = newM("S_Tie", (0.05, 0.04, 0.035), rough=1)
postM = newM("S_Post", (0.02, 0.02, 0.025), rough=0.5); woodM = newM("S_Wood", (0.07, 0.045, 0.03), rough=1)
def pboxes(name, mat, items, parent=None):   # boxes with yaw in ONE mesh: (loc, scl, rz)
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
# the old snow shed on the ledge: open on the drop side (south), wall on the mountain side, snow on the roof
sh_posts = [((x, yy, 2.1), (0.3, 0.3, 4.2), 0) for x in axis(SHED0, SHED1, 4.0) for yy in (-2.9, 3.5)]
pboxes("S_ShedPosts", woodM, sh_posts)
mk("S_ShedWall", box(), woodM, ((SHED0 + SHED1) / 2, 3.75, 2.3), scl=(SHED1 - SHED0 + 0.4, 0.25, 4.6))
mk("S_ShedRoof", box(), woodM, ((SHED0 + SHED1) / 2, 0.3, 4.6), (0.13, 0, 0), scl=(SHED1 - SHED0 + 1.0, 7.4, 0.3))
mk("S_ShedSnow", box(), newM("S_SnowTop", (0.6, 0.63, 0.7), rough=0.9), ((SHED0 + SHED1) / 2, 0.3, 4.95), (0.13, 0, 0), scl=(SHED1 - SHED0 + 1.0, 7.2, 0.4))
# the snow on top of the pass (north side of the cut): it comes down into the cut behind the train (the whistle, 28 - 31.5)
SNOWM = newM("S_SlideM", (0.7, 0.74, 0.82), emit=0.3, rough=0.9)
CH = [((60, 0, 6), (10, 9, 8)), ((70, 0, 7), (10, 10, 9)), ((65, 1, 16), (9, 8, 8)), ((76, -1, 4), (7, 9, 6)), ((55, -2, 3), (6, 8, 5)), ((66, 0, 23), (6, 6, 4))]
for i, (fin, scl) in enumerate(CH):
    o = mk(f"S_Slide{i}", sph(1, 16, 10), SNOWM, scl=scl, smooth=True)
    st = Vector((fin[0], 27 + i * 0.8, gh(fin[0], 27) + 2 + fin[2] * 0.25)); md = Vector((fin[0], 9, fin[2] * 0.6 + 16)); fn = Vector(fin)
    t0 = 28.0 + i * 0.28
    for t, p in ((0, st), (t0, st), (t0 + 1.2, md), (t0 + 2.2, fn), (100, fn)): key(o, "location", F(t), p)
    lin(o)
# the second slide (57.3 - 61.5): the snow on the slope above the shed gives way under the Hush and goes over the roof
for i, x in enumerate((148, 154, 162, 168)):
    o = mk(f"S_Slide2_{i}", sph(1, 14, 8), SNOWM, scl=(5, 4, 2.5), smooth=True)
    st = Vector((x, 16, gh(x, 16) - 1.5)); md = Vector((x - 1, 0, 6.2)); fn = Vector((x - 3, -48, gh(x - 3, -48) + 1)); t0 = 57.3 + i * 0.15
    for t, p in ((0, st), (t0, st), (t0 + 1.4, md), (t0 + 4.0, fn), (100, fn)): key(o, "location", F(t), p)
    lin(o)
# lamps along the valley (they die in a wave from the back as its face rises), along the ledge (it eats them), Pine Town station
RLAMP = []
def lamp(tag, x, y, td, e=55):
    z = max(gh(x, y), 0.0); mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, y, z + 1.7))
    hm = newM(f"L_{tag}", (1, 0.62, 0.25), emit=8); mk(f"L_{tag}", sph(0.2, 12, 8), hm, (x, y, z + 3.45))
    RLAMP.append((hm, light(f"L_{tag}L", "POINT", e, (1, 0.6, 0.3), (x, y, z + 3.2)), td))
for i, x in enumerate((-140, -110, -80, -50, -20, 10, 35)): lamp(f"V{i}", x, -3.2, 5.6 + (x + 140) * 0.012)
for i, (x, td) in enumerate(((120, 46.2), (185, 48.4), (215, 77.0), (250, 81.5), (290, 85.5), (330, 89.5), (370, 94.0))): lamp(f"E{i}", x, 3.6, td)
for i in range(5): lamp(f"St{i}", 436 + i * 9.0, 3.4, 999, 80)
# pines on the slopes, rocks, far peaks
treeM = newM("S_Pine", (0.02, 0.035, 0.025), rough=1); bm = bmesh.new()
for i in range(420):
    x = rr.uniform(-300, 470); y = rr.uniform(-160, 160)
    if abs(y) < 9 or (CUT0 - 8 < x < CUT1 + 8 and abs(y) < 16) or (SHED0 - 10 < x < SHED1 + 20 and -24 < y < 0): continue
    z0 = gh(x, y); h = rr.uniform(5, 10)
    g = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=7, radius1=h * 0.28, radius2=0.0, depth=h)["verts"]
    bmesh.ops.translate(bm, vec=(x, y, z0 + h / 2 + 0.6), verts=g)
mk("S_Pines", bm, treeM)
rocks = []
for i in range(60):
    x = rr.uniform(-280, 460); y = rr.uniform(-140, 140)
    if abs(y) < 8: continue
    s = rr.uniform(0.8, 2.4); rocks.append(((x, y, gh(x, y) + s * 0.3), (s * 1.4, s, s * 0.9), rr.uniform(0, 3)))
pboxes("S_Rocks", rockM, rocks)
farM = newM("S_FarPeak", (0.12, 0.13, 0.17), rough=1)
for i in range(9):
    hx = -320 + i * 100
    mk("S_FarPeak", cyl(1, 0.05, 1, 8), farM, (hx, rr.uniform(260, 300), 20), scl=(rr.uniform(55, 75), 45, rr.uniform(70, 110)))
    mk("S_FarPeak", cyl(1, 0.05, 1, 8), farM, (hx + 50, -rr.uniform(280, 320), -10), scl=(rr.uniform(55, 75), 45, rr.uniform(70, 110)))
# Pine Town and its station at the east end
houseM = newM("S_HouseM", (0.075, 0.07, 0.078), rough=1); roofM = newM("S_Roof", (0.5, 0.53, 0.6), rough=1)
winM = newM("S_Win", (1, 0.62, 0.25), emit=5)
for i in range(26):
    x = rr.uniform(400, 480); y = rr.choice((rr.uniform(12, 50), rr.uniform(-50, -12))); w = rr.uniform(3, 6); h = rr.uniform(2.5, 5)
    z0 = gh(x, y); sd = 1 if y > 0 else -1
    mk("S_House", box(), houseM, (x, y, z0 + h / 2 - 0.5), scl=(w, w, h)); mk("S_Roof", box(), roofM, (x, y, z0 + h - 0.4), scl=(w + 0.4, w + 0.4, 0.3))
    mk("S_Win", box(), winM, (x, y - sd * (w / 2 + 0.02), z0 + h * 0.45), scl=(0.6, 0.05, 0.7))
mk("S_Platform", box(), newM("S_Plat", (0.1, 0.09, 0.1), rough=1), (454, 2.4, 0.0), scl=(40, 2.2, 0.6))
moonM = newM("S_Moon", (0.9, 0.88, 0.8), emit=3)
mk("S_Moon", cyl(9, 9, 0.2, 48), moonM, (150, 380, 120), (math.pi / 2, 0, 0.0))
w = sc.world; w.node_tree.nodes["Background"].inputs[0].default_value = (0.014, 0.018, 0.045, 1)
O["MoonKey"].data.energy = 3.4
FIREM = newM("T_FireM", (1, 0.35, 0.08), emit=12)
mk("T_Fire", box(), FIREM, (2.45, 0, 0.55), scl=(0.06, 0.5, 0.3), parent=T)
FIRE = light("T_FireGlow", "POINT", 25, (1, 0.45, 0.15), (2.2, 0, 0.7), T)

# ---------------- the Hush ----------------
H = O["Hush"]; H.scale = (2.4, 2.4, 2.4)
mask_spot = light("T_MaskLight", "SPOT", 9000, (0.7, 0.85, 1.0), (0, 0, 0)); mask_spot.data.spot_size = math.radians(18)
c = mask_spot.constraints.new("TRACK_TO"); c.target = O["H_Mask"]; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
mask_spot.parent = H; mask_spot.location = (2.0, -14, 4.0)

# ---------------- animation ----------------
SK = [(0, 0), (5, 25), (10, 55), (14, 90), (18, 130), (22, 175), (25, 212), (27, 232), (29, 250), (33, 266), (36, 274), (40.2, 281),
      (43, 290), (46, 302), (48, 306), (61.4, 306), (62.4, 307.5), (65, 320), (70, 365), (76, 430), (82, 495), (88, 555), (92, 585),
      (95, 600), (96.5, 603), (100, 603)]
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
# the Hush: rises over the back ridge (5.4-8), walks up the valley after us (faster uphill), stops at the snow in the cut (31),
# climbs over the south ridge (36-46), stands on the slope right by the shed (50-57.4), the snow under it gives way and it
# slides down the mountain (57.4-61.5), then climbs back up and follows far behind.
HP_ = [(0, -280, 0, -40), (5.4, -280, 0, -40), (6.6, -280, 0, -14), (8.0, -280, 0, 0), (9.0, -280, 0, 0), (10, -262, 0, 0), (14, -215, 0, 0),
       (18, -160, 0, 0), (22, -90, 0, 0), (25, -30, 0, 0), (27, 10, 0, 0), (29, 36, 0, 0), (30.6, 44, 0, 0), (31.4, 46, 0, 0), (35.6, 46, 0, 0),
       (37, 50, 10, 0), (40, 64, 24, 0), (43, 88, 27, 0), (46, 116, 22, 0), (48.2, 145, 16, 0), (50, 158, 13, 0), (57.4, 158, 13, 0),
       (58.4, 158, 4, 4.0), (59.0, 158, -3, 5.0), (60.0, 157, -22, 0), (61.6, 154, -50, 0), (66, 150, -66, 0), (70, 165, -58, 0), (74, 190, -45, 0), (80, 235, -32, 0),
       (86, 295, -26, 0), (92, 350, -22, 0), (100, 420, -18, 0)]
for t, x, y, dz in HP_:
    key(H, "location", F(t), Vector((x, y, gh(x, y) + dz))); key(H, "scale", F(t), Vector((2.4, 2.4, 2.4)))
FEED = empty("S_Feed", (66, 0, 15))                      # where it looks when it is not looking at the train
for t, x, y, z in ((0, 66, 0, 15), (31, 66, 0, 15), (36, 66, 0, 15), (40, 100, 10, 10), (46, 150, 5, 0), (57.2, 150, 5, 0),
                   (57.8, 160, -80, -45), (66, 160, -90, -45)):
    key(FEED, "location", F(t), Vector((x, y, z)))
d1 = H.constraints.new("LOCKED_TRACK"); d1.target = T; d1.track_axis = "TRACK_NEGATIVE_Y"; d1.lock_axis = "LOCK_Z"
d2 = H.constraints.new("LOCKED_TRACK"); d2.target = FEED; d2.track_axis = "TRACK_NEGATIVE_Y"; d2.lock_axis = "LOCK_Z"
for t, v in ((0, 0.0), (30.6, 0.0), (31.4, 1.0), (45.0, 1.0), (47.0, 0.35), (57.2, 0.35), (57.6, 1.0), (66.0, 1.0), (68.0, 0.0)):
    d2.influence = v; d2.keyframe_insert("influence", frame=F(t))
gm = M("H_Green").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 0), (5.2, 0), (7.0, 60), (100, 60)): gm.default_value = e; gm.keyframe_insert("default_value", frame=F(t))
# our lights: out at 40.2 ("It's climbing over! Lights off!"), back on at 61.8 ("Lights on! Full steam!")
L0, L1 = 40.2, 61.8
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
# Rook head (rz = local direction + 30: 30 ahead, 120 left / up at the snow, -150 back, -60 right / the drop side)
for t, rz in ((0, 30), (5.0, 30), (5.6, -150), (9.8, -150), (10.4, 30), (13.0, 30), (13.6, -150), (16.6, -150), (17.2, 30), (21.6, 30),
              (22.2, 120), (25.8, 120), (26.4, 30), (28.0, 30), (28.6, -150), (36.8, -150), (37.4, -120), (41.4, -120), (42.0, 30), (46.0, 30),
              (46.6, 120), (57.4, 120), (58.4, -70), (60.8, -70), (61.4, 30), (72.6, 30), (73.2, -150), (77.4, -150), (78.0, 30), (100, 30)):
    key(HP, "rotation_euler", F(t), math.radians(rz), 2)
for sd in (-1, 1):
    wg = O[f"R_Wing{sd}"]
    for t, a in ((0, 0), (1.0, 0), (1.3, 1.2), (1.6, 0.3), (1.9, 1.2), (2.3, 0), (10.3, 0), (10.6, 1.3), (12.6, 1.3), (13.0, 0),
                 (16.8, 0), (17.1, 1.2), (19.2, 1.2), (19.6, 0), (26.0, 0), (26.3, 1.5), (28.4, 1.5), (28.8, 0),
                 (38.6, 0), (38.9, 1.5), (40.8, 1.5), (41.2, -0.6), (57.4, -0.6), (57.8, 1.0), (59.8, 1.0), (60.2, -0.6), (61.0, -0.6),
                 (61.3, 1.5), (64.0, 1.5), (64.4, 0), (74.6, 0), (74.9, 1.3), (77.0, 1.3), (77.4, 0), (90.4, 0), (90.7, 1.0), (92.8, 1.0), (93.2, 0)):
        key(wg, "rotation_euler", F(t), math.radians(sd * 12) + sd * a * 0.6, 1)
for f in range(1, END, 12):
    if F(40.5) <= f <= F(62.4) or f >= F(96.0): continue     # dark and slow / stopped
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
cam("Cam_01", 0, (3.0, -11, 2.6), (1.0, 0, 1.6), 26, T)                          # wide side: the train in the snowy valley
cam("Cam_02", 5.0, (6, 2.2, 3.4), "H_Mask", 90, T)                                # over the train, back: the lamps die, its face over the ridge
cam("Cam_03", 9.8, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)                       # Rook: it's coming up the valley
cam("Cam_04", 12.8, (-20, -30, 28), (-140, 0, 8), 24)                          # high wide: the valley, the train and the Hush behind
cam("Cam_05", 17.0, (-4, 3.0, 2.8), "H_Mask", 28, T)                              # from the train: it is faster uphill
cam("Cam_06", 20.4, (14, -5, 1.4), (0, 0, 1.6), 30, T)                           # front: the train runs into the cut
cam("Cam_07", 22.6, (1.2, -0.6, 2.2), (66, 24, 34), 24, T, True)                 # behind Rook: all that snow on top of the pass
cam("Cam_08", 26.0, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)                      # Rook: long whistle! bring it down!
cam("Cam_09", 28.0, (125, -3.5, 5), (60, 0, 9), 24)                             # wide: the snow comes down behind the train, it is right there
cam("Cam_10", 31.6, (15, -5, 4), (55, 0, 14), 24)                                   # the Hush stopped at the snow
cam("Cam_11", 33.2, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)                      # Rook: the pass is closed
cam("Cam_12", 36.4, (110, 60, 45), (60, 20, 28), 24)                           # wide: it climbs over the south ridge
cam("Cam_13", 38.6, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)                      # Rook: lights off!
cam("Cam_14", 41.8, (125, -7, 2), (150, 0, 2), 24)                              # the dark train creeps into the snow shed
cam("Cam_15", 46.4, (175, -9, 0.5), "H_Mask", 22)                              # from inside the shed: it comes down the slope
cam("Cam_16", 49.2, (154, -10, -0.5), (157, 2, 7), 20)                             # low behind Rook: its face right over us (cold open)
cam("Cam_17", 52.6, (2.4, -2.6, 1.5), (0.6, 0, 1.45), 30, T)                     # Rook in the dark
cam("Cam_18", 55.2, (190, -40, -12), (158, 4, 8), 30)                           # from below: it stands over the shed; the snow gives way
cam("Cam_19", 59.4, (185, -6, 2), "H_Mask", 24)                             # from the train: it slides down the mountain
cam("Cam_20", 61.0, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)                      # Rook: lights on! full steam!
cam("Cam_21", 63.6, (190, -6, 3), (160, 0, 2), 26)                               # the train comes out of the shed, lights on
cam("Cam_22", 67.6, (8, -9, 3), (0, 0, 1.4), 26, T)                              # side: full steam along the ledge
cam("Cam_23", 72.6, (-4, -3.0, 2.6), "H_Mask", 30, T)                             # back: it climbs back up and follows
cam("Cam_24", 78.6, (330, -110, 40), (260, -15, 0), 22)                          # wide: it follows far behind and below
cam("Cam_25", 85.6, (-20, -14, 8), (30, 0, 2), 24, T)                            # Pine Town ahead
cam("Cam_26", 90.2, (2.4, -3.2, 1.7), (0.6, 0, 1.35), 28, T)                     # Rook at the station
sc.camera = O["Cam_01"]
sc.render.resolution_x = 1280; sc.render.resolution_y = 720; sc.render.resolution_percentage = 100
sc.eevee.taa_render_samples = 24
try: sc.eevee.use_raytracing = False
except Exception: pass
sc.render.use_compositing = False; sc.render.use_sequencer = False
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "hush_film12.blend"))
print("film12 built", len(sc.collection.all_objects), "objects; markers", len(sc.timeline_markers))
