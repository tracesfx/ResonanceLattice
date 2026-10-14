package rsl.campaign;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.campaign.BattleAPI;
import com.fs.starfarer.api.campaign.CampaignEventListener.FleetDespawnReason;
import com.fs.starfarer.api.campaign.CampaignFleetAPI;
import com.fs.starfarer.api.campaign.FactionAPI;
import com.fs.starfarer.api.campaign.SectorEntityToken;
import com.fs.starfarer.api.campaign.StarSystemAPI;
import com.fs.starfarer.api.campaign.comm.IntelInfoPlugin;
import com.fs.starfarer.api.campaign.listeners.FleetEventListener;
import com.fs.starfarer.api.fleet.FleetMemberAPI;
import com.fs.starfarer.api.impl.campaign.ids.MemFlags;
import com.fs.starfarer.api.impl.campaign.ids.Tags;
import com.fs.starfarer.api.impl.campaign.intel.BaseIntelPlugin;
import com.fs.starfarer.api.ui.SectorMapAPI;
import com.fs.starfarer.api.ui.TooltipMakerAPI;
import com.fs.starfarer.api.util.Misc;
import org.apache.log4j.Logger;
import rsl.RslIds;

import java.awt.Color;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;

/**
 * "Requiem" (user, 2026-10-13): the optional end-game challenge. The Domain built the Lacrimosa to be the one voice no
 * machine could jam; now that it sings again, something that has listened since the Collapse comes to silence it. The
 * Silence ({@link EncoreFleets#silence}, 1,500+ DP of Remnant and Omega hulls) holds station in a remote system and
 * never comes after the player.
 *
 * It must be beaten in ONE encounter (as many engagements as it takes inside one dialog): if the player leaves with
 * any of it alive, it remakes itself at full strength. Ending it builds Encore into the Lacrimosa and pays
 * {@link #REWARD_GLASS} Pitch Glass. Opens {@link #DELAY_DAYS} days after the Lacrimosa's completion.
 */
public class RequiemIntel extends BaseIntelPlugin implements FleetEventListener {
    private static final Logger log = Global.getLogger(RequiemIntel.class);
    public static final int REWARD_GLASS = 1000;
    public static final float DELAY_DAYS = 45f;

    private CampaignFleetAPI fleet;
    private SectorEntityToken anchor;
    private boolean won, encounter, remake;
    private int attempts;
    private final List<CampaignFleetAPI> release = new ArrayList<CampaignFleetAPI>();

    public static RequiemIntel get() {
        for (IntelInfoPlugin p : Global.getSector().getIntelManager().getIntel(RequiemIntel.class)) {
            RequiemIntel q = (RequiemIntel) p;
            if (!q.isEnded()) return q;
        }
        return null;
    }

    public static boolean started() {
        return !Global.getSector().getIntelManager().getIntel(RequiemIntel.class).isEmpty()
                || Global.getSector().getMemoryWithoutUpdate().getBoolean(RslIds.MEM_REQUIEM_WON);
    }

    public static RequiemIntel start() {
        if (get() != null) return get();
        StarSystemAPI sys = pickSystem();
        if (sys == null || sys.getStar() == null) return null;
        RequiemIntel q = new RequiemIntel();
        q.anchor = sys.getStar();
        q.spawn();
        q.setImportant(true);
        Global.getSector().getIntelManager().addIntel(q);
        return q;
    }

    /** The wild system farthest from the Sector's core. */
    private static StarSystemAPI pickSystem() {
        StarSystemAPI best = null;
        float far = -1f;
        for (StarSystemAPI s : Global.getSector().getStarSystems()) {
            if (!LacrimosaIntel.isWildSystem(s)) continue;
            float d = s.getLocation().length();
            if (d > far) {
                far = d;
                best = s;
            }
        }
        return best;
    }

    private void spawn() {
        fleet = EncoreFleets.silence(anchor);
        fleet.addEventListener(this);
    }

    public CampaignFleetAPI getFleet() {
        return fleet;
    }

    public String systemName() {
        return anchor != null && anchor.getStarSystem() != null ? anchor.getStarSystem().getNameWithLowercaseType()
                : "an unknown system";
    }

    public void beginEncounter() {
        encounter = true;
        attempts++;
        fleet.getMemoryWithoutUpdate().set(MemFlags.MEMORY_KEY_MAKE_HOSTILE, true);
    }

    /** The encounter dialog closed: anything left of the Silence remakes itself. */
    public void endEncounter() {
        encounter = false;
        if (won) return;
        if (fleet == null || !fleet.isAlive() || fleet.isEmpty()) {
            victory();
            return;
        }
        remake = true;
    }

    private void victory() {
        if (won) return;
        won = true;
        if (!Global.getSector().getMemoryWithoutUpdate().getBoolean(RslIds.MEM_REQUIEM_WON)) {
            Global.getSector().getMemoryWithoutUpdate().set(RslIds.MEM_REQUIEM_WON, true);
            FleetMemberAPI v = Lacrimosa.findHull(RslIds.HULL_VIRTUOSO);
            if (v != null && !v.getVariant().hasHullMod(RslIds.HULLMOD_ENCORE)) {
                v.getVariant().addPermaMod(RslIds.HULLMOD_ENCORE, false);
                v.updateStats();
            }
            PitchGlass.add(REWARD_GLASS);
            Global.getSector().getCampaignUI().addMessage("The Silence is ended. For a long moment every lattice core "
                    + "in your fleet sings on its own, unprompted, the same note. Encore is now part of the Lacrimosa, "
                    + "and " + REWARD_GLASS + " Pitch Glass is yours.", Misc.getTextColor(), "Encore",
                    "" + REWARD_GLASS, Misc.getHighlightColor(), Misc.getHighlightColor());
        }
        if (fleet != null) release.add(fleet);
        sendUpdateIfPlayerHasIntel(null, false);
        endAfterDelay();
    }

    @Override
    protected void advanceImpl(float amount) {
        try {
            if (!release.isEmpty()) {
                for (CampaignFleetAPI f : new ArrayList<CampaignFleetAPI>(release)) {
                    f.removeEventListener(this);
                    if (f.isAlive()) f.despawn();
                }
                release.clear();
            }
            if (Global.getSector().getCampaignUI().isShowingDialog()) return;
            if (encounter && Global.getSector().getPlayerFleet().getBattle() == null) {
                log.warn("Resonance Lattice: requiem encounter ended without notice");
                endEncounter();   // a missed notifyLeave
            }
            if (won || encounter) return;
            if (remake && fleet != null) {   // the Silence remakes itself out of sight
                remake = false;
                fleet.removeEventListener(this);   // safe here: not inside a fleet callback
                if (fleet.isAlive()) fleet.despawn();
                fleet = null;
            }
            if (fleet == null || !fleet.isAlive()) {
                if (anchor == null || anchor.getContainingLocation() == null) {
                    endImmediately();
                    return;
                }
                spawn();
            }
        } catch (Throwable t) {
            log.error("Resonance Lattice: requiem tick failed", t);
        }
    }

    @Override
    public void reportBattleOccurred(CampaignFleetAPI f, CampaignFleetAPI primaryWinner, BattleAPI battle) {
        if (f == fleet && fleet != null && fleet.isEmpty()) victory();
    }

    @Override
    public void reportFleetDespawnedToListener(CampaignFleetAPI f, FleetDespawnReason reason, Object param) {
        if (f != fleet) return;
        if (reason == FleetDespawnReason.DESTROYED_BY_BATTLE) victory();
        else if (!won) fleet = null;
    }

    @Override
    protected void notifyEnded() {
        super.notifyEnded();
        if (fleet != null) fleet.removeEventListener(this);
    }

    @Override
    protected String getName() {
        return won ? "Requiem - Completed" : "Requiem";
    }

    @Override
    public FactionAPI getFactionForUIColors() {
        return Global.getSector().getFaction(RslIds.FACTION_CHOIR);
    }

    @Override
    public String getIcon() {
        return Global.getSettings().getSpriteName("intel", RslIds.GFX_INTEL_REQUIEM);
    }

    @Override
    public Set<String> getIntelTags(SectorMapAPI map) {
        Set<String> tags = super.getIntelTags(map);
        tags.add(Tags.INTEL_STORY);
        tags.add(RslIds.FACTION_CHOIR);
        return tags;
    }

    @Override
    protected void addBulletPoints(TooltipMakerAPI info, ListInfoMode mode, boolean isUpdate, Color tc, float initPad) {
        bullet(info);
        if (won) {
            info.addPara("Encore is built into the Lacrimosa", initPad, tc, Misc.getHighlightColor(), "Encore");
        } else {
            info.addPara("The Silence waits in %s", initPad, tc, Misc.getHighlightColor(), systemName());
            info.addPara("Optional. Nearly impossible.", 0f, tc);
        }
        unindent(info);
    }

    @Override
    public void createSmallDescription(TooltipMakerAPI info, float width, float height) {
        float opad = 10f;
        Color h = Misc.getHighlightColor();
        if (won) {
            info.addPara("The Silence is ended. Whatever had listened since the Collapse is not listening any more, "
                    + "and the Lacrimosa sang to the end of it.", opad);
        } else {
            info.addPara("Archivist Tanh's receivers have caught something answering the Lacrimosa: not a voice, an "
                    + "absence, a band of hyperspace where every pulsar-locked signal simply stops. Saskia Venn's last "
                    + "Score named what the Domain Navy built the Virtuoso to fight. It has come to %s.", opad, h,
                    systemName());
            info.addPara("The Silence: %s deployment points of Remnant and Omega hulls under AI cores. It will not "
                    + "come to you. It must be ended in a single encounter; if you leave with any of it alive, it "
                    + "remakes itself.", opad, h, "" + EncoreFleets.dp(fleet));
            info.addPara("This fight is a challenge for the very best, and nothing in the campaign depends on it.",
                    opad, Misc.getGrayColor());
            if (attempts > 0) info.addPara("Attempts so far: %s.", opad, h, "" + attempts);
        }
        addBulletPoints(info, ListInfoMode.IN_DESC);
    }

    @Override
    public SectorEntityToken getMapLocation(SectorMapAPI map) {
        return fleet != null && fleet.isAlive() ? fleet : anchor;
    }

    @Override
    public String getSortString() {
        return "Lacrimosa 3";
    }

    /** Console: {@code runcode rsl.campaign.RequiemIntel.debug()} opens the challenge now. */
    public static void debug() {
        try {
            RequiemIntel q = start();
            log.info("Resonance Lattice: requiem " + (q == null ? "could not start" : "in " + q.systemName()));
        } catch (Throwable t) {
            log.error("Resonance Lattice: requiem debug failed", t);
        }
    }

    public static void debugWin() {
        RequiemIntel q = get();
        if (q != null) q.victory();
    }
}
