# Resonance Lattice — Ship & Sprite Proposal (Starsector 0.98a)

## Context
You want a ship-focused faction mod with sleek, modern, original sprites that sit between vanilla and the references you like (ScalarTech's clean panelling, DA's dense greebles, UAF's crisp plating, LoA's layered machinery). Nothing is copied from them. This plan covers the theme and lore, the 8 hulls with their systems and mechanics, the faction weapons, and the sprite pipeline for the next stage (prototype sprites, then iteration). Names are placeholders. Id prefix: `rsl_` (it can be renamed later).

Decisions made: **theme = Resonance Lattice**; **art = hybrid** (Blender-scripted 3D for hulls and large or animated parts, 2D procedural for small and medium weapons).

---

## 1. Theme & lore (seed)
A refugee research polity, provisionally "the Choir", grew out of a Domain-era harmonic-flux lab. Its ships are built around **lattice cores**: crystalline resonators that turn stress (flux, impacts) into stored charge. Their doctrine is musical. Ships "tune" to each other, and a fleet fighting together is stronger than the sum of its hulls.

**Visual language (shared by every hull):**
- Ivory/pale-grey ceramic plates (~214,210,200) over dark graphite machinery (~52,54,58). The two-material rule follows vanilla.
- **Signature accent:** thin glowing *lattice seams* (teal 90,220,210 shading to violet 150,110,230) that run along plate gaps. No big paint stripes, which keeps them clear of ScalarTech and DA.
- Secondary accent: small ink-blue tech markings and hex-cell micro-texture on machinery.
- Overhead lighting with no baked direction, mirror-symmetric, dark rim (vanilla's rules from sprites.md).
- Each class gets one **signature silhouette idea** (below), so no two ships read alike at 1x.
- Moving parts (rings, vanes, prongs) are done as decorative weapons, which brings the ships to life in combat.

## 2. Faction-wide mechanic: Lattice Core (custom built-in hullmod on every hull)
- **Resonance meter, 0–100** (MagicLib status bar). It builds from damage that hits your shields and from your weapons hitting enemy hull or armor. It decays slowly while you take no fire.
- **Seam glow follows Resonance.** A separate `_glow` sprite is drawn with alpha set by charge, so you can read a ship's state just by looking at it.
- **Overtone:** at ≥60 Resonance, each ship system triggers an empowered variant and spends the charge. Every system below lists a base effect and an Overtone effect.
- **Sympathy:** Lattice ships within 1500u share 15% of the Resonance they gain with each other. This rewards fighting as a group.
- Vanilla hullmods are built in for flavour (chosen per hull below), plus one restriction: Lattice cores are incompatible with `safetyoverrides`, because SO "detunes" the lattice.

## 3. The roster

| # | Class | Name (placeholder) | Silhouette idea | Role | Target size (px) | DP (to be checked) |
|---|---|---|---|---|---|---|
| 1 | Station | **Cantor Array** | Hex core + 3 petal modules + rotating outer ring | Fortress | core ~300², petals ~150×200 | — |
| 2 | Capital | **Conductor** | Tuning fork: twin prongs with a spinal weapon between them | Flagship battleship | ~240×420 | ~45 |
| 3 | Capital | **Halo** | Hull threaded through a large rotating ring | Defensive carrier | ~300×360 | ~40 |
| 4 | Cruiser | **Tremolo** | Catamaran: twin hulls joined by glowing lattice spars | Skirmisher | ~200×250 | ~22 |
| 5 | Cruiser | **Cadence** | Arrowhead with two long flank rails | Line/artillery | ~170×270 | ~20 |
| 6 | Destroyer | **Refrain** | Compact hull with hinged armor vanes | Escort/guardian | ~120×150 | ~10 |
| 7 | Destroyer | **Staccato** | Needle with forward-swept wings | Flanker/striker | ~130×160 | ~12 |
| 8 | Frigate | **Grace Note** | Dart with split tail fins | Stance-switch interceptor | ~70×90 | ~6 |

All sizes fall inside the vanilla p10–p90 bands in sprites.md. Final stats come from `vanilla_baselines.py peers` before any data is written.

### 1. Cantor Array — station
- **Look:** a hexagonal lattice-core hub with a large exposed crystal heart (strongest glow in the mod). Three petal modules sit at 120° spacing, and a thin outer ring rotates slowly as a decorative part.
- **Modules (three different petals):** *Bell* (flak and PD), *Choir Loft* (hangar with 2 bays), *Spire* (long-range lance battery).
- **Mechanic, "Phase-Locked Petals":** when a petal dies, its stored Resonance floods into the core and the surviving petals, which jump to Overtone. Killing modules makes the station *more* dangerous, so the player has to choose a kill order.
- **System, "Grand Chorus" (periodic):** all modules fire a synchronised lance volley. Overtone: an expanding harmonic ring flames out fighters and throws off missile guidance.
- **Built-ins:** vanilla station hullmods, plus `hardened_subsystems` on petals and `never_detaches` on modules.

### 2. Conductor — capital battleship
- **Look:** a long ivory blade split into two prongs. The inner faces of the prongs carry the brightest seams, with a huge spinal *Harmonic Driver* set between them. The prong glows pulse while it charges.
- **Mechanic, "Conductor's Bridge" (custom hullmod):** Lattice allies within 2000u get double Sympathy from the Conductor. It is the hub of the faction's group play.
- **System, "Sympathetic Strike":** after a 1.5s charge, a spinal beam hits its target and *marks* it for 8s. Hits on that target from any Lattice ship deal +20% damage. Overtone: the beam chains to a second target, which is also marked.
- **Built-ins:** `stabilizedshieldemitter`, `operations_center` flavour (command ship).

### 3. Halo — capital carrier
- **Look:** a slim hull threaded through a large ring. The ring is a separate decorative sprite that spins faster while the system is on. Launch bays sit on the ring.
- **System, "Stillwater Halo":** creates a 700u zone around the ship. Enemy projectiles that enter it slow by 60%, and missiles in it lose lock. While it runs, the Halo's own dissipation drops. Overtone: damage absorbed in the zone is turned into Resonance for allies inside it.
- **Mechanic:** fighters within the ring zone get +20% replacement rate (they are "tuned").
- **Built-ins:** `expanded_deck_crew`, `hardened_subsystems`.

### 4. Tremolo — cruiser
- **Look:** a catamaran of two narrow hulls joined by open lattice spars that glow, with real empty space between them. This makes it the most distinctive silhouette.
- **System, "Standing Wave":** the first press drops a node at the ship's position. Pressing again within 8s snaps the ship back to the node and restores 40% of the armor lost since. Overtone: an afterimage left at the departure point detonates (EMP + energy damage).
- **Built-ins:** `auxiliarythrusters`.

### 5. Cadence — cruiser
- **Look:** an arrowhead hull with two long rails down the flanks that hold forward hardpoints. It reads as precise and martial.
- **System, "Crescendo" (6s):** each consecutive energy hit adds rate of fire (up to +100%), and flux cost rises with it. Overtone: at max stacks, every energy weapon fires one *Fortissimo* shot together, then the ship soft-vents.
- **Built-ins:** `dedicated_targeting_core`.

### 6. Refrain — destroyer
- **Look:** a stocky hull with two large armor vanes on hinges (decorative parts) that swing forward to shield the bow while the system is on.
- **System, "Sympathetic Ward":** targets an ally within 800u. 40% of the damage the ally takes goes to the Refrain's shield instead (shown by a beam tether). Overtone: redirected damage gives double Resonance, and the vanes reflect a share of incoming beam damage.
- **Built-ins:** `escort_package`.

### 7. Staccato — destroyer
- **Look:** a needle body with sharp forward-swept wings, aggressive and slim.
- **Mechanic, "Fracture" (hullmod):** Staccato hits put Fracture stacks on the target (up to 5). At 5 stacks, the next hit causes a shatter: bonus armor damage on that armor cell, and the stacks reset.
- **System, "Grace Dash":** a short dash (in the style of microburn). Overtone: the dash leaves a resonant wake that arcs EMP into enemies passing through it.
- **Built-ins:** `unstable_injector` (a speed-tuned drive with a range penalty, which suits a brawler).

### 8. Grace Note — frigate
- **Look:** a small dart with split tail fins and a single bright seam down the spine.
- **System, "Pitch Shift" (toggle stance):**
  - *Harmonic:* shields up, +25% dissipation, and weapons add EMP.
  - *Discord:* shields locked off, +30% speed, and +20% weapon damage.
  - The seam colour changes with the stance: teal for Harmonic, violet for Discord.
  - Overtone: switching stance releases an EMP pulse.
- **Built-ins:** `hiressensors`.

## 4. Faction weapons (initial set)

| Weapon | Mount | Behaviour |
|---|---|---|
| Chime Repeater | S energy, PD-capable | Pulse bolts; every 4th shot is an EMP "chime" |
| Lattice Lance | M energy beam | Damage ramps the longer it stays on the same target (resets on switch) |
| Crystal Flechette | M hybrid | Shotgun of crystal shards; shards that hit armor leave a short DoT |
| Tuning Spike | S/M missile | Embeds in the hull and detonates when a Lattice energy weapon hits that target (combo) |
| Harmonic Driver | L energy | Charge-up shot; a full charge pierces. Also the Conductor's built-in spinal |
| Resonance Bloom | L missile | Slow torpedo that bursts into an expanding frag + EMP ring |
| *Deco set* | DECORATIVE | Halo ring, Cantor ring, Refrain vanes, Conductor prong glows, Lattice seam glows |

Slot types lean ENERGY, with HYBRID/SYNERGY flex and few MISSILE slots. Weapons stay usable by other factions (no hard lock), but some behaviours get stronger on Lattice hulls.

---

## 5. How the sprites will be made (next stage)

### Pipeline overview
```
hull spec JSON  ──►  Blender (headless, scripted)  ──►  4x render passes  ──►  2D finishing (Python)  ──►  sprite + _glow + maps
      │                                                                                     │
      └──────────────────────────────►  .ship geometry (slots, engines, bounds) ◄───────────┘
```
One spec per hull drives **both** the art and the `.ship` file, so slots and engines can't drift off the art (the same principle as the skill's `hullgen.py`).

### 5a. Scaffold (once)
- `python ~/.claude/skills/starsector-modding/scripts/selftest.py`
- `new_mod.py create --name "Resonance Lattice" --deps lazylib,magiclib` → `mods/ResonanceLattice/` with prefix `rsl_`; GraphicsLib optional and guarded.
- Dev-only art sources go in `ResonanceLattice/art_src/` (kept out of the release zip).

### 5b. Blender toolkit (`art_src/blender/`, Blender 4.2 at `C:\Program Files\Blender Foundation\Blender 4.2\blender.exe`)
- `kit.py`, a reusable parts library:
  - beveled ceramic plates (grooves cut into them for seams)
  - graphite machinery greebles (vents, pipe runs, hex-cell blocks, heat sinks, capacitor stacks)
  - turret ring sockets, engine nozzles
  - **emissive seam strips** on a separate material
  - crystal core material
  - Each part is parameterised (size, bevel, seed) so the same vocabulary repeats across all ships. That is where the consistency comes from.
- `hulls/rsl_<id>.py`: each hull is built from a symmetric half and mirrored. The silhouette comes from the spec's polygon outline, extruded and beveled. Plates are laid in bands, and greebles fill the machinery areas.
- `render.py`: an orthographic top-down camera with soft, even overhead lighting plus AO (Cycles on GPU, or Eevee for speed), at 4x the final size. The passes are:
  - colour (seams off)
  - emission (seams only)
  - normals
  - depth
  - a material ID mask (plate, machinery, seam)
  - alpha
- Run: `blender -b -P render.py -- --hull rsl_conductor --out art_src/renders/` (each render takes seconds to about a minute; **I'll ask before the first GPU run**).
- Moving parts (Halo ring, Cantor ring, Refrain vanes, Conductor prongs) are rendered as separate objects and become decorative weapon sprites.

### 5c. 2D finishing (`art_src/finish.py`, Python + Pillow + numpy)
1. Premultiplied-alpha downscale from 4x to 1x.
2. **Ink pass:** 1px darkened panel lines found from jumps in depth and normals. This gives the crisp "painted, not rendered" read.
3. Tone-match to the vanilla band (between Midline and High Tech), plus a dark rim and alpha bleed. This reuses the functions in `sprite_tools.py` and `sslib.py` from the skill.
4. Outputs:
   - `graphics/ships/rsl_<id>.png`, 8-bit RGBA, even width.
   - `rsl_<id>_glow.png`, the seam layer, drawn by the Lattice Core plugin with alpha set by Resonance.
   - GraphicsLib maps:
     - normal, converted from the render's normal pass to GraphicsLib's axes (R = right, G = down)
     - material
     - surface
5. The `.ship` file is written from the spec: `center`, slots, engines, `bounds` (simplified from the alpha contour, 12–20 points), and `collisionRadius` and `shieldRadius` at vanilla ratios.

### 5d. Weapons
- **Small and medium weapons:** `weapongen.py` with a new *lattice* recipe: ivory housings, graphite cores, teal lens or seam accents, and the dark 1px separation and roughly 25–44% coverage vanilla uses. Turret and hardpoint sprites come out with matching `.wpn` offsets. Glow frames for charge-up use `_glow` sprites.
- **Large weapons and the deco set:** the same Blender kit, rendered top-down, then the same finishing pass.

### 5e. Prototype order & iteration loop
1. **Style test first:** Grace Note (frigate) and Refrain (destroyer). These lock the material, seam and ink look while the ships are cheap to redo. You review them before I continue.
2. Then Staccato → Cadence → Tremolo → Conductor → Halo → Cantor Array (the station's modules come last because they're the most complex).
3. After every pass:
   - `contact_sheet.py --mod . --peers 2 --scale 1,2 --overlay`, judged at **1x** next to vanilla peers.
   - `sprite_stats.py --mod .` to check tone, saturation, rim and edge density against the bands.
   - A private comparison sheet next to your reference sprites (style read only, never traced).
4. You give feedback → I adjust the spec, kit or finishing parameters → re-render. Each iteration takes minutes, because everything is generated.

## 6. Scope budget
- **MUST (next stage):** scaffold; the Blender kit, render and finish pipeline; prototype sprites + `.ship` geometry for all 8 hulls; glow layers; 6 weapon sprites + deco set; contact sheets.
- **SHOULD (stage after):** data (ship_data and weapon_data rows from vanilla baselines); the Lattice Core hullmod; the 8 ship systems in Java with AI; weapon scripts.
- **STRETCH:** a custom fighter wing for Halo and Cantor; station placement in a star system; faction, markets and lore text.

## 7. Risks
- Downscaled 3D can look "CG". The ink pass, tone-matching and the style test on two small hulls come first so this is caught early.
- The station's modular setup and the rotating rings need careful `.ship` and module wiring. That is why the station comes last.
- Blender renders use the GPU briefly, so I'll ask before the first run.
- None of the tools can judge balance or motion. In-game checks are yours (`templates/SMOKE_TEST.md`).

## 8. Verification
- `./build.sh` (or `build.bat`) reports **0 errors**. `validate_mod.py` checks for 8-bit PNGs, even weapon widths, sprite size against the `.ship`, slots on opaque pixels, and path case.
- `contact_sheet.py --overlay` shows slots, engines and bounds lined up with the art. `sprite_stats.py` is in band, or the deviation is explained.
- In game, done by you: the ships load in the simulator / Codex, sprites read clearly at combat zoom, deco parts move, and the glow responds. Afterwards, `log_scan.py --mod .` is clean.
