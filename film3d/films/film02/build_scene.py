# GLOAMRUN 3D Film 3 "The Last Car" — run INSIDE Blender (hush_lookdev.blend open, scene HUSH).
# Builds the set + animation + cameras on top of the approved 3D Rook / the Hush / train, then saves
# C:\Users\81803\TremenFilm\hush\film02\hush_film02.blend.  24 fps, 2400 frames (100 s).
# Story: snow run -> hill lamps die -> the Hush rises from the snow and chases -> on the iron bridge Rook unhooks the
# empty last car and leaves its lantern lit -> the Hush stops to eat the light -> the train sticks in a snow drift in the
# dark, the Hush walks over the frozen river toward it -> the ice breaks, it sinks to its chest -> push through, mountain lights.
import bpy, bmesh, math, random, os
from mathutils import Vector
OUT = r"C:\Users\81803\TremenFilm\hush\film02"; os.makedirs(OUT, exist_ok=True)
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
# a second (empty) car behind, on its own rig so Rook can unhook it
TR = empty("T_Rear")
car2 = O["Car"].copy(); car2.data = O["Car"].data; sc.collection.objects.link(car2); car2.name = "T_Car2"; car2.parent = TR; car2.location.x = -2.0
trim2 = O["CarTrim"].copy(); sc.collection.objects.link(trim2); trim2.name = "T_Trim2"; trim2.parent = TR; trim2.location.x = -2.0
for x in (-2.8, -1.2):
    for y in (-0.5, 0.5): mk("T_Wheel", cyl(0.2, 0.2, 0.08, 16), M("H_Iron"), (x, y, 0.15), (math.pi / 2, 0, 0), parent=TR)
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

# ---------------- world: snowfield, pines, iron bridge over a frozen river, snow drift, mountain station ----------------
rr = random.Random(23)
snow = newM("S_Snow", (0.30, 0.33, 0.45), rough=0.9); O["Ground"].data.materials.clear(); O["Ground"].data.materials.append(snow)
spM = newM("S_Peak", (0.05, 0.05, 0.09), rough=1); capM = newM("S_PeakCap", (0.42, 0.45, 0.58), rough=1)
for i in range(46):   # far mountains with snow caps
    x = rr.uniform(-100, 700); y = rr.uniform(70, 160) * (1 if rr.random() < 0.85 else -1); h = rr.uniform(18, 50); r = rr.uniform(10, 22)
    mk("S_Peak", cyl(r, 0.5, h, 7), spM, (x, y, h / 2 - 0.5))
    mk("S_PeakCap", cyl(r * 0.28, 0.4, h * 0.28, 7), capM, (x, y, h - 0.5 - h * 0.14))
pineM = newM("S_Pine", (0.02, 0.05, 0.04), rough=1); pcap = newM("S_PineSnow", (0.40, 0.43, 0.55), rough=1)
for i in range(120):  # pines near the line (never on the river)
    x = rr.uniform(-40, 640)
    if 296 < x < 384: continue
    y = rr.uniform(8, 45) * (1 if rr.random() < 0.6 else -1); h = rr.uniform(3, 8)
    mk("S_Pine", cyl(h * 0.28, 0.05, h, 7), pineM, (x, y, h / 2 - 0.5))
    mk("S_PineSnow", cyl(h * 0.12, 0.03, h * 0.3, 7), pcap, (x, y, h * 0.8 - 0.5))
tie = newM("S_Tie", (0.05, 0.035, 0.03), rough=1)
for i in range(330): mk("S_Tie", box(), tie, (-60 + i * 2.0, 0, 0.01), scl=(0.25, 1.4, 0.06))
# far hill lamps (they die at 14.5 s: something is coming)
HILL = []
for i, (x, y, z) in enumerate(((-20, 60, 9), (10, 70, 12), (40, 64, 8), (70, 75, 13), (100, 66, 10))):
    hm = newM(f"L_Hill{i}", (1, 0.62, 0.25), emit=14); mk(f"L_Hill{i}", sph(0.6, 10, 6), hm, (x, y, z)); HILL.append(hm)
# frozen river x 300..380 (runs along y) and the iron bridge
ice = newM("S_Ice", (0.20, 0.30, 0.42), rough=0.15, emit=0.0)
mk("S_Ice", box(), ice, (340, 0, -0.47), scl=(80, 400, 0.04))
bankM = newM("S_Bank", (0.36, 0.39, 0.52), rough=1)
for x in (299, 381): mk("S_Bank", box(), bankM, (x, 0, -0.3), scl=(3, 400, 0.4))
iron = newM("S_Iron", (0.06, 0.06, 0.08), rough=0.4, metal=0.8)
for y in (-0.95, 0.95):
    mk("S_Girder", box(), iron, (340, y, 1.3), scl=(84, 0.12, 0.12))
    mk("S_Girder", box(), iron, (340, y, 0.25), scl=(84, 0.14, 0.2))
    for k in range(15):
        x = 300 + k * 5.7; mk("S_Truss", box(), iron, (x, y, 0.75), (0, math.radians(35 if k % 2 else -35), 0), scl=(0.1, 0.1, 1.5))
for x in (310, 340, 370): mk("S_Pier", box(), newM("S_Stone", (0.08, 0.08, 0.1), rough=1), (x, 0, -0.6), scl=(1.6, 2.6, 1.6))
# cracks + open water that appear when the ice breaks under the Hush (71-73 s)
water = newM("S_Water", (0.0, 0.01, 0.02), rough=0.05)
HOLE = mk("S_Hole", cyl(1, 1, 0.05, 32), water, (361, 10, -0.43), scl=(0.01, 0.01, 1))
CRACKS = []
for k in range(9):
    a = k * 0.7 + rr.uniform(-0.2, 0.2); L = rr.uniform(6, 14)
    c = mk("S_Crack", box(), water, (361 + math.cos(a) * L / 2, 10 + math.sin(a) * L / 2, -0.44), (0, 0, a), scl=(0.01, 0.18, 0.02)); CRACKS.append((c, L))
# the snow drift across the track on the far bank (x 399); the train pushes it apart at 75-78 s
DR = []
for sd in (-1, 1): DR.append(mk(f"S_Drift{sd}", sph(1, 16, 10), newM("S_DriftM", (0.42, 0.45, 0.6), rough=1), (399.5, sd * 0.9, 0.0), scl=(1.6, 1.4, 1.1), smooth=True))
# mountain station + village lights (x 470..560)
winM = newM("S_Win", (1, 0.62, 0.25), emit=5); houseM = newM("S_House", (0.05, 0.04, 0.07), rough=1); roofM = newM("S_Roof", (0.40, 0.43, 0.56), rough=1)
for i in range(24):
    x = rr.uniform(470, 620); y = rr.uniform(10, 45) * (1 if rr.random() < 0.7 else -1); w = rr.uniform(2.5, 5); h = rr.uniform(3, 7)
    mk("S_House", box(), houseM, (x, y, h / 2 - 0.5), scl=(w, w, h))
    mk("S_Roof", cyl(w * 0.75, 0.1, w * 0.7, 4), roofM, (x, y, h - 0.5 + w * 0.35), (0, 0, math.pi / 4))
    for k in range(2): mk("S_Win", box(), winM, (x + rr.uniform(-w / 3, w / 3), y - w / 2 - 0.02 if y > 0 else y + w / 2 + 0.02, rr.uniform(1, h - 1.5)), scl=(0.5, 0.05, 0.7))
mk("S_Platform", box(), newM("S_Plat", (0.1, 0.09, 0.1), rough=1), (520, 2.4, 0.0), scl=(40, 2.2, 0.6))
postM = newM("S_Post", (0.02, 0.02, 0.025), rough=0.5)
for i in range(5):
    x = 504 + i * 8.0; mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, 3.2, 1.7))
    mk("L_StHead", sph(0.2, 12, 8), newM("L_StHeadM", (1, 0.62, 0.25), emit=8), (x, 3.2, 3.45))
    light(f"L_St{i}", "POINT", 80, (1, 0.6, 0.3), (x, 3.2, 3.2))
moonM = newM("S_Moon", (0.9, 0.88, 0.8), emit=3)
mk("S_Moon", cyl(9, 9, 0.2, 48), moonM, (360, 260, 70), (math.pi / 2, 0, 0))
w = sc.world; w.node_tree.nodes["Background"].inputs[0].default_value = (0.012, 0.016, 0.05, 1)
O["MoonKey"].data.energy = 0.6

# ---------------- the rear car's lantern (left behind, lit, as a lure) ----------------
lanM = newM("L_LanternM", (1, 0.7, 0.3), emit=10)
mk("L_LanternPole", cyl(0.03, 0.03, 0.8, 8), postM, (-2.6, 0, 0.95), parent=TR)
LANH = mk("L_Lantern", sph(0.16, 12, 8), lanM, (-2.6, 0, 1.4), parent=TR)
LAN = light("L_LanternLight", "POINT", 40, (1, 0.65, 0.3), (-2.6, 0, 1.6), TR)

# ---------------- the Hush ----------------
H = O["Hush"]; H.scale = (2.4, 2.4, 2.4)
mask_spot = light("T_MaskLight", "SPOT", 9000, (0.7, 0.85, 1.0), (0, 0, 0)); mask_spot.data.spot_size = math.radians(18)
c = mask_spot.constraints.new("TRACK_TO"); c.target = O["H_Mask"]; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
mask_spot.parent = H; mask_spot.location = (2.0, -14, 4.0)

# ---------------- animation ----------------
TRAIN = ((0, 0), (24, 170), (42, 300), (45, 318), (52, 392), (74, 392), (78, 410), (100, 560))
for t, x in TRAIN: key(T, "location", F(t), x, 0)
# the rear car rides with the train, is unhooked at 45 s and rolls to a stop mid-bridge (car body at x 340)
for t, x in TRAIN[:4]: key(TR, "location", F(t), x, 0)
key(TR, "location", F(46), 324, 0); key(TR, "location", F(49.5), 342, 0); key(TR, "location", F(100), 342, 0)
# hill lamps die
for i, hm in enumerate(HILL):
    td = 14.4 + i * 0.35; s = hm.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for t, e in ((td - 0.01, 14), (td + 0.2, 0)): s.default_value = e; s.keyframe_insert("default_value", frame=F(t))
# lantern: normal, bright when left as a lure, eaten by the Hush 52.5-54
ls = lanM.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 6), (44, 6), (45.5, 18), (52.5, 18), (54, 0)): ls.default_value = e; ls.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 25), (44, 25), (45.5, 120), (52.5, 120), (54, 0)): LAN.data.energy = e; LAN.data.keyframe_insert("energy", frame=F(t))
# the Hush: under the snow (0-25), rises behind (25-30), chases (30-44), stands over the lit car (50-56),
# turns and walks over the ice toward the stuck train (58-70), the ice breaks: chest deep (71-73) and stays
for t, loc, s in ((0, (110, 46, -90), 3.6), (25, (120, 46, -90), 3.6), (30, (160, 40, -2), 3.8), (37, (235, 26, -1), 3.8),
                  (44, (300, 22, -1), 3.4), (50, (336, 12, -1), 3.0), (57, (336, 12, -1), 3.0), (70.5, (360, 10, -1), 3.0),
                  (73, (361, 10, -14), 3.0), (100, (361, 10, -13), 3.0)):
    key(H, "location", F(t), Vector(loc)); key(H, "scale", F(t), Vector((s, s, s)))
# the mask faces the train, except over the lure, where it looks down at the car (50-57)
dt = H.constraints.new("LOCKED_TRACK"); dt.target = T; dt.track_axis = "TRACK_NEGATIVE_Y"; dt.lock_axis = "LOCK_Z"
d2 = H.constraints.new("LOCKED_TRACK"); d2.target = TR; d2.track_axis = "TRACK_NEGATIVE_Y"; d2.lock_axis = "LOCK_Z"
for t, a, b in ((0, 1, 0), (48, 1, 0), (49.5, 0, 1), (56.5, 0, 1), (58, 1, 0)):
    dt.influence = a; dt.keyframe_insert("influence", frame=F(t)); d2.influence = b; d2.keyframe_insert("influence", frame=F(t))
gm = M("H_Green").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 0), (27, 0), (28.5, 60), (100, 60)): gm.default_value = e; gm.keyframe_insert("default_value", frame=F(t))
# ice break
for t, s in ((70.8, 0.01), (72.0, 5), (73.5, 8)): key(HOLE, "scale", F(t), Vector((s, s, 1)))
for c, L in CRACKS:
    for t, s in ((70.6, 0.01), (71.4, L)): key(c, "scale", F(t), s, 0)
# drift pushed apart
for sd, d in zip((-1, 1), DR):
    for t, y in ((74.5, sd * 0.9), (77.5, sd * 3.4)): key(d, "location", F(t), y, 1)
    for t, z in ((74.5, 0.0), (77.5, -0.5)): key(d, "location", F(t), z, 2)
# Rook: signal eye bright when brave, dim while hiding in the drift (59-74); head turns; wings
se = M("H_Signal").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 40), (27, 40), (28, 80), (58, 80), (59.5, 3), (74.5, 3), (75.5, 60), (100, 50)): se.default_value = e; se.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 4), (58, 6), (59.5, 0.3), (74.5, 0.3), (75.5, 4)): SIGL.data.energy = e; SIGL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 900), (58.5, 900), (59, 0), (74.8, 0), (75, 900)): HL.data.energy = e; HL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 45), (58, 45), (59.5, 10), (74.5, 10), (75.5, 45)): O["Fill"].data.energy = e; O["Fill"].data.keyframe_insert("energy", frame=F(t))
wi = M("H_Window").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 4), (58.5, 4), (59, 0.0), (74.8, 0.0), (75, 4)): wi.default_value = e; wi.keyframe_insert("default_value", frame=F(t))
for t, rz in ((0, 0), (14, 0), (15, math.radians(-110)), (19, math.radians(-110)), (20, 0), (26, 0), (27, math.radians(160)), (31, math.radians(160)), (32, 0),
              (40, 0), (41, math.radians(160)), (47, math.radians(160)), (48, 0), (60, 0), (61, math.radians(150)), (73.5, math.radians(150)), (74.5, 0),
              (86, 0), (87, math.radians(150)), (90, math.radians(150)), (91, 0), (100, 0)):
    key(HP, "rotation_euler", F(t), rz, 2)
for t, rz in ((0, math.radians(58)), (30, math.radians(58)), (31, math.radians(10)), (44, math.radians(10)), (45, math.radians(58)), (100, math.radians(58))):
    key(R, "rotation_euler", F(t), rz, 2)
for sd in (-1, 1):
    wg = O[f"R_Wing{sd}"]
    for t, a in ((0, 0), (1.0, 0), (1.3, 1.2), (1.6, 0.3), (1.9, 1.2), (2.3, 0), (32, 0), (32.3, 1.4), (34, 1.4), (34.4, 0),
                 (42, 0), (42.3, 1.5), (43.5, 1.5), (44, 0.2), (44.5, 1.5), (45.5, 0),
                 (60, 0), (60.4, -0.6), (73.5, -0.6), (73.9, 0), (75, 0), (75.3, 1.4), (77, 1.4), (77.4, 0)):
        key(wg, "rotation_euler", F(t), math.radians(sd * 12) + sd * a * 0.6, 1)
for f in range(1, END, 12):
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
cam("Cam_01", 0, (3.0, -14, 3.0), (1.0, 0, 1.2), 30, T)            # wide side: snow run, two cars
cam("Cam_02", 8, (2.2, -3.0, 1.7), (0.6, 0, 1.35), 30, T)          # Rook close (hill lamps die behind)
cam("Cam_03", 27.5, (7.0, -3.5, 2.0), "H_Mask", 24, T)             # look back: the Hush rises from the snow
cam("Cam_04", 33, (22, -30, 4), (-18, 10, 9), 20, T)               # side wide: the chase
cam("Cam_05", 39.5, (296, -24, 5), (318, 4, 3), 24)                # fixed: the iron bridge, the train runs on
cam("Cam_06", 43.5, (3.0, -3.4, 1.9), (-2.2, 0, 1.2), 26, T)       # Rook + the rear car falling away
cam("Cam_07", 48, (362, -58, 6), (338, 6, 11), 20)                    # the Hush over the lit car on the bridge
cam("Cam_08", 56.5, (9, -5, 1.4), (0.5, 0, 1.3), 28, T)            # stuck in the drift, dark
cam("Cam_09", 63, (393, -12, 2.2), "H_Mask", 22)                   # from the train: the Hush walks over the ice
cam("Cam_10", 70, (402, -30, 5), (360, 8, 6), 22)                  # wide: the ice breaks
cam("Cam_11", 74.5, (8, -9, 3), (0, 0, 1.4), 26, T)                # push through the drift
cam("Cam_12", 85, (396, -8, 3.0), "H_Mask", 24)                   # chest deep, it still watches
cam("Cam_13", 90.5, (30, -30, 10), (0, 0, 2), 24, T)               # final wide: mountain lights
sc.camera = O["Cam_01"]
sc.render.resolution_x = 1280; sc.render.resolution_y = 720; sc.render.resolution_percentage = 100
sc.eevee.taa_render_samples = 24
try: sc.eevee.use_raytracing = False
except Exception: pass
sc.render.use_compositing = False; sc.render.use_sequencer = False
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "hush_film02.blend"))
print("film02 built", len(sc.collection.all_objects), "objects; markers", len(sc.timeline_markers))
