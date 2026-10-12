package rsl.systems;

import com.fs.starfarer.api.combat.ShipAPI;
import org.lwjgl.util.vector.Vector2f;
import rsl.combat.RslUtil;


/** Cantor Array: sing whenever an enemy ship is within reach of the petals. */
public class GrandChorusAI extends RslSystemAI {
    @Override
    protected boolean decide(Vector2f missileDangerDir, Vector2f collisionDangerDir, ShipAPI target) {
        return RslUtil.nearestEnemy(ship, ship.getLocation(), GrandChorusStats.RANGE + 200f, false, null) != null;
    }
}
