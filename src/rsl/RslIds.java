package rsl;

/**
 * Every data id the Java code uses, in one place.
 *
 * validate_mod.py resolves constants whose names start with HULL_, VARIANT_, WEAPON_, WING_, HULLMOD_, SYSTEM_,
 * FACTION_, CONDITION_, INDUSTRY_, SUBMARKET_, COMMODITY_, ITEM_, ENTITY_, PROJ_, ABILITY_ or SKILL_ against the
 * mod's and vanilla's data, so a typo fails the build instead of returning null in game. Name other strings
 * (memory keys, entity instance ids, stat-mod ids) with a different prefix, e.g. MEM_, ID_, MOD_.
 */
public final class RslIds {
    private RslIds() {
    }

    /** The Cantorate of Vell (display name; the id predates the rename). */
    public static final String FACTION_CHOIR = "rsl_choir";

    public static final String COMMODITY_PITCHGLASS = "rsl_pitchglass";
    public static final String ITEM_BP_HULLS = "rsl_bp_hulls_package";
    public static final String ITEM_BP_WEAPONS = "rsl_bp_weapons_package";
    public static final String ITEM_BP_WINGS = "rsl_bp_wings_package";
    public static final String ITEM_METRONOME = "rsl_pulsar_metronome";
    public static final String HULLMOD_CONCERT_PITCH = "rsl_concert_pitch";

    /** Player fleet memory: Lattice Tuning bought at the Workshop (expires after 30 days). */
    public static final String MEM_TUNED = "$rsl_tuned";
    /** Sector memory: the tuners' contract board is empty until this expires. */
    public static final String MEM_CONTRACT_COOLDOWN = "$rsl_contractCooldown";
    /** Fleet memory: a fleet of the Hush (Stage 5 boss); its Lattice wrecks yield triple Pitch Glass. */
    public static final String MEM_HUSH_FLEET = "$rsl_hush";
    /** settings.json graphics "intel" key of the contract intel icon. */
    public static final String GFX_INTEL_CONTRACT = "rsl_contract";

    public static final String MOD_NEXERELIN = "nexerelin";

    /** Sector memory: the Cantorate's starting relations were applied to this save. */
    public static final String MEM_RELATIONS_SET = "$rsl_relationsSet";
    /** Sector memory: Vell was generated in this save (never regenerated, even if it is later destroyed). */
    public static final String MEM_VELL_GENERATED = "$rsl_vellGenerated";

    // Vell (rsl.world.VellGen)
    public static final String INDUSTRY_CANTOR_ARRAY = "rsl_cantor_array";
    public static final String CONDITION_NURSERIES = "rsl_lattice_nurseries";
    public static final String MARKET_CODA = "rsl_coda";
    public static final String MARKET_GLASSHOUSE = "rsl_glasshouse";
    public static final String MARKET_TACET = "rsl_tacet";
    public static final String ID_VELL_STAR = "rsl_vell_star";
    public static final String ID_TACET = "rsl_tacet_station";
    public static final String ID_TENUTO = "rsl_tenuto";
    public static final String ID_BASSO = "rsl_basso";
    public static final String ID_CODA = "rsl_coda_planet";
    public static final String ID_GLASSHOUSE = "rsl_glasshouse_planet";
    public static final String ID_CANTOR_ARRAY = "rsl_cantor_array_station";
    public static final String ID_VELL_RELAY = "rsl_vell_relay";
    public static final String ID_VELL_BUOY = "rsl_vell_buoy";
    public static final String ID_VELL_SENSOR = "rsl_vell_sensor";
    public static final String PERSON_PRECENTOR = "rsl_precentor";
    public static final String PERSON_TANH = "rsl_tanh";
    public static final String PERSON_ABELARD = "rsl_abelard";

    // The Lacrimosa questline (Stage 5; rsl.campaign.LacrimosaIntel holds the state)
    /** Global memory: the player was given the Unsung (exactly once). */
    public static final String MEM_VIRTUOSO_GRANTED = "$rsl_virtuosoGranted";
    /** Global memory: the Lacrimosa was completed (the Unsung became the Virtuoso). */
    public static final String MEM_VIRTUOSO_UPGRADED = "$rsl_virtuosoUpgraded";
    /** Global memory: the player refused Director Sung (opens the Special Projects bounty). */
    public static final String MEM_REFUSED_SUNG = "$rsl_qRefusedSung";
    /** Global memory: "chorus" or "solo", the council's verdict (beat 4). */
    public static final String MEM_PATH = "$rsl_qPath";
    /** Global memory: the Hush was silenced (beat 5). */
    public static final String MEM_HUSH_DONE = "$rsl_qHushDone";
    /** Global memory: the quest ended because the player sold the core to Tri-Tachyon. */
    public static final String MEM_SOLD = "$rsl_qSold";
    /** Global memory: the player was told that Archivist Tanh is waiting (one campaign message). */
    public static final String MEM_HINTED = "$rsl_qHinted";
    /** Global memory: the Institute's spare frame was used (fallback for a lost Unsung). */
    public static final String MEM_SPARE_USED = "$rsl_qSpareUsed";
    /** Player fleet memory: the Virtuoso's seams glow Hush violet (cosmetic, Workshop). */
    public static final String MEM_HUSH_SEAMS = "$rsl_hushSeams";
    /** Variant tag on the Council's escorts (removed from the fleet after beat 5). */
    public static final String TAG_ESCORT = "rsl_council_escort";
    public static final String ENTITY_BUOY = "rsl_listening_buoy";
    public static final String ENTITY_INSTITUTE = "rsl_antiphon_institute";
    public static final String ENTITY_ECHO = "rsl_hush_echo";
    public static final String ENTITY_GRAVEYARD = "rsl_hush_graveyard";
    public static final String ITEM_SASH = "rsl_lacrimosa_sash";
    public static final String HULLMOD_DEAD_CHORUS = "rsl_dead_chorus";
    public static final String HULLMOD_CHORUS_MOVEMENT = "rsl_chorus_movement";
    public static final String HULLMOD_SOLO_MOVEMENT = "rsl_solo_movement";
    public static final String VARIANT_VIRTUOSO = "rsl_virtuoso_Standard";
    public static final String VARIANT_UNSUNG = "rsl_virtuoso_unsung_Standard";
    public static final String PERSON_SUNG = "rsl_sung";
    public static final String GFX_INTEL_LACRIMOSA = "rsl_lacrimosa";

    public static final String HULL_GRACENOTE = "rsl_gracenote";
    public static final String HULL_CONDUCTOR = "rsl_conductor";
    public static final String HULL_VIRTUOSO = "rsl_virtuoso";
    public static final String HULL_UNSUNG = "rsl_virtuoso_unsung";
    public static final String HULL_CANTOR = "rsl_cantor";

    public static final String HULLMOD_CORE = "rsl_lattice_core";
    public static final String HULLMOD_BRIDGE = "rsl_conductors_bridge";
    public static final String HULLMOD_FRACTURE = "rsl_fracture";
    public static final String HULLMOD_STOLEN_TIME = "rsl_stolen_time";
    public static final String HULLMOD_BRAVURA = "rsl_bravura";
    public static final String HULLMOD_UNBOUND = "rsl_unbound";
    public static final String HULLMOD_BRAVURA_LOCKED = "rsl_bravura_locked";
    public static final String HULLMOD_SAFETY = "safetyoverrides";

    public static final String SYSTEM_PITCHSHIFT = "rsl_pitchshift";
    public static final String SYSTEM_CRESCENDO = "rsl_crescendo";
    public static final String SYSTEM_STILLWATER = "rsl_stillwater";
    public static final String SYSTEM_WARD = "rsl_ward";
    public static final String SYSTEM_SYMSTRIKE = "rsl_symstrike";
    public static final String SYSTEM_GLISSANDO = "rsl_glissando";
    public static final String SYSTEM_GLISSANDO_UNSUNG = "rsl_glissando_unsung";
    public static final String SYSTEM_GRANDCHORUS = "rsl_grandchorus";

    public static final String WEAPON_CHIME_BELL = "rsl_chime_bell";
    public static final String WEAPON_BLOOM_SHARD = "rsl_bloom_shard";
    public static final String WEAPON_SFORZANDO = "rsl_sforzando";
    public static final String WEAPON_SFORZANDO_UNTUNED = "rsl_sforzando_untuned";
    public static final String WEAPON_HARMONIC_SPINAL = "rsl_harmonic_spinal";

    public static final String WEAPON_DECO_HALO_RING = "rsl_deco_halo_ring";
    public static final String WEAPON_DECO_CANTOR_RING = "rsl_deco_cantor_ring";
    public static final String WEAPON_DECO_REFRAIN_R = "rsl_deco_refrain_vane_r";
    public static final String WEAPON_DECO_REFRAIN_L = "rsl_deco_refrain_vane_l";
    public static final String WEAPON_DECO_CONDUCTOR_R = "rsl_deco_conductor_blade_r";
    public static final String WEAPON_DECO_CONDUCTOR_L = "rsl_deco_conductor_blade_l";
    public static final String WEAPON_DECO_VIRTUOSO_R = "rsl_deco_virtuoso_vane_r";
    public static final String WEAPON_DECO_VIRTUOSO_L = "rsl_deco_virtuoso_vane_l";

    /** settings.json "graphics" category holding every glow sprite, keyed by hull id or deco weapon id. */
    public static final String GFX_GLOW = "rsl_glow";
    public static final String GFX_FX = "rsl_fx";

    /** Custom-data keys (ships and the combat engine). */
    public static final String KEY_DATA = "rsl_lattice_data";
    public static final String KEY_MARK_UNTIL = "rsl_mark_until";
    public static final String KEY_STOLEN = "rsl_stolen_total";
    public static final String KEY_KILL_CR = "rsl_kill_cr_paid";
    public static final String KEY_FRACTURE = "rsl_fracture";
    public static final String KEY_ENGINE_STATE = "rsl_engine_state";
    public static final String KEY_PIERCED = "rsl_pierced";
}
