#!/usr/bin/env python3
"""log_scan.py - read starsector.log after someone ran the game: what broke, which mod, and the likely fix.

    python log_scan.py                          # last launch in <game>/starsector-core/starsector.log
    python log_scan.py --mod path/to/MyMod      # put entries that mention this mod (id, folder, prefix, package) first
    python log_scan.py --run all --errors-only  # every launch in the file
    python log_scan.py --log some/other.log

The log format is `<ms since launch> [<thread>] <LEVEL> <logger>  - <message>`, with stack-trace lines following
untagged. Each launch starts with "StarfarerLauncher - Starting Starsector <version> launcher". Read it bottom-up:
the last ERROR before the end of a run is usually the crash (wiki "Starsector log file"). The file rolls over to
starsector.log.1 at ~50 MB. Known vanilla noise (e.g. "Ship hull spec [flare] not found in ship_data.csv") is
counted but hidden unless --show-noise.
Exit code: 1 if errors were found (with --mod: errors related to that mod).
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sslib  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LINE = re.compile(r"^(\d+)\s+\[([^\]]*)\]\s+(INFO|WARN|ERROR|DEBUG|FATAL|TRACE)\s+(\S+)\s+-\s?(.*)$")
NOISE = [
    r"Ship hull spec \[(flare|module_hightech_decor)\] not found in ship_data\.csv",
    r"Weapon \[lightmortar_fighter\] from weapon_data\.csv not found in store",
    r"Weapon spec \[sw_hyperpulse\] not found",
    r"Control key \[C2_MORE_INFO_\d\] is invalid",
    r'^No such command ".*" registered',   # a mistyped Console Commands command, not a mod problem
]
EXPLAIN = [  # (regex on the entry text, explanation)
    (r"Error loading \[([^\]]+)\] resource, not found in",
     "a file the game was told to load does not exist: '{0}'. Check the path's spelling and case (Linux/macOS are "
     "case-sensitive) and that the file is inside the mod folder. The bracketed list shows every mod folder searched."),
    (r"Weapon spec \[([^\]]+)\] not found",
     "something (a variant, faction or code) references weapon id '{0}' that has no weapon_data.csv row + .wpn file."),
    (r"Weapon with spec id \[([^\]]+)\] not found",
     "a faction's knownWeapons (or priority/sell lists) names weapon '{0}', which does not exist; fleet spawning throws."),
    (r"Fighter wing with spec id \[([^\]]+)\] not found",
     "a faction knows wing '{0}', which does not exist; fleet spawning throws."),
    (r"Ship hull spec \[([^\]]+)\] not found in ship_data\.csv",
     "a .ship file's hullId '{0}' has no ship_data.csv row (logged as ERROR, the hull is unusable)."),
    (r"Weapon \[([^\]]+)\] from weapon_data\.csv not found in store",
     "weapon_data.csv row '{0}' has no matching .wpn file."),
    (r"(?:hull|variant|Variant) (?:with id )?\[?([\w-]+)\]? not found",
     "a variant/hull id '{0}' is referenced but not defined (default_ship_roles, a faction, rules or code)."),
    (r"CannotResolveClassException[\s\S]{0,300}?cause-message\s*:\s*(\S+)",
     "the SAVE references class '{0}', which no longer exists (a mod was removed, or a class was renamed or moved). "
     "Restore the class, or keep an XStream alias in configureXStream; never rename saved classes after release."),
    (r"(?:NoClassDefFoundError|ClassNotFoundException):?\s*([\w./$]+)",
     "class '{0}' is missing at runtime: its jar is not listed in mod_info.json \"jars\", a dependency is missing or "
     "outdated, or code touches an optional mod's classes without an isModEnabled() guard."),
    (r"NumberFormatException(?::\s*(.*))?",
     "a numeric CSV column or JSON field holds text ({0}): look for stray letters, % signs or shifted columns."),
    (r"JSONException(?::\s*(.*))?",
     "malformed JSON ({0}). The message gives the character position; check commas, brackets and quotes."),
    (r"TextureLoader|ArrayIndexOutOfBoundsException.*(?:Texture|PNG)",
     "an image could not be loaded: a 16-bit PNG crashes TextureLoader (wiki); save sprites as 8-bit RGBA."),
    (r"Index: (\d+), Size: (\d+)",
     "array size mismatch (index {0}, size {1}): e.g. turretOffsets vs turretAngleOffsets counts in a .wpn, or a "
     "list in data shorter than the code expects."),
    (r"NullPointerException",
     "a lookup returned null (getVariant/getFaction/getMarket/getEntityById...) or a field was never set. The first "
     "stack frame inside your own package is the place to fix; guard the lookup."),
    (r"OutOfMemoryError",
     "the game ran out of memory: raise -Xmx in vmparams (and check for leaks via static fields holding game objects)."),
    (r"ConcurrentModificationException",
     "a list was modified while being iterated (e.g. removing entities/scripts inside a for-each). Copy the list first."),
    (r"ClassCastException(?::\s*(.*))?",
     "wrong type ({0}): often a plugin/script registered under the wrong key or a memory value of another type."),
]


class Entry:
    __slots__ = ("lineno", "ms", "thread", "level", "logger", "msg", "extra")

    def __init__(self, lineno, ms, thread, level, logger, msg):
        self.lineno, self.ms, self.thread, self.level, self.logger, self.msg = lineno, ms, thread, level, logger, msg
        self.extra = []

    def text(self):
        return self.msg + "\n" + "\n".join(self.extra)


def parse(path):
    entries = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for i, raw in enumerate(fh, 1):
            line = raw.rstrip("\r\n")
            m = LINE.match(line)
            if m:
                entries.append(Entry(i, int(m.group(1)), m.group(2), m.group(3), m.group(4), m.group(5)))
            elif entries:
                if len(entries[-1].extra) < 400:
                    entries[-1].extra.append(line)
    return entries


def split_runs(entries):
    runs, cur = [], []
    for e in entries:
        if e.logger.endswith("StarfarerLauncher") and e.msg.startswith("Starting Starsector"):
            if cur:
                runs.append(cur)
            cur = []
        cur.append(e)
    if cur:
        runs.append(cur)
    return runs


def explain(text):
    for rx, msg in EXPLAIN:
        m = re.search(rx, text)
        if m:
            groups = [g if g is not None else "" for g in m.groups()] or [""]
            try:
                return msg.format(*groups)
            except IndexError:
                return msg
    return None


def mod_markers(mod):
    """Strings that identify a mod in log text: folder name, id, id prefix, Java packages from its jars."""
    out = set()
    if not mod:
        return out
    info = sslib.read_mod_info(mod)
    out.add(os.path.basename(os.path.normpath(mod)))
    if info.get("id"):
        out.add(info["id"])
    for p in (os.path.join(mod, "tools", "validate_config.json"), os.path.join(mod, "validate_config.json")):
        if os.path.isfile(p):
            pre = sslib.load_loose_json(p).get("prefix")
            if pre:
                out.add(pre)
    for j in sslib.mod_jars(mod, info):
        for c in sslib.jar_classes(j):
            parts = c.split(".")
            if len(parts) > 1:
                out.add(".".join(parts[:-1]) + ".")
    if info.get("modPlugin") and "." in info["modPlugin"]:
        out.add(info["modPlugin"].rsplit(".", 1)[0] + ".")
    return {m for m in out if len(m) >= 3}


def first_own_frame(e, markers):
    for ln in e.extra:
        s = ln.strip()
        if s.startswith("at ") and any(m.endswith(".") and s[3:].startswith(m) for m in markers):
            return s
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log")
    ap.add_argument("--game")
    ap.add_argument("--mod", help="mod folder to focus on")
    ap.add_argument("--run", default="last", help="last (default), all, or a 1-based launch number")
    ap.add_argument("--errors-only", action="store_true")
    ap.add_argument("--show-noise", action="store_true")
    ap.add_argument("--trace", type=int, default=8, help="stack-trace lines to show per entry")
    a = ap.parse_args()
    log = a.log
    if not log:
        game = sslib.require_game_dir(a.game)
        log = os.path.join(sslib.core_dir(game), "starsector.log")
    if not os.path.isfile(log):
        sys.exit("log not found: %s" % log)
    runs = split_runs(parse(log))
    if not runs:
        sys.exit("no log entries found in %s" % log)
    if a.run == "all":
        sel = list(enumerate(runs, 1))
    elif a.run == "last":
        sel = [(len(runs), runs[-1])]
    else:
        k = int(a.run)
        sel = [(k, runs[k - 1])]
    mod = sslib.find_mod_root(a.mod) if a.mod else None
    markers = mod_markers(mod)
    noise_rx = [re.compile(x) for x in NOISE]
    total_rel = total_err = 0
    for idx, run in sel:
        head = run[0]
        ver = re.search(r"Starting Starsector (\S+)", head.msg)
        java = next((e.msg for e in run[:40] if e.msg.startswith("Java version")), "")
        print("=" * 100)
        print("launch %d of %d: log lines %d-%d, %s, %s, last entry at %.0fs" % (
            idx, len(runs), run[0].lineno, run[-1].lineno, ("Starsector " + ver.group(1)) if ver else "version ?",
            java or "java ?", run[-1].ms / 1000.0))
        noise = 0
        items = []
        seen = {}
        for e in run:
            txt = e.text()
            has_exc = re.search(r"\b(\w+\.)+\w*(Exception|Error)\b", txt) and e.level in ("INFO", "WARN", "ERROR", "FATAL")
            if e.level not in ("ERROR", "FATAL", "WARN") and not has_exc:
                continue
            if e.level == "WARN" and a.errors_only:
                continue
            if any(rx.search(e.msg) for rx in noise_rx):
                noise += 1
                if not a.show_noise:
                    continue
            related = bool(markers) and any(m in txt for m in markers)
            key = (e.level, e.logger, re.sub(r"\d+", "N", e.msg)[:200], tuple(x.strip() for x in e.extra[:3]))
            if key in seen:  # identical entry again: count it instead of printing it again
                seen[key][2] += 1
                continue
            seen[key] = [related, e, 1]
            items.append(seen[key])
        items.sort(key=lambda t: (not t[0], t[1].lineno))
        for related, e, count in items:
            level = e.level if e.level != "INFO" else "EXC"
            total_err += level in ("ERROR", "FATAL", "EXC")
            total_rel += related and level in ("ERROR", "FATAL", "EXC")
            print("-" * 100)
            print("%s%-5s line %d%s  [%s] %s" % ("[MOD] " if related else "", level, e.lineno,
                                                 "  (x%d)" % count if count > 1 else "", e.thread, e.logger))
            print("   " + e.msg[:300])
            trace = [ln for ln in e.extra if ln.strip()][: a.trace]
            for ln in trace:
                print("   | " + ln[:220])
            own = first_own_frame(e, markers)
            if own:
                print("   >> first frame in your code: " + own)
            why = explain(e.text())
            if why:
                print("   => " + why)
        last = run[-1]
        last_is_noise = any(rx.search(last.msg) for rx in noise_rx)   # e.g. a mistyped console command
        if not last_is_noise and (last.level in ("ERROR", "FATAL") or re.search(r"Exception|Error", last.text())):
            print("-" * 100)
            print("The launch ENDS on an error at log line %d: that is probably the crash. Read it first." % last.lineno)
        print("-" * 100)
        print("%d issue(s) shown, %d known vanilla-noise line(s) %s" % (len(items), noise, "shown" if a.show_noise else "hidden"))
    if markers:
        print("\nentries mentioning the mod (%s): %d error(s)" % (", ".join(sorted(markers)[:6]), total_rel))
        return 1 if total_rel else 0
    return 1 if total_err else 0


if __name__ == "__main__":
    sys.exit(main())
