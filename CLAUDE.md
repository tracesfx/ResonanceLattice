# Resonance Lattice — Starsector 0.98a faction/ship mod

Ship-focused faction mod. Mod id `resonance_lattice`, id prefix `rsl_`, Java package `rsl` (`RslModPlugin`, `RslIds`).
Deps: LazyLib, MagicLib (hard); GraphicsLib optional (guard with `isModEnabled("shaderLib")`).
Use the **starsector-modding** skill (`~/.claude/skills/starsector-modding/`) for all data, code, balance and validation.
Never launch the game or edit vanilla / other mods without the user's explicit OK.

**Full approved design proposal: `DESIGN.md`** (theme, all 8 hulls with systems/mechanics, weapons, art plan, scope,
risks). Read it before designing or drawing anything. Names are placeholders; lore will rename them later.

## Status (2026-10-11)

- Stage 1 (proposal): done, approved.
- Stage 2 (prototype sprites): **style test done, waiting on user feedback.** Grace Note (frigate) and Refrain
  (destroyer + vane deco) are rendered. Review sheet: `art_src/review/styletest_v1.png`.
- The user has feedback ready; apply it to the kit/finish/specs, re-render both, then continue in order:
  Staccato → Cadence → Tremolo → Conductor → Halo → Cantor Array (station last).
- Data (ship_data/weapon_data rows), hullmods, systems and Java code are NOT started (next stage after sprites).
- Build: `./build.sh` → 0 errors. Expected warnings only: scaffold TODO placeholders, `.ship` files without
  ship_data.csv rows, unreferenced glow/map/deco assets.
- git: commits on `master`. End commit messages with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

### Questions put to the user after the style test (answers pending)
1. Overall direction: ivory + graphite + teal branching seams — right, or greyer/more muted, more saturated, darker?
2. Detail density: keep clean/modern, or push towards DA/vanilla busy machinery?
3. Shapes: Grace Note silhouette OK? Refrain's crescent bow + vanes direction OK, or more angular?
4. Seams: brightness, amount, keep the teal→violet gradient?

### Known weaknesses of the current sprites
- Cleaner/sparser than vanilla; vanilla has denser machinery and more articulation.
- Refrain still reads somewhat boxy (rounded rectangle) at 1x.
- Pixel mass: Grace Note 3,084 (frigate p10 2,838 / median ~4,300–5,300); Refrain 9,642 (destroyer p10 ~11,000;
  folded vanes add ~2,400 on screen).

## Theme / visual language (summary; details in DESIGN.md)
- "The Choir": refugee research polity; ships grown around crystalline **lattice cores**; musical doctrine.
- Ivory ceramic plates over graphite machinery; **slate** mid-grey secondary plates; ink-blue markings.
- Signature: thin glowing **lattice seams** (teal 90,220,210 → violet 150,110,230 only towards the tail) that
  **branch like crystal growth** off a main seam (see Grace Note / Refrain aft seams). Keep this motif on every hull.
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
| `art_src/review/` | Saved review sheets for the user |

Blender exe: `C:\Program Files\Blender Foundation\Blender 4.2\blender.exe`. finish.py imports `hullgen` from the skill's
scripts folder.

### Spec format (coordinates = final pixels; x = lateral offset from centre line, + = right; y = from top)
- `size [W,H]` (keep W even), `hullSize`, `id`, `name`, optional `"kind": "deco"`, optional `"finish": {...}`
  overrides (`ink`, `ink_step`, `ink_crease`, `crest`, `rim`, `seam_base`).
- `layers[]`: `name`, `mat` (ivory, ivory2, slate, graphite, steel, accent, seam, crystal, nozzle), `z [z0,z1]`,
  `bevel`, shape via `half` (x≥0 outline top→bottom, mirrored), `poly`, or `sym_poly` (poly + mirror), `holes`,
  `cuts[]` ({`pts`, `w`, `depth`, `glow`, `sym`}), `auto_cuts` ({spacing, seed, y_from, y_to}),
  `tiers[]` ({`inset`, `dz`, `mat`, `bevel`, `cuts`}) = raised inner plates stacked on the layer.
- Typical z stack: frame graphite 0–2.6, greebles 2.6–3.4, plates 3.4–6, tiers +0.4–0.7 each, spine higher.
- `greebles` {layers, z0, zmax, density, seed}; `surface_detail` {layers, density, seed}.
- `details[]`: hatch, light, vent, mark/line (decal polyline), block, crystal, dome (`sym` mirrors).
- `slots[]` / `engines[]`: hullgen format (`pos`, `size`, `type`, `mount`, `angle`, `arc`, `sym`; engine `width`,
  `length`). Decorative slot: `"type": "DECORATIVE"`, `"deco": "<deco spec id>"`, `"deco_alt_angle"` (preview only).

### Gotchas learned
- Curve-converted meshes must be welded (`remove_doubles`) or EXACT booleans silently fail — done in `slab`.
- A tier covers the grooves of the layer below: put glow cuts on the **topmost tier**, not the base layer.
- Very thin plates + large tier inset → tier vanishes (and its seams with it). Fin seams go on the base layer.
- Deco sprites rotate about their centre: pad so the pivot is at the image centre (vane = 20×152, blade in top half).
- Judge at 1x first. Check mass with `python <skill>/scripts/sprite_tools.py check <png> --kind ship --size CLASS`.
- Plates covering everything = flat white blob; leave exposed machinery bands (vanilla high tech is ~56% metal).
- Turret sockets on slate plates have low contrast; check they read.

## Next steps after sprites (from DESIGN.md scope)
SHOULD: ship_data/weapon_data rows from `vanilla_baselines.py peers` (clone nearest vanilla, change only what the
design needs), Lattice Core hullmod, the 8 ship systems + AI, weapon scripts, GraphicsLib texture_data CSV for the
maps. STRETCH: fighter wing, station placement, faction/markets/lore text.
