"""Resonance Lattice parts kit. Runs inside Blender 4.2 (bpy + bmesh).

Coordinates: 1 Blender unit = 1 final sprite pixel. Spec points are (x, y) with x = lateral offset from the centre
line (+ = image right) and y = distance from the top edge, same as hullgen specs. Blender X = x, Y = H - y, Z = up
(towards the camera). Half outlines are authored for x >= 0 and mirrored.
"""
import math
import random

import bmesh
import bpy
from mathutils import Vector

# ------------------------------------------------------------------ palette (linear-ish albedo picked by eye)
PALETTE = {
    "ivory": (0.70, 0.67, 0.60),
    "ivory2": (0.58, 0.57, 0.54),
    "slate": (0.20, 0.21, 0.23),
    "graphite": (0.040, 0.043, 0.050),
    "steel": (0.16, 0.165, 0.175),
    "accent": (0.05, 0.11, 0.24),       # ink-blue markings
    "seam": (0.25, 0.85, 0.80),         # teal lattice glow
    "seam2": (0.55, 0.38, 0.95),        # violet end of the gradient
    "crystal": (0.45, 0.95, 0.92),
    "nozzle": (0.02, 0.02, 0.025),
}
# material pass_index values (read back by finish.py from the IndexMA pass)
MAT_INDEX = {"graphite": 1, "steel": 1, "ivory": 2, "ivory2": 2, "slate": 7, "seam": 3, "seam2": 3, "crystal": 4,
             "accent": 5, "nozzle": 6}
EMISSIVE = {"seam": 6.0, "seam2": 6.0, "crystal": 9.0}

_mats = {}


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _mats.clear()


def material(name):
    if name in _mats:
        return _mats[name]
    m = bpy.data.materials.new("rsl_" + name)
    m.use_nodes = True
    m.pass_index = MAT_INDEX[name]
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    col = PALETTE[name]
    rough = {"ivory": 0.42, "ivory2": 0.5, "slate": 0.5, "graphite": 0.65, "steel": 0.45, "accent": 0.5}.get(name, 0.5)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = 0.6 if name == "steel" else 0.0
    if name in EMISSIVE:
        bsdf.inputs["Base Color"].default_value = (*[c * 0.4 for c in col], 1)
        bsdf.inputs["Emission Color"].default_value = (*col, 1)
        bsdf.inputs["Emission Strength"].default_value = EMISSIVE[name]
    else:
        # subtle object-space noise so large plates are not flat; per-object random tint for plate variety
        tc = nt.nodes.new("ShaderNodeTexCoord")
        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 0.12 if name.startswith("ivory") else 0.6
        noise.inputs["Detail"].default_value = 4.0
        info = nt.nodes.new("ShaderNodeObjectInfo")
        mix = nt.nodes.new("ShaderNodeMath")
        mix.operation = "MULTIPLY_ADD"
        mix.inputs[1].default_value = 0.10 if name.startswith("ivory") else 0.5
        nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])
        nt.links.new(noise.outputs["Fac"], mix.inputs[0])
        rnd = nt.nodes.new("ShaderNodeMath")
        rnd.operation = "MULTIPLY_ADD"
        nt.links.new(info.outputs["Random"], rnd.inputs[0])
        rnd.inputs[1].default_value = 0.08 if name.startswith("ivory") else 0.0
        rnd.inputs[2].default_value = 0.91 - (0.05 if name.startswith("ivory") else 0.25)
        nt.links.new(rnd.outputs[0], mix.inputs[2])
        rgb = nt.nodes.new("ShaderNodeRGB")
        rgb.outputs[0].default_value = (*col, 1)
        mul = nt.nodes.new("ShaderNodeMix")
        mul.data_type = "RGBA"
        mul.blend_type = "MULTIPLY"
        mul.inputs["Factor"].default_value = 1.0
        nt.links.new(rgb.outputs[0], mul.inputs["A"])
        nt.links.new(mix.outputs[0], mul.inputs["B"])
        nt.links.new(mul.outputs["Result"], bsdf.inputs["Base Color"])
    _mats[name] = m
    return m


# ------------------------------------------------------------------ geometry helpers
class Ctx:
    def __init__(self, W, H):
        self.W, self.H = W, H

    def v(self, x, y, z=0.0):
        return Vector((x, self.H - y, z))


def mirror_poly(half):
    """Half outline (x >= 0, ordered top->bottom down the right side) -> full closed outline."""
    pts = [tuple(p) for p in half]
    left = [(-x, y) for x, y in reversed(pts) if abs(x) > 1e-6]
    right = pts
    # drop duplicated centre-line points at the joins
    return right + left


def full_polys(entry):
    """A layer entry may give 'half' (mirrored), 'poly' (as is), and/or 'sym_poly' (poly + its mirror)."""
    out = []
    if "half" in entry:
        out.append(mirror_poly(entry["half"]))
    if "poly" in entry:
        out.append([tuple(p) for p in entry["poly"]])
    if "sym_poly" in entry:
        p = [tuple(q) for q in entry["sym_poly"]]
        out.append(p)
        out.append([(-x, y) for x, y in reversed(p)])
    return out


def point_in_poly(x, y, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi:
            inside = not inside
        j = i
    return inside


def dist_to_poly_edge(x, y, poly):
    best = 1e9
    n = len(poly)
    for i in range(n):
        ax, ay = poly[i]
        bx, by = poly[(i + 1) % n]
        dx, dy = bx - ax, by - ay
        L = dx * dx + dy * dy
        t = 0 if L == 0 else max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / L))
        px, py = ax + t * dx, ay + t * dy
        best = min(best, math.hypot(x - px, y - py))
    return best


def link(obj, coll=None):
    (coll or bpy.context.scene.collection).objects.link(obj)
    return obj


def mesh_obj(name, bm, mat):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    if mat is not None:
        ob.data.materials.append(material(mat) if isinstance(mat, str) else mat)
    return link(ob)


def bake(ob):
    """Apply modifiers / convert curves: replace ob by a plain mesh object with the evaluated geometry."""
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    new = bpy.data.objects.new(ob.name, me)
    new.matrix_world = ob.matrix_world
    if not me.materials and ob.material_slots:
        for s in ob.material_slots:
            me.materials.append(s.material)
    link(new)
    old_data = ob.data
    bpy.data.objects.remove(ob)
    if isinstance(old_data, bpy.types.Curve):
        bpy.data.curves.remove(old_data)
    return new


def slab(ctx, name, polys, z0, z1, bevel, mat, holes=(), inset=0.0):
    """Extruded, bevelled 2D shape (curve fill handles concave outlines and holes). inset shrinks the outline."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "2D"
    cu.fill_mode = "BOTH"
    th = z1 - z0
    bevel = min(bevel, th * 0.45)
    cu.bevel_depth = bevel
    cu.bevel_resolution = 2
    cu.offset = -bevel - inset
    cu.extrude = max(0.0, th / 2 - bevel)
    for poly in list(polys) + list(holes):
        sp = cu.splines.new("POLY")
        sp.points.add(len(poly) - 1)
        for i, (x, y) in enumerate(poly):
            v = ctx.v(x, y)
            sp.points[i].co = (v.x, v.y, 0.0, 1.0)
        sp.use_cyclic_u = True
    ob = bpy.data.objects.new(name, cu)
    ob.location.z = (z0 + z1) / 2
    ob.data.materials.append(material(mat))
    link(ob)
    ob = bake(ob)
    # curve meshes come out as separate caps + walls; weld them so EXACT booleans see a closed solid
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.002)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    return ob


def offset_polyline(pts, w):
    """Closed outline of a polyline thickened to width w (miter joins, square ends)."""
    P = [Vector((x, y)) for x, y in pts]
    if len(P) < 2:
        return []
    h = w / 2
    left, right = [], []
    for i, p in enumerate(P):
        if i == 0:
            d = (P[1] - P[0]).normalized()
            n = Vector((-d.y, d.x))
            p = p - d * h * 0.2
            left.append(p + n * h)
            right.append(p - n * h)
        elif i == len(P) - 1:
            d = (P[-1] - P[-2]).normalized()
            n = Vector((-d.y, d.x))
            p = p + d * h * 0.2
            left.append(p + n * h)
            right.append(p - n * h)
        else:
            d1 = (P[i] - P[i - 1]).normalized()
            d2 = (P[i + 1] - P[i]).normalized()
            n1 = Vector((-d1.y, d1.x))
            n2 = Vector((-d2.y, d2.x))
            m = (n1 + n2)
            if m.length < 1e-6:
                m = n1
            m.normalize()
            k = h / max(0.3, m.dot(n1))
            left.append(p + m * k)
            right.append(p - m * k)
    return [(v.x, v.y) for v in left + list(reversed(right))]


def prism(bm, ctx, outline, z0, z1):
    """Add a closed prism over a 2D outline (spec coords) to bm."""
    bot = [bm.verts.new(ctx.v(x, y, z0)) for x, y in outline]
    top = [bm.verts.new(ctx.v(x, y, z1)) for x, y in outline]
    n = len(outline)
    try:
        bm.faces.new(list(reversed(bot)))
        bm.faces.new(top)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((bot[i], bot[j], top[j], top[i]))
    except ValueError:
        pass


def expand_sym(items):
    out = []
    for it in items:
        out.append(it)
        if it.get("sym"):
            m = dict(it)
            m.pop("sym")
            if "pts" in m:
                m["pts"] = [(-x, y) for x, y in m["pts"]]
            if "pos" in m:
                m["pos"] = (-m["pos"][0], m["pos"][1])
                if "angle" in m:
                    m["angle"] = -m["angle"]
            out.append(m)
    return out


def cut(ctx, ob, cuts, ztop):
    """Boolean-subtract thickened polylines (panel lines / seam grooves) from ob."""
    if not cuts:
        return ob
    bm = bmesh.new()
    for c in cuts:
        depth = c.get("depth", 0.7)
        prism(bm, ctx, offset_polyline(c["pts"], c.get("w", 0.8)), ztop - depth, ztop + 2)
    cutter = mesh_obj(ob.name + "_cut", bm, None)
    mod = ob.modifiers.new("cut", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    mod.use_self = True
    mod.object = cutter
    new = bake(ob)
    bpy.data.objects.remove(cutter)
    return new


def strips(ctx, name, cuts, mat):
    """Emissive strips seated in glow grooves."""
    bm = bmesh.new()
    for c in cuts:
        w = c.get("w", 0.8) * 0.7
        z1 = c["_ztop"] - c.get("inset", 0.5)
        prism(bm, ctx, offset_polyline(c["pts"], w), z1 - 0.5, z1)
    return mesh_obj(name, bm, mat)


def separate_loose(ob):
    """Split a mesh into loose parts so each plate gets its own Object Info random tint."""
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.separate(type="LOOSE")
    bpy.ops.object.mode_set(mode="OBJECT")


# ------------------------------------------------------------------ surface queries
def top_z(x_bl, y_bl):
    """Height of the topmost surface at a point (samples a small cross so 1px grooves don't fool it)."""
    dg = bpy.context.evaluated_depsgraph_get()
    best = 0.0
    for dx, dy in ((0, 0), (0.6, 0), (-0.6, 0), (0, 0.6), (0, -0.6)):
        hit, loc, *_ = bpy.context.scene.ray_cast(dg, Vector((x_bl + dx, y_bl + dy, 200)), Vector((0, 0, -1)))
        if hit:
            best = max(best, loc.z)
    return best


# ------------------------------------------------------------------ greebles
def greebles(ctx, region_polys, z0, zmax, density, seed, exclude=()):
    """Dense machinery inside the region (mirrored). Items stay under zmax so plates cover them."""
    rng = random.Random(seed)
    bm_d, bm_s = bmesh.new(), bmesh.new()
    xs = [p[0] for poly in region_polys for p in poly]
    ys = [p[1] for poly in region_polys for p in poly]
    x1, y0, y1 = max(xs), min(ys), max(ys)
    area = max(1.0, x1 * (y1 - y0))
    n = int(area * density)
    hmax = max(0.3, zmax - z0)

    def inside(x, y, margin):
        ok = any(point_in_poly(x, y, p) and dist_to_poly_edge(x, y, p) > margin for p in region_polys)
        return ok and not any(point_in_poly(x, y, p) for p in exclude)

    for _ in range(n):
        x, y = rng.uniform(0, x1), rng.uniform(y0, y1)
        kind = rng.random()
        if kind < 0.34:  # box
            w, h = rng.uniform(0.8, 3.2), rng.uniform(0.8, 4.0)
            if not inside(x, y, max(w, h) / 2 + 0.3):
                continue
            hz = rng.uniform(0.25, 1.0) * hmax
            bm = bm_s if rng.random() < 0.3 else bm_d
            for sx in (1, -1):
                cx = sx * x
                prism(bm, ctx, [(cx - w / 2, y - h / 2), (cx + w / 2, y - h / 2), (cx + w / 2, y + h / 2),
                                (cx - w / 2, y + h / 2)], z0, z0 + hz)
        elif kind < 0.5:  # tank / cylinder end-on
            r = rng.uniform(0.6, 1.8)
            if not inside(x, y, r + 0.3):
                continue
            hz = rng.uniform(0.4, 1.0) * hmax
            for sx in (1, -1):
                ret = bmesh.ops.create_cone(bm_s, cap_ends=True, segments=12, radius1=r, radius2=r * 0.85,
                                            depth=hz)
                bmesh.ops.translate(bm_s, verts=ret["verts"], vec=ctx.v(sx * x, y, z0 + hz / 2))
        elif kind < 0.64:  # pipe run along y
            L = rng.uniform(4, 14)
            r = rng.uniform(0.35, 0.7)
            if not (inside(x, y - L / 2, r + 0.3) and inside(x, y + L / 2, r + 0.3)):
                continue
            for sx in (1, -1):
                ret = bmesh.ops.create_cone(bm_s, cap_ends=True, segments=8, radius1=r, radius2=r, depth=L)
                bmesh.ops.rotate(bm_s, verts=ret["verts"], cent=Vector((0, 0, 0)),
                                 matrix=__import__("mathutils").Matrix.Rotation(math.pi / 2, 3, "X"))
                bmesh.ops.translate(bm_s, verts=ret["verts"], vec=ctx.v(sx * x, y, z0 + min(hmax, r * 1.6)))
        elif kind < 0.8:  # actuator: stacked cylinders, narrowing upwards
            r = rng.uniform(0.9, 1.7)
            if not inside(x, y, r + 0.3):
                continue
            for sx in (1, -1):
                zz = z0
                for k, f in enumerate((1.0, 0.72, 0.42)):
                    hz = hmax * (0.45, 0.3, 0.25)[k]
                    ret = bmesh.ops.create_cone(bm_s if k % 2 else bm_d, cap_ends=True, segments=12, radius1=r * f,
                                                radius2=r * f, depth=hz)
                    bmesh.ops.translate(bm_s if k % 2 else bm_d, verts=ret["verts"], vec=ctx.v(sx * x, y, zz + hz / 2))
                    zz += hz
        elif kind < 0.92:  # ribbed block
            w, h = rng.uniform(2.0, 3.6), rng.uniform(2.4, 4.4)
            if not inside(x, y, max(w, h) / 2 + 0.3):
                continue
            for sx in (1, -1):
                cx = sx * x
                prism(bm_d, ctx, [(cx - w / 2, y - h / 2), (cx + w / 2, y - h / 2), (cx + w / 2, y + h / 2),
                                  (cx - w / 2, y + h / 2)], z0, z0 + 0.5 * hmax)
                yy = y - h / 2 + 0.4
                while yy < y + h / 2 - 0.5:
                    prism(bm_s, ctx, [(cx - w / 2 + 0.2, yy), (cx + w / 2 - 0.2, yy), (cx + w / 2 - 0.2, yy + 0.45),
                                      (cx - w / 2 + 0.2, yy + 0.45)], z0, z0 + 0.85 * hmax)
                    yy += 0.95
        else:  # vent bank
            k = rng.randint(3, 6)
            w = rng.uniform(1.5, 3.5)
            if not (inside(x, y, w) and inside(x, y + k * 1.1, w)):
                continue
            for sx in (1, -1):
                for i in range(k):
                    yy = y + i * 1.1
                    cx = sx * x
                    prism(bm_d, ctx, [(cx - w / 2, yy), (cx + w / 2, yy), (cx + w / 2, yy + 0.6), (cx - w / 2, yy + 0.6)],
                          z0, z0 + 0.5 * hmax)
    mesh_obj("greeble_dark", bm_d, "graphite")
    mesh_obj("greeble_steel", bm_s, "steel")


# ------------------------------------------------------------------ details placed on the surface
def ring(bm, c, r_out, r_in, z0, z1, seg=24):
    ret = bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r_out, radius2=r_out, depth=z1 - z0)
    bmesh.ops.translate(bm, verts=ret["verts"], vec=Vector((c.x, c.y, (z0 + z1) / 2)))
    ret = bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r_in, radius2=r_in, depth=z1 - z0 + 0.2)
    return ret


def disc(bm, c, r, z0, z1, seg=20):
    ret = bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=z1 - z0)
    bmesh.ops.translate(bm, verts=ret["verts"], vec=Vector((c.x, c.y, (z0 + z1) / 2)))


SOCKET_R = {"SMALL": 5.0, "MEDIUM": 8.0, "LARGE": 12.0}


def sockets(ctx, slots):
    """Turret rings and hardpoint cradles at weapon slots (after the hull exists, so we can raycast)."""
    bm_ring, bm_dark = bmesh.new(), bmesh.new()
    for s in expand_sym(slots):
        if s.get("mount") == "HIDDEN" or s.get("type") == "DECORATIVE" or s.get("no_socket"):
            continue
        x, y = s["pos"]
        c = ctx.v(x, y)
        z = top_z(c.x, c.y)
        r = SOCKET_R.get(s.get("size", "SMALL"), 5.0)
        if s.get("mount", "TURRET") == "TURRET":
            disc(bm_ring, c, r * 0.92, z - 0.6, z + 0.35, seg=28)
            disc(bm_dark, c, r * 0.72, z + 0.35, z + 0.45, seg=28)
            disc(bm_ring, c, r * 0.30, z + 0.45, z + 0.75, seg=16)
        else:  # hardpoint: recessed cradle, long axis forward
            w, h = r * 0.9, r * 1.6
            prism(bm_dark, ctx, [(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)],
                  z - 0.8, z + 0.15)
    mesh_obj("socket_ring", bm_ring, "steel")
    mesh_obj("socket_dark", bm_dark, "nozzle")


def nozzles(ctx, engines, hull_size):
    from_defaults = {"FRIGATE": 8, "DESTROYER": 12, "CRUISER": 16, "CAPITAL_SHIP": 16}
    bm_n, bm_r = bmesh.new(), bmesh.new()
    for e in expand_sym(engines):
        x, y = e["pos"]
        w = e.get("width", from_defaults.get(hull_size, 10))
        d = e.get("depth", max(3.0, w * 0.5))
        c = ctx.v(x, y - d / 2)
        z = top_z(c.x, c.y)
        hw = w / 2
        prism(bm_r, ctx, [(x - hw - 0.8, y - d - 0.6), (x + hw + 0.8, y - d - 0.6), (x + hw + 0.8, y), (x - hw - 0.8, y)],
              z - 1.0, z + 0.4)
        prism(bm_n, ctx, [(x - hw, y - d), (x + hw, y - d), (x + hw, y + 0.5), (x - hw, y + 0.5)], z + 0.1, z + 0.5)
    mesh_obj("nozzle_rim", bm_r, "steel")
    mesh_obj("nozzle", bm_n, "nozzle")


def details(ctx, items):
    bms = {}

    def bm_for(mat):
        if mat not in bms:
            bms[mat] = bmesh.new()
        return bms[mat]

    for it in expand_sym(items):
        t = it["type"]
        if t == "hatch":
            x, y = it["pos"]
            c = ctx.v(x, y)
            z = top_z(c.x, c.y)
            r = it.get("r", 2.0)
            disc(bm_for("steel"), c, r, z - 0.3, z + 0.25)
            disc(bm_for("graphite"), c, r * 0.6, z + 0.25, z + 0.35)
        elif t == "light":
            x, y = it["pos"]
            c = ctx.v(x, y)
            z = top_z(c.x, c.y)
            disc(bm_for(it.get("mat", "seam")), c, it.get("r", 0.7), z - 0.2, z + 0.3, seg=12)
        elif t == "vent":
            x, y = it["pos"]
            w, n, step = it.get("w", 4.0), it.get("n", 4), it.get("step", 1.2)
            c = ctx.v(x, y)
            z = top_z(c.x, c.y)
            for i in range(n):
                yy = y + i * step
                prism(bm_for("graphite"), ctx, [(x - w / 2, yy), (x + w / 2, yy), (x + w / 2, yy + step * 0.5),
                                                (x - w / 2, yy + step * 0.5)], z - 0.4, z + 0.12)
        elif t in ("mark", "line"):
            # flat decal polyline (ink-blue markings) or raised trim line
            pts = it["pts"]
            c = ctx.v(*pts[0])
            z = top_z(c.x, c.y)
            mat = it.get("mat", "accent")
            prism(bm_for(mat), ctx, offset_polyline(pts, it.get("w", 0.8)), z - 0.2, z + it.get("h", 0.06))
        elif t == "block":
            # raised rectangular module (e.g. a sensor housing) on the surface
            x, y = it["pos"]
            w, h = it["size"]
            c = ctx.v(x, y)
            z = top_z(c.x, c.y)
            prism(bm_for(it.get("mat", "steel")), ctx,
                  [(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)],
                  z - 0.3, z + it.get("h", 0.8))
        elif t == "crystal":
            x, y = it["pos"]
            c = ctx.v(x, y)
            z = top_z(c.x, c.y)
            r = it.get("r", 2.0)
            ret = bmesh.ops.create_cone(bm_for("crystal"), cap_ends=True, segments=6, radius1=r, radius2=r * 0.55,
                                        depth=it.get("h", 1.2))
            bmesh.ops.translate(bm_for("crystal"), verts=ret["verts"], vec=Vector((c.x, c.y, z + 0.3)))
        elif t == "dome":
            x, y = it["pos"]
            c = ctx.v(x, y)
            z = top_z(c.x, c.y)
            r = it.get("r", 1.5)
            ret = bmesh.ops.create_uvsphere(bm_for(it.get("mat", "steel")), u_segments=16, v_segments=8, radius=r)
            bmesh.ops.scale(bm_for(it.get("mat", "steel")), verts=ret["verts"], vec=Vector((1, 1, 0.45)))
            bmesh.ops.translate(bm_for(it.get("mat", "steel")), verts=ret["verts"], vec=Vector((c.x, c.y, z)))
        elif t == "conduit":
            # lattice conduit: dark channel with a glowing core, laid over whatever it crosses (max height on path)
            pts = it["pts"]
            z = path_top(ctx, pts)
            w = it.get("w", 1.2)
            prism(bm_for("nozzle"), ctx, offset_polyline(pts, w + 0.9), z - 0.3, z + 0.12)
            prism(bm_for(it.get("mat", "seam")), ctx, offset_polyline(pts, w), z + 0.05, z + 0.22)
        elif t == "node":
            # conduit terminal: steel collar, dark ring, glowing core (diamond if shape == "diamond")
            x, y = it["pos"]
            c = ctx.v(x, y)
            z = top_z(c.x, c.y)
            r = it.get("r", 1.6)
            disc(bm_for("steel"), c, r, z - 0.3, z + 0.3, seg=20)
            disc(bm_for("nozzle"), c, r * 0.72, z + 0.3, z + 0.38, seg=20)
            if it.get("shape") == "diamond":
                k = r * 0.62
                prism(bm_for("crystal"), ctx, [(x, y - k), (x + k * 0.75, y), (x, y + k), (x - k * 0.75, y)],
                      z + 0.3, z + 0.6)
            else:
                disc(bm_for("crystal"), c, r * 0.48, z + 0.3, z + 0.6, seg=14)
        elif t == "cell":
            # resonator cell: dark recessed frame holding n glowing bars; v > 0 bends the bars into chevrons
            x, y = it["pos"]
            w, h = it["size"]
            n = it.get("n", 4)
            v = it.get("v", 0.0)
            c = ctx.v(x, y)
            z = max(top_z(ctx.v(x + dx, y + dy).x, ctx.v(x + dx, y + dy).y)
                    for dx in (-w / 2, 0, w / 2) for dy in (-h / 2, 0, h / 2))
            sl = it.get("slant", 0.0)  # x shift of the bottom edge (parallelogram cells)
            frame = [(x - w / 2 - 0.5, y - h / 2 - 0.5), (x + w / 2 + 0.5, y - h / 2 - 0.5),
                     (x + w / 2 + 0.5 + sl, y + h / 2 + 0.5), (x - w / 2 - 0.5 + sl, y + h / 2 + 0.5)]
            prism(bm_for("steel"), ctx, frame, z - 0.3, z + 0.35)
            inner = [(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2 + sl, y + h / 2),
                     (x - w / 2 + sl, y + h / 2)]
            prism(bm_for("nozzle"), ctx, inner, z + 0.3, z + 0.4)
            pitch = h / n
            bw = pitch * it.get("fill", 0.55)
            for i in range(n):
                yy = y - h / 2 + pitch * (i + 0.5)
                f = (yy - (y - h / 2)) / h
                ox = sl * f
                xl, xr = x - w / 2 + 0.35 + ox, x + w / 2 - 0.35 + ox
                bar = [(xl, yy + v), ((xl + xr) / 2, yy), (xr, yy + v)] if v else [(xl, yy), (xr, yy)]
                prism(bm_for(it.get("mat", "seam")), ctx, offset_polyline(bar, bw), z + 0.35, z + 0.55)
    for mat, bm in bms.items():
        mesh_obj("detail_" + mat, bm, mat)


def path_top(ctx, pts):
    """Highest surface along a polyline (sampled every ~1 px)."""
    best = 0.0
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(bx - ax, by - ay)))
        for i in range(n + 1):
            t = i / n
            c = ctx.v(ax + (bx - ax) * t, ay + (by - ay) * t)
            best = max(best, top_z(c.x, c.y))
    return best


def surface_details(ctx, region_polys, density, seed, mats=("rsl_ivory", "rsl_ivory2", "rsl_slate")):
    """Random small details on flat plate areas: recessed slots, tiny hatches, indicator lights, trim ticks."""
    rng = random.Random(seed)
    xs = [p[0] for poly in region_polys for p in poly]
    ys = [p[1] for poly in region_polys for p in poly]
    x1, y0, y1 = max(xs), min(ys), max(ys)
    n = int(max(1.0, x1 * (y1 - y0)) * density)
    dg = bpy.context.evaluated_depsgraph_get()
    sc = bpy.context.scene
    bms = {}

    def bm_for(m):
        if m not in bms:
            bms[m] = bmesh.new()
        return bms[m]

    def probe(x, y):
        c = ctx.v(x, y)
        hit, loc, nrm, idx, ob, mtx = sc.ray_cast(dg, Vector((c.x, c.y, 200)), Vector((0, 0, -1)))
        if not hit or not ob.material_slots or ob.material_slots[0].material is None:
            return None, None
        return loc.z, ob.material_slots[0].material.name

    placed = []
    for _ in range(n):
        x, y = rng.uniform(0.8, x1), rng.uniform(y0, y1)
        kind = rng.random()
        r = 1.6 if kind < 0.5 else 1.1
        z, m = probe(x, y)
        if z is None or not m.startswith(mats):
            continue
        ok = True
        for dx, dy in ((r, 0), (-r, 0), (0, r), (0, -r), (r, r), (-r, -r), (r, -r), (-r, r)):
            z2, m2 = probe(x + dx, y + dy)
            if z2 is None or abs(z2 - z) > 0.05:
                ok = False
                break
        if not ok or any(abs(px - x) < 2.4 and abs(py - y) < 2.4 for px, py in placed):
            continue
        placed.append((x, y))
        for sx in (1, -1):
            cx = sx * x
            if kind < 0.3:      # recessed slot
                w, h = (rng.choice([0.8, 1.0]), rng.choice([1.8, 2.4])) if rng.random() < 0.6 else (2.0, 0.8)
                prism(bm_for("graphite"), ctx, [(cx - w / 2, y - h / 2), (cx + w / 2, y - h / 2),
                                                (cx + w / 2, y + h / 2), (cx - w / 2, y + h / 2)], z - 0.5, z + 0.05)
            elif kind < 0.5:    # small raised box module
                w, h = rng.uniform(1.2, 2.2), rng.uniform(1.2, 2.6)
                prism(bm_for("slate"), ctx, [(cx - w / 2, y - h / 2), (cx + w / 2, y - h / 2),
                                             (cx + w / 2, y + h / 2), (cx - w / 2, y + h / 2)], z - 0.2, z + 0.45)
            elif kind < 0.7:    # tiny hatch
                c = ctx.v(cx, y)
                disc(bm_for("steel"), c, 0.85, z - 0.2, z + 0.2, seg=12)
            elif kind < 0.8:    # indicator light
                c = ctx.v(cx, y)
                disc(bm_for("seam"), c, 0.45, z - 0.2, z + 0.15, seg=8)
            else:               # trim tick
                L = rng.uniform(1.5, 3.0)
                prism(bm_for("accent"), ctx, offset_polyline([(cx, y - L / 2), (cx, y + L / 2)], 0.5), z - 0.2, z + 0.05)
    for m, bm in bms.items():
        mesh_obj("sdetail_" + m, bm, m)


def auto_cuts(polys, spacing, seed, y_from=None, y_to=None):
    """Chevron / straight panel lines across a layer, every ~spacing px (mirrored by construction)."""
    rng = random.Random(seed)
    xs = [abs(p[0]) for poly in polys for p in poly]
    ys = [p[1] for poly in polys for p in poly]
    xm = max(xs) + 2
    y = (y_from if y_from is not None else min(ys)) + spacing * rng.uniform(0.6, 1.0)
    end = y_to if y_to is not None else max(ys)
    out = []
    while y < end - 2:
        d = rng.choice([-2.5, -1.5, 0, 0, 1.5, 2.5])
        out.append({"pts": [(-xm, y + d), (0, y), (xm, y + d)], "w": 0.55, "depth": 0.45})
        y += spacing * rng.uniform(0.7, 1.3)
    return out
