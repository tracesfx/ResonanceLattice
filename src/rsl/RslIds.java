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

    // public static final String FACTION_MAIN = "rsl_faction";
    // public static final String HULL_FRIGATE = "rsl_frigate";
}
