package rsl.hullmods;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.combat.BaseHullMod;
import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;

import java.util.List;

/** Halo: fighter replacement is faster while any of its own fighters fight inside the ring zone. */
public class TunedWings extends BaseHullMod {
    public static final float RANGE = 700f;
    public static final float REFIT_MULT = 0.8f;
    private static final String ID = "rsl_tuned_wings";

    @Override
    public void advanceInCombat(ShipAPI ship, float amount) {
        CombatEngineAPI engine = Global.getCombatEngine();
        if (engine == null || engine.isPaused() || !ship.isAlive()) return;
        boolean any = false;
        List<ShipAPI> ships = engine.getShips();
        float r2 = RANGE * RANGE;
        for (int i = 0; i < ships.size() && !any; i++) {
            ShipAPI s = ships.get(i);
            if (!s.isFighter() || s.isHulk() || s.getWing() == null || s.getWing().getSourceShip() != ship) continue;
            float dx = s.getLocation().x - ship.getLocation().x, dy = s.getLocation().y - ship.getLocation().y;
            any = dx * dx + dy * dy < r2;
        }
        if (any) ship.getMutableStats().getFighterRefitTimeMult().modifyMult(ID, REFIT_MULT);
        else ship.getMutableStats().getFighterRefitTimeMult().unmodify(ID);
    }

    @Override
    public String getDescriptionParam(int index, HullSize hullSize) {
        if (index == 0) return "" + (int) RANGE;
        if (index == 1) return (int) ((1f / REFIT_MULT - 1f) * 100f) + "%";
        return null;
    }
}
