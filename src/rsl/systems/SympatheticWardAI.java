package rsl.systems;

import com.fs.starfarer.api.combat.ShipAPI;
import org.lwjgl.util.vector.Vector2f;


/** Refrain: ward an ally that is taking a beating while the Refrain itself has flux to spare. */
public class SympatheticWardAI extends RslSystemAI {
    @Override
    protected boolean decide(Vector2f missileDangerDir, Vector2f collisionDangerDir, ShipAPI target) {
        if (ship.getFluxLevel() > 0.6f) return false;
        ShipAPI ally = SympatheticWardStats.pickAlly(ship);
        return ally != null && (ally.getFluxLevel() > 0.6f || ally.getHullLevel() < 0.55f);
    }
}
