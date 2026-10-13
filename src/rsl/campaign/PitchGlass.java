package rsl.campaign;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.campaign.CampaignFleetAPI;
import com.fs.starfarer.api.campaign.CargoAPI;
import com.fs.starfarer.api.campaign.FactionAPI;
import com.fs.starfarer.api.campaign.RepLevel;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import rsl.RslIds;

/**
 * Pitch Glass, the Cantorate's currency (CAMPAIGN.md section 8): a non-economy commodity held in the player's cargo.
 * Every source and every price lives here, so balancing is one file.
 */
public final class PitchGlass {
    private PitchGlass() {
    }

    // ---- sources
    /** Per Lattice ship disabled or destroyed in a battle the player wins, by hull size (x HUSH_MULT for the Hush). */
    public static final int SALVAGE_FRIGATE = 1, SALVAGE_DESTROYER = 2, SALVAGE_CRUISER = 4, SALVAGE_CAPITAL = 8;
    public static final int HUSH_MULT = 3;
    /** Monthly stipend at Cooperative with the Cantorate. */
    public static final int STIPEND = 10;
    /** "Silencing" AI cores at the Workshop, per core. */
    public static final int CORE_GAMMA = 5, CORE_BETA = 15, CORE_ALPHA = 40;
    /** Hegemony reputation per silenced core (the Cantorate does it to keep the inspectors away). */
    public static final float CORE_HEGEMONY_REP = 0.01f;
    /** Domain-era colony items turned in. */
    public static final int ITEM_PRISTINE_NANOFORGE = 150, ITEM_CORRUPTED_NANOFORGE = 40, ITEM_SYNCHROTRON = 80,
            ITEM_OTHER = 40;

    // ---- prices (the Virtuoso's are in the questline, Stage 5)
    public static final int PRICE_TUNING = 15;
    public static final int PRICE_BP_WEAPONS = 150, PRICE_BP_WINGS = 120, PRICE_BP_HULLS = 250;
    public static final int PRICE_CONCERT_PITCH = 200;
    public static final int PRICE_METRONOME = 250;

    public static int salvageFor(HullSize size) {
        if (size == null) return 0;
        switch (size) {
            case FRIGATE:
                return SALVAGE_FRIGATE;
            case DESTROYER:
                return SALVAGE_DESTROYER;
            case CRUISER:
                return SALVAGE_CRUISER;
            case CAPITAL_SHIP:
                return SALVAGE_CAPITAL;
            default:
                return 0;
        }
    }

    public static int held() {
        CampaignFleetAPI f = Global.getSector().getPlayerFleet();
        return f == null ? 0 : (int) f.getCargo().getCommodityQuantity(RslIds.COMMODITY_PITCHGLASS);
    }

    public static void add(int n) {
        CampaignFleetAPI f = Global.getSector().getPlayerFleet();
        if (f == null || n <= 0) return;
        f.getCargo().addCommodity(RslIds.COMMODITY_PITCHGLASS, n);
    }

    /** Removes n if the player holds that much; returns whether it did. */
    public static boolean spend(int n) {
        CampaignFleetAPI f = Global.getSector().getPlayerFleet();
        if (f == null || held() < n) return false;
        CargoAPI c = f.getCargo();
        c.removeCommodity(RslIds.COMMODITY_PITCHGLASS, n);
        return true;
    }

    public static RepLevel rep() {
        FactionAPI choir = Global.getSector().getFaction(RslIds.FACTION_CHOIR);
        return choir == null ? RepLevel.NEUTRAL : choir.getRelToPlayer().getLevel();
    }
}
