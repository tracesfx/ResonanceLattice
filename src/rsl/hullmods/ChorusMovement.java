package rsl.hullmods;

import com.fs.starfarer.api.combat.BaseHullMod;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import com.fs.starfarer.api.ui.TooltipMakerAPI;
import rsl.RslIds;

/**
 * Chorus Movement (CAMPAIGN.md section 8, the Precentor's path): a sidegrade for the full Virtuoso. Stolen Time
 * steals less, but half of everything it steals goes to allied ships nearby. The effect lives in
 * {@link StolenTime} (it asks {@link #has}); this class is the tooltip and the fitting rules.
 */
public class ChorusMovement extends BaseHullMod {
    public static final float STEAL_MULT = 0.75f;
    public static final float SHARE = 0.5f;
    public static final float RANGE = 1500f;

    public static boolean has(ShipAPI ship) {
        return ship != null && ship.getVariant() != null
                && ship.getVariant().hasHullMod(RslIds.HULLMOD_CHORUS_MOVEMENT);
    }

    @Override
    public boolean isApplicableToShip(ShipAPI ship) {
        return ship != null && RslIds.HULL_VIRTUOSO.equals(ship.getHullSpec().getHullId())
                && !ship.getVariant().hasHullMod(RslIds.HULLMOD_SOLO_MOVEMENT);
    }

    @Override
    public String getUnapplicableReason(ShipAPI ship) {
        if (ship != null && ship.getVariant().hasHullMod(RslIds.HULLMOD_SOLO_MOVEMENT)) {
            return "The core can hold only one Movement";
        }
        return "Only the Virtuoso's core can be retuned";
    }

    @Override
    public boolean showInRefitScreenModPickerFor(ShipAPI ship) {
        return ship != null && RslIds.HULL_VIRTUOSO.equals(ship.getHullSpec().getHullId());
    }

    @Override
    public void addPostDescriptionSection(TooltipMakerAPI t, HullSize hullSize, ShipAPI ship, float width,
                                          boolean isForModSpec) {
        Tip.section(t, "Bonuses");
        Tip.good(t, "%s of the combat readiness Stolen Time steals is shared among allied ships within %s units.",
                Tip.pct(SHARE), "" + (int) RANGE);
        Tip.badSection(t, "Tradeoffs");
        Tip.bad(t, "Stolen Time steals %s less.", Tip.pct(1f - STEAL_MULT));
        Tip.note(t, "Kill refunds are unchanged. Cannot be combined with Solo Movement.");
        Tip.end(t);
    }
}
