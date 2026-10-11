"""Generate art_src/specs/rsl_halo.json and the spinning ring deco art_src/specs/rsl_halo_ring.json.

python art_src/gen/gen_halo.py art_src/specs/rsl_halo.json   # then ./art_src/art.sh rsl_halo rsl_halo_ring

Direction chosen by the user (2026-10-11, option C of art_src/review/halo_options.png, "Eye"):
  a wide carrier hull that wraps around a ring spinning in a central well. Stepped spear bow with canards ->
  head whose shoulders sweep back into a deep V notch -> two forward claw prongs with swept tips -> fore flight
  deck slanting out to a tooth -> aft deck slanting in -> swept aft fins -> stepped engine block. The well is
  ringed by a raised bearing race with clamps; its floor is dark with static radial ribs and a glow ring, and the
  lattice core sits at its centre under the ring's hub.
  The ring (deco, rotates about its image centre) has 6 armoured segments with swept teeth (show the spin
  direction), bay hatches, a glowing seam, 3 spokes to a hub; alternate segments are painted dark blue so the
  rotation reads at 1x.
v2 (user: "the grey, flat-coloured platform inside is ugly; make it partially hollow, keep the parts the fighter
  bays need"): the well floor is cut open between the 12 radial struts (real empty space under the spinning ring);
  struts, hub collar, core, lip, bearing race and the flank flight decks with their bay hatches stay.
Livery: "Stillwater" ripples: broken concentric dark-blue arcs radiating from the well over the flanks, flank
gradients deepening outward, prong gradients deepening to the tips, cross-bands on the engine block.
The ring is its own sprite, so the well needs no real depth: plates run under it and the dark well floor, ribs and
bearing race are stacked ON TOP of them (curve-fill holes only work when fully inside one outline).
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
    s = -1 if area(poly) > 0 else 1          # (area() has the opposite sign of the usual shoelace)
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
    """Sutherland-Hodgman clip of poly to the band v0 <= p[axis] <= v1."""
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
    """Band of the inset outline as a 'half' (centre-line edge snapped to x=0, ordered top -> bottom down the
    right side), so the mirrored plate is ONE polygon across the centre line (needed when a hole crosses it)."""
    pts = clip(inset(poly, k), 1, y0, y1)
    xm = min(p[0] for p in pts)
    on_c = lambda p: p[0] < xm + 0.05
    top = min((i for i, p in enumerate(pts) if on_c(p)), key=lambda i: pts[i][1])
    pts = pts[top:] + pts[:top]
    if on_c(pts[1]):                               # walking along the centre line first: reverse direction
        pts = [pts[0]] + list(reversed(pts[1:]))
    return [P(0 if on_c(p) else p[0], p[1]) for p in pts]


def bar(a, b, w):
    (x0, y0), (x1, y1) = a, b
    n = math.hypot(x1 - x0, y1 - y0)
    ox, oy = -(y1 - y0) / n * w / 2, (x1 - x0) / n * w / 2
    return [P(x0 + ox, y0 + oy), P(x1 + ox, y1 + oy), P(x1 - ox, y1 - oy), P(x0 - ox, y0 - oy)]


def pol(c, rad, a):
    a = math.radians(a)
    return (c[0] + rad * math.cos(a), c[1] + rad * math.sin(a))


def arc(c, rad, a0, a1, n=None):
    n = n or max(4, int(abs(a1 - a0) / 4))
    return [P(*pol(c, rad, a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def circle(c, rad, n=72):
    return arc(c, rad, 0, 360 - 360 / n, n - 1)


def ring_cuts(c, rad, w, d, n=4, gap=5):
    """A glowing circle as n open arcs (a closed polyline makes the strip builder fill a disc)."""
    return [{"pts": arc(c, rad, -90 + k * 360 / n + gap, -90 + (k + 1) * 360 / n - gap), "w": w, "depth": d,
             "glow": True} for k in range(n)]


def closed(pts):
    return pts + [pts[0]]


def quad_at(c, a, r0, r1, half_w):
    """Radial trapezoid (clamp/hatch) centred on angle a between radii r0 and r1, half_w px wide."""
    u = (math.cos(math.radians(a)), math.sin(math.radians(a)))
    v = (-u[1], u[0])
    pts = [(c[0] + u[0] * r0 + v[0] * half_w, c[1] + u[1] * r0 + v[1] * half_w),
           (c[0] + u[0] * r1 + v[0] * half_w * 0.8, c[1] + u[1] * r1 + v[1] * half_w * 0.8),
           (c[0] + u[0] * r1 - v[0] * half_w * 0.8, c[1] + u[1] * r1 - v[1] * half_w * 0.8),
           (c[0] + u[0] * r0 - v[0] * half_w, c[1] + u[1] * r0 - v[1] * half_w)]
    return [P(*p) for p in pts]


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
H = 380
WC = (0, 190)                 # well centre
# right half, clockwise from the bow tip, closing on the centre line at the stern
HULL = [(0, 0), (3, 10), (4.5, 24), (8, 27), (10, 44), (14, 47), (16, 56),            # stepped spear
        (24, 62), (36, 56), (41, 60), (34, 68),                                       # canard (swept forward tooth)
        (58, 80), (80, 94),                                                           # head shoulder sweeps back
        (88, 88), (106, 44), (112, 26),                                               # deep V notch -> prong tip
        (118, 32), (121, 48), (126, 51), (130, 80), (126, 86),                        # prong outer: step, notch
        (134, 94), (150, 156), (152, 164), (139, 172),                                # fore deck slants out, tooth
        (134, 178), (140, 190), (130, 246),                                           # aft deck slants in
        (134, 256), (150, 296), (133, 291), (120, 294),                               # swept aft fin
        (112, 302), (104, 322), (84, 330), (78, 348), (62, 352), (58, 366), (44, 370), (40, 380),
        (0, 380)]                                                                     # stepped engine block

hs = Spec()
hs.frame("f_hull", half=[P(*p) for p in HULL])

# --- plates (bands of the frame outline; the gaps between them expose machinery)
hs.plate("h_spear", "ivory", [4.4, 6.6], bevel=0.5, sym_poly=region(HULL, 1.5, 53.5, 1.3, x1=20),
         cuts=[groove([P(8.5, 29), P(0.5, 31)])],
         tier={"inset": 1.1, "dz": 0.5, "mat": "ivory"})
hs.plate("h_head", "ivory2", PL, half=[P(0, 59.5), P(17, 59.5), P(24.6, 63.8), P(33, 68.6), P(57.6, 81.4),
                                       P(79.6, 95.6), P(86, 100), P(0, 100)],
         tier={"inset": 1.5, "dz": 0.6, "mat": "ivory",
               "cuts": [groove([P(14, 70), P(26, 80), P(56, 90)])]})
hs.plate("h_prong", "ivory", RL, sym_poly=region(HULL, 27, 97, 1.4, x0=89.5),
         tier={"inset": 1.3, "dz": 0.6, "mat": "ivory",
               "cuts": [glow([P(93.5, 76), P(106.5, 42)], 1.2, 1.7), groove([P(92, 88), P(126, 84)])]})
hs.plate("h_flank1", "ivory", PL, sym_poly=region(HULL, 102.5, 172),
         tier={"inset": 1.6, "dz": 0.6, "mat": "ivory", "cuts": [groove([P(104, 128), P(124, 124)])]})
hs.plate("h_flank2", "ivory2", PL, sym_poly=region(HULL, 175, 251),
         tier={"inset": 1.5, "dz": 0.6, "mat": "ivory", "cuts": [groove([P(106, 214), P(120, 212)])]})
hs.plate("h_stern", "ivory", PL, half=half_region(HULL, 254, 327),
         tier={"inset": 1.5, "dz": 0.6, "mat": "ivory",
               "cuts": [groove([P(60, 298), P(100, 306)]), groove([P(4, 304), P(30, 318)])]})
hs.plate("h_eng", "ivory2", PL, sym_poly=region(HULL, 330, 379),
         tier={"inset": 1.4, "dz": 0.5, "mat": "ivory2", "cuts": [groove([P(10, 352), P(56, 352)])]})
# swept aft fin blades, emitter line out to the point
hs.plate("h_fin", "ivory", RL, bevel=0.5, sym_poly=[P(130.5, 252), P(134.6, 259), P(146.4, 291.4), P(133.5, 287.4),
                                                    P(127, 270)],
         tier={"inset": 0.9, "dz": 0.4, "mat": "ivory", "cuts": [glow([P(133.5, 264), P(143, 288)], 1.1, 1.6)]})
# canard blades
hs.plate("h_canard", "slate", [5.6, 7.6], bevel=0.4, sym_poly=[P(23, 62.5), P(35.6, 57.4), P(39.4, 60.4),
                                                               P(33, 66.6), P(25, 66)],
         cuts=[glow([P(27, 63.4), P(36, 59.6)], 0.9, 1.3)])
# flight decks: raised gunmetal strips along the flanks carrying the bay hatches
DECK1 = [P(126, 106), P(134, 106), P(146, 154), P(140, 164), P(129, 164)]
DECK2 = [P(124, 188), P(137.5, 188), P(138, 194), P(129.5, 240), P(122, 236)]
hatch = lambda y, x0, x1: closed([P(x0, y), P(x1, y), P(x1, y + 9), P(x0, y + 9)])
hs.plate("deck1", "slate", [6.4, 8.2], bevel=0.4, sym_poly=DECK1,
         tier={"inset": 0.9, "dz": 0.4, "mat": "ivory2",
               "cuts": [groove(hatch(114, 127.5, 132.5)), groove(hatch(128, 128.5, 135)),
                        glow([P(133.6, 112), P(143, 150)], 1.0, 1.4)]})
hs.plate("deck2", "slate", [6.4, 8.2], bevel=0.4, sym_poly=DECK2,
         tier={"inset": 0.9, "dz": 0.4, "mat": "ivory2",
               "cuts": [groove(hatch(196, 125, 132.5)), groove(hatch(210, 124.5, 131)),
                        glow([P(135.6, 197), P(130.6, 232)], 1.0, 1.4)]})
# spines: bow (to the nose glyph) and stern keel
hs.plate("spine_b", "slate", [6.8, 8.6], half=[P(0, 30), P(2.6, 32), P(3.2, 54), P(0, 57)],
         tier={"inset": 0.6, "dz": 0.3, "mat": "ivory2"})
hs.plate("spine_s", "slate", [6.6, 8.4], half=[P(0, 293), P(5, 296), P(5.4, 340), P(3, 372), P(0, 374)],
         tier={"inset": 0.8, "dz": 0.4, "mat": "ivory2", "cuts": [glow([P(0, 300), P(0, 366)], 1.1, 1.6, False)]})
# well floor: dark plate (no greebles), static radial ribs and a glow ring that flicker through the spinning ring
hs.plate("well_floor", "graphite", [7.0, 7.4], bevel=0.3, poly=circle(WC, 95))
for k, a in enumerate((15, 45, 75)):
    hs.plate("rib%d" % k, "ivory2", [7.4, 8.4], bevel=0.3, sym_poly=bar(pol(WC, 24, a), pol(WC, 89, a), 4.4))
    hs.plate("ribu%d" % k, "ivory2", [7.4, 8.4], bevel=0.3, sym_poly=bar(pol(WC, 24, -a), pol(WC, 89, -a), 4.4))
hs.plate("well_lip", "slate", [7.4, 8.4], bevel=0.3, poly=circle(WC, 94), holes=[{"poly": circle(WC, 88)}])
# bearing race around the well + clamps
hs.plate("race", "slate", [8.0, 9.8], bevel=0.4, poly=circle(WC, 106), holes=[{"poly": circle(WC, 93)}],
         tier={"inset": 1.2, "dz": 0.4, "mat": "ivory2",
               "cuts": ring_cuts(WC, 99.5, 1.1, 1.5, 8, 2.5)})
CLAMP_A = [-60, -22.5, 22.5, 60]
for k, a in enumerate(CLAMP_A):
    hs.plate("clamp%d" % k, "slate", [8.6, 10.6], bevel=0.4, sym_poly=quad_at(WC, a, 101, 113, 5))
for k, a in enumerate((-90, 90)):
    hs.plate("clampc%d" % k, "slate", [8.6, 10.6], bevel=0.4, poly=quad_at(WC, a, 101, 113, 6))
# the well is HOLLOW (user: the flat grey inner platform was ugly): open sectors between the 12 radial struts are cut
# out of the finished sprite (finish.py "cutouts"), leaving struts, inner hub collar, lip and bearing race.
hs.plate("hub_collar", "slate", [7.4, 8.6], bevel=0.3, poly=circle(WC, 27), holes=[{"poly": circle(WC, 19.5)}],
         tier={"inset": 0.8, "dz": 0.3, "mat": "ivory2"})


def sector(c, a, r0, r1, d0, d1):
    """Open window between two struts centred on angle a: inner arc r0 (half-angle d0), outer arc r1 (d1)."""
    return arc(c, r1, a - d1, a + d1, 6) + list(reversed(arc(c, r0, a - d0, a + d0, 3)))


CUTOUTS = [sector(WC, 30 * k, 28.5, 86.5, 15 - 7.6, 15 - 2.6) for k in range(12)]
# lattice core under the ring hub
hs.plate("core", "slate", [7.4, 9.2], bevel=0.4, poly=[P(*pol(WC, 19, 30 + 60 * i)) for i in range(6)],
         tier={"inset": 1.5, "dz": 0.4, "mat": "ivory2"})

FRAMES = ["f_hull"]
CL = {a: pol(WC, 107, a) for a in CLAMP_A}
details = [
    {"type": "node", "pos": list(WC), "r": 6.5, "shape": "diamond"},
    {"type": "cell", "pos": [0, 38], "size": [3.6, 4.4], "n": 2, "v": 0.9},                 # nose glyph
    *[{"type": "node", "pos": P(*CL[a]), "r": 2.2, "sym": True} for a in CLAMP_A],
    {"type": "node", "pos": P(0, 107), "r": 2.4},
    {"type": "node", "pos": P(0, 273), "r": 2.4},
    # race clamps -> prong turret / fore turret / aft turret / engines (45/90 degree runs, no branching)
    {"type": "conduit", "pos": [0, 0], "pts": [P(58, 95), P(92, 95), P(100, 87), P(106, 72)], "w": 1.1,
     "sym": True},
    {"type": "conduit", "pos": [0, 0], "pts": [P(112, CL[-22.5][1]), P(118, CL[-22.5][1]), P(122, 153)],
     "w": 1.1, "sym": True},
    {"type": "conduit", "pos": [0, 0], "pts": [P(108, CL[22.5][1]), P(112, 235), P(112, 245)], "w": 1.1,
     "sym": True},
    {"type": "conduit", "pos": [0, 0], "pts": [P(56, 296), P(56, 318), P(40, 334), P(40, 348)], "w": 1.1,
     "sym": True},
    {"type": "node", "pos": P(40, 350), "r": 1.9, "sym": True},
    {"type": "cell", "pos": [74, 312], "size": [7.4, 16], "n": 4, "v": 1.4, "sym": True},
    {"type": "cell", "pos": [118, 180], "size": [5.6, 13], "n": 3, "v": 1.2, "sym": True},
    {"type": "cell", "pos": [22, 77], "size": [6, 9], "n": 3, "v": 1.0, "sym": True},
    {"type": "vent", "pos": [117, 272], "w": 8, "n": 6, "step": 1.3, "sym": True},
    {"type": "vent", "pos": [20, 336], "w": 10, "n": 5, "step": 1.3, "sym": True},
    {"type": "vent", "pos": [0, 284], "w": 8, "n": 3, "step": 1.3},
    {"type": "block", "pos": [122, 76], "size": [3, 7], "h": 0.5, "mat": "steel", "sym": True},
    {"type": "block", "pos": [98, 318], "size": [3, 6], "h": 0.4, "mat": "steel", "sym": True},
    {"type": "hatch", "pos": P(92, 284), "r": 1.8, "sym": True},
    {"type": "light", "pos": P(112, 31), "r": 0.6, "sym": True},
    {"type": "light", "pos": P(144, 289), "r": 0.6, "sym": True},
    {"type": "light", "pos": P(149.5, 161), "r": 0.5, "sym": True},
    {"type": "mark", "pos": [0, 0], "pts": [P(76, 326), P(84, 318)], "w": 0.7, "sym": True},
    {"type": "mark", "pos": [0, 0], "pts": [P(79, 327), P(87, 319)], "w": 0.7, "sym": True},
]
slots = [
    {"id": "WS0001", "pos": [0, 74], "size": "LARGE", "type": "ENERGY", "mount": "TURRET", "angle": 0, "arc": 180},
    {"id": "WS0002", "pos": P(111, 62), "size": "MEDIUM", "type": "HYBRID", "mount": "TURRET", "angle": 20, "arc": 240, "sym": True},
    {"id": "WS0003", "pos": P(44, 82), "size": "SMALL", "type": "ENERGY", "mount": "TURRET", "angle": 30, "arc": 270, "sym": True},
    {"id": "WS0004", "pos": P(124, 158), "size": "SMALL", "type": "ENERGY", "mount": "TURRET", "angle": 80, "arc": 200, "sym": True},
    {"id": "WS0005", "pos": P(112, 252), "size": "MEDIUM", "type": "ENERGY", "mount": "TURRET", "angle": 120, "arc": 210, "sym": True},
    {"id": "WS0006", "pos": P(96, 310), "size": "SMALL", "type": "MISSILE", "mount": "TURRET", "angle": 150, "arc": 180, "sym": True},
    {"id": "WS0007", "pos": P(131, 124), "size": "LARGE", "type": "LAUNCH_BAY", "mount": "HIDDEN", "angle": 0, "arc": 360, "sym": True},
    {"id": "WS0008", "pos": P(129, 212), "size": "LARGE", "type": "LAUNCH_BAY", "mount": "HIDDEN", "angle": 0, "arc": 360, "sym": True},
    {"id": "WS0009", "pos": list(WC), "size": "LARGE", "type": "DECORATIVE", "mount": "TURRET", "angle": 0, "arc": 360,
     "deco": "rsl_halo_ring", "deco_alt_angle": 30},
]
engines = [{"pos": [11, 380], "width": 10, "sym": True}, {"pos": [28, 380], "width": 10, "sym": True},
           {"pos": [70, 351], "width": 9, "sym": True}]
HREG = [P(*p) for p in HULL]
livery = [
    # flank gradients deepening outward, prongs deepening to the tips, bow and stern
    {"type": "gradient", "color": "navy", "poly": HREG, "a": [92, 0], "b": [150, 0], "a0": 0.05, "a1": 0.75},
    {"type": "gradient", "color": "navy", "poly": [P(88, 22), P(134, 22), P(134, 97), P(88, 97)], "a": [0, 96],
     "b": [0, 28], "a0": 0.05, "a1": 0.8},
    {"type": "gradient", "color": "navy", "a": [0, 60], "b": [0, 4], "a0": 0.0, "a1": 0.45},
    {"type": "gradient", "color": "navy", "a": [0, 300], "b": [0, 380], "a0": 0.0, "a1": 0.65},
    {"type": "gradient", "color": "navy", "poly": [P(0, 56), P(88, 56), P(88, 100), P(0, 100)], "a": [0, 100],
     "b": [0, 58], "a0": 0.1, "a1": 0.45},
    # "stillwater" ripples: broken concentric arcs of different widths
    {"type": "band", "pts": arc(WC, 115, -80, 78), "w": 4.2, "color": "navy", "sym": True, "alpha": 0.8},
    {"type": "band", "pts": arc(WC, 125, -48, 26), "w": 2.4, "color": "navy", "sym": True, "alpha": 0.75},
    {"type": "band", "pts": arc(WC, 134, -14, 46), "w": 3.4, "color": "navy", "sym": True, "alpha": 0.75},
    {"type": "band", "pts": arc(WC, 126, 56, 80), "w": 3, "color": "navy", "sym": True, "alpha": 0.75},
    # engine block: cross-bands
    {"type": "splinter", "color": "navy", "colors": [None, "navy", None, "navy", None, "navy"],
     "widths": [9, 4, 12, 3, 7, 5], "alpha": 0.55, "angle": 90,
     "poly": [P(0, 330), P(90, 330), P(90, 380), P(0, 380)]},
    {"type": "poly", "color": "gunmetal", "poly": [P(-3, 0), P(3, 0), P(3.8, 9), P(-3.8, 9)]},
    {"type": "poly", "color": "gunmetal", "poly": [P(109, 24), P(115, 24), P(118.4, 36), P(105, 36)], "sym": True},
]
for part in (hs.layers, details, slots, engines, livery):
    walk(part, SCALE)
W = 2 * int(max(p[0] for p in HULL) * SCALE + 3)
hull = {"id": "rsl_halo", "name": "Halo", "hullSize": "CAPITAL_SHIP", "size": [W, int(math.ceil(H * SCALE))],
        "layers": hs.layers,
        "greebles": {"layers": FRAMES, "z0": 3.0, "zmax": 3.9, "density": 1.0,
                     "seed": 61},
        "surface_detail": {"layers": ["h_head", "h_flank1", "h_flank2", "h_stern"], "density": 0.022, "seed": 29},
        "details": details, "slots": slots, "engines": engines, "livery": livery, "cutouts": CUTOUTS,
        "ship": {"builtInMods": ["expanded_deck_crew", "hardened_subsystems"]}}

# ================================================================== ring deco (pivot = image centre)
RS = 188                                   # sprite size (even); ring outer radius 91 < race inner radius 93
RC = (0, RS / 2)
R_IN, R_OUT, TD, NSEG, GAP, NT = 68, 91, 4.0, 6, 7.0, 4
rs = Spec()


def seg_outline(c, a0, a1, r_in, r_out, td):
    """Segment with a swept sawtooth outer edge (teeth lean clockwise: the spin direction)."""
    pts = []
    for j in range(NT):
        t0 = a0 + (a1 - a0) * j / NT
        t1 = a0 + (a1 - a0) * (j + 1) / NT
        pts += [P(*pol(c, r_out - td, t0)), P(*pol(c, r_out, t1 - 0.6))]
    pts += list(reversed(arc(c, r_in, a0, a1)))
    return pts


step = 360 / NSEG
SEGS = []
for k in range(NSEG):
    cen = -90 + k * step
    a0, a1 = cen - step / 2 + GAP / 2, cen + step / 2 - GAP / 2
    SEGS.append((cen, a0, a1))
    rs.frame("rf_seg%d" % k, poly=seg_outline(RC, a0, a1, R_IN, R_OUT, TD))
    face = seg_outline(RC, a0 + 1.2, a1 - 1.2, R_IN + 2.6, R_OUT - 1.8, TD - 0.6)
    rm = R_IN + 9.5
    hatch_ = quad_at(RC, cen, rm + 3.5, R_OUT - TD - 2, 5.5)
    rs.plate("rp_seg%d" % k, "ivory", [4.0, 6.0], poly=face,
             tier={"inset": 1.2, "dz": 0.6, "mat": "ivory",
                   "cuts": [{"pts": arc(RC, rm, a0 + 3, a1 - 3), "w": 1.2, "depth": 1.6, "glow": True},
                            {"pts": closed(hatch_), "w": 0.55, "depth": 0.5},
                            {"pts": [P(*pol(RC, R_IN + 3, a0 + 11)), P(*pol(RC, R_OUT - 4, a0 + 11))],
                             "w": 0.5, "depth": 0.45},
                            {"pts": [P(*pol(RC, R_IN + 3, a1 - 11)), P(*pol(RC, R_OUT - 4, a1 - 11))],
                             "w": 0.5, "depth": 0.45}]})
    # gunmetal armour lip on the leading end of each segment
    rs.plate("rp_lip%d" % k, "slate", [5.6, 7.4], bevel=0.3,
             poly=arc(RC, R_OUT - TD - 1, a1 - 5.5, a1 - 0.8, 3) + list(reversed(arc(RC, R_IN + 1, a1 - 5.5, a1 - 0.8, 3))))
# spokes + hub
SPOKE_A = [-90 + step / 2 + 120 * i for i in range(3)]
for k, a in enumerate(SPOKE_A):
    rs.frame("rf_spoke%d" % k, poly=bar(pol(RC, 18, a), pol(RC, R_IN + 2, a), 9))
    rs.plate("rp_spoke%d" % k, "slate", [4.2, 6.0], bevel=0.35, poly=bar(pol(RC, 21, a), pol(RC, R_IN + 1, a), 6),
             cuts=[{"pts": [P(*pol(RC, 24, a)), P(*pol(RC, R_IN - 2, a))], "w": 0.9, "depth": 1.3, "glow": True}])
rs.frame("rf_hub", poly=circle(RC, 23, 36), holes=[{"poly": circle(RC, 11.5, 36)}])
rs.plate("rp_hub", "slate", [4.4, 6.4], bevel=0.35, poly=circle(RC, 21.5, 36), holes=[{"poly": circle(RC, 13, 36)}],
         tier={"inset": 1.0, "dz": 0.4, "mat": "ivory2",
               "cuts": ring_cuts(RC, 17.2, 0.9, 1.2, 3, 12)})
ring_details = [{"type": "node", "pos": P(*pol(RC, R_IN + 1, a)), "r": 2.1} for a in SPOKE_A]
ring_livery = [{"type": "poly", "color": "navy", "alpha": 0.85,
                "poly": seg_outline(RC, a0, a1, R_IN, R_OUT + 1, TD)} for k, (cen, a0, a1) in enumerate(SEGS)
               if k % 2 == 0]
ring_livery += [{"type": "gradient", "color": "navy", "poly": seg_outline(RC, a0, a1, R_IN, R_OUT + 1, TD),
                 "a": list(pol(RC, R_IN, a0)), "b": list(pol(RC, R_OUT, a1)), "a0": 0.0, "a1": 0.45}
                for k, (cen, a0, a1) in enumerate(SEGS) if k % 2 == 1]
ring = {"id": "rsl_halo_ring", "name": "Halo Ring", "kind": "deco", "size": [RS, RS], "layers": rs.layers,
        "greebles": {"layers": [L["name"] for L in rs.layers if L["name"].startswith("rf_seg")], "z0": 3.0,
                     "zmax": 3.9, "density": 1.0, "seed": 5},
        "details": ring_details, "livery": [dict(L, sym=False, mirror=False) for L in ring_livery]}

json.dump(hull, open(sys.argv[1], "w", newline="\n"), indent=1)
ring_path = os.path.join(os.path.dirname(sys.argv[1]), "rsl_halo_ring.json")
json.dump(ring, open(ring_path, "w", newline="\n"), indent=1)
print("W", W, "H", H, "| ring", RS, "->", ring_path)
