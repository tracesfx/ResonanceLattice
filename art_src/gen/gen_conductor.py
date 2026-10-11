"""Generate art_src/specs/rsl_conductor.json and the inner emitter blade decos rsl_conductor_blade_{r,l}.json.

python art_src/gen/gen_conductor.py art_src/specs/rsl_conductor.json
./art_src/art.sh rsl_conductor rsl_conductor_blade_r rsl_conductor_blade_l

Direction chosen by the user (2026-10-11, option C of art_src/review/conductor_options.png, "Split blade"):
  ONE solid blade body that splits only at the bow (unlike the Tremolo's twin hulls). Two short spear prongs with
  stepped, toothed outer edges; an open slot between them in which the spinal Harmonic Driver barrel lies (barrel
  baked into the hull, rooted in a long raised breech cradle that carries the lattice core) -> broad shoulders ->
  forward-swept crossguard wings with sharp tips and emitter leading edges -> tapering waist with a flare tooth ->
  stern -> swept-back engine fins -> stepped engine block.
  Prongs: an inner emitter blade on each prong is a DECORATIVE part (user's choice) that folds in towards the barrel
  while Sympathetic Strike charges (deco_alt_angle +-7), then snaps back. R blade + pixel-mirrored L blade.
Livery: "tempered blade": prongs darken towards the tips, crossguards carry one bold dark-blue band parallel to the
  leading edge, midship irregular splinter (steep slant), waist gradient deepening to the flanks, stern "fermata"
  chevrons pointing forward, engine block gradient.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from scale_spec import walk  # noqa: E402

SCALE = 1.0

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

# ================================================================== hull
H = 410
CORE = (0, 190)
# right half: from the slot floor on the centre line, up the prong's inner face, round the spear tip, down the
# toothed outer edge, out along the crossguard, down the waist and stern, closing on the centre line at the stern.
HULL = [(0, 84), (16, 77),                                                 # slot floor (V) -> prong inner face
        (16, 46), (18, 38), (20, 18), (24, 0),                             # inner face, chamfer, spear tip
        (30, 16), (36, 18), (44, 34), (59, 41),                            # stepped outer edge -> swept tooth
        (52, 54), (58, 64), (64, 90), (73, 95), (65, 106), (66, 128),      # deep notch, flank, 2nd tooth, notch
        (72, 136), (74, 156),                                              # prong root -> shoulder
        (106, 162), (124, 146),                                            # crossguard leading edge -> swept tip
        (121, 160), (116, 184), (104, 204), (90, 208), (84, 218),          # guard outer edge, diagonal cut, step
        (70, 236), (58, 262), (78, 292), (70, 298), (60, 306),             # waist slants in, flare tooth
        (52, 344), (74, 378), (68, 384), (50, 376),                        # stern slants in, swept engine fin
        (44, 388), (38, 392), (40, 400), (33, 410), (0, 410)]              # stepped engine block, tail tooth

hs = Spec()
hs.frame("f_hull", half=[P(*p) for p in HULL])

# --- plates: inset bands of the frame outline (gaps between them expose machinery)
hs.plate("h_prong1", "ivory", RL, bevel=0.5, sym_poly=region(HULL, 1.5, 49, 1.3),
         tier={"inset": 1.2, "dz": 0.5, "mat": "ivory",
               "cuts": [groove([P(21, 32), P(40, 32)])]})
hs.plate("h_prong2", "ivory2", RL, sym_poly=region(HULL, 52, 126, 1.4, x0=17),
         tier={"inset": 1.4, "dz": 0.6, "mat": "ivory",
               "cuts": [glow([P(30, 60), P(30, 120)], 1.2, 1.7), groove([P(32, 86), P(60, 86)])]})
hs.plate("h_shoulder", "ivory", PL, sym_poly=region(HULL, 129, 152, 1.4, x0=21),
         tier={"inset": 1.4, "dz": 0.5, "mat": "ivory"})
hs.plate("h_guard", "ivory", RL, bevel=0.5, sym_poly=region(HULL, 140, 222, 1.4, x0=75),
         tier={"inset": 1.3, "dz": 0.6, "mat": "ivory",
               "cuts": [glow([P(80, 166), P(106, 168), P(119, 154)], 1.2, 1.7),
                        groove([P(88, 200), P(112, 180)])]})
hs.plate("h_mid", "ivory2", PL, sym_poly=region(HULL, 155, 240, 1.5, x1=72),
         tier={"inset": 1.5, "dz": 0.6, "mat": "ivory",
               "cuts": [groove([P(24, 218), P(60, 210)])]})
hs.plate("h_waist", "ivory", PL, sym_poly=region(HULL, 243, 304),
         tier={"inset": 1.5, "dz": 0.6, "mat": "ivory",
               "cuts": [groove([P(28, 270), P(56, 270)])]})
hs.plate("h_stern", "ivory2", PL, sym_poly=region(HULL, 307, 362),
         tier={"inset": 1.5, "dz": 0.6, "mat": "ivory",
               "cuts": [groove([P(8, 336), P(46, 330)])]})
hs.plate("h_fin", "ivory", RL, bevel=0.5, sym_poly=[P(53.5, 348), P(71, 375), P(67.6, 380), P(51.6, 372.6)],
         tier={"inset": 0.8, "dz": 0.4, "mat": "ivory", "cuts": [glow([P(54, 354), P(66, 373)], 1.0, 1.5)]})
hs.plate("h_eng", "slate", PL, sym_poly=region(HULL, 365, 409, 1.4, x1=46),
         tier={"inset": 1.4, "dz": 0.5, "mat": "slate", "cuts": [groove([P(6, 392), P(36, 392)])]})
# flare tooth armour + guard root clamps
hs.plate("tooth", "slate", [5.6, 7.6], bevel=0.4, sym_poly=[P(60, 270), P(74.6, 290.6), P(69.6, 295), P(57, 288)],
         cuts=[glow([P(61, 275), P(70, 289)], 0.9, 1.3)])
hs.plate("gclamp", "slate", [6.4, 8.6], bevel=0.4, sym_poly=[P(70, 160), P(80, 162), P(80, 214), P(72, 220),
                                                               P(68, 200)],
         tier={"inset": 0.9, "dz": 0.4, "mat": "ivory2"})
hs.plate("pclamp", "slate", [6.4, 8.6], bevel=0.4, sym_poly=[P(22, 122), P(44, 122), P(48, 132), P(24, 136)],
         tier={"inset": 0.8, "dz": 0.3, "mat": "ivory2"})
# spinal Harmonic Driver: breech cradle (carries the core) + barrel with muzzle brake + coil collars
CRADLE = [P(0, 112), P(9, 114), P(17, 124), P(19, 150), P(24, 162), P(24, 206), P(16, 222), P(14, 240),
          P(8, 248), P(0, 250)]
hs.plate("cradle", "slate", [7.0, 9.4], bevel=0.5, half=CRADLE,
         tier={"inset": 1.6, "dz": 0.5, "mat": "ivory2",
               "cuts": [glow([P(12, 130), P(12, 156), P(18, 166), P(18, 200)], 1.2, 1.7),
                        groove([P(4, 232), P(12, 224)])]})
hs.plate("barrel", "slate", [9.6, 12.0], bevel=0.6,
         half=[P(0, 26), P(4, 26), P(5.2, 30), P(5.2, 114), P(7, 120), P(7, 150), P(0, 150)],
         cuts=[glow([P(0, 34), P(0, 108)], 1.1, 1.6, False)])
hs.plate("muzzle", "slate", [10.4, 12.6], bevel=0.4, half=[P(0, 20), P(5, 21), P(7, 25), P(7, 33), P(0, 34)],
         cuts=[groove([P(1, 27), P(6, 27)])])
for k, y in enumerate((50, 72, 94)):
    hs.plate("collar%d" % k, "ivory2", [10.2, 12.4], bevel=0.3,
             half=[P(0, y), P(6.4, y + 1), P(6.4, y + 5), P(0, y + 6)])
# aft keel
hs.plate("keel", "slate", [6.6, 8.6], half=[P(0, 252), P(6, 256), P(6.4, 330), P(4, 396), P(0, 398)],
         tier={"inset": 0.8, "dz": 0.4, "mat": "ivory2", "cuts": [glow([P(0, 262), P(0, 390)], 1.1, 1.6, False)]})

FRAMES = ["f_hull"]
details = [
    {"type": "node", "pos": list(CORE), "r": 7.0, "shape": "diamond"},
    {"type": "cell", "pos": [0, 126], "size": [3.6, 5], "n": 2, "v": 0.9},                  # glyph on the breech
    # core -> crossguard emitters, -> prong roots (blade pivots), -> waist turrets, -> engines
    {"type": "conduit", "pos": [0, 0], "pts": [P(8, 184), P(28, 184), P(40, 172), P(80, 172)], "w": 1.2, "sym": True},
    {"type": "node", "pos": P(81, 172), "r": 2.2, "sym": True},
    {"type": "conduit", "pos": [0, 0], "pts": [P(20, 158), P(30, 148), P(30, 138)], "w": 1.1, "sym": True},
    {"type": "node", "pos": P(30, 137), "r": 2.0, "sym": True},
    {"type": "conduit", "pos": [0, 0], "pts": [P(8, 200), P(20, 212), P(34, 212), P(46, 224), P(46, 266)],
     "w": 1.1, "sym": True},
    {"type": "conduit", "pos": [0, 0], "pts": [P(12, 300), P(30, 318), P(30, 380)], "w": 1.1, "sym": True},
    {"type": "node", "pos": P(30, 382), "r": 1.9, "sym": True},
    {"type": "node", "pos": P(0, 254), "r": 2.4},
    # resonator cells: prong pair, midship pair, stern pair
    {"type": "cell", "pos": [42, 110], "size": [7, 14], "n": 4, "v": 1.3, "sym": True},
    {"type": "cell", "pos": [52, 196], "size": [8, 18], "n": 4, "v": 1.4, "sym": True},
    {"type": "cell", "pos": [36, 332], "size": [6.4, 13], "n": 3, "v": 1.2, "sym": True},
    {"type": "vent", "pos": [100, 194], "w": 9, "n": 5, "step": 1.3, "sym": True},
    {"type": "vent", "pos": [18, 356], "w": 10, "n": 5, "step": 1.3, "sym": True},
    {"type": "vent", "pos": [46, 288], "w": 7, "n": 4, "step": 1.3, "sym": True},
    {"type": "block", "pos": [58, 74], "size": [3, 7], "h": 0.5, "mat": "steel", "sym": True},
    {"type": "block", "pos": [52, 322], "size": [3, 6], "h": 0.4, "mat": "steel", "sym": True},
    {"type": "hatch", "pos": P(44, 150), "r": 1.8, "sym": True},
    {"type": "light", "pos": P(24, 3), "r": 0.6, "sym": True},
    {"type": "light", "pos": P(122, 150), "r": 0.6, "sym": True},
    {"type": "light", "pos": P(72, 379), "r": 0.5, "sym": True},
    {"type": "mark", "pos": [0, 0], "pts": [P(96, 204), P(108, 192)], "w": 0.7, "sym": True},
    {"type": "mark", "pos": [0, 0], "pts": [P(99, 206), P(111, 194)], "w": 0.7, "sym": True},
]
BLADE_PIVOT = (21, 118)
slots = [
    # spinal Harmonic Driver (barrel baked into the hull; the weapon sprite will only be muzzle glow / charge FX)
    {"id": "WS0001", "pos": [0, 24], "size": "LARGE", "type": "ENERGY", "mount": "HARDPOINT", "angle": 0, "arc": 5},
    {"id": "WS0002", "pos": P(96, 182), "size": "LARGE", "type": "ENERGY", "mount": "TURRET", "angle": 30, "arc": 210, "sym": True},
    {"id": "WS0003", "pos": P(40, 74), "size": "MEDIUM", "type": "ENERGY", "mount": "TURRET", "angle": 10, "arc": 210, "sym": True},
    {"id": "WS0004", "pos": P(31, 28), "size": "SMALL", "type": "ENERGY", "mount": "TURRET", "angle": 0, "arc": 270, "sym": True},
    {"id": "WS0005", "pos": P(40, 230), "size": "MEDIUM", "type": "HYBRID", "mount": "TURRET", "angle": 60, "arc": 240, "sym": True},
    {"id": "WS0006", "pos": P(40, 280), "size": "MEDIUM", "type": "ENERGY", "mount": "TURRET", "angle": 110, "arc": 220, "sym": True},
    {"id": "WS0007", "pos": [0, 282], "size": "LARGE", "type": "ENERGY", "mount": "TURRET", "angle": 180, "arc": 300},
    {"id": "WS0008", "pos": P(60, 294), "size": "SMALL", "type": "ENERGY", "mount": "TURRET", "angle": 140, "arc": 200, "sym": True},
    {"id": "WS0009", "pos": P(36, 354), "size": "SMALL", "type": "MISSILE", "mount": "TURRET", "angle": 160, "arc": 180, "sym": True},
    # inner emitter blades (fold in towards the barrel while Sympathetic Strike charges)
    {"id": "WS0010", "pos": P(*BLADE_PIVOT), "size": "MEDIUM", "type": "DECORATIVE", "mount": "HARDPOINT", "angle": 0,
     "arc": 0, "deco": "rsl_conductor_blade_r", "deco_alt_angle": 7},
    {"id": "WS0011", "pos": P(-BLADE_PIVOT[0], BLADE_PIVOT[1]), "size": "MEDIUM", "type": "DECORATIVE",
     "mount": "HARDPOINT", "angle": 0, "arc": 0, "deco": "rsl_conductor_blade_l", "deco_alt_angle": -7},
]
engines = [{"pos": [10, 410], "width": 9, "sym": True}, {"pos": [25, 410], "width": 9, "sym": True}]
livery = [
    # prongs: deepen towards the spear tips
    {"type": "gradient", "color": "navy", "poly": [P(14, 0), P(76, 0), P(76, 130), P(14, 130)], "a": [0, 128],
     "b": [0, 2], "a0": 0.15, "a1": 0.7},
    # crossguards: gradient to the tip + one bold band parallel to the leading edge
    {"type": "gradient", "color": "navy", "poly": [P(74, 140), P(126, 140), P(126, 222), P(74, 222)], "a": [76, 200],
     "b": [122, 152], "a0": 0.15, "a1": 0.8},
    {"type": "band", "pts": [P(84, 184), P(106, 178), P(118, 166)], "w": 6, "color": "navy", "sym": True, "alpha": 0.9},
    # shoulders + midship: deepen from the spine outward (under the splinter)
    {"type": "gradient", "color": "navy", "poly": [P(0, 128), P(76, 128), P(76, 242), P(0, 242)], "a": [10, 0],
     "b": [74, 0], "a0": 0.1, "a1": 0.6},
    # midship: irregular steep splinter
    {"type": "splinter", "color": "navy", "colors": [None, "navy", None, "navy", None],
     "widths": [22, 9, 30, 6, 18], "angle": 62, "zigzag": False, "alpha": 0.6, "mirror": True,
     "poly": [P(0, 152), P(74, 152), P(74, 242), P(0, 242)]},
    # waist: deepen to the flanks; stern: forward-pointing "fermata" chevrons; engine block gradient
    {"type": "gradient", "color": "navy", "poly": [P(0, 242), P(84, 242), P(84, 306), P(0, 306)], "a": [14, 0],
     "b": [74, 0], "a0": 0.2, "a1": 0.8},
    {"type": "band", "pts": [P(0, 318), P(58, 344)], "w": 7, "color": "navy", "sym": True, "alpha": 0.85},
    {"type": "band", "pts": [P(0, 334), P(52, 358)], "w": 3, "color": "navy", "sym": True, "alpha": 0.8},
    {"type": "gradient", "color": "navy", "poly": [P(0, 306), P(82, 306), P(82, 362), P(0, 362)], "a": [0, 308],
     "b": [0, 362], "a0": 0.15, "a1": 0.6},
    {"type": "gradient", "color": "navy", "a": [0, 364], "b": [0, 404], "a0": 0.35, "a1": 0.95},
    {"type": "gradient", "color": "navy", "poly": [P(46, 344), P(76, 344), P(76, 384), P(46, 384)], "a": [50, 352],
     "b": [72, 378], "a0": 0.1, "a1": 0.8},
    {"type": "poly", "color": "gunmetal", "poly": [P(20.6, 6), P(24, 1), P(27.4, 9), P(22.6, 13)], "sym": True},
]
for part in (hs.layers, details, slots, engines, livery):
    walk(part, SCALE)
W = 2 * int(max(p[0] for p in HULL) * SCALE + 3)
hull = {"id": "rsl_conductor", "name": "Conductor", "hullSize": "CAPITAL_SHIP",
        "size": [W, int(math.ceil(H * SCALE))], "layers": hs.layers,
        "greebles": {"layers": FRAMES, "z0": 3.0, "zmax": 3.9, "density": 1.0, "seed": 73},
        "surface_detail": {"layers": ["h_mid", "h_waist", "h_stern"], "density": 0.012, "seed": 31},
        "details": details, "slots": slots, "engines": engines, "livery": livery,
        "ship": {"builtInMods": ["stabilizedshieldemitter", "operations_center"]}}

# ================================================================== inner emitter blade (R; pivot = image centre)
BL = 84                                  # pivot -> tip
BW, BH = 18, 2 * (BL + 6)                # sprite size (even); the pivot sits at the sprite centre
PY = BH / 2
bs = Spec()
# sprite x: + = outboard (ship +x at angle 0), tip at the top. Inner edge (facing the barrel) is the emitter.
BLADE = [P(-3, PY - BL), P(5, PY - BL + 18), P(5, PY - 40), P(4, PY - 37), P(6, PY - 34), P(6, PY - 6),
         P(7, PY - 2), P(7, PY + 5), P(-6, PY + 5), P(-6, PY - 4), P(-4.6, PY - 10), P(-4.6, PY - BL + 8)]
bs.frame("bf_blade", poly=BLADE, z=[0, 2.4], bevel=0.5)
bs.plate("bp_seg1", "ivory", [3.2, 5.4], bevel=0.5,
         poly=[P(-2.2, PY - BL + 4), P(3.8, PY - BL + 18.5), P(3.8, PY - 42), P(-3.4, PY - 42), P(-3.4, PY - BL + 9)],
         tier={"inset": 1.0, "dz": 0.4, "mat": "ivory",
               "cuts": [{"pts": [P(-1.6, PY - BL + 12), P(-1.6, PY - 44)], "w": 1.0, "depth": 1.3, "glow": True},
                        {"pts": [P(-2.6, PY - 60), P(3.0, PY - 62)], "w": 0.5, "depth": 0.45}]})
bs.plate("bp_seg2", "ivory", [3.2, 5.4], bevel=0.5,
         poly=[P(-3.4, PY - 39), P(3.0, PY - 39), P(4.8, PY - 35), P(4.8, PY - 12), P(-3.4, PY - 12)],
         tier={"inset": 1.0, "dz": 0.4, "mat": "ivory",
               "cuts": [{"pts": [P(-1.6, PY - 37), P(-1.6, PY - 14)], "w": 1.0, "depth": 1.3, "glow": True}]})
bs.plate("bp_root", "slate", [3.4, 6.0], bevel=0.6,
         poly=[P(-5, PY - 9), P(5.4, PY - 9), P(6.2, PY - 4), P(6.2, PY + 4), P(-5, PY + 4)],
         tier={"inset": 1.0, "dz": 0.4, "mat": "ivory2"})
blade_details = [
    {"type": "node", "pos": P(0.5, PY - 1.5), "r": 2.0, "shape": "diamond"},
    {"type": "node", "pos": P(-1.6, PY - BL + 11), "r": 1.3},
    {"type": "node", "pos": P(-1.6, PY - 40.5), "r": 1.4},
    {"type": "cell", "pos": [1.8, PY - 26], "size": [4.4, 12], "n": 4, "v": 1.2},
    {"type": "cell", "pos": [1.6, PY - 56], "size": [3.8, 10], "n": 3, "v": 1.1},
    {"type": "light", "pos": P(-2.6, PY - BL + 2.5), "r": 0.5},
]
blade_livery = [{"type": "gradient", "color": "navy", "a": [0, PY - BL], "b": [0, PY - 20], "a0": 0.85, "a1": 0.0},
                {"type": "poly", "color": "gunmetal", "poly": [P(3, PY - 33), P(4.8, PY - 35), P(4.8, PY - 12),
                                                               P(3, PY - 12)]}]
blade = {"id": "rsl_conductor_blade_r", "kind": "deco", "size": [BW, int(BH)], "layers": bs.layers,
         "greebles": {"layers": ["bf_blade"], "z0": 2.4, "zmax": 3.1, "density": 1.0, "seed": 9},
         "details": blade_details, "livery": [dict(L, sym=False, mirror=False) for L in blade_livery]}

d = os.path.dirname(sys.argv[1])
json.dump(hull, open(sys.argv[1], "w", newline="\n"), indent=1)
json.dump(blade, open(os.path.join(d, "rsl_conductor_blade_r.json"), "w", newline="\n"), indent=1)
json.dump({"id": "rsl_conductor_blade_l", "kind": "deco", "mirror_of": "rsl_conductor_blade_r"},
          open(os.path.join(d, "rsl_conductor_blade_l.json"), "w", newline="\n"), indent=1)
print("W", W, "H", H, "| blade", BW, "x", int(BH))
