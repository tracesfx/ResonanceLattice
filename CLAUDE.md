# Resonance Lattice — Starsector 0.98a faction/ship mod

Ship-focused faction mod. Mod id `resonance_lattice`, id prefix `rsl_`, Java package `rsl` (`RslModPlugin`, `RslIds`).
Deps: LazyLib, MagicLib (hard); GraphicsLib optional (guard with `isModEnabled("shaderLib")`).
Use the **starsector-modding** skill (`~/.claude/skills/starsector-modding/`) for all data, code, balance and validation.
Never launch the game or edit vanilla / other mods without the user's explicit OK.

**Design proposal: `DESIGN.md`** (theme, 9 hulls incl. the unique Virtuoso, systems/mechanics, weapons, art plan,
scope, risks). Read it before designing or drawing anything. Names are placeholders; lore will rename them later.
**Where DESIGN.md and this file disagree on art (colours, shapes), this file wins** — it holds the latest user
feedback.

## Status (2026-10-11)

- Stage 1 (proposal): done. Stage 2 (prototype sprites): in progress.
- Sprites done: Grace Note, Refrain, Staccato, Cadence — user approved the steel + dark-blue art direction
  ("I really enjoy the art direction now") and asked for one final iteration (Cadence: no round blisters, sharp
  swept rail tips, gradients on flat areas; Refrain: gradient on the flat centre), then one more quick fix
  (Cadence: asymmetric rail/body gap, unnecessary grey web platform, livery stripes all parallel). Both done;
  sheet: `art_src/review/final_v2.png` (all four hulls + Eagle/Medusa).
- **Tremolo v2 (awaiting user feedback):** user picked option A "Fork" of `art_src/review/tremolo_options.png`.
  A filled-deck variant (spars removed, aft gap filled with a deck + scaffold, seams rerouted) was tried and
  REJECTED ("this one is worse"; the v1 seams are "actually decent") — keep the open aft gap and the v1 seams.
  v2 = v1 + the X-spars rebuilt as intricate open truss girders with NO hub/diamond at the crossing.
  Sheet `art_src/review/tremolo_v2.png` (v1: `tremolo_v1.png`); generator `art_src/gen/gen_tremolo.py`.
- Older review sheets: `final_v1.png`, `cadence_v2.png`, `steel_livery_v1.png` (yellow test, rejected), `cadence_options.png`
  (silhouette options; user chose C), `styletest_v*.png`.
- **Halo v1 (awaiting user feedback; user jumped to it ahead of Conductor/Virtuoso):** user picked option C "Eye" of
  `art_src/review/halo_options.png`. Sheet `art_src/review/halo_v1.png`; generator `art_src/gen/gen_halo.py` writes
  BOTH `rsl_halo.json` and the deco `rsl_halo_ring.json`.
- **Conductor** (option C "Split blade" of `conductor_options.png`, inner blades close). v1 rejected ("extremely bulky,
  tin-foil like", gradients uncohesive, dots ≠ detail) → **v2** slim segmented spine (awaiting feedback). Generator
  `art_src/gen/gen_conductor.py` writes `rsl_conductor.json` + deco `rsl_conductor_blade_r.json` (+ `_l` mirror_of).
- **Round 3 (awaiting feedback), sheet `art_src/review/sheet_v3.png`:** Conductor v2, Tremolo v3 (X-spars integral:
  steel chords + gussets), Halo v2 (hollow well). Per-hull sheets `conductor_v2.png`, `tremolo_v3.png`, `halo_v2.png`.
- Next, in order: round-3 feedback → **Virtuoso (+ Unsung skin)** → Cantor Array (station last).
- Data (ship_data/weapon_data rows), hullmods, systems and Java code are NOT started (next stage after sprites).
- Build: `./build.sh` → 0 errors. Expected warnings only: scaffold TODO placeholders, `.ship` files without
  ship_data.csv rows, unreferenced glow/map/deco assets.
- git: commits on `master`. End commit messages with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

### Virtuoso (unique player capital, DESIGN.md §3.9) — design agreed, art not started
Two stages: Unsung skin (55 DP, questline start) upgraded via `variant.setHullSpecAPI` to the full Virtuoso (80 DP;
the user's "OP cost 80" = DP). Power comes from its kit like Ziggurat (user: Ziggurat is strong because of system,
dissipation, phase, Phase Anchor — not raw stats): Glissando dash (2 charges, i-frames, **costs 2% CR**, leaves
"the String" that snaps after 1.2 s: line damage + CR drain, blocks projectiles), 1,200 dissipation, SO allowed on a
capital, Stolen Time (CR theft), Bravura at 100% CR (buffs + **seams cross-fade to gold-white** via a 2nd glow
sprite — gold glow is fine; the "no yellow" rule is about paint). Sforzando Lance ×2 = semi-rapid railgun TURRETS
(2,000 proj speed, zero spread, 45°/s turn, ANTI_FTR + USE_VS_FRIGATES, Cascade pierce on small-ship kills) so it
shreds frigate/fighter swarms. Quest not designed yet.

## STANDING ART DIRECTION (all user feedback so far — follow on every hull)
1. **Colours: clean stainless steel + dark blue + teal seams. NO YELLOW anywhere** (paint, markings; it read as
   caution tape). Graphite machinery underneath. Ivory was replaced (kit material names "ivory"/"ivory2"/"slate" are
   legacy: bright steel / brushed mid steel / gunmetal).
2. **Never a flat single-colour hull.** Every hull gets its own **livery** that fits its silhouette (UAF Zepporia's
   splinter tones, DA Pandemonium's bold stripes are the references). Splinter bands are **dark blue**, not grey.
   **Vary the technique per ship — not stripes everywhere; use gradients too.**
   **Vary splinters within a hull too:** different angle and irregular band widths (`widths`) per region, never one
   parallel pattern over the whole ship.
   **No large flat single-tone steel areas may remain** — check every big plate at 2x; fix with a gradient (keep
   any splinter on top). Current set:
   Grace Note = dark-blue gradient deepening aft + gunmetal chevron band; Refrain = dark-blue zigzag splinter +
   dark-blue gradient down the centre spine and aft deck, vanes = gradient from the tip; Staccato = wing gradients
   deepening to the tips + short dark-blue "staccato" dashes on the leading edges; Cadence = gradients deepening
   towards bow and stern + down the barbs, with three regional splinters on top (bow: tight forward chevrons;
   midship: broad reversed-slant zigzag; barbs: cross-bands tightening towards the tips).
3. **Busy, DA density:** exposed machinery bands, many small parts — but no speckle noise on big plates.
4. **Sharp, angular, intricate engineering.** No geometric primitives as silhouettes: no isosceles triangles, no
   rectangles/boxes, no eggs, no rockets, no parallelogram panels. A silhouette = several distinct masses with
   different edge angles, notches between them, protrusions (prongs, pods, fins, canards, swept tips — not round blisters). DA sharpness:
   split bows (stepped spear + mandibles), diagonal tip cuts, chamfers, segmented armour, stepped edges.
5. **Nothing fragile:** parts must be structurally attached (no free-standing "solar panel" rails, no splayed
   "legs"). Long attachment roots and clamps. But no filler "platforms" either: the user had the Cadence's grey web
   plates removed — an arrowhead's barb notch may stay open.
5b. **Symmetry must be exact.** Check with the mirror-diff snippet (Gotchas) after every render.
6. **Moving parts are centerpieces:** big, angular, with their own prominent seams (Refrain vanes).
6b. **No round/octagonal blisters bulging out of the silhouette** (user disliked the Cadence's "circles"); put turrets
   on the existing structure. Wing/rail ends are **sharp swept tips** (outer edge runs on to a point, inner edge
   slants into it), not blunt caps.
7. **Seams are THE identifier** — very noticeable, never tree/branch shaped: use the lattice script.
7b. **Review sheets (user, 2026-10-11):** every sheet shows Cadence, Tremolo, Halo and Conductor (+ the hull being worked
   on if it's another one) and ONE vanilla reference:
   `python art_src/preview.py out.png rsl_cadence rsl_tremolo rsl_halo rsl_conductor --peers onslaught`.
7c. **Intricate, not bulky (Conductor v1 feedback):** a big hull must be built from many distinct structural parts
   (segmented prongs/wings with clamps, housings, exposed machinery gaps), never one broad envelope. Tiny dots
   (surface_detail specks, lights, stray glow bits) are SECONDARY and never substitute for detail.
7d. **Gradients are used tastefully, at the extremities only** (edges/tips of swept wings, vanes, barbs; near the stern),
   as on Cadence/Staccato. Dark-blue gradients spread over the main plates read as "tinfoil / blue metal", not a
   livery. The livery must be one cohesive idea per hull, with crisp painted shapes doing most of the work.
7e. **Integral, purposeful structure (Tremolo/Halo feedback):** connecting parts must look like load-bearing parts of
   the hull, not auxiliary add-ons; no flat single-colour filler platforms (Halo's grey inner platform was rejected:
   hollow it out, keep only what is needed, e.g. the fighter bays).
8. When a silhouette doesn't converge after ~2 tries, sketch 2–3 flat options (`art_src/gen/cadence_options.py`
   pattern) and ask the user to pick, instead of guessing further.

### Lattice script (seam language)
- **Conduits** (`conduit` detail): straight runs with 45°/90° bends from the core to something functional (weapons,
  engines, hinges, rails, tips). No branching; a conduit ends in a node or at a socket/engine.
- **Nodes** (`node`): ringed glow terminal; the core is a `diamond` node on the spine/keel.
- **Resonator cells** (`cell`, `v` > 0 = chevron bars pointing forward): brightest signature, symmetric pairs; one
  small cell as a nose glyph. Staccato uses wide-pitch cells (fill 0.38).
- **Emitters / accelerators**: glow cuts along leading edges or down rails, with coil nodes.
- Seam colour: teal 90,220,210 → violet 150,110,230 towards the tail.

### Sprite state
- **Grace Note** 68×116, mass 3,238: sharp dart, V-notched nose, tucked clipped-delta fins, side pods.
- **Refrain** 106×160, mass 10,118 + vanes: split bow (stepped spear, glyph, medium turret behind it, two mandibles),
  stepped shoulder seams. Vanes `rsl_refrain_vane_r` (22×204, pivot at centre, ~100 px blade) + `_l` = pixel mirror;
  slots WS0009 (+x, angle -162, deployed 12) / WS0010 (-x, 162, deployed -12).
- **Staccato** 150×186, mass 11,340: needle fuselage, stepped spear, strakes, forward-swept segmented wings with
  tip prongs and a sawtooth notch.
- **Cadence** 200×320 (SCALE 1.14), mass 21,288 (cruiser p10 20,876): **arrowhead** (user picked option C, "rails
  longer, goal is an arrowhead"): long stepped needle bow → faceted head with canards → two long rails swept back
  from the shoulders as **barbs** (rooted in the hull at the shoulders, open arrowhead notch behind — no web
  platform; two raised segments stepping outward + a tapering swept-tip blade, gunmetal clamps, accelerator seams
  with coil nodes; medium/small turrets sit on the rails; core conduit enters the rails at their root) → waist →
  engine block with pods. Generated by `art_src/gen/gen_cadence.py`
  (edit the generator, never the spec). Mass is right at the band floor: removing area needs SCALE up.
- **Tremolo** 208×262, mass 24,993 (cruiser band 20,876–32,570): catamaran "Fork" — two hulls (long stepped spear
  bow + inner mandible tooth; outer edge zig-zags in/out = a "tremolo waveform" silhouette: fore slants out, sponson
  with forward-out tooth slants in, mid slants out, engine flare into a swept aft tip), forward bridge with the
  lattice core + leading-edge emitter strakes, open fork between the bows, open aft gap spanned by an X of truss
  girders (each: twin gunmetal rails with their own glow lines + steel Warren zig-zag bracing; the girders cross
  through each other, lattice nodes on the 4 rail crossings, no hub) + a cross bar, gunmetal clamps at every
  spar/bridge root. Livery: dark-blue zig-zag **waveform stripe** down each outer
  flank (two frequencies), inner faces darken towards the gap, outer flank gradient, bow/stern gradients, bridge
  chevrons, engine cross-bands. Plates are generated as inset bands of the frame outline (`region()`), so the gaps
  expose machinery. Mirror-diff reads ~380 px: invisible 1-px ink jitter along its many long plate edges
  (verified L vs mirrored R at 5x), not a geometry asymmetry.
- **Halo** 310×380, mass 78,085 (capital p10–p90 45,219–146,692): wide carrier wrapping a ring that spins in a
  central well. Stepped spear + canards → head with back-swept shoulders → deep V notch → two claw prongs with swept
  tips → fore flight deck slanting out to a tooth → aft deck slanting in → swept aft fins → stepped engine block.
  Raised gunmetal flight decks with bay hatches (4 HIDDEN LAUNCH_BAY slots), bearing race + clamps around the well,
  dark well floor with static ribs + glow ring, lattice core diamond at the centre. Conduits run from the race clamps
  to the turrets/engines. Ring = deco `rsl_halo_ring` (188×188, slot WS0009 at the well centre, arc 360): 6 segments
  with swept teeth (they show the spin direction, so the ring is deliberately NOT mirror-symmetric), hatches, glow
  seam, 3 spokes + hub (hollow centre shows the core); alternate segments navy so rotation reads. In game it needs an
  EveryFrameWeaponEffectPlugin to spin it (faster while the system is on). Livery: "Stillwater" broken concentric
  ripple arcs + flank gradient deepening outward + prong gradients + engine cross-bands.
- **Conductor v2** 264×476 (SCALE 1.07), mass 46,214 (capital band floor 45,219 — removing area needs SCALE up):
  slim segmented spine built from distinct parts: two stepped spear prongs (tip/mid/root + gunmetal clamps, slate
  inner faces) joined by a muzzle yoke that braces the baked-in Harmonic Driver barrel (the slot is an open window)
  → long breech cradle with 4 coil rings, capacitor housings (resonator cells) and the core diamond → forward-swept
  crossguard wings (root housing, 2 segments, tip blade, clamps, emitter leading edges, built like the Cadence barb
  with C(t, s)) → slim waist with strakes → tapering stern; engine nacelles sweep out and aft from a 60 px root (open
  V notch behind, like fletching) → gunmetal engine block. Blades `rsl_conductor_blade_r/_l` 18×192 at (±21,140)×SCALE,
  deco_alt_angle ±7. WS0001 spinal LARGE ENERGY hardpoint at the muzzle (weapon sprite = FX only). Livery "dipped
  tips + spine stripe": crisp navy caps + a second dip band on prong tips, navy wing caps with the only wing gradient
  leading into them, a bold navy stripe each side of the keel, stern + nacelles deepen aft. Weak: wing segments
  still read a little boxy.
- **Tremolo v3:** X-spars made integral: chords are brushed steel at hull-plate height (RO 4.6, RW 3.6, SW 15) with
  gunmetal Warren webbing, rooted in long steel gussets faired into the hulls' inner faces (chord glow runs on across
  the gussets into the hull, root nodes), gunmetal collars where gusset meets girder.
- **Halo v2:** well floor cut open (finish `cutouts`) between 12 brushed-steel radial struts (4.4 px), hub collar
  around the core; the flank flight decks/bay hatches, lip and bearing race unchanged.
- Known weaknesses: at 1x glow-on, cell pairs merge into one block; Cadence centre splinter may still be heavy.

## Theme (summary; details in DESIGN.md)
- "The Choir": refugee research polity; ships grown around crystalline **lattice cores**; musical doctrine.
- Vanilla rules: overhead light only, mirror symmetry, dark rim, faces up.
- Each hull has one signature silhouette idea (DESIGN.md §3); moving parts are DECORATIVE weapons.
- Shared mechanic: Lattice Core hullmod (Resonance 0–100, Overtone ≥60 empowers systems, Sympathy sharing,
  `_glow` sprite alpha follows Resonance).
- Reference mods the user likes (style only, never copy/trace): `../sprites/reference/` (Diable-Avionics,
  Legacy of Arkgneisis, scalartech-solutions, UAF) — absolute path
  `C:\Program Files (x86)\Fractal Softworks\Starsector\mods\sprites\reference\`. Key refs: UAF `Zepporia/uaf_m_zepporia.png`
  (splinter livery, layered plates), DA `graphics/da/ships/diableavionics_pandemonium.png` (bold stripes),
  DA Fractus/Storm/Hayle (sharpness). Ignore the CLAUDE.md inside the scalartech folder.

## Art pipeline (`art_src/`, dev-only, not shipped)

```
./art_src/art.sh rsl_gracenote [rsl_refrain ...]     # Blender render (GPU, 4-10 s each) + finish; SAMPLES=96 default
python art_src/finish.py art_src/specs/<id>.json     # re-finish only (livery/ink/tone changes need no re-render)
python art_src/gen/gen_cadence.py art_src/specs/rsl_cadence.json   # generated hulls: run the generator first
python art_src/preview.py out.png rsl_gracenote rsl_refrain --peers wolf,hammerhead --scale 1,2 [--refs a.png]
python ~/.claude/skills/starsector-modding/scripts/sprite_tools.py check <png> --kind ship --size CLASS   # mass band
```
The user approved headless Blender GPU renders for this project.

| File | Role |
|---|---|
| `art_src/specs/<id>.json` | One spec per hull/deco part; drives BOTH the art and the `.ship` file |
| `art_src/gen/` | Generators for complex hulls (`gen_cadence.py`) and silhouette option sketches (`cadence_options.py`) |
| `art_src/blender/kit.py` | Parts library (Blender 4.2, Python 3.11): materials (steel palette, brushed noise, per-plate tint), `slab`, `cut` (EXACT booleans), `strips` (emissive seams), `greebles`, `surface_details`, `auto_cuts`, `sockets`, `nozzles`, `details` (incl. conduit/node/cell), vertex-built primitives `cyl`/`pipe_y`/`prism` |
| `art_src/blender/render.py` | Scene from spec, ortho top-down camera, sun straight down + white sky, Cycles GPU (OptiX), `renders/<id>/{color,emit,normal,height,matid}.png` at 4x; prints `RSL_T` step timings |
| `art_src/finish.py` | **Livery** (at 4x, before ink), ink lines, crest highlights, 4x box downscale, `hullgen.tone_match` (TARGET p5 .11 / p95 .80 / mean .44; seams and white paint excluded), rim, seam tint/hot core/spill, alpha bleed, glow layer with halo, GraphicsLib maps, `.ship` via `hullgen`. `mirror_of` deco specs are flipped from their source |
| `art_src/preview.py` | Review sheet: sprite, glow-on variant with decos at `deco_alt_angle` (canvas padded, never cropped), peers, refs |
| `art_src/scale_spec.py` | Scale a spec's geometry incl. livery (`walk()` is also imported by generators) |
| `art_src/review/` | Saved review sheets for the user |
| `art_src/renders/` | Intermediate passes (gitignored) |

Blender exe: `C:\Program Files\Blender Foundation\Blender 4.2\blender.exe`. finish.py imports `hullgen` from the
skill's scripts folder.

### Spec format (coordinates = final pixels; x = lateral offset from centre line, + = right; y = from top)
- `size [W,H]` (W even), `hullSize`, `id`, `name`, optional `"kind": "deco"`, `"mirror_of"` (L/R deco pairs),
  `"finish": {...}` overrides (`ink`, `ink_step`, `ink_crease`, `crest`, `rim`, `seam_base`, `seam_hot`, `seam_spill`,
  `halo`).
- `layers[]`: `name`, `mat` (ivory=bright steel, ivory2=mid steel, slate=gunmetal, graphite, steel, accent, seam,
  crystal, nozzle), `z [z0,z1]`, `bevel`, shape via `half` (x≥0 outline, mirrored), `poly`, `sym_poly`; `holes`,
  `cuts[]` ({`pts`, `w`, `depth`, `glow`, `sym`}), `auto_cuts`, `tiers[]` ({`inset`, `dz`, `mat`, `bevel`, `cuts`}).
  Overlapping shapes inside ONE layer punch even-odd holes: use separate layers (e.g. `f_body`, `f_rail`, …).
- Typical z: frame graphite 0–3, greebles 3–3.9, plates 4–6.2, raised housings 5.2–7.6, tiers +0.4–0.7, spine higher.
- `greebles` {layers, z0, zmax, density, seed}; `surface_detail` {layers, density ≤ 0.08, seed}.
- `details[]`: hatch, light, vent, mark/line, block, crystal, dome, `conduit` {pts, w}, `node` {pos, r, shape},
  `cell` {pos, size, n, v, slant, fill} (`sym` mirrors).
- `livery[]` (applied in order, only on plate materials; `on` = matid list, default [2] = bright/mid steel; `sym`
  mirrors shapes, `mirror` uses |x| for patterns; `alpha`):
  `poly` {poly, color}; `band` {pts, w, color}; `stripes` {poly?, angle, period, w, color};
  `splinter` {poly?, angle, period or widths: [..] (irregular, cycling), zigzag, amp,
  colors: [null, "navy", ...] (painted bands; one entry per band) or tones: [1.0, 0.74]};
  `gradient` {poly?, color, a: [x,y], b: [x,y], a0, a1} (opacity ramp a→b).
  Paints (finish.PAINT): navy, blue, white, steel_light, steel_dark, gunmetal, black. Paint keeps the rendered
  shading; ink lines cut through it afterwards. Bands/periods must be broad (≥ ~1/4 hull width) or they read as noise.
- `slots[]` / `engines[]`: hullgen format; decorative slot: `"type": "DECORATIVE"`, `"deco"`, `"deco_alt_angle"`.

### Gotchas learned
- Curve-converted meshes must be welded (`remove_doubles`) or EXACT booleans silently fail — done in `slab`.
- A tier covers the grooves below: glow cuts go on the **topmost tier**. Very thin plates + big inset = no tier.
- Deco sprites rotate about their centre (pivot at image centre). Smaller deco angle folds INWARD; negative sweeps
  out. The game never flips deco sprites: asymmetric parts need an R spec + `mirror_of` L spec, two non-sym slots.
- **Curve-fill holes only work when the hole lies fully inside ONE outline** (render.py now carries `holes` into
  tiers too). A hole crossing a plate edge or a sym_poly pair gets filled as an extra shape. For the Halo well the
  ring is a separate sprite, so the well parts are simply stacked ABOVE full plates instead.
- `inset()` sign bug (plates ~1.5 px OUTSET) is fixed in all generators (Tremolo since v3; its mirror-diff dropped to 58).
- `finish.py` spec key `"cutouts": [poly, ...]` (spec coords, no mirroring) zeroes alpha/emit/height at 4x before
  inking: real openings through stacked parts (Halo well windows). `.ship` bounds still follow the outer contour.
- Never call `bmesh.ops.*` per part in kit.py (O(n²) → a cruiser hung 10+ min). Build primitives vertex by vertex.
- Symmetry traps (fixed 2026-10-11): (1) per-plate tint used Object Info Random → mirror twins differed; now a
  white-noise hash of the plate centre's (|x|, y) (parts get origin_set to their bounds centre) and the material
  noise uses world position with |x|. (2) EXACT booleans sometimes skip ONE of a mirrored groove pair; glow strips
  now sit flush with the surface so the seam shows even then; cuts are applied one boolean each, FAST fallback.
  Check: `python -c "import numpy as np;from PIL import Image;a=np.asarray(Image.open(P)).astype(int);
  d=np.abs(a-a[:,::-1])[...,:3].mean(-1)*(a[...,3]>0);print((d>60).sum())"` — a few dozen edge pixels is fine.
- Tone match pulls bright paint toward the mean: bright paints must be protected (done for white; yellow is banned).
- Judge at 1x first; check mass band after every pass; scale via the generator's SCALE or `scale_spec.py`.
- Silhouette lessons (Cadence took 6 versions): parallel rails = rectangle; straight diagonals = triangle; all-rect
  modules = box; one smooth envelope = egg; vertical-sided midship = rocket. What worked: a chosen massing sketch,
  then masses with different angles + long attached barbs + notches + protrusions.

## Next steps after sprites (from DESIGN.md scope)
SHOULD: ship_data/weapon_data rows from `vanilla_baselines.py peers` (clone nearest vanilla, change only what the
design needs), Lattice Core hullmod, the ship systems + AI, weapon scripts, GraphicsLib texture_data CSV for the
maps, Virtuoso hullmods/system/Sforzando. STRETCH: fighter wing, station placement, faction/markets/lore text,
Virtuoso questline.
