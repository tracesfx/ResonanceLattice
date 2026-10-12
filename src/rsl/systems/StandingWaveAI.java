package rsl.systems;

import com.fs.starfarer.api.combat.ShipAPI;
import org.lwjgl.util.vector.Vector2f;
import rsl.combat.LatticeData;
import rsl.combat.RslUtil;


/** Tremolo: drop a node when it engages healthy; snap back once it has taken real damage or is flux-locked. */
public class StandingWaveAI extends RslSystemAI {
    @Override
    protected boolean decide(Vector2f missileDangerDir, Vector2f collisionDangerDir, ShipAPI target) {
        LatticeData d = LatticeData.get(ship);
        if (system.isOn()) {
            if (d.waveStart < 0f) return false;
            float lost = (d.waveHull - ship.getHitpoints()) / ship.getMaxHitpoints();
            float held = RslUtil.now() - d.waveStart;
            return lost > 0.10f || ship.getFluxLevel() > 0.85f || (held > 6.5f && lost > 0.03f);
        }
        ShipAPI t = target != null ? target : RslUtil.nearestEnemy(ship, ship.getLocation(), 1400f, false, null);
        return t != null && dist(t) < 1100f && ship.getHullLevel() > 0.4f && ship.getFluxLevel() < 0.6f;
    }
}
