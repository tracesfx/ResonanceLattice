package rsl;

import com.fs.starfarer.api.Global;
import org.apache.log4j.Logger;

/**
 * Reads LunaLib settings (data/config/LunaSettings.csv: fieldID,fieldName,fieldType,defaultValue,secondaryValue,
 * fieldDescription,minValue,maxValue,tab; fieldType one of Header, Text, Int, Double, String, Boolean, Enum, Keycode,
 * Color, Radio) with safe defaults.
 *
 * LunaLib classes are referenced only inside the nested Luna class, which is first touched after the isModEnabled
 * check. That is the usual optional-dependency pattern (the game JVM runs with -noverify and resolves classes
 * lazily); it compiles here but was not exercised in game without LunaLib. If LunaLib is a hard dependency, just
 * call LunaSettings directly.
 */
public final class RslSettings {
    private static final Logger log = Global.getLogger(RslSettings.class);
    public static final String MOD_ID = "resonance_lattice";

    private RslSettings() {
    }

    public static boolean getBoolean(String fieldId, boolean fallback) {
        if (!Global.getSettings().getModManager().isModEnabled("lunalib")) return fallback;
        try {
            Boolean b = Luna.bool(fieldId);
            return b == null ? fallback : b;
        } catch (Throwable t) {
            log.warn("could not read LunaLib setting " + fieldId, t);
            return fallback;
        }
    }

    public static int getInt(String fieldId, int fallback, int min, int max) {
        if (!Global.getSettings().getModManager().isModEnabled("lunalib")) return fallback;
        try {
            Integer i = Luna.integer(fieldId);
            return i == null ? fallback : Math.max(min, Math.min(max, i));
        } catch (Throwable t) {
            log.warn("could not read LunaLib setting " + fieldId, t);
            return fallback;
        }
    }

    /** The only place that touches LunaLib classes. */
    private static final class Luna {
        static Boolean bool(String fieldId) {
            return lunalib.lunaSettings.LunaSettings.getBoolean(MOD_ID, fieldId);
        }

        static Integer integer(String fieldId) {
            return lunalib.lunaSettings.LunaSettings.getInt(MOD_ID, fieldId);
        }
    }
}
