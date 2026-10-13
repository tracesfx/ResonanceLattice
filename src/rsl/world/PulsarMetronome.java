package rsl.world;

import com.fs.starfarer.api.campaign.PlanetAPI;
import com.fs.starfarer.api.campaign.SpecialItemData;
import com.fs.starfarer.api.campaign.StarSystemAPI;
import com.fs.starfarer.api.campaign.econ.Industry;
import com.fs.starfarer.api.campaign.econ.InstallableIndustryItemPlugin.InstallableItemDescriptionMode;
import com.fs.starfarer.api.campaign.econ.MarketAPI;
import com.fs.starfarer.api.impl.campaign.econ.impl.BaseInstallableItemEffect;
import com.fs.starfarer.api.impl.campaign.econ.impl.ItemEffectsRepo;
import com.fs.starfarer.api.impl.campaign.ids.StarTypes;
import com.fs.starfarer.api.ui.TooltipMakerAPI;
import com.fs.starfarer.api.util.Misc;
import rsl.RslIds;

/**
 * Pulsar Metronome (Luthier's Workshop, CAMPAIGN.md section 8): a colony item for a Waystation (special_items.csv
 * plugin params "waystation"; no vanilla item uses that slot). A navigation clock keyed to a pulsar: +accessibility and
 * +stability, more in a system with a neutron star. Registered in {@link ItemEffectsRepo#ITEM_EFFECTS} on application
 * load (the map is static, nothing is saved).
 */
public class PulsarMetronome extends BaseInstallableItemEffect {
    public static final float ACCESS = 0.15f, ACCESS_PULSAR = 0.25f;
    public static final int STABILITY = 1, STABILITY_PULSAR = 2;

    public PulsarMetronome() {
        super(RslIds.ITEM_METRONOME);
    }

    public static void register() {
        ItemEffectsRepo.ITEM_EFFECTS.put(RslIds.ITEM_METRONOME, new PulsarMetronome());
    }

    private static boolean pulsar(MarketAPI market) {
        StarSystemAPI s = market == null ? null : market.getStarSystem();
        if (s == null) return false;
        for (PlanetAPI p : s.getPlanets()) {
            if (p.isStar() && StarTypes.NEUTRON_STAR.equals(p.getTypeId())) return true;
        }
        return false;
    }

    @Override
    public void apply(Industry industry) {
        MarketAPI m = industry.getMarket();
        boolean pulsar = pulsar(m);
        String name = Misc.ucFirst(spec.getName().toLowerCase());
        m.getAccessibilityMod().modifyFlat(id, pulsar ? ACCESS_PULSAR : ACCESS, name);
        m.getStability().modifyFlat(id, pulsar ? STABILITY_PULSAR : STABILITY, name);
    }

    @Override
    public void unapply(Industry industry) {
        MarketAPI m = industry.getMarket();
        m.getAccessibilityMod().unmodifyFlat(id);
        m.getStability().unmodifyFlat(id);
    }

    @Override
    protected void addItemDescriptionImpl(Industry industry, TooltipMakerAPI text, SpecialItemData data,
                                          InstallableItemDescriptionMode mode, String pre, float pad) {
        text.addPara(pre + "Increases accessibility by %s and stability by %s; %s and %s in a system with a "
                        + "neutron star.", pad, Misc.getHighlightColor(),
                "" + Math.round(ACCESS * 100f) + "%", "" + STABILITY,
                "" + Math.round(ACCESS_PULSAR * 100f) + "%", "" + STABILITY_PULSAR);
    }
}
