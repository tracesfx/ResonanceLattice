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


# ------------------------------------------------------------------ livery (paint on top of the rendered plates)
# Display colours (pre tone-match) that a plate shows at its typical shading.
# No yellow/amber: removed at the user's request (2026-10-11, "looks like caution tape"). Accent colour = dark blue.
PAINT = {
    "navy": (0.13, 0.19, 0.33), "blue": (0.22, 0.32, 0.52), "white": (0.95, 0.96, 0.97),
    "steel_light": (0.80, 0.82, 0.85), "steel_dark": (0.44, 0.47, 0.51), "gunmetal": (0.25, 0.27, 0.30),
    "black": (0.10, 0.11, 0.12),
    "ice": (0.58, 0.73, 0.96),           # very light blue (not teal) stripes, Virtuoso v3
}
MAT_PLATE, MAT_SLATE = 2, 7


def _xy(W, x, y):
    return ((W / 2 + x) * SS, y * SS)


def _mirror(pts):
    return [(-x, y) for x, y in pts]


def _shape_mask(L, W, H):
    """Rasterise one livery entry (spec coordinates) to a 4x float mask."""
    from PIL import ImageDraw
    m = Image.new("L", (W * SS, H * SS), 0)
    d = ImageDraw.Draw(m)
    t = L["type"]
    sym = L.get("sym", True)
    if t in ("poly", "stripes", "splinter", "gradient") and "poly" in L:
        for poly in [L["poly"]] + ([_mirror(L["poly"])] if sym else []):
            d.polygon([_xy(W, *p) for p in poly], fill=255)
    elif t in ("stripes", "splinter", "gradient"):
        d.rectangle([0, 0, W * SS, H * SS], fill=255)       # no region: whole sprite
    if t == "band":
        for pts in [L["pts"]] + ([_mirror(L["pts"])] if sym else []):
            d.line([_xy(W, *p) for p in pts], fill=255, width=max(1, int(round(L["w"] * SS))), joint="curve")
    mask = np.asarray(m).astype(np.float32) / 255
    if t in ("stripes", "splinter", "gradient"):
        X = (np.arange(W * SS, dtype=np.float32)[None, :] + 0.5) / SS - W / 2
        Y = (np.arange(H * SS, dtype=np.float32)[:, None] + 0.5) / SS
        ax = np.abs(X) if L.get("mirror", True) else X
        a = np.radians(L.get("angle", 45))
        u = ax * np.cos(a) + Y * np.sin(a)
        if t == "gradient":
            # linear ramp of paint opacity from point a (alpha a0) to point b (alpha a1); |x| mirrored by default
            (x0, y0), (x1, y1) = L["a"], L["b"]
            dx, dy = x1 - x0, y1 - y0
            f = np.clip(((ax - x0) * dx + (Y - y0) * dy) / max(1e-6, dx * dx + dy * dy), 0, 1)
            f = f * f * (3 - 2 * f) if L.get("smooth", True) else f
            return mask * (L.get("a0", 0.0) + (L.get("a1", 1.0) - L.get("a0", 0.0)) * f), None
        if t == "stripes":
            per, w = L["period"], L["w"]
            mask = mask * (np.mod(u - L.get("offset", 0), per) < w)
        else:
            v = -ax * np.sin(a) + Y * np.cos(a)
            zz = L.get("zigzag", 0)
            if zz:
                ph = np.mod(v / zz, 1.0)
                u = u + L.get("amp", 2.0) * (np.abs(ph - 0.5) * 4 - 1)
            if "widths" in L:      # irregular band widths, cycling (less mechanical than one period)
                cum = np.concatenate([[0.0], np.cumsum(L["widths"])]).astype(np.float32)
                idx = np.searchsorted(cum, np.mod(u - L.get("offset", 0), cum[-1]), side="right") - 1
            else:
                idx = np.floor((u - L.get("offset", 0)) / L["period"]).astype(np.int64)
            if "colors" in L:      # painted bands: 1 where this band carries paint, the colour is L["color"]
                on = np.array([c is not None for c in L["colors"]], np.float32)
                return mask * on[np.mod(idx, len(on))], None
            tones = np.array(L["tones"], np.float32)
            return mask, tones[np.mod(idx, len(tones))]
    return mask, None


def apply_livery(rgb4, mat, spec, W, H):
    """Paint the plates. Paint keeps the rendered shading (AO, bevels, grooves), so it reads as a decal on the hull;
    ink lines are drawn afterwards and cut through it."""
    entries = spec.get("livery", [])
    prot = np.zeros(mat.shape, np.float32)
    if not entries:
        return rgb4, prot
    lum = rgb4 @ np.array([0.299, 0.587, 0.114], np.float32)
    ref = {}
    for m_id in (MAT_PLATE, MAT_SLATE):
        sel = mat == m_id
        ref[m_id] = float(np.median(lum[sel])) if sel.sum() > 50 else 0.5
    for L in entries:
        mask, tone = _shape_mask(L, W, H)
        if L.get("soft"):                 # feathered edges: the stripe fades in/out instead of a hard line (px at 1x)
            mask = np.clip(hullgen.blur(mask, L["soft"] * SS), 0, 1)
        on = np.isin(mat, L.get("on", [MAT_PLATE]))
        k = mask * on * L.get("alpha", 1.0)
        if tone is not None:              # tonal pattern: multiply
            rgb4 = rgb4 * (1 + (tone - 1) * k)[..., None]
            continue
        col = np.array(PAINT.get(L["color"], L["color"]) if isinstance(L["color"], str) else L["color"], np.float32)
        refmap = np.where(mat == MAT_SLATE, ref[MAT_SLATE], ref[MAT_PLATE])
        shade = np.clip(lum / np.maximum(refmap, 1e-3), 0, 1.6)[..., None]
        rgb4 = rgb4 * (1 - k[..., None]) + np.clip(col * shade, 0, 1) * k[..., None]
        # bright paints only read as their colour when bright: keep them out of the tone remap (like the seams)
        if L.get("protect", L["color"] == "white"):
            prot = np.maximum(prot, k)
    return rgb4, prot


def finish(spec, rdir, mod, params):
    W, H = spec["size"]
    col = np.asarray(load(rdir, "color", "RGBA")).astype(np.float32) / 255
    emit = np.asarray(load(rdir, "emit", "RGB")).astype(np.float32) / 255
    nrm = np.asarray(load(rdir, "normal", "RGB")).astype(np.float32) / 255 * 2 - 1
    him = load(rdir, "height")
    h = np.asarray(him).astype(np.float32)
    h = h / (65535.0 if h.max() > 255 else 255.0) * ZMAX
    mat = np.rint(np.asarray(load(rdir, "matid", "L")).astype(np.float32) / 255 * 10).astype(np.int32)
    # --- cutouts: real openings through stacked parts (e.g. the Halo's hollow well); spec coordinates, no mirroring
    if spec.get("cutouts"):
        cut = np.zeros(mat.shape, np.float32)
        for poly in spec["cutouts"]:
            cut = np.maximum(cut, _shape_mask({"type": "poly", "poly": poly, "sym": False}, W, H)[0])
        keep = 1 - cut
        col = col * keep[..., None]
        emit = emit * keep[..., None]
        h = h * keep
        mat = np.where(cut > 0.5, 0, mat)
    A4 = col[..., 3]
    rgb4 = col[..., :3]
    solid = A4 > 0.5
    rgb4, prot4 = apply_livery(rgb4, mat, spec, W, H)

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
    prot1 = box_down(prot4, SS)
    rgb = hullgen.tone_match(rgb, A, np.maximum(emi_mask, prot1 * 2), TARGET, False)
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
    # Bravura (Virtuoso at 100% CR): same seam mask, radiant gold-white; the combat plugin cross-fades the two
    bravura_im = None
    if spec.get("bravura_glow"):
        gold = np.array([255, 200, 110], np.float32) / 255
        gb = np.concatenate([np.broadcast_to(gold, (H, W, 3)) * (1 - hot * 0.3) + hot * 0.3, ga[..., None]], -1)
        bravura_im = Image.fromarray((np.clip(gb, 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA")

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
    if bravura_im is not None:
        save(bravura_im, "%s/%s_glow_bravura.png" % (folder, sid))
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
    pairs = [(base + ".png", False), (base + "_glow.png", False), (base + "_glow_bravura.png", False),
             ("graphics/rsl/maps/%s_normal.png", True),
             ("graphics/rsl/maps/%s_material.png", False), ("graphics/rsl/maps/%s_surface.png", False)]
    for rel, is_normal in pairs:
        if not os.path.exists(os.path.join(mod, rel % src)):
            continue
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
