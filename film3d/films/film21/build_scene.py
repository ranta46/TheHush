# GLOAMRUN 3D Film 26 "The Spiral" — run INSIDE Blender (hush_lookdev.blend open, scene HUSH).
# Story (no calm start): the valley lamps die and its face rises behind us -> by 8 s it is right at the last car (Rook flinches) -> full steam
# -> Rook's move: he runs the dark train into the low door of the old spiral tunnel in Grey Mountain ("It goes round and up inside") -> it is
# too big, it bends down and stares into the door -> the train creeps out of the top door onto the ledge right above its head ("It watches the
# door. We leave by the top.") ('...Don't move.') -> surprise: a wheel knocks a stone off the ledge, it falls and clacks in front of its face,
# it looks up -> 'Lights on! Full steam!' up the ledge to the pass and Copper Town. It stands far behind (it will be back).
import bpy, bmesh, math, random, os
from mathutils import Vector
OUT = r"C:\Users\81803\TremenFilm\hush\film21"; os.makedirs(OUT, exist_ok=True)
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




# ---------------- world: the valley, Grey Mountain's cliff with the old spiral tunnel (low door + top door on the ledge), the pass, Copper Town ----------------
from mathutils import Matrix
rr = random.Random(2626)
def ss(a, b, v):
    if b < a: return 1.0 - ss(b, a, v)
    u = min(1.0, max(0.0, (v - a) / (b - a))); return u * u * (3 - 2 * u)
ZL = 12.0                       # the ledge / the pass height
UX = 56.5                       # the upper line runs north along x = UX
def gh(x, y):
    n = 0.9 * math.sin(x * 0.05 + y * 0.03) + 0.6 * math.sin(x * 0.11 - y * 0.07 + 1.3)
    ay = abs(y)
    hills = 7.0 * ss(25, 110, ay) * (0.55 + 0.45 * math.sin(x * 0.012 + 0.8))
    flat = 1.0 - (1 - ss(16, 30, ay)) * ss(-400, -380, x)
    zv = (0.45 * n + hills) * flat
    p = ss(20, 40, y) * ss(30, 52, x)                                   # the high pass north of the cliff
    z = zv * (1 - p) + ZL * p
    z = max(z, 42.0 * ss(80, 125, x) * (0.8 + 0.2 * math.sin(y * 0.02)))  # the mountain behind
    if ay < 2.6 and x < 53: z = min(z, -0.06)
    if abs(x - UX) < 2.6 and y > 38: z = min(z, ZL - 0.06)
    return z
GA = O["Ground"]; GA.location = (0, 0, -30.0); GA.scale = (1400, 1000, 1)
grassM = newM("S_Grass", (0.035, 0.05, 0.035), rough=1)
GA.data.materials.clear(); GA.data.materials.append(grassM)
def axis(a, b, step):
    out = []; v = a
    while v <= b + 1e-6: out.append(v); v += step
    return out
xs = axis(-460, -42, 8) + axis(-40, 140, 2.5) + axis(144, 400, 4) + axis(406, 640, 8)
ys = axis(-300, -62, 8) + axis(-60, -8, 2.5) + axis(-7.5, 7.5, 0.5) + axis(8, 60, 2.5) + axis(64, 340, 4) + axis(346, 420, 8)
bm = bmesh.new(); vv = [[bm.verts.new((x, y, gh(x, y))) for y in ys] for x in xs]
for i in range(len(xs) - 1):
    for j in range(len(ys) - 1):
        bm.faces.new((vv[i][j], vv[i + 1][j], vv[i + 1][j + 1], vv[i][j + 1]))
GO = mk("S_Ground", bm, grassM, smooth=True)
railM = newM("S_RailM", (0.2, 0.2, 0.22), rough=0.4, metal=0.8); tie = newM("S_Tie", (0.05, 0.04, 0.035), rough=1)
postM = newM("S_Post", (0.02, 0.02, 0.025), rough=0.5)
def pboxes(name, mat, items, parent=None):
    bm = bmesh.new()
    for loc, scl, rzz in items:
        g = bmesh.ops.create_cube(bm, size=1.0)["verts"]; bmesh.ops.scale(bm, vec=scl, verts=g)
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(rzz, 3, "Z"), verts=g); bmesh.ops.translate(bm, vec=loc, verts=g)
    return mk(name, bm, mat, parent=parent)
def B(x0, x1, y0, y1, z0, z1):
    return (((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - y0, z1 - z0), 0)
# lower line (west -> the low door), upper line (top door -> north over the ledge and the pass)
X0, X1 = -330.0, 79.0
pboxes("S_Rails", railM, [(((X0 + X1) / 2, sd * 0.53, 0.03), (X1 - X0, 0.08, 0.06), 0) for sd in (-1, 1)])
pboxes("S_Ties", tie, [((x, 0, -0.02), (0.25, 1.4, 0.06), 0) for x in axis(X0, X1, 2.0)])
Y0, Y1 = -40.0, 300.0
pboxes("S_RailsU", railM, [((UX + sd * 0.53, (Y0 + Y1) / 2, ZL + 0.03), (0.08, Y1 - Y0, 0.06), 0) for sd in (-1, 1)])
pboxes("S_TiesU", tie, [((UX, y, ZL - 0.02), (1.4, 0.25, 0.06), 0) for y in axis(Y0, Y1, 2.0)])
pboxes("S_EndStop", newM("S_Red", (0.6, 0.05, 0.03), rough=0.5), [((X0 + 2, 0, 0.4), (0.3, 1.8, 0.5), 0), ((UX, Y1, ZL + 0.4), (1.8, 0.3, 0.5), 0)])
# ---- Grey Mountain's cliff: rock blocks; low door x 53..80 (y +-2.6, 6.5 high); the ledge top at ZL (x 53..60); top door in the shoulder at y = -24 ----
rockM = newM("S_Rock", (0.05, 0.047, 0.045), rough=1)
_nt = rockM.node_tree; _nz = _nt.nodes.new("ShaderNodeTexNoise"); _nz.inputs["Scale"].default_value = 0.12; _nz.inputs["Detail"].default_value = 6
_cr = _nt.nodes.new("ShaderNodeValToRGB"); _cr.color_ramp.elements[0].color = (0.022, 0.021, 0.022, 1); _cr.color_ramp.elements[1].color = (0.075, 0.068, 0.06, 1)
_bp = _nt.nodes.new("ShaderNodeBump"); _bp.inputs["Strength"].default_value = 0.6
_pb = _nt.nodes["Principled BSDF"]; _nt.links.new(_nz.outputs["Fac"], _cr.inputs["Fac"]); _nt.links.new(_cr.outputs["Color"], _pb.inputs["Base Color"])
_nt.links.new(_nz.outputs["Fac"], _bp.inputs["Height"]); _nt.links.new(_bp.outputs["Normal"], _pb.inputs["Normal"]); darkM = newM("S_TunnelDark", (0.0, 0.0, 0.0), rough=1)
stoneM = newM("S_PortalStone", (0.2, 0.19, 0.17), rough=0.9)
pboxes("S_Cliff", rockM, [
    B(53, 80, -260, -2.6, -1, ZL), B(53, 80, 2.6, 42, -1, ZL), B(53, 80, -2.6, 2.6, 6.5, ZL),          # below the ledge, the low door's roof
    B(60, 82, -24, 42, ZL, 30),                                          # the wall above the ledge
    B(53, 54.2, -260, -24, ZL, 30), B(58.8, 82, -260, -24, ZL, 30), B(54.2, 58.8, -260, -24, ZL + 4.5, 30),  # the shoulder round the top door
    B(54.2, 58.8, -260, -41, ZL, ZL + 4.5)])
pboxes("S_TunnelEnds", darkM, [B(78, 79.9, -2.6, 2.6, -1, 6.5), B(54.2, 58.8, -41, -40, ZL, ZL + 4.5),
                               B(53.2, 80, -2.6, -2.5, -0.1, 6.5), B(53.2, 80, 2.5, 2.6, -0.1, 6.5), B(53.2, 80, -2.6, 2.6, 6.4, 6.5),
                               B(54.2, 54.3, -40, -24.2, ZL, ZL + 4.5), B(58.7, 58.8, -40, -24.2, ZL, ZL + 4.5), B(54.2, 58.8, -40, -24.2, ZL + 4.4, ZL + 4.5)])
pboxes("S_Portals", stoneM, [B(52.6, 53.3, -3.3, -2.6, -0.2, 7.2), B(52.6, 53.3, 2.6, 3.3, -0.2, 7.2), B(52.6, 53.3, -3.3, 3.3, 6.5, 7.3),
                             B(53.5, 54.2, -24.6, -23.6, ZL, ZL + 5.2), B(58.8, 59.5, -24.6, -23.6, ZL, ZL + 5.2), B(53.5, 59.5, -24.6, -23.6, ZL + 4.5, ZL + 5.3)])
pboxes("S_LedgeKerb", stoneM, [B(53.0, 53.4, -23.6, 42, ZL, ZL + 0.35)])
STONE = mk("S_Stone", sph(0.22, 8, 6), stoneM, (54.6, -1.2, ZL + 0.2))
RLAMP = []
def lamp(tag, x, y, td, e=55, z=None):
    z = gh(x, y) if z is None else z; mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, y, z + 1.7))
    hm = newM(f"L_{tag}", (1, 0.62, 0.25), emit=8); mk(f"L_{tag}", sph(0.2, 12, 8), hm, (x, y, z + 3.45))
    lo = light(f"L_{tag}L", "POINT", e, (1, 0.6, 0.3), (x, y, z + 3.2)); RLAMP.append((hm, lo, td)); return hm, lo
# the Hush: (t, x, y, dz) ; z = ground + dz   (dz < 0 = it bends down into its smoke to stare into the low door)
HP_ = [(0, -268, -6, -40), (2.4, -268, -6, -40), (3.4, -268, -6, -16), (4.4, -266, -6, 0), (8.0, -185, -3, 0), (9.4, -167, -3, 0),
       (14, -112, -5, 0), (19, -52, -6, 0), (22.6, -14, -5, 0), (26, 14, -4, 0), (29, 30, -3, 0), (31.0, 38, -2, -3), (33, 42, -2, -10),
       (35, 43, -2, -15), (56.2, 43, -2, -15), (57.6, 43, -2, -13), (58.6, 42.5, -2, -6), (60, 42, -1, 0), (64, 42, 14, 0),
       (70, 40, 55, 0), (76, 42, 110, 0), (80, 44, 145, 0), (84, 46, 165, 0), (86, 46, 170, 0), (100, 46, 170, 0)]
def h_x(x):
    for (ta, xa, *_), (tb, xb, *_) in zip(HP_[3:11], HP_[4:11]):
        if xa <= x <= xb and xb > xa: return ta + (tb - ta) * (x - xa) / (xb - xa)
    return 999.0
for i, x in enumerate((-300, -285, -270)): lamp(f"B{i}", x, -3.2, 0.2 + i * 0.5)               # the valley lamps behind die first
for i, x in enumerate((-140, -100, -60, -20)): lamp(f"V{i}", x, -3.2, h_x(x) + 0.4)
lamp("D0", 49.5, -4.0, 29.4, 70)                                                                  # the lamp at the low door: it eats it
for i, y in enumerate((120, 180)): lamp(f"K{i}", UX - 3.0, y, 999, 55, ZL)
for i in range(5): lamp(f"St{i}", UX - 3.2, 222 + i * 9.0, 999, 80, ZL)
LEDGEMOON = light("S_LedgeMoon", "AREA", 30, (0.55, 0.65, 1.0), (50, -8, 26))
LEDGEMOON.data.shape = "RECTANGLE"; LEDGEMOON.data.size = 30; LEDGEMOON.data.size_y = 60; LEDGEMOON.rotation_euler = (0, math.radians(-25), 0)
# Copper Town on the pass
houseM = newM("S_HouseM", (0.2, 0.2, 0.22), rough=1); roofM = newM("S_Roof", (0.25, 0.12, 0.09), rough=1)
winM = newM("S_Win", (1, 0.62, 0.25), emit=5)
for i in range(30):
    x = rr.choice((rr.uniform(30, 49), rr.uniform(63, 78))); y = rr.uniform(205, 320); w = rr.uniform(3, 6); h = rr.uniform(2.5, 5); z0 = gh(x, y)
    mk("S_House", box(), houseM, (x, y, z0 + h / 2 - 0.5), scl=(w, w, h)); mk("S_Roof", box(), roofM, (x, y, z0 + h - 0.4), scl=(w + 0.4, w + 0.4, 0.3))
    mk("S_Win", box(), winM, (x + (w / 2 + 0.02) * (1 if x < UX else -1), y, z0 + h * 0.45), scl=(0.05, 0.6, 0.7))
mk("S_Platform", box(), newM("S_Plat", (0.1, 0.09, 0.1), rough=1), (UX - 1.9, 240, ZL + 0.3), scl=(1.6, 44, 0.6))
# black pines in the valley and on the pass
pineM = newM("S_Pine", (0.02, 0.035, 0.03), rough=1); trunkM = newM("S_Trunk", (0.04, 0.03, 0.02), rough=1)
pines = []
for i in range(320):
    x = rr.uniform(-460, 300); y = rr.uniform(-200, 330)
    if abs(y) < 22 and x < 53: continue                    # the lower line and the space before the door
    if x > 26 and y < 48: continue                         # the cliff and the slope under it
    if abs(x - UX) < 10 and y > 30: continue               # the upper line
    if 25 < x < 82 and 195 < y < 330: continue             # Copper Town
    if x > 80: continue
    pines.append((x, y, rr.uniform(6, 12)))
bm = bmesh.new(); bt = bmesh.new()
for x, y, h in pines:
    z = gh(x, y)
    g = bmesh.ops.create_cone(bm, cap_ends=True, segments=7, radius1=h * 0.28, radius2=0.0, depth=h)["verts"]; bmesh.ops.translate(bm, vec=(x, y, z + h * 0.5 + 0.8), verts=g)
    g = bmesh.ops.create_cone(bt, cap_ends=True, segments=5, radius1=0.25, radius2=0.2, depth=1.6)["verts"]; bmesh.ops.translate(bt, vec=(x, y, z + 0.6), verts=g)
mk("S_Pines", bm, pineM); mk("S_Trunks", bt, trunkM)
farM = newM("S_FarPeak", (0.1, 0.11, 0.15), rough=1)
for i in range(9):
    mk("S_FarPeak", cyl(1, 0.05, 1, 8), farM, (rr.uniform(220, 380), -420 + i * 120, 30), scl=(55, rr.uniform(70, 95), rr.uniform(60, 85)))
# the moon in the south-west
EL = math.radians(24.0); AZ = math.radians(35)
moonM = newM("S_Moon", (0.9, 0.9, 0.85), emit=4)
mk("S_Moon", cyl(24, 24, 0.2, 48), moonM, (-800 * math.cos(AZ), -800 * math.sin(AZ), 800 * math.tan(EL)), (math.pi / 2, 0, math.pi / 2 + AZ))
w = sc.world; w.node_tree.nodes["Background"].inputs[0].default_value = (0.016, 0.02, 0.05, 1)
MK = O["MoonKey"]; MK.data.energy = 3.4; MK.data.color = (0.75, 0.82, 1.0); MK.rotation_euler = (0, EL - math.pi / 2, AZ)
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
TK = [(0, -262), (4.6, -212), (8, -172), (9.6, -152), (14, -90), (19, -15), (21, 30), (22.6, 52), (24, 64), (24.6, 68), (100, 68)]
TU = [(33, -36), (38, -27), (44, -18), (50, -9), (55.6, -2), (57.6, 1), (59.6, 2), (60.4, 4), (62, 10), (64, 24), (66, 42), (70, 90),
      (76, 160), (80, 205), (83, 230), (84.6, 238), (100, 238)]
TJ = 33.0                                                         # the jump inside the mountain (unseen): low door -> top door
def ip(K, t):
    for (ta, sa), (tb, sb) in zip(K, K[1:]):
        if ta <= t <= tb:
            u = (t - ta) / (tb - ta) if tb > ta else 0; return sa + (sb - sa) * u
    return K[-1][1] if t > K[0][0] else K[0][1]
def tpos(t):
    return Vector((ip(TK, t), 0, 0)) if t < TJ else Vector((UX, ip(TU, t), ZL))
HT = empty("V_HushLook")
for f in range(1, END + 1):
    t = (f - 1) / FPS; p = tpos(t)
    key(T, "location", f, p)
    key(HT, "location", f, Vector((75, 0, 3)) if 23.0 < t < 57.8 else p)
FJ = F(TJ)
key(T, "rotation_euler", 1, Vector((0, 0, 0))); key(T, "rotation_euler", FJ - 1, Vector((0, 0, 0))); key(T, "rotation_euler", FJ, Vector((0, 0, math.pi / 2)))
lin(T); lin(HT)
for hm, lt, td in RLAMP:
    if td > 150: continue
    s = hm.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for t, e in ((0, 8), (td - 0.01, 8), (td + 0.15, 0)): s.default_value = e; s.keyframe_insert("default_value", frame=F(max(t, 0)))
    e0 = lt.data.energy
    for t, e in ((0, e0), (td - 0.01, e0), (td + 0.15, 0)): lt.data.energy = e; lt.data.keyframe_insert("energy", frame=F(max(t, 0)))
for t, x, y, dz in HP_:
    key(H, "location", F(t), Vector((x, y, gh(x, y) + dz))); key(H, "scale", F(t), Vector((2.4, 2.4, 2.4)))
d1 = H.constraints.new("LOCKED_TRACK"); d1.target = HT; d1.track_axis = "TRACK_NEGATIVE_Y"; d1.lock_axis = "LOCK_Z"
gm = M("H_Green").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 0), (2.6, 0), (4.0, 60), (7.4, 60), (8.0, 140), (9.6, 70), (31.6, 70), (32.4, 140), (36, 80), (57.6, 80), (58.2, 140), (60.4, 70), (100, 60)):
    gm.default_value = e; gm.keyframe_insert("default_value", frame=F(t))
# the stone: a wheel knocks it off the ledge (56.0), it bounces off the door's stone roof and clacks on the rails in front of its face (57.3)
for t, loc in ((0, (54.6, -1.2, ZL + 0.2)), (55.9, (54.6, -1.2, ZL + 0.2)), (56.3, (53.4, -1.3, ZL + 0.45)), (56.6, (52.7, -1.4, ZL - 1.0)),
               (56.95, (52.3, -1.5, 7.4)), (57.3, (51.6, -1.2, 0.25)), (57.5, (51.1, -1.0, 0.4)), (57.7, (50.7, -0.9, 0.2)), (100, (50.7, -0.9, 0.2))):
    key(STONE, "location", F(t), Vector(loc))
for t, r in ((0, 0), (55.9, 0), (57.7, 9.0)): key(STONE, "rotation_euler", F(t), r, 1)
# our lights: put out by Rook at 23.2 ("Lights out."), lit again at 59.8 ("Lights on! Full steam!")
L0, L1 = 23.2, 59.8
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
# Rook head (rz = local direction + 30: 30 ahead, 120 left, -150 back, -60 right). On the ledge (heading north) the Hush is down on the left.
for t, rz_ in ((0, -150), (3.0, -150), (3.4, 30), (5.0, 30), (5.4, -150), (9.8, -150), (10.2, 30), (22.8, 30), (23.2, -150), (32.8, -150),
               (33.0, 120), (59.2, 120), (59.6, 30), (68.0, 30), (68.4, -150), (73.6, -150), (74.0, 30), (87.6, 30), (88.2, -150), (100, -150)):
    key(HP, "rotation_euler", F(t), math.radians(rz_), 2)
WUP = [(0.6, 1.3), (10.4, 1.2), (16.6, 1.3), (23.2, 1.0), (57.8, 1.4), (59.8, 1.5), (69.0, 1.2), (76.4, 1.3)]
for sd in (-1, 1):
    wg = O[f"R_Wing{sd}"]; ks = [(0, 0)]
    for t, a in WUP: ks += [(t, 0), (t + 0.3, a), (t + 1.9, a), (t + 2.3, 0)]
    ks += [(7.9, 0), (8.05, 1.7), (9.4, 1.6), (9.8, 0)]                          # flinch: it's at the last car
    ks += [(25.7, 0), (26.1, -0.6), (57.3, -0.6), (57.7, 0)]                     # small and still in the dark
    for t, a in sorted(ks): key(wg, "rotation_euler", F(t), math.radians(sd * 12) + sd * a * 0.6, 1)
for f in range(1, END, 12):
    if F(7.6) <= f <= F(8.8) or F(23.0) <= f <= F(59.8) or f >= F(84.6): continue
    key(R, "location", f, 0.62 + (0.02 if (f // 12) % 2 else 0.0), 2)
for t, z in ((7.6, 0.62), (8.05, 0.76), (8.4, 0.6), (8.8, 0.62)): key(R, "location", F(t), z, 2)

# ---------------- cameras (one per shot, bound to markers) ----------------
def cam(name, start_s, loc, look, lens=28, parent=None, world_look=False, free=False):
    if parent is None and not free: loc = (loc[0], loc[1], max(loc[2], gh(loc[0], loc[1]) + 2.0))
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_end = 2000; cd.clip_start = 0.05
    c = bpy.data.objects.new(name, cd); sc.collection.objects.link(c); c.location = loc
    if parent: c.parent = parent
    if isinstance(look, str): tgt = O[look]
    else:
        tgt = bpy.data.objects.new(name + "_T", None); sc.collection.objects.link(tgt); tgt.location = look; tgt.name = "Cam_T_" + name
        if parent and not world_look: tgt.parent = parent
    k = c.constraints.new("TRACK_TO"); k.target = tgt; k.track_axis = "TRACK_NEGATIVE_Z"; k.up_axis = "UP_Y"
    m = sc.timeline_markers.new(name, frame=F(start_s)); m.camera = c; return c
cam("Cam_01", 0, (2.6, -3.2, 1.8), (0.0, 0, 1.3), 28, T)                          # Rook: the valley lamps went dark
cam("Cam_02", 2.6, (6, 2.2, 3.4), "H_Mask", 55, T)                                 # over the train, back: its face rises
cam("Cam_03", 5.0, (-8, -34, 3), (-12, 0, 10), 18, T)                             # side wide: it catches up, right behind the last car
cam("Cam_03b", 7.8, (3.0, -1.5, 0.8), (-4, 0, 7), 16, T)                          # low on Rook: it is at the last car (flinch)
cam("Cam_04", 10.2, (-95, -45, 16), (-125, 0, 4), 24)                            # high wide: full steam, it behind
cam("Cam_05", 14.0, (-40, -24, 6), (-85, 0, 8), 24)                               # it walks after us, the lamps die
cam("Cam_06", 16.4, (-3, -2.2, 2.6), (14, 0, 3.0), 30, T)                         # over Rook: the cliff and the low door ahead
cam("Cam_07", 19.4, (28, -18, 4), (54, 0, 5), 24)                                 # the train runs into the low door under the ledge
cam("Cam_08", 22.6, (2.4, -1.7, 1.5), (0.6, 0, 1.3), 26, T)                       # inside: Rook, lights out
cam("Cam_09", 27.0, (50, -22, 3), (34, -3, 17), 22, None, free=True)                                  # outside: it comes to the door, eats the lamp, bends down
cam("Cam_10", 31.6, (66, 1.0, 1.4), "H_Mask", 24, None, free=True)                # inside the low door, out: its face fills the door
cam("Cam_11", 36.0, (47, -9, 14.5), (56.5, -24, 13.2), 26, None, free=True)        # the top door: the dark train creeps out, it below
cam("Cam_12", 40.4, (26, 22, 26), (50, -8, 9), 24, None, free=True)               # high: the dark train on the ledge right above it
cam("Cam_13", 44.4, (49.5, -26, 15.5), (50, -6, 9), 20, None, free=True)          # low by its face, up: the train above (cold open)
cam("Cam_14", 48.4, (2.2, 2.4, 1.2), (0.6, 0, 1.3), 26, T)                        # Rook in the dark, looking down at it
cam("Cam_15", 51.4, (34, -30, 22), (52, -4, 10), 26, None, free=True)                                # wide from below: almost past it
cam("Cam_16", 55.6, (52.4, -6.5, 13.2), (54.2, -1.2, 12.1), 22, None, free=True)  # on the ledge edge: the wheel knocks the stone off
cam("Cam_17", 56.6, (62, 1.4, 1.0), "H_Mask", 22, None, free=True)                # inside the low door: the stone clacks in front of its face, it looks up
cam("Cam_18", 58.6, (2.6, -1.7, 1.4), (0.6, 0, 1.35), 24, T)                      # Rook: lights on, full steam
cam("Cam_19", 60.6, (52.5, 34, 14.5), (56, -4, 14), 24, None, free=True)          # up the ledge, back: the train comes, it rises behind
cam("Cam_20", 64.6, (0, 34, 30), (48, 38, 12), 26, None, free=True)               # high: we run onto the pass, it climbs after
cam("Cam_21", 68.6, (6, -3.0, 3.5), (0, 0, 1.5), 24, T)                           # side: keep the fire hot
cam("Cam_22", 72.6, (64, 150, 16), (54, 90, 22), 22, None, free=True)             # the pass: the train passes, it far behind
cam("Cam_23", 76.2, (-3, -2.2, 2.6), (14, 0, 2.0), 26, T)                         # over Rook: Copper Town ahead
cam("Cam_24", 80.6, (2.4, -3.2, 1.7), (0.6, 0, 1.35), 28, T)                      # Rook at the station
cam("Cam_25", 85.4, (68, 276, 18), (50, 190, 26), 26, None, free=True)            # the lit station, it far behind on the pass
sc.camera = O["Cam_01"]
sc.render.resolution_x = 1280; sc.render.resolution_y = 720; sc.render.resolution_percentage = 100
sc.eevee.taa_render_samples = 24
try: sc.eevee.use_raytracing = False
except Exception: pass
sc.render.use_compositing = False; sc.render.use_sequencer = False
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "hush_film21.blend"))
print("film21 built", len(sc.collection.all_objects), "objects; markers", len(sc.timeline_markers))
