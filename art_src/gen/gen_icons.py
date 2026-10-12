#!/usr/bin/env python3
"""gen_icons.py - ship-system icons (64x64), hullmod icons (32x32) and the faction crest/flag, in the hull palette:
an angular steel frame, a navy field and a teal glyph that names the mechanic (fork, wave, ring, string, ...).

    python art_src/gen/gen_icons.py
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SS = 4
STEEL, STEEL_D, NAVY, NAVY_D = (196, 204, 212), (110, 118, 130), (44, 62, 104), (24, 32, 56)
TEAL, VIOLET, GOLD, INK = (100, 232, 222), (164, 124, 244), (255, 214, 140), (14, 16, 20)

SYSTEMS = {  # id: glyph
    "rsl_pitchshift": "split", "rsl_gracedash": "dash", "rsl_ward": "tether", "rsl_crescendo": "crescendo",
    "rsl_standingwave": "wave", "rsl_stillwater": "ring", "rsl_symstrike": "fork", "rsl_glissando": "string",
    "rsl_glissando_unsung": "string", "rsl_grandchorus": "chorus",
}
HULLMODS = {
    "rsl_lattice_core": "diamond", "rsl_conductors_bridge": "fork", "rsl_fracture": "fracture",
    "rsl_stolen_time": "hourglass", "rsl_bravura": "star", "rsl_unbound": "unbound", "rsl_phase_locked": "chorus",
    "rsl_tuned_wings": "ring", "rsl_concert_pitch": "wave",
}
LOCKED = {"rsl_bravura_locked": "star"}   # inactive versions: dim grey glyph, struck through


def frame(d, n, field=NAVY):
    c = n / 2
    r = n * 0.46
    ch = n * 0.14
    pts = [(c - r + ch, c - r), (c + r - ch, c - r), (c + r, c - r + ch), (c + r, c + r - ch), (c + r - ch, c + r),
           (c - r + ch, c + r), (c - r, c + r - ch), (c - r, c - r + ch)]
    d.polygon(pts, fill=INK)
    k = n * 0.035
    inner = [((x - c) * (1 - k / r * 1.6) + c, (y - c) * (1 - k / r * 1.6) + c) for x, y in pts]
    d.polygon(inner, fill=STEEL_D)
    inner2 = [((x - c) * 0.84 + c, (y - c) * 0.84 + c) for x, y in pts]
    d.polygon(inner2, fill=field)


def glyph(d, n, g, col=TEAL):
    c, u = n / 2, n / 64.0
    w = max(1, int(3.2 * u))
    L = lambda pts, ww=w: d.line(pts, fill=col, width=ww, joint="curve")  # noqa: E731

    def diamond(x, y, rx, ry, fill=col):
        d.polygon([(x, y - ry), (x + rx, y), (x, y + ry), (x - rx, y)], fill=fill)
    if g == "diamond":
        diamond(c, c, 10 * u, 17 * u)
        L([(c - 18 * u, c), (c - 11 * u, c)]); L([(c + 11 * u, c), (c + 18 * u, c)])
    elif g == "fork":
        L([(c - 8 * u, c - 17 * u), (c - 8 * u, c + 4 * u), (c, c + 10 * u), (c + 8 * u, c + 4 * u), (c + 8 * u, c - 17 * u)])
        L([(c, c + 10 * u), (c, c + 19 * u)])
        diamond(c, c - 6 * u, 3.5 * u, 6 * u)
    elif g == "split":
        L([(c - 14 * u, c + 16 * u), (c, c - 2 * u), (c, c - 18 * u)])
        L([(c + 14 * u, c + 16 * u), (c, c - 2 * u)], ww=w)
        diamond(c - 14 * u, c + 16 * u, 4 * u, 4 * u, TEAL)
        diamond(c + 14 * u, c + 16 * u, 4 * u, 4 * u, VIOLET)
    elif g == "dash":
        for i, a in enumerate((0.35, 0.6, 1.0)):
            x0 = c - 18 * u + i * 6 * u
            d.polygon([(x0, c - 10 * u), (x0 + 16 * u, c), (x0, c + 10 * u), (x0 + 5 * u, c)],
                      fill=tuple(int(v * a) for v in col))
    elif g == "tether":
        d.ellipse([c - 18 * u, c - 6 * u, c - 6 * u, c + 6 * u], outline=col, width=w)
        diamond(c + 12 * u, c, 6 * u, 9 * u)
        for i in range(4):
            x = c - 5 * u + i * 4 * u
            L([(x, c - 2 * u), (x + 2 * u, c + 2 * u)], ww=max(1, w - 1))
    elif g == "crescendo":
        L([(c + 18 * u, c - 12 * u), (c - 18 * u, c), (c + 18 * u, c + 12 * u)])
        for i in range(3):
            diamond(c - 6 * u + i * 9 * u, c, 2 * u + i * 1.2 * u, 2 * u + i * 1.2 * u)
    elif g == "wave":
        pts = [(c - 20 * u + i * u, c + 10 * u * math.sin(i / 40.0 * 4 * math.pi)) for i in range(41)]
        L(pts)
        diamond(c - 20 * u, c, 4 * u, 6 * u, VIOLET)
    elif g == "ring":
        d.ellipse([c - 17 * u, c - 17 * u, c + 17 * u, c + 17 * u], outline=col, width=w)
        d.ellipse([c - 9 * u, c - 9 * u, c + 9 * u, c + 9 * u], outline=tuple(v // 2 for v in col), width=max(1, w - 1))
        diamond(c, c, 3 * u, 5 * u)
    elif g == "string":
        L([(c - 18 * u, c + 14 * u), (c + 18 * u, c - 14 * u)], ww=max(1, int(2 * u)))
        diamond(c - 18 * u, c + 14 * u, 4 * u, 4 * u, VIOLET)
        diamond(c + 18 * u, c - 14 * u, 5 * u, 7 * u)
    elif g == "chorus":
        for a in range(6):
            t = a * math.pi / 3
            diamond(c + 13 * u * math.cos(t), c + 13 * u * math.sin(t), 3.5 * u, 3.5 * u)
        diamond(c, c, 5 * u, 8 * u)
    elif g == "fracture":
        L([(c - 2 * u, c - 18 * u), (c + 5 * u, c - 4 * u), (c - 5 * u, c + 4 * u), (c + 2 * u, c + 18 * u)])
        for i in range(5):
            diamond(c - 16 * u + i * 8 * u, c + 20 * u, 2 * u, 2 * u, VIOLET if i == 4 else col)
    elif g == "hourglass":
        d.polygon([(c - 12 * u, c - 16 * u), (c + 12 * u, c - 16 * u), (c, c), (c + 12 * u, c + 16 * u),
                   (c - 12 * u, c + 16 * u), (c, c)], outline=col, width=w)
        diamond(c, c + 10 * u, 5 * u, 4 * u, VIOLET)
    elif g == "star":
        for a in range(8):
            t = a * math.pi / 4
            r = 18 * u if a % 2 == 0 else 10 * u
            L([(c, c), (c + r * math.cos(t), c + r * math.sin(t))], ww=max(1, w - 1))
        diamond(c, c, 5 * u, 5 * u, GOLD)
    elif g == "unbound":
        diamond(c, c, 9 * u, 15 * u)
        L([(c - 18 * u, c - 18 * u), (c - 10 * u, c - 10 * u)]); L([(c + 18 * u, c + 18 * u), (c + 10 * u, c + 10 * u)])
        L([(c + 18 * u, c - 18 * u), (c + 10 * u, c - 10 * u)]); L([(c - 18 * u, c + 18 * u), (c - 10 * u, c + 10 * u)])


def icon(n, g, col=TEAL):
    N = n * SS
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    frame(d, N)
    lay = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    glyph(ImageDraw.Draw(lay), N, g, col)
    halo = lay.filter(ImageFilter.GaussianBlur(N * 0.03))
    im.alpha_composite(halo)
    im.alpha_composite(lay)
    return im.resize((n, n), Image.LANCZOS)


def save(im, rel):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    im.save(p)


def main():
    for sid, g in SYSTEMS.items():
        save(icon(64, g, VIOLET if sid == "rsl_glissando_unsung" else TEAL), "graphics/rsl/icons/hullsys/%s.png" % sid)
    for hid, g in HULLMODS.items():
        save(icon(32, g, (235, 255, 252) if hid == "rsl_concert_pitch" else TEAL),
             "graphics/rsl/icons/hullmods/%s.png" % hid)
    for hid, g in LOCKED.items():
        im = icon(32 * SS, g, (120, 126, 134)).convert("RGBA")
        d = ImageDraw.Draw(im)
        n = 32 * SS
        d.line([(n * 0.18, n * 0.82), (n * 0.82, n * 0.18)], fill=(200, 60, 60, 255), width=int(n * 0.09))
        save(im.resize((32, 32), Image.LANCZOS), "graphics/rsl/icons/hullmods/%s.png" % hid)
    # faction crest (256) and flag (410x256)
    crest = icon(256, "chorus")
    save(crest, "graphics/rsl/factions/rsl_crest.png")
    N = 410 * SS, 256 * SS
    flag = Image.new("RGBA", N, NAVY_D + (255,))
    d = ImageDraw.Draw(flag)
    d.polygon([(0, 0), (N[0] * 0.42, 0), (N[0] * 0.30, N[1]), (0, N[1])], fill=NAVY)
    d.line([(N[0] * 0.42, 0), (N[0] * 0.30, N[1])], fill=TEAL, width=SS * 6)
    d.line([(N[0] * 0.47, 0), (N[0] * 0.35, N[1])], fill=STEEL, width=SS * 3)
    big = icon(200, "chorus").resize((200 * SS, 200 * SS), Image.LANCZOS)
    flag.alpha_composite(big, (int(N[0] * 0.56), int(N[1] / 2 - 100 * SS)))
    save(flag.resize((410, 256), Image.LANCZOS), "graphics/rsl/factions/rsl_flag.png")
    print("icons written")


if __name__ == "__main__":
    main()
