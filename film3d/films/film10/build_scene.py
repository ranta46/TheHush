# GLOAMRUN 3D Film 11 "The Cliff Lift" — run INSIDE Blender (hush_lookdev.blend open, scene HUSH).
# Builds the set + animation + cameras on top of the approved 3D Rook / the Hush / train, then saves
# C:\Users\81803\TremenFilm\hush\film10\hush_film10.blend.  24 fps, 2400 frames (100 s).
# Story: the night moor -> the field lamps behind us die and the Hush rises there -> chase -> the line ends at the chalk cliff
# -> Rook rolls the train onto the old cliff lift ("It can't fly. Up we go!") -> the Hush reaches the foot and eats the incline
# lamps: the lift stops halfway, lights off -> it stands right beside us, its face at our height ('Don't move') -> it looks
# away over the moor -> surprise: the old counterweight slips and runs down; the lift shoots to the top -> lights on, full
# steam over the plateau to Cliff Town; it walks off along the cliff foot (it will come again).
import bpy, bmesh, math, random, os
from mathutils import Vector
OUT = r"C:\Users\81803\TremenFilm\hush\film10"; os.makedirs(OUT, exist_ok=True)
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



# ---------------- world: the moor, the chalk cliff, the old cliff lift, the plateau, Cliff Town ----------------
from mathutils import Matrix
rr = random.Random(1111)
TG = math.tan(math.radians(40))               # the lift incline: 40 degrees up the spur of the cliff
HC = 40.0                                     # cliff height (the plateau)
XF0 = 150.0                                   # the foot of the incline
XTOP = XF0 + HC / TG                          # where the top line starts (~197.7)
PL = 7.0                                      # lift deck length
def Linc(x): return (x - XF0) * TG - 0.4      # the incline line (bottom of the lift wedge)
def xc_of(D): return XF0 + D / TG - PL / 2    # lift deck centre x for deck height D
def plain(x, y):
    a = min(1.0, max(0.0, (abs(y) - 6) / 14))
    n = 1.0 * math.sin(x * 0.04 + y * 0.03) + 0.7 * math.sin(x * 0.09 - y * 0.06 + 1.3) + 0.5 * math.sin(y * 0.11)
    return a * (n + 0.012 * max(0, abs(y) - 20) ** 1.25) - 0.02
def cliff(x):
    if x < XTOP - HC / math.tan(math.radians(72)): return -99.0
    if x < XTOP: return (x - (XTOP - HC / math.tan(math.radians(72)))) * math.tan(math.radians(72))
    return HC
def gh(x, y):
    g = plain(x, y)
    if x >= XTOP:
        a = min(1.0, max(0.0, (abs(y) - 6) / 12))
        return HC + a * 0.8 * (math.sin(x * 0.05 + y * 0.04) + 0.6 * math.sin(y * 0.09 - x * 0.03))
    g = max(g, cliff(x))
    if XF0 - PL <= x < XF0 and abs(y) < 4.5: return -6.0                       # the lift pit at the foot
    if XF0 <= x < XTOP: g = max(g, Linc(x) - 0.2 - max(0.0, abs(y) - 4.5) * 1.6)   # the spur the lift runs up
    return g
grass = newM("S_Grass", (0.07, 0.08, 0.06), rough=0.95); GA.data.materials.clear(); GA.data.materials.append(grass)
GA.location = (150, 100, -7.0)
plainM = newM("S_Plain", (0.07, 0.08, 0.06), rough=1); chalkM = newM("S_Chalk", (0.34, 0.33, 0.31), rough=1)
def axis(a, b, step):
    out = []; v = a
    while v <= b: out.append(v); v += step
    return out
xs = axis(-200, 128, 5) + axis(130, 215, 1.0) + axis(220, 640, 5)
ys = axis(-240, -32, 6) + axis(-30, 30, 1.0) + axis(36, 240, 6)
bm = bmesh.new(); vv = [[bm.verts.new((x, y, gh(x, y))) for y in ys] for x in xs]
for i in range(len(xs) - 1):
    for j in range(len(ys) - 1):
        f = bm.faces.new((vv[i][j], vv[i + 1][j], vv[i + 1][j + 1], vv[i][j + 1]))
        f.normal_update()
        if f.normal.z < 0.85 and max(v.co.z for v in f.verts) > 0.6: f.material_index = 1
GO = mk("S_MoorGround", bm, plainM, smooth=False); GO.data.materials.append(chalkM)
railM = newM("S_RailM", (0.2, 0.2, 0.22), rough=0.4, metal=0.8); tie = newM("S_Tie", (0.05, 0.04, 0.035), rough=1)
postM = newM("S_Post", (0.02, 0.02, 0.025), rough=0.5); ironM = newM("S_BIron", (0.06, 0.065, 0.075), rough=0.5, metal=0.6)
woodM = newM("S_Wood", (0.1, 0.07, 0.045), rough=1)
def pboxes(name, mat, items, parent=None):   # boxes with yaw + pitch in ONE mesh: (loc, scl, rz, ry)
    bm = bmesh.new()
    for loc, scl, rz, ry in items:
        g = bmesh.ops.create_cube(bm, size=1.0)["verts"]; bmesh.ops.scale(bm, vec=scl, verts=g)
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(rz, 3, "Z") @ Matrix.Rotation(ry, 3, "Y"), verts=g)
        bmesh.ops.translate(bm, vec=loc, verts=g)
    return mk(name, bm, mat, parent=parent)
rails, ties = [], []
def line(x0, x1, y, z=0.0):
    n = int((x1 - x0) / 4)
    for i in range(n):
        xa = x0 + i * 4.0
        for yy in (-0.53, 0.53): rails.append(((xa + 2, y + yy, z + 0.03), (4.02, 0.08, 0.06), 0, 0))
        for k in (0, 2): ties.append(((xa + k + 1, y, z + 0.01), (0.25, 1.4, 0.06), 0, 0))
line(-160, XF0 - PL - 0.2, 0.0); line(XTOP + 0.2, 560, 0.0, HC)
pboxes("S_Rails", railM, rails); pboxes("S_Ties", tie, ties)
pboxes("S_EndStopTop", newM("S_Red", (0.6, 0.05, 0.03), rough=0.5), [((540, 0, HC + 0.45), (0.3, 1.8, 0.5), 0, 0)])
# the incline rails up the spur (lift on y=0, the old counterweight on y=+2.6)
ANG = -math.atan(TG); inc = []
SL = (XTOP - (XF0 - PL)) / math.cos(math.atan(TG))
for yy in (-1.0, 1.0, 2.1, 3.1):
    xm = (XF0 - PL + XTOP) / 2; inc.append(((xm, yy, Linc(xm) - 0.05), (SL, 0.12, 0.12), 0, ANG))
for k in range(int(SL / 1.5)):
    x = XF0 - PL + k * 1.5 * math.cos(math.atan(TG)); inc.append(((x, 1.05, Linc(x) - 0.15), (0.3, 5.2, 0.1), 0, ANG))
pboxes("S_InclineRails", railM, inc[:4]); pboxes("S_InclineTies", tie, inc[4:])
# the lift: a tall wooden wedge with a level deck (deck top = the empty's origin)
LIFT = empty("S_Lift", (xc_of(0), 0, 0))
bm = bmesh.new(); hb = 1.5
def bot(lx): return (lx - PL / 2) * TG - 0.4   # wedge bottom relative to the deck (front -0.4, back about -6.3)
pts = [(-PL / 2, -hb, 0), (PL / 2, -hb, 0), (PL / 2, hb, 0), (-PL / 2, hb, 0),
       (-PL / 2, -hb, bot(-PL / 2)), (PL / 2, -hb, bot(PL / 2)), (PL / 2, hb, bot(PL / 2)), (-PL / 2, hb, bot(-PL / 2))]
V = [bm.verts.new(p) for p in pts]
for f in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)): bm.faces.new([V[i] for i in f])
mk("S_LiftWedge", bm, woodM, parent=LIFT)
lb = [((0, yy, 0.03), (PL, 0.08, 0.06), 0, 0) for yy in (-0.53, 0.53)]
pboxes("S_LiftRails", railM, lb, LIFT)
pboxes("S_LiftFrame", ironM, [((lx, sd * 1.45, -1.5), (0.15, 0.15, 3.0), 0, 0) for lx in (-3.3, 0, 3.3) for sd in (-1, 1)] +
       [((0, sd * 1.45, 0.55), (PL, 0.1, 0.1), 0, 0) for sd in (-1, 1)], LIFT)
mk("S_LiftLever", box(), newM("S_Red2", (0.55, 0.06, 0.03), rough=0.5), (-1.2, -1.3, 0.6), (0.3, 0, 0), (0.08, 0.08, 1.1), parent=LIFT)
# the old counterweight: a stone block on its own rails (y=+2.6); it goes down while the lift goes up
WT = empty("S_Weight", (0, 2.6, 0))
mk("S_WeightBlock", box(), newM("S_WStone", (0.16, 0.15, 0.14), rough=1), (0, 0, 1.0), scl=(2.4, 1.3, 1.8), parent=WT)
WT.rotation_euler = (0, ANG, 0)
def wpos(Dw):                                   # Dw = the height of the weight along the incline (0 .. HC)
    x = XF0 + Dw / TG - 1.5; return Vector((x, 2.6, Linc(x) + 0.05))
# the winch house at the top with the big wheel
mk("S_WinchHouse", box(), woodM, (XTOP + 4.5, 5.5, HC + 2.0), scl=(5, 4, 4)); mk("S_WinchRoof", box(), newM("S_Roof0", (0.06, 0.06, 0.07), rough=1), (XTOP + 4.5, 5.5, HC + 4.2), scl=(5.6, 4.6, 0.4))
WHEEL = empty("S_WheelPivot", (XTOP + 1.2, 1.3, HC + 3.0))
mk("S_Wheel", cyl(1.4, 1.4, 0.2, 24), ironM, (0, 0, 0), (math.pi / 2, 0, 0), parent=WHEEL)
mk("S_WheelFrame", box(), woodM, (XTOP + 1.2, 1.3, HC + 1.4), scl=(0.3, 0.3, 3.0))
WLM = newM("L_WinchLampM", (1, 0.62, 0.25), emit=8)
mk("L_WinchLamp", sph(0.22, 12, 8), WLM, (XTOP + 1.8, 3.3, HC + 3.4)); WL = light("L_WinchLight", "POINT", 90, (1, 0.6, 0.3), (XTOP + 1.8, 3.0, HC + 3.0))
# cables from the wheel to the lift and to the weight (stretched)
cabM = newM("S_Cable", (0.03, 0.03, 0.03), rough=0.5, metal=0.5)
def cable(name, anchor_parent, anchor_loc, tgt_loc):
    a = empty(name + "_A", anchor_loc, anchor_parent); t = empty(name + "_T", tgt_loc)
    bm = bmesh.new(); g = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=6, radius1=0.035, radius2=0.035, depth=1.0)["verts"]
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(-math.pi / 2, 3, "X"), verts=g); bmesh.ops.translate(bm, vec=(0, 0.5, 0), verts=g)
    c = mk(name, bm, cabM, parent=a); s = c.constraints.new("STRETCH_TO"); s.target = t; s.rest_length = 1.0; s.volume = "NO_VOLUME"
    return c
cable("S_CableLift", LIFT, (PL / 2 - 0.2, 0, 0.6), (XTOP + 1.2, 0.2, HC + 3.0))
cable("S_CableWeight", WT, (1.2, 0, 1.5), (XTOP + 1.2, 2.4, HC + 3.0))
# lamps up the incline (the Hush eats them from the bottom up and the lift stops)
ILAMP = []
for i, D in enumerate((3, 9, 15, 21, 27, 33)):
    x = XF0 + D / TG; z = gh(x, -5.0)
    mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, -5.0, z + 1.7))
    hm = newM(f"L_IHead{i}", (1, 0.62, 0.25), emit=8); mk(f"L_IHead{i}", sph(0.2, 12, 8), hm, (x, -5.0, z + 3.45))
    ILAMP.append((hm, light(f"L_I{i}", "POINT", 70, (1, 0.6, 0.3), (x, -5.0, z + 3.2))))
# the field lamps on the moor behind us (they die when the Hush comes, far ones first)
BLAMP = []
for i, x in enumerate((-140, -125, -110, -95, -80)):
    y = 5.0; z = gh(x, y)
    mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, y, z + 1.7))
    hm = newM(f"L_BHead{i}", (1, 0.62, 0.25), emit=8); mk(f"L_BHead{i}", sph(0.2, 12, 8), hm, (x, y, z + 3.45))
    BLAMP.append((hm, light(f"L_B{i}", "POINT", 60, (1, 0.6, 0.3), (x, y, z + 3.2))))
# the moor: stone walls, rocks, bare trees; chalk rocks at the cliff foot
rocks = []
for i in range(60):
    x = rr.uniform(-180, 175); y = rr.choice((rr.uniform(9, 120), rr.uniform(-120, -9)))
    if x > 135 and abs(y) < 14: continue
    s = rr.uniform(0.5, 1.8); rocks.append(((x, y, gh(x, y) + s * 0.3), (s * 1.4, s, s * 0.9), rr.uniform(0, 3), 0))
for i in range(40):
    y = rr.uniform(-160, 160)
    if abs(y) < 12: continue
    x = XTOP - HC / math.tan(math.radians(72)) - rr.uniform(-1, 4); s = rr.uniform(1.0, 3.0)
    rocks.append(((x, y, s * 0.3), (s * 1.4, s, s), rr.uniform(0, 3), 0))
pboxes("S_Rocks", newM("S_RockM", (0.17, 0.17, 0.16), rough=1), rocks)
walls = []
for k in range(14):
    x0 = -170 + k * 22.0
    for sd in (-1, 1): walls.append(((x0 + 8, sd * rr.uniform(16, 40), 0.35), (16, 0.6, 0.9), rr.uniform(-0.2, 0.2), 0))
pboxes("S_Walls", newM("S_WallM", (0.11, 0.11, 0.1), rough=1), [((l[0][0], l[0][1], gh(l[0][0], l[0][1]) + 0.35), l[1], l[2], 0) for l in walls])
treeM = newM("S_Tree", (0.03, 0.03, 0.03), rough=1); bm = bmesh.new()
for i in range(30):
    x = rr.uniform(-190, 620); y = rr.choice((rr.uniform(12, 90), rr.uniform(-90, -12)))
    if XF0 - 20 < x < XTOP + 8: continue
    h = rr.uniform(4, 8); z0 = gh(x, y)
    g = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=6, radius1=0.25, radius2=0.08, depth=h)["verts"]; bmesh.ops.translate(bm, vec=(x, y, z0 + h / 2), verts=g)
    for b_ in range(3):
        g = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=5, radius1=0.12, radius2=0.03, depth=h * 0.45)["verts"]
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(rr.uniform(0, 6.28), 3, "Z") @ Matrix.Rotation(0.7, 3, "Y"), verts=g)
        bmesh.ops.translate(bm, vec=(x, y, z0 + h * (0.55 + b_ * 0.12)), verts=g)
mk("S_Trees", bm, treeM)
hillM = newM("S_HillM", (0.045, 0.055, 0.045), rough=1)
for i in range(6):
    hx = -180 + i * 60
    mk("S_Hill", sph(1, 20, 12), hillM, (hx, rr.uniform(140, 170), -6), scl=(rr.uniform(45, 60), 35, rr.uniform(16, 26)), smooth=True)
    mk("S_Hill", sph(1, 20, 12), hillM, (hx + 30, -rr.uniform(170, 200), -6), scl=(rr.uniform(45, 60), 35, rr.uniform(16, 26)), smooth=True)
# Cliff Town and its station on the plateau (x 440 .. 540)
houseM = newM("S_HouseM", (0.075, 0.07, 0.078), rough=1); roofM = newM("S_Roof", (0.06, 0.06, 0.07), rough=1)
winM = newM("S_Win", (1, 0.62, 0.25), emit=5)
for i in range(22):
    x = rr.uniform(440, 560); y = rr.choice((rr.uniform(9, 40), rr.uniform(-40, -9))); w = rr.uniform(3, 6); h = rr.uniform(2.5, 5)
    z0 = gh(x, y)
    mk("S_House", box(), houseM, (x, y, z0 + h / 2 - 0.5), scl=(w, w, h)); mk("S_Roof", box(), roofM, (x, y, z0 + h - 0.4), scl=(w + 0.4, w + 0.4, 0.3))
    mk("S_Win", box(), winM, (x, y - math.copysign(w / 2 + 0.02, y), z0 + h * 0.45), scl=(0.6, 0.05, 0.7))
mk("S_Platform", box(), newM("S_Plat", (0.1, 0.09, 0.1), rough=1), (478, 2.4, HC), scl=(44, 2.2, 0.6))
for i in range(5):
    x = 460 + i * 9.0; mk("S_Post", cyl(0.06, 0.08, 3.4, 8), postM, (x, 3.2, HC + 1.7))
    mk("L_StHead", sph(0.2, 12, 8), newM("L_StHeadM", (1, 0.62, 0.25), emit=8), (x, 3.2, HC + 3.45)); light(f"L_St{i}", "POINT", 80, (1, 0.6, 0.3), (x, 3.2, HC + 3.2))
moonM = newM("S_Moon", (0.9, 0.88, 0.8), emit=3)
mk("S_Moon", cyl(9, 9, 0.2, 48), moonM, (150, 320, 95), (math.pi / 2, 0, 0))
w = sc.world; w.node_tree.nodes["Background"].inputs[0].default_value = (0.014, 0.018, 0.045, 1)
O["MoonKey"].data.energy = 2.0
FIREM = newM("T_FireM", (1, 0.35, 0.08), emit=12)
mk("T_Fire", box(), FIREM, (2.45, 0, 0.55), scl=(0.06, 0.5, 0.3), parent=T)
FIRE = light("T_FireGlow", "POINT", 25, (1, 0.45, 0.15), (2.2, 0, 0.7), T)

# ---------------- the Hush ----------------
H = O["Hush"]; H.scale = (2.4, 2.4, 2.4)
mask_spot = light("T_MaskLight", "SPOT", 9000, (0.7, 0.85, 1.0), (0, 0, 0)); mask_spot.data.spot_size = math.radians(18)
c = mask_spot.constraints.new("TRACK_TO"); c.target = O["H_Mask"]; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
mask_spot.parent = H; mask_spot.location = (2.0, -14, 4.0)

# ---------------- animation ----------------
TOFF = 2.3                                     # train centre offset (the train sits in the middle of the deck)
def tkey(t, x, y, z=0.0):
    key(T, "location", F(t), Vector((x, y, z))); key(T, "rotation_euler", F(t), 0.0, 1); key(T, "rotation_euler", F(t), 0.0, 2)
# over the moor to the cliff foot, roll onto the lift (30.5)
TX = [(0, -110), (8, -55), (12, -25), (16, 10), (20, 48), (24, 88), (27, 116), (29, 134), (30.5, xc_of(0) - TOFF)]
for t, x in TX: tkey(t, x, 0)
# up the lift: D (deck height) 0 -> 17 (32 .. 41), stuck, then the old weight drops: 17 -> 40 (61.5 .. 65.5)
DK = [(30.5, 0.0), (32.0, 0.0), (34.0, 3.0), (39.0, 14.0), (41.0, 17.0), (61.5, 17.0), (62.3, 19.5), (64.6, 36.5), (65.5, 40.0), (66.6, 40.0)]
for t, D in DK:
    key(LIFT, "location", F(t), Vector((xc_of(D), 0, D))); tkey(t, xc_of(D) - TOFF, 0, D)
    key(WT, "location", F(t), wpos(HC - 3.0 - D))
key(LIFT, "location", F(0), Vector((xc_of(0), 0, 0))); key(WT, "location", F(0), wpos(HC - 3.0))
lin(LIFT); lin(WT)
for t, a in ((0, 0), (32, 0), (41, 160), (61.5, 160), (65.5, 560), (100, 560)): key(WHEEL, "rotation_euler", F(t), math.radians(a), 1)
lin(WHEEL)
# off the lift onto the plateau and away to Cliff Town
TX2 = [(69.0, XTOP + 6), (72, 226), (76, 262), (80, 300), (84, 340), (88, 380), (92, 420), (96, 452), (98.5, 466), (100, 467)]
for t, x in TX2: tkey(t, x, 0, HC)
lin(T)
# the field lamps behind us die, far ones first (6.0-8.0)
for i, (hm, lt) in enumerate(BLAMP):
    td = 6.0 + i * 0.5; s = hm.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for t, e in ((td - 0.01, 8), (td + 0.15, 0)): s.default_value = e; s.keyframe_insert("default_value", frame=F(t))
    for t, e in ((td - 0.01, 60), (td + 0.15, 0)): lt.data.energy = e; lt.data.keyframe_insert("energy", frame=F(t))
# the incline lamps: it eats them from the bottom up (39.0-40.6); the winch lamp at 40.8 (the lift stops at 41)
for i, (hm, lt) in enumerate(ILAMP):
    td = 39.0 + i * 0.32; s = hm.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for t, e in ((0, 8), (td, 8), (td + 0.15, 0)): s.default_value = e; s.keyframe_insert("default_value", frame=F(t))
    for t, e in ((0, 70), (td, 70), (td + 0.15, 0)): lt.data.energy = e; lt.data.keyframe_insert("energy", frame=F(t))
s = WLM.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 8), (40.8, 8), (41.0, 0)): s.default_value = e; s.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 90), (40.8, 90), (41.0, 0)): WL.data.energy = e; WL.data.keyframe_insert("energy", frame=F(t))
# the Hush: rises behind us on the moor (6.8-9.4), runs after us, reaches the cliff foot (38.5), eats the incline lamps,
# walks up beside the spur and stands right beside the dark lift (47.5-61.5), looks out over the moor (56-61),
# turns at the crash of the weight, can't climb the cliff: walks off along the foot (it will come again)
HP_ = [(0, -100, -26, -40), (6.8, -100, -26, -40), (8.2, -100, -26, -16), (9.4, -100, -26, 0), (12, -80, -20, 0), (16, -40, -16, 0),
       (20, 0, -15, 0), (24, 50, -15, 0), (28, 98, -14, 0), (32, 124, -14, 0), (36, 140, -15, 0), (38.5, 149, -16, 0),
       (43, 160, -16, 0), (47.5, 169, -14, 0), (61.5, 169, -14, 0), (64.0, 172, -14, 0), (66.5, 175, -18, 0), (72, 177, -40, 0),
       (80, 178, -72, 0), (90, 179, -110, 0), (100, 180, -150, 0)]
for t, x, y, dz in HP_:
    key(H, "location", F(t), Vector((x, y, max(gh(x, y), -1.0) + dz))); key(H, "scale", F(t), Vector((2.4, 2.4, 2.4)))
FEED = empty("S_Feed", (185, 10, 25))                         # where it looks while it searches (past us up the slope, then out over the moor)
for t, x, y, z in ((43, 190, 12, 30), (47, 192, 2, 30), (52, 190, 4, 28), (55.5, 186, 6, 24), (56.8, 100, -90, 8), (61.5, 90, -100, 8)):
    key(FEED, "location", F(t), Vector((x, y, z)))
d1 = H.constraints.new("LOCKED_TRACK"); d1.target = T; d1.track_axis = "TRACK_NEGATIVE_Y"; d1.lock_axis = "LOCK_Z"
d2 = H.constraints.new("LOCKED_TRACK"); d2.target = FEED; d2.track_axis = "TRACK_NEGATIVE_Y"; d2.lock_axis = "LOCK_Z"
for t, v in ((0, 0.0), (43.0, 0.0), (44.0, 0.6), (46.5, 0.6), (47.5, 0.85), (55.5, 0.85), (57.0, 1.0), (61.5, 1.0), (62.4, 0.0)):
    d2.influence = v; d2.keyframe_insert("influence", frame=F(t))
gm = M("H_Green").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 0), (6.8, 0), (8.4, 60), (100, 60)): gm.default_value = e; gm.keyframe_insert("default_value", frame=F(t))
# our lights: all out at 43.6 (Rook: "Lights off. Everyone, quiet."), back on at 66.2 at the top
se = M("H_Signal").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 40), (9, 40), (10, 80), (43.4, 80), (44.4, 3), (66.0, 3), (66.6, 60), (100, 50)): se.default_value = e; se.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 4), (10, 6), (43.4, 6), (44.4, 0.3), (66.0, 0.3), (66.6, 4)): SIGL.data.energy = e; SIGL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 900), (43.4, 900), (43.6, 0), (66.2, 0), (66.5, 900)): HL.data.energy = e; HL.data.keyframe_insert("energy", frame=F(t))
for t, e in ((0, 45), (43.4, 45), (44.0, 14), (66.0, 14), (66.8, 45)): O["Fill"].data.energy = e; O["Fill"].data.keyframe_insert("energy", frame=F(t))
wi = M("H_Window").node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 4), (43.5, 4), (43.8, 0.0), (66.2, 0.0), (66.5, 4)): wi.default_value = e; wi.keyframe_insert("default_value", frame=F(t))
fe = FIREM.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for t, e in ((0, 12), (43.4, 12), (43.7, 0), (66.0, 0), (66.4, 20), (100, 14)): fe.default_value = e; fe.keyframe_insert("default_value", frame=F(t))
for t, e in ((0, 25), (43.4, 25), (43.7, 0), (66.0, 0), (66.4, 40), (100, 30)): FIRE.data.energy = e; FIRE.data.keyframe_insert("energy", frame=F(t))
# Rook head turns (30 = ahead, -40/-60/-90 = to the side where it stands, -150 = back) and wings
for t, rz in ((0, 30), (5.8, 30), (6.6, -150), (9.6, -150), (10.2, 30), (19.8, 30), (20.6, -150), (24.0, -150), (24.8, 30),
              (38.4, 30), (39.0, -100), (41.6, -100), (42.2, 0), (46.6, 0), (47.4, -70), (55.8, -70), (56.4, -50), (61.2, -50), (61.8, 60),
              (63.8, 60), (64.4, -90), (65.8, -90), (66.2, 30), (72.6, 30), (73.4, -150), (77.4, -150), (78.2, 30), (100, 30)):
    key(HP, "rotation_euler", F(t), math.radians(rz), 2)
for sd in (-1, 1):
    wg = O[f"R_Wing{sd}"]
    for t, a in ((0, 0), (1.0, 0), (1.3, 1.2), (1.6, 0.3), (1.9, 1.2), (2.3, 0), (10.1, 0), (10.4, 1.3), (12.4, 1.3), (12.8, 0),
                 (20.8, 0), (21.1, 1.2), (23.4, 1.2), (23.8, 0), (25.0, 0), (25.3, 1.5), (27.4, 1.5), (27.8, 0),
                 (30.2, 0), (30.5, 1.4), (31.0, 0.2), (31.4, 1.4), (32.4, 0),
                 (44.2, 0), (44.6, -0.6), (61.6, -0.6), (61.9, 1.5), (64.2, 1.5), (64.6, 0),
                 (66.0, 0), (66.3, 1.5), (68.6, 1.5), (69.0, 0), (74.6, 0), (74.9, 1.3), (77.0, 1.3), (77.4, 0), (90.4, 0), (90.7, 1.0), (92.8, 1.0), (93.2, 0)):
        key(wg, "rotation_euler", F(t), math.radians(sd * 12) + sd * a * 0.6, 1)
for f in range(1, END, 12):
    if F(29) <= f <= F(69) or f >= F(98.5): continue      # slow / on the lift / stopped
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
cam("Cam_01", 0, (3.0, -11, 2.6), (1.0, 0, 1.6), 26, T)                    # wide side: the train on the night moor
cam("Cam_02", 5.8, (-6, 2.5, 4.0), (-34, -22, 9), 26, T)                   # looking back: the field lamps die, it rises
cam("Cam_03", 9.8, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)                 # Rook: full steam
cam("Cam_04", 12.8, (-5, -1.5, 3.2), "H_Mask", 55, T)                      # its face behind us
cam("Cam_05", 15.6, (38, -52, 15), (0, -8, 6), 24)                         # wide: the chase over the moor
cam("Cam_06", 20.2, (-4, -3.2, 2.6), "H_Mask", 28, T)                       # from the train: it gains on us
cam("Cam_07", 24.6, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)                # Rook: the line ends, the old cliff lift
cam("Cam_08", 27.0, (-6, -5, 3), (35, 2, 9), 24, T)                        # the chalk cliff and the old lift ahead
cam("Cam_09", 31.6, (176, -46, 8), (155, -4, 10), 22)                      # wide side: the lift climbs, it comes to the foot
cam("Cam_10", 38.8, (2.6, -3.2, 1.8), (0.6, -0.6, 1.4), 28, T)             # Rook: the lamps go, the lift stops
cam("Cam_11", 41.8, (-1.6, -1.6, 1.9), "H_Mask", 30, T)                    # from the lift: down at it, lights off
cam("Cam_12", 45.0, (179, -50, 20), (163, -8, 13), 22)                      # wide: it walks up beside the dark lift
cam("Cam_13", 48.4, (183, -5, 31), (167, -8, 19), 20)                     # low on the moor: it stands right beside us
cam("Cam_14", 52.2, (13, -4, 7.5), (3, -7, 3.2), 18, T)                      # Rook and its face, the same height
cam("Cam_15", 56.0, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)                # Rook: it looks away
cam("Cam_16", 59.2, (150, 30, 30), (165, -10, 14), 22)                      # wide from behind the spur: it looks out over the moor
cam("Cam_17", 61.4, (XTOP - 1, 9, HC + 3), (172, 2.6, 18), 28)         # the old weight slips and runs down
cam("Cam_18", 63.0, (172, -36, 30), (185, 0, 31), 22)                       # the lift shoots up the cliff
cam("Cam_19", 64.4, (-1.5, -2.2, 1.6), "H_Mask", 30, T)                    # down at it: it turns to us
cam("Cam_20", 66.0, (2.6, -3.2, 1.8), (0.6, 0, 1.4), 28, T)                # Rook: lights on, full steam
cam("Cam_21", 68.4, (8, -9, 3), (0, 0, 1.4), 26, T)                        # off the lift onto the plateau
cam("Cam_22", 72.6, (200, -20, HC + 6), (178, -46, 14), 24)                      # from the cliff edge: it walks along the foot below
cam("Cam_23", 79.0, (330, -48, HC + 14), (290, 0, HC + 2), 22)              # wide: over the plateau
cam("Cam_24", 85.6, (-20, -14, 8), (30, 0, 2), 24, T)                      # wide: Cliff Town ahead
cam("Cam_25", 90.2, (2.4, -3.2, 1.7), (0.6, 0, 1.35), 28, T)               # Rook at the station
sc.camera = O["Cam_01"]
sc.render.resolution_x = 1280; sc.render.resolution_y = 720; sc.render.resolution_percentage = 100
sc.eevee.taa_render_samples = 24
try: sc.eevee.use_raytracing = False
except Exception: pass
sc.render.use_compositing = False; sc.render.use_sequencer = False
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "hush_film10.blend"))
print("film10 built", len(sc.collection.all_objects), "objects; markers", len(sc.timeline_markers))
