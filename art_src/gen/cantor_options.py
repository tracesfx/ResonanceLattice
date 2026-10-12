"""Flat layout sketches for choosing the Cantor Array station direction (not sprites).

python art_src/gen/cantor_options.py art_src/review/cantor_options.png
Station = core hull + petal MODULES (separate hulls on STATION_MODULE slots) + a slowly rotating outer ring (deco).
Petals: Bell (flak / PD, flared mouth), Choir Loft (hangar, broad deck with bays), Spire (lance battery, long spike).
Drawn with the bow (station "forward") up. Each petal is drawn along its own axis (local coords: x across, y outward).
"""
import math
import sys

from PIL import Image, ImageDraw

C = {"frame": (52, 55, 60), "steel": (176, 182, 190), "mid": (122, 128, 136), "gun": (70, 74, 80),
     "navy": (34, 52, 92), "seam": (90, 220, 210), "ring": (150, 158, 170), "rframe": (60, 64, 72),
     "core": (110, 230, 225), "bay": (28, 32, 40)}


def rot(pts, a, c=(0, 0)):
    ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
    return [(c[0] + x * ca - y * sa, c[1] + x * sa + y * ca) for x, y in pts]


def mirror_half(h):
    return list(h) + [(-x, y) for x, y in reversed(h) if x > 0]


# petal outlines in local coords: root at y=0 (on the core), pointing outward along -y; half outlines (x >= 0)
BELL = [(0, 0), (18, 0), (22, -18), (16, -40), (20, -60), (34, -78), (44, -96), (36, -100), (22, -92), (8, -96),
        (0, -104)]
LOFT = [(0, 0), (26, 0), (34, -14), (52, -22), (58, -40), (48, -48), (54, -70), (40, -92), (14, -96), (0, -90)]
SPIRE = [(0, 0), (16, 0), (20, -20), (14, -40), (16, -70), (10, -76), (11, -110), (6, -116), (6, -150), (0, -176)]
PETALS = {"bell": BELL, "loft": LOFT, "spire": SPIRE}


def petal(kind, ang, dist, scale=1.0):
    h = [(x * scale, y * scale - dist) for x, y in PETALS[kind]]
    full = mirror_half(h)
    out = [("frame", rot(full, ang))]
    inner = [(x * 0.62, (y + dist) * 0.82 - dist) for x, y in full]
    out.append(("steel", rot(inner, ang)))
    if kind == "loft":
        for k in (-1, 1):
            bay = [(k * 14, -dist - 40), (k * 34, -dist - 40), (k * 34, -dist - 52), (k * 14, -dist - 52)]
            out.append(("bay", rot(bay, ang)))
    if kind == "spire":
        out.append(("seam", rot([(-1.2, -dist - 20), (1.2, -dist - 20), (1.2, -dist - 160), (-1.2, -dist - 160)], ang)))
    if kind == "bell":
        out.append(("navy", rot([(-26, -dist - 82), (26, -dist - 82), (30, -dist - 90), (-30, -dist - 90)], ang)))
    out.append(("seam", rot([(-1.2, -dist + 6), (1.2, -dist + 6), (1.2, -dist - 30), (-1.2, -dist - 30)], ang)))
    return out


def ring(r0, r1, nseg=9, gap=5, c=(0, 0)):
    out = []
    step = 360 / nseg
    for k in range(nseg):
        a0, a1 = k * step + gap / 2, (k + 1) * step - gap / 2
        o = [(c[0] + r1 * math.cos(math.radians(a0 + (a1 - a0) * i / 12)), c[1] + r1 * math.sin(math.radians(a0 + (a1 - a0) * i / 12))) for i in range(13)]
        n = [(c[0] + r0 * math.cos(math.radians(a1 - (a1 - a0) * i / 12)), c[1] + r0 * math.sin(math.radians(a1 - (a1 - a0) * i / 12))) for i in range(13)]
        out.append(("rframe", o + n))
        rm = (r0 + r1) / 2
        s_ = [(c[0] + (rm + 1.2) * math.cos(math.radians(a0 + 2 + (a1 - a0 - 4) * i / 12)), c[1] + (rm + 1.2) * math.sin(math.radians(a0 + 2 + (a1 - a0 - 4) * i / 12))) for i in range(13)]
        s2 = [(c[0] + (rm - 1.2) * math.cos(math.radians(a1 - 2 - (a1 - a0 - 4) * i / 12)), c[1] + (rm - 1.2) * math.sin(math.radians(a1 - 2 - (a1 - a0 - 4) * i / 12))) for i in range(13)]
        out.append(("seam", s_ + s2))
    return out


def core(kind):
    """Core hull outlines (full polygons, centred)."""
    if kind == "tri":       # three-lobed core with notches between the petal roots
        pts = []
        for k in range(3):
            a = -90 + k * 120
            for (rr, da) in ((70, -20), (96, -10), (100, 0), (96, 10), (70, 20), (52, 60)):
                pts.append((rr * math.cos(math.radians(a + da)), rr * math.sin(math.radians(a + da))))
        return pts
    if kind == "star":      # six-pointed lattice star (stepped)
        pts = []
        for k in range(6):
            a = -90 + k * 60
            for (rr, da) in ((88, 0), (60, 18), (54, 30), (60, 42)):
                pts.append((rr * math.cos(math.radians(a + da)), rr * math.sin(math.radians(a + da))))
        return pts
    pts = []                # "rose": wide disc-like core with stepped teeth
    for k in range(12):
        a = -90 + k * 30
        for (rr, da) in ((92, 0), (84, 8), (86, 15), (80, 22)):
            pts.append((rr * math.cos(math.radians(a + da)), rr * math.sin(math.radians(a + da))))
    return pts


def option(core_kind, petals, ring_r):
    out = [("frame", core(core_kind))]
    out.append(("steel", [(x * 0.7, y * 0.7) for x, y in core(core_kind)]))
    out.append(("navy", [(x * 0.42, y * 0.42) for x, y in core(core_kind)]))
    out.append(("core", [(0, -16), (12, 0), (0, 16), (-12, 0)]))
    for kind, ang, dist, sc in petals:
        out += petal(kind, ang, dist, sc)
    rg = ring(ring_r[0], ring_r[1])
    return rg + out if ring_r[2] == "under" else out + rg


OPTIONS = {
    "A  Triskelion: 3 different petals at 120 deg (Spire forward), ring around everything":
        ("tri", [("spire", 0, 92, 1.0), ("bell", 120, 92, 1.0), ("loft", 240, 92, 1.0)], (232, 246, "under")),
    "B  Hexad: 6 petals, mirror-symmetric (Spire fore+aft, 2 Bells, 2 Lofts), ring through the petals":
        ("star", [("spire", 0, 84, 0.9), ("spire", 180, 84, 0.9), ("bell", 60, 84, 0.8), ("bell", -60, 84, 0.8),
                  ("loft", 120, 84, 0.8), ("loft", -120, 84, 0.8)], (150, 162, "over")),
    "C  Rose window: wide core inside the ring, 3 petals mounted ON the ring (it runs through their roots)":
        ("rose", [("spire", 0, 150, 0.9), ("bell", 120, 150, 0.9), ("loft", 240, 150, 0.9)], (124, 138, "under")),
}


def draw(d, masses, ox, oy, S):
    for mat, pts in masses:
        d.polygon([(ox + x * S, oy + y * S) for x, y in pts], fill=C[mat],
                  outline=None if mat in ("seam", "core", "bay", "navy") else (20, 22, 26))


def main(out):
    S, pad, W = 1.0, 30, 560
    sheet = Image.new("RGB", (int((W * S + pad) * len(OPTIONS) + pad), int(W * S + 60 + W * 0.5 + 30)), (14, 17, 22))
    d = ImageDraw.Draw(sheet)
    for i, (name, (ck, pets, rr)) in enumerate(OPTIONS.items()):
        ox = pad + i * (W * S + pad) + W * S / 2
        d.text((ox - W * S / 2, 8), name, fill=(200, 205, 210))
        m = option(ck, pets, rr)
        draw(d, m, ox, 40 + W * S / 2, S)
        draw(d, m, ox, 60 + W * S + W * 0.25, 0.5)      # half scale: roughly how it reads zoomed out in combat
    sheet.save(out)
    print(out)


main(sys.argv[1])
