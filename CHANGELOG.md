# Changelog

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
