package rsl.rulecmd;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.campaign.CampaignFleetAPI;
import com.fs.starfarer.api.campaign.FleetAssignment;
import com.fs.starfarer.api.campaign.InteractionDialogAPI;
import com.fs.starfarer.api.campaign.LocationAPI;
import com.fs.starfarer.api.campaign.OptionPanelAPI;
import com.fs.starfarer.api.campaign.PlanetAPI;
import com.fs.starfarer.api.campaign.SectorAPI;
import com.fs.starfarer.api.campaign.SectorEntityToken;
import com.fs.starfarer.api.campaign.StarSystemAPI;
import com.fs.starfarer.api.campaign.TextPanelAPI;
import com.fs.starfarer.api.campaign.rules.MemoryAPI;
import com.fs.starfarer.api.impl.campaign.fleets.FleetFactoryV3;
import com.fs.starfarer.api.impl.campaign.fleets.FleetParamsV3;
import com.fs.starfarer.api.impl.campaign.ids.Factions;
import com.fs.starfarer.api.impl.campaign.ids.FleetTypes;
import com.fs.starfarer.api.impl.campaign.ids.Tags;
import com.fs.starfarer.api.impl.campaign.rulecmd.BaseCommandPlugin;
import com.fs.starfarer.api.util.Misc;
import com.fs.starfarer.api.util.Misc.Token;
import com.fs.starfarer.api.util.WeightedRandomPicker;
import rsl.RslIds;
import rsl.campaign.TunerContractIntel;

import java.util.List;
import java.util.Map;

/**
 * The tuners' contract board at Tacet Station (rules.csv rsl_contract*): "RslContracts board" shows the board,
 * "RslContracts accept" spawns a raider fleet in a system near Vell and starts a {@link TunerContractIntel}.
 * One contract at a time, then a {@link #COOLDOWN}-day wait from the day it was taken.
 */
public class RslContracts extends BaseCommandPlugin {
    public static final float COOLDOWN = 30f;
    public static final float SEARCH_LY = 10f;
    public static final float MIN_POINTS = 40f, MAX_POINTS = 160f;
    public static final int GLASS_MIN = 20, GLASS_MAX = 40;
    public static final int CREDITS_PER_POINT = 800;

    @Override
    public boolean execute(String ruleId, InteractionDialogAPI dialog, List<Token> params,
                           Map<String, MemoryAPI> memoryMap) {
        String cmd = params.isEmpty() ? "board" : params.get(0).getString(memoryMap);
        if ("accept".equals(cmd)) return accept(dialog);
        board(dialog);
        return true;
    }

    private static float points() {
        CampaignFleetAPI player = Global.getSector().getPlayerFleet();
        float fp = player == null ? 0f : player.getFleetPoints();
        return Math.max(MIN_POINTS, Math.min(MAX_POINTS, fp * 0.5f));
    }

    private static int glassFor(float pts) {
        return Math.round(GLASS_MIN + (GLASS_MAX - GLASS_MIN) * (pts - MIN_POINTS) / (MAX_POINTS - MIN_POINTS));
    }

    private static void board(InteractionDialogAPI dialog) {
        TextPanelAPI t = dialog.getTextPanel();
        OptionPanelAPI o = dialog.getOptionPanel();
        o.clearOptions();
        TunerContractIntel active = TunerContractIntel.active();
        if (active != null) {
            t.addPara("Your name is still chalked on the board: the raiders in %s, %s days left.",
                    Misc.getHighlightColor(), active.getSystemName(), "" + active.getDaysLeft());
        } else if (Global.getSector().getMemoryWithoutUpdate().getBoolean(RslIds.MEM_CONTRACT_COOLDOWN)) {
            t.addPara("The board is bare. An Archivist tells you the lanes are quiet for now; come back in a few "
                    + "weeks.");
        } else {
            float pts = points();
            t.addPara("A single contract hangs on the board, stamped with the seal of the Archivists: a raider fleet "
                    + "is preying on the crystal convoys near Vell. The Cantorate will pay %s Pitch Glass and %s for "
                    + "its flagship, within %s days.", Misc.getHighlightColor(), "" + glassFor(pts),
                    Misc.getDGSCredits(pts * CREDITS_PER_POINT), "" + (int) TunerContractIntel.DURATION);
            o.addOption("Take the contract", "rsl_contractAccept");
        }
        o.addOption("Back", "rsl_contractBack");
    }

    private static boolean accept(InteractionDialogAPI dialog) {
        SectorAPI sector = Global.getSector();
        if (TunerContractIntel.active() != null) return false;
        LocationAPI here = dialog.getInteractionTarget().getContainingLocation();
        StarSystemAPI system = pickSystem(sector, here);
        if (system == null) {
            dialog.getTextPanel().addPara("The Archivist frowns at the charts and takes the contract back down.");
            return false;
        }
        float pts = points();
        boolean path = sector.getFaction(Factions.LUDDIC_PATH) != null && Math.random() < 0.3;
        String faction = path ? Factions.LUDDIC_PATH : Factions.PIRATES;
        FleetParamsV3 p = new FleetParamsV3(null, system.getLocation(), faction, null, FleetTypes.PATROL_MEDIUM, pts,
                0f, 0f, 0f, 0f, 0f, 0f);
        CampaignFleetAPI fleet = FleetFactoryV3.createFleet(p);
        if (fleet == null || fleet.isEmpty()) {
            dialog.getTextPanel().addPara("The Archivist frowns: the raiders have already scattered.");
            return false;
        }
        String targetName = path ? "Luddic Path raiders" : "pirate raiders";
        fleet.setName(path ? "Pather Raiders" : "Raiders");
        fleet.setNoFactionInName(true);
        Misc.makeHostile(fleet);
        system.addEntity(fleet);
        SectorEntityToken anchor = anchor(system);
        fleet.setLocation(anchor.getLocation().x + 300f, anchor.getLocation().y + 300f);
        fleet.addAssignment(FleetAssignment.PATROL_SYSTEM, anchor, TunerContractIntel.DURATION + 10f);

        TunerContractIntel intel = new TunerContractIntel(fleet, system, targetName, glassFor(pts),
                Math.round(pts * CREDITS_PER_POINT));
        sector.getIntelManager().addIntel(intel, false, dialog.getTextPanel());
        sector.getMemoryWithoutUpdate().set(RslIds.MEM_CONTRACT_COOLDOWN, true, COOLDOWN);
        dialog.getTextPanel().addPara("The Archivist chalks your name across the contract. \"Bring them silence.\"");
        return true;
    }

    /** A star system within {@link #SEARCH_LY} of here (Vell), not Vell itself and not hidden; falls back to here. */
    private static StarSystemAPI pickSystem(SectorAPI sector, LocationAPI here) {
        StarSystemAPI home = here instanceof StarSystemAPI ? (StarSystemAPI) here : null;
        WeightedRandomPicker<StarSystemAPI> picker = new WeightedRandomPicker<StarSystemAPI>();
        if (home != null) {
            for (StarSystemAPI s : sector.getStarSystems()) {
                if (s == home || s.hasTag(Tags.THEME_HIDDEN) || s.getPlanets().size() < 2) continue;
                if (Misc.getDistanceLY(home.getLocation(), s.getLocation()) > SEARCH_LY) continue;
                picker.add(s);
            }
        }
        StarSystemAPI pick = picker.pick();
        return pick != null ? pick : home;
    }

    private static SectorEntityToken anchor(StarSystemAPI system) {
        WeightedRandomPicker<SectorEntityToken> picker = new WeightedRandomPicker<SectorEntityToken>();
        for (PlanetAPI p : system.getPlanets()) {
            if (!p.isStar()) picker.add(p);
        }
        SectorEntityToken pick = picker.pick();
        return pick != null ? pick : system.getCenter();
    }
}
