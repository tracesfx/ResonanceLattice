package rsl.world;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.campaign.CampaignFleetAPI;
import com.fs.starfarer.api.campaign.PlanetAPI;
import com.fs.starfarer.api.campaign.SectorAPI;
import com.fs.starfarer.api.campaign.SectorEntityToken;
import com.fs.starfarer.api.campaign.StarSystemAPI;
import com.fs.starfarer.api.impl.campaign.DerelictShipEntityPlugin.DerelictShipData;
import com.fs.starfarer.api.impl.campaign.ids.Entities;
import com.fs.starfarer.api.impl.campaign.ids.Factions;
import com.fs.starfarer.api.impl.campaign.ids.StarTypes;
import com.fs.starfarer.api.impl.campaign.procgen.themes.BaseThemeGenerator;
import com.fs.starfarer.api.impl.campaign.procgen.themes.SalvageSpecialAssigner.ShipRecoverySpecialCreator;
import com.fs.starfarer.api.impl.campaign.rulecmd.salvage.special.ShipRecoverySpecial.PerShipData;
import com.fs.starfarer.api.impl.campaign.rulecmd.salvage.special.ShipRecoverySpecial.ShipCondition;
import com.fs.starfarer.api.util.Misc;
import org.apache.log4j.Logger;
import org.lwjgl.util.vector.Vector2f;
import rsl.RslIds;
import rsl.campaign.ArrayListener;
import rsl.campaign.LacrimosaFleets;
import rsl.campaign.LacrimosaIntel;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * Secrets and exploration (CAMPAIGN.md section 7), placed once per save in procgen systems nobody lives in:
 * <ul>
 * <li>8 Lost Score caches (#1): Institute data caches, discoverable like vanilla probes; read in rsl.rulecmd.RslSecrets;</li>
 * <li>4 silent wrecks (#2): recoverable Lattice frigates/destroyers with Pitch Glass in their salvage (vanilla
 * TTBlackSite.addDerelict pattern);</li>
 * <li>the abandoned Array (#3): an automated Cantor Array in the most remote system ({@link ArrayListener} pays).</li>
 * </ul>
 * Venn's Rest (#5) is created later by {@link #createVennsRest}, when the eighth Score is read.
 *
 * Runs from onNewGameAfterProcGen and, behind {@link RslIds#MEM_SECRETS_GENERATED}, once from onGameLoad (so saves that
 * predate Stage 6 get the secrets). Also runs in Nexerelin random sectors (CAMPAIGN.md section 11).
 */
public final class SecretsGen {
    private static final Logger log = Global.getLogger(SecretsGen.class);

    public static final int SCORES = 8;
    public static final int WRECKS = 4;
    /** Pitch Glass in a silent wreck's salvage, as drop value (credits; Pitch Glass is worth 5 each to the game). */
    public static final int WRECK_GLASS_VALUE = 60;
    private static final String[] WRECK_VARIANTS = {"rsl_gracenote_Standard", "rsl_gracenote_Pluck",
            "rsl_gracenote_Warden", "rsl_refrain_Standard", "rsl_refrain_Chorister", "rsl_staccato_Burst"};

    private SecretsGen() {
    }

    public static void generate(SectorAPI sector) {
        if (sector == null || sector.getMemoryWithoutUpdate().getBoolean(RslIds.MEM_SECRETS_GENERATED)) return;
        sector.getMemoryWithoutUpdate().set(RslIds.MEM_SECRETS_GENERATED, true);
        try {
            List<StarSystemAPI> pool = new ArrayList<StarSystemAPI>();
            for (StarSystemAPI s : sector.getStarSystems()) {
                if (LacrimosaIntel.isWildSystem(s) && !s.getPlanets().isEmpty()) pool.add(s);
            }
            if (pool.isEmpty()) {
                log.warn("Resonance Lattice: no wild systems for the secrets");
                return;
            }
            // the Array goes to the most remote system; the rest are shuffled
            Collections.sort(pool, (a, b) -> Float.compare(b.getLocation().length(), a.getLocation().length()));
            StarSystemAPI arraySystem = pool.remove(0);
            placeArray(arraySystem);
            Collections.shuffle(pool);
            int k = 0;
            for (int i = 0; i < SCORES; i++) placeCache(pool.get(k++ % pool.size()), i);
            for (int i = 0; i < WRECKS; i++) placeWreck(pool.get(k++ % pool.size()), i);
            log.info("Resonance Lattice: secrets placed (" + pool.size() + " wild systems; Array in "
                    + arraySystem.getBaseName() + ")");
        } catch (Throwable t) {
            log.error("Resonance Lattice: placing the secrets failed", t);
        }
    }

    /** A random planet of the system to orbit (never the star: its corona hurts fleets). */
    private static SectorEntityToken anchor(StarSystemAPI s) {
        List<PlanetAPI> planets = new ArrayList<PlanetAPI>();
        for (PlanetAPI p : s.getPlanets()) if (!p.isStar()) planets.add(p);
        if (planets.isEmpty()) return s.getStar() != null ? s.getStar() : s.getCenter();
        return planets.get((int) (Math.random() * planets.size()));
    }

    private static float orbitRadius(SectorEntityToken anchor, float extra) {
        boolean star = anchor instanceof PlanetAPI && ((PlanetAPI) anchor).isStar();
        return anchor.getRadius() + (star ? 1800f : 0f) + extra;
    }

    private static void placeCache(StarSystemAPI s, int i) {
        SectorEntityToken a = anchor(s);
        SectorEntityToken e = s.addCustomEntity("rsl_lostscore_" + i, null, RslIds.ENTITY_SCORE_CACHE,
                Factions.NEUTRAL);
        float r = orbitRadius(a, 250f + (float) Math.random() * 300f);
        e.setCircularOrbitPointingDown(a, (float) (Math.random() * 360f), r, r / 12f);
        e.setDiscoverable(true);
        e.setSensorProfile(1f);
    }

    private static void placeWreck(StarSystemAPI s, int i) {
        SectorEntityToken a = anchor(s);
        String variant = WRECK_VARIANTS[(int) (Math.random() * WRECK_VARIANTS.length)];
        ShipCondition cond = Math.random() < 0.5 ? ShipCondition.BATTERED : ShipCondition.WRECKED;
        DerelictShipData params = new DerelictShipData(new PerShipData(variant, cond, 0f), false);
        SectorEntityToken ship = BaseThemeGenerator.addSalvageEntity(s, Entities.WRECK, Factions.NEUTRAL, params);
        ship.setDiscoverable(true);
        float r = orbitRadius(a, 300f + (float) Math.random() * 400f);
        ship.setCircularOrbit(a, (float) (Math.random() * 360f), r, r / (10f + (float) Math.random() * 5f));
        ShipRecoverySpecialCreator creator = new ShipRecoverySpecialCreator(null, 0, 0, false, null, null);
        Misc.setSalvageSpecial(ship, creator.createSpecial(ship, null));
        ship.addDropValue("rsl_pitchglass_drop", WRECK_GLASS_VALUE);
    }

    private static void placeArray(StarSystemAPI s) {
        SectorEntityToken a = null;
        for (PlanetAPI p : s.getPlanets()) {
            if (p.isStar()) continue;
            if (a == null || p.getCircularOrbitRadius() > a.getCircularOrbitRadius()) a = p;
        }
        if (a == null) a = s.getStar();
        CampaignFleetAPI fleet = LacrimosaFleets.abandonedArray(a, orbitRadius(a, 700f));
        fleet.addEventListener(new ArrayListener());
    }

    /**
     * Console testing: {@code runcode rsl.world.SecretsGen.debug()} lists where the caches, wrecks and the Array were
     * placed (campaign messages) and marks them on the map. Never called by the mod itself.
     */
    public static void debug() {
        for (StarSystemAPI s : Global.getSector().getStarSystems()) {
            for (SectorEntityToken e : s.getAllEntities()) {
                String what = null;
                if (RslIds.ENTITY_SCORE_CACHE.equals(e.getCustomEntityType())) {
                    what = e.getMemoryWithoutUpdate().getBoolean("$rsl_scoreRead") ? null : "Lost Score cache";
                } else if (e instanceof CampaignFleetAPI
                        && "array".equals(e.getMemoryWithoutUpdate().getString(LacrimosaFleets.MEM_ROLE))) {
                    what = "abandoned Array";
                } else if (Entities.WRECK.equals(e.getCustomEntityType()) && e.getDropValue() != null) {
                    for (com.fs.starfarer.api.impl.campaign.procgen.SalvageEntityGenDataSpec.DropData d : e.getDropValue()) {
                        if ("rsl_pitchglass_drop".equals(d.group)) what = "silent wreck";
                    }
                }
                if (what == null) continue;
                Misc.makeImportant(e, "rsl_debug");
                Global.getSector().getCampaignUI().addMessage(what + ": " + s.getNameWithLowercaseType());
            }
        }
    }

    // ------------------------------------------------------------------------------------------------- Venn's Rest

    public static final String VENNS_REST = "Venn's Rest";

    /** Secret #5: a small hidden system on the fringe with the cryo station and its sealed Hush. Idempotent. */
    public static SectorEntityToken createVennsRest(SectorAPI sector) {
        StarSystemAPI existing = sector.getStarSystem(VENNS_REST);
        if (existing != null) return existing.getEntityById(RslIds.ENTITY_VENNS_REST);
        StarSystemAPI system = sector.createStarSystem(VENNS_REST);
        float w = Global.getSettings().getFloat("sectorWidth"), h = Global.getSettings().getFloat("sectorHeight");
        // the upper-right fringe, far from the abyss in the lower left
        Vector2f preferred = new Vector2f(w * 0.36f, h * 0.30f);
        Vector2f loc = VellGen.findFreeHyperspaceLocation(sector, preferred);
        system.getLocation().set(loc.x, loc.y);
        system.setBackgroundTextureFilename("graphics/backgrounds/background2.jpg");
        PlanetAPI star = system.initStar("rsl_venn_star", StarTypes.RED_DWARF, 350f, 300f);
        system.setLightColor(new java.awt.Color(255, 200, 190));
        PlanetAPI rock = system.addPlanet("rsl_venn_rock", star, "Lacuna", "barren", 40f, 110f, 2600f, 120f);
        rock.setCustomDescriptionId("rsl_desc_venn_rock");
        SectorEntityToken st = system.addCustomEntity(RslIds.ENTITY_VENNS_REST, "Venn's Rest",
                RslIds.ENTITY_VENNS_REST, Factions.NEUTRAL);
        st.setCircularOrbitPointingDown(rock, 90f, rock.getRadius() + 350f, 40f);
        st.setDiscoverable(false);
        system.autogenerateHyperspaceJumpPoints(true, true);
        VellGen.clearHyperspaceAround(system);
        LacrimosaFleets.hushRemnant(st);
        return st;
    }
}
