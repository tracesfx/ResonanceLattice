"""4x Blender passes -> 1x Starsector sprite, seam glow layer, GraphicsLib maps and the .ship file.

python finish.py specs/rsl_gracenote.json [--renders renders] [--mod ..]

Steps: ink lines from height/normal breaks, convex-edge highlight, premultiplied 4x box downscale, tone match to
the vanilla band (between Midline and High Tech), dark silhouette rim, alpha bleed. Reuses hullgen.py from the
starsector-modding skill (tone_match, alpha_bleed, ship_json, check).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

SKILL = os.path.join(os.path.expanduser("~"), ".claude", "skills", "starsector-modding", "scripts")
sys.path.insert(0, SKILL)
import hullgen  # noqa: E402

SS = 4
ZMAX = 16.0
# Lattice sits between Midline (p5 .125 / p95 .835 / mean .47) and High Tech (.105 / .76 / .42)
TARGET = dict(p5=0.11, p95=0.80, mean=0.44, sat=0.14)
SEAM_A = np.array([90, 220, 210], np.float32) / 255   # teal (top)
SEAM_B = np.array([150, 110, 230], np.float32) / 255  # violet (tail)


def load(d, name, mode=None):
    im = Image.open(os.path.join(d, name + ".png"))
    return im if mode is None else im.convert(mode)


def shift(a, dy, dx):
    return np.roll(np.roll(a, dy, 0), dx, 1)


def box_down(a, k):
    H, W = a.shape[0] // k, a.shape[1] // k
    a = a[:H * k, :W * k]
    return a.reshape(H, k, W, k, *a.shape[2:]).mean(axis=(1, 3))


def dilate(m, r=1):
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            out |= shift(m, dy, dx)
    return out


def finish(spec, rdir, mod, params):
    W, H = spec["size"]
    col = np.asarray(load(rdir, "color", "RGBA")).astype(np.float32) / 255
    emit = np.asarray(load(rdir, "emit", "RGB")).astype(np.float32) / 255
    nrm = np.asarray(load(rdir, "normal", "RGB")).astype(np.float32) / 255 * 2 - 1
    him = load(rdir, "height")
    h = np.asarray(him).astype(np.float32)
    h = h / (65535.0 if h.max() > 255 else 255.0) * ZMAX
    mat = np.rint(np.asarray(load(rdir, "matid", "L")).astype(np.float32) / 255 * 10).astype(np.int32)
    A4 = col[..., 3]
    rgb4 = col[..., :3]
    solid = A4 > 0.5

    # --- ink: steps in height and creases in the normal field (1-2 px at 4x -> ~0.5 px dark line at 1x)
    step = np.zeros_like(h)
    crease = np.zeros_like(h)
    for dy, dx in ((1, 0), (0, 1), (-1, 0), (0, -1)):
        hs = shift(h, dy, dx)
        step = np.maximum(step, h - hs)          # we are the higher side: line sits on the lower side instead
        crease = np.maximum(crease, 1 - (nrm * shift(nrm, dy, dx)).sum(-1))
    low_side = np.zeros_like(h, dtype=bool)
    for dy, dx in ((1, 0), (0, 1), (-1, 0), (0, -1)):
        low_side |= (shift(h, dy, dx) - h) > params["ink_step"]
    ink = (low_side | (crease > params["ink_crease"])) & solid
    ink = dilate(ink, 1) & solid
    rgb4 = rgb4 * (1 - params["ink"] * ink[..., None])

    # --- convex highlight: points higher than their surroundings (plate edges, bevels, greeble tops)
    hb = hullgen.blur(h, 3.0)
    crest = np.clip((h - hb) / 1.2, 0, 1) * solid * (mat != 3)
    rgb4 = np.clip(rgb4 + params["crest"] * crest[..., None] * (0.35 + rgb4), 0, 1)

    # --- downscale (premultiplied)
    pm = np.concatenate([rgb4 * A4[..., None], A4[..., None]], -1)
    d = box_down(pm, SS)
    A = d[..., 3]
    rgb = np.where(A[..., None] > 1e-4, d[..., :3] / np.maximum(A[..., None], 1e-4), 0)
    emi1 = box_down(emit, SS).max(-1)
    seam1 = box_down((mat == 3) | (mat == 4), SS)
    emi_mask = np.clip(np.maximum(emi1 * 3, seam1 * 1.5), 0, 1)

    # --- tone match (emissive pixels excluded), dark rim
    rgb = hullgen.tone_match(rgb, A, emi_mask, TARGET, False)
    opaque = A > 0.5
    edge = opaque & ~(shift(opaque, 1, 0) & shift(opaque, -1, 0) & shift(opaque, 0, 1) & shift(opaque, 0, -1))
    rgb = np.where(edge[..., None], rgb * params["rim"], rgb)
    # seams in the base sprite: keep them readable but dim, tinted along the hull
    t = (np.clip((np.linspace(0, 1, H, dtype=np.float32) - 0.55) / 0.45, 0, 1) * 0.6)[:, None, None]
    seam_col = SEAM_A * (1 - t) + SEAM_B * t
    base_seam = np.clip(emi_mask, 0, 1)[..., None] * params["seam_base"]
    # hot core: strongly emissive pixels lift towards white so seams read at 1x
    hot = np.clip(emi1 * 2.2 - 0.6, 0, 1)[..., None] * params["seam_hot"]
    seam_px = seam_col * (1 - hot) + hot
    rgb = rgb * (1 - base_seam) + seam_px * base_seam
    # faint spill onto neighbouring plate pixels (1 px), so the seams separate from the ivory
    spill = np.clip(hullgen.blur(emi_mask, 0.9) - emi_mask, 0, 1)[..., None] * params["seam_spill"] * (A[..., None] > 0.5)
    rgb = rgb * (1 - spill) + seam_col * spill
    A = np.where(A < 0.02, 0, A)
    out = np.concatenate([rgb, A[..., None]], -1)
    sprite = hullgen.alpha_bleed(Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA"))

    # --- glow layer: seams only, gradient colour, alpha = emission
    ga = np.clip(emi_mask * 1.2, 0, 1)
    ga = np.maximum(ga, np.clip(hullgen.blur(ga, 1.4) * params["halo"], 0, 1))
    glow = np.concatenate([np.broadcast_to(seam_col, (H, W, 3)) * (1 - hot * 0.5) + hot * 0.5, ga[..., None]], -1)
    glow_im = Image.fromarray((np.clip(glow, 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA")

    # --- GraphicsLib maps (normal: R = +right, G = +down, B = +z)
    n1 = box_down(nrm * A4[..., None], SS)
    n1 = n1 / np.maximum(np.linalg.norm(n1, axis=-1, keepdims=True), 1e-4)
    nmap = np.stack([n1[..., 0] * 0.5 + 0.5, -n1[..., 1] * 0.5 + 0.5, np.clip(n1[..., 2], 0, 1) * 0.5 + 0.5, A], -1)
    m1 = np.rint(box_down(mat.astype(np.float32), SS)).astype(np.int32)
    spec_i = np.select([m1 == 2, m1 == 1], [0.55, 0.3], 0.15)
    surf = np.stack([np.zeros_like(A), spec_i, np.full_like(A, 0.35), A], -1)
    matmap = np.concatenate([rgb * 0.72, A[..., None]], -1)

    def save(arr_or_im, rel):
        p = os.path.join(mod, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        im = arr_or_im if isinstance(arr_or_im, Image.Image) else \
            Image.fromarray((np.clip(arr_or_im, 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA")
        im.save(p)
        return p

    sid = spec["id"]
    kind = spec.get("kind", "ship")
    folder = "graphics/rsl/ships" if kind == "ship" else "graphics/rsl/weapons/deco"
    save(sprite, "%s/%s.png" % (folder, sid))
    save(glow_im, "%s/%s_glow.png" % (folder, sid))
    save(nmap, "graphics/rsl/maps/%s_normal.png" % sid)
    save(matmap, "graphics/rsl/maps/%s_material.png" % sid)
    save(surf, "graphics/rsl/maps/%s_surface.png" % sid)
    if kind == "ship":
        spec = dict(spec, sprite_path="%s/%s.png" % (folder, sid))
        spec.setdefault("ship", {}).setdefault("style", "MIDLINE")
        ship = hullgen.ship_json(spec, sprite)
        for w in hullgen.check(spec, sprite, ship):
            print("WARN", w)
        p = os.path.join(mod, "data", "hulls", sid + ".ship")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            json.dump(ship, f, indent=2)
    a = np.asarray(sprite)[..., 3]
    print("finished %s: %dx%d, opaque px %d" % (sid, W, H, int((a > 127).sum())))
    return sprite


def mirror(spec, mod):
    """Left/right deco pair: the game never flips weapon sprites, so build the mirrored part from the finished one
    (pixel-exact; the normal map's x channel is inverted)."""
    src, dst = spec["mirror_of"], spec["id"]
    base = "graphics/rsl/weapons/deco/%s"
    pairs = [(base + ".png", False), (base + "_glow.png", False), ("graphics/rsl/maps/%s_normal.png", True),
             ("graphics/rsl/maps/%s_material.png", False), ("graphics/rsl/maps/%s_surface.png", False)]
    for rel, is_normal in pairs:
        im = Image.open(os.path.join(mod, rel % src)).convert("RGBA").transpose(Image.FLIP_LEFT_RIGHT)
        if is_normal:
            a = np.asarray(im).copy()
            a[..., 0] = np.where(a[..., 3] > 0, 255 - a[..., 0], a[..., 0])
            im = Image.fromarray(a, "RGBA")
        im.save(os.path.join(mod, rel % dst))
    print("mirrored %s -> %s" % (src, dst))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--renders", default=os.path.join(here, "renders"))
    ap.add_argument("--mod", default=os.path.dirname(here))
    a = ap.parse_args()
    with open(a.spec, encoding="utf-8") as f:
        spec = json.load(f)
    if spec.get("mirror_of"):
        mirror(spec, a.mod)
        return
    params = dict(ink=0.65, ink_step=0.45, ink_crease=0.25, crest=0.35, rim=0.62, seam_base=0.95, seam_hot=0.45,
                  seam_spill=0.35, halo=0.6)
    params.update(spec.get("finish", {}))
    finish(spec, os.path.join(a.renders, spec["id"]), a.mod, params)


if __name__ == "__main__":
    main()
