package rsl.hullmods;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.combat.BaseHullMod;
import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
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
        float r2 = LatticeData.BRIDGE_RANGE * LatticeData.BRIDGE_RANGE;
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
    public String getDescriptionParam(int index, HullSize hullSize) {
        if (index == 0) return "" + (int) LatticeData.BRIDGE_RANGE;
        if (index == 1) return (int) (LatticeData.BRIDGE_SHARE * 100f) + "%";
        if (index == 2) return "" + TRICKLE;
        return null;
    }
}
