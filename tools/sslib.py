"""Shared helpers for the starsector-modding scripts (stdlib only, plus optional Pillow/numpy users).

* find_game_dir()          locate the Starsector install (env STARSECTOR_DIR, common paths, or walking up from cwd)
* find_mod_root(start)     the folder holding mod_info.json at or above `start`
* installed_mods(game)     {mod id: (folder, mod_info dict)} for every folder in mods/
* game_version(game)       e.g. "0.98a-RC7", read from Version.class in starfarer_obf.jar
* jar_classes(jar)         set of fully qualified class names in a jar
* loose_json(text)         parse Starsector's relaxed JSON (# comments, trailing commas, unquoted keys/values, 0.5f)
* read_csv(path)           list of dict rows (utf-8, BOM-tolerant), skipping blank/#comment ids
* ship_to_image / image_to_ship   convert .ship coordinates <-> sprite pixel coordinates
"""
import csv
import io
import json
import os
import re
import sys
import zipfile

COMMON_GAME_DIRS = [
    r"C:\Program Files (x86)\Fractal Softworks\Starsector",
    r"C:\Program Files\Fractal Softworks\Starsector",
    r"C:\Games\Starsector",
    os.path.expanduser("~/Starsector"),
    "/Applications/Starsector.app",
    os.path.expanduser("~/Applications/Starsector.app"),
    os.path.expanduser("~/starsector"),
    "/opt/starsector",
]


def core_dir(game):
    """starsector-core (Windows/Linux layout) or Contents/Resources/Java (macOS app bundle)."""
    for sub in ("starsector-core", os.path.join("Contents", "Resources", "Java"), "."):
        p = os.path.join(game, sub)
        # a mod also has data/hulls, so require the API jar too (otherwise a mod folder passes for the game)
        if os.path.isdir(os.path.join(p, "data", "hulls")) and os.path.isfile(os.path.join(p, "starfarer.api.jar")):
            return p
    return None


def find_game_dir(explicit=None):
    cands = []
    if explicit:
        cands.append(explicit)
    if os.environ.get("STARSECTOR_DIR"):
        cands.append(os.environ["STARSECTOR_DIR"])
    here = os.path.abspath(os.getcwd())
    while True:
        cands.append(here)
        parent = os.path.dirname(here)
        if parent == here:
            break
        here = parent
    cands += COMMON_GAME_DIRS
    for c in cands:
        if c and core_dir(c):
            return os.path.abspath(c)
    return None


def require_game_dir(explicit=None):
    g = find_game_dir(explicit)
    if not g:
        sys.exit("Starsector install not found. Pass --game <dir> or set STARSECTOR_DIR.")
    return g


def mods_dir(game):
    p = os.path.join(game, "mods")
    if os.path.isdir(p):
        return p
    # macOS: mods sit next to the .app bundle
    p = os.path.join(os.path.dirname(game), "mods")
    return p if os.path.isdir(p) else os.path.join(game, "mods")


def find_mod_root(start=None):
    """Walk up from `start` (default cwd) to the first folder that contains mod_info.json."""
    here = os.path.abspath(start or os.getcwd())
    if os.path.isfile(here):
        here = os.path.dirname(here)
    while True:
        if os.path.isfile(os.path.join(here, "mod_info.json")):
            return here
        parent = os.path.dirname(here)
        if parent == here:
            return None
        here = parent


def read_mod_info(mod_dir):
    return load_loose_json(os.path.join(mod_dir, "mod_info.json"))


def installed_mods(game):
    """{mod id: (absolute folder, mod_info dict)} for every mods/* folder with a parseable mod_info.json."""
    out = {}
    md = mods_dir(game)
    if not os.path.isdir(md):
        return out
    for name in sorted(os.listdir(md)):
        p = os.path.join(md, name, "mod_info.json")
        if os.path.isfile(p):
            try:
                info = load_loose_json(p)
            except Exception:
                continue
            if isinstance(info, dict) and info.get("id"):
                out[info["id"]] = (os.path.join(md, name), info)
    return out


def version_string(v):
    """mod_info / .version 'version' value -> 'major.minor.patch' text. Accepts a string or a {major, minor, patch} object."""
    if isinstance(v, dict):
        parts = [v.get("major"), v.get("minor"), v.get("patch")]
        return ".".join(str(p) for p in parts if p not in (None, ""))
    return "" if v is None else str(v)


def enabled_mod_ids(game):
    """Ids listed in mods/enabled_mods.json (what the launcher last enabled), or an empty set."""
    p = os.path.join(mods_dir(game), "enabled_mods.json")
    try:
        return set(load_loose_json(p).get("enabledMods", []))
    except Exception:
        return set()


def mod_jars(mod_dir, info=None):
    """Absolute paths of the jars a mod declares in mod_info.json (existing files only)."""
    info = info if info is not None else read_mod_info(mod_dir)
    out = []
    for j in info.get("jars", []) or []:
        p = os.path.join(mod_dir, j.replace("\\", "/"))
        if os.path.isfile(p):
            out.append(p)
    return out


def jar_classes(jar):
    """Fully qualified class names (inner classes included, with '$') contained in a jar."""
    out = set()
    try:
        with zipfile.ZipFile(jar) as z:
            for n in z.namelist():
                if n.endswith(".class") and not n.startswith("META-INF/"):
                    out.add(n[:-6].replace("/", "."))
    except (OSError, zipfile.BadZipFile):
        pass
    return out


def game_version(game):
    """Installed game version such as '0.98a-RC7' (from com/fs/starfarer/Version.class), or None."""
    jar = os.path.join(core_dir(game) or game, "starfarer_obf.jar")
    try:
        with zipfile.ZipFile(jar) as z:
            raw = z.read("com/fs/starfarer/Version.class")
    except (OSError, KeyError, zipfile.BadZipFile):
        return None
    found = [m.group(0).decode() for m in re.finditer(rb"\d+\.\d+(?:\.\d+)?[a-z]?-RC\d+", raw)]
    return min(found, key=len) if found else None


def jre_version(game):
    """JAVA_VERSION of the JRE bundled with the game (e.g. '17.0.10'), or None. Compile mods for this major."""
    for rel in ("jre/release", "jre_linux/release", "Contents/Home/release"):
        p = os.path.join(game, rel)
        if os.path.isfile(p):
            m = re.search(r'JAVA_VERSION="([^"]+)"', open(p, encoding="utf-8", errors="replace").read())
            if m:
                return m.group(1)
    return None


# ---------------------------------------------------------------- relaxed JSON
_TOKEN = re.compile(r'''
    (?P<ws>\s+)
  | (?P<comment>\#[^\n]*|//[^\n]*)
  | (?P<str>"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')
  | (?P<punct>[{}\[\]:,;])
  | (?P<bare>[^\s{}\[\]:,;"'#]+)
''', re.X | re.S)


def loose_json(text):
    """Parse Starsector-dialect JSON the way the game's lenient org.json parser does.

    Accepts # and // comments, trailing commas, ';' as a separator, single-quoted strings, unquoted keys and
    values, 0.5f / .5 / 5. numbers, and ignores anything after the first complete value. Raises ValueError.
    Use strict_json_error() for files you write yourself: keep your own files strict so other tools can read them.
    """
    if text.startswith("\ufeff"):
        text = text[1:]
    out = []
    pos = 0
    while pos < len(text):
        m = _TOKEN.match(text, pos)
        if not m:
            line = text.count("\n", 0, pos) + 1
            raise ValueError("unexpected character %r at line %d" % (text[pos], line))
        pos = m.end()
        kind = m.lastgroup
        tok = m.group(kind)
        if kind in ("ws", "comment"):
            continue
        if kind == "str":
            if tok[0] == "'":
                tok = json.dumps(tok[1:-1].replace("\\'", "'"))
            out.append(tok)
        elif kind == "punct":
            out.append("," if tok == ";" else tok)  # org.json accepts ';' as a separator
        else:  # bare word: number (5, 0.5, .5, 5., 0.5f, 1e3), true/false/null, or unquoted string
            t = tok
            if re.fullmatch(r"[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?[fFdD]?", t):
                num = t.rstrip("fFdD").lstrip("+")
                out.append(num if re.fullmatch(r"-?\d+", num) else repr(float(num)))
            elif t in ("true", "false", "null"):
                out.append(t)
            else:
                out.append(json.dumps(t))
    # drop trailing commas and fix missing commas between values on separate lines is NOT attempted
    cleaned = []
    for i, tok in enumerate(out):
        if tok == "," and i + 1 < len(out) and out[i + 1] in ("}", "]"):
            continue
        cleaned.append(tok)
    s = " ".join(cleaned)
    # org.json stops after the first complete value, so trailing junk (e.g. an extra '}') is ignored by the game
    obj, _end = json.JSONDecoder().raw_decode(s)
    return obj


def load_loose_json(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return loose_json(fh.read())


def strict_json_error(path):
    """Return None if the file is strict JSON (utf-8, no BOM), else an error string."""
    raw = open(path, "rb").read()
    if raw.startswith(b"\xef\xbb\xbf"):
        return "UTF-8 BOM present (Starsector fails to parse files with a BOM)"
    try:
        json.loads(raw.decode("utf-8"))
        return None
    except UnicodeDecodeError as e:
        return "not UTF-8: %s" % e
    except json.JSONDecodeError as e:
        return "line %d col %d: %s" % (e.lineno, e.colno, e.msg)


# ---------------------------------------------------------------- CSV
def read_csv(path, key="id"):
    """Rows as dicts. Skips rows whose key column is blank or starts with '#'. BOM-tolerant."""
    with open(path, encoding="utf-8-sig", errors="replace", newline="") as fh:
        rows = list(csv.DictReader(fh))
    out = []
    for r in rows:
        k = (r.get(key) or "").strip() if key else "x"
        if key and (not k or k.startswith("#")):
            continue
        out.append(r)
    return out


def csv_header(path):
    with open(path, encoding="utf-8-sig", errors="replace", newline="") as fh:
        return next(csv.reader(fh), [])


def write_csv(path, header, rows):
    """Write rows (dicts) with the exact header, LF line endings, UTF-8 without BOM, minimal quoting."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=header, lineterminator="\n", extrasaction="raise")
    w.writeheader()
    for r in rows:
        w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in header})
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(buf.getvalue())


def write_text(path, text):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def _np_default(o):
    """Let json.dumps accept numpy scalars/arrays."""
    if hasattr(o, "item") and getattr(o, "shape", None) == ():
        return o.item()
    if hasattr(o, "tolist"):
        return o.tolist()
    raise TypeError("not JSON serializable: %r" % type(o))


def write_json(path, obj):
    write_text(path, json.dumps(obj, indent=4, default=_np_default) + "\n")


# ---------------------------------------------------------------- .ship coordinates
# .ship "center" is [x from the sprite's LEFT edge, y from the sprite's BOTTOM edge].
# Every other .ship position (bounds, weaponSlots.locations, engineSlots.location, shieldCenter) is ship-local:
#   +x = forward (towards the TOP of the sprite), +y = LEFT (towards the left edge of the sprite).
# Angles are degrees counter-clockwise from forward (90 = left, -90 = right, 180 = backwards).
def ship_to_image(x, y, center, height):
    cx, cy = center
    return (cx - y, height - cy - x)


def image_to_ship(px, py, center, height):
    cx, cy = center
    return ((height - py) - cy, cx - px)


HULL_SIZES = ("FIGHTER", "FRIGATE", "DESTROYER", "CRUISER", "CAPITAL_SHIP")


def vanilla_hulls(game):
    """{hullId: (ship_json, path)} for vanilla .ship files."""
    core = core_dir(game)
    out = {}
    for root, _, files in os.walk(os.path.join(core, "data", "hulls")):
        for f in files:
            if f.endswith(".ship"):
                p = os.path.join(root, f)
                try:
                    d = load_loose_json(p)
                except Exception:
                    continue
                if isinstance(d, dict) and d.get("hullId"):
                    out[d["hullId"]] = (d, p)
    return out
