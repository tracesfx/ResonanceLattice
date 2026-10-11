"""Generate art_src/specs/rsl_tremolo.json.

python art_src/gen/gen_tremolo.py art_src/specs/rsl_tremolo.json   # then ./art_src/art.sh rsl_tremolo

Direction chosen by the user (2026-10-11, option A of art_src/review/tremolo_options.png, "Fork"):
  a catamaran of two narrow hulls. Each hull: stepped spear bow with an inner mandible tooth -> shoulder steps ->
  sponson with a sharp forward-out tooth -> notch -> mid section -> engine block flaring into a swept aft tip.
  A forward bridge with the lattice core joins the hulls behind the open fork; glowing X-spars (open girders: twin
  glowing rails + rungs, no hub at the crossing) and a cross bar span the open gap aft. Real empty space: the fork between the bows and the truss windows.
Plates are made from the frame outline (inset + clipped to bands), so the gaps between them expose machinery.
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


# ------------------------------------------------------------------ polygon helpers (no shapely)
def area(poly):
    return sum(poly[i][0] * poly[i - 1][1] - poly[i - 1][0] * poly[i][1] for i in range(len(poly))) / 2


def inset(poly, k, miter=3.0):
    """Offset a simple polygon inward by k (miter joins, clamped at sharp tips)."""
    s = 1 if area(poly) > 0 else -1
    n, out = len(poly), []
    for i in range(n):
        (x0, y0), (x1, y1), (x2, y2) = poly[i - 1], poly[i], poly[(i + 1) % n]
        e0, e1 = (x1 - x0, y1 - y0), (x2 - x1, y2 - y1)
        l0, l1 = math.hypot(*e0) or 1, math.hypot(*e1) or 1
        n0 = (-e0[1] / l0 * s, e0[0] / l0 * s)          # inward normals
        n1 = (-e1[1] / l1 * s, e1[0] / l1 * s)
        bx, by = n0[0] + n1[0], n0[1] + n1[1]
        bl = math.hypot(bx, by)
        if bl < 1e-6:
            bx, by, bl = n0[0], n0[1], 1
        cosh = max(1 / miter, (bx * n0[0] + by * n0[1]) / bl)
        d = k / cosh
        out.append((x1 + bx / bl * d, y1 + by / bl * d))
    return out


def clip_y(poly, y0, y1):
    """Sutherland-Hodgman clip of poly to the band y0 <= y <= y1."""
    def cut(pts, keep, yc):
        res = []
        for i in range(len(pts)):
            a, b = pts[i - 1], pts[i]
            ka, kb = keep(a), keep(b)
            if kb:
                if not ka:
                    t = (yc - a[1]) / (b[1] - a[1])
                    res.append((a[0] + (b[0] - a[0]) * t, yc))
                res.append(b)
            elif ka:
                t = (yc - a[1]) / (b[1] - a[1])
                res.append((a[0] + (b[0] - a[0]) * t, yc))
        return res
    pts = cut(poly, lambda p: p[1] >= y0, y0)
    return cut(pts, lambda p: p[1] <= y1, y1)


def region(poly, y0, y1, k=1.5):
    return [P(x, y) for x, y in clip_y(inset(poly, k), y0, y1)]


def bar(a, b, w):
    (x0, y0), (x1, y1) = a, b
    n = math.hypot(x1 - x0, y1 - y0)
    ox, oy = -(y1 - y0) / n * w / 2, (x1 - x0) / n * w / 2
    return [P(x0 + ox, y0 + oy), P(x1 + ox, y1 + oy), P(x1 - ox, y1 - oy), P(x0 - ox, y0 - oy)]


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


layers = []
FZ, PL, RL = [0, 3.0], [4.0, 6.2], [5.2, 7.6]


def frame(name, **shape):
    layers.append(dict({"name": name, "mat": "graphite", "z": FZ, "bevel": 0.6}, **shape))


def plate(name, mat, z, tier=None, cuts=None, bevel=0.6, **shape):
    L = dict({"name": name, "mat": mat, "z": z, "bevel": bevel}, **shape)
    if cuts:
        L["cuts"] = cuts
    if tier:
        L["tiers"] = [tier]
    layers.append(L)


H = 262
# right hull, clockwise from the bow tip (outer edge down, stern, inner edge up)
# The outer edge oscillates in/out down the hull (a "tremolo" waveform): every section slants the other way.
HULL = [(44, 0), (46, 10), (47.5, 26), (52, 29), (54, 46), (58, 49),                 # long stepped spear
        (60, 52), (63, 70), (61.5, 73), (67, 94),                                    # fore: slants out, step notch
        (76, 97), (91, 104), (87.5, 110), (84, 146), (78, 152),                      # sponson: forward-out tooth,
        (80, 158), (87, 200), (85, 210),                                             #   slants in; mid slants out
        (90, 220), (99, 252), (89, 247), (85, 257),                                  # engine flare -> swept aft tip
        (67, 257), (63, 251), (56, 255), (51, 248),                                  # stern, nozzle notch
        (51, 236), (48.5, 230), (48, 176), (44.5, 166), (44, 138), (43, 110), (39.5, 100), (36.5, 54),
        (30, 30), (36, 34), (38.5, 26), (42, 10)]                                   # inner mandible tooth
BRIDGE = [P(0, 74), P(5, 84), P(14, 88), P(40, 99), P(45, 104), P(45.5, 134), P(30, 138), P(18, 148), P(8, 152),
          P(4, 162), P(0, 164)]
XA, XB = (51, 174), (-51, 224)                    # X-spar (the other one is its mirror image)
HY = 199                                          # cross bar

# ------------------------------------------------------------------ silhouette
frame("f_hull", sym_poly=[P(*p) for p in HULL])
frame("f_bridge", half=BRIDGE)
SW = 11                                           # X girder width (twin rails + rungs)
frame("f_spar_x1", poly=bar(XA, XB, SW))
frame("f_spar_x2", poly=bar((-XA[0], XA[1]), (-XB[0], XB[1]), SW))
frame("f_spar_h", sym_poly=[P(52, HY - 3), P(52, HY + 3), P(12, HY + 3), P(12, HY - 3)])

# ------------------------------------------------------------------ hull plates (bands of the frame outline)
glow = lambda pts, w=1.5, d=2.0: {"pts": pts, "w": w, "depth": d, "glow": True, "sym": True}
plate("h_spear", "ivory", [4.4, 6.6], bevel=0.5, sym_poly=region(HULL, 1.5, 48, 1.3),
      cuts=[{"pts": [P(38, 29.5), P(51, 30.5)], "w": 0.5, "depth": 0.45, "sym": True}],
      tier={"inset": 1.1, "dz": 0.5, "mat": "ivory"})
plate("h_fore", "ivory", PL, sym_poly=region(HULL, 50.5, 96),
      tier={"inset": 1.4, "dz": 0.6, "mat": "ivory",
            "cuts": [{"pts": [P(40, 72), P(64, 76)], "w": 0.55, "depth": 0.5, "sym": True}]})
plate("h_spon", "ivory", PL, sym_poly=region(HULL, 99, 149),
      tier={"inset": 1.6, "dz": 0.6, "mat": "ivory",
            "cuts": [{"pts": [P(46, 126), P(84, 122)], "w": 0.55, "depth": 0.5, "sym": True}]})
plate("h_mid", "ivory2", PL, sym_poly=region(HULL, 154, 205),
      tier={"inset": 1.5, "dz": 0.6, "mat": "ivory",
            "cuts": [glow([P(55, 160), P(55, 200)], 1.4)]})
plate("h_eng", "ivory2", PL, sym_poly=region(HULL, 209, 231),
      tier={"inset": 1.4, "dz": 0.5, "mat": "ivory2",
            "cuts": [{"pts": [P(54, 220), P(88, 220)], "w": 0.55, "depth": 0.5, "sym": True}]})
plate("h_eng2", "ivory2", PL, sym_poly=region(HULL, 234, 256.5),
      tier={"inset": 1.3, "dz": 0.5, "mat": "ivory"})
# swept aft tip blade: raised, with an emitter line running out to the point
plate("h_tip", "ivory", RL, bevel=0.5, sym_poly=[P(86, 222), P(89.4, 223), P(96.4, 249), P(87.6, 245.6), P(84, 240)],
      tier={"inset": 0.9, "dz": 0.4, "mat": "ivory", "cuts": [glow([P(87.6, 228), P(93.6, 246)], 1.1, 1.6)]})
# raised inner keel rail on each hull (gunmetal), carries the accelerator line from the bridge to the bow gun
plate("h_keel", "slate", [6.6, 8.4], bevel=0.4,
      sym_poly=[P(38.4, 54), P(43, 51), P(46, 54), P(46, 96), P(42, 100), P(39.5, 98)],
      tier={"inset": 0.7, "dz": 0.4, "mat": "ivory2", "cuts": [glow([P(42.4, 57), P(42.4, 94)], 1.1, 1.6)]})

# ------------------------------------------------------------------ bridge (lattice core) and spars
plate("br_a", "ivory", PL, half=[P(0, 76.5), P(4.4, 86), P(13.6, 90), P(39, 100.6), P(43.4, 105), P(43.4, 118),
                                 P(0, 118)],
      tier={"inset": 1.5, "dz": 0.6, "mat": "ivory",
            "cuts": [{"pts": [P(-30, 104), P(0, 98), P(30, 104)], "w": 0.55, "depth": 0.5}]})
plate("br_b", "ivory2", PL, half=[P(0, 121), P(43.4, 121), P(43.6, 132), P(29.4, 135.8), P(17, 146), P(7, 150),
                                  P(3, 159.6), P(0, 161)],
      tier={"inset": 1.3, "dz": 0.5, "mat": "ivory"})
# leading-edge emitter strakes on the bridge chevron (gunmetal, glow cut along them)
plate("br_edge", "slate", [6.4, 8.2], bevel=0.4, sym_poly=[P(6, 88.4), P(14.4, 91.4), P(38, 101.4), P(38, 105.4),
                                                          P(13.6, 95.6), P(6, 92.6)],
      cuts=[{"pts": [P(8, 90.6), P(14, 93.2), P(36, 102.6)], "w": 1.0, "depth": 1.4, "glow": True, "sym": True}])
plate("br_spine", "slate", [6.8, 8.4], half=[P(0, 92), P(3.6, 94), P(4, 150), P(2, 154), P(0, 155)],
      tier={"inset": 0.7, "dz": 0.4, "mat": "ivory2"})
RO, RW_ = 3.5, 2.8                                # girder rail offset from the spar's centre line, rail width
mir = lambda pts: [P(-x, y) for x, y in pts]


def spar_pt(t, o):
    """Point on X-spar 1 (XA -> XB): t along, o across (px)."""
    dx, dy = XB[0] - XA[0], XB[1] - XA[1]
    n = math.hypot(dx, dy)
    return (XA[0] + dx * t - dy / n * o, XA[1] + dy * t + dx / n * o)


def isect(p, r, q, s_):
    """Intersection of the lines p + a*r and q + b*s_."""
    den = r[0] * s_[1] - r[1] * s_[0]
    a_ = ((q[0] - p[0]) * s_[1] - (q[1] - p[1]) * s_[0]) / den
    return (p[0] + r[0] * a_, p[1] + r[1] * a_)


# X-spars as open girders that really cross (no hub): each spar = two gunmetal rails, each with its own glow line,
# and steel rungs between them. Every rail of spar 1 crosses both rails of spar 2; a lattice node sits on each of
# those four rail crossings (it also hides where the coplanar rails overlap).
T0, T1 = 0.025, 0.975
for k, o in enumerate((-RO, RO)):
    rail = [P(*spar_pt(T0, o - RW_ / 2)), P(*spar_pt(T1, o - RW_ / 2)), P(*spar_pt(T1, o + RW_ / 2)),
            P(*spar_pt(T0, o + RW_ / 2))]
    line = [P(*spar_pt(T0 + 0.03, o)), P(*spar_pt(T1 - 0.03, o))]
    glow_cut = lambda pts: [{"pts": pts, "w": 0.8, "depth": 1.2, "glow": True}]
    plate("gx1_rail%d" % k, "slate", [4.8, 6.4], bevel=0.3, poly=rail, cuts=glow_cut(line))
    plate("gx2_rail%d" % k, "slate", [4.8, 6.4], bevel=0.3, poly=mir(rail), cuts=glow_cut(mir(line)))
# Warren-truss bracing between the rails (zig-zag struts), none near the crossing
k = 0
for t_a, t_b in ((0.03, 0.43), (0.57, 0.97)):
    m = 8
    for q in range(m):
        ta, tb = t_a + (t_b - t_a) * q / m, t_a + (t_b - t_a) * (q + 1) / m
        oa, ob = (-RO, RO) if q % 2 == 0 else (RO, -RO)
        plate("gx_brace%d" % k, "ivory", [4.2, 5.9], bevel=0.25, sym_poly=bar(spar_pt(ta, oa), spar_pt(tb, ob), 1.3))
        k += 1
D1 = (XB[0] - XA[0], XB[1] - XA[1])
RAIL_X = [isect(spar_pt(0, o1), D1, (-spar_pt(0, o2)[0], spar_pt(0, o2)[1]), (-D1[0], D1[1]))
          for o1 in (-RO, RO) for o2 in (-RO, RO)]
plate("s_h", "slate", [4.4, 6.0], bevel=0.4, sym_poly=[P(13, HY - 1.8), P(49, HY - 1.8), P(49, HY + 1.8), P(13, HY + 1.8)],
      cuts=[{"pts": [P(15, HY), P(46, HY)], "w": 0.9, "depth": 1.3, "glow": True, "sym": True}])
for k, (y, h) in enumerate(((175, 7), (HY, 4), (223, 7))):       # spar root clamps on the inner hull edge
    plate("clamp%d" % k, "slate", [6.2, 8.4], bevel=0.4,
          sym_poly=[P(46.6, y - h), P(53.5, y - h - 1.4), P(53.5, y + h + 1.4), P(46.6, y + h)])
for k, y in enumerate((102, 132)):                                # bridge root clamps
    plate("bclamp%d" % k, "slate", [6.2, 8.4], bevel=0.4,
          sym_poly=[P(41.5, y - 3), P(48, y - 4), P(48, y + 4), P(41.5, y + 3)])

FRAMES = ["f_hull", "f_bridge"]
details = [
    {"type": "node", "pos": [0, 128], "r": 3.2, "shape": "diamond"},
    {"type": "cell", "pos": [0, 82], "size": [4.4, 4.4], "n": 2, "v": 1.0},               # nose glyph
    # core -> keel rails -> bow guns
    {"type": "conduit", "pos": [0, 0], "pts": [P(4, 128), P(26, 128), P(34, 120), P(42.4, 112), P(42.4, 99)],
     "w": 1.2, "sym": True},
    {"type": "node", "pos": P(42.4, 54), "r": 2.0, "sym": True},
    # core -> sponson turret
    {"type": "conduit", "pos": [0, 0], "pts": [P(0, 134), P(0, 142), P(10, 142), P(16, 136), P(56, 136),
                                               P(66, 126)], "w": 1.1, "sym": True},
    {"type": "node", "pos": P(66.6, 125.4), "r": 2.0, "sym": True},
    # truss -> engines
    {"type": "conduit", "pos": [0, 0], "pts": [P(55, 204), P(55, 222), P(60, 228), P(60, 246)], "w": 1.1,
     "sym": True},
    *[{"type": "node", "pos": P(*q), "r": 1.9} for q in RAIL_X],                  # X-spar rail crossings
    {"type": "cell", "pos": [72, 176], "size": [7.6, 18], "n": 4, "v": 1.4, "sym": True},
    {"type": "cell", "pos": [56, 74], "size": [6, 14], "n": 3, "v": 1.3, "sym": True},
    {"type": "vent", "pos": [0, 110], "w": 8, "n": 4, "step": 1.3},
    {"type": "vent", "pos": [74, 232], "w": 6, "n": 6, "step": 1.2, "sym": True},
    {"type": "block", "pos": [76, 140], "size": [3, 6], "h": 0.5, "mat": "steel", "sym": True},
    {"type": "block", "pos": [64, 214], "size": [3, 6], "h": 0.4, "mat": "steel", "sym": True},
    {"type": "hatch", "pos": P(78, 194), "r": 1.8, "sym": True},
    {"type": "light", "pos": P(93, 244), "r": 0.6, "sym": True},
    {"type": "light", "pos": P(86, 109), "r": 0.5, "sym": True},
    {"type": "mark", "pos": [0, 0], "pts": [P(20, 112), P(20, 120)], "w": 0.7, "sym": True},
    {"type": "mark", "pos": [0, 0], "pts": [P(22, 112), P(22, 120)], "w": 0.7, "sym": True},
]
slots = [
    {"id": "WS0001", "pos": P(46, 34), "size": "MEDIUM", "type": "ENERGY", "mount": "HARDPOINT", "angle": 0, "arc": 10, "sym": True},
    {"id": "WS0003", "pos": [0, 104], "size": "LARGE", "type": "ENERGY", "mount": "TURRET", "angle": 0, "arc": 150},
    {"id": "WS0004", "pos": P(74, 116), "size": "MEDIUM", "type": "HYBRID", "mount": "TURRET", "angle": 45, "arc": 240, "sym": True},
    {"id": "WS0006", "pos": P(70, 200), "size": "SMALL", "type": "ENERGY", "mount": "TURRET", "angle": 100, "arc": 220, "sym": True},
    {"id": "WS0008", "pos": P(62, 84), "size": "SMALL", "type": "MISSILE", "mount": "TURRET", "angle": 30, "arc": 180, "sym": True},
]
engines = [{"pos": [62, 256], "width": 8, "sym": True}, {"pos": [77, 256], "width": 8, "sym": True}]
# livery ("tremolo" = a trembling note): a dark-blue WAVEFORM stripe runs down each hull's outer flank (two
# regions with different frequencies), the inner faces darken towards the gap, gradients deepen to bow and stern,
# forward chevrons on the bridge, tight cross bands on the engine blocks. No yellow, no flat steel.
HREG = [P(*p) for p in HULL]
livery = [
    {"type": "gradient", "color": "navy", "a": [0, 110], "b": [0, 10], "a0": 0.0, "a1": 0.42},
    {"type": "gradient", "color": "navy", "a": [0, 176], "b": [0, 256], "a0": 0.0, "a1": 0.7},
    {"type": "gradient", "color": "navy", "poly": HREG, "a": [70, 0], "b": [42, 0], "a0": 0.0, "a1": 0.5},
    {"type": "gradient", "color": "navy", "poly": [P(58, 98), P(100, 98), P(100, 208), P(58, 208)], "a": [62, 0],
     "b": [90, 0], "a0": 0.0, "a1": 0.5},
    {"type": "gradient", "color": "navy", "poly": BRIDGE, "a": [0, 150], "b": [0, 80], "a0": 0.15, "a1": 0.55},
    {"type": "splinter", "color": "navy", "colors": [None, "navy", None], "widths": [55, 5, 200], "angle": 0,
     "zigzag": 7, "amp": 1.6, "alpha": 0.8, "poly": [P(30, 50), P(80, 50), P(80, 96), P(30, 96)]},
    {"type": "splinter", "color": "navy", "colors": [None, "navy", None], "widths": [72.5, 7, 200], "angle": 0,
     "zigzag": 12, "amp": 2.6, "alpha": 0.8, "poly": [P(60, 100), P(100, 100), P(100, 206), P(60, 206)]},
    {"type": "splinter", "color": "navy", "colors": [None, "navy", None, "navy"], "widths": [8, 4, 11, 5],
     "alpha": 0.5, "angle": 58, "poly": [P(0, 74), P(46, 74), P(46, 120), P(0, 120)]},
    {"type": "splinter", "color": "navy", "colors": [None, "navy", None, "navy", None, "navy"],
     "widths": [6, 3, 9, 4, 5, 3], "alpha": 0.55, "angle": 84, "poly": [P(46, 208), P(100, 208), P(100, 258), P(46, 258)]},
    {"type": "poly", "color": "gunmetal", "poly": [P(42.5, 0), P(45.5, 0), P(46.6, 9), P(41.4, 9)]},
]
for part in (layers, details, slots, engines, livery):
    walk(part, SCALE)
W = 2 * int(max(p[0] for L in layers for p in (L.get("half") or L.get("sym_poly") or L.get("poly"))) + 3)
H = int(math.ceil(H * SCALE))
spec = {"id": "rsl_tremolo", "name": "Tremolo", "hullSize": "CRUISER", "size": [W, H], "layers": layers,
        "greebles": {"layers": FRAMES, "z0": 3.0, "zmax": 3.9, "density": 1.0, "seed": 47},
        "surface_detail": {"layers": ["h_fore", "h_spon", "br_a"], "density": 0.06, "seed": 23},
        "details": details, "slots": slots, "engines": engines, "livery": livery,
        "ship": {"builtInMods": ["auxiliarythrusters"]}}
json.dump(spec, open(sys.argv[1], "w", newline="\n"), indent=1)
print("W", W, "H", H)
