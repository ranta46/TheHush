# GLOAMRUN 3D Film 6 "The Lift Bridge" — run INSIDE Blender (hush_lookdev.blend open, scene HUSH).
# Builds the set + animation + cameras on top of the approved 3D Rook / the Hush / train, then saves
# C:\Users\81803\TremenFilm\hush\film05\hush_film05.blend.  24 fps, 2400 frames (100 s).
# Story: river line by a lake under pine hills -> the mill on the hill goes dark -> the Hush rises behind the hills
# -> chase, too close -> Rook crosses the old lift bridge over the deep river, stops and pulls the lever: the bridge
# goes up behind them -> the Hush stops at the bank and eats the train's lights from across the water ("Don't move")
# -> surprise: the old chains slip and the bridge comes down by itself -> "Lights stay on if we move!" full steam;
# the Hush walks over the bridge after them (it will come again) -> the mill town lights.
import bpy, bmesh, math, random, os
from mathutils import Vector
OUT = r"C:\Users\81803\TremenFilm\hush\film05"; os.makedirs(OUT, exist_ok=True)
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
# ground in two parts with a deep river channel between (x 380-440); our own rails (gap at the river)
GA = O["Ground"]; GA.scale = (1080, 400, 1); GA.location = (-160, 0, -0.5)
for n in ("Rail", "Rail2"): O[n].hide_render = True; O[n].hide_viewport = True

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

# ---------------- world: lake (-y) and pine hills (+y), the mill on the hill, the deep river, the old lift bridge, mill town ----------------
rr = random.Random(66)
grass = newM("S_Grass", (0.07, 0.085, 0.07), rough=0.95); GA.data.materials.clear(); GA.data.materials.append(grass)
GB = GA.copy(); GB.data = GA.data; GB.name = "S_GroundB"; sc.collection.objects.link(GB); GB.animation_data_clear()
GB.scale = (860, 400, 1); GB.location = (870, 0, -0.5)
stone = newM("S_Stone", (0.17, 0.16, 0.17), rough=0.95); stone2 = newM("S_Stone2", (0.11, 0.105, 0.115), rough=0.95)
waterM = newM("S_Water", (0.01, 0.025, 0.05), rough=0.08)
mk("S_Lake", box(), waterM, (150, -160, 0.02), scl=(470, 290, 0.04))                  # lake beside the line (x -80..380)
mk("S_River", box(), waterM, (410, 0, -2.4), scl=(62, 700, 0.2))                     # deep river channel
for qx in (379.4, 440.6): mk("S_Quay", box(), stone, (qx, 0, -1.5), scl=(1.2, 700, 3.0))
railM = newM("S_RailM", (0.2, 0.2, 0.22), rough=0.4, metal=0.8)
tie = newM("S_Tie", (0.05, 0.04, 0.035), rough=1)
for x0, x1 in ((-80, 380), (440, 800)):
    for ry in (-0.53, 0.53): mk("S_Rail", box(), railM, ((x0 + x1) / 2, ry, 0.03), scl=(x1 - x0, 0.08, 0.06))
    for i in range(int((x1 - x0) / 2.0)): mk("S_Tie", box(), tie, (x0 + 1 + i * 2.0, 0, 0.01), scl=(0.25, 1.4, 0.06))
# the bascule (lift) bridge: two leaves, pivots at the two banks
ironM = newM("S_BIron", (0.06, 0.065, 0.075), rough=0.5, metal=0.6)
PA = empty("S_PivotA", (380, 0, 0)); PB = empty("S_PivotB", (440, 0, 0))
for P, sgn in ((PA, 1), (PB, -1)):
    mk("S_Leaf", box(), ironM, (sgn * 15, 0, -0.25), scl=(30, 4.0, 0.5), parent=P)
    for ry in (-0.53, 0.53): mk("S_LeafRail", box(), railM, (sgn * 15, ry, 0.03), scl=(30, 0.08, 0.06), parent=P)
    for i in range(15): mk("S_LeafTie", box(), tie, (sgn * (1 + i * 2.0), 0, 0.01), scl=(0.25, 1.4, 0.06), parent=P)
    for sy in (-2.0, 2.0):
        mk("S_Truss", box(), ironM, (sgn * 15, sy, 0.6), scl=(30, 0.15, 1.2), parent=P)
        for i in range(7): mk("S_TrussV", box(), ironM, (sgn * (2 + i * 4.3), sy, 0.6), (0, math.radians(35 * sgn * (1 if i % 2 else -1)), 0), scl=(0.15, 0.15, 1.6), parent=P)
TWIN = newM("L_TowerWin", (1, 0.65, 0.3), emit=6)
for bx, sgn in ((376, 1), (444, -1)):   # towers with machine houses
    for sy in (-3.6, 3.6): mk("S_Tower", box(), stone2, (bx, sy, 6.0), scl=(3.2, 2.6, 12.5))
    mk("S_House", box(), stone, (bx, 0, 11.0), scl=(3.4, 9.8, 3.0)); mk("S_HRoof", box(), newM("S_RoofD", (0.12, 0.05, 0.04), rough=1), (bx, 0, 12.7), scl=(3.8, 10.4, 0.4))
    for wy in (-2.5, 0, 2.5): mk("L_TowerWin", box(), TWIN, (bx - sgn * 1.72, wy, 11.0), scl=(0.05, 0.9, 1.0))
TWL = light("L_TowerGlow", "POINT", 120, (1, 0.65, 0.3), (444 + 3, 0, 11.0))
LEVER = empty("S_LeverPivot", (458.6, -1.15, 0.05))
mk("S_LeverBase", box(), ironM, (0, 0, 0.15), scl=(0.3, 0.3, 0.3), parent=LEVER)
mk("S_LeverArm", cyl(0.035, 0.035, 1.3, 8), M("H_Iron") if "H_Iron" in bpy.data.materials else ironM, (0, 0, 0.75), parent=LEVER)
mk("S_LeverKnob", sph(0.08, 10, 6), newM("S_Red", (0.4, 0.04, 0.03), rough=0.5), (0, 0, 1.4), parent=LEVER)
# pine hills on the land side, the mill on the hill
pineM = newM("S_Pine", (0.02, 0.05, 0.035), rough=1); trunkM = newM("S_Trunk", (0.05, 0.03, 0.02), rough=1)
for i in range(6):
    hx = -60 + i * 70; mk("S_Hill", sph(1, 20, 12), newM("S_HillM", (0.05, 0.065, 0.05), rough=1), (hx, rr.uniform(70, 95), -6), scl=(rr.uniform(40, 55), 30, rr.uniform(16, 24)), smooth=True)
for i in range(110):
    x = rr.uniform(-80, 372); y = rr.uniform(9, 60); h = rr.uniform(4, 9)
    mk("S_PineT", cyl(h * 0.28, 0.05, h, 8), pineM, (x, y, h / 2 + 0.6)); mk("S_Trunk", box(), trunkM, (x, y, 0.3), scl=(0.3, 0.3, 0.8))
for i in range(40):
    x = rr.uniform(450, 600); y = rr.uniform(10, 50); h = rr.uniform(4, 8)
    mk("S_PineT", cyl(h * 0.28, 0.05, h, 8), pineM, (x, y, h / 2 + 0.6))
MX, MY = 150, 80
mk("S_Mill", box(), stone, (MX, MY, 15.5), scl=(9, 7, 9)); mk("S_MillRoof", cyl(6.5, 0.4, 4.5, 4), newM("S_RoofD", (0.12, 0.05, 0.04), rough=1), (MX, MY, 22.2), (0, 0, math.radians(45)))
MILLW = []
for i in range(6):
    wm = newM(f"L_MillWin{i}", (1, 0.62, 0.25), emit=8); MILLW.append(wm)
    mk(f"L_MillWin{i}", box(), wm, (MX - 3 + (i % 3) * 3, MY - 3.55, 13.5 + (i // 3) * 3.5), scl=(1.0, 0.1, 1.4))
WHEEL = empty("S_MillWheel", (MX, MY - 4.4, 18))
for k in range(4): mk("S_Blade", box(), newM("S_Wood", (0.09, 0.07, 0.05), rough=1), (0, 0, 0), (0, math.radians(45 * k), 0), scl=(17, 0.15, 1.1), parent=WHEEL)
V_MILL = empty("V_Mill", (MX, MY, 16))
MILLL = light("L_MillGlow", "POINT", 300, (1, 0.62, 0.25), (MX, MY - 8, 15))
# mill town and station beyond the river
winM = newM("S_Win", (1, 0.62, 0.25), emit=5); houseM = newM("S_HouseM", (0.07, 0.065, 0.07), rough=1); roofM = newM("S_Roof", (0.16, 0.07, 0.05), rough=1)
for i in range(30):
    x = rr.uniform(640, 790); y = rr.choice((rr.uniform(8, 45), rr.uniform(-45, -8))); w = rr.uniform(3, 6); h = rr.uniform(2.5, 6)
    mk("S_House", box(), houseM, (x, y, h / 2 - 0.5), scl=(w, w, h)); mk("S_Roof", box(), roofM, (x, y, h - 0.4), scl=(w + 0.4, w + 0.4, 0.3))
    for k in range(2): mk("S_Win", box(), winM, (x + rr.uniform(-w / 3, w / 3), y - math.copysign(w / 2 + 0.02, y), rr.uniform(0.8, h - 1.2)), scl=(0.5, 0.05, 0.6))
postM = newM("S_Post", (0.02, 0.02, 0.025), rough=0.5)
mk("S_Platform", box(), newM("S_Plat", (0.1, 0.09, 0.1), rough=1), (700, 2.4, 0.0), scl=(40, 2.2, 0.6))
for i in range(5):
    x = 684 + i * 8.0; mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, 3.2, 1.7))
    mk("L_StHead", sph(0.2, 12, 8), newM("L_StHeadM", (1, 0.62, 0.25), emit=8), (x, 3.2, 3.45)); light(f"L_St{i}", "POINT", 80, (1, 0.6, 0.3), (x, 3.2, 3.2))
moonM = newM("S_Moon", (0.9, 0.88, 0.8), emit=3)
mk("S_Moon", cyl(9, 9, 0.2, 48), moonM, (300, -340, 75), (math.pi / 2, 0, 0))
w = sc.world; w.node_tree.nodes["Background"].inputs[0].default_value = (0.014, 0.018, 0.045, 1)
O["MoonKey"].data.energy = 1.8

# ---------------- the Hush ----------------
H = O["Hush"]; H.scale = (2.4, 2.4, 2.4)
mask_spot = light("T_MaskLight", "SPOT", 9000, (0.7, 0.85, 1.0), (0, 0, 0)); mask_spot.data.spot_size = math.radians(18)
c = mask_spot.constraints.new("TRACK_TO"); c.target = O["H_Mask"]; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
mask_spot.parent = H; mask_spot.location = (2.0, -14, 4.0)

# ---------------- animation ----------------
TRAIN = ((0, 0), (24, 170), (38, 300), (44, 362), (47, 400), (49.5, 452), (51, 458), (78, 458), (80, 466), (100, 700))
for t, x in TRAIN: key(T, "location", F(t), x, 0)
for i, wm in enumerate(MILLW):   # the mill windows die one by one
    td = 9.3 + i * 0.25; s = wm.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for t, e in ((td - 0.01, 8), (td + 0.15, 0)): s.default_value = e; s.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 300), (9.3, 300), (10.8, 0)): MILLL.data.energy = e; MILLL.data.keyframe_insert("energy", frame=F(t))
key(WHEEL, "rotation_euler", F(0), 0.0, 1); key(WHEEL, "rotation_euler", F(9.5), math.radians(60), 1); key(WHEEL, "rotation_euler", F(12), math.radians(64), 1)
# the Hush: rises behind the hills (14-18), chases along the line (18-47), stops at the river bank (53-81),
# walks onto the bridge when it comes down (82-92) and on after the train
for t, loc in ((0, (60, 70, -40)), (13.5, (62, 66, -40)), (16, (66, 58, -14)), (18.5, (72, 50, 0)), (24, (110, 30, 0)),
               (32, (210, 12, 0)), (38, (270, 6, 0)), (44, (325, 0, 0)), (49, (352, -2, 0)), (53, (366, -3, 0)),
               (81.5, (366, -3, 0)), (85, (392, 0, 0)), (90, (424, 0, 0)), (100, (456, 0, 0))):
    key(H, "location", F(t), Vector(loc)); key(H, "scale", F(t), Vector((2.4, 2.4, 2.4)))
dt = H.constraints.new("LOCKED_TRACK"); dt.target = T; dt.track_axis = "TRACK_NEGATIVE_Y"; dt.lock_axis = "LOCK_Z"
gm = M("H_Green").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 0), (15, 0), (16.5, 60), (100, 60)): gm.default_value = e; gm.keyframe_insert("default_value", frame=F(t))
# the bridge: up (51-55), old chains slip and it comes down (72.5-78)
for t, a in ((0, 0), (51.2, 0), (55, 72), (72.4, 72), (72.7, 61), (73.8, 58), (74.1, 46), (75.4, 43), (75.7, 28), (77.2, 20), (77.9, 0), (100, 0)):
    key(PA, "rotation_euler", F(t), math.radians(-a), 1); key(PB, "rotation_euler", F(t), math.radians(a), 1)
for t, a in ((0, 0), (50.6, 0), (51.2, math.radians(-55)), (100, math.radians(-55))): key(LEVER, "rotation_euler", F(t), a, 1)
# lights: the Hush eats the train's lights from across the water (57-59); back on when we move (79)
se = M("H_Signal").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 40), (16, 40), (17, 80), (57, 80), (58.6, 3), (78.5, 3), (79.5, 60), (100, 50)): se.default_value = e; se.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 4), (57, 6), (58.6, 0.3), (78.5, 0.3), (79.5, 4)): SIGL.data.energy = e; SIGL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 900), (57.2, 900), (57.4, 200), (57.6, 700), (58.0, 0), (78.9, 0), (79.2, 900)): HL.data.energy = e; HL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 45), (57.5, 45), (58.3, 12), (78.5, 12), (79.5, 45)): O["Fill"].data.energy = e; O["Fill"].data.keyframe_insert("energy", frame=F(t))
wi = M("H_Window").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 4), (57.6, 4), (58.0, 0.0), (78.9, 0.0), (79.2, 4)): wi.default_value = e; wi.keyframe_insert("default_value", frame=F(t))
tws = TWIN.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 6), (56.6, 6), (56.9, 0)): tws.default_value = e; tws.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 120), (56.6, 120), (56.9, 0)): TWL.data.energy = e; TWL.data.keyframe_insert("energy", frame=F(t))
# Rook head turns and wings
for t, rz in ((0, 0), (9.0, 0), (9.8, math.radians(-60)), (12.5, math.radians(-60)), (13.3, 0), (15.5, 0), (16.3, math.radians(-150)), (19.5, math.radians(-150)), (20.3, 0),
              (32, 0), (32.8, math.radians(-150)), (36, math.radians(-150)), (36.8, 0),
              (52, 0), (53, math.radians(-150)), (66, math.radians(-150)), (72.3, math.radians(-160)), (76.5, math.radians(-160)), (77.3, 0),
              (85, 0), (85.8, math.radians(-150)), (89.5, math.radians(-150)), (90.3, 0), (100, 0)):
    key(HP, "rotation_euler", F(t), rz, 2)
for sd in (-1, 1):
    wg = O[f"R_Wing{sd}"]
    for t, a in ((0, 0), (1.0, 0), (1.3, 1.2), (1.6, 0.3), (1.9, 1.2), (2.3, 0), (25.8, 0), (26.1, 1.4), (28.0, 1.4), (28.4, 0),
                 (39.2, 0), (39.5, 1.0), (41.0, 1.0), (41.4, 0), (50.0, 0), (50.4, 1.5), (51.4, 1.5), (51.8, 0),
                 (59, 0), (59.4, -0.6), (73.0, -0.6), (73.4, 1.2), (75.6, 1.2), (76.0, 0), (78.3, 0), (78.6, 1.4), (80.5, 1.4), (80.9, 0),
                 (92, 0), (92.3, 1.4), (94, 1.4), (94.4, 0)):
        key(wg, "rotation_euler", F(t), math.radians(sd * 12) + sd * a * 0.6, 1)
for f in range(1, END, 12):
    if F(51) <= f <= F(78.5): continue   # train stopped
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
cam("Cam_01", 0, (3.0, -11, 2.6), (1.0, 0, 1.6), 26, T)              # wide side: the river line by the lake
cam("Cam_02", 8, (-5, -7, 3.0), "V_Mill", 26, T)                     # over the train: the mill on the hill goes dark
cam("Cam_03", 12.5, (-2.4, -4.6, 1.9), (3.0, 0, 1.5), 22, T)         # Rook close
cam("Cam_04", 15.5, (-3.0, -5.5, 2.2), "H_Mask", 22, T)              # the Hush rises behind the hills
cam("Cam_05", 25, (22, -12, 2.5), (-20, 14, 10), 18, T)              # chase along the line
cam("Cam_06", 31, (-3.2, -2.8, 1.5), "H_Mask", 20, T)                # looking back: too close
cam("Cam_07", 38.5, (-3.0, 1.8, 2.4), (40, 0, 5), 24, T)             # ahead: the old lift bridge
cam("Cam_08", 43.5, (412, -48, 9), (410, 0, 4), 24)                  # wide: the train crosses the bridge
cam("Cam_09", 49.8, (2.6, -3.4, 1.8), (0.6, -0.6, 1.2), 28, T)       # Rook pulls the lever
cam("Cam_10", 52.5, (472, -16, 2.6), (402, 0, 10), 20)               # the bridge goes up, the Hush at the bank
cam("Cam_11", 56.5, (452, -7, 1.2), "H_Mask", 18)                    # across the water: it eats our lights
cam("Cam_12", 60.5, (2.4, -3.0, 1.6), (0.6, 0, 1.35), 28, T)         # Rook in the dark
cam("Cam_13", 66, (447, -6.5, 0.6), "H_Mask", 16)                    # from below across the water: it towers over us
cam("Cam_14", 71.5, (424, -34, 4), (410, 0, 9), 22)                  # the old chains slip: the bridge comes down
cam("Cam_15", 77.5, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)          # Rook: go!
cam("Cam_16", 81, (8, -9, 3), (0, 0, 1.4), 26, T)                    # lights on, full steam
cam("Cam_17", 85, (-4, -3.2, 2.6), "H_Mask", 26, T)                  # looking back: the Hush walks over the bridge
cam("Cam_18", 90.5, (30, -30, 10), (0, 0, 2), 24, T)                 # final wide: the mill town lights
sc.camera = O["Cam_01"]
sc.render.resolution_x = 1280; sc.render.resolution_y = 720; sc.render.resolution_percentage = 100
sc.eevee.taa_render_samples = 24
try: sc.eevee.use_raytracing = False
except Exception: pass
sc.render.use_compositing = False; sc.render.use_sequencer = False
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "hush_film05.blend"))
print("film05 built", len(sc.collection.all_objects), "objects; markers", len(sc.timeline_markers))
