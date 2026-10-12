package rsl.systems;

import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.DamageType;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import org.lazywizard.lazylib.CollisionUtils;
import org.lwjgl.util.vector.Vector2f;
import rsl.combat.RslUtil;

import java.awt.Color;
import java.util.List;

/** Helpers shared by the ship system scripts. */
final class SystemUtil {
    private SystemUtil() {
    }

    static ShipAPI ship(MutableShipStatsAPI stats) {
        return stats.getEntity() instanceof ShipAPI ? (ShipAPI) stats.getEntity() : null;
    }

    /** Nearest point of a ship's bounds on the line from {@code from} to its centre (falls back to the centre). */
    static Vector2f hitPoint(Vector2f from, ShipAPI target) {
        Vector2f p = CollisionUtils.getCollisionPoint(from, target.getLocation(), target);
        return p != null ? p : new Vector2f(target.getLocation());
    }

    /** A resonant lance: a thick arc visual plus the damage, applied at the bounds. */
    static void lance(CombatEngineAPI engine, ShipAPI source, Vector2f from, ShipAPI target, float damage, float emp,
                      float thickness, Color fringe) {
        Vector2f p = hitPoint(from, target);
        engine.spawnEmpArcVisual(from, source, p, target, thickness, fringe, RslUtil.WHITE);
        engine.applyDamage(target, p, damage, DamageType.ENERGY, emp, false, false, source, true);
        engine.addHitParticle(p, target.getVelocity(), thickness * 4f, 1f, 0.3f, fringe);
    }

    /** Enemy (non-fighter) ships whose collision circle touches the segment a-b. */
    static boolean touches(ShipAPI s, Vector2f a, Vector2f b, float radiusMult) {
        return CollisionUtils.getCollides(a, b, s.getLocation(), s.getCollisionRadius() * radiusMult);
    }

    static int countEnemiesNear(CombatEngineAPI engine, ShipAPI ship, float range) {
        int n = 0;
        List<ShipAPI> ships = engine.getShips();
        float r2 = range * range;
        for (int i = 0; i < ships.size(); i++) {
            ShipAPI s = ships.get(i);
            if (s.isHulk() || s.isFighter() || !RslUtil.isEnemy(ship, s)) continue;
            float dx = s.getLocation().x - ship.getLocation().x, dy = s.getLocation().y - ship.getLocation().y;
            if (dx * dx + dy * dy < r2) n++;
        }
        return n;
    }
}
