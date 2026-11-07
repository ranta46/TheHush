# GLOAMRUN 3D Film 9 "The Sleeping City" — run INSIDE Blender (hush_lookdev.blend open, scene HUSH).
# Builds the set + animation + cameras on top of the approved 3D Rook / the Hush / train, then saves
# C:\Users\81803\TremenFilm\hush\film08\hush_film08.blend.  24 fps, 2400 frames (100 s).
# Story: the open plain at night, the train runs toward the old city that has slept dark for years -> the lamps
# BEHIND us die and the Hush rises back there -> chase, it is faster than us -> the train stops at the old power
# house and Rook pulls the big switch: the whole sleeping city lights up at once -> the Hush stops and turns to all
# that light -> Rook puts out our lights ("Let it eat") and the dark train creeps through the city while the Hush eats
# it street by street -> it stands right over the line ("Don't move") -> it walks deeper in, we creep on -> surprise:
# every light left in the city dies at once, and the Hush turns to us -> lights on, full steam over the river bridge
# to the hill station; the Hush follows (it will come again).
import bpy, bmesh, math, random, os
from mathutils import Vector
OUT = r"C:\Users\81803\TremenFilm\hush\film08"; os.makedirs(OUT, exist_ok=True)
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


# ---------------- world: the open plain, the old power house, the sleeping city, the river bridge, the hill station ----------------
from mathutils import Matrix
rr = random.Random(99)
def gh(x, y):                              # ground height (flat bed by the line and in the city, low rolls on the plain)
    a = min(1.0, max(0.0, (abs(y) - 8) / 14))
    if 170 < x < 440: a *= 0.15            # the city is flat
    n = 1.0 * math.sin(x * 0.04 + y * 0.03) + 0.7 * math.sin(x * 0.09 - y * 0.06 + 1.3) + 0.5 * math.sin(y * 0.11)
    return a * (n + 0.012 * max(0, abs(y) - 20) ** 1.25) - 0.02
grass = newM("S_Grass", (0.07, 0.08, 0.06), rough=0.95); GA.data.materials.clear(); GA.data.materials.append(grass)
plainM = newM("S_Plain", (0.07, 0.075, 0.06), rough=1)
bm = bmesh.new(); xs = [-200 + i * 5 for i in range(171)]; ys = [-240 + j * 6 for j in range(81)]
vv = [[bm.verts.new((x, y, gh(x, y) if not (455 < x < 505 and abs(y) > 4) else -3.0)) for y in ys] for x in xs]
for i in range(len(xs) - 1):
    for j in range(len(ys) - 1): bm.faces.new((vv[i][j], vv[i + 1][j], vv[i + 1][j + 1], vv[i][j + 1]))
mk("S_PlainGround", bm, plainM, smooth=True)
railM = newM("S_RailM", (0.2, 0.2, 0.22), rough=0.4, metal=0.8); tie = newM("S_Tie", (0.05, 0.04, 0.035), rough=1)
postM = newM("S_Post", (0.02, 0.02, 0.025), rough=0.5); ironM = newM("S_BIron", (0.06, 0.065, 0.075), rough=0.5, metal=0.6)
def pboxes(name, mat, items):   # boxes with yaw + pitch in ONE mesh: (loc, scl, rz, ry)
    bm = bmesh.new()
    for loc, scl, rz, ry in items:
        g = bmesh.ops.create_cube(bm, size=1.0)["verts"]; bmesh.ops.scale(bm, vec=scl, verts=g)
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(rz, 3, "Z") @ Matrix.Rotation(ry, 3, "Y"), verts=g)
        bmesh.ops.translate(bm, vec=loc, verts=g)
    return mk(name, bm, mat)
rails, ties = [], []
for i in range(200):                                        # the line, x -160 .. 640, straight and flat
    xa = -160 + i * 4.0
    for yy in (-0.53, 0.53): rails.append(((xa + 2, yy, 0.03), (4.02, 0.08, 0.06), 0, 0))
    for k in (0, 2): ties.append(((xa + k + 1, 0, 0.01), (0.25, 1.4, 0.06), 0, 0))
pboxes("S_Rails", railM, rails); pboxes("S_Ties", tie, ties)
# the plain: fences, a few lone trees, rocks; the line lamps behind us (they die first, far ones first)
rocks = []
for i in range(60):
    x = rr.uniform(-180, 160); y = rr.choice((rr.uniform(8, 140), rr.uniform(-140, -8))); s = rr.uniform(0.5, 2.0)
    rocks.append(((x, y, gh(x, y) + s * 0.3), (s * 1.4, s, s * 0.9), rr.uniform(0, 3), 0))
pboxes("S_Rocks", newM("S_RockM", (0.12, 0.115, 0.11), rough=1), rocks)
treeM = newM("S_Tree", (0.03, 0.035, 0.03), rough=1)
for i in range(14):
    x = rr.uniform(-170, 150); y = rr.choice((rr.uniform(14, 90), rr.uniform(-90, -14))); h = rr.uniform(3, 6)
    mk("S_TreeT", cyl(0.12, 0.08, h, 6), treeM, (x, y, gh(x, y) + h / 2))
    mk("S_TreeC", sph(1, 10, 6), treeM, (x, y, gh(x, y) + h), scl=(h * 0.45, h * 0.35, h * 0.25))
BLAMP = []
for i, x in enumerate((-140, -115, -90, -65, -40, -15)):
    mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, -4.0, 1.7))
    hm = newM(f"L_BHead{i}", (1, 0.62, 0.25), emit=8); mk(f"L_BHead{i}", sph(0.2, 12, 8), hm, (x, -4.0, 3.45))
    BLAMP.append((hm, light(f"L_B{i}", "POINT", 60, (1, 0.6, 0.3), (x, -4.0, 3.2))))
# the old power house by the line (x 150): brick hall, tall chimney, the big switch on a post by the track
brick = newM("S_Brick", (0.13, 0.06, 0.045), rough=1); roofM = newM("S_Roof", (0.06, 0.06, 0.07), rough=1)
PX = 146.0
mk("S_PowerHall", box(), brick, (PX + 2, -16, 5), scl=(22, 12, 10)); mk("S_PowerRoof", box(), roofM, (PX + 2, -16, 10.3), scl=(23, 13, 0.6))
mk("S_Chimney", cyl(1.6, 1.2, 30, 16), brick, (PX - 6, -20, 15))
mk("S_PowerWin", box(), newM("S_DarkWin", (0.02, 0.025, 0.03), rough=0.3), (PX + 2, -9.95, 5.5), scl=(16, 0.05, 3))
mk("S_SwitchPost", box(), ironM, (PX + 0.8, -2.2, 0.8), scl=(0.5, 0.5, 1.6))
LEV = empty("S_LeverPivot", (PX + 0.8, -2.2, 1.6))
mk("S_Lever", box(), ironM, (0, 0, 0.55), scl=(0.08, 0.08, 1.1), parent=LEV)
mk("S_LeverKnob", sph(0.12, 10, 6), newM("S_Red", (0.6, 0.05, 0.03), rough=0.5), (0, 0, 1.1), parent=LEV)
PLM = newM("L_PLampM", (1, 0.62, 0.25), emit=8)
mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (PX - 2, -3.0, 1.7)); mk("L_PLamp", sph(0.2, 12, 8), PLM, (PX - 2, -3.0, 3.45))
PL = light("L_PowerLamp", "POINT", 60, (1, 0.6, 0.3), (PX - 2, -3.0, 3.2))
# the sleeping city (x 180 .. 430): blocks on both sides of a wide street; windows grouped in 8 districts (they wake and die)
houseM = newM("S_HouseM", (0.075, 0.07, 0.078), rough=1)
NDIS = 8; DX0, DX1 = 180.0, 430.0
def dist_of(x): return min(NDIS - 1, max(0, int((x - DX0) / ((DX1 - DX0) / NDIS))))
blocks = []; roofs = []; wins = [[] for _ in range(NDIS)]
for side in (-1, 1):
    for row in range(4):
        x = DX0 + rr.uniform(0, 6)
        while x < DX1:
            w = rr.uniform(6, 11); d = rr.uniform(6, 10); h = rr.uniform(6, 16) + row * 2.5
            y = side * (9 + row * 14 + rr.uniform(0, 3) + d / 2)
            if not (row == 0 and side == -1 and x < 200):
                blocks.append(((x + w / 2, y, h / 2 - 0.3), (w, d, h), 0, 0)); roofs.append(((x + w / 2, y, h - 0.2), (w + 0.4, d + 0.4, 0.4), 0, 0))
                fy = y - side * (d / 2 + 0.03); di = dist_of(x + w / 2)
                for fl in range(int((h - 2) / 2.6)):
                    for c in range(int(w / 2.4)):
                        if rr.random() < 0.72: wins[di].append(((x + 1.2 + c * 2.4, fy, 1.6 + fl * 2.6), (0.9, 0.06, 1.1), 0, 0))
                # windows on the side facing the ends too (seen in the wide shots)
            x += w + rr.uniform(0.5, 3)
pboxes("S_Blocks", houseM, blocks); pboxes("S_Roofs", roofM, roofs)
CWIN = []; CLT = []
for di in range(NDIS):
    m = newM(f"L_CityWin{di}", (1, 0.66, 0.3), emit=0); pboxes(f"L_CityWin{di}", m, wins[di]); CWIN.append(m)
    cx = DX0 + (di + 0.5) * (DX1 - DX0) / NDIS
    CLT.append((light(f"L_City{di}a", "POINT", 0, (1, 0.62, 0.3), (cx, -16, 9)), light(f"L_City{di}b", "POINT", 0, (1, 0.62, 0.3), (cx, 16, 9))))
# street lamps along the line in the city (they wake with their district)
SLAMP = []
for i in range(10):
    x = 188 + i * 24.0; di = dist_of(x)
    mk("S_Post", cyl(0.06, 0.08, 3.6, 8), postM, (x, 4.0, 1.8))
    SLAMP.append((di, x))
    mk(f"L_SHead{di}", sph(0.2, 12, 8), CWIN[di], (x, 4.0, 3.65))
# a clock tower in the middle of the city (dark, it never wakes: we see its face in the window light)
mk("S_Tower", box(), houseM, (300, 30, 13), scl=(6, 6, 26)); mk("S_TowerTop", cyl(4.6, 0.2, 7, 4), roofM, (300, 30, 29.5), (0, 0, math.pi / 4))
mk("S_Clock", cyl(1.8, 1.8, 0.1, 24), CWIN[5], (300, 26.95, 22), (math.pi / 2, 0, 0))
# the river (x 455 .. 505) and the iron bridge
mk("S_River", box(), newM("S_Water", (0.01, 0.02, 0.04), rough=0.08, metal=0.3), (480, 0, -1.6), scl=(50, 480, 0.1))
truss = []
for sd in (-1, 1):
    truss.append(((480, sd * 1.9, 3.2), (54, 0.25, 0.3), 0, 0)); truss.append(((480, sd * 1.9, -0.25), (54, 0.4, 0.5), 0, 0))
    for k in range(10):
        x = 455 + k * 5.6; truss.append(((x, sd * 1.9, 1.5), (0.25, 0.25, 3.4), 0, 0))
        truss.append(((x + 2.8, sd * 1.9, 1.5), (0.2, 0.2, 4.3), 0, math.radians(40 if k % 2 else -40)))
for k in range(10): truss.append(((455 + k * 5.6, 0, 3.3), (0.2, 3.8, 0.2), 0, 0))
for x in (455, 480, 505): truss.append(((x, 0, -1.8), (2, 3, 3.2), 0, 0))
pboxes("S_Bridge", ironM, truss)
# the hill station (x 560 .. 640) under low hills
hillM = newM("S_HillM", (0.05, 0.06, 0.05), rough=1)
for i in range(5):
    hx = 540 + i * 50
    mk("S_Hill", sph(1, 20, 12), hillM, (hx, rr.uniform(95, 115), -6), scl=(rr.uniform(40, 55), 30, rr.uniform(16, 26)), smooth=True)
    mk("S_Hill", sph(1, 20, 12), hillM, (hx + 25, -rr.uniform(95, 115), -6), scl=(rr.uniform(40, 55), 30, rr.uniform(16, 26)), smooth=True)
winM = newM("S_Win", (1, 0.62, 0.25), emit=5)
for i in range(18):
    x = rr.uniform(560, 660); y = rr.choice((rr.uniform(8, 36), rr.uniform(-36, -10))); w = rr.uniform(3, 6); h = rr.uniform(2.5, 5)
    mk("S_House", box(), houseM, (x, y, h / 2 - 0.5), scl=(w, w, h)); mk("S_Roof", box(), roofM, (x, y, h - 0.4), scl=(w + 0.4, w + 0.4, 0.3))
    mk("S_Win", box(), winM, (x, y - math.copysign(w / 2 + 0.02, y), h * 0.45), scl=(0.6, 0.05, 0.7))
mk("S_Platform", box(), newM("S_Plat", (0.1, 0.09, 0.1), rough=1), (605, 2.4, 0.0), scl=(50, 2.2, 0.6))
for i in range(5):
    x = 585 + i * 10.0; mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, 3.2, 1.7))
    mk("L_StHead", sph(0.2, 12, 8), newM("L_StHeadM", (1, 0.62, 0.25), emit=8), (x, 3.2, 3.45)); light(f"L_St{i}", "POINT", 80, (1, 0.6, 0.3), (x, 3.2, 3.2))
moonM = newM("S_Moon", (0.9, 0.88, 0.8), emit=3)
mk("S_Moon", cyl(9, 9, 0.2, 48), moonM, (300, 280, 95), (math.pi / 2, 0, 0))
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
def tkey(t, x):
    key(T, "location", F(t), Vector((x, 0, 0))); key(T, "rotation_euler", F(t), 0.0, 1); key(T, "rotation_euler", F(t), 0.0, 2)
TX = [(0, -110), (8, -45), (12, -12), (16, 22), (20, 58), (24, 96), (26.5, 124), (28.5, 141), (29.0, 142.5), (38, 142.5),
      (42, 160), (46.2, 186), (46.6, 187), (56, 187), (60, 202), (64, 222), (65.5, 224), (67.5, 230), (70, 252), (74, 300),
      (78, 352), (82, 405), (86, 458), (90, 514), (94, 566), (97.5, 600), (100, 604)]
for t, x in TX: tkey(t, x)
lin(T)
# the lamps behind us die, far ones first (8-11)
for i, (hm, lt) in enumerate(BLAMP):
    td = 8.0 + i * 0.5; s = hm.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for t, e in ((td - 0.01, 8), (td + 0.15, 0)): s.default_value = e; s.keyframe_insert("default_value", frame=F(t))
    for t, e in ((td - 0.01, 60), (td + 0.15, 0)): lt.data.energy = e; lt.data.keyframe_insert("energy", frame=F(t))
# the power house lamp: on until we put our lights out (35.6)
s = PLM.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 8), (35.6, 8), (35.8, 0)): s.default_value = e; s.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 60), (35.6, 60), (35.8, 0)): PL.data.energy = e; PL.data.keyframe_insert("energy", frame=F(t))
# the lever (29.6-30.6), then the city wakes, district by district from the power house outwards (31-33.8)
for t, a in ((0, -35), (29.6, -35), (30.6, 35), (100, 35)): key(LEV, "rotation_euler", F(t), math.radians(a), 0)
DIE = [40.5, 50.5, 58.0, 61.0, 64.2, 64.2, 64.2, 64.2]       # when the Hush eats each district (the last four at once)
for di, m in enumerate(CWIN):
    tw = 31.0 + di * 0.35; td = DIE[di]; s = m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for t, e in ((0, 0), (tw, 0), (tw + 0.25, 7), (td, 7), (td + 0.5, 0)): s.default_value = e; s.keyframe_insert("default_value", frame=F(t))
    for lt in CLT[di]:
        for t, e in ((0, 0), (tw, 0), (tw + 0.25, 1500), (td, 1500), (td + 0.5, 0)): lt.data.energy = e; lt.data.keyframe_insert("energy", frame=F(t))
# the Hush: rises behind us on the plain (12-15), gains on us, stops at the city light (31.5), walks in and eats it
HP_ = [(0, -75, -18, -40), (12.0, -75, -18, -40), (13.8, -75, -18, -14), (15.5, -75, -18, 0), (20, -30, -16, 0), (24, 20, -16, 0),
       (28, 72, -16, 0), (31.5, 98, -16, 0), (34, 104, -16, 0), (38, 150, -26, 0), (41, 186, -26, 0), (46, 195, -15, 0), (55.5, 197, -15, 0),
       (58.5, 215, -50, 0), (61.5, 240, -62, 0), (64.2, 250, -62, 0), (66.5, 250, -62, 0), (70, 262, -40, 0), (74, 280, -16, 0),
       (80, 336, -14, 0), (86, 390, -14, 0), (92, 438, -14, 0), (100, 470, -14, 0)]
for t, x, y, dz in HP_:
    key(H, "location", F(t), Vector((x, y, gh(x, y) + dz))); key(H, "scale", F(t), Vector((2.4, 2.4, 2.4)))
FEED = empty("S_Feed", (200, -30, 8))                           # where it is eating (it faces this while the city is lit)
for t, x, y in ((31.5, 250, -20), (38, 200, -40), (46, 205, -40), (55.5, 205, -40), (58.5, 245, -75), (61.5, 285, -60), (64.2, 330, -45)):
    key(FEED, "location", F(t), Vector((x, y, 8)))
d1 = H.constraints.new("LOCKED_TRACK"); d1.target = T; d1.track_axis = "TRACK_NEGATIVE_Y"; d1.lock_axis = "LOCK_Z"
d2 = H.constraints.new("LOCKED_TRACK"); d2.target = FEED; d2.track_axis = "TRACK_NEGATIVE_Y"; d2.lock_axis = "LOCK_Z"
for t, v in ((0, 0.0), (31.6, 0.0), (33.0, 1.0), (47.0, 1.0), (48.2, 0.35), (54.0, 0.35), (55.5, 1.0), (64.4, 1.0), (65.8, 0.0)):
    d2.influence = v; d2.keyframe_insert("influence", frame=F(t))
gm = M("H_Green").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 0), (12.5, 0), (14, 60), (100, 60)): gm.default_value = e; gm.keyframe_insert("default_value", frame=F(t))
# our lights: all out at 35.6 (Rook: "Now lights off. Let it eat."), back on at 67.4
se = M("H_Signal").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 40), (14, 40), (15, 80), (35.4, 80), (36.4, 3), (67.2, 3), (67.8, 60), (100, 50)): se.default_value = e; se.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 4), (15, 6), (35.4, 6), (36.4, 0.3), (67.2, 0.3), (67.8, 4)): SIGL.data.energy = e; SIGL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 900), (35.4, 900), (35.6, 0), (67.4, 0), (67.7, 900)): HL.data.energy = e; HL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 45), (35.4, 45), (36.0, 14), (67.2, 14), (68.0, 45)): O["Fill"].data.energy = e; O["Fill"].data.keyframe_insert("energy", frame=F(t))
wi = M("H_Window").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 4), (35.5, 4), (35.8, 0.0), (67.4, 0.0), (67.7, 4)): wi.default_value = e; wi.keyframe_insert("default_value", frame=F(t))
fe = FIREM.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 12), (35.4, 12), (35.7, 0), (67.2, 0), (67.6, 20), (100, 14)): fe.default_value = e; fe.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 25), (35.4, 25), (35.7, 0), (67.2, 0), (67.6, 40), (100, 30)): FIRE.data.energy = e; FIRE.data.keyframe_insert("energy", frame=F(t))
# Rook head turns (30 = ahead, -40 = to the side, -150 = back) and wings
for t, rz in ((0, 30), (7.6, 30), (8.4, -150), (12.6, -150), (16.2, -150), (17.0, 30), (20.6, 30), (21.4, -150), (24.6, -150), (25.4, 30),
              (28.6, 30), (29.2, -60), (31.2, -60), (31.8, -20), (34.6, -20), (35.2, 0), (40, 0), (40.8, -40), (52, -40), (52.6, -60),
              (56.5, -60), (57.2, 0), (63.8, 0), (64.4, -40), (66.6, -40), (67.2, 30), (75.6, 30), (76.4, -150), (80, -150), (80.6, 30), (100, 30)):
    key(HP, "rotation_euler", F(t), math.radians(rz), 2)
for sd in (-1, 1):
    wg = O[f"R_Wing{sd}"]
    for t, a in ((0, 0), (1.0, 0), (1.3, 1.2), (1.6, 0.3), (1.9, 1.2), (2.3, 0), (15.5, 0), (15.8, 1.3), (18.0, 1.3), (18.4, 0),
                 (26.0, 0), (26.3, 1.0), (28.4, 1.0), (28.8, 0), (29.4, 0), (29.7, 1.5), (30.7, 0.4), (31.4, 1.5), (32.4, 1.5), (32.8, 0),
                 (36.5, 0), (36.9, -0.6), (63.5, -0.6), (63.9, 0), (64.6, 0), (64.9, 1.4), (66.4, 1.4), (66.8, 0),
                 (67.2, 0), (67.5, 1.5), (70.0, 1.5), (70.4, 0), (80.6, 0), (80.9, 1.3), (83.0, 1.3), (83.4, 0), (91, 0), (91.3, 1.0), (93.2, 1.0), (93.6, 0)):
        key(wg, "rotation_euler", F(t), math.radians(sd * 12) + sd * a * 0.6, 1)
for f in range(1, END, 12):
    if F(28.5) <= f <= F(38) or F(46.2) <= f <= F(56) or f >= F(97.5): continue      # train stopped
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
cam("Cam_01", 0, (3.0, -11, 2.6), (1.0, 0, 1.6), 26, T)                    # wide side: the train on the plain, the dark city ahead
cam("Cam_02", 7.6, (-6, 2.5, 4.0), (-80, -4, 1.5), 30, T)                  # looking back: the lamps behind us die
cam("Cam_03", 11.4, (2.6, -3.4, 1.8), (0.6, -0.4, 1.3), 28, T)             # Rook close
cam("Cam_04", 13.2, (-5, -1.5, 3.2), "H_Mask", 55, T)                      # it rises behind us
cam("Cam_05", 15.5, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)                # Rook: full steam
cam("Cam_06", 18.4, (60, -95, 26), (10, -10, 8), 18)                        # wide: the chase over the plain
cam("Cam_07", 21.2, (-4, -3.2, 2.6), "H_Mask", 28, T)                       # from the train: it gains on us
cam("Cam_08", 24.6, (120, -42, 14), (150, -8, 5), 22)                       # the old power house ahead
cam("Cam_09", 28.6, (PX + 5.5, -7.5, 2.6), (PX + 0.6, -1.2, 1.6), 28)      # Rook at the big switch
cam("Cam_10", 30.9, (150, -70, 42), (300, 0, 4), 20)                        # the whole city wakes up
cam("Cam_11", 33.4, (128, -4, 4), "H_Mask", 35)                             # it stops, turns to the light
cam("Cam_12", 35.0, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)                # Rook: lights off, let it eat
cam("Cam_13", 39.2, (165, 28, 16), (200, -14, 9), 22)                       # the dark train creeps in, it eats the first street
cam("Cam_14", 45.6, (2.6, -3.0, 1.6), (0.6, 0, 1.35), 28, T)               # Rook in the dark
cam("Cam_15", 49.4, (191, 7, 1.2), (195, -12, 13), 18)                      # low by the line: it stands right over us
cam("Cam_16", 52.6, (-1.6, -1.0, 1.9), "H_Mask", 30, T)                    # from the cab: up at its face
cam("Cam_17", 56.0, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)                # Rook: it's going
cam("Cam_18", 59.2, (215, 45, 26), (250, -30, 6), 22)                       # wide: it walks deeper in, street by street dies
cam("Cam_19", 63.2, (236, -4, 24), "H_Mask", 32)                             # every light dies at once; it turns to us
cam("Cam_20", 66.4, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)                # Rook: lights on, full steam
cam("Cam_21", 70.4, (8, -9, 3), (0, 0, 1.4), 26, T)                        # lights on, out of the city
cam("Cam_22", 75.6, (-4, -3.2, 2.6), "H_Mask", 28, T)                      # looking back: it follows
cam("Cam_23", 80.4, (470, -36, 9), (482, 0, 2), 22)                         # over the river bridge
cam("Cam_24", 85.6, (-20, -14, 8), (30, 0, 2), 24, T)                      # wide: the hill station ahead
cam("Cam_25", 90.6, (2.4, -3.2, 1.7), (0.6, 0, 1.35), 28, T)               # Rook at the station
sc.camera = O["Cam_01"]
sc.render.resolution_x = 1280; sc.render.resolution_y = 720; sc.render.resolution_percentage = 100
sc.eevee.taa_render_samples = 24
try: sc.eevee.use_raytracing = False
except Exception: pass
sc.render.use_compositing = False; sc.render.use_sequencer = False
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "hush_film08.blend"))
print("film08 built", len(sc.collection.all_objects), "objects; markers", len(sc.timeline_markers))
