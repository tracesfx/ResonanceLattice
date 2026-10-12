"""Generate art_src/specs/rsl_virtuoso.json and the tip vane decos rsl_virtuoso_vane_{r,l}.json.

python art_src/gen/gen_virtuoso.py art_src/specs/rsl_virtuoso.json
./art_src/art.sh rsl_virtuoso rsl_virtuoso_vane_r rsl_virtuoso_vane_l

Unique player capital (DESIGN.md 3.9). Direction chosen by the user (2026-10-11, option C of
art_src/review/virtuoso_options.png, "Swallowtail", with the back-swept wings extending wider and the base of the
stem sharper and longer; compact size; "Sash" livery):
  stepped needle prow -> swept guard (quillons) carrying the two Sforzando mounts -> narrow waist -> long swallowtail
  wings sweeping back and out past the engines, ending in DECORATIVE tip vanes that flare open in Bravura -> stern
  sponsons with the engines -> long, sharp, stepped tail spike.
Seams + livery are ONE idea (user: they must complement each other): a single dark-blue SASH runs from the needle down
  the spine, splits at the lattice core and runs out along both wings onto the vanes; a second, narrow arm runs down the
  stern to the tail spike. The sash's edges ARE the main seams (two continuous runs per side, no branching); the
  faction's biggest resonator cells sit inside it, slanted with it. Gradients only at the extremities (wing tips,
  spike). Bravura: finish.py also writes rsl_virtuoso_glow_bravura.png (same seams, radiant gold-white).
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from scale_spec import walk  # noqa: E402

SCALE = 1.08

r = lambda v: round(v, 2)


def P(x, y):
    return [r(x), r(y)]


# ------------------------------------------------------------------ polygon helpers (no shapely; as gen_halo.py)
def area(poly):
    return sum(poly[i][0] * poly[i - 1][1] - poly[i - 1][0] * poly[i][1] for i in range(len(poly))) / 2


def inset(poly, k, miter=3.0):
    """Offset a simple polygon inward by k (miter joins, clamped at sharp tips)."""
    s = -1 if area(poly) > 0 else 1
    n, out = len(poly), []
    for i in range(n):
        (x0, y0), (x1, y1), (x2, y2) = poly[i - 1], poly[i], poly[(i + 1) % n]
        e0, e1 = (x1 - x0, y1 - y0), (x2 - x1, y2 - y1)
        l0, l1 = math.hypot(*e0) or 1, math.hypot(*e1) or 1
        n0 = (-e0[1] / l0 * s, e0[0] / l0 * s)
        n1 = (-e1[1] / l1 * s, e1[0] / l1 * s)
        bx, by = n0[0] + n1[0], n0[1] + n1[1]
        bl = math.hypot(bx, by)
        if bl < 1e-6:
            bx, by, bl = n0[0], n0[1], 1
        cosh = max(1 / miter, (bx * n0[0] + by * n0[1]) / bl)
        d = k / cosh
        out.append((x1 + bx / bl * d, y1 + by / bl * d))
    return out


def clip(poly, axis, v0, v1):
    def cut(pts, keep, vc):
        res = []
        for i in range(len(pts)):
            a, b = pts[i - 1], pts[i]
            ka, kb = keep(a), keep(b)
            if ka != kb:
                t = (vc - a[axis]) / (b[axis] - a[axis])
                res.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
            if kb:
                res.append(b)
        return res
    pts = cut(poly, lambda p: p[axis] >= v0, v0)
    return cut(pts, lambda p: p[axis] <= v1, v1)


def region(poly, y0, y1, k=1.5, x0=-1e9, x1=1e9):
    return [P(x, y) for x, y in clip(clip(inset(poly, k), 1, y0, y1), 0, x0, x1)]


def half_region(poly, y0, y1, k=1.5):
    pts = clip(inset(poly, k), 1, y0, y1)
    xm = min(p[0] for p in pts)
    on_c = lambda p: p[0] < xm + 0.05
    top = min((i for i, p in enumerate(pts) if on_c(p)), key=lambda i: pts[i][1])
    pts = pts[top:] + pts[:top]
    if on_c(pts[1]):
        pts = [pts[0]] + list(reversed(pts[1:]))
    return [P(0 if on_c(p) else p[0], p[1]) for p in pts]


def closed(pts):
    return pts + [pts[0]]


FZ, PL, RL = [0, 3.0], [4.0, 6.2], [5.2, 7.6]


class Spec:
    def __init__(self):
        self.layers = []

    def frame(self, name, **shape):
        self.layers.append(dict({"name": name, "mat": "graphite", "z": FZ, "bevel": 0.6}, **shape))

    def plate(self, name, mat, z, tier=None, cuts=None, bevel=0.6, **shape):
        L = dict({"name": name, "mat": mat, "z": z, "bevel": bevel}, **shape)
        if cuts:
            L["cuts"] = cuts
        if tier:
            L["tiers"] = [tier]
        self.layers.append(L)


glow = lambda pts, w=1.5, d=2.0, sym=True: {"pts": pts, "w": w, "depth": d, "glow": True, "sym": sym}
groove = lambda pts, sym=True: {"pts": pts, "w": 0.55, "depth": 0.5, "sym": sym}


def clip_dir(poly, d, v0, v1):
    """Clip poly to the band v0 <= p . d <= v1 (d unit vector): segments perpendicular to a swept axis."""
    rot = [(p[0] * d[0] + p[1] * d[1], -p[0] * d[1] + p[1] * d[0]) for p in poly]
    band = clip([list(q) for q in rot], 0, v0, v1)
    return [P(a * d[0] - b * d[1], a * d[1] + b * d[0]) for a, b in band]


def along(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


# ================================================================== hull
H = 374
CORE = (0, 163)
# body (half): stepped needle prow -> swept guard (quillon) carrying the Sforzando mount -> narrow waist (wing roots)
# -> stern sponsons with the engines -> long sharp tail spike (user: "base of the stem sharper and longer")
BODY = [(0, 0), (2.2, 14), (3.2, 40), (6, 44), (7, 68), (10, 72), (11, 92),                 # stepped needle
        (15, 96), (18, 104), (30, 108), (46, 102),                                          # guard -> forward tooth
        (42, 116), (36, 132), (28, 138), (25, 146),                                         # guard trailing edge
        (25, 254), (22, 264), (31, 280), (36, 298), (34, 312), (12, 319),                   # waist, sponson, engines
        (8, 324), (7, 338), (5, 341), (4, 356), (0, 374)]                                   # stepped tail spike
# swallowtail wing (user: "back-swept wings extend wider"): long root along the waist, leading edge sweeping back
# and out to the vane mount; the deco vane carries the line on to the tip
WING = [(24, 148), (38, 164), (54, 196), (63, 199), (80, 244), (99, 298), (98, 311), (92, 318), (82, 317),
        (72, 306), (64, 300), (66, 292), (50, 288), (36, 280), (24, 270)]           # stepped tooth, trailing notch

# ---- the SASH: one dark-blue ribbon whose two edges are the ship's two main seams on each side.
#   outer seam: needle (2.2, 46) -> spine -> out along the wing to the vane mount
#   inner seam: vane mount -> back along the wing -> into the core V -> down the stern to the tail spike tip
U = (0.504, 0.864)                                   # wing/sash axis (unit), from the core towards the vane mount
SASH_OUT = [(2.2, 46), (3.6, 96), (4.6, 152), (90.0, 298.5)]
SASH_IN = [(78.0, 305.5), (3.0, 177.0), (3.0, 318), (2.4, 340), (0.8, 358)]
SASH = [(0, 44)] + SASH_OUT + SASH_IN + [(0, 362)]
WCELL = [(33.8, 215.9), (59.5, 260.0)]               # big resonator cells on the sash centre line

hs = Spec()
hs.frame("f_body", half=[P(*p) for p in BODY])
hs.frame("f_wing", sym_poly=[P(*p) for p in WING])

# --- needle: three stepped segments
hs.plate("n_tip", "ivory", RL, bevel=0.45, half=half_region(BODY, 1.2, 42.5, 1.0),
         tier={"inset": 0.7, "dz": 0.4, "mat": "ivory"})
hs.plate("n_mid", "ivory", RL, bevel=0.45, half=half_region(BODY, 45.5, 70.5, 1.0),
         tier={"inset": 0.8, "dz": 0.4, "mat": "ivory"})
hs.plate("n_root", "ivory2", RL, half=half_region(BODY, 73.5, 95, 1.1),
         tier={"inset": 0.9, "dz": 0.5, "mat": "ivory"})
# --- guard: armoured quillon plates + raised Sforzando mount housing
hs.plate("g_guard", "ivory", RL, sym_poly=region(BODY, 97, 145, 1.3, x0=12.5),
         tier={"inset": 1.2, "dz": 0.5, "mat": "ivory", "cuts": [groove([P(14, 128), P(30, 128)])]})
hs.plate("g_mount", "slate", [7.0, 9.2], bevel=0.45,
         sym_poly=[P(22, 110), P(36, 109), P(41, 116), P(37, 130), P(25, 133), P(19, 126)],
         tier={"inset": 1.0, "dz": 0.4, "mat": "ivory2"})
hs.plate("g_collar", "ivory2", RL, half=[P(0, 97.5), P(11.6, 97.5), P(12.4, 145), P(0, 145)],
         tier={"inset": 0.9, "dz": 0.4, "mat": "ivory"})
# --- waist / stern / engines / spike
hs.plate("b_waist", "ivory", PL, half=[P(0, 148), P(23.6, 148), P(23.6, 252), P(0, 252)],
         tier={"inset": 1.2, "dz": 0.5, "mat": "ivory"})
hs.plate("b_stern", "ivory2", PL, half=half_region(BODY, 253.5, 299, 1.3),
         tier={"inset": 1.2, "dz": 0.5, "mat": "ivory", "cuts": [groove([P(6, 276), P(24, 282)])]})
hs.plate("b_eng", "slate", PL, half=half_region(BODY, 301.5, 317, 1.1),
         tier={"inset": 0.9, "dz": 0.4, "mat": "slate"})
hs.plate("b_spike", "ivory", RL, bevel=0.45, half=half_region(BODY, 320, 373.5, 1.0),
         tier={"inset": 0.7, "dz": 0.4, "mat": "ivory"})
# sponson armour strakes beside the engines
hs.plate("strake", "slate", [6.2, 8.2], bevel=0.35, sym_poly=[P(25.6, 266), P(30.4, 281), P(34.4, 296), P(31, 298),
                                                            P(24, 284)])
# --- wings: three segments perpendicular to the sweep (clamps between), raised gunmetal leading-edge armour,
#     vane mount at the tip
for k, (v0, v1, mat) in enumerate(((144, 200, "ivory"), (204, 256, "ivory"), (260, 302, "ivory2"))):
    hs.plate("w_seg%d" % k, mat, RL, sym_poly=clip_dir(inset(WING, 1.3), U, v0, v1),
             tier={"inset": 1.2, "dz": 0.5, "mat": "ivory"})
for k, v in enumerate((202, 258)):
    hs.plate("w_clamp%d" % k, "slate", [6.6, 8.8], bevel=0.3, sym_poly=clip_dir(inset(WING, 0.6), U, v - 1.6, v + 1.6))
hs.plate("w_mount", "slate", [6.6, 9.0], bevel=0.4, sym_poly=clip_dir(inset(WING, 0.8), U, 305, 330),
         tier={"inset": 0.8, "dz": 0.3, "mat": "ivory2"})
hs.plate("w_edge1", "slate", [7.4, 8.8], bevel=0.3,
         sym_poly=[P(26.4, 151.2), P(38.8, 165.6), P(53.2, 194.2), P(50.4, 195.8), P(36.4, 168.6), P(25.6, 156.4)])
hs.plate("w_edge2", "slate", [7.4, 8.8], bevel=0.3,
         sym_poly=[P(64, 200.4), P(80.8, 244.4), P(97.2, 296), P(94.4, 297), P(78.2, 246.4), P(61.4, 203.2)])

FRAMES = ["f_body", "f_wing"]
cell_slant = 0.586 * 22                     # bottom-edge shift so the cells follow the sash (dx/dy of its edges)
details = [
    {"type": "node", "pos": list(CORE), "r": 6.8, "shape": "diamond"},
    # the two seams per side ARE the sash edges (one continuous run each, no branching)
    {"type": "conduit", "pos": [0, 0], "pts": [P(*p) for p in SASH_OUT], "w": 1.25, "sym": True},
    {"type": "conduit", "pos": [0, 0], "pts": [P(*p) for p in SASH_IN], "w": 1.25, "sym": True},
    {"type": "node", "pos": P(86.5, 303), "r": 2.4, "sym": True},                     # sash end -> vane mount
    {"type": "node", "pos": P(0, 364), "r": 1.6},                                     # spike tip
    # the faction's biggest resonator cells, inside the sash, slanted with it; a small nose glyph
    *[{"type": "cell", "pos": [r(sg * (c[0] - cell_slant / 2)), c[1]], "size": [8.4, 22], "n": 5, "v": 1.6,
       "slant": r(sg * cell_slant)} for c in WCELL for sg in (1, -1)],        # explicit L/R: slant is not mirrored
    {"type": "cell", "pos": [0, 120], "size": [5, 9], "n": 3, "v": 1.0},
    {"type": "vent", "pos": [14, 292], "w": 8, "n": 4, "step": 1.2, "sym": True},
    {"type": "vent", "pos": [12, 230], "w": 7, "n": 4, "step": 1.2, "sym": True},
    {"type": "block", "pos": [38, 122], "size": [2.4, 6], "h": 0.4, "mat": "steel", "sym": True},
    {"type": "hatch", "pos": P(14, 200), "r": 1.6, "sym": True},
    {"type": "light", "pos": P(46, 103), "r": 0.5, "sym": True},
]
VANE_PIVOT, VANE_ANG = (86.5, 310), -161.6          # vane points aft-outward along the wing's sweep
slots = [
    # Sforzando Lances (built-in, ~300 deg arcs) on the guard mounts
    {"id": "WS0001", "pos": P(30, 121), "size": "LARGE", "type": "ENERGY", "mount": "TURRET", "angle": 10, "arc": 300, "sym": True},
    {"id": "WS0002", "pos": P(54, 214), "size": "MEDIUM", "type": "ENERGY", "mount": "TURRET", "angle": 45, "arc": 240, "sym": True},
    {"id": "WS0003", "pos": P(19, 289), "size": "MEDIUM", "type": "HYBRID", "mount": "TURRET", "angle": 140, "arc": 220, "sym": True},
    {"id": "WS0004", "pos": P(7.5, 82), "size": "SMALL", "type": "ENERGY", "mount": "TURRET", "angle": 5, "arc": 200, "sym": True},
    {"id": "WS0005", "pos": P(72, 256), "size": "SMALL", "type": "ENERGY", "mount": "TURRET", "angle": 70, "arc": 220, "sym": True},
    {"id": "WS0006", "pos": P(14, 212), "size": "SMALL", "type": "ENERGY", "mount": "TURRET", "angle": 90, "arc": 200, "sym": True},
    # tip vanes (deco): flare open in Bravura
    {"id": "WS0007", "pos": P(*VANE_PIVOT), "size": "MEDIUM", "type": "DECORATIVE", "mount": "HARDPOINT",
     "angle": VANE_ANG, "arc": 0, "deco": "rsl_virtuoso_vane_r", "deco_alt_angle": VANE_ANG + 22},
    {"id": "WS0008", "pos": P(-VANE_PIVOT[0], VANE_PIVOT[1]), "size": "MEDIUM", "type": "DECORATIVE",
     "mount": "HARDPOINT", "angle": -VANE_ANG, "arc": 0, "deco": "rsl_virtuoso_vane_l",
     "deco_alt_angle": -(VANE_ANG + 22)},
]
engines = [{"pos": [17, 317.6], "width": 6, "sym": True}, {"pos": [27, 315], "width": 7, "sym": True}]
livery = [
    # the sash (crisp, one cohesive shape; its edges are the conduits above)
    {"type": "poly", "color": "navy", "poly": [P(*p) for p in SASH], "sym": True},
    # steel tone bands parallel to the sash on the wings (tonal, not paint: the plates echo the sash)
    {"type": "splinter", "tones": [1.0, 0.76, 1.0, 0.84, 1.0, 0.72], "widths": [10, 5, 14, 4, 8, 6], "angle": -30.3,
     "mirror": True, "poly": [P(0, 140), P(104, 140), P(104, 322), P(0, 322)]},
    # gradients only at the extremities: wing tips deepen towards the vane mounts, the tail spike darkens to its tip
    {"type": "gradient", "color": "navy", "poly": [P(*p) for p in WING], "a": [62, 250], "b": [94, 306],
     "a0": 0.0, "a1": 0.55},
    {"type": "gradient", "color": "navy", "poly": [P(0, 320), P(10, 320), P(10, 374), P(0, 374)], "a": [0, 326],
     "b": [0, 372], "a0": 0.0, "a1": 0.6},
    {"type": "poly", "color": "gunmetal", "poly": [P(-2.2, 0), P(2.2, 0), P(2.8, 10), P(-2.8, 10)]},
]
for part in (hs.layers, details, slots, engines, livery):
    walk(part, SCALE)
W = 2 * int(max(p[0] for p in WING) * SCALE + 10)                    # + room for the flared vanes
hull = {"id": "rsl_virtuoso", "name": "Virtuoso", "hullSize": "CAPITAL_SHIP",
        "size": [W, int(math.ceil(H * SCALE))], "layers": hs.layers,
        "greebles": {"layers": FRAMES, "z0": 3.0, "zmax": 3.9, "density": 1.0, "seed": 91},
        "surface_detail": {"layers": ["b_waist", "b_stern"], "density": 0.02, "seed": 37},
        "details": details, "slots": slots, "engines": engines, "livery": livery, "bravura_glow": True,
        "ship": {"builtInMods": ["auxiliarythrusters"]}}

# ================================================================== tip vane (R; pivot = image centre = vane root)
# Sprite points UP (tip at the top). At slot angle ~-162 the sprite is turned to point aft, so sprite -x faces the
# ship's outside: the straight OUTER edge is on sprite -x and runs on to the point, the inner edge slants into it.
VL = round(56 * SCALE)
VW, VH = 16, 2 * (VL + 8)
PY = VH / 2
vs = Spec()
VANE = [P(-5.4, PY - VL), P(-6.4, PY - 20), P(-6.4, PY + 6), P(6.4, PY + 6), P(6.4, PY - 6), P(4.6, PY - 10),
        P(5.4, PY - 18), P(0.6, PY - 40)]
vs.frame("vf_vane", poly=VANE, z=[0, 2.4], bevel=0.45)
vs.plate("vp_blade", "ivory", [3.2, 5.4], bevel=0.45,
         poly=[P(-4.6, PY - VL + 4), P(-5.4, PY - 20), P(-5.4, PY - 3), P(4.2, PY - 3), P(4.2, PY - 7),
               P(3.6, PY - 10), P(4.2, PY - 17.6), P(-0.2, PY - 38.6)],
         tier={"inset": 0.9, "dz": 0.4, "mat": "ivory",
               "cuts": [{"pts": [P(-3.6, PY - VL + 9), P(-4.0, PY - 6)], "w": 0.9, "depth": 1.3, "glow": True},
                        {"pts": [P(-1.6, PY - 34), P(2.2, PY - 16), P(2.2, PY - 6)], "w": 0.9, "depth": 1.3,
                         "glow": True}]})
vs.plate("vp_root", "slate", [3.4, 6.0], bevel=0.5, poly=[P(-6, PY - 1.6), P(6, PY - 1.6), P(6, PY + 5.4),
                                                          P(-6, PY + 5.4)],
         tier={"inset": 0.9, "dz": 0.4, "mat": "ivory2"})
vane_details = [
    {"type": "node", "pos": P(0, PY + 2), "r": 2.0, "shape": "diamond"},
    {"type": "cell", "pos": [-1.2, PY - 20], "size": [3.6, 12], "n": 3, "v": 1.0, "slant": -0.8},
]
# the sash runs on along the vane between its two glow lines, deepening to the tip
vane_livery = [{"type": "poly", "color": "navy", "poly": [P(-3.4, PY - VL + 8), P(-1.2, PY - 34), P(1.6, PY - 16),
                                                          P(1.6, PY - 4), P(-3.4, PY - 4)]},
               {"type": "gradient", "color": "navy", "a": [0, PY - 10], "b": [0, PY - VL], "a0": 0.0, "a1": 0.5}]
vane = {"id": "rsl_virtuoso_vane_r", "kind": "deco", "size": [VW, int(VH)], "layers": vs.layers,
        "greebles": {"layers": ["vf_vane"], "z0": 2.4, "zmax": 3.1, "density": 1.0, "seed": 13},
        "details": vane_details, "livery": [dict(L, sym=False, mirror=False) for L in vane_livery],
        "bravura_glow": True}

d = os.path.dirname(sys.argv[1])
json.dump(hull, open(sys.argv[1], "w", newline="\n"), indent=1)
json.dump(vane, open(os.path.join(d, "rsl_virtuoso_vane_r.json"), "w", newline="\n"), indent=1)
json.dump({"id": "rsl_virtuoso_vane_l", "kind": "deco", "mirror_of": "rsl_virtuoso_vane_r"},
          open(os.path.join(d, "rsl_virtuoso_vane_l.json"), "w", newline="\n"), indent=1)
print("W", W, "H", H, "| vane", VW, "x", int(VH))
