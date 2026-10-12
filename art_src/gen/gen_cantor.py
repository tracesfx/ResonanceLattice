"""Generate the Cantor Array station: core rsl_cantor, ring deco rsl_cantor_ring and the petal modules
rsl_cantor_spire / rsl_cantor_bell / rsl_cantor_loft (one spec each, written next to argv[1]).

python art_src/gen/gen_cantor.py art_src/specs/rsl_cantor.json
./art_src/art.sh rsl_cantor rsl_cantor_ring rsl_cantor_spire rsl_cantor_bell rsl_cantor_loft
python art_src/station_preview.py art_src/review/cantor_v1.png        # composite: core + ring + 6 modules

Direction chosen by the user (2026-10-11, option B "Hexad" of art_src/review/cantor_options.png, vanilla scale):
  six petals, mirror-symmetric: Spire fore and aft, two Bells (flak/PD) at +-60 deg from the bow, two Choir Lofts
  (hangars) at +-120 deg; the slowly rotating ring runs under raised bearing collars on every petal.
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


def clip_dir(poly, d, v0, v1):
    rot = [(p[0] * d[0] + p[1] * d[1], -p[0] * d[1] + p[1] * d[0]) for p in poly]
    band = clip([list(q) for q in rot], 0, v0, v1)
    return [P(a * d[0] - b * d[1], a * d[1] + b * d[0]) for a, b in band]


def node(pos, rad=2.0, shape=None, sym=False):
    n = {"type": "node", "pos": P(*pos), "r": rad, "sym": sym}
    if shape:
        n["shape"] = shape
    return n


def conduit(pts, w=1.2, sym=False):
    return {"type": "conduit", "pos": [0, 0], "pts": [P(*q) for q in pts], "w": w, "sym": sym}


def navy(pts, sym=True, alpha=1.0):
    return {"type": "poly", "color": "navy", "poly": [P(*q) for q in pts], "sym": sym, "alpha": alpha}


def dump(spec, d):
    path = os.path.join(d, spec["id"] + ".json")
    json.dump(spec, open(path, "w", newline="\n"), indent=1)
    print(spec["id"], spec["size"])


OUT = os.path.dirname(sys.argv[1])

# ================================================================== CORE
# A lattice rosette: six petal sockets (Spire fore/aft, Bells at +-60 deg from the bow, Choir Lofts at +-120), toothed
# notches between them, a segmented armour annulus, a bearing race and a recessed well holding the mod's brightest
# crystal heart, which feeds every petal through one straight conduit each. Mirror-symmetric about the bow axis.
CS = 360
CC = (0, CS / 2)                                   # core centre in spec coords
cp = lambda rad, a: pol(CC, rad, a)                # polar point, screen angles (0 = right, -90 = bow)
ARMS = [(-150, "bell"), (-90, "spire"), (-30, "bell"), (30, "loft"), (90, "spire"), (150, "loft")]
# socket profile per kind: (half-angle at r104, at r128, end radius, half-angle at the end)
SOCK = {"spire": (21, 12.5, 162, 8.5), "bell": (23, 15, 148, 10.5), "loft": (23, 15.5, 148, 11.5)}
R_ROOT = {"spire": 152, "bell": 140, "loft": 140}   # where each module's root sits (it overlaps the socket end)

outline = []
for a, kind in ARMS:
    h104, h128, rend, hend = SOCK[kind]
    outline += [cp(100, a - h104 - 2), cp(128, a - h128), cp(rend, a - hend), cp(rend, a + hend), cp(128, a + h128),
                cp(100, a + h104 + 2)]
    t = a + 30                                     # notch tooth between this arm and the next
    outline += [cp(94, t - 4), cp(118, t), cp(94, t + 4)]
cs = Spec()
cs.frame("cf_core", poly=[P(*q) for q in outline])
# armour annulus: 12 sectors (6 over the arms, 6 over the gaps), joints between them expose the frame
for k in range(12):
    a0 = -90 - 15 + k * 30
    on_arm = k % 2 == 0
    sec = arc(CC, 98, a0 + 0.9, a0 + 30 - 0.9, 8) + list(reversed(arc(CC, 64, a0 + 1.3, a0 + 30 - 1.3, 6)))
    cs.plate("c_sec%d" % k, "ivory" if on_arm else "ivory2", PL, poly=sec,
             tier={"inset": 1.4, "dz": 0.5, "mat": "ivory",
                   "cuts": [groove(arc(CC, 82, a0 + 6, a0 + 24, 6), sym=False)]})
# petal sockets (raised), each with a gunmetal clamp band across it
for i, (a, kind) in enumerate(ARMS):
    h104, h128, rend, hend = SOCK[kind]
    sock = [cp(101, a - h104 + 1), cp(127, a - h128 + 1), cp(rend - 1.5, a - hend + 0.8), cp(rend - 1.5, a + hend - 0.8),
            cp(127, a + h128 - 1), cp(101, a + h104 - 1)]
    cs.plate("c_sock%d" % i, "ivory", RL, poly=[P(*q) for q in sock],
             tier={"inset": 1.3, "dz": 0.6, "mat": "ivory"})
    cs.plate("c_sclamp%d" % i, "slate", [6.8, 9.0], bevel=0.35,
             poly=quad_at(CC, a, 114, 121, 33 if kind == "spire" else 36))
    cs.plate("c_tooth%d" % i, "slate", [5.4, 7.4], bevel=0.35,
             poly=[P(*cp(95, a + 30 - 3.2)), P(*cp(115, a + 30)), P(*cp(95, a + 30 + 3.2))])
# bearing race + six clamps, recessed dark well, the crystal heart
cs.plate("c_race", "slate", [7.4, 9.4], bevel=0.4, poly=circle(CC, 64), holes=[{"poly": circle(CC, 50)}],
         tier={"inset": 1.2, "dz": 0.4, "mat": "ivory2", "cuts": ring_cuts(CC, 57, 1.2, 1.6, 6, 6)})
for i, (a, kind) in enumerate(ARMS):
    cs.plate("c_rclamp%d" % i, "slate", [8.4, 10.4], bevel=0.35, poly=quad_at(CC, a, 54, 67, 5.5))
cs.plate("c_well", "graphite", [5.0, 5.6], bevel=0.3, poly=circle(CC, 51))
cs.plate("c_heart", "slate", [5.6, 7.2], bevel=0.4, poly=[P(*cp(30, 0 + 60 * i + 30 * (i % 2 == 0))) for i in range(6)])
core_details = [
    node(CC, 14, "diamond"),
    *[{"type": "crystal", "pos": P(*cp(21, a)), "r": 4.2, "h": 2.4} for a, _ in ARMS],
    *[{"type": "crystal", "pos": P(*cp(36, a + 30)), "r": 2.6, "h": 1.6} for a, _ in ARMS],
    # the heart feeds every petal: one straight run each, through the race clamp, to a node at the socket end
    *[conduit([cp(17, a), cp(SOCK[k][2] - 8, a)], 1.5) for a, k in ARMS],
    *[node(cp(SOCK[k][2] - 7, a), 2.6) for a, k in ARMS],
    # resonator cells on the side gap sectors (they read upright there)
    {"type": "cell", "pos": P(*cp(81, 0)), "size": [8, 20], "n": 4, "v": 1.4, "sym": True},
    {"type": "vent", "pos": P(*cp(80, -60)), "w": 9, "n": 4, "step": 1.3, "sym": True},
    {"type": "vent", "pos": P(*cp(80, 60)), "w": 9, "n": 4, "step": 1.3, "sym": True},
]
# STATION_MODULE slots: location = module root, angle = module heading (hullgen passes the type through)
core_slots = [{"id": "WS%04d" % (i + 1), "pos": P(*cp(R_ROOT[k], a)), "size": "LARGE", "type": "STATION_MODULE",
               "mount": "HIDDEN", "angle": -90 - a, "arc": 0, "module": "rsl_cantor_" + k, "no_socket": True}
              for i, (a, k) in enumerate(ARMS)]
core_slots.append({"id": "WS0007", "pos": list(CC), "size": "LARGE", "type": "DECORATIVE", "mount": "TURRET",
                   "angle": 0, "arc": 360, "deco": "rsl_cantor_ring", "deco_alt_angle": 15})
core_livery = [
    # the faction's sash language: every heart->petal conduit runs down a dark-blue ribbon on its socket
    *[{"type": "band", "pts": [P(*cp(64, a)), P(*cp(SOCK[k][2] - 3, a))], "w": 11, "color": "navy", "sym": False}
      for a, k in ARMS],
    # the diagonal gap sectors are dark blue (echoing the ring's painted segments); the side gaps carry cells
    *[{"type": "poly", "color": "navy", "sym": False, "alpha": 0.9,
       "poly": arc(CC, 99, a + 16, a + 44, 6) + list(reversed(arc(CC, 63, a + 16, a + 44, 6)))}
      for a, _ in ARMS if a + 30 in (-120, -60, 60, 120)],      # the four diagonal gaps (mirror-symmetric)
    # dipped tips: the six notch teeth
    *[navy([cp(94, a + 30 - 4), cp(118, a + 30), cp(94, a + 30 + 4)], sym=False) for a, _ in ARMS],
]
core = {"id": "rsl_cantor", "name": "Cantor Array", "hullSize": "CAPITAL_SHIP", "size": [CS, CS],
        "layers": cs.layers, "greebles": {"layers": ["cf_core"], "z0": 3.0, "zmax": 3.9, "density": 1.0, "seed": 101},
        "details": core_details, "slots": core_slots, "engines": [], "livery": core_livery,
        "ship": {"builtInMods": []}}

# ================================================================== RING (deco, pivot = image centre)
RS = 444
RC = (0, RS / 2)
R_IN, R_OUT, TD, NSEG, GAP, NT = 197, 213, 3.4, 12, 3.2, 5
rs = Spec()


def seg_outline(c, a0, a1, r_in, r_out, td):
    pts = []
    for j in range(NT):
        t0 = a0 + (a1 - a0) * j / NT
        t1 = a0 + (a1 - a0) * (j + 1) / NT
        pts += [P(*pol(c, r_out - td, t0)), P(*pol(c, r_out, t1 - 0.3))]
    pts += list(reversed(arc(c, r_in, a0, a1, 10)))
    return pts


step = 360 / NSEG
RSEG = []
for k in range(NSEG):
    cen = -90 + k * step
    a0, a1 = cen - step / 2 + GAP / 2, cen + step / 2 - GAP / 2
    RSEG.append((cen, a0, a1))
    rs.frame("rf_seg%d" % k, poly=seg_outline(RC, a0, a1, R_IN, R_OUT, TD))
    rm = R_IN + 5.5
    rs.plate("rp_seg%d" % k, "ivory", [4.0, 6.0],
             poly=seg_outline(RC, a0 + 0.5, a1 - 0.5, R_IN + 1.8, R_OUT - 1.4, TD - 0.5),
             tier={"inset": 1.0, "dz": 0.5, "mat": "ivory",
                   "cuts": [{"pts": arc(RC, rm, a0 + 1.6, a1 - 1.6, 10), "w": 1.1, "depth": 1.5, "glow": True},
                            {"pts": closed(quad_at(RC, cen, rm + 2.4, R_OUT - TD - 1.6, 4.5)), "w": 0.5,
                             "depth": 0.45}]})
    rs.plate("rp_lip%d" % k, "slate", [5.6, 7.4], bevel=0.3,
             poly=arc(RC, R_OUT - TD - 0.6, a1 - 2.6, a1 - 0.4, 3) + list(reversed(arc(RC, R_IN + 0.8, a1 - 2.6, a1 - 0.4, 3))))
ring_details = [node(pol(RC, R_IN + 5.5, cen), 1.6) for cen, a0, a1 in RSEG[::3]]
ring_livery = [{"type": "poly", "color": "navy", "alpha": 0.85, "sym": False, "mirror": False,
                "poly": seg_outline(RC, a0, a1, R_IN, R_OUT + 1, TD)} for k, (cen, a0, a1) in enumerate(RSEG)
               if k % 2 == 0]
ring = {"id": "rsl_cantor_ring", "name": "Cantor Ring", "kind": "deco", "size": [RS, RS], "layers": rs.layers,
        "greebles": {"layers": [L["name"] for L in rs.layers if L["name"].startswith("rf_")], "z0": 3.0,
                     "zmax": 3.9, "density": 1.0, "seed": 7},
        "details": ring_details, "livery": ring_livery}

# ================================================================== PETAL MODULES (drawn pointing up = outward;
# the root is the bottom edge, which overlaps the core socket). The ring passes ~55-65 px out from the core, under a
# raised gunmetal bearing collar on every petal.


def module(mid, name, size, half, plates, details, slots, livery, hull_size="CRUISER", seed=1):
    ms = Spec()
    ms.frame("mf_" + mid, half=[P(*q) for q in half])
    for pl in plates:
        ms.layers.append(pl)
    return {"id": mid, "name": name, "hullSize": hull_size, "size": size, "layers": ms.layers,
            "greebles": {"layers": ["mf_" + mid], "z0": 3.0, "zmax": 3.9, "density": 1.0, "seed": seed},
            "details": details, "slots": slots, "engines": [], "livery": livery,
            "ship": {"builtInMods": ["hardened_subsystems"]}}


def pl(name, mat, z, half=None, poly=None, sym_poly=None, tier=None, cuts=None, bevel=0.5):
    L = {"name": name, "mat": mat, "z": z, "bevel": bevel}
    if half:
        L["half"] = half
    if poly:
        L["poly"] = poly
    if sym_poly:
        L["sym_poly"] = sym_poly
    if tier:
        L["tiers"] = [tier]
    if cuts:
        L["cuts"] = cuts
    return L


# ---- SPIRE: long lance battery (stepped spear, body with two large mounts, bearing collar, root fins)
SPH = 236
SPIRE = [(0, 0), (2.5, 14), (3.5, 40), (7, 44), (8, 80), (12, 84), (13, 118), (19, 124), (21, 158), (30, 166),
         (31, 192), (24, 197), (25, 212), (35, 224), (33, 236), (0, 236)]
sp = [
    pl("s_tip", "ivory", RL, half=half_region(SPIRE, 1.2, 42, 1.0), tier={"inset": 0.7, "dz": 0.4, "mat": "ivory"}),
    pl("s_mid", "ivory", RL, half=half_region(SPIRE, 46, 82, 1.1), tier={"inset": 0.8, "dz": 0.4, "mat": "ivory"}),
    pl("s_neck", "ivory2", RL, half=half_region(SPIRE, 86, 122, 1.2), tier={"inset": 0.9, "dz": 0.5, "mat": "ivory"}),
    pl("s_body", "ivory", PL, half=half_region(SPIRE, 125, 162, 1.3), tier={"inset": 1.2, "dz": 0.5, "mat": "ivory"}),
    pl("s_collar", "slate", [6.6, 8.8], half=[P(0, 166), P(29.4, 167.6), P(30.4, 191), P(0, 192)],
       tier={"inset": 1.0, "dz": 0.4, "mat": "ivory2"}),
    pl("s_root", "ivory2", PL, half=half_region(SPIRE, 196, 235, 1.2), tier={"inset": 1.1, "dz": 0.5, "mat": "ivory"}),
    pl("s_strake", "slate", [6.6, 8.4], sym_poly=[P(14.6, 128), P(19.8, 129), P(20.8, 158), P(15.6, 160)], bevel=0.35),
    pl("s_rclamp", "slate", [6.6, 8.6], sym_poly=[P(8, 84.6), P(12.4, 84.6), P(12.8, 90), P(8, 90)], bevel=0.3),
    pl("s_spine", "slate", [8.0, 10.0], half=[P(0, 8), P(1.8, 12), P(2.2, 150), P(0, 152)]),
]
spire = module("rsl_cantor_spire", "Cantor Spire", [72, SPH], SPIRE, sp,
               [conduit([(0, 232), (0, 196)], 1.4), node((0, 194), 2.2),
                conduit([(0, 160), (0, 150)], 1.2), node((0, 148), 1.8),
                {"type": "cell", "pos": [0, 64], "size": [5, 14], "n": 3, "v": 1.0},
                {"type": "vent", "pos": [14, 206], "w": 6, "n": 4, "step": 1.2, "sym": True}],
               [{"id": "WS0001", "pos": [0, 140], "size": "LARGE", "type": "ENERGY", "mount": "TURRET", "angle": 0, "arc": 270},
                {"id": "WS0002", "pos": [0, 214], "size": "LARGE", "type": "ENERGY", "mount": "TURRET", "angle": 0, "arc": 300},
                {"id": "WS0003", "pos": [17, 182], "size": "SMALL", "type": "ENERGY", "mount": "TURRET", "angle": 60, "arc": 240, "sym": True},
                {"id": "WS0004", "pos": [0, 104], "size": "MEDIUM", "type": "ENERGY", "mount": "HARDPOINT", "angle": 0, "arc": 10}],
               [{"type": "band", "pts": [P(0, 16), P(0, 160)], "w": 9, "color": "navy", "sym": False},
                {"type": "band", "pts": [P(0, 198), P(0, 234)], "w": 9, "color": "navy", "sym": False},
                navy([(0, 0), (3.6, 0), (3.6, 34), (0, 38)]), navy([(25, 212), (35, 224), (33, 236), (26, 230)])],
               seed=11)
# the spear carries the lance's accelerator: a glow cut along the spine (topmost part)
spire["layers"][-1]["cuts"] = [{"pts": [P(0, 14), P(0, 146)], "w": 1.1, "depth": 1.4, "glow": True, "sym": False}]

# ---- BELL: flak / PD petal, a flared mouth with a resonating rim
BEH = 156
BELL = [(0, 24), (10, 22), (24, 14), (40, 4), (57, 0), (62, 8), (52, 16), (44, 30), (38, 52), (30, 70), (34, 90),
        (35, 112), (28, 116), (24, 134), (31, 146), (27, 156), (0, 156)]
be = [
    pl("b_mouth", "ivory", RL, half=half_region(BELL, 2, 48, 1.2),
       tier={"inset": 1.1, "dz": 0.5, "mat": "ivory",
             "cuts": [{"pts": [P(0, 28), P(11, 26), P(25, 18.6), P(40, 9.4), P(52, 6)], "w": 1.3, "depth": 1.7,
                       "glow": True, "sym": True}]}),
    pl("b_throat", "ivory2", PL, half=half_region(BELL, 52, 86, 1.3), tier={"inset": 1.2, "dz": 0.5, "mat": "ivory"}),
    pl("b_collar", "slate", [6.6, 8.8], half=[P(0, 90), P(33, 91), P(34.4, 111), P(0, 112)],
       tier={"inset": 1.0, "dz": 0.4, "mat": "ivory2"}),
    pl("b_root", "ivory", PL, half=half_region(BELL, 116, 155, 1.2), tier={"inset": 1.1, "dz": 0.5, "mat": "ivory"}),
]
bell = module("rsl_cantor_bell", "Cantor Bell", [128, BEH], BELL, be,
              [conduit([(0, 152), (0, 116)], 1.4), node((0, 114), 2.2), conduit([(0, 88), (0, 34)], 1.3),
               node((0, 32), 2.2),
               {"type": "cell", "pos": [20, 62], "size": [6, 14], "n": 3, "v": 1.2, "sym": True},
               {"type": "vent", "pos": [14, 140], "w": 7, "n": 4, "step": 1.2, "sym": True}],
              [{"id": "WS0001", "pos": [22, 44], "size": "MEDIUM", "type": "HYBRID", "mount": "TURRET", "angle": 15, "arc": 240, "sym": True},
               {"id": "WS0002", "pos": [48, 10], "size": "SMALL", "type": "ENERGY", "mount": "TURRET", "angle": 30, "arc": 270, "sym": True},
               {"id": "WS0003", "pos": [30, 22], "size": "SMALL", "type": "ENERGY", "mount": "TURRET", "angle": 0, "arc": 270, "sym": True},
               {"id": "WS0004", "pos": [0, 134], "size": "MEDIUM", "type": "ENERGY", "mount": "TURRET", "angle": 0, "arc": 300}],
              [{"type": "band", "pts": [P(0, 36), P(0, 152)], "w": 9, "color": "navy", "sym": False},
               navy([(40, 4), (57, 0), (62, 8), (52, 16), (47, 12)]),
               {"type": "gradient", "color": "navy", "poly": [P(0, 0), P(64, 0), P(64, 50), P(0, 50)], "a": [0, 48],
                "b": [0, 10], "a0": 0.0, "a1": 0.45}],
              seed=13)

# ---- CHOIR LOFT: hangar petal, a broad deck with two launch bays, swept side fins
LOH = 156
LOFT = [(0, 12), (16, 8), (34, 14), (46, 2), (52, 12), (52, 40), (66, 52), (68, 64), (54, 62), (50, 84), (40, 92),
        (41, 112), (34, 116), (30, 134), (36, 146), (30, 156), (0, 156)]
lo = [
    pl("l_deck", "ivory2", PL, half=half_region(LOFT, 8, 86, 1.3), tier={"inset": 1.2, "dz": 0.5, "mat": "ivory"}),
    pl("l_bays", "slate", [6.6, 8.6], sym_poly=[P(8, 28), P(36, 28), P(38, 60), P(8, 62)],
       tier={"inset": 0.9, "dz": 0.4, "mat": "ivory2",
             "cuts": [groove(closed([P(12, 34), P(32, 34), P(32, 44), P(12, 44)])),
                      groove(closed([P(12, 48), P(33, 48), P(33, 56), P(12, 56)])),
                      glow([P(36, 31), P(37, 58)], 1.0, 1.4)]}),
    pl("l_fin", "ivory", RL, sym_poly=[P(53, 42), P(65.4, 52.6), P(66.4, 61.4), P(55, 59.6)],
       tier={"inset": 0.7, "dz": 0.4, "mat": "ivory"}),
    pl("l_collar", "slate", [6.6, 8.8], half=[P(0, 92), P(39.4, 93), P(40.4, 111), P(0, 112)],
       tier={"inset": 1.0, "dz": 0.4, "mat": "ivory2"}),
    pl("l_root", "ivory", PL, half=half_region(LOFT, 116, 155, 1.2), tier={"inset": 1.1, "dz": 0.5, "mat": "ivory"}),
]
loft = module("rsl_cantor_loft", "Cantor Choir Loft", [140, LOH], LOFT, lo,
              [conduit([(0, 152), (0, 116)], 1.4), node((0, 114), 2.2), conduit([(0, 90), (0, 66)], 1.3),
               node((0, 64), 2.2),
               {"type": "cell", "pos": [0, 20], "size": [6, 8], "n": 2, "v": 1.0},
               {"type": "vent", "pos": [16, 140], "w": 7, "n": 4, "step": 1.2, "sym": True}],
              [{"id": "WS0001", "pos": [22, 44], "size": "LARGE", "type": "LAUNCH_BAY", "mount": "HIDDEN", "angle": 0, "arc": 360, "sym": True},
               {"id": "WS0002", "pos": [44, 18], "size": "SMALL", "type": "ENERGY", "mount": "TURRET", "angle": 20, "arc": 260, "sym": True},
               {"id": "WS0003", "pos": [0, 76], "size": "MEDIUM", "type": "ENERGY", "mount": "TURRET", "angle": 0, "arc": 300},
               {"id": "WS0004", "pos": [0, 134], "size": "MEDIUM", "type": "HYBRID", "mount": "TURRET", "angle": 0, "arc": 300}],
              [{"type": "band", "pts": [P(0, 66), P(0, 152)], "w": 9, "color": "navy", "sym": False},
               {"type": "band", "pts": [P(2, 16), P(16, 12.4), P(33, 18), P(45.6, 8)], "w": 3, "color": "navy",
                "sym": True},
               navy([(34, 14), (46, 2), (52, 12), (44, 14)]), navy([(54, 44), (66, 52), (68, 64), (56, 60)])],
              seed=17)

for part in (core["layers"], core["details"], core["slots"], core["livery"]):
    walk(part, SCALE)
for spec in (core, ring, spire, bell, loft):
    dump(spec, OUT)
