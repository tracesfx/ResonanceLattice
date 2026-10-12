package rsl.hullmods;

import com.fs.starfarer.api.combat.BaseHullMod;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.ui.TooltipMakerAPI;
import rsl.RslIds;

import java.awt.Color;

/**
 * The Virtuoso's "unbound core": vanilla Safety Overrides refuses capitals, so the Virtuoso gets its own copy of
 * the SO effects (values from data/hullmods/SafetyOverrides.java, capital column) without the range penalty.
 * Only the full Virtuoso can install it; Stolen Time is what pays for the peak-time cut (DESIGN.md 3.9, "Unique synergy").
 */
public class UnboundCore extends BaseHullMod {
    public static final float SPEED = 15f;
    public static final float FLUX_MULT = 2f;
    public static final float PEAK_MULT = 0.33f;
    /** Built in with a story point (an expensive hullmod): a permanent readiness cost. */
    public static final float SMOD_MAX_CR = -0.10f;
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
        if (isSMod(stats)) stats.getMaxCombatReadiness().modifyFlat(id + "_smod", SMOD_MAX_CR, "Unbound Core (S-mod)");
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
    public void addPostDescriptionSection(TooltipMakerAPI t, HullSize hullSize, ShipAPI ship, float width,
                                          boolean isForModSpec) {
        Tip.section(t, "Bonuses");
        Tip.good(t, "%s top speed (and a matching boost to acceleration).", "+" + (int) SPEED);
        Tip.good(t, "Flux dissipation %s.", "x" + (int) FLUX_MULT);
        Tip.good(t, "The zero-flux speed boost works at %s flux level.", "any");
        Tip.badSection(t, "Tradeoffs");
        Tip.bad(t, "Active venting is %s.", "disabled");
        Tip.bad(t, "Peak performance time is cut to %s.", "a third");
        Tip.note(t, "Stolen Time pays the readiness back.");
        Tip.end(t);
    }

    @Override
    public boolean isSModEffectAPenalty() {
        return true;
    }

    @Override
    public String getSModDescriptionParam(int index, HullSize hullSize) {
        return index == 0 ? Tip.pct(-SMOD_MAX_CR) : null;
    }
}
