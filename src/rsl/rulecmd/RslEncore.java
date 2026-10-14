package rsl.rulecmd;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.campaign.CampaignFleetAPI;
import com.fs.starfarer.api.campaign.CargoAPI;
import com.fs.starfarer.api.campaign.InteractionDialogAPI;
import com.fs.starfarer.api.campaign.InteractionDialogPlugin;
import com.fs.starfarer.api.campaign.OptionPanelAPI;
import com.fs.starfarer.api.campaign.SectorEntityToken;
import com.fs.starfarer.api.campaign.TextPanelAPI;
import com.fs.starfarer.api.campaign.rules.MemoryAPI;
import com.fs.starfarer.api.combat.BattleCreationContext;
import com.fs.starfarer.api.combat.EngagementResultAPI;
import com.fs.starfarer.api.impl.campaign.FleetEncounterContext;
import com.fs.starfarer.api.impl.campaign.FleetInteractionDialogPluginImpl;
import com.fs.starfarer.api.impl.campaign.FleetInteractionDialogPluginImpl.FIDConfig;
import com.fs.starfarer.api.impl.campaign.FleetInteractionDialogPluginImpl.FIDDelegate;
import com.fs.starfarer.api.util.Misc;
import rsl.RslIds;
import rsl.campaign.DuelIntel;
import rsl.campaign.EncoreFleets;
import rsl.campaign.RequiemIntel;

import java.util.HashMap;
import java.util.Map;

/**
 * The encore encounters (rsl.campaign.DuelIntel, rsl.campaign.RequiemIntel). Picked for their fleets by
 * {@link rsl.campaign.RslCampaignPlugin}; on "engage" the dialog hands over to vanilla's fleet interaction with a
 * set-piece config (as vanilla's SalvageDefenderInteraction does), whose delegate tells the intel when it closes.
 */
public class RslEncore implements InteractionDialogPlugin {

    private enum Opt { DUEL_HEAR, DUEL_ACCEPT, DUEL_CONFIRM, REQ_LOOK, REQ_ENGAGE, REQ_CONFIRM, LEAVE }

    private final String scene;
    private InteractionDialogAPI dialog;
    private CampaignFleetAPI fleet;

    public RslEncore(String scene) {
        this.scene = scene;
    }

    @Override
    public void init(InteractionDialogAPI dialog) {
        this.dialog = dialog;
        SectorEntityToken t = dialog.getInteractionTarget();
        fleet = t instanceof CampaignFleetAPI ? (CampaignFleetAPI) t : null;
        if (fleet != null) dialog.getVisualPanel().showFleetInfo("Your fleet", Global.getSector().getPlayerFleet(),
                fleet.getName(), fleet);
        if ("duel".equals(scene)) duel();
        else requiem();
    }

    private TextPanelAPI t() {
        return dialog.getTextPanel();
    }

    private void options(Object... pairs) {
        OptionPanelAPI o = dialog.getOptionPanel();
        o.clearOptions();
        for (int i = 0; i + 1 < pairs.length; i += 2) o.addOption((String) pairs[i], pairs[i + 1]);
    }

    private void leave(String text) {
        dialog.getOptionPanel().addOption(text, Opt.LEAVE);
        dialog.setOptionOnEscape(text, Opt.LEAVE);
    }

    // ------------------------------------------------------------------------------------------------- the duel

    private void duel() {
        DuelIntel q = DuelIntel.get();
        com.fs.starfarer.api.characters.PersonAPI raike = Global.getSector().getImportantPeople()
                .getPerson(RslIds.PERSON_RAIKE);
        if (raike != null) dialog.getVisualPanel().showPersonInfo(raike, true);
        if (q != null && q.getAttempts() > 0) {
            t().addPara("The Dies Irae is whole again, its seams the violet of the Hush. Raike answers before the "
                    + "channel has finished opening.");
            t().addPara("\"Back so soon? Good. Again, then. From the top.\"");
        } else {
            t().addPara("The ship holding station over the Institute is a Virtuoso. Not a copy of the silhouette, "
                    + "not a Tri-Tachyon hull dressed in Cantorate lines: the same rapier, the same swallowtail, two "
                    + "Sforzando lances on the guard. Its seams burn violet. Somebody grew this core from a shard of the "
                    + "Hush.");
            t().addPara("A woman in a Special Projects flight suit accepts your hail. She looks delighted.");
            t().addPara("\"Captain. Commander Isolde Raike. Director Sung sends his regrets; he hates losing. I don't "
                    + "mind it, as long as it's to someone worth losing to.\"");
        }
        options("Hear her terms", Opt.DUEL_HEAR);
        leave("Leave");
    }

    private void duelTerms() {
        t().addPara("\"Two Virtuosos. There have only ever been two, and there will never be a third. One ship each, "
                + "no seconds, no escorts, no fighters. Your fleet waits here and watches. If I win, you limp home and "
                + "I wait for the next time. If you win...\" She shrugs. \"Then you'll have earned whatever is left of "
                + "my notes.\"");
        TextPanelAPI tp = t();
        tp.setFontSmallInsignia();
        tp.addPara("Commander Raike is a level %s officer: every combat skill elite, and Second Voice.",
                Misc.getHighlightColor(), "" + EncoreFleets.RAIKE_LEVEL);
        tp.addPara("Only the Lacrimosa fights. It will break off before it is disabled.", Misc.getGrayColor());
        tp.setFontInsignia();
        String why = DuelIntel.whyNot();
        if (why != null) {
            tp.addPara(why, Misc.getNegativeHighlightColor());
            options();
            leave("Leave for now");
            return;
        }
        options("Accept the duel", Opt.DUEL_ACCEPT);
        leave("Not yet");
    }

    private void duelConfirm() {
        t().addPara("Your other ships fall back to the Institute's dock and hold. On every bridge, the crews go quiet "
                + "and watch the two swallowtails turn to face each other.");
        DuelIntel q = DuelIntel.get();
        if (q == null || fleet == null) {
            options();
            leave("Leave");
            return;
        }
        q.beginEncounter();
        FIDConfig c = setPiece();
        c.withSalvage = false;
        c.lootCredits = false;
        c.firstTimeEngageOptionText = "Begin the duel";
        c.afterFirstTimeEngageOptionText = "Face her again";
        c.delegate = new Delegate(false);
        engage(c);
    }

    // ------------------------------------------------------------------------------------------------- the Silence

    private void requiem() {
        t().addPara("There is no hail. There is no transponder chatter, no fleet doctrine you recognise, no pattern to "
                + "the formation except that it is perfect. Your sensor officer reads the contacts out and then stops "
                + "reading them out.");
        t().addPara("Every lattice core in your fleet has gone quiet. Not dark: quiet, the way a choir goes quiet "
                + "when something walks into the hall.");
        options("Study the Silence", Opt.REQ_LOOK);
        leave("Leave");
    }

    private void requiemLook() {
        TextPanelAPI tp = t();
        int dp = EncoreFleets.dp(fleet);
        tp.setFontSmallInsignia();
        tp.addPara("The Silence: %s ships, %s deployment points. Omega Tesseracts at its heart, a full Remnant battle "
                + "line around them, every hull under an AI core.", Misc.getHighlightColor(),
                "" + fleet.getFleetData().getNumMembers(), "" + dp);
        tp.addPara("It must be ended in one encounter. If you leave with any of it alive, it remakes itself.",
                Misc.getHighlightColor());
        tp.addPara("This is an optional challenge, meant to be nearly impossible.", Misc.getGrayColor());
        tp.setFontInsignia();
        options("Bring the fight to it", Opt.REQ_ENGAGE);
        leave("Leave it be");
    }

    private void requiemConfirm() {
        t().addPara("You give the order. Somewhere aft, a tuner starts to hum the Lacrimosa's reference pitch, and "
                + "one by one the cores in your fleet take it up.");
        RequiemIntel q = RequiemIntel.get();
        if (q == null || fleet == null) {
            options();
            leave("Leave");
            return;
        }
        q.beginEncounter();
        FIDConfig c = setPiece();
        c.firstTimeEngageOptionText = "Sing";
        c.afterFirstTimeEngageOptionText = "Sing again";
        c.delegate = new Delegate(true);
        engage(c);
    }

    // ------------------------------------------------------------------------------------------------- shared

    /** No other fleets or stations join, no reputation, the player may leave, the encore fleet never pursues. */
    private static FIDConfig setPiece() {
        FIDConfig c = new FIDConfig();
        c.pullInAllies = false;
        c.pullInEnemies = false;
        c.pullInStations = false;
        c.leaveAlwaysAvailable = true;
        c.alwaysLetGo = true;
        c.showTransponderStatus = false;
        c.showFleetAttitude = false;
        c.showCommLinkOption = false;
        c.impactsEnemyReputation = false;
        c.impactsAllyReputation = false;
        c.showWarningDialogWhenNotHostile = false;
        return c;
    }

    private void engage(FIDConfig c) {
        FleetInteractionDialogPluginImpl p = new FleetInteractionDialogPluginImpl(c);
        dialog.setInteractionTarget(fleet);
        dialog.setPlugin(p);
        p.init(dialog);
    }

    /** Fights to the end on the encore side; tells the intel when the encounter closes. */
    private static class Delegate implements FIDDelegate {
        private final boolean requiem;

        Delegate(boolean requiem) {
            this.requiem = requiem;
        }

        @Override
        public void postPlayerSalvageGeneration(InteractionDialogAPI dialog, FleetEncounterContext context,
                                                CargoAPI salvage) {
        }

        @Override
        public void battleContextCreated(InteractionDialogAPI dialog, BattleCreationContext bcc) {
            bcc.aiRetreatAllowed = false;
            bcc.fightToTheLast = true;
            if (!requiem) bcc.objectivesAllowed = false;   // a duel: nothing to capture
        }

        @Override
        public void notifyLeave(InteractionDialogAPI dialog) {
            if (requiem) {
                RequiemIntel q = RequiemIntel.get();
                if (q != null) q.endEncounter();
            } else {
                DuelIntel q = DuelIntel.get();
                if (q != null) q.endEncounter();
            }
        }
    }

    @Override
    public void optionSelected(String optionText, Object optionData) {
        if (optionText != null) t().addPara(optionText, Global.getSettings().getColor("buttonText"));
        if (!(optionData instanceof Opt)) return;
        switch ((Opt) optionData) {
            case DUEL_HEAR:
                duelTerms();
                break;
            case DUEL_ACCEPT:
                t().addPara("\"Wonderful.\" Raike is already moving. \"Don't hold anything back. I won't.\"");
                options("Take the Lacrimosa out", Opt.DUEL_CONFIRM);
                leave("Call it off");
                break;
            case DUEL_CONFIRM:
                duelConfirm();
                break;
            case REQ_LOOK:
                requiemLook();
                break;
            case REQ_ENGAGE:
                t().addPara("Your officers do not argue. One of them asks, very quietly, whether the Lacrimosa was "
                        + "built for this. It was.");
                options("Engage the Silence", Opt.REQ_CONFIRM);
                leave("Not today");
                break;
            case REQ_CONFIRM:
                requiemConfirm();
                break;
            default:
                dialog.dismiss();
                break;
        }
    }

    @Override
    public void optionMousedOver(String optionText, Object optionData) {
    }

    @Override
    public void advance(float amount) {
    }

    @Override
    public void backFromEngagement(EngagementResultAPI battleResult) {
    }

    @Override
    public Object getContext() {
        return null;
    }

    @Override
    public Map<String, MemoryAPI> getMemoryMap() {
        return new HashMap<String, MemoryAPI>();
    }
}
