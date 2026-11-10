# GLOAMRUN 3D Film 12 "Round Hill" — run INSIDE Blender (hush_lookdev.blend open, scene HUSH).
# Builds the set + animation + cameras on top of the approved 3D Rook / the Hush / train, then saves
# C:\Users\81803\TremenFilm\hush\film11\hush_film11.blend.  24 fps, 2400 frames (100 s).
# Story: the night heath -> the lamps on Round Hill die and its face rises over the hilltop -> it comes round the hill, crosses
# the line behind us and follows us onto the old ring line -> Rook's move: lights off, "Keep the hill between us": the dark
# train creeps round the ring, always on the far side of the hill from the Hush -> at the north point the old switch is stuck
# -> it comes round and stands right by the dark train ('Don't move') -> surprise: a falling star crosses the sky, it turns
# and walks off after the light -> the switch gives: lights on, full steam west to Lamp Town; it follows (it will come again).
import bpy, bmesh, math, random, os
from mathutils import Vector
OUT = r"C:\Users\81803\TremenFilm\hush\film11"; os.makedirs(OUT, exist_ok=True)
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



# ---------------- world: the heath, Round Hill and the old ring line, the junction, Lamp Town ----------------
from mathutils import Matrix
rr = random.Random(1212)
CX, CY, RR = 150.0, 0.0, 45.0                 # the ring line round Round Hill (radius 45)
HILL_R, HILL_H = 34.0, 15.0                   # Round Hill (its face looks over the top: the mask is ~21 m up)
YA, YE = -45.0, 45.0                          # the approach line (into the ring at the south point) / the exit line (out at the north point, west to Lamp Town)
S_RING0 = 210.0                               # arc length where the ring starts (approach x -60 .. 150)
S_EXIT0 = S_RING0 + RR * math.pi              # the north point (exit junction)
def pose(s):                                  # the train path: approach east -> ring counter-clockwise S -> E -> N -> west to Lamp Town
    if s <= S_RING0: return (-60.0 + s, YA, 0.0)
    if s <= S_EXIT0:
        th = -math.pi / 2 + (s - S_RING0) / RR
        return (CX + RR * math.cos(th), CY + RR * math.sin(th), th + math.pi / 2)
    return (CX - (s - S_EXIT0), YE, math.pi)
def ring(thd, r): return (CX + r * math.cos(math.radians(thd)), CY + r * math.sin(math.radians(thd)))
def flatd(x, y):                              # distance to the nearest rail line (ground is flat near the lines)
    d = abs(math.hypot(x - CX, y - CY) - RR)
    if x <= CX + 2: d = min(d, abs(y - YA) if x >= -175 else 99, abs(y - YE) if x >= -260 else 99)
    return d
def gh(x, y):
    d = math.hypot(x - CX, y - CY)
    if d < HILL_R:
        u = 1 - (d / HILL_R) ** 2; return HILL_H * u * u * (1.0 + 0.04 * math.sin(x * 0.3 + y * 0.2))
    a = min(1.0, max(0.0, (flatd(x, y) - 7) / 16))
    n = 1.1 * math.sin(x * 0.035 + y * 0.03) + 0.8 * math.sin(x * 0.08 - y * 0.05 + 1.3) + 0.5 * math.sin(y * 0.1)
    return a * (n + 0.012 * max(0, abs(y) - 90) ** 1.2) - 0.02
GA = O["Ground"]; grass = newM("S_Grass", (0.07, 0.075, 0.06), rough=0.95); GA.data.materials.clear(); GA.data.materials.append(grass)
GA.location = (0, 0, -3.0); GA.scale = (1400, 1000, 1)
heathM = newM("S_Heath", (0.075, 0.075, 0.055), rough=1); hillM2 = newM("S_HillTop", (0.08, 0.09, 0.065), rough=1)
def axis(a, b, step):
    out = []; v = a
    while v <= b: out.append(v); v += step
    return out
xs = axis(-420, -282, 6) + axis(-280, 230, 2.0) + axis(236, 520, 6)
ys = axis(-300, -122, 6) + axis(-120, 120, 2.0) + axis(126, 300, 6)
bm = bmesh.new(); vv = [[bm.verts.new((x, y, gh(x, y))) for y in ys] for x in xs]
for i in range(len(xs) - 1):
    for j in range(len(ys) - 1):
        f = bm.faces.new((vv[i][j], vv[i + 1][j], vv[i + 1][j + 1], vv[i][j + 1]))
        if math.hypot(xs[i] - CX, ys[j] - CY) < HILL_R - 2: f.material_index = 1
GO = mk("S_HeathGround", bm, heathM, smooth=True); GO.data.materials.append(hillM2)
railM = newM("S_RailM", (0.2, 0.2, 0.22), rough=0.4, metal=0.8); tie = newM("S_Tie", (0.05, 0.04, 0.035), rough=1)
postM = newM("S_Post", (0.02, 0.02, 0.025), rough=0.5); stoneM = newM("S_Stone", (0.15, 0.15, 0.14), rough=1)
def pboxes(name, mat, items, parent=None):   # boxes with yaw in ONE mesh: (loc, scl, rz)
    bm = bmesh.new()
    for loc, scl, rz in items:
        g = bmesh.ops.create_cube(bm, size=1.0)["verts"]; bmesh.ops.scale(bm, vec=scl, verts=g)
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(rz, 3, "Z"), verts=g); bmesh.ops.translate(bm, vec=loc, verts=g)
    return mk(name, bm, mat, parent=parent)
rails, ties = [], []
def seg(x, y, h, L):
    for yy in (-0.53, 0.53):
        rails.append(((x - math.sin(h) * yy, y + math.cos(h) * yy, 0.03), (L + 0.03, 0.08, 0.06), h))
    ties.append(((x, y, 0.01), (0.25, 1.4, 0.06), h))
def straight(x0, x1, y):
    for i in range(int((x1 - x0) / 2)): seg(x0 + i * 2 + 1, y, 0.0, 2.0)
straight(-175, CX, YA); straight(-260, CX, YE)
NR = 140
for i in range(NR):                            # the whole ring
    th = 2 * math.pi * (i + 0.5) / NR; L = 2 * math.pi * RR / NR
    seg(CX + RR * math.cos(th), CY + RR * math.sin(th), th + math.pi / 2, L)
pboxes("S_Rails", railM, rails); pboxes("S_Ties", tie, ties)
pboxes("S_EndStop", newM("S_Red", (0.6, 0.05, 0.03), rough=0.5), [((-258, YE, 0.45), (0.3, 1.8, 0.5), 0), ((-173, YA, 0.45), (0.3, 1.8, 0.5), 0)])
# the old switch at the north point: a lever box beside the line (Rook pulls it; it is stuck)
LEV = empty("S_LeverPivot", (CX - 1.0, YE + 1.9, 0.35))
mk("S_LeverBox", box(), newM("S_LBox", (0.12, 0.1, 0.08), rough=1), (CX - 1.0, YE + 1.9, 0.18), scl=(0.9, 0.6, 0.36))
mk("S_Lever", box(), newM("S_Red2", (0.6, 0.06, 0.03), rough=0.5), (0, 0, 0.6), scl=(0.09, 0.09, 1.2), parent=LEV)
LEV.rotation_euler = (0, math.radians(30), 0)
# Round Hill: an old stone ring on top
stones = []
for i in range(11):
    a = 2 * math.pi * i / 11 + 0.2; x, y = CX + 7 * math.cos(a), CY + 7 * math.sin(a)
    if i in (3, 8): continue
    stones.append(((x, y, gh(x, y) + 1.3), (1.0, 0.7, 3.0), a))
pboxes("S_Stones", stoneM, stones)
# lamps round the ring (the Hush eats them first: they die from the north point both ways)
RLAMP = []
for i in range(10):
    thd = 90 + 36 * i; x, y = ring(thd, RR - 4.5); z = gh(x, y)
    mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, y, z + 1.7))
    hm = newM(f"L_RHead{i}", (1, 0.62, 0.25), emit=8); mk(f"L_RHead{i}", sph(0.2, 12, 8), hm, (x, y, z + 3.45))
    td = 5.4 + min(i, 10 - i) * 0.45
    RLAMP.append((hm, light(f"L_R{i}", "POINT", 60, (1, 0.6, 0.3), (x, y, z + 3.2)), td))
# lamps along the approach line (they die as the Hush crosses the line behind us)
for i, x in enumerate((-40, -10, 20, 50, 80, 110, 135)):
    y = YA - 3.2; mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, y, 1.7))
    hm = newM(f"L_AHead{i}", (1, 0.62, 0.25), emit=8); mk(f"L_AHead{i}", sph(0.2, 12, 8), hm, (x, y, 3.45))
    td = 99.0 if x < 60 else {80: 20.6, 110: 21.6, 135: 23.2}[x]
    RLAMP.append((hm, light(f"L_A{i}", "POINT", 55, (1, 0.6, 0.3), (x, y, 3.2)), td))
# lamps along the exit line (it eats them as it follows us)
for i, x in enumerate((110, 60, 10, -40, -90, -140)):
    y = YE + 3.2; mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, y, 1.7))
    hm = newM(f"L_EHead{i}", (1, 0.62, 0.25), emit=8); mk(f"L_EHead{i}", sph(0.2, 12, 8), hm, (x, y, 3.45))
    td = {110: 79.0, 60: 84.0, 10: 89.5, -40: 95.5}.get(x, 199)
    RLAMP.append((hm, light(f"L_E{i}", "POINT", 55, (1, 0.6, 0.3), (x, y, 3.2)), td))
# the heath: rocks, low stone walls, gorse, bare trees, far hills
rocks = []
for i in range(80):
    x = rr.uniform(-300, 420); y = rr.uniform(-160, 160)
    if flatd(x, y) < 9 or math.hypot(x - CX, y - CY) < HILL_R + 4: continue
    s = rr.uniform(0.5, 1.8); rocks.append(((x, y, gh(x, y) + s * 0.3), (s * 1.4, s, s * 0.9), rr.uniform(0, 3)))
pboxes("S_Rocks", newM("S_RockM", (0.16, 0.16, 0.15), rough=1), rocks)
walls = []
for k in range(26):
    x = rr.uniform(-280, 400); y = rr.choice((rr.uniform(-130, -60), rr.uniform(-25, 25), rr.uniform(65, 130)))
    if flatd(x, y) < 10 or math.hypot(x - CX, y - CY) < RR + 14: continue
    walls.append(((x, y, gh(x, y) + 0.35), (rr.uniform(10, 18), 0.6, 0.9), rr.uniform(-0.3, 0.3)))
pboxes("S_Walls", newM("S_WallM", (0.11, 0.11, 0.1), rough=1), walls)
gorse = []
for i in range(120):
    x = rr.uniform(-250, 380); y = rr.uniform(-140, 140)
    if flatd(x, y) < 6: continue
    s = rr.uniform(0.6, 1.4); gorse.append(((x, y, gh(x, y) + s * 0.35), (s * 1.5, s * 1.3, s * 0.7), rr.uniform(0, 3)))
pboxes("S_Gorse", newM("S_GorseM", (0.05, 0.065, 0.04), rough=1), gorse)
treeM = newM("S_Tree", (0.03, 0.03, 0.03), rough=1); bm = bmesh.new()
for i in range(34):
    x = rr.uniform(-280, 420); y = rr.choice((rr.uniform(14, 120), rr.uniform(-120, -14)))
    if flatd(x, y) < 10 or math.hypot(x - CX, y - CY) < RR + 16: continue
    h = rr.uniform(4, 8); z0 = gh(x, y)
    g = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=6, radius1=0.25, radius2=0.08, depth=h)["verts"]; bmesh.ops.translate(bm, vec=(x, y, z0 + h / 2), verts=g)
    for b_ in range(3):
        g = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=5, radius1=0.12, radius2=0.03, depth=h * 0.45)["verts"]
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(rr.uniform(0, 6.28), 3, "Z") @ Matrix.Rotation(0.7, 3, "Y"), verts=g)
        bmesh.ops.translate(bm, vec=(x, y, z0 + h * (0.55 + b_ * 0.12)), verts=g)
mk("S_Trees", bm, treeM)
farM = newM("S_FarHill", (0.045, 0.055, 0.045), rough=1)
for i in range(8):
    hx = -300 + i * 95
    mk("S_FarHill", sph(1, 20, 12), farM, (hx, rr.uniform(230, 260), -6), scl=(rr.uniform(55, 70), 40, rr.uniform(18, 30)), smooth=True)
    mk("S_FarHill", sph(1, 20, 12), farM, (hx + 40, -rr.uniform(230, 260), -6), scl=(rr.uniform(55, 70), 40, rr.uniform(18, 30)), smooth=True)
# Lamp Town and its station at the west end of the exit line
houseM = newM("S_HouseM", (0.075, 0.07, 0.078), rough=1); roofM = newM("S_Roof", (0.06, 0.06, 0.07), rough=1)
winM = newM("S_Win", (1, 0.62, 0.25), emit=5)
for i in range(26):
    x = rr.uniform(-270, -160); y = rr.choice((rr.uniform(54, 95), rr.uniform(10, 36))); w = rr.uniform(3, 6); h = rr.uniform(2.5, 5)
    z0 = gh(x, y); sd = 1 if y > YE else -1
    mk("S_House", box(), houseM, (x, y, z0 + h / 2 - 0.5), scl=(w, w, h)); mk("S_Roof", box(), roofM, (x, y, z0 + h - 0.4), scl=(w + 0.4, w + 0.4, 0.3))
    mk("S_Win", box(), winM, (x, y - sd * (w / 2 + 0.02), z0 + h * 0.45), scl=(0.6, 0.05, 0.7))
mk("S_Platform", box(), newM("S_Plat", (0.1, 0.09, 0.1), rough=1), (-206, YE + 2.4, 0.0), scl=(40, 2.2, 0.6))
for i in range(5):
    x = -224 + i * 9.0; mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, YE + 3.2, 1.7))
    mk("L_StHead", sph(0.2, 12, 8), newM("L_StHeadM", (1, 0.62, 0.25), emit=8), (x, YE + 3.2, 3.45)); light(f"L_St{i}", "POINT", 80, (1, 0.6, 0.3), (x, YE + 3.2, 3.2))
moonM = newM("S_Moon", (0.9, 0.88, 0.8), emit=3)
mk("S_Moon", cyl(9, 9, 0.2, 48), moonM, (230, 330, 90), (math.pi / 2, 0, 0.25))
w = sc.world; w.node_tree.nodes["Background"].inputs[0].default_value = (0.014, 0.018, 0.045, 1)
O["MoonKey"].data.energy = 2.2
FIREM = newM("T_FireM", (1, 0.35, 0.08), emit=12)
mk("T_Fire", box(), FIREM, (2.45, 0, 0.55), scl=(0.06, 0.5, 0.3), parent=T)
FIRE = light("T_FireGlow", "POINT", 25, (1, 0.45, 0.15), (2.2, 0, 0.7), T)
# the falling star (56.6 - 59.8): a bright streak across the sky
STAR = empty("S_StarPivot", (40, 160, 120))
STM = newM("S_StarM", (0.85, 0.95, 1.0), emit=60)
mk("S_StarHead", sph(0.9, 12, 8), STM, (0, 0, 0), parent=STAR)
mk("S_StarTail", box(), newM("S_StarTailM", (0.6, 0.8, 1.0), emit=18), (-9, 0, 0), scl=(18, 0.35, 0.35), parent=STAR)
P0, P1 = Vector((40, 160, 120)), Vector((360, -150, 62))
STAR.rotation_euler = (0, -math.atan2((P1 - P0).z, (P1 - P0).to_2d().length), math.atan2((P1 - P0).y, (P1 - P0).x))
for t, p in ((0, P0), (56.6, P0), (59.8, P1), (100, P1)): key(STAR, "location", F(t), p)
lin(STAR)
for t, s_ in ((0, 0.0), (56.5, 0.0), (56.6, 1.0), (59.7, 1.0), (59.8, 0.0)): key(STAR, "scale", F(t), Vector((s_, s_, s_)))

# ---------------- the Hush ----------------
H = O["Hush"]; H.scale = (2.4, 2.4, 2.4)
mask_spot = light("T_MaskLight", "SPOT", 9000, (0.7, 0.85, 1.0), (0, 0, 0)); mask_spot.data.spot_size = math.radians(18)
c = mask_spot.constraints.new("TRACK_TO"); c.target = O["H_Mask"]; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
mask_spot.parent = H; mask_spot.location = (2.0, -14, 4.0)

# ---------------- animation ----------------
SK = [(0, 0), (5, 25), (10, 50), (14, 100), (18, 160), (21, 200), (25.6, 250), (30, 275), (36, 305), (40, 335), (42.5, S_EXIT0),
      (61.4, S_EXIT0), (62.4, S_EXIT0 + 1.5), (65, S_EXIT0 + 18), (70, S_EXIT0 + 68), (76, S_EXIT0 + 143), (82, S_EXIT0 + 218),
      (88, S_EXIT0 + 288), (92, S_EXIT0 + 328), (95, S_EXIT0 + 348), (96.5, S_EXIT0 + 352), (100, S_EXIT0 + 352)]
def s_at(t):
    for (ta, sa), (tb, sb) in zip(SK, SK[1:]):
        if ta <= t <= tb:
            u = (t - ta) / (tb - ta) if tb > ta else 0; return sa + (sb - sa) * u
    return SK[-1][1]
for f in range(1, END + 1, 4):
    x, y, h = pose(s_at((f - 1) / FPS)); key(T, "location", f, Vector((x, y, 0.0))); key(T, "rotation_euler", f, h, 2)
x, y, h = pose(s_at(100)); key(T, "location", END, Vector((x, y, 0.0))); key(T, "rotation_euler", END, h, 2)
lin(T)
# lamps die
for hm, lt, td in RLAMP:
    if td > 150: continue
    s = hm.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for t, e in ((0, 8), (td - 0.01, 8), (td + 0.15, 0)): s.default_value = e; s.keyframe_insert("default_value", frame=F(t))
    e0 = lt.data.energy
    for t, e in ((0, e0), (td - 0.01, e0), (td + 0.15, 0)): lt.data.energy = e; lt.data.keyframe_insert("energy", frame=F(t))
# the Hush: rises behind Round Hill (5.5-8.5), comes round the west side and crosses the line behind us, follows us into the ring;
# lights off -> it loses us and searches slowly round (we keep the hill between us); the switch is stuck -> it comes round
# and stands right by the dark train (50-57); the falling star: it turns and walks after the light; then it follows us west.
HPOL = [(0, 90, 64, -40), (5.5, 90, 64, -40), (7.0, 90, 64, -14), (8.5, 90, 64, 0), (10, 100, 63, 0), (14, 140, 59, 0), (18, 180, 56, 0),
        (21, 212, 54, 0), (23, 240, 54, 0), (25.6, 262, 54, 0), (30, 274, 55, 0), (36, 300, 56, 0), (40, 330, 56, 0), (44, 375, 56, 0),
        (47, 405, 56, 0), (50, 420, 56, 0), (57.3, 420, 56, 0), (60, 404, 62, 0), (63, 388, 68, 0), (66.5, 378, 72, 0), (70, 380, 74, 0),
        (73, 395, 74, 0)]
for t, thd, r, dz in HPOL:
    x, y = ring(thd, r); key(H, "location", F(t), Vector((x, y, max(gh(x, y), 0.0) * 0.3 + dz))); key(H, "scale", F(t), Vector((2.4, 2.4, 2.4)))
for t, x, y in ((80, 100, 72), (86, 40, 70), (92, -20, 70), (100, -95, 70)):
    key(H, "location", F(t), Vector((x, y, max(gh(x, y), 0.0)))); key(H, "scale", F(t), Vector((2.4, 2.4, 2.4)))
FEED = empty("S_Feed", (150, 0, 10))                      # where it looks while it searches / after the star
for t, x, y, z in ((0, 0, -45, 0), (25.6, 200, -40, 0), (30, 220, -20, 0), (36, 225, 10, 0), (40, 150, -60, 0), (42, 170, 60, 0),
                   (50, 120, 46, 0), (53.5, 100, 40, 0), (55.5, 150, 30, 0), (56.6, 70, 160, 60), (58.2, 200, 0, 100), (59.8, 360, -150, 62),
                   (66.5, 360, -150, 40)):
    key(FEED, "location", F(t), Vector((x, y, z)))
d1 = H.constraints.new("LOCKED_TRACK"); d1.target = T; d1.track_axis = "TRACK_NEGATIVE_Y"; d1.lock_axis = "LOCK_Z"
d2 = H.constraints.new("LOCKED_TRACK"); d2.target = FEED; d2.track_axis = "TRACK_NEGATIVE_Y"; d2.lock_axis = "LOCK_Z"
for t, v in ((0, 0.0), (25.6, 0.0), (26.8, 1.0), (40.6, 1.0), (42.0, 0.5), (49.0, 0.5), (50.0, 0.85), (55.5, 0.85), (56.6, 1.0), (66.5, 1.0), (68.0, 0.0)):
    d2.influence = v; d2.keyframe_insert("influence", frame=F(t))
gm = M("H_Green").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 0), (5.5, 0), (7.4, 60), (100, 60)): gm.default_value = e; gm.keyframe_insert("default_value", frame=F(t))
# our lights: out at 26.0 ("Lights off! Keep the hill between us."), back on at 61.6 ("The switch! Now, full steam!")
L0, L1 = 26.0, 61.6
se = M("H_Signal").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 40), (9, 40), (10, 80), (L0 - 0.2, 80), (L0 + 0.8, 3), (L1 - 0.2, 3), (L1 + 0.4, 60), (100, 50)): se.default_value = e; se.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 4), (10, 6), (L0 - 0.2, 6), (L0 + 0.8, 0.3), (L1 - 0.2, 0.3), (L1 + 0.4, 4)): SIGL.data.energy = e; SIGL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 900), (L0 - 0.2, 900), (L0, 0), (L1, 0), (L1 + 0.3, 900)): HL.data.energy = e; HL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 45), (L0 - 0.2, 45), (L0 + 0.4, 16), (L1 - 0.2, 16), (L1 + 0.6, 45)): O["Fill"].data.energy = e; O["Fill"].data.keyframe_insert("energy", frame=F(t))
wi = M("H_Window").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 4), (L0 - 0.1, 4), (L0 + 0.2, 0.0), (L1, 0.0), (L1 + 0.3, 4)): wi.default_value = e; wi.keyframe_insert("default_value", frame=F(t))
fe = FIREM.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 12), (L0 - 0.2, 12), (L0 + 0.1, 0), (L1 - 0.2, 0), (L1 + 0.2, 20), (100, 14)): fe.default_value = e; fe.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 25), (L0 - 0.2, 25), (L0 + 0.1, 0), (L1 - 0.2, 0), (L1 + 0.2, 40), (100, 30)): FIRE.data.energy = e; FIRE.data.keyframe_insert("energy", frame=F(t))
# the stuck lever: Rook pulls (42.8-46), it won't move; it gives at 61.2
for t, a in ((0, 30), (42.8, 30), (43.4, 24), (43.8, 30), (44.6, 23), (45.0, 30), (61.0, 30), (61.5, -30), (100, -30)):
    key(LEV, "rotation_euler", F(t), math.radians(a), 1)
# Rook head (rz = local direction + 30: 30 ahead, 120 left / over the hill in the ring, -150 back, -60 right)
for t, rz in ((0, 30), (5.0, 30), (5.6, 70), (9.6, 70), (10.2, 30), (12.0, 30), (12.6, 90), (16.0, 90), (16.6, 30), (20.4, 30), (21.0, -170), (24.4, -170),
              (25.0, 30), (27.0, 30), (27.6, 120), (33.0, 120), (33.6, 100), (38.4, 100), (39.0, 30), (42.4, 30), (42.8, -40), (46.0, -40),
              (46.6, -170), (56.2, -170), (56.8, 170), (60.4, 170), (61.0, -40), (61.8, 30), (72.6, 30), (73.2, -150), (77.4, -150), (78.0, 30), (100, 30)):
    key(HP, "rotation_euler", F(t), math.radians(rz), 2)
for sd in (-1, 1):
    wg = O[f"R_Wing{sd}"]
    for t, a in ((0, 0), (1.0, 0), (1.3, 1.2), (1.6, 0.3), (1.9, 1.2), (2.3, 0), (10.1, 0), (10.4, 1.3), (12.4, 1.3), (12.8, 0),
                 (18.2, 0), (18.5, 1.2), (20.4, 1.2), (20.8, 0), (24.0, 0), (24.3, 1.5), (26.4, 1.5), (26.8, 0),
                 (27.4, 0), (27.8, -0.6), (42.6, -0.6), (42.9, 1.5), (43.4, 0.4), (43.8, 1.5), (44.6, 0.4), (45.0, 1.5), (45.6, -0.6),
                 (56.6, -0.6), (57.0, 1.0), (59.6, 1.0), (60.0, -0.6), (61.0, -0.6), (61.3, 1.5), (64.0, 1.5), (64.4, 0),
                 (74.6, 0), (74.9, 1.3), (77.0, 1.3), (77.4, 0), (90.4, 0), (90.7, 1.0), (92.8, 1.0), (93.2, 0)):
        key(wg, "rotation_euler", F(t), math.radians(sd * 12) + sd * a * 0.6, 1)
for f in range(1, END, 12):
    if F(26.5) <= f <= F(62.4) or f >= F(96.0): continue     # dark and slow / stopped
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
cam("Cam_01", 0, (3.0, -11, 2.6), (1.0, 0, 1.6), 26, T)                          # wide side: the train on the night heath
cam("Cam_02", 5.0, (-4, -2.2, 3.4), "H_Mask", 34, T)                               # over the train: the hill lamps die, its face rises over Round Hill
cam("Cam_03", 9.8, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)                       # Rook: it's coming round the hill
cam("Cam_04", 12.6, (20, -150, 55), (110, -20, 6), 24)                           # high wide: the hill, the line, it comes round the west side
cam("Cam_05", 17.2, (-4, 3.0, 2.8), "H_Mask", 28, T)                              # from the train: it closes in from the hill side
cam("Cam_06", 20.4, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)                      # Rook: faster! it's right behind us
cam("Cam_07", 22.4, (205, -98, 16), (150, -40, 8), 24)                           # wide: into the ring, it crosses the line behind us
cam("Cam_08", 24.6, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)                      # Rook: lights off! keep the hill between us
cam("Cam_09", 28.4, (150, -118, 120), (150, 0, 0), 26)                           # high over the ring: the dark train and the Hush on opposite sides
cam("Cam_10", 33.4, (1.4, 2.6, 2.2), "H_Mask", 34, T)                             # from the dark train: its face over the hilltop, going round
cam("Cam_11", 37.2, (262, 70, 60), (160, 10, 6), 24)                             # wide from the north-east: still opposite, we near the north point
cam("Cam_12", 39.6, (118, 53, 4.5), (150, 44, 1.5), 24)                          # at the switch: the dark train rolls up and stops
cam("Cam_13", 42.6, (-1.5, -4.2, 2.2), (0.9, -1.0, 1.0), 26, T)                   # Rook pulls the lever: stuck
cam("Cam_14", 46.0, (118, 112, 34), (172, 32, 10), 24)                           # wide: it comes round the east side to the dark train
cam("Cam_15", 49.4, (136, 51, 2.2), (186, 36, 17), 20)                           # low behind the train: it stands right by us (cold open)
cam("Cam_16", 52.6, (4.5, 1.0, 2.4), "H_Mask", 26, T)                            # Rook and its face
cam("Cam_17", 56.0, (126, 64, 4), (230, -60, 55), 20)                            # the falling star; it turns to the light
cam("Cam_18", 59.4, (-3.0, -2.6, 2.6), "H_Mask", 30, T)                           # from the train: it walks off after the star
cam("Cam_19", 60.8, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)                      # Rook: the switch! lights on, full steam
cam("Cam_20", 63.4, (98, 36, 4), (135, 45, 2), 26)                               # the train leaves west, lights on
cam("Cam_21", 67.6, (8, -9, 3), (0, 0, 1.4), 26, T)                              # side: full steam on the exit line
cam("Cam_22", 72.6, (-4, -3.0, 2.6), "H_Mask", 30, T)                             # back: it turns and follows
cam("Cam_23", 78.6, (-120, 10, 26), (60, 70, 8), 22)                             # wide over the heath: it follows far behind
cam("Cam_24", 85.6, (-20, -14, 8), (30, 0, 2), 24, T)                            # Lamp Town ahead
cam("Cam_25", 90.2, (2.4, -3.2, 1.7), (0.6, 0, 1.35), 28, T)                     # Rook at the station
sc.camera = O["Cam_01"]
sc.render.resolution_x = 1280; sc.render.resolution_y = 720; sc.render.resolution_percentage = 100
sc.eevee.taa_render_samples = 24
try: sc.eevee.use_raytracing = False
except Exception: pass
sc.render.use_compositing = False; sc.render.use_sequencer = False
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "hush_film11.blend"))
print("film11 built", len(sc.collection.all_objects), "objects; markers", len(sc.timeline_markers))
