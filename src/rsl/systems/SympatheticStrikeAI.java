package rsl.systems;

import com.fs.starfarer.api.combat.ShipAPI;
import org.lwjgl.util.vector.Vector2f;


/** Conductor: strike whenever a target is in range and the flux allows it. */
public class SympatheticStrikeAI extends RslSystemAI {
    @Override
    protected boolean decide(Vector2f missileDangerDir, Vector2f collisionDangerDir, ShipAPI target) {
        if (ship.getFluxLevel() > 0.75f) return false;
        ShipAPI t = SympatheticStrikeStats.pickTarget(ship);
        return t != null && dist(t) < SympatheticStrikeStats.RANGE * 0.95f;
    }
}
