# GLOAMRUN 3D Film 4 "The Echo Canyon" — run INSIDE Blender (hush_lookdev.blend open, scene HUSH).
# Builds the set + animation + cameras on top of the approved 3D Rook / the Hush / train, then saves
# C:\Users\81803\TremenFilm\hush\film03\hush_film03.blend.  24 fps, 2400 frames (100 s).
# Story: canyon run, the walls sing the wheels back -> the echo stops, the lamps die -> the Hush on the rim -> chase
# -> at the fork Rook blows a long whistle into the side canyon; the Hush follows the echo away -> it comes around and
# stands on the rim above the stone arch where the train hides, dark -> the old echo comes back from far away and it
# walks off after it -> quiet wheels, then full steam out of the canyon to the desert station lights.
import bpy, bmesh, math, random, os
from mathutils import Vector
OUT = r"C:\Users\81803\TremenFilm\hush\film03"; os.makedirs(OUT, exist_ok=True)
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
for o in list(bpy.data.objects):
    if o.name.startswith(("S_", "L_", "Cam_", "T_", "V_", "Peek")): bpy.data.objects.remove(o, do_unlink=True)
for o in list(sc.collection.all_objects):
    if o.animation_data: o.animation_data_clear()
sc.timeline_markers.clear()
for n in ("HCam", "MoonDisc", "MaskLight", "WarmRim", "SignalGlow"):
    if n in O: bpy.data.objects.remove(O[n], do_unlink=True)
O["Ground"].scale = (2000, 400, 1); O["Ground"].location = (300, 0, -0.5)
for n in ("Rail", "Rail2"): O[n].scale = (1400, 0.08, 0.04); O[n].location.x = 300

# ---------------- train group ----------------
T = empty("Train")
for n in ("Car", "CarTrim", "Cab", "CabWin", "Boiler", "Stack", "Lamp", "Rook") + tuple(o.name for o in sc.collection.all_objects if o.name.startswith("Wheel")):
    o = O[n]; o.parent = T
# head light + Rook light travel with the train
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
# Rook head pivot (to turn the head)
R = O["Rook"]; R.location = (0.6, 0, 0.62); R.rotation_euler = (0, 0, math.radians(58))
HP = empty("R_HeadPivot", (0, -0.02, 0.98), R)
for n in ("R_Head", "R_Beak", "R_EyeL", "R_PupL", "R_EyeR", "R_Ring", "R_Hat", "R_Band", "R_Brim", "R_Badge"):
    o = O[n]; o.parent = HP; o.location = o.location - Vector((0, -0.02, 0.98))
# key spin (the wind-up key always turns)
for n in ("R_KeyLoop-1", "R_KeyLoop1"):
    o = O[n]; key(o, "rotation_euler", 1, 0.0, 0); key(o, "rotation_euler", END, math.radians(-360 * 40), 0); lin(o)

# ---------------- world: red-rock canyon (walls |y| >= 16, rim z 12), a side canyon at the fork, a stone arch, desert station ----------------
rr = random.Random(41)
sand = newM("S_Sand", (0.20, 0.12, 0.08), rough=0.95); O["Ground"].data.materials.clear(); O["Ground"].data.materials.append(sand)
rock = newM("S_Rock", (0.52, 0.24, 0.14), rough=0.95); rock2 = newM("S_Rock2", (0.40, 0.18, 0.11), rough=0.95)
RIM = 12.0; W0 = 16.0; FORK = (318, 348); MOUTH = 470
def wall(x0, x1, sd, depth=26):
    x = x0
    while x < x1:
        w = rr.uniform(7, 11); w = min(w, x1 - x + 0.5); inset = rr.uniform(0, 1.6); h = RIM + 0.5 + rr.uniform(-0.3, 0.3)
        yc = sd * (W0 + inset + depth / 2)
        mk("S_Wall", box(), rock if rr.random() < 0.6 else rock2, (x + w / 2, yc, h / 2 - 0.5), (0, 0, rr.uniform(-0.03, 0.03)), scl=(w + 0.6, depth, h))
        if rr.random() < 0.7:   # ledges / boulders give the faces some shape
            b = rr.uniform(1.2, 3.0); mk("S_Ledge", box(), rock2, (x + w / 2 + rr.uniform(-2, 2), sd * (W0 + inset - b / 3), rr.uniform(0.5, RIM - 2)), (rr.uniform(-.3, .3), rr.uniform(-.3, .3), rr.uniform(-.5, .5)), scl=(b * 1.6, b, b * 0.7))
        x += w
wall(-70, MOUTH, -1)
wall(-70, FORK[0], 1); wall(FORK[1], MOUTH, 1)
# side canyon (goes off to +y at the fork, 60 deg): two rows of wall blocks
ang = math.radians(62); dx, dy = math.cos(ang), math.sin(ang)
for x0, sd in ((FORK[0], -1), (FORK[1], 1)):
    for k in range(14):
        s = 6 + k * 9.0; cx = x0 + dx * s + sd * 6 * dy * 0; cy = W0 + dy * s
        mk("S_SideWall", box(), rock if k % 2 else rock2, (cx + sd * 9 * dy, cy - sd * 9 * dx, RIM / 2 - 0.25), (0, 0, ang), scl=(9.6, 18, RIM + 0.5))
# big rim boulders far up (skyline shapes)
for i in range(40):
    x = rr.uniform(-60, MOUTH); sd = 1 if rr.random() < 0.5 else -1
    if sd > 0 and FORK[0] - 10 < x < FORK[1] + 40: continue
    b = rr.uniform(2, 6); mk("S_RimRock", box(), rock2, (x, sd * rr.uniform(W0 + 8, W0 + 30), RIM + b * 0.3), (0, 0, rr.uniform(0, 3)), scl=(b * 1.5, b, b))
# the stone arch across the canyon (the train hides under it, 57-74 s)
ARCHX = 400
mk("S_Arch", box(), rock, (ARCHX, 0, RIM - 1.4), scl=(7, 2 * W0 + 4, 3.2))
for sd in (-1, 1): mk("S_ArchFoot", cyl(3.5, 5.5, RIM - 2, 8), rock2, (ARCHX, sd * (W0 - 1.5), (RIM - 2) / 2 - 0.5))
# track lamps in the canyon (they die at 14.4 s)
tie = newM("S_Tie", (0.05, 0.035, 0.03), rough=1)
for i in range(330): mk("S_Tie", box(), tie, (-60 + i * 2.0, 0, 0.01), scl=(0.25, 1.4, 0.06))
postM = newM("S_Post", (0.02, 0.02, 0.025), rough=0.5)
LAMPS = []
for i in range(6):
    x = 80 + i * 14; mk("S_Post", cyl(0.06, 0.08, 3.0, 8), postM, (x, -3.0, 1.5))
    hm = newM(f"L_Track{i}", (1, 0.62, 0.25), emit=12); mk(f"L_Track{i}", sph(0.22, 10, 6), hm, (x, -3.0, 3.1)); LAMPS.append(hm)
# desert beyond the mouth: far mesas + the station and its town
mesa = newM("S_Mesa", (0.10, 0.05, 0.04), rough=1)
for i in range(22):
    x = rr.uniform(480, 900); y = rr.uniform(60, 200) * (1 if rr.random() < 0.8 else -1); h = rr.uniform(10, 30); w = rr.uniform(15, 40)
    mk("S_Mesa", box(), mesa, (x, y, h / 2 - 0.5), scl=(w, w * 0.6, h))
winM = newM("S_Win", (1, 0.62, 0.25), emit=5); houseM = newM("S_House", (0.09, 0.05, 0.04), rough=1); roofM = newM("S_Roof", (0.22, 0.10, 0.07), rough=1)
for i in range(22):
    x = rr.uniform(500, 640); y = rr.uniform(10, 45) * (1 if rr.random() < 0.7 else -1); w = rr.uniform(3, 6); h = rr.uniform(2.5, 5)
    mk("S_House", box(), houseM, (x, y, h / 2 - 0.5), scl=(w, w, h))
    mk("S_Roof", box(), roofM, (x, y, h - 0.4), scl=(w + 0.4, w + 0.4, 0.3))
    for k in range(2): mk("S_Win", box(), winM, (x + rr.uniform(-w / 3, w / 3), y - w / 2 - 0.02 if y > 0 else y + w / 2 + 0.02, rr.uniform(0.8, h - 1.2)), scl=(0.5, 0.05, 0.6))
mk("S_Platform", box(), newM("S_Plat", (0.1, 0.09, 0.1), rough=1), (540, 2.4, 0.0), scl=(40, 2.2, 0.6))
for i in range(5):
    x = 524 + i * 8.0; mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, 3.2, 1.7))
    mk("L_StHead", sph(0.2, 12, 8), newM("L_StHeadM", (1, 0.62, 0.25), emit=8), (x, 3.2, 3.45))
    light(f"L_St{i}", "POINT", 80, (1, 0.6, 0.3), (x, 3.2, 3.2))
moonM = newM("S_Moon", (0.9, 0.88, 0.8), emit=3)
mk("S_Moon", cyl(9, 9, 0.2, 48), moonM, (420, 260, 95), (math.pi / 2, 0, 0))
w = sc.world; w.node_tree.nodes["Background"].inputs[0].default_value = (0.014, 0.016, 0.045, 1)
O["MoonKey"].data.energy = 1.6
# steam puffs for the long whistle (44.5-48 s)
stk = O["Stack"].location.copy()
puffM = newM("T_PuffM", (0.75, 0.75, 0.8), emit=0.6, rough=1)
PUFF = [mk(f"T_Puff{i}", sph(0.35, 12, 8), puffM, (stk.x - i * 0.35, 0, stk.z + 0.5 + i * 0.4), scl=(0.01, 0.01, 0.01), parent=T, smooth=True) for i in range(4)]
# where the echo seems to come from
ECHO_A = empty("V_EchoA", (FORK[0] + 70, 150, 6)); ECHO_B = empty("V_EchoB", (150, 120, 6))

# ---------------- the Hush ----------------
H = O["Hush"]; H.scale = (2.4, 2.4, 2.4)
mask_spot = light("T_MaskLight", "SPOT", 9000, (0.7, 0.85, 1.0), (0, 0, 0)); mask_spot.data.spot_size = math.radians(18)
c = mask_spot.constraints.new("TRACK_TO"); c.target = O["H_Mask"]; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
mask_spot.parent = H; mask_spot.location = (2.0, -14, 4.0)

# ---------------- animation ----------------
TRAIN = ((0, 0), (24, 170), (44, 300), (52, 360), (54, 380), (57.5, 398), (74.5, 398), (78, 414), (100, 560))
for t, x in TRAIN: key(T, "location", F(t), x, 0)
for i, hm in enumerate(LAMPS):   # track lamps die one by one
    td = 14.4 + i * 0.3; s = hm.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for t, e in ((td - 0.01, 12), (td + 0.2, 0)): s.default_value = e; s.keyframe_insert("default_value", frame=F(t))
# the Hush: under the rim (0-25), rises on the +y rim behind (25-30), chases along the rim (30-44), turns to the echo
# and climbs down into the side canyon (46-56), comes around and stands on the rim above the arch (60-72),
# the old echo returns: it walks away after it (73-100)
FX0 = FORK[0]
for t, loc, s in ((0, (110, 26, -80), 2.4), (25, (118, 26, -80), 2.4), (30, (150, 24, RIM), 2.4), (37, (232, 22, RIM), 2.4),
                  (44, (290, 21, RIM), 2.4), (46.5, (306, 22, RIM), 2.4), (50, (346, 40, 2.0), 2.4), (56, (370, 86, 0), 2.4),
                  (58, (370, 110, -60), 2.4), (59.5, (412, 60, -60), 2.4), (61, (412, 36, RIM), 2.4), (64, (402, 19, RIM), 2.4),
                  (72.5, (402, 19, RIM), 2.4), (80, (386, 28, RIM), 2.4), (90, (364, 32, RIM), 2.4), (100, (352, 34, RIM), 2.4)):
    key(H, "location", F(t), Vector(loc)); key(H, "scale", F(t), Vector((s, s, s)))
dt = H.constraints.new("LOCKED_TRACK"); dt.target = T; dt.track_axis = "TRACK_NEGATIVE_Y"; dt.lock_axis = "LOCK_Z"
da = H.constraints.new("LOCKED_TRACK"); da.target = ECHO_A; da.track_axis = "TRACK_NEGATIVE_Y"; da.lock_axis = "LOCK_Z"
db = H.constraints.new("LOCKED_TRACK"); db.target = ECHO_B; db.track_axis = "TRACK_NEGATIVE_Y"; db.lock_axis = "LOCK_Z"
for t, a, b, cc in ((0, 1, 0, 0), (45.5, 1, 0, 0), (47, 0, 1, 0), (58, 0, 1, 0), (59, 1, 0, 0), (71.5, 1, 0, 0), (73, 0, 0, 1), (100, 0, 0, 1)):
    for con, v in ((dt, a), (da, b), (db, cc)): con.influence = v; con.keyframe_insert("influence", frame=F(t))
gm = M("H_Green").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 0), (27, 0), (28.5, 60), (100, 60)): gm.default_value = e; gm.keyframe_insert("default_value", frame=F(t))
# steam puffs for the whistle
for i, pf in enumerate(PUFF):
    t0 = 44.6 + i * 0.25
    for t, s in ((t0, 0.01), (t0 + 0.6, 1.0 + i * 0.4), (48.0 + i * 0.2, 1.6 + i * 0.5), (48.6 + i * 0.2, 0.01)): key(pf, "scale", F(t), Vector((s, s, s)))
    for t, z in ((t0, stk.z + 0.5), (48.6 + i * 0.2, stk.z + 1.5 + i * 0.8)): key(pf, "location", F(t), z, 2)
# Rook: signal eye bright when brave, dim while hiding under the arch (57.5-74.5); head turns; wings
se = M("H_Signal").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 40), (27, 40), (28, 80), (57, 80), (58.5, 3), (74.5, 3), (75.5, 60), (100, 50)): se.default_value = e; se.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 4), (57, 6), (58.5, 0.3), (74.5, 0.3), (75.5, 4)): SIGL.data.energy = e; SIGL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 900), (57.5, 900), (58, 0), (74.8, 0), (75, 900)): HL.data.energy = e; HL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 45), (57.5, 45), (58.5, 10), (74.5, 10), (75.5, 45)): O["Fill"].data.energy = e; O["Fill"].data.keyframe_insert("energy", frame=F(t))
wi = M("H_Window").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 4), (57.5, 4), (58, 0.0), (74.8, 0.0), (75, 4)): wi.default_value = e; wi.keyframe_insert("default_value", frame=F(t))
for t, rz in ((0, 0), (14, 0), (15, math.radians(-110)), (19, math.radians(-110)), (20, 0), (26, 0), (27, math.radians(160)), (31, math.radians(160)), (32, 0),
              (51, 0), (52, math.radians(-110)), (55, math.radians(-110)), (56, 0),
              (62, 0), (63, math.radians(-110)), (73.5, math.radians(-110)), (74.5, 0), (86, 0), (87, math.radians(150)), (90, math.radians(150)), (91, 0), (100, 0)):
    key(HP, "rotation_euler", F(t), rz, 2)
for t, rz in ((0, math.radians(58)), (30, math.radians(58)), (31, math.radians(10)), (44, math.radians(10)), (45, math.radians(58)), (100, math.radians(58))):
    key(R, "rotation_euler", F(t), rz, 2)
for sd in (-1, 1):
    wg = O[f"R_Wing{sd}"]
    for t, a in ((0, 0), (1.0, 0), (1.3, 1.2), (1.6, 0.3), (1.9, 1.2), (2.3, 0), (32, 0), (32.3, 1.4), (34, 1.4), (34.4, 0),
                 (44.3, 0), (44.6, 1.6), (48, 1.6), (48.4, 0), (52, 0), (52.3, 1.0), (53.5, 1.0), (53.8, 0),
                 (58, 0), (58.4, -0.6), (74, -0.6), (74.4, 0), (75, 0), (75.3, 1.4), (77, 1.4), (77.4, 0)):
        key(wg, "rotation_euler", F(t), math.radians(sd * 12) + sd * a * 0.6, 1)
for f in range(1, END, 12):
    if F(57.5) <= f <= F(74.5): continue   # stands still while hiding
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
cam("Cam_01", 0, (3.0, -11, 2.6), (1.0, 0, 1.6), 26, T)             # wide side: canyon run
cam("Cam_02", 8, (2.2, -3.0, 1.7), (0.6, 0, 1.35), 30, T)          # Rook close (track lamps die)
cam("Cam_03", 27.5, (6.0, -7.0, 1.4), "H_Mask", 20, T)             # look up: the Hush rises on the rim
cam("Cam_04", 33, (22, -12, 2.5), (-16, 16, 12), 18, T)            # chase: train + the Hush on the rim behind
cam("Cam_05", 39.5, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)        # Rook: "let's give it a song"
cam("Cam_06", 44, (288, -14, 3.0), (322, 24, 15), 18)               # the fork: the whistle, the Hush turns
cam("Cam_07", 49, (378, 104, 3.0), "H_Mask", 24)                    # it climbs down into the side canyon
cam("Cam_08", 55.5, (382, -12, 2.2), (399, 0, 5), 22)              # brakes under the stone arch
cam("Cam_09", 61, (390, -10, 1.4), "H_Mask", 18)                   # from below: it stands on the rim above
cam("Cam_10", 65.5, (9, -5, 1.4), (0.5, 0, 1.3), 28, T)            # dark, still
cam("Cam_11", 70, (432, -13, 4), (402, 18, 22), 20)                # the old echo: it turns away
cam("Cam_12", 74.5, (8, -9, 3), (0, 0, 1.4), 26, T)                # quiet wheels, then full steam
cam("Cam_13", 84, (300, 45, 16), "H_Mask", 26)                   # it walks away along the rim
cam("Cam_14", 90.5, (30, -30, 10), (0, 0, 2), 24, T)               # final wide: desert station lights
sc.camera = O["Cam_01"]
sc.render.resolution_x = 1280; sc.render.resolution_y = 720; sc.render.resolution_percentage = 100
sc.eevee.taa_render_samples = 24
try: sc.eevee.use_raytracing = False
except Exception: pass
sc.render.use_compositing = False; sc.render.use_sequencer = False
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "hush_film03.blend"))
print("film03 built", len(sc.collection.all_objects), "objects; markers", len(sc.timeline_markers))
