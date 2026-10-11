"""Generate art_src/specs/rsl_cadence.json (arrowhead body + diagonal stair-stepped flank rails from formulas).

python art_src/gen/gen_cadence.py art_src/specs/rsl_cadence.json   # then ./art_src/art.sh rsl_cadence
"""
import json
import sys

K = 0.16                       # rail taper (x per y)
I = lambda y: 16 + (y - 30) * K          # rail inner edge
STEP = [(30, 62, 0.0), (65, 120, 3.0), (123, 180, 6.0), (183, 252, 9.0)]   # rail segments (y0, y1, outward stair offset)
RW = 13.0                       # base rail width
O = lambda y, e: I(y) + RW + e           # rail outer edge (segment shifted outward by e)
In = lambda y, e: I(y) + e               # rail inner edge of a segment
def B(y):
    """Body plate edge: in front it hugs the rail (graphite channel), aft of the gap it tapers inward."""
    if y < 150:
        e = 0 if y < 64 else 3 if y < 122 else 6
        return I(y) + e - 3.2
    return I(150) + 6 - 3.2 - (y - 150) * 0.05

r = lambda v: round(v, 2)


def P(x, y):
    return [r(x), r(y)]


# ---------------- frame: body outline (half) + rail outline (sym_poly) + struts. Rails hug the body in front and
# separate from it aft of y=150 (real negative space between them).
GAP_Y = 152
body_frame = [P(0, 0), P(2.5, 7), P(3.2, 18), P(7, 22), P(7.6, 36), P(11, 39), P(11.6, 50), P(14.6, 52),
              P(In(56, 0), 56), P(In(64, 0), 64), P(In(66, 3), 66), P(In(121, 3), 121), P(In(123, 6), 123),
              P(In(GAP_Y - 4, 6), GAP_Y - 4), P(B(GAP_Y + 4) + 1, GAP_Y + 4), P(B(232) + 1, 232),
              P(In(238, 9), 238), P(In(246, 9) - 0.6, 249.5), P(35, 252), P(30.5, 259.5), P(24, 266), P(0, 268)]
rail_frame = [P(In(30, 0) - 0.6, 30), P(I(30) + 7, 20), P(O(30, 0) + 0.8, 27)]
for y0, y1, e in STEP:
    rail_frame += [P(O(y0, e) + 0.8, y0 - 1.5 if e else y0), P(O(y1, e) + 0.8, y1 + 1.5)]
rail_frame += [P(O(258, 9), 262), P(In(258, 9) + 2, 264), P(In(252, 9) - 0.8, 254)]
for y0, y1, e in reversed(STEP):
    rail_frame += [P(In(y1, e) - 0.8, y1 + 1.5), P(In(y0, e) - 0.8, y0 - 1.5 if e else y0)]
struts = [[P(B(y) - 1, y), P(In(y, 9) + 1, y), P(In(y + 6, 9) + 1, y + 6), P(B(y + 6) - 1, y + 6)] for y in (192,)]
frame = body_frame + rail_frame
layers = [{"name": "frame", "mat": "graphite", "z": [0, 3.0], "bevel": 0.7, "half": body_frame, "sym_poly": rail_frame},
          {"name": "strut", "mat": "graphite", "z": [0, 3.4], "bevel": 0.5, "sym_poly": struts[0]}]

layers.append({"name": "spear", "mat": "ivory", "z": [4.4, 6.6], "bevel": 0.5,
               "half": [P(0, 1.5), P(2, 7.5), P(2.6, 18.6), P(6.2, 22.6), P(6.8, 36.6), P(10.2, 39.6), P(10.8, 50), P(0, 54)],
               "cuts": [{"pts": [P(2.2, 20.4), P(5.8, 23.6)], "w": 0.55, "depth": 0.5, "sym": True},
                        {"pts": [P(6.8, 38.4), P(10, 41.2)], "w": 0.55, "depth": 0.5, "sym": True}],
               "tiers": [{"inset": 1.0, "dz": 0.5, "mat": "ivory"}]})


def chevron_plate(name, y0, y1, mat, v=6.0, tier_mat="ivory", cuts=None):
    """Body segment: forward-pointing chevron top and bottom edges, sides follow the body edge."""
    half = [P(0, y0), P(B(y0 + v), y0 + v), P(B(y1 + v), y1 + v), P(0, y1)]
    L = {"name": name, "mat": mat, "z": [4.0, 6.2], "bevel": 0.6, "half": half,
         "tiers": [{"inset": 1.8, "dz": 0.6, "mat": tier_mat}]}
    if cuts:
        L["tiers"][0]["cuts"] = cuts
    return L


layers.append({"name": "prow", "mat": "ivory", "z": [4.0, 6.2], "bevel": 0.6,
               "half": [P(0, 52), P(11.6, 53), P(B(56), 56), P(B(76), 76), P(0, 70)],
               "tiers": [{"inset": 1.4, "dz": 0.5, "mat": "ivory"}]})
layers.append(chevron_plate("deck", 72.5, 82, "slate", tier_mat="ivory2"))
layers.append(chevron_plate("body1", 84.5, 138, "ivory",
                            cuts=[{"pts": [P(-20, 102), P(0, 97), P(20, 102)], "w": 0.55, "depth": 0.5},
                                  {"pts": [P(-20, 124), P(0, 119), P(20, 124)], "w": 0.55, "depth": 0.5},
                                  {"pts": [P(7.5, 90), P(7.5, 133)], "w": 0.5, "depth": 0.45, "sym": True}]))
layers.append(chevron_plate("body2", 140.5, 198, "ivory",
                            cuts=[{"pts": [P(-24, 158), P(0, 153), P(24, 158)], "w": 0.55, "depth": 0.5},
                                  {"pts": [P(-24, 192), P(0, 187), P(24, 192)], "w": 0.55, "depth": 0.5},
                                  {"pts": [P(7.5, 146), P(7.5, 194)], "w": 0.5, "depth": 0.45, "sym": True}]))
layers.append(chevron_plate("body3", 200.5, 236, "ivory", tier_mat="slate"))
layers.append({"name": "spine", "mat": "slate", "z": [7.2, 8.6], "bevel": 0.6,
               "half": [P(0, 86), P(5.4, 90), P(6, 196), P(3.4, 202), P(0, 203)],
               "tiers": [{"inset": 0.9, "dz": 0.45, "mat": "ivory2"}]})
layers.append({"name": "aft", "mat": "slate", "z": [3.8, 5.8], "bevel": 0.6,
               "half": [P(0, 236.5), P(B(234) + 0.4, 234.5), P(In(240, 9) + 0.2, 240), P(In(245, 9) - 1.4, 248), P(34, 250.4), P(29.6, 258.4), P(23, 264.4), P(0, 266)],
               "tiers": [{"inset": 1.3, "dz": 0.45, "mat": "ivory2"}]})

# rails: 4 segments, each a separate plate; front one ends in the diagonal-cut prong
for k, (y0, y1, e) in enumerate(STEP):
    a, b = y0 + 1.2, y1 - 1.2
    if k == 0:
        poly = [P(In(31, e) + 0.6, 31.5), P(I(30) + 7, 21.6), P(O(30, 0) - 0.6, 28), P(O(b, e) - 0.6, b), P(In(b, e) + 0.6, b)]
    elif k == 3:
        poly = [P(In(a, e) + 0.6, a), P(O(a, e) - 0.6, a), P(O(250, e) - 0.6, 250), P(O(258, e) - 1.4, 260.4), P(In(258, e) + 2.4, 262), P(In(252, e) + 0.6, 254)]
    else:
        poly = [P(In(a, e) + 0.6, a), P(O(a, e) - 0.6, a), P(O(b, e) - 0.6, b), P(In(b, e) + 0.6, b)]
    L = {"name": "rail%d" % (k + 1), "mat": "ivory", "z": [4.0, 6.2], "bevel": 0.6, "sym_poly": poly,
         "tiers": [{"inset": 1.4, "dz": 0.6, "mat": "slate" if k == 0 else "ivory"}]}
    if k in (1, 2):   # accelerator line down the rail centre
        c0, c1 = a + 3, b - 3
        L["tiers"][0]["cuts"] = [{"pts": [P(In(c0, e) + RW / 2, c0), P(In(c1, e) + RW / 2, c1)],
                                  "w": 1.5, "depth": 2.0, "glow": True, "sym": True}]
    if k == 0:        # prong leading-edge emitter
        L["cuts"] = [{"pts": [P(I(33) + 1.8, 31.8), P(I(30) + 7, 24.6), P(O(30, 0) - 2.2, 29.6)],
                      "w": 1.1, "depth": 1.4, "glow": True, "sym": True}]
    layers.append(L)

rc = lambda y, e: r(In(y, e) + RW / 2)      # rail centre line
details = [
    {"type": "node", "pos": [0, 150], "r": 3.0, "shape": "diamond"},
    {"type": "cell", "pos": [0, 61], "size": [5, 5], "n": 2, "v": 1.0},
    {"type": "conduit", "pos": [0, 0], "pts": [[0, 8], [0, 48]], "w": 1.1},
    {"type": "conduit", "pos": [0, 0], "pts": [P(6, 142), P(B(142) - 6, 142), P(B(142) - 2, 138), P(rc(138, 6) - 1.5, 138)], "w": 1.3, "sym": True},
    {"type": "conduit", "pos": [0, 0], "pts": [P(rc(195, 9) - 2, 195), P(B(195) + 1, 195), P(B(195) - 6, 195)], "w": 1.1, "sym": True},
    {"type": "node", "pos": P(rc(68, 3), 68.4), "r": 2.2, "sym": True},
    {"type": "node", "pos": P(rc(117, 3), 117), "r": 2.2, "sym": True},
    {"type": "node", "pos": P(rc(138, 6), 138), "r": 2.4, "sym": True},
    {"type": "node", "pos": P(rc(176, 6), 176), "r": 2.2, "sym": True},
    {"type": "node", "pos": P(rc(195, 9), 195), "r": 2.2, "sym": True},
    {"type": "node", "pos": P(rc(232, 9), 232), "r": 2.2, "sym": True},
    {"type": "vent", "pos": [31, 240], "w": 5, "n": 5, "step": 1.2, "sym": True},
    {"type": "vent", "pos": [26, 104], "w": 3.6, "n": 4, "step": 1.1, "sym": True},
    {"type": "vent", "pos": [28, 162], "w": 3.6, "n": 4, "step": 1.1, "sym": True},
    {"type": "cell", "pos": [13, 172], "size": [7, 22], "n": 5, "v": 1.5, "sym": True},
    {"type": "cell", "pos": [12, 112], "size": [6.4, 14], "n": 4, "v": 1.4, "sym": True},
    {"type": "conduit", "pos": [0, 0], "pts": [P(13, 184), P(13, 224), P(20, 231), P(20, 240)], "w": 1.1, "sym": True},
    {"type": "vent", "pos": [0, 214], "w": 7, "n": 6, "step": 1.3},
    {"type": "vent", "pos": [26, 206], "w": 4, "n": 5, "step": 1.2, "sym": True},
    {"type": "block", "pos": [22, 96], "size": [3, 7], "h": 0.5, "mat": "steel", "sym": True},
    {"type": "block", "pos": [8, 226], "size": [3, 7], "h": 0.4, "mat": "steel", "sym": True},
    {"type": "hatch", "pos": [27, 160], "r": 2.0, "sym": True},
    {"type": "mark", "pos": [0, 0], "pts": [P(18, 128), P(23, 124)], "w": 0.7, "sym": True},
    {"type": "mark", "pos": [0, 0], "pts": [P(18, 131), P(24.4, 126)], "w": 0.7, "sym": True},
    {"type": "light", "pos": P(I(30) + 7, 23.4), "r": 0.7, "sym": True},
]
slots = [
    {"id": "WS0001", "pos": P(rc(46, 0), 46), "size": "LARGE", "type": "ENERGY", "mount": "HARDPOINT", "angle": 0, "arc": 10, "sym": True},
    {"id": "WS0003", "pos": [0, 64], "size": "MEDIUM", "type": "HYBRID", "mount": "TURRET", "angle": 0, "arc": 270},
    {"id": "WS0004", "pos": [17, 130], "size": "MEDIUM", "type": "ENERGY", "mount": "TURRET", "angle": 20, "arc": 240, "sym": True},
    {"id": "WS0006", "pos": [24, 222], "size": "SMALL", "type": "ENERGY", "mount": "TURRET", "angle": 90, "arc": 200, "sym": True},
    {"id": "WS0008", "pos": P(rc(214, 9), 214), "size": "SMALL", "type": "ENERGY", "mount": "TURRET", "angle": 60, "arc": 220, "sym": True},
    {"id": "WS0010", "pos": [12, 251], "size": "SMALL", "type": "MISSILE", "mount": "TURRET", "angle": 150, "arc": 180, "sym": True},
]
engines = [{"pos": [0, 266], "width": 12}, {"pos": [22, 262], "width": 7, "sym": True},
           {"pos": P(rc(258, 9), 262), "width": 6, "length": 22, "sym": True}]
W = int(2 * (max(p[0] for p in frame) + 2) + 1) // 2 * 2
H = 270
spec = {"id": "rsl_cadence", "name": "Cadence", "hullSize": "CRUISER", "size": [W, 270], "layers": layers,
        "greebles": {"layers": ["frame"], "z0": 3.0, "zmax": 3.9, "density": 1.0, "seed": 31},
        "surface_detail": {"layers": ["prow", "deck", "body1", "body2"], "density": 0.08, "seed": 19},
        "details": details, "slots": slots, "engines": engines, "ship": {"builtInMods": []}}
json.dump(spec, open(sys.argv[1], "w", newline="\n"), indent=1)
print("W", W, "max x", max(p[0] for p in frame))
