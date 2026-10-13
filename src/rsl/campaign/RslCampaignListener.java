package rsl.campaign;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.campaign.BaseCampaignEventListener;
import com.fs.starfarer.api.campaign.BattleAPI;
import com.fs.starfarer.api.campaign.CampaignFleetAPI;
import com.fs.starfarer.api.campaign.CargoAPI;
import com.fs.starfarer.api.campaign.FleetEncounterContextPlugin;
import com.fs.starfarer.api.campaign.FleetEncounterContextPlugin.DataForEncounterSide;
import com.fs.starfarer.api.campaign.FleetEncounterContextPlugin.FleetMemberData;
import com.fs.starfarer.api.campaign.FleetEncounterContextPlugin.Status;
import com.fs.starfarer.api.campaign.RepLevel;
import com.fs.starfarer.api.fleet.FleetMemberAPI;
import com.fs.starfarer.api.util.Misc;
import org.apache.log4j.Logger;
import rsl.RslIds;

/**
 * Transient campaign listener (re-added on every load by RslModPlugin):
 * - after a battle the player wins, Pitch Glass from every Lattice ship the enemy lost goes into the loot;
 * - at the end of each month, the Cantorate pays a Cooperative player a stipend, and a player ready for the
 *   Lacrimosa questline is told once that Archivist Tanh is waiting.
 */
public class RslCampaignListener extends BaseCampaignEventListener {
    private static final Logger log = Global.getLogger(RslCampaignListener.class);

    public RslCampaignListener() {
        super(false);
    }

    @Override
    public void reportEncounterLootGenerated(FleetEncounterContextPlugin plugin, CargoAPI loot) {
        try {
            BattleAPI battle = plugin == null ? null : plugin.getBattle();
            if (battle == null || loot == null || !battle.isPlayerInvolved()) return;
            int glass = 0;
            for (CampaignFleetAPI fleet : battle.getNonPlayerSideSnapshot()) {
                DataForEncounterSide data = plugin.getDataFor(fleet);
                if (data == null) continue;
                int mult = fleet.getMemoryWithoutUpdate().getBoolean(RslIds.MEM_HUSH_FLEET) ? PitchGlass.HUSH_MULT : 1;
                for (FleetMemberData d : data.getOwnCasualties()) {
                    if (d.getStatus() != Status.DISABLED && d.getStatus() != Status.DESTROYED) continue;
                    FleetMemberAPI m = d.getMember();
                    if (m == null || m.isFighterWing() || m.getHullSpec() == null) continue;
                    String base = m.getHullSpec().getBaseHullId();
                    if (base == null || !base.startsWith("rsl_")) continue;
                    glass += PitchGlass.salvageFor(m.getHullSpec().getHullSize()) * mult;
                }
            }
            if (glass > 0) loot.addCommodity(RslIds.COMMODITY_PITCHGLASS, glass);
        } catch (Throwable t) {
            log.warn("Resonance Lattice: Pitch Glass salvage skipped", t);
        }
    }

    @Override
    public void reportEconomyMonthEnd() {
        if (Global.getSector().getFaction(RslIds.FACTION_CHOIR) == null) return;
        hintLacrimosa();
        if (!PitchGlass.rep().isAtWorst(RepLevel.COOPERATIVE)) return;
        PitchGlass.add(PitchGlass.STIPEND);
        Global.getSector().getCampaignUI().addMessage(
                "The Cantorate's Luthiers send you " + PitchGlass.STIPEND + " Pitch Glass in thanks.",
                Misc.getTextColor(), "" + PitchGlass.STIPEND, null, Misc.getHighlightColor(), null);
    }

    /** Once the player is ready for the questline: a single message pointing at any Cantorate market. */
    private static void hintLacrimosa() {
        try {
            if (Global.getSector().getMemoryWithoutUpdate().getBoolean(RslIds.MEM_HINTED)) return;
            if (!Lacrimosa.canStart() || !LacrimosaIntel.hasCantorateMarket()) return;
            Global.getSector().getMemoryWithoutUpdate().set(RslIds.MEM_HINTED, true);
            Global.getSector().getCampaignUI().addMessage("A sealed message for you has been waiting at Tacet Station "
                    + "for weeks. Any Cantorate market will pass it on.", Misc.getHighlightColor());
        } catch (Throwable t) {
            log.warn("Resonance Lattice: questline hint skipped", t);
        }
    }
}
