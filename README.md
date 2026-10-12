# Resonance Lattice

The Cantorate of Vell: a refugee polity whose ships are grown around crystalline lattice cores. Every hull builds **Resonance** from shield hits
and from landing its own guns, shares it with nearby Lattice ships, and at 60+ Resonance its next ship-system use is
an **Overtone** (an empowered version).

This build has the ships, weapons and the faction (relations, items, Nexerelin support) but no territory or
quests yet (ROADMAP.md). Spawn everything with Console Commands or play the two included missions.

## Requirements

- Starsector 0.98a-RC7
- LazyLib, MagicLib
- Optional: GraphicsLib (normal/material/surface maps are loaded when it is enabled)
- For testing: Console Commands

## Testing in game

### Missions (no save needed)

Main menu -> Missions:

- **Lattice: Proving Chorus** - every Lattice hull (you fly the Virtuoso, at 100% CR = Bravura) against a vanilla
  battle line. Switch ships to try each system.
- **Lattice: Cantor Siege** - you fly the Virtuoso (Unsung) with a vanilla strike force against the Cantor Array
  station and an AI-flown Lattice squadron.

### Console Commands (campaign)

Ships (variant ids):

```
addship rsl_gracenote_Standard
addship rsl_refrain_Standard
addship rsl_staccato_Standard
addship rsl_cadence_Standard
addship rsl_tremolo_Standard
addship rsl_halo_Standard        # the Fermata (id predates the rename)
addship rsl_conductor_Standard
addship rsl_virtuoso_Standard
addship rsl_virtuoso_unsung_Standard
```

Preset loadouts (two per hull, besides `_Standard`): `rsl_gracenote_Pluck` / `_Warden`, `rsl_refrain_Bulwark` /
`_Chorister`, `rsl_staccato_Burst` / `_Lancer`, `rsl_cadence_Battery` / `_Drumline`, `rsl_tremolo_Waveform` /
`_Riptide`, `rsl_halo_Nocturne` / `_Sanctuary`, `rsl_conductor_Maestro` / `_Fortissimo`, `rsl_virtuoso_Soloist` /
`_Unbound`, `rsl_virtuoso_unsung_Wanderer` / `_LastStand`.

The Cantor Array (`rsl_cantor_Standard`) is a station: use the Cantor Siege mission to fight it.

Weapons:

```
addweapon rsl_chime 4
addweapon rsl_pizzicato 4
addweapon rsl_shardcaster 4
addweapon rsl_tuningspike 4
addweapon rsl_tuningspike_pod 2
addweapon rsl_lattice_lance 4
addweapon rsl_flechette 4
addweapon rsl_arpeggio 4
addweapon rsl_cantus 4
addweapon rsl_harmonic_driver 2
addweapon rsl_sostenuto 2
addweapon rsl_bloom 2
addwing rsl_trill_wing 2
addwing rsl_cadenza_wing 2
addwing rsl_requiem_wing 2
```

Fighter wings: Trill (interceptor, micro-rail), Cadenza (heavy fighter, twin rails), Requiem (rail bomber: a
piercing heavy slug + two Tuning Spikes). The Fermata and the Cantor Array's Lofts carry them.

The Sforzando lances and the Conductor's spinal Harmonic Driver are built in (no cargo item). The Tuning Spike Pod
(medium missile) and Resonance Bloom (large missile) have no matching slot on Lattice hulls; mount them on vanilla
ships.

Hullmods: all Lattice hullmods are built in, except **Unbound Core** (`addhullmod rsl_unbound`; Virtuoso only, the
Safety Overrides of a capital).

Fleets: `spawnfleet rsl_choir 150` spawns an AI Cantorate fleet (start a new game first if the save predates the mod: the
faction is created with the sector).

Campaign items (Stage 2 of ROADMAP.md; the Workshop that spends them comes later):

```
additem rsl_pitchglass 100          # Pitch Glass, the Cantorate's currency
addspecial rsl_bp_hulls_package
addspecial rsl_bp_weapons_package
addspecial rsl_bp_wings_package
```

Handy: `god`, `nocooldown`, `infiniteammo`, `addcredits 1000000`, `allhullmods`.

## Contents

| Hull | Class | System | Built-in mechanic |
|---|---|---|---|
| Grace Note | frigate | Pitch Shift (Harmonic / Discord stance toggle) | Discord recolors the seams violet |
| Refrain | destroyer | Sympathetic Ward (takes 40% of an ally's damage) | armor vanes swing over the bow |
| Staccato | destroyer | Grace Dash | Fracture: 6th hit shatters armor |
| Cadence | cruiser | Crescendo (energy hits stack rate of fire) | Overtone: Fortissimo volley |
| Tremolo | cruiser | Standing Wave (node, snap back, restore 40% damage) | Overtone: afterimage detonates |
| Fermata | capital carrier | Fermata Field (slows shots, breaks missile locks) | ring spins up; Tuned Wings |
| Conductor | capital | Sympathetic Strike (resonant strike + mark +20% damage) | Conductor's Bridge: double Sympathy |
| Virtuoso | unique capital | Glissando (blink-dash, the String snaps) | Stolen Time (CR theft), Bravura at 100% CR |
| Virtuoso (Unsung) | prototype | Glissando (Unsung) | Stolen Time, no Bravura |
| Cantor Array | station | Grand Chorus (every petal fires a lance) | Phase-Locked Petals |

Weapons (doctrine: long-range, high-velocity rails; PD and missiles excepted): Chime Repeater, Pizzicato Lancet,
Shard Caster, Tuning Spike (+ Pod), Lattice Lance, Crystal Flechette, Arpeggio Pulser, Cantus Flak, Harmonic Driver,
Sostenuto Rail, Resonance Bloom, Sforzando Lance (+ Untuned). Every sound is synthesised for the mod
(`art_src/gen/gen_sounds.py`); slug trails need MagicLib (a hard dependency already).
Descriptions are in the Codex / refit tooltips.

## Status

Statically verified only (build, validator, compile of the missions). Not yet run in game: AI behaviour, balance,
visuals in motion and the station deployment need an in-game session. See BALANCE.md for the stat choices.

## Save compatibility

The mod saves no custom classes. On first load it sets the Cantorate's starting relations once (a sector memory
flag remembers it). Ships bought or spawned are ordinary fleet members;
removing the mod from a save that contains them will break that save, as with any ship mod.

## Credits

All art is original (Blender-rendered hulls, procedural weapons and icons in `art_src/`). Libraries: LazyLib,
MagicLib, GraphicsLib (optional).
