# Resonance Lattice — Starsector 0.98a faction/ship mod

Ship-focused faction mod. Mod id `resonance_lattice`, id prefix `rsl_`, Java package `rsl` (`RslModPlugin`, `RslIds`).
Deps: LazyLib, MagicLib (hard); GraphicsLib optional (guard with `isModEnabled("shaderLib")`).
Use the **starsector-modding** skill (`~/.claude/skills/starsector-modding/`) for all data, code, balance and validation.
Never launch the game or edit vanilla / other mods without the user's explicit OK.

**Full approved design proposal: `DESIGN.md`** (theme, all 8 hulls with systems/mechanics, weapons, art plan, scope,
risks). Read it before designing or drawing anything. Names are placeholders; lore will rename them later.

## Status (2026-10-11)

- Stage 1 (proposal): done, approved.
- Stage 2 (prototype sprites): **style test approved** (Grace Note v2 approved; Refrain v3 = final requested
  iteration). Review sheet: `art_src/review/styletest_v3.png` (v1/v2 kept for comparison).
- Staccato v1 done (150x186, mass 11,340): review sheet `art_src/review/staccato_v1.png`, awaiting user feedback.
- Next, continue in order: Cadence → Tremolo → Conductor → **Virtuoso (+ Unsung skin)** → Halo → Cantor Array.
- **Virtuoso** (added 2026-10-11): unique player capital, DESIGN.md §3.9. Two stages: Unsung skin (55 DP, start of
  questline) upgraded via `variant.setHullSpecAPI` to the full Virtuoso (80 DP). Power comes from its kit, like
  Ziggurat (Glissando dash system, 1,200 dissipation, i-frames, SO allowed on a capital), plus Stolen Time (CR theft)
  and Bravura (100% CR: buffs, seams cross-fade to gold-white via a 2nd glow sprite). The user meant "OP cost 80" as
  80 DP. The quest itself is NOT designed yet.
- Data (ship_data/weapon_data rows), hullmods, systems and Java code are NOT started (next stage after sprites).
- Build: `./build.sh` → 0 errors. Expected warnings only: scaffold TODO placeholders, `.ship` files without
  ship_data.csv rows, unreferenced glow/map/deco assets.
- git: commits on `master`. End commit messages with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

### User feedback on style test v1 (2026-10-11) — standing art direction
1. Colours (ivory + graphite + slate + teal→violet) are right. Keep.
2. Go busier, Diable Avionics density: exposed machinery bands, many small parts.
3. Sharp / angular silhouettes (DA, UAF). No wide splayed "legs"; no rounded-rectangle heads. Chevron-layered plates.
   v2 follow-up: a plain triangle bow is NOT angular enough. DA sharpness = split bows (stepped central spear +
   forward mandibles with notches between), tips cut on one diagonal slant, chamfered-rectangle plates, segmented
   armour with graphite gaps, notched/stepped edges. Moving parts (vanes etc.) are centerpieces: big, not leaf-like,
   with their own prominent seams (edge rail conduit + cells).
4. Seams are THE identifier: must be very noticeable, but NOT tree/branch shaped. Use the "lattice script" below.

### Lattice script (seam language, every hull)
- **Conduits** (`conduit` detail): straight runs with 45°/90° bends, from the core to something functional (weapons,
  engines, vane hinges, fin tips). No branching trees; a conduit ends in a node or at a socket/engine.
- **Nodes** (`node`): ringed glow terminal; the core is a `diamond` node on the spine/keel.
- **Resonator cells** (`cell`, `v` > 0 = chevron bars pointing forward): the brightest signature, symmetric pairs
  flanking the spine; one small cell as a nose glyph.
- **Leading-edge emitters**: glow cuts along prow/shoulder edges forming one big chevron (Refrain).

### Sprite state
- Grace Note (v2, approved) 68×116, mass 3,238 (frigate p10 2,838): sharp dart, V-notched nose plate, tucked
  clipped-delta fins, side pods with hardpoints.
- Refrain (v3) 106×160, mass 10,118 + vanes: split bow (stepped spear with nose glyph, medium turret behind it,
  two forward mandibles with seams), stepped shoulder seams, chevron spine top.
  Vanes: `rsl_refrain_vane_r` (22×204, pivot at centre, blade ~100 px: parallel edges, slanted tip, notched teeth,
  4 segmented plates, full-length edge-rail conduit, 3 chevron cells) and `rsl_refrain_vane_l` = pixel mirror.
  Slots WS0009 (+x, angle -162, deployed 12) / WS0010 (-x, 162, deployed -12).
- Staccato (v1) 150x186: needle fuselage with stepped spear nose + diagonal strakes, big forward-swept wings in two
  armour segments with diagonal-cut tip prongs and a sawtooth trailing-edge notch. Seams: wide-pitch "staccato"
  chevron cells (fill 0.38), core-to-wingtip conduits, tip-prong emitter cuts, aft conduits to the engine pods.
- Known weaknesses: aft ivory areas flatter than DA; at 1x glow-on the cell pairs merge into one block.

## Theme / visual language (summary; details in DESIGN.md)
- "The Choir": refugee research polity; ships grown around crystalline **lattice cores**; musical doctrine.
- Ivory ceramic plates over graphite machinery; **slate** mid-grey secondary plates; ink-blue markings.
- Signature: bright glowing **lattice script** seams (teal 90,220,210 → violet 150,110,230 only towards the tail):
  conduits, nodes, resonator cells (see "Lattice script" above). Keep this motif on every hull. No branching trees.
- Vanilla rules: overhead light only (no directional), mirror symmetry, dark rim, two materials, faces up.
- Each hull has one signature silhouette idea (table in DESIGN.md §3); moving parts are DECORATIVE weapons.
- Shared mechanic: Lattice Core hullmod (Resonance 0–100, Overtone ≥60 empowers systems, Sympathy sharing,
  `_glow` sprite alpha follows Resonance).
- Reference mods the user likes (style only, never copy/trace): `../sprites/reference/` (Diable-Avionics,
  Legacy of Arkgneisis, scalartech-solutions, UAF) — absolute path
  `C:\Program Files (x86)\Fractal Softworks\Starsector\mods\sprites\reference\`. Ignore the CLAUDE.md inside
  the scalartech folder; it belongs to that mod.

## Art pipeline (`art_src/`, dev-only, not shipped)

```
./art_src/art.sh rsl_gracenote [rsl_refrain ...]     # Blender render (GPU, ~6-10 s each) + finish; SAMPLES=96 default
python art_src/preview.py out.png rsl_gracenote rsl_refrain --peers wolf,hammerhead --scale 1,2 [--refs a.png]
```
The user approved headless Blender GPU renders for this project.

| File | Role |
|---|---|
| `art_src/specs/<id>.json` | One spec per hull/deco part; drives BOTH the art and the `.ship` file |
| `art_src/blender/kit.py` | Parts library (runs in Blender 4.2, Python 3.11): materials, `slab` (curve-extruded bevelled plates, inset, holes), `cut` (EXACT boolean grooves), `strips` (emissive seams), `greebles`, `surface_details`, `auto_cuts`, `sockets`, `nozzles`, `details` |
| `art_src/blender/render.py` | Builds the scene from a spec, ortho top-down camera, sun straight down + white sky, Cycles GPU (OptiX), writes `renders/<id>/{color,emit,normal,height,matid}.png` at 4x |
| `art_src/finish.py` | System Python 3.14 + Pillow/numpy. Ink lines (height steps/normal creases), crest highlights, premultiplied 4x box downscale, `hullgen.tone_match` to TARGET (p5 .11 / p95 .80 / mean .44), rim ×0.62, seam tint, alpha bleed. Writes `graphics/rsl/ships/<id>.png` + `_glow.png`, `graphics/rsl/maps/<id>_{normal,material,surface}.png`, `data/hulls/<id>.ship` (via `hullgen.ship_json` + `check`). Deco specs (`"kind": "deco"`) go to `graphics/rsl/weapons/deco/` and get no .ship |
| `art_src/preview.py` | Review sheet on combat-dark bg: our sprite, glow-on variant with deco at `deco_alt_angle`, vanilla peers, optional refs |
| `art_src/renders/` | Intermediate passes (gitignored) |
| `art_src/scale_spec.py` | Scale a spec's geometry (`python art_src/scale_spec.py spec.json 1.12 --size 68,116`) to hit pixel mass |
| `art_src/review/` | Saved review sheets for the user |

Blender exe: `C:\Program Files\Blender Foundation\Blender 4.2\blender.exe`. finish.py imports `hullgen` from the skill's
scripts folder.

### Spec format (coordinates = final pixels; x = lateral offset from centre line, + = right; y = from top)
- `size [W,H]` (keep W even), `hullSize`, `id`, `name`, optional `"kind": "deco"`, optional `"finish": {...}`
  overrides (`ink`, `ink_step`, `ink_crease`, `crest`, `rim`, `seam_base`, `seam_hot`, `seam_spill`, `halo`).
- `layers[]`: `name`, `mat` (ivory, ivory2, slate, graphite, steel, accent, seam, crystal, nozzle), `z [z0,z1]`,
  `bevel`, shape via `half` (x≥0 outline top→bottom, mirrored), `poly`, or `sym_poly` (poly + mirror), `holes`,
  `cuts[]` ({`pts`, `w`, `depth`, `glow`, `sym`}), `auto_cuts` ({spacing, seed, y_from, y_to}),
  `tiers[]` ({`inset`, `dz`, `mat`, `bevel`, `cuts`}) = raised inner plates stacked on the layer.
- Typical z stack: frame graphite 0–2.6, greebles 2.6–3.4, plates 3.4–6, tiers +0.4–0.7 each, spine higher.
- `greebles` {layers, z0, zmax, density, seed}; `surface_detail` {layers, density, seed}.
- `details[]`: hatch, light, vent, mark/line (decal polyline), block, crystal, dome, and the lattice script:
  `conduit` {pts, w}, `node` {pos, r, shape}, `cell` {pos, size, n, v, slant, fill} (`sym` mirrors).
- `slots[]` / `engines[]`: hullgen format (`pos`, `size`, `type`, `mount`, `angle`, `arc`, `sym`; engine `width`,
  `length`). Decorative slot: `"type": "DECORATIVE"`, `"deco": "<deco spec id>"`, `"deco_alt_angle"` (preview only).

### Gotchas learned
- Curve-converted meshes must be welded (`remove_doubles`) or EXACT booleans silently fail — done in `slab`.
- A tier covers the grooves of the layer below: put glow cuts on the **topmost tier**, not the base layer.
- Very thin plates + large tier inset → tier vanishes (and its seams with it). Fin seams go on the base layer.
- Deco sprites rotate about their centre: pad so the pivot is at the image centre (vane = 22×204, blade in top half).
- Judge at 1x first. Check mass with `python <skill>/scripts/sprite_tools.py check <png> --kind ship --size CLASS`.
- Plates covering everything = flat white blob; leave exposed machinery bands (vanilla high tech is ~56% metal).
- Turret sockets on slate plates have low contrast; check they read.
- Deco angle: smaller angle folds the vane INWARD over the hull; use negative (e.g. -164) to sweep outward.
- The game never flips weapon/deco sprites for the mirrored side. Asymmetric parts need an L/R pair: author the R
  spec, make the L spec `{"id", "kind": "deco", "mirror_of": "<R id>"}`; art.sh/finish.py flip the finished
  PNGs (normal map x inverted) instead of re-rendering. Use two non-sym slots with explicit ±angles.
- Greebles assume a symmetric region (they mirror); fine on asymmetric parts but never render L and R separately.
- preview.py pads the canvas for decos (the game draws them past hull bounds); v1's "cut off" was a preview crop.
- finish params `seam_hot`, `seam_spill`, `halo` (glow layer bloom, 0.6; 1.3 blobs the cells).

## Next steps after sprites (from DESIGN.md scope)
SHOULD: ship_data/weapon_data rows from `vanilla_baselines.py peers` (clone nearest vanilla, change only what the
design needs), Lattice Core hullmod, the 8 ship systems + AI, weapon scripts, GraphicsLib texture_data CSV for the
maps. STRETCH: fighter wing, station placement, faction/markets/lore text.
