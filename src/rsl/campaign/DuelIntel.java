package rsl.campaign;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.campaign.BattleAPI;
import com.fs.starfarer.api.campaign.CampaignEventListener.FleetDespawnReason;
import com.fs.starfarer.api.campaign.CampaignFleetAPI;
import com.fs.starfarer.api.campaign.FactionAPI;
import com.fs.starfarer.api.campaign.SectorEntityToken;
import com.fs.starfarer.api.campaign.TextPanelAPI;
import com.fs.starfarer.api.campaign.comm.IntelInfoPlugin;
import com.fs.starfarer.api.campaign.listeners.FleetEventListener;
import com.fs.starfarer.api.characters.PersonAPI;
import com.fs.starfarer.api.fleet.FleetMemberAPI;
import com.fs.starfarer.api.impl.campaign.ids.MemFlags;
import com.fs.starfarer.api.impl.campaign.ids.Tags;
import com.fs.starfarer.api.impl.campaign.intel.BaseIntelPlugin;
import com.fs.starfarer.api.ui.SectorMapAPI;
import com.fs.starfarer.api.ui.TooltipMakerAPI;
import com.fs.starfarer.api.util.Misc;
import org.apache.log4j.Logger;
import rsl.RslIds;

import java.awt.Color;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;

/**
 * "The Second Voice" (user, 2026-10-13): once the Lacrimosa is complete, Tri-Tachyon's Special Projects answers it with
 * a Virtuoso of its own, the Dies Irae, flown by Commander Isolde Raike (level 15). She waits at the Antiphon Institute
 * for a duel: one ship each, no seconds.
 *
 * The duel is fought by the Lacrimosa alone: while the encounter runs, every other ship in the player's fleet is held
 * here ({@link #hold}) and given back when the encounter dialog closes ({@link #restore}; also on the next tick if
 * that callback is ever missed). Losing is not fatal: the combat side makes the Lacrimosa yield and withdraw instead of
 * being disabled (rsl.combat.EncoreCombat). Raike repairs and waits for a rematch. Winning builds Ossia into the
 * Lacrimosa and pays {@link #REWARD_GLASS} Pitch Glass.
 */
public class DuelIntel extends BaseIntelPlugin implements FleetEventListener {
    private static final Logger log = Global.getLogger(DuelIntel.class);
    public static final int REWARD_GLASS = 250;
    /** Days after the Lacrimosa's completion before Raike's challenge arrives. */
    public static final float DELAY_DAYS = 14f;
    public static final String INSTITUTE_ID = "rsl_antiphon_institute";

    private CampaignFleetAPI fleet;
    private SectorEntityToken anchor;
    private boolean won;
    private int attempts;
    /** Ships held out of the duel, with the captains they had. */
    private final List<FleetMemberAPI> held = new ArrayList<FleetMemberAPI>();
    private final List<PersonAPI> heldCaptains = new ArrayList<PersonAPI>();
    private boolean encounter;
    private final List<CampaignFleetAPI> release = new ArrayList<CampaignFleetAPI>();

    public static DuelIntel get() {
        for (IntelInfoPlugin p : Global.getSector().getIntelManager().getIntel(DuelIntel.class)) {
            DuelIntel q = (DuelIntel) p;
            if (!q.isEnded()) return q;
        }
        return null;
    }

    public static boolean started() {
        return !Global.getSector().getIntelManager().getIntel(DuelIntel.class).isEmpty()
                || Global.getSector().getMemoryWithoutUpdate().getBoolean(RslIds.MEM_DUEL_WON);
    }

    /** Raike's challenge (from RslCampaignScript, or the console). Null if the Institute is gone. */
    public static DuelIntel start() {
        if (get() != null) return get();
        SectorEntityToken inst = Global.getSector().getEntityById(INSTITUTE_ID);
        if (inst == null || inst.getContainingLocation() == null) return null;
        DuelIntel q = new DuelIntel();
        q.anchor = inst;
        q.spawn();
        q.setImportant(true);
        Global.getSector().getIntelManager().addIntel(q);
        return q;
    }

    private void spawn() {
        fleet = EncoreFleets.diesIrae(anchor);
        fleet.addEventListener(this);
    }

    public CampaignFleetAPI getFleet() {
        return fleet;
    }

    public int getAttempts() {
        return attempts;
    }

    // ------------------------------------------------------------------------------------------------- the duel

    /** Why the duel cannot start now, or null. */
    public static String whyNot() {
        CampaignFleetAPI pf = Global.getSector().getPlayerFleet();
        FleetMemberAPI v = Lacrimosa.findHull(RslIds.HULL_VIRTUOSO);
        if (pf == null || v == null) return "The Lacrimosa is not in your fleet.";
        if (pf.getFlagship() != v) return "The Lacrimosa must be your flagship: Raike will duel its captain, not a proxy.";
        if (v.isMothballed()) return "The Lacrimosa is mothballed.";
        return null;
    }

    /** Accepting: every other ship is held out of the encounter, the Dies Irae turns hostile. */
    public void beginEncounter() {
        CampaignFleetAPI pf = Global.getSector().getPlayerFleet();
        FleetMemberAPI v = Lacrimosa.findHull(RslIds.HULL_VIRTUOSO);
        if (pf == null || v == null) return;
        restore();   // never hold twice
        for (FleetMemberAPI m : pf.getFleetData().getMembersListCopy()) {
            if (m == v) continue;
            heldCaptains.add(m.getCaptain());
            held.add(m);
            pf.getFleetData().removeFleetMember(m);
        }
        pf.getMemoryWithoutUpdate().set(RslIds.MEM_DUEL_ACTIVE, true);
        fleet.getMemoryWithoutUpdate().set(MemFlags.MEMORY_KEY_MAKE_HOSTILE, true);
        encounter = true;
        attempts++;
    }

    /** The encounter dialog closed (FIDDelegate.notifyLeave). */
    public void endEncounter() {
        restore();
        encounter = false;
        if (won) return;
        if (fleet != null && fleet.isAlive() && !fleet.isEmpty()) {
            fleet.getMemoryWithoutUpdate().unset(MemFlags.MEMORY_KEY_MAKE_HOSTILE);
            EncoreFleets.restore(fleet);
        }
    }

    private void restore() {
        CampaignFleetAPI pf = Global.getSector().getPlayerFleet();
        if (pf != null) pf.getMemoryWithoutUpdate().unset(RslIds.MEM_DUEL_ACTIVE);
        if (pf == null || held.isEmpty()) return;
        for (int i = 0; i < held.size(); i++) {
            FleetMemberAPI m = held.get(i);
            pf.getFleetData().addFleetMember(m);
            PersonAPI c = i < heldCaptains.size() ? heldCaptains.get(i) : null;
            if (c != null && !c.isDefault() && pf.getFleetData().getMemberWithCaptain(c) == null) m.setCaptain(c);
        }
        held.clear();
        heldCaptains.clear();
        pf.getFleetData().sort();
        pf.forceSync();
    }

    private void victory() {
        if (won) return;
        won = true;   // held ships come back when the encounter dialog closes (never mid-encounter)
        if (!Global.getSector().getMemoryWithoutUpdate().getBoolean(RslIds.MEM_DUEL_WON)) {
            Global.getSector().getMemoryWithoutUpdate().set(RslIds.MEM_DUEL_WON, true);
            FleetMemberAPI v = Lacrimosa.findHull(RslIds.HULL_VIRTUOSO);
            if (v != null && !v.getVariant().hasHullMod(RslIds.HULLMOD_OSSIA)) {
                v.getVariant().addPermaMod(RslIds.HULLMOD_OSSIA, false);
                v.updateStats();
            }
            PitchGlass.add(REWARD_GLASS);
            Global.getSector().getCampaignUI().addMessage("The Dies Irae is silent. In the wreck's core room you find "
                    + "Raike's own score of the duel, annotated in her hand: Ossia is now part of the Lacrimosa, and "
                    + REWARD_GLASS + " Pitch Glass is yours.", Misc.getTextColor(), "Ossia",
                    "" + REWARD_GLASS, Misc.getHighlightColor(), Misc.getHighlightColor());
        }
        if (fleet != null) release.add(fleet);
        sendUpdateIfPlayerHasIntel(null, false);
        endAfterDelay();
    }

    // ------------------------------------------------------------------------------------------------- ticks

    @Override
    protected void advanceImpl(float amount) {
        try {
            if (!release.isEmpty()) {
                for (CampaignFleetAPI f : new ArrayList<CampaignFleetAPI>(release)) {
                    f.removeEventListener(this);
                    if (f.isAlive()) LacrimosaFleets.retire(f);
                }
                release.clear();
            }
            // a missed notifyLeave must never strand the fleet's other ships
            if (!held.isEmpty() && !Global.getSector().getCampaignUI().isShowingDialog()
                    && Global.getSector().getPlayerFleet().getBattle() == null) {
                log.warn("Resonance Lattice: duel encounter ended without notice; returning held ships");
                endEncounter();
            }
            if (!won && !encounter && (fleet == null || !fleet.isAlive())) {
                if (anchor == null || anchor.getContainingLocation() == null) {
                    endImmediately();
                    return;
                }
                spawn();   // despawned by something other than the duel: put her back
            }
        } catch (Throwable t) {
            log.error("Resonance Lattice: duel tick failed", t);
        }
    }

    @Override
    public void reportBattleOccurred(CampaignFleetAPI f, CampaignFleetAPI primaryWinner, BattleAPI battle) {
        if (f == fleet && fleet != null && (fleet.isEmpty() || fleet.getFlagship() == null)) victory();
    }

    @Override
    public void reportFleetDespawnedToListener(CampaignFleetAPI f, FleetDespawnReason reason, Object param) {
        if (f != fleet) return;
        if (reason == FleetDespawnReason.DESTROYED_BY_BATTLE) victory();
        else if (!won) fleet = null;
    }

    @Override
    protected void notifyEnded() {
        super.notifyEnded();
        restore();
        if (fleet != null) fleet.removeEventListener(this);
    }

    // ------------------------------------------------------------------------------------------------- display

    @Override
    protected String getName() {
        return won ? "The Second Voice - Won" : "The Second Voice";
    }

    @Override
    public FactionAPI getFactionForUIColors() {
        return Global.getSector().getFaction(RslIds.FACTION_CHOIR);
    }

    @Override
    public String getIcon() {
        return Global.getSettings().getSpriteName("intel", RslIds.GFX_INTEL_DUEL);
    }

    @Override
    public Set<String> getIntelTags(SectorMapAPI map) {
        Set<String> tags = super.getIntelTags(map);
        tags.add(Tags.INTEL_STORY);
        tags.add(RslIds.FACTION_CHOIR);
        return tags;
    }

    @Override
    protected void addBulletPoints(TooltipMakerAPI info, ListInfoMode mode, boolean isUpdate, Color tc, float initPad) {
        bullet(info);
        if (won) {
            info.addPara("Ossia is built into the Lacrimosa", initPad, tc, Misc.getHighlightColor(), "Ossia");
        } else {
            info.addPara("The Dies Irae waits at the Antiphon Institute", initPad, tc);
            info.addPara("One ship each: the Lacrimosa, as your flagship", 0f, tc);
        }
        unindent(info);
    }

    @Override
    public void createSmallDescription(TooltipMakerAPI info, float width, float height) {
        float opad = 10f;
        Color h = Misc.getHighlightColor();
        info.addImage(Global.getSector().getImportantPeople().getPerson(RslIds.PERSON_RAIKE) != null
                ? Global.getSector().getImportantPeople().getPerson(RslIds.PERSON_RAIKE).getPortraitSprite()
                : getIcon(), 128f, opad);
        if (won) {
            info.addPara("You met Commander Isolde Raike's Dies Irae over the Antiphon Institute and sang it down. "
                    + "She was the only other pilot who ever flew a Virtuoso.", opad);
        } else {
            info.addPara("Tri-Tachyon's Special Projects picked through the Hush's graveyard after you silenced it, "
                    + "and built a Virtuoso of its own around a cracked core: the %s. Its pilot, Commander %s, has "
                    + "sent the Lacrimosa a challenge. She waits at the Antiphon Institute.", opad, h, "Dies Irae",
                    "Isolde Raike");
            info.addPara("One ship each, no seconds: the Lacrimosa must be your flagship, and your other ships will "
                    + "hold back. Raike is a level %s commander with every combat skill at its peak.", opad, h,
                    "" + EncoreFleets.RAIKE_LEVEL);
            info.addPara("Losing is not the end. The Lacrimosa will break off before it breaks, and Raike will wait "
                    + "for a rematch.", opad);
            if (attempts > 0) info.addPara("Attempts so far: %s.", opad, h, "" + attempts);
        }
        addBulletPoints(info, ListInfoMode.IN_DESC);
    }

    @Override
    public SectorEntityToken getMapLocation(SectorMapAPI map) {
        return anchor;
    }

    @Override
    public String getSortString() {
        return "Lacrimosa 2";
    }

    // ------------------------------------------------------------------------------------------------- testing

    /** Console: {@code runcode rsl.campaign.DuelIntel.debug()} starts the challenge now (needs the Institute). */
    public static void debug() {
        try {
            DuelIntel q = start();
            log.info("Resonance Lattice: duel " + (q == null ? "could not start (no Antiphon Institute)" : "started"));
        } catch (Throwable t) {
            log.error("Resonance Lattice: duel debug failed", t);
        }
    }

    /** Console: the reward without the fight. */
    public static void debugWin() {
        DuelIntel q = get();
        if (q != null) q.victory();
    }
}
