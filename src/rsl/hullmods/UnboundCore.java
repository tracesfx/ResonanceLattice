package rsl.hullmods;

import com.fs.starfarer.api.combat.BaseHullMod;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import rsl.RslIds;

import java.awt.Color;

/**
 * The Virtuoso's "unbound core": vanilla Safety Overrides refuses capitals, so the Virtuoso gets its own copy of
 * the SO effects (values from data/hullmods/SafetyOverrides.java, capital column). Only the full Virtuoso can
 * install it; Stolen Time is what pays for the peak-time cut (DESIGN.md 3.9, "Unique synergy").
 */
public class UnboundCore extends BaseHullMod {
    public static final float SPEED = 15f;
    public static final float FLUX_MULT = 2f;
    public static final float PEAK_MULT = 0.33f;
    public static final float RANGE_THRESHOLD = 450f;
    public static final float RANGE_MULT = 0.25f;
    private static final Color ENGINE = new Color(255, 214, 140, 255);

    @Override
    public void applyEffectsBeforeShipCreation(HullSize hullSize, MutableShipStatsAPI stats, String id) {
        stats.getMaxSpeed().modifyFlat(id, SPEED);
        stats.getAcceleration().modifyFlat(id, SPEED * 2f);
        stats.getDeceleration().modifyFlat(id, SPEED * 2f);
        stats.getZeroFluxMinimumFluxLevel().modifyFlat(id, 2f);
        stats.getFluxDissipation().modifyMult(id, FLUX_MULT);
        stats.getPeakCRDuration().modifyMult(id, PEAK_MULT);
        stats.getVentRateMult().modifyMult(id, 0f);
        stats.getWeaponRangeThreshold().modifyFlat(id, RANGE_THRESHOLD);
        stats.getWeaponRangeMultPastThreshold().modifyMult(id, RANGE_MULT);
    }

    @Override
    public void advanceInCombat(ShipAPI ship, float amount) {
        ship.getEngineController().fadeToOtherColor(this, ENGINE, null, 1f, 0.4f);
        ship.getEngineController().extendFlame(this, 0.25f, 0.25f, 0.25f);
    }

    @Override
    public boolean isApplicableToShip(ShipAPI ship) {
        return ship != null && RslIds.HULL_VIRTUOSO.equals(ship.getHullSpec().getHullId());
    }

    @Override
    public String getUnapplicableReason(ShipAPI ship) {
        return "Only the Virtuoso's core can be unbound";
    }

    @Override
    public boolean showInRefitScreenModPickerFor(ShipAPI ship) {
        return isApplicableToShip(ship);
    }

    @Override
    public String getDescriptionParam(int index, HullSize hullSize) {
        switch (index) {
            case 0:
                return "" + (int) SPEED;
            case 1:
                return "" + (int) FLUX_MULT;
            case 2:
                return "" + (int) RANGE_THRESHOLD;
            default:
                return null;
        }
    }
}
