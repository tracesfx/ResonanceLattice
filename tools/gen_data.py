#!/usr/bin/env python3
"""gen_data.py - writes ALL of Resonance Lattice's game data from code. Re-run after every change; never hand-edit
the files it writes (list at the bottom of this docstring).

    python art_src/gen/gen_weapons.py      # weapon sprites + art_src/gen/weapon_offsets.json (muzzle offsets)
    python art_src/gen/gen_icons.py        # system / hullmod icons, crest, flag
    python tools/gen_data.py               # everything below

Order matters only in one place: art_src/finish.py writes data/hulls/<hull>.ship from the hull specs (geometry), and
this script post-processes those .ship files (hull style, engine style, built-in weapons and hullmods, module
anchors, deco arcs). Run it again after any finish.py run.

Stats come from vanilla peers (`vanilla_baselines.py peers`) via ssdata.clone_row: only the columns the design needs
are changed. BALANCE.md lists the deviations.

Writes: data/hulls/{ship_data.csv, *.ship (post-process), rsl_virtuoso_unsung.ship}, data/variants/rsl/*.variant,
data/weapons/{weapon_data.csv, *.wpn, proj/*.proj}, data/shipsystems/{ship_systems.csv, *.system},
data/hullmods/hull_mods.csv, data/strings/descriptions.csv, data/world/factions/{factions.csv, rsl_choir.faction,
default_ship_roles.json}, data/config/{settings.json, hull_styles.json, engine_styles.json},
data/lights/rsl_texture_data.csv, data/missions/** (test missions).
"""
import csv
import io
import json
import os
import shutil
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.expanduser("~"), ".claude", "skills", "starsector-modding", "scripts"))
import ssdata  # noqa: E402
import sslib  # noqa: E402

V = ssdata.Vanilla()
MFR = "Resonance Lattice"
BP = "rsl_bp"
TEAL = [100, 230, 220, 255]
TEAL_SOFT = [60, 200, 190, 255]
VIOLET = [160, 120, 240, 255]
WHITE = [235, 255, 252, 255]
OFFS = json.load(open(os.path.join(ROOT, "art_src", "gen", "weapon_offsets.json")))


def P(*rel):
    return os.path.join(ROOT, *rel)


def write_text(rel, text):
    p = P(rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def write_json(rel, obj):
    write_text(rel, json.dumps(obj, indent=4) + "\n")


def write_csv(rel, header, rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    for r in rows:
        unknown = [k for k in r if k not in header]
        if unknown:
            raise KeyError("%s: unknown columns %s" % (rel, unknown))
        w.writerow(["" if r.get(c) is None else str(r.get(c)) for c in header])
    write_text(rel, buf.getvalue())


DESC = []   # (id, type, text1, text2, text3)


def desc(did, dtype, t1, t2="", t3=""):
    DESC.append((did, dtype, t1, t2, t3))


# ===================================================================================================== weapons
def blank_row(**kw):
    hdr = V.header("weapon_data.csv")
    r = {c: "" for c in hdr}
    r["OPs"] = "0"
    r.update({k: str(v) for k, v in kw.items()})
    return r


def muzzle_flash(color, length=24.0, spread=8.0, size=14.0, count=8):
    return {"length": length, "spread": spread, "particleSizeMin": size, "particleSizeRange": size * 0.8,
            "particleDuration": 0.12, "particleCount": count, "particleColor": color}


def wpn_base(wid, mount_type, size, spec_class="projectile", glow=True, barrel="ALTERNATING"):
    o = OFFS[wid]
    w = {"id": wid, "specClass": spec_class, "type": mount_type, "size": size,
         "turretSprite": o["turret"]["sprite"], "hardpointSprite": o["hardpoint"]["sprite"],
         "turretOffsets": o["turret"]["offsets"], "turretAngleOffsets": o["turret"]["angles"],
         "hardpointOffsets": o["hardpoint"]["offsets"], "hardpointAngleOffsets": o["hardpoint"]["angles"],
         "barrelMode": barrel}
    if glow:
        w["turretGlowSprite"] = o["turret"]["glow"]
        w["hardpointGlowSprite"] = o["hardpoint"]["glow"]
        w["glowColor"] = TEAL
    return w


def bolt(pid, length, width, fringe, core=WHITE, glow_r=0, hit_glow=0, sprite=None, on_hit=None, spawn="BALLISTIC_AS_BEAM",
         coll="RAY", coll_f="RAY_FIGHTER", fade=0.25, glow_a=90):
    p = {"id": pid, "specClass": "projectile", "spawnType": spawn, "collisionClass": coll,
         "collisionClassByFighter": coll_f, "length": length, "width": width, "fadeTime": fade,
         "fringeColor": fringe, "coreColor": core, "textureScrollSpeed": 64.0, "pixelsPerTexel": 5.0}
    if glow_r:
        p["glowColor"] = fringe[:3] + [glow_a]
        p["glowRadius"] = glow_r
    if hit_glow:
        p["hitGlowRadius"] = hit_glow
    if sprite:
        p["bulletSprite"] = sprite
    if on_hit:
        p["onHitEffect"] = on_hit
    return p


def engine_slot(length, width, color=TEAL, contrail=None):
    return [{"id": "ES1", "loc": [-length * 0.5, 0], "style": "CUSTOM",
             "styleSpec": {"mode": "QUAD_STRIP", "engineColor": color, "contrailDuration": 0.6,
                           "contrailWidthMult": 1.2, "contrailWidthAddedFractionAtEnd": 1.5, "contrailMinSeg": 5,
                           "contrailMaxSpeedMult": 0.0, "contrailAngularVelocityMult": 0.5,
                           "contrailSpawnDistMult": 0.0, "contrailColor": contrail or [140, 110, 230, 60],
                           "glowSizeMult": 1.6, "type": "GLOW"},
             "width": width, "length": length * 1.4, "angle": 180.0}]


WEAPONS, WPN, PROJ = [], {}, {}
PKG = "rsl.weapons."


def add_weapon(row, wpn, projs=(), description=""):
    WEAPONS.append(row)
    WPN[row["id"]] = wpn
    for p in projs:
        PROJ[p["id"]] = p
    if description:
        desc(row["id"], "WEAPON", description)


def weapons():
    # ---- SMALL ---------------------------------------------------------------------------------------------
    w = wpn_base("rsl_chime", "ENERGY", "SMALL")
    w.update(animationType="GLOW_AND_FLASH", muzzleFlashSpec=muzzle_flash(TEAL, 18, 6, 10, 6),
             projectileSpecId="rsl_chime_shot", fireSoundTwo="rsl_chime_fire",
             onFireEffect=PKG + "ChimeRepeaterEffect", autocharge=True)
    add_weapon(blank_row(name="Chime Repeater", id="rsl_chime", tier=1, **{
        "base value": 1400, "range": 500, "damage/shot": 30, "emp": 0, "impact": 0, "turn rate": 120, "OPs": 5,
        "type": "ENERGY", "energy/shot": 22, "chargeup": 0, "chargedown": 0.55, "burst size": 2, "burst delay": 0.1,
        "min spread": 0, "max spread": 3, "spread/shot": 1, "spread decay/sec": 8, "proj speed": 1800,
        "hints": "PD, ANTI_FTR", "tags": "pd8, energy7, SR, " + BP, "tech/manufacturer": MFR,
        "primaryRoleStr": "Point Defense", "customPrimary": "Every %s shot is a resonant chime: %s EMP damage and an arc to a nearby missile or fighter.",
        "customPrimaryHL": "4th | 150"}), w,
        [bolt("rsl_chime_shot", 40, 4, TEAL_SOFT, hit_glow=22, fade=0.15, on_hit=PKG + "RailImpactOnHit"),
         bolt("rsl_chime_bell", 50, 6, VIOLET, hit_glow=40, glow_r=18, on_hit=PKG + "ChimeBellOnHit", fade=0.15)],
        "A compact micro-rail built around a pair of tuning prongs. It flicks needles out in short pairs; every fourth "
        "needle is allowed to ring, and the chime spills over as an EMP arc that snaps at nearby missiles and fighters.")
    # the chime shot is spawned from a hidden weapon so it can carry its own projectile spec
    hid = wpn_base("rsl_chime", "ENERGY", "SMALL", glow=False)
    hid.update(id="rsl_chime_bell", projectileSpecId="rsl_chime_bell", animationType="MUZZLE_FLASH",
               muzzleFlashSpec=muzzle_flash(VIOLET, 18, 6, 10, 6))
    add_weapon(blank_row(name="Chime (bell)", id="rsl_chime_bell", **{
        "range": 450, "damage/shot": 30, "emp": 150, "type": "ENERGY", "energy/shot": 0, "chargedown": 1,
        "proj speed": 1800, "tags": "SYSTEM", "tech/manufacturer": MFR}), hid, [],
        "The ringing fourth shot of a Chime Repeater.")

    w = wpn_base("rsl_pizzicato", "ENERGY", "SMALL")
    w.update(animationType="GLOW_AND_FLASH", muzzleFlashSpec=muzzle_flash(TEAL, 26, 4, 12, 8),
             projectileSpecId="rsl_pizzicato_shot", fireSoundTwo="rsl_pizzicato_fire",
             onFireEffect=PKG + "PizzicatoEffect")
    add_weapon(blank_row(name="Pizzicato Lancet", id="rsl_pizzicato", tier=1, **{
        "base value": 1800, "range": 800, "damage/shot": 110, "impact": 4, "turn rate": 30, "OPs": 7,
        "type": "ENERGY", "energy/shot": 100, "chargeup": 0, "chargedown": 0.9, "proj speed": 2200,
        "tags": "energy8, " + BP, "tech/manufacturer": MFR, "primaryRoleStr": "General",
        "customPrimary": "A shot fired after at least %s of silence is plucked: it deals %s damage.",
        "customPrimaryHL": "2.5 seconds | double"}), w,
        [bolt("rsl_pizzicato_shot", 80, 5, TEAL, glow_r=12, hit_glow=30, on_hit=PKG + "RailImpactOnHit")],
        "A needle-thin rail with a tensioned crystal at its breech. Left alone, the crystal stores its charge and "
        "the next slug leaves with a sharp, plucked report - and twice the bite.")

    w = wpn_base("rsl_shardcaster", "BALLISTIC", "SMALL", barrel="LINKED")
    w.update(animationType="MUZZLE_FLASH", muzzleFlashSpec=muzzle_flash(TEAL, 16, 20, 8, 10),
             projectileSpecId="rsl_shard_shot", fireSoundTwo="rsl_shard_fire")
    add_weapon(blank_row(name="Shard Caster", id="rsl_shardcaster", tier=1, **{
        "base value": 1100, "range": 700, "damage/shot": 30, "impact": 2, "turn rate": 50, "OPs": 6,
        "type": "KINETIC", "energy/shot": 18, "chargeup": 0, "chargedown": 0.6, "min spread": 1, "max spread": 4,
        "spread/shot": 1, "spread decay/sec": 12, "proj speed": 1800, "hints": "ANTI_FTR",
        "tags": "kinetic6, energy6, LR, " + BP, "tech/manufacturer": MFR, "primaryRoleStr": "Assault"}), w,
        [bolt("rsl_shard_shot", 10, 5, TEAL_SOFT, spawn="BALLISTIC", coll="PROJECTILE_FF", coll_f="PROJECTILE_FIGHTER",
              sprite=OFFS["rsl_shard_proj"]["sprite"], fade=0.15, on_hit=PKG + "RailImpactOnHit")],
        "Three short rails throw grown crystal shards in a near-parallel volley. Crude by Choir standards, the Shard "
        "Caster is what the lattice yards fit when a hull needs reach and has little flux to spare.")

    w = wpn_base("rsl_tuningspike", "MISSILE", "SMALL", glow=False)
    w.update(animationType="SMOKE", projectileSpecId="rsl_tuningspike_msl", fireSoundTwo="rsl_spike_fire",
             smokeSpec={"particleSizeMin": 8.0, "particleSizeRange": 8.0, "cloudParticleCount": 4,
                        "cloudDuration": 1.0, "cloudRadius": 8.0, "blowbackParticleCount": 3, "blowbackDuration": 1.5,
                        "blowbackLength": 14.0, "blowbackSpread": 10.0, "particleColor": [120, 140, 160, 160]})
    spike_proj = {
        "id": "rsl_tuningspike_msl", "specClass": "missile", "missileType": "MISSILE",
        "sprite": OFFS["rsl_tuningspike_msl"]["sprite"], "size": OFFS["rsl_tuningspike_msl"]["size"],
        "center": [OFFS["rsl_tuningspike_msl"]["size"][0] / 2, OFFS["rsl_tuningspike_msl"]["size"][1] / 2],
        "collisionRadius": 10, "collisionClass": "MISSILE_NO_FF", "explosionColor": TEAL, "explosionRadius": 40,
        "flameoutTime": 1, "armingTime": 0.2, "noEngineGlowTime": 0.3, "fadeTime": 0.5,
        "onHitEffect": PKG + "TuningSpikeOnHit",
        "engineSpec": {"turnAcc": 600, "turnRate": 180, "acc": 900, "dec": 400},
        "engineSlots": engine_slot(10, 5)}
    add_weapon(blank_row(name="Tuning Spike", id="rsl_tuningspike", tier=1, **{
        "base value": 900, "range": 1200, "damage/shot": 150, "impact": 5, "turn rate": 40, "OPs": 4, "ammo": 6,
        "ammo/sec": 0.1, "reload size": 1, "type": "HIGH_EXPLOSIVE", "energy/shot": 0, "chargeup": 0, "chargedown": 1.5,
        "burst size": 2, "burst delay": 0.2, "proj speed": 600, "launch speed": 150, "flight time": 2.6,
        "proj hitpoints": 100, "hints": "", "tags": "missile6, strike5, " + BP, "tech/manufacturer": MFR,
        "primaryRoleStr": "Combo", "speedStr": "Fast", "trackingStr": "Good",
        "customPrimary": "Spikes that hit hull or armor embed for %s. The next energy weapon hit on that ship detonates every embedded spike for %s energy damage each.",
        "customPrimaryHL": "10 seconds | 300", "noDPSInTooltip": "TRUE"}), w, [spike_proj],
        "A lattice shard grown around a tuned core. It buries itself in the target's plating and hums there until an "
        "energy weapon strikes the same hull; the matching frequency shatters it from the inside. The lattice regrows "
        "spent spikes slowly.")
    w = wpn_base("rsl_tuningspike_pod", "MISSILE", "MEDIUM", glow=False)
    w.update({k: WPN["rsl_tuningspike"][k] for k in ("animationType", "projectileSpecId", "fireSoundTwo", "smokeSpec")})
    add_weapon(blank_row(name="Tuning Spike Pod", id="rsl_tuningspike_pod", tier=1, **{
        "base value": 2400, "range": 1200, "damage/shot": 150, "impact": 5, "turn rate": 30, "OPs": 10, "ammo": 16,
        "ammo/sec": 0.25, "reload size": 2, "type": "HIGH_EXPLOSIVE", "energy/shot": 0, "chargedown": 2.0,
        "burst size": 4, "burst delay": 0.15, "proj speed": 600, "launch speed": 150, "flight time": 2.6,
        "proj hitpoints": 100, "tags": "missile8, strike6, " + BP, "tech/manufacturer": MFR, "primaryRoleStr": "Combo",
        "speedStr": "Fast", "trackingStr": "Good", "customPrimary": WEAPONS[-1]["customPrimary"],
        "customPrimaryHL": WEAPONS[-1]["customPrimaryHL"], "noDPSInTooltip": "TRUE"}), w, [],
        "Four Tuning Spike racks in an armored pod, for hulls that build their whole battle plan around the combo.")

    # ---- MEDIUM --------------------------------------------------------------------------------------------
    w = wpn_base("rsl_lattice_lance", "ENERGY", "MEDIUM")
    w.update(animationType="GLOW_AND_FLASH", muzzleFlashSpec=muzzle_flash(TEAL, 34, 4, 16, 8),
             projectileSpecId="rsl_lance_shot", fireSoundTwo="rsl_lance_fire")
    add_weapon(blank_row(name="Lattice Lance", id="rsl_lattice_lance", tier=2, **{
        "base value": 3200, "range": 1000, "damage/shot": 140, "impact": 6, "turn rate": 25, "OPs": 12,
        "type": "ENERGY", "energy/shot": 120, "chargeup": 0, "chargedown": 0.7, "min spread": 0, "max spread": 0,
        "proj speed": 2400, "tags": "energy10, LR, " + BP, "tech/manufacturer": MFR, "primaryRoleStr": "Sustained",
        "customPrimary": "Each consecutive hit on the same ship adds %s damage, up to %s; switching targets or %s "
                         "without a hit resets it.",
        "customPrimaryHL": "15% | 75% | 2.5 seconds"}), w,
        [bolt("rsl_lance_shot", 110, 6, [40, 190, 185, 255], glow_r=16, hit_glow=45, on_hit=PKG + "LatticeLanceOnHit")],
        "A long rail that tunes itself to whatever it keeps hitting. Every slug that lands on the same hull brings its "
        "resonance closer to the target's own, and the next one cuts deeper. Switching targets throws the tuning away.")

    w = wpn_base("rsl_flechette", "BALLISTIC", "MEDIUM", barrel="LINKED")
    w.update(animationType="MUZZLE_FLASH", muzzleFlashSpec=muzzle_flash(TEAL, 22, 24, 10, 14),
             projectileSpecId="rsl_flechette_shot", fireSoundTwo="rsl_flechette_fire")
    add_weapon(blank_row(name="Crystal Flechette", id="rsl_flechette", tier=2, **{
        "base value": 2600, "range": 850, "damage/shot": 60, "impact": 3, "turn rate": 35, "OPs": 10,
        "type": "KINETIC", "energy/shot": 45, "chargeup": 0, "chargedown": 0.75, "min spread": 1, "max spread": 5,
        "spread/shot": 1, "spread decay/sec": 12, "proj speed": 1900, "tags": "kinetic9, LR, " + BP,
        "tech/manufacturer": MFR, "primaryRoleStr": "Assault",
        "customPrimary": "Shards that hit armor or hull splinter and keep cutting: %s energy damage over %s.",
        "customPrimaryHL": "45 | 3 seconds"}), w,
        [bolt("rsl_flechette_shot", 14, 6, TEAL_SOFT, spawn="BALLISTIC", coll="PROJECTILE_FF",
              coll_f="PROJECTILE_FIGHTER", sprite=OFFS["rsl_shard_proj"]["sprite"], on_hit=PKG + "FlechetteOnHit",
              fade=0.15)],
        "A three-rail shard thrower. The flechettes are grown with fracture planes along their length, so a shard "
        "that lodges in plating keeps splitting - and cutting - for seconds after impact.")

    w = wpn_base("rsl_arpeggio", "ENERGY", "MEDIUM")
    w.update(animationType="GLOW_AND_FLASH", muzzleFlashSpec=muzzle_flash(TEAL, 26, 6, 14, 8),
             projectileSpecId="rsl_arpeggio_shot", fireSoundTwo="rsl_arpeggio_fire",
             onFireEffect=PKG + "ArpeggioEffect")
    add_weapon(blank_row(name="Arpeggio Pulser", id="rsl_arpeggio", tier=2, **{
        "base value": 2800, "range": 900, "damage/shot": 100, "impact": 3, "turn rate": 25, "OPs": 10,
        "type": "ENERGY", "energy/shot": 85, "chargeup": 0, "chargedown": 1.2, "burst size": 3, "burst delay": 0.15,
        "proj speed": 2000, "tags": "energy10, " + BP, "tech/manufacturer": MFR, "primaryRoleStr": "General",
        "customPrimary": "Fires a rising three-note burst: the notes deal %s of the listed damage.",
        "customPrimaryHL": "80% | 100% | 140%"}), w,
        [bolt("rsl_arpeggio_shot", 90, 6, TEAL, glow_r=16, hit_glow=40, on_hit=PKG + "RailImpactOnHit")],
        "Three rails of different length, fired in sequence. Each note is driven harder than the last, and the "
        "third one lands like a struck bell.")

    w = wpn_base("rsl_cantus", "BALLISTIC", "MEDIUM", glow=False)
    w.update(animationType="MUZZLE_FLASH", muzzleFlashSpec=muzzle_flash(TEAL, 34, 26, 14, 30),
             projectileSpecId="rsl_cantus_shot", fireSoundTwo="rsl_flak_fire", displayArcRadius=400)
    flak = V.spec("proj", "flak_shot")
    flak.update(id="rsl_cantus_shot", fringeColor=TEAL_SOFT, coreColor=[230, 255, 250, 160])
    flak["behaviorSpec"]["explosionSpec"]["particleColor"] = [120, 240, 230, 255]
    add_weapon(blank_row(name="Cantus Flak", id="rsl_cantus", tier=1, **{
        "base value": 1300, "range": 500, "damage/shot": 160, "impact": 8, "turn rate": 45, "OPs": 9,
        "type": "FRAGMENTATION", "energy/shot": 40, "chargeup": 0, "chargedown": 0.7, "min spread": 0,
        "max spread": 10, "spread/shot": 2, "spread decay/sec": 10, "proj speed": 750, "proj hitpoints": 30,
        "hints": "PD", "tags": "pd12, SR, " + BP, "tech/manufacturer": MFR,
        "primaryRoleStr": "Point Defense (Area)"}), w, [flak],
        "Twin flak barrels that fire tuned fragmentation shells. The shells listen for missile drives and burst when "
        "the pitch is right.")

    # ---- LARGE ---------------------------------------------------------------------------------------------
    w = wpn_base("rsl_harmonic_driver", "ENERGY", "LARGE")
    w.update(animationType="GLOW_AND_FLASH", muzzleFlashSpec=muzzle_flash(TEAL, 50, 10, 30, 14),
             projectileSpecId="rsl_harmonic_shot", fireSoundOne="rsl_charge",
             fireSoundTwo="rsl_driver_fire", autocharge=True, requiresFullCharge=True)
    add_weapon(blank_row(name="Harmonic Driver", id="rsl_harmonic_driver", tier=3, **{
        "base value": 9000, "range": 1200, "damage/shot": 900, "impact": 20, "turn rate": 10, "OPs": 26,
        "type": "ENERGY", "energy/shot": 900, "chargeup": 1.5, "chargedown": 2.0, "proj speed": 2600,
        "proj hitpoints": 500, "hints": "STRIKE", "tags": "energy20, LR, " + BP, "tech/manufacturer": MFR,
        "primaryRoleStr": "Anti Armor",
        "customPrimary": "A fully charged shot that breaks through hull or armor pierces the ship and carries on with %s of its damage.",
        "customPrimaryHL": "50%"}), w,
        [bolt("rsl_harmonic_shot", 180, 12, TEAL, glow_r=40, hit_glow=110, on_hit=PKG + "PierceOnHit")],
        "The Choir's standard heavy gun: a fork of conductive rails that winds a lattice slug up to its breaking "
        "frequency and throws it across the battlefield. A clean hit on plating does not stop it.")
    w = wpn_base("rsl_harmonic_spinal", "ENERGY", "LARGE")
    w.update(animationType="GLOW_AND_FLASH", muzzleFlashSpec=muzzle_flash(TEAL, 80, 12, 44, 20),
             projectileSpecId="rsl_harmonic_spinal_shot", fireSoundOne="rsl_charge",
             fireSoundTwo="rsl_spinal_fire", autocharge=True, requiresFullCharge=True)
    add_weapon(blank_row(name="Harmonic Driver (Spinal)", id="rsl_harmonic_spinal", tier=3, **{
        "base value": 0, "range": 1500, "damage/shot": 1500, "impact": 40, "turn rate": 0, "OPs": 0,
        "type": "ENERGY", "energy/shot": 1400, "chargeup": 2.0, "chargedown": 3.0, "proj speed": 2800,
        "proj hitpoints": 1000, "hints": "STRIKE", "tags": "no_drop, no_sell, no_dealer, restricted",
        "tech/manufacturer": MFR, "primaryRoleStr": "Anti Armor",
        "customPrimary": "Pierces ships it breaks through, keeping %s of its damage.", "customPrimaryHL": "50%"}), w,
        [bolt("rsl_harmonic_spinal_shot", 240, 16, TEAL, glow_r=60, hit_glow=160, on_hit=PKG + "PierceOnHit")],
        "The Conductor's spine is the gun. Its prongs wind the core crystal to a frequency no turret could survive.")

    w = wpn_base("rsl_sostenuto", "ENERGY", "LARGE")
    w.update(animationType="GLOW_AND_FLASH", muzzleFlashSpec=muzzle_flash([90, 160, 255, 255], 40, 5, 22, 10),
             projectileSpecId="rsl_sostenuto_shot", fireSoundTwo="rsl_sostenuto_fire")
    add_weapon(blank_row(name="Sostenuto Rail", id="rsl_sostenuto", tier=3, **{
        "base value": 8000, "range": 1100, "damage/shot": 100, "impact": 4, "turn rate": 8, "OPs": 22,
        "type": "ENERGY", "energy/shot": 95, "chargeup": 0, "chargedown": 0.33, "min spread": 0, "max spread": 1,
        "spread/shot": 0.2, "spread decay/sec": 4, "proj speed": 2400,
        "tags": "energy18, LR, " + BP, "tech/manufacturer": MFR, "primaryRoleStr": "Anti Shield",
        "customPrimary": "Slugs that hit a shield add another %s of the flux they caused, as hard flux.",
        "customPrimaryHL": "35%"}), w,
        [bolt("rsl_sostenuto_shot", 120, 7, [50, 120, 210, 255], core=[225, 245, 255, 255], glow_r=20, hit_glow=50,
              on_hit=PKG + "SostenutoOnHit")],
        "A rapid heavy rail held on one note. Its slugs ring a shield at the pitch of the emitter's own dissipation "
        "band, and part of the load simply stays.")

    w = wpn_base("rsl_bloom", "MISSILE", "LARGE", glow=False)
    w.update(animationType="SMOKE", projectileSpecId="rsl_bloom_msl", fireSoundTwo="rsl_bloom_fire",
             smokeSpec=WPN["rsl_tuningspike"]["smokeSpec"])
    bloom = {"id": "rsl_bloom_msl", "specClass": "missile", "missileType": "MISSILE",
             "sprite": OFFS["rsl_bloom_msl"]["sprite"], "size": OFFS["rsl_bloom_msl"]["size"],
             "center": [OFFS["rsl_bloom_msl"]["size"][0] / 2, OFFS["rsl_bloom_msl"]["size"][1] / 2],
             "collisionRadius": 18, "collisionClass": "MISSILE_FF", "explosionColor": VIOLET, "explosionRadius": 260,
             "flameoutTime": 2, "armingTime": 0.5, "noEngineGlowTime": 0.5, "fadeTime": 0.5,
             "onHitEffect": PKG + "BloomOnHit",
             "engineSpec": {"turnAcc": 60, "turnRate": 25, "acc": 300, "dec": 150},
             "engineSlots": engine_slot(16, 9, VIOLET, [160, 120, 240, 80])}
    add_weapon(blank_row(name="Resonance Bloom", id="rsl_bloom", tier=3, **{
        "base value": 5000, "range": 1500, "damage/shot": 1500, "emp": 1000, "impact": 50, "turn rate": 10,
        "OPs": 22, "ammo": 4, "type": "HIGH_EXPLOSIVE", "energy/shot": 0, "chargeup": 0, "chargedown": 6,
        "burst size": 1, "proj speed": 300, "launch speed": 100, "flight time": 6, "proj hitpoints": 600,
        "hints": "STRIKE", "tags": "missile12, strike10, " + BP, "tech/manufacturer": MFR, "primaryRoleStr": "Torpedo",
        "speedStr": "Slow", "trackingStr": "Poor",
        "customPrimary": "Bursts into a ring of %s crystal fragments and arcs EMP into up to %s nearby targets.",
        "customPrimaryHL": "16 | 4", "noDPSInTooltip": "TRUE"}), w, [bloom],
        "A slow torpedo carrying an unstable lattice bloom. On impact the bloom flowers outward as a ring of crystal "
        "fragments, and the shock arcs through anything nearby.")
    hid = wpn_base("rsl_bloom", "MISSILE", "LARGE", glow=False)
    hid.update(id="rsl_bloom_shard", type="ENERGY", projectileSpecId="rsl_bloom_shard_shot",
               animationType="MUZZLE_FLASH", muzzleFlashSpec=muzzle_flash(VIOLET, 10, 10, 6, 4))
    add_weapon(blank_row(name="Bloom Shard", id="rsl_bloom_shard", **{
        "range": 400, "damage/shot": 120, "type": "FRAGMENTATION", "chargedown": 1, "proj speed": 700,
        "tags": "SYSTEM", "tech/manufacturer": MFR}), hid,
        [bolt("rsl_bloom_shard_shot", 12, 6, VIOLET, spawn="BALLISTIC", coll="PROJECTILE_FF",
              coll_f="PROJECTILE_FIGHTER", sprite=OFFS["rsl_shard_proj"]["sprite"], fade=0.2)],
        "A crystal fragment of a Resonance Bloom.")

    # ---- Virtuoso built-ins ---------------------------------------------------------------------------------
    for wid, name, cd, spd, turn, dmg, tags_extra, text in (
            ("rsl_sforzando", "Sforzando Lance", 0.4, 2600, 45, 160, "",
             "The Virtuoso's voice. A long twin-rail lance that throws lattice slugs fast enough that nothing has time to "
             "move. Once a hull is bare, a slug goes straight through it and on into the next ship in line."),
            ("rsl_sforzando_untuned", "Sforzando Lance (Untuned)", 0.6, 2000, 30, 144, "",
             "The Sforzando as the Unsung carries it: rails out of true, crystal dim. Still a fine gun. Not yet a voice.")):
        full = wid == "rsl_sforzando"
        w = wpn_base(wid, "ENERGY", "LARGE")
        w.update(animationType="GLOW_AND_FLASH", muzzleFlashSpec=muzzle_flash(WHITE,
                                                                               55 if full else 40, 4, 26 if full else 20,
                                                                               14 if full else 10),
                 projectileSpecId=wid + "_shot", fireSoundTwo="rsl_sforzando_fire")
        add_weapon(blank_row(name=name, id=wid, tier=3, **{
            "base value": 0, "range": 1200 if full else 1000, "damage/shot": dmg, "impact": 10, "turn rate": turn,
            "OPs": 0,
            "type": "KINETIC", "energy/shot": int(dmg * 1.1), "chargeup": 0, "chargedown": cd, "min spread": 0,
            "max spread": 0, "spread/shot": 0, "spread decay/sec": 0, "proj speed": spd,
            "hints": "ANTI_FTR, USE_VS_FRIGATES", "tags": "no_drop, no_sell, no_dealer, restricted",
            "tech/manufacturer": MFR, "primaryRoleStr": "Swarm Breaker",
            "customPrimary": ("+%s damage to fighters and frigates. Skewer: a slug that hits hull or armor passes "
                              "through at full damage into the next target, up to %s ships in a row. Accented after a "
                              "Glissando dash, at high speed or in Bravura: every hit deals %s damage and arcs EMP."
                              if wid == "rsl_sforzando" else
                              "+%s damage to fighters and frigates. Skewer: a slug that hits hull or armor passes "
                              "through at full damage into the next target, up to %s ships in a row."),
            "customPrimaryHL": "50% | 12 | +50%" if wid == "rsl_sforzando" else "50% | 3"}), w,
            # the full lance stands apart from every other Lattice gun: a wide, bright, white-teal slug
            [bolt(wid + "_shot", 190, 10, [190, 245, 238, 255], core=[255, 255, 255, 255], glow_r=30, hit_glow=36,
                  on_hit=PKG + "SforzandoOnHit", fade=0.15, glow_a=112) if full else
             # the Unsung's lance: white as well, a little narrower and dimmer than the full Virtuoso's
             bolt(wid + "_shot", 130, 9, [200, 240, 236, 255], core=[255, 255, 255, 255], glow_r=23, hit_glow=55,
                  on_hit=PKG + "SforzandoOnHit", fade=0.15, glow_a=104)], text)

    # ---- decorative parts (moving hull parts) ----------------------------------------------------------------
    for wid, size, mount, sprite, glow, effect in (
            ("rsl_deco_halo_ring", "LARGE", "TURRET", "rsl_halo_ring", True, "DecoRingEffect"),
            ("rsl_deco_cantor_ring", "LARGE", "TURRET", "rsl_cantor_ring", True, "DecoRingEffect"),
            ("rsl_deco_refrain_vane_r", "MEDIUM", "HARDPOINT", "rsl_refrain_vane_r", True, "DecoVaneEffect"),
            ("rsl_deco_refrain_vane_l", "MEDIUM", "HARDPOINT", "rsl_refrain_vane_l", True, "DecoVaneEffect"),
            ("rsl_deco_conductor_blade_r", "MEDIUM", "HARDPOINT", "rsl_conductor_blade_r", True, "DecoVaneEffect"),
            ("rsl_deco_conductor_blade_l", "MEDIUM", "HARDPOINT", "rsl_conductor_blade_l", True, "DecoVaneEffect"),
            ("rsl_deco_virtuoso_vane_r", "MEDIUM", "HARDPOINT", "rsl_virtuoso_vane_r", True, "DecoVaneEffect"),
            ("rsl_deco_virtuoso_vane_l", "MEDIUM", "HARDPOINT", "rsl_virtuoso_vane_l", True, "DecoVaneEffect")):
        spr = "graphics/rsl/weapons/deco/%s.png" % sprite
        w = {"specClass": "beam", "id": wid, "type": "DECORATIVE", "size": size, "showDamageWhenDecorative": True,
             "renderBelowAllWeapons": True, "everyFrameEffect": PKG + effect, "turretSprite": spr,
             "hardpointSprite": spr, "turretOffsets": [0, 0], "turretAngleOffsets": [0], "hardpointOffsets": [0, 0],
             "hardpointAngleOffsets": [0], "fringeColor": [255, 255, 255, 255], "coreColor": [255, 255, 255, 255],
             "glowColor": [255, 255, 255, 255], "width": 1.0, "textureType": "ROUGH", "textureScrollSpeed": 1.0,
             "pixelsPerTexel": 1.0}
        add_weapon(blank_row(name="Lattice part", id=wid, tags="SYSTEM", **{"tech/manufacturer": MFR}), w, [],
                   "A moving part of a Lattice hull.")

    # ---- fighter guns (HIDDEN mounts on the Choir wings; sprites borrowed, never drawn) ---------------------
    for wid, src, size, rng, dmg, cd, burst, spd, snd, onhit, hints, role, length in (
            ("rsl_microrail_ftr", "rsl_chime", "SMALL", 600, 30, 0.35, 2, 2000, "rsl_chime_fire", "RailImpactOnHit",
             "ANTI_FTR", "Point Defense", 45),
            ("rsl_cadenza_rail_ftr", "rsl_pizzicato", "SMALL", 800, 70, 0.9, 1, 2200, "rsl_pizzicato_fire",
             "RailImpactOnHit", "", "General", 70),
            ("rsl_requiem_slug_ftr", "rsl_pizzicato", "SMALL", 900, 300, 4.0, 1, 2400, "rsl_lance_fire",
             "PierceOnHit", "STRIKE", "Anti Armor", 110)):
        w = wpn_base(src, "ENERGY", size, glow=False)
        w.update(id=wid, animationType="MUZZLE_FLASH", muzzleFlashSpec=muzzle_flash(TEAL, 16, 4, 8, 5),
                 projectileSpecId=wid + "_shot", fireSoundTwo=snd)
        add_weapon(blank_row(name={"rsl_microrail_ftr": "Trill Micro-rail", "rsl_cadenza_rail_ftr": "Cadenza Rail",
                                   "rsl_requiem_slug_ftr": "Requiem Slug"}[wid], id=wid, **{
            "range": rng, "damage/shot": dmg, "impact": 2, "turn rate": 0, "type": "ENERGY", "energy/shot": 0,
            "chargedown": cd, "burst size": burst, "burst delay": 0.08, "min spread": 0, "max spread": 1,
            "proj speed": spd, "hints": hints, "tags": "SYSTEM", "tech/manufacturer": MFR, "primaryRoleStr": role}),
            w, [bolt(wid + "_shot", length, 4 if dmg < 100 else 7, TEAL, glow_r=10, hit_glow=25 + dmg / 6,
                     on_hit=PKG + onhit)], "A fighter's rail gun.")
    w = wpn_base("rsl_tuningspike", "MISSILE", "SMALL", glow=False)
    w.update({k: WPN["rsl_tuningspike"][k] for k in ("animationType", "projectileSpecId", "fireSoundTwo", "smokeSpec")})
    w["id"] = "rsl_tuningspike_ftr"
    add_weapon(blank_row(name="Tuning Spike (Requiem)", id="rsl_tuningspike_ftr", **{
        "range": 1200, "damage/shot": 150, "impact": 5, "turn rate": 0, "ammo": 2, "type": "HIGH_EXPLOSIVE",
        "energy/shot": 0, "chargedown": 1.0, "burst size": 2, "burst delay": 0.2, "proj speed": 600,
        "launch speed": 150, "flight time": 2.6, "proj hitpoints": 100, "tags": "SYSTEM", "tech/manufacturer": MFR,
        "primaryRoleStr": "Combo", "noDPSInTooltip": "TRUE"}), w, [], "The Requiem's pair of Tuning Spikes.")

    hdr = V.header("weapon_data.csv")
    for r in WEAPONS:
        r["number"] = ""
    write_csv("data/weapons/weapon_data.csv", hdr, WEAPONS)
    for wid, w in WPN.items():
        write_json("data/weapons/%s.wpn" % wid, w)
    for pid, p in PROJ.items():
        write_json("data/weapons/proj/%s.proj" % pid, p)


# ===================================================================================================== hulls
FIGHTER_IDS = ["rsl_trill", "rsl_cadenza", "rsl_requiem"]
SHIP_IDS = ["rsl_gracenote", "rsl_refrain", "rsl_staccato", "rsl_cadence", "rsl_tremolo", "rsl_halo",
            "rsl_conductor", "rsl_virtuoso", "rsl_virtuoso_unsung", "rsl_cantor", "rsl_cantor_spire",
            "rsl_cantor_bell", "rsl_cantor_loft"] + FIGHTER_IDS
CORE = "rsl_lattice_core"
BUILTIN_MODS = {
    "rsl_gracenote": [CORE, "hiressensors"],
    "rsl_refrain": [CORE, "escort_package"],
    "rsl_staccato": [CORE, "rsl_fracture", "unstable_injector"],
    "rsl_cadence": [CORE, "dedicated_targeting_core"],
    "rsl_tremolo": [CORE, "auxiliarythrusters"],
    "rsl_halo": [CORE, "expanded_deck_crew", "hardened_subsystems", "rsl_tuned_wings"],
    "rsl_conductor": [CORE, "stabilizedshieldemitter", "operations_center", "rsl_conductors_bridge"],
    "rsl_virtuoso": [CORE, "auxiliarythrusters", "rsl_stolen_time", "rsl_bravura", "rsl_concert_pitch"],
    "rsl_virtuoso_unsung": [CORE, "auxiliarythrusters", "rsl_stolen_time", "rsl_bravura_locked", "rsl_concert_pitch"],
    "rsl_cantor": [CORE, "rsl_phase_locked", "vastbulk", "axialrotation", "supercomputer"],
    "rsl_cantor_spire": [CORE, "rsl_phase_locked", "hardened_subsystems", "reduced_explosion", "do_not_fire_through"],
    "rsl_cantor_bell": [CORE, "rsl_phase_locked", "hardened_subsystems", "reduced_explosion", "do_not_fire_through"],
    "rsl_cantor_loft": [CORE, "rsl_phase_locked", "hardened_subsystems", "reduced_explosion", "do_not_fire_through"],
    "rsl_trill": [], "rsl_cadenza": [], "rsl_requiem": [],
}
BUILTIN_WEAPONS = {
    "rsl_halo": {"WS0009": "rsl_deco_halo_ring"},
    "rsl_cantor": {"WS0007": "rsl_deco_cantor_ring"},
    "rsl_refrain": {"WS0009": "rsl_deco_refrain_vane_r", "WS0010": "rsl_deco_refrain_vane_l"},
    "rsl_conductor": {"WS0001": "rsl_harmonic_spinal", "WS0010": "rsl_deco_conductor_blade_r",
                      "WS0011": "rsl_deco_conductor_blade_l"},
    "rsl_virtuoso": {"WS0001": "rsl_sforzando", "WS0001R": "rsl_sforzando", "WS0007": "rsl_deco_virtuoso_vane_r",
                     "WS0008": "rsl_deco_virtuoso_vane_l"},
    "rsl_virtuoso_unsung": {"WS0001": "rsl_sforzando_untuned", "WS0001R": "rsl_sforzando_untuned"},
}

# peer to clone, then the columns the design changes
HULLS = {
    "rsl_gracenote": ("wolf", dict(name="Grace Note", designation="Interceptor", **{
        "system id": "rsl_pitchshift", "fleet pts": 6, "hitpoints": 1700, "armor rating": 200, "max flux": 2500,
        "flux dissipation": 190, "ordnance points": 50, "max speed": 150, "acceleration": 140, "deceleration": 110,
        "max turn rate": 80, "turn acceleration": 160, "mass": 220, "shield type": "FRONT", "shield arc": 180,
        "shield upkeep": 0.4, "shield efficiency": 0.8, "supplies/rec": 6, "supplies/mo": 6, "peak CR sec": 240,
        "base value": 16000})),
    "rsl_refrain": ("hammerhead", dict(name="Refrain", designation="Escort", **{
        "system id": "rsl_ward", "fleet pts": 10, "hitpoints": 4800, "armor rating": 550, "max flux": 4500,
        "flux dissipation": 260, "ordnance points": 90, "max speed": 85, "acceleration": 65, "deceleration": 50,
        "max turn rate": 32, "turn acceleration": 64, "mass": 420, "shield type": "OMNI", "shield arc": 270,
        "shield upkeep": 0.4, "shield efficiency": 0.8, "supplies/rec": 10, "supplies/mo": 10, "base value": 45000})),
    "rsl_staccato": ("medusa", dict(name="Staccato", designation="Striker", **{
        "system id": "rsl_gracedash", "fleet pts": 12, "hitpoints": 3800, "armor rating": 350, "max flux": 5600,
        "flux dissipation": 360, "ordnance points": 100, "max speed": 100, "acceleration": 90, "deceleration": 70,
        "max turn rate": 45, "turn acceleration": 110, "mass": 330, "shield type": "OMNI", "shield arc": 180,
        "shield upkeep": 0.35, "shield efficiency": 0.7, "supplies/rec": 12, "supplies/mo": 12, "base value": 62000,
        "tags": BP})),
    "rsl_cadence": ("eagle", dict(name="Cadence", designation="Line Cruiser", **{
        "system id": "rsl_crescendo", "fleet pts": 14, "hitpoints": 8000, "armor rating": 950, "max flux": 11000,
        "flux dissipation": 680, "ordnance points": 155, "max speed": 60, "mass": 1250, "shield type": "FRONT",
        "shield arc": 240, "shield upkeep": 0.4, "shield efficiency": 0.8, "supplies/rec": 20, "supplies/mo": 20,
        "base value": 110000})),
    "rsl_tremolo": ("fury", dict(name="Tremolo", designation="Skirmisher", **{
        "system id": "rsl_standingwave", "fleet pts": 15, "hitpoints": 7000, "armor rating": 800, "max flux": 10000,
        "flux dissipation": 620, "ordnance points": 145, "max speed": 80, "acceleration": 70, "deceleration": 55,
        "max turn rate": 25, "turn acceleration": 45, "mass": 1500, "shield type": "OMNI", "shield arc": 200,
        "shield upkeep": 0.3, "shield efficiency": 0.75, "supplies/rec": 22, "supplies/mo": 22,
        "base value": 120000})),
    "rsl_halo": ("astral", dict(name="Halo", designation="Carrier", **{
        "system id": "rsl_stillwater", "fleet pts": 26, "hitpoints": 12000, "armor rating": 1100, "max flux": 14000,
        "flux dissipation": 700, "ordnance points": 270, "fighter bays": 4, "max speed": 35, "acceleration": 20,
        "deceleration": 15, "max turn rate": 8, "turn acceleration": 6, "mass": 3200, "shield type": "FRONT",
        "shield arc": 300, "shield upkeep": 0.5, "shield efficiency": 0.8, "supplies/rec": 40, "supplies/mo": 40,
        "base value": 380000})),
    "rsl_conductor": ("odyssey", dict(name="Conductor", designation="Battleship", **{
        "system id": "rsl_symstrike", "fleet pts": 28, "hitpoints": 16000, "armor rating": 1500, "max flux": 18000,
        "flux dissipation": 1050, "ordnance points": 320, "fighter bays": "", "max speed": 40, "acceleration": 25,
        "deceleration": 20, "max turn rate": 8, "turn acceleration": 10, "mass": 3400, "shield type": "FRONT",
        "shield arc": 240, "shield upkeep": 0.4, "shield efficiency": 0.8, "supplies/rec": 45, "supplies/mo": 45,
        "base value": 420000})),
    "rsl_virtuoso": ("odyssey", dict(name="Virtuoso", designation="Duelist", **{
        "system id": "rsl_glissando", "fleet pts": 40, "hitpoints": 12000, "armor rating": 1200, "max flux": 15000,
        "flux dissipation": 1200, "ordnance points": 260, "fighter bays": "", "max speed": 70, "acceleration": 85,
        "deceleration": 75, "max turn rate": 24, "turn acceleration": 45, "mass": 2600, "shield type": "OMNI",
        "shield arc": 240, "shield upkeep": 0.4, "shield efficiency": 0.5, "supplies/rec": 80, "supplies/mo": 80,
        "peak CR sec": 420, "CR loss/sec": 0.3, "base value": 1200000, "hints": "UNBOARDABLE",
        "tags": "restricted, no_dealer, no_drop, no_bp_drop, no_sell"})),
    "rsl_virtuoso_unsung": ("odyssey", dict(name="Virtuoso (Unsung)", designation="Duelist Prototype", **{
        "system id": "rsl_glissando_unsung", "fleet pts": 30, "hitpoints": 10000, "armor rating": 1000,
        "max flux": 12500, "flux dissipation": 950, "ordnance points": 220, "fighter bays": "", "max speed": 55,
        "acceleration": 38, "deceleration": 34, "max turn rate": 12, "turn acceleration": 17, "mass": 2600,
        "shield type": "OMNI", "shield arc": 240, "shield upkeep": 0.4, "shield efficiency": 0.85,
        "supplies/rec": 55, "supplies/mo": 55, "peak CR sec": 360, "CR loss/sec": 0.3, "base value": 700000,
        "hints": "UNBOARDABLE", "tags": "restricted, no_dealer, no_drop, no_bp_drop, no_sell"})),
    "rsl_cantor": ("station2_hightech", dict(name="Cantor Array", designation="Lattice Station", **{
        "system id": "rsl_grandchorus", "hitpoints": 40000, "armor rating": 1800, "max flux": 20000,
        "flux dissipation": 1200, "ordnance points": 300, "tags": "", "tech/manufacturer": MFR})),
    "rsl_cantor_spire": ("module_hightech_attack", dict(name="Spire", designation="Lance Petal", **{
        "hitpoints": 12000, "armor rating": 1500, "max flux": 12000, "flux dissipation": 800,
        "ordnance points": 200, "supplies/rec": 1, "supplies/mo": 1})),
    "rsl_cantor_bell": ("module_hightech_attack", dict(name="Bell", designation="Defense Petal", **{
        "hitpoints": 9000, "armor rating": 1250, "max flux": 9000, "flux dissipation": 700, "ordnance points": 160,
        "shield type": "FRONT", "shield arc": 150, "shield upkeep": 0.4, "shield efficiency": 1, "supplies/rec": 1, "supplies/mo": 1})),
    "rsl_cantor_loft": ("module_hightech_hangar", dict(name="Choir Loft", designation="Hangar Petal", **{
        "system id": "", "hitpoints": 8000, "armor rating": 1100, "max flux": 8000, "flux dissipation": 600,
        "ordnance points": 150, "fighter bays": 2, "supplies/rec": 1, "supplies/mo": 1})),
    # fighters: Thunder / Broadsword / Dagger peers
    "rsl_trill": ("thunder", dict(name="Trill", designation="Interceptor", **{
        "hitpoints": 350, "armor rating": 50, "max speed": 470, "acceleration": 1000, "deceleration": 800,
        "max turn rate": 240, "turn acceleration": 520, "base value": 0})),
    "rsl_cadenza": ("broadsword", dict(name="Cadenza", designation="Heavy Fighter", **{
        "hitpoints": 550, "armor rating": 100, "max speed": 260, "base value": 0})),
    "rsl_requiem": ("dagger", dict(name="Requiem", designation="Bomber", **{
        "hitpoints": 650, "armor rating": 100, "max speed": 230, "base value": 0})),
}
HULL_DESC = {
    "rsl_gracenote": "A lattice dart barely larger than its own crystal. The Grace Note flips its core between two "
                     "tunings in an instant: Harmonic, with the shield up and the seams running teal, or Discord, with "
                     "the shield folded away, the seams burning violet and every weapon pushed past its rating.",
    "rsl_refrain": "A stocky escort built around two hinged armor vanes. When the Refrain ties its core to an ally's, "
                   "the vanes swing forward over its bow and a share of everything that hits the ally arrives on the "
                   "Refrain's shield instead.",
    "rsl_staccato": "A needle hull with forward-swept wings and a drive tuned for short, violent bursts. Its weapons "
                    "leave fracture lines in whatever they hit, and enough of them make plating simply come apart.",
    "rsl_cadence": "The Choir's line cruiser: an arrowhead with two accelerator rails swept back as barbs. Its "
                   "Crescendo lets the energy batteries feed on their own rhythm, every hit quickening the next.",
    "rsl_tremolo": "Two narrow hulls joined by lattice girders, with real empty space between them. The Tremolo marks "
                   "a point in space with a standing wave and can snap back to it, shedding the damage it took since.",
    "rsl_halo": "A carrier threaded through a great ring that turns in a well at its heart. When the ring spins up, "
                "the space around the Halo goes still: shots slow to a crawl and missile seekers lose their song.",
    "rsl_conductor": "A long steel blade split into two prongs with the Harmonic Driver set between them. The "
                     "Conductor's core does not just resonate, it leads: every Lattice ship near it tunes to it, and "
                     "what it marks, the whole chorus strikes.",
    "rsl_virtuoso": "The Choir's lost first soloist, finished. A rapier of a capital with two Sforzando lances on its "
                    "shoulders, a drive that skips across space and leaves a string behind it, and a core that feeds "
                    "on the readiness of everything it wounds. At full voice, its seams burn gold.",
    "rsl_virtuoso_unsung": "A prototype that sang alone after its chorus died. The sash is bare metal, the lances are "
                           "out of true and half the cells are dark, but it is still the fastest capital you have ever "
                           "seen move, and it still takes what it needs from its enemies.",
    "rsl_cantor": "A lattice station: a crystal heart in a six-petal rosette, with a ring turning slowly around it. "
                  "When a petal dies, its stored resonance floods the others.",
    "rsl_cantor_spire": "A lance petal of the Cantor Array.",
    "rsl_cantor_bell": "A defensive petal of the Cantor Array, full of flak and point defense.",
    "rsl_cantor_loft": "A hangar petal of the Cantor Array.",
    "rsl_trill": "A needle interceptor with a micro-rail in its nose and canards for its tightest turns. Trills hunt "
                 "fighters and missiles in pairs of notes, never far from the carrier that tuned them.",
    "rsl_cadenza": "A heavy fighter built around twin rails. Cadenzas engage from well outside the range most fighters "
                   "fight at, and keep plucking at a target until it breaks.",
    "rsl_requiem": "A rail bomber: one heavy slug that punches through armor and out the far side, and a pair of Tuning "
                   "Spikes that the slug's own hits - or any Lattice energy weapon - will detonate.",
}


def hull_rows():
    rows = []
    for hid, (peer, ch) in HULLS.items():
        ch = dict(ch)
        ch.setdefault("tech/manufacturer", MFR)
        is_station_part = hid.startswith("rsl_cantor")
        if hid in FIGHTER_IDS:
            ch.setdefault("tags", "")
            ch.setdefault("codex variant id", "")
        elif not is_station_part:
            ch.setdefault("tags", BP)
            ch.setdefault("codex variant id", hid + "_Standard")
        r = V.clone_row("ship_data.csv", peer, id=hid, number="", **ch)
        rows.append(r)
        desc(hid, "SHIP", HULL_DESC[hid])
    write_csv("data/hulls/ship_data.csv", V.header("ship_data.csv"), rows)


def ship_files():
    """Post-process the .ship files finish.py wrote; derive the Unsung's .ship from the Virtuoso's."""
    vir = sslib.load_loose_json(P("data/hulls/rsl_virtuoso.ship"))
    uns = json.loads(json.dumps(vir))
    uns.update(hullId="rsl_virtuoso_unsung", hullName="Virtuoso (Unsung)",
               spriteName="graphics/rsl/ships/rsl_virtuoso_unsung.png")
    uns["weaponSlots"] = [s for s in uns["weaponSlots"] if s["type"] != "DECORATIVE"]
    write_json("data/hulls/rsl_virtuoso_unsung.ship", uns)
    for hid in SHIP_IDS:
        p = "data/hulls/%s.ship" % hid
        s = sslib.load_loose_json(P(p))
        s["style"] = "RSL"
        for e in s.get("engineSlots", []):
            e["style"] = "RSL"
        s["builtInMods"] = BUILTIN_MODS[hid]
        s["builtInWeapons"] = BUILTIN_WEAPONS.get(hid, {})
        for slot in s["weaponSlots"]:
            if slot["type"] == "DECORATIVE":
                slot["arc"] = 360.0   # the deco effects set the angle every frame; 360 never clamps it
                # deco parts pivot about their sprite centre (art + glow renderer); a HARDPOINT mount would draw the
                # sprite a quarter of its length forward of the slot, detaching it from the hull
                slot["mount"] = "TURRET"
            elif slot["id"] in s["builtInWeapons"]:
                slot["type"] = "BUILT_IN"   # as vanilla (Onslaught TPCs): the weapon cannot be removed in refit
            if slot["type"] == "STATION_MODULE":
                slot["mount"] = "HARDPOINT"   # as every vanilla station
                slot["arc"] = 4.0
        shield_fit(s)
        if hid in ("rsl_cantor_spire", "rsl_cantor_bell", "rsl_cantor_loft"):
            s["moduleAnchor"] = [-float(s["center"][1]), 0.0]   # the module root = the sprite's bottom edge
        write_json(p, s)
    return {hid: sslib.load_loose_json(P("data/hulls/%s.ship" % hid)) for hid in SHIP_IDS}


SHIELD_MARGIN = 1.10   # shield radius = 10% beyond the farthest opaque pixel (hull + deco parts at rest)


def opaque_points(png):
    from PIL import Image
    import numpy as np
    a = np.asarray(Image.open(P(png)).convert("RGBA"))[..., 3] > 40
    ys, xs = np.nonzero(a)
    return xs + 0.5, ys + 0.5, a.shape[1], a.shape[0]


def shield_fit(s):
    """Shield radius from the sprite itself (plus deco parts drawn at their rest angle); collision radius >= it."""
    import math
    import numpy as np
    xs, ys, W, H = opaque_points(s["spriteName"])
    sx, sy = sslib.image_to_ship(xs, ys, s["center"], H)
    pts = [(sx, sy)]
    deco = {sid: wid for sid, wid in s["builtInWeapons"].items() if WPN.get(wid, {}).get("type") == "DECORATIVE"}
    for slot in s["weaponSlots"]:
        wid = deco.get(slot["id"])
        if not wid:
            continue
        u, v, w, h = opaque_points(WPN[wid]["turretSprite"])
        fwd, left = h / 2.0 - v, w / 2.0 - u
        a = math.radians(slot["angle"])
        lx, ly = slot["locations"][0], slot["locations"][1]
        pts.append((lx + fwd * math.cos(a) - left * math.sin(a), ly + fwd * math.sin(a) + left * math.cos(a)))
    px = np.concatenate([p[0] for p in pts])
    py = np.concatenate([p[1] for p in pts])
    cx = float(s["shieldCenter"][0])
    r = float(np.max(np.hypot(px - cx, py - float(s["shieldCenter"][1]))))
    s["shieldRadius"] = int(math.ceil(r * SHIELD_MARGIN))
    s["collisionRadius"] = max(int(s["collisionRadius"]), s["shieldRadius"])


# ===================================================================================================== variants
OP = {}          # weapon id -> OP


def mod_cost(mod, size):
    col = {"FRIGATE": "cost_frigate", "DESTROYER": "cost_dest", "CRUISER": "cost_cruiser",
           "CAPITAL_SHIP": "cost_capital"}[size]
    return int(float(V.row("hull_mods.csv", mod)[col]))


FITS = {"ENERGY": {"ENERGY", "HYBRID", "SYNERGY", "UNIVERSAL"}, "BALLISTIC": {"BALLISTIC", "HYBRID", "COMPOSITE", "UNIVERSAL"},
        "MISSILE": {"MISSILE", "SYNERGY", "COMPOSITE", "UNIVERSAL"}, "HYBRID": {"HYBRID", "UNIVERSAL"}}
SIZES = ["SMALL", "MEDIUM", "LARGE"]
MAXVC = {"FRIGATE": 10, "DESTROYER": 20, "CRUISER": 30, "CAPITAL_SHIP": 50}
WING_OP = {r["id"]: int(float(r["op cost"])) for r in V.rows("wing_data.csv") if r.get("op cost")}

LOADOUTS = {  # variant id: (hull, display name, {slot: weapon}, wings, hullmods)
    "rsl_gracenote_Standard": ("rsl_gracenote", "Standard", {
        "WS0001": "rsl_pizzicato", "WS0001R": "rsl_pizzicato", "WS0003": "rsl_shardcaster"}, [], []),
    "rsl_refrain_Standard": ("rsl_refrain", "Standard", {
        "WS0001": "rsl_lattice_lance", "WS0002": "rsl_chime", "WS0002R": "rsl_chime", "WS0004": "rsl_flechette",
        "WS0005": "rsl_chime", "WS0005R": "rsl_chime", "WS0007": "rsl_tuningspike", "WS0007R": "rsl_tuningspike"},
        [], ["hardenedshieldemitter"]),
    "rsl_staccato_Standard": ("rsl_staccato", "Standard", {
        "WS0001": "rsl_arpeggio", "WS0001R": "rsl_arpeggio", "WS0003": "rsl_flechette", "WS0004": "rsl_pizzicato",
        "WS0004R": "rsl_pizzicato", "WS0006": "rsl_chime", "WS0006R": "rsl_chime", "WS0008": "rsl_tuningspike",
        "WS0008R": "rsl_tuningspike"}, [], []),
    "rsl_cadence_Standard": ("rsl_cadence", "Standard", {
        "WS0001": "rsl_harmonic_driver", "WS0001R": "rsl_harmonic_driver", "WS0003": "rsl_cantus",
        "WS0004": "rsl_arpeggio", "WS0004R": "rsl_arpeggio", "WS0006": "rsl_pizzicato", "WS0006R": "rsl_pizzicato",
        "WS0008": "rsl_chime", "WS0008R": "rsl_chime", "WS0010": "rsl_tuningspike", "WS0010R": "rsl_tuningspike"},
        [], []),
    "rsl_tremolo_Standard": ("rsl_tremolo", "Standard", {
        "WS0001": "rsl_lattice_lance", "WS0001R": "rsl_lattice_lance", "WS0003": "rsl_sostenuto",
        "WS0004": "rsl_flechette", "WS0004R": "rsl_flechette", "WS0006": "rsl_chime", "WS0006R": "rsl_chime",
        "WS0008": "rsl_tuningspike", "WS0008R": "rsl_tuningspike"}, [], ["hardenedshieldemitter"]),
    "rsl_halo_Standard": ("rsl_halo", "Standard", {
        "WS0001": "rsl_sostenuto", "WS0002": "rsl_cantus", "WS0002R": "rsl_cantus", "WS0003": "rsl_chime",
        "WS0003R": "rsl_chime", "WS0004": "rsl_chime", "WS0004R": "rsl_chime", "WS0005": "rsl_lattice_lance",
        "WS0005R": "rsl_lattice_lance", "WS0006": "rsl_tuningspike", "WS0006R": "rsl_tuningspike"},
        ["rsl_trill_wing", "rsl_cadenza_wing", "rsl_requiem_wing", "rsl_requiem_wing"], []),
    "rsl_conductor_Standard": ("rsl_conductor", "Standard", {
        "WS0002": "rsl_harmonic_driver", "WS0002R": "rsl_harmonic_driver", "WS0003": "rsl_arpeggio",
        "WS0003R": "rsl_arpeggio", "WS0004": "rsl_pizzicato", "WS0004R": "rsl_pizzicato", "WS0005": "rsl_cantus",
        "WS0005R": "rsl_cantus", "WS0006": "rsl_lattice_lance", "WS0006R": "rsl_lattice_lance",
        "WS0007": "rsl_sostenuto", "WS0008": "rsl_chime", "WS0008R": "rsl_chime", "WS0009": "rsl_tuningspike",
        "WS0009R": "rsl_tuningspike"}, [], ["hardenedshieldemitter"]),
    "rsl_virtuoso_Standard": ("rsl_virtuoso", "Soloist", {
        "WS0002": "rsl_arpeggio", "WS0002R": "rsl_arpeggio", "WS0003": "rsl_flechette", "WS0003R": "rsl_flechette",
        "WS0004": "rsl_pizzicato", "WS0004R": "rsl_pizzicato", "WS0005": "rsl_chime", "WS0005R": "rsl_chime",
        "WS0006": "rsl_chime", "WS0006R": "rsl_chime"}, [], ["hardenedshieldemitter"]),
    "rsl_virtuoso_unsung_Standard": ("rsl_virtuoso_unsung", "Unsung", {
        "WS0002": "rsl_arpeggio", "WS0002R": "rsl_arpeggio", "WS0003": "rsl_flechette", "WS0003R": "rsl_flechette",
        "WS0004": "rsl_pizzicato", "WS0004R": "rsl_pizzicato", "WS0005": "rsl_chime", "WS0005R": "rsl_chime",
        "WS0006": "rsl_chime", "WS0006R": "rsl_chime"}, [], []),
    "rsl_cantor_spire_Standard": ("rsl_cantor_spire", "Standard", {
        "WS0001": "rsl_harmonic_driver", "WS0002": "rsl_harmonic_driver", "WS0003": "rsl_chime", "WS0003R": "rsl_chime",
        "WS0004": "rsl_lattice_lance"}, [], []),
    "rsl_cantor_bell_Standard": ("rsl_cantor_bell", "Standard", {
        "WS0001": "rsl_cantus", "WS0001R": "rsl_cantus", "WS0002": "rsl_chime", "WS0002R": "rsl_chime",
        "WS0003": "rsl_chime", "WS0003R": "rsl_chime", "WS0004": "rsl_arpeggio"}, [], []),
    "rsl_cantor_loft_Standard": ("rsl_cantor_loft", "Standard", {
        "WS0002": "rsl_chime", "WS0002R": "rsl_chime", "WS0003": "rsl_lattice_lance", "WS0004": "rsl_cantus"},
        ["rsl_trill_wing", "rsl_cadenza_wing"], []),
}


def variants(ships):
    for r in WEAPONS:
        OP[r["id"]] = int(float(r["OPs"] or 0))
    wtype = {wid: (w["type"], w["size"]) for wid, w in WPN.items()}
    ops = {r["id"]: int(float(r["ordnance points"] or 0)) for r in
           sslib.read_csv(P("data/hulls/ship_data.csv"), key="id")}
    shutil.rmtree(P("data/variants/rsl"), ignore_errors=True)
    report = []
    for vid, (hid, name, fit, wings, mods) in LOADOUTS.items():
        ship = ships[hid]
        slots = {s["id"]: s for s in ship["weaponSlots"]}
        size = ship["hullSize"]
        used = 0
        for sid, wid in fit.items():
            s = slots[sid]
            t, sz = wtype[wid]
            if s["type"] not in FITS[t] or not (0 <= SIZES.index(s["size"]) - SIZES.index(sz) <= 1):
                raise ValueError("%s: %s (%s %s) does not fit slot %s (%s %s)" % (vid, wid, t, sz, sid, s["type"],
                                                                                 s["size"]))
            used += OP[wid]
        used += sum(WING_OP[w] for w in wings)
        used += sum(mod_cost(m, size) for m in mods)
        budget = ops[hid]
        if used > budget:
            raise ValueError("%s over budget: %d > %d" % (vid, used, budget))
        free = budget - used
        if not hid.startswith("rsl_cantor"):
            mods = list(mods)
            pref = ["hardenedshieldemitter", "fluxbreakers", "reinforcedhull", "turretgyros"]  # no beams left: no Advanced Optics
            if "dedicated_targeting_core" not in BUILTIN_MODS[hid]:
                pref.insert(1, "targetingunit")
            for m in pref:
                c = mod_cost(m, size)
                if m not in mods and free - c >= MAXVC[size] + 4:
                    mods.append(m)
                    free -= c
        vents = min(MAXVC[size], free)
        caps = min(MAXVC[size], free - vents)
        groups, by = [], {}
        built = {sid: wid for sid, wid in BUILTIN_WEAPONS.get(hid, {}).items() if WPN[wid]["type"] != "DECORATIVE"}
        for sid, wid in list(built.items()) + list(fit.items()):
            by.setdefault(wid, {})[sid] = wid
        order = sorted(by, key=lambda w: (w not in built.values(), WPN[w]["type"] == "MISSILE", "PD" in WEAPONS_BY_ID[w]["hints"], -OP[w]))
        for i, wid in enumerate(order[:7]):
            pd = "PD" in WEAPONS_BY_ID[wid]["hints"]
            groups.append({"autofire": pd or i >= 2, "mode": "LINKED", "weapons": by[wid]})
        for wid in order[7:]:
            groups[-1]["weapons"].update(by[wid])
        v = {"variantId": vid, "hullId": hid, "displayName": name, "fluxVents": vents, "fluxCapacitors": caps,
             "hullMods": mods, "permaMods": [], "sMods": [], "wings": wings, "weaponGroups": groups,
             "goalVariant": True, "quality": 0}
        if hid == "rsl_cantor":
            pass
        write_json("data/variants/rsl/%s.variant" % vid, v)
        report.append("%-30s OP %3d/%3d  vents %2d caps %2d  mods %s" % (vid, budget - free + vents + caps, budget, vents, caps, ",".join(mods)))
    # the station core: modules on their STATION_MODULE slots
    core = ships["rsl_cantor"]
    mods = []
    for s in core["weaponSlots"]:
        if s["type"] == "STATION_MODULE":
            pass
    spec_slots = {s["id"]: s for s in json.load(open(P("art_src/specs/rsl_cantor.json")))["slots"]}
    for sid, s in spec_slots.items():
        if s.get("type") == "STATION_MODULE":
            mods.append({sid: s["module"] + "_Standard"})
    write_json("data/variants/rsl/rsl_cantor_Standard.variant", {
        "variantId": "rsl_cantor_Standard", "hullId": "rsl_cantor", "displayName": "Standard", "fluxVents": 0,
        "fluxCapacitors": 0, "hullMods": [], "permaMods": [], "sMods": [], "wings": [], "weaponGroups": [],
        "quality": 0.5, "modules": mods})
    print("\n".join(report))


WEAPONS_BY_ID = {}

# wing id: (peer wing, hull, {slot: weapon}, wing_data changes)
WINGS = {
    "rsl_trill_wing": ("thunder_wing", "rsl_trill", {"WS0001": "rsl_microrail_ftr"}, {
        "tags": "fighter3, interceptor, " + BP, "fleet pts": 4, "op cost": 8, "num": 3, "refit": 10,
        "role desc": "Interceptor", "base value": 6000}),
    "rsl_cadenza_wing": ("broadsword_wing", "rsl_cadenza", {"WS0001": "rsl_cadenza_rail_ftr",
                                                            "WS0001R": "rsl_cadenza_rail_ftr"}, {
        "tags": "fighter4, fighter, " + BP, "fleet pts": 6, "op cost": 12, "num": 3, "refit": 12,
        "role desc": "Heavy Fighter", "base value": 8000}),
    "rsl_requiem_wing": ("dagger_wing", "rsl_requiem", {"WS0001": "rsl_requiem_slug_ftr",
                                                        "WS0002": "rsl_tuningspike_ftr"}, {
        "tags": "bomber4, bomber, " + BP, "fleet pts": 6, "op cost": 16, "num": 3, "refit": 18,
        "role desc": "Rail Bomber", "base value": 10000}),
}


def wings():
    rows = []
    for wing, (peer, hull, fit, ch) in WINGS.items():
        vid = hull + "_Wing"
        groups = [{"autofire": False, "mode": "LINKED", "weapons": {sid: wid}} for sid, wid in fit.items()]
        write_json("data/variants/rsl/%s.variant" % vid, {
            "variantId": vid, "hullId": hull, "displayName": WINGS_NAME[wing], "fluxVents": 0, "fluxCapacitors": 0,
            "hullMods": ["no_weapon_flux"], "permaMods": [], "sMods": [], "wings": [], "weaponGroups": groups,
            "quality": 0.5})
        rows.append(V.clone_row("wing_data.csv", peer, id=wing, variant=vid, **ch))
    write_csv("data/hulls/wing_data.csv", V.header("wing_data.csv"), rows)


WINGS_NAME = {"rsl_trill_wing": "Interceptor", "rsl_cadenza_wing": "Heavy Fighter", "rsl_requiem_wing": "Bomber"}
WING_OP.update({w: int(v[3]["op cost"]) for w, v in WINGS.items()})   # carrier variants are budgeted before wings()


# ===================================================================================================== systems
SYS = "rsl.systems."
SYSTEMS = [  # id, name, csv overrides, .system extras, description
    ("rsl_pitchshift", "Pitch Shift", {"charge up": 0.2, "down": 0.2, "cooldown": 1, "toggle": "TRUE"},
     {"aiType": "CUSTOM", "aiScript": SYS + "PitchShiftAI", "useSound": "system_phase_skimmer",
      "runScriptWhileIdle": True},
     "Toggles the lattice core between two tunings. Harmonic (off): shields available, +25% flux dissipation and "
     "energy weapons add EMP. Discord (on): shields locked, +30% top speed and +20% weapon damage. Overtone: "
     "switching tunings releases an EMP pulse."),
    ("rsl_gracedash", "Grace Dash", {"flux/second": 1, "max uses": 2, "regen": 0.1, "charge up": 0.25, "active": 0.4,
                                     "down": 0.4, "noShield": "TRUE", "noVent": "TRUE"},
     {"type": "ENGINE_MOD", "aiType": "BURN_DRIVE", "engineGlowColor": [100, 230, 220, 255],
      "engineGlowLengthMult": 3, "engineGlowWidthMult": 1.5, "engineGlowGlowMult": 3, "clampTurnRateAfter": True,
      "clampMaxSpeedAfter": True, "alwaysAccelerate": True, "useSound": "system_plasma_burn",
      "loopSound": "system_plasma_burn_loop", "outOfUsesSound": "engine_disabled",
      "aiHints": {"activeSpeedIncrease": 0, "burstMovementPotential": 350, "averageSpeedIncrease": 40}},
     "A short, violent burst of thrust. Overtone: the dash leaves a resonant wake that arcs EMP into enemies that pass "
     "through it."),
    ("rsl_ward", "Sympathetic Ward", {"charge up": 0.3, "active": 7, "down": 0.5, "cooldown": 12},
     {"aiType": "CUSTOM", "aiScript": SYS + "SympatheticWardAI", "useSound": "system_targeting_feed_loop"},
     "Ties the Refrain's core to the most endangered ally within 800 units. 40% of the damage that ally takes is "
     "redirected to the Refrain's shield as flux (or hull if the shield is down), and the armor vanes swing forward "
     "over the bow. Overtone: redirected damage builds double Resonance and the Refrain takes 30% less beam damage."),
    ("rsl_crescendo", "Crescendo", {"charge up": 0.5, "active": 6, "down": 0.5, "cooldown": 14},
     {"aiType": "WEAPON_BOOST", "weaponGlowColor": [100, 230, 220, 255], "weaponTypes": ["ENERGY"],
      "useSound": "system_high_energy_focus_activate", "outOfUsesSound": "gun_out_of_ammo"},
     "Every energy weapon hit adds a Crescendo stack (up to 20): +5% energy rate of fire and +3% energy flux cost per "
     "stack. Overtone: reaching 20 stacks fires a Fortissimo - every energy weapon releases one extra empowered shot "
     "- and the ship sheds 30% of its soft flux."),
    ("rsl_standingwave", "Standing Wave", {"charge up": 0.1, "down": 0.2, "cooldown": 12, "toggle": "TRUE"},
     {"aiType": "CUSTOM", "aiScript": SYS + "StandingWaveAI", "useSound": "system_phase_skimmer"},
     "First use drops a standing-wave node at the ship's position. Using it again within 8 seconds snaps the ship "
     "back to the node and restores 40% of the armor and hull lost since. Overtone: the afterimage left behind "
     "detonates for 400 energy damage and 600 EMP around it."),
    ("rsl_stillwater", "Stillwater Halo", {"charge up": 1, "active": 8, "down": 1, "cooldown": 20},
     {"aiType": "CUSTOM", "aiScript": SYS + "StillwaterHaloAI", "useSound": "system_temporalshell",
      "loopSound": "system_temporalshell_loop"},
     "Creates a 700-unit zone of still space around the Halo. Enemy projectiles inside slow by 60% and enemy missiles "
     "lose their lock. The Halo's own flux dissipation drops by 30% while it runs. Overtone: damage the zone absorbs "
     "is turned into Resonance for every Lattice ship inside it."),
    ("rsl_symstrike", "Sympathetic Strike", {"charge up": 1.5, "active": 0.3, "down": 0.5, "cooldown": 18,
                                             "flux/use": 1500},
     {"aiType": "CUSTOM", "aiScript": SYS + "SympatheticStrikeAI", "useSound": "tachyon_lance_fire"},
     "After a 1.5 second charge, the prongs discharge a resonant beam into the target (2,000 range, 800 energy "
     "damage) and mark it for 8 seconds: all Lattice ships deal +20% damage to it. Overtone: the beam chains to a "
     "second enemy, which is marked as well."),
    ("rsl_glissando", "Glissando", {"max uses": 3, "regen": 0.1667, "charge up": 0.05, "active": 0.45, "down": 0.1,
                                    "cooldown": 0.5, "noFiring": "TRUE"},
     {"aiType": "CUSTOM", "aiScript": SYS + "GlissandoAI", "useSound": "system_phase_skimmer"},
     "A 720-unit blink-dash in the direction of movement; thrusting mid-dash bends its path, so it can change direction. 2 "
     "charges (3 in Bravura). The ship cannot be hit mid-dash. Costs 1% combat readiness "
     "per dash and cannot be used below 30%. The path stays behind as a taut string for 1.2 seconds - it deletes "
     "enemy projectiles that cross it - then snaps: 400 energy damage to every enemy touching it (fighters and "
     "missiles are destroyed) and 2% CR stolen from each ship hit. For 2 seconds after a dash the Sforzando lances "
     "are Accented. Overtone: the string snaps twice and the dash refunds half a charge."),
    ("rsl_glissando_unsung", "Glissando (Unsung)", {"max uses": 2, "regen": 0.125, "charge up": 0.05, "active": 0.45,
                                                    "down": 0.1, "cooldown": 0.5, "noFiring": "TRUE"},
     {"aiType": "CUSTOM", "aiScript": SYS + "GlissandoAI", "useSound": "system_phase_skimmer"},
     "An untuned, steerable 720-unit blink-dash: 2 charges, 1.5% combat readiness per dash, untargetable for 0.2 seconds. The string it "
     "leaves blocks projectiles for 1.2 seconds but never snaps."),
    ("rsl_grandchorus", "Grand Chorus", {"charge up": 1, "active": 0.5, "down": 0.5, "cooldown": 25},
     {"aiType": "CUSTOM", "aiScript": SYS + "GrandChorusAI", "useSound": "tachyon_lance_fire"},
     "Every petal discharges a synchronized resonant lance into the nearest enemy in its sector (600 energy damage "
     "each). Overtone: an expanding harmonic ring flames out fighters and throws missiles off their targets."),
]


def systems():
    hdr = V.header("ship_systems.csv")
    rows = []
    for sid, name, csvo, sysx, text in SYSTEMS:
        r = {c: "" for c in hdr}
        r.update(name=name, id=sid, icon="graphics/rsl/icons/hullsys/%s.png" % sid, tags="")
        r.update({k: str(v) for k, v in csvo.items()})
        rows.append(r)
        cls = {"rsl_glissando_unsung": "GlissandoStats"}.get(sid) or (
            "".join(p.capitalize() for p in sid[4:].split("_")) + "Stats")
        cls = {"PitchshiftStats": "PitchShiftStats", "GracedashStats": "GraceDashStats",
               "WardStats": "SympatheticWardStats", "StandingwaveStats": "StandingWaveStats",
               "StillwaterStats": "StillwaterHaloStats", "SymstrikeStats": "SympatheticStrikeStats",
               "GrandchorusStats": "GrandChorusStats"}.get(cls, cls)
        spec = {"id": sid, "type": "STAT_MOD", "statsScript": SYS + cls, "outOfUsesSound": "gun_out_of_ammo"}
        spec.update(sysx)
        write_json("data/shipsystems/%s.system" % sid, spec)
        desc(sid, "SHIP_SYSTEM", text)
    write_csv("data/shipsystems/ship_systems.csv", hdr, rows)


# ===================================================================================================== hullmods
HM = "rsl.hullmods."
HULLMODS = [  # id, name, script, desc, hidden, costs, tags
    ("rsl_lattice_core", "Lattice Core", "LatticeCore",
     "A crystalline resonator grown through the hull. It builds Resonance (0-100) from damage absorbed by shields and "
     "from this ship's hits on enemy hull and armor, and loses it slowly out of combat contact. At %s Resonance or "
     "more the core is in Overtone: the next ship-system use is empowered and spends %s Resonance. Lattice ships "
     "within %s units share %s of the Resonance they gain. The core's seams glow brighter with Resonance. "
     "Incompatible with Safety Overrides.", True, (0, 0, 0, 0)),
    ("rsl_conductors_bridge", "Conductor's Bridge", "ConductorsBridge",
     "Lattice allies within %s units receive %s Sympathy from this ship instead of the usual share, and gain %s "
     "Resonance per second while in range.", True, (0, 0, 0, 0)),
    ("rsl_fracture", "Fracture", "Fracture",
     "Hits from this ship's weapons on enemy hull or armor add a Fracture stack to the target (up to %s; stacks fade "
     "after %s without a new hit). The hit that would add a %s stack shatters the plating instead: %s bonus damage to "
     "armor at the impact point, and the stacks reset.", True, (0, 0, 0, 0)),
    ("rsl_stolen_time", "Stolen Time", "StolenTime",
     "Hull and armor damage this ship deals to enemy ships steals combat readiness: about %s CR per %s damage "
     "(scaled by target size), which the target loses and this ship gains. At most %s can be taken from any one "
     "ship. Destroying an enemy ship restores a large amount of CR at once: %s for a frigate up to %s for a capital. "
     "On the Virtuoso, CR gained while already at 100%% extends peak performance time instead (%s per 1%%). "
     "Theft (not kills) is half as effective when not piloted by the player.", True, (0, 0, 0, 0)),
    ("rsl_bravura", "Bravura", "Bravura",
     "At %s combat readiness the Virtuoso enters Bravura until its CR drops below %s: +%s top speed and "
     "maneuverability, +%s flux dissipation, +%s energy weapon rate of fire, +%s damage to shields, %s faster "
     "system recharge and %s Glissando charges, and the Sforzando lances are always Accented (%s damage). The seams "
     "burn gold-white and the shield turns white-teal.", True, (0, 0, 0, 0)),
    ("rsl_unbound", "Unbound Core", "UnboundCore",
     "The Virtuoso's core can drop its safety tuning, as Safety Overrides does for lesser hulls: +%s top speed, "
     "flux dissipation multiplied by %s, the zero-flux boost at any flux level and no active venting; peak "
     "performance time is cut to a third, but weapon range is untouched. Stolen Time pays the readiness back. "
     "Only the full Virtuoso can install it.", False, (0, 0, 0, 50)),
    ("rsl_bravura_locked", "Bravura (Silent)", "BravuraLocked",
     "INACTIVE on the Unsung. On the restored Virtuoso: at %s combat readiness it enters Bravura until its CR drops "
     "below %s: +%s top speed and maneuverability, +%s flux dissipation, +%s energy weapon rate of fire, +%s damage to "
     "shields, %s faster system recharge and %s Glissando charges, and the Sforzando lances are always Accented (%s "
     "damage).", True, (0, 0, 0, 0)),
    ("rsl_concert_pitch", "Concert Pitch", "ConcertPitch",
     "A rare lattice augment that retunes the core to a perfect reference pitch. +%s range for every Resonance Lattice "
     "weapon, +%s maximum combat readiness, +%s seconds of peak performance time and %s resistance to EMP damage. "
     "Lattice hulls only.", False, (6, 10, 15, 25)),
    ("rsl_phase_locked", "Phase-Locked Petals", "PhaseLockedPetals",
     "When a petal of the array is destroyed, its stored Resonance floods the core and the surviving petals, which "
     "jump straight into Overtone and gain %s weapon damage for the rest of the battle.", True, (0, 0, 0, 0)),
    ("rsl_tuned_wings", "Tuned Wings", "TunedWings",
     "Fighters within %s units of the ship are tuned to its ring: fighter replacement rate is %s faster while any "
     "of its wings fight inside the zone.", True, (0, 0, 0, 0)),
]


# rare: high tier, low drop rarity, not known from the start (must be learned); built into both Virtuosos regardless
HULLMOD_OVERRIDES = {"rsl_concert_pitch": {"tier": 3, "rarity": 0.1, "base value": 150000, "unlocked": "",
                                           "tags": BP}}


def hullmods():
    hdr = V.header("hull_mods.csv")
    rows = []
    for hid, name, cls, text, hidden, costs in HULLMODS:
        r = {c: "" for c in hdr}
        r.update({"name": name, "id": hid, "tier": 0, "tech/manufacturer": MFR,
                  "tags": "special" if not hidden else "", "uiTags": "Special", "base value": 10000 if not hidden else 0,
                  "unlocked": "TRUE", "hidden": "TRUE" if hidden else "", "cost_frigate": costs[0],
                  "cost_dest": costs[1], "cost_cruiser": costs[2], "cost_capital": costs[3], "script": HM + cls,
                  "desc": text, "short": text.split(".")[0] + ".",
                  "sprite": "graphics/rsl/icons/hullmods/%s.png" % hid})
        r.update(HULLMOD_OVERRIDES.get(hid, {}))
        rows.append(r)
    write_csv("data/hullmods/hull_mods.csv", hdr, rows)


# ===================================================================================================== faction etc.
FACTION = "rsl_choir"


def faction():
    f = V.spec("faction", "tritachyon")
    f.update({"id": FACTION, "color": [100, 230, 220, 255], "displayName": "Choir", "displayNameWithArticle": "the Choir",
              "displayNameLong": "the Resonance Choir", "displayNameLongWithArticle": "the Resonance Choir",
              "logo": "graphics/rsl/factions/rsl_flag.png", "crest": "graphics/rsl/factions/rsl_crest.png",
              "shipNamePrefix": "RCS", "variantOverrides": {}, "hullFrequency": {"tags": {}, "hulls": {}},
              "shipsWhenImporting": {"tags": [], "hulls": []},
              "knownShips": {"tags": [BP], "hulls": ["rsl_gracenote", "rsl_refrain", "rsl_staccato", "rsl_cadence",
                                                      "rsl_tremolo", "rsl_halo", "rsl_conductor"]},
              "priorityShips": {"tags": [BP], "hulls": []},
              "knownFighters": {"tags": [BP], "fighters": ["rsl_trill_wing", "rsl_cadenza_wing", "rsl_requiem_wing"]},
              "priorityFighters": {"tags": [BP], "fighters": []},
              "knownWeapons": {"tags": [BP], "weapons": []}, "priorityWeapons": {"tags": [BP], "weapons": []},
              "knownHullMods": {"tags": ["standard"], "hullMods": []},
              "weaponSellFrequency": {}, "hullmodSellFrequency": {}, "illegalCommodities": []})
    f["factionDoctrine"].update({"warships": 5, "carriers": 1, "phaseShips": 1})
    f["custom"]["offersCommissions"] = False
    f["custom"]["engagesInHostilities"] = False
    f["custom"]["buysAICores"] = False
    f["custom"].pop("punitiveExpeditionData", None)
    f["showInIntelTab"] = False
    write_json("data/world/factions/%s.faction" % FACTION, f)
    write_csv("data/world/factions/factions.csv", ["faction"], [{"faction": "data/world/factions/%s.faction" % FACTION}])
    write_json("data/world/factions/default_ship_roles.json", {
        "combatSmall": {"rsl_gracenote_Standard": 10},
        "combatSmallForSmallFleet": {"rsl_gracenote_Standard": 10},
        "fastAttack": {"rsl_gracenote_Standard": 5, "rsl_staccato_Standard": 5},
        "escortSmall": {"rsl_gracenote_Standard": 10},
        "combatMedium": {"rsl_refrain_Standard": 6, "rsl_staccato_Standard": 6},
        "escortMedium": {"rsl_refrain_Standard": 10},
        "combatLarge": {"rsl_cadence_Standard": 6, "rsl_tremolo_Standard": 6},
        "carrierLarge": {"rsl_halo_Standard": 10},
        "combatCapital": {"rsl_conductor_Standard": 6, "rsl_halo_Standard": 3},
    })


def config():
    glow = {}
    for hid in SHIP_IDS:
        glow[hid] = "graphics/rsl/ships/%s_glow.png" % hid
    glow["rsl_virtuoso_bravura"] = "graphics/rsl/ships/rsl_virtuoso_glow_bravura.png"
    for d in ("halo_ring", "cantor_ring", "refrain_vane_r", "refrain_vane_l", "conductor_blade_r", "conductor_blade_l",
              "virtuoso_vane_r", "virtuoso_vane_l"):
        glow["rsl_deco_" + d] = "graphics/rsl/weapons/deco/rsl_%s_glow.png" % d
    glow["rsl_deco_virtuoso_vane_r_bravura"] = "graphics/rsl/weapons/deco/rsl_virtuoso_vane_r_glow_bravura.png"
    glow["rsl_deco_virtuoso_vane_l_bravura"] = "graphics/rsl/weapons/deco/rsl_virtuoso_vane_l_glow_bravura.png"
    for k, v in glow.items():
        if not os.path.isfile(P(v)):
            raise FileNotFoundError(v)
    write_json("data/config/settings.json", {
        "plugins": {"rsl_combatPlugin": "rsl.combat.RslCombatPlugin"},
        "designTypeColors": {MFR: [100, 230, 220, 255]},
        "graphics": {"rsl_glow": glow, "rsl_fx": {"spike": OFFS["rsl_tuningspike_msl"]["sprite"]}},
    })
    hs = sslib.load_loose_json(os.path.join(V.core, "data/config/hull_styles.json"))["HIGH_TECH"]
    hs.update({"hyperspaceJitterColor": [100, 230, 220, 200], "baseCampaignExplosionColor": [100, 230, 220, 255],
               "baseCombatExplosionColor": [100, 230, 220, 255],
               "combatExplosionNonFlashColorOverride": [100, 230, 220, 255],
               "fighterRepairFlickerColor": [100, 230, 220, 255], "fighterChipIconColor": [100, 230, 220, 255],
               "weaponDisabledExplosionColor": [100, 230, 220, 255], "shieldRingColor": [235, 255, 252, 255],
               "shieldInnerColor": [70, 200, 190, 70], "fluxVentCoreColor": [235, 255, 252, 255],
               "fluxVentFringeColor": [120, 90, 210, 255]})
    write_json("data/config/hull_styles.json", {"RSL": hs})
    es = sslib.load_loose_json(os.path.join(V.core, "data/config/engine_styles.json"))["HIGH_TECH"]
    es.update({"engineColor": [100, 230, 220, 255], "contrailColor": [140, 110, 230, 30],
               "contrailCampaignColor": [100, 230, 220, 75]})
    write_json("data/config/engine_styles.json", {"RSL": es})
    # GraphicsLib maps (loaded only when GraphicsLib is enabled, see rsl.RslGraphicsLib)
    rows = []
    for f in sorted(os.listdir(P("graphics/rsl/maps"))):
        base, kind = f[:-4].rsplit("_", 1)
        if kind not in ("normal", "material", "surface"):
            continue
        if base in SHIP_IDS:
            rows.append({"id": base, "type": "ship", "frame": 0, "magnitude": 1, "map": kind,
                         "path": "graphics/rsl/maps/" + f})
        else:
            for wid in ("rsl_deco_" + base[4:],):
                if wid in WPN:
                    for t in ("turret", "hardpoint"):
                        rows.append({"id": wid, "type": t, "frame": 0, "magnitude": 1, "map": kind,
                                     "path": "graphics/rsl/maps/" + f})
    write_csv("data/lights/rsl_texture_data.csv", ["id", "type", "frame", "magnitude", "map", "path"], rows)


# ===================================================================================================== sounds + trails
# Sound files are processed derivatives of vanilla sounds (art_src/gen/gen_sounds.py).
# id -> ([files], volume). Files are peak-normalised to -1 dB; volumes put each back near the vanilla level of
# the sound it is derived from (louder for the Sforzando, the Virtuoso's signature)
SOUNDS = {
    "rsl_chime_fire": (["rsl_chime_fire_1", "rsl_chime_fire_2", "rsl_chime_fire_3"], 0.25),
    "rsl_pizzicato_fire": (["rsl_pizzicato_fire"], 0.45), "rsl_shard_fire": (["rsl_shard_fire"], 0.55),
    "rsl_flechette_fire": (["rsl_flechette_fire"], 0.45), "rsl_lance_fire": (["rsl_lance_fire"], 0.5),
    "rsl_arpeggio_fire": (["rsl_arpeggio_fire_1", "rsl_arpeggio_fire_2", "rsl_arpeggio_fire_3"], 0.45),
    "rsl_sostenuto_fire": (["rsl_sostenuto_fire"], 0.45), "rsl_charge": (["rsl_charge"], 0.6),
    "rsl_driver_fire": (["rsl_driver_fire"], 0.75), "rsl_spinal_fire": (["rsl_spinal_fire"], 0.7),
    "rsl_sforzando_fire": (["rsl_sforzando_fire"], 0.6), "rsl_flak_fire": (["rsl_flak_fire"], 0.6),
    "rsl_spike_fire": (["rsl_spike_fire"], 0.3), "rsl_bloom_fire": (["rsl_bloom_fire"], 1.0),
}
# MagicLib trails: projectile id -> visual weight (core wake + ion haze scale with it)
TRAILS = {"rsl_chime_shot": 0.5, "rsl_chime_bell": 0.6, "rsl_pizzicato_shot": 0.8, "rsl_shard_shot": 0.5,
          "rsl_lance_shot": 1.1, "rsl_flechette_shot": 0.7, "rsl_arpeggio_shot": 0.9, "rsl_sostenuto_shot": 1.1,
          "rsl_harmonic_shot": 1.8, "rsl_harmonic_spinal_shot": 2.4, "rsl_sforzando_shot": 1.3,
          "rsl_sforzando_untuned_shot": 1.0, "rsl_bloom_shard_shot": 0.5}
MISSILE_TRAILS = {"rsl_tuningspike_msl": 0.7, "rsl_bloom_msl": 1.6}
TRAIL_HDR = ["trail", "projectile", "sprite", "minLength", "fadeIn", "duration", "fadeOut", "sizeIn", "sizeOut",
             "colorIn", "colorOut", "opacity", "textLength", "textScroll", "randomTextureOffset", "distance",
             "dispersion", "drift", "frameOffsetMult", "fadeOnFadeOut", "angleAdjustment", "additive", "velocityIn",
             "velocityOut", "randomVelocity", "angle", "rotationIn", "rotationOut", "randomRotation",
             "renderBelowExplosions"]


def sounds_and_trails():
    sj = {}
    for sid, (files, vol) in SOUNDS.items():
        for f in files:
            if not os.path.isfile(P("sounds/rsl/%s.ogg" % f)):
                raise FileNotFoundError("sounds/rsl/%s.ogg (run art_src/gen/gen_sounds.py)" % f)
        pitches = (1.0,) if len(files) > 1 else (0.97, 1.0, 1.03)   # one file: vary it a little
        sj[sid] = [{"file": "sounds/rsl/%s.ogg" % f, "pitch": p, "volume": vol} for f in files for p in pitches]
    write_json("data/config/sounds.json", sj)

    def trail(tid, pid, sprite, w, dur, fade, s_in, s_out, c_in, c_out, opacity, dist, disp, additive=True,
              noise=False):
        return {"trail": tid, "projectile": pid, "sprite": sprite, "minLength": 15, "fadeIn": 0, "duration": dur,
                "fadeOut": round(fade, 2), "sizeIn": round(s_in * w, 1), "sizeOut": round(s_out * w, 1),
                # MagicLib parses colours with Integer.parseInt on each item: no spaces ("[210,255,250]")
                "colorIn": json.dumps(c_in, separators=(",", ":")), "colorOut": json.dumps(c_out, separators=(",", ":")),
                "opacity": opacity, "textLength": 256, "textScroll": 0, "randomTextureOffset": "TRUE", "distance": dist, "dispersion": disp, "drift": 1,
                "frameOffsetMult": 1, "fadeOnFadeOut": "TRUE", "angleAdjustment": "FALSE",
                "additive": "TRUE" if additive else "FALSE", "velocityIn": 0, "velocityOut": 0, "randomVelocity": 0,
                "angle": 0, "rotationIn": 0, "rotationOut": 0, "randomRotation": "FALSE",
                "renderBelowExplosions": "FALSE",
                # noise: segments drift out and curl at random as the haze fades, breaking up the straight,
                # angular segment joints (user: "the trail smoke deforms angularly")
                **({"velocityOut": round(18 * w, 1), "randomVelocity": 0.9, "rotationIn": 10, "rotationOut": 70,
                    "randomRotation": "TRUE", "textScroll": -48} if noise else {})}
    rows = []
    for pid, w in TRAILS.items():
        length = PROJ[pid]["length"]
        # a thin white-teal wake right behind the streak, then a wide teal->violet ion haze that lingers
        rows.append(trail(pid + "_core", pid, "base_trail_smooth", w, 0.04, 0.3, 4, 1.5, [210, 255, 250],
                          [90, 210, 220], 0.75, round(length * 0.5), 0))
        rows.append(trail(pid + "_haze", pid, "base_trail_smoke", w, 0.08, 0.7 + 0.2 * w, 7, 20, [100, 230, 220],
                          [150, 110, 230], 0.3, round(length * 0.5), 22 * w, noise=True))
    for r in rows:   # the Sforzando's slugs pierce whole lines of ships: a white-teal wake that hangs much longer
        if r["projectile"] in ("rsl_sforzando_shot", "rsl_sforzando_untuned_shot"):
            r["distance"] = 0
        if r["projectile"] == "rsl_sforzando_shot":
            r["duration"], r["fadeOut"] = r["duration"] * 4, round(r["fadeOut"] * 3, 2)
            core = r["trail"].endswith("_core")
            r["colorIn"] = "[245,255,255]" if core else "[215,250,245]"
            r["colorOut"] = "[190,240,236]" if core else "[130,215,210]"
            r["opacity"] = 0.76 if core else 0.36   # user: 20% less vivid than the first gold version
        elif r["projectile"] == "rsl_sforzando_untuned_shot":   # white too, normal length
            core = r["trail"].endswith("_core")
            r["colorIn"] = "[240,255,255]" if core else "[200,240,236]"
            r["colorOut"] = "[180,232,228]" if core else "[120,200,196]"
            r["sizeIn"], r["sizeOut"] = round(r["sizeIn"] * 1.6, 1), round(r["sizeOut"] * 1.4, 1)
    for pid, w in MISSILE_TRAILS.items():
        rows.append(trail(pid + "_haze", pid, "base_trail_smoke", w, 0.1, 1.2, 8, 22, [120, 220, 215],
                          [140, 110, 220], 0.4, 6, 18 * w, additive=False, noise=True))
    write_csv("data/config/modFiles/magicTrail_data.csv", TRAIL_HDR, rows)


def descriptions():
    hdr = V.header("descriptions.csv")
    rows = [{"id": d, "type": t, "text1": a, "text2": b, "text3": c} for d, t, a, b, c in DESC]
    rows.append({"id": FACTION, "type": "FACTION",
                 "text1": "A refugee research polity grown out of a Domain-era harmonic-flux laboratory. The Choir "
                          "builds its ships around crystalline lattice cores and fights the way it sings: together."})
    write_csv("data/strings/descriptions.csv", hdr, rows)


# ===================================================================================================== missions
MISSIONS = {
    "rsl_proving": dict(
        title="Lattice: Proving Chorus", difficulty="EASY", bg="graphics/backgrounds/background4.jpg",
        text="Test mission (Resonance Lattice). Every Lattice hull against a mixed Hegemony-style line.\n\n"
             "Watch the Resonance bar (bottom left) fill as your shields absorb fire and your guns land; at 60 the next "
             "ship system use is an Overtone. The Virtuoso starts at 100% CR, i.e. in Bravura.",
        player_tag="The Choir's full chorus, every hull in the book.", enemy_tag="A Hegemony-pattern battle line.",
        briefing=["Fly the Virtuoso: Glissando (system key) dashes and leaves a string that snaps",
                  "Switch ships to try every Lattice system",
                  "Point defense and fighters test the Chime Repeater and Cantus Flak"],
        player=[("rsl_virtuoso_Standard", "Virtuoso", True), ("rsl_conductor_Standard", None, False),
                ("rsl_halo_Standard", None, False), ("rsl_cadence_Standard", None, False),
                ("rsl_tremolo_Standard", None, False), ("rsl_refrain_Standard", None, False),
                ("rsl_staccato_Standard", None, False), ("rsl_gracenote_Standard", None, False),
                ("rsl_gracenote_Standard", None, False)],
        enemy=[("onslaught_Elite", None, False), ("dominator_Assault", None, False), ("eagle_Assault", None, False),
               ("falcon_CS", None, False), ("heron_Strike", None, False), ("hammerhead_Balanced", None, False),
               ("enforcer_Assault", None, False), ("condor_Support", None, False), ("lasher_CS", None, False),
               ("lasher_CS", None, False), ("wolf_CS", None, False), ("wolf_CS", None, False)],
        cr100="Virtuoso"),
    "rsl_siege": dict(
        title="Lattice: Cantor Siege", difficulty="HARD", bg="graphics/backgrounds/background2.jpg",
        text="Test mission (Resonance Lattice). A vanilla strike force against the Cantor Array and an AI-flown "
             "Lattice squadron.\n\nKill a petal and the others go into Overtone (Phase-Locked Petals); the Grand "
             "Chorus fires lances from every petal at once.",
        player_tag="Strike force with orders to silence the array.",
        enemy_tag="The Cantor Array and its squadron.",
        briefing=["Destroy the Cantor Array", "Choose your kill order: every dead petal empowers the rest",
                  "The Unsung is yours - try the untuned Glissando"],
        player=[("rsl_virtuoso_unsung_Standard", "Unsung", True), ("onslaught_Elite", None, False),
                ("conquest_Elite", None, False), ("eagle_Assault", None, False), ("eagle_Assault", None, False),
                ("aurora_Balanced", None, False), ("medusa_Attack", None, False), ("sunder_CS", None, False),
                ("hammerhead_Balanced", None, False), ("wolf_CS", None, False), ("wolf_CS", None, False)],
        enemy=[("rsl_cantor_Standard", "Cantor Array", False), ("rsl_conductor_Standard", None, False),
               ("rsl_halo_Standard", None, False), ("rsl_tremolo_Standard", None, False),
               ("rsl_cadence_Standard", None, False), ("rsl_refrain_Standard", None, False),
               ("rsl_staccato_Standard", None, False), ("rsl_gracenote_Standard", None, False)],
        cr100=None),
}

MISSION_JAVA = """package data.missions.%(id)s;

import com.fs.starfarer.api.fleet.FleetGoal;
import com.fs.starfarer.api.fleet.FleetMemberAPI;
import com.fs.starfarer.api.fleet.FleetMemberType;
import com.fs.starfarer.api.mission.FleetSide;
import com.fs.starfarer.api.mission.MissionDefinitionAPI;
import com.fs.starfarer.api.mission.MissionDefinitionPlugin;

/** Generated by tools/gen_data.py - test mission for Resonance Lattice. */
public class MissionDefinition implements MissionDefinitionPlugin {

    public void defineMission(MissionDefinitionAPI api) {
        api.initFleet(FleetSide.PLAYER, "%(ptag)s", FleetGoal.ATTACK, false);
        api.initFleet(FleetSide.ENEMY, "%(etag)s", FleetGoal.ATTACK, true);
        api.setFleetTagline(FleetSide.PLAYER, "%(player_tag)s");
        api.setFleetTagline(FleetSide.ENEMY, "%(enemy_tag)s");
%(briefing)s
        FleetMemberAPI m;
%(adds)s
        float width = 16000f;
        float height = 16000f;
        api.initMap(-width / 2f, width / 2f, -height / 2f, height / 2f);
        api.addNebula(-3000f, 2000f, 1200f);
        api.addNebula(4000f, -2500f, 900f);
    }
}
"""


def missions():
    rows = [{"mission": mid} for mid in MISSIONS]
    write_csv("data/missions/mission_list.csv", ["mission"], rows)
    from PIL import Image
    icon = Image.open(P("graphics/rsl/factions/rsl_flag.png")).convert("RGB").resize((256, 160))
    for mid, m in MISSIONS.items():
        write_json("data/missions/%s/descriptor.json" % mid,
                   {"title": m["title"], "difficulty": m["difficulty"], "icon": "icon.jpg", "background": m["bg"]})
        write_text("data/missions/%s/mission_text.txt" % mid, m["text"] + "\n")
        icon.save(P("data/missions/%s/icon.jpg" % mid), quality=92)
        adds = []
        for side, lst in (("PLAYER", m["player"]), ("ENEMY", m["enemy"])):
            for vid, name, flag in lst:
                nm = '"%s"' % name if name else "null"
                adds.append('        m = api.addToFleet(FleetSide.%s, "%s", FleetMemberType.SHIP, %s, %s);'
                            % (side, vid, nm, "true" if flag else "false"))
                if name and name == m.get("cr100"):
                    adds.append("        m.getRepairTracker().setCR(1f);")
        brief = "\n".join('        api.addBriefingItem("%s");' % b for b in m["briefing"])
        write_text("data/missions/%s/MissionDefinition.java" % mid, MISSION_JAVA % {
            "id": mid, "ptag": "RCS" if mid == "rsl_proving" else "ISS", "etag": "ISS" if mid == "rsl_proving" else "RCS",
            "player_tag": m["player_tag"], "enemy_tag": m["enemy_tag"], "briefing": brief, "adds": "\n".join(adds)})


def main():
    weapons()
    WEAPONS_BY_ID.update({r["id"]: r for r in WEAPONS})
    hull_rows()
    ships = ship_files()
    variants(ships)
    wings()   # after variants(): that one clears data/variants/rsl
    systems()
    hullmods()
    faction()
    config()
    sounds_and_trails()
    descriptions()
    missions()
    print("ok: %d weapons, %d hulls, %d systems, %d hullmods, %d descriptions" % (
        len(WEAPONS), len(HULLS), len(SYSTEMS), len(HULLMODS), len(DESC) + 1))


if __name__ == "__main__":
    main()
