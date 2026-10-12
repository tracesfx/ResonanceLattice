"""Composite review sheet for the Cantor Array: core + ring deco + petal modules on their STATION_MODULE slots, as the
game would assemble it (module root on the slot, module pointing away from the core), normal and glow-on, next to
the other big hulls and one vanilla station.

python art_src/station_preview.py art_src/review/cantor_v1.png [--ring-angle 0] [--peers station2_hightech]
"""
import argparse
import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw

from preview import BG, HERE, MOD, vanilla_sprite, with_deco, with_glow

SHIPS = os.path.join(MOD, "graphics", "rsl", "ships")
DECO = os.path.join(MOD, "graphics", "rsl", "weapons", "deco")


def sprite(sid, folder, glow):
    if glow:
        return with_glow(sid, folder=folder)
    return Image.open(os.path.join(MOD, "graphics", "rsl", folder, sid + ".png")).convert("RGBA")


def composite(core_id, glow=False, ring_angle=0.0):
    spec = json.load(open(os.path.join(HERE, "specs", core_id + ".json"), encoding="utf-8"))
    core = sprite(core_id, "ships", glow)
    W, H = spec["size"]
    cx, cy = W / 2, H / 2
    pad = 260
    out = Image.new("RGBA", (W + 2 * pad, H + 2 * pad))
    out.alpha_composite(core, (pad, pad))
    for s in spec["slots"]:
        if s.get("deco"):
            d = sprite(s["deco"], "weapons/deco", glow).rotate(ring_angle, resample=Image.BICUBIC, expand=True)
            out.alpha_composite(d, (int(round(pad + cx + s["pos"][0] - d.width / 2)),
                                    int(round(pad + s["pos"][1] - d.height / 2))))
    for s in spec["slots"]:
        if s.get("type") != "STATION_MODULE":
            continue
        m = sprite(s["module"], "ships", glow)
        rx, ry = s["pos"][0], s["pos"][1] - cy                        # root, relative to the core centre
        a = math.degrees(math.atan2(ry, rx))
        r = m.rotate(-90 - a, resample=Image.BICUBIC, expand=True)
        mx = pad + cx + rx + m.height / 2 * math.cos(math.radians(a))
        my = pad + cy + ry + m.height / 2 * math.sin(math.radians(a))
        out.alpha_composite(r, (int(round(mx - r.width / 2)), int(round(my - r.height / 2))))
    return out.crop(out.getbbox())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--core", default="rsl_cantor")
    ap.add_argument("--ring-angle", type=float, default=0.0)
    ap.add_argument("--peers", default="station2_hightech")
    ap.add_argument("--hulls", default="rsl_cadence,rsl_tremolo,rsl_halo,rsl_conductor")
    a = ap.parse_args()
    items = [("Cantor Array 1x", composite(a.core)), ("+glow 1x", composite(a.core, True, 15))]
    for p in filter(None, a.peers.split(",")):
        items.append((p + " (core only) 1x", vanilla_sprite(p)))
    small = [(h, with_deco(h, Image.open(os.path.join(SHIPS, h + ".png")).convert("RGBA")))
             for h in filter(None, a.hulls.split(","))]
    pad = 16
    W = sum(im.width + pad for _, im in items) + pad
    H = max(im.height for _, im in items) + 40 + max(im.height for _, im in small) + 40
    sheet = Image.new("RGBA", (max(W, sum(im.width + pad for _, im in small) + pad), H), BG)
    dr = ImageDraw.Draw(sheet)
    x = pad
    hmax = max(im.height for _, im in items)
    for n, im in items:
        dr.text((x, 6), n, fill=(150, 160, 170, 255))
        sheet.alpha_composite(im, (x, 22 + (hmax - im.height) // 2))
        x += im.width + pad
    x, y = pad, hmax + 50
    for n, im in small:
        dr.text((x, y - 14), n + " 1x", fill=(150, 160, 170, 255))
        sheet.alpha_composite(im, (x, y))
        x += im.width + pad
    sheet.save(a.out)
    print(a.out, sheet.size)


if __name__ == "__main__":
    main()
