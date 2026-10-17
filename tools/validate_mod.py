#!/usr/bin/env python3
"""validate_mod.py - static QA for a Starsector mod. Run it on every build: exit code 1 on any ERROR.

    python validate_mod.py                          # the mod = folder with mod_info.json at or above the cwd
    python validate_mod.py --mod path/to/MyMod --prefix xyz_
    python validate_mod.py --strict                 # warnings fail too (use before a release)
    python validate_mod.py --only hulls,variants    # run some check groups (see --list-checks)
    python validate_mod.py --quiet                  # hide notes

Everything is cross-checked against vanilla (starsector-core/data), the mod's declared dependencies (their data,
graphics and jars), and optional mods named in the config. The rules come from the engine's own data and source where
possible: CSV headers are compared with vanilla's, enum values are read from the API, and limits such as vents/caps
(10/20/30/50) come from CoreAutofitPlugin.getBaseMax.

Optional config: <mod>/validate_config.json or <mod>/tools/validate_config.json
    {"prefix": "xyz_",                       # new ids must start with it (also --prefix)
     "optional_mods": ["shaderLib"],         # mods you integrate with but do not depend on (compile/lookup only)
     "literal_whitelist": ["xyz_star_1"],    # prefixed strings in Java that are not data ids (entity ids, keys...)
     "allow_overrides": ["hegemony"],        # vanilla ids you intend to override (silences the warning)
     "ignore": ["regex on the message"]}     # silence specific findings (keep this list short and justified)
"""
import argparse
import collections
import csv
import difflib
import json
import os
import re
import struct
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sslib  # noqa: E402

try:
    from PIL import Image
except ImportError:  # sprite pixel checks are skipped without Pillow
    Image = None

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

GROUPS = ["modinfo", "version", "files", "ids", "hulls", "weapons", "variants", "wings", "factions", "roles",
          "systems", "hullmods", "campaign", "settings", "rules", "java", "graphics", "sounds", "descriptions", "lights",
          "missions"]
JSON_EXT = (".json", ".ship", ".variant", ".wpn", ".proj", ".system", ".faction", ".skin")
SKIP_DIRS = {".git", "build", "dist", "__pycache__", ".idea", ".vscode", "node_modules", ".gradle", "out", ".svn"}
REG_CSV = {  # kind: (path under data/, id column)
    "hull": ("hulls/ship_data.csv", "id"),
    "weapon": ("weapons/weapon_data.csv", "id"),
    "wing": ("hulls/wing_data.csv", "id"),
    "hullmod": ("hullmods/hull_mods.csv", "id"),
    "system": ("shipsystems/ship_systems.csv", "id"),
    "commodity": ("campaign/commodities.csv", "id"),
    "condition": ("campaign/market_conditions.csv", "id"),
    "industry": ("campaign/industries.csv", "id"),
    "submarket": ("campaign/submarkets.csv", "id"),
    "item": ("campaign/special_items.csv", "id"),
    "ability": ("campaign/abilities.csv", "id"),
    "skill": ("characters/skills/skill_data.csv", "id"),
}
MAX_VENTS = {"FIGHTER": 5, "FRIGATE": 10, "DESTROYER": 20, "CRUISER": 30, "CAPITAL_SHIP": 50}  # CoreAutofitPlugin.getBaseMax
HMOD_COST = {"FRIGATE": "cost_frigate", "DESTROYER": "cost_dest", "CRUISER": "cost_cruiser", "CAPITAL_SHIP": "cost_capital"}
SLOT_COMPAT = {"BALLISTIC": {"BALLISTIC"}, "ENERGY": {"ENERGY"}, "MISSILE": {"MISSILE"},
               "HYBRID": {"BALLISTIC", "ENERGY"}, "SYNERGY": {"ENERGY", "MISSILE"},
               "COMPOSITE": {"BALLISTIC", "MISSILE"}, "UNIVERSAL": {"BALLISTIC", "ENERGY", "MISSILE"}}
SIZE_N = {"SMALL": 0, "MEDIUM": 1, "LARGE": 2}
LUNA_TYPES = {"Header", "Text", "Int", "Double", "String", "Boolean", "Enum", "Keycode", "Color", "Radio"}  # LunaSettingsLoader.kt
AUTOFIT_TAG = re.compile(r"^(kinetic|he|energy|pd|beam|strike|missile|rocket|utility)\d+$")
ID_CONST_PREFIX = [("HULL_", "hull"), ("SHIP_", "hull"), ("VARIANT_", "variant"), ("WEAPON_", "weapon"),
                   ("WING_", "wing"), ("FIGHTER_", "wing"), ("HULLMOD_", "hullmod"), ("SYSTEM_", "system"),
                   ("CONDITION_", "condition"), ("ITEM_", "item"), ("FACTION_", "faction"), ("ENTITY_", "entity"),
                   ("INDUSTRY_", "industry"), ("SUBMARKET_", "submarket"), ("COMMODITY_", "commodity"),
                   ("PROJ_", "proj"), ("ABILITY_", "ability"), ("SKILL_", "skill")]
_LIT = r'"([^"]+)"\s*[,)]'  # a whole string literal argument (not "prefix_" + x)
JAVA_LOOKUPS = [  # (regex with the id as group 1, registry kind)
    (r'getVariant\(\s*' + _LIT, "variant"), (r'getHullSpec\(\s*' + _LIT, "hull"),
    (r'getWeaponSpec\(\s*' + _LIT, "weapon"), (r'getHullModSpec\(\s*' + _LIT, "hullmod"),
    (r'getFighterWingSpec\(\s*' + _LIT, "wing"), (r'getShipSystemSpec\(\s*' + _LIT, "system"),
    (r'getCommoditySpec\(\s*' + _LIT, "commodity"), (r'getSpecialItemSpec\(\s*' + _LIT, "item"),
    (r'getIndustrySpec\(\s*' + _LIT, "industry"), (r'getMarketConditionSpec\(\s*' + _LIT, "condition"),
    (r'getFaction\(\s*' + _LIT, "faction"), (r'addCondition\(\s*' + _LIT, "condition"),
    (r'hasCondition\(\s*' + _LIT, "condition"), (r'addIndustry\(\s*' + _LIT, "industry"),
    (r'addSubmarket\(\s*' + _LIT, "submarket"), (r'addAbility\(\s*' + _LIT, "ability"),
    (r'addCustomEntity\([^,()]+,[^,()]+,\s*' + _LIT, "entity"),
]
NOT_ID_CONST = re.compile(r"_(PATH|DIR|FILE|KEY|TAG|PREFIX|SUFFIX|FORMAT|NAME|TEXT|LABEL|SOUND|SPRITE|ICON|CATEGORY)$")
LEAKY_TYPE = re.compile(r"(?<!Sprite)(?<!Settings)API\b(?!\.)|\b(Sector|CampaignFleet|FleetMember|Ship|Market|Planet|"
                        r"SectorEntityToken|Person|StarSystem|IntelInfoPlugin|InteractionDialog|CombatEngine)\b(?!\.)")
ALWAYS_LOADED_JSON = {"data/config/settings.json", "data/config/custom_entities.json", "data/config/engine_styles.json",
                      "data/config/hull_styles.json", "data/config/sounds.json", "data/config/planets.json",
                      "data/world/factions/default_ship_roles.json", "data/strings/ship_names.json",
                      "data/config/battle_objectives.json", "data/campaign/abilities.json"}
GFX_REF = re.compile(r"(?:graphics|sounds|data)/[A-Za-z0-9_\-./ ]+?\.(?:png|jpg|jpeg|ogg|wav|csv|json|frag|vert)", re.I)


# =============================================================================================== reporting
class Report:
    def __init__(self, ignore=()):
        self.items = []
        self.ignore = [re.compile(x) for x in ignore]
        self.group = "files"

    def add(self, level, msg, where=None, group=None):
        if any(rx.search(msg) for rx in self.ignore):
            return
        self.items.append((level, group or self.group, msg, where))

    def error(self, msg, where=None):
        self.add("ERROR", msg, where)

    def warn(self, msg, where=None):
        self.add("WARN", msg, where)

    def note(self, msg, where=None):
        self.add("note", msg, where)

    def count(self, level):
        return sum(1 for i in self.items if i[0] == level)


# =============================================================================================== file helpers
def walk(root, subdirs=None):
    tops = [os.path.join(root, s) for s in subdirs] if subdirs else [root]
    for top in tops:
        if not os.path.isdir(top):
            continue
        for dp, dns, fs in os.walk(top):
            dns[:] = [d for d in dns if d not in SKIP_DIRS]
            for f in fs:
                yield os.path.relpath(os.path.join(dp, f), root).replace("\\", "/")


def png_info(path):
    """(width, height, bit depth, colour type) from the PNG header, or None."""
    try:
        with open(path, "rb") as fh:
            head = fh.read(33)
    except OSError:
        return None
    if len(head) < 26 or head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
        return None
    w, h = struct.unpack(">II", head[16:24])
    return w, h, head[24], head[25]


def image_size(path):
    pi = png_info(path)
    if pi:
        return pi[0], pi[1]
    if Image is not None:
        try:
            with Image.open(path) as im:
                return im.size
        except Exception:
            return None
    return None


class Source:
    """One data root: vanilla core, a dependency/optional mod, or the mod under test."""

    def __init__(self, label, root, is_mod=False):
        self.label = label
        self.root = root
        self.is_mod = is_mod
        self.files = list(walk(root) if is_mod else walk(root, ["data", "graphics", "sounds"]))
        self.json = {}
        self._csv = {}

    def load_json(self, report=None):
        for rel in self.files:
            if not rel.startswith("data/") or not rel.lower().endswith(JSON_EXT):
                continue
            p = os.path.join(self.root, rel)
            if self.is_mod and report is not None:
                obj = parse_mod_json(p, rel, report)
            else:
                try:
                    obj = sslib.load_loose_json(p)
                except Exception:
                    obj = None
            if obj is not None:
                self.json[rel] = obj

    def csv(self, rel):
        """(header, rows) for a CSV path relative to the root; rows are dicts with '_line'. Cached."""
        if rel in self._csv:
            return self._csv[rel]
        p = os.path.join(self.root, rel)
        if not os.path.isfile(p):
            self._csv[rel] = (None, [])
            return self._csv[rel]
        with open(p, encoding="utf-8-sig", errors="replace", newline="") as fh:
            rd = csv.reader(fh)
            rows = []
            header = None
            for rec in rd:
                if header is None:
                    header = [h.strip() for h in rec]
                    continue
                if not rec or not any(c.strip() for c in rec):
                    continue
                if rec[0].lstrip().startswith("#"):  # comment row (the game skips rows whose first cell starts with #)
                    continue
                d = {header[i]: (rec[i] if i < len(rec) else "") for i in range(len(header))}
                d["_line"] = rd.line_num
                d["_ncols"] = len(rec)
                rows.append(d)
        self._csv[rel] = (header, rows)
        return self._csv[rel]

    def rows(self, rel, key="id"):
        _, rows = self.csv(rel)
        out = []
        for r in rows:
            k = (r.get(key) or "").strip()
            if k and not k.startswith("#"):
                out.append(r)
        return out


def parse_mod_json(path, rel, report):
    raw = open(path, "rb").read()
    report.group = "files"
    if raw.startswith(b"\xef\xbb\xbf"):
        report.error("UTF-8 BOM: the game's parser fails on files with a BOM; save as UTF-8 without BOM", rel)
        raw = raw[3:]
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        report.error("not valid UTF-8 (%s)" % e, rel)
        text = raw.decode("utf-8", "replace")
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        try:
            obj = sslib.loose_json(text)
        except Exception as e2:
            # Typed spec files and files the game reads by name are always loaded; other JSON only if code reads it.
            loaded = rel.lower().endswith(JSON_EXT[1:]) or rel in ALWAYS_LOADED_JSON or rel == "mod_info.json"
            (report.error if loaded else report.warn)(
                "JSON does not parse even with the game's lenient rules: %s%s"
                % (e2, "" if loaded else " (only matters if code loads this file)"), rel)
            return None
        report.note("not strict JSON (%s, line %d); the game's lenient parser accepts it" % (e.msg, e.lineno), rel)
        return obj


# =============================================================================================== the validator
class Validator:
    def __init__(self, mod, game, cfg, report):
        self.mod = mod
        self.game = game
        self.core = sslib.core_dir(game)
        self.cfg = cfg
        self.r = report
        self.prefix = cfg.get("prefix") or None
        self.info = {}
        self.sources = []          # [Source]; vanilla first, mod last
        self.reg = collections.defaultdict(dict)    # kind -> id -> (payload, source label)
        self.mod_ids = collections.defaultdict(dict)  # kind -> id -> payload (defined by the mod)
        self.classes = set()
        self.mod_classes = set()
        self.files_exact = {}      # rel path -> source label
        self.files_lower = {}      # lower rel path -> actual rel path
        self.enums = {}
        self.referenced_assets = set()

    # ------------------------------------------------------------------------------------------- setup
    def setup(self):
        r = self.r
        r.group = "modinfo"
        p = os.path.join(self.mod, "mod_info.json")
        self.info = parse_mod_json(p, "mod_info.json", r) or {}
        installed = sslib.installed_mods(self.game)
        deps = []
        for d in self.info.get("dependencies", []) or []:
            did = d.get("id") if isinstance(d, dict) else None
            if did and did in installed and os.path.abspath(installed[did][0]) != os.path.abspath(self.mod):
                deps.append((did, installed[did][0], installed[did][1]))
        for oid in self.cfg.get("optional_mods", []) or []:
            if oid in installed and oid not in [x[0] for x in deps]:
                deps.append((oid, installed[oid][0], installed[oid][1]))
        self.deps = deps
        self.installed = installed
        van = Source("vanilla", self.core)
        van.load_json()
        self.sources.append(van)
        for did, folder, info in deps:
            s = Source(did, folder)
            s.load_json()
            self.sources.append(s)
        self.modsrc = Source("mod", self.mod, is_mod=True)
        self.modsrc.load_json(r)
        self.sources.append(self.modsrc)
        for s in self.sources:
            for rel in s.files:
                self.files_exact.setdefault(rel, s.label)
                self.files_lower.setdefault(rel.lower(), rel)
            self._registries(s)
        self._classes()
        self._enums()

    def _registries(self, s):
        is_mod = s is self.modsrc

        def put(kind, k, payload):
            if k is None:
                return
            k = k if isinstance(k, tuple) else str(k)
            self.reg[kind][k] = (payload, s.label)
            if is_mod:
                self.mod_ids[kind][k] = payload

        for kind, (rel, col) in REG_CSV.items():
            for row in s.rows("data/" + rel, col):
                put(kind, row[col].strip(), row)
        for rel, obj in s.json.items():
            if not isinstance(obj, dict):
                continue
            low = rel.lower()
            if low.endswith(".ship") and obj.get("hullId"):
                put("ship_file", obj["hullId"], (obj, rel))
            elif low.endswith(".skin") and obj.get("skinHullId"):
                put("skin", obj["skinHullId"], (obj, rel))
                put("hull", obj["skinHullId"], {"_skin": True})
            elif low.endswith(".variant") and obj.get("variantId"):
                put("variant", obj["variantId"], (obj, rel))
            elif low.endswith(".wpn") and obj.get("id"):
                put("wpn", obj["id"], (obj, rel))
            elif low.endswith(".proj") and obj.get("id"):
                put("proj", obj["id"], (obj, rel))
            elif low.endswith(".system") and obj.get("id"):
                put("system_file", obj["id"], (obj, rel))
            elif low.endswith(".faction"):
                fid = obj.get("id")
                if not fid and not is_mod:
                    continue
                if not fid:  # a merge patch of another faction file: take the id from the patched file
                    for other in self.sources:
                        if other is not s and rel in other.json and isinstance(other.json[rel], dict):
                            fid = other.json[rel].get("id")
                if fid:
                    put("faction_file", fid, (obj, rel))
                    if rel in self._listed_faction_files(s) or not is_mod:
                        put("faction", fid, obj)
        named = {"data/config/custom_entities.json": "entity", "data/config/engine_styles.json": "engine_style",
                 "data/config/hull_styles.json": "hull_style", "data/strings/ship_names.json": "shipname_src",
                 "data/config/planets.json": "planet_type", "data/world/factions/default_ship_roles.json": "role"}
        for rel, kind in named.items():
            obj = s.json.get(rel)
            if isinstance(obj, dict):
                for k, v in obj.items():
                    put(kind, k, v)
        snd = s.json.get("data/config/sounds.json")
        if isinstance(snd, dict):
            for k, v in snd.items():
                if k == "music" and isinstance(v, dict):
                    for mk in v:
                        put("music", mk, v[mk])
                else:
                    put("sound", k, v)
        for row in s.rows("data/strings/descriptions.csv"):
            put("desc", (row["id"].strip(), row.get("type", "").strip()), row)
        for row in s.rows("data/characters/person_names.csv", "category"):
            put("person_name_cat", row["category"].strip(), True)
        for row in s.rows("data/campaign/rules.csv"):
            put("rule", row["id"].strip(), row)

    def _listed_faction_files(self, s):
        return {(row.get("faction") or "").strip().replace("\\", "/")
                for row in s.rows("data/world/factions/factions.csv", "faction")}

    def _classes(self):
        api = os.path.join(self.core, "starfarer.api.jar")
        self.classes |= sslib.jar_classes(api)
        for _, folder, info in self.deps:
            for j in sslib.mod_jars(folder, info):
                self.classes |= sslib.jar_classes(j)
        for j in sslib.mod_jars(self.mod, self.info):
            self.mod_classes |= sslib.jar_classes(j)
        bc = os.path.join(self.mod, "build", "classes")
        if os.path.isdir(bc):
            for rel in walk(bc):
                if rel.endswith(".class"):
                    self.mod_classes.add(rel[:-6].replace("/", "."))
        for s in self.sources:  # loose .java anywhere under data/ is compiled at startup by the game (Janino);
            for rel in s.files:  # vanilla's own hullmods (data.hullmods.HeavyArmor) and systems load this way
                if rel.startswith("data/") and rel.endswith(".java"):
                    (self.mod_classes if s is self.modsrc else self.classes).add(rel[:-5].replace("/", "."))
        self.classes |= self.mod_classes

    def _enums(self):
        z = os.path.join(self.core, "starfarer.api.zip")
        want = {"ShipTypeHints": "com/fs/starfarer/api/combat/ShipHullSpecAPI.java",
                "AIHints": "com/fs/starfarer/api/combat/WeaponAPI.java",
                "WeaponType": "com/fs/starfarer/api/combat/WeaponAPI.java",
                "WeaponSize": "com/fs/starfarer/api/combat/WeaponAPI.java",
                "ShieldType": "com/fs/starfarer/api/combat/ShieldAPI.java"}
        try:
            with zipfile.ZipFile(z) as zf:
                for name, path in want.items():
                    t = zf.read(path).decode("utf-8", "replace")
                    t = re.sub(r"//[^\n]*|/\*.*?\*/", "", t, flags=re.S)
                    m = re.search(r"enum\s+%s\s*\{([^;}]*)" % name, t)
                    if m:
                        self.enums[name] = {x.strip().split("(")[0] for x in m.group(1).split(",") if x.strip()}
        except (OSError, KeyError, zipfile.BadZipFile):
            pass
        van = self.sources[0]
        self.enums.setdefault("ShieldType", {"NONE", "FRONT", "OMNI", "PHASE"})
        self.enums["specClass"] = {o.get("specClass") for o, _ in self._vals("wpn") if o.get("specClass")}
        self.enums["aiType"] = {o.get("aiType") for o, _ in self._vals("system_file") if o.get("aiType")} | {"CUSTOM", "NONE"}
        self.enums["desc_type"] = {k[1] for k in self.reg["desc"]} | {"SHIP", "WEAPON", "SHIP_SYSTEM", "FACTION",
                                                                     "CUSTOM", "RESOURCE", "PLANET"}
        self.enums["damage_type"] = {"KINETIC", "HIGH_EXPLOSIVE", "FRAGMENTATION", "ENERGY", "OTHER", ""}
        rh = van.csv("data/campaign/rules.csv")[0]
        self.rules_header = rh

    def _vals(self, kind):
        return [v[0] for v in self.reg[kind].values()]

    # ------------------------------------------------------------------------------------------- lookups
    def has(self, kind, k):
        return k in self.reg[kind]

    def class_ok(self, fqcn, where, what="class"):
        if not fqcn:
            return
        fq = fqcn.strip()
        if fq in self.classes or fq.replace("$", ".") in {c.replace("$", ".") for c in self.classes if "$" in c}:
            return
        self.r.error("%s not found in the mod's jars/build output, dependency jars or the API: %s" % (what, fq), where)

    def path_ok(self, path, where, what="file"):
        """Check a data/graphics/sounds path the game will load. Returns True if it exists exactly."""
        if not path or not isinstance(path, str):
            return False
        if "\\" in path:
            self.r.error("%s path uses backslashes (breaks on Linux/macOS; use /): %s" % (what, path), where)
            path = path.replace("\\", "/")
        p = path.lstrip("/")
        self.referenced_assets.add(p)
        if p in self.files_exact:
            return True
        actual = self.files_lower.get(p.lower())
        if actual:
            self.r.error("%s path case differs from the file on disk: %s vs %s (works on Windows, crashes on "
                         "Linux/macOS)" % (what, path, actual), where)
            return False
        self.r.error("%s missing: %s" % (what, path), where)
        return False

    def abs_path(self, rel):
        rel = rel.replace("\\", "/").lstrip("/")
        for s in reversed(self.sources):
            p = os.path.join(s.root, rel)
            if os.path.isfile(p):
                return p
        actual = self.files_lower.get(rel.lower())
        if actual:
            for s in reversed(self.sources):
                p = os.path.join(s.root, actual)
                if os.path.isfile(p):
                    return p
        return None

    def ship_spec(self, hid):
        """(ship dict, csv row, skin dict or None) with skin changes applied; None if unknown."""
        skin = None
        if hid in self.reg["skin"]:
            skin = self.reg["skin"][hid][0][0]
            base = skin.get("baseHullId")
        else:
            base = hid
        sf = self.reg["ship_file"].get(base)
        row = self.reg["hull"].get(base, (None,))[0]
        if not sf:
            return None
        ship = json.loads(json.dumps(sf[0][0]))
        if skin:
            slots = {s.get("id"): s for s in ship.get("weaponSlots", [])}
            for sid in skin.get("removeWeaponSlots", []) or []:
                slots.pop(sid, None)
            for sid, ch in (skin.get("weaponSlotChanges") or {}).items():
                if sid in slots and isinstance(ch, dict):
                    slots[sid].update(ch)
            ship["weaponSlots"] = list(slots.values())
            bim = set(ship.get("builtInMods", [])) - set(skin.get("removeBuiltInMods", []) or [])
            ship["builtInMods"] = list(bim | set(skin.get("builtInMods", []) or []))
            bw = dict(ship.get("builtInWeapons", {}) or {})
            for sid in skin.get("removeBuiltInWeapons", []) or []:
                bw.pop(sid, None)
            bw.update(skin.get("builtInWeapons", {}) or {})
            ship["builtInWeapons"] = bw
            if skin.get("builtInWings"):
                ship["builtInWings"] = skin["builtInWings"]
        return ship, row, skin

    # ------------------------------------------------------------------------------------------- checks
    def run(self, only=None):
        for g in GROUPS:
            if only and g not in only:
                continue
            self.r.group = g
            getattr(self, "check_" + g)()

    # .............................................................................. mod_info.json
    def check_modinfo(self):
        r, info = self.r, self.info
        where = "mod_info.json"
        for k in ("id", "name", "version", "description", "gameVersion"):
            if k not in info:
                r.error("missing required field '%s'" % k, where)
        mid = info.get("id")
        if mid:
            other = self.installed.get(mid)
            if other and os.path.abspath(other[0]) != os.path.abspath(self.mod):
                r.error("mod id '%s' is also used by %s (the launcher hides one of them)" % (mid, other[0]), where)
        gv = sslib.game_version(self.game)
        mm = lambda s: (re.match(r"\d+\.\d+", str(s)) or re.match("", "")).group(0)  # noqa: E731  ('0.98a-RC7' -> '0.98')
        if gv and info.get("gameVersion") and mm(info["gameVersion"]) != mm(gv):
            r.warn("gameVersion %s targets a different release than the installed game %s" % (info["gameVersion"], gv), where)
        for j in info.get("jars", []) or []:
            if not os.path.isfile(os.path.join(self.mod, j)):
                r.error("jar listed in mod_info.json does not exist: %s (build first)" % j, where)
        if info.get("modPlugin"):
            self.class_ok(info["modPlugin"], where, "modPlugin class")
        for k in ("utility", "totalConversion"):
            if k in info and str(info[k]).lower() not in ("true", "false"):
                r.error("%s must be true or false" % k, where)
        for d in info.get("dependencies", []) or []:
            if not isinstance(d, dict) or not d.get("id"):
                r.error("dependency entries need an 'id'", where)
                continue
            inst = self.installed.get(d["id"])
            if not inst:
                r.error("dependency '%s' is not installed in mods/" % d["id"], where)
                continue
            want = d.get("version")
            if want:
                have = sslib.version_string(inst[1].get("version"))
                if _vtuple(have) < _vtuple(sslib.version_string(want)):
                    r.error("dependency %s needs version %s, installed %s" % (d["id"], sslib.version_string(want), have), where)
        enabled = sslib.enabled_mod_ids(self.game)
        if enabled and mid and mid not in enabled:
            r.note("mod is not enabled in mods/enabled_mods.json (enable it in the launcher to test)", where)
        if self.prefix is None:
            r.note("no id prefix configured; pass --prefix (or set it in validate_config.json) to enforce one", where)

    # .............................................................................. Version Checker
    def check_version(self):
        r = self.r
        vf = "data/config/version/version_files.csv"
        hdr, rows = self.modsrc.csv(vf)
        if hdr is None:
            r.warn("no Version Checker support (%s + a .version file); every installed library mod has it" % vf)
            return
        if hdr[:1] != ["version file"]:
            r.error("header must be exactly 'version file' (found %s)" % hdr, vf)
        active = [row for row in rows if (row.get("version file") or "").strip()
                  and not (row.get("version file") or "").strip().startswith("#")]
        if not active:
            r.note("Version Checker row commented out (fine until the .version file is hosted; uncomment it with a real "
                   "masterVersionFile URL before release)", vf)
        raw = _read(os.path.join(self.mod, vf)) if os.path.isfile(os.path.join(self.mod, vf)) else ""
        parked = [{"version file": ln.strip()} for ln in raw.splitlines() if ln.strip().startswith("#")]
        for row in list(rows) + [p for p in parked if p not in rows]:
            rel = (row.get("version file") or "").strip()
            commented = rel.startswith("#")
            if commented:   # still keep a parked .version file in sync with mod_info.json
                m = re.search(r"([\w./-]+\.version)\b", rel)
                rel = m.group(1) if m else ""
            if not rel:
                continue
            p = os.path.join(self.mod, rel)
            if commented and not os.path.isfile(p):
                continue
            if not os.path.isfile(p):
                r.error("listed .version file does not exist: %s" % rel, vf)
                continue
            try:
                v = sslib.load_loose_json(p)
            except Exception as e:
                r.error("does not parse: %s" % e, rel)
                continue
            for k in ("masterVersionFile", "modName", "modVersion"):
                if k not in v:
                    r.error("missing '%s'" % k, rel)
            mv = sslib.version_string(v.get("modVersion"))
            iv = sslib.version_string(self.info.get("version"))
            if mv and iv and _vtuple(mv) != _vtuple(iv):
                r.error("modVersion %s does not match mod_info.json version %s" % (mv, iv), rel)
            if commented:
                continue
            if str(v.get("masterVersionFile", "")).strip() in ("", "TODO") or "TODO" in str(v.get("masterVersionFile")):
                r.warn("masterVersionFile is not a real URL yet: LunaLib's and Nexerelin's version checkers log a "
                       "MalformedURLException at every launch. Point it at the raw .version file you host, or comment "
                       "out the row in version_files.csv until then", rel)

    # .............................................................................. files: encoding, CSV shape
    def check_files(self):
        r = self.r
        van = self.sources[0]
        for rel in self.modsrc.files:
            low = rel.lower()
            if not low.startswith("data/") or not low.endswith(".csv"):
                continue
            raw = open(os.path.join(self.mod, rel), "rb").read()
            if raw.startswith(b"\xef\xbb\xbf"):
                r.error("UTF-8 BOM (save as UTF-8 without BOM; the game misreads the first column)", rel)
            try:
                raw.decode("utf-8")
            except UnicodeDecodeError as e:
                r.error("not valid UTF-8 (%s)" % e, rel)
            hdr, rows = self.modsrc.csv(rel)
            if hdr is None:
                continue
            vh = van.csv(rel)[0]
            if vh is None:
                for d in self.sources[1:-1]:
                    vh = d.csv(rel)[0] or vh
            if vh:
                missing = [c for c in vh if c and c not in hdr]
                extra = [c for c in hdr if c and c not in vh]
                key_cols = {"id", "fieldID", "faction", "version file", "trigger"} & set(vh)
                if [c for c in missing if c in key_cols]:
                    r.error("header lacks key column(s) %s" % ", ".join(c for c in missing if c in key_cols), rel)
                elif missing:
                    r.warn("header lacks vanilla columns %s (tolerated, values read as blank; copy vanilla's header "
                           "to be safe)" % ", ".join(missing), rel)
                if extra:
                    r.warn("header has columns vanilla does not: %s" % ", ".join(extra), rel)
                if not missing and not extra and [c for c in hdr if c] != [c for c in vh if c]:
                    r.note("column order differs from vanilla (fine: columns are read by name)", rel)
            for row in rows:
                if row["_ncols"] != len(hdr):
                    (r.error if vh else r.warn)("line %d has %d columns, header has %d (unbalanced quotes or commas?)"
                                                % (row["_line"], row["_ncols"], len(hdr)), rel)
            registry_csvs = {"data/" + p for p, _ in REG_CSV.values()} | {"data/campaign/rules.csv",
                                                                          "data/config/LunaSettings.csv"}
            key = ("fieldID" if "fieldID" in hdr else "id") if rel in registry_csvs else None
            if key:
                seen = {}
                for row in rows:
                    k = (row.get(key) or "").strip()
                    if not k or k.startswith("#"):
                        continue
                    if k in seen and not rel.endswith("descriptions.csv"):
                        r.error("duplicate id '%s' (lines %d and %d)" % (k, seen[k], row["_line"]), rel)
                    seen[k] = row["_line"]
        todo = re.compile(r"\bTODO\b|\bFIXME\b|lorem ipsum|\bplaceholder\b", re.I)
        for rel in self.modsrc.files:
            if rel.lower().endswith((".csv", ".json", ".ship", ".variant", ".wpn", ".proj", ".system", ".faction",
                                     ".skin", ".java", ".version", ".md")) and rel != "mod_info.json":
                base = os.path.basename(rel)
                if base != base.strip():
                    r.error("file name has leading/trailing spaces", rel)
            if rel.lower().endswith((".csv", ".json", ".ship", ".variant", ".wpn", ".proj", ".system", ".faction",
                                     ".skin", ".java", ".kt", ".version", ".md")) and not rel.startswith("tools/"):
                with open(os.path.join(self.mod, rel), encoding="utf-8", errors="replace") as fh:
                    for ln, line in enumerate(fh, 1):
                        if todo.search(line):
                            r.warn("unfinished placeholder text (line %d): %s" % (ln, line.strip()[:90]), rel)
                            break

    # .............................................................................. id ownership / prefix
    def check_ids(self):
        r = self.r
        allow = set(self.cfg.get("allow_overrides", []) or [])
        kinds = list(REG_CSV) + ["variant", "wpn", "proj", "ship_file", "system_file", "faction", "entity",
                                 "engine_style", "hull_style", "shipname_src", "rule"]
        prefix_kinds = set(REG_CSV) | {"variant", "proj", "faction", "entity", "rule"}
        for kind in kinds:
            for k in self.mod_ids.get(kind, {}):
                owners = [s.label for s in self.sources[:-1] if self._defined_in(s, kind, k)]
                if owners:
                    if k not in allow and kind not in ("ship_file", "system_file", "wpn"):
                        r.warn("%s '%s' overrides %s's (intended? list it in allow_overrides)" % (kind, k, owners[-1]))
                    continue
                if self.prefix and kind in prefix_kinds and not k.lower().startswith(self.prefix.lower()):
                    r.error("new %s id '%s' lacks the prefix '%s' (collision risk with other mods)" % (kind, k, self.prefix))
        if not self.prefix:
            new = [k for kind in prefix_kinds for k in self.mod_ids.get(kind, {})
                   if not any(self._defined_in(s, kind, k) for s in self.sources[:-1])]
            pre = collections.Counter(re.match(r"^([A-Za-z0-9]+_)", k).group(1).lower() for k in new
                                      if re.match(r"^([A-Za-z0-9]+_)", k))
            if pre:
                p, n = pre.most_common(1)[0]
                r.note("most new ids start with '%s' (%d of %d); pass --prefix %s to enforce it" % (p, n, len(new), p))

    def _defined_in(self, s, kind, k):
        if kind in REG_CSV:
            rel, col = REG_CSV[kind]
            return any(row[col].strip() == k for row in s.rows("data/" + rel, col))
        if kind == "rule":
            return any(row["id"].strip() == k for row in s.rows("data/campaign/rules.csv"))
        ext = {"variant": ".variant", "wpn": ".wpn", "proj": ".proj", "ship_file": ".ship", "system_file": ".system"}
        if kind in ext:
            key = {"variant": "variantId", "ship_file": "hullId"}.get(kind, "id")
            return any(rel.endswith(ext[kind]) and isinstance(o, dict) and o.get(key) == k for rel, o in s.json.items())
        if kind == "faction":
            return any(rel.endswith(".faction") and isinstance(o, dict) and o.get("id") == k for rel, o in s.json.items())
        files = {"entity": "data/config/custom_entities.json", "engine_style": "data/config/engine_styles.json",
                 "hull_style": "data/config/hull_styles.json", "shipname_src": "data/strings/ship_names.json"}
        obj = s.json.get(files.get(kind, ""))
        return isinstance(obj, dict) and k in obj

    # .............................................................................. hulls
    def check_hulls(self):
        r = self.r
        hints_ok = self.enums.get("ShipTypeHints", set())
        mod_rows = {k: v for k, v in self.mod_ids["hull"].items() if not v.get("_skin")}
        mod_ships = self.mod_ids["ship_file"]
        for hid, row in mod_rows.items():
            where = "data/hulls/ship_data.csv line %s (%s)" % (row.get("_line"), hid)
            if hid not in self.reg["ship_file"]:
                r.error("no .ship file with hullId '%s' (the hull cannot load)" % hid, where)
            num_cols = ["fleet pts", "hitpoints", "armor rating", "max flux", "flux dissipation", "ordnance points",
                        "max speed", "acceleration", "deceleration", "max turn rate", "turn acceleration", "mass",
                        "supplies/rec", "supplies/mo", "cr %/day", "peak CR sec", "CR loss/sec", "min crew", "max crew",
                        "cargo", "fuel", "fuel/ly", "max burn", "base value"]
            for c in num_cols:
                v = (row.get(c) or "").strip()
                if v and _num(v) is None:
                    r.error("column '%s' is not a number: %r (NumberFormatException at load)" % (c, v), where)
            sf = self.reg["ship_file"].get(hid)
            fighter = bool(sf) and sf[0][0].get("hullSize") == "FIGHTER"   # vanilla fighters: 0 OP, 0 supplies
            for c in (("hitpoints",) if fighter else ("supplies/rec", "ordnance points", "hitpoints")):
                if _num(row.get(c)) is not None and _num(row.get(c)) <= 0:
                    r.error("'%s' must be positive" % c, where)
            st = (row.get("shield type") or "").strip()
            if st and st not in self.enums["ShieldType"]:
                r.error("shield type '%s' is not one of %s" % (st, sorted(self.enums["ShieldType"])), where)
            for c in ("system id", "defense id"):
                v = (row.get(c) or "").strip()
                if v and not self.has("system", v):
                    r.error("%s '%s' is not a known ship system" % (c, v), where)
            for h in _split(row.get("hints")):
                if hints_ok and h not in hints_ok:
                    r.error("unknown hint '%s' (valid: ShipHullSpecAPI.ShipTypeHints)" % h, where)
            bays = _num(row.get("fighter bays")) or 0
            if bays >= 8:
                r.error("%d fighter bays: 8 or more breaks the game (wiki)" % bays, where)
            elif bays == 7:
                r.warn("7 fighter bays causes graphical quirks (wiki: 6 is the safe maximum)", where)
            cv = (row.get("codex variant id") or "").strip()
            if cv and not self.has("variant", cv):
                r.error("codex variant id '%s' does not exist" % cv, where)
            if not self.has("desc", (hid, "SHIP")) and "MODULE" not in _split(row.get("hints")):
                r.warn("no descriptions.csv row (%s, SHIP): the codex and refit screen show no text" % hid, where)
            tags = set(_split(row.get("tags")))
            if not any(t.endswith("_bp") for t in tags) and not self._known_by_some_faction(hid, tags):
                r.note("hull is in no blueprint package (*_bp tag) and no faction knows it: players only get it "
                       "from scripts/quests", where)
        for hid, (ship, rel) in mod_ships.items():
            self._check_ship_file(hid, ship, rel, mod_rows.get(hid) or self.reg["hull"].get(hid, (None,))[0])
        for sid, (skin, rel) in self.mod_ids["skin"].items():
            b = skin.get("baseHullId")
            if not b or b not in self.reg["ship_file"]:
                r.error("baseHullId '%s' has no .ship file" % b, rel)
                continue
            base_slots = {s.get("id") for s in self.reg["ship_file"][b][0][0].get("weaponSlots", [])}
            for k in ("removeWeaponSlots",):
                for slot in skin.get(k, []) or []:
                    if slot not in base_slots:
                        r.error("%s names slot '%s' that %s does not have" % (k, slot, b), rel)
            for slot in (skin.get("weaponSlotChanges") or {}):
                if slot not in base_slots:
                    r.error("weaponSlotChanges names slot '%s' that %s does not have" % (slot, b), rel)
            if skin.get("spriteName"):
                self.path_ok(skin["spriteName"], rel, "sprite")
            for m in (skin.get("builtInMods") or []):
                if not self.has("hullmod", m):
                    r.error("unknown built-in hullmod '%s'" % m, rel)
            for slot, w in (skin.get("builtInWeapons") or {}).items():
                if not self.has("weapon", w):
                    r.error("unknown built-in weapon '%s'" % w, rel)
            if skin.get("systemId") and not self.has("system", skin["systemId"]):
                r.error("unknown systemId '%s'" % skin["systemId"], rel)
            if os.path.basename(rel)[:-5] != sid:
                r.note("file name differs from skinHullId '%s' (allowed; vanilla does it once)" % sid, rel)

    def _known_by_some_faction(self, hid, tags):
        for fid, (f, rel) in self.reg["faction_file"].items():
            ks = f.get("knownShips", {}) if isinstance(f, dict) else {}
            if hid in (ks.get("hulls") or []) or tags & set(ks.get("tags") or []):
                return True
        return False

    def _check_ship_file(self, hid, sh, rel, row):
        r = self.r
        if os.path.basename(rel)[:-5] != hid:
            r.note("file name differs from hullId '%s' (allowed: the game indexes by hullId)" % hid, rel)
        if row is None:
            r.warn("hullId '%s' has no ship_data.csv row (log: 'Ship hull spec [%s] not found in ship_data.csv')"
                   % (hid, hid), rel)
        size = sh.get("hullSize")
        if size not in ("FIGHTER", "FRIGATE", "DESTROYER", "CRUISER", "CAPITAL_SHIP"):
            r.error("hullSize '%s' is invalid" % size, rel)
        style = sh.get("style")
        if style and not self.has("hull_style", style):
            r.error("style '%s' is not in hull_styles.json" % style, rel)
        for m in sh.get("builtInMods", []) or []:
            if not self.has("hullmod", m):
                r.error("unknown built-in hullmod '%s'" % m, rel)
        slots = {}
        for s in sh.get("weaponSlots", []) or []:
            sid = s.get("id")
            if sid in slots:
                r.error("duplicate weapon slot id '%s'" % sid, rel)
            slots[sid] = s
            if s.get("mount") not in ("TURRET", "HARDPOINT", "HIDDEN"):
                r.error("slot %s: mount '%s' invalid" % (sid, s.get("mount")), rel)
            if s.get("size") not in SIZE_N:
                r.error("slot %s: size '%s' invalid" % (sid, s.get("size")), rel)
            wt = self.enums.get("WeaponType")
            if wt and s.get("type") not in wt:
                r.error("slot %s: type '%s' invalid" % (sid, s.get("type")), rel)
            arc = _num(s.get("arc"))
            if arc is None or not (0 <= arc <= 360):
                r.error("slot %s: arc %s outside 0-360" % (sid, s.get("arc")), rel)
            loc = s.get("locations") or []
            if len(loc) < 2 or len(loc) % 2:
                r.error("slot %s: 'locations' must hold x,y pairs" % sid, rel)
        for slot, w in (sh.get("builtInWeapons") or {}).items():
            if slot not in slots:
                r.error("builtInWeapons uses slot '%s' that does not exist" % slot, rel)
            if not self.has("weapon", w):
                r.error("unknown built-in weapon '%s'" % w, rel)
        for w in sh.get("builtInWings", []) or []:
            if not self.has("wing", w):
                r.error("unknown built-in wing '%s'" % w, rel)
        for i, e in enumerate(sh.get("engineSlots", []) or []):
            st = e.get("style")
            if st != "CUSTOM" and not self.has("engine_style", st):
                r.error("engine %d: style '%s' is not in engine_styles.json" % (i, st), rel)
            if st == "CUSTOM" and not isinstance(e.get("styleSpec"), dict):
                r.error("engine %d: style CUSTOM needs a styleSpec object" % i, rel)
            for k in ("width", "length"):
                if (_num(e.get(k)) or 0) <= 0:
                    r.error("engine %d: %s must be > 0" % (i, k), rel)
        sp = sh.get("spriteName")
        if not sp:
            r.error("no spriteName", rel)
            return
        if not self.path_ok(sp, rel, "sprite"):
            return
        ap = self.abs_path(sp)
        dims = image_size(ap) if ap else None
        if not dims:
            return
        W, H = dims
        if (W, H) != (_num(sh.get("width")), _num(sh.get("height"))):
            r.error("sprite is %dx%d but .ship width/height say %sx%s" % (W, H, sh.get("width"), sh.get("height")), rel)
        center = sh.get("center") or [0, 0]
        cx, cy = _num(center[0]) or 0, _num(center[1]) or 0
        if not (0 <= cx <= W and 0 <= cy <= H):
            r.error("center %s lies outside the %dx%d sprite" % (center, W, H), rel)
        alpha = None
        if Image is not None:
            try:
                with Image.open(ap) as im:
                    alpha = im.convert("RGBA").split()[3].load()
            except Exception:
                alpha = None

        def to_img(x, y):
            return sslib.ship_to_image(x, y, (cx, cy), H)

        def opaque(px, py, rad=1):
            if alpha is None:
                return True
            for dx in range(-rad, rad + 1):
                for dy in range(-rad, rad + 1):
                    qx, qy = int(round(px)) + dx, int(round(py)) + dy
                    if 0 <= qx < W and 0 <= qy < H and alpha[qx, qy] > 40:
                        return True
            return False

        for sid, s in slots.items():
            loc = s.get("locations") or []
            for k in range(0, len(loc) - 1, 2):
                px, py = to_img(_num(loc[k]) or 0, _num(loc[k + 1]) or 0)
                if not (-2 <= px <= W + 2 and -2 <= py <= H + 2):
                    r.error("slot %s at (%s, %s) lies outside the sprite" % (sid, loc[k], loc[k + 1]), rel)
                elif s.get("mount") in ("TURRET", "HARDPOINT") and s.get("type") not in ("LAUNCH_BAY", "SYSTEM", "DECORATIVE") \
                        and not opaque(px, py):
                    r.warn("slot %s sits over transparent pixels (weapon will float off the hull)" % sid, rel)
        for i, e in enumerate(sh.get("engineSlots", []) or []):
            loc = e.get("location") or [0, 0]
            px, py = to_img(_num(loc[0]) or 0, _num(loc[1]) or 0)
            if not (-4 <= px <= W + 4 and -4 <= py <= H + 4):
                r.error("engine %d at %s lies outside the sprite" % (i, loc), rel)
        sc = sh.get("shieldCenter") or [0, 0]
        px, py = to_img(_num(sc[0]) or 0, _num(sc[1]) or 0)
        if not (0 <= px <= W and 0 <= py <= H):
            r.warn("shieldCenter %s lies outside the sprite" % sc, rel)
        b = sh.get("bounds") or []
        if len(b) < 6 or len(b) % 2:
            r.error("bounds must hold at least 3 x,y points", rel)
        else:
            ext = 0.0
            for k in range(0, len(b) - 1, 2):
                x, y = _num(b[k]) or 0, _num(b[k + 1]) or 0
                ext = max(ext, (x * x + y * y) ** 0.5)
                px, py = to_img(x, y)
                if not (-4 <= px <= W + 4 and -4 <= py <= H + 4):
                    r.error("bounds point (%s, %s) lies outside the sprite" % (b[k], b[k + 1]), rel)
                    break
            cr = _num(sh.get("collisionRadius")) or 0
            if cr < ext - 0.5:
                r.error("collisionRadius %s is smaller than the bounds extent %.1f" % (sh.get("collisionRadius"), ext), rel)
        if (_num(sh.get("shieldRadius")) or 0) <= 0 and row and (row.get("shield type") or "").strip() in ("FRONT", "OMNI"):
            r.error("shieldRadius must be > 0 for a shielded hull", rel)

    # .............................................................................. weapons + projectiles
    def check_weapons(self):
        r = self.r
        hints_ok = self.enums.get("AIHints", set())
        mod_rows = self.mod_ids["weapon"]
        for wid, row in mod_rows.items():
            where = "data/weapons/weapon_data.csv line %s (%s)" % (row.get("_line"), wid)
            if wid not in self.reg["wpn"]:
                r.error("no .wpn file with id '%s' (log: 'Weapon spec [%s] not found!')" % (wid, wid), where)
            if _num(row.get("OPs")) is None:
                r.error("OPs is not a number", where)
            for c in ("range", "damage/shot", "damage/second", "energy/shot", "energy/second", "chargeup", "chargedown",
                      "burst size", "burst delay", "proj speed", "ammo", "ammo/sec", "reload size", "turn rate", "emp",
                      "impact", "base value", "tier", "rarity"):
                v = (row.get(c) or "").strip()
                if v and _num(v) is None:
                    r.error("column '%s' is not a number: %r" % (c, v), where)
            if (row.get("type") or "").strip() not in self.enums["damage_type"]:
                r.error("damage type '%s' invalid" % row.get("type"), where)
            for h in _split(row.get("hints")):
                if hints_ok and h not in hints_ok:
                    r.error("unknown hint '%s' (valid: WeaponAPI.AIHints)" % h, where)
            tags = _split(row.get("tags"))
            if not any(AUTOFIT_TAG.match(t) for t in tags) and "SYSTEM" not in _split(row.get("hints")):
                r.warn("no autofit tag (kinetic#, he#, energy#, pd#, beam#, strike#, missile#, rocket#, utility#): "
                       "autofit and the fleet inflater ignore the weapon", where)
            if not self.has("desc", (wid, "WEAPON")):
                r.warn("no descriptions.csv row (%s, WEAPON)" % wid, where)
        for wid, (spec, rel) in self.mod_ids["wpn"].items():
            if wid not in self.reg["weapon"]:
                r.error("no weapon_data.csv row for '%s'" % wid, rel)
            if os.path.basename(rel)[:-4] != wid:
                r.note("file name differs from id '%s' (allowed)" % wid, rel)
            wt = self.enums.get("WeaponType")
            if wt and spec.get("type") not in wt:
                r.error("type '%s' invalid" % spec.get("type"), rel)
            if spec.get("size") not in SIZE_N:
                r.error("size '%s' invalid" % spec.get("size"), rel)
            if spec.get("specClass") not in self.enums["specClass"]:
                r.error("specClass '%s' invalid (vanilla uses %s)" % (spec.get("specClass"), sorted(self.enums["specClass"])), rel)
            for k in ("turretSprite", "hardpointSprite", "turretGunSprite", "hardpointGunSprite", "turretGlowSprite",
                      "hardpointGlowSprite", "turretUnderSprite", "hardpointUnderSprite"):
                if spec.get(k):
                    if self.path_ok(spec[k], rel, k):
                        ap = self.abs_path(spec[k])
                        dims = image_size(ap) if ap else None
                        if dims and dims[0] % 2 and k in ("turretSprite", "hardpointSprite"):
                            r.warn("%s is %d px wide: odd-width weapon sprites blur (wiki); use an even width"
                                   % (k, dims[0]), rel)
            for mount in ("turret", "hardpoint"):
                offs = spec.get(mount + "Offsets") or []
                angs = spec.get(mount + "AngleOffsets") or []
                if len(offs) % 2:
                    r.error("%sOffsets must hold x,y pairs" % mount, rel)
                if offs and len(offs) // 2 != len(angs):
                    r.error("%sOffsets has %d barrels but %sAngleOffsets has %d (crash: 'Index: 1, Size: 1')"
                            % (mount, len(offs) // 2, mount, len(angs)), rel)
            if spec.get("specClass") == "projectile":
                pid = spec.get("projectileSpecId")
                if not pid or not self.has("proj", pid):
                    r.error("projectileSpecId '%s' is not a known .proj id" % pid, rel)
            for k in ("fireSoundOne", "fireSoundTwo"):
                if spec.get(k) and not self.has("sound", spec[k]):
                    r.error("%s '%s' is not in sounds.json" % (k, spec[k]), rel)
            for k in ("everyFrameEffect", "onFireEffect", "beamEffect", "onHitEffect"):
                if spec.get(k):
                    self.class_ok(spec[k], rel, k)
            if spec.get("textureType") and isinstance(spec["textureType"], list):
                for t in spec["textureType"]:
                    if isinstance(t, str) and t.startswith("graphics/"):
                        self.path_ok(t, rel, "beam texture")
        for pid, (proj, rel) in self.mod_ids["proj"].items():
            for k in ("spriteName", "sprite", "bulletSprite", "glowSprite"):
                if proj.get(k) and isinstance(proj[k], str):
                    self.path_ok(proj[k], rel, k)
            for k in ("onHitEffect", "onFireEffect"):
                if proj.get(k):
                    self.class_ok(proj[k], rel, k)
            for k, v in (proj.get("engineSpec") or {}).items() if isinstance(proj.get("engineSpec"), dict) else []:
                pass
            if proj.get("behaviorSpec") and isinstance(proj["behaviorSpec"], dict):
                for k, v in proj["behaviorSpec"].items():
                    if k.endswith("Sound") and isinstance(v, str) and not self.has("sound", v):
                        r.error("behaviorSpec.%s '%s' is not in sounds.json" % (k, v), rel)

    # .............................................................................. variants
    def check_variants(self):
        r = self.r
        maxs = 3
        for vid, (v, rel) in self.mod_ids["variant"].items():
            if os.path.basename(rel)[:-8] != vid:
                r.note("file name differs from variantId '%s' (allowed: the game indexes by variantId)" % vid, rel)
            hid = v.get("hullId")
            spec = self.ship_spec(hid) if hid else None
            if not spec:
                r.error("hullId '%s' is not a known hull or skin with a .ship file" % hid, rel)
                continue
            ship, row, skin = spec
            size = ship.get("hullSize")
            slots = {s.get("id"): s for s in ship.get("weaponSlots", [])}
            builtin_w = set((ship.get("builtInWeapons") or {}).keys())
            builtin_m = set(ship.get("builtInMods", []) or [])
            if not v.get("displayName"):
                r.warn("no displayName", rel)
            q = _num(v.get("quality"))
            if q is not None and not (0 <= q <= 1):
                r.warn("quality %s outside 0..1" % v.get("quality"), rel)
            op = 0.0
            used = set()
            for g in v.get("weaponGroups", []) or []:
                if g.get("mode") not in ("LINKED", "ALTERNATING"):
                    r.error("weapon group mode '%s' must be LINKED or ALTERNATING" % g.get("mode"), rel)
                for sid, wid in (g.get("weapons") or {}).items():
                    if sid in used:
                        r.error("slot %s is in two weapon groups" % sid, rel)
                    used.add(sid)
                    if sid not in slots:
                        r.error("slot '%s' does not exist on %s" % (sid, hid), rel)
                        continue
                    if not self.has("wpn", wid) or not self.has("weapon", wid):
                        r.error("unknown weapon '%s' (log: 'Weapon spec [%s] not found!')" % (wid, wid), rel)
                        continue
                    if sid in builtin_w:
                        continue
                    sl = slots[sid]
                    ws = self.reg["wpn"][wid][0][0]
                    if sl.get("type") in SLOT_COMPAT:
                        if ws.get("type") not in SLOT_COMPAT[sl["type"]]:
                            r.error("%s (%s) cannot mount in %s slot %s" % (wid, ws.get("type"), sl["type"], sid), rel)
                        d = SIZE_N.get(sl.get("size"), 9) - SIZE_N.get(ws.get("size"), 9)
                        if d not in (0, 1):
                            r.error("%s (%s) is illegal in %s slot %s (same size or one smaller only)"
                                    % (wid, ws.get("size"), sl.get("size"), sid), rel)
                    wrow = self.reg["weapon"][wid][0]
                    op += _num(wrow.get("OPs")) or 0
            smods = set(v.get("sMods", []) or [])
            if len(smods) > maxs:
                r.warn("%d s-mods (vanilla variants use at most %d)" % (len(smods), maxs), rel)
            for m in list(v.get("hullMods", []) or []) + list(smods) + list(v.get("permaMods", []) or []):
                if not self.has("hullmod", m):
                    r.error("unknown hullmod '%s'" % m, rel)
            for m in v.get("hullMods", []) or []:
                if m in builtin_m or m in smods or not self.has("hullmod", m):
                    continue
                hm = self.reg["hullmod"][m][0]
                if (hm.get("hidden") or "").strip().upper() == "TRUE":
                    r.warn("hidden hullmod '%s' on a variant (it is not a built-in of the hull)" % m, rel)
                op += _num(hm.get(HMOD_COST.get(size, ""))) or 0
            bays = _num((row or {}).get("fighter bays")) or 0
            if skin and skin.get("fighterBays") is not None:
                bays = _num(skin.get("fighterBays")) or 0
            builtin_wings = list(ship.get("builtInWings", []) or [])
            wings = list(v.get("wings", []) or [])
            for w in wings:
                if not self.has("wing", w):
                    r.error("unknown wing '%s'" % w, rel)
            if len(wings) > bays:
                r.error("%d wings but the hull has %d fighter bays" % (len(wings), bays), rel)
            for i, w in enumerate(wings):
                if i < len(builtin_wings) or not self.has("wing", w):
                    continue
                op += _num(self.reg["wing"][w][0].get("op cost")) or 0
            vents, caps = _num(v.get("fluxVents")) or 0, _num(v.get("fluxCapacitors")) or 0
            mx = MAX_VENTS.get(size, 50)
            if vents > mx or caps > mx:
                r.error("vents %d / capacitors %d exceed the %s maximum %d" % (vents, caps, size, mx), rel)
            op += vents + caps
            hop = _num((row or {}).get("ordnance points"))
            if skin and skin.get("ordnancePoints") is not None:
                hop = _num(skin.get("ordnancePoints"))
            if hop is not None:
                if op > hop + 1e-6:
                    r.error("uses %.0f OP but %s has %.0f" % (op, hid, hop), rel)
                elif op < hop - 10 and not v.get("goalVariant") is False:
                    r.note("%.0f of %.0f OP unused" % (hop - op, hop), rel)
            for mslot, mvar in (v.get("modules") or {}).items() if isinstance(v.get("modules"), dict) else \
                    [(k, val) for d in (v.get("modules") or []) if isinstance(d, dict) for k, val in d.items()]:
                if mslot not in slots:
                    r.error("module slot '%s' does not exist on %s" % (mslot, hid), rel)
                if not self.has("variant", mvar):
                    r.error("module variant '%s' does not exist" % mvar, rel)

    # .............................................................................. wings
    def check_wings(self):
        r = self.r
        for wid, row in self.mod_ids["wing"].items():
            where = "data/hulls/wing_data.csv line %s (%s)" % (row.get("_line"), wid)
            var = (row.get("variant") or "").strip()
            if not self.has("variant", var):
                r.error("variant '%s' does not exist" % var, where)
            else:
                v = self.reg["variant"][var][0][0]
                sp = self.ship_spec(v.get("hullId"))
                if sp and sp[0].get("hullSize") != "FIGHTER":
                    r.error("wing variant '%s' is not on a FIGHTER hull" % var, where)
            for c in ("op cost", "num", "refit", "range"):
                if _num(row.get(c)) is None:
                    r.error("column '%s' is not a number" % c, where)
            if (row.get("role") or "").strip() not in {x[0].get("role", "").strip() for x in self.reg["wing"].values()
                                                       if isinstance(x[0], dict)}:
                r.warn("role '%s' is not used by any other wing" % row.get("role"), where)
            if not any(AUTOFIT_TAG.match(t) or t.endswith("_bp") for t in _split(row.get("tags"))):
                r.note("no autofit/blueprint tags; fleets and autofit may never pick it", where)

    # .............................................................................. factions
    def check_factions(self):
        r = self.r
        listed = self._listed_faction_files(self.modsrc)
        for row in self.modsrc.rows("data/world/factions/factions.csv", "faction"):
            self.path_ok(row["faction"].strip(), "data/world/factions/factions.csv", "faction file")
        all_weapon_rows = {k: v[0] for k, v in self.reg["weapon"].items()}
        all_hmods = {k: v[0] for k, v in self.reg["hullmod"].items()}
        roles = self.modsrc.json.get("data/world/factions/default_ship_roles.json") or {}
        role_variants = {vid for vs in roles.values() if isinstance(vs, dict) for vid in vs}
        for rel, f in self.modsrc.json.items():
            if not rel.endswith(".faction") or not isinstance(f, dict):
                continue
            patch = any(rel in s.json for s in self.sources[:-1])
            if not patch and rel not in listed:
                r.error("faction file is not listed in data/world/factions/factions.csv (it will not load)", rel)
            fid = f.get("id")
            if not patch:
                for k in ("id", "displayName", "displayNameWithArticle", "logo", "names", "portraits", "color"):
                    if k not in f:
                        r.error("new faction lacks '%s'" % k, rel)
                if fid and not self.has("desc", (fid, "FACTION")):
                    r.warn("no descriptions.csv row (%s, FACTION)" % fid, rel)
            for k in ("logo", "crest"):
                if f.get(k):
                    self.path_ok(f[k], rel, k)
            ks, kw = f.get("knownShips") or {}, f.get("knownWeapons") or {}
            for h in (ks.get("hulls") or []) + ((f.get("priorityShips") or {}).get("hulls") or []):
                if not self.has("hull", h):
                    r.error("knownShips/priorityShips: unknown hull '%s'" % h, rel)
            for w in (kw.get("weapons") or []) + ((f.get("priorityWeapons") or {}).get("weapons") or []):
                if not self.has("weapon", w):
                    r.error("knownWeapons: unknown weapon '%s' (fleet spawn throws 'Weapon with spec id [%s] not "
                            "found')" % (w, w), rel)
            for w in ((f.get("knownFighters") or {}).get("fighters") or []):
                if not self.has("wing", w):
                    r.error("knownFighters: unknown wing '%s' (fleet spawn throws)" % w, rel)
            for m in ((f.get("knownHullMods") or {}).get("hullMods") or []):
                if not self.has("hullmod", m):
                    r.error("knownHullMods: unknown hullmod '%s'" % m, rel)
            for key, kind in (("weaponSellFrequency", "weapon"), ("shipSellFrequency", "hull"),
                              ("fighterSellFrequency", "wing"), ("hullmodSellFrequency", "hullmod"),
                              ("hullFrequency", None)):
                block = f.get(key)
                if isinstance(block, dict) and kind:
                    for k in block:
                        if not self.has(kind, k):
                            r.error("%s: unknown %s '%s'" % (key, kind, k), rel)
            for k in (f.get("shipNameSources") or {}):
                if not self.has("shipname_src", k):
                    r.error("shipNameSources: '%s' is not in ship_names.json" % k, rel)
            for k in (f.get("names") or {}):
                if not self.has("person_name_cat", k):
                    r.error("names: '%s' is not a person_names.csv category" % k, rel)
            for lst in (f.get("portraits") or {}).values():
                for p in lst if isinstance(lst, list) else []:
                    self.path_ok(p, rel, "portrait")
            for k, m in (f.get("music") or {}).items():
                if isinstance(m, str) and not self.has("music", m):
                    r.error("music.%s '%s' is not a music id in sounds.json" % (k, m), rel)
            for c in f.get("illegalCommodities", []) or []:
                if not self.has("commodity", c):
                    r.error("illegalCommodities: unknown commodity '%s'" % c, rel)
            for role, vs in (f.get("variantOverrides") or {}).items() if isinstance(f.get("variantOverrides"), dict) else []:
                pass
            # role variants this faction will spawn must use gear it knows, or the fleet inflater refits them
            if not fid:
                continue
            known_hulls = set(ks.get("hulls") or [])
            hull_tags = set(ks.get("tags") or [])
            kws = set(kw.get("weapons") or [])
            wtags = set(kw.get("tags") or [])
            kws |= {wid for wid, row in all_weapon_rows.items() if wtags & set(_split(row.get("tags")))}
            khm = set((f.get("knownHullMods") or {}).get("hullMods") or [])
            htags = set((f.get("knownHullMods") or {}).get("tags") or [])
            khm |= {mid for mid, row in all_hmods.items() if isinstance(row, dict) and htags & set(_split(row.get("tags")))}
            for vid in role_variants:
                if not self.has("variant", vid):
                    continue
                v = self.reg["variant"][vid][0][0]
                hid = v.get("hullId")
                hrow = self.reg["hull"].get(hid, ({},))[0] or {}
                if hid not in known_hulls and not (hull_tags & set(_split(hrow.get("tags") if isinstance(hrow, dict) else ""))):
                    continue
                spec = self.ship_spec(hid)
                bi_w = set(((spec or ({},))[0].get("builtInWeapons") or {}).values()) if spec else set()
                bi_m = set((spec or ({},))[0].get("builtInMods") or []) if spec else set()
                for g in v.get("weaponGroups", []) or []:
                    for wid in (g.get("weapons") or {}).values():
                        if wid not in kws and wid not in bi_w:
                            r.warn("%s spawns role variant %s with weapon '%s' it does not know: the fleet inflater "
                                   "refits from known weapons, so the loadout will not match" % (fid, vid, wid), rel)
                for m in v.get("hullMods", []) or []:
                    if m not in khm and m not in bi_m:
                        r.warn("%s spawns role variant %s with hullmod '%s' it does not know" % (fid, vid, m), rel)

    # .............................................................................. default_ship_roles.json
    def check_roles(self):
        r = self.r
        rel = "data/world/factions/default_ship_roles.json"
        roles = self.modsrc.json.get(rel)
        if roles is None:
            if self.mod_ids["variant"] and any(not (v[0].get("hullId") or "").endswith("_wing") for v in self.mod_ids["variant"].values()):
                r.note("no default_ship_roles.json: factions will never pick the mod's variants for random fleets", rel)
            return
        van_roles = set(self.sources[0].json.get(rel, {}).keys())
        for role, vs in roles.items():
            if van_roles and role not in van_roles:
                r.error("unknown role '%s' (vanilla roles: %s)" % (role, ", ".join(sorted(van_roles))), rel)
            if not isinstance(vs, dict):
                r.error("role '%s' must map variant ids to weights" % role, rel)
                continue
            for vid, wgt in vs.items():
                if not self.has("variant", vid):
                    r.error("role %s: unknown variant '%s'" % (role, vid), rel)
                if _num(wgt) is None:
                    r.error("role %s: weight for %s is not a number" % (role, vid), rel)

    # .............................................................................. ship systems
    def check_systems(self):
        r = self.r
        for sid, row in self.mod_ids["system"].items():
            where = "data/shipsystems/ship_systems.csv line %s (%s)" % (row.get("_line"), sid)
            if sid not in self.reg["system_file"]:
                r.error("no .system file with id '%s'" % sid, where)
            if row.get("icon"):
                self.path_ok(row["icon"].strip(), where, "icon")
            if not self.has("desc", (sid, "SHIP_SYSTEM")):
                r.warn("no descriptions.csv row (%s, SHIP_SYSTEM)" % sid, where)
        for sid, (sp, rel) in self.mod_ids["system_file"].items():
            if sid not in self.reg["system"]:
                r.error("no ship_systems.csv row for '%s'" % sid, rel)
            self.class_ok(sp.get("statsScript"), rel, "statsScript")
            ai = sp.get("aiType")
            if ai and ai not in self.enums["aiType"]:
                r.warn("aiType '%s' is not used by vanilla (%s)" % (ai, ", ".join(sorted(self.enums["aiType"]))), rel)
            if ai == "CUSTOM":
                if not sp.get("aiScript"):
                    r.error("aiType CUSTOM needs an aiScript class", rel)
                self.class_ok(sp.get("aiScript"), rel, "aiScript")
            for k in ("useSound", "loopSound", "deactivateSound", "outOfUsesSound"):
                if sp.get(k) and not self.has("sound", sp[k]):
                    r.error("%s '%s' is not in sounds.json" % (k, sp[k]), rel)

    # .............................................................................. hullmods
    def check_hullmods(self):
        r = self.r
        for hid, row in self.mod_ids["hullmod"].items():
            where = "data/hullmods/hull_mods.csv line %s (%s)" % (row.get("_line"), hid)
            self.class_ok((row.get("script") or "").strip(), where, "hullmod script")
            if row.get("sprite"):
                self.path_ok(row["sprite"].strip(), where, "sprite")
            for c in ("cost_frigate", "cost_dest", "cost_cruiser", "cost_capital"):
                v = (row.get(c) or "").strip()
                if v and _num(v) is None:
                    r.error("%s is not a number" % c, where)
            for c in ("hidden", "hiddenEverywhere", "unlocked"):
                v = (row.get(c) or "").strip().upper()
                if v and v not in ("TRUE", "FALSE"):
                    r.error("%s must be TRUE/FALSE" % c, where)
            if not (row.get("desc") or "").strip() and (row.get("hidden") or "").strip().upper() != "TRUE":
                r.warn("empty 'desc' column (the tooltip text)", where)
            # desc/short/sModDesc are passed through String.format: a bare % (e.g. "100% extends") crashes the refit
            # screen and the codex with IllegalFormatConversionException ("e != java.lang.String")
            for c in ("desc", "short", "sModDesc"):
                txt = row.get(c) or ""
                if re.search(r"%(?![s%])", txt):
                    r.error("'%s' has a bare %% sign: write %%%% for a literal percent (String.format crash)" % c,
                            where)

    # .............................................................................. campaign specs and plugins
    def check_campaign(self):
        r = self.r
        for kind in ("commodity", "condition", "industry", "submarket", "item", "ability", "skill"):
            rel = "data/" + REG_CSV[kind][0]
            hdr, _ = self.modsrc.csv(rel)
            if hdr is None:
                continue
            for k, row in self.mod_ids[kind].items():
                where = "%s line %s (%s)" % (rel, row.get("_line"), k)
                for col in hdr:
                    v = (row.get(col) or "").strip()
                    if not v:
                        continue
                    if col in ("script", "plugin", "class") or col.endswith("plugin"):
                        if re.match(r"^[a-z][\w]*(\.[\w$]+)+$", v):
                            self.class_ok(v, where, "%s class" % col)
                    elif col in ("icon", "sprite", "image") or v.startswith("graphics/"):
                        if "/" in v and re.search(r"\.(png|jpg|jpeg)$", v, re.I):
                            self.path_ok(v, where, col)
        # blueprint packages: MultiBlueprintItemPlugin gives every hull/weapon/wing carrying ALL its params tags
        for k, row in self.mod_ids["item"].items():
            if not (row.get("plugin") or "").strip().endswith("MultiBlueprintItemPlugin"):
                continue
            want = [t.strip() for t in (row.get("plugin params") or "").split(",") if t.strip()]
            if not want:
                continue
            n = 0
            for kind in ("hull", "weapon", "wing"):
                for v in self.reg[kind].values():
                    tags = {t.strip() for t in (v[0].get("tags") or "").split(",")}
                    if all((t[1:] not in tags) if t.startswith("!") else (t in tags) for t in want):
                        n += 1
            if n == 0:
                r.warn("blueprint package provides nothing: no hull, weapon or wing carries all of its plugin params "
                       "tags %s" % want, "data/campaign/special_items.csv line %s (%s)" % (row.get("_line"), k))
        ents = self.modsrc.json.get("data/config/custom_entities.json") or {}
        for eid, e in ents.items():
            if not isinstance(e, dict):
                continue
            for k in ("sprite", "icon", "interactionImage", "spriteName"):
                if isinstance(e.get(k), str):
                    self.path_ok(e[k], "custom_entities.json:%s" % eid, k)
            if e.get("pluginClass"):
                self.class_ok(e["pluginClass"], "custom_entities.json:%s" % eid, "pluginClass")
            cd = e.get("customDescriptionId")
            if cd and not self.has("desc", (cd, "CUSTOM")):
                r.error("customDescriptionId '%s' has no (id, CUSTOM) description" % cd, "custom_entities.json:%s" % eid)
        self._check_magic_bounties()

    def _check_magic_bounties(self):
        """MagicLib bounties ignore unknown keys and fail at runtime on unknown ids: check both statically."""
        r = self.r
        rel = "data/config/modFiles/magicBounty_data.json"
        data = self.modsrc.json.get(rel)
        if not isinstance(data, dict):
            return
        known_keys = set()
        for s in self.sources:
            p = os.path.join(s.root, "data", "config", "modFiles", "magicBounty_data_example.json")
            if os.path.isfile(p):
                try:
                    ex = sslib.load_loose_json(p)
                    for b in ex.values():
                        if isinstance(b, dict):
                            known_keys |= set(b)
                except Exception:
                    pass
        factions = set(self.reg["faction"]) | {"ML_bounty"}
        for bid, b in data.items():
            if not isinstance(b, dict):
                continue
            where = "%s:%s" % (rel, bid)
            if known_keys:
                for k in b:
                    if k not in known_keys:
                        close = difflib.get_close_matches(k, sorted(known_keys), n=1, cutoff=0.75)
                        r.error("unknown bounty key '%s'%s (MagicLib ignores it silently)"
                                % (k, "; did you mean '%s'?" % close[0] if close else ""), where)
            flag = b.get("fleet_flagship_variant")
            variants = (flag if isinstance(flag, list) else [flag] if flag else []) + list(
                (b.get("fleet_preset_ships") or {}).keys())
            if not flag and not b.get("existing_target_memkey"):
                r.error("no fleet_flagship_variant (required)", where)
            for v in variants:
                if not self.has("variant", v):
                    r.error("unknown variant '%s' (the bounty fails to spawn)" % v, where)
            for key in ("fleet_faction", "fleet_composition_faction", "job_forFaction"):
                f = b.get(key)
                if f and f not in factions:
                    r.error("%s: unknown faction '%s'" % (key, f), where)
            for f in (b.get("trigger_marketFaction_any") or []) + (b.get("trigger_marketFaction_none") or []):
                if f not in factions:
                    r.warn("trigger faction '%s' is not a known faction" % f, where)
            for item in (b.get("job_item_reward") or {}):
                if " " in item:   # Console Commands syntax: "ship_bp <id>", "weapon_bp <id>", ...
                    continue
                if not (self.has("commodity", item) or self.has("item", item)):
                    r.error("job_item_reward '%s' is neither a commodity nor a special item" % item, where)
            if isinstance(b.get("target_portrait"), str) and "/" in b["target_portrait"]:
                self.path_ok(b["target_portrait"], where, "target_portrait")

    # .............................................................................. settings.json, styles, LunaLib
    def check_settings(self):
        r = self.r
        rel = "data/config/settings.json"
        s = self.modsrc.json.get(rel) or {}
        for cat, entries in (s.get("graphics") or {}).items():
            if isinstance(entries, dict):
                for k, p in entries.items():
                    if isinstance(p, str):
                        self.path_ok(p, "%s graphics.%s.%s" % (rel, cat, k), "graphics")
        for k, cls in (s.get("plugins") or {}).items():
            if isinstance(cls, str):
                self.class_ok(cls, "%s plugins.%s" % (rel, k), "plugin")
        for pkg in s.get("ruleCommandPackages", []) or []:
            if not any(c.startswith(pkg + ".") for c in self.mod_classes):
                r.error("ruleCommandPackages entry '%s' has no compiled classes in the mod" % pkg, rel)
        for sid, st in (self.modsrc.json.get("data/config/hull_styles.json") or {}).items():
            for k, v in (st or {}).items() if isinstance(st, dict) else []:
                if isinstance(v, str) and v.startswith("graphics/"):
                    self.path_ok(v, "hull_styles.json:%s.%s" % (sid, k), "graphics")
        luna = "data/config/LunaSettings.csv"
        hdr, rows = self.modsrc.csv(luna)
        if hdr is not None:
            deps = {d.get("id") for d in self.info.get("dependencies", []) or [] if isinstance(d, dict)}
            deps.add(self.info.get("id"))
            if "lunalib" not in deps:
                r.warn("LunaSettings.csv present but lunalib is not a declared dependency (settings are ignored "
                       "without it; guard reads with isModEnabled(\"lunalib\"))", luna)
            seen = set()
            for row in rows:
                fid = (row.get("fieldID") or "").strip()
                if fid in seen:
                    r.error("duplicate fieldID '%s'" % fid, luna)
                seen.add(fid)
                if (row.get("fieldType") or "").strip() == "Header" and not (row.get("defaultValue") or "").strip():
                    r.warn("Header '%s' has an empty defaultValue: LunaLib shows defaultValue as the header's "
                           "title" % fid, luna)
                if (row.get("fieldType") or "").strip() not in LUNA_TYPES:
                    r.error("fieldType '%s' invalid (LunaLib accepts %s)" % (row.get("fieldType"), ", ".join(sorted(LUNA_TYPES))), luna)
                if self.prefix and fid and not fid.lower().startswith(self.prefix.lower().rstrip("_")):
                    r.warn("fieldID '%s' lacks the mod prefix (LunaLib ids are global per mod, but prefixing avoids "
                           "confusion in Java)" % fid, luna)

    # .............................................................................. rules.csv
    def check_rules(self):
        r = self.r
        rel = "data/campaign/rules.csv"
        hdr, rows = self.modsrc.csv(rel)
        if hdr is None:
            return
        if self.rules_header and hdr != self.rules_header:
            r.error("header differs from vanilla %s" % self.rules_header, rel)
        pkgs = []
        for s in self.sources:
            pkgs += (s.json.get("data/config/settings.json") or {}).get("ruleCommandPackages", []) or []
        cmds = {c.rsplit(".", 1)[1] for c in self.classes for p in pkgs if c.startswith(p + ".") and "$" not in c
                and c.rsplit(".", 1)[0] == p}
        handled, triggers = set(), set()
        for s in self.sources:
            for row in s.rows(rel):
                triggers.add(row.get("trigger", "").strip())
                if row.get("trigger", "").strip() == "DialogOptionSelected":
                    for m in re.finditer(r"\$option\s*==\s*([^\s]+)", row.get("conditions", "")):
                        handled.add(m.group(1))
        introduced = {}
        fired = []
        for row in self.modsrc.rows(rel):
            rid = row["id"].strip()
            where = "%s line %s (%s)" % (rel, row["_line"], rid)
            trig = row.get("trigger", "").strip()
            if not trig:
                r.error("empty trigger", where)
            if self.prefix and not rid.lower().startswith(self.prefix.lower()) and \
                    not any(rid in [x["id"].strip() for x in s.rows(rel)] for s in self.sources[:-1]):
                r.warn("rule id lacks the prefix '%s' (rule ids are global; collisions silently replace rules)" % self.prefix, where)
            for col in ("conditions", "script"):
                for line in (row.get(col) or "").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    first = line.split()[0].lstrip("!")
                    if first.startswith("$") or first in ("", "=", "=="):
                        continue
                    if first not in cmds:
                        r.error("%s: '%s' is not a rule command (no class in any ruleCommandPackages)" % (col, first), where)
                    if col == "script" and first in ("FireAll", "FireBest") and len(line.split()) > 1:
                        fired.append((where, line.split()[1]))
            for line in (row.get("options") or "").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split(":")
                oid = parts[1].strip() if len(parts) >= 3 and re.match(r"^-?\d+(\.\d+)?$", parts[0].strip()) else parts[0].strip()
                introduced.setdefault(oid, where)
        for oid, where in introduced.items():
            if oid not in handled:
                r.error("option '%s' has no DialogOptionSelected rule with '$option == %s' (dead button)" % (oid, oid), where)
        for where, t in fired:
            if t not in triggers:
                r.warn("fires trigger '%s' but no rule (mod or vanilla) uses it as a trigger" % t, where)
        for p in self._java_files():
            src = _read(p)
            if "BaseCommandPlugin" not in src:
                continue
            for m in re.finditer(r'addOption\(\s*[^,]+,\s*"([A-Za-z0-9_]+)"', src):
                if m.group(1) not in handled:
                    r.error("rule command adds dialog option '%s' but no rule handles it" % m.group(1), self._rel(p))

    # .............................................................................. Java sources
    def _java_files(self):
        return [os.path.join(self.mod, rel) for rel in self.modsrc.files if rel.endswith(".java")]

    def _rel(self, p):
        return os.path.relpath(p, self.mod).replace("\\", "/")

    # Fleet callbacks run while the engine iterates the fleet's listener list (CampaignEngine.reportBattleOccurred):
    # removing a listener or despawning a fleet from inside one throws ConcurrentModificationException = "Fatal: null"
    # after the battle (Resonance Lattice, 2026-10-13). Vanilla only removes listeners from advance()/end paths.
    FLEET_CALLBACKS = ("reportBattleOccurred", "reportFleetDespawnedToListener")
    CALLBACK_MUTATION = re.compile(r"\bremoveEventListener\s*\(|\.despawn\s*\(|\bdespawn\s*\(\s*\)")

    @staticmethod
    def _method_bodies(src):
        """{method name: body text} for every method in a Java source (brace matching, comments/strings stripped)."""
        clean = re.sub(r"//[^\n]*|/\*.*?\*/", "", src, flags=re.S)
        clean = re.sub(r'"(?:\\.|[^"\\])*"', '""', clean)
        bodies = {}
        for m in re.finditer(r"\b(\w+)\s*\([^;{}()]*(?:\([^()]*\)[^;{}()]*)*\)\s*(?:throws\s+[\w.,\s]+)?\{", clean):
            name = m.group(1)
            if name in ("if", "for", "while", "switch", "catch", "synchronized", "return", "new"):
                continue
            depth, i = 1, m.end()
            while i < len(clean) and depth:
                depth += {"{": 1, "}": -1}.get(clean[i], 0)
                i += 1
            bodies.setdefault(name, "")
            bodies[name] += clean[m.end():i]
        return bodies

    def _check_fleet_callbacks(self, src, rel):
        bodies = self._method_bodies(src)
        for cb in self.FLEET_CALLBACKS:
            if cb not in bodies:
                continue
            seen, todo = set(), [cb]
            while todo:   # follow calls into methods of the same file (helpers like endHunt())
                name = todo.pop()
                if name in seen:
                    continue
                seen.add(name)
                body = bodies.get(name, "")
                hit = self.CALLBACK_MUTATION.search(body)
                if hit:
                    via = "" if name == cb else " (via %s())" % name
                    self.r.error("%s()%s calls %s: the engine is iterating the fleet's listeners, so this throws "
                                 "ConcurrentModificationException after the battle; queue the fleet and do it in "
                                 "advance()" % (cb, via, hit.group(0).strip(" (.")), rel)
                    break
                for c in re.findall(r"(?<![.\w])(\w+)\s*\(", body):
                    if c in bodies and c not in seen:
                        todo.append(c)

    def check_java(self):
        r = self.r
        files = self._java_files()
        if not files:
            return
        whitelist = set(self.cfg.get("literal_whitelist", []) or [])
        known = set()
        for kind in list(REG_CSV) + ["variant", "proj", "faction", "entity", "wpn", "music", "sound"]:
            known |= set(self.reg[kind].keys())
        known |= {k[0] for k in self.reg["desc"]}
        luna_ids = {(row.get("fieldID") or "").strip() for row in self.modsrc.csv("data/config/LunaSettings.csv")[1]}
        known |= luna_ids
        dep_ids = {d.get("id") for d in self.info.get("dependencies", []) or [] if isinstance(d, dict)}
        dep_ids.add(self.info.get("id"))
        lib_pkgs = {"org.lazywizard": "lw_lazylib", "org.magiclib": "MagicLib", "data.scripts.util.Magic": "MagicLib",
                    "org.dark.shaders": "shaderLib", "lunalib": "lunalib", "exerelin": "nexerelin"}
        newest_src = 0
        all_src = ""
        unknown_lits = {}
        for p in files:
            src = _read(p)
            all_src += src
            newest_src = max(newest_src, os.path.getmtime(p))
            rel = self._rel(p)
            for name, val in re.findall(r'static\s+final\s+String\s+(\w+)\s*=\s*"([^"]*)"\s*;', src):
                if NOT_ID_CONST.search(name) or re.search(r"[/\\ .%]", val) or not val:
                    continue
                for pre, kind in ID_CONST_PREFIX:
                    if name.startswith(pre):
                        if not self.has(kind, val) and not (kind == "hull" and self.has("ship_file", val)):
                            r.error("constant %s = \"%s\" is not a known %s id" % (name, val, kind), rel)
                        break
            for rx, kind in JAVA_LOOKUPS:
                for m in re.finditer(rx, src):
                    k = m.group(1)
                    if not self.has(kind, k):
                        r.error("%s(\"%s\"): unknown %s id (null at runtime)" % (rx.split("\\(")[0], k, kind), rel)
            for m in re.finditer(r'setCustomDescriptionId\(\s*"([^"]+)"', src):
                if not self.has("desc", (m.group(1), "CUSTOM")):
                    r.error("custom description '%s' has no (id, CUSTOM) row in descriptions.csv" % m.group(1), rel)
            for m in GFX_REF.finditer(src):  # Java may load other mods' assets behind a runtime check: warn only
                ref = m.group(0)
                self.referenced_assets.add(ref)
                if ref not in self.files_exact:
                    actual = self.files_lower.get(ref.lower())
                    if actual:
                        r.error("asset path case differs from the file on disk: %s vs %s (crashes on Linux/macOS)"
                                % (ref, actual), rel)
                    elif ref.startswith("data/"):
                        r.note("loads %s at runtime; no installed source provides it (fine for merged CSVs other "
                               "mods supply)" % ref, rel)
                    else:
                        r.warn("asset referenced in code is missing: %s" % ref, rel)
            if self.prefix:
                for lit in re.findall(r'"(%s[A-Za-z0-9_]+)"' % re.escape(self.prefix), src):
                    if lit not in known and lit not in whitelist:
                        unknown_lits.setdefault(lit, rel)
            self._check_fleet_callbacks(src, rel)
            if re.search(r"\bjava\.io\.File\b|\bnew\s+File\(|FileInputStream|FileOutputStream|java\.nio\.file|"
                         r"java\.lang\.reflect|Class\.forName\(|MethodHandles", src):
                r.warn("file I/O or reflection: the game's script classloader restricts these (wiki); use "
                       "Global.getSettings() file methods instead", rel)
            for m in re.finditer(r"^\s*(?:(?:public|private|protected)\s+)?static\s+(?!final\b)(?!class\b)(?!interface\b)"
                                 r"(?!enum\b)(?!void\b)([\w<>\[\],.? ]+?)\s+(\w+)\s*(=|;)", src, re.M):
                typ = m.group(1).strip()
                if LEAKY_TYPE.search(typ) and not re.match(r"(Weak|Soft)Reference\b", typ):
                    r.warn("static field '%s %s' holds game objects: it survives loading another save and leaks the "
                           "old sector (wiki); use persistent data or instance fields" % (typ, m.group(2)), rel)
            for pkg, mid in lib_pkgs.items():
                uses = (re.search(r"^\s*import\s+%s" % re.escape(pkg), src, re.M)
                        or re.search(r"(?<![\w.\"])%s\.[a-z]+\.[A-Z]" % re.escape(pkg), src))   # fully qualified use
                if uses and mid not in dep_ids:
                    every = _read_all(files)
                    consts = re.findall(r'static\s+final\s+String\s+(\w+)\s*=\s*"%s"' % re.escape(mid), every)
                    guarded = 'isModEnabled("%s")' % mid in every or any(
                        re.search(r"isModEnabled\([\w.]*%s\)" % c, every) for c in consts)
                    if not guarded:
                        r.warn("imports %s classes but %s is not a dependency and no isModEnabled(\"%s\") guard was "
                               "found (NoClassDefFoundError when it is absent)" % (pkg, mid, mid), rel)
        # A prefixed string that is not a data id is usually an entity/market/stat/key id (fine). Flag only the ones
        # that look like a misspelt data id; list the rest once so they can be eyeballed or whitelisted.
        data_ids = sorted(k for k in known if isinstance(k, str) and self.prefix and k.lower().startswith(self.prefix.lower()))
        rest = []
        for lit, rel in sorted(unknown_lits.items()):
            close = difflib.get_close_matches(lit, data_ids, n=1, cutoff=0.88)
            if close:
                r.warn("string \"%s\" is not a data id; did you mean \"%s\"? (whitelist it if intended)" % (lit, close[0]), rel)
            else:
                rest.append(lit)
        if rest:
            r.note("%d prefixed strings in Java are not data ids (entity/market/stat/key ids are fine): %s"
                   % (len(rest), ", ".join(rest[:30]) + (" ..." if len(rest) > 30 else "")))
        jars = sslib.mod_jars(self.mod, self.info)
        if jars and newest_src:
            jt = min(os.path.getmtime(j) for j in jars)
            if jt < newest_src - 1:
                r.warn("jar is older than the newest Java source: rebuild before testing or packaging",
                       os.path.relpath(jars[0], self.mod).replace("\\", "/"))

    # .............................................................................. graphics
    def check_graphics(self):
        r = self.r
        for rel in self.modsrc.files:
            low = rel.lower()
            if not low.startswith("graphics/"):
                continue
            if low.endswith(".png"):
                pi = png_info(os.path.join(self.mod, rel))
                if not pi:
                    r.error("not a valid PNG", rel)
                    continue
                if pi[2] == 16:
                    r.error("16-bit PNG: the game's TextureLoader crashes (ArrayIndexOutOfBounds); save as 8-bit", rel)
                if pi[3] not in (2, 6):
                    r.warn("PNG colour type %d (vanilla only uses RGB/RGBA); convert to RGBA" % pi[3], rel)
            elif low.endswith((".psd", ".xcf", ".kra", ".blend")):
                r.warn("source art file inside graphics/ (ship it outside the mod folder)", rel)
        refs = set(self.referenced_assets)
        blobs = []
        for rel, obj in self.modsrc.json.items():
            blobs.append(json.dumps(obj))
        for rel in self.modsrc.files:
            if rel.lower().endswith((".csv", ".java", ".kt", ".json")):
                blobs.append(_read(os.path.join(self.mod, rel)))
        text = "\n".join(blobs)
        for m in GFX_REF.finditer(text):
            refs.add(m.group(0))
        settings = self.modsrc.json.get("data/config/settings.json") or {}
        for cat, entries in (settings.get("graphics") or {}).items():
            if isinstance(entries, dict):
                refs |= {p for p in entries.values() if isinstance(p, str)}
        refs_l = {x.lower() for x in refs}
        for rel in self.modsrc.files:
            low = rel.lower()
            if low.startswith("graphics/") and low.endswith((".png", ".jpg", ".jpeg")) and low not in refs_l:
                if "/shaders/" in low and any(low.startswith(x.lower()) for x in refs):
                    continue
                r.warn("asset is never referenced in data, settings or code (unused, or built dynamically?)", rel)

    # .............................................................................. sounds
    def check_sounds(self):
        r = self.r
        snd = self.modsrc.json.get("data/config/sounds.json")
        if isinstance(snd, dict):
            def walk_files(node, where):
                if isinstance(node, dict):
                    for k, v in node.items():
                        if k == "file" and isinstance(v, str):
                            self.path_ok(v, where, "sound file")
                        else:
                            walk_files(v, where + "." + k)
                elif isinstance(node, list):
                    for x in node:
                        walk_files(x, where)
            walk_files(snd, "sounds.json")
        for rel in self.modsrc.files:
            if rel.lower().startswith("sounds/") and rel.lower().endswith(".wav"):
                r.warn("WAV file: macOS builds cannot play .wav (wiki); use .ogg", rel)

        # MagicLib trails: colours are parsed item by item with Integer.parseInt and no trim
        trails = os.path.join(self.mod, "data", "config", "modFiles", "magicTrail_data.csv")
        if os.path.isfile(trails):
            with open(trails, encoding="utf-8", errors="replace") as f:
                for n, row in enumerate(csv.DictReader(f), 2):
                    for c in ("colorIn", "colorOut"):
                        v = (row.get(c) or "")
                        if v and " " in v:
                            r.error("MagicLib trail %s %r has spaces: write [r,g,b] (launch crash: For input string "
                                    "\" 255\")" % (c, v), "magicTrail_data.csv line %d" % n)

    # .............................................................................. descriptions
    def check_descriptions(self):
        r = self.r
        rel = "data/strings/descriptions.csv"
        seen = {}
        for row in self.modsrc.rows(rel):
            k = (row["id"].strip(), (row.get("type") or "").strip())
            if k in seen:
                r.error("duplicate (%s, %s) (lines %d and %d)" % (k[0], k[1], seen[k], row["_line"]), rel)
            seen[k] = row["_line"]
            if k[1] not in self.enums["desc_type"]:
                r.error("type '%s' is not a description type vanilla uses (%s)" % (k[1], ", ".join(sorted(self.enums["desc_type"]))),
                        "%s line %d" % (rel, row["_line"]))
        for fid in self.mod_ids["faction"]:
            pass

    # .............................................................................. GraphicsLib lights / texture data
    def check_lights(self):
        r = self.r
        glib = self.installed.get("shaderLib")
        core_light = core_tex = None
        if glib:
            core_light = Source("shaderLib", glib[0]).csv("data/lights/core_light_data.csv")[0]
            core_tex = Source("shaderLib", glib[0]).csv("data/lights/core_texture_data.csv")[0]
        mod_csvs = [rel for rel in self.modsrc.files if rel.startswith("data/lights/") and rel.endswith(".csv")]
        if not mod_csvs:
            return
        src = _read_all(self._java_files())
        for rel in mod_csvs:
            hdr, rows = self.modsrc.csv(rel)
            if hdr is None:
                continue
            is_tex = "map" in hdr and "path" in hdr
            ref = core_tex if is_tex else core_light
            if ref and hdr != ref:
                r.error("header differs from GraphicsLib's %s" % ("core_texture_data.csv" if is_tex else "core_light_data.csv"), rel)
            for row in rows:
                where = "%s line %d" % (rel, row["_line"])
                if is_tex:
                    if (row.get("map") or "").strip() not in ("normal", "material", "surface"):
                        r.error("map must be normal, material or surface", where)
                    self.path_ok((row.get("path") or "").strip(), where, "texture map")
                    tid = row["id"].strip()
                    styled = any(tid.endswith("_" + st) and (self.has("hull", tid[:-len(st) - 1]) or
                                                             self.has("ship_file", tid[:-len(st) - 1]))
                                 for st in self.reg["hull_style"])
                    if (row.get("type") or "").strip() == "ship" and not self.has("hull", tid) \
                            and not self.has("ship_file", tid) and not styled:
                        r.warn("ship '%s' is not a known hull id (ids may also be hullid_STYLEID; check spelling)" % tid, where)
                else:
                    t = (row.get("type") or "").strip()
                    if t == "projectile" and not self.has("proj", row["id"].strip()):
                        r.error("projectile '%s' unknown" % row["id"], where)
                    elif t == "beam" and not (self.has("wpn", row["id"].strip()) and
                                              self.reg["wpn"][row["id"].strip()][0][0].get("specClass") == "beam"):
                        r.error("'%s' is not a beam weapon" % row["id"], where)
                    elif t not in ("projectile", "beam"):
                        r.error("type must be projectile or beam", where)
            base = os.path.basename(rel)
            if base not in src and self.info.get("id") != "shaderLib":
                r.error("nothing in the Java sources loads %s (readLightDataCSV/readTextureDataCSV)" % rel, rel)
        if 'isModEnabled("shaderLib")' not in src and self.info.get("id") != "shaderLib" and "shaderLib" not in \
                {d.get("id") for d in self.info.get("dependencies", []) or [] if isinstance(d, dict)}:
            r.error("GraphicsLib data is present but no isModEnabled(\"shaderLib\") guard was found in Java "
                    "(NoClassDefFoundError without GraphicsLib)", "data/lights")


    # .............................................................................. missions
    def check_missions(self):
        """data/missions: every listed mission has its four files, a difficulty the mission list accepts and a
        256x256 icon (vanilla's size; other sizes are stretched)."""
        r = self.r
        hdr, rows = self.modsrc.csv("data/missions/mission_list.csv")
        if hdr is None:
            return
        for row in rows:
            mid = (row.get("mission") or "").strip()
            if not mid:
                continue
            d = "data/missions/" + mid
            for f in ("descriptor.json", "mission_text.txt", "MissionDefinition.java"):
                if not os.path.isfile(os.path.join(self.mod, d, f)):
                    r.error("mission '%s' has no %s" % (mid, f), d)
            desc = self.modsrc.json.get(d + "/descriptor.json") or {}
            diff = desc.get("difficulty")
            if diff is not None and diff not in MISSION_DIFFICULTIES:
                r.error("difficulty '%s' is not one vanilla uses (%s)" % (diff, ", ".join(MISSION_DIFFICULTIES)),
                        d + "/descriptor.json")
            icon = desc.get("icon")
            if icon:
                ip = os.path.join(self.mod, d, icon)
                if not os.path.isfile(ip):
                    r.error("icon '%s' not found (it is relative to the mission folder)" % icon, d + "/descriptor.json")
                else:
                    size = image_size(ip)
                    if size and tuple(size) != (256, 256):
                        r.warn("mission icon is %dx%d; vanilla's are 256x256 (others are stretched)" % tuple(size),
                               d + "/" + icon)
            txt = os.path.join(self.mod, d, "mission_text.txt")
            if os.path.isfile(txt):
                t = _read(txt)
                if "Location:" not in t and len(t) < 600:
                    r.note("mission text is short and has no 'Location:/Date:' header; vanilla's open with "
                           "Location and Date, then the story, *** and how to play it", d + "/mission_text.txt")
        # loose data/**/*.java is compiled by Janino at load: it resolves an interface's clone() (ShipVariantAPI,
        # FleetMemberAPI, ...) against Object.clone() and rejects it unless CloneNotSupportedException is caught
        # (crash "Error loading [data.missions.x.MissionDefinition]" on the mission screen). Arrays are fine.
        droot = os.path.join(self.mod, "data")
        for base, _dirs, files in os.walk(droot):
            for f in files:
                if not f.endswith(".java"):
                    continue
                fp = os.path.join(base, f)
                rel = os.path.relpath(fp, self.mod).replace(os.sep, "/")
                for i, line in enumerate(_read(fp).splitlines(), 1):
                    code = line.split("//", 1)[0]
                    if re.search(r"\)\s*\.\s*clone\s*\(\s*\)", code) and "catch" not in _read(fp):
                        r.error("'.clone()' on a method result in a loose script: Janino (the game's script "
                                "compiler) treats it as Object.clone() and fails with an uncaught "
                                "CloneNotSupportedException; move the code into the jar or wrap it in "
                                "try/catch (line %d)" % i, rel)


MISSION_DIFFICULTIES = ("EASY", "MEDIUM", "HARD", "IMPOSSIBLE", "VARIABLE")


# =============================================================================================== helpers
def _num(v):
    try:
        return float(str(v).strip())
    except (TypeError, ValueError):
        return None


def _split(v):
    return [t.strip() for t in (v or "").split(",") if t.strip()]


def _vtuple(v):
    out = []
    for part in re.split(r"[.\-]", str(v)):
        m = re.match(r"^(\d+)(.*)$", part)
        out.append((int(m.group(1)), m.group(2)) if m else (-1, part))
    return tuple(out)


_READ_CACHE = {}


def _read(p):
    if p not in _READ_CACHE:
        with open(p, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        _READ_CACHE[p] = strip_java_comments(text) if p.endswith((".java", ".kt")) else text
    return _READ_CACHE[p]


def strip_java_comments(text):
    """Remove // and /* */ comments, keeping string and char literals (and line numbers) intact."""
    out = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            j = text.find("\n", i)
            i = n if j < 0 else j
        elif c == "/" and i + 1 < n and text[i + 1] == "*":
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append("\n" * text.count("\n", i, j))
            i = j
        elif c in "\"'":
            j = i + 1
            while j < n and text[j] != c and text[j] != "\n":
                j += 2 if text[j] == "\\" else 1
            out.append(text[i:j + 1])
            i = j + 1
        else:
            out.append(c)
            i += 1
    return "".join(out)


def _read_all(files):
    return "\n".join(_read(p) for p in files)


def load_config(mod, path=None):
    for p in ([path] if path else [os.path.join(mod, "validate_config.json"), os.path.join(mod, "tools", "validate_config.json")]):
        if p and os.path.isfile(p):
            try:
                return sslib.load_loose_json(p), p
            except Exception as e:
                sys.exit("config %s does not parse: %s" % (p, e))
    return {}, None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mod", help="mod folder (default: the folder with mod_info.json at/above cwd)")
    ap.add_argument("--game", help="Starsector folder (default: auto-detect from the mod folder)")
    ap.add_argument("--prefix", help="required id prefix for new ids, e.g. xyz_")
    ap.add_argument("--config", help="config JSON (default <mod>/validate_config.json or <mod>/tools/validate_config.json)")
    ap.add_argument("--only", help="comma list of check groups")
    ap.add_argument("--strict", action="store_true", help="warnings also fail")
    ap.add_argument("--quiet", action="store_true", help="hide notes")
    ap.add_argument("--list-checks", action="store_true")
    a = ap.parse_args()
    if a.list_checks:
        print("\n".join(GROUPS))
        return 0
    mod = sslib.find_mod_root(a.mod or os.getcwd())
    if not mod:
        sys.exit("no mod_info.json at or above %s" % (a.mod or os.getcwd()))
    game = sslib.find_game_dir(a.game) if a.game else (sslib.find_game_dir(os.path.dirname(os.path.dirname(mod))) or
                                                      sslib.find_game_dir())
    if not game:
        sys.exit("Starsector install not found; pass --game")
    cfg, cfg_path = load_config(mod, a.config)
    if a.prefix:
        cfg["prefix"] = a.prefix
    rep = Report(cfg.get("ignore", []) or [])
    v = Validator(mod, game, cfg, rep)
    v.setup()
    only = set(a.only.split(",")) if a.only else None
    v.run(only)
    name = v.info.get("name", "?")
    print("validate_mod: %s (%s) %s" % (name, v.info.get("id", "?"), sslib.version_string(v.info.get("version"))))
    print("  mod  %s" % mod)
    print("  game %s (%s)%s" % (game, sslib.game_version(game) or "?", "  config " + cfg_path if cfg_path else ""))
    if v.deps:
        print("  deps " + ", ".join("%s %s" % (d[0], sslib.version_string(d[2].get("version"))) for d in v.deps))
    order = {"ERROR": 0, "WARN": 1, "note": 2}
    for level, group, msg, where in sorted(rep.items, key=lambda i: (order[i[0]], GROUPS.index(i[1]) if i[1] in GROUPS else 99)):
        if a.quiet and level == "note":
            continue
        print("%-5s %-12s %s%s" % (level, group, msg, ("   [%s]" % where) if where else ""))
    ne, nw, nn = rep.count("ERROR"), rep.count("WARN"), rep.count("note")
    print("\nvalidate_mod: %d error(s), %d warning(s), %d note(s)%s" % (ne, nw, nn, " (strict)" if a.strict else ""))
    return 1 if ne or (a.strict and nw) else 0


if __name__ == "__main__":
    sys.exit(main())
