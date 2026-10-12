package rsl.hullmods;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.combat.BaseHullMod;
import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.ui.TooltipMakerAPI;
import rsl.combat.LatticeData;
import rsl.combat.RslUtil;

import java.util.List;

/**
 * Conductor: doubles the Sympathy it shares (handled in {@link LatticeData#gain}) and hums a slow trickle of
 * Resonance into Lattice allies within range.
 */
public class ConductorsBridge extends BaseHullMod {
    public static final float TRICKLE = 0.5f;

    @Override
    public void advanceInCombat(ShipAPI ship, float amount) {
        CombatEngineAPI engine = Global.getCombatEngine();
        if (engine == null || engine.isPaused() || !ship.isAlive()) return;
        float range = LatticeData.bridgeRange(ship);
        float r2 = range * range;
        List<ShipAPI> ships = engine.getShips();
        for (int i = 0; i < ships.size(); i++) {
            ShipAPI s = ships.get(i);
            if (s == ship || s.getOwner() != ship.getOwner() || s.isHulk() || s.isFighter() || !RslUtil.isLattice(s)) {
                continue;
            }
            float dx = s.getLocation().x - ship.getLocation().x, dy = s.getLocation().y - ship.getLocation().y;
            if (dx * dx + dy * dy > r2) continue;
            LatticeData d = LatticeData.get(s);
            d.resonance = Math.min(LatticeData.MAX, d.resonance + TRICKLE * amount);
        }
    }

    @Override
    public void addPostDescriptionSection(TooltipMakerAPI t, HullSize hullSize, ShipAPI ship, float width,
                                          boolean isForModSpec) {
        Tip.section(t, "The chorus follows");
        Tip.good(t, "Lattice allies within %s units receive %s of the Resonance this ship gains (instead of the "
                + "usual %s within %s).", "" + (int) LatticeData.BRIDGE_RANGE, Tip.pct(LatticeData.BRIDGE_SHARE),
                Tip.pct(LatticeData.SYMPATHY_SHARE), "" + (int) LatticeData.SYMPATHY_RANGE);
        Tip.good(t, "They also gain %s Resonance per second while in range.", "" + TRICKLE);
        Tip.end(t);
    }

    @Override
    public String getSModDescriptionParam(int index, HullSize hullSize) {
        return index == 0 ? "" + (int) (LatticeData.BRIDGE_RANGE * LatticeData.ENHANCED_BRIDGE_RANGE) : null;
    }
}
