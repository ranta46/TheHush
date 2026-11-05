# GLOAMRUN 3D Film 7 "The Turntable" — run INSIDE Blender (hush_lookdev.blend open, scene HUSH).
# Builds the set + animation + cameras on top of the approved 3D Rook / the Hush / train, then saves
# C:\Users\81803\TremenFilm\hush\film06\hush_film06.blend.  24 fps, 2400 frames (100 s).
# Story: windmill hills at night -> the windmills ahead stop and go dark -> the Hush rises AHEAD, on the line
# -> "Back! Full steam back!" the train runs backwards, the Hush walks after it, too fast -> Rook backs onto the
# turntable in the old roundhouse yard and turns the whole train a quarter round to the branch line, slowly
# -> the Hush arrives, eats the yard lamps and the train's lights while the table creaks round ("Don't move")
# -> surprise: a gust starts the big old mill by the yard; its sails sweep between the Hush and the train and it
# steps back -> "Now! Full steam!" up the branch line; the Hush follows (it will come again) -> the town past the hills.
import bpy, bmesh, math, random, os
from mathutils import Vector
OUT = r"C:\Users\81803\TremenFilm\hush\film06"; os.makedirs(OUT, exist_ok=True)
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

# ---------------- world: windmill hills, the old roundhouse yard with a turntable, the town past the hills ----------------
rr = random.Random(77)
def boxes(name, mat, items):   # many boxes in ONE mesh (fewer objects): items = (loc, scl, rotz)
    bm = bmesh.new()
    for loc, scl, rz in items:
        g = bmesh.ops.create_cube(bm, size=1.0)["verts"]
        bmesh.ops.scale(bm, vec=scl, verts=g); bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=__import__("mathutils").Matrix.Rotation(rz, 3, "Z"), verts=g)
        bmesh.ops.translate(bm, vec=loc, verts=g)
    return mk(name, bm, mat)
grass = newM("S_Grass", (0.07, 0.085, 0.065), rough=0.95); GA.data.materials.clear(); GA.data.materials.append(grass)
stone = newM("S_Stone", (0.17, 0.16, 0.17), rough=0.95); stone2 = newM("S_Stone2", (0.11, 0.105, 0.115), rough=0.95)
railM = newM("S_RailM", (0.2, 0.2, 0.22), rough=0.4, metal=0.8); tie = newM("S_Tie", (0.05, 0.04, 0.035), rough=1)
ironM = newM("S_BIron", (0.06, 0.065, 0.075), rough=0.5, metal=0.6); woodM = newM("S_Wood", (0.09, 0.07, 0.05), rough=1)
CX, CY, TR = 60.0, 0.0, 3.6          # turntable centre and radius
rails, ties = [], []
for x0, x1 in ((-120, CX - TR), (CX + TR, 430)):          # main line (x)
    for ry in (-0.53, 0.53): rails.append((((x0 + x1) / 2, ry, 0.03), (x1 - x0, 0.08, 0.06), 0))
    for i in range(int((x1 - x0) / 2.0)): ties.append(((x0 + 1 + i * 2.0, 0, 0.01), (0.25, 1.4, 0.06), 0))
y0, y1 = CY + TR, 270                                       # the branch line north to the town (y)
for rx in (-0.53, 0.53): rails.append(((CX + rx, (y0 + y1) / 2, 0.03), (0.08, y1 - y0, 0.06), 0))
for i in range(int((y1 - y0) / 2.0)): ties.append(((CX, y0 + 1 + i * 2.0, 0.01), (1.4, 0.25, 0.06), 0))
STALLS = [math.radians(a) for a in (118, 133, 148, 163)]
for a in STALLS:                                            # short rails into the roundhouse stalls
    for off in (-0.53, 0.53):
        r0, r1 = TR, 17.0; mx = CX + math.cos(a) * (r0 + r1) / 2 - math.sin(a) * off; my = CY + math.sin(a) * (r0 + r1) / 2 + math.cos(a) * off
        rails.append(((mx, my, 0.03), (r1 - r0, 0.08, 0.06), a))
boxes("S_Rails", railM, rails); boxes("S_Ties", tie, ties)
# turntable: a stone pit and a turning iron deck with its own rails
mk("S_Pit", cyl(TR + 0.4, TR + 0.4, 0.06, 40), stone2, (CX, CY, 0.0))
TT = empty("S_TablePivot", (CX, CY, 0))
mk("S_Deck", box(), ironM, (0, 0, 0.0), scl=(2 * TR, 2.0, 0.08), parent=TT)
for ry in (-0.53, 0.53): mk("S_DeckRail", box(), railM, (0, ry, 0.06), scl=(2 * TR, 0.08, 0.06), parent=TT)
for sy in (-1.05, 1.05): mk("S_DeckSide", box(), ironM, (0, sy, 0.25), scl=(2 * TR, 0.1, 0.5), parent=TT)
mk("S_Cabin", box(), woodM, (TR - 0.4, -1.5, 0.7), scl=(0.7, 0.7, 1.4), parent=TT)
# the old roundhouse (stalls west-north-west of the table)
roofD = newM("S_RoofD", (0.12, 0.05, 0.04), rough=1); doorM = newM("S_Door", (0.01, 0.01, 0.012), rough=1)
RHW = newM("L_RHWin", (1, 0.62, 0.25), emit=5)
for i, a in enumerate(STALLS):
    cx, cy = CX + math.cos(a) * 16.5, CY + math.sin(a) * 16.5
    mk("S_Stall", box(), stone, (cx, cy, 2.7), (0, 0, a), (8.5, 4.4, 5.4))
    mk("S_StallRoof", box(), roofD, (cx, cy, 5.6), (0, 0, a), (9.0, 4.8, 0.4))
    dx, dy = CX + math.cos(a) * 12.2, CY + math.sin(a) * 12.2
    mk("S_StallDoor", box(), doorM, (dx, dy, 1.9), (0, 0, a), (0.1, 3.0, 3.8))
    if i % 2 == 0: mk("L_RHWin", box(), RHW, (CX + math.cos(a) * 12.25, CY + math.sin(a) * 12.25, 4.6), (0, 0, a), (0.08, 1.2, 0.5))
# yard lamps
YLAMP = []
postM = newM("S_Post", (0.02, 0.02, 0.025), rough=0.5)
for i, a in enumerate((25, 60, 205, 300, 330)):
    a = math.radians(a); x, y = CX + math.cos(a) * 7.5, CY + math.sin(a) * 7.5
    mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, y, 1.7))
    hm = newM(f"L_YardHead{i}", (1, 0.62, 0.25), emit=8); mk(f"L_YardHead{i}", sph(0.2, 12, 8), hm, (x, y, 3.45))
    YLAMP.append((hm, light(f"L_Yard{i}", "POINT", 70, (1, 0.6, 0.3), (x, y, 3.2))))
# windmills: stone towers, caps, 4 sails on a hub that turns about its own axis
millM = newM("S_MillStone", (0.15, 0.14, 0.135), rough=1); sailM = newM("S_Sail", (0.2, 0.18, 0.15), rough=1)
MILLS = []
def windmill(i, x, y, yaw, s=1.0):
    h = 10 * s
    mk("S_MillTower", cyl(2.6 * s, 1.6 * s, h, 12), millM, (x, y, h / 2))
    cap = empty(f"S_MillCap{i}", (x, y, h + 0.3 * s)); cap.rotation_euler = (0, 0, yaw)
    mk("S_MillHead", cyl(1.9 * s, 0.6 * s, 2.0 * s, 10), roofD, (0, 0, 0.6 * s), parent=cap)
    hub = empty(f"S_MillHub{i}", (2.1 * s, 0, 0.6 * s), cap)
    mk("S_MillAxle", cyl(0.25 * s, 0.25 * s, 1.0 * s, 8), ironM, (0, 0, 0), (0, math.pi / 2, 0), parent=hub)
    for k in range(4):
        arm = empty(f"S_MillArm{i}_{k}", (0, 0, 0), hub); arm.rotation_euler = (math.radians(90 * k), 0, 0)
        mk("S_SailSpar", box(), woodM, (0.1 * s, 0, 4.6 * s), scl=(0.12 * s, 0.18 * s, 9.2 * s), parent=arm)
        mk("S_SailCloth", box(), sailM, (0.12 * s, 0.75 * s, 5.4 * s), scl=(0.05 * s, 1.3 * s, 7.0 * s), parent=arm)
    lm = newM(f"L_MillWin{i}", (1, 0.62, 0.25), emit=7)
    mk(f"L_MillWin{i}", box(), lm, (x + math.cos(yaw) * 2.1 * s, y + math.sin(yaw) * 2.1 * s, h * 0.45), (0, 0, yaw), (0.1, 0.9 * s, 1.2 * s))
    MILLS.append((hub, lm)); return hub
mills_xy = [(110, 26, 1), (150, -30, -1), (185, 34, 1), (220, -24, -1), (255, 40, 1), (290, -34, -1), (325, 30, 1), (360, -28, -1), (395, 36, 1), (30, 32, 1)]
for i, (x, y, side) in enumerate(mills_xy): windmill(i, x, y, math.radians(-90 if side > 0 else 90))
# the big old mill right by the yard (its sails will sweep between the Hush and the train)
d = Vector((0.816, -0.578, 0)); BMX, BMY = CX + 15 * d.x, CY + 15 * d.y
BIG = windmill(10, BMX, BMY, math.atan2(-d.y, -d.x), 1.75)
# hills, pines
hillM = newM("S_HillM", (0.05, 0.065, 0.05), rough=1)
for i in range(8):
    hx = -40 + i * 65
    mk("S_Hill", sph(1, 20, 12), hillM, (hx, rr.uniform(85, 110), -6), scl=(rr.uniform(40, 55), 30, rr.uniform(16, 26)), smooth=True)
    mk("S_Hill", sph(1, 20, 12), hillM, (hx + 30, -rr.uniform(90, 115), -6), scl=(rr.uniform(40, 55), 30, rr.uniform(14, 22)), smooth=True)
pineM = newM("S_Pine", (0.02, 0.05, 0.035), rough=1)
for i in range(70):
    x = rr.uniform(-110, 420); y = rr.choice((rr.uniform(10, 70), rr.uniform(-70, -10)))
    if abs(x - CX) < 30 and abs(y) < 30: continue
    if abs(x - CX) < 8 and y > 0: continue
    h = rr.uniform(4, 8); mk("S_PineT", cyl(h * 0.28, 0.05, h, 8), pineM, (x, y, h / 2 + 0.4))
# the town past the hills, at the end of the branch line
winM = newM("S_Win", (1, 0.62, 0.25), emit=5); houseM = newM("S_HouseM", (0.07, 0.065, 0.07), rough=1); roofM = newM("S_Roof", (0.16, 0.07, 0.05), rough=1)
for i in range(34):
    x = rr.choice((rr.uniform(20, 54), rr.uniform(66, 100))); y = rr.uniform(150, 270); w = rr.uniform(3, 6); h = rr.uniform(2.5, 6)
    mk("S_House", box(), houseM, (x, y, h / 2 - 0.5), scl=(w, w, h)); mk("S_Roof", box(), roofM, (x, y, h - 0.4), scl=(w + 0.4, w + 0.4, 0.3))
    for k in range(2): mk("S_Win", box(), winM, (x - math.copysign(w / 2 + 0.02, x - CX), y + rr.uniform(-w / 3, w / 3), rr.uniform(0.8, h - 1.2)), scl=(0.05, 0.5, 0.6))
mk("S_Platform", box(), newM("S_Plat", (0.1, 0.09, 0.1), rough=1), (CX + 2.4, 200, 0.0), scl=(2.2, 40, 0.6))
for i in range(5):
    y = 184 + i * 8.0; mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (CX + 3.2, y, 1.7))
    mk("L_StHead", sph(0.2, 12, 8), newM("L_StHeadM", (1, 0.62, 0.25), emit=8), (CX + 3.2, y, 3.45)); light(f"L_St{i}", "POINT", 80, (1, 0.6, 0.3), (CX + 3.2, y, 3.2))
moonM = newM("S_Moon", (0.9, 0.88, 0.8), emit=3)
mk("S_Moon", cyl(9, 9, 0.2, 48), moonM, (200, 340, 80), (math.pi / 2, 0, 0))
w = sc.world; w.node_tree.nodes["Background"].inputs[0].default_value = (0.014, 0.018, 0.045, 1)
O["MoonKey"].data.energy = 1.8

# ---------------- the Hush ----------------
H = O["Hush"]; H.scale = (2.4, 2.4, 2.4)
mask_spot = light("T_MaskLight", "SPOT", 9000, (0.7, 0.85, 1.0), (0, 0, 0)); mask_spot.data.spot_size = math.radians(18)
c = mask_spot.constraints.new("TRACK_TO"); c.target = O["H_Mask"]; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
mask_spot.parent = H; mask_spot.location = (2.0, -14, 4.0)

# ---------------- animation ----------------
def smooth(a):
    return a * a * (3 - 2 * a)
OFF = 2.3                                  # train centre is 2.3 m ahead of the Train origin
for t, x in ((0, -20), (17, 128), (20.5, 140), (22, 138.5), (26, 125), (32, 101), (38, 75), (42, 60.2), (43.5, CX - OFF)):
    key(T, "location", F(t), Vector((x, 0, 0))); key(T, "rotation_euler", F(t), 0.0, 2)
# the turntable turns the train a quarter round (45-66), slowly
for f in range(F(45), F(66) + 1, 6):
    a = smooth((f - F(45)) / (F(66) - F(45))) * math.pi / 2
    key(TT, "rotation_euler", f, a, 2); key(T, "rotation_euler", f, a, 2)
    key(T, "location", f, Vector((CX - OFF * math.cos(a), CY - OFF * math.sin(a), 0)))
key(TT, "rotation_euler", F(44.9), 0.0, 2)
for t, y in ((76.8, -OFF), (80, 5), (85, 28), (90, 62), (95, 104), (100, 150)):
    key(T, "location", F(t), Vector((CX, y, 0))); key(T, "rotation_euler", F(t), math.pi / 2, 2)
# the windmills ahead stop and go dark, far ones first (8.5-12.5); the big mill too
for i, (hub, lm) in enumerate(MILLS):
    order = {9: 99, 10: 6.5}.get(i, (len(mills_xy) - 2 - i) * 0.45)     # mill 9 (behind us) keeps turning
    td = 8.5 + order if i != 9 else 999
    ph = rr.uniform(0, 6)
    if td < 100:
        key(hub, "rotation_euler", F(0), ph, 0); key(hub, "rotation_euler", F(td), ph + td * 0.9, 0); key(hub, "rotation_euler", F(td + 1.5), ph + td * 0.9 + 0.5, 0)
        s = lm.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
        for t, e in ((td - 0.01, 7), (td + 0.15, 0)): s.default_value = e; s.keyframe_insert("default_value", frame=F(t))
    else:
        key(hub, "rotation_euler", F(0), ph, 0); key(hub, "rotation_euler", END, ph + 100 * 0.9, 0); lin(hub)
# the gust: the big mill starts turning again (69-) and sweeps between the Hush and the train
bh = MILLS[10][0]; a0 = bh.rotation_euler[0]
for t, a in ((68.8, 0), (70.0, 0.4), (71.0, 1.5), (72.0, 3.2), (76.0, 11.0), (100, 58.0)): key(bh, "rotation_euler", F(t), a0 + a, 0)
# the Hush: rises AHEAD behind the hills (15-19), walks down the line at us, stands over the yard (54-71),
# steps back from the sails (71-74), then walks after the train up the branch line
for t, loc in ((0, (320, 78, -40)), (14.5, (320, 76, -40)), (16.5, (318, 64, -14)), (19, (312, 50, 0)), (23, (295, 14, 0)),
               (28, (255, -4, 0)), (34, (195, -5, 0)), (40, (140, -6, 0)), (46, (108, -10, 0)), (51, (92, -14, 0)),
               (54, (CX + 30 * d.x, CY + 30 * d.y, 0)), (71, (CX + 30 * d.x, CY + 30 * d.y, 0)), (74, (CX + 37 * d.x, CY + 37 * d.y, 0)),
               (79, (CX + 37 * d.x, CY + 37 * d.y, 0)), (83, (95, 0, 0)), (90, (76, 26, 0)), (96, (65, 58, 0)), (100, (62, 82, 0))):
    key(H, "location", F(t), Vector(loc)); key(H, "scale", F(t), Vector((2.4, 2.4, 2.4)))
dt = H.constraints.new("LOCKED_TRACK"); dt.target = T; dt.track_axis = "TRACK_NEGATIVE_Y"; dt.lock_axis = "LOCK_Z"
gm = M("H_Green").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 0), (15, 0), (16.5, 60), (100, 60)): gm.default_value = e; gm.keyframe_insert("default_value", frame=F(t))
# lights: the yard lamps die as it comes (50.5-52.5), then the train's lights (53.6-55); back on when we go (76.6)
for i, (hm, lt) in enumerate(YLAMP):
    td = 50.5 + i * 0.45; s = hm.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for t, e in ((td - 0.01, 8), (td + 0.15, 0)): s.default_value = e; s.keyframe_insert("default_value", frame=F(t))
    for t, e in ((td - 0.01, 70), (td + 0.15, 0)): lt.data.energy = e; lt.data.keyframe_insert("energy", frame=F(t))
rs = RHW.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 5), (50.3, 5), (50.6, 0)): rs.default_value = e; rs.keyframe_insert("default_value", frame=F(t))
se = M("H_Signal").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 40), (16, 40), (17, 80), (54, 80), (55.4, 3), (76.4, 3), (77.2, 60), (100, 50)): se.default_value = e; se.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 4), (54, 6), (55.4, 0.3), (76.4, 0.3), (77.2, 4)): SIGL.data.energy = e; SIGL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 900), (53.8, 900), (54.0, 200), (54.2, 700), (54.6, 0), (76.6, 0), (76.9, 900)): HL.data.energy = e; HL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 45), (54.2, 45), (55.0, 12), (76.4, 12), (77.2, 45)): O["Fill"].data.energy = e; O["Fill"].data.keyframe_insert("energy", frame=F(t))
wi = M("H_Window").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 4), (54.2, 4), (54.6, 0.0), (76.6, 0.0), (76.9, 4)): wi.default_value = e; wi.keyframe_insert("default_value", frame=F(t))
# Rook head turns (rz 30 = looks ahead/at the Hush ahead, -150 = looks back) and wings
for t, rz in ((0, 0), (8.6, 0), (9.4, 30), (12.0, 30), (12.8, 0), (16.2, 0), (17.0, 30), (20.0, 30), (20.6, -150), (25.0, -150), (25.8, 30),
              (33.5, 30), (34.3, 0), (44, 0), (44.8, -40), (49.5, -40), (50.3, 20), (66, 20), (66.8, -40), (68.6, -40), (69.4, 20),
              (75.5, 20), (76.3, 0), (84, 0), (84.8, -110), (89.5, -110), (90.3, 0), (100, 0)):
    key(HP, "rotation_euler", F(t), math.radians(rz), 2)
for sd in (-1, 1):
    wg = O[f"R_Wing{sd}"]
    for t, a in ((0, 0), (1.0, 0), (1.3, 1.2), (1.6, 0.3), (1.9, 1.2), (2.3, 0), (17.0, 0), (17.3, 1.3), (19.0, 1.3), (19.4, 0),
                 (21.0, 0), (21.3, 1.5), (23.0, 1.5), (23.4, 0), (35.0, 0), (35.3, 1.0), (37.0, 1.0), (37.4, 0),
                 (45.0, 0), (45.3, 1.2), (46.5, 1.2), (46.9, 0), (52.0, 0), (52.3, 0.8), (54.0, 0.8), (54.4, 0),
                 (56, 0), (56.4, -0.6), (69.5, -0.6), (69.9, 1.2), (72.5, 1.2), (72.9, 0), (76.2, 0), (76.5, 1.4), (78.5, 1.4), (78.9, 0),
                 (92, 0), (92.3, 1.4), (94, 1.4), (94.4, 0)):
        key(wg, "rotation_euler", F(t), math.radians(sd * 12) + sd * a * 0.6, 1)
for f in range(1, END, 12):
    if F(43.5) <= f <= F(77) or F(20.2) <= f <= F(22.2): continue   # train stopped
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
cam("Cam_01", 0, (3.0, -11, 2.6), (1.0, 0, 1.6), 26, T)              # wide side: the windmill line
cam("Cam_02", 8, (-6, -4, 3.5), (90, 18, 6), 26, T)                   # over the train: the windmills ahead stop and go dark
cam("Cam_03", 12.5, (2.6, -3.4, 1.8), (0.6, -0.4, 1.3), 28, T)       # Rook close
cam("Cam_04", 15.5, (-6, -3, 3.0), "H_Mask", 24, T)                  # the Hush rises ahead, on the line
cam("Cam_05", 20, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)            # Rook: back!
cam("Cam_06", 23.5, (-16, -14, 3.0), (10, 0, 6), 20, T)              # wide: the train runs back, the Hush follows
cam("Cam_07", 29, (-1.6, -2.6, 1.6), "H_Mask", 20, T)                # from the cab: too fast
cam("Cam_08", 34, (2.6, -3.4, 1.8), (0.6, 0, 1.35), 28, T)           # Rook: the old turntable
cam("Cam_09", 38, (36, -26, 9), (CX, 0, 2), 24)                      # wide: the yard, the train backs onto the table
cam("Cam_10", 44, (CX - 13, CY - 11, 13), (CX, CY, 0), 26)           # high: the table turns
cam("Cam_11", 49.5, (CX - 6, CY + 7, 1.4), "H_Mask", 22)             # low from the table: it arrives, the yard goes dark
cam("Cam_12", 55, (2.6, -3.0, 1.6), (0.6, 0, 1.35), 28, T)           # Rook in the dark
cam("Cam_13", 60, (CX - 8, CY + 9, 0.8), "H_Mask", 18)               # from below: it towers over us, the big mill between
cam("Cam_14", 64, (2.2, -2.6, 2.2), (0.6, 0, 1.3), 32, T)            # Rook: almost there
cam("Cam_15", 68, (36, -42, 6), (78, -12, 14), 22)                   # wide: the gust, the big mill turns
cam("Cam_16", 72, (CX - 4, CY + 5, 3), "H_Mask", 24)                 # sails sweep before its face; it steps back
cam("Cam_17", 75.5, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)          # Rook: now!
cam("Cam_18", 79, (8, -9, 3), (0, 0, 1.4), 26, T)                    # lights on, full steam
cam("Cam_19", 84.5, (-4, -3.2, 2.6), "H_Mask", 26, T)                # looking back: it follows
cam("Cam_20", 90.5, (-24, -22, 12), (40, 0, 2), 24, T)               # final wide: the town past the hills
sc.camera = O["Cam_01"]
sc.render.resolution_x = 1280; sc.render.resolution_y = 720; sc.render.resolution_percentage = 100
sc.eevee.taa_render_samples = 24
try: sc.eevee.use_raytracing = False
except Exception: pass
sc.render.use_compositing = False; sc.render.use_sequencer = False
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "hush_film06.blend"))
print("film06 built", len(sc.collection.all_objects), "objects; markers", len(sc.timeline_markers))
