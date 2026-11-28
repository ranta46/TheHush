# GLOAMRUN 3D Film 29 "Not a Hill" (VERTICAL short, 26 s, pattern P1 SCALE REVEAL, LOOP) - run INSIDE Blender on hush_lookdev.blend.
# Frame 0: a dark round hill by the lake line, two pale green eyes in it, Rook small below ("That is not a hill. It's awake.").
# The train creeps past; the line lamps die near it -> its eyes flare -> the hill STANDS UP (the Hush, sting) -> full steam, it strides after
# us -> it bends over the last car, finger at its mask ('...Don't move.') -> it is gone... -> 'Wait. That hill wasn't there.' -> cut to the
# same shot as frame 0 (a new hill ahead, same eyes) = seamless loop.
import bpy, bmesh, math, random, os
from mathutils import Vector
OUT = r"C:\Users\81803\TremenFilm\hush\film24"; os.makedirs(OUT, exist_ok=True)
sc = bpy.data.scenes["HUSH"]; bpy.context.window.scene = sc; O = bpy.data.objects
FPS = 24; END = 624; sc.render.fps = FPS; sc.frame_start = 1; sc.frame_end = END
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
# ---------------- world: the lake line on the night moor, the lone "hill" between the line and the black lake ----------------
from mathutils import Matrix
rr = random.Random(2929)
def ss(a, b, v):
    if b < a: return 1.0 - ss(b, a, v)
    u = min(1.0, max(0.0, (v - a) / (b - a))); return u * u * (3 - 2 * u)
LAKE_Y = -60.0
def gh(x, y):
    ay = abs(y); n = 0.5 * math.sin(x * 0.05 + y * 0.04) + 0.35 * math.sin(x * 0.13 - y * 0.06 + 1.1)
    z = n * ss(4, 14, ay)
    if y > 0: z += 9.0 * ss(60, 200, y) * (0.6 + 0.4 * math.sin(x * 0.015))          # low hills far on the left
    if y < LAKE_Y + 6: z = min(z, -0.6 - 2.0 * ss(LAKE_Y + 6, LAKE_Y - 10, y))         # the lake bed
    z = max(z, 40.0 * ss(-420, -560, y) * (0.75 + 0.25 * math.sin(x * 0.01)))          # far ridge across the lake
    if ay < 2.6: z = min(z, -0.06)
    return z
GA = O["Ground"]; GA.location = (0, 0, -30.0); GA.scale = (1400, 1000, 1)
grassM = newM("S_Moor", (0.05, 0.055, 0.04), rough=1)
GA.data.materials.clear(); GA.data.materials.append(grassM)
def axis(a, b, step):
    out = []; v = a
    while v <= b + 1e-6: out.append(v); v += step
    return out
xs = axis(-300, -82, 8) + axis(-80, 420, 2.5) + axis(424, 700, 8)
ys = axis(-600, -72, 8) + axis(-70, -8, 2.0) + axis(-7.5, 7.5, 0.5) + axis(8, 60, 2.5) + axis(66, 320, 8)
bm = bmesh.new(); vv = [[bm.verts.new((x, y, gh(x, y))) for y in ys] for x in xs]
for i in range(len(xs) - 1):
    for j in range(len(ys) - 1):
        bm.faces.new((vv[i][j], vv[i + 1][j], vv[i + 1][j + 1], vv[i][j + 1]))
GO = mk("S_Ground", bm, grassM, smooth=True)
lakeM = newM("S_Lake", (0.02, 0.03, 0.06), rough=0.08, metal=0.0)
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5); bmesh.ops.scale(bm, vec=(1100, 420, 1), verts=bm.verts)
mk("S_LakeWater", bm, lakeM, (200, LAKE_Y - 210, -0.9))
railM = newM("S_RailM", (0.2, 0.2, 0.22), rough=0.4, metal=0.8); tie = newM("S_Tie", (0.05, 0.04, 0.035), rough=1)
postM = newM("S_Post", (0.02, 0.02, 0.025), rough=0.5)
def pboxes(name, mat, items, parent=None):
    bm = bmesh.new()
    for loc, scl, rzz in items:
        g = bmesh.ops.create_cube(bm, size=1.0)["verts"]; bmesh.ops.scale(bm, vec=scl, verts=g)
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(rzz, 3, "Z"), verts=g); bmesh.ops.translate(bm, vec=loc, verts=g)
    return mk(name, bm, mat, parent=parent)
X0, X1 = -200.0, 600.0
pboxes("S_Rails", railM, [(((X0 + X1) / 2, sd * 0.53, 0.03), (X1 - X0, 0.08, 0.06), 0) for sd in (-1, 1)])
pboxes("S_Ties", tie, [((x, 0, -0.02), (0.25, 1.4, 0.06), 0) for x in axis(X0, X1, 2.0)])
stoneM = newM("S_StoneM", (0.16, 0.16, 0.15), rough=0.95)
items = []
for k in range(30):
    x0 = rr.uniform(-250, 600); y0 = rr.uniform(12, 140); a = rr.uniform(0, 3.14); L = rr.uniform(15, 40)
    items.append(((x0, y0, gh(x0, y0) + 0.4), (L, 0.6, 1.0), a))
pboxes("S_Walls", stoneM, items)
reedM = newM("S_Reed", (0.06, 0.06, 0.035), rough=1)
bm = bmesh.new()
for i in range(160):
    x = rr.uniform(-100, 500); y = LAKE_Y + rr.uniform(-2, 9); hh = rr.uniform(1.0, 2.2)
    g = bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=0.12, radius2=0.01, depth=hh)["verts"]
    bmesh.ops.translate(bm, vec=(x, y, gh(x, y) + hh / 2), verts=g)
mk("S_Reeds", bm, reedM)
RLAMP = []
def lamp(tag, x, y, td, e=55, z=None):
    z = gh(x, y) if z is None else z; mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, y, z + 1.7))
    hm = newM(f"L_{tag}", (1, 0.62, 0.25), emit=8); mk(f"L_{tag}", sph(0.2, 12, 8), hm, (x, y, z + 3.45))
    lo = light(f"L_{tag}L", "POINT", e, (1, 0.6, 0.3), (x, y, z + 3.2)); RLAMP.append((hm, lo, td)); return hm, lo
# ---------------- timing ----------------
TK = [(0, 0), (13.0, 120), (13.6, 125), (22.4, 270), (26.0, 303)]      # creep, full steam, ease at the end (loop speed = start speed)
def ip(K, t):
    for (ta, sa), (tb, sb) in zip(K, K[1:]):
        if ta <= t <= tb:
            u = (t - ta) / (tb - ta) if tb > ta else 0; return sa + (sb - sa) * u
    return K[-1][1] if t > K[0][0] else K[0][1]
def tpos(t): return Vector((ip(TK, t), 0, 0))
HX0, HY, HDZ = 30.0, -26.0, -22.0                                       # the "hill": lying low, 30 m ahead-right of the train at t=0
LOOP = 24.8; HX1 = ip(TK, LOOP) + (HX0 - ip(TK, 0))                    # the new "hill" ahead at the loop cut, same place relative to us
HP_ = [(0, HX0, HY, HDZ), (13.4, HX0, HY, HDZ), (15.0, HX0, HY + 2, 0), (16.4, 62, -20, 0), (18.8, 190, -10, 0)]
for t in (19.4, 19.8, 20.2, 20.6, 21.0, 21.4, 21.8, 22.2):              # bent over the last car
    HP_.append((t, ip(TK, t) - 9.0, -5.0, -19.0))
HP_ += [(22.5, ip(TK, 22.5) - 6, -14, -30), (24.2, HX1, HY, -30), (24.6, HX1, HY, HDZ), (26.0, HX1, HY, HDZ)]
# the grassy mound around its shoulders (the "hill"); one at the start and one at the loop
for k, hx in enumerate((HX0, HX1)):
    mk(f"S_Mound{k}", sph(1.0, 24, 12), grassM, (hx, HY, gh(hx, HY) - 1.2), scl=(19, 19, 5.0), smooth=True)
# line lamps: near the hill they die as we pass; ahead they live (the last shot = the first shot)
for i, x in enumerate((8, 22, 36, 50)): lamp(f"A{i}", x, 3.2, 3.8 + i * 0.7)
for i, x in enumerate((150, 175, 200, 225)): lamp(f"C{i}", x, 3.2, 999)
for i, x in enumerate((-30, -12)): lamp(f"Z{i}", x, 3.2, 0.6 + i * 0.6)
for i, x in enumerate((285, 300, 315, 330)): lamp(f"E{i}", x, 3.2, 999)
# the moon low over the lake, behind the hill (it shows the round shape), plus a cold key on the Hush's face from our side
EL = math.radians(14.0); AZ = math.radians(-78)
moonM = newM("S_Moon", (0.95, 0.95, 0.9), emit=6)
MD = mk("S_Moon", cyl(38, 38, 0.2, 48), moonM, (0, 0, 0), (math.pi / 2, 0, math.pi / 2 + AZ))
MD.location = Vector((150 + 900 * math.cos(AZ), 900 * math.sin(AZ), 900 * math.tan(EL)))
w = sc.world; BG = w.node_tree.nodes["Background"].inputs[0]; BG.default_value = (0.035, 0.045, 0.1, 1)
MK = O["MoonKey"]; MK.data.energy = 3.2; MK.data.color = (0.75, 0.82, 1.0); MK.rotation_euler = (0, EL - math.pi / 2, AZ)
try: MK.data.use_shadow = True; MK.data.angle = math.radians(0.6)
except Exception: pass
FIREM = newM("T_FireM", (1, 0.35, 0.08), emit=12)
mk("T_Fire", box(), FIREM, (2.45, 0, 0.55), scl=(0.06, 0.5, 0.3), parent=T)
FIRE = light("T_FireGlow", "POINT", 25, (1, 0.45, 0.15), (2.2, 0, 0.7), T)
# ---------------- the Hush ----------------
HS = 3.0
H = O["Hush"]; H.scale = (HS, HS, HS)
mask_spot = light("T_MaskLight", "SPOT", 14000, (0.7, 0.85, 1.0), (0, 0, 0)); mask_spot.data.spot_size = math.radians(18)
c = mask_spot.constraints.new("TRACK_TO"); c.target = O["H_Mask"]; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
mask_spot.parent = H; mask_spot.location = (2.0, -14, 4.0)
rim = light("T_HushRim", "SPOT", 9000, (0.55, 0.7, 1.0), (0, 0, 0)); rim.data.spot_size = math.radians(40)
c = rim.constraints.new("TRACK_TO"); c.target = O["H_Mask"]; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
rim.parent = H; rim.location = (-6, 10, 9)
# ---------------- animation ----------------
HT = empty("V_HushLook"); hv = None
for f in range(1, END + 1):
    t = (f - 1) / FPS; p = tpos(t)
    key(T, "location", f, p)
    want = p + Vector((0, 0, 0))
    hv = Vector(want) if hv is None else hv + (Vector(want) - hv) * 0.25
    if t >= 24.2: hv = p + Vector((0, 0, 0))
    key(HT, "location", f, hv)
lin(T); lin(HT)
for hm, lt, td in RLAMP:
    if td > 150: continue
    s = hm.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for t, e in ((0, 8), (td - 0.01, 8), (td + 0.15, 0)): s.default_value = e; s.keyframe_insert("default_value", frame=F(max(t, 0)))
    e0 = lt.data.energy
    for t, e in ((0, e0), (td - 0.01, e0), (td + 0.15, 0)): lt.data.energy = e; lt.data.keyframe_insert("energy", frame=F(max(t, 0)))
for t, x, y, dz in HP_:
    key(H, "location", F(t), Vector((x, y, gh(x, y) + dz))); key(H, "scale", F(t), Vector((HS, HS, HS)))
d1 = H.constraints.new("LOCKED_TRACK"); d1.target = HT; d1.track_axis = "TRACK_NEGATIVE_Y"; d1.lock_axis = "LOCK_Z"
gm = M("H_Green").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
gk = [(0, 70), (9.2, 70), (9.6, 170), (13.2, 170), (13.6, 120), (18.8, 120), (19.4, 180), (22.4, 180), (22.8, 0), (24.4, 0), (24.6, 70), (26.0, 70)]
for t, e in gk: gm.default_value = e; gm.keyframe_insert("default_value", frame=F(t))
se = M("H_Signal").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 60), (100, 60)): se.default_value = e; se.keyframe_insert("default_value", frame=F(t))
# Rook head (rz = local direction + 30: 30 ahead, 120 left, -150 back, -60 right). The hill / the Hush is on the right (-y).
for t, rz_ in ((0, -60), (3.2, -60), (6.4, -60), (9.2, -100), (13.2, -150), (16.4, 30), (18.6, -150), (22.4, 30), (23.2, -60), (26.0, -60)):
    key(HP, "rotation_euler", F(t), math.radians(rz_), 2)
WUP = [(13.8, 1.4)]
for sd in (-1, 1):
    wg = O[f"R_Wing{sd}"]; ks = [(0, 0)]
    for t, a in WUP: ks += [(t, 0), (t + 0.3, a), (t + 1.6, a), (t + 1.9, 0)]
    ks += [(9.4, 0), (9.55, 1.5), (10.6, 1.4), (11.0, 0)]                       # flinch: its eyes open
    ks += [(18.9, 0), (19.2, -0.6), (22.2, -0.6), (22.5, 0)]                     # small and still under it
    for t, a in sorted(ks): key(wg, "rotation_euler", F(t), math.radians(sd * 12) + sd * a * 0.6, 1)
for f in range(1, END, 12):
    if F(9.3) <= f <= F(10.0) or F(18.8) <= f <= F(22.4): continue
    key(R, "location", f, 0.62 + (0.02 if (f // 12) % 2 else 0.0), 2)
for t, z in ((9.3, 0.62), (9.55, 0.76), (9.8, 0.6), (10.0, 0.62)): key(R, "location", F(t), z, 2)
# ---------------- cameras (VERTICAL 720x1280; one per shot, bound to markers) ----------------
def cam(name, start_s, loc, look, lens=28, parent=None, world_look=False, free=False):
    if parent is None and not free: loc = (loc[0], loc[1], max(loc[2], gh(loc[0], loc[1]) + 2.0))
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_end = 3000; cd.clip_start = 0.05; cd.sensor_fit = "VERTICAL"
    c = bpy.data.objects.new(name, cd); sc.collection.objects.link(c); c.location = loc
    if parent: c.parent = parent
    if isinstance(look, str): tgt = O[look]
    else:
        tgt = bpy.data.objects.new(name + "_T", None); sc.collection.objects.link(tgt); tgt.location = look; tgt.name = "Cam_T_" + name
        if parent and not world_look: tgt.parent = parent
    k = c.constraints.new("TRACK_TO"); k.target = tgt; k.track_axis = "TRACK_NEGATIVE_Z"; k.up_axis = "UP_Y"
    m = sc.timeline_markers.new(name, frame=F(start_s)); m.camera = c; return c
A_LOC, A_LOOK, A_LENS = (-3.2, 2.6, 1.5), (HX0, HY, 4.5), 22                       # the money shot: Rook small below, the hill and its eyes above
cam("Cam_01", 0, A_LOC, A_LOOK, A_LENS, T, world_look=True)
cam("Cam_02", 3.2, (34, 34, 16), (30, -12, 3), 20)                                # high side: the train creeps past it, the lamps die
cam("Cam_03", 6.4, (2.4, -1.9, 1.3), (0.6, 0, 1.35), 30, T)                        # Rook: the lamps die when we pass it
cam("Cam_04", 9.2, (-1.6, 1.0, 2.0), "H_Mask", 40, T)                             # over Rook, back at the hill: its eyes flare
cam("Cam_05", 13.2, (-16, 5, 1.0), "H_Mask", 14, T)                               # low behind the last car: the hill STANDS UP
cam("Cam_06", 16.4, (240, 30, 20), (170, -6, 10), 20)                             # front high: full steam, it strides after us
cam("Cam_07", 18.8, (-4.0, 2.2, 0.7), "H_Mask", 14, T)                            # low at the last car: it bends over us
cam("Cam_08", 22.4, (2.4, -1.9, 1.3), (0.6, 0, 1.35), 30, T)                       # Rook: wait. that hill wasn't there.
cam("Cam_09", LOOP, A_LOC, (HX1, A_LOOK[1], A_LOOK[2]), A_LENS, T, world_look=True)           # = Cam_01 (the loop)
sc.camera = O["Cam_01"]
sc.render.resolution_x = 720; sc.render.resolution_y = 1280; sc.render.resolution_percentage = 100
sc.eevee.taa_render_samples = 24
try: sc.eevee.use_raytracing = False
except Exception: pass
sc.render.use_compositing = False; sc.render.use_sequencer = False
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "hush_film24.blend"))
print("film24 built", len(sc.collection.all_objects), "objects; markers", len(sc.timeline_markers))
