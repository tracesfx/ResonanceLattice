"""Scale a spec's geometry in place (positions and outlines; line widths, bevels and z stay as they are).

python scale_spec.py specs/rsl_gracenote.json 1.12 --size 68,116
"""
import argparse
import json

GEOM = {"half", "poly", "sym_poly", "pts", "pos"}
LEN = {"r", "y_from", "y_to", "width", "length", "spacing"}


def walk(o, k):
    if isinstance(o, dict):
        for key, v in o.items():
            if key in GEOM:
                o[key] = sc(v, k)
            elif key == "size" and isinstance(v, list) and all(isinstance(x, (int, float)) for x in v):
                o[key] = [round(x * k, 2) for x in v]
            elif key in LEN and isinstance(v, (int, float)):
                o[key] = round(v * k, 2)
            else:
                walk(v, k)
    elif isinstance(o, list):
        for v in o:
            walk(v, k)


def sc(v, k):
    if isinstance(v, (int, float)):
        return round(v * k, 2)
    return [sc(x, k) for x in v]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("k", type=float)
    ap.add_argument("--size", required=True, help="new canvas W,H (W even)")
    a = ap.parse_args()
    s = json.load(open(a.spec, encoding="utf-8"))
    walk(s["layers"], a.k)
    for key in ("details", "slots", "engines"):
        walk(s.get(key, []), a.k)
    s["size"] = [int(x) for x in a.size.split(",")]
    with open(a.spec, "w", encoding="utf-8", newline="\n") as f:
        json.dump(s, f, indent=1)


if __name__ == "__main__":
    main()
