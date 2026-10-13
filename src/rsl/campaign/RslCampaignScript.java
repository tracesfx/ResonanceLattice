package rsl.campaign;

import com.fs.starfarer.api.EveryFrameScript;
import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.campaign.CampaignFleetAPI;
import com.fs.starfarer.api.campaign.CampaignTerrainAPI;
import com.fs.starfarer.api.campaign.LocationAPI;
import com.fs.starfarer.api.fleet.FleetMemberAPI;
import com.fs.starfarer.api.impl.campaign.terrain.PulsarBeamTerrainPlugin;
import com.fs.starfarer.api.util.IntervalUtil;
import com.fs.starfarer.api.util.Misc;
import org.apache.log4j.Logger;
import rsl.RslIds;

/**
 * Transient campaign script (re-added on every load by RslModPlugin). Secret #6, "the pulsar choir": the first time
 * the player flies a Virtuoso (either hull) through Vell's pulsar beam, every core in the fleet rings with the pulsar,
 * once, and the whole fleet's combat readiness is restored.
 */
public class RslCampaignScript implements EveryFrameScript {
    private static final Logger log = Global.getLogger(RslCampaignScript.class);
    private final IntervalUtil interval = new IntervalUtil(0.2f, 0.3f);
    private boolean broken;

    @Override
    public void advance(float amount) {
        if (broken) return;
        interval.advance(Global.getSector().getClock().convertToDays(amount));
        if (!interval.intervalElapsed()) return;
        try {
            pulsarChoir();
        } catch (Throwable t) {
            broken = true;
            log.error("Resonance Lattice: campaign script disabled after an error", t);
        }
    }

    private static void pulsarChoir() {
        if (Global.getSector().getMemoryWithoutUpdate().getBoolean(RslIds.MEM_PULSAR_CHOIR)) return;
        CampaignFleetAPI pf = Global.getSector().getPlayerFleet();
        if (pf == null) return;
        LocationAPI loc = pf.getContainingLocation();
        if (!(loc instanceof com.fs.starfarer.api.campaign.StarSystemAPI)
                || !rsl.world.VellGen.SYSTEM_NAME.equals(((com.fs.starfarer.api.campaign.StarSystemAPI) loc).getBaseName())) {
            return;
        }
        if (Lacrimosa.findHull(RslIds.HULL_VIRTUOSO) == null && Lacrimosa.findUnsung() == null) return;
        boolean inBeam = false;
        for (CampaignTerrainAPI t : loc.getTerrainCopy()) {
            if (t.getPlugin() instanceof PulsarBeamTerrainPlugin && t.getPlugin().containsEntity(pf)) {
                inBeam = true;
                break;
            }
        }
        if (!inBeam) return;
        Global.getSector().getMemoryWithoutUpdate().set(RslIds.MEM_PULSAR_CHOIR, true);
        for (FleetMemberAPI m : pf.getFleetData().getMembersListCopy()) {
            m.getRepairTracker().setCR(Math.max(m.getRepairTracker().getCR(), m.getRepairTracker().getMaxCR()));
        }
        Global.getSector().getCampaignUI().addMessage("The pulsar sweeps across the Virtuoso and every hull in your "
                + "fleet answers it, one clear note held for a full rotation. On Coda, a whole shift of tuners stops "
                + "to listen. Your fleet's readiness is fully restored.", Misc.getHighlightColor());
    }

    @Override
    public boolean isDone() {
        return false;
    }

    @Override
    public boolean runWhilePaused() {
        return false;
    }
}
