package rsl.combat;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.combat.BeamAPI;
import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.CombatEntityAPI;
import com.fs.starfarer.api.combat.DamagingProjectileAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.WeaponAPI;
import org.lwjgl.util.vector.Vector2f;
import rsl.RslIds;

import java.awt.Color;
import java.util.List;

/** Small shared helpers. Stateless: everything per-ship lives in {@link LatticeData}. */
public final class RslUtil {
    private RslUtil() {
    }

    public static final Color TEAL = new Color(100, 230, 220, 255);
    public static final Color TEAL_DIM = new Color(60, 190, 180, 200);
    public static final Color VIOLET = new Color(160, 120, 240, 255);
    public static final Color WHITE = new Color(235, 255, 252, 255);
    public static final Color GOLD = new Color(255, 214, 140, 255);

    public static CombatEngineAPI engine() {
        return Global.getCombatEngine();
    }

    public static float now() {
        CombatEngineAPI e = engine();
        return e == null ? 0f : e.getTotalElapsedTime(false);
    }

    /** The ship responsible for a damage source (projectile, missile, beam or the ship itself). */
    public static ShipAPI sourceShip(Object o) {
        if (o instanceof DamagingProjectileAPI) return ((DamagingProjectileAPI) o).getSource();
        if (o instanceof BeamAPI) return ((BeamAPI) o).getSource();
        if (o instanceof ShipAPI) return (ShipAPI) o;
        return null;
    }

    /** The weapon behind a damage source, or null. */
    public static WeaponAPI sourceWeapon(Object o) {
        if (o instanceof DamagingProjectileAPI) return ((DamagingProjectileAPI) o).getWeapon();
        if (o instanceof BeamAPI) return ((BeamAPI) o).getWeapon();
        return null;
    }

    public static boolean isEnergyWeaponHit(Object o) {
        WeaponAPI w = sourceWeapon(o);
        return w != null && w.getType() == WeaponAPI.WeaponType.ENERGY;
    }

    public static boolean hasMod(ShipAPI ship, String mod) {
        return ship != null && ship.getVariant() != null && ship.getVariant().hasHullMod(mod);
    }

    public static boolean isLattice(ShipAPI ship) {
        return hasMod(ship, RslIds.HULLMOD_CORE);
    }

    public static boolean alive(ShipAPI ship) {
        return ship != null && ship.isAlive() && !ship.isHulk() && engine() != null && engine().isEntityInPlay(ship);
    }

    public static boolean isEnemy(ShipAPI a, CombatEntityAPI b) {
        return a != null && b != null && b.getOwner() != a.getOwner() && b.getOwner() != 100;
    }

    /** Nearest living enemy ship (fighters included only if wanted) within range of a point, or null. */
    public static ShipAPI nearestEnemy(ShipAPI from, Vector2f point, float range, boolean fighters, ShipAPI exclude) {
        CombatEngineAPI e = engine();
        if (e == null) return null;
        ShipAPI best = null;
        float bestD = range * range;
        List<ShipAPI> ships = e.getShips();
        for (int i = 0; i < ships.size(); i++) {
            ShipAPI s = ships.get(i);
            if (s == exclude || s.isHulk() || !s.isAlive() || s.isShuttlePod() || !isEnemy(from, s)) continue;
            if (!fighters && s.isFighter()) continue;
            if (s.isPhased()) continue;
            float dx = s.getLocation().x - point.x, dy = s.getLocation().y - point.y;
            float d = dx * dx + dy * dy;
            if (d < bestD) {
                bestD = d;
                best = s;
            }
        }
        return best;
    }

    public static float sizeMult(ShipAPI s) {
        switch (s.getHullSize()) {
            case FRIGATE:
                return 0.5f;
            case DESTROYER:
                return 0.8f;
            case CRUISER:
                return 1.1f;
            case CAPITAL_SHIP:
                return 1.5f;
            default:
                return 0.5f;
        }
    }

    /** First point beyond a ship's bounds along a ray from inside it (used to continue a piercing shot). */
    public static Vector2f exitPoint(CombatEntityAPI target, Vector2f from, float facing) {
        float rad = (float) Math.toRadians(facing);
        float cx = (float) Math.cos(rad), cy = (float) Math.sin(rad);
        float max = target.getCollisionRadius() * 2.2f + 20f;
        Vector2f p = new Vector2f(from);
        for (float d = 10f; d < max; d += 10f) {
            p.set(from.x + cx * d, from.y + cy * d);
            if (!target.isPointInBounds(p)) {
                p.set(from.x + cx * (d + 12f), from.y + cy * (d + 12f));
                return p;
            }
        }
        p.set(from.x + cx * max, from.y + cy * max);
        return p;
    }

    public static Color lerp(Color a, Color b, float t, float alpha) {
        t = Math.max(0f, Math.min(1f, t));
        alpha = Math.max(0f, Math.min(1f, alpha));
        return new Color((int) (a.getRed() + (b.getRed() - a.getRed()) * t),
                (int) (a.getGreen() + (b.getGreen() - a.getGreen()) * t),
                (int) (a.getBlue() + (b.getBlue() - a.getBlue()) * t), (int) (255 * alpha));
    }
}
