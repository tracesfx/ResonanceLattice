package rsl.hullmods;

import com.fs.starfarer.api.combat.BaseHullMod;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.WeaponAPI;
import com.fs.starfarer.api.combat.listeners.WeaponBaseRangeModifier;
import com.fs.starfarer.api.ui.TooltipMakerAPI;
import rsl.RslIds;

/**
 * Concert Pitch: a rare lattice augment for Lattice hulls (built into both Virtuosos). +{@link #RANGE} base range for
 * every Resonance Lattice weapon (ids rsl_*, decorative parts excluded), +{@link #MAX_CR} maximum combat readiness,
 * +{@link #PEAK} seconds peak performance time and {@link #EMP_RESIST} EMP damage resistance.
 */
public class ConcertPitch extends BaseHullMod {
    public static final float RANGE = 200f;
    public static final float MAX_CR = 0.15f;
    public static final float PEAK = 60f;
    public static final float EMP_RESIST = 0.9f;
    /** Built in with a story point: +SMOD_RANGE more. Enhanced as a hull built-in (the Virtuosos): also CR and peak. */
    public static final float SMOD_RANGE = 100f;
    public static final float ENHANCED_MAX_CR = 0.05f;
    public static final float ENHANCED_PEAK = 30f;
    private static final String MOD_ID = "rsl_concert_pitch";

    @Override
    public void applyEffectsBeforeShipCreation(HullSize hullSize, MutableShipStatsAPI stats, String id) {
        stats.getMaxCombatReadiness().modifyFlat(id, MAX_CR, "Concert Pitch");
        stats.getPeakCRDuration().modifyFlat(id, PEAK);
        stats.getEmpDamageTakenMult().modifyMult(id, 1f - EMP_RESIST);
        if (stats.getVariant() != null && stats.getVariant().getSModdedBuiltIns().contains(MOD_ID)) {
            stats.getMaxCombatReadiness().modifyFlat(id + "_enh", ENHANCED_MAX_CR, "Concert Pitch (enhanced)");
            stats.getPeakCRDuration().modifyFlat(id + "_enh", ENHANCED_PEAK);
        }
    }

    @Override
    public void applyEffectsAfterShipCreation(ShipAPI ship, String id) {
        if (!ship.hasListenerOfClass(LatticeRange.class)) ship.addListener(new LatticeRange());
    }

    /** +RANGE flat base range on Lattice weapons only. */
    public static class LatticeRange implements WeaponBaseRangeModifier {
        @Override
        public float getWeaponBaseRangePercentMod(ShipAPI ship, WeaponAPI weapon) {
            return 0f;
        }

        @Override
        public float getWeaponBaseRangeMultMod(ShipAPI ship, WeaponAPI weapon) {
            return 1f;
        }

        @Override
        public float getWeaponBaseRangeFlatMod(ShipAPI ship, WeaponAPI weapon) {
            if (weapon == null || weapon.isDecorative() || weapon.getId() == null) return 0f;
            if (!weapon.getId().startsWith("rsl_")) return 0f;
            boolean smod = ship != null && ship.getVariant() != null
                    && (ship.getVariant().getSMods().contains(MOD_ID)
                    || ship.getVariant().getSModdedBuiltIns().contains(MOD_ID));
            return RANGE + (smod ? SMOD_RANGE : 0f);
        }
    }

    @Override
    public boolean isApplicableToShip(ShipAPI ship) {
        return ship != null && ship.getVariant() != null && ship.getVariant().hasHullMod(RslIds.HULLMOD_CORE);
    }

    @Override
    public String getUnapplicableReason(ShipAPI ship) {
        return "Only a lattice core can hold Concert Pitch";
    }

    @Override
    public void addPostDescriptionSection(TooltipMakerAPI t, HullSize hullSize, ShipAPI ship, float width,
                                          boolean isForModSpec) {
        Tip.section(t, "Bonuses");
        Tip.good(t, "%s range for every Resonance Lattice weapon.", "+" + (int) RANGE);
        Tip.good(t, "%s maximum combat readiness, %s seconds of peak performance time.", Tip.pct(MAX_CR),
                "+" + (int) PEAK);
        Tip.good(t, "%s resistance to EMP damage.", Tip.pct(EMP_RESIST));
        Tip.badSection(t, "Requires");
        Tip.bad(t, "A %s (Lattice hulls only).", "lattice core");
        Tip.end(t);
    }

    @Override
    public String getSModDescriptionParam(int index, HullSize hullSize) {
        if (index == 0) return "+" + (int) SMOD_RANGE;
        if (index == 1) return Tip.pct(ENHANCED_MAX_CR);
        if (index == 2) return "+" + (int) ENHANCED_PEAK;
        return null;
    }
}
