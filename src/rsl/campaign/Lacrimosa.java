package rsl.campaign;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.campaign.CampaignFleetAPI;
import com.fs.starfarer.api.campaign.SpecialItemData;
import com.fs.starfarer.api.campaign.TextPanelAPI;
import com.fs.starfarer.api.characters.PersonAPI;
import com.fs.starfarer.api.combat.ShipHullSpecAPI;
import com.fs.starfarer.api.combat.ShipVariantAPI;
import com.fs.starfarer.api.fleet.FleetMemberAPI;
import com.fs.starfarer.api.fleet.FleetMemberType;
import com.fs.starfarer.api.impl.campaign.ids.Factions;
import com.fs.starfarer.api.impl.campaign.ids.Tags;
import com.fs.starfarer.api.loading.HullModSpecAPI;
import com.fs.starfarer.api.loading.VariantSource;
import com.fs.starfarer.api.loading.WeaponSlotAPI;
import com.fs.starfarer.api.util.Misc;
import org.apache.log4j.Logger;
import rsl.RslIds;

/**
 * The Lacrimosa's numbers and the actions on the player's fleet: the start gate, the Unsung grant, Sung's sale, the
 * Hush's rewards and the completion (Unsung -> Virtuoso). State lives in {@link LacrimosaIntel}.
 *
 * Testing from the Console Commands mod: {@code runcode rsl.campaign.Lacrimosa.debug("council")} jumps the quest to a
 * stage (buoys, institute, council, recording, search, hush, return), granting the Unsung on the way.
 */
public final class Lacrimosa {
    private static final Logger log = Global.getLogger(Lacrimosa.class);

    private Lacrimosa() {
    }

    // ---- beat 1 gate (mid-game)
    public static final int START_LEVEL = 8;
    public static final float START_FLEET_DP = 80f;
    // ---- beat 2
    /** Waking the Lacrimosa drinks every ship in the fleet down to this CR. */
    public static final float WAKE_CR = 0.3f;
    public static final String UNSUNG_NAME = "Lacrimosa";
    // ---- beat 3
    public static final int SUNG_CREDITS = 2000000;
    public static final float SUNG_TT_REP = 0.25f;
    public static final float SOLD_CHOIR_REP = -0.15f;
    // ---- beat 4
    public static final float CHORUS_REP = 0.20f;
    public static final float SOLO_REP = -0.10f;
    /** Chorus path: the Workshop's prices drop by this fraction. */
    public static final float CHORUS_DISCOUNT = 0.10f;
    // ---- beat 5
    public static final int HUSH_GLASS = 150;
    // ---- beat 6 (CAMPAIGN.md section 8)
    public static final int PRICE_GLASS = 600;
    public static final int PRICE_CREDITS = 3000000;
    /** The Unsung is gone: the Institute's spare frame, once, for this much more and a story point. */
    public static final int SPARE_CREDITS = 1000000;
    public static final int SPARE_STORY_POINTS = 1;

    // ------------------------------------------------------------------------------------------------- gate

    /** Level 8+ and an 80+ DP fleet, Cantorate not hostile, quest not started. */
    public static boolean canStart() {
        if (LacrimosaIntel.started()) return false;
        if (Global.getSector().getPlayerStats().getLevel() < START_LEVEL) return false;
        if (PitchGlass.rep().isAtBest(com.fs.starfarer.api.campaign.RepLevel.HOSTILE)) return false;
        return fleetDP() >= START_FLEET_DP;
    }

    public static float fleetDP() {
        CampaignFleetAPI pf = Global.getSector().getPlayerFleet();
        if (pf == null) return 0f;
        float dp = 0f;
        for (FleetMemberAPI m : pf.getFleetData().getMembersListCopy()) {
            if (!m.isFighterWing()) dp += m.getDeploymentPointsCost();
        }
        return dp;
    }

    // ------------------------------------------------------------------------------------------------- the Unsung

    /** The Lacrimosa (or any Unsung) in the player's fleet, or null. */
    public static FleetMemberAPI findUnsung() {
        return findHull(RslIds.HULL_UNSUNG);
    }

    public static FleetMemberAPI findHull(String hullId) {
        CampaignFleetAPI pf = Global.getSector().getPlayerFleet();
        if (pf == null) return null;
        for (FleetMemberAPI m : pf.getFleetData().getMembersListCopy()) {
            if (m.getHullSpec() != null && hullId.equals(m.getHullSpec().getBaseHullId())) return m;
        }
        return null;
    }

    /** Beat 2: the Unsung joins, named Lacrimosa, at full CR (it drank the fleet's). Exactly once per save. */
    public static FleetMemberAPI grantUnsung(TextPanelAPI text) {
        if (Global.getSector().getMemoryWithoutUpdate().getBoolean(RslIds.MEM_VIRTUOSO_GRANTED)) return findUnsung();
        Global.getSector().getMemoryWithoutUpdate().set(RslIds.MEM_VIRTUOSO_GRANTED, true);
        FleetMemberAPI m = Global.getFactory().createFleetMember(FleetMemberType.SHIP, RslIds.VARIANT_UNSUNG);
        m.setVariant(m.getVariant().clone(), false, false);
        m.getVariant().setSource(VariantSource.REFIT);
        m.getVariant().addTag(Tags.VARIANT_ALWAYS_RECOVERABLE);
        m.setShipName(UNSUNG_NAME);
        CampaignFleetAPI pf = Global.getSector().getPlayerFleet();
        pf.getFleetData().addFleetMember(m);
        m.updateStats();
        m.getRepairTracker().setCR(m.getRepairTracker().getMaxCR());
        if (text != null) {
            text.setFontSmallInsignia();
            text.addParagraph("Gained the " + UNSUNG_NAME + " (Virtuoso, Unsung)", Misc.getPositiveHighlightColor());
            text.setFontInsignia();
        }
        return m;
    }

    /** Sung's sale: the Unsung leaves, credits and Tri-Tachyon goodwill arrive, the Cantorate hears of it. */
    public static void sellToSung(TextPanelAPI text) {
        CampaignFleetAPI pf = Global.getSector().getPlayerFleet();
        FleetMemberAPI m = findUnsung();
        if (m != null) {
            PersonAPI c = m.getCaptain();
            if (c != null && !c.isDefault() && !c.isPlayer()) m.setCaptain(null);
            pf.getFleetData().removeFleetMember(m);
        }
        pf.getCargo().getCredits().add(SUNG_CREDITS);
        Global.getSector().getPlayerFaction().adjustRelationship(Factions.TRITACHYON, SUNG_TT_REP);
        Global.getSector().getPlayerFaction().adjustRelationship(RslIds.FACTION_CHOIR, SOLD_CHOIR_REP);
        if (text != null) {
            text.setFontSmallInsignia();
            text.addParagraph("Lost the " + UNSUNG_NAME, Misc.getNegativeHighlightColor());
            text.addPara("Gained %s", Misc.getHighlightColor(), Misc.getDGSCredits(SUNG_CREDITS));
            text.addPara("Relations with Tri-Tachyon improved; relations with the Cantorate worsened",
                    Misc.getHighlightColor());
            text.setFontInsignia();
        }
    }

    /** Sung can buy only an Unsung that is in the fleet, not the flagship, and not the fleet's only ship. */
    public static String whyCannotSell() {
        FleetMemberAPI m = findUnsung();
        if (m == null) return "The Lacrimosa is not in your fleet.";
        CampaignFleetAPI pf = Global.getSector().getPlayerFleet();
        if (m.isFlagship() || pf.getFlagship() == m) return "You command the fleet from the Lacrimosa.";
        if (pf.getFleetData().getNumMembers() <= 1) return "The Lacrimosa is your only ship.";
        return null;
    }

    // ------------------------------------------------------------------------------------------------- beat 5

    /** The sash and vanes (quest item), Pitch Glass and a Concert Pitch modspec. */
    public static void hushRewards() {
        CampaignFleetAPI pf = Global.getSector().getPlayerFleet();
        if (pf == null) return;
        pf.getCargo().addSpecial(new SpecialItemData(RslIds.ITEM_SASH, null), 1);
        PitchGlass.add(HUSH_GLASS);
        pf.getCargo().addHullmods(RslIds.HULLMOD_CONCERT_PITCH, 1);
        Global.getSector().getCampaignUI().addMessage("The Hush falls silent. In the Kyrie's hold you find the "
                + "Lacrimosa's sash and vanes, " + HUSH_GLASS + " Pitch Glass and a Concert Pitch augment.",
                Misc.getTextColor(), "" + HUSH_GLASS, null, Misc.getHighlightColor(), null);
    }

    public static boolean hasSash() {
        CampaignFleetAPI pf = Global.getSector().getPlayerFleet();
        return pf != null && pf.getCargo().getQuantity(com.fs.starfarer.api.campaign.CargoAPI.CargoItemType.SPECIAL,
                new SpecialItemData(RslIds.ITEM_SASH, null)) > 0;
    }

    // ------------------------------------------------------------------------------------------------- beat 6

    /**
     * Unsung -> Virtuoso, in place: the same fleet member (name, captain, id, flagship status) gets a new Virtuoso
     * variant carrying the Unsung's fitted weapons, hullmods, S-mods, vents and capacitors. Rebuilding the variant from
     * the Virtuoso's hull spec (rather than vanilla's variant.setHullSpecAPI, which keeps the old variant's built-ins)
     * gives the Virtuoso's own built-in weapons (Sforzando), hullmods (Bravura) and decorative vanes. The Luthiers'
     * rebuild clears D-mods. CR goes to maximum.
     */
    public static FleetMemberAPI upgrade(FleetMemberAPI unsung) {
        ShipHullSpecAPI spec = Global.getSettings().getHullSpec(RslIds.HULL_VIRTUOSO);
        ShipVariantAPI old = unsung.getVariant();
        ShipVariantAPI v = Global.getSettings().createEmptyVariant(RslIds.HULL_VIRTUOSO + "_" + Misc.genUID(), spec);
        v.setSource(VariantSource.REFIT);
        for (String slotId : old.getNonBuiltInWeaponSlots()) {
            String w = old.getWeaponId(slotId);
            WeaponSlotAPI slot = v.getSlot(slotId);
            if (w == null || slot == null || slot.isBuiltIn() || slot.isDecorative() || slot.isSystemSlot()) continue;
            v.addWeapon(slotId, w);   // the two hulls share every fittable slot (the Unsung's .ship is derived)
        }
        for (String id : old.getNonBuiltInHullmods()) {
            HullModSpecAPI hm = Global.getSettings().getHullModSpec(id);
            if (hm == null || hm.hasTag(Tags.HULLMOD_DMOD) || old.getPermaMods().contains(id)) continue;
            v.addMod(id);
        }
        for (String id : old.getSMods()) {
            HullModSpecAPI hm = Global.getSettings().getHullModSpec(id);
            if (hm == null || hm.hasTag(Tags.HULLMOD_DMOD)) continue;
            v.addMod(id);
            v.addPermaMod(id, true);
        }
        for (String id : old.getSModdedBuiltIns()) {
            String nid = RslIds.HULLMOD_BRAVURA_LOCKED.equals(id) ? RslIds.HULLMOD_BRAVURA : id;
            if (spec.getBuiltInMods().contains(nid)) v.getSModdedBuiltIns().add(nid);
        }
        v.setNumFluxVents(old.getNumFluxVents());
        v.setNumFluxCapacitors(old.getNumFluxCapacitors());
        for (String tag : old.getTags()) v.addTag(tag);
        v.addTag(Tags.VARIANT_ALWAYS_RECOVERABLE);
        v.autoGenerateWeaponGroups();
        unsung.setVariant(v, false, true);
        unsung.updateStats();
        unsung.getRepairTracker().setCR(unsung.getRepairTracker().getMaxCR());
        log.info("Resonance Lattice: the Lacrimosa was completed (" + unsung.getShipName() + ")");
        return unsung;
    }

    /** Fallback for a lost or sold Unsung: a fresh Virtuoso from the Institute's spare frame (once). */
    public static FleetMemberAPI spareVirtuoso() {
        Global.getSector().getMemoryWithoutUpdate().set(RslIds.MEM_SPARE_USED, true);
        FleetMemberAPI m = Global.getFactory().createFleetMember(FleetMemberType.SHIP, RslIds.VARIANT_VIRTUOSO);
        m.setVariant(m.getVariant().clone(), false, false);
        m.getVariant().setSource(VariantSource.REFIT);
        m.getVariant().addTag(Tags.VARIANT_ALWAYS_RECOVERABLE);
        m.setShipName(UNSUNG_NAME);
        Global.getSector().getPlayerFleet().getFleetData().addFleetMember(m);
        m.updateStats();
        m.getRepairTracker().setCR(m.getRepairTracker().getMaxCR());
        return m;
    }

    // ------------------------------------------------------------------------------------------------- testing

    /** Console helper: jump the quest to {@code stage} (see the class comment). Never called by the mod itself. */
    public static void debug(String stage) {
        try {
            LacrimosaIntel q = LacrimosaIntel.get();
            if (q == null) q = LacrimosaIntel.start(null);
            if (q == null) return;
            q.debugJump(stage);
        } catch (Throwable t) {
            log.error("Resonance Lattice: debug jump failed", t);
        }
    }
}
