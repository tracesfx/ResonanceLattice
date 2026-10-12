package rsl.systems;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.MissileAPI;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.impl.combat.BaseShipSystemScript;
import org.lwjgl.util.vector.Vector2f;
import rsl.combat.LatticeData;
import rsl.combat.RslUtil;

import java.util.List;

/**
 * Cantor Array (core): every living petal (and the core) discharges one synchronized lance into the nearest enemy
 * ship. Overtone: a harmonic ring flames out enemy fighters and missiles around the station.
 */
public class GrandChorusStats extends BaseShipSystemScript {
    public static final float RANGE = 1600f;
    public static final float DAMAGE = 600f;
    public static final float RING = 1300f;

    @Override
    public void apply(MutableShipStatsAPI stats, String id, State state, float effectLevel) {
        ShipAPI ship = SystemUtil.ship(stats);
        if (ship == null || state == State.COOLDOWN || state == State.IDLE) return;
        LatticeData d = LatticeData.get(ship);
        CombatEngineAPI engine = Global.getCombatEngine();
        if (state != State.ACTIVE || d.systemFired) return;
        d.systemFired = true;
        fire(engine, ship, ship);
        if (ship.isShipWithModules()) {
            List<ShipAPI> mods = ship.getChildModulesCopy();
            for (int i = 0; i < mods.size(); i++) if (RslUtil.alive(mods.get(i))) fire(engine, ship, mods.get(i));
        }
        if (LatticeData.consumeOvertone(ship)) ring(engine, ship);
    }

    private static void fire(CombatEngineAPI engine, ShipAPI owner, ShipAPI from) {
        ShipAPI t = RslUtil.nearestEnemy(owner, from.getLocation(), RANGE, false, null);
        if (t != null) SystemUtil.lance(engine, from, from.getLocation(), t, DAMAGE, DAMAGE * 0.5f, 30f, RslUtil.TEAL);
    }

    private static void ring(CombatEngineAPI engine, ShipAPI ship) {
        engine.addSmoothParticle(ship.getLocation(), new Vector2f(), RING * 2f, 0.5f, 0.8f, RslUtil.VIOLET);
        float r2 = RING * RING;
        List<ShipAPI> ships = engine.getShips();
        for (int i = 0; i < ships.size(); i++) {
            ShipAPI s = ships.get(i);
            if (!s.isFighter() || s.isHulk() || !RslUtil.isEnemy(ship, s)) continue;
            float dx = s.getLocation().x - ship.getLocation().x, dy = s.getLocation().y - ship.getLocation().y;
            if (dx * dx + dy * dy < r2) s.getEngineController().forceFlameout();
        }
        List<MissileAPI> ms = engine.getMissiles();
        for (int i = 0; i < ms.size(); i++) {
            MissileAPI m = ms.get(i);
            if (m.getOwner() == ship.getOwner()) continue;
            float dx = m.getLocation().x - ship.getLocation().x, dy = m.getLocation().y - ship.getLocation().y;
            if (dx * dx + dy * dy < r2) m.flameOut();
        }
    }

    @Override
    public void unapply(MutableShipStatsAPI stats, String id) {
        ShipAPI ship = SystemUtil.ship(stats);
        if (ship != null) LatticeData.get(ship).systemFired = false;
    }
}
