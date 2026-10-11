"""Generate art_src/specs/rsl_cadence.json.

python art_src/gen/gen_cadence.py art_src/specs/rsl_cadence.json   # then ./art_src/art.sh rsl_cadence

Direction chosen by the user (2026-10-11, option C of art_src/review/cadence_options.png, "make the rails longer;
the design goal is an arrowhead"):
  long stepped needle bow -> faceted head -> the two rails sweep back from the shoulders as long BARBS of an
  arrowhead -> narrow waist -> engine block with pods.
Each barb is attached to the body along a long root through web plates (no fragile free-standing rails); only the
last third of the barb is free, which makes the arrowhead notch. Rails are raised, segmented (stepped outward),
carry glowing accelerator lines, turret blisters on their outer edge and a small thruster at the tip.
Earlier rejected versions: rectangle, isosceles triangle with free-standing rails, box, egg, rocket.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from scale_spec import walk  # noqa: E402

SCALE = 1.14        # final size factor (keeps the cruiser in the vanilla pixel-mass band)

r = lambda v: round(v, 2)


def P(x, y):
    return [r(x), r(y)]


def octa(cx, cy, rad):
    return [P(cx + rad * math.cos(math.radians(22.5 + 45 * i)), cy + rad * math.sin(math.radians(22.5 + 45 * i)))
            for i in range(8)]


def shrink(poly, k):
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    return [P(x - (x - cx) / (math.hypot(x - cx, y - cy) or 1) * k, y - (y - cy) / (math.hypot(x - cx, y - cy) or 1) * k)
            for x, y in poly]


# ------------------------------------------------------------------ the barb (right rail) geometry
A, B, RW = (24.0, 92.0), (68.0, 206.0), 16.0           # rail centre line start/end, rail width
LEN = math.hypot(B[0] - A[0], B[1] - A[1])
D = ((B[0] - A[0]) / LEN, (B[1] - A[1]) / LEN)          # along the rail (aft-outward)
N = (D[1], -D[0])                                       # outward normal (+x, -y)


def C(t, s=0.0):
    """Point on the rail: t along (0 root .. 1 tip), s across (+ outward, - inward), in px."""
    return (A[0] + (B[0] - A[0]) * t + N[0] * s, A[1] + (B[1] - A[1]) * t + N[1] * s)


def CP(t, s=0.0):
    return P(*C(t, s))


def seg(t0, t1, s_in, s_out, c=1.6):
    """Rail segment quad with chamfered outer corners."""
    dt = c / LEN
    return [CP(t0, s_in), CP(t0, s_out - c), CP(t0 + dt, s_out), CP(t1 - dt, s_out), CP(t1, s_out - c), CP(t1, s_in)]


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


H = 280
BODY = [P(0, 0), P(1.8, 8), P(2.6, 20), P(5, 24), P(5.6, 38), P(8.4, 42), P(9, 56), P(12.6, 60), P(16, 72),
        P(20.5, 84), P(24, 92), P(27, 100), P(27.5, 192), P(24, 202), P(24, 214), P(29, 222), P(31, 252), P(25, 264),
        P(14.5, 268), P(10.5, 278), P(0, 278)]
TF = 0.66                                    # the barb is attached up to here; free beyond (arrowhead notch)
WEB = [P(26, 99), CP(0.04, -RW / 2 + 0.5), CP(TF, -RW / 2 + 0.5), P(26.6, 176)]
TIP = 1.14                                   # sharp swept-wing tip (user, 2026-10-11): no blunt cap, no tip thruster
RAIL = [CP(0, -RW / 2), CP(0, RW / 2 - 2), CP(0.02, RW / 2), CP(0.36, RW / 2), CP(0.37, RW / 2 + 2.2),
        CP(0.70, RW / 2 + 2.2), CP(0.71, RW / 2 + 4), CP(TIP, RW / 2 + 4.6), CP(0.80, -RW / 2)]
POD = [P(29, 224), P(36, 222), P(41, 230), P(42, 252), P(36.5, 260), P(30.5, 258)]

# ------------------------------------------------------------------ silhouette
frame("f_body", half=BODY)
frame("f_rail", sym_poly=RAIL)
frame("f_pod", sym_poly=POD)
frame("f_vane", sym_poly=[P(12.4, 62), P(17.5, 60), P(20, 64), P(16.4, 70)])         # small forward canards

# ------------------------------------------------------------------ plates
plate("spear", "ivory", [4.4, 6.6], bevel=0.5,
      half=[P(0, 1.5), P(1.4, 8.4), P(2.1, 20.4), P(4.4, 24.6), P(5, 38.4), P(7.6, 42.6), P(8.2, 55.6), P(0, 58)],
      cuts=[{"pts": [P(2.0, 22.4), P(4.4, 25.4)], "w": 0.5, "depth": 0.45, "sym": True},
            {"pts": [P(5.2, 40.4), P(7.6, 43.4)], "w": 0.5, "depth": 0.45, "sym": True}],
      tier={"inset": 0.9, "dz": 0.5, "mat": "ivory"})
plate("canard", "ivory2", [3.8, 5.8], sym_poly=shrink([P(12.4, 62), P(17.5, 60), P(20, 64), P(16.4, 70)], 0.7))
plate("head_a", "ivory", PL, half=[P(0, 56.6), P(11.6, 60.6), P(15, 72), P(19, 82.6), P(0, 76)],
      tier={"inset": 1.4, "dz": 0.6, "mat": "ivory"})
plate("head_b", "slate", PL, half=[P(0, 78), P(19.6, 84.6), P(22.8, 92), P(0, 88)],
      tier={"inset": 1.2, "dz": 0.5, "mat": "ivory2"})
plate("body1", "ivory", PL, half=[P(0, 90.4), P(22.6, 94), P(25.6, 100.6), P(25.8, 146), P(0, 142)],
      tier={"inset": 1.6, "dz": 0.6, "mat": "ivory",
            "cuts": [{"pts": [P(-20, 122), P(0, 118), P(20, 122)], "w": 0.55, "depth": 0.5}]})
plate("body2", "ivory", PL, half=[P(0, 145), P(25.8, 149), P(26, 190), P(22.8, 199), P(0, 196)],
      tier={"inset": 1.6, "dz": 0.6, "mat": "ivory",
            "cuts": [{"pts": [P(-20, 172), P(0, 168), P(20, 172)], "w": 0.55, "depth": 0.5}]})
plate("spine", "slate", [6.8, 8.4], half=[P(0, 92), P(4.6, 95), P(5, 192), P(3, 197), P(0, 198)],
      tier={"inset": 0.8, "dz": 0.45, "mat": "ivory2"})
# barb: three raised segments stepping outward + a gunmetal tip
for k, (t0, t1, so) in enumerate(((0.0, 0.355, RW / 2), (0.375, 0.69, RW / 2 + 2.2))):
    tier = {"inset": 1.3, "dz": 0.6, "mat": "ivory"}
    tier["cuts"] = [{"pts": [CP(t0 + 0.03, 0.6), CP(t1 - 0.03, 0.6)], "w": 1.6, "depth": 2.2, "glow": True, "sym": True}]
    plate("rail%d" % k, "ivory", RL, sym_poly=seg(t0 + 0.004, t1, -RW / 2 + 1.2, so - 1.2), tier=tier)
# last segment = the swept tip blade (tapers to the point)
plate("rail2", "ivory", RL, sym_poly=[CP(0.715, -RW / 2 + 1.3), CP(0.715, RW / 2 + 2.8), CP(TIP - 0.03, RW / 2 + 3.4),
                                      CP(0.81, -RW / 2 + 1.3)],
      tier={"inset": 1.2, "dz": 0.5, "mat": "ivory",
            "cuts": [{"pts": [CP(0.74, 4.6), CP(1.0, 7.4)], "w": 1.4, "depth": 2.0, "glow": True, "sym": True}]})
for k, t in enumerate((0.365, 0.70)):                   # gunmetal clamps between barb segments
    plate("clamp%d" % k, "slate", [6.4, 8.6], bevel=0.4,
          sym_poly=[CP(t - 0.014, -RW / 2 - 1), CP(t - 0.014, RW / 2 + 3), CP(t + 0.014, RW / 2 + 3), CP(t + 0.014, -RW / 2 - 1)])
plate("aft", "ivory", PL, half=[P(0, 199.6), P(22.6, 202.6), P(22.6, 214.6), P(27.6, 222.6), P(29.2, 240), P(0, 240)],
      tier={"inset": 1.6, "dz": 0.6, "mat": "ivory",
            "cuts": [{"pts": [P(-20, 226), P(0, 222), P(20, 226)], "w": 0.55, "depth": 0.5}]})
plate("aft_b", "slate", PL, half=[P(0, 242.4), P(29.4, 242.4), P(29.6, 251), P(24, 262), P(14, 265.6), P(10, 275),
                                 P(0, 275)],
      tier={"inset": 1.3, "dz": 0.45, "mat": "ivory2"})
plate("pod", "ivory", [4.4, 6.6], sym_poly=shrink(POD, 1.2), tier={"inset": 1.3, "dz": 0.5, "mat": "ivory"})

FRAMES = [L["name"] for L in layers if L["name"].startswith("f_")]
details = [
    {"type": "node", "pos": [0, 150], "r": 3.0, "shape": "diamond"},
    {"type": "cell", "pos": [0, 66], "size": [4.6, 4.6], "n": 2, "v": 1.0},
    {"type": "conduit", "pos": [0, 0], "pts": [[0, 9], [0, 54]], "w": 1.1},
    # core feeds both barbs where they are rooted in the hull (the web platform was removed, user 2026-10-11)
    {"type": "conduit", "pos": [0, 0], "pts": [P(5, 150), P(14, 150), P(14, 116), P(21, 109), CP(0.15, -2.4)], "w": 1.3, "sym": True},
    {"type": "node", "pos": CP(0.52, 0.6), "r": 2.4, "sym": True},
    {"type": "node", "pos": CP(0.20, 0.6), "r": 2.2, "sym": True},
    {"type": "node", "pos": CP(0.80, 4.2), "r": 2.0, "sym": True},
    {"type": "cell", "pos": [12, 124], "size": [6.4, 16], "n": 4, "v": 1.4, "sym": True},
    {"type": "cell", "pos": [12, 176], "size": [6.6, 18], "n": 4, "v": 1.5, "sym": True},
    {"type": "conduit", "pos": [0, 0], "pts": [P(12, 186.6), P(12, 232), P(17, 237), P(17, 244)], "w": 1.1, "sym": True},
    {"type": "vent", "pos": [0, 100], "w": 8, "n": 4, "step": 1.3},
    {"type": "vent", "pos": [19, 216], "w": 4, "n": 6, "step": 1.2, "sym": True},
    {"type": "vent", "pos": [0, 244], "w": 10, "n": 6, "step": 1.3},
    {"type": "block", "pos": [14, 80], "size": [2.6, 5], "h": 0.5, "mat": "steel", "sym": True},
    {"type": "block", "pos": [8, 230], "size": [3, 7], "h": 0.4, "mat": "steel", "sym": True},
    {"type": "hatch", "pos": P(21, 156), "r": 1.8, "sym": True},
    {"type": "light", "pos": CP(TIP - 0.08, RW / 2 + 2.4), "r": 0.6, "sym": True},
    {"type": "light", "pos": P(18.6, 61), "r": 0.5, "sym": True},
    {"type": "mark", "pos": [0, 0], "pts": [P(8.4, 96), P(8.4, 102)], "w": 0.7, "sym": True},
    {"type": "mark", "pos": [0, 0], "pts": [P(10.2, 96), P(10.2, 102)], "w": 0.7, "sym": True},
]
slots = [
    {"id": "WS0001", "pos": CP(0.07, 0.4), "size": "LARGE", "type": "ENERGY", "mount": "HARDPOINT", "angle": 0, "arc": 10, "sym": True},
    {"id": "WS0003", "pos": [0, 80], "size": "MEDIUM", "type": "HYBRID", "mount": "TURRET", "angle": 0, "arc": 270},
    {"id": "WS0004", "pos": CP(0.29, 0.6), "size": "MEDIUM", "type": "ENERGY", "mount": "TURRET", "angle": 45, "arc": 240, "sym": True},
    {"id": "WS0006", "pos": CP(0.60, 1.0), "size": "SMALL", "type": "ENERGY", "mount": "TURRET", "angle": 90, "arc": 220, "sym": True},
    {"id": "WS0008", "pos": P(16, 160), "size": "SMALL", "type": "ENERGY", "mount": "TURRET", "angle": 60, "arc": 240, "sym": True},
    {"id": "WS0010", "pos": P(35.4, 240), "size": "SMALL", "type": "MISSILE", "mount": "TURRET", "angle": 150, "arc": 180, "sym": True},
]
engines = [{"pos": [0, 276], "width": 10}, {"pos": [17.5, 266], "width": 7, "sym": True},
           {"pos": P(35, 259), "width": 6, "length": 22, "sym": True}]
# livery: dark-blue splinter chevrons angled with the barbs (they read as the arrowhead's fletching), a dark-blue
# gradient deepening towards the barb tips, gunmetal needle tip. No yellow (user, 2026-10-11).
ang = math.degrees(math.atan2(N[1], N[0])) + 180
BOW = [P(0, 0), P(30, 0), P(30, 92), P(0, 92)]
MID = [P(0, 92), P(27.5, 92), P(27.5, 200), P(0, 200)]
rail_ang = math.degrees(math.atan2(D[1], D[0]))
livery = [
    # gradients first (no flat steel left), splinters on top -- each region has its own angle and rhythm
    {"type": "gradient", "color": "navy", "a": [0, 150], "b": [0, 276], "a0": 0.0, "a1": 0.75},
    {"type": "gradient", "color": "navy", "a": [0, 112], "b": [0, 40], "a0": 0.0, "a1": 0.6},
    {"type": "gradient", "color": "navy", "poly": RAIL, "a": list(C(0.3)), "b": list(C(TIP)), "a0": 0.0, "a1": 0.9},
    # bow: forward chevrons, tight irregular rhythm
    {"type": "splinter", "color": "navy", "colors": [None, "navy", None, "navy"], "widths": [7, 4, 11, 6],
     "alpha": 0.6, "angle": 62, "poly": BOW},
    # midship: reversed slant + zigzag, broad irregular bands
    {"type": "splinter", "color": "navy", "colors": [None, "navy", None, "navy", None, "navy"],
     "widths": [14, 6, 9, 15, 7, 4], "alpha": 0.55, "angle": -38, "zigzag": 16, "amp": 3, "poly": MID},
    # rails: bands across the barbs (perpendicular to their sweep), getting tighter towards the tips
    {"type": "splinter", "color": "navy", "colors": [None, "navy", None, "navy", None, "navy"],
     "widths": [16, 5, 11, 4, 7, 3], "alpha": 0.5, "angle": rail_ang, "poly": RAIL},
    {"type": "poly", "color": "gunmetal", "sym": False, "poly": [P(-2.6, 0), P(2.6, 0), P(2.6, 12), P(-2.6, 12)]},
]
for part in (layers, details, slots, engines, livery):
    walk(part, SCALE)
W = 2 * int(max(p[0] for L in layers for p in (L.get("half") or L.get("sym_poly"))) + 3)
H = int(math.ceil(H * SCALE))
spec = {"id": "rsl_cadence", "name": "Cadence", "hullSize": "CRUISER", "size": [W, H], "layers": layers,
        "greebles": {"layers": FRAMES, "z0": 3.0, "zmax": 3.9, "density": 1.0, "seed": 31},
        "surface_detail": {"layers": ["head_a", "body1", "body2", "aft"], "density": 0.06, "seed": 19},
        "details": details, "slots": slots, "engines": engines, "livery": livery, "ship": {"builtInMods": []}}
json.dump(spec, open(sys.argv[1], "w", newline="\n"), indent=1)
print("W", W, "rail length", round(LEN, 1), "barb tip", CP(1.0, RW / 2))
