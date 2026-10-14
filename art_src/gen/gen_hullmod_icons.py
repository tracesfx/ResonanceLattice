#!/usr/bin/env python3
"""gen_hullmod_icons.py - hullmod icons in the vanilla style (user, 2026-10-12: "more in line with vanilla").

    python art_src/gen/gen_hullmod_icons.py      # needs the Blender renders in art_src/renders/<id>/ (./art_src/art.sh)

Vanilla hullmod icons (graphics/hullmods/*.png, 32x32) are full-bleed little paintings: a close-up of machinery or
an effect, strong light from one side, glow, a dark vignette, no frame. These are built the same way from our own
hull renders: a square crop of a render's colour pass (darkened and tinted to the steel/navy palette) over a dark
field, its emit pass bloomed, a key light gradient, the mechanic painted on top as light, then a vignette; worked at
128 px and reduced to 32 px. Writes graphics/rsl/icons/hullmods/<id>.png (overwrites gen_icons.py's versions).
"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
REN = os.path.join(ROOT, "art_src", "renders")
OUT = os.path.join(ROOT, "graphics", "rsl", "icons", "hullmods")
N = 128
TEAL, WHITE, VIOLET, GOLD = (90, 230, 220), (235, 255, 252), (170, 120, 255), (255, 215, 140)
random.seed(11)


def crop(render, cx, cy, size, rot=0):
    """Close-up of a hull render: colour darkened to the in-game tone, emit bloomed back on."""
    c = Image.open(os.path.join(REN, render, "color.png")).convert("RGBA")
    e = Image.open(os.path.join(REN, render, "emit.png")).convert("RGB")
    box = (int(cx - size / 2), int(cy - size / 2), int(cx + size / 2), int(cy + size / 2))
    c, e = c.crop(box), e.crop(box)
    if rot:
        c, e = c.rotate(rot, Image.BICUBIC), e.rotate(rot, Image.BICUBIC)
    c, e = c.resize((N, N), Image.LANCZOS), e.resize((N, N), Image.LANCZOS)
    a = np.asarray(c).astype(float) / 255
    rgb = a[..., :3] * np.array([0.40, 0.50, 0.68])           # steel -> navy-cool, darker (raw renders are near-white)
    y, x = np.mgrid[0:N, 0:N] / (N - 1)
    field = (np.array([0.02, 0.05, 0.12]) * (1 - y)[..., None] + np.array([0.01, 0.10, 0.13]) * y[..., None])
    out = field * (1 - a[..., 3:4]) + rgb * a[..., 3:4]
    em = np.asarray(e).astype(float) / 255
    bloom = np.asarray(e.filter(ImageFilter.GaussianBlur(5))).astype(float) / 255
    out = out + em * 0.9 + bloom * 0.7
    return out


def light(img, angle=-135, strength=0.55, rim=TEAL):
    """Key light from one corner (vanilla icons are lit from the upper left) plus a coloured rim light opposite."""
    y, x = np.mgrid[0:N, 0:N] / (N - 1) - 0.5
    d = x * math.cos(math.radians(angle)) + y * math.sin(math.radians(angle))
    lit = img * (1 + strength * (d * 1.6))[..., None]
    r = np.clip(-d * 1.4, 0, 1) ** 2
    return lit + r[..., None] * np.array(rim) / 255 * 0.35


def vignette(img, k=0.75):
    y, x = np.mgrid[0:N, 0:N] / (N - 1) - 0.5
    r = np.sqrt(x * x + y * y) / 0.707
    return img * (1 - k * np.clip(r, 0, 1) ** 2.2)[..., None]


def glow_layer(draw_fn, blur=4, gain=1.0):
    """Paint with draw_fn on a black canvas; return core + bloom as float RGB."""
    im = Image.new("RGB", (N, N), (0, 0, 0))
    draw_fn(ImageDraw.Draw(im))
    core = np.asarray(im).astype(float) / 255
    b1 = np.asarray(im.filter(ImageFilter.GaussianBlur(blur))).astype(float) / 255
    b2 = np.asarray(im.filter(ImageFilter.GaussianBlur(blur * 3))).astype(float) / 255
    return (core * 0.9 + b1 * 1.4 + b2 * 1.2) * gain


def screen(a, b):
    return 1 - (1 - np.clip(a, 0, 1)) * (1 - np.clip(b, 0, 1))


def finish(img, name, sat=1.45, size=32, out=None):
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype("uint8"), "RGB")
    if sat != 1.0:
        im = ImageEnhance.Color(im).enhance(sat)
    im = im.resize((size, size), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=1, percent=60, threshold=2))
    im = ImageEnhance.Contrast(im).enhance(1.12)
    out = out or OUT
    os.makedirs(out, exist_ok=True)
    im.convert("RGBA").save(os.path.join(out, name + ".png"))
    print(name)
    return im


def col(c, a=1.0):
    return tuple(int(v * a) for v in c)


# ------------------------------------------------------------------ icons
def lattice_core():
    base = light(crop("rsl_cantor", 1044, 1044, 330))
    def d(dr):
        c = N / 2
        dr.polygon([(c, c - 22), (c + 14, c), (c, c + 22), (c - 14, c)], fill=col(WHITE))
        for k in range(6):                                   # lattice spokes
            a = math.radians(k * 60 + 30)
            dr.line([(c + 18 * math.cos(a), c + 18 * math.sin(a)), (c + 58 * math.cos(a), c + 58 * math.sin(a))],
                    fill=col(TEAL, 0.8), width=3)
    return finish(vignette(screen(base, glow_layer(d, 3, 0.9))), "rsl_lattice_core")


def conductors_bridge():
    base = light(crop("rsl_conductor", 528, 330, 420))
    def d(dr):
        for k in range(5):                                   # beams fanning out from the muzzle to the chorus
            a = math.radians(-90 + (k - 2) * 24)
            dr.line([(64, 40), (64 + 90 * math.cos(a), 40 + 90 * math.sin(a))], fill=col(TEAL, 0.75), width=2)
        dr.ellipse([56, 32, 72, 48], fill=col(WHITE))
    return finish(vignette(screen(base, glow_layer(d, 3, 0.9))), "rsl_conductors_bridge")


def fracture():
    base = light(crop("rsl_staccato", 190, 430, 230, rot=20), strength=0.7)
    def d(dr):
        def crack(x, y, a, n, w):
            for _ in range(n):
                nx, ny = x + 9 * math.cos(a), y + 9 * math.sin(a)
                dr.line([(x, y), (nx, ny)], fill=col(TEAL), width=w)
                if random.random() < 0.35 and w > 1:
                    crack(nx, ny, a + random.choice((-0.9, 0.9)), n // 2, w - 1)
                x, y, a = nx, ny, a + random.uniform(-0.5, 0.5)
        crack(30, 34, 0.75, 10, 3)
        crack(98, 30, 2.2, 8, 2)
    return finish(vignette(screen(base * 0.85, glow_layer(d, 2, 1.0))), "rsl_fracture")


def stolen_time():
    base = light(crop("rsl_virtuoso", 496, 820, 380))
    def d(dr):
        for k in range(3):                                   # three violet wisps spiralling into the core
            pts = []
            for t in np.linspace(0, 1, 40):
                a = k * 2.094 + t * 4.2
                r = 60 * (1 - t) + 4
                pts.append((64 + r * math.cos(a), 64 + r * math.sin(a)))
            dr.line(pts, fill=col(VIOLET), width=3)
        dr.ellipse([56, 56, 72, 72], fill=col(WHITE))
    return finish(vignette(screen(base, glow_layer(d, 3, 0.9))), "rsl_stolen_time")


def bravura(name="rsl_bravura", silent=False):
    base = light(crop("rsl_virtuoso", 496, 600, 440), strength=0.6)
    if silent:
        gray = base.mean(axis=2, keepdims=True)
        img = vignette(np.repeat(gray, 3, axis=2) * 0.55, 0.85)
        def d(dr):
            dr.line([(20, 108), (108, 20)], fill=(150, 40, 40), width=6)
        return finish(screen(img, glow_layer(d, 1, 0.8)), name, sat=0.6)
    def d(dr):
        for k in range(12):                                  # white flare: the seams burning at full voice
            a = math.radians(k * 30 + 15)
            r = 60 if k % 2 == 0 else 38
            dr.line([(64, 64), (64 + r * math.cos(a), 64 + r * math.sin(a))], fill=col(WHITE, 0.8), width=2)
        dr.ellipse([52, 52, 76, 76], fill=col(WHITE))
    return finish(vignette(screen(base, glow_layer(d, 4, 1.0))), name, sat=1.25)


def unbound():
    base = light(crop("rsl_virtuoso", 496, 1330, 360), strength=0.6)
    def d(dr):
        for x in (40, 64, 88):                               # overdriven engines: white-violet plumes
            dr.polygon([(x - 7, 70), (x + 7, 70), (x, 126)], fill=col(VIOLET, 0.9))
            dr.ellipse([x - 7, 62, x + 7, 76], fill=col(WHITE))
    return finish(vignette(screen(base, glow_layer(d, 4, 1.1))), "rsl_unbound")


def phase_locked():
    base = light(crop("rsl_cantor", 1044, 1044, 980))
    def d(dr):
        for k in range(6):                                   # six petals locked to one phase
            a = math.radians(k * 60 - 90)
            x, y = 64 + 44 * math.cos(a), 64 + 44 * math.sin(a)
            dr.ellipse([x - 6, y - 6, x + 6, y + 6], fill=col(TEAL))
        dr.ellipse([20, 20, 108, 108], outline=col(TEAL, 0.6), width=2)
    return finish(vignette(screen(base, glow_layer(d, 3, 0.9))), "rsl_phase_locked")


def tuned_wings():
    base = light(crop("rsl_halo_ring", 376, 376, 720))
    ftr = Image.open(os.path.join(REN, "rsl_trill", "color.png")).convert("RGBA")
    def d(dr):
        dr.ellipse([14, 14, 114, 114], outline=col(TEAL, 0.7), width=2)
    img = screen(base, glow_layer(d, 3, 0.7))
    out = Image.fromarray((np.clip(img, 0, 1) * 255).astype("uint8"), "RGB").convert("RGBA")
    for k in range(3):                                       # three tuned fighters riding the ring
        a = k * 120 + 20
        f = ftr.resize((24, 40), Image.LANCZOS).rotate(-a, expand=True, resample=Image.BICUBIC)
        fa = np.asarray(f).astype(float)
        fa[..., :3] = np.clip(fa[..., :3] * np.array([0.85, 1.0, 1.05]) + np.array([10, 40, 40]), 0, 255)
        f = Image.fromarray(fa.astype("uint8"), "RGBA")
        x = 64 + 50 * math.cos(math.radians(a - 90)) - f.size[0] / 2
        y = 64 + 50 * math.sin(math.radians(a - 90)) - f.size[1] / 2
        out.alpha_composite(f, (int(x), int(y)))
    img = np.asarray(out.convert("RGB")).astype(float) / 255
    return finish(vignette(img), "rsl_tuned_wings")


def concert_pitch():
    base = light(crop("rsl_halo", 620, 760, 300)) * 0.8
    def d(dr):
        for k, r in enumerate((14, 28, 42, 56)):             # a perfect reference tone ringing outward
            dr.ellipse([64 - r, 64 - r, 64 + r, 64 + r], outline=col(WHITE, 1 - k * 0.2), width=2)
        dr.ellipse([58, 58, 70, 70], fill=col(WHITE))
    return finish(vignette(screen(base, glow_layer(d, 3, 0.85))), "rsl_concert_pitch")


def chorus_movement():
    base = light(crop("rsl_virtuoso", 496, 820, 380))
    def d(dr):
        for k in range(3):                                   # the stolen readiness flowing OUT to three allies
            a = math.radians(-90 + (k - 1) * 55)
            ex, ey = 64 + 54 * math.cos(a), 64 + 54 * math.sin(a)
            dr.line([(64, 64), (ex, ey)], fill=col(TEAL, 0.85), width=3)
            dr.ellipse([ex - 6, ey - 6, ex + 6, ey + 6], fill=col(WHITE))
        dr.ellipse([54, 54, 74, 74], fill=col(VIOLET))
    return finish(vignette(screen(base, glow_layer(d, 3, 0.9))), "rsl_chorus_movement")


def solo_movement():
    base = light(crop("rsl_virtuoso", 496, 600, 440), strength=0.65) * 0.8
    def d(dr):
        dr.ellipse([22, 22, 106, 106], outline=col(VIOLET, 0.7), width=3)   # nothing inside the ring but itself
        dr.polygon([(64, 30), (76, 64), (64, 98), (52, 64)], fill=col(WHITE))
    return finish(vignette(screen(base, glow_layer(d, 4, 1.0)), 0.85), "rsl_solo_movement")


def dead_chorus():
    base = light(crop("rsl_conductor", 528, 900, 420), strength=0.5)
    gray = base.mean(axis=2, keepdims=True)
    img = np.repeat(gray, 3, axis=2) * 0.7
    def d(dr):
        for k in range(6):                                   # a ring of dead voices, all on one violet note
            a = math.radians(k * 60 - 90)
            x, y = 64 + 42 * math.cos(a), 64 + 42 * math.sin(a)
            dr.ellipse([x - 7, y - 7, x + 7, y + 7], outline=col(VIOLET), width=3)
            dr.line([(x, y), (64, 64)], fill=col(VIOLET, 0.5), width=2)
        dr.ellipse([56, 56, 72, 72], fill=col(VIOLET))
    return finish(vignette(screen(img, glow_layer(d, 3, 1.0))), "rsl_dead_chorus", sat=1.1)


def ossia():
    """The duel's prize: the score's alternative passage - a second, fainter staff line branching off the dash."""
    base = light(crop("rsl_virtuoso", 496, 1100, 420), strength=0.6) * 0.8
    def d(dr):
        dr.line([(18, 100), (64, 54), (110, 30)], fill=col(TEAL), width=4)            # the written dash
        dr.line([(64, 54), (104, 70)], fill=col(WHITE, 0.75), width=3)                # ...and the ossia
        for x, y in ((18, 100), (110, 30), (104, 70)):
            dr.ellipse([x - 6, y - 6, x + 6, y + 6], fill=col(WHITE))
        dr.polygon([(64, 44), (72, 54), (64, 64), (56, 54)], fill=col(WHITE))
    return finish(vignette(screen(base, glow_layer(d, 3, 1.0))), "rsl_ossia")


def encore():
    """The Silence's prize: a single white note rising out of a dark, closed ring."""
    base = light(crop("rsl_virtuoso", 496, 600, 440), strength=0.55) * 0.55
    def d(dr):
        dr.ellipse([18, 18, 110, 110], outline=col((60, 70, 90), 0.9), width=6)       # the silence
        dr.arc([18, 18, 110, 110], 250, 290, fill=col(WHITE), width=6)                # broken by one voice
        dr.line([(64, 104), (64, 20)], fill=col(WHITE, 0.8), width=3)
        dr.polygon([(64, 14), (76, 30), (64, 46), (52, 30)], fill=col(WHITE))
    return finish(vignette(screen(base, glow_layer(d, 4, 1.1)), 0.85), "rsl_encore", sat=1.1)


def second_voice_skill():
    """Isolde Raike's skill icon (64x64): two diamond notes, one teal and one Hush violet, crossing blades."""
    base = light(crop("rsl_virtuoso", 496, 600, 440), strength=0.6) * 0.7
    def d(dr):
        dr.line([(24, 104), (104, 24)], fill=col(TEAL), width=5)
        dr.line([(24, 24), (104, 104)], fill=col(VIOLET), width=5)
        dr.polygon([(40, 26), (52, 40), (40, 54), (28, 40)], fill=col(WHITE))
        dr.polygon([(88, 26), (100, 40), (88, 54), (76, 40)], fill=col(VIOLET))
    return finish(vignette(screen(base, glow_layer(d, 4, 1.0))), "rsl_second_voice", sat=1.2, size=64,
                  out=os.path.join(ROOT, "graphics", "rsl", "icons", "skills"))


def concertmaster_skill():
    """Odile Marchetti's skill icon (64x64, vanilla skill-icon size): an unlocked tuning collar around a single clear
    note, over the Conductor's breech."""
    base = light(crop("rsl_conductor", 528, 700, 380), strength=0.6) * 0.75
    def d(dr):
        dr.arc([22, 22, 106, 106], 200, 500, fill=col(TEAL), width=6)       # the collar, open at the bottom
        dr.line([(40, 100), (52, 110)], fill=col(TEAL, 0.8), width=4)
        dr.polygon([(64, 36), (80, 64), (64, 92), (48, 64)], fill=col(WHITE))
        for k in (-1, 1):
            dr.line([(64 + k * 24, 64), (64 + k * 40, 64)], fill=col(WHITE, 0.7), width=2)
    return finish(vignette(screen(base, glow_layer(d, 4, 1.0))), "rsl_concertmaster", sat=1.2, size=64,
                  out=os.path.join(ROOT, "graphics", "rsl", "icons", "skills"))


def main():
    lattice_core()
    conductors_bridge()
    fracture()
    stolen_time()
    bravura()
    bravura("rsl_bravura_locked", silent=True)
    unbound()
    phase_locked()
    tuned_wings()
    concert_pitch()
    chorus_movement()
    solo_movement()
    dead_chorus()
    concertmaster_skill()
    ossia()
    encore()
    second_voice_skill()
    # review sheet: ours at 4x next to a few vanilla icons
    names = sorted(f for f in os.listdir(OUT) if f.endswith(".png"))
    van = os.path.join(ROOT, "..", "..", "starsector-core", "graphics", "hullmods")
    vnames = ["heavy_armor.png", "hardened_shields.png", "safety_overrides.png", "integrated_targeting_unit.png"]
    ims = [Image.open(os.path.join(OUT, f)) for f in names] + [Image.open(os.path.join(van, f)) for f in vnames]
    sheet = Image.new("RGBA", (len(ims) * 138 + 10, 148), (20, 22, 26, 255))
    for k, im in enumerate(ims):
        sheet.alpha_composite(im.convert("RGBA").resize((128, 128), Image.NEAREST), (10 + k * 138, 10))
    sheet.save(os.path.join(ROOT, "art_src", "review", "hullmod_icons_v2.png"))


if __name__ == "__main__":
    main()
