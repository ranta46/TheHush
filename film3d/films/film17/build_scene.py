# GLOAMRUN 3D Film 20 "The Sea Road" — run INSIDE Blender (hush_lookdev.blend open, scene HUSH).
# Story (no calm start): the coast lamps die behind us and its face rises over the dunes at once -> it is faster on the sand ->
# Rook's move: he takes the old sea road over the tidal flats to Isle Town just as the tide comes in ("We cross before the sea
# closes it") -> it follows us onto the sea road -> the low road: the rails are under water, we must go slow, it gains, it eats
# our lamp and the fire ('...Don't look back. Keep rolling.') -> surprise: a big wave rolls over the road between us and it;
# the sea closes the road behind us -> fire lit, up the hill onto the island; it wades after us into the deep water and stops,
# the sea at its chest. Isle Town. It stands out in the sea, waiting for low tide (it will be back).
import bpy, bmesh, math, random, os
from mathutils import Vector
OUT = r"C:\Users\81803\TremenFilm\hush\film17"; os.makedirs(OUT, exist_ok=True)
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






# ---------------- world: the coast and dunes, the old sea road over the tidal flats, the low road, Isle Town ----------------
from mathutils import Matrix
rr = random.Random(2020)
X0 = -240.0                                    # the line runs straight east along y = 0 (x -240 .. 600)
def ss(a, b, v):
    u = min(1.0, max(0.0, (v - a) / (b - a))); return u * u * (3 - 2 * u)
def rz(x):                                     # rail height: coast +3, down onto the sea road (0), the low road (-1), up onto the island (+3)
    z = 3.0 - 3.0 * ss(20, 60, x)
    z -= 1.0 * ss(180, 200, x) * (1 - ss(240, 260, x))
    z += 3.0 * ss(400, 440, x); return z
def slope(x): return (rz(x + 1.0) - rz(x - 1.0)) / 2.0
def gh(x, y):
    n = 0.9 * math.sin(x * 0.045 + y * 0.03) + 0.6 * math.sin(x * 0.09 - y * 0.06 + 1.3)
    d = abs(y)
    land = 2.98 + ss(12, 45, d) * (2.5 + 1.6 * n) + 20.0 * math.exp(-((x + 320.0) / 35.0) ** 2) + ss(150, 260, y) * 10
    flats = -3.2 + 0.25 * n
    island = 2.98 + ss(30, 70, d) * (1.0 + 0.8 * n) + 15.0 * math.exp(-(((x - 515) / 45.0) ** 2 + ((y - 72) / 28.0) ** 2))
    kl = 1 - ss(10, 70, x); ki = ss(392, 438, x) * (1 - ss(610, 660, x)) * (1 - ss(70, 105, d))
    z = flats + (land - flats) * kl
    return z + (island - z) * ki - (0.02 if d < 3 else 0)
def pose(x): return (x, 0.0, rz(x))
GA = O["Ground"]; GA.location = (0, 0, -40.0); GA.scale = (1400, 1000, 1)
sandM = newM("S_WetSand", (0.085, 0.08, 0.075), rough=0.35); grassM = newM("S_Dune", (0.07, 0.08, 0.06), rough=1)
rockM = newM("S_RockM", (0.08, 0.08, 0.09), rough=1)
GA.data.materials.clear(); GA.data.materials.append(rockM)
def axis(a, b, step):
    out = []; v = a
    while v <= b: out.append(v); v += step
    return out
xs = axis(-440, -346, 6) + axis(-340, -202, 3.0) + axis(-198, 700, 4.0) + axis(706, 900, 8)
ys = axis(-300, -132, 8) + axis(-126, 126, 4.0) + axis(132, 300, 8)
bm = bmesh.new(); vv = [[bm.verts.new((x, y, gh(x, y))) for y in ys] for x in xs]
for i in range(len(xs) - 1):
    for j in range(len(ys) - 1):
        f = bm.faces.new((vv[i][j], vv[i + 1][j], vv[i + 1][j + 1], vv[i][j + 1]))
        if vv[i][j].co.z > 2.0: f.material_index = 1
GO = mk("S_Ground", bm, sandM, smooth=True); GO.data.materials.append(grassM)
# the sea road: a stone causeway over the flats (top follows the rails)
stoneM = newM("S_Stone", (0.11, 0.1, 0.1), rough=0.9)
bm = bmesh.new(); prev = None
for x in axis(16, 444, 2.0):
    t = rz(x) - 0.06
    row = [bm.verts.new((x, -6.0, -3.6)), bm.verts.new((x, -2.4, t)), bm.verts.new((x, 2.4, t)), bm.verts.new((x, 6.0, -3.6))]
    if prev:
        for k in range(3): bm.faces.new((prev[k], row[k], row[k + 1], prev[k + 1]))
    prev = row
mk("S_Causeway", bm, stoneM)
railM = newM("S_RailM", (0.2, 0.2, 0.22), rough=0.4, metal=0.8); tie = newM("S_Tie", (0.05, 0.04, 0.035), rough=1)
postM = newM("S_Post", (0.02, 0.02, 0.025), rough=0.5)
def pboxes(name, mat, items, parent=None):
    bm = bmesh.new()
    for loc, scl, rzz in items:
        g = bmesh.ops.create_cube(bm, size=1.0)["verts"]; bmesh.ops.scale(bm, vec=scl, verts=g)
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(rzz, 3, "Z"), verts=g); bmesh.ops.translate(bm, vec=loc, verts=g)
    return mk(name, bm, mat, parent=parent)
rails, ties = [], []
for i in range(int((600 - X0) / 2)):
    x = X0 + i * 2 + 1; z = rz(x)
    for yy in (-0.53, 0.53): rails.append(((x, yy, z + 0.03), (2.06, 0.08, 0.06), 0.0))
    ties.append(((x, 0, z + 0.01), (0.25, 1.4, 0.06), 0.0))
pboxes("S_Rails", railM, rails); pboxes("S_Ties", tie, ties)
pboxes("S_EndStop", newM("S_Red", (0.6, 0.05, 0.03), rough=0.5), [((X0 + 2, 0, 3.45), (0.3, 1.8, 0.5), 0), ((598, 0, 3.45), (0.3, 1.8, 0.5), 0)])
# old tide poles along the sea road (they show how high the sea is)
poles = []
for x in axis(70, 390, 20):
    poles.append(((x, -7.5, 0.4), (0.22, 0.22, 8.0), 0))
    for k in range(4): poles.append(((x, -7.5, -2.0 + k * 1.5), (0.5, 0.06, 0.08), 0))
pboxes("S_TidePoles", newM("S_PoleW", (0.32, 0.3, 0.27), rough=0.8), poles)
# lamps: the coast lamps (die as it passes), the sea road lamps (the near ones die when it eats our light), Isle Town
RLAMP = []
def lamp(tag, x, y, td, e=55, z=None):
    z = rz(x) if z is None else z; mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, y, z + 1.7))
    hm = newM(f"L_{tag}", (1, 0.62, 0.25), emit=8); mk(f"L_{tag}", sph(0.2, 12, 8), hm, (x, y, z + 3.45))
    lo = light(f"L_{tag}L", "POINT", e, (1, 0.6, 0.3), (x, y, z + 3.2)); RLAMP.append((hm, lo, td)); return hm, lo
HP_ = [(0, -300, 25, -40), (2.4, -300, 25, -40), (3.4, -300, 25, -14), (4.6, -300, 25, 0), (5.4, -296, 22, 0), (6, -288, 18, 0),
       (11, -215, 6, 0), (16, -150, 0, 0), (22, -75, 0, 0), (28, 0, 0, 0), (34, 70, 0, 0), (40, 125, 0, 0), (44, 158, 0, 0),
       (50, 186, 0, 0), (55, 205, 0, 0), (56.6, 210, 0, 0), (57.4, 210, 0, 0), (58.4, 207, 0, 0), (64.4, 207, 0, 0),
       (66, 212, 0, -1), (70, 226, 0, -5), (74, 238, 3, -10), (77, 244, 5, -13), (100, 245, 5, -13)]
def h_time(x):
    for (ta, xa, *_), (tb, xb, *_) in zip(HP_[4:], HP_[5:]):
        if xa <= x <= xb and xb > xa: return ta + (tb - ta) * (x - xa) / (xb - xa)
    return 999.0
def hz(x, y): return rz(x) if abs(y) < 8 and x > -150 else max(gh(x, y), rz(x) if abs(y) < 3 else -99)
for i, x in enumerate((-225, -205, -185, -165)): lamp(f"B{i}", x, -3.2, 0.2 + i * 0.5)          # the coast lamps behind die first
for i, x in enumerate((-130, -100, -70, -40, -10, 20)): lamp(f"V{i}", x, -3.2, h_time(x) + 0.4)
for i, x in enumerate((70, 110, 150)): lamp(f"C{i}", x, -2.1, h_time(x) + 0.4)                 # sea road lamps it passes
for i, x in enumerate((190, 230)): lamp(f"N{i}", x, -2.1, 44.7 + i * 0.35)                      # the near ones: eaten with our lamp
for i, x in enumerate((270, 310, 350, 390)): lamp(f"F{i}", x, -2.1, 999)                        # the far ones lead to the island
for i, x in enumerate((450, 480, 510)): lamp(f"E{i}", x, -3.2, 999)
for i in range(5): lamp(f"St{i}", 545 + i * 9.0, 3.4, 999, 80)
# Isle Town: houses with lit windows, the lighthouse on the hill, the platform
houseM = newM("S_HouseM", (0.2, 0.2, 0.22), rough=1); roofM = newM("S_Roof", (0.25, 0.12, 0.09), rough=1)
winM = newM("S_Win", (1, 0.62, 0.25), emit=5)
for i in range(26):
    x = rr.uniform(470, 600); y = rr.choice((rr.uniform(12, 48), rr.uniform(-48, -12))); w = rr.uniform(3, 6); h = rr.uniform(2.5, 5)
    z0 = gh(x, y); sd = 1 if y > 0 else -1
    mk("S_House", box(), houseM, (x, y, z0 + h / 2 - 0.5), scl=(w, w, h)); mk("S_Roof", box(), roofM, (x, y, z0 + h - 0.4), scl=(w + 0.4, w + 0.4, 0.3))
    mk("S_Win", box(), winM, (x, y - sd * (w / 2 + 0.02), z0 + h * 0.45), scl=(0.6, 0.05, 0.7))
LZ = gh(515, 72)
mk("S_Lighthouse", cyl(2.2, 1.5, 16, 16), newM("S_LHW", (0.6, 0.58, 0.55), rough=0.8), (515, 72, LZ + 8))
mk("S_LHTop", cyl(1.9, 1.9, 0.6, 16), roofM, (515, 72, LZ + 18.3))
lhM = newM("L_LHLamp", (1, 0.75, 0.4), emit=10); mk("L_LHLamp", sph(1.2, 16, 10), lhM, (515, 72, LZ + 17.0))
light("L_LHLight", "POINT", 600, (1, 0.7, 0.4), (515, 72, LZ + 17.0))
mk("S_Platform", box(), newM("S_Plat", (0.1, 0.09, 0.1), rough=1), (562, 2.4, 3.0), scl=(40, 2.2, 0.6))
# far hills along the north coast (behind the dunes)
farM = newM("S_FarPeak", (0.1, 0.11, 0.15), rough=1)
for i in range(8):
    hx = -420 + i * 95
    mk("S_FarPeak", cyl(1, 0.05, 1, 8), farM, (hx, rr.uniform(300, 340), 10), scl=(rr.uniform(55, 75), 45, rr.uniform(30, 50)))
# the sea: rises all film (the tide comes in); a big wave rolls over the low road between us and it (55-59.5)
seaM = newM("S_SeaM", (0.012, 0.03, 0.06), rough=0.07, metal=0.35)
SEA = mk("S_Sea", box(), seaM, (300, 0, -2.6), scl=(1600, 1400, 0.1))
waveM = newM("S_WaveM", (0.08, 0.14, 0.2), emit=0.15, rough=0.2, metal=0.2)
WAVE = mk("S_Wave", sph(1.0, 32, 12), waveM, (214, -140, -10), scl=(30, 8.0, 9.0), smooth=True)
foamM = newM("S_FoamM", (0.55, 0.62, 0.68), emit=0.5, rough=0.6)
mk("S_Foam", sph(1.0, 32, 8), foamM, (0, 0.35, 0.72), scl=(0.9, 0.35, 0.3), parent=WAVE, smooth=True)
# the big low moon in the west (behind the Hush): it lights the sea
EL = math.radians(14.0)
moonM = newM("S_Moon", (0.9, 0.9, 0.85), emit=4)
mk("S_Moon", cyl(26, 26, 0.2, 48), moonM, (-760, -40, 760 * math.tan(EL)), (math.pi / 2, 0, math.pi / 2))
w = sc.world; w.node_tree.nodes["Background"].inputs[0].default_value = (0.014, 0.018, 0.045, 1)
MK = O["MoonKey"]; MK.data.energy = 3.2; MK.data.color = (0.75, 0.82, 1.0); MK.rotation_euler = (0, EL - math.pi / 2, 0)
try: MK.data.use_shadow = True; MK.data.angle = math.radians(0.6)
except Exception: pass
FIREM = newM("T_FireM", (1, 0.35, 0.08), emit=12)
mk("T_Fire", box(), FIREM, (2.45, 0, 0.55), scl=(0.06, 0.5, 0.3), parent=T)
FIRE = light("T_FireGlow", "POINT", 25, (1, 0.45, 0.15), (2.2, 0, 0.7), T)

# ---------------- the Hush ----------------
H = O["Hush"]; H.scale = (2.4, 2.4, 2.4)
mask_spot = light("T_MaskLight", "SPOT", 9000, (0.7, 0.85, 1.0), (0, 0, 0)); mask_spot.data.spot_size = math.radians(18)
c = mask_spot.constraints.new("TRACK_TO"); c.target = O["H_Mask"]; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
mask_spot.parent = H; mask_spot.location = (2.0, -14, 4.0)

# ---------------- animation ----------------
TK = [(0, -150), (4, -104), (8, -58), (12, -12), (16, 32), (20, 76), (24, 118), (28, 152), (32, 178), (34, 190), (36, 200), (40, 214),
      (44, 224), (48, 232), (52, 240), (55, 246), (58, 262), (60, 286), (62, 316), (65, 370), (68, 420), (72, 462), (76, 494),
      (80, 520), (84, 540), (87, 552), (89, 556), (100, 556)]
def x_at(t):
    for (ta, sa), (tb, sb) in zip(TK, TK[1:]):
        if ta <= t <= tb:
            u = (t - ta) / (tb - ta) if tb > ta else 0; return sa + (sb - sa) * u
    return TK[-1][1]
for f in list(range(1, END + 1, 4)) + [END]:
    x, y, z = pose(x_at((f - 1) / FPS)); key(T, "location", f, Vector((x, y, z))); key(T, "rotation_euler", f, -math.atan(slope(x)), 1)
lin(T)
SLK = [(0, -2.6), (16, -2.2), (26, -1.6), (33, -1.0), (36, -0.9), (44, -0.86), (55, -0.8), (57, -0.6), (59, -0.4), (62, -0.25), (65, 0.1), (68, 0.8),
       (72, 1.4), (78, 1.9), (84, 2.0), (100, 2.05)]
for t, z in SLK: key(SEA, "location", F(t), z, 2)
lin(SEA)
for t, y, z in ((0, -140, -10), (54.4, -140, -10), (55.4, -80, -2.0), (57.0, -10, -1.2), (58.2, 30, -1.0), (59.6, 90, -2.0), (60.6, 140, -10)):
    key(WAVE, "location", F(t), Vector((214, y, z)))
for hm, lt, td in RLAMP:
    if td > 150: continue
    s = hm.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for t, e in ((0, 8), (td - 0.01, 8), (td + 0.15, 0)): s.default_value = e; s.keyframe_insert("default_value", frame=F(max(t, 0)))
    e0 = lt.data.energy
    for t, e in ((0, e0), (td - 0.01, e0), (td + 0.15, 0)): lt.data.energy = e; lt.data.keyframe_insert("energy", frame=F(max(t, 0)))
for t, (x, y, dz) in [(p[0], p[1:]) for p in HP_]:
    key(H, "location", F(t), Vector((x, y, hz(x, y) + dz))); key(H, "scale", F(t), Vector((2.4, 2.4, 2.4)))
d1 = H.constraints.new("LOCKED_TRACK"); d1.target = T; d1.track_axis = "TRACK_NEGATIVE_Y"; d1.lock_axis = "LOCK_Z"
gm = M("H_Green").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 0), (2.6, 0), (4.0, 60), (44.4, 60), (44.8, 140), (46.4, 70), (66, 70), (66.6, 120), (68, 60), (100, 60)):
    gm.default_value = e; gm.keyframe_insert("default_value", frame=F(t))
# our lights: eaten at 44.6 ("Our lamp! It's eating the light!"), lit again at 64.6 ("Light the fire! Up the hill!")
L0, L1 = 44.6, 64.6
se = M("H_Signal").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 80), (L0, 80), (L0 + 0.3, 20), (L0 + 0.45, 60), (L0 + 0.9, 3), (L1 - 0.2, 3), (L1 + 0.4, 60), (100, 50)): se.default_value = e; se.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 6), (L0, 6), (L0 + 0.9, 0.3), (L1 - 0.2, 0.3), (L1 + 0.4, 4)): SIGL.data.energy = e; SIGL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 900), (L0, 900), (L0 + 0.15, 200), (L0 + 0.3, 700), (L0 + 0.6, 0), (L1, 0), (L1 + 0.3, 900)): HL.data.energy = e; HL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 45), (L0, 45), (L0 + 0.6, 16), (L1 - 0.2, 16), (L1 + 0.6, 45)): O["Fill"].data.energy = e; O["Fill"].data.keyframe_insert("energy", frame=F(t))
wi = M("H_Window").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 4), (L0 + 0.1, 4), (L0 + 0.5, 0.0), (L1, 0.0), (L1 + 0.3, 4)): wi.default_value = e; wi.keyframe_insert("default_value", frame=F(t))
fe = FIREM.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 12), (L0 + 0.2, 12), (L0 + 1.2, 1.5), (L1 - 0.2, 1.5), (L1 + 0.2, 20), (100, 14)): fe.default_value = e; fe.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 25), (L0 + 0.2, 25), (L0 + 1.2, 3), (L1 - 0.2, 3), (L1 + 0.2, 40), (100, 30)): FIRE.data.energy = e; FIRE.data.keyframe_insert("energy", frame=F(t))
# Rook head (rz = local direction + 30: 30 ahead, 120 left / north, -150 back, -60 right / south = the open sea)
for t, rz_ in ((0, -150), (2.8, -150), (3.2, 30), (5.6, 30), (6.0, -150), (8.4, -150), (8.8, 30), (21.6, 30), (22.0, -150), (25.0, -150),
               (25.4, 30), (30.0, 30), (30.4, -150), (33.2, -150), (33.6, 30), (44.2, 30), (44.6, -150), (47.4, -150), (47.8, 30),
               (55.4, 30), (55.8, -60), (58.0, -60), (58.4, -150), (63.6, -150), (64.0, 30), (72.0, 30), (72.4, -150), (79.0, -150), (79.4, 30), (100, 30)):
    key(HP, "rotation_euler", F(t), math.radians(rz_), 2)
for sd in (-1, 1):
    wg = O[f"R_Wing{sd}"]
    for t, a in ((0, 0), (0.6, 0), (0.9, 1.3), (1.3, 0.4), (1.7, 1.3), (2.6, 0), (5.8, 0), (6.1, 1.2), (8.0, 1.2), (8.4, 0),
                 (11.2, 0), (11.5, 1.3), (13.6, 1.3), (14.0, 0), (16.4, 0), (16.7, 1.0), (18.8, 1.0), (19.2, 0), (30.4, 0), (30.7, 1.2), (32.6, 1.2), (33.0, 0),
                 (34.4, 0), (34.7, 1.0), (36.8, 1.0), (37.2, 0), (44.4, 0), (44.7, 1.4), (46.6, 1.4), (47.0, -0.6), (55.8, -0.6), (56.1, 1.5), (58.0, 1.5),
                 (58.4, -0.3), (64.8, -0.3), (65.1, 1.4), (67.2, 1.4), (67.6, 0), (76.4, 0), (76.7, 1.3), (78.6, 1.3), (79.0, 0),
                 (86.6, 0), (86.9, 1.0), (88.8, 1.0), (89.2, 0)):
        key(wg, "rotation_euler", F(t), math.radians(sd * 12) + sd * a * 0.6, 1)
for f in range(1, END, 12):
    if F(44.6) <= f <= F(64.6) or f >= F(89.0): continue
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
cam("Cam_01", 0, (2.6, -3.2, 1.8), (0.0, 0, 1.3), 28, T)                          # Rook: the coast lamps are dying behind us
cam("Cam_02", 2.6, (6, 2.2, 3.4), "H_Mask", 60, T)                                 # over the train, back: its face rises over the dunes
cam("Cam_03", 5.6, (-50, -110, 40), (-160, 0, 6), 22)                             # high wide: the coast, the train, the Hush behind, the sea
cam("Cam_04", 11.0, (14, -5, 1.4), (0, 0, 1.6), 30, T)                            # front: Rook, the sea road ahead
cam("Cam_05", 16.0, (0, -60, 26), (110, 0, -1), 22)                              # high: the long sea road over the flats to the island
cam("Cam_06", 21.6, (-4, 3.0, 2.8), "H_Mask", 28, T)                               # from the train: it comes down to the shore
cam("Cam_07", 26.0, (178, -24, -0.6), (132, 0, 1.0), 24)                          # low on the flats: the train on the sea road
cam("Cam_08", 30.0, (300, 30, 10), (60, 0, 8), 35)                                # from the island side: it walks onto the sea road
cam("Cam_09", 34.0, (2.4, -2.6, 3.0), (0.6, 0, 1.45), 30, T)                      # Rook: the low road, the rails under water
cam("Cam_10", 37.2, (6, -4, 0.35), (2, 0, 0.2), 24, T)                            # low: the wheels in the sea
cam("Cam_11", 39.2, (-3, -1.5, 2.8), (8, 0, 1), 26, T)                            # behind Rook: slow now
cam("Cam_12", 41.8, (232, -80, 40), (195, 0, 0), 26)                              # high: the dark sea, the train small, it close behind
cam("Cam_13", 44.4, (2.6, -2.2, 1.6), (0.5, 0, 1.3), 30, T)                       # Rook: our lamp dies
cam("Cam_14", 47.2, (252, 1.4, -0.35), "H_Mask", 20)                              # low in front of the train: it towers behind us
cam("Cam_15", 49.6, (2.6, -2.2, 0.75), (-4.0, 0.4, 3.6), 18, T)                   # low beside Rook: its face right over us (cold open)
cam("Cam_16", 53.6, (228, -40, 0.6), (225, 0, 7), 26)                             # side low on the water: it right behind us
cam("Cam_17", 55.6, (262, -95, 14), (222, -10, 2), 30)                            # wide: the big wave rolls over the low road
cam("Cam_18", 58.4, (2.0, 1.6, 2.2), "H_Mask", 26, T)                              # behind Rook: the road is gone behind us
cam("Cam_19", 62.4, (240, -120, 45), (275, 0, 0), 24)                             # high: the sea over the road, it standing in it
cam("Cam_20", 64.4, (2.4, -2.6, 3.0), (0.6, 0, 1.45), 28, T)                      # Rook: light the fire
cam("Cam_21", 67.6, (6, 8, 9), (0, 0, 1), 28, T)                                  # side: full steam up onto the island
cam("Cam_22", 71.6, (-4, 3.0, 3.2), "H_Mask", 60, T)                               # back: it wades after us
cam("Cam_23", 75.6, (445, -30, 9), (244, 5, 7), 85)                               # from the island: it stopped in the deep water
cam("Cam_24", 80.0, (-20, -14, 8), (30, 0, 2), 24, T)                             # Isle Town ahead
cam("Cam_25", 85.6, (2.4, -3.2, 1.7), (0.6, 0, 1.35), 28, T)                      # Rook at the station
cam("Cam_26", 91.6, (578, -6, 5.5), (250, 5, 6), 55)                               # the lit island, the sea, it waits out there
sc.camera = O["Cam_01"]
sc.render.resolution_x = 1280; sc.render.resolution_y = 720; sc.render.resolution_percentage = 100
sc.eevee.taa_render_samples = 24
try: sc.eevee.use_raytracing = False
except Exception: pass
sc.render.use_compositing = False; sc.render.use_sequencer = False
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "hush_film17.blend"))
print("film17 built", len(sc.collection.all_objects), "objects; markers", len(sc.timeline_markers))
