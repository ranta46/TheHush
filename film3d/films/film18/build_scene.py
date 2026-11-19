# GLOAMRUN 3D Film 21 "The Zigzag" — run INSIDE Blender (hush_lookdev.blend open, scene HUSH).
# Story (no calm start): the valley lamps die behind us and its face rises in the pine valley at once -> it is faster in the valley ->
# Rook's move: he takes the old zigzag line (switchback) up the steep loose-stone face of Iron Mountain: forward, then BACKWARDS
# up the second leg, then forward again ("Rails go where feet can't") -> it tries to climb straight up and the stones slide under it
# -> it climbs again, higher; at switch two Rook stops with every light out, its face right beside the ledge ('...Don't move.')
# -> the stones give and it slides a little; Rook creeps on in the dark -> surprise: the wheels slip on the wet rails and the train
# rolls back toward it -> "Sand on the rails! Full steam!" -> up the last leg; it slides all the way down to the foot -> High Gate.
# It stands at the foot of the mountain, looking up (it will be back).
import bpy, bmesh, math, random, os
from mathutils import Vector
OUT = r"C:\Users\81803\TremenFilm\hush\film18"; os.makedirs(OUT, exist_ok=True)
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






# ---------------- world: the pine valley, Iron Mountain and its old zigzag line (switchback), High Gate on the top ----------------
from mathutils import Matrix
rr = random.Random(2121)
def ss(a, b, v):
    u = min(1.0, max(0.0, (v - a) / (b - a))); return u * u * (3 - 2 * u)
def face(y): return 0.9 * min(60.0, max(0.0, y - 4.0))          # the steep loose-stone face (45 deg), plateau 54 m up
# the line: valley (A-B) -> leg 1 forward up (B-C) -> switch one, leg 2 BACKWARDS up (C-D) -> switch two, leg 3 forward up (D-E) -> High Gate (E-F)
PTS = [Vector((-330, 0, 0)), Vector((-10, 0, 0)), Vector((150, 22, face(22))), Vector((10, 40, face(40))), Vector((170, 66, 54.0)), Vector((340, 66, 54.0))]
REV = [False, False, True, False, False]
SEG = [(PTS[i + 1] - PTS[i]).length for i in range(5)]; CUM = [0.0]
for l in SEG: CUM.append(CUM[-1] + l)
def path(s):
    s = max(0.0, min(CUM[-1], s))
    for i in range(5):
        if s <= CUM[i + 1] + 1e-6:
            u = (s - CUM[i]) / SEG[i]; d = (PTS[i + 1] - PTS[i]).normalized()
            return PTS[i].lerp(PTS[i + 1], u), (-d if REV[i] else d)
def dseg(x, y, a, b):
    ax, ay, bx, by = a.x, a.y, b.x, b.y; vx, vy = bx - ax, by - ay
    u = max(0.0, min(1.0, ((x - ax) * vx + (y - ay) * vy) / (vx * vx + vy * vy)))
    px, py = ax + vx * u, ay + vy * u; return math.hypot(x - px, y - py), a.z + (b.z - a.z) * u
def gh(x, y):
    n = 0.9 * math.sin(x * 0.05 + y * 0.03) + 0.6 * math.sin(x * 0.11 - y * 0.07 + 1.3)
    z = face(y) + (0.6 * n if y > 6 else 0.3 * n - 0.2) + (0.5 * n if 8 < y < 62 else 0)
    z += ss(-60, -140, y) * (8 + 4 * n)                          # the far side of the valley rises (south)
    for i in range(1, 5):                                         # ledges cut into the face for the rails
        d, lz = dseg(x, y, PTS[i], PTS[i + 1])
        if d < 6.5: k = 1 - ss(3.6, 6.5, d); z = z + (lz - 0.06 - z) * k
    d, lz = dseg(x, y, PTS[0], PTS[1])
    if d < 5: z = min(z, -0.06 + (z + 0.06) * ss(3.0, 5.0, d))
    return z
GA = O["Ground"]; GA.location = (0, 0, -30.0); GA.scale = (1400, 1000, 1)
stoneM = newM("S_Scree", (0.034, 0.033, 0.036), rough=1); grassM = newM("S_Grass", (0.045, 0.06, 0.045), rough=1)
rockM = newM("S_RockM", (0.08, 0.08, 0.09), rough=1)
GA.data.materials.clear(); GA.data.materials.append(rockM)
def axis(a, b, step):
    out = []; v = a
    while v <= b: out.append(v); v += step
    return out
xs = axis(-460, -130, 8) + axis(-126, 380, 3.0) + axis(386, 640, 8)
ys = axis(-300, -64, 8) + axis(-60, 76, 2.0) + axis(80, 300, 8)
bm = bmesh.new(); vv = [[bm.verts.new((x, y, gh(x, y))) for y in ys] for x in xs]
for i in range(len(xs) - 1):
    for j in range(len(ys) - 1):
        f = bm.faces.new((vv[i][j], vv[i + 1][j], vv[i + 1][j + 1], vv[i][j + 1]))
        yy = ys[j]
        if yy < 4 or yy > 66: f.material_index = 1
GO = mk("S_Ground", bm, stoneM, smooth=True); GO.data.materials.append(grassM)
railM = newM("S_RailM", (0.2, 0.2, 0.22), rough=0.4, metal=0.8); tie = newM("S_Tie", (0.05, 0.04, 0.035), rough=1)
postM = newM("S_Post", (0.02, 0.02, 0.025), rough=0.5)
def pboxes(name, mat, items, parent=None):
    bm = bmesh.new()
    for loc, scl, rzz in items:
        g = bmesh.ops.create_cube(bm, size=1.0)["verts"]; bmesh.ops.scale(bm, vec=scl, verts=g)
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(rzz, 3, "Z"), verts=g); bmesh.ops.translate(bm, vec=loc, verts=g)
    return mk(name, bm, mat, parent=parent)
def bar(bm, a, b, off, w, h, z0):                                 # a long box from a to b, offset sideways
    d = (b - a); sd = Vector((-d.y, d.x, 0)).normalized()
    vs = []
    for p in (a, b):
        c = p + sd * off + Vector((0, 0, z0))
        for s, t in ((-1, 0), (1, 0), (1, 1), (-1, 1)): vs.append(bm.verts.new(c + sd * (s * w / 2) + Vector((0, 0, t * h))))
    for k in range(4): bm.faces.new((vs[k], vs[(k + 1) % 4], vs[4 + (k + 1) % 4], vs[4 + k]))
    bm.faces.new(vs[3::-1]); bm.faces.new(vs[4:])
bm = bmesh.new()
for i in range(5):
    for off in (-0.53, 0.53): bar(bm, PTS[i], PTS[i + 1], off, 0.08, 0.06, 0.0)
mk("S_Rails", bm, railM)
ties = []
for i in range(5):
    a, b = PTS[i], PTS[i + 1]; n = int(SEG[i] / 2); yaw = math.atan2(b.y - a.y, b.x - a.x)
    for k in range(n): p = a.lerp(b, (k + 0.5) / n); ties.append(((p.x, p.y, p.z - 0.02), (0.25, 1.4, 0.06), yaw + math.pi / 2 - math.pi / 2))
pboxes("S_Ties", tie, [((l[0], l[1], l[2]), (0.25, 1.4, 0.06), r) for l, s, r in ties])
pboxes("S_EndStop", newM("S_Red", (0.6, 0.05, 0.03), rough=0.5), [((-328, 0, 0.4), (0.3, 1.8, 0.5), 0), ((338, 66, 54.4), (0.3, 1.8, 0.5), 0)])
# lamps: valley lamps (die as it passes), lamps on the zigzag, High Gate
RLAMP = []
def lamp(tag, x, y, td, e=55, z=None):
    z = gh(x, y) if z is None else z; mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, y, z + 1.7))
    hm = newM(f"L_{tag}", (1, 0.62, 0.25), emit=8); mk(f"L_{tag}", sph(0.2, 12, 8), hm, (x, y, z + 3.45))
    lo = light(f"L_{tag}L", "POINT", e, (1, 0.6, 0.3), (x, y, z + 3.2)); RLAMP.append((hm, lo, td)); return hm, lo
HP_ = [(0, -300, -22, -40), (2.4, -300, -22, -40), (3.4, -300, -22, -14), (4.6, -300, -22, 0), (5.4, -294, -20, 0), (6, -286, -18, 0),
       (11, -222, -12, 0), (16, -158, -8, 0), (20, -100, -6, 0), (24, -40, -4, 0), (26.6, 2, -1, 0),
       (29.0, 24, 8, 0), (30.6, 30, 15, 0), (31.4, 31, 16, 0), (33.6, 36, 2, -1.0), (34.8, 36, 1, -0.6),
       (37.0, 30, 8, 0), (39.4, 24, 16, 0), (40.8, 22, 20, 0), (41.6, 21, 21, 0), (44, 19, 21.5, 0), (47, 22, 21, 0), (50, 18, 21.5, 0),
       (53.6, 20, 21, 0), (55.4, 23, 15.5, -0.5), (57.4, 24, 15, 0), (60.0, 22, 19, 0), (62.6, 24, 21.5, 0), (64.4, 30, 23, 0),
       (66.2, 38, 25, 0), (67.0, 40, 25.5, 0), (69.4, 46, 8, -1.0), (71.0, 48, 0, -1.2), (72.4, 48, -1, -0.6), (76, 44, -3, 0),
       (82, 44, -3, 0), (100, 44, -3, 0)]
def h_x(x):
    for (ta, xa, *_), (tb, xb, *_) in zip(HP_[4:11], HP_[5:11]):
        if xa <= x <= xb and xb > xa: return ta + (tb - ta) * (x - xa) / (xb - xa)
    return 999.0
for i, x in enumerate((-250, -215, -180)): lamp(f"B{i}", x, -3.2, 0.2 + i * 0.5)                # the valley lamps behind die first
for i, x in enumerate((-140, -100, -60, -20)): lamp(f"V{i}", x, -3.2, h_x(x) + 0.4)
for i, x in enumerate((40, 100)):                                                                # leg 1 lamps (uphill side)
    p = PTS[1].lerp(PTS[2], (x + 10) / 160); lamp(f"G{i}", x, p.y + 2.6, 30.4 + i * 0.5, z=p.z)
lamp("SW1", 152, 25.4, 999, z=PTS[2].z)                                                         # switch one
lamp("SW2", 8, 43.4, 40.9, z=PTS[3].z)                                                          # switch two: it eats it
for i, x in enumerate((60, 115)):
    p = PTS[3].lerp(PTS[4], (x - 10) / 160); lamp(f"K{i}", x, p.y + 2.6, 999, z=p.z)            # leg 3 lamps lead up
for i in range(5): lamp(f"St{i}", 236 + i * 10.0, 69.6, 999, 80, z=54.0)
# High Gate on the top: houses with lit windows, the platform, an old stone gate
houseM = newM("S_HouseM", (0.2, 0.2, 0.22), rough=1); roofM = newM("S_Roof", (0.25, 0.12, 0.09), rough=1)
winM = newM("S_Win", (1, 0.62, 0.25), emit=5)
for i in range(22):
    x = rr.uniform(200, 330); y = rr.uniform(78, 120); w = rr.uniform(3, 6); h = rr.uniform(2.5, 5); z0 = gh(x, y)
    mk("S_House", box(), houseM, (x, y, z0 + h / 2 - 0.5), scl=(w, w, h)); mk("S_Roof", box(), roofM, (x, y, z0 + h - 0.4), scl=(w + 0.4, w + 0.4, 0.3))
    mk("S_Win", box(), winM, (x, y - (w / 2 + 0.02), z0 + h * 0.45), scl=(0.6, 0.05, 0.7))
mk("S_Platform", box(), newM("S_Plat", (0.1, 0.09, 0.1), rough=1), (256, 69.4, 54.3), scl=(44, 2.2, 0.6))
gateM = newM("S_GateM", (0.16, 0.15, 0.15), rough=1)
for gy in (61.5, 70.5): mk("S_Gate", box(), gateM, (205, gy, 58), scl=(2.0, 2.0, 8))
mk("S_Gate", box(), gateM, (205, 66, 62.5), scl=(2.4, 11, 1.4))
# black pines in the valley and on the top
pineM = newM("S_Pine", (0.02, 0.035, 0.03), rough=1); trunkM = newM("S_Trunk", (0.04, 0.03, 0.02), rough=1)
pines = []
for i in range(170):
    x = rr.uniform(-440, 120); y = rr.choice((rr.uniform(-110, -9), rr.uniform(-110, -9), rr.uniform(-110, -9), rr.uniform(-60, -9)))
    if abs(y) < 9: continue
    pines.append((x, y, rr.uniform(6, 13)))
for i in range(40): pines.append((rr.uniform(150, 420), rr.uniform(80, 200), rr.uniform(6, 11)))
bm = bmesh.new(); bt = bmesh.new()
for x, y, h in pines:
    z = gh(x, y)
    g = bmesh.ops.create_cone(bm, cap_ends=True, segments=7, radius1=h * 0.28, radius2=0.0, depth=h)["verts"]; bmesh.ops.translate(bm, vec=(x, y, z + h * 0.5 + 0.8), verts=g)
    g = bmesh.ops.create_cone(bt, cap_ends=True, segments=5, radius1=0.25, radius2=0.2, depth=1.6)["verts"]; bmesh.ops.translate(bt, vec=(x, y, z + 0.6), verts=g)
mk("S_Pines", bm, pineM); mk("S_Trunks", bt, trunkM)
# loose stones that roll down the face when it slides
ROCKS = []
for i in range(10):
    ROCKS.append(mk(f"S_Stone{i}", sph(rr.uniform(0.5, 1.1), 8, 6), rockM, (0, 0, -50)))
# far mountains behind Iron Mountain
farM = newM("S_FarPeak", (0.1, 0.11, 0.15), rough=1)
for i in range(9):
    mk("S_FarPeak", cyl(1, 0.05, 1, 8), farM, (-420 + i * 110, rr.uniform(330, 380), 40), scl=(rr.uniform(70, 95), 55, rr.uniform(60, 90)))
# the moon in the south-west lights the face
EL = math.radians(20.0); AZ = math.radians(35)
moonM = newM("S_Moon", (0.9, 0.9, 0.85), emit=4)
mk("S_Moon", cyl(24, 24, 0.2, 48), moonM, (-800 * math.cos(AZ), -800 * math.sin(AZ), 800 * math.tan(EL)), (math.pi / 2, 0, math.pi / 2 + AZ))
w = sc.world; w.node_tree.nodes["Background"].inputs[0].default_value = (0.014, 0.018, 0.045, 1)
MK = O["MoonKey"]; MK.data.energy = 3.2; MK.data.color = (0.75, 0.82, 1.0); MK.rotation_euler = (0, EL - math.pi / 2, AZ)
try: MK.data.use_shadow = True; MK.data.angle = math.radians(0.6)
except Exception: pass
FIREM = newM("T_FireM", (1, 0.35, 0.08), emit=12)
mk("T_Fire", box(), FIREM, (2.45, 0, 0.55), scl=(0.06, 0.5, 0.3), parent=T)
FIRE = light("T_FireGlow", "POINT", 25, (1, 0.45, 0.15), (2.2, 0, 0.7), T)
SANDM = newM("T_SandM", (0.6, 0.5, 0.35), emit=0.6, rough=1)
SAND = []
for sd in (-1, 1):
    SAND.append(mk(f"T_Sand{sd}", cyl(0.02, 0.18, 0.5, 8), SANDM, (4.3, sd * 0.53, 0.25), parent=T))

# ---------------- the Hush ----------------
H = O["Hush"]; H.scale = (2.4, 2.4, 2.4)
mask_spot = light("T_MaskLight", "SPOT", 9000, (0.7, 0.85, 1.0), (0, 0, 0)); mask_spot.data.spot_size = math.radians(18)
c = mask_spot.constraints.new("TRACK_TO"); c.target = O["H_Mask"]; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
mask_spot.parent = H; mask_spot.location = (2.0, -14, 4.0)

# ---------------- animation ----------------
TK = [(0, 130), (4, 168), (8, 208), (12, 250), (16, 292), (18, 312), (22, 356), (26, 410), (28, 448), (29.4, 467), (30.2, CUM[2]), (31.4, CUM[2]),
      (32.4, CUM[2] + 5), (40.4, CUM[3] - 8), (41.6, CUM[3]), (56.0, CUM[3]), (60.0, CUM[3] + 6.5), (60.4, CUM[3] + 6.5), (62.4, CUM[3] + 2.0),
      (63.6, CUM[3] + 2.0), (64.6, CUM[3] + 5.0), (66.0, CUM[3] + 16), (76.0, CUM[4]), (78, CUM[4] + 24), (82, CUM[4] + 60), (85, CUM[4] + 80),
      (86.6, CUM[4] + 84), (100, CUM[4] + 84)]
def s_at(t):
    for (ta, sa), (tb, sb) in zip(TK, TK[1:]):
        if ta <= t <= tb:
            u = (t - ta) / (tb - ta) if tb > ta else 0; return sa + (sb - sa) * u
    return TK[-1][1]
prev_yaw = None
for f in list(range(1, END + 1, 2)) + [END]:
    p, d = path(s_at((f - 1) / FPS)); yaw = math.atan2(d.y, d.x); pitch = -math.atan2(d.z, math.hypot(d.x, d.y))
    if prev_yaw is not None:
        while yaw - prev_yaw > math.pi: yaw -= 2 * math.pi
        while yaw - prev_yaw < -math.pi: yaw += 2 * math.pi
    prev_yaw = yaw
    key(T, "location", f, Vector(p)); key(T, "rotation_euler", f, Vector((0, pitch, yaw)))
lin(T)
for hm, lt, td in RLAMP:
    if td > 150: continue
    s = hm.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for t, e in ((0, 8), (td - 0.01, 8), (td + 0.15, 0)): s.default_value = e; s.keyframe_insert("default_value", frame=F(max(t, 0)))
    e0 = lt.data.energy
    for t, e in ((0, e0), (td - 0.01, e0), (td + 0.15, 0)): lt.data.energy = e; lt.data.keyframe_insert("energy", frame=F(max(t, 0)))
for t, x, y, dz in HP_:
    key(H, "location", F(t), Vector((x, y, gh(x, y) + dz))); key(H, "scale", F(t), Vector((2.4, 2.4, 2.4)))
d1 = H.constraints.new("LOCKED_TRACK"); d1.target = T; d1.track_axis = "TRACK_NEGATIVE_Y"; d1.lock_axis = "LOCK_Z"
# stones roll down when it slides (31.4-34, 54-56, 67-72)
for i, R_ in enumerate(ROCKS):
    t0 = (31.6, 54.2, 67.2)[i % 3] + rr.uniform(0, 1.2); x0 = {0: 31, 1: 21, 2: 40}[i % 3] + rr.uniform(-8, 8)
    y0 = {0: 17, 1: 22, 2: 26}[i % 3] + rr.uniform(-2, 3); y1 = rr.uniform(-6, 0)
    key(R_, "location", 1, Vector((x0, y0, -50))); key(R_, "location", F(t0) - 1, Vector((x0, y0, -50)))
    for k in range(6):
        u = k / 5; y = y0 + (y1 - y0) * u; key(R_, "location", F(t0 + 2.4 * u), Vector((x0 + u * 3, y, gh(x0 + u * 3, y) + 0.6)))
    key(R_, "rotation_euler", F(t0), 0.0, 0); key(R_, "rotation_euler", F(t0 + 2.4), -12.0, 0)
    lin(R_)
gm = M("H_Green").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 0), (2.6, 0), (4.0, 60), (40.6, 60), (41.0, 140), (42.6, 70), (64.0, 70), (64.6, 120), (66, 60), (100, 60)):
    gm.default_value = e; gm.keyframe_insert("default_value", frame=F(t))
# our lights: put out by Rook at 41.4 ("Lights out. Stop here."), lit again at 63.8 ("Sand on the rails! Full steam!")
L0, L1 = 41.4, 63.8
se = M("H_Signal").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 80), (L0, 80), (L0 + 0.6, 3), (L1 - 0.2, 3), (L1 + 0.4, 60), (100, 50)): se.default_value = e; se.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 6), (L0, 6), (L0 + 0.6, 0.3), (L1 - 0.2, 0.3), (L1 + 0.4, 4)): SIGL.data.energy = e; SIGL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 900), (L0, 900), (L0 + 0.4, 0), (L1, 0), (L1 + 0.3, 900)): HL.data.energy = e; HL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 45), (L0, 45), (L0 + 0.6, 16), (L1 - 0.2, 16), (L1 + 0.6, 45)): O["Fill"].data.energy = e; O["Fill"].data.keyframe_insert("energy", frame=F(t))
wi = M("H_Window").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 4), (L0, 4), (L0 + 0.5, 0.0), (L1, 0.0), (L1 + 0.3, 4)): wi.default_value = e; wi.keyframe_insert("default_value", frame=F(t))
fe = FIREM.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 12), (L0, 12), (L0 + 1.0, 1.0), (L1 - 0.2, 1.0), (L1 + 0.2, 20), (100, 14)): fe.default_value = e; fe.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 25), (L0, 25), (L0 + 1.0, 2), (L1 - 0.2, 2), (L1 + 0.2, 40), (100, 30)): FIRE.data.energy = e; FIRE.data.keyframe_insert("energy", frame=F(t))
for sm in SAND:                                                    # sand pours on the rails at 63.6
    for t, sz in ((0, 0.0), (63.4, 0.0), (63.7, 1.0), (66.5, 1.0), (67.0, 0.0)): key(sm, "scale", F(t), Vector((sz, sz, sz)))
# Rook head (rz = local direction + 30: 30 ahead, 120 left / uphill, -150 back, -60 right / downhill)
for t, rz_ in ((0, -150), (2.8, -150), (3.2, 30), (5.6, 30), (6.0, -150), (8.4, -150), (8.8, 30), (19.4, 30), (19.8, -150), (23.6, -150),
               (24.0, 30), (30.6, 30), (31.0, -60), (34.4, -60), (34.8, -150), (36.2, -150), (36.6, -60), (39.6, -60), (40.0, -150), (41.0, -150),
               (41.4, -70), (55.0, -70), (55.4, 30), (60.0, 30), (60.4, -150), (63.0, -150), (63.4, 30), (68.6, 30), (69.0, -60), (74.8, -60),
               (75.2, 30), (88.8, 30), (89.4, -95), (100, -95)):
    key(HP, "rotation_euler", F(t), math.radians(rz_), 2)
WUP = [(0.6, 1.3), (5.8, 1.2), (11.2, 1.3), (16.0, 1.2), (27.8, 1.3), (31.4, 1.2), (36.6, 0.9), (60.4, 1.4), (63.4, 1.5), (72.4, 1.3), (81.4, 1.2)]
for sd in (-1, 1):
    wg = O[f"R_Wing{sd}"]; ks = [(0, 0)]
    for t, a in WUP: ks += [(t, 0), (t + 0.3, a), (t + 1.9, a), (t + 2.3, 0)]
    ks += [(41.2, 0), (41.6, -0.6), (55.2, -0.6), (55.6, 0)]
    for t, a in sorted(ks): key(wg, "rotation_euler", F(t), math.radians(sd * 12) + sd * a * 0.6, 1)
for f in range(1, END, 12):
    if F(41.4) <= f <= F(63.8) or f >= F(86.6): continue
    key(R, "location", f, 0.62 + (0.02 if (f // 12) % 2 else 0.0), 2)

# ---------------- cameras (one per shot, bound to markers) ----------------
def cam(name, start_s, loc, look, lens=28, parent=None, world_look=False):
    if parent is None: loc = (loc[0], loc[1], max(loc[2], gh(loc[0], loc[1]) + 2.0))
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_end = 2000
    c = bpy.data.objects.new(name, cd); sc.collection.objects.link(c); c.location = loc
    if parent: c.parent = parent
    if isinstance(look, str): tgt = O[look]
    else:
        tgt = bpy.data.objects.new(name + "_T", None); sc.collection.objects.link(tgt); tgt.location = look; tgt.name = "Cam_T_" + name
        if parent and not world_look: tgt.parent = parent
    k = c.constraints.new("TRACK_TO"); k.target = tgt; k.track_axis = "TRACK_NEGATIVE_Z"; k.up_axis = "UP_Y"
    m = sc.timeline_markers.new(name, frame=F(start_s)); m.camera = c; return c
cam("Cam_01", 0, (2.6, -3.2, 1.8), (0.0, 0, 1.3), 28, T)                          # Rook: the valley lamps went dark
cam("Cam_02", 2.6, (6, 2.2, 3.4), "H_Mask", 55, T)                                 # over the train, back: its face rises in the valley
cam("Cam_03", 5.6, (-130, -95, 32), (-235, 0, 8), 22)                             # high wide: the pine valley, the train, it behind
cam("Cam_04", 11.0, (14, -5, 1.4), (0, 0, 1.6), 30, T)                            # front: Rook, Iron Mountain ahead
cam("Cam_05", 15.0, (70, -150, 34), (75, 34, 26), 24)                             # wide: the steep face and its old zigzag line
cam("Cam_06", 19.6, (-4, -3.0, 2.8), "H_Mask", 28, T)                              # from the train: it comes down the valley
cam("Cam_07", 24.0, (118, -14, 10), (74, 12, 8), 26)                                # above leg 1: the train climbs the first leg
cam("Cam_08", 27.6, (2.4, -2.6, 3.0), (0.6, 0, 1.45), 30, T)                      # Rook: switch one, now backwards
cam("Cam_09", 30.6, (95, -45, 18), (32, 12, 14), 30)                              # side: it climbs straight up and slides
cam("Cam_10", 33.8, (75, 62, 0), (60, 25, 18), 24)                                # from the top: the train reversing up leg 2, it at the foot
cam("Cam_11", 36.4, (-2, 2.5, 3.0), "H_Mask", 30, T)                               # over Rook: it climbs again, higher
cam("Cam_12", 40.8, (2.6, -2.2, 1.6), (0.5, 0, 1.3), 30, T)                       # Rook: lights out, stop here
cam("Cam_13", 44.6, (0.9, 2.6, 1.3), "H_Mask", 24, T)                            # low beside Rook: its face right beside us (cold open)
cam("Cam_14", 49.4, (2, 52, 47), (18, 22, 33), 26)                              # side: the dark train on the ledge, it searching below
cam("Cam_15", 52.6, (-5, 1.5, 2.4), "H_Mask", 24, T)                               # behind the train: its face beside us
cam("Cam_16", 55.2, (-40, 10, 0), (18, 28, 26), 28)                               # wide: the stones give, it slides a little
cam("Cam_17", 58.6, (4.2, -2.4, 0.45), (2.0, 0, 0.3), 24, T)                      # low: the wheels slip on the wet rails
cam("Cam_18", 61.0, (2.4, -2.6, 3.0), (0.6, 0, 1.45), 28, T)                      # Rook: slipping back, sand on the rails
cam("Cam_19", 65.2, (6, -9, 4.5), (0, 0, 1), 28, T)                               # side: full steam up leg 3, it climbing below
cam("Cam_20", 68.6, (70, 72, 0), (42, 10, 8), 30)                                 # from the top: it slides all the way down
cam("Cam_21", 72.2, (-4, -3.0, 3.2), "H_Mask", 45, T)                              # back: it small at the foot
cam("Cam_22", 76.2, (-20, -14, 8), (30, 0, 2), 24, T)                             # High Gate ahead through the old stone gate
cam("Cam_23", 81.0, (2.4, -3.2, 1.7), (0.6, 0, 1.35), 28, T)                      # Rook at the station
cam("Cam_24", 87.4, (262, 58, 0), (46, -2, 12), 40)                               # from the top: the lit station, it at the foot looking up
sc.camera = O["Cam_01"]
sc.render.resolution_x = 1280; sc.render.resolution_y = 720; sc.render.resolution_percentage = 100
sc.eevee.taa_render_samples = 24
try: sc.eevee.use_raytracing = False
except Exception: pass
sc.render.use_compositing = False; sc.render.use_sequencer = False
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "hush_film18.blend"))
print("film18 built", len(sc.collection.all_objects), "objects; markers", len(sc.timeline_markers), "path", [round(c) for c in CUM])
