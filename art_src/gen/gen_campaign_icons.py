"""Campaign cargo icons (80x80, vanilla cargo-icon size), drawn at 4x and box-downscaled.

    python art_src/gen/gen_campaign_icons.py [review.png]

- graphics/rsl/icons/cargo/rsl_pitchglass.png: a cluster of faceted lattice-crystal shards (teal -> violet, glowing
  cores) held in a gunmetal tuning clamp.
- graphics/rsl/icons/cargo/rsl_lacrimosa_sash.png: the Lacrimosa's sash and vanes (quest item).
- graphics/rsl/icons/intel/rsl_lacrimosa.png: the questline's intel icon (the Virtuoso, glow on).
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


def starfield(w, h, seed):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    bg = np.zeros((h, w, 3))
    bg[:] = np.array([6, 9, 18.0])
    bg += (NAVY * 0.5) * np.clip(1 - np.hypot(xx / w - 0.7, yy / h - 0.3) * 1.4, 0, 1)[..., None]
    for _ in range(int(w * h / 260)):
        x, y = rng.integers(0, w), rng.integers(0, h)
        bg[y, x] = np.clip(bg[y, x] + rng.uniform(60, 200), 0, 255)
    return bg


def nurseries():
    """Market condition icon (40x40, full bleed like vanilla's): glowing shards in a dark vault."""
    rgb = starfield(N, N, 3) * 0.6
    a = np.ones((N, N))
    halo = Image.new("L", (N, N), 0)
    ImageDraw.Draw(halo).ellipse([6 * S, 4 * S, 74 * S, 76 * S], fill=200)
    comp(rgb, a, TEAL, np.asarray(halo.filter(ImageFilter.GaussianBlur(S * 9))).astype(float) / 255.0 * 0.55)
    shard(18, 84, 22, 8.0, -8, rgb, a, 0.6)
    shard(62, 84, 18, 8.0, 8, rgb, a, 0.5)
    shard(40, 86, 2, 11.0, 0, rgb, a, 0.12)
    shard(29, 88, 40, 6.0, -4, rgb, a, 0.85)
    shard(52, 88, 36, 6.0, 4, rgb, a, 0.3)
    im = finish(rgb, a)
    return im.resize((40, 40), Image.LANCZOS)


def cantor_industry():
    """Industry image (190x95, vanilla station images are close crops): the glow-on Cantor Array on a starfield."""
    sys.path.insert(0, os.path.join(ROOT, "art_src"))
    import station_preview
    st = station_preview.composite("rsl_cantor", glow=True, ring_angle=20.0)
    bb = st.getbbox()
    st = st.crop(bb)
    scale = 300.0 / st.width
    st = st.resize((int(st.width * scale), int(st.height * scale)), Image.LANCZOS).rotate(-18, Image.BICUBIC,
                                                                                         expand=True)
    w, h = 190, 95
    bg = Image.fromarray(np.clip(starfield(w, h, 7), 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    bg.alpha_composite(st, (w // 2 - st.width // 2 + 40, h // 2 - st.height // 2 + 10))
    return bg


def metronome():
    """Pulsar Metronome colony item: a chamfered steel clock housing, navy face, tick ring, a glowing crystal hand."""
    rgb = np.zeros((N, N, 3))
    a = np.zeros((N, N))
    halo = Image.new("L", (N, N), 0)
    ImageDraw.Draw(halo).ellipse([8 * S, 8 * S, 72 * S, 72 * S], fill=160)
    comp(rgb, a, TEAL, np.asarray(halo.filter(ImageFilter.GaussianBlur(S * 6))).astype(float) / 255.0 * 0.45)
    a[:] = np.asarray(halo.filter(ImageFilter.GaussianBlur(S * 6))).astype(float) / 255.0 * 0.45
    c = 40.0

    def octo(r, k=0.38):
        return [(c + r * x, c + r * y) for x, y in [(-k, -1), (k, -1), (1, -k), (1, k), (k, 1), (-k, 1), (-1, k),
                                                     (-1, -k)]]
    outer, face = octo(33), octo(26)
    t = ramp((14, 10), (66, 70))
    comp(rgb, a, np.array([214, 222, 232.0]) * (1 - t * 0.55) + np.array([70, 78, 90.0]) * t * 0.55, mask(outer))
    tf = ramp((40, 14), (40, 66))
    comp(rgb, a, (NAVY + 8) * (1 - tf * 0.4) + np.array([10, 16, 30.0]) * tf * 0.4, mask(face))
    ticks = Image.new("L", (N, N), 0)
    d = ImageDraw.Draw(ticks)
    for i in range(16):
        ang = i * math.pi / 8
        r0, r1 = (17, 23) if i % 4 == 0 else (19.5, 23)
        d.line([((c + r0 * math.sin(ang)) * S, (c - r0 * math.cos(ang)) * S),
                ((c + r1 * math.sin(ang)) * S, (c - r1 * math.cos(ang)) * S)], fill=255, width=int(1.4 * S))
    tm = np.asarray(ticks).astype(float) / 255.0
    comp(rgb, a, TEAL, np.asarray(ticks.filter(ImageFilter.GaussianBlur(S * 1.2))).astype(float) / 255.0 * 0.7)
    comp(rgb, a, np.array([200, 255, 250.0]), tm)
    # the hand: a slim crystal shard swept to "two o'clock", pivoting on a gunmetal hub
    ang = math.radians(35)
    tip = (c + 21 * math.sin(ang), c - 21 * math.cos(ang))
    side = (math.cos(ang) * 3.2, math.sin(ang) * 3.2)
    hand = [(c - side[0], c - side[1]), tip, (c + side[0], c + side[1]),
            (c - 6 * math.sin(ang), c + 6 * math.cos(ang))]
    comp(rgb, a, np.clip(TEAL * 0.6 + 120, 0, 255), mask(hand))
    glow = Image.new("L", (N, N), 0)
    ImageDraw.Draw(glow).polygon([(x * S, y * S) for x, y in hand], fill=255)
    comp(rgb, a, TEAL, np.asarray(glow.filter(ImageFilter.GaussianBlur(S * 2.5))).astype(float) / 255.0 * 0.6)
    hub = octo(4.5)
    comp(rgb, a, np.array([90, 98, 110.0]), mask(hub))
    ol = Image.new("L", (N, N), 0)
    d = ImageDraw.Draw(ol)
    d.polygon([(x * S, y * S) for x, y in outer], outline=255, width=S)
    d.polygon([(x * S, y * S) for x, y in face], outline=255, width=S)
    comp(rgb, a, np.array([12, 16, 22.0]), np.asarray(ol).astype(float) / 255.0)
    return finish(rgb, a)


def sash():
    """The Lacrimosa's sash and vanes (quest item): two swept steel vane blades crossed by a navy ribbon with a glowing
    teal seam down its middle."""
    rgb = np.zeros((N, N, 3))
    a = np.zeros((N, N))
    halo = Image.new("L", (N, N), 0)
    ImageDraw.Draw(halo).ellipse([10 * S, 10 * S, 70 * S, 70 * S], fill=140)
    hal = np.asarray(halo.filter(ImageFilter.GaussianBlur(S * 7))).astype(float) / 255.0 * 0.4
    comp(rgb, a, VIOLET * 0.6 + TEAL * 0.4, hal)
    a[:] = hal
    steel = np.array([206, 214, 224.0])
    for sx in (1, -1):   # vanes: long swept blades with a stepped root, mirrored
        vane = [(40 + sx * 3, 68), (40 + sx * 6, 58), (40 + sx * 27, 12), (40 + sx * 35, 9), (40 + sx * 31, 24),
                (40 + sx * 16, 62), (40 + sx * 10, 70)]
        t = ramp((40, 66), (40 + sx * 32, 12))
        comp(rgb, a, steel * (1 - t * 0.35) + NAVY * t * 0.35, mask(vane))
        tip = [(40 + sx * 26, 26), (40 + sx * 30, 14), (40 + sx * 33, 12), (40 + sx * 29, 22)]
        comp(rgb, a, NAVY + 10, mask(tip))
    ribbon = [(14, 32), (66, 32), (71, 40), (66, 48), (14, 48), (9, 40)]
    tr = ramp((18, 34), (62, 46))
    comp(rgb, a, np.array([150, 160, 176.0]), mask([(x + (1 if x > 40 else -1), y + (1 if y > 40 else -1))
                                                     for x, y in ribbon]))   # steel edge
    comp(rgb, a, (NAVY + 30) * (1 - tr * 0.3) + np.array([20, 30, 60.0]) * tr * 0.3, mask(ribbon))
    seam = Image.new("L", (N, N), 0)
    ImageDraw.Draw(seam).line([(13 * S, 40 * S), (67 * S, 40 * S)], fill=255, width=int(2.2 * S))
    comp(rgb, a, TEAL, np.asarray(seam.filter(ImageFilter.GaussianBlur(S * 2))).astype(float) / 255.0 * 0.8)
    comp(rgb, a, np.array([210, 255, 250.0]), np.asarray(seam).astype(float) / 255.0)
    ol = Image.new("L", (N, N), 0)
    ImageDraw.Draw(ol).polygon([(x * S, y * S) for x, y in ribbon], outline=255, width=S)
    comp(rgb, a, np.array([12, 16, 22.0]), np.asarray(ol).astype(float) / 255.0)
    return finish(rgb, a)


def lacrimosa_intel():
    """Intel icon (40x40) for the Lacrimosa questline: the Virtuoso itself, glow on."""
    ship = Image.open(os.path.join(ROOT, "graphics", "rsl", "ships", "rsl_virtuoso.png")).convert("RGBA")
    glow = Image.open(os.path.join(ROOT, "graphics", "rsl", "ships", "rsl_virtuoso_glow.png")).convert("RGBA")
    arr = np.asarray(ship).astype(float)
    g = np.asarray(glow).astype(float)
    arr[..., :3] = np.clip(arr[..., :3] + g[..., :3] * (g[..., 3:4] / 255.0) * 0.9, 0, 255)
    im = Image.fromarray(arr.astype(np.uint8), "RGBA")
    k = 38.0 / max(im.width, im.height)
    im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
    out = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
    out.alpha_composite(im, ((40 - im.width) // 2, (40 - im.height) // 2))
    return out


def scores_intel():
    """Intel icon (40x40) for the Lost Scores: a five-line stave on a navy plate with one glowing diamond note."""
    n = 40 * S
    rgb = np.zeros((n, n, 3))
    a = np.zeros((n, n))
    plate = Image.new("L", (n, n), 0)
    ImageDraw.Draw(plate).polygon([(4 * S, 2 * S), (36 * S, 2 * S), (38 * S, 6 * S), (38 * S, 38 * S),
                                   (2 * S, 38 * S), (2 * S, 6 * S)], fill=255)
    pm = np.asarray(plate).astype(float) / 255.0
    yy = np.mgrid[0:n, 0:n][0] / n
    col = (NAVY + 10) * (1 - yy[..., None] * 0.4) + np.array([10, 14, 26.0]) * yy[..., None] * 0.4
    rgb[:] = col * pm[..., None]
    a[:] = pm
    lines = Image.new("L", (n, n), 0)
    d = ImageDraw.Draw(lines)
    for k in range(5):
        y = (11 + k * 4.5) * S
        d.line([(6 * S, y), (34 * S, y)], fill=150, width=S)
    d.polygon([(22 * S, 12 * S), (27 * S, 20 * S), (22 * S, 28 * S), (17 * S, 20 * S)], fill=255)
    lm = np.asarray(lines).astype(float) / 255.0
    glow = np.asarray(lines.filter(ImageFilter.GaussianBlur(S * 1.5))).astype(float) / 255.0
    rgb = rgb * (1 - glow[..., None] * 0.6) + TEAL * glow[..., None] * 0.6
    rgb = rgb * (1 - lm[..., None]) + np.array([210, 255, 250.0]) * lm[..., None]
    im = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a * 255]).astype(np.uint8), "RGBA")
    return im.resize((40, 40), Image.LANCZOS)


def contract_intel():
    """Intel icon (40x40) for the tuners' contract: the faction crest, as vanilla faction intel does."""
    crest = Image.open(os.path.join(ROOT, "graphics", "rsl", "factions", "rsl_crest.png")).convert("RGBA")
    return crest.resize((40, 40), Image.LANCZOS)


def main():
    os.makedirs(OUT, exist_ok=True)
    icons = {"rsl_pitchglass": pitchglass(), "rsl_pulsar_metronome": metronome(), "rsl_lacrimosa_sash": sash()}
    for k in GLYPHS:
        icons["rsl_bp_" + k] = blueprint(k)
    for name, im in icons.items():
        im.save(os.path.join(OUT, name + ".png"))
        print("wrote", name)
    extra = {os.path.join(ROOT, "graphics", "rsl", "icons", "markets", "rsl_lattice_nurseries.png"): nurseries(),
             os.path.join(ROOT, "graphics", "rsl", "icons", "industry", "rsl_cantor_array.png"): cantor_industry(),
             os.path.join(ROOT, "graphics", "rsl", "icons", "intel", "rsl_contract.png"): contract_intel(),
             os.path.join(ROOT, "graphics", "rsl", "icons", "intel", "rsl_lacrimosa.png"): lacrimosa_intel(),
             os.path.join(ROOT, "graphics", "rsl", "icons", "intel", "rsl_scores.png"): scores_intel()}
    for path, im in extra.items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        im.save(path)
        print("wrote", os.path.relpath(path, ROOT))
    icons.update({os.path.basename(p): im for p, im in extra.items()})
    if len(sys.argv) > 1:
        icons_dir = os.path.join(GAME, "starsector-core", "graphics", "icons")
        refs = [Image.open(os.path.join(icons_dir, f)).convert("RGBA")
                for f in ("cargo/ai_core_beta.png", "cargo/blueprint_hightech.png", "markets/rareore_rich.png",
                          "industry/star_fortress.png")]
        tiles = list(icons.values()) + refs
        width = sum(t.width * 2 + 20 for t in tiles) + 20
        full = Image.new("RGBA", (width, 2 * 190 + 60), (36, 38, 44, 255))
        x = 20
        for t in tiles:   # 2x row on top, 1x row below
            full.alpha_composite(t.resize((t.width * 2, t.height * 2), Image.NEAREST), (x, 20))
            full.alpha_composite(t, (x, 2 * 95 + 60 + 120))
            x += t.width * 2 + 20
        full.save(sys.argv[1])
        print("sheet", sys.argv[1])


if __name__ == "__main__":
    main()
