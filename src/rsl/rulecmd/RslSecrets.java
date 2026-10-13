package rsl.rulecmd;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.campaign.CampaignFleetAPI;
import com.fs.starfarer.api.campaign.InteractionDialogAPI;
import com.fs.starfarer.api.campaign.InteractionDialogPlugin;
import com.fs.starfarer.api.campaign.OptionPanelAPI;
import com.fs.starfarer.api.campaign.SectorEntityToken;
import com.fs.starfarer.api.campaign.TextPanelAPI;
import com.fs.starfarer.api.campaign.rules.MemoryAPI;
import com.fs.starfarer.api.combat.EngagementResultAPI;
import com.fs.starfarer.api.impl.campaign.rulecmd.BaseCommandPlugin;
import com.fs.starfarer.api.util.Misc;
import com.fs.starfarer.api.util.Misc.Token;
import rsl.campaign.Lacrimosa;
import rsl.campaign.LacrimosaFleets;
import rsl.campaign.LacrimosaIntel;
import rsl.campaign.ScoresIntel;

import java.util.List;
import java.util.Map;

/**
 * Dialogs of the secrets (CAMPAIGN.md section 7): {@code RslSecrets cache} (a Lost Score cache) and
 * {@code RslSecrets vennsrest} (the cryo station of Venn's Rest). Same takeover pattern as {@link RslWorkshop};
 * both are custom entities, so leaving dismisses the dialog.
 */
public class RslSecrets extends BaseCommandPlugin implements InteractionDialogPlugin {

    private enum Opt { READ, WAKE, LEAVE }

    private static final String MEM_READ = "$rsl_scoreRead";

    private InteractionDialogPlugin originalPlugin;
    private InteractionDialogAPI dialog;
    private Map<String, MemoryAPI> memoryMap;

    @Override
    public boolean execute(String ruleId, InteractionDialogAPI dialog, List<Token> params,
                           Map<String, MemoryAPI> memoryMap) {
        this.dialog = dialog;
        this.memoryMap = memoryMap;
        originalPlugin = dialog.getPlugin();
        dialog.setPlugin(this);
        String cmd = params.isEmpty() ? "" : params.get(0).getString(memoryMap);
        if ("cache".equals(cmd)) cache();
        else if ("vennsrest".equals(cmd)) vennsRest();
        else leave();
        return true;
    }

    private TextPanelAPI t() {
        return dialog.getTextPanel();
    }

    private void only(String leaveText) {
        OptionPanelAPI o = dialog.getOptionPanel();
        o.clearOptions();
        o.addOption(leaveText, Opt.LEAVE);
        dialog.setOptionOnEscape(leaveText, Opt.LEAVE);
    }

    // ------------------------------------------------------------------------------------------------- caches

    private void cache() {
        SectorEntityToken e = dialog.getInteractionTarget();
        t().addPara("A Domain-era data cache, no bigger than a lifeboat, stamped with the crest of the Antiphon "
                + "Institute. Its hull is scored with five parallel lines, like an empty stave.");
        if (e.getMemoryWithoutUpdate().getBoolean(MEM_READ)) {
            t().addPara("Its memory core has already been pulled. The cache is only a shell now.");
            only("Leave");
            return;
        }
        t().addPara("Your salvage chief reports a sealed memory core and a small vault of lattice shards, still "
                + "ringing faintly.");
        OptionPanelAPI o = dialog.getOptionPanel();
        o.clearOptions();
        o.addOption("Recover the core and the shards", Opt.READ);
        o.addOption("Leave", Opt.LEAVE);
        dialog.setOptionOnEscape("Leave", Opt.LEAVE);
    }

    private void read() {
        SectorEntityToken e = dialog.getInteractionTarget();
        if (e.getMemoryWithoutUpdate().getBoolean(MEM_READ)) {
            cache();
            return;
        }
        e.getMemoryWithoutUpdate().set(MEM_READ, true);
        ScoresIntel s = ScoresIntel.getOrCreate(t());
        int i = s.read(t());
        t().addPara("The core holds one file: a tuning score, written out by hand and scanned, with notes in the "
                + "margin.");
        t().addPara(ScoresIntel.SCORES[i], Misc.getGrayColor());
        t().setFontSmallInsignia();
        t().addPara("Gained %s Pitch Glass", Misc.getPositiveHighlightColor(), "" + ScoresIntel.GLASS);
        t().setFontInsignia();
        if (i == 0 && !LacrimosaIntel.started() && Lacrimosa.canStart() && LacrimosaIntel.hasCantorateMarket()) {
            t().addPara("Under the score lies a second file: a recording, weeks old, of a pulsar-locked signal "
                    + "somewhere in hyperspace, flagged by an automated Institute receiver. Someone at Tacet Station "
                    + "would give a great deal to hear it.");
            LacrimosaIntel.start(t());
        }
        if (s.getFound() >= ScoresIntel.SCORES.length && s.getVennsRest() != null) {
            t().addPara("Eight scores. The last one resolves into a navigation fix: a system on the fringe that is on "
                    + "no chart. Venn's Rest.", Misc.getHighlightColor());
        }
        only("Leave");
    }

    // ------------------------------------------------------------------------------------------------- Venn's Rest

    private void vennsRest() {
        ScoresIntel s = ScoresIntel.get();
        SectorEntityToken st = dialog.getInteractionTarget();
        t().addPara("A cryogenic vault grown into a cold rock, the size of a small station, humming at the edge of "
                + "hearing. Someone has painted a single word over its airlock: REST.");
        if (guardNear(st)) {
            t().addPara("Lattice hulls hang around the vault, their seams glowing violet: a sealed remnant of the "
                    + "Hush, left to keep the silence. They turn towards you as one.",
                    Misc.getNegativeHighlightColor());
            only("Leave");
            return;
        }
        if (s != null && s.isMarchettiFound()) {
            t().addPara("The vault is empty now, and very quiet.");
            only("Leave");
            return;
        }
        t().addPara("Inside, a single cryo pod, a single terminal, and a woman's voice recorded two hundred years ago:");
        t().addPara(ScoresIntel.VENN_LAST, Misc.getGrayColor());
        OptionPanelAPI o = dialog.getOptionPanel();
        o.clearOptions();
        o.addOption("Wake the sleeper", Opt.WAKE);
        o.addOption("Leave", Opt.LEAVE);
        dialog.setOptionOnEscape("Leave", Opt.LEAVE);
    }

    private static boolean guardNear(SectorEntityToken st) {
        for (CampaignFleetAPI f : st.getContainingLocation().getFleets()) {
            if (!"remnant".equals(f.getMemoryWithoutUpdate().getString(LacrimosaFleets.MEM_ROLE))) continue;
            if (f.isAlive() && !f.isEmpty() && Misc.getDistance(f, st) < 3000f) return true;
        }
        return false;
    }

    private void wake() {
        ScoresIntel s = ScoresIntel.getOrCreate(t());
        t().addPara("The pod takes an hour to thaw. When it opens, the woman inside is young, grey-eyed, and has a "
                + "tuning collar still locked around her throat. She listens to Venn's message twice without a word.");
        t().addPara("\"She was always sorry afterwards,\" Odile Marchetti says at last. \"Never before.\" She "
                + "unlocks the collar and drops it on the floor. \"First chair of the First Chorus. The only chair "
                + "left, I suppose. You have ships that sing? Then you need someone who can hear them.\"");
        s.wakeMarchetti(t());
        only("Leave Venn's Rest");
    }

    // ------------------------------------------------------------------------------------------------- plugin

    private void leave() {
        if (originalPlugin != null) dialog.setPlugin(originalPlugin);
        dialog.dismiss();
    }

    @Override
    public void optionSelected(String optionText, Object optionData) {
        if (optionText != null) {
            dialog.getTextPanel().addParagraph(optionText, Global.getSettings().getColor("buttonText"));
        }
        if (optionData == Opt.READ) read();
        else if (optionData == Opt.WAKE) wake();
        else leave();
    }

    @Override
    public void init(InteractionDialogAPI dialog) {
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
        return memoryMap;
    }
}
