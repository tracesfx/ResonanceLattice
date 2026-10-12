#!/usr/bin/env python3
"""gen_weapons.py - Resonance Lattice weapon, projectile and missile sprites (2D procedural, the hulls' palette).

    python art_src/gen/gen_weapons.py [--preview art_src/review/weapons_v1.png]

Writes graphics/rsl/weapons/<id>_{turret,hardpoint}[_glow].png and graphics/rsl/missiles/*.png, and
art_src/gen/weapon_offsets.json (muzzle offsets per weapon and mount) that tools/gen_data.py reads for the .wpn files.

Visual language shared with the hulls (CLAUDE.md "standing art direction"): bright / brushed steel housings with
chamfered, angular outlines (no round turret discs), gunmetal and graphite machinery underneath, dark-blue (navy)
livery panels, teal lattice seams and crystal emitters (the emissive parts; they also form the _glow sprites).
Recurring faction motif: the tuning fork (twin prongs around a crystal) on the energy weapons.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SKILL = os.path.join(os.path.expanduser("~"), ".claude", "skills", "starsector-modding", "scripts")
sys.path.insert(0, SKILL)
import hullgen  # noqa: E402
import weapongen as wg  # noqa: E402

wg.PAL["lattice"] = dict(
    metal_l=(206, 212, 218), metal_m=(140, 148, 160), metal_d=(64, 68, 76), paint=(48, 66, 108),
    paint_d=(34, 46, 80), accent=(78, 84, 94), glow=(110, 235, 225))
NAVY, NAVY_D, GUN, GRAPH = (48, 66, 108), (34, 46, 80), (70, 75, 84), (40, 43, 48)
TEAL, VIOLET, WHITE = (100, 230, 220), (160, 120, 240), (225, 245, 245)
SS = wg.SS


def sd_poly(x, y, pts):
    """Signed distance to a closed polygon (negative inside)."""
    pts = np.asarray(pts, np.float32)
    d = np.full(x.shape, 1e9, np.float32)
    inside = np.zeros(x.shape, bool)
    n = len(pts)
    for i in range(n):
        ax, ay = pts[i]
        bx, by = pts[(i + 1) % n]
        px, py, vx, vy = x - ax, y - ay, bx - ax, by - ay
        t = np.clip((px * vx + py * vy) / max(1e-6, vx * vx + vy * vy), 0, 1)
        d = np.minimum(d, np.hypot(px - vx * t, py - vy * t))
        cond = ((ay > y) != (by > y)) & (x < (bx - ax) * (y - ay) / (by - ay + 1e-9) + ax)
        inside ^= cond
    return np.where(inside, -d, d)


class LKit(wg.Kit):
    """weapongen's Kit plus angular plates, emissive seams and crystals."""

    def __init__(self, W, H, seed, scale):
        super().__init__(W, H, "lattice", np.random.default_rng(seed), scale)

    def c(self, name):
        if isinstance(name, str):
            return self.pal[name]
        v = np.array(name, np.float32)
        return v / 255.0 if v.max() > 1.0 else v

    def plate(self, pts, color, mirror=False, ink=0.6, bevel=True, grad=0.0):
        """Chamfered plate from a polygon in design units (x from centre line, y from top). `grad` darkens the plate
        towards its outer/rear extremity (the hulls' "dipped" gradients)."""
        sets = [pts]
        if mirror:
            sets.append([(-px, py) for px, py in pts])
        for p in sets:
            d = sd_poly(self.x, self.y, p)
            e = -d
            shade = np.full(d.shape, 0.80, np.float32)
            if bevel:
                shade = np.where(e < 0.6, 1.04, np.where(e < 1.3, 0.68, 0.82))
            if grad:
                ys = np.array([q[1] for q in p])
                t = np.clip((self.y - ys.min()) / max(1.0, ys.max() - ys.min()), 0, 1)
                shade = shade * (1.0 - grad * t)
            self._fill(d, shade, color, ink)

    def seam(self, pts, w=0.55, color=TEAL, mirror=False):
        """Emissive lattice seam polyline (no ink: it reads as a glowing groove)."""
        for sgn in ((1, -1) if mirror else (1,)):
            for (ax, ay), (bx, by) in zip(pts[:-1], pts[1:]):
                d = wg.sd_segment(self.x, self.y, ax * sgn, ay, bx * sgn, by, w / 2.0)
                self._fill(d, np.full(d.shape, 1.0, np.float32), color, ink=0, emissive=True, noise=0)

    def crystal(self, cx, cy, rx, ry, color=TEAL, mirror=False):
        """Diamond crystal emitter: bright core, inked rim."""
        for sx in ((cx, -cx) if mirror and abs(cx) > 1e-3 else (cx,)):
            p = [(sx, cy - ry), (sx + rx, cy), (sx, cy + ry), (sx - rx, cy)]
            d = sd_poly(self.x, self.y, p)
            r = np.clip(np.abs(self.x - sx) / rx + np.abs(self.y - cy) / ry, 0, 1)
            self._fill(d, 1.25 - 0.5 * r, color, ink=0.45, emissive=True, noise=0)

    def node(self, cx, cy, r, mirror=False):
        self.dome(cx, cy, r, r, TEAL, emissive=True, mirror=mirror, ink=0.35)

    def prong(self, x0, x1, y_tip, y_root, color="metal_l", mirror=True, tip_cut=2.0):
        """Tuning-fork prong: a slab with a diagonal tip cut (outer edge runs on to the point)."""
        self.plate([(x0, y_tip + tip_cut), (x1, y_tip), (x1, y_root), (x0, y_root)], color, mirror=mirror)

    def rail(self, x0, x1, y0, y1, color="metal_l", ribs=0, mirror=False):
        self.cyl(x0, y0, x1, y1, color, mirror=mirror, r=min(0.6, (x1 - x0) * 0.25), ribs=ribs)


def housing(k, y0, y1, hw, navy=True, step=0.30, seams=True, color="metal_l"):
    """Angular gun housing (stepped, chamfered, never a disc): a narrower front block, a wider rear block with
    chamfered shoulders, a navy livery panel and seams running back from the barrel root."""
    h = y1 - y0
    ys = y0 + h * step
    k.plate([(0, y1), (hw, y1 - h * 0.12), (hw, ys + h * 0.10), (hw * 0.78, ys), (0, ys)], "metal_m", mirror=True,
            grad=0.25)
    k.plate([(0, ys + 0.5), (hw * 0.62, ys + 0.5), (hw * 0.70, y0 + h * 0.08), (hw * 0.40, y0), (0, y0)], color,
            mirror=True)
    if navy:
        k.plate([(hw * 0.18, ys + h * 0.18), (hw * 0.86, ys + h * 0.20), (hw * 0.86, y1 - h * 0.24),
                 (hw * 0.30, y1 - h * 0.30)], NAVY, mirror=True, bevel=False, ink=0.4)
    k.slits(-hw * 0.5, y1 - h * 0.16, hw * 0.5, y1 - h * 0.04, 2, color=GRAPH)
    if seams:
        k.seam([(hw * 0.12, y0 + h * 0.10), (hw * 0.12, ys + h * 0.12), (hw * 0.55, y1 - h * 0.18)], mirror=True)


def mounts(k, y, hw, s):
    """Short gunmetal clamps under the housing (attachment to the slot)."""
    k.plate([(hw * 0.55, y - 1.5 * s), (hw * 1.02, y - 0.5 * s), (hw * 0.95, y + 2.0 * s), (hw * 0.50, y + 2.4 * s)],
            GUN, mirror=True, bevel=False)


# ======================================================================================== compositions
# Each returns (kit, muzzles). Design units = final px; x from the centre line (+ right), y from the top.

def comp_chime(W, H, hp, s):
    k = LKit(W, H, 11, s)
    t = 1.0
    body0 = H * (0.55 if hp else 0.48)
    housing(k, body0, H - (1 if hp else 4), W * (0.40 if hp else 0.26))
    gap = W * (0.10 if hp else 0.07)
    k.prong(gap, gap + 2.0 * s + 0.6, t + 1, body0 + 1, "metal_l")
    k.crystal(0, body0 - 3.0 * s, 1.5 * s, 2.6 * s)
    k.seam([(0, body0 - 0.5), (0, H - 4)], w=0.5)
    return k, [(0.0, t + 2)]


def comp_pizzicato(W, H, hp, s):
    k = LKit(W, H, 12, s)
    body0 = H * (0.58 if hp else 0.52)
    housing(k, body0, H - (1 if hp else 4), W * (0.36 if hp else 0.24), step=0.4)
    k.rail(-0.9 * s, 0.9 * s, 1.0, body0 + 1, ribs=4)
    k.plate([(0, 0.5), (1.6 * s, 2.6 * s), (0, 4.0 * s)], "metal_m", mirror=True, bevel=False)
    k.plate([(1.0 * s, body0 - 6 * s), (2.6 * s, body0 - 4 * s), (2.6 * s, body0), (1.0 * s, body0)], GUN, mirror=True)
    k.seam([(0, body0 - 4 * s), (0, body0 + 3)], w=0.45)
    k.node(0, body0 + 4 * s, 0.9 * s)
    return k, [(0.0, 1.0)]


def comp_shard(W, H, hp, s):
    k = LKit(W, H, 13, s)
    body0 = H * (0.50 if hp else 0.46)
    hw = W * (0.40 if hp else 0.28)
    housing(k, body0, H - (1 if hp else 4), hw, step=0.35)
    muz = []
    for xi in (-1, 0, 1):
        x = xi * hw * 0.42
        top = (2.0 if xi == 0 else 3.5)
        k.plate([(x - 1.1 * s, body0 + 1), (x - 1.0 * s, top + 1.5), (x, top), (x + 1.0 * s, top + 1.5),
                 (x + 1.1 * s, body0 + 1)], "metal_l")
        k.crystal(x, top + 2.2 * s, 0.7 * s, 1.4 * s)
        muz.append((x, top))
    k.plate([(-hw * 0.8, body0 - 1.2 * s), (hw * 0.8, body0 - 1.2 * s), (hw * 0.7, body0 + 0.8 * s),
             (-hw * 0.7, body0 + 0.8 * s)], NAVY, bevel=False)
    return k, muz


def comp_spike_rack(W, H, hp, s, n):
    k = LKit(W, H, 14 + n, s)
    top = H * (0.06 if hp else 0.14)
    bot = H - (1 if hp else 3)
    hw = W * (0.44 if hp else 0.40)
    k.plate([(0, bot), (hw, bot - 2), (hw, top + 3), (hw - 2, top), (0, top)], "metal_m", mirror=True, grad=0.3)
    cols = n if n <= 2 else n // 2
    rows = 1 if n <= 2 else 2
    cw = 2 * hw / cols
    rh = (bot - top - 2) / rows
    muz = []
    for r in range(rows):
        for c in range(cols):
            cx = -hw + (c + 0.5) * cw
            y0 = top + 1.5 + r * rh
            tw = min(cw * 0.55, 3.4 * s + 0.6)
            k.box(cx - tw / 2 - 0.4, y0, cx + tw / 2 + 0.4, y0 + rh - 1.2, GRAPH, r=0.3, bevel=False)
            k.plate([(cx, y0 + 0.4), (cx + tw / 2, y0 + tw * 1.3), (cx + tw * 0.32, y0 + rh - 2.0),
                     (cx - tw * 0.32, y0 + rh - 2.0), (cx - tw / 2, y0 + tw * 1.3)], "metal_l", ink=0.4)
            k.crystal(cx, y0 + tw * 0.75, tw * 0.28, tw * 0.6)
            muz.append((cx, y0 + 0.5))
    k.plate([(-hw, (top + bot) / 2 - 0.8 * s), (hw, (top + bot) / 2 - 0.8 * s), (hw, (top + bot) / 2 + 0.8 * s),
             (-hw, (top + bot) / 2 + 0.8 * s)], NAVY, bevel=False)
    return k, muz


def comp_lattice_lance(W, H, hp, s):
    k = LKit(W, H, 21, s)
    body0 = H * (0.58 if hp else 0.50)
    hw = W * (0.40 if hp else 0.28)
    housing(k, body0, H - (1 if hp else 5), hw)
    mounts(k, H - (5 if not hp else 3), hw, s)
    g = 1.6 * s
    k.prong(g, g + 2.2 * s, 1.5, body0 + 1)
    k.plate([(g + 2.2 * s, 6 * s), (g + 3.2 * s, 8 * s), (g + 3.2 * s, body0), (g + 2.2 * s, body0)], NAVY,
            mirror=True, bevel=False)
    k.seam([(g + 0.6, 4), (g + 0.6, body0 - 1)], mirror=True, w=0.5)
    for f in (0.35, 0.6, 0.85):
        y = 1.5 + (body0 - 1.5) * f
        k.plate([(g - 0.2, y), (g + 3.4 * s, y + 0.6), (g + 3.4 * s, y + 1.6 * s), (g - 0.2, y + 1.2 * s)], GUN,
                mirror=True, bevel=False)
    k.crystal(0, body0 - 4.5 * s, 1.4 * s, 3.4 * s)
    return k, [(0.0, 3.0)]


def comp_flechette(W, H, hp, s):
    k = LKit(W, H, 22, s)
    body0 = H * (0.52 if hp else 0.46)
    hw = W * (0.42 if hp else 0.30)
    housing(k, body0, H - (1 if hp else 5), hw, step=0.3)
    mounts(k, H - (5 if not hp else 3), hw, s)
    muz = []
    for xi, top in ((-1, 5.0), (0, 2.0), (1, 5.0)):
        x = xi * hw * 0.48
        k.plate([(x - 1.6 * s, body0 + 1), (x - 1.4 * s, top + 2), (x, top), (x + 1.4 * s, top + 2),
                 (x + 1.6 * s, body0 + 1)], "metal_l" if xi == 0 else "metal_m")
        k.crystal(x, top + 3.5 * s, 0.9 * s, 2.0 * s)
        k.box(x - 1.8 * s, body0 - 3 * s, x + 1.8 * s, body0 - 1.6 * s, GUN, r=0.2, bevel=False)
        muz.append((x, top))
    k.seam([(0, body0 - 1), (0, H - 6)], w=0.5)
    return k, muz


def comp_arpeggio(W, H, hp, s):
    k = LKit(W, H, 23, s)
    body0 = H * (0.56 if hp else 0.50)
    hw = W * (0.42 if hp else 0.30)
    housing(k, body0, H - (1 if hp else 5), hw)
    mounts(k, H - (5 if not hp else 3), hw, s)
    muz = []
    for xi, top in ((-1, body0 * 0.42), (0, 1.0), (1, body0 * 0.42)):   # rising notes: short-long-short
        x = xi * hw * 0.50
        k.rail(x - 1.1 * s, x + 1.1 * s, top, body0 + 1, ribs=3 if xi == 0 else 2)
        k.box(x - 1.6 * s, top, x + 1.6 * s, top + 1.6 * s, "metal_m", r=0.3, bevel=False)
        muz.append((x, top))
    k.seam([(hw * 0.25, body0 + 2), (hw * 0.25, body0 + 6 * s), (hw * 0.6, body0 + 9 * s)], mirror=True)
    k.crystal(0, body0 + 5 * s, 1.2 * s, 2.0 * s)
    return k, muz


def comp_cantus(W, H, hp, s):
    k = LKit(W, H, 24, s)
    body0 = H * (0.54 if hp else 0.50)
    hw = W * (0.42 if hp else 0.30)
    housing(k, body0, H - (1 if hp else 5), hw, step=0.4, seams=False)
    mounts(k, H - (5 if not hp else 3), hw, s)
    muz = []
    for sx in (-1, 1):
        x = sx * hw * 0.36
        k.rail(x - 1.5 * s, x + 1.5 * s, 3, body0 + 2, ribs=4, color="metal_m")
        k.plate([(x - 2.0 * s, 2), (x + 2.0 * s, 2), (x + 2.0 * s, 5 * s), (x - 2.0 * s, 5 * s)], NAVY, bevel=False)
        muz.append((x, 2.0))
    k.seam([(0, body0 - 2), (0, H - 6)], w=0.5)
    k.node(0, body0 + 3 * s, 1.0 * s)
    return k, muz


def comp_harmonic(W, H, hp, s, spinal=False):
    k = LKit(W, H, 31, s)
    if spinal:   # the barrel is baked into the Conductor's hull: only the emitter crystal and its seam
        k.crystal(0, 7.0, 3.0, 6.0)
        k.seam([(0, 13.0), (0, 22.0)], w=0.9)
        return k, [(0.0, 2.0)]
    body0 = H * (0.56 if hp else 0.50)
    hw = W * (0.40 if hp else 0.27)
    housing(k, body0, H - (1 if hp else 6), hw)
    mounts(k, H - (6 if not hp else 3), hw, s)
    g = 2.2 * s
    k.prong(g, g + 3.0 * s, 1.0, body0 + 2)
    k.plate([(g + 3.0 * s, 4 * s), (g + 4.4 * s, 7 * s), (g + 4.4 * s, body0 - 2 * s), (g + 3.0 * s, body0)], NAVY,
            mirror=True, bevel=False)
    for f in (0.30, 0.55, 0.80):
        y = 1 + (body0 - 1) * f
        k.plate([(g - 0.4, y), (g + 4.6 * s, y + 1.0), (g + 4.6 * s, y + 2.2 * s), (g - 0.4, y + 1.6 * s)], GUN,
                mirror=True, bevel=False)
    k.seam([(g + 0.7, 4), (g + 0.7, body0)], w=0.6, mirror=True)
    k.crystal(0, body0 - 5 * s, 1.8 * s, 4.5 * s)
    k.crystal(0, body0 + 5 * s, 2.4 * s, 3.0 * s)
    return k, [(0.0, 3.0)]


def comp_sostenuto(W, H, hp, s):
    k = LKit(W, H, 32, s)
    body0 = H * (0.55 if hp else 0.48)
    hw = W * (0.42 if hp else 0.30)
    housing(k, body0, H - (1 if hp else 6), hw, step=0.35)
    mounts(k, H - (6 if not hp else 3), hw, s)
    # three converging vanes focus on a crystal tip
    tip = 4.0
    k.plate([(0.8 * s, tip + 3), (hw * 0.55, body0 * 0.55), (hw * 0.62, body0 + 1), (hw * 0.30, body0 + 1),
             (0.8 * s, tip + 8)], "metal_l", mirror=True)
    k.plate([(hw * 0.40, body0 * 0.6), (hw * 0.58, body0 * 0.62), (hw * 0.60, body0 - 1), (hw * 0.40, body0 - 1)],
            NAVY, mirror=True, bevel=False)
    k.rail(-1.2 * s, 1.2 * s, tip + 2, body0 + 2, ribs=4, color="metal_m")
    k.crystal(0, tip + 2.0 * s, 1.6 * s, 3.2 * s)
    k.seam([(1.5 * s, tip + 6 * s), (hw * 0.45, body0 * 0.6), (hw * 0.45, body0 + 2)], mirror=True, w=0.55)
    return k, [(0.0, tip)]


def comp_bloom(W, H, hp, s):
    k = LKit(W, H, 33, s)
    top = H * (0.05 if hp else 0.12)
    bot = H - (1 if hp else 5)
    hw = W * (0.44 if hp else 0.34)
    k.plate([(0, bot), (hw, bot - 3), (hw, top + 6), (hw - 4, top), (0, top)], "metal_m", mirror=True, grad=0.3)
    k.box(-hw * 0.62, top + 2, hw * 0.62, bot - 4, GRAPH, r=0.5, bevel=False)
    tw = hw * 0.55
    k.plate([(0, top + 2.5), (tw, top + tw * 1.6), (tw * 0.8, bot - 8), (0, bot - 6)], "metal_l", mirror=True, ink=0.4)
    k.crystal(0, top + tw * 1.4, tw * 0.55, tw * 1.0, color=VIOLET)
    k.plate([(tw * 0.25, bot - 22 * s), (tw * 0.85, bot - 20 * s), (tw * 0.80, bot - 12 * s), (tw * 0.25, bot - 14 * s)],
            NAVY, mirror=True, bevel=False)
    k.seam([(hw * 0.8, top + 8), (hw * 0.8, bot - 6)], mirror=True)
    mounts(k, bot - 2, hw, s)
    return k, [(0.0, top + 2)]


def comp_sforzando(W, H, hp, s, untuned=False):
    """Long twin-rail railgun on an irregular angular housing; the body sits on the sprite centre (the slot)."""
    k = LKit(W, H, 41, s)
    cy = H / 2.0
    hw = W * 0.40
    body0, body1 = cy - 15, cy + 15
    housing(k, body0, body1, hw, seams=not untuned, navy=not untuned)
    mounts(k, body1 - 3, hw, s)
    rail = "metal_m" if untuned else "metal_l"
    g = 1.4
    k.plate([(g, 2.0), (g + 2.6, 4.5), (g + 2.6, body0 + 2), (g, body0 + 2)], rail, mirror=True)
    for f in (0.18, 0.42, 0.66, 0.88):
        y = 2.0 + (body0 - 2.0) * f
        k.plate([(g - 0.3, y), (g + 3.4, y + 0.8), (g + 3.4, y + 2.4), (g - 0.3, y + 2.0)], GUN, mirror=True,
                bevel=False)
    k.box(-g + 0.2, 3.0, g - 0.2, body0 + 2, GRAPH, r=0.2, bevel=False)
    if untuned:
        k.seam([(0, body0 - 8), (0, body0 + 1)], w=0.5)
    else:
        k.seam([(0, 4.0), (0, body0 + 1)], w=0.7)
        k.crystal(0, body0 + 6, 2.2, 4.0)
    k.plate([(hw * 0.6, cy + 2), (hw * 1.05, cy + 6), (hw * 0.95, body1 - 1), (hw * 0.55, body1 - 3)],
            "metal_l", mirror=True)
    return k, [(0.0, 2.0)]


WEAPONS = {
    # id: (size, composer, turret size override (W,H) or None, hardpoint override)
    "rsl_chime": ("SMALL", comp_chime, None, None),
    "rsl_pizzicato": ("SMALL", comp_pizzicato, None, None),
    "rsl_shardcaster": ("SMALL", comp_shard, None, None),
    "rsl_tuningspike": ("SMALL", lambda W, H, hp, s: comp_spike_rack(W, H, hp, s, 2), None, None),
    "rsl_tuningspike_pod": ("MEDIUM", lambda W, H, hp, s: comp_spike_rack(W, H, hp, s, 4), None, None),
    "rsl_lattice_lance": ("MEDIUM", comp_lattice_lance, None, None),
    "rsl_flechette": ("MEDIUM", comp_flechette, None, None),
    "rsl_arpeggio": ("MEDIUM", comp_arpeggio, None, None),
    "rsl_cantus": ("MEDIUM", comp_cantus, None, None),
    "rsl_harmonic_driver": ("LARGE", comp_harmonic, None, None),
    "rsl_harmonic_spinal": ("LARGE", lambda W, H, hp, s: comp_harmonic(W, H, hp, s, spinal=True), (36, 40), (36, 40)),
    "rsl_sostenuto": ("LARGE", comp_sostenuto, None, None),
    "rsl_bloom": ("LARGE", comp_bloom, None, None),
    "rsl_sforzando": ("LARGE", comp_sforzando, (40, 116), (40, 116)),
    "rsl_sforzando_untuned": ("LARGE", lambda W, H, hp, s: comp_sforzando(W, H, hp, s, untuned=True), (40, 116),
                              (40, 116)),
}


def glow_image(k):
    """The _glow sprite: emissive pixels only, near-white teal (the .wpn glowColor tints it in game)."""
    H, W = k.H, k.W
    e = (k.emi * k.a).reshape(H, SS, W, SS).mean(axis=(1, 3))
    rgb = (k.rgb * (k.emi * k.a)[..., None]).reshape(H, SS, W, SS, 3).mean(axis=(1, 3)) / np.maximum(e, 1e-4)[..., None]
    rgb = np.clip(rgb * 0.55 + 0.45, 0, 1)
    out = np.concatenate([rgb, np.clip(e * 1.2, 0, 1)[..., None]], axis=2)
    return hullgen.alpha_bleed(Image.fromarray((out * 255 + 0.5).astype(np.uint8), "RGBA"))


def offsets(muzzles, H):
    offs, angs = [], []
    for x, y in muzzles:
        offs += [round(H / 2.0 - y, 1), round(-x, 1)]
        angs.append(0)
    return offs, angs


# ======================================================================================== missiles / projectiles
def missile_spike():
    k = LKit(8, 26, 51, 0.8)
    k.plate([(0, 0.5), (2.6, 6), (2.0, 21), (0, 23)], "metal_l", mirror=True)
    k.plate([(2.0, 15), (3.6, 21), (3.4, 25), (1.6, 23)], NAVY, mirror=True, bevel=False)
    k.crystal(0, 5.0, 1.2, 3.6)
    k.seam([(0, 9), (0, 19)], w=0.5)
    return k


def missile_bloom():
    k = LKit(16, 40, 52, 1.2)
    k.plate([(0, 0.5), (5.0, 7), (5.4, 30), (3.5, 36), (0, 37)], "metal_l", mirror=True)
    k.crystal(0, 9.0, 3.4, 7.0, color=VIOLET)
    k.plate([(4.8, 24), (7.6, 32), (7.4, 39), (4.0, 35)], NAVY, mirror=True, bevel=False)
    k.seam([(2.0, 18), (2.0, 32)], mirror=True)
    k.box(-2.0, 34, 2.0, 39, GRAPH, r=0.3, bevel=False)
    return k


def proj_shard():
    k = LKit(6, 14, 53, 0.6)
    k.crystal(0, 7, 2.4, 6.4)
    return k


def save(im, rel):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    im.save(p)
    return rel


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview")
    a = ap.parse_args()
    data, shots = {}, []
    for wid, (size, comp, tsz, hsz) in WEAPONS.items():
        s = wg.SCALE[size]
        entry = {}
        for mount, key in (("TURRET", "turret"), ("HARDPOINT", "hardpoint")):
            if mount == "TURRET":
                W, H = tsz or (wg.TURRET[size], wg.TURRET[size])
            else:
                W, H = hsz or wg.HARDPOINT[size]
            W = wg.even(W)
            k, muz = comp(W, H, mount == "HARDPOINT", s)
            im = k.finish()
            rel = save(im, "graphics/rsl/weapons/%s_%s.png" % (wid, key))
            grel = save(glow_image(k), "graphics/rsl/weapons/%s_%s_glow.png" % (wid, key))
            offs, angs = offsets(muz, H)
            entry[key] = {"sprite": rel, "glow": grel, "offsets": offs, "angles": angs, "size": [W, H]}
            shots.append(im)
        data[wid] = entry
        print("%-24s turret %s  hardpoint %s  barrels %d" % (wid, entry["turret"]["size"], entry["hardpoint"]["size"],
                                                           len(entry["turret"]["angles"])))
    for name, fn in (("rsl_tuningspike_msl", missile_spike), ("rsl_bloom_msl", missile_bloom),
                     ("rsl_shard_proj", proj_shard)):
        k = fn()
        im = k.finish()
        rel = save(im, "graphics/rsl/missiles/%s.png" % name)
        data[name] = {"sprite": rel, "size": [k.W, k.H]}
        shots.append(im)
    with open(os.path.join(ROOT, "art_src", "gen", "weapon_offsets.json"), "w", newline="\n") as f:
        json.dump(data, f, indent=1)
    if a.preview:
        sc = 4
        Wt = sum(i.width * sc + 12 for i in shots) + 12
        Ht = max(i.height * sc for i in shots) + 24
        sheet = Image.new("RGBA", (Wt, Ht), (14, 16, 22, 255))
        x = 12
        for i in shots:
            sheet.alpha_composite(i.resize((i.width * sc, i.height * sc), Image.NEAREST), (x, 12))
            x += i.width * sc + 12
        sheet.save(a.preview)
        print("preview", a.preview)


if __name__ == "__main__":
    main()
