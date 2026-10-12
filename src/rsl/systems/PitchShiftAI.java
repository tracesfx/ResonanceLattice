package rsl.systems;

import com.fs.starfarer.api.combat.ShipAPI;
import org.lwjgl.util.vector.Vector2f;
import rsl.combat.LatticeData;
import rsl.combat.RslUtil;


/** Grace Note: Discord when it can afford to drop shields near a target, Harmonic when flux or danger rises. */
public class PitchShiftAI extends RslSystemAI {
    @Override
    protected boolean decide(Vector2f missileDangerDir, Vector2f collisionDangerDir, ShipAPI target) {
        ShipAPI t = target != null ? target : RslUtil.nearestEnemy(ship, ship.getLocation(), 1400f, false, null);
        boolean wantDiscord = t != null && dist(t) < 1000f && ship.getFluxLevel() < 0.45f && ship.getHullLevel() > 0.35f
                && missileDangerDir == null;
        boolean wantHarmonic = t == null || ship.getFluxLevel() > 0.7f || ship.getHullLevel() < 0.3f
                || missileDangerDir != null;
        boolean discord = LatticeData.get(ship).discord;
        return discord ? wantHarmonic : wantDiscord;
    }
}
