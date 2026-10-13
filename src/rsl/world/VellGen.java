package rsl.world;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.campaign.FactionAPI;
import com.fs.starfarer.api.campaign.PersonImportance;
import com.fs.starfarer.api.campaign.PlanetAPI;
import com.fs.starfarer.api.campaign.SectorAPI;
import com.fs.starfarer.api.campaign.SectorEntityToken;
import com.fs.starfarer.api.campaign.StarSystemAPI;
import com.fs.starfarer.api.campaign.econ.MarketAPI;
import com.fs.starfarer.api.characters.FullName;
import com.fs.starfarer.api.characters.PersonAPI;
import com.fs.starfarer.api.impl.campaign.ids.Conditions;
import com.fs.starfarer.api.impl.campaign.ids.Entities;
import com.fs.starfarer.api.impl.campaign.ids.Industries;
import com.fs.starfarer.api.impl.campaign.ids.Ranks;
import com.fs.starfarer.api.impl.campaign.ids.StarTypes;
import com.fs.starfarer.api.impl.campaign.ids.Submarkets;
import com.fs.starfarer.api.impl.campaign.ids.Tags;
import com.fs.starfarer.api.impl.campaign.ids.Terrain;
import com.fs.starfarer.api.impl.campaign.procgen.NebulaEditor;
import com.fs.starfarer.api.impl.campaign.procgen.StarGenDataSpec;
import com.fs.starfarer.api.impl.campaign.terrain.HyperspaceTerrainPlugin;
import com.fs.starfarer.api.impl.campaign.terrain.StarCoronaTerrainPlugin;
import com.fs.starfarer.api.util.Misc;
import org.apache.log4j.Logger;
import org.lwjgl.util.vector.Vector2f;
import rsl.RslIds;

import java.awt.Color;

/**
 * Vell, the Cantorate's pulsar (CAMPAIGN.md section 4): the neutron star with its pulsar beam, Tacet Station near it,
 * the irradiated rock Tenuto, the ice giant Basso with its moons Coda (capital, guarded by the Cantor Array) and
 * Glasshouse (crystal nurseries), an outer belt and the usual relay/buoy/array.
 *
 * Idempotent: called from onNewGame and (behind {@link RslIds#MEM_VELL_GENERATED}) from onGameLoad, so a save that
 * predates the mod gets Vell once. Skipped in a Nexerelin random sector, where Nex places the Cantorate's markets.
 */
public final class VellGen {
    private static final Logger log = Global.getLogger(VellGen.class);

    public static final String SYSTEM_NAME = "Vell";
    /** South-east fringe, past Naraka and Samarra (vanilla core spans x -19100..11000, y -14500..3200). */
    private static final Vector2f PREFERRED_LOCATION = new Vector2f(14500f, -13000f);
    private static final float MIN_SYSTEM_SEPARATION = 2600f;

    private VellGen() {
    }

    public static boolean shouldGenerate(SectorAPI sector) {
        if (sector == null) return false;
        if (sector.getMemoryWithoutUpdate().getBoolean(RslIds.MEM_VELL_GENERATED)) return false;
        if (sector.getStarSystem(SYSTEM_NAME) != null) return false;
        return !RslNex.isRandomSector();
    }

    public static void generate(SectorAPI sector) {
        if (!shouldGenerate(sector)) return;
        sector.getMemoryWithoutUpdate().set(RslIds.MEM_VELL_GENERATED, true);
        String f = RslIds.FACTION_CHOIR;

        StarSystemAPI system = sector.createStarSystem(SYSTEM_NAME);
        Vector2f loc = findFreeHyperspaceLocation(sector, PREFERRED_LOCATION);
        system.getLocation().set(loc.x, loc.y);
        system.setBackgroundTextureFilename("graphics/backgrounds/background5.jpg");

        // the pulsar, set up as StarSystemGenerator.setPulsarIfNeutron does
        PlanetAPI star = system.initStar(RslIds.ID_VELL_STAR, StarTypes.NEUTRON_STAR, 120f, 250f);
        star.setCustomDescriptionId("rsl_desc_vell");
        system.setLightColor(new Color(205, 220, 255));
        StarCoronaTerrainPlugin corona = Misc.getCoronaFor(star);
        if (corona != null) system.removeEntity(corona.getEntity());
        system.addCorona(star, 300f, 3f, 0f, 3f);
        StarGenDataSpec data = (StarGenDataSpec) Global.getSettings().getSpec(StarGenDataSpec.class,
                StarTypes.NEUTRON_STAR, true);
        float band = 600f, wind = 3f, flare = 0f, crLoss = 3f;
        if (data != null) {   // vanilla's numbers with the random terms at their middle
            band = Math.max(star.getRadius() * data.getCoronaMult(), data.getCoronaMin());
            wind = data.getSolarWind();
            flare = (data.getMinFlare() + data.getMaxFlare()) * 0.5f;
            crLoss = data.getCrLossMult();
        }
        SectorEntityToken beam = system.addTerrain(Terrain.PULSAR_BEAM, new StarCoronaTerrainPlugin.CoronaParams(
                star.getRadius() + band, (star.getRadius() + band) / 2f, star, wind, flare, crLoss));
        beam.setCircularOrbit(star, 0f, 0f, 100f);

        SectorEntityToken tacetEntity = system.addCustomEntity(RslIds.ID_TACET, "Tacet Station", "station_side04", f);
        tacetEntity.setCircularOrbitPointingDown(star, 30f, 1900f, 55f);
        tacetEntity.setCustomDescriptionId("rsl_desc_tacet");

        PlanetAPI tenuto = system.addPlanet(RslIds.ID_TENUTO, star, "Tenuto", "irradiated", 200f, 70f, 3300f, 90f);
        tenuto.setCustomDescriptionId("rsl_desc_tenuto");
        Misc.initConditionMarket(tenuto);
        tenuto.getMarket().addCondition(Conditions.IRRADIATED);
        tenuto.getMarket().addCondition(Conditions.NO_ATMOSPHERE);
        tenuto.getMarket().addCondition(Conditions.ORE_SPARSE);

        PlanetAPI basso = system.addPlanet(RslIds.ID_BASSO, star, "Basso", "ice_giant", 120f, 300f, 6200f, 250f);
        basso.setCustomDescriptionId("rsl_desc_basso");
        system.addRingBand(basso, "misc", "rings_ice0", 256f, 1, new Color(170, 200, 230, 200), 256f, 560f, 40f);

        PlanetAPI coda = system.addPlanet(RslIds.ID_CODA, basso, "Coda", "frozen", 40f, 110f, 900f, 32f);
        coda.setCustomDescriptionId("rsl_desc_coda");
        PlanetAPI glass = system.addPlanet(RslIds.ID_GLASSHOUSE, basso, "Glasshouse", "rocky_ice", 220f, 80f, 1350f,
                48f);
        glass.setCustomDescriptionId("rsl_desc_glasshouse");

        // the Cantor Array's station entity: connected to Coda's market so CantorArrayIndustry spawns on it
        SectorEntityToken array = system.addCustomEntity(RslIds.ID_CANTOR_ARRAY, "Cantor Array",
                Entities.STATION_BUILT_FROM_INDUSTRY, f);
        array.addTag(Tags.USE_STATION_VISUAL);
        array.setCircularOrbitWithSpin(coda, 90f, 330f, 24f, 2f, 2f);
        array.setCustomDescriptionId("rsl_desc_cantor_array");

        system.addAsteroidBelt(star, 120, 9000f, 400f, 280f, 340f, Terrain.ASTEROID_BELT, "The Long Rest");
        system.addRingBand(star, "misc", "rings_dust0", 256f, 2, new Color(150, 170, 200, 180), 256f, 9000f, 300f);

        SectorEntityToken relay = system.addCustomEntity(RslIds.ID_VELL_RELAY, null, Entities.COMM_RELAY, f);
        relay.setCircularOrbitPointingDown(star, 300f, 4600f, 140f);
        SectorEntityToken buoy = system.addCustomEntity(RslIds.ID_VELL_BUOY, null, Entities.NAV_BUOY, f);
        buoy.setCircularOrbitPointingDown(basso, 200f, 1800f, 60f);
        SectorEntityToken sensor = system.addCustomEntity(RslIds.ID_VELL_SENSOR, null, Entities.SENSOR_ARRAY, f);
        sensor.setCircularOrbitPointingDown(star, 100f, 7600f, 220f);

        system.autogenerateHyperspaceJumpPoints(true, true);
        clearHyperspaceAround(system);

        FactionAPI faction = sector.getFaction(f);
        PersonAPI precentor = person(sector, RslIds.PERSON_PRECENTOR, "Ilian", "Okoro-Vass", FullName.Gender.MALE,
                "graphics/portraits/portrait25.png", Ranks.FACTION_LEADER, Ranks.POST_FACTION_LEADER,
                PersonImportance.VERY_HIGH);
        PersonAPI tanh = person(sector, RslIds.PERSON_TANH, "Mireille", "Tanh", FullName.Gender.FEMALE,
                "graphics/portraits/portrait27.png", Ranks.CITIZEN, Ranks.POST_INTELLIGENCE_DIRECTOR,
                PersonImportance.HIGH);
        PersonAPI abelard = person(sector, RslIds.PERSON_ABELARD, "Corvin", "Abelard", FullName.Gender.MALE,
                "graphics/portraits/portrait_league13.png", Ranks.CITIZEN, Ranks.POST_SCIENTIST,
                PersonImportance.HIGH);

        MarketAPI codaM = market(RslIds.MARKET_CODA, coda, "Coda", 5,
                new String[]{Conditions.POPULATION_5, Conditions.VERY_COLD, Conditions.LOW_GRAVITY,
                        Conditions.THIN_ATMOSPHERE, Conditions.VOLATILES_DIFFUSE, Conditions.ORE_MODERATE},
                new String[]{Industries.POPULATION, Industries.MEGAPORT, Industries.MILITARYBASE,
                        Industries.ORBITALWORKS, Industries.REFINING, Industries.HEAVYBATTERIES,
                        RslIds.INDUSTRY_CANTOR_ARRAY},
                new String[]{Submarkets.SUBMARKET_OPEN, Submarkets.GENERIC_MILITARY, Submarkets.SUBMARKET_BLACK,
                        Submarkets.SUBMARKET_STORAGE});
        codaM.getConnectedEntities().add(array);
        array.setMarket(codaM);
        staff(codaM, precentor, precentor);
        staff(codaM, abelard, null);

        MarketAPI glassM = market(RslIds.MARKET_GLASSHOUSE, glass, "Glasshouse", 4,
                new String[]{Conditions.POPULATION_4, Conditions.NO_ATMOSPHERE, Conditions.VERY_COLD,
                        Conditions.LOW_GRAVITY, Conditions.RARE_ORE_RICH, Conditions.ORE_MODERATE,
                        RslIds.CONDITION_NURSERIES},
                new String[]{Industries.POPULATION, Industries.SPACEPORT, Industries.MINING, Industries.PATROLHQ,
                        Industries.GROUNDDEFENSES},
                new String[]{Submarkets.SUBMARKET_OPEN, Submarkets.SUBMARKET_BLACK, Submarkets.SUBMARKET_STORAGE});
        PersonAPI glassAdmin = admin(faction);
        staff(glassM, glassAdmin, glassAdmin);

        MarketAPI tacetM = market(RslIds.MARKET_TACET, tacetEntity, "Tacet Station", 3,
                new String[]{Conditions.POPULATION_3},
                new String[]{Industries.POPULATION, Industries.SPACEPORT, Industries.WAYSTATION,
                        Industries.ORBITALSTATION_HIGH},
                new String[]{Submarkets.SUBMARKET_OPEN, Submarkets.SUBMARKET_BLACK, Submarkets.SUBMARKET_STORAGE});
        PersonAPI tacetAdmin = admin(faction);
        staff(tacetM, tacetAdmin, tacetAdmin);
        staff(tacetM, tanh, null);

        log.info("Resonance Lattice: generated Vell at " + loc);
    }

    private static MarketAPI market(String id, SectorEntityToken entity, String name, int size, String[] conditions,
                                    String[] industries, String[] submarkets) {
        MarketAPI m = Global.getFactory().createMarket(id, name, size);
        m.setFactionId(RslIds.FACTION_CHOIR);
        m.setPrimaryEntity(entity);
        m.getTariff().modifyFlat("default_tariff", m.getFaction().getTariffFraction());   // as vanilla Galatia.java
        for (String c : conditions) m.addCondition(c);
        for (String i : industries) m.addIndustry(i);
        for (String s : submarkets) m.addSubmarket(s);
        m.setSurveyLevel(MarketAPI.SurveyLevel.FULL);
        entity.setMarket(m);
        entity.setFaction(RslIds.FACTION_CHOIR);
        Global.getSector().getEconomy().addMarket(m, true);
        return m;
    }

    /** Adds a person to the market and its comm directory; also makes them the admin when {@code admin} is them. */
    private static void staff(MarketAPI m, PersonAPI p, PersonAPI admin) {
        m.addPerson(p);
        m.getCommDirectory().addPerson(p);
        p.setMarket(m);
        if (admin != null) m.setAdmin(admin);
    }

    private static PersonAPI admin(FactionAPI faction) {
        PersonAPI p = faction.createRandomPerson();
        p.setRankId(Ranks.CITIZEN);
        p.setPostId(Ranks.POST_ADMINISTRATOR);
        p.setImportance(PersonImportance.MEDIUM);
        return p;
    }

    /** A named, important person: created once and kept in the sector's important people. */
    private static PersonAPI person(SectorAPI sector, String id, String first, String last, FullName.Gender gender,
                                    String portrait, String rank, String post, PersonImportance importance) {
        PersonAPI p = sector.getImportantPeople().getPerson(id);
        if (p != null) return p;
        p = Global.getFactory().createPerson();
        p.setId(id);
        p.setFaction(RslIds.FACTION_CHOIR);
        p.setGender(gender);
        p.setName(new FullName(first, last, gender));
        p.setPortraitSprite(portrait);
        p.setRankId(rank);
        p.setPostId(post);
        p.setImportance(importance);
        sector.getImportantPeople().addPerson(p);
        return p;
    }

    static Vector2f findFreeHyperspaceLocation(SectorAPI sector, Vector2f preferred) {
        for (int ring = 0; ring < 14; ring++) {
            float r = ring * 1400f;
            int steps = ring == 0 ? 1 : 8 + ring * 4;
            for (int i = 0; i < steps; i++) {
                double a = i * 2.0 * Math.PI / steps;
                Vector2f c = new Vector2f(preferred.x + (float) Math.cos(a) * r, preferred.y + (float) Math.sin(a) * r);
                if (isFree(sector, c)) return c;
            }
        }
        return new Vector2f(preferred);
    }

    private static boolean isFree(SectorAPI sector, Vector2f c) {
        for (StarSystemAPI s : sector.getStarSystems()) {
            if (s != null && s.getLocation() != null && Misc.getDistance(s.getLocation(), c) < MIN_SYSTEM_SEPARATION) {
                return false;
            }
        }
        return true;
    }

    static void clearHyperspaceAround(StarSystemAPI system) {
        try {
            if (Misc.getHyperspaceTerrain() == null) return;
            HyperspaceTerrainPlugin plugin = (HyperspaceTerrainPlugin) Misc.getHyperspaceTerrain().getPlugin();
            NebulaEditor editor = new NebulaEditor(plugin);
            float minRadius = plugin.getTileSize() * 2f;
            float radius = system.getMaxRadiusInHyperspace();
            editor.clearArc(system.getLocation().x, system.getLocation().y, 0, radius + minRadius * 0.5f, 0, 360f);
            editor.clearArc(system.getLocation().x, system.getLocation().y, 0, radius + minRadius, 0, 360f, 0.25f);
        } catch (Throwable t) {
            log.warn("Resonance Lattice: could not clear hyperspace around Vell", t);
        }
    }
}
