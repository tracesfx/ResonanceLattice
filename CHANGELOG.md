# Changelog

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
