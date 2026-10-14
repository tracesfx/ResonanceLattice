# Changelog

## Unreleased - 2026-10-13 (Stage 7: polish and encore events)

**The Virtuoso**
- **Two colour schemes**: teal normally, white in Bravura. The Bravura seam sprite (hull and vanes) is now white
  instead of gold-white; the Bravura shield is white (it was white-teal); Glissando's flare, afterimages and String are
  white only in Bravura and white-teal outside it (the Unsung stays dim teal). The Sforzando slugs are teal with a
  white core normally; in Bravura every slug is pure white with a white wake (each fresh slug is swapped for an
  identical white twin, `rsl_sforzando_bravura`, with the same damage, range and skewer). Accent arcs: white in
  Bravura, teal outside it (they were violet).
- **The Bravura transition is an event**: entering flares the seams far past full brightness for about 2.5 s before
  they cool to the Bravura glow, with a white shockwave ring, flung motes, the hull shivering with light, a "BRAVURA"
  callout over the player's ship and a rising chord (`rsl_bravura_on`). Leaving flares the teal seams hot and vents
  teal heat, with a falling chord (`rsl_bravura_off`). A ship deployed already at 100% simply starts in Bravura.
- Concert Pitch EMP resistance **90% -> 60%** (user).
- Bravura hullmod icon: white flare instead of gold.

**Encore events** (after the Lacrimosa questline; both can be turned off in LunaLib's settings)
- **The Second Voice**: 14 days after the Lacrimosa is completed, Commander Isolde Raike of Tri-Tachyon's Special
  Projects challenges it to a duel. She flies the *Dies Irae*, a second Virtuoso grown around a Hush core (violet
  seams, 3 S-mods), and is a **level 15** commander: every combat skill elite plus her own skill, *Second Voice*
  (+10% damage to ships, +25% system recharge, +10% top speed). She waits at the Antiphon Institute. One ship each:
  the Lacrimosa must be your flagship, and every other ship is held out of the encounter and given back afterwards.
  Losing is not fatal: the Lacrimosa yields and leaves the field instead of being disabled, and Raike waits for a
  rematch at full strength. Winning builds **Ossia** into the Lacrimosa (Glissando costs half the CR, the String
  snaps once more) and pays 250 Pitch Glass.
- **Requiem**: 45 days after completion, the **Silence** appears in the wild system farthest from the core: about
  1,580 deployment points of Omega (4 Tesseracts, Facets, Shards) and Remnant hulls (Radiants, Apexes, Novas,
  Brilliants and escorts), every hull under an alpha core, an omega-core commander, 2 S-mods per ship, no retreat.
  It never moves or attacks; it must be ended in one encounter (any number of engagements in one dialog), and if you
  leave with any of it alive it remakes itself. Optional and meant to be nearly impossible. Ending it builds
  **Encore** into the Lacrimosa (once per battle a disabling blow is refused: 3 s of invulnerability, hull back to
  40%, CR to full, straight into Bravura) and pays 1,000 Pitch Glass.
- Console: `rsl.campaign.DuelIntel.debug()` / `debugWin()`, `rsl.campaign.RequiemIntel.debug()` / `debugWin()`.
- Optional **LunaLib** settings (`data/config/LunaSettings.csv`): toggles for both events, read through
  `rsl.RslSettings` with defaults when LunaLib is absent.

**Missions**
- Mission texts follow vanilla's layout: Location and Date, the story, `***`, then how to play it; better briefing
  bullets and named ships.
- New 256x256 mission illustrations (`art_src/gen/gen_mission_icons.py`; the old ones were the faction flag stretched).
- New mission **Lattice: The Second Voice**: the Lacrimosa against Raike's Dies Irae, one on one.

## Unreleased - 2026-10-13 (campaign Stage 6: secrets and exploration)

- **The Lost Scores**: 8 Antiphon Institute caches in uninhabited systems (discoverable like probes). Each holds one of
  Saskia Venn's tuning scores (kept in a "Lost Scores" intel entry) and 15 Pitch Glass. The first can start the
  Lacrimosa questline; the fourth explains the Full Chorus; the eighth reveals Venn's Rest.
- **Venn's Rest**: a hidden red-dwarf system on the upper-right fringe, created when the eighth Score is read. A sealed
  Hush (~190 DP, Conductor flagship, 3 S-mods, level-7 elite officers, Dead Chorus) guards Venn's cryo vault. Inside:
  Venn's last log and **Concertmaster Odile Marchetti**, a unique level-7 officer (every skill elite) with her own
  skill **Concertmaster**: while her ship is deployed, every allied ship +5% weapon damage and +10% flux dissipation;
  allied Lattice ships gain Resonance 25% faster and share Sympathy at any range. At the Virtuoso's helm she has a line
  of her own in Bravura. (The planned "+10% CR recovery after battle" was dropped: officer skills cannot reach the
  fleet's campaign stats.)
- **Silent wrecks**: 4 recoverable Lattice frigates/destroyers drifting in uninhabited systems, Pitch Glass in the
  salvage.
- **The abandoned Array**: an automated Cantor Array (3 S-mods, alpha-core commander) in the most remote system.
  Silencing it pays a Cantorate hull blueprint package, 100 Pitch Glass and a Concert Pitch modspec, once.
- **Full Chorus**: a side that fields a Grace Note, Refrain, Staccato, Cadence, Tremolo, Fermata and Conductor at once
  gives its Lattice ships +5% weapon damage and +25% Resonance gain.
- **The pulsar choir**: flying a Virtuoso through Vell's pulsar beam once restores the whole fleet's readiness.
- **The true name**: a Virtuoso named Lacrimosa has a line of its own in the Stolen Time tooltip.
- Console: `rsl.world.SecretsGen.debug()`, `rsl.campaign.ScoresIntel.debugReadAll()`; `Lacrimosa.debug` accepts stage
  prefixes ("buoy" works now).

## Unreleased - 2026-10-13 (campaign Stage 5: the Lacrimosa questline)

- **Lacrimosa**, the Virtuoso's questline (CAMPAIGN.md section 6), one story intel entry:
  1. *Static in the Score*: at level 8 with an 80+ DP fleet, Archivist Tanh's sealed message waits at any Cantorate
     market (a one-time campaign message points to it). Scan three Antiphon Institute listening buoys in fringe
     hyperspace; the farthest is stripped by pirate scavengers. Each buoy plays one of Director Venn's logs.
  2. *The Antiphon*: the Institute in a deep-fringe system, guarded by Domain derelicts (~180 DP: Guardian, Ramparts,
     Bastillons..., 1 S-mod each). Waking the Lacrimosa drains the fleet to 30% CR and grants the **Unsung**, named
     Lacrimosa (always recoverable).
  3. *A Rival Bid*: Director Hale Sung (Tri-Tachyon Special Projects) offers 2,000,000 credits for the core (two
     warnings; selling ends the quest, Cantorate -15). Refuse and a **Special Projects** fleet (~280 DP: Paragon,
     2 Doom, 2 Harbinger, Aurora, 2 Medusa, phase escorts; 3 S-mods each, level-7 all-elite officers) hunts you for up
     to 60 days. Opens the *Special Projects Remnant* bounty.
  4. *The Council* at Coda: **Chorus** (Cantorate +20, Workshop -10%, two S-modded Cantorate escorts with level-5
     officers for beat 5, Chorus Movement) or **Solo** (Cantorate -10, Abelard trades at any standing short of hostile,
     Solo Movement). Then Tanh's pulsar recording at Tacet Station.
  5. *The Hush*: three sensor sweeps in the Orion-Perseus Abyss lead to the graveyard of the First Chorus. The Hush:
     2 Conductor, Fermata, 3 Cadence, 3 Tremolo, 3 Staccato, 2 Refrain, 2 Grace Note (~320 DP, 3 S-mods each,
     level-7 all-elite officers on the big hulls, violet seams) with the **Dead Chorus** fleet hullmod (a dead sister
     ship floods the others to full Resonance and +10% weapon damage each, up to +50%). Rewards: the Lacrimosa's
     sash and vanes, 150 Pitch Glass, a Concert Pitch modspec; Hush wrecks give triple Pitch Glass salvage.
  6. *Lacrimosa*: at the Institute, 600 Pitch Glass + 3,000,000 credits turn the Unsung into the **Virtuoso** in place
     (name, captain and fit kept; D-mods cleared; CR to max). If the Unsung was lost: the Institute's spare frame, once
     (+1,000,000 credits and a story point).
- **Workshop** after completion: **Unbound Core** (400 Pitch Glass + 1,000,000 credits), **Chorus Movement** or
  **Solo Movement** (300, by path), **Hush seams** (50, cosmetic violet glow; toggles).
- New hullmods: Chorus Movement (Stolen Time -25%, half of every steal shared among allies within 1,500), Solo Movement
  (alone within 1,500: +25% theft and +10% damage; in company: -25% theft), Dead Chorus (Hush only).
- Unbound Core is no longer known from the start: the Workshop teaches it.
- Console testing: `runcode rsl.campaign.Lacrimosa.debug("<stage>")` (README).
- Fix: "Fatal: null" after beating the buoy scavengers (and the same trap after the Special Projects and Hush fights): the quest unhooked/despawned fleets inside the battle callback; now done on the next tick.

## Unreleased - 2026-10-12 (campaign Stage 4: ambient life, Pitch Glass economy, Luthier's Workshop)

- **Luthier's Workshop** at Coda (Luthier Abelard), priced in Pitch Glass: Lattice Tuning (15), Cantorate weapon /
  wing / hull blueprints (150 / 120 / 250, Favorable), Concert Pitch hullmod (200, Cooperative), Pulsar Metronome
  colony item (250, Cooperative). Hand over AI cores to be silenced (alpha 40 / beta 15 / gamma 5 Pitch Glass, small
  Hegemony reputation gain) and Domain-era colony items (pristine nanoforge 150, synchrotron 80, corrupted nanoforge
  40, others 40).
- **Pitch Glass sources**: salvage from every Lattice ship the enemy loses in a battle you win (1 / 2 / 4 / 8 by
  size), a 10/month stipend at Cooperative, Tuners' Contracts, bounties.
- **Tuners' Contracts** at Tacet Station: hunt a pirate or Luddic Path raider fleet near Vell within 60 days (20-40
  Pitch Glass + credits + reputation), one at a time, 30-day cooldown; intel entry.
- **Lattice Tuning**: for 30 days your Lattice ships gain Resonance 25% faster and lose it half as fast.
- **Pulsar Metronome** (new colony item, Waystation): +15% accessibility, +1 stability; +25% / +2 with a neutron star.
- Concert Pitch no longer drops as a modspec; it is learned at the Workshop.
- Comm greetings for Cantorate fleets (friendly, neutral, hostile, and one for tuned fleets).
- MagicLib bounties: **The Discordant** (pirates in mistuned Lattice ships), **Inspection Overreach** (a rogue
  Hegemony inspector in Vell), **Special Projects Remnant** (unlocked by the questline later).

## Unreleased - 2026-10-12 (campaign Stage 3: Vell)

- New star system **Vell** (south-east fringe): a pulsar with its beam, Tacet Station (size 3, high-tech orbital
  station), the ice giant Basso with Coda (capital, size 5: megaport, military base, orbital works, refining, heavy
  batteries) and Glasshouse (size 4: mining, patrol HQ, new condition **Lattice Nurseries**: +1 stability, +1
  transplutonics), the rock Tenuto, an outer belt, relay, buoy and sensor array.
- The **Cantor Array** is Coda's defence station (industry `rsl_cantor_array`, star-fortress tier, cannot be built
  elsewhere).
- Named people: Precentor Ilian Okoro-Vass (faction leader, Coda's administrator), Luthier Corvin Abelard (Coda),
  Archivist Mireille Tanh (Tacet Station).
- Generated in new games and once in existing saves; skipped in Nexerelin random sectors.

## Unreleased - 2026-10-12 (campaign Stage 2: faction foundation)

- The faction is now **the Cantorate of Vell** (id still `rsl_choir`): own ranks and posts (Precentor, Maestro,
  Principal, Chorister...), fleet names, ship-name list (`CCS` prefix, data/strings/ship_names.json), spacer portraits,
  voices, music, doctrine skills; offers commissions, takes part in hostilities, AI cores are contraband, no punitive
  expeditions. Longer faction description (CAMPAIGN.md).
- Renamed Halo -> **Fermata**, Stillwater Halo -> **Fermata Field** (ids unchanged).
- New commodity **Pitch Glass** (`rsl_pitchglass`, non-economy, ~5 credits to outsiders) with its own icon.
- Three blueprint packages (hulls / weapons / wings; `no_drop`), backed by new `rsl_bp_hulls|weapons|wings` tags.
- Starting relations (Independents +30, League +20, TT -20, Hegemony -30, Church -20, Path -60), applied once per
  save by `rsl.world.RslRelations` (Nexerelin new games use the Nex config instead).
- Nexerelin: playable faction config (`data/config/exerelinFactionConfig/`): alignments, diplomacy traits, start
  fleets from the presets, starting relations. Only read when Nexerelin is enabled.

## Unreleased - 2026-10-12 (readability, S-mods, icons)

- Hullmod tooltips rebuilt in sections (Resonance / Overtone / Bonuses / Tradeoffs ...) with bulleted, highlighted
  numbers; short plain descriptions. Ship-system descriptions in paragraphs with vanilla category and one-line
  summary; ship descriptions gain an "In battle" paragraph.
- S-mod effects: Unbound Core (expensive) -10% max CR when built in; Concert Pitch +100 range when built in, plus
  +5% max CR and +30 s peak when enhanced on the Virtuoso; enhanced built-ins: Lattice Core +50% Resonance gain,
  Fracture shatters a stack sooner for +50% armor damage, Stolen Time +50%, Bravura from 95% CR (until 87%),
  Conductor's Bridge 3,000 range, Tuned Wings 1,000 units and 50% faster refits.
- New vanilla-style hullmod icons (painted close-ups of the hulls with the mechanic in light).
- Validator: errors on a bare % in hull_mods.csv texts and on spaced colours in MagicLib trail data.

## Unreleased - 2026-10-12 (final balance pass, presets)

- Fix: pierce continuations (Sforzando, Harmonic Driver) no longer extend the shot's range; they are removed once
  the original shot's range from its firing point is used up.
- Fix: Glissando afterimages drawn by the mod itself (hull sprite snapshots left in place, fading), tinted white on
  the Virtuoso and teal on the Unsung.
- Balance: main rail guns ~15% less sustained DPS and slightly worse flux efficiency (range is the edge); shard guns
  fire explicit 3-shot bursts; Virtuoso 15,000 hull; Unsung 250 OP (BALANCE.md).
- Two preset loadouts per hull (18 variants), used by Choir fleets; see README.

## Unreleased - 2026-10-12 (DP, Bravura regen, station rebalance)

- Glissando activation glow a further 40% dimmer.
- Bravura: repairs 0.5% of maximum hull per second while active.
- Deployment points: Virtuoso 120, Unsung 45 (monthly supplies match).
- Sforzando slug width 12 (Untuned 10).
- Cantor Array rebalanced to the high-tech Star Fortress: core 160,000 hull / 2,400 armor (cloned from
  station3_hightech), Spires 14,000 hull with 0.6-efficiency shields and a Harmonic Driver + Sostenuto Rail each,
  Bells 12,000 hull with 220-degree 0.6-efficiency shields and Fortress Shield, Lofts 10,000 hull flying Requiem +
  Cadenza; ~232,000 hull in total (vanilla ~239,000).

## Unreleased - 2026-10-12 (Glissando/Sforzando visual pass)

- Glissando: the String's arcs and snap are white (Virtuoso); afterimages stay where they were left; activation
  glow a further 40% dimmer.
- Sforzando: the wake runs right up to the slug, so it continues through a skewered hull instead of breaking at
  the impact point; hull-impact glow 40% smaller and 50% dimmer (the slug is seen boring through); slug head glow
  20% smaller and dimmer.
- All rail haze trails: noisier smoke texture whose segments drift and curl at random as they fade, hiding the
  angular segment joints.

## Unreleased - 2026-10-12 (Glissando steering, kinetic Sforzando)

- Glissando: 720-unit dash (+20%), lasting 0.4 s; its heading swings towards the direction the ship is being flown
  (agility x3 while dashing), so thrusting mid-dash changes its direction (Virtuoso and Unsung). Activation glow 40%
  smaller and dimmer, white on the Virtuoso; the dash leaves a fading trail of afterimages.
- Sforzando: 160 damage (Untuned 144, both -20%), KINETIC damage (bonus and through-hull damage too). A slug
  stopped by a shield is removed on contact, so nothing renders inside the shield.
- Unsung: its untuned lance now skewers too (up to 3 ships); slug white, width 9, glow +15%.
- Virtuoso: shield raise rate x3 (was x2).

## Unreleased - 2026-10-12 (Sforzando tuning, Concert Pitch)

- Sforzando: slug width 10, head glow radius and intensity -30%, colour white-teal (mostly white) instead of gold,
  trail 20% less vivid; Skewer reaches 12 ships. Internal (through-hull) damage is now a fixed share of the slug's
  damage by hull size - +20% frigate, +40% destroyer, +60% cruiser, +80% capital - spread along the wound; shield
  hits unchanged.
- Rail impact effects (shield ripple, hull sparks, muzzle flash, pierce exits) toned down to roughly a third of
  their size and brightness.
- Bravura: the shield turns white-teal; EMP resistance moved to Concert Pitch.
- Unsung: 2 Glissando charges; its Bravura is now a separate "Bravura (Silent)" hullmod with a struck-through icon
  and a red INACTIVE section in the tooltip.
- New rare hullmod Concert Pitch (Lattice hulls only, 6/10/15/25 OP, not known from the start): +200 range for
  Resonance Lattice weapons, +15% max CR, +60 s peak performance time, 90% EMP resistance. Built into the Virtuoso
  and the Unsung.

## Unreleased - 2026-10-12 (Sforzando bore, gold slug, sounds v3)

- Skewer now bores through the inside of the hull instead of jumping to the far side: the slug carries on from the
  impact point, and every 25 units of path inside the hull deal 20% of its damage to the armor there (sparks along
  the wound), then it exits and continues to the next ship.
- The full Sforzando's slug is wider (13), hotter (glow radius 55, strong glow) and yellow-white, with a gold wake;
  its muzzle flash is gold-white. The Unsung's untuned lance stays teal.
- Sounds v3: stronger pitch shifts, a quiet octave-up shimmer layer, flanger/phaser/chorus modulation, light grit on
  the shard guns; every file peak-normalised, volumes re-levelled against vanilla.

## Unreleased - 2026-10-12 (Sforzando skewer, sounds v2)

- Sforzando Lance: 1,200 range (Untuned 1,000). Skewer: slugs that hit hull or armor go straight through at full
  damage into the next target, up to 6 ships in a row (replaces Cascade and the Accent pierce). Its trail lingers
  about three times longer.
- Sounds rebuilt as processed derivatives of the vanilla sounds the weapons used before (pitch, EQ, layering, a short
  metallic slap-back); the synthesised bell/string set and the custom impact sounds are gone (vanilla hit sounds play).

## Unreleased - 2026-10-12 (rail doctrine + fighters)

- Weapon doctrine: every gun is now a long-range, high-velocity rail (ranges 700-1500, slug speeds 1800-2800),
  keeping its gimmick. The Lattice Lance and Sostenuto are no longer beams: the Lance tunes in over consecutive hits
  on one ship (+15% per hit, up to +75%), the Sostenuto Rail adds 35% extra hard flux on shield hits. PD (Chime,
  Cantus) stays short-ranged.
- New sounds for every weapon and for shield/hull impacts, synthesised from scratch (no vanilla samples).
- Effects: MagicLib trails (white-teal wake + teal-to-violet ion haze) on every slug and missile; muzzle vent jets;
  glinting motes in flight; shield hits ripple along the shield's curve, hull hits throw sparks and crystal dust.
- Fighter wings: Trill (interceptor), Cadenza (heavy fighter), Requiem (rail bomber), with fighter-only rail guns.
  The Halo and the Cantor Lofts carry them; the Choir faction knows them.

## Unreleased - 2026-10-12 (Virtuoso power pass)

- Virtuoso: max speed 70, acceleration 85, deceleration 75, turn rate 24, turn acceleration 45; shield flux/damage
  0.5, shield turn and raise rate x2, EMP damage taken -75% (-90% in Bravura).
- Glissando is steerable: the dash adds to the ship's own movement and its heading turns with the ship.
- Bravura: +75% flux dissipation, +50% energy rate of fire, +20% damage to shields, +100% system recharge, a 3rd
  Glissando charge, white-gold shield. Accented Sforzando hits deal +50% damage.
- Unbound Core: no more range penalty.

## Unreleased - 2026-10-12 (first in-game feedback)

- Fix: crash in the refit/codex tooltip (`e != java.lang.String`): a bare `100%` in the Stolen Time description.
- Built-in guns (Sforzando lances, Conductor's spinal driver) sit in BUILT_IN slots and can no longer be removed;
  they are in the default weapon groups.
- Glissando costs 1% CR per dash (Unsung 1.5%). Stolen Time: killing a ship restores 5% (frigate) to 18% (capital)
  CR at once.
- One Resonance bar (it split into a second bar when the label switched to OVERTONE).
- Moving parts (vanes, blades, rings) use turret mounts so they pivot on their slot instead of floating a quarter
  of their length away (refit and combat).
- Seam glow drawn above the hull layers, brighter at zero Resonance.
- Shield radius = 10% beyond the farthest sprite pixel (hull + moving parts at rest); collision radius at least that.
- Cantor Array scaled x1.45 (core, ring and petals) to vanilla Battlestation size.

## 0.1.0 - 2026-10-11

- Ships-and-weapons build: 9 hulls + the Unsung + the Cantor Array station (core and 3 petal modules), with
  variants, descriptions and hull/engine styles.
- 13 weapons (12 + the Sforzando's untuned version), the Conductor's spinal driver, and 8 moving hull parts
  (rings, vanes, blades) as decorative weapons with animation scripts.
- 10 ship systems with AI, 8 hullmods (Lattice Core with Resonance/Overtone/Sympathy, Conductor's Bridge,
  Fracture, Stolen Time, Bravura, Unbound Core, Phase-Locked Petals, Tuned Wings).
- Seam glow rendered over every Lattice ship, following Resonance (CR for the Virtuoso, gold in Bravura).
- Choir faction (for fleet spawning only), two test missions.
