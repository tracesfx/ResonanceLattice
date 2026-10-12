package rsl.systems;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.ShipSystemAPI;
import com.fs.starfarer.api.combat.WeaponAPI;
import com.fs.starfarer.api.impl.combat.BaseShipSystemScript;
import org.lwjgl.util.vector.Vector2f;
import rsl.RslIds;
import rsl.combat.LatticeData;
import rsl.combat.RslUtil;

import java.util.List;

/**
 * Conductor: a 1.5 s charge (the prong blades flex, DecoVaneEffect), then a resonant beam from the spinal muzzle
 * into the target; the target is marked and takes +20% damage from Lattice ships (LatticeDealtModifier).
 * Overtone: the beam chains to a second enemy, which is marked too.
 */
public class SympatheticStrikeStats extends BaseShipSystemScript {
    public static final float RANGE = 2000f;
    public static final float CHAIN_RANGE = 1000f;
    public static final float DAMAGE = 800f;
    public static final float EMP = 400f;
    public static final float MARK_TIME = 8f;

    public static ShipAPI pickTarget(ShipAPI ship) {
        ShipAPI t = ship.getShipTarget();
        if (t != null && !t.isHulk() && RslUtil.isEnemy(ship, t) && !t.isFighter()
                && Vector2f.sub(t.getLocation(), ship.getLocation(), null).length() <= RANGE) {
            return t;
        }
        return RslUtil.nearestEnemy(ship, ship.getLocation(), RANGE, false, null);
    }

    static Vector2f muzzle(ShipAPI ship) {
        List<WeaponAPI> ws = ship.getAllWeapons();
        for (int i = 0; i < ws.size(); i++) {
            if (RslIds.WEAPON_HARMONIC_SPINAL.equals(ws.get(i).getId())) return ws.get(i).getFirePoint(0);
        }
        return ship.getLocation();
    }

    @Override
    public boolean isUsable(ShipSystemAPI system, ShipAPI ship) {
        return pickTarget(ship) != null;
    }

    @Override
    public String getInfoText(ShipSystemAPI system, ShipAPI ship) {
        if (system.isActive()) return null;
        return pickTarget(ship) == null ? "NO TARGET IN RANGE" : "READY";
    }

    @Override
    public void apply(MutableShipStatsAPI stats, String id, State state, float effectLevel) {
        ShipAPI ship = SystemUtil.ship(stats);
        if (ship == null || state == State.COOLDOWN || state == State.IDLE) return;
        LatticeData d = LatticeData.get(ship);
        CombatEngineAPI engine = Global.getCombatEngine();
        Vector2f from = muzzle(ship);
        if (state == State.IN && !engine.isPaused() && Math.random() < 0.3) {
            Vector2f a = new Vector2f(from.x + (float) Math.random() * 40f - 20f, from.y + (float) Math.random() * 40f - 20f);
            engine.spawnEmpArcVisual(from, ship, a, ship, 3f + 6f * effectLevel, RslUtil.TEAL, RslUtil.WHITE);
        }
        if (state != State.ACTIVE || d.systemFired) return;
        d.systemFired = true;
        ShipAPI t = pickTarget(ship);
        if (t == null) return;
        boolean overtone = LatticeData.consumeOvertone(ship);
        SystemUtil.lance(engine, ship, from, t, DAMAGE, EMP, 40f, RslUtil.TEAL);
        mark(t);
        if (overtone) {
            ShipAPI t2 = RslUtil.nearestEnemy(ship, t.getLocation(), CHAIN_RANGE, false, t);
            if (t2 != null) {
                SystemUtil.lance(engine, ship, t.getLocation(), t2, DAMAGE * 0.6f, EMP, 28f, RslUtil.VIOLET);
                mark(t2);
            }
        }
    }

    static void mark(ShipAPI t) {
        t.setCustomData(RslIds.KEY_MARK_UNTIL, RslUtil.now() + MARK_TIME);
        Global.getCombatEngine().addFloatingText(t.getLocation(), "Marked", 26f, RslUtil.TEAL, t, 0.5f, 1f);
    }

    @Override
    public void unapply(MutableShipStatsAPI stats, String id) {
        ShipAPI ship = SystemUtil.ship(stats);
        if (ship != null) LatticeData.get(ship).systemFired = false;
    }

    @Override
    public StatusData getStatusData(int index, State state, float effectLevel) {
        return index == 0 && state == State.IN ? new StatusData("charging sympathetic strike", false) : null;
    }
}
