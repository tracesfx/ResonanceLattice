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

    public static final String FACTION_CHOIR = "rsl_choir";

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
    public static final String KEY_FRACTURE = "rsl_fracture";
    public static final String KEY_ENGINE_STATE = "rsl_engine_state";
    public static final String KEY_PIERCED = "rsl_pierced";
}
