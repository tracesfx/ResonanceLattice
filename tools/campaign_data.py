"""Campaign data for the Cantorate of Vell (CAMPAIGN.md): faction, ship names, Pitch Glass, blueprint packages,
Nexerelin config and the campaign descriptions. Called from gen_data.py (`campaign_data.build(gen_data)`), which owns
the writers, the vanilla data access (V) and the faction id. Never hand-edit the files this writes.
"""

FACTION_NAME = "Cantorate"
CURRENCY = "rsl_pitchglass"
SHIP_PREFIX = "CCS"   # Cantorate Choir Ship
NAME_SOURCE = "RSL_CANTORATE"

# CAMPAIGN.md section 4. Applied by rsl.world.RslRelations in a vanilla game; Nexerelin applies startRelationships.
RELATIONS = {
    "independent": 0.30,
    "persean": 0.20,
    "sindrian_diktat": 0.0,
    "tritachyon": -0.20,
    "hegemony": -0.30,
    "luddic_church": -0.20,
    "luddic_path": -0.60,
}

RANKS = {
    "factionLeader": "Precentor",
    "spaceAdmiral": "Maestro",
    "spaceCommander": "Principal",
    "spaceCaptain": "Chorister",
    "spaceLieutenant": "Cantor",
    "spaceEnsign": "Cantor",
    "spaceChief": "Voice",
    "spaceSailor": "Voice",
    "groundGeneral": "Warden of the Score",
    "groundColonel": "Warden",
    "groundMajor": "Keeper",
    "groundCaptain": "Keeper",
}
POSTS = {
    "factionLeader": "Precentor",
    "administrator": "Cantor-Steward",
    "stationCommander": "Keeper of the Array",
    "baseCommander": "Keeper of the Array",
    "patrolCommander": "Watch Principal",
    "fleetCommander": "Maestro",
    "portmaster": "Harbour Cantor",
    "supplyOfficer": "Quartermaster",
    "intelligenceDirector": "Archivist of the Score",
    "scientist": "Luthier",
}

FLEET_NAMES = {
    "trade": "Crystal Convoy", "tradeLiner": "Choir Liner", "tradeSmuggler": "Quiet Trader",
    "smallTrader": "Tuners' Run", "patrolSmall": "Watch Quartet", "patrolMedium": "Patrol Ensemble",
    "patrolLarge": "Grand Choir", "inspectionFleet": "Pitch Inspection", "taskForce": "Concert Fleet",
    "foodReliefFleet": "Relief Choir", "mercBountyHunter": "Hired Voice", "mercPrivateer": "Hired Voice",
}

# Spacers in vac-suits and work collars: a refugee navy of workers and engineers, not executives.
PORTRAITS_M = ["portrait12", "portrait18", "portrait25", "portrait26", "portrait30", "portrait33", "portrait35",
               "portrait36", "portrait38", "portrait48", "portrait_league02", "portrait_league09"]
PORTRAITS_F = ["portrait14", "portrait16", "portrait21", "portrait22", "portrait27", "portrait28", "portrait29",
               "portrait32", "portrait37", "portrait41", "portrait_league08", "portrait_league10"]

# Musical forms, liturgy, theory and the working life of a tuner. Quest names (Lacrimosa, Antiphon, Aubade) and
# mechanic names (Overtone, Glissando, Bravura) are left out on purpose.
SHIP_NAMES = [
    "Vespers", "Matins", "Lauds", "Compline", "Nocturne", "Evensong", "Te Deum", "Magnificat", "Kyrie", "Gloria",
    "Agnus Dei", "Sanctus", "Benedictus", "Dies Irae", "Ostinato", "Ritornello", "Rubato", "Pianissimo",
    "Diminuendo", "Tutti", "Ripieno", "Concertino", "Canon", "Fugue", "Passacaglia", "Chaconne", "Toccata",
    "Partita", "Sarabande", "Gigue", "Courante", "Gavotte", "Madrigal", "Motet", "Plainchant", "Descant",
    "Fauxbourdon", "Melisma", "Neume", "Hocket", "Organum", "Perfect Fifth", "Open String", "Picardy Third",
    "Circle of Fifths", "Leading Tone", "Suspension", "Resolution", "Unison", "Octave", "Dorian", "Lydian",
    "Mixolydian", "Phrygian", "Aeolian", "Long Rest", "Breath Mark", "Da Capo", "Dal Segno", "Al Fine",
    "Held Note", "Sixteen-Hour Hum", "Tuner's Patience", "Collar and Chord", "By Ear", "No Voice Alone",
    "Kept Pitch", "The Long Flight", "Vell Sings", "Second Verse", "Reference Pitch", "Pulsar's Beat",
    "Quiet Hands", "What We Remember", "Lantern Choir", "Basso Continuo", "Cantus Firmus", "Tenebrae",
    "Stabat Mater", "Ave Verum", "Last Rehearsal", "Unbroken Chord",
]

FACTION_DESC = (
    "A small refugee polity in the pulsar system of Vell, descended from the staff of a Domain harmonic-flux "
    "laboratory that was cut off by the Collapse. The Cantorate builds its ships around crystalline lattice cores "
    "that lock to one another's pitch: a battle network with no comm traffic to jam and no AI core to ban.\n\n"
    "Everything the Cantorate knows survives as scores, tuning protocols memorised by its engineers after the "
    "databanks were lost. Its crews hold their cores in tune through long shifts, its government rules by "
    "consensus, and dissent is treated as what it is in a choir: a fault that weakens everyone. Its first and "
    "oldest law is that no voice sings alone.\n\n"
    "Poor in everything but crystal, the Cantorate cannot leave Vell, the only star whose beat its crystals grow "
    "true to. The Hegemony inspects its cores for artificial minds, Tri-Tachyon wants to buy or steal them, and the "
    "Luddic Path calls them machine-worship.")

PITCHGLASS_DESC = (
    "Shards of lattice crystal grown true to the pulsar of Vell, each still ringing at the Cantorate's reference "
    "pitch. Outside Vell it is pretty glass worth next to nothing; to the Cantorate it is the only thing that can "
    "retune a core, and the Luthiers of Coda value it above credits.")

PACKAGES = [
    # id, name, tag, icon, base price, desc
    ("rsl_bp_hulls_package", "Cantorate Hull Blueprints", "rsl_bp_hulls", "rsl_bp_hulls", 120000,
     "The Cantorate's hull scores: growth and calibration protocols for the lattice cores of its line ships, "
     "with the frames written around them. Enables heavy industry to construct Lattice hulls."),
    ("rsl_bp_weapons_package", "Cantorate Weapon Blueprints", "rsl_bp_weapons", "rsl_bp_weapons", 80000,
     "Rail, lance and spike patterns tuned to lattice cores. Enables heavy industry to construct the Cantorate's "
     "weapons."),
    ("rsl_bp_wings_package", "Cantorate Wing Blueprints", "rsl_bp_wings", "rsl_bp_wings", 60000,
     "Fighter LPCs for the Cantorate's tuned wings. Enables heavy industry to construct Lattice fighters."),
]


def faction(g):
    f = g.V.spec("faction", "tritachyon")
    f.pop("internalComms", None)   # Tri-Tachyon's comm channel (logo and reports); the Cantorate has none yet
    f.update({
        "id": g.FACTION, "color": [100, 230, 220, 255],
        "displayName": FACTION_NAME, "displayNameWithArticle": "the " + FACTION_NAME,
        "displayNameLong": "Cantorate of Vell", "displayNameLongWithArticle": "the Cantorate of Vell",
        "logo": "graphics/rsl/factions/rsl_flag.png", "crest": "graphics/rsl/factions/rsl_crest.png",
        "shipNamePrefix": SHIP_PREFIX, "shipNameSources": {NAME_SOURCE: 4, "GENERAL": 1},
        "names": {"modern": 1, "world": 1, "future": 1},
        "variantOverrides": {}, "hullFrequency": {"tags": {}, "hulls": {}},
        "shipsWhenImporting": {"tags": [], "hulls": []},
        "knownShips": {"tags": [g.BP], "hulls": ["rsl_gracenote", "rsl_refrain", "rsl_staccato", "rsl_cadence",
                                                   "rsl_tremolo", "rsl_halo", "rsl_conductor"]},
        "priorityShips": {"tags": [g.BP], "hulls": []},
        "knownFighters": {"tags": [g.BP], "fighters": ["rsl_trill_wing", "rsl_cadenza_wing", "rsl_requiem_wing"]},
        "priorityFighters": {"tags": [g.BP], "fighters": []},
        "knownWeapons": {"tags": [g.BP], "weapons": []}, "priorityWeapons": {"tags": [g.BP], "weapons": []},
        "knownHullMods": {"tags": ["standard"], "hullMods": []},
        "weaponSellFrequency": {}, "fighterSellFrequency": {}, "hullmodSellFrequency": {},
        # AI cores are contraband in Vell: the Cantorate takes them only to silence them (Luthier's Workshop)
        "illegalCommodities": ["ai_cores"],
        "music": {
            "theme": "music_galatia_academy",
            "market_neutral": "music_tritach_market_neutral",
            "market_hostile": "music_tritach_market_hostile",
            "market_friendly": "music_tritach_market_friendly",
            "encounter_neutral": "music_tritach_encounter_neutral",
            "encounter_hostile": "music_tritach_encounter_hostile",
            "encounter_friendly": "music_tritach_encounter_friendly",
        },
        "portraits": {
            "standard_male": ["graphics/portraits/%s.png" % p for p in PORTRAITS_M],
            "standard_female": ["graphics/portraits/%s.png" % p for p in PORTRAITS_F],
        },
        "ranks": {"ranks": {k: {"name": v} for k, v in RANKS.items()},
                  "posts": {k: {"name": v} for k, v in POSTS.items()}},
        "voices": {"LOW": {"spacer": 10, "soldier": 5}, "MEDIUM": {"spacer": 5, "scientist": 5, "soldier": 5},
                   "HIGH": {"scientist": 10, "aristo": 3}},
        "fleetTypeNames": FLEET_NAMES,
        "showInIntelTab": True,
    })
    f["factionDoctrine"].update({"warships": 5, "carriers": 1, "phaseShips": 1, "officerQuality": 1,
                                 "shipQuality": 5, "numShips": 1, "shipSize": 4, "aggression": 2,
                                 "officerSkills": ["energy_weapon_mastery", "field_modulation"],
                                 "commanderSkills": ["coordinated_maneuvers", "flux_regulation", "electronic_warfare"]})
    c = f["custom"]
    c["offersCommissions"] = True
    c["engagesInHostilities"] = True
    c["buysAICores"] = False
    c["buysSurveyData"] = True
    c["hostilityImpactOnGrowth"] = True
    c.pop("AICoreValueMult", None)
    c.pop("AICoreRepMult", None)
    c.pop("punitiveExpeditionData", None)   # a small enclave: no punitive expeditions
    g.write_json("data/world/factions/%s.faction" % g.FACTION, f)
    g.write_csv("data/world/factions/factions.csv", ["faction"],
                [{"faction": "data/world/factions/%s.faction" % g.FACTION}])
    g.write_json("data/world/factions/default_ship_roles.json", {
        "combatSmall": {"rsl_gracenote_Standard": 6, "rsl_gracenote_Pluck": 6},
        "combatSmallForSmallFleet": {"rsl_gracenote_Standard": 6, "rsl_gracenote_Pluck": 6},
        "fastAttack": {"rsl_gracenote_Pluck": 5, "rsl_staccato_Burst": 5},
        "escortSmall": {"rsl_gracenote_Warden": 10},
        "combatMedium": {"rsl_refrain_Chorister": 4, "rsl_staccato_Standard": 4, "rsl_staccato_Burst": 4,
                         "rsl_staccato_Lancer": 4},
        "escortMedium": {"rsl_refrain_Standard": 4, "rsl_refrain_Bulwark": 6},
        "combatLarge": {"rsl_cadence_Standard": 3, "rsl_cadence_Battery": 4, "rsl_cadence_Drumline": 3,
                        "rsl_tremolo_Standard": 3, "rsl_tremolo_Waveform": 4, "rsl_tremolo_Riptide": 3},
        "carrierLarge": {"rsl_halo_Standard": 4, "rsl_halo_Nocturne": 5, "rsl_halo_Sanctuary": 5},
        "combatCapital": {"rsl_conductor_Standard": 3, "rsl_conductor_Maestro": 4, "rsl_conductor_Fortissimo": 3,
                          "rsl_halo_Nocturne": 2},
    })


def ship_names(g):
    g.write_json("data/strings/ship_names.json", {NAME_SOURCE: SHIP_NAMES})


def commodities(g):
    """Pitch Glass: a non-economy commodity (markets never stock it). Worth ~5 credits to outsiders, so selling it on
    an open market is pointless; its real price is in the Luthier's Workshop (Stage 4)."""
    hdr = g.V.header("commodities.csv")
    r = g.V.clone_row("commodities.csv", "gamma_core", **{
        "name": "Pitch Glass", "id": CURRENCY, "demand class": CURRENCY, "base price": 5, "utility": 1,
        "price variability": 0, "tags": "nonecon, no_loss_from_combat",
        "icon": "graphics/rsl/icons/cargo/rsl_pitchglass.png", "sound id": "ui_cargo_metals",
        "sound id drop": "ui_cargo_metals_drop", "order": 42, "baseRaidDanger": "", "desc": PITCHGLASS_DESC})
    g.write_csv("data/campaign/commodities.csv", hdr, [r])


def special_items(g):
    """Blueprint packages (MultiBlueprintItemPlugin: every hull/weapon/wing carrying ALL the listed tags). no_drop:
    they come only from the Luthier's Workshop and the abandoned Array (CAMPAIGN.md sections 7-8)."""
    hdr = g.V.header("special_items.csv")
    rows = []
    for i, (iid, name, tag, icon, price, text) in enumerate(PACKAGES):
        rows.append(g.V.clone_row("special_items.csv", "high_tech_package", **{
            "name": name, "id": iid, "tags": "package_bp, no_drop, codex_unlockable", "base price": price,
            "icon": "graphics/rsl/icons/cargo/%s.png" % icon, "plugin params": tag, "desc": text,
            "order": 290 + i}))
    g.write_csv("data/campaign/special_items.csv", hdr, rows)


PLACES = {
    # (id, CUSTOM) descriptions, set on the entities by rsl.world.VellGen
    "rsl_desc_vell": "A neutron star that turns once every 1.3 seconds and sweeps the system with a beam of hard "
                     "radiation. Its beat is steadier than any clock humanity has built, and it is the only reason "
                     "anyone lives here: lattice crystal grows true only to a pulsar's rhythm.",
    "rsl_desc_tacet": "A listening station in a tight orbit around Vell, shielded against the beam that crosses it "
                      "every rotation. Tacet Station records the pulsar and broadcasts the Cantorate's reference "
                      "pitch, the tone every lattice core in Vell is tuned against. Its archives hold what the "
                      "refugees managed to save of the Antiphon Institute, and some of what they chose to forget.",
    "rsl_desc_tenuto": "A scorched rock that holds its orbit through the pulsar's beam. Nothing grows here and nobody "
                       "has tried; the Cantorate's tuners use it as a reference target.",
    "rsl_desc_basso": "A cold, slow ice giant whose low radio drone gave it its name. Its moons are the Cantorate's "
                      "home: Coda, where the refugees settled, and Glasshouse, where they grow the crystal.",
    "rsl_desc_coda": "A frozen moon of Basso and the capital of the Cantorate of Vell. Its habitats were dug by a "
                     "refugee fleet that had run out of places to go, and they still hum: every district keeps a "
                     "tuning shift, and the whole city falls silent at the change of watch.\n\nAbove it turns the "
                     "Cantor Array, the largest lattice instrument the Cantorate has ever grown.",
    "rsl_desc_glasshouse": "An airless moon of Basso where lattice crystal is grown in pressurised vaults timed to "
                           "the pulsar. The nurseries are tended in shifts by workers who can hear a flawed crystal "
                           "before any instrument can find it, and who lose that hearing young.",
    "rsl_desc_cantor_array": "A lattice station of six petals around a crystal heart, turning slowly above Coda. "
                             "When one petal is lost, its stored resonance floods the others.",
}

INDUSTRY_DESC = (
    "The Cantor Array: a six-petal lattice station grown around a crystal heart. Its Spires hold the long lances, its "
    "Bells the flak and point defense, its Lofts the Cantorate's fighters, and every petal that falls makes the rest "
    "stronger.\n\nMust be reduced before a bombardment can be attempted.")

NURSERIES_DESC = (
    "Lattice crystal is grown on $market in pressurised vaults timed to the pulsar of Vell. The tailings feed the "
    "mines, and the hum of the nurseries carries through every corridor.")


def industries(g):
    hdr = g.V.header("industries.csv")
    r = g.V.clone_row("industries.csv", "starfortress_high", **{
        "id": "rsl_cantor_array", "name": "Cantor Array", "downgrade": "", "upgrade": "",
        "tags": "station, starfortress, unraidable, structure",
        "data": "{\nradius:110,\nvariant:rsl_cantor_Standard,\nfleetName:Cantor Array\n}",   # as vanilla
        "image": "graphics/rsl/icons/industry/rsl_cantor_array.png",
        "plugin": "rsl.world.CantorArrayIndustry", "desc": INDUSTRY_DESC})
    g.write_csv("data/campaign/industries.csv", hdr, [r])


def conditions(g):
    hdr = g.V.header("market_conditions.csv")
    r = {c: "" for c in hdr}
    r.update({"name": "Lattice Nurseries", "id": "rsl_lattice_nurseries", "planetary": "",
              "script": "rsl.world.LatticeNurseries", "desc": NURSERIES_DESC,
              "icon": "graphics/rsl/icons/markets/rsl_lattice_nurseries.png", "order": 1390})
    g.write_csv("data/campaign/market_conditions.csv", hdr, [r])


def nexerelin(g):
    """Read only when Nexerelin is enabled; harmless otherwise. Keys copied from Nex's own faction configs."""
    g.write_csv("data/config/exerelinFactionConfig/mod_factions.csv", ["faction"], [{"faction": g.FACTION}])
    g.write_json("data/config/exerelinFactionConfig/%s.json" % g.FACTION, {
        "playableFaction": True,
        "corvusCompatible": True,
        "rebelFleetSuffix": "Dissonants",
        "directoryUseShortName": True,
        "marketSpawnWeight": 0.6,
        "startRelationships": {k: v for k, v in RELATIONS.items() if v != 0},
        "morality": "neutral",
        "alignments": {"technocratic": 1, "diplomatic": 0.5, "ideological": 0.5, "corporate": -0.5,
                       "militarist": 0},
        "diplomacyTraits": ["dislikes_ai", "lowprofile", "helps_allies", "pacifist"],
        "vengeanceLevelNames": ["Dissonance", "Discord", "Requiem"],
        "vengeanceFleetNames": ["Dissonance", "Discord", "Requiem"],
        "vengeanceFleetNamesSingle": ["a Dissonance Choir", "a Discord Choir", "a Requiem Choir"],
        "startShipsSolo": [["rsl_gracenote_Pluck"], ["rsl_gracenote_Warden"]],
        "startShipsCombatSmall": [
            ["rsl_staccato_Burst", "rsl_gracenote_Standard", "rsl_gracenote_Warden"],
            ["rsl_refrain_Chorister", "rsl_gracenote_Pluck", "rsl_gracenote_Standard"],
        ],
        "startShipsCombatLarge": [
            ["rsl_cadence_Battery", "rsl_refrain_Bulwark", "rsl_gracenote_Warden"],
            ["rsl_tremolo_Waveform", "rsl_staccato_Lancer", "rsl_gracenote_Pluck"],
        ],
        "startShipsCarrierLarge": [["rsl_halo_Sanctuary", "rsl_refrain_Standard"]],
        "startSpecialItems": [[["rsl_bp_weapons_package", ""]]],
        "industrySeeds": [
            {"id": "orbitalworks", "mult": 0.1},
            {"id": "militarybase", "mult": 0.1},
            {"id": "refining", "mult": 0.1},
        ],
    })


def descriptions():
    rows = [{"id": "rsl_choir", "type": "FACTION", "text1": FACTION_DESC}]
    rows += [{"id": k, "type": "CUSTOM", "text1": v} for k, v in PLACES.items()]
    return rows


def build(g):
    faction(g)
    ship_names(g)
    commodities(g)
    special_items(g)
    industries(g)
    conditions(g)
    nexerelin(g)
