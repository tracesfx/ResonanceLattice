#!/usr/bin/env python3
"""package_mod.py - build a release zip that installs by extracting into mods/, after the release checks pass.

    python package_mod.py                    # mod = folder with mod_info.json at/above cwd -> dist/<Folder>-<version>.zip
    python package_mod.py --strict           # warnings (placeholders, unused assets, ...) also block the release
    python package_mod.py --with-src         # also ship src/, tools/ and the build scripts (lets others rebuild)

Checks before zipping (any failure aborts): validate_mod.py passes; the jar is newer than every Java source; the
.version file's modVersion equals mod_info.json's version; CHANGELOG mentions the version (warning only).
The zip holds exactly one top-level folder named like the mod folder, so extracting it into mods/ gives
mods/<Folder>/mod_info.json. Dev files are left out: .git, build, dist, tools, src (unless --with-src), __pycache__,
editor/art sources (*.psd, *.xcf, *.kra, *.blend), backups and OS junk.
"""
import argparse
import fnmatch
import os
import re
import subprocess
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sslib  # noqa: E402

TOP_INCLUDE = ["mod_info.json", "*.version", "jars", "data", "graphics", "sounds", "README*", "LICENSE*",
               "CHANGELOG*", "CREDITS*", "*.txt"]
SRC_INCLUDE = ["src", "tools", "build.sh", "build.bat", ".gitattributes"]
EXCLUDE = [".git", ".gitignore", "build", "dist", "__pycache__", "*.pyc", "*.psd", "*.xcf", "*.kra", "*.blend",
           "*.bak", "*.tmp", "*.orig", "*~", "Thumbs.db", ".DS_Store", "desktop.ini", ".idea", ".vscode", "*.iml"]


def excluded(name):
    return any(fnmatch.fnmatch(name, pat) for pat in EXCLUDE)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mod")
    ap.add_argument("--game")
    ap.add_argument("--out", help="output folder (default <mod>/dist)")
    ap.add_argument("--with-src", action="store_true")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--skip-validate", action="store_true", help="not recommended")
    a = ap.parse_args()
    mod = sslib.find_mod_root(a.mod or os.getcwd())
    if not mod:
        sys.exit("no mod_info.json at or above %s" % (a.mod or os.getcwd()))
    info = sslib.read_mod_info(mod)
    version = sslib.version_string(info.get("version"))
    folder = os.path.basename(os.path.normpath(mod))
    problems = []

    if not a.skip_validate:
        cmd = [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "validate_mod.py"), "--mod", mod, "--quiet"]
        if a.game:
            cmd += ["--game", a.game]
        if a.strict:
            cmd.append("--strict")
        rc = subprocess.run(cmd).returncode
        if rc != 0:
            problems.append("validate_mod.py failed%s" % (" (strict)" if a.strict else ""))

    jars = sslib.mod_jars(mod, info)
    for j in info.get("jars", []) or []:
        if not os.path.isfile(os.path.join(mod, j)):
            problems.append("jar listed in mod_info.json is missing: %s (build first)" % j)
    newest = 0.0
    for dp, dns, fs in os.walk(os.path.join(mod, "src")):
        for f in fs:
            if f.endswith((".java", ".kt")):
                newest = max(newest, os.path.getmtime(os.path.join(dp, f)))
    for j in jars:
        if newest and os.path.getmtime(j) < newest - 1:
            problems.append("%s is older than the newest source file: rebuild" % os.path.relpath(j, mod))

    vf_csv = os.path.join(mod, "data", "config", "version", "version_files.csv")
    if os.path.isfile(vf_csv):
        for row in sslib.read_csv(vf_csv, key="version file"):
            p = os.path.join(mod, row["version file"].strip())
            if os.path.isfile(p):
                mv = sslib.version_string(sslib.load_loose_json(p).get("modVersion"))
                if mv != version:
                    problems.append("%s modVersion %s != mod_info.json version %s" % (row["version file"].strip(), mv, version))
    else:
        print("warning: no Version Checker files (data/config/version/version_files.csv)")
    ch = [f for f in os.listdir(mod) if f.upper().startswith("CHANGELOG")]
    if ch and version not in open(os.path.join(mod, ch[0]), encoding="utf-8", errors="replace").read():
        print("warning: %s does not mention version %s" % (ch[0], version))

    if problems:
        for p in problems:
            print("RELEASE BLOCKED: " + p)
        return 1

    include = TOP_INCLUDE + (SRC_INCLUDE if a.with_src else [])
    files = []
    for name in sorted(os.listdir(mod)):
        if excluded(name) or not any(fnmatch.fnmatch(name, pat) for pat in include):
            continue
        full = os.path.join(mod, name)
        if os.path.isfile(full):
            files.append(name)
            continue
        for dp, dns, fs in os.walk(full):
            dns[:] = sorted(d for d in dns if not excluded(d))
            for f in sorted(fs):
                if not excluded(f):
                    files.append(os.path.relpath(os.path.join(dp, f), mod).replace("\\", "/"))
    out_dir = os.path.abspath(a.out or os.path.join(mod, "dist"))
    os.makedirs(out_dir, exist_ok=True)
    safe_ver = re.sub(r"[^\w.\-]+", "_", version or "0")
    zpath = os.path.join(out_dir, "%s-%s.zip" % (folder, safe_ver))
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in files:
            z.write(os.path.join(mod, rel), "%s/%s" % (folder, rel))
    with zipfile.ZipFile(zpath) as z:
        names = set(z.namelist())
        bad = z.testzip()
    missing = [j for j in (info.get("jars") or []) if "%s/%s" % (folder, j.replace("\\", "/")) not in names]
    if bad or "%s/mod_info.json" % folder not in names or missing:
        print("RELEASE BLOCKED: zip check failed (corrupt entry %s, missing %s)" % (bad, missing or "mod_info.json"))
        return 1
    size = os.path.getsize(zpath)
    print("wrote %s (%d files, %.1f MB). Extract into mods/ -> mods/%s/mod_info.json" % (zpath, len(files), size / 1e6, folder))
    return 0


if __name__ == "__main__":
    sys.exit(main())
