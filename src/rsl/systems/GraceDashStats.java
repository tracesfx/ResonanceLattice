package rsl.systems;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.combat.BaseEveryFrameCombatPlugin;
import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.DamageType;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.impl.combat.BaseShipSystemScript;
import com.fs.starfarer.api.input.InputEventAPI;
import org.lwjgl.util.vector.Vector2f;
import rsl.combat.LatticeData;
import rsl.combat.RslUtil;

import java.util.ArrayList;
import java.util.List;

/**
 * Staccato: a short dash (vanilla Plasma Burn numbers, ENGINE_MOD + BURN_DRIVE AI). Overtone: the path becomes a
 * resonant wake for 3 seconds that arcs EMP into enemies passing through it.
 */
public class GraceDashStats extends BaseShipSystemScript {
    public static final float SPEED = 500f;
    public static final float ACCEL = 1100f;

    @Override
    public void apply(MutableShipStatsAPI stats, String id, State state, float effectLevel) {
        ShipAPI ship = SystemUtil.ship(stats);
        if (ship == null || state == State.COOLDOWN || state == State.IDLE) return;
        LatticeData d = LatticeData.get(ship);
        if (!d.systemFired) {
            d.systemFired = true;
            d.sysObj = null;
            if (LatticeData.consumeOvertone(ship)) {
                Wake w = new Wake(ship);
                d.sysObj = w;
                Global.getCombatEngine().addPlugin(w);
            }
        }
        if (d.sysObj instanceof Wake) ((Wake) d.sysObj).record(ship.getLocation());
        if (state == State.OUT) {
            stats.getMaxSpeed().unmodify(id);
        } else {
            stats.getMaxSpeed().modifyFlat(id, SPEED * effectLevel);
            stats.getAcceleration().modifyFlat(id, ACCEL * effectLevel);
        }
    }

    @Override
    public void unapply(MutableShipStatsAPI stats, String id) {
        stats.getMaxSpeed().unmodify(id);
        stats.getAcceleration().unmodify(id);
        ShipAPI ship = SystemUtil.ship(stats);
        if (ship != null) {
            LatticeData d = LatticeData.get(ship);
            d.systemFired = false;
            d.sysObj = null;
        }
    }

    @Override
    public StatusData getStatusData(int index, State state, float effectLevel) {
        return index == 0 ? new StatusData("grace dash", false) : null;
    }

    /** The Overtone wake: path points that arc EMP into enemies nearby. */
    static class Wake extends BaseEveryFrameCombatPlugin {
        static final float LIFE = 3f, RADIUS = 110f, EMP = 250f;
        final ShipAPI ship;
        final List<Vector2f> pts = new ArrayList<>();
        float t, tick, sample;

        Wake(ShipAPI ship) {
            this.ship = ship;
        }

        void record(Vector2f p) {
            if (pts.size() < 40 && (pts.isEmpty() || Vector2f.sub(p, pts.get(pts.size() - 1), null).lengthSquared() > 1600f)) {
                pts.add(new Vector2f(p));
            }
        }

        @Override
        public void advance(float amount, List<InputEventAPI> events) {
            CombatEngineAPI engine = Global.getCombatEngine();
            if (engine.isPaused()) return;
            t += amount;
            tick += amount;
            sample += amount;
            if (t > LIFE) {
                engine.removePlugin(this);
                return;
            }
            if (sample > 0.1f && !pts.isEmpty()) {
                sample = 0f;
                Vector2f p = pts.get((int) (Math.random() * pts.size()));
                engine.addHitParticle(p, new Vector2f(), 40f, 0.7f, 0.3f, RslUtil.TEAL);
            }
            if (tick < 0.4f) return;
            tick = 0f;
            List<ShipAPI> ships = engine.getShips();
            for (int i = 0; i < ships.size(); i++) {
                ShipAPI s = ships.get(i);
                if (s.isHulk() || !RslUtil.isEnemy(ship, s)) continue;
                for (int k = 0; k < pts.size(); k++) {
                    Vector2f p = pts.get(k);
                    float dx = s.getLocation().x - p.x, dy = s.getLocation().y - p.y;
                    float r = RADIUS + s.getCollisionRadius() * 0.5f;
                    if (dx * dx + dy * dy < r * r) {
                        engine.spawnEmpArc(ship, p, null, s, DamageType.ENERGY, 40f, EMP, 600f,
                                "system_emp_emitter_impact", 5f, RslUtil.TEAL, RslUtil.WHITE);
                        break;
                    }
                }
            }
        }
    }
}
