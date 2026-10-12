package rsl.systems;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.combat.ArmorGridAPI;
import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.DamageType;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.impl.combat.BaseShipSystemScript;
import org.lwjgl.util.vector.Vector2f;
import rsl.combat.LatticeData;
import rsl.combat.RslUtil;

import java.util.List;

/**
 * Tremolo, toggle. Turning it on drops a node (position, hull and the armor grid are recorded). Turning it off within
 * {@link #WINDOW} seconds snaps the ship back to the node and restores {@link #RESTORE} of the hull and armor lost
 * since; if the window runs out the node simply collapses (no snap). Overtone: the departure point detonates.
 */
public class StandingWaveStats extends BaseShipSystemScript {
    public static final float WINDOW = 8f;
    public static final float RESTORE = 0.4f;
    public static final float BLAST_RADIUS = 260f;
    public static final float BLAST_DAMAGE = 400f;
    public static final float BLAST_EMP = 600f;

    @Override
    public void apply(MutableShipStatsAPI stats, String id, State state, float effectLevel) {
        ShipAPI ship = SystemUtil.ship(stats);
        if (ship == null || state == State.COOLDOWN || state == State.IDLE) return;
        LatticeData d = LatticeData.get(ship);
        CombatEngineAPI engine = Global.getCombatEngine();
        float now = RslUtil.now();
        if (d.waveStart < 0f) {
            d.waveStart = now;
            d.waveTimedOut = false;
            d.waveNode = new Vector2f(ship.getLocation());
            d.waveHull = ship.getHitpoints();
            float[][] g = ship.getArmorGrid().getGrid();
            d.waveArmor = new float[g.length][];
            for (int i = 0; i < g.length; i++) d.waveArmor[i] = g[i].clone();
            d.overtoneThisUse = false;
        }
        if (!engine.isPaused() && Math.random() < 0.4) {
            Vector2f vel = new Vector2f((float) Math.random() * 60f - 30f, (float) Math.random() * 60f - 30f);
            engine.addHitParticle(d.waveNode, vel, 30f + 40f * (float) Math.random(), 0.8f, 0.4f, RslUtil.VIOLET);
        }
        if (!d.waveTimedOut && now - d.waveStart > WINDOW && ship.getSystem() != null) {
            d.waveTimedOut = true;
            ship.getSystem().deactivate();
        }
    }

    @Override
    public void unapply(MutableShipStatsAPI stats, String id) {
        ShipAPI ship = SystemUtil.ship(stats);
        if (ship == null) return;
        LatticeData d = LatticeData.get(ship);
        if (d.waveStart >= 0f && !d.waveTimedOut && d.waveNode != null && RslUtil.alive(ship)) snap(ship, d);
        d.waveStart = -1f;
        d.waveNode = null;
        d.waveArmor = null;
    }

    private static void snap(ShipAPI ship, LatticeData d) {
        CombatEngineAPI engine = Global.getCombatEngine();
        Vector2f from = new Vector2f(ship.getLocation());
        engine.spawnEmpArcVisual(from, null, d.waveNode, null, 14f, RslUtil.VIOLET, RslUtil.WHITE);
        engine.addSmoothParticle(from, new Vector2f(), ship.getCollisionRadius() * 2f, 0.8f, 0.5f, RslUtil.VIOLET);
        ship.getLocation().set(d.waveNode);
        ship.getVelocity().scale(0.2f);
        float hp = ship.getHitpoints();
        if (hp < d.waveHull) ship.setHitpoints(Math.min(ship.getMaxHitpoints(), hp + (d.waveHull - hp) * RESTORE));
        ArmorGridAPI grid = ship.getArmorGrid();
        float[][] g = grid.getGrid();
        if (d.waveArmor != null && d.waveArmor.length == g.length) {
            for (int x = 0; x < g.length; x++) {
                for (int y = 0; y < g[x].length && y < d.waveArmor[x].length; y++) {
                    float was = d.waveArmor[x][y];
                    if (g[x][y] < was) grid.setArmorValue(x, y, g[x][y] + (was - g[x][y]) * RESTORE);
                }
            }
            ship.syncWithArmorGridState();
        }
        engine.addSmoothParticle(d.waveNode, new Vector2f(), ship.getCollisionRadius() * 2.5f, 1f, 0.4f, RslUtil.TEAL);
        if (LatticeData.consumeOvertone(ship)) detonate(ship, from);
    }

    private static void detonate(ShipAPI ship, Vector2f at) {
        CombatEngineAPI engine = Global.getCombatEngine();
        engine.spawnExplosion(at, new Vector2f(), RslUtil.VIOLET, BLAST_RADIUS, 0.6f);
        List<ShipAPI> ships = engine.getShips();
        for (int i = 0; i < ships.size(); i++) {
            ShipAPI s = ships.get(i);
            if (s.isHulk() || !RslUtil.isEnemy(ship, s)) continue;
            float dx = s.getLocation().x - at.x, dy = s.getLocation().y - at.y;
            float r = BLAST_RADIUS + s.getCollisionRadius();
            if (dx * dx + dy * dy > r * r) continue;
            Vector2f p = SystemUtil.hitPoint(at, s);
            engine.applyDamage(s, p, BLAST_DAMAGE, DamageType.ENERGY, BLAST_EMP, false, false, ship, true);
        }
    }

    @Override
    public StatusData getStatusData(int index, State state, float effectLevel) {
        return index == 0 ? new StatusData("standing wave node held - use again to snap back", false) : null;
    }
}
