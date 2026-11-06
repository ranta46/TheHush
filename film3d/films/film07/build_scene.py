# GLOAMRUN 3D Film 8 "The Long Hill" — run INSIDE Blender (hush_lookdev.blend open, scene HUSH).
# Builds the set + animation + cameras on top of the approved 3D Rook / the Hush / train, then saves
# C:\Users\81803\TremenFilm\hush\film07\hush_film07.blend.  24 fps, 2400 frames (100 s).
# Story: the high moor at night, the train stops at the top of Long Hill -> the lamps down in the valley die and
# the Hush rises down there, by our line -> it starts to walk UP the hill toward the sound and the light
# -> no way round: Rook closes the firebox, puts out every light (even his eye) and lets the train ROLL down the
# hill with no fire, no light, no sound, right past the Hush in the dark ("Don't move") -> past it! -> surprise:
# at the bottom the old level crossing wakes up, bell ringing, red lamps flashing; the Hush turns
# -> "Open the fire! Full steam!" across the valley to the town; the Hush follows (it will come again).
import bpy, bmesh, math, random, os
from mathutils import Vector
OUT = r"C:\Users\81803\TremenFilm\hush\film07"; os.makedirs(OUT, exist_ok=True)
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

# ---------------- world: the high moor, Long Hill down into the valley, the old level crossing, the valley town ----------------
from mathutils import Matrix
rr = random.Random(88)
PH, X0, X1 = 34.0, 55.0, 255.0            # moor height, top and foot of Long Hill
def prof(x):                               # height of the line
    if x <= X0: return PH
    if x >= X1: return 0.0
    return PH * (1 + math.cos(math.pi * (x - X0) / (X1 - X0))) / 2
def pitch(x):                              # slope angle of the line (+ = going down toward +x)
    if x <= X0 or x >= X1: return 0.0
    return math.atan(PH * math.pi / (2 * (X1 - X0)) * math.sin(math.pi * (x - X0) / (X1 - X0)))
def gh(x, y):                              # ground height (flat bed by the line, rough moor away from it)
    a = min(1.0, max(0.0, (abs(y) - 6) / 10))
    n = 1.2 * math.sin(x * 0.05 + y * 0.03) + 0.8 * math.sin(x * 0.11 - y * 0.07 + 1.3) + 0.6 * math.sin(y * 0.13)
    return prof(x) + a * (n + 0.015 * max(0, abs(y) - 16) ** 1.25) - 0.02
grass = newM("S_Grass", (0.07, 0.08, 0.06), rough=0.95); GA.data.materials.clear(); GA.data.materials.append(grass)
moorM = newM("S_Moor", (0.075, 0.07, 0.065), rough=1)
bm = bmesh.new(); xs = [-200 + i * 4 for i in range(119)]; ys = [-260 + j * 6 for j in range(88)]
vv = [[bm.verts.new((x, y, gh(x, y))) for y in ys] for x in xs]
for i in range(len(xs) - 1):
    for j in range(len(ys) - 1): bm.faces.new((vv[i][j], vv[i + 1][j], vv[i + 1][j + 1], vv[i][j + 1]))
mk("S_MoorGround", bm, moorM, smooth=True)
railM = newM("S_RailM", (0.2, 0.2, 0.22), rough=0.4, metal=0.8); tie = newM("S_Tie", (0.05, 0.04, 0.035), rough=1)
stone = newM("S_Stone", (0.15, 0.145, 0.14), rough=1); woodM = newM("S_Wood", (0.09, 0.07, 0.05), rough=1)
postM = newM("S_Post", (0.02, 0.02, 0.025), rough=0.5); ironM = newM("S_BIron", (0.06, 0.065, 0.075), rough=0.5, metal=0.6)
def pboxes(name, mat, items):   # boxes with yaw + pitch in ONE mesh: (loc, scl, rz, ry)
    bm = bmesh.new()
    for loc, scl, rz, ry in items:
        g = bmesh.ops.create_cube(bm, size=1.0)["verts"]; bmesh.ops.scale(bm, vec=scl, verts=g)
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(rz, 3, "Z") @ Matrix.Rotation(ry, 3, "Y"), verts=g)
        bmesh.ops.translate(bm, vec=loc, verts=g)
    return mk(name, bm, mat)
rails, ties = [], []
for i in range(165):                                        # the line, x -140 .. 520, following the hill
    xa, xb = -140 + i * 4.0, -140 + (i + 1) * 4.0; xm = (xa + xb) / 2
    ln = math.hypot(4.0, prof(xb) - prof(xa)) + 0.02; ry = math.atan2(prof(xa) - prof(xb), 4.0)
    for yy in (-0.53, 0.53): rails.append(((xm, yy, (prof(xa) + prof(xb)) / 2 + 0.03), (ln, 0.08, 0.06), 0, ry))
    for k in (0, 2): ties.append(((xa + k + 1, 0, prof(xa + k + 1) + 0.01), (0.25, 1.4, 0.06), 0, pitch(xa + k + 1)))
pboxes("S_Rails", railM, rails); pboxes("S_Ties", tie, ties)
# dry-stone walls and boulders on the moor, a few bent lone trees
walls, rocks = [], []
for i in range(46):
    x = rr.uniform(-160, 240); y = rr.choice((rr.uniform(9, 120), rr.uniform(-120, -9))); L = rr.uniform(12, 40); a = rr.uniform(-0.5, 0.5) + rr.choice((0, math.pi / 2))
    for k in range(int(L / 3)):
        px, py = x + math.cos(a) * k * 3, y + math.sin(a) * k * 3
        if abs(py) < 7: continue
        walls.append(((px, py, gh(px, py) + 0.45), (3.1, 0.6, 1.1), a, 0))
for i in range(70):
    x = rr.uniform(-180, 260); y = rr.choice((rr.uniform(8, 140), rr.uniform(-140, -8))); s = rr.uniform(0.6, 2.4)
    rocks.append(((x, y, gh(x, y) + s * 0.3), (s * 1.4, s, s * 0.9), rr.uniform(0, 3), 0))
pboxes("S_Walls", stone, walls); pboxes("S_Rocks", newM("S_RockM", (0.12, 0.115, 0.11), rough=1), rocks)
treeM = newM("S_Tree", (0.03, 0.035, 0.03), rough=1)
for i in range(16):
    x = rr.uniform(-150, 250); y = rr.choice((rr.uniform(12, 90), rr.uniform(-90, -12))); h = rr.uniform(3, 6)
    mk("S_TreeT", cyl(0.12, 0.08, h, 6), treeM, (x, y, gh(x, y) + h / 2), (rr.uniform(-0.25, 0.25), rr.uniform(-0.25, 0.25), 0))
    mk("S_TreeC", sph(1, 10, 6), treeM, (x, y, gh(x, y) + h), scl=(h * 0.45, h * 0.35, h * 0.25))
# the valley: road lamps (they die first), farm houses, the river of pines along the valley sides
VLAMP = []
for i, x in enumerate((300, 320, 340, 360, 380, 400)):
    mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, -7.5, 1.7))
    hm = newM(f"L_VHead{i}", (1, 0.62, 0.25), emit=8); mk(f"L_VHead{i}", sph(0.2, 12, 8), hm, (x, -7.5, 3.45))
    VLAMP.append((hm, light(f"L_V{i}", "POINT", 70, (1, 0.6, 0.3), (x, -7.5, 3.2))))
roadM = newM("S_Road", (0.045, 0.04, 0.04), rough=1)
mk("S_Road", box(), roadM, (370, -9.5, 0.005), scl=(260, 3.5, 0.02))
mk("S_CrossRoad", box(), roadM, (280, 0, 0.012), scl=(4.0, 240, 0.02))
winM = newM("S_Win", (1, 0.62, 0.25), emit=5); houseM = newM("S_HouseM", (0.07, 0.065, 0.07), rough=1); roofM = newM("S_Roof", (0.16, 0.07, 0.05), rough=1)
FWIN = newM("L_FarmWin", (1, 0.62, 0.25), emit=5)
for x, y in ((315, -28), (352, 24), (390, -40)):
    mk("S_House", box(), houseM, (x, y, 2.0), scl=(6, 5, 4.5)); mk("S_Roof", box(), roofM, (x, y, 4.4), scl=(6.6, 5.6, 0.4))
    mk("L_FarmWin", box(), FWIN, (x - 3.02, y, 2.2), scl=(0.05, 0.8, 0.9))
pineM = newM("S_Pine", (0.02, 0.05, 0.035), rough=1)
for i in range(60):
    x = rr.uniform(275, 560); y = rr.choice((rr.uniform(14, 80), rr.uniform(-80, -16)))
    if 300 < x < 400 and -46 < y < 30 and rr.random() < 0.6: continue
    h = rr.uniform(4, 8); mk("S_PineT", cyl(h * 0.28, 0.05, h, 8), pineM, (x, y, h / 2 + 0.2))
# valley sides: low hills
hillM = newM("S_HillM", (0.05, 0.06, 0.05), rough=1)
for i in range(6):
    hx = 300 + i * 55
    mk("S_Hill", sph(1, 20, 12), hillM, (hx, rr.uniform(105, 125), -6), scl=(rr.uniform(40, 55), 30, rr.uniform(16, 24)), smooth=True)
    mk("S_Hill", sph(1, 20, 12), hillM, (hx + 25, -rr.uniform(105, 125), -6), scl=(rr.uniform(40, 55), 30, rr.uniform(16, 24)), smooth=True)
# the old level crossing at the foot of the hill (it wakes up by itself)
XX = 280.0; XLAMP = []
for k, (py, sd) in enumerate(((-3.2, -1), (3.2, 1))):
    mk("S_XPost", cyl(0.08, 0.1, 3.6, 8), postM, (XX - 2.5 * sd, py, 1.8))
    mk("S_XBar", box(), newM("S_XWhite", (0.6, 0.6, 0.58), rough=0.8), (XX - 2.5 * sd, py, 3.1), (math.radians(35), 0, 0), (0.06, 1.6, 0.18))
    mk("S_XBar", box(), M("S_XWhite"), (XX - 2.5 * sd, py, 3.1), (math.radians(-35), 0, 0), (0.06, 1.6, 0.18))
    mk("S_XBell", cyl(0.25, 0.08, 0.3, 12), ironM, (XX - 2.5 * sd, py, 3.75))
    mk("S_XBoard", box(), postM, (XX - 2.5 * sd, py, 2.3), scl=(0.06, 1.1, 0.4))
    for j, off in enumerate((-0.4, 0.4)):
        lm = newM(f"L_XRed{k}{j}", (1, 0.05, 0.03), emit=0)
        mk(f"L_XRed{k}{j}", sph(0.16, 12, 8), lm, (XX - 2.5 * sd - 0.08 * sd, py + off, 2.3)); XLAMP.append((j, lm))
XLT = light("L_XLight", "POINT", 0, (1, 0.08, 0.04), (XX, 0, 2.8))
# the valley town and its station
for i in range(36):
    x = rr.uniform(440, 580); y = rr.choice((rr.uniform(8, 40), rr.uniform(-40, -12))); w = rr.uniform(3, 6); h = rr.uniform(2.5, 6)
    mk("S_House", box(), houseM, (x, y, h / 2 - 0.5), scl=(w, w, h)); mk("S_Roof", box(), roofM, (x, y, h - 0.4), scl=(w + 0.4, w + 0.4, 0.3))
    for k in range(2): mk("S_Win", box(), winM, (x + rr.uniform(-w / 3, w / 3), y - math.copysign(w / 2 + 0.02, y), rr.uniform(0.8, h - 1.2)), scl=(0.5, 0.05, 0.6))
mk("S_Platform", box(), newM("S_Plat", (0.1, 0.09, 0.1), rough=1), (505, 2.4, 0.0), scl=(50, 2.2, 0.6))
for i in range(5):
    x = 485 + i * 10.0; mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, 3.2, 1.7))
    mk("L_StHead", sph(0.2, 12, 8), newM("L_StHeadM", (1, 0.62, 0.25), emit=8), (x, 3.2, 3.45)); light(f"L_St{i}", "POINT", 80, (1, 0.6, 0.3), (x, 3.2, 3.2))
moonM = newM("S_Moon", (0.9, 0.88, 0.8), emit=3)
mk("S_Moon", cyl(9, 9, 0.2, 48), moonM, (380, 260, 90), (math.pi / 2, 0, 0))
w = sc.world; w.node_tree.nodes["Background"].inputs[0].default_value = (0.014, 0.018, 0.045, 1)
O["MoonKey"].data.energy = 1.8
# the firebox glow under the cab (closed while we roll)
FIREM = newM("T_FireM", (1, 0.35, 0.08), emit=12)
mk("T_Fire", box(), FIREM, (2.45, 0, 0.55), scl=(0.06, 0.5, 0.3), parent=T)
FIRE = light("T_FireGlow", "POINT", 25, (1, 0.45, 0.15), (2.2, 0, 0.7), T)

# ---------------- the Hush ----------------
H = O["Hush"]; H.scale = (2.4, 2.4, 2.4)
mask_spot = light("T_MaskLight", "SPOT", 9000, (0.7, 0.85, 1.0), (0, 0, 0)); mask_spot.data.spot_size = math.radians(18)
c = mask_spot.constraints.new("TRACK_TO"); c.target = O["H_Mask"]; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
mask_spot.parent = H; mask_spot.location = (2.0, -14, 4.0)

# ---------------- animation ----------------
def tkey(t, x):
    key(T, "location", F(t), Vector((x, 0, prof(x)))); key(T, "rotation_euler", F(t), pitch(x), 1); key(T, "rotation_euler", F(t), 0.0, 2)
TX = [(0, -60), (8, 4), (11, 26), (13.5, 38), (15.5, 42), (30, 42), (34, 47), (38, 60), (42, 81), (46, 108), (50, 140), (54, 174),
      (58, 209), (62, 244), (66, 280), (68, 298), (70, 318), (75, 366), (80, 412), (85, 452), (90, 484), (94, 502), (97.5, 510), (100, 510)]
def tx_at(t):
    for (ta, xa), (tb, xb) in zip(TX, TX[1:]):
        if ta <= t <= tb: u = (t - ta) / (tb - ta); return xa + (xb - xa) * u
    return TX[-1][1]
for (ta, xa), (tb, xb) in zip(TX, TX[1:]):           # dense keys so the train sits on the hill
    n = max(1, int((tb - ta) * 2))
    for k in range(n): t = ta + (tb - ta) * k / n; tkey(t, tx_at(t))
tkey(100, 510); lin(T)
# the valley lamps die, far ones first (9-12)
for i, (hm, lt) in enumerate(VLAMP):
    td = 9.0 + (len(VLAMP) - 1 - i) * 0.5; s = hm.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for t, e in ((td - 0.01, 8), (td + 0.15, 0)): s.default_value = e; s.keyframe_insert("default_value", frame=F(t))
    for t, e in ((td - 0.01, 70), (td + 0.15, 0)): lt.data.energy = e; lt.data.keyframe_insert("energy", frame=F(t))
fs_ = FWIN.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 5), (11.6, 5), (11.9, 0)): fs_.default_value = e; fs_.keyframe_insert("default_value", frame=F(t))
# the Hush: rises in the valley by the line (12-15.5), walks UP the hill beside the line, searches where our light was,
# the dark train rolls right past it (~50), the crossing bell (64.8) turns it round, it walks after us
HY = -16.0
HP_ = [(0, 345, -40), (12.0, 345, -40), (13.5, 345, -14), (15.5, 345, 0), (19, 345, 0), (24, 300, 0), (30, 245, 0), (33, 238, 0),
       (38, 212, 0), (43, 186, 0), (48, 163, 0), (53, 147, 0), (58, 132, 0), (64.8, 112, 0), (67.5, 112, 0), (72, 160, 0), (78, 225, 0),
       (84, 290, 0), (90, 350, 0), (96, 400, 0), (100, 425, 0)]
for t, x, dz in HP_:
    key(H, "location", F(t), Vector((x, HY, gh(x, HY) + dz))); key(H, "scale", F(t), Vector((2.4, 2.4, 2.4)))
BROW = empty("S_Brow", (40, 0, PH + 1))
d1 = H.constraints.new("LOCKED_TRACK"); d1.target = T; d1.track_axis = "TRACK_NEGATIVE_Y"; d1.lock_axis = "LOCK_Z"
d2 = H.constraints.new("LOCKED_TRACK"); d2.target = BROW; d2.track_axis = "TRACK_NEGATIVE_Y"; d2.lock_axis = "LOCK_Z"
for t, v in ((0, 0.0), (31, 0.0), (33, 1.0), (64.9, 1.0), (66.8, 0.0)): d2.influence = v; d2.keyframe_insert("influence", frame=F(t))
gm = M("H_Green").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 0), (12.5, 0), (14, 60), (100, 60)): gm.default_value = e; gm.keyframe_insert("default_value", frame=F(t))
# our lights: Rook closes the firebox and puts out every light (29-31.5); all back on at 68
se = M("H_Signal").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 40), (13, 40), (14, 80), (30.6, 80), (31.6, 3), (67.6, 3), (68.4, 60), (100, 50)): se.default_value = e; se.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 4), (14, 6), (30.6, 6), (31.6, 0.3), (67.6, 0.3), (68.4, 4)): SIGL.data.energy = e; SIGL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 900), (30.0, 900), (30.2, 0), (68.0, 0), (68.3, 900)): HL.data.energy = e; HL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 45), (30.0, 45), (30.8, 12), (67.8, 12), (68.6, 45)): O["Fill"].data.energy = e; O["Fill"].data.keyframe_insert("energy", frame=F(t))
wi = M("H_Window").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 4), (30.3, 4), (30.6, 0.0), (68.0, 0.0), (68.3, 4)): wi.default_value = e; wi.keyframe_insert("default_value", frame=F(t))
fe = FIREM.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 12), (29.2, 12), (29.5, 0), (67.4, 0), (67.8, 20), (100, 14)): fe.default_value = e; fe.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 25), (29.2, 25), (29.5, 0), (67.4, 0), (67.8, 40), (100, 30)): FIRE.data.energy = e; FIRE.data.keyframe_insert("energy", frame=F(t))
# the crossing wakes up: red lamps flash in turn (64.8-75)
for j, lm in XLAMP:
    s = lm.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]; s.default_value = 0; s.keyframe_insert("default_value", frame=F(64.7))
    t = 64.8; on = (j == 0)
    while t < 75:
        s.default_value = 25 if on else 0.3; s.keyframe_insert("default_value", frame=F(t)); on = not on; t += 0.5
    s.default_value = 0; s.keyframe_insert("default_value", frame=F(75.2))
t = 64.8; on = True
while t < 75:
    XLT.data.energy = 120 if on else 40; XLT.data.keyframe_insert("energy", frame=F(t)); on = not on; t += 0.5
XLT.data.energy = 0; XLT.data.keyframe_insert("energy", frame=F(64.7)); XLT.data.keyframe_insert("energy", frame=F(75.2))
for idb in [lm for _, lm in XLAMP] + [XLT.data]:
    ad = idb.animation_data if hasattr(idb, "animation_data") and idb.animation_data else getattr(idb.node_tree, "animation_data", None) if hasattr(idb, "node_tree") else None
    if not ad or not ad.action: continue
    try: fcs = ad.action.layers[0].strips[0].channelbag(ad.action_slot).fcurves
    except Exception: fcs = getattr(ad.action, "fcurves", [])
    for fc in fcs:
        for kp in fc.keyframe_points: kp.interpolation = "CONSTANT"
# Rook head turns (30 = ahead, -40 = to the side, -150 = back) and wings
for t, rz in ((0, 0), (8.4, 0), (9.2, 30), (14.6, 30), (15.4, 30), (19, 30), (25.5, 30), (26.3, 0), (29, 0), (29.8, -40), (31.5, -40),
              (32.3, 30), (44, 30), (44.8, -40), (52, -40), (52.8, -150), (56.5, -150), (57.3, 0), (63, 0), (63.8, 30), (65.5, 30),
              (66.3, -150), (67.2, -150), (68.0, 30), (78, 30), (78.8, -150), (83, -150), (83.8, 0), (100, 0)):
    key(HP, "rotation_euler", F(t), math.radians(rz), 2)
for sd in (-1, 1):
    wg = O[f"R_Wing{sd}"]
    for t, a in ((0, 0), (1.0, 0), (1.3, 1.2), (1.6, 0.3), (1.9, 1.2), (2.3, 0), (15.5, 0), (15.8, 1.3), (18.5, 1.3), (18.9, 0),
                 (25, 0), (25.3, 0.9), (27.5, 0.9), (27.9, 0), (29.0, 0), (29.3, 1.3), (30.5, 1.3), (30.9, 0),
                 (33, 0), (33.4, -0.6), (62.5, -0.6), (62.9, 0), (64.8, 0), (65.1, 1.4), (66.5, 1.4), (66.9, 0),
                 (67.5, 0), (67.8, 1.5), (70.5, 1.5), (70.9, 0), (88, 0), (88.3, 1.4), (90, 1.4), (90.4, 0)):
        key(wg, "rotation_euler", F(t), math.radians(sd * 12) + sd * a * 0.6, 1)
for f in range(1, END, 12):
    if F(15.5) <= f <= F(30) or f >= F(97.5): continue      # train stopped
    if F(31) <= f <= F(67.5): continue                       # rolling in silence (no engine beat)
    key(R, "location", f, 0.62 + (0.02 if (f // 12) % 2 else 0.0), 2)

# ---------------- cameras (one per shot, bound to markers) ----------------
def cam(name, start_s, loc, look, lens=28, parent=None):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_end = 2000
    c = bpy.data.objects.new(name, cd); sc.collection.objects.link(c); c.location = loc
    if parent: c.parent = parent
    if isinstance(look, str): tgt = O[look]
    else:
        tgt = bpy.data.objects.new(name + "_T", None); sc.collection.objects.link(tgt); tgt.location = look; tgt.name = "Cam_T_" + name
        if parent: tgt.parent = parent
    k = c.constraints.new("TRACK_TO"); k.target = tgt; k.track_axis = "TRACK_NEGATIVE_Z"; k.up_axis = "UP_Y"
    m = sc.timeline_markers.new(name, frame=F(start_s)); m.camera = c; return c
cam("Cam_01", 0, (3.0, -11, 2.6), (1.0, 0, 1.6), 26, T)                    # wide side: the train on the high moor
cam("Cam_02", 8, (-7, 0.5, 5.5), (320, -10, -22), 30, T)                    # over the train: down the hill, the valley lamps die
cam("Cam_03", 11.8, (2.6, -3.4, 1.8), (0.6, -0.4, 1.3), 28, T)             # Rook close
cam("Cam_04", 13.5, (-5, -1.5, 3.2), "H_Mask", 70, T)                      # it rises down there, by our line
cam("Cam_05", 19, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)                  # Rook: it is coming up
cam("Cam_06", 22.5, (165, -140, 38), (165, 0, 14), 18)                      # wide: the train at the top, the Hush climbing
cam("Cam_07", 26, (2.2, -2.6, 2.2), (0.6, 0, 1.3), 32, T)                  # Rook: only down
cam("Cam_08", 29, (8, -5, 1.8), (2.2, 0, 1.1), 28, T)                      # outside: fire closed, lights out
cam("Cam_09", 34, (78, 34, prof(78) + 10), (118, -8, prof(118) + 2), 20)                          # wide: the dark train rolls, the Hush comes up
cam("Cam_10", 41, (-1.6, -1.0, 1.9), "H_Mask", 30, T)                      # from the cab: rolling toward it
cam("Cam_11", 46, (2.6, -3.0, 1.6), (0.6, 0, 1.35), 28, T)                 # Rook in the dark
cam("Cam_12", 49.5, (152, 7.0, prof(152) + 0.8), "H_Mask", 16)             # low by the line: the dark train rolls past its feet
cam("Cam_13", 53.5, (-6, -2, 2.4), "H_Mask", 30, T)                         # behind us: its back, it still searches up the hill
cam("Cam_14", 56.5, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)                # Rook: past it
cam("Cam_15", 60, (300, -26, 7), (262, 0, 3), 24)                           # wide: the foot of the hill, the old crossing
cam("Cam_16", 64.5, (287, -10, 2.4), (280, -2, 2.6), 30)                    # the crossing wakes up
cam("Cam_17", 66, (-5, -3, 2.6), "H_Mask", 45, T)                          # it turns round
cam("Cam_18", 68.5, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)                # Rook: open the fire
cam("Cam_19", 72.5, (8, -9, 3), (0, 0, 1.4), 26, T)                         # lights on, full steam across the valley
cam("Cam_20", 78.5, (-4, -3.2, 2.6), "H_Mask", 28, T)                       # looking back: it follows down the hill
cam("Cam_21", 85, (-20, -14, 8), (30, 0, 2), 24, T)                         # wide: the valley town
cam("Cam_22", 92, (2.4, -3.2, 1.7), (0.6, 0, 1.35), 28, T)                  # Rook at the station
sc.camera = O["Cam_01"]
sc.render.resolution_x = 1280; sc.render.resolution_y = 720; sc.render.resolution_percentage = 100
sc.eevee.taa_render_samples = 24
try: sc.eevee.use_raytracing = False
except Exception: pass
sc.render.use_compositing = False; sc.render.use_sequencer = False
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "hush_film07.blend"))
print("film07 built", len(sc.collection.all_objects), "objects; markers", len(sc.timeline_markers))
