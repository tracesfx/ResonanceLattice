# Resonance Lattice — Campaign Roadmap (factions, sector, quests, secrets)

Written 2026-10-12, after the ships-and-weapons build (DESIGN.md §6 MUST + SHOULD) was finished and balanced.
This file plans everything DESIGN.md left as STRETCH: faction, markets, lore, station placement, the Virtuoso
questline and exploration content. Each stage ends with `./build.sh` at 0 errors, a commit, CHANGELOG/README
updates, the new insights added to the starsector-modding skill, and an in-game checkpoint for the user (campaign
content is far harder to verify statically than combat content).

## Where we start (asset review)

| Area | State | Gap for the campaign |
|---|---|---|
| Hulls | 9 hulls + Unsung + Cantor station (core, ring, 3 modules), 2 presets each, balanced | Cantor is only reachable in a mission: no station industry, no market |
| Weapons / wings | 12 weapons, Sforzando x2, 3 wings, all `rsl_bp`-tagged | No blueprint package item; Choir knows them only via tags |
| Faction | `rsl_choir.faction` = Tri-Tachyon clone (ranks "CEO", tritach music, corporate portraits), doctrine set, `default_ship_roles.json` presets | No relations, no markets, no Nexerelin config, no ship-name list of its own, no illegal commodities, generic sell lists |
| Code | `RslModPlugin` loads GraphicsLib maps only; no `onNewGame`/`onGameLoad`; nothing saved | Worldgen, campaign scripts, rule commands, intel, XStream aliases all missing |
| Text | 84 description rows; one-line FACTION blurb; DESIGN.md §1 lore seed (refugee polity, Domain harmonic-flux lab) | No history, places, people or names (all names are placeholders) |
| Virtuoso | Both stages built, uniqueness tags in place; Concert Pitch augment exists as a hullmod | Grant, upgrade (hull swap), `$rsl_virtuosoGranted/Upgraded` flags, quest |
| Environment | Nexerelin, LunaLib, MagicLib (bounties), Console Commands installed | — |

## Decisions (user, 2026-10-12)

- **Scale: small enclave.** One home system, 2-3 markets, the Cantor Array guards the capital.
- **Nexerelin: full support** (playable faction, diplomacy, invasions, random-sector placement, start options),
  loaded only when Nex is present.
- **Naming: final names now**, in Stage 1 (I propose 2-3 options, the user picks); ids stay `rsl_*`.
- **Virtuoso questline: medium, 5-6 beats** (find the Unsung, 3-4 middle beats with one meaningful choice, a boss
  fight near the end, then the completion/upgrade).

## Stage 1 — Lore bible and campaign design (docs only, no code) — DONE (CAMPAIGN.md v2, 2026-10-12)

Goal: one approved document, `CAMPAIGN.md`, that every later stage implements. Cheap to iterate; renaming a quest
after it is built is expensive.

1. **Naming pass.** Final display names for the faction, hulls, weapons, systems, hullmods (ids stay `rsl_*`, only
   names/descriptions change). 2-3 options per name where it matters; user picks.
2. **History.** The Domain harmonic-flux lab, the Collapse, the Choir's flight, how they survive now, what lattice
   cores are, why the Virtuoso was built and why its chorus died. Tie-ins to vanilla lore (Domain, Persean
   League, Tri-Tachyon, Luddic Church/Path, Remnants) without contradicting it.
3. **Place in the Sector.** Disposition and relations table vs every vanilla faction (and the reasons); territory
   (home system, markets, sizes, industries, the Cantor Array as the capital's station); where it sits on the map.
4. **People.** Faction leader, a quest giver, an antagonist, 2-3 named contacts (vanilla portraits until custom ones
   exist).
5. **Questline beat sheet (the Virtuoso).** Start trigger, each beat (place, dialog, combat, choice), the Unsung
   grant, the upgrade beat, rewards, fail/fallback paths (lost or sold Unsung), and the lifecycle table for every
   quest-critical entity (skill rule 6).
6. **Secrets catalogue.** Hidden sites, collectibles, rare drops, a secret encounter/boss, easter eggs: what the
   player finds, how, and what it pays.
7. **Ambient content.** Choir fleet behaviours, encounter dialog flavour, MagicLib bounties, market services.
8. **Compatibility decisions.** Nexerelin (playable faction, invasions, random-sector placement), existing saves.

Exit: user approves CAMPAIGN.md; DESIGN.md and CLAUDE.md point to it.

## Stage 2 — Faction foundation — DONE (2026-10-12; relations in `rsl.world.RslRelations`, data in `tools/campaign_data.py`)

- Rewrite the faction in `gen_data.py`: own ranks and posts (musical titles), name lists, portraits (vanilla subset
  for now), music choice, doctrine, known/priority weapons, hullmods and fighters, sell frequencies, illegal
  commodities, `internalComms`, a richer FACTION description.
- Rename pass: "Choir" -> "the Cantorate" in every display string, Halo -> Fermata, Stillwater Halo -> Fermata
  Field (gen_data + descriptions; ids unchanged).
- **Pitch Glass** commodity (`rsl_pitchglass`, commodities.csv, non-economy) + icon.
- Blueprint package special items (hulls / weapons / wings), sold only for Pitch Glass.
- Relations applied in worldgen (`SectorAPI` faction relationships, set once, idempotent).
- Nexerelin config `data/config/exerelinFactionConfig/rsl_choir.json` (playable, alignments, start fleets from the
  presets, invasion/diplomacy traits) — only loaded by Nex, so no hard dependency.
- Validator: faction knows every weapon/wing its role variants use (already checked), new files clean.

## Stage 3 — Home in the Sector (worldgen)

- `rsl.world.RslWorldGen`: home star system per CAMPAIGN.md (star, planets, jump points, hyperspace clearing,
  market conditions, industries, submarkets, admin and important people), created in `onNewGame` and, behind a
  sector memory flag, in `onGameLoad` for existing saves.
- **Cantor Array in the campaign:** a station industry (`industries.csv` + an `OrbitalStation` subclass) that
  spawns the Cantor Array as the capital's defence station (vanilla pattern: `orbitalstation_high` etc.).
- Military base → Choir patrols spawn through vanilla market fleets (no custom fleet manager needed).
- Nexerelin random-sector: home market spawn data in the Nex config; worldgen skips itself when Nex says so.
- Save compatibility: `configureXStream` aliases for every saved class from here on.

## Stage 4 — Ambient campaign life

- Encounter dialog flavour for Choir fleets (rules.csv greetings per relation, "tuning" lines).
- MagicLib bounties (`data/config/modFiles/magicBounty_data.json`): 2-4 bounties fighting or featuring the Choir.
- **Pitch Glass economy:** salvage drops from Lattice ships, Cantorate bar missions, AI-core silencing and
  colony-item turn-ins (CAMPAIGN.md §8).
- **The Luthier's Workshop:** a dialog shop at Coda priced in Pitch Glass (blueprints, Concert Pitch, Pulsar
  Metronome colony item, Lattice Tuning; Virtuoso items unlock in Stage 5).

## Stage 5 — The Virtuoso questline

- Quest state machine in sector memory (`rsl.campaign.VirtuosoQuest`, stages as strings), intel plugin, rule
  commands, rules.csv dialogs (generated from Python like the rest of the data), custom entities for quest sites.
- The Unsung grant (exactly once, `$rsl_virtuosoGranted`), the upgrade via `setHullSpecAPI` + built-in swap
  (`$rsl_virtuosoUpgraded`), with the rebuild-and-copy fallback (DESIGN.md §3.9); completion paid in Pitch Glass.
- Three hard boss fleets (derelict defences, Special Projects, the Hush): S-mods, level-7 elite officers, the
  Dead Chorus fleet hullmod, violet Hush glow recolour; Unbound Core + Chorus/Solo Movements in the Workshop.
- Pacing target ~30 minutes of play (CAMPAIGN.md §6).
- Every quest-critical entity: story-critical + no-decivilization until the quest ends; every dialog option has a
  handler and a way back (validator checks rules).

## Stage 6 — Secrets and exploration

- Hidden sites and collectibles from the catalogue (procgen-placed derelicts/lab stations in random systems,
  salvage that drops Choir blueprints or lore fragments as intel).
- Concert Pitch as an obtainable rare item (it is described as a rare augment).
- Venn's Rest and the unique officer **Concertmaster Odile Marchetti** with the custom fleet-wide skill.

## Stage 7 — Polish, review, release

- Optional LunaLib settings (quest/boss toggles), guarded.
- README (spoiler-free), CHANGELOG, CREDITS, version bump.
- Independent review with `templates/REVIEW_PROMPT.md` (only if the user allows a subagent), fixes, re-review.
- `package_mod.py --strict`; user runs `templates/SMOKE_TEST.md` + `log_scan.py --mod .`.

## Risks

- **Nothing campaign-side has ever run in game.** Worldgen, rules dialogs and hull swaps fail at runtime, not at
  build time. Mitigation: small stages, an in-game checkpoint after each, `log_scan.py` after every session.
- **Hull swap (Unsung → Virtuoso) is unverified** (built-ins and deco slots after `setHullSpecAPI`). Prototype it
  early in Stage 5 with a console-triggerable rule command.
- **Station industry for the Cantor Array** (multi-module station as a market station) is the riskiest data wiring;
  copy vanilla's station industries exactly.
- **Nexerelin** can place or remove the faction in ways a fixed worldgen does not expect; every script must cope
  with the home market being gone or owned by someone else.
- **Portraits/illustrations** have no good generator: vanilla portraits until the user decides otherwise.
