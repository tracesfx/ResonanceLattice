# Balance notes (0.1.0)

Every hull row is a clone of its nearest vanilla peer (`tools/gen_data.py`, `HULLS`), with only the design's columns
changed. Checked with `vanilla_baselines.py check --mod .`; each OUT-of-band stat and its reason:

| Hull (peer) | OUT | Why |
|---|---|---|
| Refrain (Hammerhead) | turn 32 (p90 34.5 - in band after tuning) | - |
| Staccato (Medusa) | accel 90, turn 45, durability/DP low | Striker: Unstable Injector and Grace Dash; pays in hull/armor |
| Tremolo (Fury) | shield upkeep 0.30 | Shield is its main defense between Standing Wave snaps |
| Halo (Astral) | low cargo/fuel | Combat carrier, logistics not its job |
| Virtuoso (Odyssey) | 80 DP, diss/DP 23, turn 14, peak CR 420 s, OP/DP 3.25 | Unique duelist (DESIGN.md 3.9): its cost is DP; short peak time is refilled by Stolen Time |
| Unsung | 55 DP, OP 220, peak 360 s | Prototype stage of the same ship |
| Cantor Array + petals | everything | Station core/modules (vanilla stations are outside the warship bands too) |

Weapons:

| Weapon | OUT | Why |
|---|---|---|
| Shard Caster, Crystal Flechette | "DPS low" | The checker counts one projectile; both fire 3 linked shards per shot (150 / 240 DPS) |
| Chime Repeater | range 450 | Short-range PD with an EMP chime every 4th shot |
| Pizzicato Lancet, Harmonic Driver | projectile speed 1200 / 1400 | Precision identity; Harmonic pays with a 1.5 s charge and 2 s cooldown |
| Tuning Spike | speed 600 | Low damage alone; value comes from the energy-hit combo |
| Lattice Lance | flux/s 110 | Base DPS 150 is low; the ramp (+75% after 3 s on one target) is the payoff |
| Resonance Bloom | EMP 1000 | Slow (300), poorly guided torpedo |
| Sforzando (built-in) | speed 2000, 200 dmg | Designed swarm breaker, never available separately |
| Unbound Core | 50 OP on a capital | Safety Overrides equivalent; vanilla SO is 45 OP on a cruiser |

Levers to tune in play (all constants in the Java classes): Resonance gain (`RslDamageListener.GAIN_*`), Overtone
cost (`LatticeData`), Stolen Time rate/cap (`StolenTime`), Glissando CR cost and string damage (`GlissandoStats`),
Sforzando bonuses (`SforzandoOnHit`).
