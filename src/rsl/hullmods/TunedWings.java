package rsl.hullmods;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.combat.BaseHullMod;
import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.ui.TooltipMakerAPI;
import rsl.combat.RslUtil;

import java.util.List;

/** Halo: fighter replacement is faster while any of its own fighters fight inside the ring zone. */
public class TunedWings extends BaseHullMod {
    public static final float RANGE = 700f;
    public static final float REFIT_MULT = 0.8f;
    public static final float ENHANCED_RANGE = 1000f;
    public static final float ENHANCED_REFIT_MULT = 0.67f;
    private static final String ID = "rsl_tuned_wings";

    @Override
    public void advanceInCombat(ShipAPI ship, float amount) {
        CombatEngineAPI engine = Global.getCombatEngine();
        if (engine == null || engine.isPaused() || !ship.isAlive()) return;
        boolean any = false;
        boolean enh = RslUtil.enhanced(ship, ID);
        List<ShipAPI> ships = engine.getShips();
        float r = enh ? ENHANCED_RANGE : RANGE;
        float r2 = r * r;
        for (int i = 0; i < ships.size() && !any; i++) {
            ShipAPI s = ships.get(i);
            if (!s.isFighter() || s.isHulk() || s.getWing() == null || s.getWing().getSourceShip() != ship) continue;
            float dx = s.getLocation().x - ship.getLocation().x, dy = s.getLocation().y - ship.getLocation().y;
            any = dx * dx + dy * dy < r2;
        }
        if (any) ship.getMutableStats().getFighterRefitTimeMult().modifyMult(ID, enh ? ENHANCED_REFIT_MULT : REFIT_MULT);
        else ship.getMutableStats().getFighterRefitTimeMult().unmodify(ID);
    }

    @Override
    public void addPostDescriptionSection(TooltipMakerAPI t, HullSize hullSize, ShipAPI ship, float width,
                                          boolean isForModSpec) {
        Tip.section(t, "Tuned to the ring");
        Tip.good(t, "While any of this ship's fighters fight within %s units of it, its fighters are replaced %s "
                + "faster.", "" + (int) RANGE, Tip.pct(1f / REFIT_MULT - 1f));
        Tip.end(t);
    }

    @Override
    public String getSModDescriptionParam(int index, HullSize hullSize) {
        if (index == 0) return "" + (int) ENHANCED_RANGE;
        if (index == 1) return Tip.pct(Math.round((1f / ENHANCED_REFIT_MULT - 1f) * 100f) / 100f);
        return null;
    }
}
