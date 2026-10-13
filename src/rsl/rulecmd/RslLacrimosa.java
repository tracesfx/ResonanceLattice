package rsl.rulecmd;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.campaign.CampaignFleetAPI;
import com.fs.starfarer.api.campaign.CargoAPI;
import com.fs.starfarer.api.campaign.InteractionDialogAPI;
import com.fs.starfarer.api.campaign.InteractionDialogPlugin;
import com.fs.starfarer.api.campaign.OptionPanelAPI;
import com.fs.starfarer.api.campaign.SectorEntityToken;
import com.fs.starfarer.api.campaign.SpecialItemData;
import com.fs.starfarer.api.campaign.TextPanelAPI;
import com.fs.starfarer.api.campaign.econ.MarketAPI;
import com.fs.starfarer.api.campaign.rules.MemoryAPI;
import com.fs.starfarer.api.characters.FullName;
import com.fs.starfarer.api.characters.PersonAPI;
import com.fs.starfarer.api.combat.EngagementResultAPI;
import com.fs.starfarer.api.fleet.FleetMemberAPI;
import com.fs.starfarer.api.impl.campaign.ids.Factions;
import com.fs.starfarer.api.impl.campaign.ids.Ranks;
import com.fs.starfarer.api.impl.campaign.rulecmd.BaseCommandPlugin;
import com.fs.starfarer.api.impl.campaign.rulecmd.FireAll;
import com.fs.starfarer.api.util.Misc;
import com.fs.starfarer.api.util.Misc.Token;
import rsl.RslIds;
import rsl.campaign.Lacrimosa;
import rsl.campaign.LacrimosaIntel;
import rsl.campaign.LacrimosaIntel.Stage;
import rsl.campaign.PitchGlass;

import java.awt.Color;
import java.util.List;
import java.util.Map;

/**
 * Every dialog of the Lacrimosa questline (CAMPAIGN.md section 6). Like {@link RslWorkshop} it takes over the dialog
 * and its options carry enum data, so no rules are needed past the entry points:
 * <ul>
 * <li>rules.csv conditions: {@code RslLacrimosa can tanh|council|recording} (market menu options);</li>
 * <li>rules.csv scripts: {@code RslLacrimosa tanh|council|recording} (markets, back to the market menu on leave) and
 * {@code RslLacrimosa buoy|institute|echo|graveyard} (custom entities, dismissed on leave);</li>
 * <li>Java: {@code new RslLacrimosa("sung")} shown by {@link LacrimosaIntel} through showInteractionDialog.</li>
 * </ul>
 */
public class RslLacrimosa extends BaseCommandPlugin implements InteractionDialogPlugin {

    private enum Opt {
        TANH_LISTEN, TANH_ACCEPT,
        BUOY_SCAN,
        INST_LOGS, INST_WAKE, INST_WAKE_CONFIRM, INST_COMPLETE, INST_COMPLETE_CONFIRM, INST_SPARE, INST_SPARE_CONFIRM,
        SUNG_HEAR, SUNG_SELL, SUNG_SELL_CONFIRM, SUNG_SELL_FINAL, SUNG_REFUSE, SUNG_DEFER,
        COUNCIL_HEAR, COUNCIL_CHORUS, COUNCIL_SOLO, COUNCIL_CHORUS_CONFIRM, COUNCIL_SOLO_CONFIRM,
        RECORDING_TAKE,
        ECHO_SWEEP,
        BACK, LEAVE
    }

    private String scene;
    private boolean atMarket;
    private InteractionDialogPlugin originalPlugin;
    private InteractionDialogAPI dialog;
    private Map<String, MemoryAPI> memoryMap;

    /** Rule-command form (rules.csv). */
    public RslLacrimosa() {
    }

    /** Stand-alone form (Director Sung's hail). */
    public RslLacrimosa(String scene) {
        this.scene = scene;
    }

    // ------------------------------------------------------------------------------------------------- entry

    @Override
    public boolean execute(String ruleId, InteractionDialogAPI dialog, List<Token> params,
                           Map<String, MemoryAPI> memoryMap) {
        String cmd = params.isEmpty() ? "" : params.get(0).getString(memoryMap);
        if ("can".equals(cmd)) return params.size() > 1 && can(params.get(1).getString(memoryMap), dialog);
        this.dialog = dialog;
        this.memoryMap = memoryMap;
        this.scene = cmd;
        atMarket = "tanh".equals(cmd) || "council".equals(cmd) || "recording".equals(cmd);
        originalPlugin = dialog.getPlugin();
        dialog.setPlugin(this);
        if (atMarket) dialog.getVisualPanel().saveCurrentVisual();
        open();
        return true;
    }

    @Override
    public void init(InteractionDialogAPI dialog) {
        this.dialog = dialog;
        if (memoryMap == null) memoryMap = new java.util.HashMap<String, MemoryAPI>();
        open();
    }

    private static boolean can(String what, InteractionDialogAPI dialog) {
        if (dialog == null || dialog.getInteractionTarget() == null) return false;
        MarketAPI m = dialog.getInteractionTarget().getMarket();
        if (m == null || !RslIds.FACTION_CHOIR.equals(m.getFactionId())) return false;
        LacrimosaIntel q = LacrimosaIntel.get();
        if ("tanh".equals(what)) return Lacrimosa.canStart();
        if ("council".equals(what)) return q != null && q.getStage() == Stage.COUNCIL && preferred(m, RslIds.MARKET_CODA);
        if ("recording".equals(what)) {
            return q != null && q.getStage() == Stage.RECORDING && preferred(m, RslIds.MARKET_TACET);
        }
        return false;
    }

    /** True at the preferred market, or at any Cantorate market once the Cantorate has lost the preferred one. */
    private static boolean preferred(MarketAPI here, String preferredId) {
        if (preferredId.equals(here.getId())) return true;
        MarketAPI p = Global.getSector().getEconomy().getMarket(preferredId);
        return p == null || !RslIds.FACTION_CHOIR.equals(p.getFactionId());
    }

    private void open() {
        if ("tanh".equals(scene)) tanh();
        else if ("buoy".equals(scene)) buoy();
        else if ("institute".equals(scene)) institute();
        else if ("sung".equals(scene)) sung();
        else if ("council".equals(scene)) council();
        else if ("recording".equals(scene)) recording();
        else if ("echo".equals(scene)) echo();
        else if ("graveyard".equals(scene)) graveyard();
        else leave();
    }

    // ------------------------------------------------------------------------------------------------- helpers

    private TextPanelAPI t() {
        return dialog.getTextPanel();
    }

    private OptionPanelAPI options(Object... pairs) {
        OptionPanelAPI o = dialog.getOptionPanel();
        o.clearOptions();
        for (int i = 0; i + 1 < pairs.length; i += 2) o.addOption((String) pairs[i], pairs[i + 1]);
        return o;
    }

    private void leaveOption(String text) {
        dialog.getOptionPanel().addOption(text, Opt.LEAVE);
        dialog.setOptionOnEscape(text, Opt.LEAVE);
    }

    private static PersonAPI person(String id) {
        return Global.getSector().getImportantPeople().getPerson(id);
    }

    private void show(PersonAPI p) {
        if (p != null) dialog.getVisualPanel().showPersonInfo(p, true);
    }

    private static Color hl() {
        return Misc.getHighlightColor();
    }

    private LacrimosaIntel q() {
        return LacrimosaIntel.get();
    }

    // ------------------------------------------------------------------------------------------------- beat 1

    private void tanh() {
        show(person(RslIds.PERSON_TANH));
        t().addPara("A sealed message is waiting for you, routed through three relays so that it cannot be traced "
                + "back to Tacet Station. When you open it, Archivist Mireille Tanh's face fills the screen. She looks "
                + "as if she has not slept in a week.");
        t().addPara("\"Captain. I need someone who is not Cantorate, and who can fight. Please hear me out before you "
                + "decide which of those matters more.\"");
        options("Hear her out", Opt.TANH_LISTEN);
        leaveOption("Not now");
    }

    private void tanhListen() {
        t().addPara("\"Three weeks ago our pulsar receivers caught a signal in hyperspace. Faint. Pulsar-locked. "
                + "There is exactly one thing in the Sector that sings like that and does not belong to us.\" She "
                + "hesitates. \"The Lacrimosa. The Domain's Virtuoso. The ship that killed the First Chorus. We teach "
                + "our children it was scrapped. It was not. Its core is waking up.\"");
        t().addPara("\"I cannot take this to the Precentor. The taboo is older than the Cantorate itself, and the "
                + "council would bury it, and me with it. But if we can hear it, so can Tri-Tachyon.\"");
        t().addPara("\"The Antiphon Institute left listening buoys along the fringe before the Collapse. Three of "
                + "them still answer. Scan them, and I can cross their bearings to the Institute. One of them has "
                + "gone quiet in a way I do not like. Scavengers, perhaps.\"");
        options("Agree to find the buoys", Opt.TANH_ACCEPT);
        leaveOption("Decline for now");
    }

    private void tanhAccept() {
        LacrimosaIntel.start(t());
        t().addPara("\"Thank you.\" For a moment the Archivist only breathes. \"I have sent you the buoys' last "
                + "known positions. And captain... when you find it, do not listen to it for long.\"");
        options();
        leaveOption("Close the channel");
    }

    // ------------------------------------------------------------------------------------------------- buoys

    private static final String[] VENN_LOGS = {
        "\"Antiphon Institute, Director's log, day 212 since the Gates went dark. Relief is not coming; I have stopped "
                + "saying it might. The Navy crews call the Lacrimosa 'the Director's cathedral'. They are not wrong. "
                + "Twelve escorts, one voice, one core large enough to carry them all. On paper it can hold a whole "
                + "battle in tune. On paper.\"",
        "\"Day 340. Raiders took the ice convoy. Ninety-one dead. The core has never been run at full voice; we do "
                + "not know what it does when twelve ships lean on it at once. Doctor Ashe says the models diverge. I "
                + "told her models always diverge. I am no longer sure which of us is afraid.\"",
        "\"Day 351. They are coming back, with more. I have ordered the First Chorus to collar up. If the core does "
                + "what we built it to do, the families live. If it does what Ashe fears, then I will be the one who "
                + "stops it. I wanted that on the record.\"",
    };

    private void buoy() {
        LacrimosaIntel q = q();
        SectorEntityToken b = dialog.getInteractionTarget();
        t().addPara("A Domain listening buoy, its hull pitted by two centuries of hyperspace weather. Under the "
                + "Institute's crest someone has scratched a stave of five lines and a single note.");
        if (q == null || q.getStage() != Stage.BUOYS || q.isScanned(b)) {
            t().addPara("Its memory has already been read. Now it only repeats a carrier tone, patient and empty.");
            options();
            leaveOption("Leave");
            return;
        }
        if (q.isScavengerNear(b)) {
            t().addPara("Cutting lines run from the buoy to a scavenger hulk riding beside it. Their crews have "
                    + "already started stripping the antenna mast, and their escorts turn towards you. Nobody "
                    + "scans anything here until they are gone.", Misc.getNegativeHighlightColor());
            options();
            leaveOption("Leave");
            return;
        }
        t().addPara("It still answers. Your sensors officer says the buoy's last bearing log is intact, and "
                + "something else besides: an audio file, compressed in a format nobody has used in two hundred "
                + "years.");
        options("Scan the buoy and play the recording", Opt.BUOY_SCAN);
        leaveOption("Leave");
    }

    private void buoyScan() {
        LacrimosaIntel q = q();
        if (q == null) {
            leave();
            return;
        }
        int log = Math.min(q.getScans(), VENN_LOGS.length - 1);
        t().addPara("The bearing log copies across in seconds. The recording takes longer to decode. A woman's "
                + "voice, tired and precise:");
        t().addPara(VENN_LOGS[log], Misc.getGrayColor());
        q.scanBuoy(dialog.getInteractionTarget(), t());
        if (q.getStage() == Stage.INSTITUTE && q.getInstitute() != null) {
            t().addPara("Three bearings, one answer. Your navigator lays them over the chart and they cross in %s. "
                    + "The Antiphon Institute.", hl(), q.getInstitute().getStarSystem().getNameWithLowercaseType());
        } else {
            t().addPara("One more bearing on the chart. Not enough to fix a position yet.");
        }
        options();
        leaveOption("Leave");
    }

    // ------------------------------------------------------------------------------------------------- the Institute

    private void institute() {
        LacrimosaIntel q = q();
        Stage s = q == null ? null : q.getStage();
        t().addPara("The Antiphon Institute is a long spindle of habitat rings around a dock built for a capital "
                + "ship. Every ring is dark. Frost has grown over the viewports in patterns that look, if you stare "
                + "long enough, like sheet music.");
        if (s == Stage.INSTITUTE && q.isGuardAlive()) {
            t().addPara("Domain-era defence drones hang in a lattice around the dock, transponders broadcasting "
                    + "Navy codes two centuries dead. They will not let you dock while they fly.",
                    Misc.getNegativeHighlightColor());
            options();
            leaveOption("Leave");
            return;
        }
        if (s == Stage.INSTITUTE) {
            t().addPara("Your marines go in first. They find what everyone finds in places like this: bunks, "
                    + "photographs, a child's drawing of a ship with a ribbon down its spine. In the dock, under "
                    + "work lights that still flicker on at your approach, lies the Lacrimosa: plates missing, sash "
                    + "stripped to bare metal, its two great lances out of true. Its core is dark. And yet your "
                    + "hull is humming.");
            options("Read Director Venn's last log", Opt.INST_LOGS, "Wake the Lacrimosa", Opt.INST_WAKE);
            leaveOption("Leave");
            return;
        }
        if (s == Stage.RETURN) {
            showCompletion();
            return;
        }
        if (s == Stage.DONE || s == null) {
            t().addPara("The dock is quiet. Whatever the Institute was for, it is finished now.");
        } else {
            t().addPara("The empty dock waits for the Lacrimosa's sash and vanes. Only here can they be mounted.");
        }
        options();
        leaveOption("Leave");
    }

    private void instituteLogs() {
        t().addPara("The Director's terminal still has power. The last entry is short.");
        t().addPara("\"Day 352. It worked. The raiders are gone. And then it did not stop. The core pulled the "
                + "resonance out of all twelve escorts to keep singing, and then their readiness, and then their "
                + "reactor margins, and then the crews at their collars. I shut it down with my own hands. I am "
                + "taking the survivors away. We will remember the scores and forget this place. Let no one find "
                + "it.\"", Misc.getGrayColor());
        t().addPara("Someone found it anyway.");
        options("Wake the Lacrimosa", Opt.INST_WAKE);
        leaveOption("Leave");
    }

    private void instituteWake() {
        t().addPara("Your engineers rig the dock's old power couplings to your fleet. The Institute's chief "
                + "engineer left a note taped over the main breaker, in a hand that shakes: IT DRINKS TO WAKE.");
        t().addPara("Waking the core will drain every ship in your fleet to %s combat readiness.",
                Misc.getNegativeHighlightColor(), Math.round(Lacrimosa.WAKE_CR * 100f) + "%");
        t().addPara("The Lacrimosa is unique. If it is sold or scuttled, it is gone; the Institute could build one "
                + "more frame, once, at great cost.", hl());
        options("Wake it", Opt.INST_WAKE_CONFIRM, "Not yet", Opt.BACK);
        dialog.setOptionOnEscape("Not yet", Opt.BACK);
    }

    private void instituteWakeConfirm() {
        LacrimosaIntel q = q();
        if (q == null) {
            leave();
            return;
        }
        t().addPara("The breaker closes. For a long moment nothing happens. Then every hull in your fleet rings at "
                + "once, a single low note you feel in your teeth, and your readiness boards go amber, then red, one "
                + "ship after another, as something in the dock drinks.");
        t().addPara("When it stops, the Lacrimosa's seams are glowing. Faintly, unevenly, like a voice that has "
                + "forgotten the words. It answers your helm.");
        q.wake(t());
        options();
        leaveOption("Leave the Institute");
    }

    private void showCompletion() {
        t().addPara("The Luthiers you hired from Coda are waiting in the dock with their rigs and their collars. "
                + "The sash and vanes from the Hush lie on the deck between them, still humming.");
        t().addPara("\"%s Pitch Glass to retune the core to the sash,\" their foreman says, \"and %s for the "
                + "plating, the lances and the rest. Two hundred years late, but it will be finished as it was "
                + "drawn.\"", hl(), "" + Lacrimosa.PRICE_GLASS, Misc.getDGSCredits(Lacrimosa.PRICE_CREDITS));
        OptionPanelAPI o = options();
        FleetMemberAPI unsung = Lacrimosa.findUnsung();
        String why = completionBlock(Lacrimosa.PRICE_CREDITS);
        if (unsung != null) {
            o.addOption("Have the Luthiers finish the Lacrimosa", Opt.INST_COMPLETE);
            if (why != null) {
                o.setEnabled(Opt.INST_COMPLETE, false);
                o.setTooltip(Opt.INST_COMPLETE, why);
            }
        } else if (!Global.getSector().getMemoryWithoutUpdate().getBoolean(RslIds.MEM_SPARE_USED)) {
            t().addPara("The Lacrimosa is not in your fleet. The foreman shrugs towards a second dock, where a bare "
                    + "Virtuoso frame has waited two centuries under tarpaulin. \"Venn built a spare. One. It will "
                    + "cost you more, and something harder to replace than money.\"");
            int credits = Lacrimosa.PRICE_CREDITS + Lacrimosa.SPARE_CREDITS;
            o.addOption("Build the Virtuoso on the spare frame", Opt.INST_SPARE);
            String w = completionBlock(credits);
            if (w == null && Global.getSector().getPlayerStats().getStoryPoints() < Lacrimosa.SPARE_STORY_POINTS) {
                w = "Requires a story point.";
            }
            if (w != null) {
                o.setEnabled(Opt.INST_SPARE, false);
                o.setTooltip(Opt.INST_SPARE, w);
            }
        } else {
            t().addPara("The Lacrimosa is not in your fleet, and the spare frame is gone. There is nothing left in "
                    + "the dock to finish.");
        }
        leaveOption("Leave");
    }

    private static String completionBlock(int credits) {
        if (PitchGlass.held() < Lacrimosa.PRICE_GLASS) return "You need " + Lacrimosa.PRICE_GLASS + " Pitch Glass.";
        if (Global.getSector().getPlayerFleet().getCargo().getCredits().get() < credits) {
            return "You need " + Misc.getDGSCredits(credits) + ".";
        }
        return null;
    }

    private void completionConfirm(boolean spare) {
        int credits = Lacrimosa.PRICE_CREDITS + (spare ? Lacrimosa.SPARE_CREDITS : 0);
        t().addPara("This will cost %s Pitch Glass and %s" + (spare ? ", and a story point." : "."), hl(),
                "" + Lacrimosa.PRICE_GLASS, Misc.getDGSCredits(credits));
        options(spare ? "Build it" : "Finish it", spare ? Opt.INST_SPARE_CONFIRM : Opt.INST_COMPLETE_CONFIRM,
                "Not yet", Opt.BACK);
        dialog.setOptionOnEscape("Not yet", Opt.BACK);
    }

    private void complete(boolean spare) {
        LacrimosaIntel q = q();
        int credits = Lacrimosa.PRICE_CREDITS + (spare ? Lacrimosa.SPARE_CREDITS : 0);
        String why = completionBlock(credits);
        FleetMemberAPI unsung = Lacrimosa.findUnsung();
        if (q == null || why != null || (!spare && unsung == null)) {
            institute();
            return;
        }
        CampaignFleetAPI pf = Global.getSector().getPlayerFleet();
        if (spare) {
            if (Global.getSector().getPlayerStats().getStoryPoints() < Lacrimosa.SPARE_STORY_POINTS) {
                institute();
                return;
            }
            Global.getSector().getPlayerStats().spendStoryPoints(Lacrimosa.SPARE_STORY_POINTS, true, t(), false,
                    "Built the Virtuoso on the Antiphon Institute's spare frame");
        }
        PitchGlass.spend(Lacrimosa.PRICE_GLASS);
        pf.getCargo().getCredits().subtract(credits);
        // the sash is consumed if it is still aboard; the stage alone proves the Hush is silenced (no softlock if lost)
        if (Lacrimosa.hasSash()) {
            pf.getCargo().removeItems(CargoAPI.CargoItemType.SPECIAL, new SpecialItemData(RslIds.ITEM_SASH, null), 1);
        }
        t().setFontSmallInsignia();
        t().addPara("Paid %s Pitch Glass and %s", Misc.getNegativeHighlightColor(), "" + Lacrimosa.PRICE_GLASS,
                Misc.getDGSCredits(credits));
        t().setFontInsignia();
        FleetMemberAPI m = spare ? Lacrimosa.spareVirtuoso() : Lacrimosa.upgrade(unsung);
        t().addPara("It takes the Luthiers nineteen days. They sing through all of them, in shifts, collars on, and "
                + "on the last night the whole Institute sings with them: the sash locks into the spine, the vanes "
                + "unfold, and the lances come true.");
        t().addPara("The %s is a Virtuoso again. Its seams run white and steady. At full readiness, it will sing "
                + "at full voice.", hl(), m.getShipName());
        if (LacrimosaIntel.isChorus()) {
            t().addPara("A message from Coda follows you out of the dock: the Precentor names you an honorary "
                    + "Maestro of the Cantorate. \"Teach it to listen,\" the message ends.");
        } else {
            t().addPara("Abelard's message is three lines long. The last one reads: \"Now it sings alone. Try not to "
                    + "let it get hungry.\"");
        }
        t().addPara("The Luthier's Workshop at Coda can now build the Unbound Core and the %s for it.", hl(),
                LacrimosaIntel.isChorus() ? "Chorus Movement" : "Solo Movement");
        q.complete(t());
        options();
        leaveOption("Leave the Institute");
    }

    // ------------------------------------------------------------------------------------------------- beat 3: Sung

    private static PersonAPI sungPerson() {
        PersonAPI p = person(RslIds.PERSON_SUNG);
        if (p != null) return p;
        p = Global.getFactory().createPerson();
        p.setId(RslIds.PERSON_SUNG);
        p.setFaction(Factions.TRITACHYON);
        p.setGender(FullName.Gender.MALE);
        p.setName(new FullName("Hale", "Sung", FullName.Gender.MALE));
        p.setPortraitSprite("graphics/portraits/portrait_corporate07.png");
        p.setRankId(Ranks.SPACE_ADMIRAL);
        p.setPostId(Ranks.POST_SENIOR_EXECUTIVE);
        Global.getSector().getImportantPeople().addPerson(p);
        return p;
    }

    private void sung() {
        show(sungPerson());
        t().addPara("A courier with no transponder has been shadowing you since the Institute. Now it hails, on a "
                + "tight beam with Tri-Tachyon encryption.");
        t().addPara("\"Captain. Director Hale Sung, Special Projects.\" A pleasant man in an expensive collar, "
                + "lit from below by a dozen screens. \"You have something I have been looking for since before you "
                + "were born. Shall we be civilised about it?\"");
        options("Hear him out", Opt.SUNG_HEAR, "\"I need time.\"", Opt.SUNG_DEFER);
        dialog.setOptionOnEscape("\"I need time.\"", Opt.SUNG_DEFER);
    }

    private void sungHear() {
        t().addPara("\"I do not want the ship. A duelist with a famous name: lovely, impractical. I want the core. A "
                + "single crystal that can carry a fleet's readiness and spend it as it likes. Do you understand "
                + "what the Company could do with that? No more fleets idling for want of supplies. No more crews "
                + "at all, perhaps.\"");
        t().addPara("\"Two million credits. The Company's gratitude. And you never have to explain to the "
                + "Cantorate what you are carrying around in their sacred taboo.\"", hl());
        OptionPanelAPI o = options("Sell him the core (" + Misc.getDGSCredits(Lacrimosa.SUNG_CREDITS) + ")",
                Opt.SUNG_SELL, "Refuse", Opt.SUNG_REFUSE, "\"I need time.\"", Opt.SUNG_DEFER);
        String why = Lacrimosa.whyCannotSell();
        if (why != null) {
            o.setEnabled(Opt.SUNG_SELL, false);
            o.setTooltip(Opt.SUNG_SELL, why);
        }
        dialog.setOptionOnEscape("\"I need time.\"", Opt.SUNG_DEFER);
    }

    private void sungSell(boolean finalWarning) {
        if (!finalWarning) {
            t().addPara("Selling ends the Lacrimosa's story. The ship leaves your fleet for good, and the Cantorate "
                    + "will learn who sold its oldest grief to Tri-Tachyon.", Misc.getNegativeHighlightColor());
            options("Sell", Opt.SUNG_SELL_CONFIRM, "Reconsider", Opt.SUNG_HEAR);
        } else {
            t().addPara("Are you certain? There is no way back from this.", Misc.getNegativeHighlightColor());
            options("Sell the Lacrimosa to Tri-Tachyon", Opt.SUNG_SELL_FINAL, "Reconsider", Opt.SUNG_HEAR);
        }
        dialog.setOptionOnEscape("Reconsider", Opt.SUNG_HEAR);
    }

    private void sungSold() {
        LacrimosaIntel q = q();
        if (Lacrimosa.whyCannotSell() != null || q == null) {
            sungHear();
            return;
        }
        t().addPara("\"A sensible choice.\" Sung's people are aboard within the hour, polite, efficient and armed. "
                + "When the courier pulls away with the Lacrimosa in tow, the hum in your hulls goes with it.");
        Lacrimosa.sellToSung(t());
        q.sold(t());
        options();
        leaveOption("Cut the comm link");
    }

    private void sungRefuse() {
        LacrimosaIntel q = q();
        t().addPara("Sung's smile does not move at all. \"Then I will have to collect it. Special Projects does not "
                + "send couriers twice, captain. Enjoy your ship while you have it.\"");
        t().addPara("The channel closes. A Special Projects fleet will come for the Lacrimosa.",
                Misc.getNegativeHighlightColor());
        if (q != null) q.refused(t());
        options();
        leaveOption("Cut the comm link");
    }

    private void sungDefer() {
        LacrimosaIntel q = q();
        t().addPara("\"Of course. Take a few days. My courier will find you.\"");
        if (q != null) q.deferSung();
        options();
        leaveOption("Cut the comm link");
    }

    // ------------------------------------------------------------------------------------------------- beat 4

    private void council() {
        PersonAPI precentor = person(RslIds.PERSON_PRECENTOR);
        show(precentor);
        if (person(RslIds.PERSON_TANH) != null) dialog.getVisualPanel().showSecondPerson(person(RslIds.PERSON_TANH));
        if (person(RslIds.PERSON_ABELARD) != null) {
            dialog.getVisualPanel().showThirdPerson(person(RslIds.PERSON_ABELARD));
        }
        t().addPara("Cantorate wardens meet you at the dock and walk you, politely and without a word, to the "
                + "council hall. Precentor Ilian Okoro-Vass sits at the reference console. Archivist Tanh stands "
                + "beside it, pale and very straight. Luthier Corvin Abelard leans on the far wall with his arms "
                + "folded.");
        t().addPara("\"Every core in Vell has been ringing for a month,\" the Precentor says. \"You will forgive us "
                + "for noticing what you brought into our sky.\"");
        options("Hear the council", Opt.COUNCIL_HEAR);
        leaveOption("Ask for time to think");
    }

    private void councilHear() {
        t().addPara("The Precentor: \"The Lacrimosa killed the First Chorus because it was built to sing alone. We "
                + "will not finish that. But we can retune it: teach the core to give as well as take. It would be "
                + "weaker for it, and it would never be a monster again. The Cantorate would stand with you.\"");
        t().addPara("Abelard, without unfolding his arms: \"Venn's design was not a mistake, it was an "
                + "unfinished one. Finish it as drawn and it is the finest hull ever grown. I would build it. The "
                + "council would not thank either of us.\"");
        t().addPara("Tanh says nothing. She is looking at you.");
        t().addPara("Either way, the Lacrimosa can be completed and the Unbound Core built for it. The choice "
                + "decides which Movement the Luthiers can tune into it, and where you stand with the Cantorate.",
                Misc.getGrayColor());
        options("Side with the Precentor: teach it to sing with others", Opt.COUNCIL_CHORUS,
                "Side with Abelard: finish it as Venn designed it", Opt.COUNCIL_SOLO);
        leaveOption("Ask for time to think");
    }

    private void councilChoice(boolean chorus) {
        if (chorus) {
            t().addPara("Chorus: Cantorate reputation %s, the Workshop's prices %s, two Cantorate escorts for the "
                    + "search for the Hush, and the %s.", hl(), "+" + Math.round(Lacrimosa.CHORUS_REP * 100f),
                    "-" + Math.round(Lacrimosa.CHORUS_DISCOUNT * 100f) + "%", "Chorus Movement");
        } else {
            t().addPara("Solo: Cantorate reputation %s, no escorts, Abelard will trade with you at any standing "
                    + "short of hostile, and the %s.", hl(), "" + Math.round(Lacrimosa.SOLO_REP * 100f),
                    "Solo Movement");
        }
        options("Decide", chorus ? Opt.COUNCIL_CHORUS_CONFIRM : Opt.COUNCIL_SOLO_CONFIRM, "Back", Opt.COUNCIL_HEAR);
        dialog.setOptionOnEscape("Back", Opt.COUNCIL_HEAR);
    }

    private void councilDecide(boolean chorus) {
        LacrimosaIntel q = q();
        if (q == null || q.getStage() != Stage.COUNCIL) {
            leave();
            return;
        }
        float rep = chorus ? Lacrimosa.CHORUS_REP : Lacrimosa.SOLO_REP;
        Global.getSector().getPlayerFaction().adjustRelationship(RslIds.FACTION_CHOIR, rep);
        if (chorus) {
            t().addPara("The Precentor bows his head. \"Then it will learn to listen. So will we.\" Abelard sighs, "
                    + "unfolds his arms, and shakes your hand anyway.");
        } else {
            t().addPara("The hall goes very quiet. \"So be it,\" the Precentor says at last, and leaves without "
                    + "another word. Abelard waits until the door closes. \"Thank you,\" he says. \"I have waited "
                    + "my whole life to build it.\"");
        }
        t().setFontSmallInsignia();
        t().addPara("Relations with the Cantorate %s by %s", rep > 0 ? Misc.getPositiveHighlightColor()
                : Misc.getNegativeHighlightColor(), rep > 0 ? "improved" : "worsened",
                "" + Math.round(Math.abs(rep) * 100f));
        t().setFontInsignia();
        t().addPara("Tanh catches you at the door. \"The First Chorus died somewhere in the abyss. I can find "
                + "where, but I need Tacet Station's raw pulsar recording to clean the signal. Come to the station "
                + "and I will have it ready.\"");
        q.decide(chorus ? "chorus" : "solo", t());
        options();
        leaveOption("Leave the hall");
    }

    // ------------------------------------------------------------------------------------------------- beat 4: Tacet

    private void recording() {
        show(person(RslIds.PERSON_TANH));
        t().addPara("Archivist Tanh meets you in a listening room lined with grey foam. On the desk lies a crystal "
                + "the size of your thumb, singing faintly.");
        t().addPara("\"Forty years of Vell, beat by beat. The First Chorus's cores were grown to the same kind of "
                + "clock. Hold this against the abyss and anything still ringing in tune with it will answer.\"");
        options("Take the recording", Opt.RECORDING_TAKE);
        leaveOption("Not yet");
    }

    private void recordingTake() {
        LacrimosaIntel q = q();
        if (q == null) {
            leave();
            return;
        }
        t().addPara("\"Fly out past the Sector's edge, into the abyss. Sweep wherever the echo is strongest; each "
                + "sweep will narrow it. And captain... there were twelve of them. There are more than twelve wrecks "
                + "out there now. Things that come to listen do not always leave.\"");
        q.beginSearch(t());
        options();
        leaveOption("Leave");
    }

    // ------------------------------------------------------------------------------------------------- beat 5

    private static final String[] ECHO_TEXT = {
        "A Cantorate frigate of a pattern two centuries old, drifting nose-down in the dark. Its hull is cold. Its "
                + "core is not: under your sensors it gives off a pulse, faint and perfectly regular.",
        "A second wreck, closer to the dark. This one still has its crew aboard, collars on, at their stations. "
                + "The pulse is stronger here, and there is a second one under it, and a third.",
        "The third echo is not one wreck but a field of debris, all of it humming the same note. Somewhere ahead, "
                + "the note is coming from a great many throats at once.",
    };

    private void echo() {
        LacrimosaIntel q = q();
        SectorEntityToken e = dialog.getInteractionTarget();
        if (q == null || !q.isCurrentEcho(e)) {
            t().addPara("A dead hull, silent now. Whatever it had to tell you, it has told.");
            options();
            leaveOption("Leave");
            return;
        }
        t().addPara(ECHO_TEXT[Math.min(q.getEchoIndex(), ECHO_TEXT.length - 1)]);
        options("Run a sensor sweep with Tanh's recording", Opt.ECHO_SWEEP);
        leaveOption("Leave");
    }

    private void echoSweep() {
        LacrimosaIntel q = q();
        if (q == null) {
            leave();
            return;
        }
        q.sweep(dialog.getInteractionTarget(), t());
        if (q.getStage() == Stage.HUSH) {
            t().addPara("The sweep comes back as a chord. Twelve voices, and more under them, all on one pitch, all "
                    + "pointing at the same patch of dark. The graveyard of the First Chorus is marked on your "
                    + "chart.", hl());
            t().addPara("The wrecks there are not drifting. They are waiting.", Misc.getNegativeHighlightColor());
        } else {
            t().addPara("The recording and the echo beat against each other until the interference resolves into "
                    + "a bearing. The next echo is marked on your chart.");
        }
        options();
        leaveOption("Leave");
    }

    private void graveyard() {
        LacrimosaIntel q = q();
        if (q != null && q.getStage() == Stage.HUSH && q.isHushAlive()) {
            t().addPara("Lattice hulls hang in a ring in the dark, dozens of them, their seams glowing a sick "
                    + "violet. As you close, every one of them turns to face you at once. Your hull begins to hum "
                    + "with them, and your crews put their hands over their ears.");
            t().addPara("The Hush has heard the Lacrimosa.", Misc.getNegativeHighlightColor());
        } else {
            t().addPara("The graveyard of the First Chorus. The wrecks are only wrecks now, and the abyss is "
                    + "silent.");
        }
        options();
        leaveOption("Leave");
    }

    // ------------------------------------------------------------------------------------------------- leave

    private void leave() {
        if (atMarket && originalPlugin != null) {
            dialog.getVisualPanel().restoreSavedVisual();
            dialog.setPlugin(originalPlugin);
            FireAll.fire(null, dialog, memoryMap, "PopulateOptions");
        } else {
            dialog.dismiss();
        }
    }

    @Override
    public void optionSelected(String optionText, Object optionData) {
        if (optionText != null) {
            dialog.getTextPanel().addParagraph(optionText, Global.getSettings().getColor("buttonText"));
        }
        if (!(optionData instanceof Opt)) {
            leave();
            return;
        }
        switch ((Opt) optionData) {
            case TANH_LISTEN: tanhListen(); break;
            case TANH_ACCEPT: tanhAccept(); break;
            case BUOY_SCAN: buoyScan(); break;
            case INST_LOGS: instituteLogs(); break;
            case INST_WAKE: instituteWake(); break;
            case INST_WAKE_CONFIRM: instituteWakeConfirm(); break;
            case INST_COMPLETE: completionConfirm(false); break;
            case INST_SPARE: completionConfirm(true); break;
            case INST_COMPLETE_CONFIRM: complete(false); break;
            case INST_SPARE_CONFIRM: complete(true); break;
            case SUNG_HEAR: sungHear(); break;
            case SUNG_SELL: sungSell(false); break;
            case SUNG_SELL_CONFIRM: sungSell(true); break;
            case SUNG_SELL_FINAL: sungSold(); break;
            case SUNG_REFUSE: sungRefuse(); break;
            case SUNG_DEFER: sungDefer(); break;
            case COUNCIL_HEAR: councilHear(); break;
            case COUNCIL_CHORUS: councilChoice(true); break;
            case COUNCIL_SOLO: councilChoice(false); break;
            case COUNCIL_CHORUS_CONFIRM: councilDecide(true); break;
            case COUNCIL_SOLO_CONFIRM: councilDecide(false); break;
            case RECORDING_TAKE: recordingTake(); break;
            case ECHO_SWEEP: echoSweep(); break;
            case BACK: open(); break;
            default: leave(); break;
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
        return memoryMap;
    }
}
