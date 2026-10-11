"""Flat silhouette sketches for choosing the Cadence direction (not sprites).

python art_src/gen/cadence_options.py art_src/review/cadence_options.png
Each option is a list of (material, half-outline) masses, mirrored and stacked in order.
"""
import sys

from PIL import Image, ImageDraw

C = {"frame": (52, 55, 60), "steel": (176, 182, 190), "mid": (122, 128, 136), "gun": (70, 74, 80),
     "seam": (90, 220, 210), "yellow": (240, 196, 60)}

OPTIONS = {
    "A  Layered wedge": [
        ("frame", [(0, 0), (4, 14), (9, 32), (16, 40), (22, 58), (30, 66), (36, 92), (46, 104), (52, 140), (58, 150),
                   (60, 196), (54, 206), (46, 210), (44, 236), (36, 252), (22, 262), (12, 270), (0, 270)]),
        ("steel", [(0, 4), (7, 32), (14, 42), (19, 60), (0, 56)]),
        ("mid", [(0, 58), (20, 62), (28, 70), (33, 94), (0, 90)]),
        ("steel", [(0, 92), (34, 96), (44, 108), (49, 142), (40, 146), (0, 140)]),
        ("steel", [(0, 144), (42, 150), (56, 156), (57, 196), (44, 204), (0, 200)]),
        ("gun", [(0, 204), (42, 208), (41, 236), (32, 250), (0, 252)]),
        ("seam", [(44, 112), (46, 112), (54, 194), (52, 194)]),
        ("yellow", [(50, 154), (55, 158), (55, 162), (50, 158)]),
    ],
    "B  Trident (rails = long forward prongs)": [
        ("frame", [(0, 30), (8, 40), (14, 70), (22, 74), (24, 20), (30, 4), (36, 2), (40, 14), (42, 120), (48, 128),
                   (50, 200), (56, 214), (56, 246), (44, 262), (14, 266), (10, 272), (0, 272)]),
        ("steel", [(0, 34), (7, 44), (12, 72), (0, 70)]),
        ("steel", [(25, 22), (30, 8), (35, 6), (38, 16), (39, 118), (26, 118)]),
        ("mid", [(0, 76), (24, 78), (24, 120), (0, 118)]),
        ("steel", [(0, 122), (46, 132), (48, 204), (0, 200)]),
        ("gun", [(0, 204), (50, 210), (53, 244), (42, 258), (0, 262)]),
        ("seam", [(31, 20), (33, 20), (33, 116), (31, 116)]),
        ("yellow", [(30, 6), (35, 4), (36, 10), (31, 12)]),
    ],
    "C  Cross-shoulder (rails swept back like wings)": [
        ("frame", [(0, 0), (4, 14), (8, 40), (14, 60), (16, 92), (30, 98), (58, 118), (64, 134), (60, 142),
                   (40, 140), (30, 150), (30, 200), (42, 212), (46, 244), (36, 258), (14, 264), (10, 272), (0, 272)]),
        ("steel", [(0, 4), (6, 40), (12, 62), (13, 90), (0, 88)]),
        ("steel", [(14, 96), (30, 100), (56, 120), (61, 133), (42, 136), (28, 128), (16, 120)]),
        ("mid", [(0, 92), (14, 94), (16, 140), (0, 140)]),
        ("steel", [(0, 142), (28, 146), (28, 202), (0, 200)]),
        ("gun", [(0, 204), (40, 212), (43, 244), (34, 256), (0, 260)]),
        ("seam", [(20, 108), (22, 106), (54, 126), (52, 128)]),
        ("yellow", [(56, 122), (60, 126), (60, 132), (56, 130)]),
    ],
}


def main(out):
    S, pad, W, H = 2, 30, 140, 280
    sheet = Image.new("RGB", ((W * S + pad) * len(OPTIONS) + pad, H * S + 70), (14, 17, 22))
    d = ImageDraw.Draw(sheet)
    for i, (name, masses) in enumerate(OPTIONS.items()):
        ox = pad + i * (W * S + pad) + W * S // 2
        d.text((ox - W * S // 2, 8), name, fill=(200, 205, 210))
        for mat, half in masses:
            if min(x for x, _ in half) > 0:      # off-centre part: draw it and its mirror image separately
                polys = [half, [(-x, y) for x, y in half]]
            else:                                # touches the centre line: half outline, mirrored
                polys = [[(x, y) for x, y in half] + [(-x, y) for x, y in reversed(half) if x > 0]]
            for poly in polys:
                d.polygon([(ox + x * S, 40 + y * S) for x, y in poly], fill=C[mat], outline=(20, 22, 26))
    sheet.save(out)
    print(out)


main(sys.argv[1])
