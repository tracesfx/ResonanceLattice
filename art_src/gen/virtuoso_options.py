"""Flat silhouette + livery/seam concept sketches for choosing the Virtuoso direction (not sprites).

python art_src/gen/virtuoso_options.py art_src/review/virtuoso_options.png
Masses as in conductor_options.py ("h" half on the centre line, "m" off-centre part + mirror, "f" full polygon).
Each option also draws the livery+seam idea: ONE dark-blue "sash" (a ribbon running from the prow down the spine and
out along both wings to the tip vanes) whose two edges ARE the seams, so paint and light share the same lines; the big
resonator cells sit inside the sash on the wings. In Bravura the sash edges turn gold. Tip vanes (deco) = lighter
steel. Gold Bravura variant shown on the right half of each sheet entry at 1x.
"""
import math
import sys

from PIL import Image, ImageDraw

C = {"frame": (52, 55, 60), "steel": (176, 182, 190), "mid": (122, 128, 136), "gun": (70, 74, 80),
     "navy": (34, 52, 92), "seam": (90, 220, 210), "violet": (150, 110, 230), "gold": (255, 215, 140),
     "vane": (196, 202, 210), "bore": (24, 26, 31)}


def bar(a, b, w):
    (x0, y0), (x1, y1) = a, b
    n = math.hypot(x1 - x0, y1 - y0)
    ox, oy = -(y1 - y0) / n * w / 2, (x1 - x0) / n * w / 2
    return [(x0 + ox, y0 + oy), (x1 + ox, y1 + oy), (x1 - ox, y1 - oy), (x0 - ox, y0 - oy)]


def ribbon(pts, w, seam="seam", sym=True):
    """Dark-blue sash along a polyline with seam lines on both edges (+ mirror)."""
    out = []
    mode = "m" if sym else "f"
    for a, b in zip(pts, pts[1:]):
        out.append(("navy", mode, bar(a, b, w)))
    for side in (-1, 1):
        for a, b in zip(pts, pts[1:]):
            n = math.hypot(b[0] - a[0], b[1] - a[1])
            ox, oy = -(b[1] - a[1]) / n * w / 2 * side, (b[0] - a[0]) / n * w / 2 * side
            out.append((seam, mode, bar((a[0] + ox, a[1] + oy), (b[0] + ox, b[1] + oy), 1.4)))
    return out


def cells(cx, cy, n=4, w=7, h=3, gap=2):
    return [("seam", "m", [(cx - w / 2, cy + k * (h + gap) + h), (cx, cy + k * (h + gap)), (cx + w / 2, cy + k * (h + gap) + h),
                           (cx + w / 2, cy + k * (h + gap) + h + 1.2), (cx, cy + k * (h + gap) + 1.2),
                           (cx - w / 2, cy + k * (h + gap) + h + 1.2)]) for k in range(n)]


def turret(x, y, L=34):
    """Sforzando: raised shoulder mount + long barrel (drawn pointing forward)."""
    return [("gun", "m", [(x - 7, y - 4), (x - 3, y - 8), (x + 3, y - 8), (x + 7, y - 4), (x + 7, y + 6), (x - 7, y + 6)]),
            ("steel", "m", [(x - 1.6, y - 8 - L), (x + 1.6, y - 8 - L), (x + 2.2, y - 6), (x - 2.2, y - 6)]),
            ("seam", "m", [(x - 0.4, y - 6 - L), (x + 0.4, y - 6 - L), (x + 0.4, y - 10), (x - 0.4, y - 10)])]


SPEAR = [(0, 0), (2.5, 12), (3.5, 40), (6.5, 44), (7.5, 70), (11, 74), (12, 96)]

# ---------------------------------------------------------------- A: rapier with a swept guard and blade wings
A = [
    ("frame", "h", SPEAR + [(18, 102), (22, 114), (40, 120), (48, 130), (44, 146), (28, 150), (26, 160), (30, 186),
                            (28, 238), (22, 262), (26, 300), (34, 318), (30, 326), (20, 322), (16, 356), (0, 356)]),
    ("frame", "m", [(28, 186), (60, 214), (90, 252), (96, 270), (82, 262), (54, 246), (30, 240)]),
    ("vane", "m", [(78, 236), (90, 252), (96, 270), (82, 262), (72, 256)]),
    ("steel", "h", [(0, 4), (2, 14), (3, 40), (0, 40)]),
    ("steel", "h", [(0, 100), (17, 104), (20, 116), (26, 120), (26, 150), (24, 162), (26, 186), (0, 190)]),
    ("mid", "m", [(30, 122), (40, 123), (46, 131), (42, 144), (30, 147)]),
    ("steel", "m", [(32, 194), (58, 218), (74, 238), (68, 248), (52, 242), (32, 236)]),
    ("mid", "h", [(0, 196), (26, 196), (24, 236), (18, 262), (22, 300), (0, 300)]),
    ("gun", "h", [(0, 304), (24, 304), (28, 316), (18, 318), (14, 350), (0, 350)]),
] + ribbon([(0, 48), (0, 150), (14, 176), (42, 214), (80, 254)], 9) + cells(54, 222, 3) + turret(38, 134)

# ---------------------------------------------------------------- B: bow, crescent wings drawn back from the shoulders
B = [
    ("frame", "h", SPEAR + [(18, 102), (24, 118), (36, 124), (40, 136), (30, 142), (26, 150), (28, 220), (22, 250),
                            (26, 290), (20, 300), (16, 340), (0, 340)]),
    ("frame", "m", [(26, 146), (54, 152), (82, 172), (102, 206), (110, 250), (98, 236), (78, 210), (52, 198),
                    (28, 202)]),
    ("vane", "m", [(100, 202), (110, 250), (98, 236), (94, 222)]),
    ("steel", "h", [(0, 4), (2, 14), (3, 40), (0, 40)]),
    ("steel", "h", [(0, 100), (17, 104), (22, 118), (24, 150), (24, 196), (0, 196)]),
    ("steel", "m", [(30, 152), (54, 157), (78, 175), (92, 198), (84, 204), (72, 196), (50, 190), (30, 192)]),
    ("mid", "h", [(0, 204), (26, 204), (24, 222), (20, 250), (24, 288), (0, 288)]),
    ("gun", "h", [(0, 292), (20, 294), (16, 336), (0, 336)]),
] + ribbon([(0, 48), (0, 140), (20, 162), (52, 172), (80, 188), (100, 226)], 9) + cells(62, 176, 3) + turret(32, 128)

# ---------------------------------------------------------------- C: swallowtail, wings sweep back past the stern
C_ = [
    ("frame", "h", SPEAR + [(18, 102), (22, 114), (36, 120), (42, 130), (36, 142), (24, 148), (26, 176), (24, 250),
                            (18, 280), (20, 306), (12, 330), (0, 330)]),
    ("frame", "m", [(25, 170), (50, 206), (72, 262), (86, 330), (90, 356), (76, 340), (60, 292), (40, 262),
                    (24, 254)]),
    ("vane", "m", [(80, 312), (86, 330), (90, 356), (76, 340), (72, 324)]),
    ("steel", "h", [(0, 4), (2, 14), (3, 40), (0, 40)]),
    ("steel", "h", [(0, 100), (17, 104), (21, 116), (24, 148), (24, 176), (0, 176)]),
    ("steel", "m", [(28, 182), (48, 210), (64, 252), (60, 268), (44, 254), (28, 248)]),
    ("mid", "h", [(0, 182), (24, 182), (22, 250), (16, 280), (0, 284)]),
    ("gun", "h", [(0, 288), (18, 288), (16, 306), (10, 326), (0, 326)]),
] + ribbon([(0, 48), (0, 148), (16, 176), (40, 214), (62, 266), (80, 324)], 9) + cells(46, 222, 3) + turret(34, 130)

OPTIONS = {
    "A  Rapier: swept guard at the shoulders, blade wings": A,
    "B  Bow: crescent wings drawn back from the shoulders": B,
    "C  Swallowtail: wings sweep back past the stern": C_,
}


def draw(d, masses, ox, oy, S, gold=False):
    for mat, mode, pts in masses:
        if gold and mat in ("seam", "violet"):
            mat = "gold"
        if mode == "m":
            polys = [pts, [(-x, y) for x, y in pts]]
        elif mode == "h":
            polys = [list(pts) + [(-x, y) for x, y in reversed(pts) if x > 0]]
        else:
            polys = [pts]
        for poly in polys:
            d.polygon([(ox + x * S, oy + y * S) for x, y in poly], fill=C[mat],
                      outline=None if mat in ("seam", "violet", "gold", "bore", "navy") else (20, 22, 26))


def main(out):
    S, pad, W, H = 2, 40, 240, 360
    sheet = Image.new("RGB", ((W * S + pad) * len(OPTIONS) + pad, H * S + 70 + H + 20), (14, 17, 22))
    d = ImageDraw.Draw(sheet)
    for i, (name, masses) in enumerate(OPTIONS.items()):
        ox = pad + i * (W * S + pad) + W * S // 2
        d.text((ox - W * S // 2, 8), name, fill=(200, 205, 210))
        draw(d, masses, ox, 40, S)
        draw(d, masses, ox - 70, 60 + H * S, 1)
        draw(d, masses, ox + 70, 60 + H * S, 1, gold=True)
        d.text((ox + 30, 50 + H * S), "Bravura", fill=(255, 215, 140))
    sheet.save(out)
    print(out)


main(sys.argv[1])
