package rsl.systems;

import com.fs.starfarer.api.combat.ShipAPI;
import org.lwjgl.util.vector.Vector2f;
import rsl.combat.RslUtil;


/**
 * Virtuoso: dash to evade when threatened, to close distance when the target is just beyond lance range and the ship
 * is already heading for it, and to escape a flux spike. Conservative with CR (never below 45%).
 */
public class GlissandoAI extends RslSystemAI {
    @Override
    protected boolean decide(Vector2f missileDangerDir, Vector2f collisionDangerDir, ShipAPI target) {
        if (ship.getCurrentCR() < 0.45f || system.getAmmo() < 1) return false;
        if (missileDangerDir != null && ship.getFluxLevel() > 0.3f) return true;
        ShipAPI t = target != null ? target : RslUtil.nearestEnemy(ship, ship.getLocation(), 2000f, false, null);
        if (t == null) return false;
        float d = dist(t);
        if (ship.getFluxLevel() > 0.85f && d < 900f) return true;
        if (d > 950f && d < 1700f && ship.getVelocity().length() > ship.getMaxSpeed() * 0.6f) {
            Vector2f to = Vector2f.sub(t.getLocation(), ship.getLocation(), null);
            float dot = Vector2f.dot(to, ship.getVelocity()) / (to.length() * ship.getVelocity().length() + 1f);
            return dot > 0.9f && ship.getFluxLevel() < 0.6f;
        }
        return false;
    }
}
