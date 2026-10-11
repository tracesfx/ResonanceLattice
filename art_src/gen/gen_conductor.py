"""Generate art_src/specs/rsl_conductor.json and the inner emitter blade decos rsl_conductor_blade_{r,l}.json.

python art_src/gen/gen_conductor.py art_src/specs/rsl_conductor.json
./art_src/art.sh rsl_conductor rsl_conductor_blade_r rsl_conductor_blade_l

Direction chosen by the user (2026-10-11, option C of art_src/review/conductor_options.png, "Split blade"):
  ONE blade that splits only at the bow. v2 (user: v1 "extremely bulky, tin-foil like", gradients uncohesive, dots
  are no substitute for intricacy): a slim segmented spine built from distinct parts --
  two stepped spear prongs (tip / mid / root segments + gunmetal clamps) joined by a muzzle yoke that braces the
  spinal Harmonic Driver barrel (the slot between prongs, yoke and breech is an open window) -> long breech cradle
  with coil rings, capacitor housings and the lattice core -> segmented forward-swept crossguard wings (root housing,
  two segments, tip blade, clamps, emitter leading edges) -> slim waist with side strakes -> tapering stern;
  two engine nacelles sweep out and aft from a 60 px root (open V notch behind, like fletching) -> engine block.
  Inner emitter blades on the prongs = DECORATIVE parts that fold in towards the barrel while Sympathetic Strike
  charges (deco_alt_angle +-7). R blade + pixel-mirrored L blade.
Livery "dipped tips + spine stripes": crisp dark-blue caps on prong and wing tips, one bold stripe each side of the
  keel; gradients only at the extremities (into the wing caps, nacelle fins) and deepening towards the stern.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from scale_spec import walk  # noqa: E402

SCALE = 1.07

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
# v2 (user feedback on v1: "extremely bulky, tin-foil like"; gradients uncohesive; dots are no substitute for
# detail): a slim segmented spine instead of one broad envelope; every mass is its own part with clamps and
# machinery gaps between; dark blue only at the extremities + bold spine stripes.
H = 444
CORE = (0, 160)


def prong_outline():
    # inner face, chamfer, spear tip, then the outer edge stepping out every ~30 px (stepped spear), root
    return [(14, 150), (14, 40), (17, 30), (21, 0), (25, 12), (27, 26), (31, 30), (33, 54), (38, 58), (40, 86),
            (45, 91), (46, 120), (51, 125), (52, 150)]


PRONG = prong_outline()
BODY = [(0, 148), (16, 145), (52, 144), (55, 150), (44, 160), (40, 176), (40, 256), (38, 262), (34, 296),
        (34, 340), (30, 400), (28, 414), (28, 428), (22, 444), (0, 444)]
# nacelles sweep out and aft: rooted along the body for 60 px, then an open V notch behind (arrow fletching)
POD = [(35, 296), (44, 291), (52, 299), (62, 352), (72, 390), (85, 412), (68, 404), (66, 414), (52, 414),
       (46, 396), (38, 352), (34, 320)]

# --- forward-swept crossguard wing, built like the Cadence barb: point = C(t along, s across; + = leading edge)
WA, WB = (36.0, 224.0), (118.0, 166.0)
WLEN = math.hypot(WB[0] - WA[0], WB[1] - WA[1])
WD = ((WB[0] - WA[0]) / WLEN, (WB[1] - WA[1]) / WLEN)
WN = (WD[1], -WD[0])                                  # leading-edge normal (points forward)


def C(t, s=0.0):
    return (WA[0] + (WB[0] - WA[0]) * t + WN[0] * s, WA[1] + (WB[1] - WA[1]) * t + WN[1] * s)


def CP(t, s=0.0):
    return P(*C(t, s))


WTIP = 1.10
WING = [C(0, -17), C(0, 16), C(0.38, 16), C(0.39, 13.5), C(0.70, 13.5), C(0.71, 11), C(WTIP, 9), C(0.86, -6),
        C(0.70, -7.5), C(0.69, -10), C(0.39, -9), C(0.38, -13)]


def wseg(t0, t1, s_in0, s_in1, s_out, c=1.6):
    """Wing segment: straight leading edge (chamfered corners), trailing edge tapering s_in0 -> s_in1."""
    dt = c / WLEN
    return [CP(t0, s_in0), CP(t0, s_out - c), CP(t0 + dt, s_out), CP(t1 - dt, s_out), CP(t1, s_out - c), CP(t1, s_in1)]


hs = Spec()
hs.frame("f_body", half=[P(*p) for p in BODY])
hs.frame("f_prong", sym_poly=[P(*p) for p in PRONG])
hs.frame("f_wing", sym_poly=[P(*p) for p in WING])
hs.frame("f_pod", sym_poly=[P(*p) for p in POD])

# --- prongs: three segments (tip / mid / root) separated by gunmetal clamps
hs.plate("p_tip", "ivory", RL, bevel=0.5, sym_poly=region(PRONG, 1.5, 52, 1.2),
         tier={"inset": 1.0, "dz": 0.5, "mat": "ivory", "cuts": [groove([P(18, 34), P(29, 34)])]})
hs.plate("p_mid", "ivory2", RL, sym_poly=region(PRONG, 60, 99, 1.3, x0=27),
         tier={"inset": 1.2, "dz": 0.5, "mat": "ivory"})
hs.plate("p_root", "ivory", RL, sym_poly=region(PRONG, 103, 148, 1.3, x0=27),
         tier={"inset": 1.2, "dz": 0.5, "mat": "ivory", "cuts": [glow([P(33, 108), P(33, 144)], 1.1, 1.6)]})
hs.plate("p_inner", "slate", [5.6, 7.6], bevel=0.4, sym_poly=region(PRONG, 56, 148, 1.3, x1=26))
for k, (y0, y1, xo) in enumerate(((53.5, 59, 37), (99.5, 104, 44.4))):
    hs.plate("p_clamp%d" % k, "slate", [6.6, 8.8], bevel=0.35,
             sym_poly=[P(13.4, y0), P(xo, y0 - 0.6), P(xo + 1.4, (y0 + y1) / 2), P(xo, y1 + 0.6), P(13.4, y1)])
# muzzle yoke: braces the barrel between the prong tips, closing the slot into a window
hs.plate("yoke", "slate", [8.0, 10.6], bevel=0.4,
         half=[P(0, 43), P(12, 43), P(16, 41), P(18, 45), P(18, 50), P(14, 53), P(0, 53)],
         tier={"inset": 0.8, "dz": 0.4, "mat": "ivory2"})

# --- spinal Harmonic Driver: barrel + muzzle brake + coil collars, long breech cradle with capacitor housings
hs.plate("barrel", "slate", [9.6, 12.0], bevel=0.6,
         half=[P(0, 24), P(4, 24), P(5.2, 28), P(5.2, 128), P(7, 134), P(7, 150), P(0, 150)],
         cuts=[glow([P(0, 58), P(0, 144)], 1.1, 1.6, False)])
hs.plate("muzzle", "slate", [10.4, 12.6], bevel=0.4, half=[P(0, 18), P(5, 19), P(7, 23), P(7, 33), P(0, 34)],
         cuts=[groove([P(1, 26), P(6, 26)])])
for k, y in enumerate((64, 84, 104, 122)):
    hs.plate("collar%d" % k, "ivory2", [10.2, 12.4], bevel=0.3,
             half=[P(0, y), P(6.6, y + 1), P(6.6, y + 5), P(0, y + 6)])
CRADLE = [P(0, 136), P(9, 137), P(14, 144), P(14, 176), P(17, 180), P(17, 252), P(11, 264), P(0, 268)]
hs.plate("cradle", "slate", [7.0, 9.4], bevel=0.5, half=CRADLE,
         tier={"inset": 1.4, "dz": 0.5, "mat": "ivory2", "cuts": [glow([P(0, 170), P(0, 258)], 1.1, 1.6, False)]})
for k, y in enumerate((186, 204, 222, 240)):
    hs.plate("coil%d" % k, "slate", [9.6, 11.2], bevel=0.3, half=[P(0, y), P(15.6, y), P(15.6, y + 6), P(0, y + 6)],
             tier={"inset": 0.6, "dz": 0.3, "mat": "ivory2"})
hs.plate("cap", "slate", [6.4, 8.6], bevel=0.4, sym_poly=[P(19.5, 180), P(30, 184), P(31, 244), P(19.5, 250)],
         tier={"inset": 0.9, "dz": 0.4, "mat": "slate"})

# --- body: segmented plates with machinery gaps between them
hs.plate("b_shoulder", "ivory", PL, sym_poly=region(BODY, 149, 168, 1.4, x0=15),
         tier={"inset": 1.3, "dz": 0.5, "mat": "ivory"})
hs.plate("b_mid", "ivory2", PL, sym_poly=region(BODY, 172, 258, 1.5, x0=18),
         tier={"inset": 1.4, "dz": 0.5, "mat": "ivory2", "cuts": [groove([P(33, 192), P(33, 238)])]})
hs.plate("b_waist", "ivory", PL, sym_poly=region(BODY, 262, 297),
         tier={"inset": 1.4, "dz": 0.6, "mat": "ivory", "cuts": [groove([P(14, 280), P(40, 280)])]})
hs.plate("b_aft1", "ivory2", PL, sym_poly=region(BODY, 301, 349),
         tier={"inset": 1.4, "dz": 0.6, "mat": "ivory"})
hs.plate("b_aft2", "ivory", PL, sym_poly=region(BODY, 353, 401),
         tier={"inset": 1.4, "dz": 0.6, "mat": "ivory", "cuts": [groove([P(14, 376), P(38, 376)])]})
hs.plate("b_eng", "slate", PL, sym_poly=region(BODY, 405, 443, 1.4),
         tier={"inset": 1.2, "dz": 0.5, "mat": "slate", "cuts": [groove([P(4, 424), P(28, 424)])]})
hs.plate("keel", "slate", [6.6, 8.6], half=[P(0, 270), P(5, 273), P(5.4, 400), P(3.6, 436), P(0, 438)],
         tier={"inset": 0.8, "dz": 0.4, "mat": "ivory2", "cuts": [glow([P(0, 276), P(0, 430)], 1.1, 1.6, False)]})
# side strakes along the waist (raised armour with a notch)
hs.plate("strake", "slate", [6.2, 8.2], bevel=0.4, sym_poly=[P(34, 266), P(38.6, 264.6), P(35.4, 292), P(31.6, 294),
                                                            P(30, 282)])

# --- wings: root housing + 2 raised segments stepping inward + tapering tip blade, clamps between
hs.plate("w_root", "slate", [6.4, 8.8], bevel=0.45, sym_poly=[CP(-0.02, -17), CP(-0.02, 17), CP(0.10, 17),
                                                               CP(0.10, -17)],
         tier={"inset": 1.0, "dz": 0.4, "mat": "ivory2"})
hs.plate("w_seg1", "ivory", RL, sym_poly=wseg(0.115, 0.375, -15.2, -11.8, 14.6),
         tier={"inset": 1.3, "dz": 0.6, "mat": "ivory", "cuts": [glow([CP(0.14, 10.5), CP(0.36, 10.5)], 1.3, 1.8)]})
hs.plate("w_seg2", "ivory", RL, sym_poly=wseg(0.40, 0.695, -8.4, -6.8, 12.2),
         tier={"inset": 1.2, "dz": 0.6, "mat": "ivory", "cuts": [glow([CP(0.43, 8.4), CP(0.67, 8.4)], 1.2, 1.7)]})
hs.plate("w_tip", "ivory", RL, bevel=0.5, sym_poly=[CP(0.72, -5.6), CP(0.72, 9.6), CP(WTIP - 0.03, 8.2),
                                                    CP(0.86, -4.8)],
         tier={"inset": 1.0, "dz": 0.5, "mat": "ivory", "cuts": [glow([CP(0.75, 6.2), CP(1.0, 6.6)], 1.1, 1.6)]})
for k, t in enumerate((0.385, 0.705)):
    hs.plate("w_clamp%d" % k, "slate", [6.6, 8.8], bevel=0.35,
             sym_poly=[CP(t - 0.012, -13 if t < 0.5 else -8.4), CP(t - 0.012, 15), CP(t + 0.012, 15), CP(t + 0.012, -12 if t < 0.5 else -7.4)])

# --- engine nacelles along the stern (attached over their whole length), swept fin
hs.plate("n_pod", "ivory", RL, sym_poly=region(POD, 309, 413, 1.2),
         tier={"inset": 1.1, "dz": 0.5, "mat": "ivory", "cuts": [glow([P(46, 322), P(57, 396)], 1.1, 1.6),
                                                                  groove([P(38, 344), P(60, 344)])]})
hs.plate("n_fin", "ivory2", [5.6, 7.8], bevel=0.4, sym_poly=[P(66.4, 372), P(81.6, 408.6), P(69, 401.6)],
         cuts=[glow([P(68, 380), P(78, 404)], 0.9, 1.3)])
hs.plate("n_intake", "slate", [6.8, 8.8], bevel=0.35, sym_poly=region(POD, 292, 306.5, 1.0))
hs.plate("n_clamp", "slate", [6.6, 8.6], bevel=0.35, sym_poly=[P(30, 326), P(42, 326), P(43, 333), P(30, 333)])

FRAMES = ["f_body", "f_prong", "f_wing", "f_pod"]
WN0 = CP(0.13, 10.5)
details = [
    {"type": "node", "pos": list(CORE), "r": 6.5, "shape": "diamond"},
    {"type": "cell", "pos": [0, 48], "size": [3.4, 4.4], "n": 2, "v": 0.9},                  # glyph on the yoke
    # core -> wing emitters (one run each, 45/90 bends) ; core -> nacelles ; blade pivots get a node each
    {"type": "conduit", "pos": [0, 0], "pts": [P(7, 164), P(28, 164), P(36, 172), P(WN0[0], 172), WN0], "w": 1.2,
     "sym": True},
    {"type": "node", "pos": WN0, "r": 2.2, "sym": True},
    {"type": "conduit", "pos": [0, 0], "pts": [P(6, 156), P(16, 146), P(21, 141)], "w": 1.2, "sym": True},
    {"type": "conduit", "pos": [0, 0], "pts": [P(6, 318), P(40, 318), P(46, 322)], "w": 1.1, "sym": True},
    {"type": "node", "pos": P(46, 322), "r": 1.9, "sym": True},
    {"type": "node", "pos": P(0, 318), "r": 2.4},
    # resonator cells on the capacitor housings and the nacelles
    {"type": "cell", "pos": [25, 214], "size": [6.4, 24], "n": 5, "v": 1.4, "sym": True},
    {"type": "cell", "pos": [52, 366], "size": [5.6, 11], "n": 3, "v": 1.2, "sym": True},
    {"type": "vent", "pos": [22, 332], "w": 10, "n": 5, "step": 1.3, "sym": True},
    {"type": "vent", "pos": [0, 416], "w": 12, "n": 4, "step": 1.3},
    {"type": "vent", "pos": [37, 160], "w": 8, "n": 4, "step": 1.2, "sym": True},
    {"type": "block", "pos": [38, 246], "size": [3, 8], "h": 0.5, "mat": "steel", "sym": True},
    {"type": "hatch", "pos": P(16, 390), "r": 1.8, "sym": True},
    {"type": "light", "pos": P(21, 3), "r": 0.6, "sym": True},
    {"type": "light", "pos": CP(WTIP - 0.06, 7), "r": 0.6, "sym": True},
]
BLADE_PIVOT = (21, 140)
slots = [
    # spinal Harmonic Driver (barrel baked into the hull; the weapon sprite will only be muzzle glow / charge FX)
    {"id": "WS0001", "pos": [0, 20], "size": "LARGE", "type": "ENERGY", "mount": "HARDPOINT", "angle": 0, "arc": 5},
    {"id": "WS0002", "pos": CP(0.245, 0), "size": "LARGE", "type": "ENERGY", "mount": "TURRET", "angle": 20, "arc": 220, "sym": True},
    {"id": "WS0003", "pos": P(32, 80), "size": "MEDIUM", "type": "ENERGY", "mount": "TURRET", "angle": 5, "arc": 200, "sym": True},
    {"id": "WS0004", "pos": P(37, 128), "size": "SMALL", "type": "ENERGY", "mount": "TURRET", "angle": 30, "arc": 240, "sym": True},
    {"id": "WS0005", "pos": CP(0.55, 0), "size": "MEDIUM", "type": "HYBRID", "mount": "TURRET", "angle": 40, "arc": 220, "sym": True},
    {"id": "WS0006", "pos": P(22, 282), "size": "MEDIUM", "type": "ENERGY", "mount": "TURRET", "angle": 90, "arc": 220, "sym": True},
    {"id": "WS0007", "pos": [0, 340], "size": "LARGE", "type": "ENERGY", "mount": "TURRET", "angle": 180, "arc": 300},
    {"id": "WS0008", "pos": P(48, 340), "size": "SMALL", "type": "ENERGY", "mount": "TURRET", "angle": 120, "arc": 220, "sym": True},
    {"id": "WS0009", "pos": P(22, 356), "size": "SMALL", "type": "MISSILE", "mount": "TURRET", "angle": 160, "arc": 180, "sym": True},
    # inner emitter blades (fold in towards the barrel while Sympathetic Strike charges)
    {"id": "WS0010", "pos": P(*BLADE_PIVOT), "size": "MEDIUM", "type": "DECORATIVE", "mount": "HARDPOINT", "angle": 0,
     "arc": 0, "deco": "rsl_conductor_blade_r", "deco_alt_angle": 7},
    {"id": "WS0011", "pos": P(-BLADE_PIVOT[0], BLADE_PIVOT[1]), "size": "MEDIUM", "type": "DECORATIVE",
     "mount": "HARDPOINT", "angle": 0, "arc": 0, "deco": "rsl_conductor_blade_l", "deco_alt_angle": -7},
]
engines = [{"pos": [8, 444], "width": 8, "sym": True}, {"pos": [19, 441], "width": 6, "sym": True},
           {"pos": [59, 414], "width": 10, "sym": True}]
# livery "dipped tips + spine stripes" (one cohesive idea): crisp dark-blue caps on the prong and wing tips (the wing
# tip fades into its cap: the only gradients are at the extremities), bold twin stripes beside the keel down the
# whole spine, nacelle fins + stern deepen slightly.
livery = [
    {"type": "poly", "color": "navy", "poly": [P(12, 0), P(42, 0), P(42, 22), P(12, 36)], "sym": True},
    {"type": "band", "pts": [P(12, 42), P(42, 28)], "w": 3.2, "color": "navy", "sym": True},
    {"type": "band", "pts": [P(26, 112), P(52, 100)], "w": 6, "color": "navy", "sym": True},
    {"type": "gradient", "color": "navy", "poly": [P(*p) for p in WING], "a": list(C(0.45)), "b": list(C(0.80)),
     "a0": 0.0, "a1": 0.55},
    {"type": "poly", "color": "navy", "poly": [CP(0.80, -22), CP(0.80, 22), CP(1.25, 22), CP(1.25, -22)], "sym": True},
    # stern deepens (as the Cadence), nacelles deepen towards their fins, then the bold spine stripe on top
    {"type": "gradient", "color": "navy", "poly": [P(0, 256), P(40, 256), P(40, 444), P(0, 444)], "a": [0, 262],
     "b": [0, 440], "a0": 0.0, "a1": 0.6},
    {"type": "gradient", "color": "navy", "poly": [P(*p) for p in POD], "a": [44, 330], "b": [70, 404],
     "a0": 0.0, "a1": 0.75},
    {"type": "band", "pts": [P(14, 272), P(14, 400), P(11, 438)], "w": 7, "color": "navy", "sym": True},
    {"type": "band", "pts": [P(14, 150), P(14, 170)], "w": 7, "color": "navy", "sym": True},
    {"type": "poly", "color": "gunmetal", "poly": [P(-3.6, 43), P(3.6, 43), P(3.6, 53), P(-3.6, 53)]},
]
for part in (hs.layers, details, slots, engines, livery):
    walk(part, SCALE)
W = 2 * int(max(max(p[0] for p in WING), max(p[0] for p in PRONG), max(p[0] for p in POD)) * SCALE + 3)
hull = {"id": "rsl_conductor", "name": "Conductor", "hullSize": "CAPITAL_SHIP",
        "size": [W, int(math.ceil(H * SCALE))], "layers": hs.layers,
        "greebles": {"layers": FRAMES, "z0": 3.0, "zmax": 3.9, "density": 1.0, "seed": 73},
        "surface_detail": {"layers": ["b_mid", "b_aft1"], "density": 0.025, "seed": 31},
        "details": details, "slots": slots, "engines": engines, "livery": livery,
        "ship": {"builtInMods": ["stabilizedshieldemitter", "operations_center"]}}


# ================================================================== inner emitter blade (R; pivot = image centre)
BL = 90                                  # pivot -> tip (~84 x SCALE)
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
