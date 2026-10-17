package rsl.campaign;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.campaign.CampaignFleetAPI;
import com.fs.starfarer.api.campaign.FleetAssignment;
import com.fs.starfarer.api.campaign.SectorEntityToken;
import com.fs.starfarer.api.campaign.rules.MemoryAPI;
import com.fs.starfarer.api.characters.FullName;
import com.fs.starfarer.api.characters.PersonAPI;
import com.fs.starfarer.api.combat.ShipVariantAPI;
import com.fs.starfarer.api.fleet.FleetMemberAPI;
import com.fs.starfarer.api.impl.campaign.fleets.FleetFactoryV3;
import com.fs.starfarer.api.impl.campaign.ids.Commodities;
import com.fs.starfarer.api.impl.campaign.ids.Factions;
import com.fs.starfarer.api.impl.campaign.ids.FleetTypes;
import com.fs.starfarer.api.impl.campaign.ids.MemFlags;
import com.fs.starfarer.api.impl.campaign.ids.Personalities;
import com.fs.starfarer.api.impl.campaign.ids.Ranks;
import com.fs.starfarer.api.impl.campaign.ids.Skills;
import com.fs.starfarer.api.impl.campaign.ids.Tags;
import com.fs.starfarer.api.loading.VariantSource;
import com.fs.starfarer.api.util.Misc;
import rsl.RslIds;

import java.util.Random;

/**
 * The two encore fleets after the Lacrimosa questline (user, 2026-10-13):
 * <ul>
 * <li>{@link #diesIrae}: one ship - the Dies Irae, a second Virtuoso that Tri-Tachyon's Special Projects built around a
 * cracked core taken from the Hush's graveyard - flown by Commander Isolde Raike, a level-15 commander (every combat
 * skill elite plus her own, Second Voice). Waits at the Antiphon Institute for a duel.</li>
 * <li>{@link #silence}: the Silence, an AI armada of {@link #SILENCE_MIN_DP}+ deployment points (Remnant battle line
 * and Omega hulls, alpha-core captains, an omega-core commander, two S-mods per ship) that heard the finished
 * Lacrimosa sing. Optional and meant to be nearly impossible. It never moves and never attacks: the player brings the
 * fight to it.</li>
 * </ul>
 */
public final class EncoreFleets {
    private EncoreFleets() {
    }

    public static final int RAIKE_LEVEL = 15;
    public static final int DIES_IRAE_SMODS = 3;
    public static final int SILENCE_SMODS = 2;
    /** The armada is built until its deployment points reach this. */
    public static final float SILENCE_MIN_DP = 1500f;
    /** Every combat skill vanilla gives an officer (14), all elite; Second Voice makes it level 15. */
    static final String[] COMBAT_SKILLS = {Skills.HELMSMANSHIP, Skills.COMBAT_ENDURANCE, Skills.IMPACT_MITIGATION,
            Skills.DAMAGE_CONTROL, Skills.FIELD_MODULATION, Skills.POINT_DEFENSE, Skills.TARGET_ANALYSIS,
            Skills.BALLISTIC_MASTERY, Skills.SYSTEMS_EXPERTISE, Skills.MISSILE_SPECIALIZATION, Skills.GUNNERY_IMPLANTS,
            Skills.ENERGY_WEAPON_MASTERY, Skills.ORDNANCE_EXPERTISE, Skills.POLARIZED_ARMOR};
    /** The Dies Irae's S-mods (no Unbound Core: its penalty would only weaken her). */
    static final String[] DIES_IRAE_SMOD_IDS = {"hardenedshieldemitter", "fluxdistributor", "reinforcedhull"};

    /** The Silence, by battle line: variant, count. Omega first (the heart), then the Remnant line. */
    static final Object[][] SILENCE = {
            {"tesseract_Attack", 2}, {"tesseract_Shieldbreaker", 1}, {"tesseract_Disruptor", 1},
            {"facet_Attack", 2}, {"facet_Shieldbreaker", 2}, {"facet_Armorbreaker", 2},
            {"shard_left_Attack", 3}, {"shard_right_Attack", 3},
            {"radiant_Assault", 5}, {"radiant_Standard", 5}, {"radiant_Strike", 2}, {"apex_Assault", 2},
            {"nova_Attack", 4}, {"nova_Standard", 4},
            {"brilliant_Standard", 5}, {"brilliant_Support", 3},
            {"scintilla_Strike", 3}, {"fulgent_Assault", 4}, {"fulgent_Support", 2},
            {"glimmer_Assault", 4}, {"lumen_Standard", 4},
    };
    /** Filler added (in this order, cycling) if the line above falls short of SILENCE_MIN_DP. */
    static final String[] SILENCE_FILL = {"radiant_Assault", "nova_Attack", "brilliant_Standard"};

    // ------------------------------------------------------------------------------------------------- the duel

    /** Commander Isolde Raike: level 15, every combat skill elite plus Second Voice. Made once, kept by the intel. */
    public static PersonAPI raike() {
        PersonAPI p = Global.getSector().getImportantPeople().getPerson(RslIds.PERSON_RAIKE);
        if (p != null) return p;
        p = newRaike();
        p.getMemoryWithoutUpdate().set("$rsl_raike", true);
        Global.getSector().getImportantPeople().addPerson(p);
        return p;
    }

    /** A fresh Raike, not registered anywhere (also used by the rsl_duel mission, where there is no sector). */
    public static PersonAPI newRaike() {
        PersonAPI p = Global.getFactory().createPerson();
        p.setId(RslIds.PERSON_RAIKE);
        p.setFaction(Factions.TRITACHYON);
        p.setGender(FullName.Gender.FEMALE);
        p.setName(new FullName("Isolde", "Raike", FullName.Gender.FEMALE));
        p.setPortraitSprite("graphics/portraits/portrait_corporate10.png");
        p.setRankId(Ranks.SPACE_COMMANDER);
        p.setPostId(Ranks.POST_FLEET_COMMANDER);
        p.setPersonality(Personalities.AGGRESSIVE);
        for (String s : COMBAT_SKILLS) p.getStats().setSkillLevel(s, 2);
        p.getStats().setSkillLevel(RslIds.SKILL_SECOND_VOICE, 1);
        p.getStats().setLevel(RAIKE_LEVEL);
        return p;
    }

    /** The Dies Irae alone, waiting at {@code anchor} (the Antiphon Institute). Neutral until the duel is accepted. */
    public static CampaignFleetAPI diesIrae(SectorEntityToken anchor) {
        CampaignFleetAPI fleet = FleetFactoryV3.createEmptyFleet(Factions.TRITACHYON, FleetTypes.PATROL_SMALL, null);
        fleet.setName("Dies Irae");
        fleet.setNoFactionInName(true);
        FleetMemberAPI m = fleet.getFleetData().addFleetMember(RslIds.VARIANT_DIES_IRAE);
        outfitDiesIrae(m);
        m.setShipName("TTS Dies Irae");
        PersonAPI cmd = raike();
        fleet.setCommander(cmd);
        m.setCaptain(cmd);
        fleet.getFleetData().setFlagship(m);
        m.updateStats();
        m.getRepairTracker().setCR(m.getRepairTracker().getMaxCR());
        fleet.forceSync();

        MemoryAPI mem = fleet.getMemoryWithoutUpdate();
        mem.set(RslIds.MEM_ENCORE, "duel");
        mem.set(MemFlags.MEMORY_KEY_MAKE_NON_AGGRESSIVE, true);
        mem.set(MemFlags.MEMORY_KEY_NO_REP_IMPACT, true);
        mem.set(MemFlags.MEMORY_KEY_LOW_REP_IMPACT, true);
        mem.set(MemFlags.MEMORY_KEY_NO_SHIP_RECOVERY, true);
        mem.set(MemFlags.FLEET_IGNORES_OTHER_FLEETS, true);
        mem.set(MemFlags.FLEET_IGNORED_BY_OTHER_FLEETS, true);
        mem.set(MemFlags.MEMORY_KEY_NO_JUMP, true);
        fleet.setTransponderOn(true);
        Misc.makeImportant(fleet, "rsl_duel");
        anchor.getContainingLocation().addEntity(fleet);
        fleet.setLocation(anchor.getLocation().x + 300f, anchor.getLocation().y + 300f);
        fleet.addAssignment(FleetAssignment.ORBIT_PASSIVE, anchor, 1000000f, "waiting for the Lacrimosa");
        return fleet;
    }

    /** Own variant copy, limited tooltip, unboardable, the S-mods and the Hush core. */
    private static void outfitDiesIrae(FleetMemberAPI m) {
        m.setVariant(m.getVariant().clone(), false, false);
        ShipVariantAPI v = m.getVariant();
        v.setSource(VariantSource.REFIT);
        v.addTag(Tags.SHIP_LIMITED_TOOLTIP);
        v.addTag(Tags.VARIANT_UNBOARDABLE);
        for (int i = 0; i < DIES_IRAE_SMOD_IDS.length && i < DIES_IRAE_SMODS; i++) {
            String id = DIES_IRAE_SMOD_IDS[i];
            if (Global.getSettings().getHullModSpec(id) == null) continue;
            v.addMod(id);
            v.addPermaMod(id, true);
        }
        v.addPermaMod(RslIds.HULLMOD_DEAD_CHORUS, false);   // a Hush core: violet seams (no allies to mourn)
    }

    /** The rsl_duel mission's Dies Irae: same outfit, a fresh Raike. Lives in the jar because Janino (which
     *  compiles mission scripts) rejects {@code ShipVariantAPI.clone()} as throwing CloneNotSupportedException. */
    public static void missionDiesIrae(FleetMemberAPI m) {
        outfitDiesIrae(m);
        m.setCaptain(newRaike());
        m.updateStats();
        m.getRepairTracker().setCR(1f);
    }

    /** Back to full strength between attempts: full hull, armor and CR (Raike's crew works fast). */
    public static void restore(CampaignFleetAPI fleet) {
        if (fleet == null) return;
        for (FleetMemberAPI m : fleet.getFleetData().getMembersListCopy()) {
            m.getStatus().repairFully();
            m.updateStats();
            m.getRepairTracker().setCR(m.getRepairTracker().getMaxCR());
        }
    }

    // ------------------------------------------------------------------------------------------------- the Silence

    /** The Silence (see the class comment), holding station at {@code anchor}. */
    public static CampaignFleetAPI silence(SectorEntityToken anchor) {
        CampaignFleetAPI fleet = FleetFactoryV3.createEmptyFleet(Factions.REMNANTS, FleetTypes.PATROL_LARGE, null);
        fleet.setName("The Silence");
        fleet.setNoFactionInName(true);
        Random r = new Random();
        FleetMemberAPI flag = null;
        float dp = 0f;
        for (Object[] row : SILENCE) {
            for (int i = 0; i < (Integer) row[1]; i++) {
                FleetMemberAPI m = add(fleet, (String) row[0], r);
                if (m == null) continue;
                if (flag == null) flag = m;
                dp += m.getDeploymentPointsCost();
            }
        }
        for (int i = 0; dp < SILENCE_MIN_DP && i < 60; i++) {
            FleetMemberAPI m = add(fleet, SILENCE_FILL[i % SILENCE_FILL.length], r);
            if (m != null) dp += m.getDeploymentPointsCost();
        }
        if (flag != null) {
            flag.setShipName("Silentium");
            fleet.getFleetData().setFlagship(flag);
        }
        fleet.getFleetData().ensureHasFlagship();
        PersonAPI cmd = core(Commodities.OMEGA_CORE, r);
        if (cmd == null) cmd = core(Commodities.ALPHA_CORE, r);
        cmd.setRankId(Ranks.SPACE_ADMIRAL);
        cmd.setPostId(Ranks.POST_FLEET_COMMANDER);
        cmd.getStats().setSkillLevel(Skills.COORDINATED_MANEUVERS, 1);
        cmd.getStats().setSkillLevel(Skills.TACTICAL_DRILLS, 1);
        cmd.getStats().setSkillLevel(Skills.CREW_TRAINING, 1);
        cmd.getStats().setSkillLevel(Skills.FLUX_REGULATION, 1);
        cmd.getStats().setSkillLevel(Skills.ELECTRONIC_WARFARE, 1);
        cmd.getStats().setSkillLevel(Skills.CARRIER_GROUP, 1);
        cmd.getStats().setSkillLevel(Skills.OFFICER_TRAINING, 1);
        fleet.setCommander(cmd);
        fleet.getFlagship().setCaptain(cmd);
        for (FleetMemberAPI m : fleet.getFleetData().getMembersListCopy()) {
            if (m != fleet.getFlagship()) m.setCaptain(core(Commodities.ALPHA_CORE, r));
            m.updateStats();
            m.getRepairTracker().setCR(m.getRepairTracker().getMaxCR());
        }
        fleet.getFleetData().sort();
        fleet.forceSync();

        MemoryAPI mem = fleet.getMemoryWithoutUpdate();
        mem.set(RslIds.MEM_ENCORE, "requiem");
        mem.set(MemFlags.MEMORY_KEY_MAKE_NON_AGGRESSIVE, true);
        mem.set(MemFlags.MEMORY_KEY_NO_REP_IMPACT, true);
        mem.set(MemFlags.MEMORY_KEY_NO_SHIP_RECOVERY, true);
        mem.set(MemFlags.FLEET_IGNORES_OTHER_FLEETS, true);
        mem.set(MemFlags.FLEET_IGNORED_BY_OTHER_FLEETS, true);
        mem.set(MemFlags.MEMORY_KEY_NO_JUMP, true);
        fleet.addTag(Tags.NEUTRINO_HIGH);
        fleet.setTransponderOn(true);
        Misc.makeImportant(fleet, "rsl_requiem");
        anchor.getContainingLocation().addEntity(fleet);
        fleet.setLocation(anchor.getLocation().x + 400f, anchor.getLocation().y);
        fleet.addAssignment(FleetAssignment.ORBIT_PASSIVE, anchor, 1000000f, "listening");
        return fleet;
    }

    /** Total deployment points of a fleet (for the dialog's warning). */
    public static int dp(CampaignFleetAPI fleet) {
        float dp = 0f;
        if (fleet != null) for (FleetMemberAPI m : fleet.getFleetData().getMembersListCopy()) dp += m.getDeploymentPointsCost();
        return Math.round(dp);
    }

    private static FleetMemberAPI add(CampaignFleetAPI fleet, String variantId, Random r) {
        if (Global.getSettings().getVariant(variantId) == null) return null;
        FleetMemberAPI m = fleet.getFleetData().addFleetMember(variantId);
        if (m == null) return null;
        m.setVariant(m.getVariant().clone(), false, false);
        ShipVariantAPI v = m.getVariant();
        v.setSource(VariantSource.REFIT);
        v.addTag(Tags.SHIP_LIMITED_TOOLTIP);
        LacrimosaFleets.sMods(v, SILENCE_SMODS, r);
        return m;
    }

    private static PersonAPI core(String coreId, Random r) {
        try {
            return Misc.getAICoreOfficerPlugin(coreId).createPerson(coreId, Factions.REMNANTS, r);
        } catch (Throwable t) {
            return null;
        }
    }
}
