"""Flat silhouette sketches for choosing the Tremolo direction (not sprites).

python art_src/gen/tremolo_options.py art_src/review/tremolo_options.png
Each option is a list of (material, mode, polygon) masses stacked in order:
mode "h" = half outline touching the centre line (mirrored); "m" = off-centre part drawn with its mirror image.
"""
import sys

from PIL import Image, ImageDraw

C = {"frame": (52, 55, 60), "steel": (176, 182, 190), "mid": (122, 128, 136), "gun": (70, 74, 80),
     "navy": (40, 58, 96), "seam": (90, 220, 210)}


def bar(a, b, w):
    """Thin quad from a to b, w px wide (a lattice spar)."""
    (x0, y0), (x1, y1) = a, b
    dx, dy = x1 - x0, y1 - y0
    n = (dx * dx + dy * dy) ** 0.5
    ox, oy = -dy / n * w / 2, dx / n * w / 2
    return [(x0 + ox, y0 + oy), (x1 + ox, y1 + oy), (x1 - ox, y1 - oy), (x0 - ox, y0 - oy)]


def spar(a, b, w=7):
    """Frame bar with a glowing seam down its middle."""
    return [("frame", "m", bar(a, b, w)), ("seam", "m", bar(a, b, 2))]


OPTIONS = {
    "A  Fork: twin bows, core bridge, X-truss aft": [
        # hull: stepped spear bow, shoulder notch, sponson, waist, flared engine block; inner edge differs from outer
        ("frame", "m", [(44, 0), (50, 18), (55, 22), (58, 50), (66, 58), (70, 96), (82, 104), (88, 150), (82, 158),
                        (88, 196), (84, 226), (93, 236), (90, 258), (58, 258), (56, 238), (50, 230), (50, 172),
                        (45, 160), (44, 112), (37, 100), (35, 42), (30, 30), (36, 24), (40, 16)]),
        ("steel", "m", [(44, 4), (49, 20), (54, 24), (56, 50), (40, 50), (38, 24)]),
        ("navy", "m", [(40, 54), (64, 60), (67, 96), (42, 98)]),
        ("steel", "m", [(46, 102), (68, 100), (80, 108), (85, 150), (48, 156)]),
        ("mid", "m", [(52, 162), (80, 160), (84, 196), (53, 200)]),
        ("gun", "m", [(54, 204), (82, 204), (88, 238), (86, 254), (60, 254)]),
        # centre bridge with the lattice core, joined into both hulls
        ("frame", "h", [(0, 84), (16, 88), (40, 100), (46, 108), (46, 130), (24, 138), (12, 152), (0, 156)]),
        ("steel", "h", [(0, 90), (14, 93), (36, 103), (42, 110), (42, 127), (20, 133), (0, 148)]),
        ("seam", "h", [(0, 104), (8, 112), (0, 120)]),
        ("seam", "m", [(10, 118), (44, 118), (44, 120), (10, 120)]),
    ] + spar((50, 176), (-50, 222)) + spar((50, 222), (-50, 176)) + spar((50, 199), (-50, 199), 5) + [
        ("seam", "m", [(52, 108), (54, 108), (54, 196), (52, 196)]),
    ],
    "B  Cradle: core pod slung between two long hulls": [
        # outer hull: long forward prong, stepped outer edge, tucked engines
        ("frame", "m", [(66, 0), (72, 20), (76, 22), (80, 60), (92, 72), (96, 130), (90, 138), (94, 196), (98, 210),
                        (96, 250), (84, 260), (60, 260), (56, 240), (58, 200), (54, 190), (54, 92), (58, 60),
                        (60, 24)]),
        ("steel", "m", [(66, 6), (71, 22), (75, 26), (77, 60), (60, 62), (62, 26)]),
        ("steel", "m", [(58, 66), (78, 64), (90, 76), (93, 130), (58, 132)]),
        ("navy", "m", [(58, 136), (88, 140), (91, 196), (58, 192)]),
        ("gun", "m", [(60, 200), (92, 204), (94, 248), (82, 256), (62, 256)]),
        # core pod: stepped spear nose, diamond core, small tail engine
        ("frame", "h", [(0, 40), (5, 56), (10, 60), (16, 84), (26, 96), (28, 150), (20, 166), (16, 196), (8, 204),
                        (0, 204)]),
        ("steel", "h", [(0, 44), (4, 58), (9, 62), (14, 86), (0, 86)]),
        ("mid", "h", [(0, 90), (24, 98), (25, 148), (0, 150)]),
        ("gun", "h", [(0, 154), (18, 162), (14, 194), (0, 200)]),
        ("seam", "h", [(0, 110), (10, 120), (0, 130)]),
    ] + spar((26, 104), (56, 132), 9) + spar((24, 160), (56, 146), 9) + spar((26, 128), (56, 112), 6) + [
        ("seam", "m", [(80, 70), (82, 70), (86, 190), (84, 190)]),
    ],
    "C  Wishbone: shared faceted head, hulls diverge, spar-bridged stern": [
        # head with canards; both hulls grow out of its shoulders
        ("frame", "h", [(0, 0), (5, 18), (10, 22), (14, 50), (26, 56), (34, 52), (38, 62), (30, 70), (32, 92),
                        (20, 100), (0, 104)]),
        ("steel", "h", [(0, 4), (4, 20), (9, 24), (12, 52), (0, 52)]),
        ("navy", "h", [(0, 56), (24, 60), (28, 90), (18, 96), (0, 98)]),
        ("seam", "h", [(0, 66), (6, 72), (0, 78)]),
        # hull arm: leaves the head swept outward, kinks to run aft, notch, engine block
        ("frame", "m", [(26, 74), (48, 84), (72, 108), (84, 112), (88, 150), (82, 158), (86, 200), (92, 214),
                        (90, 250), (80, 260), (56, 260), (54, 240), (56, 206), (52, 196), (52, 140), (40, 116),
                        (24, 100)]),
        ("steel", "m", [(30, 80), (48, 88), (70, 110), (82, 116), (85, 150), (55, 148), (54, 136), (40, 112),
                        (28, 98)]),
        ("mid", "m", [(56, 154), (80, 156), (83, 200), (57, 198)]),
        ("gun", "m", [(58, 206), (86, 210), (88, 248), (78, 256), (60, 256)]),
    ] + spar((54, 214), (-54, 214), 8) + spar((54, 170), (-54, 214)) + spar((54, 214), (-54, 170)) + [
        ("seam", "m", [(34, 92), (36, 90), (70, 116), (68, 118)]),
        ("seam", "m", [(68, 118), (70, 118), (72, 196), (70, 196)]),
    ],
}


def main(out):
    S, pad, W, H = 2, 30, 220, 262
    sheet = Image.new("RGB", ((W * S + pad) * len(OPTIONS) + pad, H * S + 70), (14, 17, 22))
    d = ImageDraw.Draw(sheet)
    for i, (name, masses) in enumerate(OPTIONS.items()):
        ox = pad + i * (W * S + pad) + W * S // 2
        d.text((ox - W * S // 2, 8), name, fill=(200, 205, 210))
        for mat, mode, pts in masses:
            if mode == "m":
                polys = [pts, [(-x, y) for x, y in pts]]
            else:
                polys = [list(pts) + [(-x, y) for x, y in reversed(pts) if x > 0]]
            for poly in polys:
                d.polygon([(ox + x * S, 40 + y * S) for x, y in poly], fill=C[mat],
                          outline=None if mat == "seam" else (20, 22, 26))
    sheet.save(out)
    print(out)


main(sys.argv[1])
