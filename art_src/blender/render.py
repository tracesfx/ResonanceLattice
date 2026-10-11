"""Build a hull (or deco part) from a spec and render top-down passes at 4x.

blender -b --factory-startup -P render.py -- <spec.json> <out_dir> [--samples N] [--blend]

Writes <out_dir>/{color,emit,normal,height,matid}.png (4x the spec size). finish.py turns them into the sprite.
"""
import json
import os
import sys
import time

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit  # noqa: E402

SS = 4
CAM_Z = 100.0
ZMAX = 16.0


_T = [time.time()]


def lap(what):
    now = time.time()
    print("RSL_T %-28s %6.1fs" % (what, now - _T[0]), flush=True)
    _T[0] = now


def build(spec):
    W, H = spec["size"]
    ctx = kit.Ctx(W, H)
    layer_polys = {}
    for L in spec.get("layers", []):
        polys = kit.full_polys(L)
        holes = []
        for hentry in L.get("holes", []):
            holes += kit.full_polys(hentry)
        layer_polys[L["name"]] = polys
        z0, z1 = L["z"]
        ob = kit.slab(ctx, L["name"], polys, z0, z1, L.get("bevel", 0.5), L.get("mat", "ivory"), holes)
        cuts = kit.expand_sym(L.get("cuts", []))
        if L.get("auto_cuts"):
            ac = L["auto_cuts"]
            cuts += kit.auto_cuts(polys, ac.get("spacing", 9), ac.get("seed", 1), ac.get("y_from"), ac.get("y_to"))
        if cuts:
            ob = kit.cut(ctx, ob, cuts, z1)
            glow = [dict(c, _ztop=z1) for c in cuts if c.get("glow")]
            if glow:
                kit.strips(ctx, L["name"] + "_seam", glow, L.get("seam_mat", "seam"))
        if L.get("split", L.get("mat", "ivory").startswith("ivory")):
            kit.separate_loose(ob)
        # raised inner tiers: same outline shrunk by `inset`, stacked on top (sculpted plate look)
        ztop = z1
        for k, T in enumerate(L.get("tiers", [])):
            zt = ztop + T.get("dz", 0.6)
            tob = kit.slab(ctx, "%s_t%d" % (L["name"], k), polys, ztop - 0.2, zt, T.get("bevel", 0.35),
                           T.get("mat", L.get("mat", "ivory")), (), T.get("inset", 1.5))
            tcuts = kit.expand_sym(T.get("cuts", []))
            if tcuts:
                tob = kit.cut(ctx, tob, tcuts, zt)
                glow = [dict(c, _ztop=zt) for c in tcuts if c.get("glow")]
                if glow:
                    kit.strips(ctx, "%s_t%d_seam" % (L["name"], k), glow, "seam")
            ztop = zt
        lap("layer " + L["name"])
    g = spec.get("greebles")
    if g:
        region = []
        for name in g.get("layers", []):
            region += layer_polys[name]
        exclude = []
        for name in g.get("exclude_layers", []):
            exclude += layer_polys[name]
        kit.greebles(ctx, region, g["z0"], g["zmax"], g.get("density", 0.25), g.get("seed", 1), exclude)
        lap("greebles")
    bpy.context.view_layer.update()
    kit.nozzles(ctx, spec.get("engines", []), spec.get("hullSize", "FRIGATE"))
    lap("nozzles")
    kit.details(ctx, spec.get("details", []))
    lap("details")
    bpy.context.view_layer.update()
    sd = spec.get("surface_detail")
    if sd:
        region = []
        for name in sd.get("layers", list(layer_polys)):
            region += layer_polys[name]
        kit.surface_details(ctx, region, sd.get("density", 0.05), sd.get("seed", 1))
        bpy.context.view_layer.update()
        lap("surface_details")
    kit.sockets(ctx, spec.get("slots", []))
    lap("sockets")


def setup_render(spec, out_dir, samples):
    W, H = spec["size"]
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for dev_type in ("OPTIX", "CUDA"):
        try:
            prefs.compute_device_type = dev_type
            prefs.get_devices()
            gpus = [d for d in prefs.devices if d.type == dev_type]
            if gpus:
                for d in prefs.devices:
                    d.use = d.type == dev_type
                sc.cycles.device = "GPU"
                break
        except Exception:
            continue
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.cycles.pixel_filter_type = "BLACKMAN_HARRIS"
    sc.cycles.filter_width = 1.2
    sc.render.film_transparent = True
    sc.render.resolution_x = W * SS
    sc.render.resolution_y = H * SS
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"

    cam_data = bpy.data.cameras.new("cam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = max(W, H)
    cam_data.sensor_fit = "AUTO"
    cam_data.clip_end = 300
    cam = bpy.data.objects.new("cam", cam_data)
    cam.location = (0, H / 2, CAM_Z)
    sc.collection.objects.link(cam)
    sc.camera = cam

    # overhead light only: soft sun straight down + uniform sky (gives ambient occlusion in crevices)
    sun_data = bpy.data.lights.new("sun", "SUN")
    sun_data.energy = spec.get("render", {}).get("sun", 2.6)
    sun_data.angle = 0.6
    sun = bpy.data.objects.new("sun", sun_data)
    sc.collection.objects.link(sun)
    world = bpy.data.worlds.new("world")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (1, 1, 1, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = spec.get("render", {}).get("sky", 0.55)
    sc.world = world

    vl = sc.view_layers[0]
    vl.use_pass_z = True
    vl.use_pass_normal = True
    vl.use_pass_emit = True
    vl.use_pass_material_index = True

    sc.use_nodes = True
    nt = sc.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    rl = nt.nodes.new("CompositorNodeRLayers")
    comp = nt.nodes.new("CompositorNodeComposite")
    nt.links.new(rl.outputs["Image"], comp.inputs["Image"])
    fo = nt.nodes.new("CompositorNodeOutputFile")
    fo.base_path = out_dir
    fo.format.file_format = "PNG"
    fo.file_slots.clear()

    def slot(name, mode, depth="8"):
        fo.file_slots.new(name + "_")
        s = fo.file_slots[-1]
        s.use_node_format = False
        s.format.file_format = "PNG"
        s.format.color_mode = mode
        s.format.color_depth = depth
        return fo.inputs[-1]

    def map_range(sock, a, b, c, d):
        m = nt.nodes.new("CompositorNodeMapRange")
        m.use_clamp = True
        nt.links.new(sock, m.inputs["Value"])
        m.inputs["From Min"].default_value = a
        m.inputs["From Max"].default_value = b
        m.inputs["To Min"].default_value = c
        m.inputs["To Max"].default_value = d
        return m.outputs["Value"]

    # colour (with alpha)
    nt.links.new(rl.outputs["Image"], slot("color", "RGBA"))
    # emission, scaled into 0..1
    mul = nt.nodes.new("CompositorNodeMixRGB")
    mul.blend_type = "MULTIPLY"
    mul.inputs["Fac"].default_value = 1.0
    mul.inputs[2].default_value = (0.12, 0.12, 0.12, 1)
    nt.links.new(rl.outputs["Emit"], mul.inputs[1])
    nt.links.new(mul.outputs["Image"], slot("emit", "RGB"))
    # normals -1..1 -> 0..1 per channel
    sep = nt.nodes.new("CompositorNodeSeparateColor")
    nt.links.new(rl.outputs["Normal"], sep.inputs["Image"])
    comb = nt.nodes.new("CompositorNodeCombineColor")
    for i, ch in enumerate(("Red", "Green", "Blue")):
        nt.links.new(map_range(sep.outputs[ch], -1, 1, 0, 1), comb.inputs[ch])
    nt.links.new(comb.outputs["Image"], slot("normal", "RGB", "16"))
    # height above z=0 (16-bit grey)
    nt.links.new(map_range(rl.outputs["Depth"], CAM_Z - ZMAX, CAM_Z, 1, 0), slot("height", "BW", "16"))
    # material index /10
    nt.links.new(map_range(rl.outputs["IndexMA"], 0, 10, 0, 1), slot("matid", "BW"))


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    spec_path, out_dir = argv[0], os.path.abspath(argv[1])
    samples = int(argv[argv.index("--samples") + 1]) if "--samples" in argv else 96
    with open(spec_path, encoding="utf-8") as f:
        spec = json.load(f)
    os.makedirs(out_dir, exist_ok=True)
    kit.reset()
    build(spec)
    setup_render(spec, out_dir, samples)
    if "--blend" in argv:
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out_dir, spec["id"] + ".blend"))
    bpy.context.scene.frame_set(1)
    lap("setup")
    bpy.ops.render.render(write_still=False)
    lap("render")
    # File Output appends the frame number; strip it
    for name in ("color", "emit", "normal", "height", "matid"):
        src = os.path.join(out_dir, "%s_0001.png" % name)
        dst = os.path.join(out_dir, name + ".png")
        if os.path.exists(src):
            os.replace(src, dst)
    print("RSL_RENDER_OK", out_dir)


main()
