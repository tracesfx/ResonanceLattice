package rsl.hullmods;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.combat.BaseHullMod;
import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.ui.TooltipMakerAPI;
import org.magiclib.util.MagicIncompatibleHullmods;
import org.magiclib.util.MagicUI;
import rsl.RslIds;
import rsl.combat.LatticeData;
import rsl.combat.LatticeDealtModifier;
import rsl.combat.RslUtil;

import java.awt.Color;

/**
 * The faction-wide built-in (DESIGN.md section 2). Resonance itself is kept in {@link LatticeData} and fed by
 * {@link rsl.combat.RslDamageListener}; this class decays it, shows the player's Resonance bar and wires the
 * per-ship damage modifier. Safety Overrides "detunes" the lattice and is removed with a warning.
 */
public class LatticeCore extends BaseHullMod {
    /** One keyed bar: the keyless MagicUI call keys bars by label, so the label switch drew a second bar. */
    private static final String BAR_KEY = "rsl_resonance";
    private static final Color BAR = new Color(100, 230, 220, 255);
    private static final Color BAR_OVERTONE = new Color(180, 150, 255, 255);
    private static final Color BORDER = new Color(60, 140, 140, 255);

    @Override
    public void applyEffectsBeforeShipCreation(HullSize hullSize, MutableShipStatsAPI stats, String id) {
        if (stats.getVariant() != null && stats.getVariant().getHullMods().contains(RslIds.HULLMOD_SAFETY)) {
            MagicIncompatibleHullmods.removeHullmodWithWarning(stats.getVariant(), RslIds.HULLMOD_SAFETY, id);
        }
    }

    @Override
    public void applyEffectsAfterShipCreation(ShipAPI ship, String id) {
        if (!ship.hasListenerOfClass(LatticeDealtModifier.class)) ship.addListener(new LatticeDealtModifier(ship));
    }

    @Override
    public void advanceInCombat(ShipAPI ship, float amount) {
        CombatEngineAPI engine = Global.getCombatEngine();
        if (engine == null || engine.isPaused() || !ship.isAlive()) return;
        LatticeData d = LatticeData.get(ship);
        d.sinceGain += amount;
        if (d.sinceGain > LatticeData.DECAY_DELAY && d.resonance > 0f) {
            float decay = LatticeData.isTuned(ship, d) ? LatticeData.TUNED_DECAY : 1f;
            d.resonance = Math.max(0f, d.resonance - LatticeData.DECAY_PER_SEC * decay * amount);
        }
        if (ship == engine.getPlayerShip()) {
            boolean over = d.resonance >= LatticeData.OVERTONE;
            MagicUI.drawInterfaceStatusBar(ship, BAR_KEY, d.resonance / LatticeData.MAX, over ? BAR_OVERTONE : BAR, BORDER,
                    LatticeData.OVERTONE / LatticeData.MAX, over ? "OVERTONE" : "RESONANCE", (int) d.resonance);
        }
    }

    @Override
    public void addPostDescriptionSection(TooltipMakerAPI t, HullSize hullSize, ShipAPI ship, float width,
                                          boolean isForModSpec) {
        Tip.section(t, "Resonance");
        Tip.good(t, "Builds %s Resonance from damage absorbed by this ship's shields and from its hits on enemy hull "
                + "and armor.", "0-100");
        Tip.good(t, "Decays by %s per second after %s seconds without any gain.",
                "" + (int) LatticeData.DECAY_PER_SEC, "" + (int) LatticeData.DECAY_DELAY);
        Tip.good(t, "The seams glow brighter as Resonance rises.");
        Tip.section(t, "Overtone");
        Tip.good(t, "At %s Resonance or more, the next ship-system use is empowered (see the system's description) "
                + "and spends %s.", "" + (int) LatticeData.OVERTONE, "" + (int) LatticeData.OVERTONE_COST);
        Tip.section(t, "Sympathy");
        Tip.good(t, "Lattice allies within %s units receive %s of the Resonance this ship gains.",
                "" + (int) LatticeData.SYMPATHY_RANGE, Tip.pct(LatticeData.SYMPATHY_SHARE));
        Tip.badSection(t, "Incompatible");
        Tip.bad(t, "%s detunes the lattice and is removed.", "Safety Overrides");
        Tip.end(t);
    }

    @Override
    public String getSModDescriptionParam(int index, HullSize hullSize) {
        return index == 0 ? Tip.pct(LatticeData.ENHANCED_GAIN - 1f) : null;
    }

    @Override
    public boolean isApplicableToShip(ShipAPI ship) {
        return RslUtil.isLattice(ship);
    }
}
