package rsl.campaign;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.campaign.CampaignFleetAPI;
import com.fs.starfarer.api.campaign.FactionAPI;
import com.fs.starfarer.api.campaign.FleetAssignment;
import com.fs.starfarer.api.campaign.LocationAPI;
import com.fs.starfarer.api.campaign.SectorEntityToken;
import com.fs.starfarer.api.campaign.rules.MemoryAPI;
import com.fs.starfarer.api.characters.PersonAPI;
import com.fs.starfarer.api.combat.ShipVariantAPI;
import com.fs.starfarer.api.fleet.FleetMemberAPI;
import com.fs.starfarer.api.impl.campaign.FleetInteractionDialogPluginImpl.FIDConfig;
import com.fs.starfarer.api.impl.campaign.FleetInteractionDialogPluginImpl.FIDConfigGen;
import com.fs.starfarer.api.impl.campaign.events.OfficerManagerEvent;
import com.fs.starfarer.api.impl.campaign.events.OfficerManagerEvent.SkillPickPreference;
import com.fs.starfarer.api.impl.campaign.fleets.FleetFactoryV3;
import com.fs.starfarer.api.impl.campaign.fleets.FleetParamsV3;
import com.fs.starfarer.api.impl.campaign.ids.Factions;
import com.fs.starfarer.api.impl.campaign.ids.FleetTypes;
import com.fs.starfarer.api.impl.campaign.ids.MemFlags;
import com.fs.starfarer.api.impl.campaign.ids.Personalities;
import com.fs.starfarer.api.impl.campaign.ids.Ranks;
import com.fs.starfarer.api.impl.campaign.ids.Skills;
import com.fs.starfarer.api.impl.campaign.ids.Tags;
import com.fs.starfarer.api.loading.HullModSpecAPI;
import com.fs.starfarer.api.loading.VariantSource;
import com.fs.starfarer.api.util.Misc;
import com.fs.starfarer.api.util.WeightedRandomPicker;
import rsl.RslIds;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * The questline's fleets (CAMPAIGN.md section 6, boss specs): fixed strength, never scaled to the player.
 * Bosses: pristine hulls (stock variants, no D-mods), 3 S-mods per ship, level-7 officers with every skill elite and a
 * commander with fleet skills, no ship recovery, no reputation impact, nearby fleets and stations kept out.
 */
public final class LacrimosaFleets {
    private LacrimosaFleets() {
    }

    /** Hullmods that suit any hull, used when a variant has too few of its own to build in. */
    private static final String HULLMOD_REINFORCED = "reinforcedhull";
    private static final String HULLMOD_HEAVY_ARMOR = "heavyarmor";
    private static final String HULLMOD_FLUX_DIST = "fluxdistributor";
    private static final String HULLMOD_FLUX_COIL = "fluxcoil";
    private static final String HULLMOD_ARMORED_MOUNTS = "armoredweapons";
    private static final String HULLMOD_HARDENED = "hardened_subsystems";
    private static final String[] FALLBACK_SMODS = {HULLMOD_FLUX_DIST, HULLMOD_REINFORCED, HULLMOD_HARDENED,
            HULLMOD_ARMORED_MOUNTS, HULLMOD_FLUX_COIL, HULLMOD_HEAVY_ARMOR};

    public static final int BOSS_OFFICER_LEVEL = 7;
    public static final int ESCORT_OFFICER_LEVEL = 5;

    /** Fleet memory: which quest fleet this is (rsl.campaign.LacrimosaIntel matches on it). */
    public static final String MEM_ROLE = "$rsl_qRole";

    // ------------------------------------------------------------------------------------------------- beat 1

    /** Pirate scavengers stripping the last listening buoy (medium fight, ~70 FP). */
    public static CampaignFleetAPI scavengers(SectorEntityToken buoy) {
        FleetParamsV3 p = new FleetParamsV3(null, buoy.getLocationInHyperspace(), Factions.PIRATES, 1f,
                FleetTypes.SCAVENGER_MEDIUM, 70f, 0f, 0f, 0f, 0f, 0f, 0f);
        p.random = new Random();
        CampaignFleetAPI fleet = FleetFactoryV3.createFleet(p);
        if (fleet == null || fleet.isEmpty()) return null;
        fleet.setName("Buoy Scavengers");
        fleet.setNoFactionInName(true);
        hostile(fleet, "scavengers");
        place(fleet, buoy, 250f);
        fleet.addAssignment(FleetAssignment.ORBIT_AGGRESSIVE, buoy, 100000f, "stripping the listening buoy");
        return fleet;
    }

    // ------------------------------------------------------------------------------------------------- beat 2

    /** Domain-era derelict defences around the Antiphon Institute: ~180 DP, 1 S-mod each, no officers. */
    public static CampaignFleetAPI derelictGuard(SectorEntityToken institute) {
        CampaignFleetAPI fleet = FleetFactoryV3.createEmptyFleet(Factions.DERELICT, FleetTypes.PATROL_LARGE, null);
        fleet.setName("Institute Defences");
        fleet.setNoFactionInName(true);
        Random r = new Random();
        add(fleet, "guardian_Standard", 1, 1, r);
        add(fleet, "rampart_Standard", 4, 1, r);
        add(fleet, "bastillon_Standard", 6, 1, r);
        add(fleet, "berserker_Assault", 4, 1, r);
        add(fleet, "warden_Defense", 4, 1, r);
        add(fleet, "defender_PD", 3, 1, r);
        finish(fleet, null);
        hostile(fleet, "guard");
        place(fleet, institute, 200f);
        fleet.addAssignment(FleetAssignment.ORBIT_AGGRESSIVE, institute, 100000f, "guarding the Antiphon Institute");
        return fleet;
    }

    // ------------------------------------------------------------------------------------------------- beat 3

    /** Director Sung's Special Projects group (~280 DP, phase-heavy), sent after the player who refused him. */
    public static CampaignFleetAPI specialProjects(LocationAPI where, float x, float y) {
        CampaignFleetAPI fleet = FleetFactoryV3.createEmptyFleet(Factions.TRITACHYON, FleetTypes.TASK_FORCE, null);
        fleet.setName("Special Projects");
        fleet.setNoFactionInName(true);
        Random r = new Random();
        FactionAPI tt = Global.getSector().getFaction(Factions.TRITACHYON);
        FleetMemberAPI flag = add(fleet, "paragon_Elite", 1, 3, r).get(0);
        flag.setShipName("TTS Contrapuntal");
        officers(add(fleet, "doom_Strike", 2, 3, r), tt, fleet, r);
        officers(add(fleet, "harbinger_Strike", 2, 3, r), tt, fleet, r);
        officers(add(fleet, "aurora_Assault", 1, 3, r), tt, fleet, r);
        officers(add(fleet, "medusa_Attack", 2, 3, r), tt, fleet, r);
        add(fleet, "afflictor_Strike", 2, 3, r);
        add(fleet, "shade_Assault", 2, 3, r);
        add(fleet, "tempest_Attack", 2, 3, r);
        PersonAPI cmd = officer(tt, fleet, r);
        cmd.setPersonality(Personalities.AGGRESSIVE);
        cmd.setRankId(Ranks.SPACE_COMMANDER);
        cmd.setPostId(Ranks.POST_FLEET_COMMANDER);
        commanderSkills(cmd);
        finish(fleet, flag, cmd);
        hostile(fleet, "hunter");
        MemoryAPI mem = fleet.getMemoryWithoutUpdate();
        mem.set(MemFlags.MEMORY_KEY_MAKE_AGGRESSIVE, true);
        mem.set(MemFlags.MEMORY_KEY_MAKE_ALWAYS_PURSUE, true);
        mem.set(MemFlags.MEMORY_KEY_PURSUE_PLAYER, true);
        fleet.setTransponderOn(false);
        where.addEntity(fleet);
        fleet.setLocation(x, y);
        fleet.addAssignment(FleetAssignment.INTERCEPT, Global.getSector().getPlayerFleet(), 1000f,
                "hunting the Lacrimosa");
        return fleet;
    }

    // ------------------------------------------------------------------------------------------------- beat 5

    /**
     * The Hush: the First Chorus, dead and still ringing (~320 DP of Lattice hulls with the Dead Chorus fleet hullmod).
     * Its own faction would be the Cantorate; it flies as derelict so it is hostile to everyone, the Cantorate too.
     */
    public static CampaignFleetAPI hush(SectorEntityToken graveyard) {
        CampaignFleetAPI fleet = FleetFactoryV3.createEmptyFleet(Factions.DERELICT, FleetTypes.PATROL_LARGE, null);
        fleet.setName("The Hush");
        fleet.setNoFactionInName(true);
        Random r = new Random();
        FactionAPI choir = Global.getSector().getFaction(RslIds.FACTION_CHOIR);
        FleetMemberAPI flag = add(fleet, "rsl_conductor_Maestro", 1, 3, r).get(0);
        flag.setShipName("Kyrie");
        List<FleetMemberAPI> big = new ArrayList<FleetMemberAPI>();
        big.addAll(add(fleet, "rsl_conductor_Fortissimo", 1, 3, r));
        big.addAll(add(fleet, "rsl_halo_Nocturne", 1, 3, r));
        big.addAll(add(fleet, "rsl_cadence_Battery", 2, 3, r));
        big.addAll(add(fleet, "rsl_cadence_Drumline", 1, 3, r));
        big.addAll(add(fleet, "rsl_tremolo_Waveform", 2, 3, r));
        big.addAll(add(fleet, "rsl_tremolo_Riptide", 1, 3, r));
        add(fleet, "rsl_staccato_Burst", 2, 3, r);
        add(fleet, "rsl_staccato_Lancer", 1, 3, r);
        add(fleet, "rsl_refrain_Bulwark", 2, 3, r);
        add(fleet, "rsl_gracenote_Pluck", 2, 3, r);
        officers(big, choir, fleet, r);
        String[] names = {"Gloria", "Sanctus", "Benedictus", "Agnus Dei", "Dies Irae", "Tuba Mirum", "Rex Tremendae",
                "Recordare", "Confutatis", "Offertorium", "Hostias", "Communio", "Libera Me", "In Paradisum",
                "Pie Jesu"};
        int i = 0;
        for (FleetMemberAPI m : fleet.getFleetData().getMembersListCopy()) {
            m.getVariant().addPermaMod(RslIds.HULLMOD_DEAD_CHORUS, false);
            if (m != flag) m.setShipName(names[i++ % names.length]);
        }
        PersonAPI cmd = officer(choir, fleet, r);
        cmd.setPersonality(Personalities.RECKLESS);
        cmd.setRankId(Ranks.SPACE_ADMIRAL);
        cmd.setPostId(Ranks.POST_FLEET_COMMANDER);
        cmd.getName().setFirst("Maestro");
        cmd.getName().setLast("of the First Chorus");
        commanderSkills(cmd);
        finish(fleet, flag, cmd);
        hostile(fleet, "hush");
        fleet.getMemoryWithoutUpdate().set(RslIds.MEM_HUSH_FLEET, true);
        place(fleet, graveyard, 150f);
        fleet.addAssignment(FleetAssignment.ORBIT_AGGRESSIVE, graveyard, 100000f, "keeping the silence");
        return fleet;
    }

    /** Chorus path: two Cantorate escorts with S-mods and level-5 officers join the player's fleet for beat 5. */
    public static List<FleetMemberAPI> councilEscorts() {
        List<FleetMemberAPI> out = new ArrayList<FleetMemberAPI>();
        CampaignFleetAPI player = Global.getSector().getPlayerFleet();
        if (player == null) return out;
        FactionAPI choir = Global.getSector().getFaction(RslIds.FACTION_CHOIR);
        Random r = new Random();
        String[][] ships = {{"rsl_cadence_Battery", "Tenebrae"}, {"rsl_refrain_Bulwark", "Kept Pitch"}};
        for (String[] s : ships) {
            FleetMemberAPI m = Global.getFactory().createFleetMember(
                    com.fs.starfarer.api.fleet.FleetMemberType.SHIP, s[0]);
            m.setVariant(m.getVariant().clone(), false, false);
            ShipVariantAPI v = m.getVariant();
            v.setSource(VariantSource.REFIT);
            sMods(v, 2, r);
            v.addTag(RslIds.TAG_ESCORT);
            v.addTag(Tags.SHIP_CAN_NOT_SCUTTLE);
            m.setShipName(choir.getShipNamePrefix() + " " + s[1]);
            PersonAPI o = OfficerManagerEvent.createOfficer(choir, ESCORT_OFFICER_LEVEL, SkillPickPreference.ANY,
                    false, null, true, true, 2, r);
            o.getMemoryWithoutUpdate().set("$rsl_escort", true);
            player.getFleetData().addFleetMember(m);
            player.getFleetData().addOfficer(o);
            m.setCaptain(o);
            m.updateStats();
            m.getRepairTracker().setCR(m.getRepairTracker().getMaxCR());
            out.add(m);
        }
        return out;
    }

    /** Sends the Council's escorts home; returns how many ships left. */
    public static int dismissEscorts() {
        CampaignFleetAPI player = Global.getSector().getPlayerFleet();
        if (player == null) return 0;
        int n = 0;
        for (FleetMemberAPI m : player.getFleetData().getMembersListCopy()) {
            if (m.getVariant() == null || !m.getVariant().hasTag(RslIds.TAG_ESCORT)) continue;
            PersonAPI c = m.getCaptain();
            player.getFleetData().removeFleetMember(m);
            if (c != null && !c.isDefault() && c.getMemoryWithoutUpdate().getBoolean("$rsl_escort")) {
                player.getFleetData().removeOfficer(c);
            }
            n++;
        }
        for (com.fs.starfarer.api.characters.OfficerDataAPI od : player.getFleetData().getOfficersCopy()) {
            if (od.getPerson().getMemoryWithoutUpdate().getBoolean("$rsl_escort")) {
                FleetMemberAPI m = player.getFleetData().getMemberWithCaptain(od.getPerson());
                if (m != null) m.setCaptain(null);
                player.getFleetData().removeOfficer(od.getPerson());
            }
        }
        return n;
    }

    // ------------------------------------------------------------------------------------------------- helpers

    /** Adds {@code count} ships of a variant, each a saved clone with {@code smods} S-mods and full CR. */
    private static List<FleetMemberAPI> add(CampaignFleetAPI fleet, String variantId, int count, int smods, Random r) {
        List<FleetMemberAPI> out = new ArrayList<FleetMemberAPI>();
        for (int i = 0; i < count; i++) {
            FleetMemberAPI m = fleet.getFleetData().addFleetMember(variantId);
            if (m == null) continue;
            m.setVariant(m.getVariant().clone(), false, false);   // "perm" the variant: saved, not re-read by id
            ShipVariantAPI v = m.getVariant();
            v.setSource(VariantSource.REFIT);
            v.addTag(Tags.SHIP_LIMITED_TOOLTIP);
            sMods(v, smods, r);
            out.add(m);
        }
        return out;
    }

    /** Builds in {@code n} hullmods: the variant's own first (as vanilla ShipRecoverySpecial), then safe generics. */
    static void sMods(ShipVariantAPI v, int n, Random r) {
        WeightedRandomPicker<String> picker = new WeightedRandomPicker<String>(r);
        for (String id : v.getNonBuiltInHullmods()) {
            HullModSpecAPI spec = Global.getSettings().getHullModSpec(id);
            if (spec == null || spec.isHidden() || spec.isHiddenEverywhere() || spec.hasTag(Tags.HULLMOD_DMOD)
                    || spec.hasTag(Tags.HULLMOD_NO_BUILD_IN) || v.getPermaMods().contains(id)) {
                continue;
            }
            picker.add(id, 1f + spec.getCapitalCost());
        }
        int done = 0;
        while (done < n && !picker.isEmpty()) {
            v.addPermaMod(picker.pickAndRemove(), true);
            done++;
        }
        for (int i = 0; done < n && i < FALLBACK_SMODS.length; i++) {
            String id = FALLBACK_SMODS[i];
            if (v.hasHullMod(id) || Global.getSettings().getHullModSpec(id) == null) continue;
            v.addMod(id);
            v.addPermaMod(id, true);
            done++;
        }
    }

    private static PersonAPI officer(FactionAPI faction, CampaignFleetAPI fleet, Random r) {
        // allowAnyLevel = true: past the normal officer cap; elite override 7 = every skill elite
        return OfficerManagerEvent.createOfficer(faction, BOSS_OFFICER_LEVEL, SkillPickPreference.ANY, false, fleet,
                true, true, BOSS_OFFICER_LEVEL, r);
    }

    private static void officers(List<FleetMemberAPI> members, FactionAPI faction, CampaignFleetAPI fleet, Random r) {
        for (FleetMemberAPI m : members) m.setCaptain(officer(faction, fleet, r));
    }

    /** The boss commander's fleet-wide skills (the strongest set vanilla gives an AI commander). */
    private static void commanderSkills(PersonAPI p) {
        p.getStats().setSkillLevel(Skills.COORDINATED_MANEUVERS, 1);
        p.getStats().setSkillLevel(Skills.TACTICAL_DRILLS, 1);
        p.getStats().setSkillLevel(Skills.CREW_TRAINING, 1);
        p.getStats().setSkillLevel(Skills.FLUX_REGULATION, 1);
        p.getStats().setSkillLevel(Skills.ELECTRONIC_WARFARE, 1);
        p.getStats().setSkillLevel(Skills.CARRIER_GROUP, 1);
        p.getStats().setSkillLevel(Skills.OFFICER_TRAINING, 1);
        p.getStats().setSkillLevel(Skills.PHASE_CORPS, 1);
    }

    private static void finish(CampaignFleetAPI fleet, FleetMemberAPI flag) {
        finish(fleet, flag, null);
    }

    private static void finish(CampaignFleetAPI fleet, FleetMemberAPI flag, PersonAPI commander) {
        if (flag != null) fleet.getFleetData().setFlagship(flag);
        fleet.getFleetData().ensureHasFlagship();
        if (commander != null) {
            fleet.setCommander(commander);
            fleet.getFlagship().setCaptain(commander);
        }
        fleet.getFleetData().sort();
        for (FleetMemberAPI m : fleet.getFleetData().getMembersListCopy()) {
            m.updateStats();
            m.getRepairTracker().setCR(m.getRepairTracker().getMaxCR());
        }
        fleet.forceSync();
    }

    /** As vanilla's Ziggurat (TTBlackSite.addFleet): hostile, no reputation impact, no recovery, set-piece config. */
    private static void hostile(CampaignFleetAPI fleet, String role) {
        MemoryAPI mem = fleet.getMemoryWithoutUpdate();
        mem.set(MEM_ROLE, role);
        mem.set(MemFlags.MEMORY_KEY_MAKE_HOSTILE, true);
        mem.set(MemFlags.MEMORY_KEY_NO_REP_IMPACT, true);
        mem.set(MemFlags.MEMORY_KEY_LOW_REP_IMPACT, true);
        if (!"scavengers".equals(role)) {
            mem.set(MemFlags.MEMORY_KEY_NO_SHIP_RECOVERY, true);
            mem.set(MemFlags.FLEET_INTERACTION_DIALOG_CONFIG_OVERRIDE_GEN, new BossConfigGen());
        }
        Misc.makeImportant(fleet, "rsl_lacrimosa");
    }

    private static void place(CampaignFleetAPI fleet, SectorEntityToken near, float spread) {
        near.getContainingLocation().addEntity(fleet);
        fleet.setLocation(near.getLocation().x + spread * ((float) Math.random() - 0.5f),
                near.getLocation().y + spread * ((float) Math.random() - 0.5f));
    }

    /** Despawn a quest fleet, quietly if the player cannot see it, else by flying off. */
    public static void retire(CampaignFleetAPI fleet) {
        if (fleet == null || !fleet.isAlive()) return;
        Misc.makeUnimportant(fleet, "rsl_lacrimosa");
        CampaignFleetAPI player = Global.getSector().getPlayerFleet();
        if (player == null || player.getContainingLocation() != fleet.getContainingLocation()
                || !fleet.isVisibleToPlayerFleet()) {
            fleet.despawn();
            return;
        }
        fleet.getMemoryWithoutUpdate().unset(MemFlags.MEMORY_KEY_MAKE_HOSTILE);
        fleet.getMemoryWithoutUpdate().unset(MemFlags.MEMORY_KEY_MAKE_AGGRESSIVE);
        fleet.getMemoryWithoutUpdate().unset(MemFlags.MEMORY_KEY_MAKE_ALWAYS_PURSUE);
        fleet.getMemoryWithoutUpdate().unset(MemFlags.MEMORY_KEY_PURSUE_PLAYER);
        fleet.clearAssignments();
        SectorEntityToken away = fleet.getContainingLocation().createToken(
                fleet.getLocation().x + 8000f * (float) Math.cos(Math.random() * 6.283),
                fleet.getLocation().y + 8000f * (float) Math.sin(Math.random() * 6.283));
        fleet.addAssignment(FleetAssignment.GO_TO_LOCATION_AND_DESPAWN, away, 60f, "withdrawing");
    }

    /**
     * Set-piece battles: no nearby stations or other fleets join the boss's side (allies of the player still may),
     * and the player may always withdraw (the Hush waits; Special Projects keeps hunting). Saved in fleet memory, so
     * it is aliased in RslModPlugin.
     */
    public static class BossConfigGen implements FIDConfigGen {
        @Override
        public FIDConfig createConfig() {
            FIDConfig c = new FIDConfig();
            c.pullInStations = false;
            c.pullInEnemies = false;
            c.pullInAllies = true;
            c.leaveAlwaysAvailable = true;
            c.showTransponderStatus = false;
            return c;
        }
    }
}
