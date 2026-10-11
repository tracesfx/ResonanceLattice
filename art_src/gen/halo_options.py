"""Flat silhouette sketches for choosing the Halo direction (not sprites).

python art_src/gen/halo_options.py art_src/review/halo_options.png
Each option is a list of (material, mode, polygon) masses stacked in order:
mode "h" = half outline touching the centre line (mirrored); "m" = off-centre part drawn with its mirror image;
"f" = full polygon drawn as is (ring segments; the spinning ring may be asymmetric: its teeth show the spin).
The ring is drawn semi-transparent over the hull on a second pass so the threading reads.
"""
import math
import sys

from PIL import Image, ImageDraw

C = {"frame": (52, 55, 60), "steel": (176, 182, 190), "mid": (122, 128, 136), "gun": (70, 74, 80),
     "navy": (40, 58, 96), "seam": (90, 220, 210), "well": (24, 26, 31), "bay": (28, 32, 40),
     "rframe": (60, 64, 72), "rsteel": (150, 158, 170)}


def bar(a, b, w):
    (x0, y0), (x1, y1) = a, b
    dx, dy = x1 - x0, y1 - y0
    n = (dx * dx + dy * dy) ** 0.5
    ox, oy = -dy / n * w / 2, dx / n * w / 2
    return [(x0 + ox, y0 + oy), (x1 + ox, y1 + oy), (x1 - ox, y1 - oy), (x0 - ox, y0 - oy)]


def pt(cx, cy, r, a):
    a = math.radians(a)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def arc(cx, cy, r, a0, a1, n=24):
    return [pt(cx, cy, r, a0 + (a1 - a0) * i / n) for i in range(n + 1)]


def ring(cx, cy, r0, r1, nseg, gap=6, teeth=0, td=0, flip=False, bays=True, spokes=0):
    """Segmented ring around (cx, cy): frame segments with swept sawtooth outer edge, steel face, seam, bays."""
    out = []
    step = 360 / nseg
    for k in range(nseg):
        c = -90 + k * step
        a0, a1 = c - step / 2 + gap / 2, c + step / 2 - gap / 2
        outer = []
        if teeth:
            for j in range(teeth):
                t0 = a0 + (a1 - a0) * j / teeth
                t1 = a0 + (a1 - a0) * (j + 1) / teeth
                lo, hi = (r1, r1 - td) if flip else (r1 - td, r1)
                outer += [pt(cx, cy, lo, t0), pt(cx, cy, hi, t1 - 0.01)]
        else:
            outer = arc(cx, cy, r1, a0, a1)
        inner = arc(cx, cy, r0, a1, a0)
        out.append(("rframe", "f", outer + inner))
        w = r1 - r0
        face = arc(cx, cy, r1 - td - 2, a0 + 2, a1 - 2) + arc(cx, cy, r0 + 3, a1 - 2, a0 + 2)
        out.append(("rsteel", "f", face))
        rm = r0 + w * 0.42
        out.append(("seam", "f", arc(cx, cy, rm + 1.2, a0 + 3, a1 - 3) + arc(cx, cy, rm - 1.2, a1 - 3, a0 + 3)))
        if bays:
            bm = c
            out.append(("bay", "f", arc(cx, cy, r1 - td - 4, bm - 5, bm + 5, 4) + arc(cx, cy, rm + 4, bm + 5, bm - 5, 4)))
    for k in range(spokes):
        a = -90 + step / 2 + k * 360 / spokes
        out.append(("rframe", "f", bar(pt(cx, cy, 14, a), pt(cx, cy, r0 + 2, a), 8)))
        out.append(("seam", "f", bar(pt(cx, cy, 14, a), pt(cx, cy, r0 + 2, a), 2)))
    return out


def circle(cx, cy, r, n=48):
    return arc(cx, cy, r, 0, 360, n)


def hexa(cx, cy, r):
    return [pt(cx, cy, r, 30 + 60 * i) for i in range(6)]


def spar(a, b, w=7):
    return [("frame", "m", bar(a, b, w)), ("seam", "m", bar(a, b, 2))]


# ---------------------------------------------------------------- A: spear threaded through one big ring
A_HULL = [
    ("frame", "h", [(0, 0), (5, 16), (10, 20), (13, 52), (26, 60), (36, 54), (38, 64), (26, 78), (30, 118),
                    (50, 132), (56, 168), (46, 184), (54, 222), (38, 244), (44, 282), (60, 300), (82, 334), (82, 350), (62, 344),
                    (46, 336), (42, 360), (28, 374), (0, 374)]),
    ("steel", "h", [(0, 4), (4, 18), (9, 22), (11, 52), (0, 52)]),
    ("mid", "h", [(0, 58), (22, 62), (24, 80), (28, 116), (0, 116)]),
    ("navy", "h", [(0, 122), (46, 136), (51, 168), (41, 184), (48, 222), (0, 232)]),
    ("steel", "h", [(0, 238), (34, 244), (40, 280), (0, 290)]),
    ("gun", "h", [(0, 296), (42, 300), (40, 334), (26, 366), (0, 368)]),
    ("seam", "h", [(0, 170), (9, 180), (0, 190)]),
    ("seam", "m", [(8, 26), (10, 26), (11, 50), (9, 50)]),
    # bearing yokes where the ring crosses the spine + ring pylons at the waist
    ("gun", "h", [(0, 56), (32, 58), (38, 74), (30, 84), (0, 84)]),
    ("gun", "h", [(0, 298), (40, 298), (46, 314), (38, 322), (0, 322)]),
] + spar((52, 160), (112, 136), 9) + spar((50, 220), (112, 244), 9) + [
    ("gun", "m", [(104, 128), (118, 134), (118, 146), (106, 146)]),
    ("gun", "m", [(104, 236), (118, 236), (118, 250), (106, 254)]),
]
A_RING = ring(0, 190, 106, 130, 6, gap=7, teeth=4, td=5)

# ---------------------------------------------------------------- B: orrery, two counter-rotating outrigger rings
B_HULL = [
    ("frame", "h", [(0, 0), (5, 18), (10, 22), (14, 60), (28, 68), (26, 82), (36, 114), (50, 128), (54, 160), (44, 176), (44, 214), (54, 232),
                    (48, 252), (40, 264), (50, 300), (66, 330), (62, 350), (44, 346), (36, 372), (0, 372)]),
    # sponson arms out to the ring hubs, with a forward fin each
    ("frame", "m", [(44, 164), (74, 154), (100, 174), (140, 178), (140, 206), (100, 212), (74, 236), (44, 230)]),
    ("frame", "m", [(80, 158), (90, 116), (98, 110), (100, 166)]),
    ("steel", "h", [(0, 4), (4, 20), (9, 24), (12, 60), (0, 60)]),
    ("navy", "h", [(0, 66), (24, 72), (22, 84), (32, 116), (0, 120)]),
    ("steel", "h", [(0, 126), (46, 132), (50, 160), (40, 176), (40, 214), (50, 234), (44, 250), (0, 250)]),
    ("navy", "m", [(48, 170), (72, 160), (94, 176), (94, 208), (72, 228), (48, 224)]),
    ("gun", "h", [(0, 256), (36, 264), (46, 300), (60, 330), (40, 340), (30, 366), (0, 366)]),
    ("seam", "h", [(0, 180), (9, 190), (0, 200)]),
    ("seam", "m", [(10, 189), (130, 189), (130, 191), (10, 191)]),
    ("gun", "m", hexa(134, 192, 15)),
    ("seam", "m", [(134, 184), (140, 192), (134, 200), (128, 192)]),
]
B_RING = ring(136, 192, 46, 64, 5, gap=8, teeth=3, td=4) + [(m, "f", [(-x, y) for x, y in p]) for m, _, p in ring(136, 192, 46, 64, 5, gap=8, teeth=3, td=4)]

# ---------------------------------------------------------------- C: eye, hull wraps around a ring set in a well
C_HULL = [
    ("frame", "h", [(0, 0), (6, 20), (11, 24), (14, 58), (40, 72), (88, 80), (112, 38), (124, 50), (136, 104),
                    (146, 160), (134, 176), (140, 226), (122, 262), (126, 290), (104, 300), (86, 326), (62, 334),
                    (58, 352), (40, 360), (28, 376), (0, 376)]),
    ("steel", "h", [(0, 4), (5, 22), (10, 26), (12, 58), (0, 58)]),
    ("navy", "m", [(96, 80), (112, 46), (122, 54), (134, 108), (130, 120), (104, 116)]),
    ("steel", "m", [(102, 122), (132, 124), (142, 160), (130, 176), (134, 224), (112, 230)]),
    ("navy", "m", [(110, 238), (132, 232), (118, 262), (120, 284), (100, 290)]),
    ("gun", "h", [(0, 290), (96, 292), (82, 320), (58, 328), (54, 346), (36, 354), (26, 368), (0, 368)]),
    ("mid", "h", [(0, 64), (38, 76), (86, 84), (98, 100), (0, 100)]),
    ("seam", "m", [(98, 84), (100, 82), (124, 132), (122, 134)]),
    ("seam", "m", [(122, 134), (124, 134), (130, 230), (128, 230)]),
    ("seam", "h", [(0, 20), (5, 26), (0, 32)]),
    ("well", "f", circle(0, 190, 98)),
    ("gun", "f", hexa(0, 190, 16)),
    ("seam", "f", [(0, 180), (8, 190), (0, 200), (-8, 190)]),
]
C_RING = ring(0, 190, 70, 92, 6, gap=6, teeth=4, td=4, spokes=3)

OPTIONS = {
    "A  Spear: slim hull threaded through one big ring": (A_HULL, A_RING),
    "B  Orrery: twin counter-rotating outrigger rings": (B_HULL, B_RING),
    "C  Eye: hull wraps a ring spinning in a central well": (C_HULL, C_RING),
}


def draw(d, masses, ox, oy, S):
    for mat, mode, pts in masses:
        if mode == "m":
            polys = [pts, [(-x, y) for x, y in pts]]
        elif mode == "h":
            polys = [list(pts) + [(-x, y) for x, y in reversed(pts) if x > 0]]
        else:
            polys = [pts]
        for poly in polys:
            d.polygon([(ox + x * S, oy + y * S) for x, y in poly], fill=C[mat],
                      outline=None if mat in ("seam", "bay") else (20, 22, 26))


def main(out):
    S, pad, W, H = 2, 30, 330, 380
    sheet = Image.new("RGB", ((W * S + pad) * len(OPTIONS) + pad, H * S + 70 + H + 20), (14, 17, 22))
    d = ImageDraw.Draw(sheet)
    for i, (name, (hull, rng)) in enumerate(OPTIONS.items()):
        ox = pad + i * (W * S + pad) + W * S // 2
        d.text((ox - W * S // 2, 8), name, fill=(200, 205, 210))
        draw(d, hull, ox, 40, S)
        draw(d, rng, ox, 40, S)
        # 1x thumbnail below (judge the silhouette at game scale)
        draw(d, hull, ox, 60 + H * S, 1)
        draw(d, rng, ox, 60 + H * S, 1)
    sheet.save(out)
    print(out)


main(sys.argv[1])
