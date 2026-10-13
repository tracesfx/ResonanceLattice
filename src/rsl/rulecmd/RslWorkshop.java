package rsl.rulecmd;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.campaign.CampaignFleetAPI;
import com.fs.starfarer.api.campaign.CargoAPI;
import com.fs.starfarer.api.campaign.CargoStackAPI;
import com.fs.starfarer.api.campaign.InteractionDialogAPI;
import com.fs.starfarer.api.campaign.InteractionDialogPlugin;
import com.fs.starfarer.api.campaign.OptionPanelAPI;
import com.fs.starfarer.api.campaign.RepLevel;
import com.fs.starfarer.api.campaign.SpecialItemData;
import com.fs.starfarer.api.campaign.SpecialItemSpecAPI;
import com.fs.starfarer.api.campaign.TextPanelAPI;
import com.fs.starfarer.api.campaign.rules.MemoryAPI;
import com.fs.starfarer.api.combat.EngagementResultAPI;
import com.fs.starfarer.api.impl.campaign.ids.Commodities;
import com.fs.starfarer.api.impl.campaign.ids.Factions;
import com.fs.starfarer.api.impl.campaign.ids.Items;
import com.fs.starfarer.api.impl.campaign.rulecmd.BaseCommandPlugin;
import com.fs.starfarer.api.impl.campaign.rulecmd.FireAll;
import com.fs.starfarer.api.util.Misc;
import com.fs.starfarer.api.util.Misc.Token;
import rsl.RslIds;
import rsl.campaign.Lacrimosa;
import rsl.campaign.LacrimosaIntel;
import rsl.campaign.PitchGlass;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * The Luthier's Workshop at Coda (CAMPAIGN.md section 8): a dialog shop priced in Pitch Glass.
 * rules.csv: option rsl_workshopOpen (PopulateOptions at Coda) -> "RslWorkshop". This command then takes over the
 * dialog like vanilla's PaginatedOptions (its options carry objects, not rule ids, so no rules are involved), and
 * hands it back with FireAll PopulateOptions when the player leaves.
 */
public class RslWorkshop extends BaseCommandPlugin implements InteractionDialogPlugin {

    private enum Nav { BUY, SILENCE, TURN_IN, MAIN, LEAVE }

    private enum Kind { TUNING, ITEM, HULLMOD, HUSH_SEAMS }

    /** One thing for sale. */
    private static final class Offer {
        final Kind kind;
        final String id, name, desc;
        final int price, credits;
        final RepLevel minRep;

        Offer(Kind kind, String id, String name, int price, RepLevel minRep, String desc) {
            this(kind, id, name, price, 0, minRep, desc);
        }

        Offer(Kind kind, String id, String name, int price, int credits, RepLevel minRep, String desc) {
            this.kind = kind;
            this.id = id;
            this.name = name;
            this.price = discounted(price);
            this.credits = credits;
            // Solo path: Abelard keeps trading with the player at any standing short of hostile
            this.minRep = LacrimosaIntel.isSolo() ? RepLevel.INHOSPITABLE : minRep;
            this.desc = desc;
        }
    }

    /** Option data for turning cores or colony items in. */
    private static final class TurnIn {
        final boolean core;
        final String id, name;
        final int count, glassEach;

        TurnIn(boolean core, String id, String name, int count, int glassEach) {
            this.core = core;
            this.id = id;
            this.name = name;
            this.count = count;
            this.glassEach = glassEach;
        }
    }

    /** Confirm a purchase. */
    private static final class Confirm {
        final Offer offer;

        Confirm(Offer offer) {
            this.offer = offer;
        }
    }

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
        TextPanelAPI t = dialog.getTextPanel();
        t.addPara("Luthier Corvin Abelard's workshop is a long, cold hall full of half-grown crystal and humming "
                + "test rigs. Everything here is priced in Pitch Glass; credits only buy you the time to ask.");
        showMain();
        return true;
    }

    // ------------------------------------------------------------------------------------------------- menus

    private void showMain() {
        TextPanelAPI t = dialog.getTextPanel();
        t.addPara("You hold %s Pitch Glass.", Misc.getHighlightColor(), "" + PitchGlass.held());
        OptionPanelAPI o = dialog.getOptionPanel();
        o.clearOptions();
        o.addOption("Commission work from the Luthiers", Nav.BUY);
        o.addOption("Hand over AI cores to be silenced", Nav.SILENCE);
        if (coreTurnIns().isEmpty()) {
            o.setEnabled(Nav.SILENCE, false);
            o.setTooltip(Nav.SILENCE, "You carry no AI cores.");
        }
        o.addOption("Offer Domain-era equipment", Nav.TURN_IN);
        if (itemTurnIns().isEmpty()) {
            o.setEnabled(Nav.TURN_IN, false);
            o.setTooltip(Nav.TURN_IN, "You carry no colony items the Luthiers want.");
        }
        o.addOption("Leave the workshop", Nav.LEAVE);
        dialog.setOptionOnEscape("Leave", Nav.LEAVE);
    }

    private void showBuy() {
        OptionPanelAPI o = dialog.getOptionPanel();
        o.clearOptions();
        int held = PitchGlass.held();
        RepLevel rep = PitchGlass.rep();
        float credits = Global.getSector().getPlayerFleet().getCargo().getCredits().get();
        for (Offer of : offers()) {
            o.addOption(of.name + " (" + priceText(of) + ")", of);
            String why = null;
            if (!rep.isAtWorst(of.minRep)) {
                why = "Requires " + of.minRep.getDisplayName().toLowerCase() + " standing with the Cantorate.";
            } else if (owned(of)) {
                why = of.kind == Kind.TUNING ? "Your fleet is already tuned." : "You already have this.";
            } else if (held < of.price) {
                why = "You need " + of.price + " Pitch Glass.";
            } else if (credits < of.credits) {
                why = "You need " + Misc.getDGSCredits(of.credits) + ".";
            }
            if (why != null) o.setEnabled(of, false);
            o.setTooltip(of, of.desc + (why != null ? "\n\n" + why : ""));
        }
        o.addOption("Back", Nav.MAIN);
        dialog.setOptionOnEscape("Back", Nav.MAIN);
    }

    private void showConfirm(Offer of) {
        TextPanelAPI t = dialog.getTextPanel();
        t.addPara(of.desc);
        t.addPara("Abelard names the price: %s.", Misc.getHighlightColor(), priceText(of));
        OptionPanelAPI o = dialog.getOptionPanel();
        o.clearOptions();
        o.addOption("Pay " + priceText(of), new Confirm(of));
        o.addOption("Never mind", Nav.BUY);
        dialog.setOptionOnEscape("Never mind", Nav.BUY);
    }

    private void showTurnIns(List<TurnIn> list, String intro) {
        dialog.getTextPanel().addPara(intro);
        OptionPanelAPI o = dialog.getOptionPanel();
        o.clearOptions();
        for (TurnIn ti : list) {
            o.addOption("Hand over " + (ti.count > 1 ? ti.count + "x " : "") + ti.name + " (+" + ti.count * ti.glassEach
                    + " Pitch Glass)", ti);
        }
        o.addOption("Back", Nav.MAIN);
        dialog.setOptionOnEscape("Back", Nav.MAIN);
    }

    // ------------------------------------------------------------------------------------------------- content

    private static List<Offer> offers() {
        List<Offer> list = new ArrayList<Offer>();
        list.add(new Offer(Kind.TUNING, null, "Lattice Tuning", PitchGlass.PRICE_TUNING, RepLevel.SUSPICIOUS,
                "The Luthiers retune every lattice core in your fleet against the reference pitch. For 30 days your "
                        + "Lattice ships gain Resonance 25% faster and lose it half as fast."));
        list.add(new Offer(Kind.ITEM, RslIds.ITEM_BP_WEAPONS, "Cantorate Weapon Blueprints",
                PitchGlass.PRICE_BP_WEAPONS, RepLevel.FAVORABLE,
                "Rail, lance and spike patterns: every Cantorate weapon, for your heavy industry."));
        list.add(new Offer(Kind.ITEM, RslIds.ITEM_BP_WINGS, "Cantorate Wing Blueprints", PitchGlass.PRICE_BP_WINGS,
                RepLevel.FAVORABLE, "Fighter LPCs for the Trill, Cadenza and Requiem wings."));
        list.add(new Offer(Kind.ITEM, RslIds.ITEM_BP_HULLS, "Cantorate Hull Blueprints", PitchGlass.PRICE_BP_HULLS,
                RepLevel.FAVORABLE, "The hull scores of the Cantorate's line ships, from the Grace Note to the "
                + "Conductor."));
        list.add(new Offer(Kind.HULLMOD, RslIds.HULLMOD_CONCERT_PITCH, "Concert Pitch", PitchGlass.PRICE_CONCERT_PITCH,
                RepLevel.COOPERATIVE, "The Luthiers teach your engineers the Concert Pitch augment: Lattice ships "
                + "can mount it (more weapon range, combat readiness and EMP resistance)."));
        list.add(new Offer(Kind.ITEM, RslIds.ITEM_METRONOME, "Pulsar Metronome", PitchGlass.PRICE_METRONOME,
                RepLevel.COOPERATIVE, "A colony item for a Waystation: a navigation clock keyed to a pulsar. "
                + "Better accessibility and stability, more of both in a neutron star system."));
        // the Lacrimosa questline (CAMPAIGN.md section 8): Virtuoso work once it is completed, by the council's path
        MemoryAPI g = Global.getSector().getMemoryWithoutUpdate();
        if (g.getBoolean(RslIds.MEM_VIRTUOSO_UPGRADED)) {
            list.add(new Offer(Kind.HULLMOD, RslIds.HULLMOD_UNBOUND, "Unbound Core", PitchGlass.PRICE_UNBOUND,
                    PitchGlass.PRICE_UNBOUND_CREDITS, RepLevel.SUSPICIOUS, "Abelard strips the safety tuning from the "
                    + "Virtuoso's core: more speed and twice the dissipation, no venting, a third of the peak time. "
                    + "Your engineers learn to fit it."));
            boolean chorus = LacrimosaIntel.isChorus();
            list.add(new Offer(Kind.HULLMOD, chorus ? RslIds.HULLMOD_CHORUS_MOVEMENT : RslIds.HULLMOD_SOLO_MOVEMENT,
                    chorus ? "Chorus Movement" : "Solo Movement", PitchGlass.PRICE_MOVEMENT, RepLevel.SUSPICIOUS,
                    chorus ? "The Precentor's retuning: the Virtuoso steals less readiness, but shares half of what it "
                            + "steals with allied ships nearby."
                            : "Venn's own tuning: alone, the Virtuoso steals more readiness and hits harder; in "
                            + "company it steals less."));
        }
        if (g.getBoolean(RslIds.MEM_HUSH_DONE)) {
            list.add(new Offer(Kind.HUSH_SEAMS, null, "Hush seams", PitchGlass.PRICE_HUSH_SEAMS, RepLevel.SUSPICIOUS,
                    "A cosmetic retuning: the Virtuoso's seams glow the violet of the Hush. Buy it again to restore "
                    + "the teal."));
        }
        return list;
    }

    private static int discounted(int price) {
        if (!LacrimosaIntel.isChorus()) return price;
        return Math.round(price * (1f - Lacrimosa.CHORUS_DISCOUNT));
    }

    private static String priceText(Offer of) {
        String s = of.price + " Pitch Glass";
        return of.credits > 0 ? s + " + " + Misc.getDGSCredits(of.credits) : s;
    }

    private static boolean owned(Offer of) {
        if (of.kind == Kind.TUNING) {
            CampaignFleetAPI f = Global.getSector().getPlayerFleet();
            return f != null && f.getMemoryWithoutUpdate().getBoolean(RslIds.MEM_TUNED);
        }
        if (of.kind == Kind.HULLMOD) return Global.getSector().getPlayerFaction().knowsHullMod(of.id);
        return false;   // items stack; Hush seams toggle
    }

    private static List<TurnIn> coreTurnIns() {
        List<TurnIn> list = new ArrayList<TurnIn>();
        CampaignFleetAPI f = Global.getSector().getPlayerFleet();
        if (f == null) return list;
        String[][] cores = {{Commodities.ALPHA_CORE, "alpha core"}, {Commodities.BETA_CORE, "beta core"},
                {Commodities.GAMMA_CORE, "gamma core"}};
        int[] glass = {PitchGlass.CORE_ALPHA, PitchGlass.CORE_BETA, PitchGlass.CORE_GAMMA};
        for (int i = 0; i < cores.length; i++) {
            int n = (int) f.getCargo().getCommodityQuantity(cores[i][0]);
            if (n > 0) list.add(new TurnIn(true, cores[i][0], cores[i][1] + (n > 1 ? "s" : ""), n, glass[i]));
        }
        return list;
    }

    private static List<TurnIn> itemTurnIns() {
        List<TurnIn> list = new ArrayList<TurnIn>();
        CampaignFleetAPI f = Global.getSector().getPlayerFleet();
        if (f == null) return list;
        for (CargoStackAPI s : f.getCargo().getStacksCopy()) {
            if (!s.isSpecialStack() || s.getSpecialDataIfSpecial() == null) continue;
            String id = s.getSpecialDataIfSpecial().getId();
            SpecialItemSpecAPI spec = Global.getSettings().getSpecialItemSpec(id);
            if (spec == null || !spec.hasTag("colony_item") || RslIds.ITEM_METRONOME.equals(id)) continue;
            int each = Items.PRISTINE_NANOFORGE.equals(id) ? PitchGlass.ITEM_PRISTINE_NANOFORGE
                    : Items.CORRUPTED_NANOFORGE.equals(id) ? PitchGlass.ITEM_CORRUPTED_NANOFORGE
                    : Items.SYNCHROTRON.equals(id) ? PitchGlass.ITEM_SYNCHROTRON : PitchGlass.ITEM_OTHER;
            list.add(new TurnIn(false, id, spec.getName(), 1, each));   // one at a time: they are rare and valuable
        }
        return list;
    }

    // ------------------------------------------------------------------------------------------------- actions

    private void buy(Offer of) {
        CargoAPI cargo = Global.getSector().getPlayerFleet().getCargo();
        if (cargo.getCredits().get() < of.credits || !PitchGlass.spend(of.price)) {
            showBuy();
            return;
        }
        if (of.credits > 0) cargo.getCredits().subtract(of.credits);
        TextPanelAPI t = dialog.getTextPanel();
        switch (of.kind) {
            case TUNING:
                Global.getSector().getPlayerFleet().getMemoryWithoutUpdate().set(RslIds.MEM_TUNED, true, 30f);
                t.addPara("For a day and a night the hulls of your Lattice ships ring with the reference pitch.");
                break;
            case HULLMOD:
                Global.getSector().getPlayerFaction().addKnownHullMod(of.id);
                t.addPara("Your engineers can now fit %s.", Misc.getHighlightColor(), of.name);
                break;
            case HUSH_SEAMS:
                MemoryAPI fm = Global.getSector().getPlayerFleet().getMemoryWithoutUpdate();
                boolean on = !fm.getBoolean(RslIds.MEM_HUSH_SEAMS);
                fm.set(RslIds.MEM_HUSH_SEAMS, on);
                t.addPara(on ? "The Virtuoso's seams now glow the violet of the Hush."
                        : "The Virtuoso's seams glow teal again.");
                break;
            default:
                cargo.addSpecial(new SpecialItemData(of.id, null), 1);
                t.addPara("Gained %s.", Misc.getHighlightColor(), of.name);
                break;
        }
        t.addPara("Paid %s.", Misc.getNegativeHighlightColor(), priceText(of));
        showMain();
    }

    private void turnIn(TurnIn ti) {
        CargoAPI cargo = Global.getSector().getPlayerFleet().getCargo();
        TextPanelAPI t = dialog.getTextPanel();
        if (ti.core) {
            cargo.removeCommodity(ti.id, ti.count);
            Global.getSector().getPlayerFaction().adjustRelationship(Factions.HEGEMONY,
                    PitchGlass.CORE_HEGEMONY_REP * ti.count);
            t.addPara("The Luthiers take the cores into a shielded vault. Through the glass you watch them sing the "
                    + "cores silent, one tone at a time, until nothing in them answers.");
            t.addPara("Word reaches the Hegemony's inspectors: relations with the Hegemony improve slightly.",
                    Misc.getPositiveHighlightColor());
        } else {
            cargo.removeItems(CargoAPI.CargoItemType.SPECIAL, new SpecialItemData(ti.id, null), 1);
            t.addPara("Abelard turns the %s over in his hands for a long time before he names a price.",
                    Misc.getHighlightColor(), ti.name);
        }
        int glass = ti.count * ti.glassEach;
        PitchGlass.add(glass);
        t.addPara("Gained %s Pitch Glass.", Misc.getPositiveHighlightColor(), "" + glass);
        showMain();
    }

    private void leave() {
        dialog.setPlugin(originalPlugin);
        FireAll.fire(null, dialog, memoryMap, "PopulateOptions");
    }

    // ------------------------------------------------------------------------------------------------- plugin

    @Override
    public void optionSelected(String optionText, Object optionData) {
        if (optionText != null) {
            dialog.getTextPanel().addParagraph(optionText, Global.getSettings().getColor("buttonText"));
        }
        if (optionData == Nav.BUY) {
            showBuy();
        } else if (optionData == Nav.SILENCE) {
            showTurnIns(coreTurnIns(), "\"Cores?\" Abelard does not ask where you found them. \"We will pay in glass. "
                    + "Nobody needs to know they ever existed.\"");
        } else if (optionData == Nav.TURN_IN) {
            showTurnIns(itemTurnIns(), "\"Domain work,\" Abelard says, almost tenderly. \"We cannot build these "
                    + "any more. We can still learn from them.\"");
        } else if (optionData == Nav.MAIN) {
            showMain();
        } else if (optionData == Nav.LEAVE) {
            leave();
        } else if (optionData instanceof Offer) {
            showConfirm((Offer) optionData);
        } else if (optionData instanceof Confirm) {
            buy(((Confirm) optionData).offer);
        } else if (optionData instanceof TurnIn) {
            turnIn((TurnIn) optionData);
        } else {
            showMain();
        }
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
