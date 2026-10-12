package rsl.hullmods;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.combat.BaseHullMod;
import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
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
            d.resonance = Math.max(0f, d.resonance - LatticeData.DECAY_PER_SEC * amount);
        }
        if (ship == engine.getPlayerShip()) {
            boolean over = d.resonance >= LatticeData.OVERTONE;
            MagicUI.drawInterfaceStatusBar(ship, BAR_KEY, d.resonance / LatticeData.MAX, over ? BAR_OVERTONE : BAR, BORDER,
                    LatticeData.OVERTONE / LatticeData.MAX, over ? "OVERTONE" : "RESONANCE", (int) d.resonance);
        }
    }

    @Override
    public String getDescriptionParam(int index, HullSize hullSize) {
        switch (index) {
            case 0:
                return "" + (int) LatticeData.OVERTONE;
            case 1:
                return "" + (int) LatticeData.OVERTONE_COST;
            case 2:
                return "" + (int) LatticeData.SYMPATHY_RANGE;
            case 3:
                return (int) (LatticeData.SYMPATHY_SHARE * 100f) + "%";
            default:
                return null;
        }
    }

    @Override
    public boolean isApplicableToShip(ShipAPI ship) {
        return RslUtil.isLattice(ship);
    }
}
