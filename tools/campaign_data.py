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


INTEL_ICONS = {"rsl_contract": "graphics/rsl/icons/intel/rsl_contract.png",
               "rsl_lacrimosa": "graphics/rsl/icons/intel/rsl_lacrimosa.png",
               "rsl_scores": "graphics/rsl/icons/intel/rsl_scores.png",
               "rsl_duel": "graphics/rsl/icons/intel/rsl_duel.png",
               "rsl_requiem": "graphics/rsl/icons/intel/rsl_requiem.png"}

METRONOME_DESC = (
    "A navigation clock grown around a sliver of lattice crystal and keyed to the beat of a pulsar. Installed in a "
    "Waystation it times every approach, docking and departure to a pitch no jammer can touch; traffic flows, and "
    "nobody waits in the dark.")

# ------------------------------------------------------------------------------------------------- rules.csv
# Each rule: (id, trigger, [conditions], [script lines], text, [options "order:id:text"]). Texts may use OR lines.
FACTION_COND = "$faction.id == rsl_choir"
RULES = [
    # ---- comm greetings from Cantorate fleets (copied structure of vanilla greetingTT*)
    ("rsl_greetingTuned", "OpenCommLink", [FACTION_COND, "!$entity.isHostile", "$player.rsl_tuned"],
     ["$menuState = fleetConvMain 0", "FireAll PopulateOptions"],
     "\"Your cores are ringing at our reference pitch, captain. Someone in Coda thinks well of you.\" The "
     "$personRank sounds almost warm.\nOR\n\"We can hear you before we see you. You are in tune. Welcome.\"", []),
    ("rsl_greetingFriendly", "OpenCommLink", [FACTION_COND, "$faction.friendlyToPlayer"],
     ["$menuState = fleetConvMain 0", "FireAll PopulateOptions"],
     "\"Comm open. Voice and pitch confirmed. Good to hear you, captain.\"\nOR\n\"Ah, a friend of the chorus. "
     "Forgive the hum; we are mid-shift.\" Behind the $personRank a row of tuners sit with their eyes closed, "
     "holding one long note.", []),
    ("rsl_greetingNeutral", "OpenCommLink", [FACTION_COND, "$faction.neutralToPlayer"],
     ["$menuState = fleetConvMain 0", "FireAll PopulateOptions"],
     "\"Cantorate vessel. State your business and keep clear of our formation; your drive noise is fouling our "
     "tuning.\"\nOR\n\"We are on a working patrol, captain. Please do not cross our line.\" The $personRank does "
     "not quite look at the camera; $heOrShe is listening to something you cannot hear.", []),
    ("rsl_greetingHostileWeaker", "OpenCommLink", [FACTION_COND, "$entity.isHostile", "$entity.relativeStrength < 0"],
     ["$entity.ignorePlayerCommRequests = true 1"],
     "\"You are out of tune, captain, and the whole choir can hear it.\" The $personRank's voice is steady, but "
     "the hum behind $himOrHer has gone ragged.\nOR\n\"No voice sings alone. If you take us, all of Vell will "
     "know your name.\"", ["cutCommLink:Cut the comm link"]),
    ("rsl_greetingHostileStronger", "OpenCommLink", [FACTION_COND, "$entity.isHostile",
                                                     "$entity.relativeStrength >= 0"],
     ["$entity.ignorePlayerCommRequests = true 1"],
     "\"You are out of tune, captain.\" The $personRank closes the channel before you can answer.\nOR\n\"All "
     "voices, on my pitch.\" The order is not meant for you, and the hum on the channel rises into a single note.",
     ["cutCommLink:Cut the comm link"]),
    # ---- Luthier's Workshop at Coda (rsl.rulecmd.RslWorkshop takes over the dialog until the player leaves)
    ("rsl_workshopOpt", "PopulateOptions", ["$hasMarket", "$menuState == main", "$market.id == rsl_coda",
                                            "$faction.id == rsl_choir", "$tradeMode != NONE", "!$faction.isHostile"],
     [], "", ["6:rsl_workshopOpen:Visit the Luthier's Workshop"]),
    ("rsl_workshopOpen", "DialogOptionSelected", ["$option == rsl_workshopOpen"], ["RslWorkshop"], "", []),
    # ---- tuners' contract board at Tacet Station (rsl.rulecmd.RslContracts)
    ("rsl_contractOpt", "PopulateOptions", ["$hasMarket", "$menuState == main", "$market.id == rsl_tacet",
                                            "$faction.id == rsl_choir", "$tradeMode != NONE", "!$faction.isHostile"],
     [], "", ["7:rsl_contractBoard:Check the tuners' contract board"]),
    ("rsl_contractBoard", "DialogOptionSelected", ["$option == rsl_contractBoard"], ["RslContracts board"], "", []),
    ("rsl_contractAccept", "DialogOptionSelected", ["$option == rsl_contractAccept"],
     ["RslContracts accept", "FireAll PopulateOptions"], "", []),
    ("rsl_contractBack", "DialogOptionSelected", ["$option == rsl_contractBack"], ["FireAll PopulateOptions"], "", []),
    # ---- the Lacrimosa questline (Stage 5). Every scene runs in rsl.rulecmd.RslLacrimosa, which takes over the dialog;
    # the conditions are the same command in "can" mode (market owned by the Cantorate + quest stage).
    ("rsl_qTanhOpt", "PopulateOptions", ["$hasMarket", "$menuState == main", "RslLacrimosa can tanh"],
     [], "", ["4:rsl_qTanh:Open the sealed message from Tacet Station"]),
    ("rsl_qTanh", "DialogOptionSelected", ["$option == rsl_qTanh"], ["RslLacrimosa tanh"], "", []),
    ("rsl_qCouncilOpt", "PopulateOptions", ["$hasMarket", "$menuState == main", "RslLacrimosa can council"],
     [], "", ["4:rsl_qCouncil:Answer the Precentor's summons"]),
    ("rsl_qCouncil", "DialogOptionSelected", ["$option == rsl_qCouncil"], ["RslLacrimosa council"], "", []),
    ("rsl_qRecordingOpt", "PopulateOptions", ["$hasMarket", "$menuState == main", "RslLacrimosa can recording"],
     [], "", ["4:rsl_qRecording:Meet Archivist Tanh about the pulsar recording"]),
    ("rsl_qRecording", "DialogOptionSelected", ["$option == rsl_qRecording"], ["RslLacrimosa recording"], "", []),
    # quest sites (custom entities); score as vanilla's abyssal_light so no generic rule wins
    ("rsl_qBuoyOpen", "OpenInteractionDialog", ["$customType == rsl_listening_buoy score:1000"],
     ["ShowDefaultVisual", "RslLacrimosa buoy"], "", []),
    ("rsl_qInstituteOpen", "OpenInteractionDialog", ["$customType == rsl_antiphon_institute score:1000"],
     ["ShowDefaultVisual", "RslLacrimosa institute"], "", []),
    ("rsl_qEchoOpen", "OpenInteractionDialog", ["$customType == rsl_hush_echo score:1000"],
     ["ShowDefaultVisual", "RslLacrimosa echo"], "", []),
    ("rsl_qGraveyardOpen", "OpenInteractionDialog", ["$customType == rsl_hush_graveyard score:1000"],
     ["ShowDefaultVisual", "RslLacrimosa graveyard"], "", []),
    # ---- secrets (Stage 6, rsl.rulecmd.RslSecrets)
    ("rsl_sCacheOpen", "OpenInteractionDialog", ["$customType == rsl_score_cache score:1000"],
     ["ShowDefaultVisual", "RslSecrets cache"], "", []),
    ("rsl_sVennOpen", "OpenInteractionDialog", ["$customType == rsl_venns_rest score:1000"],
     ["ShowDefaultVisual", "RslSecrets vennsrest"], "", []),
]


def entity(name, in_text, radius, desc, icon, sprite, sw, sh, image, aoran="a"):
    return {"defaultName": name, "nameInText": in_text, "shortName": in_text.split()[-1], "aOrAn": aoran,
            "isOrAre": "is", "defaultRadius": radius, "customDescriptionId": desc, "interactionImage": image,
            "icon": icon, "iconWidth": 22, "iconHeight": 22, "sprite": sprite, "spriteWidth": sw, "spriteHeight": sh,
            "renderShadow": True, "useLightColor": True, "showInCampaign": True, "showIconOnMap": True,
            "showNameOnMap": False, "scaleNameWithZoom": False, "scaleIconWithZoom": True,
            "renderCircleIndicator": True, "renderCircleIndicatorSelectionFlash": True,
            "tags": ["has_interaction_dialog", "neutrino"], "layers": ["STATIONS"]}


# Quest sites (vanilla sprites and pictures; the echo and the graveyard are our own dead Lattice hulls)
CUSTOM_ENTITIES = {
    "rsl_listening_buoy": entity("Listening Buoy", "listening buoy", 30, "rsl_desc_buoy",
                                 "graphics/icons/generic_probe_icon.png", "graphics/stations/survey_probe.png", 40, 40,
                                 "graphics/illustrations/comm_relay.jpg"),
    "rsl_antiphon_institute": entity("Antiphon Institute", "Antiphon Institute", 60, "rsl_desc_institute",
                                     "graphics/icons/station_research_broken.png",
                                     "graphics/stations/station_side00.png", 72, 72,
                                     "graphics/illustrations/orbital_construction.jpg", aoran="the"),
    "rsl_hush_echo": entity("Silent Echo", "silent echo", 25, "rsl_desc_echo", "graphics/icons/derelict.png",
                            "graphics/rsl/ships/rsl_gracenote.png", 34, 58, "graphics/illustrations/space_wreckage.jpg"),
    "rsl_score_cache": dict(entity("Institute Cache", "Institute data cache", 25, "rsl_desc_score_cache",
                                   "graphics/icons/derelict.png", "graphics/stations/survey_probe.png", 34, 34,
                                   "graphics/illustrations/space_wreckage.jpg", aoran="an"),
                            discoverable=True, discoveryXP=400, detectionRange=1200),
    "rsl_venns_rest": entity("Venn's Rest", "cryo vault", 50, "rsl_desc_venns_rest",
                             "graphics/icons/station_research_broken.png", "graphics/stations/station_side06.png",
                             60, 60, "graphics/illustrations/orbital_construction.jpg"),
    "rsl_hush_graveyard": entity("The Hush", "graveyard of the First Chorus", 80, "rsl_desc_graveyard",
                                 "graphics/icons/derelict.png", "graphics/rsl/ships/rsl_conductor.png", 66, 119,
                                 "graphics/illustrations/space_wreckage.jpg", aoran="the"),
}


def custom_entities(g):
    g.write_json("data/config/custom_entities.json", CUSTOM_ENTITIES)


# Silent wrecks carry Pitch Glass in their salvage (drop value in credits; Pitch Glass is worth 5)
def drop_groups(g):
    g.write_csv("data/campaign/procgen/drop_groups.csv", ["commodity", "group", "freq"],
                [{"commodity": CURRENCY, "group": "rsl_pitchglass_drop", "freq": 1}])


# Concertmaster Odile Marchetti's unique skill (CAMPAIGN.md section 9): npc_only, so nobody else can learn it. Its
# battle effect is applied by rsl.combat.ChorusEffects; rsl.skills.Concertmaster only describes it.
def skills(g):
    hdr = g.V.header("characters/skills/skill_data.csv")
    r = {c: "" for c in hdr}
    r.update({"id": "rsl_concertmaster", "name": "Concertmaster", "order": 10050, "tier": 0,
              "description": "\"You have ships that sing? Then you need someone who can hear them.\"",
              "author": "Odile Marchetti, first chair of the First Chorus", "combat officer": "TRUE",
              "tags": "npc_only", "icon": "graphics/rsl/icons/skills/rsl_concertmaster.png"})
    r2 = {c: "" for c in hdr}
    r2.update({"id": "rsl_second_voice", "name": "Second Voice", "order": 10051, "tier": 0,
               "description": "\"There have only ever been two. I intend to be the one they remember.\"",
               "author": "Commander Isolde Raike, Tri-Tachyon Special Projects", "combat officer": "TRUE",
               "tags": "npc_only", "icon": "graphics/rsl/icons/skills/rsl_second_voice.png"})
    g.write_csv("data/characters/skills/skill_data.csv", hdr, [r, r2])
    # Isolde Raike's unique fifteenth skill (rsl.campaign.EncoreFleets): her own ship only
    g.write_json("data/characters/skills/rsl_second_voice.skill", {
        "id": "rsl_second_voice", "governingAptitude": "combat", "compressHullmods": False, "scope": "PILOTED_SHIP",
        "effectGroups": [{"requiredSkillLevel": 1, "effectBasedOnLevel": False, "effects": [
            {"type": "SHIP", "script": "rsl.skills.SecondVoice$Level1"}]}]})
    g.write_json("data/characters/skills/rsl_concertmaster.skill", {
        "id": "rsl_concertmaster", "governingAptitude": "combat", "compressHullmods": False,
        "scope": "CUSTOM", "scopeStr": "all ships in the battle, while her ship is deployed",
        "effectGroups": [{"requiredSkillLevel": 1, "effectBasedOnLevel": False, "effects": [
            {"type": "SHIP", "script": "rsl.skills.Concertmaster$Level1"},
            {"type": "SHIP", "script": "rsl.skills.Concertmaster$Level2"}]}]})


SASH_DESC = (
    "The Lacrimosa's sash and vanes, taken from the flagship of the Hush: a ribbon of lattice crystal grown to run "
    "down a Virtuoso's spine, and the two great vanes that steer its voice. Still humming. Only the dock of the "
    "Antiphon Institute can mount them.")


def rules(g):
    hdr = ["id", "trigger", "conditions", "script", "text", "options", "notes"]
    rows = [{"id": i, "trigger": t, "conditions": "\n".join(c), "script": "\n".join(s), "text": x,
             "options": "\n".join(o), "notes": ""} for i, t, c, s, x, o in RULES]
    g.write_csv("data/campaign/rules.csv", hdr, rows)


# ------------------------------------------------------------------------------------------------- MagicLib bounties
BOUNTY_LOCATION = {
    "location_distance": "CLOSE",
    "location_themes": ["procgen_no_theme", "procgen_no_theme_pulsar_blackhole", "theme_ruins_secondary",
                        "theme_interesting_minor"],
    "location_themes_blacklist": ["theme_already_occupied", "theme_already_colonized", "theme_hidden"],
    "location_entities": ["planet", "jump_point", "stable_location"],
    "location_prioritizeUnexplored": False,
    "location_defaultToAnyEntity": True,
}

BOUNTIES = {
    "rsl_discordant": dict({
        "trigger_marketFaction_any": ["rsl_choir", "independent"],
        "trigger_player_minLevel": 8,
        "trigger_weight_mult": 1.0,
        "job_name": "The Discordant",
        "job_description": "A pirate lord calling $himselfHerselfThemselves ==the Discordant== has been flying "
                           "Lattice ships stripped from Cantorate wrecks, their cores ==never retuned==. They shriek "
                           "on every band, and the Cantorate wants them silenced before someone learns to copy them."
                           "\n\nThe Luthiers add ==60 Pitch Glass== to the credit reward: the cores in those hulls "
                           "are still theirs.",
        "job_comm_reply": "The channel fills with a grinding, mistuned howl. Somewhere under it, someone is laughing.",
        "job_intel_success": "The Discordant's flagship has been silenced.",
        "job_intel_expired": "The Discordant has gone quiet, for now.",
        "job_forFaction": "rsl_choir",
        "job_deadline": 180,
        "job_credit_reward": 160000,
        "job_reward_scaling": 0.5,
        "job_reputation_reward": 5,
        "job_item_reward": {"rsl_pitchglass": 60},
        "job_type": "assassination",
        "job_show_type": True,
        "job_show_captain": True,
        "job_show_fleet": "flagshipText",
        "job_show_distance": "vanillaDistance",
        "job_difficultyDescription": "auto",
        "target_first_name": "Dariel",
        "target_last_name": "Vasko",
        "target_portrait": "graphics/portraits/portrait_pirate14.png",
        "target_gender": "MALE",
        "target_rank": "spaceCaptain",
        "target_post": "fleetCommander",
        "target_personality": "reckless",
        "target_level": 6,
        "target_elite_skills": 3,
        "fleet_name": "The Discordant Choir",
        "fleet_faction": "pirates",
        "fleet_flagship_variant": "rsl_cadence_Battery",
        "fleet_flagship_name": "Wolf Note",
        "fleet_flagship_autofit": False,
        "fleet_preset_ships": {"rsl_staccato_Burst": 2, "rsl_gracenote_Pluck": 2, "rsl_refrain_Standard": 1},
        "fleet_preset_autofit": False,
        "fleet_scaling_multiplier": 0.6,
        "fleet_min_FP": 110,
        "fleet_composition_faction": "pirates",
        "fleet_composition_quality": 0.6,
        "fleet_transponder": False,
        "fleet_behavior": "GUARDED",
    }, **BOUNTY_LOCATION),
    "rsl_inspection_overreach": {
        "trigger_market_id": ["rsl_coda", "rsl_glasshouse", "rsl_tacet"],
        "trigger_marketFaction_any": ["rsl_choir"],
        "trigger_player_minLevel": 10,
        "job_name": "Inspection Overreach",
        "job_description": "Inspector ==Arno Vettrick== came to Vell with a Hegemony warrant to search Cantorate "
                           "cores for artificial minds. The warrant expired a year ago. He stayed, with a privately "
                           "crewed squadron, boarding crystal convoys and confiscating whatever he cannot understand."
                           "\n\nThe Cantorate cannot fire on a Hegemony officer. You are not the Cantorate. The "
                           "Luthiers add ==40 Pitch Glass==.",
        "job_comm_reply": "\"By the authority of the Hegemony's AI inspection mandate, stand down for search.\"",
        "job_intel_success": "Vettrick's squadron will board no more convoys.",
        "job_intel_expired": "Vettrick has left Vell, his holds full.",
        "job_forFaction": "rsl_choir",
        "job_deadline": 120,
        "job_credit_reward": 200000,
        "job_reward_scaling": 0.5,
        "job_reputation_reward": 8,
        "job_item_reward": {"rsl_pitchglass": 40},
        "job_type": "assassination",
        "job_show_fleet": "presetText",
        "job_show_distance": "system",
        "job_difficultyDescription": "auto",
        "target_first_name": "Arno",
        "target_last_name": "Vettrick",
        "target_portrait": "graphics/portraits/portrait_hegemony05.png",
        "target_gender": "MALE",
        "target_rank": "spaceCommander",
        "target_post": "fleetCommander",
        "target_personality": "steady",
        "target_level": 7,
        "target_elite_skills": 3,
        "fleet_name": "Inspection Squadron",
        "fleet_faction": "ML_bounty",
        "fleet_flagship_variant": "dominator_Assault",
        "fleet_flagship_name": "Writ of Search",
        "fleet_flagship_autofit": False,
        "fleet_preset_ships": {"enforcer_Elite": 2, "hammerhead_Elite": 2, "lasher_CS": 2},
        "fleet_preset_autofit": False,
        "fleet_scaling_multiplier": 0.6,
        "fleet_min_FP": 130,
        "fleet_composition_faction": "hegemony",
        "fleet_composition_quality": 1,
        "fleet_attitude": "HOSTILE",
        "fleet_behavior": "AGGRESSIVE",
        "location_entitiesID": ["rsl_basso", "rsl_glasshouse_planet"],
        "location_distance": "CLOSE",
        "location_defaultToAnyEntity": True,
    },
    # Opens in Stage 5 (the questline sets $rsl_qRefusedSung when the player refuses Director Sung's offer).
    "rsl_special_projects": dict({
        "trigger_memKeys_all": {"$rsl_qRefusedSung": True},
        "trigger_marketFaction_any": ["rsl_choir", "independent"],
        "trigger_player_minLevel": 12,
        "job_name": "Special Projects Remnant",
        "job_description": "What is left of Director Sung's Special Projects group has not given up on lattice "
                           "cores. A phase-heavy Tri-Tachyon squadron, flying without transponders, is hunting "
                           "Cantorate couriers for their crystal.\n\nThe Luthiers add ==80 Pitch Glass==.",
        "job_comm_reply": "\"This conversation is not happening.\"",
        "job_intel_success": "Special Projects has lost another squadron it never had.",
        "job_intel_expired": "The squadron has vanished back into the Company's books.",
        "job_forFaction": "rsl_choir",
        "job_deadline": 150,
        "job_credit_reward": 250000,
        "job_reward_scaling": 0.5,
        "job_reputation_reward": 8,
        "job_item_reward": {"rsl_pitchglass": 80},
        "job_type": "assassination",
        "job_show_fleet": "flagshipText",
        "job_show_distance": "vanillaDistance",
        "job_difficultyDescription": "auto",
        "target_first_name": "Imre",
        "target_last_name": "Calloway",
        "target_portrait": "graphics/portraits/portrait_corporate05.png",
        "target_gender": "MALE",
        "target_rank": "spaceCommander",
        "target_post": "fleetCommander",
        "target_personality": "aggressive",
        "target_level": 7,
        "target_elite_skills": 4,
        "fleet_name": "Special Projects Squadron",
        "fleet_faction": "ML_bounty",
        "fleet_flagship_variant": "doom_Strike",
        "fleet_flagship_autofit": False,
        "fleet_preset_ships": {"harbinger_Strike": 1, "afflictor_Strike": 2, "shade_Assault": 2,
                               "medusa_Attack": 1},
        "fleet_preset_autofit": False,
        "fleet_scaling_multiplier": 0.7,
        "fleet_min_FP": 160,
        "fleet_composition_faction": "tritachyon",
        "fleet_composition_quality": 2,
        "fleet_transponder": False,
        "fleet_attitude": "HOSTILE",
        "fleet_behavior": "ROAMING",
    }, **BOUNTY_LOCATION),
}


def bounties(g):
    g.write_json("data/config/modFiles/magicBounty_data.json", BOUNTIES)


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
    # Pulsar Metronome: a Waystation colony item (effect: rsl.world.PulsarMetronome, registered on app load)
    rows.append(g.V.clone_row("special_items.csv", "fullerene_spool", **{
        "name": "Pulsar Metronome", "id": "rsl_pulsar_metronome", "tags": "colony_item, no_drop, codex_unlockable",
        "base price": 150000, "icon": "graphics/rsl/icons/cargo/rsl_pulsar_metronome.png",
        "plugin params": "waystation", "desc": METRONOME_DESC, "order": 295}))
    # the Lacrimosa's sash and vanes (quest item from the Hush, consumed at the Institute)
    rows.append(g.V.clone_row("special_items.csv", "planetkiller", **{
        "name": "Lacrimosa's Sash and Vanes", "id": "rsl_lacrimosa_sash", "tags": "mission_item, no_drop",
        "base price": 1, "icon": "graphics/rsl/icons/cargo/rsl_lacrimosa_sash.png", "plugin params": "",
        "desc": SASH_DESC, "order": 296}))
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
    # the Lacrimosa questline's sites
    "rsl_desc_buoy": "A Domain-era listening buoy of the Antiphon Institute, left on the fringe to record the "
                     "harmonic flux of hyperspace storms. Two centuries later some of them still listen.",
    "rsl_desc_institute": "The Antiphon Institute: a Domain hyperspace-physics laboratory, a spindle of dark habitat "
                          "rings around a dock built for one capital ship. The Cantorate's ancestors fled it two "
                          "centuries ago, and chose to forget where it was.",
    "rsl_desc_echo": "A Lattice hull of a pattern two centuries old, drifting in the abyss. Its crew are long dead. Its "
                     "core still keeps time.",
    "rsl_desc_score_cache": "A Domain-era data cache of the Antiphon Institute, scored with five empty lines like a "
                            "stave. Someone hid it here on purpose.",
    "rsl_desc_venns_rest": "A cryogenic vault grown into a cold rock at the edge of the Sector, humming at the edge "
                           "of hearing. On no chart.",
    "rsl_desc_venn_rock": "A cold, airless rock circling a dim red star. Its only feature is the vault someone "
                          "grew into it.",
    "rsl_desc_graveyard": "Where the First Chorus died. Lattice wrecks hang in a ring in the dark, and the abyss hums "
                          "with them.",
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
    rules(g)
    custom_entities(g)
    drop_groups(g)
    skills(g)
    bounties(g)
    nexerelin(g)
