package rsl.systems;

import com.fs.starfarer.api.combat.DamagingProjectileAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import org.lwjgl.util.vector.Vector2f;

import java.util.List;


/** Halo: raise the still zone when enough enemy fire is inbound. */
public class StillwaterHaloAI extends RslSystemAI {
    @Override
    protected boolean decide(Vector2f missileDangerDir, Vector2f collisionDangerDir, ShipAPI target) {
        float r2 = StillwaterHaloStats.RADIUS * StillwaterHaloStats.RADIUS;
        float dmg = 0f;
        int missiles = 0;
        List<DamagingProjectileAPI> projs = engine.getProjectiles();
        for (int i = 0; i < projs.size(); i++) {
            DamagingProjectileAPI p = projs.get(i);
            if (p.getOwner() == ship.getOwner()) continue;
            float dx = p.getLocation().x - ship.getLocation().x, dy = p.getLocation().y - ship.getLocation().y;
            if (dx * dx + dy * dy > r2) continue;
            dmg += p.getDamageAmount();
            if (p instanceof com.fs.starfarer.api.combat.MissileAPI) missiles++;
        }
        return missiles >= 3 || dmg > 2500f || (missileDangerDir != null && dmg > 1200f);
    }
}
