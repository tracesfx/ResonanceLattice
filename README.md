# Resonance Lattice

The Cantorate of Vell: a refugee polity whose ships are grown around crystalline lattice cores. Every hull builds **Resonance** from shield hits
and from landing its own guns, shares it with nearby Lattice ships, and at 60+ Resonance its next ship-system use is
an **Overtone** (an empowered version).

This build has the ships, weapons, the faction and its home system **Vell** (a pulsar on the south-east fringe:
Coda with the Cantor Array, Glasshouse, Tacet Station), the Workshop, contracts and bounties, and the Virtuoso's
questline **Lacrimosa**, the exploration secrets and two optional encore events after the questline (ROADMAP.md:
release remains). Spawn everything with Console Commands or play the three included missions.

## Requirements

- Starsector 0.98a-RC7
- LazyLib, MagicLib
- Optional: GraphicsLib (normal/material/surface maps are loaded when it is enabled)
- Optional: LunaLib (in-game toggles for the encore events; without it both are on)
- For testing: Console Commands

## Testing in game

### Missions (no save needed)

Main menu -> Missions:

- **Lattice: Proving Chorus** - every Lattice hull (you fly the Virtuoso, at 100% CR = Bravura) against a vanilla
  battle line. Switch ships to try each system.
- **Lattice: Cantor Siege** - you fly the Virtuoso (Unsung) with a vanilla strike force against the Cantor Array
  station and an AI-flown Lattice squadron.
- **Lattice: The Second Voice** - the Virtuoso one on one against another Virtuoso flown by a level 15 commander.

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

Vell: `jump Vell`, then `goto Coda`. The Cantor Array guards Coda as its station; fight it by attacking Coda.

At Coda: **Visit the Luthier's Workshop** (spend Pitch Glass). At Tacet Station: **Check the tuners' contract
board**. Pitch Glass also comes from Lattice wrecks, bounties and a monthly stipend at Cooperative.

Campaign items:

```
additem rsl_pitchglass 100          # Pitch Glass, the Cantorate's currency
addspecial rsl_bp_hulls_package
addspecial rsl_bp_weapons_package
addspecial rsl_bp_wings_package
addspecial rsl_pulsar_metronome
```

Handy: `god`, `nocooldown`, `infiniteammo`, `addcredits 1000000`, `allhullmods`.

### The Lacrimosa questline (spoilers)

Starts at player level 8 with an 80+ DP fleet: a message waits at any Cantorate market ("Open the sealed message from
Tacet Station"). Beats: three listening buoys in fringe hyperspace (one watched by scavengers) -> the Antiphon
Institute (derelict defences, waking the Lacrimosa drops the fleet to 30% CR, you get the Unsung) -> Director Sung's
offer (sell = bad ending; refuse = a Special Projects fleet hunts you) -> the council at Coda (Chorus or Solo) ->
Tacet's pulsar recording -> three echoes in the abyss (lower-left corner of the map) -> the Hush (boss) -> back to the
Institute: 600 Pitch Glass + 3,000,000 credits turn the Unsung into the Virtuoso. Then the Workshop sells the Unbound
Core, your path's Movement and the Hush seams.

Skip ahead with Console Commands (fights are skipped; the Unsung is granted on the way):

```
runcode rsl.campaign.Lacrimosa.debug("institute")   # buoys | institute | sung | hunted | council | recording |
                                                    # search | hush | return
additem rsl_pitchglass 700
addcredits 3000000
```
`debug` also takes a stage prefix (`debug("inst")`); an unknown name is logged with the valid list.
`debug("council")` passes through the refusal (Special Projects is skipped). `debug("hush")` places the Hush in the
abyss so you can fight it (the intel shows where); `debug("hunted")` and then waiting 4-14 days brings Special
Projects.

### Secrets (spoilers)

Placed once per save in uninhabited systems (also in existing saves): 8 **Lost Score** caches (Venn's tuning scores,
15 Pitch Glass each; the first can start the questline, the fourth explains the Full Chorus, the eighth reveals
**Venn's Rest**, a hidden system with a sealed Hush and the unique officer **Odile Marchetti**, skill
*Concertmaster*), 4 recoverable **silent wrecks** (Lattice frigates/destroyers, Pitch Glass in the salvage) and the
**abandoned Array** (an automated Cantor Array in the most remote system: hull blueprints, 100 Pitch Glass, Concert
Pitch). **Full Chorus**: field all seven Lattice line hulls together. Fly a Virtuoso through Vell's pulsar beam once.

```
runcode rsl.world.SecretsGen.debug()               # messages + map markers for every cache, wreck and the Array
runcode rsl.campaign.ScoresIntel.debugReadAll()    # read all 8 Scores: Venn's Rest appears (intel shows it)
```

### Encore events (spoilers)

After the Lacrimosa is completed: **The Second Voice** (14 days later) - Commander Isolde Raike waits at the Antiphon
Institute in a second Virtuoso, the Dies Irae, for a duel. The Lacrimosa must be your flagship; your other ships sit
the encounter out and come back afterwards. Losing makes the Lacrimosa yield and withdraw, never die; rematches any
time. Prize: the Ossia hullmod, 250 Pitch Glass. **Requiem** (45 days later) - the Silence, ~1,580 DP of Omega and
Remnant hulls under AI cores, waits in the remote system the intel names. It never comes to you and must be ended in
one encounter, or it remakes itself. Optional, meant to be nearly impossible. Prize: the Encore hullmod, 1,000 Pitch
Glass. Both can be switched off in LunaLib's mod settings.

```
runcode rsl.campaign.DuelIntel.debug()       # Raike's challenge now (needs the Antiphon Institute: quest beat 2+)
runcode rsl.campaign.RequiemIntel.debug()    # the Silence now
runcode rsl.campaign.DuelIntel.debugWin()    # the reward without the fight (also RequiemIntel.debugWin())
```

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
| Virtuoso | unique capital | Glissando (blink-dash, the String snaps) | Stolen Time (CR theft), Bravura at 100% CR (teal -> white) |
| Virtuoso (Unsung) | prototype | Glissando (Unsung) | Stolen Time, no Bravura |
| Cantor Array | station | Grand Chorus (every petal fires a lance) | Phase-Locked Petals |

Weapons (doctrine: long-range, high-velocity rails; PD and missiles excepted): Chime Repeater, Pizzicato Lancet,
Shard Caster, Tuning Spike (+ Pod), Lattice Lance, Crystal Flechette, Arpeggio Pulser, Cantus Flak, Harmonic Driver,
Sostenuto Rail, Resonance Bloom, Sforzando Lance (+ Untuned). Every sound is a processed derivative of vanilla sounds
(`art_src/gen/gen_sounds.py`); slug trails need MagicLib (a hard dependency already).
Descriptions are in the Codex / refit tooltips.

## Status

Statically verified only (build, validator, compile of the missions). Not yet run in game: AI behaviour, balance,
visuals in motion and the station deployment need an in-game session. See BALANCE.md for the stat choices.

## Save compatibility

On first load the mod creates Vell and sets the Cantorate's starting relations, once per save (sector memory
flags), so it can be added to an existing save. In a Nexerelin random sector Vell is not created; Nex places the
Cantorate's markets. Saved classes: `rsl.world.CantorArrayIndustry`, `rsl.world.LatticeNurseries`,
`rsl.campaign.TunerContractIntel`, `rsl.campaign.LacrimosaIntel` (+ its `Stage`), `rsl.campaign.LacrimosaFleets$BossConfigGen`,
`rsl.campaign.ScoresIntel`, `rsl.campaign.ArrayListener`, `rsl.campaign.DuelIntel`, `rsl.campaign.RequiemIntel`
(aliased). Officer skills `rsl_concertmaster` (Odile) and `rsl_second_voice` (Raike). The questline's sites and fleets are created when it reaches them, never at worldgen. Ships bought or spawned are ordinary fleet members;
removing the mod from a save that contains them will break that save, as with any ship mod.

## Credits

All art is original (Blender-rendered hulls, procedural weapons and icons in `art_src/`). Libraries: LazyLib,
MagicLib, GraphicsLib (optional), LunaLib (optional). Mission illustrations are composed from the mod's sprites
over vanilla backgrounds; portraits are vanilla.
