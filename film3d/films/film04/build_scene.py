# GLOAMRUN 3D Film 5 "The Sleeping Yard" — run INSIDE Blender (hush_lookdev.blend open, scene HUSH).
# Builds the set + animation + cameras on top of the approved 3D Rook / the Hush / train, then saves
# C:\Users\81803\TremenFilm\hush\film04\hush_film04.blend.  24 fps, 2400 frames (100 s).
# Story: harbor run along the sea -> the lighthouse goes dark, the track lamps die -> the Hush rises out of the sea
# -> chase on the beach, it is too close -> Rook runs into the old train yard, turns off every light and stops among
# the rows of sleeping trains ("now we are one of them") -> the Hush searches the yard and stands right over them
# -> surprise: Old Nine, a dead engine two tracks over, hisses and its old lamp flickers on; the Hush turns to it
# -> quiet wheels, the train slips out; the Hush eats Old Nine's light -> full steam to the harbor town lights.
import bpy, bmesh, math, random, os
from mathutils import Vector
OUT = r"C:\Users\81803\TremenFilm\hush\film04"; os.makedirs(OUT, exist_ok=True)
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

# ---------------- world: sea coast (sea y < -12), cliffs (+y), lighthouse, the old train yard, harbor town ----------------
rr = random.Random(57)
sand = newM("S_Sand", (0.16, 0.13, 0.10), rough=0.95); O["Ground"].data.materials.clear(); O["Ground"].data.materials.append(sand)
rock = newM("S_Rock", (0.20, 0.19, 0.21), rough=0.95); rock2 = newM("S_Rock2", (0.14, 0.13, 0.15), rough=0.95)
seaM = newM("S_SeaM", (0.012, 0.03, 0.06), rough=0.12)
mk("S_Sea", box(), seaM, (400, -312, -0.42), scl=(1400, 600, 0.05))
YS, YE = 300, 440                       # the old yard
ROWS = (-10.4, -7.8, -5.2, -2.6, 2.6, 5.2, 7.8, 10.4)
# cliffs on the land side of the coast
x = -70
while x < 290:
    w = rr.uniform(8, 14); h = rr.uniform(6, 15); y = rr.uniform(18, 26)
    mk("S_Cliff", box(), rock if rr.random() < 0.5 else rock2, (x + w / 2, y + 10, h / 2 - 0.5), (0, 0, rr.uniform(-0.1, 0.1)), scl=(w + 1, 20, h))
    x += w
for i in range(30):   # rocks on the beach and in the shallow water
    b = rr.uniform(0.6, 2.2); mk("S_Stone", box(), rock2, (rr.uniform(-40, 300), rr.uniform(-30, -6), b * 0.2 - 0.3), (rr.uniform(-.4, .4), rr.uniform(-.4, .4), rr.uniform(0, 3)), scl=(b * 1.5, b, b * 0.7))
# lighthouse on a rock out at sea (goes dark at 9.3 s)
mk("S_LhRock", box(), rock2, (250, -125, 1.0), (0, 0, 0.4), scl=(14, 10, 3.5))
mk("S_LhTower", cyl(2.2, 1.4, 16, 16), newM("S_LhWhite", (0.55, 0.53, 0.5), rough=0.8), (250, -125, 10))
mk("S_LhTop", cyl(1.9, 1.9, 0.5, 16), newM("S_LhIron", (0.05, 0.05, 0.06), rough=0.5), (250, -125, 18.2))
LHM = newM("L_LhLamp", (1, 0.85, 0.55), emit=40); mk("L_LhLamp", sph(1.3, 14, 8), LHM, (250, -125, 19.6))
mk("S_LhCap", cyl(1.9, 0.2, 1.6, 16), newM("S_LhRed", (0.25, 0.04, 0.03), rough=0.6), (250, -125, 21.2))
# track lamps on the land side (they die at 14.8 s)
tie = newM("S_Tie", (0.05, 0.04, 0.035), rough=1)
for i in range(330): mk("S_Tie", box(), tie, (-60 + i * 2.0, 0, 0.01), scl=(0.25, 1.4, 0.06))
postM = newM("S_Post", (0.02, 0.02, 0.025), rough=0.5)
LAMPS = []
for i in range(6):
    x = 112 + i * 12; mk("S_Post", cyl(0.06, 0.08, 3.0, 8), postM, (x, 3.0, 1.5))
    hm = newM(f"L_Track{i}", (1, 0.62, 0.25), emit=12); mk(f"L_Track{i}", sph(0.22, 10, 6), hm, (x, 3.0, 3.1)); LAMPS.append(hm)
# the yard: rows of sleeping trains (old box cars, flat cars and dead engines), rails, a water tower, a big shed
rustM = newM("S_Rust", (0.16, 0.07, 0.05), rough=0.9); rust2 = newM("S_Rust2", (0.08, 0.09, 0.10), rough=0.8)
railM = newM("S_YRail", (0.18, 0.18, 0.2), rough=0.4, metal=0.8)
for ry in ROWS:
    for sd in (-0.42, 0.42): mk("S_YRail", box(), railM, ((YS + YE) / 2, ry + sd, 0.03), scl=(YE - YS, 0.08, 0.06))
    for k in range(int((YE - YS) / 2.2)):
        if rr.random() < 0.6: mk("S_YTie", box(), tie, (YS + k * 2.2, ry, 0.01), scl=(0.25, 1.4, 0.06))
    x = YS + rr.uniform(4, 14)
    while x < YE - 4:
        if ry == -10.4 and 330 < x < 348: x = 348; continue      # room for Old Nine
        L = 2.2
        if rr.random() < 0.82:
            mk("S_OldCar", box(), rustM if rr.random() < 0.6 else rust2, (x, ry, 0.62), scl=(L, 0.95, 1.05))
            mk("S_OldRoof", box(), rust2, (x, ry, 1.18), scl=(L + 0.1, 1.05, 0.08))
            for wx in (-0.7, 0.7):
                for wy in (-0.45, 0.45): mk("S_OldWheel", cyl(0.2, 0.2, 0.08, 10), M("H_Iron"), (x + wx, ry + wy, 0.15), (math.pi / 2, 0, 0))
        x += L + rr.uniform(0.3, 0.6)
        if rr.random() < 0.12: x += rr.uniform(2, 6)
# dead engines in the rows (copies of our engine, rusted, no light)
def engine_copy(tag, x0, y0, lampM=None):
    parts = []
    for n in ("Cab", "Boiler", "Stack", "CabWin") + tuple(o.name for o in sc.collection.all_objects if o.name.startswith("Wheel")):
        if n not in O: continue
        src = O[n]; c = src.copy(); c.data = src.data.copy(); c.name = f"S_{tag}_{n}"; sc.collection.objects.link(c)
        c.parent = None; c.animation_data_clear(); c.location = (x0 + src.location.x, y0 + src.location.y, src.location.z)
        for s in c.material_slots: s.link = "OBJECT"; s.material = rust2 if n == "CabWin" else (rustM if n != "Stack" else rust2)
        parts.append(c)
    if lampM:
        lp = O["Lamp"]; mk(f"L_{tag}Lamp", sph(0.11, 12, 8), lampM, (x0 + lp.location.x, y0, lp.location.z))
    mk(f"S_{tag}_Car", box(), rust2, (x0 + 0.6, y0, 0.38), scl=(2.2, 1.0, 0.5))
    return parts
engine_copy("Dead1", 392, 5.2); engine_copy("Dead2", 410, -2.6); engine_copy("Dead3", 318, 7.8)
NINEX, NINEY = 336, -10.4
NINEM = newM("L_NineLampM", (1, 0.7, 0.35), emit=0.0)
engine_copy("Nine", NINEX, NINEY, NINEM)
NINEL = light("L_NineGlow", "POINT", 0.0, (1, 0.7, 0.35), (NINEX + 5.4, NINEY, 0.9))
V_NINE = empty("V_Nine", (NINEX + 4, NINEY, 1.0))
puffM = newM("T_PuffM", (0.75, 0.75, 0.8), emit=0.6, rough=1)
NPUFF = [mk(f"S_NinePuff{i}", sph(0.35, 12, 8), puffM, (NINEX + 4.6 - i * 0.3, NINEY, 2.0 + i * 0.35), scl=(0.01, 0.01, 0.01), smooth=True) for i in range(4)]
mk("S_WTank", cyl(2.0, 2.0, 3.2, 16), rust2, (326, 15, 7.0)); mk("S_WTankTop", cyl(2.2, 0.3, 1.2, 16), rustM, (326, 15, 9.2))
for dx in (-1.3, 1.3):
    for dy in (-1.3, 1.3): mk("S_WLeg", box(), postM, (326 + dx, 15 + dy, 2.7), scl=(0.2, 0.2, 5.6))
mk("S_Shed", box(), rust2, (400, 24, 4.0), scl=(34, 14, 9)); mk("S_ShedRoof", box(), rustM, (400, 24, 8.8), scl=(35, 15, 0.6))
for i in range(6): mk("S_ShedDoor", box(), newM("S_Dark", (0.01, 0.01, 0.012), rough=1), (386 + i * 5.6, 16.95, 2.0), scl=(3.6, 0.1, 4.0))
for i in range(5): mk("S_Pole", cyl(0.1, 0.14, 12, 8), postM, (YS + 15 + i * 26, -13.5, 5.5))
# harbor town beyond the yard, boats on the water, the station
winM = newM("S_Win", (1, 0.62, 0.25), emit=5); houseM = newM("S_House", (0.07, 0.065, 0.07), rough=1); roofM = newM("S_Roof", (0.16, 0.07, 0.05), rough=1)
for i in range(26):
    x = rr.uniform(480, 640); y = rr.uniform(8, 45); w = rr.uniform(3, 6); h = rr.uniform(2.5, 6)
    mk("S_House", box(), houseM, (x, y, h / 2 - 0.5), scl=(w, w, h))
    mk("S_Roof", box(), roofM, (x, y, h - 0.4), scl=(w + 0.4, w + 0.4, 0.3))
    for k in range(2): mk("S_Win", box(), winM, (x + rr.uniform(-w / 3, w / 3), y - w / 2 - 0.02, rr.uniform(0.8, h - 1.2)), scl=(0.5, 0.05, 0.6))
boatM = newM("S_Boat", (0.09, 0.06, 0.05), rough=1)
for i in range(9):
    x = rr.uniform(490, 640); y = rr.uniform(-22, -55)
    mk("S_Boat", box(), boatM, (x, y, -0.1), (0, 0, rr.uniform(-0.3, 0.3)), scl=(5, 1.8, 0.9)); mk("S_Mast", cyl(0.06, 0.06, 6, 6), postM, (x, y, 3))
    mk("S_BoatWin", box(), winM, (x + 1.2, y + 0.92, 0.4), scl=(0.6, 0.05, 0.3))
mk("S_Pier", box(), newM("S_Plank", (0.08, 0.06, 0.05), rough=1), (560, -18, -0.15), scl=(80, 8, 0.4))
mk("S_Platform", box(), newM("S_Plat", (0.1, 0.09, 0.1), rough=1), (540, 2.4, 0.0), scl=(40, 2.2, 0.6))
for i in range(5):
    x = 524 + i * 8.0; mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, 3.2, 1.7))
    mk("L_StHead", sph(0.2, 12, 8), newM("L_StHeadM", (1, 0.62, 0.25), emit=8), (x, 3.2, 3.45))
    light(f"L_St{i}", "POINT", 80, (1, 0.6, 0.3), (x, 3.2, 3.2))
moonM = newM("S_Moon", (0.9, 0.88, 0.8), emit=3)
mk("S_Moon", cyl(9, 9, 0.2, 48), moonM, (330, -330, 70), (math.pi / 2, 0, 0))
w = sc.world; w.node_tree.nodes["Background"].inputs[0].default_value = (0.014, 0.018, 0.045, 1)
O["MoonKey"].data.energy = 1.8
V_LOOK = empty("V_Look", (300, 0, 2))

# ---------------- the Hush ----------------
H = O["Hush"]; H.scale = (2.4, 2.4, 2.4)
mask_spot = light("T_MaskLight", "SPOT", 9000, (0.7, 0.85, 1.0), (0, 0, 0)); mask_spot.data.spot_size = math.radians(18)
c = mask_spot.constraints.new("TRACK_TO"); c.target = O["H_Mask"]; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
mask_spot.parent = H; mask_spot.location = (2.0, -14, 4.0)

# ---------------- animation ----------------
TRAIN = ((0, 0), (26, 180), (40, 306), (44, 336), (47.5, 354), (50, 360), (76.5, 360), (80, 374), (100, 560))
for t, x in TRAIN: key(T, "location", F(t), x, 0)
for i, hm in enumerate(LAMPS):   # track lamps die one by one, far to near
    td = 14.8 + (5 - i) * 0.3; s = hm.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for t, e in ((td - 0.01, 12), (td + 0.2, 0)): s.default_value = e; s.keyframe_insert("default_value", frame=F(t))
s = LHM.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 40), (9.2, 40), (9.35, 6), (9.5, 30), (9.7, 0)): s.default_value = e; s.keyframe_insert("default_value", frame=F(t))
# the Hush: under the sea (0-24), rises out of the water (25-30), walks up the beach and chases (30-44), loses the dark
# train at the yard and searches (46-58), stands right over it (61-72.5), turns to Old Nine (73-79), eats its light (85.5)
for t, loc in ((0, (150, -70, -40)), (24, (160, -60, -40)), (26, (168, -46, -14)), (29, (176, -36, -4)), (32, (202, -24, 0)),
               (40, (290, -18, 0)), (44, (318, -19, 0)), (47, (326, -21, 0)), (52, (334, -20, 0)), (57, (346, -16, 0)),
               (61, (355, -14, 0)), (72.5, (355, -14, 0)), (76, (344, -18, 0)), (79, (334, -21, 0)), (100, (333, -21, 0))):
    key(H, "location", F(t), Vector(loc)); key(H, "scale", F(t), Vector((2.4, 2.4, 2.4)))
for t, loc in ((46.5, (340, -2, 1)), (50, (318, 6, 1)), (54, (352, 8, 1)), (58, (372, -4, 1)), (61, (362, 0, 1))):
    key(V_LOOK, "location", F(t), Vector(loc))
dt = H.constraints.new("LOCKED_TRACK"); dt.target = T; dt.track_axis = "TRACK_NEGATIVE_Y"; dt.lock_axis = "LOCK_Z"
dl = H.constraints.new("LOCKED_TRACK"); dl.target = V_LOOK; dl.track_axis = "TRACK_NEGATIVE_Y"; dl.lock_axis = "LOCK_Z"
dn = H.constraints.new("LOCKED_TRACK"); dn.target = V_NINE; dn.track_axis = "TRACK_NEGATIVE_Y"; dn.lock_axis = "LOCK_Z"
for t, a, b, cc in ((0, 1, 0, 0), (46.5, 1, 0, 0), (47.5, 0, 1, 0), (60, 0, 1, 0), (61, 1, 0, 0), (72.3, 1, 0, 0), (73.5, 0, 0, 1), (100, 0, 0, 1)):
    for con, v in ((dt, a), (dl, b), (dn, cc)): con.influence = v; con.keyframe_insert("influence", frame=F(t))
gm = M("H_Green").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 0), (26, 0), (27.5, 60), (100, 60)): gm.default_value = e; gm.keyframe_insert("default_value", frame=F(t))
# Old Nine: hisses, its old lamp flickers on (72), the Hush eats the light (85.5)
ns = NINEM.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 0), (72.0, 0), (72.2, 20), (72.4, 2), (72.7, 30), (73.0, 8), (73.3, 35), (85.3, 35), (85.5, 8), (85.7, 30), (86.0, 0), (100, 0)):
    ns.default_value = e; ns.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 0), (72.0, 0), (72.2, 40), (72.4, 5), (72.7, 60), (73.0, 15), (73.3, 70), (85.3, 70), (85.5, 15), (85.7, 60), (86.0, 0), (100, 0)):
    NINEL.data.energy = e; NINEL.data.keyframe_insert("energy", frame=F(t))
for i, pf in enumerate(NPUFF):
    t0 = 71.8 + i * 0.25
    for t, s in ((t0, 0.01), (t0 + 0.5, 0.8 + i * 0.35), (75.0 + i * 0.2, 1.4 + i * 0.45), (75.6 + i * 0.2, 0.01)): key(pf, "scale", F(t), Vector((s, s, s)))
    for t, z in ((t0, 2.0 + i * 0.35), (75.6 + i * 0.2, 3.0 + i * 0.8)): key(pf, "location", F(t), z, 2)
# Rook: signal eye bright when brave, dim while hiding in the yard (46.5-78); head turns; wings
se = M("H_Signal").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 40), (26, 40), (27, 80), (46, 80), (47, 3), (78.5, 3), (79.5, 60), (100, 50)): se.default_value = e; se.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 4), (46, 6), (47, 0.3), (78.5, 0.3), (79.5, 4)): SIGL.data.energy = e; SIGL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 900), (46.3, 900), (46.6, 0), (78.8, 0), (79, 900)): HL.data.energy = e; HL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 45), (46.3, 45), (47, 12), (78.5, 12), (79.5, 45)): O["Fill"].data.energy = e; O["Fill"].data.keyframe_insert("energy", frame=F(t))
wi = M("H_Window").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 4), (46.3, 4), (46.6, 0.0), (78.8, 0.0), (79, 4)): wi.default_value = e; wi.keyframe_insert("default_value", frame=F(t))
for t, rz in ((0, 0), (9.0, 0), (9.8, math.radians(-110)), (12.5, math.radians(-110)), (13.3, 0), (14.5, 0), (15.3, math.radians(110)), (18.5, math.radians(110)), (19.3, 0),
              (26, 0), (27, math.radians(-150)), (31, math.radians(-150)), (32, 0), (36, 0), (36.6, math.radians(-150)), (38.6, math.radians(-150)), (39.2, 0),
              (55, 0), (56, math.radians(-110)), (60, math.radians(-110)), (61, math.radians(-60)), (71.5, math.radians(-60)), (72.3, math.radians(-130)), (76, math.radians(-130)), (77, 0),
              (86, 0), (87, math.radians(-150)), (90, math.radians(-150)), (91, 0), (100, 0)):
    key(HP, "rotation_euler", F(t), rz, 2)
for sd in (-1, 1):
    wg = O[f"R_Wing{sd}"]
    for t, a in ((0, 0), (1.0, 0), (1.3, 1.2), (1.6, 0.3), (1.9, 1.2), (2.3, 0), (31.4, 0), (31.7, 1.4), (33.4, 1.4), (33.8, 0),
                 (44.4, 0), (44.7, 1.0), (46.2, 1.0), (46.6, 0), (47, 0), (47.4, -0.6), (76.5, -0.6), (76.9, 0), (77.2, 0), (77.5, 0.8), (79.0, 0.8), (79.4, 0),
                 (92, 0), (92.3, 1.4), (94, 1.4), (94.4, 0)):
        key(wg, "rotation_euler", F(t), math.radians(sd * 12) + sd * a * 0.6, 1)
for f in range(1, END, 12):
    if F(47) <= f <= F(78.5): continue   # stands still while hiding
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
cam("Cam_01", 0, (3.0, -11, 2.6), (1.0, 0, 1.6), 26, T)              # wide side: the coast run
cam("Cam_02", 8, (-6, 6, 3.5), (120, -90, 8), 24, T)                 # over the train: the lighthouse goes dark
cam("Cam_03", 12.5, (2.2, -3.0, 1.7), (0.6, 0, 1.35), 30, T)         # Rook close: the track lamps die
cam("Cam_04", 25.5, (6.0, -6.0, 1.4), "H_Mask", 20, T)               # the Hush rises out of the sea
cam("Cam_05", 31, (22, -12, 2.5), (-14, -20, 10), 18, T)             # chase on the beach
cam("Cam_06", 39.5, (334, 6, 4), (305, -8, 4), 18)                    # into the old yard
cam("Cam_07", 44, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)            # Rook: lights off
cam("Cam_08", 48.5, (385, -28, 16), (352, -4, 1), 22)                # high: the dark train among the rows, the Hush comes
cam("Cam_09", 55, (372, -1.3, 1.0), "H_Mask", 16)                    # low on the track: it comes closer
cam("Cam_10", 60.5, (2.4, -3.0, 1.6), (0.6, 0, 1.35), 28, T)         # Rook in the dark
cam("Cam_11", 66, (368, 2.5, 0.8), "H_Mask", 16)                     # from below: right over them
cam("Cam_12", 71.5, (352, -3, 1.6), (338, -10.4, 1.2), 20)           # Old Nine wakes up
cam("Cam_13", 76, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)            # Rook: thank you, quiet wheels
cam("Cam_14", 80, (8, -9, 3), (0, 0, 1.4), 26, T)                    # lights on, out of the yard
cam("Cam_15", 84.5, (300, -50, 8), "H_Mask", 24)                     # the Hush eats Old Nine's light
cam("Cam_16", 90.5, (30, -30, 10), (0, 0, 2), 24, T)                 # final wide: the harbor town lights
sc.camera = O["Cam_01"]
sc.render.resolution_x = 1280; sc.render.resolution_y = 720; sc.render.resolution_percentage = 100
sc.eevee.taa_render_samples = 24
try: sc.eevee.use_raytracing = False
except Exception: pass
sc.render.use_compositing = False; sc.render.use_sequencer = False
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "hush_film04.blend"))
print("film04 built", len(sc.collection.all_objects), "objects; markers", len(sc.timeline_markers))
