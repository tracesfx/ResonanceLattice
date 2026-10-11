#!/usr/bin/env python3
"""build_mod.py - one-command build for a Starsector mod: compile Java -> jar -> run the validator. Fails loudly.

    python build_mod.py                      # mod = folder with mod_info.json at/above the cwd
    python build_mod.py --mod path/to/MyMod
    python build_mod.py --no-validate        # compile + jar only
    python build_mod.py --with-mod shaderLib # also compile against a mod you integrate with but do not depend on

What it does
  * target = the major version of the JRE bundled with the game (jre/release; 0.98a ships Java 17) -> javac --release N
  * classpath = the game's API jars (starfarer.api.jar, json, log4j, lwjgl, lwjgl_util, xstream, ...; never the
    obfuscated jars unless --with-obf) + every jar of each mod_info.json dependency + optional_mods from
    validate_config.json + --with-mod mods + --extra-cp entries
  * sources = every .java under src/ (change with --src); a mod without Java skips straight to validation
  * output = the first jar listed in mod_info.json "jars" (or --jar), written with Python's zipfile (no `jar` needed)
  * then runs validate_mod.py (which lives next to this script) on the mod; its exit code becomes the build's

The javac on PATH must be a JDK whose version is >= the target (JDK 17 for 0.98a).
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sslib  # noqa: E402

LINT = "-Xlint:all,-serial,-options,-classfile,-processing,-path"


def find_javac():
    j = shutil.which("javac")
    if j:
        return j
    for env in ("JAVA_HOME", "JDK_HOME"):
        h = os.environ.get(env)
        if h:
            p = os.path.join(h, "bin", "javac.exe" if os.name == "nt" else "javac")
            if os.path.isfile(p):
                return p
    return None


def javac_major(javac):
    out = subprocess.run([javac, "-version"], capture_output=True, text=True)
    m = re.search(r"javac\s+(\d+)(?:\.(\d+))?", (out.stdout or "") + (out.stderr or ""))
    if not m:
        return None
    major = int(m.group(1))
    return int(m.group(2)) if major == 1 and m.group(2) else major


def core_classpath(core, with_obf=False):
    jars = []
    for f in sorted(os.listdir(core)):
        if not f.endswith(".jar") or f.endswith("-sources.jar"):
            continue
        if "_obf" in f and not with_obf:
            continue
        jars.append(os.path.join(core, f))
    return jars


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mod")
    ap.add_argument("--game")
    ap.add_argument("--src", default="src", help="source folder relative to the mod (default src)")
    ap.add_argument("--jar", help="output jar relative to the mod (default: first entry of mod_info.json jars)")
    ap.add_argument("--release", type=int, help="javac --release (default: the game's bundled JRE major)")
    ap.add_argument("--with-mod", action="append", default=[], help="extra mod id to compile against (repeatable)")
    ap.add_argument("--extra-cp", default="", help="extra classpath entries, separated by os.pathsep")
    ap.add_argument("--with-obf", action="store_true", help="also compile against the obfuscated core jars (fragile)")
    ap.add_argument("--no-validate", action="store_true")
    ap.add_argument("--strict", action="store_true", help="pass --strict to the validator (warnings fail)")
    ap.add_argument("--prefix", help="passed to the validator")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)  # keep our lines ordered with the validator's output

    mod = sslib.find_mod_root(a.mod or os.getcwd())
    if not mod:
        sys.exit("BUILD ERROR: no mod_info.json at or above %s" % (a.mod or os.getcwd()))
    game = sslib.find_game_dir(a.game) if a.game else (sslib.find_game_dir(os.path.dirname(os.path.dirname(mod)))
                                                      or sslib.find_game_dir())
    if not game:
        sys.exit("BUILD ERROR: Starsector install not found; pass --game or set STARSECTOR_DIR")
    core = sslib.core_dir(game)
    info = sslib.read_mod_info(mod)
    t0 = time.time()
    src_dir = os.path.join(mod, a.src)
    sources = []
    if os.path.isdir(src_dir):
        for dp, _, fs in os.walk(src_dir):
            sources += [os.path.join(dp, f) for f in fs if f.endswith(".java")]
    sources.sort()
    print("[build] %s (%s) %s" % (info.get("name", "?"), info.get("id", "?"), sslib.version_string(info.get("version"))))
    if sources:
        javac = find_javac()
        if not javac:
            sys.exit("BUILD ERROR: javac not found. Install a JDK (17 for Starsector 0.98a) and put it on PATH or set JAVA_HOME.")
        jre = sslib.jre_version(game)
        target = a.release or (int(jre.split(".")[0]) if jre else 17)
        have = javac_major(javac)
        if have is not None and have < target:
            sys.exit("BUILD ERROR: %s is JDK %s but the game runs Java %s; install JDK %s+" % (javac, have, target, target))
        installed = sslib.installed_mods(game)
        cp = core_classpath(core, a.with_obf)
        want = [d.get("id") for d in info.get("dependencies", []) or [] if isinstance(d, dict)]
        cfg_p = next((p for p in (os.path.join(mod, "validate_config.json"), os.path.join(mod, "tools", "validate_config.json"))
                      if os.path.isfile(p)), None)
        if cfg_p:
            try:
                want += sslib.load_loose_json(cfg_p).get("optional_mods", []) or []
            except Exception:
                pass
        want += a.with_mod
        for mid in dict.fromkeys(want):
            if mid not in installed:
                sys.exit("BUILD ERROR: mod '%s' (dependency/optional) is not installed in %s" % (mid, sslib.mods_dir(game)))
            folder, minfo = installed[mid]
            if os.path.abspath(folder) == os.path.abspath(mod):
                continue
            jars = sslib.mod_jars(folder, minfo)
            cp += jars
            print("[build] + %-14s %s" % (mid, ", ".join(os.path.basename(j) for j in jars) or "(no jars)"))
        cp += [p for p in a.extra_cp.split(os.pathsep) if p]
        for p in cp:
            if not os.path.isfile(p):
                sys.exit("BUILD ERROR: classpath entry missing: %s" % p)
        out_classes = os.path.join(mod, "build", "classes")
        if os.path.isdir(os.path.join(mod, "build")):
            shutil.rmtree(os.path.join(mod, "build"))
        os.makedirs(out_classes)
        argfile = os.path.join(mod, "build", "sources.txt")
        with open(argfile, "w", encoding="utf-8", newline="\n") as fh:
            for s in sources:
                fh.write('"%s"\n' % s.replace("\\", "/"))
        cmd = [javac, "--release", str(target), "-encoding", "UTF-8", LINT, "-cp", os.pathsep.join(cp),
               "-d", out_classes, "@" + argfile]
        print("[build] javac --release %d: %d source file(s), %d classpath jar(s)" % (target, len(sources), len(cp)))
        res = subprocess.run(cmd, capture_output=True, text=True)
        diag = (res.stdout or "") + (res.stderr or "")
        if diag.strip():
            print(diag.rstrip())
        if res.returncode != 0:
            sys.exit("BUILD FAILED: javac exit %d" % res.returncode)
        nwarn = len(re.findall(r": warning:", diag))
        jar_rel = a.jar or ((info.get("jars") or [None])[0]) or "jars/%s.jar" % re.sub(r"\W+", "", info.get("name", "mod"))
        jar_path = os.path.join(mod, jar_rel)
        os.makedirs(os.path.dirname(jar_path), exist_ok=True)
        tmp = jar_path + ".tmp"
        n = 0
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("META-INF/MANIFEST.MF", "Manifest-Version: 1.0\r\nCreated-By: build_mod.py\r\n\r\n")
            for dp, _, fs in sorted(os.walk(out_classes)):
                for f in sorted(fs):
                    full = os.path.join(dp, f)
                    z.write(full, os.path.relpath(full, out_classes).replace("\\", "/"))
                    n += 1
        os.replace(tmp, jar_path)
        print("[build] wrote %s (%d classes)%s" % (jar_rel, n, ", %d javac warning(s): review them" % nwarn if nwarn else ""))
        if jar_rel.replace("\\", "/") not in [j.replace("\\", "/") for j in info.get("jars", []) or []]:
            print("[build] WARNING: %s is not listed in mod_info.json \"jars\": the game will not load it" % jar_rel)
    else:
        print("[build] no Java sources under %s: data-only mod, skipping compile" % a.src)
    rc = 0
    if not a.no_validate:
        print("[build] validating ...")
        vargs = [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "validate_mod.py"),
                 "--mod", mod, "--game", game, "--quiet"]
        if a.strict:
            vargs.append("--strict")
        if a.prefix:
            vargs += ["--prefix", a.prefix]
        rc = subprocess.run(vargs).returncode
    print("[build] %s in %.1fs" % ("OK" if rc == 0 else "FAILED (validation)", time.time() - t0))
    return rc


if __name__ == "__main__":
    sys.exit(main())
