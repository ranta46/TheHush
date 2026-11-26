# GLOAMRUN 3D Film 28 "The Fog Sea" — run INSIDE Blender (hush_lookdev.blend open, scene HUSH).
# Story (no calm start): the moor lamps die and its face rises behind us -> by 8 s it is right at the last car (Rook flinches) -> full steam
# -> it is faster on the moor; ahead the valley is full of white fog (the fog sea) -> Rook's move: lights out, fire low, and the dark train
# goes down UNDER the fog; the Hush stops at the edge and sees only white ('It sees only fog.') -> it wades in, comes right beside the stopped
# train and bends down, its mask just over the fog ('...Don't move.') -> surprise: the fog rises over its face; it is lost in the white ->
# the dark train creeps out the far side -> 'Lights on! Full steam!' to Mist Town. It stands far behind (it will be back).
import bpy, bmesh, math, random, os
from mathutils import Vector
OUT = r"C:\Users\81803\TremenFilm\hush\film23"; os.makedirs(OUT, exist_ok=True)
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
# ---------------- world: the high moor, the valley full of fog (the fog sea), Mist Town ----------------
from mathutils import Matrix
rr = random.Random(2828)
def ss(a, b, v):
    if b < a: return 1.0 - ss(b, a, v)
    u = min(1.0, max(0.0, (v - a) / (b - a))); return u * u * (3 - 2 * u)
FX0, FX1 = 6.0, 100.0                                                          # the fog sea along the line
def gh(x, y):
    n = 0.9 * math.sin(x * 0.05 + y * 0.03) + 0.6 * math.sin(x * 0.11 - y * 0.07 + 1.3)
    ay = abs(y)
    z = 0.45 * n * ss(4, 16, ay) + 5.0 * ss(40, 150, ay) * (0.55 + 0.45 * math.sin(x * 0.012 + 0.8))
    wall = 34.0 * ss(70, 150, ay) * ss(FX0 - 30, FX0 + 10, x) * ss(FX1 + 40, FX1 - 5, x)     # the steep valley sides
    z = max(z, wall * (0.85 + 0.15 * math.sin(x * 0.05 + y * 0.02)))
    z = max(z, 30.0 * ss(240, 330, ay) * (0.8 + 0.2 * math.sin(x * 0.02)))
    if ay < 2.6: z = min(z, -0.06)
    return z
GA = O["Ground"]; GA.location = (0, 0, -30.0); GA.scale = (1400, 1000, 1)
grassM = newM("S_Moor", (0.045, 0.05, 0.035), rough=1)
GA.data.materials.clear(); GA.data.materials.append(grassM)
def axis(a, b, step):
    out = []; v = a
    while v <= b + 1e-6: out.append(v); v += step
    return out
xs = axis(-460, -42, 8) + axis(-40, 160, 2.5) + axis(164, 520, 4) + axis(528, 700, 8)
ys = axis(-340, -62, 6) + axis(-60, -8, 2.5) + axis(-7.5, 7.5, 0.5) + axis(8, 60, 2.5) + axis(66, 340, 6)
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
X0, X1 = -330.0, 398.0
pboxes("S_Rails", railM, [(((X0 + X1) / 2, sd * 0.53, 0.03), (X1 - X0, 0.08, 0.06), 0) for sd in (-1, 1)])
pboxes("S_Ties", tie, [((x, 0, -0.02), (0.25, 1.4, 0.06), 0) for x in axis(X0, X1, 2.0)])
pboxes("S_EndStop", newM("S_Red", (0.6, 0.05, 0.03), rough=0.5), [((X0 + 2, 0, 0.4), (0.3, 1.8, 0.5), 0), ((X1 - 1, 0, 0.4), (0.3, 1.8, 0.5), 0)])
# stone walls on the moor
stoneM = newM("S_StoneM", (0.15, 0.15, 0.14), rough=0.95)
items = []
for k in range(26):
    x0 = rr.uniform(-430, 0); y0 = rr.choice((-1, 1)) * rr.uniform(14, 120); a = rr.uniform(0, 3.14); L = rr.uniform(20, 50)
    items.append(((x0, y0, gh(x0, y0) + 0.4), (L, 0.6, 1.0), a))
pboxes("S_Walls", stoneM, items)
# dark pines in the valley: their tips stand out of the fog
pineM = newM("S_Pine", (0.02, 0.04, 0.03), rough=1)
bm = bmesh.new()
for i in range(70):
    x = rr.uniform(FX0 + 4, FX1 - 4); y = rr.choice((-1, 1)) * rr.uniform(16, 75); hh = rr.uniform(6, 11); z0 = gh(x, y)
    g = bmesh.ops.create_cone(bm, cap_ends=True, segments=7, radius1=rr.uniform(1.6, 2.4), radius2=0.05, depth=hh)["verts"]
    bmesh.ops.translate(bm, vec=(x, y, z0 + hh / 2), verts=g)
mk("S_Pines", bm, pineM)
RLAMP = []
def lamp(tag, x, y, td, e=55, z=None):
    z = gh(x, y) if z is None else z; mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, y, z + 1.7))
    hm = newM(f"L_{tag}", (1, 0.62, 0.25), emit=8); mk(f"L_{tag}", sph(0.2, 12, 8), hm, (x, y, z + 3.45))
    lo = light(f"L_{tag}L", "POINT", e, (1, 0.6, 0.3), (x, y, z + 3.2)); RLAMP.append((hm, lo, td)); return hm, lo
# the Hush: (t, x, y, dz) ; z = ground + dz   (dz -17 = bent down low in the fog, mask just over it)
HP_ = [(0, -268, -6, -40), (2.4, -268, -6, -40), (3.4, -268, -6, -16), (4.4, -266, -6, 0), (8.0, -185, -3, 0), (9.4, -167, -3, 0),
       (14, -112, -5, 0), (19, -45, -6, 0), (22.4, -22, -7, 0), (25.5, -7, -8, 0), (30.0, -3, -10, 0), (34.0, 2, -12, 0),
       (37.4, 18, -13, 0), (41.6, 40, -12, 0), (44.4, 55, -9, 0), (45.0, 56, -8.5, 0), (46.8, 57, -8.0, -17), (57.0, 57, -8.0, -17),
       (60.0, 56, -9.0, -17), (63.2, 56, -9.0, -17), (64.8, 58, -8, 0), (66.0, 66, -8, 0), (70, 100, -7, 0),
       (76, 150, -6, 0), (80, 185, -6, 0), (84, 205, -6, 0), (86, 210, -6, 0), (100, 210, -6, 0)]
def h_x(x):
    for (ta, xa, *_), (tb, xb, *_) in zip(HP_[3:8], HP_[4:8]):
        if xa <= x <= xb and xb > xa: return ta + (tb - ta) * (x - xa) / (xb - xa)
    return 999.0
for i, x in enumerate((-300, -285, -270)): lamp(f"B{i}", x, -3.2, 0.2 + i * 0.5)               # the moor lamps behind die first
for i, x in enumerate((-140, -100, -60)): lamp(f"V{i}", x, -3.2, h_x(x) + 0.4)
for i, x in enumerate((250, 300)): lamp(f"K{i}", x, 3.2, 999, 55)
for i in range(5): lamp(f"St{i}", 345 + i * 11.0, 3.4, 999, 80)
# Mist Town
houseM = newM("S_HouseM", (0.2, 0.2, 0.22), rough=1); roofM = newM("S_Roof", (0.12, 0.14, 0.2), rough=1)
winM = newM("S_Win", (1, 0.62, 0.25), emit=5)
for i in range(34):
    x = rr.uniform(320, 450); y = rr.choice((-1, 1)) * rr.uniform(9, 55); w = rr.uniform(3, 6); h = rr.uniform(2.5, 5); z0 = gh(x, y)
    mk("S_House", box(), houseM, (x, y, z0 + h / 2 - 0.5), scl=(w, w, h)); mk("S_Roof", box(), roofM, (x, y, z0 + h - 0.4), scl=(w + 0.4, w + 0.4, 0.3))
    mk("S_Win", box(), winM, (x, y - (w / 2 + 0.02) * (1 if y > 0 else -1), z0 + h * 0.45), scl=(0.6, 0.05, 0.7))
mk("S_Platform", box(), newM("S_Plat", (0.1, 0.09, 0.1), rough=1), (370, 1.9, 0.3), scl=(60, 1.6, 0.6))
farM = newM("S_FarPeak", (0.1, 0.11, 0.15), rough=1)
for i in range(9):
    mk("S_FarPeak", cyl(1, 0.05, 1, 8), farM, (rr.uniform(600, 760), -420 + i * 110, 20), scl=(70, rr.uniform(70, 95), rr.uniform(40, 70)))
# the moon, high enough to light the fog
EL = math.radians(26.0); AZ = math.radians(35)
moonM = newM("S_Moon", (0.9, 0.9, 0.85), emit=4)
mk("S_Moon", cyl(24, 24, 0.2, 48), moonM, (-800 * math.cos(AZ), -800 * math.sin(AZ), 800 * math.tan(EL)), (math.pi / 2, 0, math.pi / 2 + AZ))
w = sc.world; BG = w.node_tree.nodes["Background"].inputs[0]; BG.default_value = (0.018, 0.022, 0.05, 1)
MK = O["MoonKey"]; MK.data.energy = 3.0; MK.data.color = (0.75, 0.82, 1.0); MK.rotation_euler = (0, EL - math.pi / 2, AZ)
try: MK.data.use_shadow = True; MK.data.angle = math.radians(0.6)
except Exception: pass
FIREM = newM("T_FireM", (1, 0.35, 0.08), emit=12)
mk("T_Fire", box(), FIREM, (2.45, 0, 0.55), scl=(0.06, 0.5, 0.3), parent=T)
FIRE = light("T_FireGlow", "POINT", 25, (1, 0.45, 0.15), (2.2, 0, 0.7), T)
# ---------------- the fog sea: soft layers (no volumetrics), they thicken and rise at 50.5-53.8 ----------------
FOGR = empty("S_FogRig", (0, 0, 0))
def fogmat(name, a, cmin):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True
    try: m.surface_render_method = "DITHERED"
    except Exception: pass
    try: m.blend_method = "HASHED"
    except Exception: pass
    nt = m.node_tree; N = nt.nodes; Lk = nt.links
    b = N.get("Principled BSDF"); b.inputs["Base Color"].default_value = (0.36, 0.4, 0.5, 1); b.inputs["Roughness"].default_value = 1
    b.inputs["Emission Color"].default_value = (0.5, 0.56, 0.72, 1); b.inputs["Emission Strength"].default_value = 0.14
    tc = N.new("ShaderNodeTexCoord"); sp = N.new("ShaderNodeSeparateXYZ"); Lk.new(tc.outputs["Generated"], sp.inputs[0])
    nz = N.new("ShaderNodeTexNoise"); nz.noise_dimensions = "4D"; nz.inputs["Scale"].default_value = 0.035; nz.inputs["Detail"].default_value = 3
    Lk.new(tc.outputs["Object"], nz.inputs["Vector"])
    nz.inputs["W"].default_value = 0.0; nz.inputs["W"].keyframe_insert("default_value", frame=1)
    nz.inputs["W"].default_value = 2.5; nz.inputs["W"].keyframe_insert("default_value", frame=END)
    cr = N.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].position = 0.36; cr.color_ramp.elements[1].position = 0.64
    Lk.new(nz.outputs["Fac"], cr.inputs[0])
    def edge(out, k):
        inv = N.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0; Lk.new(out, inv.inputs[1])
        mn = N.new("ShaderNodeMath"); mn.operation = "MINIMUM"; Lk.new(out, mn.inputs[0]); Lk.new(inv.outputs[0], mn.inputs[1])
        ml = N.new("ShaderNodeMath"); ml.operation = "MULTIPLY"; ml.use_clamp = True; ml.inputs[1].default_value = k; Lk.new(mn.outputs[0], ml.inputs[0]); return ml.outputs[0]
    ex = edge(sp.outputs[0], 9.0); ey = edge(sp.outputs[1], 4.0)
    m1 = N.new("ShaderNodeMath"); m1.operation = "MULTIPLY"; Lk.new(ex, m1.inputs[0]); Lk.new(ey, m1.inputs[1])
    mr = N.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = 0.2 * a; mr.inputs["To Max"].default_value = a
    Lk.new(cr.outputs["Color"], mr.inputs["Value"])
    m2 = N.new("ShaderNodeMath"); m2.operation = "MULTIPLY"; m2.use_clamp = True; Lk.new(m1.outputs[0], m2.inputs[0]); Lk.new(mr.outputs[0], m2.inputs[1])
    # a thin clearing around the stopped train (so the low shots can see its face); it closes when the fog rises
    dv = N.new("ShaderNodeVectorMath"); dv.operation = "DISTANCE"; Lk.new(tc.outputs["Object"], dv.inputs[0])
    dv.inputs[1].default_value = (58.0 - (FX0 + FX1) / 2, -3.0, 0.0)
    c1 = N.new("ShaderNodeMapRange"); c1.inputs["From Min"].default_value = 7; c1.inputs["From Max"].default_value = 20; Lk.new(dv.outputs["Value"], c1.inputs["Value"])
    c2 = N.new("ShaderNodeMapRange"); Lk.new(c1.outputs["Result"], c2.inputs["Value"])
    for t, v in ((0, cmin), (50.5, cmin), (53.8, 1.0), (100, 1.0)):
        c2.inputs["To Min"].default_value = v; c2.inputs["To Min"].keyframe_insert("default_value", frame=F(t))
    m3 = N.new("ShaderNodeMath"); m3.operation = "MULTIPLY"; Lk.new(m2.outputs[0], m3.inputs[0]); Lk.new(c2.outputs["Result"], m3.inputs[1])
    Lk.new(m3.outputs[0], b.inputs["Alpha"]); return m
FOGL = []
for k, (z, a, cm) in enumerate(((0.9, 0.2, 0.15), (1.9, 0.28, 0.15), (2.9, 0.42, 0.2), (3.7, 0.75, 0.5))):
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5)
    bmesh.ops.scale(bm, vec=(FX1 - FX0 + 30, 230, 1), verts=bm.verts)
    o = mk(f"S_Fog{k}", bm, fogmat(f"S_FogM{k}", a, cm), ((FX0 + FX1) / 2, 0, z), parent=FOGR)
    o.visible_shadow = False
    try: o.visible_diffuse = False; o.visible_glossy = False
    except Exception: pass
    FOGL.append(o)
for t, s in ((0, 1.0), (50.5, 1.0), (53.8, 2.8), (63.0, 2.8), (70.0, 1.0), (100, 1.0)):
    key(FOGR, "scale", F(t), 1.0, 0); key(FOGR, "scale", F(t), 1.0, 1); key(FOGR, "scale", F(t), s, 2)

# ---------------- the Hush ----------------
H = O["Hush"]; H.scale = (2.4, 2.4, 2.4)
mask_spot = light("T_MaskLight", "SPOT", 9000, (0.7, 0.85, 1.0), (0, 0, 0)); mask_spot.data.spot_size = math.radians(18)
c = mask_spot.constraints.new("TRACK_TO"); c.target = O["H_Mask"]; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
mask_spot.parent = H; mask_spot.location = (2.0, -14, 4.0)

# ---------------- animation ----------------
TK = [(0, -262), (4.6, -212), (8, -172), (9.6, -152), (14, -90), (19.6, -20), (22.4, 4), (24.4, 16), (27.0, 24), (31.0, 32),
      (35.0, 40), (39.0, 50), (41.6, 56), (42.4, 57), (55.6, 57), (56.6, 59), (59.0, 72), (62.0, 98), (62.8, 108), (64.0, 122),
      (66, 145), (70, 205), (76, 290), (80, 345), (83, 378), (84.6, 386), (100, 386)]
def ip(K, t):
    for (ta, sa), (tb, sb) in zip(K, K[1:]):
        if ta <= t <= tb:
            u = (t - ta) / (tb - ta) if tb > ta else 0; return sa + (sb - sa) * u
    return K[-1][1] if t > K[0][0] else K[0][1]
def tpos(t):
    return Vector((ip(TK, t), 0, 0))
HT = empty("V_HushLook"); hv = None
for f in range(1, END + 1):
    t = (f - 1) / FPS; p = tpos(t)
    key(T, "location", f, p)
    want = p
    if 25.5 <= t < 44.0:                                   # it sees only fog: it searches the white
        want = Vector((30 + 28 * math.sin(0.55 * t), -6 + 30 * math.cos(0.4 * t), 0))
    if 53.8 <= t < 63.2:                                   # lost in the fog
        want = Vector((57, -8, 0)) + Vector((30 * math.sin(0.7 * t), 30 * math.cos(0.7 * t), 0))
    hv = Vector(want) if hv is None else hv + (Vector(want) - hv) * 0.12
    key(HT, "location", f, hv)
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
gk = [(0, 0), (2.6, 0), (4.0, 60), (7.4, 60), (8.0, 140), (9.6, 70), (25.5, 70), (26.0, 150), (41.0, 150), (44.4, 110), (45.4, 170),
      (50.5, 170), (53.8, 90), (63.2, 90), (64.2, 140), (100, 60)]
for t, e in gk: gm.default_value = e; gm.keyframe_insert("default_value", frame=F(t))
# our lights: put out by Rook at 22.0 ("Lights out, fire low."), lit again at 62.8 ("Lights on!")
L0, L1 = 22.0, 62.8
se = M("H_Signal").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 80), (L0, 80), (L0 + 0.6, 3), (L1 - 0.2, 3), (L1 + 0.4, 60), (100, 50)): se.default_value = e; se.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 6), (L0, 6), (L0 + 0.6, 0.3), (L1 - 0.2, 0.3), (L1 + 0.4, 4)): SIGL.data.energy = e; SIGL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 900), (L0, 900), (L0 + 0.4, 0), (L1, 0), (L1 + 0.3, 900)): HL.data.energy = e; HL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 45), (L0, 45), (L0 + 0.6, 24), (L1 - 0.2, 24), (L1 + 0.6, 45)): O["Fill"].data.energy = e; O["Fill"].data.keyframe_insert("energy", frame=F(t))
wi = M("H_Window").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 4), (L0, 4), (L0 + 0.5, 0.0), (L1, 0.0), (L1 + 0.3, 4)): wi.default_value = e; wi.keyframe_insert("default_value", frame=F(t))
fe = FIREM.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 12), (L0, 12), (L0 + 1.0, 1.0), (L1 - 0.2, 1.0), (L1 + 0.2, 20), (100, 14)): fe.default_value = e; fe.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 25), (L0, 25), (L0 + 1.0, 2), (L1 - 0.2, 2), (L1 + 0.2, 40), (100, 30)): FIRE.data.energy = e; FIRE.data.keyframe_insert("energy", frame=F(t))
# Rook head (rz = local direction + 30: 30 ahead, 120 left, -150 back, -60 right). The Hush is on the right (-y).
for t, rz_ in ((0, -150), (3.0, -150), (3.4, 30), (5.0, 30), (5.4, -150), (9.8, -150), (10.2, 30), (14.2, 30), (14.6, -150), (17.0, -150),
               (17.4, 30), (27.8, 30), (28.2, -150), (37.2, -150), (37.6, -60), (55.6, -60), (56.0, 30), (68.0, 30), (68.4, -150), (73.6, -150),
               (74.0, 30), (87.6, 30), (88.2, -150), (100, -150)):
    key(HP, "rotation_euler", F(t), math.radians(rz_), 2)
WUP = [(0.6, 1.3), (10.4, 1.2), (14.6, 1.0), (17.4, 1.2), (21.8, 1.0), (62.6, 1.5), (69.0, 1.2), (76.4, 1.3)]
for sd in (-1, 1):
    wg = O[f"R_Wing{sd}"]; ks = [(0, 0)]
    for t, a in WUP: ks += [(t, 0), (t + 0.3, a), (t + 1.6, a), (t + 1.9, 0)]
    ks += [(7.9, 0), (8.05, 1.7), (9.4, 1.6), (9.8, 0)]                          # flinch: it's at the last car
    ks += [(24.2, 0), (24.6, -0.6), (61.8, -0.6), (62.2, 0)]                     # small and still in the fog
    for t, a in sorted(ks): key(wg, "rotation_euler", F(t), math.radians(sd * 12) + sd * a * 0.6, 1)
for f in range(1, END, 12):
    if F(7.6) <= f <= F(8.8) or F(24.0) <= f <= F(62.6) or f >= F(84.6): continue
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
cam("Cam_01", 0, (2.6, -3.2, 1.8), (0.0, 0, 1.3), 28, T)                          # Rook: the moor lamps went out
cam("Cam_02", 2.6, (6, 2.2, 3.4), "H_Mask", 55, T)                                 # over the train, back: its face rises
cam("Cam_03", 5.0, (-8, -34, 3), (-12, 0, 10), 18, T)                             # side wide: it catches up
cam("Cam_03b", 7.8, (3.0, -1.5, 0.8), (-4, 0, 7), 16, T)                          # low on Rook: it is at the last car (flinch)
cam("Cam_04", 10.2, (-95, -45, 16), (-125, 0, 4), 24)                            # high wide: full steam, it behind
cam("Cam_05", 14.0, (2.6, -3.0, 2.0), (-14, 0, 6), 22, T)                         # Rook looks back: it's faster
cam("Cam_06", 17.2, (-3, -2.2, 2.6), (40, 0.6, 2.0), 30, T)                       # over Rook: the valley full of fog ahead
cam("Cam_07", 19.8, (70, -70, 34), (-5, 0, 2), 24)                                # high: the fog sea, the train runs to it, it behind
cam("Cam_08", 21.6, (2.4, -1.7, 1.5), (0.6, 0, 1.3), 26, T)                       # Rook: lights out, into the fog
cam("Cam_09", 24.4, (40, -34, 12), (14, 0, 1), 22)                                # the dark train slides under the fog
cam("Cam_10", 26.8, (38, 14, 7), "H_Mask", 24, None, free=True)                   # it stands at the edge of the fog, eyes searching
cam("Cam_11", 30.8, (90, 70, 48), (20, -6, 2), 24)                                # high: a white sea, it looks for us
cam("Cam_12", 33.6, (2.4, -1.7, 1.4), (0.6, 0, 1.35), 24, T)                      # Rook under the fog, quiet
cam("Cam_13", 36.4, (40, -80, 26), (28, -12, 6), 22)                              # it wades into the fog
cam("Cam_14", 41.0, (64, 7, 1.6), "H_Mask", 22, None, free=True)                  # from the dark train: it comes beside us
cam("Cam_15", 44.4, (64, 3.5, 1.2), "H_Mask", 20, None, free=True)               # low by the train: its face comes down to the fog (cold open)
cam("Cam_16", 48.4, (2.2, 2.4, 1.2), (0.6, 0, 1.3), 26, T)                        # Rook in the dark, it right behind him
cam("Cam_17", 50.4, (70, -48, 26), (57, -8, 4), 24)                               # the fog rises over its face
cam("Cam_18", 54.2, (110, 60, 40), (60, -5, 4), 24)                               # high: only white, its eyes lost in it
cam("Cam_19", 55.6, (2.6, -1.7, 1.4), (0.6, 0, 1.35), 24, T)                      # Rook: now. go.
cam("Cam_20", 58.4, (122, -22, 5), (80, -3, 2.5), 26)                             # the dark train creeps out under the fog
cam("Cam_21", 62.2, (2.6, -1.7, 1.4), (0.6, 0, 1.35), 24, T)                      # Rook: lights on, full steam
cam("Cam_22", 64.8, (170, -36, 10), (70, -8, 14), 22)                             # we run, it stands up out of the fog behind
cam("Cam_23", 68.6, (6, -3.0, 3.5), (0, 0, 1.5), 24, T)                           # side: keep the fire hot
cam("Cam_24", 72.6, (320, -22, 10), (230, 0, 8), 22)                              # front: the train comes, it far behind
cam("Cam_25", 76.2, (-3, -2.2, 2.6), (14, 0, 2.0), 26, T)                         # over Rook: Mist Town ahead
cam("Cam_26", 80.6, (2.4, -3.2, 1.7), (0.6, 0, 1.35), 28, T)                      # Rook at the station
cam("Cam_27", 85.4, (420, 26, 18), (300, -10, 14), 26)                            # the lit station, it far behind by the fog
sc.camera = O["Cam_01"]
sc.render.resolution_x = 1280; sc.render.resolution_y = 720; sc.render.resolution_percentage = 100
sc.eevee.taa_render_samples = 24
try: sc.eevee.use_raytracing = False
except Exception: pass
sc.render.use_compositing = False; sc.render.use_sequencer = False
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "hush_film23.blend"))
print("film23 built", len(sc.collection.all_objects), "objects; markers", len(sc.timeline_markers))
