package rsl.hullmods;

import com.fs.starfarer.api.combat.BaseHullMod;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.ui.Alignment;
import com.fs.starfarer.api.ui.TooltipMakerAPI;
import com.fs.starfarer.api.util.Misc;

/**
 * The Unsung's Bravura slot: shown (struck-through icon, "INACTIVE" in the tooltip) so the player sees what the full
 * Virtuoso will unlock, but it has no effect at all.
 */
public class BravuraLocked extends BaseHullMod {
    @Override
    public void addPostDescriptionSection(TooltipMakerAPI tooltip, HullSize hullSize, ShipAPI ship, float width,
                                          boolean isForModSpec) {
        tooltip.addSectionHeading("INACTIVE", Misc.getNegativeHighlightColor(), Misc.getDarkHighlightColor(),
                Alignment.MID, 10f);
        tooltip.addPara("The Unsung's core is out of tune and cannot reach Bravura. None of the effects below apply "
                + "until the Virtuoso is restored.", Misc.getNegativeHighlightColor(), 6f);
        Bravura.addEffects(tooltip);
    }

    @Override
    public String getDescriptionParam(int index, HullSize hullSize) {
        return null;
    }
}
