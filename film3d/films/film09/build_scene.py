# GLOAMRUN 3D Film 10 "The Old Ferry" — run INSIDE Blender (hush_lookdev.blend open, scene HUSH).
# Builds the set + animation + cameras on top of the approved 3D Rook / the Hush / train, then saves
# C:\Users\81803\TremenFilm\hush\film09\hush_film09.blend.  24 fps, 2400 frames (100 s).
# Story: the river valley at night -> the road lamps behind us die and the Hush rises there -> chase -> the line ends at
# the wide river (the old bridge is gone) -> Rook drives onto the old ferry, cuts the rope and puts out every light:
# the dark ferry drifts down the river while the Hush searches the empty line end -> it wades in and stands right
# over us ('Don't move') -> it looks up the river, we drift on -> surprise: the ferry bumps the far dock and the old
# dock bell rings -> the Hush turns; lights on, full steam off the dock along the far bank to River Town; it wades
# after us (it will come again).
import bpy, bmesh, math, random, os
from mathutils import Vector
OUT = r"C:\Users\81803\TremenFilm\hush\film09"; os.makedirs(OUT, exist_ok=True)
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



# ---------------- world: the river valley, the broken bridge, the old ferry, the far dock, River Town ----------------
from mathutils import Matrix
rr = random.Random(1010)
RX0, RX1 = 150.0, 230.0                     # the wide river (flows from +y to -y)
Y2 = -60.0                                  # the far line, on the other bank
def gh(x, y):
    if RX0 < x < RX1: return -3.0           # river bed
    dy = abs(y) if x < RX0 else abs(y - Y2)
    a = min(1.0, max(0.0, (dy - 8) / 14))
    n = 1.0 * math.sin(x * 0.04 + y * 0.03) + 0.7 * math.sin(x * 0.09 - y * 0.06 + 1.3) + 0.5 * math.sin(y * 0.11)
    return a * (n + 0.014 * max(0, dy - 20) ** 1.25) - 0.02
grass = newM("S_Grass", (0.07, 0.08, 0.06), rough=0.95); GA.data.materials.clear(); GA.data.materials.append(grass)
GA.location = (150, 100, -4.0)
plainM = newM("S_Plain", (0.065, 0.08, 0.06), rough=1)
bm = bmesh.new(); xs = [-200 + i * 5 for i in range(171)]; ys = [-240 + j * 6 for j in range(81)]
vv = [[bm.verts.new((x, y, gh(x, y))) for y in ys] for x in xs]
for i in range(len(xs) - 1):
    for j in range(len(ys) - 1): bm.faces.new((vv[i][j], vv[i + 1][j], vv[i + 1][j + 1], vv[i][j + 1]))
mk("S_ValleyGround", bm, plainM, smooth=True)
railM = newM("S_RailM", (0.2, 0.2, 0.22), rough=0.4, metal=0.8); tie = newM("S_Tie", (0.05, 0.04, 0.035), rough=1)
postM = newM("S_Post", (0.02, 0.02, 0.025), rough=0.5); ironM = newM("S_BIron", (0.06, 0.065, 0.075), rough=0.5, metal=0.6)
woodM = newM("S_Wood", (0.09, 0.06, 0.04), rough=1)
def pboxes(name, mat, items, parent=None):   # boxes with yaw + pitch in ONE mesh: (loc, scl, rz, ry)
    bm = bmesh.new()
    for loc, scl, rz, ry in items:
        g = bmesh.ops.create_cube(bm, size=1.0)["verts"]; bmesh.ops.scale(bm, vec=scl, verts=g)
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(rz, 3, "Z") @ Matrix.Rotation(ry, 3, "Y"), verts=g)
        bmesh.ops.translate(bm, vec=loc, verts=g)
    return mk(name, bm, mat, parent=parent)
rails, ties = [], []
def line(x0, x1, y):
    n = int((x1 - x0) / 4)
    for i in range(n):
        xa = x0 + i * 4.0
        for yy in (-0.53, 0.53): rails.append(((xa + 2, y + yy, 0.03), (4.02, 0.08, 0.06), 0, 0))
        for k in (0, 2): ties.append(((xa + k + 1, y, 0.01), (0.25, 1.4, 0.06), 0, 0))
line(-160, 148, 0.0); line(232, 644, Y2)
pboxes("S_Rails", railM, rails); pboxes("S_Ties", tie, ties)
# the river
mk("S_River", box(), newM("S_Water", (0.012, 0.025, 0.045), rough=0.06, metal=0.3), ((RX0 + RX1) / 2, 0, -0.9), scl=(RX1 - RX0 + 2, 480, 0.1))
# the valley: rocks, pines, hills
rocks = []
for i in range(50):
    x = rr.uniform(-180, 140); y = rr.choice((rr.uniform(9, 120), rr.uniform(-120, -9))); s = rr.uniform(0.5, 1.8)
    rocks.append(((x, y, gh(x, y) + s * 0.3), (s * 1.4, s, s * 0.9), rr.uniform(0, 3), 0))
pboxes("S_Rocks", newM("S_RockM", (0.12, 0.115, 0.11), rough=1), rocks)
pineM = newM("S_Pine", (0.025, 0.045, 0.03), rough=1)
bm = bmesh.new()
for i in range(70):
    x = rr.uniform(-190, 640)
    if RX0 - 6 < x < RX1 + 6: continue
    yc = 0.0 if x < RX0 else Y2
    y = yc + rr.choice((rr.uniform(14, 80), rr.uniform(-80, -14))); h = rr.uniform(5, 11)
    if x > 440 and abs(y - Y2) < 40: continue
    g = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=h * 0.28, radius2=0, depth=h)["verts"]
    bmesh.ops.translate(bm, vec=(x, y, gh(x, y) + h / 2), verts=g)
mk("S_Pines", bm, pineM)
hillM = newM("S_HillM", (0.045, 0.055, 0.045), rough=1)
for i in range(9):
    hx = -150 + i * 95
    mk("S_Hill", sph(1, 20, 12), hillM, (hx, rr.uniform(130, 160), -6), scl=(rr.uniform(45, 60), 35, rr.uniform(18, 30)), smooth=True)
    mk("S_Hill", sph(1, 20, 12), hillM, (hx + 40, -rr.uniform(170, 200), -6), scl=(rr.uniform(45, 60), 35, rr.uniform(18, 30)), smooth=True)
# the farm road lamps behind us on the slope (they die when the Hush comes, far ones first)
BLAMP = []
for i, x in enumerate((-120, -100, -80, -60, -40)):
    y = -22.0; z = gh(x, y)
    mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, y, z + 1.7))
    hm = newM(f"L_BHead{i}", (1, 0.62, 0.25), emit=8); mk(f"L_BHead{i}", sph(0.2, 12, 8), hm, (x, y, z + 3.45))
    BLAMP.append((hm, light(f"L_B{i}", "POINT", 60, (1, 0.6, 0.3), (x, y, z + 3.2))))
# the broken bridge: the old line runs on to the water and stops; stone stumps in the river
pboxes("S_Stumps", newM("S_Stone", (0.1, 0.1, 0.1), rough=1), [((x, 0, -1.2), (3, 4, 4.4), 0, 0) for x in (172, 194, 216)] +
       [((RX1 + 1, 0, -1.2), (3, 4, 4.4), 0, 0)])
pboxes("S_BrokenTruss", ironM, [((176, 1.9, 2.0), (6, 0.25, 0.3), 0, math.radians(-20)), ((176, -1.9, 2.0), (6, 0.25, 0.3), 0, math.radians(-25)),
                                 ((214, 1.9, 1.7), (5, 0.25, 0.3), 0, math.radians(30))])
pboxes("S_EndStop", newM("S_Red", (0.6, 0.05, 0.03), rough=0.5), [((148.4, 0, 0.45), (0.3, 1.8, 0.5), 0, 0)])
# the west dock: plank pier beside the line end, a rope post and a lamp (it dies when the Hush comes)
pboxes("S_WestDock", woodM, [((150.5, 0, -0.25), (5, 6, 0.5), 0, 0)] + [((148.5 + k * 2, sd * 2.8, -1.6), (0.3, 0.3, 3), 0, 0) for k in range(3) for sd in (-1, 1)])
mk("S_RopePost", cyl(0.15, 0.15, 1.2, 8), woodM, (152.0, -3.2, 0.6))
DLM = newM("L_DockLampM", (1, 0.62, 0.25), emit=8)
mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (146.5, -3.4, 1.7)); mk("L_DockLamp", sph(0.2, 12, 8), DLM, (146.5, -3.4, 3.45))
DL = light("L_DockLight", "POINT", 70, (1, 0.6, 0.3), (146.5, -3.4, 3.2))
# the old ferry: a flat wooden barge with rails (it carries the train over the river)
BX = 158.5
FER = empty("S_Ferry", (BX, 0, 0))
pboxes("S_FerryDeck", woodM, [((0, 0, -0.35), (13, 4.6, 0.6), 0, 0), ((0, 2.25, 0.05), (13, 0.15, 0.3), 0, 0), ((0, -2.25, 0.05), (13, 0.15, 0.3), 0, 0)], FER)
pboxes("S_FerryRails", railM, [((0, yy, 0.03), (12.6, 0.08, 0.06), 0, 0) for yy in (-0.53, 0.53)], FER)
mk("S_FerryPost", cyl(0.12, 0.12, 1.0, 8), woodM, (-5.6, -2.1, 0.45), parent=FER)
ROPE = mk("S_Rope", cyl(0.04, 0.04, 1.0, 6), newM("S_RopeM", (0.35, 0.28, 0.16), rough=1), (0, 0, 0))
# the rope from the dock post to the barge post (cut at 33.0)
a = Vector((152.0, -3.2, 1.0)); b = Vector((BX - 5.6, -2.1, 0.8)); mid = (a + b) / 2; dv = b - a
ROPE.location = mid; ROPE.rotation_mode = "QUATERNION"; ROPE.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(dv); ROPE.scale = (1, 1, dv.length)
for t, s in ((0, dv.length), (32.9, dv.length), (33.0, 0.0)): key(ROPE, "scale", F(t), s, 2)
# the far dock (other bank, at the far line) with the old dock bell
FDX = 226.0
pboxes("S_FarDock", woodM, [((FDX + 1, Y2, -0.25), (14, 6, 0.5), 0, 0)] + [((FDX - 5 + k * 3, Y2 + sd * 2.8, -1.6), (0.3, 0.3, 3), 0, 0) for k in range(5) for sd in (-1, 1)])
pboxes("S_FarDockRails", railM, [((FDX + 1, Y2 + yy, 0.03), (14, 0.08, 0.06), 0, 0) for yy in (-0.53, 0.53)])
mk("S_BellPost", box(), woodM, (FDX + 2, Y2 - 3.6, 1.6), scl=(0.25, 0.25, 3.2)); mk("S_BellArm", box(), woodM, (FDX + 2, Y2 - 3.1, 3.1), scl=(0.2, 1.2, 0.2))
BELL = empty("S_BellPivot", (FDX + 2, Y2 - 2.6, 3.0))
mk("S_Bell", cyl(0.12, 0.38, 0.6, 16), newM("S_Brass", (0.55, 0.38, 0.12), rough=0.35, metal=0.9), (0, 0, -0.35), parent=BELL)
# River Town and its station (far line, x 480 .. 640)
houseM = newM("S_HouseM", (0.075, 0.07, 0.078), rough=1); roofM = newM("S_Roof", (0.06, 0.06, 0.07), rough=1)
winM = newM("S_Win", (1, 0.62, 0.25), emit=5)
for i in range(22):
    x = rr.uniform(500, 660); y = Y2 + rr.choice((rr.uniform(9, 40), rr.uniform(-40, -9))); w = rr.uniform(3, 6); h = rr.uniform(2.5, 5)
    z0 = gh(x, y)
    mk("S_House", box(), houseM, (x, y, z0 + h / 2 - 0.5), scl=(w, w, h)); mk("S_Roof", box(), roofM, (x, y, z0 + h - 0.4), scl=(w + 0.4, w + 0.4, 0.3))
    mk("S_Win", box(), winM, (x, y - math.copysign(w / 2 + 0.02, y - Y2), z0 + h * 0.45), scl=(0.6, 0.05, 0.7))
mk("S_Platform", box(), newM("S_Plat", (0.1, 0.09, 0.1), rough=1), (565, Y2 + 2.4, 0.0), scl=(50, 2.2, 0.6))
for i in range(5):
    x = 545 + i * 10.0; mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, Y2 + 3.2, 1.7))
    mk("L_StHead", sph(0.2, 12, 8), newM("L_StHeadM", (1, 0.62, 0.25), emit=8), (x, Y2 + 3.2, 3.45)); light(f"L_St{i}", "POINT", 80, (1, 0.6, 0.3), (x, Y2 + 3.2, 3.2))
moonM = newM("S_Moon", (0.9, 0.88, 0.8), emit=3)
mk("S_Moon", cyl(9, 9, 0.2, 48), moonM, (190, 300, 90), (math.pi / 2, 0, 0))
w = sc.world; w.node_tree.nodes["Background"].inputs[0].default_value = (0.014, 0.018, 0.045, 1)
O["MoonKey"].data.energy = 1.8
FIREM = newM("T_FireM", (1, 0.35, 0.08), emit=12)
mk("T_Fire", box(), FIREM, (2.45, 0, 0.55), scl=(0.06, 0.5, 0.3), parent=T)
FIRE = light("T_FireGlow", "POINT", 25, (1, 0.45, 0.15), (2.2, 0, 0.7), T)

# ---------------- the Hush ----------------
H = O["Hush"]; H.scale = (2.4, 2.4, 2.4)
mask_spot = light("T_MaskLight", "SPOT", 9000, (0.7, 0.85, 1.0), (0, 0, 0)); mask_spot.data.spot_size = math.radians(18)
c = mask_spot.constraints.new("TRACK_TO"); c.target = O["H_Mask"]; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
mask_spot.parent = H; mask_spot.location = (2.0, -14, 4.0)

# ---------------- animation ----------------
def tkey(t, x, y):
    key(T, "location", F(t), Vector((x, y, 0))); key(T, "rotation_euler", F(t), 0.0, 1); key(T, "rotation_euler", F(t), 0.0, 2)
# drive to the river, roll onto the ferry (31), cut loose (33), drift down and across in the dark, bump the far dock (63.6), drive off (66.6)
TX = [(0, -110, 0), (8, -50, 0), (12, -15, 0), (16, 20, 0), (20, 58, 0), (24, 95, 0), (27, 124, 0), (29, 141, 0), (31, 157, 0), (34, 157, 0),
      (40, 163, -7), (46, 171, -17), (52, 180, -27), (58, 192, -38), (62, 205, -52), (63.6, 212, -59.6), (64.0, 212.4, -60),
      (66.6, 212.4, -60)]
DRIFT_END = 64.0
# the ferry moves with the train while it carries it
for t, x, y in TX:
    if t >= 31: key(FER, "location", F(t), Vector((x + 1.5, y, 0)))
key(FER, "location", F(0), Vector((BX, 0, 0))); key(FER, "location", F(31), Vector((BX, 0, 0)))
lin(FER)
# off the ferry onto the far dock and the far line
TX2 = [(69.0, 222, -60), (72, 245, -60), (76, 290, -60), (80, 340, -60), (84, 395, -60), (88, 450, -60), (92, 505, -60),
       (96, 552, -60), (98.5, 566, -60), (100, 567, -60)]
for t, x, y in TX + TX2: tkey(t, x, y)
lin(T)
# the lamps behind us die, far ones first (8.0-10.0)
for i, (hm, lt) in enumerate(BLAMP):
    td = 8.0 + i * 0.5; s = hm.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for t, e in ((td - 0.01, 8), (td + 0.15, 0)): s.default_value = e; s.keyframe_insert("default_value", frame=F(t))
    for t, e in ((td - 0.01, 60), (td + 0.15, 0)): lt.data.energy = e; lt.data.keyframe_insert("energy", frame=F(t))
# the west dock lamp: the Hush eats it when it reaches the bank (39.0)
s = DLM.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 8), (39.0, 8), (39.3, 0)): s.default_value = e; s.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 70), (39.0, 70), (39.3, 0)): DL.data.energy = e; DL.data.keyframe_insert("energy", frame=F(t))
# the dock bell: the ferry bumps the far dock at 63.6 and the old bell swings and rings
for t, a in ((0, 0), (63.6, 0), (63.9, 28), (64.3, -22), (64.8, 16), (65.3, -10), (65.9, 5), (66.6, 0)): key(BELL, "rotation_euler", F(t), math.radians(a), 1)
# the Hush: rises behind us on the slope (8-11.5), runs after us, reaches the bank (38), searches the empty line end,
# wades in and stands right over the dark ferry (47-55), looks up the river, turns at the bell (64), wades after us
HP_ = [(0, -78, -30, -40), (8.0, -78, -30, -40), (9.8, -78, -30, -14), (11.5, -78, -30, 0), (16, -45, -18, 0), (20, 0, -16, 0),
       (24, 50, -16, 0), (28, 95, -15, 0), (31, 118, -14, 0), (35, 134, -8, 0), (38, 142, -6, 0), (42, 146, -8, 0),
       (46.5, 176, -14, 0), (55.5, 180, -14, 0), (59, 182, -12, 0), (64.2, 186, -16, 0), (66.5, 188, -24, 0), (70, 196, -40, 0),
       (74, 212, -70, 0), (78, 245, -74, 0), (84, 300, -74, 0), (90, 355, -74, 0), (100, 420, -74, 0)]
for t, x, y, dz in HP_:
    key(H, "location", F(t), Vector((x, y, max(gh(x, y), -1.6) + dz))); key(H, "scale", F(t), Vector((2.4, 2.4, 2.4)))
FEED = empty("S_Feed", (240, 0, 8))                           # where it looks while it searches (the empty line end, then up the river)
for t, x, y in ((34, 240, 2), (44, 240, 2), (46, 200, 6), (55, 170, 80), (64, 170, 90)):
    key(FEED, "location", F(t), Vector((x, y, 8)))
d1 = H.constraints.new("LOCKED_TRACK"); d1.target = T; d1.track_axis = "TRACK_NEGATIVE_Y"; d1.lock_axis = "LOCK_Z"
d2 = H.constraints.new("LOCKED_TRACK"); d2.target = FEED; d2.track_axis = "TRACK_NEGATIVE_Y"; d2.lock_axis = "LOCK_Z"
for t, v in ((0, 0.0), (35.0, 0.0), (36.4, 1.0), (46.4, 1.0), (47.6, 0.0), (54.4, 0.0), (55.8, 1.0), (64.0, 1.0), (65.0, 0.0)):
    d2.influence = v; d2.keyframe_insert("influence", frame=F(t))
gm = M("H_Green").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 0), (8.5, 0), (10, 60), (100, 60)): gm.default_value = e; gm.keyframe_insert("default_value", frame=F(t))
# our lights: all out at 35.4 (Rook: "Lights off. Let the river take us."), back on at 66.6
se = M("H_Signal").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 40), (10, 40), (11, 80), (35.2, 80), (36.2, 3), (66.4, 3), (67.0, 60), (100, 50)): se.default_value = e; se.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 4), (11, 6), (35.2, 6), (36.2, 0.3), (66.4, 0.3), (67.0, 4)): SIGL.data.energy = e; SIGL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 900), (35.2, 900), (35.4, 0), (66.6, 0), (66.9, 900)): HL.data.energy = e; HL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 45), (35.2, 45), (35.8, 14), (66.4, 14), (67.2, 45)): O["Fill"].data.energy = e; O["Fill"].data.keyframe_insert("energy", frame=F(t))
wi = M("H_Window").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 4), (35.3, 4), (35.6, 0.0), (66.6, 0.0), (66.9, 4)): wi.default_value = e; wi.keyframe_insert("default_value", frame=F(t))
fe = FIREM.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 12), (35.2, 12), (35.5, 0), (66.4, 0), (66.8, 20), (100, 14)): fe.default_value = e; fe.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 25), (35.2, 25), (35.5, 0), (66.4, 0), (66.8, 40), (100, 30)): FIRE.data.energy = e; FIRE.data.keyframe_insert("energy", frame=F(t))
# Rook head turns (30 = ahead, -40/-60 = to the side, -150 = back) and wings
for t, rz in ((0, 30), (7.6, 30), (8.4, -150), (12.6, -150), (15.6, -150), (16.4, 30), (20.6, 30), (21.4, -150), (24.4, -150), (25.2, 30),
              (31.6, 30), (32.2, -120), (33.6, -120), (34.2, 0), (40, 0), (40.8, -60), (52, -60), (52.6, -40), (56.5, -40), (57.2, 0),
              (63.4, 0), (63.9, -60), (65.6, -60), (66.2, 30), (73.6, 30), (74.4, -150), (78.4, -150), (79.2, 30), (100, 30)):
    key(HP, "rotation_euler", F(t), math.radians(rz), 2)
for sd in (-1, 1):
    wg = O[f"R_Wing{sd}"]
    for t, a in ((0, 0), (1.0, 0), (1.3, 1.2), (1.6, 0.3), (1.9, 1.2), (2.3, 0), (15.5, 0), (15.8, 1.3), (18.0, 1.3), (18.4, 0),
                 (25.4, 0), (25.7, 1.2), (27.8, 1.2), (28.2, 0), (28.9, 0), (29.2, 1.5), (31.2, 1.5), (31.6, 0),
                 (32.2, 0), (32.5, 1.5), (32.9, 0.2), (33.2, 1.5), (33.8, 0),
                 (36.2, 0), (36.6, -0.6), (63.3, -0.6), (63.7, 0), (63.9, 1.4), (65.6, 1.4), (66.0, 0),
                 (66.2, 0), (66.5, 1.5), (69.0, 1.5), (69.4, 0), (78.0, 0), (78.3, 1.3), (80.4, 1.3), (80.8, 0), (91, 0), (91.3, 1.0), (93.2, 1.0), (93.6, 0)):
        key(wg, "rotation_euler", F(t), math.radians(sd * 12) + sd * a * 0.6, 1)
for f in range(1, END, 12):
    if F(29) <= f <= F(67.5) or f >= F(98.5): continue      # slow / on the ferry / stopped
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
cam("Cam_01", 0, (3.0, -11, 2.6), (1.0, 0, 1.6), 26, T)                    # wide side: the train in the river valley
cam("Cam_02", 7.6, (-6, 2.5, 4.0), (-75, -26, 6), 30, T)                   # looking back: the lamps die, it rises
cam("Cam_03", 11.4, (2.6, -3.4, 1.8), (0.6, -0.4, 1.3), 28, T)             # Rook close
cam("Cam_04", 13.2, (-5, -1.5, 3.2), "H_Mask", 55, T)                      # its face behind us
cam("Cam_05", 15.5, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)                # Rook: full steam
cam("Cam_06", 18.4, (75, -95, 26), (30, -10, 6), 18)                        # wide: the chase down the valley
cam("Cam_07", 21.2, (-4, -3.2, 2.6), "H_Mask", 28, T)                       # from the train: it gains on us
cam("Cam_08", 25.4, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)                # Rook: the bridge is gone
cam("Cam_09", 27.6, (166, -14, 3.4), (151, 0, 1.0), 26)                     # the line ends at the river, the old ferry
cam("Cam_10", 31.6, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)                # Rook: cut the rope, lights off
cam("Cam_11", 37.0, (122, -42, 16), (152, -12, 6), 22)                      # wide: the dark ferry drifts, it comes to the bank
cam("Cam_12", 41.0, (-1.6, -1.0, 1.9), "H_Mask", 35, T)                    # from the ferry: it searches the empty line end
cam("Cam_13", 45.4, (2.6, -3.0, 1.6), (0.6, 0, 1.35), 28, T)               # Rook in the dark
cam("Cam_14", 49.4, (5, -8, 0.2), (1, 8, 8), 16, T)                         # low on the water: it stands right over us
cam("Cam_15", 52.6, (-1.6, -1.0, 1.9), "H_Mask", 30, T)                    # from the cab: up at its face
cam("Cam_16", 56.0, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)                # Rook: it looks up the river
cam("Cam_17", 59.6, (236, -82, 12), (198, -36, 5), 22)                      # wide from downstream: the ferry drifts to the far dock
cam("Cam_18", 63.0, (FDX + 7, Y2 - 9, 2.6), (FDX + 1, Y2 - 2.6, 2.4), 30)   # the bump: the old dock bell rings
cam("Cam_19", 64.6, (-4, -3.2, 2.6), "H_Mask", 32, T)                       # it turns to us
cam("Cam_20", 66.0, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)                # Rook: lights on, full steam
cam("Cam_21", 68.6, (8, -9, 3), (0, 0, 1.4), 26, T)                        # off the dock, away along the far bank
cam("Cam_22", 73.6, (-4, -3.2, 2.6), "H_Mask", 28, T)                      # looking back: it wades after us
cam("Cam_23", 81.0, (395, -22, 10), (350, -66, 3), 22)                      # wide: along the far bank, it follows
cam("Cam_24", 87.0, (-20, -14, 8), (30, 0, 2), 24, T)                      # wide: River Town ahead
cam("Cam_25", 90.6, (2.4, -3.2, 1.7), (0.6, 0, 1.35), 28, T)               # Rook at the station
sc.camera = O["Cam_01"]
sc.render.resolution_x = 1280; sc.render.resolution_y = 720; sc.render.resolution_percentage = 100
sc.eevee.taa_render_samples = 24
try: sc.eevee.use_raytracing = False
except Exception: pass
sc.render.use_compositing = False; sc.render.use_sequencer = False
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "hush_film09.blend"))
print("film09 built", len(sc.collection.all_objects), "objects; markers", len(sc.timeline_markers))
