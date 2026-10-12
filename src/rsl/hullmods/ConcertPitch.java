package rsl.hullmods;

import com.fs.starfarer.api.combat.BaseHullMod;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import com.fs.starfarer.api.combat.WeaponAPI;
import com.fs.starfarer.api.combat.listeners.WeaponBaseRangeModifier;
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

    @Override
    public void applyEffectsBeforeShipCreation(HullSize hullSize, MutableShipStatsAPI stats, String id) {
        stats.getMaxCombatReadiness().modifyFlat(id, MAX_CR, "Concert Pitch");
        stats.getPeakCRDuration().modifyFlat(id, PEAK);
        stats.getEmpDamageTakenMult().modifyMult(id, 1f - EMP_RESIST);
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
            return weapon.getId().startsWith("rsl_") ? RANGE : 0f;
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
    public String getDescriptionParam(int index, HullSize hullSize) {
        switch (index) {
            case 0:
                return "" + (int) RANGE;
            case 1:
                return (int) (MAX_CR * 100f) + "%";
            case 2:
                return "" + (int) PEAK;
            case 3:
                return (int) (EMP_RESIST * 100f) + "%";
            default:
                return null;
        }
    }
}
