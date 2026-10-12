package rsl.hullmods;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.combat.BaseHullMod;
import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import rsl.combat.LatticeData;

/**
 * Virtuoso: at 100% CR the ship enters Bravura (hysteresis down to 92%). The glow renderer cross-fades the seams to
 * the gold sprite and the wing vanes flare from {@link LatticeData#bravuraLevel}. Locked on the Unsung.
 */
public class Bravura extends BaseHullMod {
    public static final float ENTER = 0.995f;
    public static final float EXIT = 0.92f;
    public static final float SPEED = 20f;
    public static final float FLUX = 25f;
    public static final float ROF = 20f;
    public static final float SYSTEM_REGEN = 30f;
    private static final String ID = "rsl_bravura";
    private static final Object STATUS = new Object();

    @Override
    public void advanceInCombat(ShipAPI ship, float amount) {
        CombatEngineAPI engine = Global.getCombatEngine();
        if (engine == null || !ship.isAlive() || !StolenTime.isFull(ship)) return;
        LatticeData d = LatticeData.get(ship);
        float cr = ship.getCurrentCR();
        if (!d.bravura && cr >= ENTER) d.bravura = true;
        else if (d.bravura && cr < EXIT) d.bravura = false;
        MutableShipStatsAPI s = ship.getMutableStats();
        if (d.bravura) {
            s.getMaxSpeed().modifyPercent(ID, SPEED);
            s.getAcceleration().modifyPercent(ID, SPEED);
            s.getDeceleration().modifyPercent(ID, SPEED);
            s.getMaxTurnRate().modifyPercent(ID, SPEED);
            s.getTurnAcceleration().modifyPercent(ID, SPEED);
            s.getFluxDissipation().modifyPercent(ID, FLUX);
            s.getEnergyRoFMult().modifyPercent(ID, ROF);
            s.getSystemRegenBonus().modifyPercent(ID, SYSTEM_REGEN);
            if (ship == engine.getPlayerShip()) {
                engine.maintainStatusForPlayerShip(STATUS, "graphics/rsl/icons/hullmods/rsl_bravura.png", "BRAVURA",
                        "full voice: faster, hotter, every lance accented", false);
            }
        } else {
            s.getMaxSpeed().unmodify(ID);
            s.getAcceleration().unmodify(ID);
            s.getDeceleration().unmodify(ID);
            s.getMaxTurnRate().unmodify(ID);
            s.getTurnAcceleration().unmodify(ID);
            s.getFluxDissipation().unmodify(ID);
            s.getEnergyRoFMult().unmodify(ID);
            s.getSystemRegenBonus().unmodify(ID);
        }
    }

    @Override
    public String getDescriptionParam(int index, HullSize hullSize) {
        switch (index) {
            case 0:
                return "100%";
            case 1:
                return (int) (EXIT * 100f) + "%";
            case 2:
                return (int) SPEED + "%";
            case 3:
                return (int) FLUX + "%";
            case 4:
                return (int) ROF + "%";
            case 5:
                return (int) SYSTEM_REGEN + "%";
            default:
                return null;
        }
    }
}
