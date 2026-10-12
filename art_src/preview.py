"""Review sheet: our sprites at 1x / 2x (+ glow-on variant) next to vanilla peers, on the combat-dark background.

python preview.py out.png rsl_gracenote [rsl_refrain ...] --peers wolf,tempest,hammerhead [--scale 1,2] [--refs a.png,b.png]
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
SKILL = os.path.join(os.path.expanduser("~"), ".claude", "skills", "starsector-modding", "scripts")
sys.path.insert(0, SKILL)
import sslib  # noqa: E402

BG = (14, 17, 22, 255)


def vanilla_sprite(hull):
    core = sslib.core_dir(sslib.require_game_dir())
    ship = sslib.load_loose_json(os.path.join(core, "data", "hulls", hull + ".ship"))
    return Image.open(os.path.join(core, ship["spriteName"])).convert("RGBA")


def with_glow(sid, strength=1.0, suffix="_glow", folder="ships"):
    base = Image.open(os.path.join(MOD, "graphics/rsl/%s/%s.png" % (folder, sid))).convert("RGBA")
    gp = os.path.join(MOD, "graphics/rsl/%s/%s%s.png" % (folder, sid, suffix))
    if not os.path.exists(gp):
        return base
    b = np.asarray(base).astype(np.float32) / 255
    g = np.asarray(Image.open(gp).convert("RGBA")).astype(np.float32) / 255
    rgb = np.clip(b[..., :3] + g[..., :3] * g[..., 3:4] * strength, 0, 1)
    return Image.fromarray((np.concatenate([rgb, b[..., 3:4]], -1) * 255).astype(np.uint8), "RGBA")


def with_deco(sid, im, alt=False, suffix=None):
    """Paste decorative-slot sprites (rotated about their centre) onto the hull, as the game would draw them."""
    import json
    sp = os.path.join(HERE, "specs", sid + ".json")
    if not os.path.exists(sp):
        return im
    spec = json.load(open(sp, encoding="utf-8"))
    decos = [s for s in spec.get("slots", []) if s.get("deco")]
    if not decos:
        return im
    # the game draws decorative weapons past the hull bounds: pad the canvas instead of cropping them
    P = max(max(Image.open(os.path.join(MOD, "graphics/rsl/weapons/deco/%s.png" % s["deco"])).size) for s in decos)
    out = Image.new("RGBA", (im.width + 2 * P, im.height + 2 * P))
    out.paste(im, (P, P))
    W = im.width
    for s in decos:
        deco = Image.open(os.path.join(MOD, "graphics/rsl/weapons/deco/%s.png" % s["deco"])).convert("RGBA")
        if suffix:                                 # deco seams in the same glow state as the hull
            deco = with_glow(s["deco"], suffix=suffix, folder="weapons/deco")
        ang = s.get("deco_alt_angle", s.get("angle", 0)) if alt else s.get("angle", 0)
        for sx in ([1, -1] if s.get("sym") else [1]):
            r = deco.rotate(ang * sx, resample=Image.BICUBIC, expand=True)
            cx, cy = P + W / 2 + sx * s["pos"][0], P + s["pos"][1]
            out.alpha_composite(r, (int(round(cx - r.width / 2)), int(round(cy - r.height / 2))))
    x0, y0, x1, y1 = out.getbbox()
    return out.crop((min(x0, P), min(y0, P), max(x1, P + im.width), max(y1, P + im.height)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("ids", nargs="+")
    ap.add_argument("--peers", default="")
    ap.add_argument("--refs", default="")
    ap.add_argument("--scale", default="1,2")
    a = ap.parse_args()
    scales = [int(s) for s in a.scale.split(",")]
    items = []
    for sid in a.ids:
        base = Image.open(os.path.join(MOD, "graphics/rsl/ships/%s.png" % sid)).convert("RGBA")
        items.append((sid, with_deco(sid, base)))
        items.append((sid + " +glow", with_deco(sid, with_glow(sid), alt=True)))
        if os.path.exists(os.path.join(MOD, "graphics/rsl/ships/%s_glow_bravura.png" % sid)):
            items.append((sid + " bravura", with_deco(sid, with_glow(sid, suffix="_glow_bravura"), alt=True,
                                                      suffix="_glow_bravura")))
    for p in filter(None, a.peers.split(",")):
        items.append((p, vanilla_sprite(p)))
    for p in filter(None, a.refs.split(",")):
        items.append((os.path.basename(p), Image.open(p).convert("RGBA")))
    rows = []
    for s in scales:
        ims = [(n, im.resize((im.width * s, im.height * s), Image.NEAREST)) for n, im in items]
        rows.append((s, ims))
    pad = 12
    W = max(sum(im.width + pad for _, im in ims) + pad for _, ims in rows)
    H = sum(max(im.height for _, im in ims) + pad + 14 for _, ims in rows) + pad
    sheet = Image.new("RGBA", (W, H), BG)
    dr = ImageDraw.Draw(sheet)
    y = pad
    for s, ims in rows:
        x = pad
        hmax = max(im.height for _, im in ims)
        for n, im in ims:
            sheet.alpha_composite(im, (x, y + 14 + hmax - im.height))
            dr.text((x, y), "%s %dx" % (n, s), fill=(150, 160, 170, 255))
            x += im.width + pad
        y += hmax + pad + 14
    sheet.save(a.out)
    print(a.out)


if __name__ == "__main__":
    main()
