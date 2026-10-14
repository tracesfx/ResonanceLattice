# Resonance Lattice — Campaign Bible (Stage 1, v2, 2026-10-12)

Status: **v2, approved direction.** User decisions so far:
- faction = **the Cantorate** (of Vell); Halo -> **Fermata**; all other names kept; names in §2d are fine and may be
  refined while writing;
- the Virtuoso's original name = **Lacrimosa**;
- waking the Lacrimosa drops the fleet's CR to 30%; the Hush boss reuses the existing hulls with a violet recolour;
- **Unbound Core is core to the Virtuoso's gameplay**: it must not hinge on a quest choice (§6, beat 4; §8);
- secret #5 rewards a **unique officer with a fleet-wide special skill** (§7, §9);
- the musical motif must be **purposeful in Starsector's dystopian Sector**, not decoration (§1);
- the questline takes **~30 minutes of play**, not 10 (§6 pacing table);
- **boss fights are genuinely hard**: S-modded high-quality ships, maxed officers (§6 boss specs);
- **Virtuoso upgrades are extremely expensive**, paid in a faction currency, **Pitch Glass**, that also buys
  exclusive items (§8).

Ids never change (`rsl_*`, faction id `rsl_choir`); only display names and text do.

---

## 1. Why music: the purpose of the motif

The Sector is a dying machine. The Gates are dark, Domain databanks rot, AI cores are banned and feared, comms are
jammed and spoofed in every war, and every polity survives on salvage it no longer understands. The Cantorate's
music is not art. It is **the only technology they still fully own**, and every musical word in the faction names a
working part of a survival system:

1. **A network that cannot be hacked, jammed or banned.** Lattice cores lock to each other's pitch over a distance.
   A Cantorate fleet coordinates *by resonance*: no comm traffic to intercept, no AI core to outlaw, nothing for a
   Hegemony inspector to confiscate. In a Sector of electronic warfare and AI paranoia, a choir is the most secure
   battle-network there is. (Sympathy, Overtone and the Conductor's Bridge are this network in combat.)
2. **The score is the manual.** The refugees lost their databanks in the flight. What survived was what people
   could memorise: the tuning protocols, encoded as **scores** — sequences of pitches that tell a crew how to grow,
   calibrate and repair a core. Every Cantorate engineer is trained by ear. A "Lost Score" is lost engineering.
3. **Tuning is labour.** A core holds its pitch only while people hold it with it: crews hum calibration tones
   through long shifts, wired to the core through bone-conduction collars. Choristers are workers. Hearing loss,
   "pitch fatigue" and burnt-out tuners are the price of every Cantorate hull. The cores take endurance from the
   people around them — the same thing Stolen Time does to enemy crews, and the same thing the Lacrimosa did to its
   own.
4. **Harmony is politics.** A ship that disagrees with its fleet literally drifts out of tune and weakens the whole
   network. The Cantorate's consensus government is its fleet doctrine: the Precentor sets the reference pitch,
   broadcast from Tacet Station, locked to Vell's pulsar. Dissent is a technical fault. That is the Cantorate's
   quiet tyranny, and why the taboo against the solo voice is enforced so hard.
5. **The pulsar is the clock.** Crystals only grow true to a pulsar's beat, so the Cantorate cannot leave Vell.
   Their whole existence depends on one dead star nobody else wanted — and on nobody taking it from them.

**The one idea: "No voice sings alone."** A lattice core grows stronger in company and *hungry* alone. The
Cantorate's founding trauma is the one time a core sang alone: the Lacrimosa drained its own chorus to death. The
questline asks the player — an outsider, a soloist by nature — whether to finish it anyway, in a Sector where the
collective is a survival mechanism and also a cage.

---

## 2. Naming pass

### 2a. Faction (picked)
**The Cantorate of Vell** ("the Cantorate"). Its people are **Choristers**; a Cantorate fleet is **a choir**; the
fleet-wide network is **the chorus**.

### 2b. Ranks and posts (vanilla `ranks` / `posts` keys)

| Key | Name | Note |
|---|---|---|
| factionLeader | **Precentor** | sets the reference pitch for the whole polity |
| spaceAdmiral | Maestro | conducts a fleet |
| spaceCommander | Principal | first chair of a squadron |
| spaceCaptain | Chorister | |
| spaceLieutenant / spaceSailor | Cantor / Voice | |
| ground ranks | Warden of the Score, Keeper | |
| post administrator | Cantor-Steward | |
| post stationCommander | Keeper of the Array | Cantor Array commander |
| custom post | **Luthier** | ship designers; a luthier builds string instruments |

### 2c. Ships, weapons, systems, hullmods

| Id | Name | Note |
|---|---|---|
| rsl_halo | **Fermata** | was Halo; 𝄐 = an arc over a dot = the ring round the core; means "hold" |
| rsl_stillwater | **Fermata Field** | was Stillwater Halo |
| everything else | unchanged | Grace Note, Refrain, Staccato, Cadence, Tremolo, Conductor, Virtuoso (+ Unsung), Cantor Array (+ Spire, Bell, Choir Loft), Trill, Cadenza, Requiem, all weapons, systems and hullmods |

### 2d. Places, people, things

| Thing | Name |
|---|---|
| Home system | **Vell** (a pulsar) |
| Capital (cold moon of a gas giant) | **Coda** |
| Gas giant | **Basso** |
| Crystal nursery moon | **Glasshouse** |
| Pulsar listening station | **Tacet Station** (tacet = "the part is silent") |
| The Domain lab | **the Antiphon Institute** |
| The Virtuoso's original name | **the Lacrimosa** ("weeping"; from the Requiem mass) |
| Its dead escort fleet | **the First Chorus**; what remains of it: **the Hush** |
| The currency | **Pitch Glass** (§8) |
| The questline | **"Lacrimosa"** |

---

## 3. History

**c-40s (late Domain).** The Domain's **Antiphon Institute**, a hyperspace-physics lab on the then-frontier,
studies *harmonic flux*: the way hyperspace storms ring like struck metal. Its researchers learn to grow **lattice
crystals** to a pulsar's beat. A grown core turns stress (flux, impacts) into stored resonance, and cores near each
other fall into step and share it. A core is **not** an AI: it has no will, only a pitch. (The Hegemony will never
quite believe that.)

**The Virtuoso program.** The Domain Navy funds one question: can a single core carry a whole chorus? The Institute
builds the **Lacrimosa**, a duelist capital around an enormous core meant to conduct twelve escorts, the First
Chorus.

**The Collapse.** The Gates go dark. The Institute is cut off with its staff, their families and a few hundred navy
crew. No relief comes.

**The Hush (c+3).** A raider fleet finds the Institute. Director **Saskia Venn** orders the untested Lacrimosa core to
conduct the First Chorus at full voice. It works, and then it does not stop: the core pulls the resonance — and the
readiness, the crews' endurance, the reactor margins — out of all twelve escorts to keep singing. The raiders die.
So does the First Chorus: twelve ships adrift, crews dead at their collars, cores still ringing in silence. Venn
shuts the Lacrimosa down with her own hands and disappears.

**The flight (c+3 to c+25).** The survivors abandon the Institute and wander as a refugee fleet, selling
core-tuning to anyone who pays, losing their databanks piece by piece and keeping their knowledge alive as memorised
scores. Doctrine is born from the Hush: **no voice sings alone.**

**The Cantorate (c+25 to now).** The fleet settles at **Vell**, a pulsar nobody wanted. Coda is a cold moon of the
gas giant Basso; Glasshouse grows the crystal; Tacet Station broadcasts the reference pitch. Small, poor in
everything but crystal, superb shipwrights, under constant pressure: the Hegemony inspects their cores for AI,
Tri-Tachyon wants to buy or steal the tech, the Luddic Path calls it machine-worship.

**Now (c+206).** The Lacrimosa is a children's warning. The Institute's location was deliberately forgotten.

---

## 4. The Cantorate in the Sector

### Relations (start values; applied once in worldgen)

| Faction | Start | Why |
|---|---|---|
| Independent | +0.30 favorable | trade partners; many independents hire Cantorate tuners |
| Persean League | +0.20 welcoming | took in refugees during the flight; likes small autonomous polities |
| Sindrian Diktat | 0 | buys crystal, asks no questions |
| Tri-Tachyon | -0.20 suspicious | has tried to buy and to steal lattice tech |
| Hegemony | -0.30 suspicious | treats lattice cores as unlicensed AI-adjacent tech; inspections |
| Luddic Church | -0.20 suspicious | machine-voices singing in the dark |
| Luddic Path | -0.60 hostile | heresy |
| Pirates, Remnants, Derelict, Omega, Threat, Dweller | hostile | vanilla default |

### Territory (small enclave): **Vell**, a pulsar on the fringe
Placed by a free-spot search outside the Core (checked against the vanilla map in Stage 3). Two jump points.

| Market | Size | Type | Industries / conditions | Notes |
|---|---|---|---|---|
| **Coda** (capital) | 5 | cold moon of Basso | Population, Megaport, Military Base, Orbital Works, Refining, **Cantor Array** (station industry) | Precentor, Luthier Abelard, the Luthier's Workshop (§8) |
| **Glasshouse** | 4 | crystal moon | Population, Mining, Patrol HQ, **Lattice Nurseries** (custom condition) | the crystal source; Path raid target |
| **Tacet Station** | 3 | orbital station near the pulsar | Population, Waystation, Orbital Station; research flavour condition | Archivist Tanh; the reference-pitch broadcaster |

Vanilla market fleets provide patrols, traders and smugglers. Lattice hulls appear in the Cantorate's military
submarket; blueprints are never sold for credits (only for Pitch Glass, §8).

### Doctrine (kept)
Warships 5 / carriers 1 / phase 1, ship quality 5, ship size 4, aggression 2, officer quality 1. Fleets use the 18
preset loadouts.

---

## 5. People

| Person | Post | Where | Role |
|---|---|---|---|
| **Precentor Ilian Okoro-Vass** | factionLeader | Coda | careful, keeps the taboo; decides beat 4 |
| **Archivist Mireille Tanh** | contact (science) | Tacet Station | quest giver; keeps the forbidden records of the Hush |
| **Luthier Corvin Abelard** | contact (military) | Coda | best shipwright alive; runs the Luthier's Workshop; wants the Lacrimosa finished |
| **Director Hale Sung** | Tri-Tachyon antagonist | roams | Special Projects; wants the core, not the ship |
| **Saskia Venn** | — | dead; logs | built the Lacrimosa; her logs are the Lost Scores |
| **Concertmaster Odile Marchetti** | unique officer | Venn's Rest | Venn's first chair, alive in cryosleep (§7 #5, §9) |

Portraits: vanilla portraits until custom ones exist.

---

## 6. The Virtuoso questline: "Lacrimosa" (6 beats, ~30 min)

### Pacing (play time, excluding Pitch Glass earning for beat 6)

| Beat | What fills the time | Est. |
|---|---|---|
| 1 Static in the Score | 3 buoys in 3 different fringe regions (long hyperspace legs), a scan + short dialog each | 7 min |
| 2 The Antiphon | travel to a deep-fringe system, a hard fight, a long dialog | 6 min |
| 3 A Rival Bid | Sung's offer, then a hard pursuit fight that can catch you anywhere within 30 days | 4 min |
| 4 The Council | travel to Vell, council dialog, choice; then fetch Tacet Station's pulsar recording | 4 min |
| 5 The Hush | find the graveyard (3 sensor sweeps in an abyssal hyperspace region), boss fight | 8 min |
| 6 Lacrimosa | return to the Institute, pay, completion dialog | 2 min |
| | | **~31 min** |

### Beat 1 — "Static in the Score"
- **Trigger** (any one): a bar event at any Cantorate market (Archivist Tanh; player level ≥ 8 *and* fleet ≥ 80 DP,
  so it starts mid-game); the first Lost Score salvaged anywhere; a Nexerelin Cantorate start (Tanh contacts the
  player once the level gate is met).
- Tanh has heard the Lacrimosa's core waking: a faint pulsar-locked signal in hyperspace. She cannot tell the
  Precentor (the taboo). She asks the player to triangulate it from **3 old Institute listening buoys** (custom
  entities in deep hyperspace near 3 fringe systems far apart). Each buoy: approach, scan (a short dialog with a Venn
  log excerpt), and the intel narrows the search. The last buoy is watched by a pirate scavenger fleet (medium fight).
- Exit: the Antiphon Institute's system is revealed.

### Beat 2 — "The Antiphon"
- The Institute (custom entity, story-critical) in a procgen deep-fringe system, guarded by **Domain-era derelict
  defences**: a fixed-strength derelict fleet of ~180 DP (vanilla `derelict` hulls, no D-mods, 1 S-mod each). Hard
  for the level-8 player, beatable.
- Inside: Venn's last logs; the Lacrimosa dormant in its dock, plates missing, cores dark.
- **Waking costs every ship in the fleet down to 30% CR** (the core drinks to wake). The dialog warns first and
  lets the player leave and come back.
- The player gets the **Virtuoso (Unsung)**, named *Lacrimosa* (`$rsl_virtuosoGranted`). The dialog warns that it is
  unique and that selling or scuttling it is final (fallbacks below).

### Beat 3 — "A Rival Bid"
- On leaving, Director Hale Sung hails: he knows. Offer: **2,000,000 credits** + Tri-Tachyon reputation for the core.
  - **Sell:** quest ends (bad ending, warned twice). The Unsung is removed, credits and rep paid; the Cantorate
    (-15) learns of it. Epilogue intel.
  - **Refuse:** Sung sends a **Special Projects fleet** after the player within 30 days (boss spec below).
    Win to continue (fleeing keeps it hunting until defeated or 60 days pass, after which beat 4 opens anyway).

### Beat 4 — "The Council" (the choice)
- At Coda, the Precentor, Tanh and Abelard argue in council. The Cantorate learns what the player carries.
- The choice decides **how the Lacrimosa is retuned**, i.e. which **Movement** (a Virtuoso-only sidegrade hullmod,
  §8) the Workshop can build and how the Cantorate treats the player. **Unbound Core is NOT part of the choice**:
  both paths can buy it (§8), because it is central to the Virtuoso's gameplay.
  - **"Chorus"** (the Precentor): the Lacrimosa learns to sing *with* others. Cantorate rep +20; 10% Workshop
    discount; 2 Cantorate escorts (Refrain + Cadence, level-5 officers, S-modded) join for beat 5; Movement
    available: **Chorus Movement**.
  - **"Solo"** (Abelard): the Lacrimosa is finished as Venn designed it. Cantorate rep -10; no escorts; Abelard
    becomes a personal contact who keeps trading with the player at any rep above hostile; Movement available:
    **Solo Movement**.
- Then: Tanh needs Tacet Station's raw pulsar recording to tune the search for the graveyard (travel + dialog).

### Beat 5 — "The Hush" (boss)
- The graveyard lies in an **abyssal hyperspace pocket** (far out, beyond the Sector's edge): 3 sensor sweeps
  narrow it down, then twelve wrecks wake as the **Hush** (boss spec below).
- Reward: the Lacrimosa's **sash and vanes** (quest item), graveyard salvage, **150 Pitch Glass**, and Concert Pitch
  as a guaranteed drop.

### Beat 6 — "Lacrimosa" (completion)
- Return to the Antiphon Institute: only its dock can mount the sash. The completion **costs 600 Pitch Glass +
  3,000,000 credits** (the Workshop's Luthiers do the work there). The player can leave and come back with the
  price.
- On payment: the hull swap Unsung -> Virtuoso (`$rsl_virtuosoUpgraded`), CR to max, Bravura unlocked; the Unbound
  Core and the path's Movement become purchasable at the Workshop.
- Epilogue by path: *Chorus* — the Precentor names the player an honorary Maestro. *Solo* — Abelard: "Now it sings
  alone. Try not to let it get hungry."

### Boss specs (fixed strength, not scaled down)

All three use **no D-mods, 3 S-mods per ship** (built in through `addPermaMod(id, true)`), the best preset or a
hand-made boss variant, and officers **level 7 with every skill elite** (the strongest vanilla allows; exact cap
checked with `api_lookup` in Stage 5); the flagship commander gets maxed fleet skills. Fleets cannot be avoided by
transponder tricks, and the battle is "no retreat" where vanilla bosses use it.

| Fight | Composition (target) | DP | Special rule |
|---|---|---|---|
| Derelict defences (beat 2) | derelict Rampart/Bastillon-class drones | ~180 | none (warm-up), only 1 S-mod each, no officers |
| **Special Projects** (beat 3) | Tri-Tachyon: Paragon flagship, 2 Doom, 2 Harbinger, Aurora, 2 Medusa, 3 Afflictor/Shade, Tempest escorts | ~280 | phase-heavy; flagship commander with alpha-core-level skills |
| **The Hush** (beat 5) | 2 Conductor, 1 Fermata, 3 Cadence, 2 Tremolo, 2 Staccato, 2 Refrain + Trill/Requiem wings, "First Chorus" boss variants | ~330 | **Dead Chorus** fleet hullmod: when a Hush ship dies, its Resonance floods the others (they jump to Overtone and gain +10% damage per dead ship, up to +50%). Kill order matters; the Virtuoso's Stolen Time is the counter |

### Fallbacks and lifecycle (quest-critical entities)

| Entity | Destroyed / lost | Captured (Nex) | Save/load, mod added mid-game |
|---|---|---|---|
| Unsung (fleet member) | lost in battle: `always_recoverable`; sold/scuttled before beat 6: the Institute dock holds a spare frame — the completion then costs +1 story point and +1,000,000 credits and grants a fresh Virtuoso, once | n/a | flags re-checked on load |
| Antiphon Institute (custom entity) | story-critical, indestructible | n/a | created on beat 1, not at worldgen |
| Coda market (beat 4) | no-deciv until beat 4 is done | not Cantorate-owned: the council meets aboard a Cantorate fleet at another Cantorate market; no Cantorate markets: beat 4 resolves as "Solo" without the council | worldgen idempotent |
| Contacts | important people; if their market changes hands they move to another Cantorate market, else the beat runs from intel | same | |
| Special Projects fleet | despawns after defeat or 60 days; flags cleared on every exit path | | |
| Hush fleet | despawns after defeat; waits if the player leaves (no pursuit) | n/a | |

---

## 7. Secrets and exploration

| # | Secret | How it is found | What it pays |
|---|---|---|---|
| 1 | **The Lost Scores** — 8 Venn logs | salvaging Institute probes and caches in random procgen systems | lore intel + 15 Pitch Glass each; the first can start the quest; all 8 reveal #5 |
| 2 | **Silent wrecks** | derelict Grace Notes / Refrains (D-mods) in random systems | recoverable Lattice hulls early + salvage Pitch Glass |
| 3 | **The abandoned Array** | a derelict Cantor Array in one remote system, petals still firing (automated, 3 S-mods, hard) | Cantorate blueprint package + 100 Pitch Glass + Concert Pitch |
| 4 | **Full Chorus** | hinted by a Score | a fleet that deploys one of each of the 7 Lattice line hulls gets a "Full Chorus" battle bonus |
| 5 | **Venn's Rest** | all 8 Scores | hidden system; Venn's last log (the Hush was no malfunction: she tuned it that way to save the Institute's families); guarded by a sealed Hush remnant (smaller than beat 5, same rules); reward: **Concertmaster Odile Marchetti**, the unique officer (§9) |
| 6 | **The pulsar choir** | flying the Virtuoso through Vell's pulsar beam | an easter-egg line and a one-time CR refill |
| 7 | **The true name** | the Virtuoso named *Lacrimosa* | a unique line in its intel and description |

---

## 8. Pitch Glass: the Cantorate's currency

**What it is:** shards of lattice crystal grown true to Vell's pulsar, each carrying the reference pitch. The
Cantorate cannot buy crystal anywhere else, so it values Pitch Glass above credits: it is the only thing that can
retune a core. A cargo commodity (`rsl_pitchglass`), tagged non-economy so no market trades it for credits; only the
**Luthier's Workshop** and Cantorate dialogs accept it.

### Sources (starting values, tuned in Stage 4)

| Source | Amount |
|---|---|
| Salvaging after a battle with Lattice ships (hostile Cantorate, Discordant pirates, the Hush) | frigate 1 / destroyer 2 / cruiser 4 / capital 8 per ship destroyed; Hush ×3 |
| Tuners' Contracts at Tacet Station (hunt a pirate or Path raider fleet within 10 LY of Vell; one at a time, 30-day cooldown) | 20-40 per contract + credits |
| MagicLib bounties (§10) | 40-80 each |
| **Silencing AI cores** — the Cantorate quietly buys AI cores to destroy them (it keeps the Hegemony away) | gamma 5 / beta 15 / alpha 40; +Hegemony rep 1 per core |
| Domain-era special items turned in (the Cantorate needs their physics) | corrupted nanoforge 40, pristine nanoforge 150, synchrotron 80, other colony items 30-60 |
| Secrets (§7) | Lost Score 15 each, abandoned Array 100 |
| Beat 5 | 150 |
| Stipend at Cooperative rep | 10 per month |

### The Luthier's Workshop (Coda; Abelard; a dialog shop priced in Pitch Glass)

| Item | Price | Requires |
|---|---|---|
| **Completing the Lacrimosa** (beat 6) | 600 PG + 3,000,000 cr | beat 5 done |
| **Unbound Core** (installable on the Virtuoso) | 400 PG + 1,000,000 cr | the Virtuoso completed (either path) |
| **Chorus Movement** / **Solo Movement** (Virtuoso-only sidegrade hullmod, by path) | 300 PG | the Virtuoso completed |
| Cantorate blueprint packages: hulls / weapons / wings | 250 / 150 / 120 PG | Cantorate rep ≥ Favorable (any rep for Abelard on "Solo") |
| Concert Pitch augment (the hullmod is learned; any Lattice ship can mount it; it never drops) | 200 PG | Cooperative |
| **Pulsar Metronome** colony item (Waystation: +15% accessibility, +1 stability; +25% / +2 in a neutron-star system) | 250 PG | Cooperative |
| Lattice Tuning (30 days: the player fleet's Lattice ships gain Resonance 25% faster and lose it half as fast) | 15 PG | not hostile |
| Hush recolour of the Virtuoso's seams (cosmetic) | 50 PG | beat 5 done |

Total for a fully upgraded Virtuoso: **~1,300 Pitch Glass + 4,000,000 credits**, on top of the questline.

**Movements (sidegrades, not power creep):**
- **Chorus Movement:** CR the Virtuoso steals is shared: 50% of every steal also goes to allied ships within 1,500 u;
  the Virtuoso's own steal rate -25%.
- **Solo Movement:** +25% Stolen Time rate and +10% damage while no allied ship is within 1,500 u; -25% when one is.

---

## 9. The unique officer: Concertmaster Odile Marchetti

- Venn's first chair, found in cryosleep at Venn's Rest (§7 #5). Unique; level 7, every combat skill elite;
  personality steady. Cannot be an administrator.
- **Unique skill "Concertmaster"** (custom skill, cannot be removed or learned by others): while her ship is
  deployed, **every allied ship in the battle** gets +5% weapon damage, +10% flux dissipation and +10% faster CR
  recovery after battle; **Lattice ships** additionally gain Resonance 25% faster and share Sympathy at any range.
  (Numbers tuned in Stage 6.)
- Captaining the Virtuoso: one extra line in Bravura ("She is in tune at last.").

---

## 10. Ambient campaign content

- **Encounter dialog** for Cantorate fleets by relation ("You are out of tune, captain."); a Hegemony inspection
  hassle aimed at Cantorate traders (flavour).
- **MagicLib bounties** (3): *the Discordant* (a pirate lord flying stolen, mistuned Lattice ships; drops Pitch
  Glass); *Inspection Overreach* (a rogue Hegemony inspector harassing Vell); *Special Projects Remnant* (after beat
  3).
- **Lattice Tuning** (§8) at the Workshop.
- **Path raids** on Glasshouse happen through vanilla Path cells.

---

## 11. Nexerelin (full support; loaded only when Nex is present)

- `exerelinFactionConfig/rsl_choir.json`: playable; alignments technocratic + diplomatic (some ideological);
  paranoid of AI-tech factions, low invasion appetite; likes League and Independents; dislikes Hegemony, Path, TT.
- Starts: "Cantorate Chorister" (Grace Note + Refrain + Staccato) and a larger one (Cadence + escorts).
- Random sector: Nex places the home markets; our worldgen skips Vell, quest/secret entities still spawn.
- Invasions: Cantorate markets can fall; the quest survives it (§6 lifecycle).

---

## 12. Encores (Stage 7, user 2026-10-13; after the questline)

Two optional events once the Lacrimosa is complete (`$rsl_virtuosoUpgraded`); LunaLib toggles, both on by default.

| Event | Opens | Where | Rules | Prize |
|---|---|---|---|---|
| **The Second Voice** | 14 days after completion, Virtuoso in the fleet | the Antiphon Institute | duel vs **Commander Isolde Raike** (Tri-Tachyon Special Projects, level 15: 14 elite combat skills + *Second Voice*) in the **Dies Irae**, a second Virtuoso grown around a Hush core (violet seams, 3 S-mods). One ship each: the Lacrimosa as flagship, all other ships held out. Losing = the Lacrimosa yields and withdraws; rematch any time | **Ossia** hullmod (Glissando half CR cost, the String snaps once more), 250 Pitch Glass |
| **Requiem** | 45 days after completion | the wild system farthest from the core | **the Silence**: ~1,580 DP of Omega (4 Tesseracts) and Remnant hulls under AI cores, omega-core commander, 2 S-mods each. Never moves or attacks; must be ended in one encounter or it remakes itself. Nearly impossible by design | **Encore** hullmod (once per battle a disabling blow is refused: 3 s invulnerable, hull to 40%, CR to full), 1,000 Pitch Glass |

Lore: the Domain Navy built the Virtuoso to be the one voice no machine could jam or subvert; Venn's last Score names
what it was meant to fight. Special Projects picked the Hush's graveyard clean after beat 5 and grew the Dies Irae.

## 12. Open questions (none blocking Stage 2)

1. Pitch Glass amounts and Workshop prices are starting values; tune once you have played with them (Stage 4).
2. Concertmaster numbers (Stage 6).
