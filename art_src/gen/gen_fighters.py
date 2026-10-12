"""Generate the three Choir fighter specs (user, 2026-10-12: "rail mix"): interceptor, heavy fighter, bomber.

python art_src/gen/gen_fighters.py
./art_src/art.sh rsl_trill rsl_cadenza rsl_requiem
python art_src/preview.py art_src/review/fighters_v1.png rsl_trill rsl_cadenza rsl_requiem --peers thunder,broadsword,dagger --scale 1,3

Sizes follow the vanilla peers (Thunder 26x43, Broadsword 30x33, Dagger 26x34), a little larger because Lattice hulls
are built from more parts. House style at fighter scale: a sharp split silhouette (stepped needle or twin rails,
swept tips, a notch behind every wing), steel plates on a graphite frame, crisp navy caps on every extremity ("dipped
tips", the Virtuoso's approved livery), a nose glyph cell and a diamond core node feeding the guns/wings by conduits.
Weapon slots are HIDDEN (as vanilla fighters); the guns are fighter-only rail weapons defined in tools/gen_data.py.
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "specs")


def plate(name, mat, z, bevel=0.3, tier=None, **shape):
    d = {"name": name, "mat": mat, "z": z, "bevel": bevel}
    d.update(shape)
    if tier:
        d["tiers"] = [tier]
    return d


def navy(poly, sym=True):
    return {"type": "poly", "color": "navy", "poly": poly, "sym": sym}


def spec(sid, name, size, layers, details, slots, engines, livery, seed):
    return {"id": sid, "name": name, "hullSize": "FIGHTER", "size": size, "layers": layers,
            "greebles": {"layers": ["frame"], "z0": 2.0, "zmax": 2.7, "density": 0.6, "seed": seed},
            "surface_detail": {"layers": [l["name"] for l in layers if l["mat"] in ("ivory", "ivory2")],
                               "density": 0.05, "seed": seed + 1},
            "details": details, "slots": slots, "engines": engines, "ship": {"builtInMods": []}, "livery": livery}


# ------------------------------------------------------------------ Trill: interceptor (stepped needle + canards)
trill = spec("rsl_trill", "Trill", [28, 46], [
    plate("frame", "graphite", [0, 2.0], 0.4, half=[
        [0, 0], [1.4, 5], [2.4, 12], [3.4, 17], [9.6, 14.2], [9.0, 18.2], [4.7, 21.6], [5.3, 28], [13.6, 36.4],
        [12.8, 39.6], [7.4, 37.4], [6.6, 41], [4.6, 45], [0, 45]]),
    plate("nose", "ivory", [3.0, 4.4], half=[[0, 1.6], [1.2, 6], [2.0, 12], [2.8, 17.6], [0, 16]],
          tier={"inset": 0.6, "dz": 0.4, "mat": "ivory"}),
    plate("body", "ivory", [3.0, 4.6], half=[[0, 17.2], [2.9, 18.6], [4.1, 22], [4.5, 30], [3.8, 40], [0, 41.4]],
          tier={"inset": 0.8, "dz": 0.4, "mat": "slate"}),
    plate("canard", "ivory2", [2.8, 4.0], sym_poly=[[4.0, 18.6], [8.9, 15.4], [8.5, 17.9], [4.6, 20.8]]),
    plate("wing", "ivory2", [2.8, 4.2], sym_poly=[[5.5, 28.8], [12.8, 36.6], [12.3, 38.6], [7.3, 36.6], [5.3, 34]]),
], [
    {"type": "cell", "pos": [0, 9], "size": [1.6, 3.6], "n": 2, "v": 0.8, "fill": 0.5},
    {"type": "node", "pos": [0, 24], "r": 1.3, "shape": "diamond"},
    {"type": "conduit", "pos": [0, 0], "pts": [[0, 12.5], [0, 22.6]], "w": 0.45},
    {"type": "conduit", "pos": [0, 0], "pts": [[1.2, 25.2], [2.6, 27], [2.6, 31], [9.6, 36.2]], "w": 0.45, "sym": True},
    {"type": "node", "pos": [10.4, 36.8], "r": 0.9, "sym": True},
    {"type": "vent", "pos": [0, 38], "w": 2.4, "n": 3, "step": 0.9},
], [
    {"id": "WS0001", "pos": [0, 4], "size": "SMALL", "type": "ENERGY", "mount": "HIDDEN", "angle": 0, "arc": 5},
], [
    {"pos": [0, 45], "width": 4.0, "length": 12},
], [
    {"type": "gradient", "color": "navy", "a": [0, 30], "b": [0, 45], "a0": 0.0, "a1": 0.7},
    navy([[11.4, 34.6], [13.6, 36.4], [12.8, 39.6], [11.0, 38.6]]),
    navy([[7.9, 14.9], [9.6, 14.2], [9.0, 18.2], [7.8, 18.6]]),
    navy([[-1.0, 0], [1.0, 0], [1.6, 5.4], [-1.6, 5.4]], sym=False),
], 31)

# ------------------------------------------------------------------ Cadenza: heavy fighter (twin rails, swept wings)
cadenza = spec("rsl_cadenza", "Cadenza", [34, 40], [
    plate("frame", "graphite", [0, 2.0], 0.4, half=[
        [0, 7.6], [2.2, 9.4], [4.4, 8.4], [5.6, 1.2], [6.6, 0], [8.0, 5.8], [8.4, 14], [9.0, 17.6], [16.2, 23.4],
        [16.6, 28.2], [10.4, 27.2], [9.6, 31], [6.2, 34], [5.0, 38.4], [0, 38.4]]),
    plate("rail", "slate", [2.6, 4.8], sym_poly=[[5.7, 1.8], [6.6, 0.6], [7.6, 6], [7.9, 16.4], [5.5, 16.4]],
          cuts=[{"pts": [[6.6, 3], [6.7, 15]], "w": 0.3, "depth": 0.4, "glow": True, "sym": True}]),
    plate("body", "ivory", [3.0, 4.6], half=[[0, 8.6], [2.2, 10.4], [4.6, 11.6], [5.0, 20], [4.7, 30], [0, 32.4]],
          tier={"inset": 0.8, "dz": 0.4, "mat": "ivory"}),
    plate("wing", "ivory2", [2.8, 4.2], sym_poly=[[8.4, 18], [15.6, 24], [15.9, 27.3], [10.2, 26.4], [8.2, 23.6]]),
    plate("stern", "slate", [2.8, 4.0], half=[[0, 31.6], [4.4, 30.4], [5.6, 33.6], [4.4, 38], [0, 38]]),
], [
    {"type": "cell", "pos": [2.3, 18], "size": [1.6, 4.4], "n": 3, "v": 0.9, "sym": True},
    {"type": "node", "pos": [0, 25], "r": 1.4, "shape": "diamond"},
    {"type": "conduit", "pos": [0, 0], "pts": [[0, 23.6], [0, 13], [3.4, 11], [6.0, 11]], "w": 0.45, "sym": True},
    {"type": "conduit", "pos": [0, 0], "pts": [[1.3, 26], [5.6, 26], [12.4, 25.4]], "w": 0.45, "sym": True},
    {"type": "node", "pos": [13.4, 25.6], "r": 0.9, "sym": True},
], [
    {"id": "WS0001", "pos": [6.6, 1], "size": "SMALL", "type": "ENERGY", "mount": "HIDDEN", "angle": 0, "arc": 5,
     "sym": True},
], [
    {"pos": [3.2, 38.4], "width": 3.0, "length": 10, "sym": True},
], [
    {"type": "gradient", "color": "navy", "a": [0, 30], "b": [0, 38], "a0": 0.0, "a1": 0.6},
    navy([[14.2, 22.4], [16.2, 23.4], [16.6, 28.2], [14.4, 27.8]]),
    {"type": "band", "color": "navy", "pts": [[1.6, 12], [1.6, 30]], "w": 1.2, "sym": True},
], 41)

# ------------------------------------------------------------------ Requiem: bomber (spike spine, notched delta)
requiem = spec("rsl_requiem", "Requiem", [38, 40], [
    plate("frame", "graphite", [0, 2.0], 0.4, half=[
        [0, 0], [1.2, 4], [2.0, 10], [4.2, 12.2], [6.0, 10.6], [7.0, 14], [11.6, 20.0], [11.0, 21.8], [17.4, 27.8], [16.2, 31], [9.2, 29.2],
        [8.6, 33], [5.2, 37.4], [0, 37.4]]),
    plate("spine", "ivory", [3.2, 4.8], half=[[0, 1], [1.0, 5], [1.8, 11], [3.0, 14], [3.4, 26], [2.4, 34], [0, 35]],
          tier={"inset": 0.7, "dz": 0.4, "mat": "ivory"}),
    plate("prong", "slate", [2.8, 4.2], sym_poly=[[4.4, 12.4], [6.0, 10.8], [6.8, 14.2], [5.0, 15.2]]),
    plate("wing", "ivory2", [2.8, 4.3], sym_poly=[[4.0, 15.6], [6.9, 15.0], [11.0, 20.4], [10.5, 22.2], [16.0, 27.6], [15.4, 29.6], [9.2, 28.2],
                                                  [4.2, 25]],
          cuts=[{"pts": [[6.0, 18.4], [11.4, 26.8]], "w": 0.5, "depth": 0.4, "sym": True}]),
    plate("pod", "slate", [3.0, 5.2], half=[[0, 14], [1.8, 15], [2.0, 24], [0, 25.4]],
          tier={"inset": 0.5, "dz": 0.4, "mat": "slate"}),
], [
    {"type": "cell", "pos": [0, 7], "size": [1.4, 3.2], "n": 2, "v": 0.8, "fill": 0.5},
    {"type": "node", "pos": [0, 28.4], "r": 1.4, "shape": "diamond"},
    {"type": "conduit", "pos": [0, 0], "pts": [[0, 27], [0, 25.6]], "w": 0.45},
    {"type": "conduit", "pos": [0, 0], "pts": [[1.2, 29.4], [4.8, 29.4], [8.0, 26.2], [13.6, 27.8]], "w": 0.45,
     "sym": True},
    {"type": "node", "pos": [14.6, 28.2], "r": 0.9, "sym": True},
    {"type": "crystal", "pos": [0, 19.5], "r": 1.4},
], [
    {"id": "WS0001", "pos": [0, 2], "size": "SMALL", "type": "ENERGY", "mount": "HIDDEN", "angle": 0, "arc": 5},
    {"id": "WS0002", "pos": [0, 16], "size": "SMALL", "type": "MISSILE", "mount": "HIDDEN", "angle": 0, "arc": 5},
], [
    {"pos": [3.0, 37.4], "width": 3.0, "length": 10, "sym": True},
], [
    {"type": "gradient", "color": "navy", "a": [0, 30], "b": [0, 37], "a0": 0.0, "a1": 0.6},
    navy([[15.0, 25.6], [17.4, 27.8], [16.2, 31], [14.6, 30.4]]),
    navy([[9.6, 18.4], [11.6, 20.0], [11.0, 21.8], [9.4, 20.6]]),
    navy([[-0.9, 0], [0.9, 0], [1.4, 4.6], [-1.4, 4.6]], sym=False),
    {"type": "band", "color": "navy", "pts": [[5.2, 17.2], [10.6, 25.2]], "w": 1.4, "sym": True},
], 51)

for s in (trill, cadenza, requiem):
    with open(os.path.join(OUT, s["id"] + ".json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(s, f, indent=1)
    print(s["id"], s["size"])
