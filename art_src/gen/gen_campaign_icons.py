"""Campaign cargo icons (80x80, vanilla cargo-icon size), drawn at 4x and box-downscaled.

    python art_src/gen/gen_campaign_icons.py [review.png]

- graphics/rsl/icons/cargo/rsl_pitchglass.png: a cluster of faceted lattice-crystal shards (teal -> violet, glowing
  cores) held in a gunmetal tuning clamp.
- graphics/rsl/icons/cargo/rsl_bp_{hulls,weapons,wings}.png: vanilla's high-tech blueprint chip recoloured to steel +
  dark blue, with a teal lattice glyph on the screen (one glyph per package).
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GAME = os.path.abspath(os.path.join(ROOT, "..", ".."))
OUT = os.path.join(ROOT, "graphics", "rsl", "icons", "cargo")
S = 4
N = 80 * S

TEAL = np.array([90, 220, 210], float)
VIOLET = np.array([150, 110, 230], float)
NAVY = np.array([28, 44, 86], float)


def mask(poly):
    m = Image.new("L", (N, N), 0)
    ImageDraw.Draw(m).polygon([(x * S, y * S) for x, y in poly], fill=255)
    return np.asarray(m).astype(float) / 255.0


def ramp(a, b):
    """0..1 along the vector a->b (icon coordinates) for every pixel."""
    yy, xx = np.mgrid[0:N, 0:N].astype(float) / S
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    t = ((xx - ax) * dx + (yy - ay) * dy) / (dx * dx + dy * dy)
    return np.clip(t, 0, 1)[..., None]


def comp(rgb, a, col, m):
    """Paint col (HxWx3 or 3) over rgb/a with coverage m."""
    m = m[..., None]
    rgb[:] = rgb * (1 - m) + col * m
    a[:] = np.maximum(a, m[..., 0])


def shard(cx, base_y, top_y, w, lean, rgb, a, tint):
    """A hexagonal-prism shard seen from above-front: left face, right face, sharp tip."""
    tx = cx + lean
    tip = (tx, top_y)
    sl = (cx - w, base_y - w * 0.6)
    sr = (cx + w, base_y - w * 0.6)
    shl = (tx - w * 0.92, top_y + w * 2.2)
    shr = (tx + w * 0.92, top_y + w * 2.2)
    mid_b = (cx + w * 0.15, base_y)
    mid_t = (tx + w * 0.1, top_y + w * 2.6)
    left = [sl, shl, tip, mid_t, mid_b]
    right = [mid_b, mid_t, tip, shr, sr]
    hue = TEAL * (1 - tint) + VIOLET * tint
    t = ramp((cx, base_y), (tx, top_y))
    lcol = hue * (0.75 + 0.45 * t) + 70 * t
    rcol = hue * (0.42 + 0.4 * t)
    comp(rgb, a, np.clip(lcol, 0, 255), mask(left))
    comp(rgb, a, np.clip(rcol, 0, 255), mask(right))
    # glowing core line + bright edge highlight
    core = Image.new("L", (N, N), 0)
    d = ImageDraw.Draw(core)
    d.line([(mid_b[0] * S, mid_b[1] * S - 6), (mid_t[0] * S, mid_t[1] * S)], fill=255, width=int(w * 0.9))
    core = np.asarray(core.filter(ImageFilter.GaussianBlur(S * 1.6))).astype(float) / 255.0
    core *= np.maximum(mask(left), mask(right))
    comp(rgb, a, np.clip(hue * 0.5 + 150, 0, 255), np.clip(core * 1.3, 0, 1))
    edge = Image.new("L", (N, N), 0)
    ImageDraw.Draw(edge).line([(shl[0] * S, shl[1] * S), (tip[0] * S, tip[1] * S)], fill=255, width=S)
    comp(rgb, a, np.array([235, 255, 252.0]), np.asarray(edge).astype(float) / 255.0 * 0.8)
    # dark outline
    ol = Image.new("L", (N, N), 0)
    ImageDraw.Draw(ol).polygon([(x * S, y * S) for x, y in [sl, shl, tip, shr, sr, mid_b]], outline=255, width=S)
    comp(rgb, a, np.array([12, 18, 26.0]), np.asarray(ol).astype(float) / 255.0)


def pitchglass():
    rgb = np.zeros((N, N, 3))
    a = np.zeros((N, N))
    # glow halo behind the cluster
    halo = Image.new("L", (N, N), 0)
    ImageDraw.Draw(halo).ellipse([10 * S, 2 * S, 70 * S, 66 * S], fill=190)
    halo = np.asarray(halo.filter(ImageFilter.GaussianBlur(S * 8))).astype(float) / 255.0
    comp(rgb, a, TEAL, halo * 0.6)
    a[:] = halo * 0.6
    # back row, then front row (painter's order)
    shard(22, 58, 16, 7.0, -9, rgb, a, 0.6)
    shard(58, 58, 14, 7.0, 9, rgb, a, 0.5)
    shard(40, 60, 1, 10.0, 0, rgb, a, 0.12)
    shard(30, 63, 28, 5.5, -4, rgb, a, 0.85)
    shard(51, 63, 26, 5.5, 4, rgb, a, 0.3)
    # gunmetal tuning clamp in 3/4 view: lit top face, darker front face, chamfered ends, navy band, tell-tales
    top = [(12, 56), (20, 52), (60, 52), (68, 56), (60, 60), (20, 60)]
    front = [(12, 56), (20, 60), (60, 60), (68, 56), (68, 66), (60, 72), (20, 72), (12, 66)]
    t = ramp((40, 60), (40, 72))
    comp(rgb, a, np.array([118, 128, 142.0]) * (1 - t) + np.array([48, 54, 64.0]) * t, mask(front))
    t2 = ramp((12, 54), (68, 58))
    comp(rgb, a, np.array([206, 214, 224.0]) * (1 - t2 * 0.35), mask(top))
    comp(rgb, a, NAVY + 12, mask([(14, 63), (66, 63), (66, 66), (14, 66)]))
    for x in (24, 40, 56):
        dot = Image.new("L", (N, N), 0)
        ImageDraw.Draw(dot).ellipse([(x - 1.8) * S, 67.2 * S, (x + 1.8) * S, 70.4 * S], fill=255)
        dm = np.asarray(dot).astype(float) / 255.0
        comp(rgb, a, TEAL, np.asarray(dot.filter(ImageFilter.GaussianBlur(S * 1.5))).astype(float) / 255.0 * 0.8)
        comp(rgb, a, np.array([200, 255, 250.0]), dm)
    ol = Image.new("L", (N, N), 0)
    d = ImageDraw.Draw(ol)
    d.polygon([(x * S, y * S) for x, y in front], outline=255, width=S)
    d.line([(x * S, y * S) for x, y in [(12, 56), (20, 60), (60, 60), (68, 56)]], fill=255, width=S)
    comp(rgb, a, np.array([12, 16, 22.0]), np.asarray(ol).astype(float) / 255.0)
    return finish(rgb, a)


def finish(rgb, a):
    im = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.clip(a * 255, 0, 255)]).astype(np.uint8), "RGBA")
    # premultiplied box downscale
    arr = np.asarray(im).astype(float)
    pm = arr[..., :3] * arr[..., 3:4] / 255.0
    pm = pm.reshape(80, S, 80, S, 3).mean((1, 3))
    al = arr[..., 3].reshape(80, S, 80, S).mean((1, 3))
    col = np.where(al[..., None] > 0, pm * 255.0 / np.maximum(al[..., None], 1e-6), 0)
    return Image.fromarray(np.dstack([np.clip(col, 0, 255), al]).astype(np.uint8), "RGBA")


GLYPHS = {
    # simple lattice glyphs on the chip screen (icon coordinates)
    "hulls": [[(40, 26), (49, 40), (40, 54), (31, 40), (40, 26)], [(40, 31), (40, 49)]],
    "weapons": [[(30, 48), (50, 28)], [(36, 50), (52, 34)], [(44, 26), (52, 26), (52, 34)]],
    "wings": [[(28, 46), (34, 34), (40, 46)], [(40, 46), (46, 34), (52, 46)], [(34, 34), (46, 34)]],
}


def blueprint(kind):
    src = Image.open(os.path.join(GAME, "starsector-core", "graphics", "icons", "cargo",
                                  "blueprint_hightech.png")).convert("RGBA")
    arr = np.asarray(src).astype(float)
    rgb, al = arr[..., :3], arr[..., 3]
    lum = rgb.mean(-1, keepdims=True) / 255.0
    sat = (rgb.max(-1) - rgb.min(-1))[..., None] / 255.0
    steel = np.array([196, 204, 214.0]) * lum * 1.15
    navy = NAVY * 0.6 + NAVY * 1.6 * lum
    out = np.where(sat > 0.25, navy, steel)
    out = np.clip(out, 0, 255)
    im = Image.fromarray(np.dstack([out, al]).astype(np.uint8), "RGBA")
    big = im.resize((N, N), Image.LANCZOS)
    glow = Image.new("L", (N, N), 0)
    d = ImageDraw.Draw(glow)
    for line in GLYPHS[kind]:
        d.line([(x * S, y * S) for x, y in line], fill=255, width=int(2.2 * S), joint="curve")
    g = np.asarray(glow).astype(float) / 255.0
    soft = np.asarray(glow.filter(ImageFilter.GaussianBlur(S * 2))).astype(float) / 255.0
    barr = np.asarray(big).astype(float)
    rgb, a = barr[..., :3].copy(), barr[..., 3] / 255.0
    comp(rgb, a, TEAL, np.clip(soft * 0.7, 0, 1) * (a > 0.5))
    comp(rgb, a, np.array([200, 255, 250.0]), g * (a > 0.5))
    return finish(rgb, a)


def main():
    os.makedirs(OUT, exist_ok=True)
    icons = {"rsl_pitchglass": pitchglass()}
    for k in GLYPHS:
        icons["rsl_bp_" + k] = blueprint(k)
    for name, im in icons.items():
        im.save(os.path.join(OUT, name + ".png"))
        print("wrote", name)
    if len(sys.argv) > 1:
        refs = [Image.open(os.path.join(GAME, "starsector-core", "graphics", "icons", "cargo", f)).convert("RGBA")
                for f in ("ai_core_beta.png", "blueprint_hightech.png", "survey_data3.png")]
        tiles = list(icons.values()) + refs
        sheet = Image.new("RGBA", (len(tiles) * 90 * 3, 270), (36, 38, 44, 255))
        for i, t in enumerate(tiles):
            sheet.alpha_composite(t.resize((240, 240), Image.NEAREST), (i * 270 + 15, 15))
        small = Image.new("RGBA", (len(tiles) * 90, 90), (36, 38, 44, 255))
        for i, t in enumerate(tiles):
            small.alpha_composite(t, (i * 90 + 5, 5))
        full = Image.new("RGBA", (sheet.width, 360), (36, 38, 44, 255))
        full.alpha_composite(sheet, (0, 0))
        full.alpha_composite(small, (0, 270))
        full.save(sys.argv[1])
        print("sheet", sys.argv[1])


if __name__ == "__main__":
    main()
