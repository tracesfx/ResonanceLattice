package rsl.world;

import com.fs.starfarer.api.campaign.econ.Industry;
import com.fs.starfarer.api.impl.campaign.econ.BaseMarketConditionPlugin;
import com.fs.starfarer.api.impl.campaign.ids.Commodities;
import com.fs.starfarer.api.impl.campaign.ids.Industries;
import com.fs.starfarer.api.ui.TooltipMakerAPI;
import com.fs.starfarer.api.util.Misc;

/**
 * Lattice Nurseries (Glasshouse): crystal grown to the pulsar's beat. +1 stability (the hum), +1 transplutonics from a
 * functional Mining industry (crystal tailings), as {@code ResourceDepositsCondition} adds its supply.
 */
public class LatticeNurseries extends BaseMarketConditionPlugin {
    public static final int STABILITY = 1;
    public static final int RARE_METALS = 1;

    @Override
    public void apply(String id) {
        market.getStability().modifyFlat(id, STABILITY, "Lattice nurseries");
        Industry mining = market.getIndustry(Industries.MINING);
        if (mining == null) return;
        if (mining.isFunctional()) {
            mining.supply(id, Commodities.RARE_METALS, RARE_METALS, "Lattice nurseries");
        } else {
            mining.getSupply(Commodities.RARE_METALS).getQuantity().unmodifyFlat(id);
        }
    }

    @Override
    public void unapply(String id) {
        market.getStability().unmodifyFlat(id);
        Industry mining = market.getIndustry(Industries.MINING);
        if (mining != null) mining.getSupply(Commodities.RARE_METALS).getQuantity().unmodifyFlat(id);
    }

    @Override
    public boolean hasCustomTooltip() {
        return true;
    }

    @Override
    protected void createTooltipAfterDescription(TooltipMakerAPI tooltip, boolean expanded) {
        tooltip.addPara("%s stability.", 10f, Misc.getHighlightColor(), "+" + STABILITY);
        tooltip.addPara("%s transplutonics production (Mining).", 10f, Misc.getHighlightColor(), "+" + RARE_METALS);
    }
}
