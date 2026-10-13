package rsl.campaign;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.campaign.BattleAPI;
import com.fs.starfarer.api.campaign.CampaignEventListener.FleetDespawnReason;
import com.fs.starfarer.api.campaign.CampaignFleetAPI;
import com.fs.starfarer.api.campaign.SpecialItemData;
import com.fs.starfarer.api.campaign.listeners.FleetEventListener;
import com.fs.starfarer.api.util.Misc;
import rsl.RslIds;

/**
 * Pays for silencing the abandoned Array (secret #3): a Cantorate hull blueprint package, {@link #GLASS} Pitch Glass
 * and a Concert Pitch modspec, once per save. Saved on the station fleet (aliased in RslModPlugin). Never removes
 * itself or despawns anything from inside a callback (the engine is iterating the listener list).
 */
public class ArrayListener implements FleetEventListener {
    public static final int GLASS = 100;

    @Override
    public void reportBattleOccurred(CampaignFleetAPI fleet, CampaignFleetAPI primaryWinner, BattleAPI battle) {
        if (battle == null || !battle.isPlayerInvolved() || battle.onPlayerSide(fleet)) return;
        boolean stationDown = fleet.isEmpty() || fleet.getFlagship() == null
                || !RslIds.HULL_CANTOR.equals(fleet.getFlagship().getHullSpec().getBaseHullId());
        if (stationDown) pay();
    }

    @Override
    public void reportFleetDespawnedToListener(CampaignFleetAPI fleet, FleetDespawnReason reason, Object param) {
        CampaignFleetAPI pf = Global.getSector().getPlayerFleet();
        if (reason == FleetDespawnReason.DESTROYED_BY_BATTLE && pf != null
                && pf.getContainingLocation() == fleet.getContainingLocation()) {
            pay();
        }
    }

    private static void pay() {
        if (Global.getSector().getMemoryWithoutUpdate().getBoolean(RslIds.MEM_ARRAY_SILENCED)) return;
        Global.getSector().getMemoryWithoutUpdate().set(RslIds.MEM_ARRAY_SILENCED, true);
        CampaignFleetAPI pf = Global.getSector().getPlayerFleet();
        if (pf == null) return;
        pf.getCargo().addSpecial(new SpecialItemData(RslIds.ITEM_BP_HULLS, null), 1);
        PitchGlass.add(GLASS);
        pf.getCargo().addHullmods(RslIds.HULLMOD_CONCERT_PITCH, 1);
        Global.getSector().getCampaignUI().addMessage("The abandoned Array falls silent. In its crystal heart your "
                + "salvage crews find a Cantorate hull blueprint package, " + GLASS + " Pitch Glass and a Concert "
                + "Pitch augment.", Misc.getHighlightColor());
    }
}
