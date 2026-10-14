#!/usr/bin/env python3
"""gen_mission_icons.py - mission-select illustrations (256x256 JPG, vanilla's icon size).

    python art_src/gen/gen_mission_icons.py [review.png]

User, 2026-10-13: "mission info needs to look better, not just plain text". Vanilla's mission icons are dramatic
close-ups (a hull filling the frame, beams crossing it, a nebula behind). These are composed the same way from our
own sprites: a crop of a vanilla nebula background, hulls scaled up past the frame with their seam glow bloomed,
rail-slug streaks, a dark vignette. Writes data/missions/<id>/icon.jpg (tools/gen_data.py keeps existing icons).
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CORE = os.path.abspath(os.path.join(ROOT, "..", "..", "starsector-core"))
sys.path.insert(0, os.path.join(ROOT, "art_src"))
N = 512   # worked at 2x, saved at 256


def bg(name, cx, cy, size, gain=1.0):
    im = Image.open(os.path.join(CORE, "graphics", "backgrounds", name)).convert("RGB")
    im = im.crop((cx - size // 2, cy - size // 2, cx + size // 2, cy + size // 2)).resize((N, N), Image.LANCZOS)
    a = np.asarray(im).astype(float) * gain
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


def lit(path, glow_path=None, tint=None, gain=1.0):
    """Sprite with its glow added, plus a separate bloom layer (both RGBA)."""
    s = Image.open(path).convert("RGBA")
    if not glow_path or not os.path.isfile(glow_path):
        return s, None
    g = np.asarray(Image.open(glow_path).convert("RGBA")).astype(float)
    if tint is not None:
        g[..., :3] = np.array(tint, float)
    a = np.asarray(s).astype(float)
    a[..., :3] = np.clip(a[..., :3] + g[..., :3] * (g[..., 3:4] / 255.0) * gain, 0, 255)
    bloom = g.copy()
    bloom[..., 3] = np.clip(bloom[..., 3] * gain, 0, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA"), Image.fromarray(bloom.astype(np.uint8), "RGBA")


def place(canvas, layers, scale, angle, x, y, bloom_r=10):
    """Paste a lit sprite (and its bloom, additively) scaled, rotated (degrees, CCW) and centred at (x, y)."""
    spr, bloom = layers
    w, h = spr.size
    spr = spr.resize((int(w * scale), int(h * scale)), Image.LANCZOS).rotate(angle, expand=True,
                                                                              resample=Image.BICUBIC)
    canvas.alpha_composite(spr, (int(x - spr.width / 2), int(y - spr.height / 2)))
    if bloom is not None:
        b = bloom.resize((int(w * scale), int(h * scale)), Image.LANCZOS).rotate(angle, expand=True,
                                                                                resample=Image.BICUBIC)
        layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        layer.alpha_composite(b, (int(x - b.width / 2), int(y - b.height / 2)))
        add(canvas, layer.filter(ImageFilter.GaussianBlur(bloom_r)), 1.1)
        add(canvas, layer.filter(ImageFilter.GaussianBlur(bloom_r * 3)), 0.6)


def add(canvas, layer, k):
    c = np.asarray(canvas).astype(float)
    l = np.asarray(layer).astype(float)
    c[..., :3] = np.clip(c[..., :3] + l[..., :3] * (l[..., 3:4] / 255.0) * k, 0, 255)
    canvas.paste(Image.fromarray(c.astype(np.uint8), "RGBA"))


def streak(canvas, p0, p1, color, width=6):
    """A rail slug's wake: hot white core, coloured haze."""
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.line([p0, p1], fill=tuple(color) + (255,), width=width * 3)
    add(canvas, layer.filter(ImageFilter.GaussianBlur(width * 2)), 1.0)
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).line([p0, p1], fill=(255, 255, 255, 255), width=max(2, width // 2))
    add(canvas, layer.filter(ImageFilter.GaussianBlur(1)), 1.0)


def vignette(canvas, k=0.8):
    yy, xx = np.mgrid[0:N, 0:N] / (N - 1) - 0.5
    v = 1 - k * np.clip((xx ** 2 + yy ** 2) * 2.2, 0, 1) ** 1.6
    c = np.asarray(canvas).astype(float)
    c[..., :3] *= v[..., None]
    return Image.fromarray(c.astype(np.uint8), "RGBA")


def ship(sid, tint=None, gain=1.0):
    p = os.path.join(ROOT, "graphics", "rsl", "ships", sid)
    return lit(p + ".png", p + "_glow.png", tint, gain)


def vanilla(path):
    return Image.open(os.path.join(CORE, "graphics", "ships", path)).convert("RGBA"), None


def proving():
    c = bg("background3.jpg", 1216, 1088, 900, 1.1)
    place(c, vanilla("onslaught/onslaught_base.png"), 1.0, 200, 430, 70)
    place(c, ship("rsl_conductor"), 0.75, 30, 110, 330, 8)
    place(c, ship("rsl_halo"), 0.62, 25, 470, 430, 8)
    for y0 in (150, 205):
        streak(c, (120, 512 - y0 + 40), (420, 70 + y0 * 0.2), (110, 232, 218), 5)
    place(c, ship("rsl_virtuoso", tint=(246, 251, 255), gain=1.4), 1.25, 22, 270, 300, 12)   # in Bravura
    return vignette(c)


def siege():
    c = bg("background2.jpg", 1536, 832, 900, 1.2)
    try:
        import station_preview
        st = station_preview.composite("rsl_cantor", glow=True)
        place(c, (st, None), 0.95, 0, 300, 230)
    except Exception as e:   # the composite needs the module specs; fall back to the core alone
        print("station composite failed (%s); core only" % e)
        place(c, ship("rsl_cantor"), 1.0, 0, 300, 230, 10)
    place(c, vanilla("onslaught/onslaught_base.png"), 0.8, 160, 110, 450)
    for k, (tx, ty) in enumerate(((110, 450), (230, 480), (60, 330))):   # the Grand Chorus: petals firing at once
        a = math.radians(100 + k * 30)
        streak(c, (300 + 170 * math.cos(a), 230 + 170 * math.sin(a)), (tx, ty), (110, 232, 218), 5)
    place(c, vanilla("eagle/eagle_base.png"), 0.9, 150, 230, 480)
    place(c, ship("rsl_virtuoso_unsung"), 0.7, 205, 440, 440, 6)
    return vignette(c)


def duel():
    c = bg("background6.jpg", 900, 900, 1000, 1.0)
    # the Dies Irae (Hush-violet seams) diving in from the top right, the Lacrimosa (Bravura white) from below
    place(c, ship("rsl_virtuoso", tint=(190, 110, 255), gain=1.3), 0.95, 225, 380, 130, 10)
    streak(c, (330, 210), (60, 470), (190, 110, 255), 5)
    streak(c, (170, 400), (470, 40), (240, 246, 255), 6)
    place(c, ship("rsl_virtuoso", tint=(246, 251, 255), gain=1.4), 1.15, 40, 150, 380, 12)
    return vignette(c, 0.85)


ICONS = {"rsl_proving": proving, "rsl_siege": siege, "rsl_duel": duel}


def main():
    out = {}
    for mid, fn in ICONS.items():
        im = fn().convert("RGB").resize((256, 256), Image.LANCZOS)
        d = os.path.join(ROOT, "data", "missions", mid)
        os.makedirs(d, exist_ok=True)
        im.save(os.path.join(d, "icon.jpg"), quality=92)
        out[mid] = im
        print("wrote", mid)
    if len(sys.argv) > 1:
        sheet = Image.new("RGB", (256 * len(out), 256))
        for k, im in enumerate(out.values()):
            sheet.paste(im, (256 * k, 0))
        sheet.save(sys.argv[1])


if __name__ == "__main__":
    main()
