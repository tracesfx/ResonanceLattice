"""Flat silhouette sketches for choosing the Conductor direction (not sprites).

python art_src/gen/conductor_options.py art_src/review/conductor_options.png
Masses as in halo_options.py: "h" = half outline on the centre line (mirrored), "m" = off-centre part + mirror,
"f" = full polygon. All three keep ONE solid blade body that splits only at the bow (unlike the Tremolo's twin hulls),
with the spinal Harmonic Driver lying in the slot between the prongs.
"""
import sys

from PIL import Image, ImageDraw

C = {"frame": (52, 55, 60), "steel": (176, 182, 190), "mid": (122, 128, 136), "gun": (70, 74, 80),
     "navy": (40, 58, 96), "seam": (90, 220, 210), "violet": (150, 110, 230), "bore": (24, 26, 31)}


def driver(y0, y1, w=6, cradle=(0, 0, 0)):
    """Spinal Harmonic Driver: gunmetal barrel with a dark bore and coil nodes, plus a breech cradle."""
    cy0, cy1, cw = cradle
    out = [("gun", "h", [(0, y0), (w * 0.6, y0 + 4), (w, y0 + 12), (w, y1), (0, y1)]),
           ("bore", "h", [(0, y0 + 3), (1.5, y0 + 6), (1.5, y1 - 4), (0, y1 - 4)])]
    for k in range(4):
        y = y0 + 24 + k * (y1 - y0 - 40) / 3
        out.append(("seam", "m", [(w - 1, y), (w + 2, y + 2), (w + 2, y + 6), (w - 1, y + 8)]))
    if cw:
        out.append(("gun", "h", [(0, cy0), (cw * 0.7, cy0 + 4), (cw, cy0 + 14), (cw, cy1 - 8), (cw * 0.6, cy1), (0, cy1)]))
        out.append(("seam", "h", [(0, cy0 + 20), (8, cy0 + 30), (0, cy0 + 40)]))
    return out


# ---------------------------------------------------------------- A: tuning fork, long parallel-ish prongs
A = [
    ("frame", "h", [(0, 168), (66, 176), (96, 196), (100, 206), (78, 212), (72, 222), (78, 268), (64, 296), (74, 336),
                    (84, 360), (66, 372), (52, 368), (42, 384), (38, 412), (0, 412)]),
    ("frame", "m", [(14, 190), (14, 44), (20, 34), (28, 12), (36, 0), (44, 26), (40, 36), (50, 70), (46, 96),
                    (56, 138), (62, 190)]),
    ("steel", "m", [(18, 46), (24, 36), (32, 14), (40, 30), (36, 40), (44, 70), (40, 96), (18, 96)]),
    ("navy", "m", [(18, 102), (42, 102), (50, 140), (54, 176), (18, 176)]),
    ("mid", "h", [(0, 182), (62, 184), (86, 200), (70, 206), (64, 220), (0, 220)]),
    ("navy", "h", [(0, 226), (66, 226), (70, 266), (58, 294), (0, 300)]),
    ("steel", "h", [(0, 304), (60, 304), (68, 334), (48, 358), (0, 360)]),
    ("gun", "h", [(0, 364), (40, 366), (34, 382), (32, 406), (0, 406)]),
    ("seam", "m", [(14, 50), (16, 48), (16, 186), (14, 186)]),
    ("seam", "m", [(16, 186), (16, 184), (48, 184), (64, 200), (62, 202), (47, 188), (16, 188)]),
] + driver(36, 200, cradle=(150, 250, 18))

# ---------------------------------------------------------------- B: lyre, prongs bow out and hook in at the tips
B = [
    ("frame", "h", [(0, 186), (60, 190), (98, 226), (100, 240), (76, 238), (70, 272), (88, 312), (84, 330), (60, 322),
                    (54, 360), (42, 370), (36, 402), (0, 402)]),
    ("frame", "m", [(16, 14), (22, 0), (42, 20), (54, 58), (48, 72), (62, 108), (58, 128), (72, 168), (66, 204),
                    (10, 204), (18, 150), (28, 100), (30, 62), (24, 34)]),
    ("steel", "m", [(24, 10), (40, 26), (50, 58), (44, 70), (34, 66), (28, 34)]),
    ("navy", "m", [(34, 76), (46, 78), (56, 108), (52, 130), (64, 168), (26, 168), (32, 110)]),
    ("steel", "h", [(0, 198), (56, 198), (84, 224), (66, 232), (62, 270), (0, 276)]),
    ("navy", "m", [(64, 240), (72, 240), (68, 276), (80, 306), (66, 314), (60, 286)]),
    ("mid", "h", [(0, 282), (58, 282), (54, 316), (50, 352), (0, 356)]),
    ("gun", "h", [(0, 360), (40, 362), (32, 380), (30, 396), (0, 396)]),
    ("seam", "m", [(28, 36), (30, 34), (34, 62), (30, 100), (22, 150), (16, 196), (14, 196), (20, 150), (28, 100),
                   (32, 62)]),
    ("violet", "m", [(16, 196), (60, 196), (92, 228), (90, 230), (58, 200), (16, 200)]),
] + driver(26, 212, cradle=(160, 270, 16))

# ---------------------------------------------------------------- C: split blade, short prongs + crossguard
C_ = [
    ("frame", "h", [(0, 128), (68, 136), (74, 168), (104, 178), (122, 160), (116, 206), (82, 222), (66, 262),
                    (80, 290), (62, 312), (58, 346), (78, 374), (74, 386), (50, 380), (42, 410), (0, 410)]),
    ("frame", "m", [(8, 150), (8, 46), (14, 30), (20, 0), (34, 24), (46, 38), (42, 52), (58, 84), (54, 100),
                    (66, 150)]),
    ("steel", "m", [(12, 48), (18, 32), (22, 12), (32, 28), (40, 42), (36, 52), (12, 60)]),
    ("navy", "m", [(12, 66), (38, 58), (52, 86), (48, 102), (60, 144), (12, 144)]),
    ("navy", "m", [(78, 176), (104, 184), (116, 170), (110, 200), (80, 212)]),
    ("steel", "h", [(0, 156), (64, 156), (70, 196), (0, 200)]),
    ("mid", "h", [(0, 206), (74, 214), (62, 262), (74, 288), (0, 296)]),
    ("navy", "h", [(0, 302), (58, 310), (54, 348), (44, 372), (0, 374)]),
    ("navy", "m", [(62, 352), (72, 372), (56, 374)]),
    ("gun", "h", [(0, 378), (42, 378), (38, 404), (0, 404)]),
    ("seam", "m", [(8, 52), (10, 50), (10, 146), (8, 146)]),
    ("seam", "m", [(10, 146), (10, 144), (70, 144), (110, 182), (108, 184), (69, 148), (10, 148)]),
] + driver(30, 150, cradle=(120, 240, 20))

OPTIONS = {
    "A  Fork: long prongs (~45% of length), broad shoulders, narrow stem": A,
    "B  Lyre: prongs bow out and hook in at the tips, lens-shaped slot": B,
    "C  Split blade: short twin spear prongs + forward-swept crossguard": C_,
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
                      outline=None if mat in ("seam", "violet", "bore") else (20, 22, 26))


def main(out):
    S, pad, W, H = 2, 40, 260, 420
    sheet = Image.new("RGB", ((W * S + pad) * len(OPTIONS) + pad, H * S + 70 + H + 20), (14, 17, 22))
    d = ImageDraw.Draw(sheet)
    for i, (name, masses) in enumerate(OPTIONS.items()):
        ox = pad + i * (W * S + pad) + W * S // 2
        d.text((ox - W * S // 2, 8), name, fill=(200, 205, 210))
        draw(d, masses, ox, 40, S)
        draw(d, masses, ox, 60 + H * S, 1)
    sheet.save(out)
    print(out)


main(sys.argv[1])
