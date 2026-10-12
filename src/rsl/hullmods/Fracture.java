package rsl.hullmods;

import com.fs.starfarer.api.combat.BaseHullMod;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.ui.TooltipMakerAPI;
import rsl.combat.LatticeDealtModifier;

/** Staccato: the stacks and the shatter are applied by {@link LatticeDealtModifier}; this class only describes it. */
public class Fracture extends BaseHullMod {
    @Override
    public void addPostDescriptionSection(TooltipMakerAPI t, HullSize hullSize, ShipAPI ship, float width,
                                          boolean isForModSpec) {
        Tip.section(t, "Fracture");
        Tip.good(t, "Every hit from this ship on enemy hull or armor adds a Fracture stack, up to %s.",
                "" + LatticeDealtModifier.FRACTURE_MAX);
        Tip.good(t, "Stacks fade after %s seconds without a new hit.", (int) LatticeDealtModifier.FRACTURE_TIMEOUT + "");
        Tip.section(t, "Shatter");
        Tip.good(t, "The next hit on a fully fractured ship shatters the plating: %s armor removed around the "
                + "impact, then the stacks reset.", "" + (int) LatticeDealtModifier.FRACTURE_SHATTER);
        Tip.end(t);
    }

    @Override
    public String getSModDescriptionParam(int index, HullSize hullSize) {
        if (index == 0) return "" + (LatticeDealtModifier.FRACTURE_MAX - 1);
        if (index == 1) return "" + (int) (LatticeDealtModifier.FRACTURE_SHATTER
                * LatticeDealtModifier.FRACTURE_ENHANCED_SHATTER);
        return null;
    }
}
