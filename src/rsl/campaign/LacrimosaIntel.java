package rsl.campaign;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.campaign.BattleAPI;
import com.fs.starfarer.api.campaign.CampaignEventListener.FleetDespawnReason;
import com.fs.starfarer.api.campaign.CampaignFleetAPI;
import com.fs.starfarer.api.campaign.CampaignUIAPI;
import com.fs.starfarer.api.campaign.FactionAPI;
import com.fs.starfarer.api.campaign.LocationAPI;
import com.fs.starfarer.api.campaign.PlanetAPI;
import com.fs.starfarer.api.campaign.SectorEntityToken;
import com.fs.starfarer.api.campaign.StarSystemAPI;
import com.fs.starfarer.api.campaign.TextPanelAPI;
import com.fs.starfarer.api.campaign.comm.IntelInfoPlugin;
import com.fs.starfarer.api.campaign.econ.MarketAPI;
import com.fs.starfarer.api.campaign.listeners.FleetEventListener;
import com.fs.starfarer.api.characters.PersonAPI;
import com.fs.starfarer.api.impl.campaign.ids.Factions;
import com.fs.starfarer.api.impl.campaign.ids.Tags;
import com.fs.starfarer.api.impl.campaign.intel.BaseIntelPlugin;
import com.fs.starfarer.api.ui.SectorMapAPI;
import com.fs.starfarer.api.ui.TooltipMakerAPI;
import com.fs.starfarer.api.util.Misc;
import org.apache.log4j.Logger;
import org.lwjgl.util.vector.Vector2f;
import rsl.RslIds;
import rsl.rulecmd.RslLacrimosa;

import java.awt.Color;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Set;

/**
 * The Lacrimosa questline (CAMPAIGN.md section 6): the whole quest state, its timers and its fleets, in one saved intel
 * item (aliased in RslModPlugin). The dialogs are in {@link RslLacrimosa}; facts other content needs after the quest
 * (path, upgraded, Hush done, refused Sung) are mirrored into global memory ({@link RslIds} MEM_*), so the intel can
 * end without losing them.
 *
 * Lifecycle (skill rule 6): every quest fleet reports to this listener; a lost or despawned boss never blocks the
 * quest (Special Projects: beat 4 opens anyway; the Hush: respawned if it vanished undefeated); the Unsung can be
 * lost or sold (beat 6 then offers the Institute's spare frame once); no Cantorate market left: the council resolves
 * as "Solo" and the recording is skipped.
 */
public class LacrimosaIntel extends BaseIntelPlugin implements FleetEventListener {
    private static final Logger log = Global.getLogger(LacrimosaIntel.class);

    public enum Stage { BUOYS, INSTITUTE, SUNG, HUNTED, COUNCIL, RECORDING, SEARCH, HUSH, RETURN, DONE, SOLD }

    /** Days after the Lacrimosa wakes before Director Sung's courier finds the player. */
    public static final float SUNG_DELAY = 1.5f;
    /** Special Projects strikes this many days (random in range) after the refusal ... */
    public static final float HUNT_DELAY_MIN = 4f, HUNT_DELAY_MAX = 14f;
    /** ... and gives up this many days after the refusal; beat 4 opens either way. */
    public static final float HUNT_GIVE_UP = 60f;
    /** A hunter that has lost the player's trail this long is moved onto it again. */
    public static final float HUNT_RETRACK = 4f;
    public static final float BUOY_MIN_SPREAD = 14000f;
    /** Graveyard: inside the Orion-Perseus Abyss, shallow enough that AI fleets do not flee the depth (0.5). */
    public static final float HUSH_DEPTH_MIN = 0.3f, HUSH_DEPTH_MAX = 0.45f;

    private Stage stage = Stage.BUOYS;
    private final List<SectorEntityToken> buoys = new ArrayList<SectorEntityToken>();
    private final boolean[] scanned = new boolean[3];
    private int scans;
    private int guardedBuoy = -1;
    private CampaignFleetAPI scavengers;

    private SectorEntityToken institute;
    private CampaignFleetAPI guard;

    private float sinceWake;
    private float sungRetry;

    private CampaignFleetAPI hunter;
    private PersonAPI hunterCommander;
    private float hunterDelay;
    private float huntedDays;
    private float hunterLostDays;

    private final List<SectorEntityToken> echoes = new ArrayList<SectorEntityToken>();
    private int echo;
    private SectorEntityToken graveyard;
    private CampaignFleetAPI hush;
    /**
     * Fleets to unhook (and retire, if still alive) on the next tick. Never call removeEventListener or despawn from
     * inside a fleet callback: the engine is iterating that fleet's listener list (ConcurrentModificationException in
     * CampaignEngine.reportBattleOccurred, seen in game).
     */
    private List<CampaignFleetAPI> release = new ArrayList<CampaignFleetAPI>();
    private PersonAPI hushCommander;

    // ------------------------------------------------------------------------------------------------- access

    /** The running quest, or null if it never started (or ended). */
    public static LacrimosaIntel get() {
        for (IntelInfoPlugin p : Global.getSector().getIntelManager().getIntel(LacrimosaIntel.class)) {
            LacrimosaIntel q = (LacrimosaIntel) p;
            if (!q.isEnded()) return q;
        }
        return null;
    }

    public static boolean started() {
        return get() != null || Global.getSector().getMemoryWithoutUpdate().getBoolean(RslIds.MEM_VIRTUOSO_GRANTED)
                || Global.getSector().getMemoryWithoutUpdate().getBoolean(RslIds.MEM_SOLD);
    }

    public Stage getStage() {
        return stage;
    }

    public SectorEntityToken getInstitute() {
        return institute;
    }

    public boolean isGuardAlive() {
        return guard != null && guard.isAlive() && !guard.isEmpty();
    }

    public boolean isScavengerNear(SectorEntityToken buoy) {
        return scavengers != null && scavengers.isAlive() && buoys.indexOf(buoy) == guardedBuoy
                && scavengers.getContainingLocation() == buoy.getContainingLocation()
                && Misc.getDistance(scavengers, buoy) < 3000f;
    }

    public boolean isScanned(SectorEntityToken buoy) {
        int i = buoys.indexOf(buoy);
        return i >= 0 && scanned[i];
    }

    public int getScans() {
        return scans;
    }

    public boolean isCurrentEcho(SectorEntityToken e) {
        return stage == Stage.SEARCH && echo < echoes.size() && echoes.get(echo) == e;
    }

    public int getEchoIndex() {
        return echo;
    }

    public boolean isHushAlive() {
        return hush != null && hush.isAlive() && !hush.isEmpty();
    }

    public static String path() {
        Object o = Global.getSector().getMemoryWithoutUpdate().get(RslIds.MEM_PATH);
        return o instanceof String ? (String) o : null;
    }

    public static boolean isChorus() {
        return "chorus".equals(path());
    }

    public static boolean isSolo() {
        return "solo".equals(path());
    }

    // ------------------------------------------------------------------------------------------------- beat 1

    /** Starts the quest (Archivist Tanh): three listening buoys in fringe hyperspace, the last one watched. */
    public static LacrimosaIntel start(TextPanelAPI text) {
        if (started()) return get();
        LacrimosaIntel q = new LacrimosaIntel();
        List<StarSystemAPI> picks = pickBuoySystems(3);
        LocationAPI hyper = Global.getSector().getHyperspace();
        String[] names = {"Listening Buoy Aleph", "Listening Buoy Bet", "Listening Buoy Gimel"};
        float farthest = -1f;
        Vector2f home = vellLocation();
        for (int i = 0; i < picks.size(); i++) {
            StarSystemAPI s = picks.get(i);
            float r = s.getMaxRadiusInHyperspace() + 1400f;
            float a = (float) (Math.random() * Math.PI * 2.0);
            SectorEntityToken b = hyper.addCustomEntity(null, names[i], RslIds.ENTITY_BUOY, Factions.NEUTRAL);
            b.setFixedLocation(s.getLocation().x + (float) Math.cos(a) * r, s.getLocation().y + (float) Math.sin(a) * r);
            b.setDiscoverable(false);
            b.getMemoryWithoutUpdate().set("$rsl_nearSystem", s.getNameWithLowercaseType());
            Misc.makeImportant(b, "rsl_lacrimosa");
            q.buoys.add(b);
            float d = Misc.getDistance(home, b.getLocation());
            if (d > farthest) {
                farthest = d;
                q.guardedBuoy = i;
            }
        }
        if (q.buoys.isEmpty()) {   // a sector with no wild fringe systems: straight to the Institute
            q.revealInstitute();
            q.stage = Stage.INSTITUTE;
        }
        if (q.guardedBuoy >= 0) q.scavengers = LacrimosaFleets.scavengers(q.buoys.get(q.guardedBuoy));
        if (q.scavengers != null) q.scavengers.addEventListener(q);
        q.setImportant(true);
        Global.getSector().getIntelManager().addIntel(q, false, text);
        return q;
    }

    /** Fringe systems without markets, as far apart as can be found (relaxing the spread until 3 are found). */
    private static List<StarSystemAPI> pickBuoySystems(int n) {
        List<StarSystemAPI> pool = new ArrayList<StarSystemAPI>();
        for (StarSystemAPI s : Global.getSector().getStarSystems()) {
            if (!isWildSystem(s)) continue;
            if (s.getLocation().length() < 12000f) continue;   // the fringe, not the core
            pool.add(s);
        }
        if (pool.size() < n) {
            for (StarSystemAPI s : Global.getSector().getStarSystems()) if (isWildSystem(s) && !pool.contains(s)) pool.add(s);
        }
        Collections.shuffle(pool);
        float[] spreads = {BUOY_MIN_SPREAD, 9000f, 5000f, 0f};
        for (float spread : spreads) {
            List<StarSystemAPI> out = new ArrayList<StarSystemAPI>();
            for (StarSystemAPI s : pool) {
                boolean ok = true;
                for (StarSystemAPI o : out) if (Misc.getDistance(o.getLocation(), s.getLocation()) < spread) ok = false;
                if (ok) out.add(s);
                if (out.size() == n) return out;
            }
        }
        return pool.subList(0, Math.min(n, pool.size()));
    }

    /** A procgen system nobody lives in: no markets, not hidden, not in the abyss, not Vell. */
    public static boolean isWildSystem(StarSystemAPI s) {
        if (s == null || s.getLocation() == null || s.hasTag(Tags.THEME_HIDDEN) || s.hasTag(Tags.THEME_CORE)) return false;
        if (s.isNebula() || s.getStar() == null || s.getId().startsWith("rsl_") || "Vell".equals(s.getBaseName())) return false;
        if (Misc.getAbyssalDepth(s.getLocation()) > 0f) return false;
        return Misc.getMarketsInLocation(s).isEmpty();
    }

    private static Vector2f vellLocation() {
        StarSystemAPI vell = Global.getSector().getStarSystem("Vell");
        return vell != null ? vell.getLocation() : new Vector2f(0f, 0f);
    }

    public void scanBuoy(SectorEntityToken buoy, TextPanelAPI text) {
        int i = buoys.indexOf(buoy);
        if (i < 0 || scanned[i]) return;
        scanned[i] = true;
        scans++;
        Misc.makeUnimportant(buoy, "rsl_lacrimosa");
        if (scans >= buoys.size()) {
            revealInstitute();
            stage = Stage.INSTITUTE;
        }
        sendUpdate(text);
    }

    // ------------------------------------------------------------------------------------------------- beat 2

    private void revealInstitute() {
        StarSystemAPI sys = pickInstituteSystem();
        if (sys == null) {
            log.error("Resonance Lattice: no system for the Antiphon Institute; using Vell's neighbourhood");
            sys = Global.getSector().getStarSystems().get(0);
        }
        SectorEntityToken anchor = sys.getStar();
        float orbit = anchor.getRadius() + 3500f;
        PlanetAPI best = null;
        for (PlanetAPI p : sys.getPlanets()) {
            if (p.isStar()) continue;
            if (best == null || p.getCircularOrbitRadius() > best.getCircularOrbitRadius()) best = p;
        }
        if (best != null) {
            anchor = best;
            orbit = best.getRadius() + 450f;
        }
        institute = sys.addCustomEntity("rsl_antiphon_institute", "Antiphon Institute", RslIds.ENTITY_INSTITUTE,
                Factions.NEUTRAL);
        institute.setCircularOrbitPointingDown(anchor, (float) (Math.random() * 360f), orbit, 120f);
        institute.setDiscoverable(false);
        Misc.makeImportant(institute, "rsl_lacrimosa");
        guard = LacrimosaFleets.derelictGuard(institute);
        guard.addEventListener(this);
    }

    /** The deepest-fringe wild system not used by a buoy: farthest from the sector's centre. */
    private StarSystemAPI pickInstituteSystem() {
        List<StarSystemAPI> pool = new ArrayList<StarSystemAPI>();
        for (StarSystemAPI s : Global.getSector().getStarSystems()) {
            if (!isWildSystem(s) || s.getPlanets().size() < 2) continue;
            boolean used = false;
            for (SectorEntityToken b : buoys) if (Misc.getDistance(b.getLocation(), s.getLocation()) < 4000f) used = true;
            if (!used) pool.add(s);
        }
        if (pool.isEmpty()) return null;
        Collections.sort(pool, (a, b) -> Float.compare(b.getLocation().length(), a.getLocation().length()));
        int top = Math.max(1, pool.size() / 5);   // random among the outermost fifth
        return pool.get((int) (Math.random() * top));
    }

    /** Beat 2 climax: the fleet drops to 30% CR, the Unsung joins as the Lacrimosa. */
    public void wake(TextPanelAPI text) {
        CampaignFleetAPI pf = Global.getSector().getPlayerFleet();
        for (com.fs.starfarer.api.fleet.FleetMemberAPI m : pf.getFleetData().getMembersListCopy()) {
            float cr = m.getRepairTracker().getCR();
            if (cr > Lacrimosa.WAKE_CR) m.getRepairTracker().setCR(Lacrimosa.WAKE_CR);
        }
        Lacrimosa.grantUnsung(text);
        stage = Stage.SUNG;
        sinceWake = 0f;
        sendUpdate(text);
    }

    // ------------------------------------------------------------------------------------------------- beat 3

    public void sold(TextPanelAPI text) {
        stage = Stage.SOLD;
        Global.getSector().getMemoryWithoutUpdate().set(RslIds.MEM_SOLD, true);
        Misc.makeUnimportant(institute, "rsl_lacrimosa");
        sendUpdate(text);
        endAfterDelay();
    }

    public void refused(TextPanelAPI text) {
        stage = Stage.HUNTED;
        Global.getSector().getMemoryWithoutUpdate().set(RslIds.MEM_REFUSED_SUNG, true);
        hunterDelay = HUNT_DELAY_MIN + (float) Math.random() * (HUNT_DELAY_MAX - HUNT_DELAY_MIN);
        huntedDays = 0f;
        sendUpdate(text);
    }

    /** "I need time": Sung's courier comes back in a few days. */
    public void deferSung() {
        sungRetry = 3f;
    }

    private void spawnHunter() {
        CampaignFleetAPI pf = Global.getSector().getPlayerFleet();
        LocationAPI where = pf.getContainingLocation();
        Vector2f p = Misc.getPointAtRadius(pf.getLocation(), 2200f);
        hunter = LacrimosaFleets.specialProjects(where, p.x, p.y);
        hunterCommander = hunter.getCommander();
        hunter.addEventListener(this);
        Global.getSector().getCampaignUI().addMessage("Your sensors officer reports a phase signature closing fast: "
                + "Special Projects has found you.", Misc.getNegativeHighlightColor());
    }

    private void endHunt(boolean beaten) {
        releaseLater(hunter);
        hunter = null;
        stage = Stage.COUNCIL;
        if (!hasCantorateMarket()) resolveWithoutCouncil();
        sendUpdate(beaten ? "beaten" : "lost");
    }

    // ------------------------------------------------------------------------------------------------- beat 4

    public static boolean hasCantorateMarket() {
        for (MarketAPI m : Global.getSector().getEconomy().getMarketsCopy()) {
            if (RslIds.FACTION_CHOIR.equals(m.getFactionId()) && !m.isHidden()) return true;
        }
        return false;
    }

    /** The council's verdict: "chorus" or "solo". */
    public void decide(String path, TextPanelAPI text) {
        Global.getSector().getMemoryWithoutUpdate().set(RslIds.MEM_PATH, path);
        stage = Stage.RECORDING;
        sendUpdate(text);
    }

    private void resolveWithoutCouncil() {
        Global.getSector().getMemoryWithoutUpdate().set(RslIds.MEM_PATH, "solo");
        beginSearch(null);
    }

    /** Tanh's pulsar recording: the search for the graveyard begins (and the Chorus escorts join). */
    public void beginSearch(TextPanelAPI text) {
        stage = Stage.SEARCH;
        placeEchoes();
        echo = 0;
        Misc.makeImportant(echoes.get(0), "rsl_lacrimosa");
        if (isChorus()) {
            List<com.fs.starfarer.api.fleet.FleetMemberAPI> esc = LacrimosaFleets.councilEscorts();
            if (text != null && !esc.isEmpty()) {
                text.addPara("Two Cantorate ships join your fleet for the search, on the Precentor's orders: %s and "
                        + "%s, with their captains.", Misc.getPositiveHighlightColor(), esc.get(0).getShipName(),
                        esc.size() > 1 ? esc.get(1).getShipName() : "");
            }
        }
        sendUpdate(text);
    }

    // ------------------------------------------------------------------------------------------------- beat 5

    /** Three echoes leading in to the graveyard, from the abyss edge towards its centre. */
    private void placeEchoes() {
        Vector2f grave = findGraveyardLocation();
        Vector2f from = institute != null ? institute.getLocationInHyperspace() : vellLocation();
        Vector2f dir = Vector2f.sub(from, grave, null);
        if (dir.lengthSquared() < 1f) dir.set(1f, 0f);
        dir.normalise();
        LocationAPI hyper = Global.getSector().getHyperspace();
        float[] dists = {7000f, 4200f, 1800f};
        for (int i = 0; i < 3; i++) {
            float side = (i % 2 == 0 ? 1f : -1f) * 900f;
            SectorEntityToken e = hyper.addCustomEntity(null, "Silent Echo", RslIds.ENTITY_ECHO, Factions.NEUTRAL);
            e.setFixedLocation(grave.x + dir.x * dists[i] - dir.y * side, grave.y + dir.y * dists[i] + dir.x * side);
            e.setDiscoverable(false);
            echoes.add(e);
        }
        graveyard = hyper.addCustomEntity(null, "The Hush", RslIds.ENTITY_GRAVEYARD, Factions.NEUTRAL);
        graveyard.setFixedLocation(grave.x, grave.y);
        graveyard.setDiscoverable(false);
    }

    /** The point inside the abyss depth band that is closest to the Institute (or to Vell). */
    private Vector2f findGraveyardLocation() {
        float w = Global.getSettings().getFloat("sectorWidth"), h = Global.getSettings().getFloat("sectorHeight");
        Vector2f from = institute != null ? institute.getLocationInHyperspace() : vellLocation();
        Vector2f best = null;
        float bestD = Float.MAX_VALUE;
        Vector2f p = new Vector2f();
        for (float x = -w / 2f - 4000f; x <= w / 2f + 4000f; x += 1500f) {
            for (float y = -h / 2f - 4000f; y <= h / 2f + 4000f; y += 1500f) {
                p.set(x, y);
                float depth = Misc.getAbyssalDepth(p);
                if (depth < HUSH_DEPTH_MIN || depth > HUSH_DEPTH_MAX) continue;
                float d = Misc.getDistance(p, from);
                if (d < bestD) {
                    bestD = d;
                    best = new Vector2f(p);
                }
            }
        }
        if (best == null) best = new Vector2f(-w / 2f + 3000f, -h / 2f + 3000f);
        return best;
    }

    /** A sensor sweep at the current echo: reveals the next one, or after the third the graveyard and the Hush. */
    public void sweep(SectorEntityToken e, TextPanelAPI text) {
        if (!isCurrentEcho(e)) return;
        Misc.makeUnimportant(e, "rsl_lacrimosa");
        echo++;
        if (echo < echoes.size()) {
            Misc.makeImportant(echoes.get(echo), "rsl_lacrimosa");
        } else {
            stage = Stage.HUSH;
            Misc.makeImportant(graveyard, "rsl_lacrimosa");
            spawnHush();
        }
        sendUpdate(text);
    }

    private void spawnHush() {
        hush = LacrimosaFleets.hush(graveyard);
        hushCommander = hush.getCommander();
        hush.addEventListener(this);
    }

    private void hushSilenced() {
        releaseLater(hush);
        hush = null;
        Global.getSector().getMemoryWithoutUpdate().set(RslIds.MEM_HUSH_DONE, true);
        Misc.makeUnimportant(graveyard, "rsl_lacrimosa");
        stage = Stage.RETURN;
        if (institute != null) Misc.makeImportant(institute, "rsl_lacrimosa");
        Lacrimosa.hushRewards();
        int left = LacrimosaFleets.dismissEscorts();
        if (left > 0) {
            Global.getSector().getCampaignUI().addMessage("The Cantorate escorts salute the Lacrimosa and turn for "
                    + "home.", Misc.getTextColor());
        }
        sendUpdate("hush");
    }

    // ------------------------------------------------------------------------------------------------- beat 6

    public void complete(TextPanelAPI text) {
        stage = Stage.DONE;
        Global.getSector().getMemoryWithoutUpdate().set(RslIds.MEM_VIRTUOSO_UPGRADED, true);
        Global.getSector().getMemoryWithoutUpdate().set(RslIds.MEM_UPGRADED_AT,
                Global.getSector().getClock().getTimestamp());
        Misc.makeUnimportant(institute, "rsl_lacrimosa");
        sendUpdate(text);
        endAfterDelay();
    }

    // ------------------------------------------------------------------------------------------------- testing

    /** Console testing (Lacrimosa.debug): plays the beats forward, skipping fights, until {@code target}. */
    void debugJump(String target) {
        Stage want = null;
        String t = target.trim().toUpperCase();
        for (Stage s : Stage.values()) {   // prefix match: "buoy", "inst", "hush" ...
            if (s.name().startsWith(t) || t.startsWith(s.name())) {
                want = s;
                break;
            }
        }
        if (want == null) {
            log.warn("Resonance Lattice: unknown quest stage '" + target + "'; use one of "
                    + java.util.Arrays.toString(Stage.values()));
            return;
        }
        for (int guardLoop = 0; guardLoop < 20 && stage.ordinal() < want.ordinal(); guardLoop++) {
            switch (stage) {
                case BUOYS:
                    for (SectorEntityToken b : new ArrayList<SectorEntityToken>(buoys)) scanBuoy(b, null);
                    if (scavengers != null && scavengers.isAlive()) scavengers.despawn();
                    break;
                case INSTITUTE:
                    if (guard != null && guard.isAlive()) guard.despawn();
                    wake(null);
                    break;
                case SUNG:
                    refused(null);
                    break;
                case HUNTED:
                    endHunt(true);
                    break;
                case COUNCIL:
                    decide("chorus", null);
                    break;
                case RECORDING:
                    beginSearch(null);
                    break;
                case SEARCH:
                    sweep(echoes.get(echo), null);
                    break;
                case HUSH:
                    hushSilenced();
                    break;
                default:
                    return;
            }
        }
    }

    // ------------------------------------------------------------------------------------------------- timers

    @Override
    protected void advanceImpl(float amount) {
        try {
            if (release == null) release = new ArrayList<CampaignFleetAPI>();   // saves from before this field
            if (!release.isEmpty()) {
                List<CampaignFleetAPI> copy = new ArrayList<CampaignFleetAPI>(release);
                release.clear();
                for (CampaignFleetAPI f : copy) {
                    f.removeEventListener(this);
                    if (f.isAlive()) LacrimosaFleets.retire(f);
                }
            }
            float days = Global.getSector().getClock().convertToDays(amount);
            switch (stage) {
                case SUNG:
                    sinceWake += days;
                    if (sungRetry > 0f) sungRetry -= days;
                    if (sinceWake >= SUNG_DELAY && sungRetry <= 0f && canShowDialog()) {
                        sungRetry = 1f;   // if the dialog could not open, try again tomorrow
                        CampaignFleetAPI pf = Global.getSector().getPlayerFleet();
                        Global.getSector().getCampaignUI().showInteractionDialog(new RslLacrimosa("sung"), pf);
                    }
                    break;
                case HUNTED:
                    advanceHunt(days);
                    break;
                case COUNCIL:
                case RECORDING:
                    if (!hasCantorateMarket()) {
                        if (stage == Stage.COUNCIL) Global.getSector().getMemoryWithoutUpdate().set(RslIds.MEM_PATH, "solo");
                        beginSearch(null);
                    }
                    break;
                case HUSH:
                    // the Hush must exist while the quest waits for it (despawned by anything but defeat: respawn)
                    if (hush == null || !hush.isAlive()) spawnHush();
                    break;
                default:
                    break;
            }
        } catch (Throwable t) {
            log.error("Resonance Lattice: Lacrimosa quest tick failed", t);
        }
    }

    private void advanceHunt(float days) {
        huntedDays += days;
        if (huntedDays >= HUNT_GIVE_UP) {
            endHunt(false);
            return;
        }
        CampaignFleetAPI pf = Global.getSector().getPlayerFleet();
        if (hunter == null) {
            hunterDelay -= days;
            if (hunterDelay <= 0f && pf != null && !pf.isInHyperspaceTransition() && canShowDialog()) spawnHunter();
            return;
        }
        if (!hunter.isAlive()) {
            endHunt(false);
            return;
        }
        if (hunter.getContainingLocation() != pf.getContainingLocation()) {
            hunterLostDays += days;
            if (hunterLostDays >= HUNT_RETRACK && !pf.isInHyperspaceTransition()) {
                hunterLostDays = 0f;
                hunter.getContainingLocation().removeEntity(hunter);
                pf.getContainingLocation().addEntity(hunter);
                Vector2f p = Misc.getPointAtRadius(pf.getLocation(), 3000f);
                hunter.setLocation(p.x, p.y);
                hunter.clearAssignments();
                hunter.addAssignment(com.fs.starfarer.api.campaign.FleetAssignment.INTERCEPT, pf, 1000f,
                        "hunting the Lacrimosa");
            }
        } else {
            hunterLostDays = 0f;
        }
    }

    private static boolean canShowDialog() {
        CampaignUIAPI ui = Global.getSector().getCampaignUI();
        CampaignFleetAPI pf = Global.getSector().getPlayerFleet();
        return ui != null && pf != null && !ui.isShowingDialog() && !ui.isShowingMenu()
                && Global.getSector().isPaused() == false && !pf.isInHyperspaceTransition();
    }

    // ------------------------------------------------------------------------------------------------- listener

    @Override
    public void reportBattleOccurred(CampaignFleetAPI fleet, CampaignFleetAPI primaryWinner, BattleAPI battle) {
        if (fleet == hunter && hunter != null && stage == Stage.HUNTED) {
            if (hunter.getFlagship() == null || hunter.getFlagship().getCaptain() != hunterCommander) endHunt(true);
        } else if (fleet == hush && hush != null && stage == Stage.HUSH) {
            if (hush.getFlagship() == null || hush.getFlagship().getCaptain() != hushCommander || hush.isEmpty()) {
                if (battle.isPlayerInvolved()) hushSilenced();
            }
        } else if (fleet == scavengers && (scavengers.isEmpty() || !scavengers.isAlive())) {
            releaseLater(scavengers);
            scavengers = null;
        }
    }

    @Override
    public void reportFleetDespawnedToListener(CampaignFleetAPI fleet, FleetDespawnReason reason, Object param) {
        if (fleet == hunter && stage == Stage.HUNTED) {
            endHunt(reason == FleetDespawnReason.DESTROYED_BY_BATTLE);
        } else if (fleet == hush && stage == Stage.HUSH) {
            if (reason == FleetDespawnReason.DESTROYED_BY_BATTLE) {
                hushSilenced();
            } else {
                hush = null;   // advanceImpl puts it back
            }
        } else if (fleet == guard) {
            guard = null;
        } else if (fleet == scavengers) {
            scavengers = null;
        }
    }

    private void releaseLater(CampaignFleetAPI f) {
        if (f == null) return;
        if (release == null) release = new ArrayList<CampaignFleetAPI>();
        if (!release.contains(f)) release.add(f);
    }

    @Override
    protected void notifyEnded() {
        super.notifyEnded();
        if (hunter != null) hunter.removeEventListener(this);
        if (hush != null) hush.removeEventListener(this);
        if (guard != null) guard.removeEventListener(this);
        if (scavengers != null) scavengers.removeEventListener(this);
        if (release != null) {
            for (CampaignFleetAPI f : release) f.removeEventListener(this);
            release.clear();
        }
    }

    private void sendUpdate(Object param) {
        if (param instanceof TextPanelAPI) {
            Global.getSector().getIntelManager().addIntelToTextPanel(this, (TextPanelAPI) param);
        } else {
            sendUpdateIfPlayerHasIntel(param, false);
        }
    }

    // ------------------------------------------------------------------------------------------------- display

    @Override
    protected String getName() {
        if (stage == Stage.DONE) return "Lacrimosa - Completed";
        if (stage == Stage.SOLD) return "Lacrimosa - Sold";
        return "Lacrimosa";
    }

    @Override
    public FactionAPI getFactionForUIColors() {
        return Global.getSector().getFaction(RslIds.FACTION_CHOIR);
    }

    @Override
    public String getIcon() {
        return Global.getSettings().getSpriteName("intel", RslIds.GFX_INTEL_LACRIMOSA);
    }

    @Override
    public Set<String> getIntelTags(SectorMapAPI map) {
        Set<String> tags = super.getIntelTags(map);
        tags.add(Tags.INTEL_STORY);
        tags.add(Tags.INTEL_ACCEPTED);
        tags.add(RslIds.FACTION_CHOIR);
        return tags;
    }

    /** One line: what to do now. */
    private String objective() {
        switch (stage) {
            case BUOYS:
                return "Scan the Antiphon Institute's listening buoys (" + scans + " of " + buoys.size() + ")";
            case INSTITUTE:
                return "Find the Antiphon Institute in " + systemName(institute);
            case SUNG:
                return "Leave the Institute with the Lacrimosa";
            case HUNTED:
                return hunter == null ? "Director Sung will not take no for an answer" : "Special Projects is hunting you";
            case COUNCIL:
                return "Answer the Precentor's summons at a Cantorate market (Coda)";
            case RECORDING:
                return "Collect Tacet Station's pulsar recording from Archivist Tanh";
            case SEARCH:
                return "Run sensor sweeps in the abyss (" + echo + " of " + echoes.size() + ")";
            case HUSH:
                return "Silence the Hush";
            case RETURN:
                return "Return the sash to the Antiphon Institute's dock";
            case DONE:
                return "The Lacrimosa sings again";
            default:
                return "The Lacrimosa belongs to Tri-Tachyon now";
        }
    }

    @Override
    protected void addBulletPoints(TooltipMakerAPI info, ListInfoMode mode, boolean isUpdate, Color tc, float initPad) {
        bullet(info);
        info.addPara(objective(), initPad, tc);
        if (stage == Stage.BUOYS) {
            for (int i = 0; i < buoys.size(); i++) {
                if (scanned[i] || mode == ListInfoMode.IN_DESC) continue;
                info.addPara("A buoy near %s", 0f, tc, Misc.getHighlightColor(),
                        buoys.get(i).getMemoryWithoutUpdate().getString("$rsl_nearSystem"));
            }
        }
        if (stage == Stage.RETURN) {
            info.addPara("Price: %s Pitch Glass and %s", 0f, tc, Misc.getHighlightColor(), "" + Lacrimosa.PRICE_GLASS,
                    Misc.getDGSCredits(Lacrimosa.PRICE_CREDITS));
        }
        unindent(info);
    }

    @Override
    public void createSmallDescription(TooltipMakerAPI info, float width, float height) {
        float opad = 10f;
        Color h = Misc.getHighlightColor();
        switch (stage) {
            case BUOYS:
                info.addPara("Archivist Mireille Tanh has heard a pulsar-locked signal in hyperspace: the core of the "
                        + "Lacrimosa, the Domain's lost Virtuoso, waking after two centuries. Three of the Antiphon "
                        + "Institute's old listening buoys can triangulate it. One is said to be watched by "
                        + "scavengers.", opad);
                break;
            case INSTITUTE:
                info.addPara("The buoys agree. The Antiphon Institute lies in %s, and its Domain defences are still "
                        + "awake.", opad, h, systemName(institute));
                break;
            case SUNG:
            case HUNTED:
                info.addPara("The Lacrimosa is in your fleet. Tri-Tachyon's Special Projects, under Director Hale "
                        + "Sung, wants its core.", opad);
                if (stage == Stage.HUNTED) {
                    info.addPara("You refused him. A Special Projects fleet will come for you; destroy its flagship. "
                            + "If you can stay ahead of it, Sung will give up after %s days.", opad, h,
                            "" + (int) Math.max(1, Math.ceil(HUNT_GIVE_UP - huntedDays)));
                }
                break;
            case COUNCIL:
                info.addPara("The Cantorate knows what you carry. The Precentor has called a council at Coda to "
                        + "decide how the Lacrimosa is to be retuned.", opad);
                break;
            case RECORDING:
                info.addPara("The council has spoken (%s). Archivist Tanh needs Tacet Station's raw pulsar recording "
                        + "to tune the search for the First Chorus.", opad, h, isChorus() ? "Chorus" : "Solo");
                break;
            case SEARCH:
                info.addPara("The First Chorus died in the abyss beyond the Sector's edge. Its cores still ring. Fly "
                        + "to each faint echo and sweep it to narrow the search.", opad);
                break;
            case HUSH:
                info.addPara("Twelve wrecks and more, still singing: the Hush. When one falls, its resonance floods "
                        + "the others. Kill order matters; the Lacrimosa's Stolen Time is the counter.", opad);
                break;
            case RETURN:
                info.addPara("The Lacrimosa's sash and vanes are in your hold. Only the Institute's dock can mount "
                        + "them. The Luthiers will do the work there, for %s Pitch Glass and %s.", opad, h,
                        "" + Lacrimosa.PRICE_GLASS, Misc.getDGSCredits(Lacrimosa.PRICE_CREDITS));
                break;
            case DONE:
                info.addPara(isChorus() ? "The Lacrimosa is whole, and it has learned to sing with others. The "
                        + "Precentor has named you an honorary Maestro." : "The Lacrimosa is whole, finished as Saskia "
                        + "Venn designed it. \"Now it sings alone,\" Abelard said. \"Try not to let it get hungry.\"",
                        opad);
                break;
            default:
                info.addPara("You sold the Lacrimosa's core to Director Sung. The Cantorate will not forget it.", opad);
                break;
        }
        addBulletPoints(info, ListInfoMode.IN_DESC);
    }

    private static String systemName(SectorEntityToken e) {
        if (e == null || e.getStarSystem() == null) return "an unknown system";
        return e.getStarSystem().getNameWithLowercaseType();
    }

    @Override
    public SectorEntityToken getMapLocation(SectorMapAPI map) {
        switch (stage) {
            case BUOYS:
                for (int i = 0; i < buoys.size(); i++) if (!scanned[i]) return buoys.get(i);
                return null;
            case INSTITUTE:
            case RETURN:
            case DONE:
                return institute;
            case COUNCIL:
                return cantorateEntity(RslIds.MARKET_CODA);
            case RECORDING:
                return cantorateEntity(RslIds.MARKET_TACET);
            case SEARCH:
                return echo < echoes.size() ? echoes.get(echo) : graveyard;
            case HUSH:
                return graveyard;
            default:
                return null;
        }
    }

    /** The preferred market's entity if the Cantorate still holds it, else any Cantorate market's. */
    private static SectorEntityToken cantorateEntity(String preferred) {
        MarketAPI m = Global.getSector().getEconomy().getMarket(preferred);
        if (m != null && RslIds.FACTION_CHOIR.equals(m.getFactionId())) return m.getPrimaryEntity();
        for (MarketAPI o : Global.getSector().getEconomy().getMarketsCopy()) {
            if (RslIds.FACTION_CHOIR.equals(o.getFactionId()) && !o.isHidden()) return o.getPrimaryEntity();
        }
        return null;
    }

    @Override
    public String getSortString() {
        return "Lacrimosa";
    }

}
