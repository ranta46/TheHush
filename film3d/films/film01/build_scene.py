# GLOAMRUN 3D Film 1 "Into the Dark" — run INSIDE Blender (hush_lookdev.blend open, scene HUSH).
# Builds the set + animation + cameras on top of the approved 3D Rook / the Hush / train, then saves
# C:\Users\81803\TremenFilm\hush\film01\hush_film01.blend.  24 fps, 2400 frames (100 s).
# Story: night run -> lamps die behind -> the Hush rises and chases -> the train dives into a tunnel ->
# Rook turns off every light (even his signal eye) -> the Hush's eyes search the dark and give up -> out into a lit valley.
import bpy, bmesh, math, random, os
from mathutils import Vector
OUT = r"C:\Users\81803\TremenFilm\hush\film01"; os.makedirs(OUT, exist_ok=True)
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
# a second car behind
car2 = O["Car"].copy(); car2.data = O["Car"].data; sc.collection.objects.link(car2); car2.name = "T_Car2"; car2.parent = T; car2.location.x = -2.0
trim2 = O["CarTrim"].copy(); sc.collection.objects.link(trim2); trim2.name = "T_Trim2"; trim2.parent = T; trim2.location.x = -2.0
for x in (-2.8, -1.2):
    for y in (-0.5, 0.5): mk("T_Wheel", cyl(0.2, 0.2, 0.08, 16), M("H_Iron"), (x, y, 0.15), (math.pi / 2, 0, 0), parent=T)
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

# ---------------- world: plains, spires, lamps, tunnel, valley ----------------
rr = random.Random(9); spM = newM("S_Spire", (0.03, 0.03, 0.07), rough=1)
for i in range(70):
    x = rr.uniform(-100, 700); y = rr.uniform(45, 140) * (1 if rr.random() < 0.85 else -1); h = rr.uniform(10, 45)
    mk("S_Spire", cyl(rr.uniform(2, 6), 0.3, h, 6), spM, (x, y, h / 2 - 0.5))
tie = newM("S_Tie", (0.05, 0.035, 0.03), rough=1)
for i in range(330): mk("S_Tie", box(), tie, (-60 + i * 2.0, 0, 0.01), scl=(0.25, 1.4, 0.06))
postM = newM("S_Post", (0.02, 0.02, 0.025), rough=0.5); LAMPS = []
for i in range(19):
    x = 10 + i * 20.0
    mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, 2.2, 1.7))
    hm = newM(f"L_Head{i}", (1, 0.62, 0.25), emit=6)
    head = mk(f"L_Head{i}", sph(0.18, 12, 8), hm, (x, 2.2, 3.45))
    lo = light(f"L_Light{i}", "POINT", 60, (1, 0.6, 0.3), (x, 2.2, 3.2)); LAMPS.append((x, hm, lo))
# the tunnel through a hill (x 380..432)
rock = newM("S_Rock", (0.03, 0.028, 0.04), rough=1)
for y in (-3.2, 3.2): mk("S_TunWall", box(), rock, (406, y, 3), scl=(52, 2.2, 7))
mk("S_TunRoof", box(), rock, (406, 0, 6.6), scl=(52, 8.6, 1.4))
light("S_MouthLamp", "POINT", 150, (1, 0.6, 0.3), (378, -3.0, 5.0))
mk("S_MouthLampHead", sph(0.2, 12, 8), newM("S_MLH", (1, 0.62, 0.25), emit=8), (378, -3.0, 5.2))
mk("S_Hill", cyl(48, 8, 26, 24), rock, (406, 0, 13), scl=(0.52, 0.9, 1))
# the lit valley after the tunnel
winM = newM("S_Win", (1, 0.62, 0.25), emit=5); houseM = newM("S_House", (0.05, 0.04, 0.07), rough=1)
for i in range(26):
    x = rr.uniform(450, 640); y = rr.uniform(12, 50) * (1 if rr.random() < 0.7 else -1); w = rr.uniform(2, 5); h = rr.uniform(3, 9)
    mk("S_House", box(), houseM, (x, y, h / 2 - 0.5), scl=(w, w, h))
    for k in range(2): mk("S_Win", box(), winM, (x + rr.uniform(-w / 3, w / 3), y - w / 2 - 0.02 if y > 0 else y + w / 2 + 0.02, rr.uniform(1, h - 1.5)), scl=(0.5, 0.05, 0.7))
moonM = newM("S_Moon", (0.9, 0.88, 0.8), emit=3)
mk("S_Moon", cyl(9, 9, 0.2, 48), moonM, (380, 260, 60), (math.pi / 2, 0, 0))
w = sc.world; w.node_tree.nodes["Background"].inputs[0].default_value = (0.010, 0.012, 0.04, 1)
O["MoonKey"].data.energy = 0.35

# ---------------- the Hush ----------------
H = O["Hush"]; H.scale = (2.4, 2.4, 2.4)
mask_spot = light("T_MaskLight", "SPOT", 9000, (0.7, 0.85, 1.0), (0, 0, 0)); mask_spot.data.spot_size = math.radians(18)
c = mask_spot.constraints.new("TRACK_TO"); c.target = O["H_Mask"]; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
mask_spot.parent = H; mask_spot.location = (2.0, -14, 4.0)
# peeking eyes at the tunnel mouth (only the eyes, in the dark)
peekM = newM("Peek_Eyes", (0.4, 1, 0.7), emit=0.0)
for sd in (-1, 1): mk(f"Peek{sd}", sph(0.35, 12, 8), peekM, (379, sd * 1.1, 3.4), scl=(1.3, 0.4, 0.55))

# ---------------- animation ----------------
# train x (front of loco ~ +5)
for t, x in ((0, 0), (24, 168), (44, 375), (47.5, 395), (72, 395), (78, 420), (100, 560)):
    key(T, "location", F(t), x, 0)
# lamps behind the train die one by one (the Hush eats them) from 25 s
for i, (x, hm, lo) in enumerate(LAMPS):
    td = 25.0 + i * 0.75
    for (t, e) in ((td - 0.01, 1), (td, 1), (td + 0.25, 0)):
        hm.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 6 * e
        hm.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].keyframe_insert("default_value", frame=F(t))
        lo.data.energy = 60 * e; lo.data.keyframe_insert("energy", frame=F(t))
# the Hush: rises far behind (24-30), chases (30-44), stands over the tunnel (56-74), turns away (74-82)
for t, loc, s in ((0, (110, 46, -90), 3.6), (25, (120, 46, -90), 3.6), (30, (160, 40, -2), 3.8), (37, (225, 24, -1), 3.8),
                  (44, (335, 22, -1), 3.4), (50, (360, 16, 4), 2.6), (62, (372, 14, 6), 2.6), (74, (372, 14, 6), 2.6), (84, (330, 50, -8), 2.4), (100, (300, 90, -40), 2.2)):
    key(H, "location", F(t), Vector(loc)); key(H, "scale", F(t), Vector((s, s, s)))
for t, rz in ((0, 0), (30, math.radians(-25)), (44, math.radians(-40)), (62, math.radians(-10)), (74, math.radians(-10)), (82, math.radians(160))):
    key(H, "rotation_euler", F(t), rz, 2)
gm = M("H_Green").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 0), (27, 0), (28.5, 60), (74, 60), (80, 6), (100, 0)): gm.default_value = e; gm.keyframe_insert("default_value", frame=F(t))
pk = peekM.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 0), (51, 0), (53, 25), (60, 25), (61, 6), (63, 30), (70, 30), (72.5, 0)): pk.default_value = e; pk.keyframe_insert("default_value", frame=F(t))
for sd in (-1, 1):   # the eyes slide along the tunnel mouth, searching
    pe = O[f"Peek{sd}"]
    for t, y in ((51, -1.5), (58, 1.6), (65, -1.2), (71, 0.6)): key(pe, "location", F(t), sd * 1.1 + y, 1)
# Rook: signal eye + glow (bright when brave, OFF in the tunnel), head turns, wings
se = M("H_Signal").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 40), (27, 40), (28, 80), (52, 80), (54, 2), (75, 2), (77, 50), (100, 50)): se.default_value = e; se.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 4), (52, 6), (54, 0.2), (75, 0.2), (77, 4)): SIGL.data.energy = e; SIGL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 900), (52, 900), (53, 0), (75, 0), (76, 900)): HL.data.energy = e; HL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 45), (52, 45), (54, 6), (75, 6), (77, 45)): O["Fill"].data.energy = e; O["Fill"].data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 2.5), (52, 2.5), (53, 0.0), (75, 0.0), (76, 2.5)):
    wi = M("H_Window").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]; wi.default_value = e * 1.6; wi.keyframe_insert("default_value", frame=F(t))
# head: forward / look back at the lamps / back to front / look back at the Hush / in the tunnel looks to the mouth
for t, rz in ((0, 0), (14, 0), (15, math.radians(150)), (19, math.radians(150)), (20, 0), (26, 0), (27, math.radians(160)), (31, math.radians(160)), (32, 0),
              (52, 0), (53, math.radians(140)), (72, math.radians(140)), (73, 0), (100, 0)):
    key(HP, "rotation_euler", F(t), rz, 2)
for t, rz in ((0, math.radians(58)), (30, math.radians(58)), (31, math.radians(10)), (44, math.radians(10)), (45, math.radians(58)), (100, math.radians(58))):
    key(R, "rotation_euler", F(t), rz, 2)
for sd in (-1, 1):
    wg = O[f"R_Wing{sd}"]
    for t, a in ((0, 0), (1.0, 0), (1.3, 1.2), (1.6, 0.3), (1.9, 1.2), (2.3, 0), (32, 0), (32.3, 1.4), (34, 1.4), (34.4, 0),
                 (53, 0), (53.4, -0.6), (72, -0.6), (72.4, 0), (86, 0), (86.3, 1.3), (86.6, 0.4), (86.9, 1.3), (87.3, 0)):
        key(wg, "rotation_euler", F(t), math.radians(sd * 12) + sd * a * 0.6, 1)
# small bob of the whole Rook while running
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
cam("Cam_01", 0, (3.0, -15, 3.2), (2.0, 0, 1.2), 30, T)            # wide side: the night run
cam("Cam_02", 8, (2.2, -3.0, 1.7), (0.6, 0, 1.35), 30, T)          # Rook close
cam("Cam_03", 27.5, (7.0, -3.5, 2.0), "H_Mask", 24, T)          # look back: lamps die, the Hush rises
cam("Cam_04", 33, (6, -26, 3), "H_Mask", 20, T)              # side wide: the chase
cam("Cam_05", 40, (358, -13, 2.2), (380, 0, 2.6), 22)                  # fixed: tunnel mouth, train dives in
cam("Cam_06", 50, (2.2, -1.6, 1.7), (-6, 0, 2.2), 26, T)          # in the dark: Rook, the mouth behind him
cam("Cam_07", 62, (318, -30, 4), "H_Mask", 22)                # outside: the Hush over the tunnel
cam("Cam_08", 66, (2.2, -1.6, 1.7), (-6, 0, 2.2), 26, T)          # back in: eyes search
cam("Cam_09", 76, (318, -34, 4), "H_Mask", 22)                # outside: the Hush turns away
cam("Cam_10", 84, (8, -9, 3), (0, 0, 1.4), 26, T)                  # the valley lights, Rook
cam("Cam_11", 93, (30, -30, 10), (0, 0, 2), 24, T)                 # final wide
sc.camera = O["Cam_01"]
# render settings (GPU safe)
sc.render.resolution_x = 1280; sc.render.resolution_y = 720; sc.render.resolution_percentage = 100
sc.eevee.taa_render_samples = 24
try: sc.eevee.use_raytracing = False
except Exception: pass
sc.render.use_compositing = False; sc.render.use_sequencer = False
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "hush_film01.blend"))
print("film01 built", len(sc.collection.all_objects), "objects; markers", len(sc.timeline_markers))
