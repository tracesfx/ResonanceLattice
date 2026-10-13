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
import com.fs.starfarer.api.characters.PersonAPI;
import com.fs.starfarer.api.impl.campaign.CoreReputationPlugin.RepActionEnvelope;
import com.fs.starfarer.api.impl.campaign.CoreReputationPlugin.RepActions;
import com.fs.starfarer.api.impl.campaign.ids.Tags;
import com.fs.starfarer.api.impl.campaign.intel.BaseIntelPlugin;
import com.fs.starfarer.api.ui.SectorMapAPI;
import com.fs.starfarer.api.ui.TooltipMakerAPI;
import com.fs.starfarer.api.util.Misc;
import rsl.RslIds;

import java.awt.Color;
import java.util.Set;

/**
 * A Tuners' Contract (CAMPAIGN.md section 8): hunt one raider fleet near Vell within {@link #DURATION} days, for
 * Pitch Glass, credits and Cantorate reputation. Success = the player is in the battle that takes the raiders'
 * flagship (vanilla PersonBountyIntel's rule). Saved with the game (aliased in RslModPlugin).
 */
public class TunerContractIntel extends BaseIntelPlugin implements FleetEventListener {
    public static final float DURATION = 60f;

    private enum Result { NONE, SUCCESS, LOST, EXPIRED }

    private final CampaignFleetAPI fleet;
    private final PersonAPI commander;
    private final StarSystemAPI system;
    private final String targetName;
    private final int glass, credits;
    private float days;
    private Result result = Result.NONE;

    public TunerContractIntel(CampaignFleetAPI fleet, StarSystemAPI system, String targetName, int glass, int credits) {
        this.fleet = fleet;
        this.commander = fleet.getCommander();
        this.system = system;
        this.targetName = targetName;
        this.glass = glass;
        this.credits = credits;
        fleet.addEventListener(this);
    }

    /** The contract in progress, or null. */
    public static TunerContractIntel active() {
        for (IntelInfoPlugin p : Global.getSector().getIntelManager().getIntel(TunerContractIntel.class)) {
            TunerContractIntel c = (TunerContractIntel) p;
            if (!c.isEnding() && !c.isEnded() && c.result == Result.NONE) return c;
        }
        return null;
    }

    public String getSystemName() {
        return system.getNameWithLowercaseType();
    }

    public int getDaysLeft() {
        return (int) Math.max(1f, Math.ceil(DURATION - days));
    }

    @Override
    protected void advanceImpl(float amount) {
        if (result != Result.NONE) return;
        days += Global.getSector().getClock().convertToDays(amount);
        if (days >= DURATION) {
            finish(Result.EXPIRED);
            if (fleet.isAlive()) {
                fleet.clearAssignments();
                Misc.giveStandardReturnAssignments(fleet, Misc.findNearestJumpPointTo(fleet), null, true);
            }
        }
    }

    @Override
    public void reportBattleOccurred(CampaignFleetAPI f, CampaignFleetAPI primaryWinner, BattleAPI battle) {
        if (result != Result.NONE || f != fleet || !battle.isInvolved(fleet) || battle.onPlayerSide(fleet)) return;
        if (fleet.getFlagship() != null && fleet.getFlagship().getCaptain() == commander) return;   // flagship lives
        if (!battle.isPlayerInvolved()) {
            finish(Result.LOST);
            return;
        }
        PitchGlass.add(glass);
        Global.getSector().getPlayerFleet().getCargo().getCredits().add(credits);
        Global.getSector().adjustPlayerReputation(new RepActionEnvelope(RepActions.PERSON_BOUNTY_REWARD, null, null,
                null, true, false), RslIds.FACTION_CHOIR);
        finish(Result.SUCCESS);
        if (fleet.isAlive()) {
            fleet.clearAssignments();
            Misc.giveStandardReturnAssignments(fleet, Misc.findNearestJumpPointTo(fleet), null, true);
        }
    }

    @Override
    public void reportFleetDespawnedToListener(CampaignFleetAPI f, FleetDespawnReason reason, Object param) {
        if (f == fleet && result == Result.NONE) finish(Result.LOST);
    }

    private void finish(Result r) {
        result = r;
        sendUpdateIfPlayerHasIntel(r, false);
        endAfterDelay();
    }

    @Override
    protected void notifyEnded() {
        super.notifyEnded();
        fleet.removeEventListener(this);
    }

    @Override
    protected String getName() {
        String n = "Tuners' Contract";
        if (result == Result.SUCCESS) return n + " - Completed";
        if (result == Result.EXPIRED) return n + " - Expired";
        if (result == Result.LOST) return n + " - Ended";
        return n;
    }

    @Override
    public FactionAPI getFactionForUIColors() {
        return Global.getSector().getFaction(RslIds.FACTION_CHOIR);
    }

    @Override
    public String getIcon() {
        return Global.getSettings().getSpriteName("intel", RslIds.GFX_INTEL_CONTRACT);
    }

    @Override
    public Set<String> getIntelTags(SectorMapAPI map) {
        Set<String> tags = super.getIntelTags(map);
        tags.add(Tags.INTEL_BOUNTY);
        tags.add(Tags.INTEL_ACCEPTED);
        tags.add(RslIds.FACTION_CHOIR);
        return tags;
    }

    @Override
    protected void addBulletPoints(TooltipMakerAPI info, ListInfoMode mode, boolean isUpdate, Color tc, float initPad) {
        Color h = Misc.getHighlightColor();
        bullet(info);
        if (result == Result.NONE) {
            info.addPara("Target: %s in %s", initPad, tc, h, targetName, system.getNameWithLowercaseType());
            info.addPara("%s days left", 0f, tc, h, "" + getDaysLeft());
            info.addPara("Reward: %s Pitch Glass, %s", 0f, tc, h, "" + glass, Misc.getDGSCredits(credits));
        } else if (result == Result.SUCCESS) {
            info.addPara("Received %s Pitch Glass and %s", initPad, tc, h, "" + glass, Misc.getDGSCredits(credits));
        } else if (result == Result.LOST) {
            info.addPara("Someone else silenced the raiders first", initPad, tc);
        } else {
            info.addPara("The raiders moved on before you found them", initPad, tc);
        }
        unindent(info);
    }

    @Override
    public void createSmallDescription(TooltipMakerAPI info, float width, float height) {
        float opad = 10f;
        Color h = Misc.getHighlightColor();
        info.addPara("The Cantorate's tuners need the lanes around Vell quiet. A fleet of %s has been preying on the "
                + "crystal convoys from %s; the Archivists at Tacet Station will pay for its flagship.", opad, h,
                targetName, system.getNameWithLowercaseType());
        addBulletPoints(info, ListInfoMode.IN_DESC);
    }

    @Override
    public SectorEntityToken getMapLocation(SectorMapAPI map) {
        return system.getCenter();
    }

    @Override
    public String getSortString() {
        return "Tuners' Contract";
    }
}
