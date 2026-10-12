package rsl.weapons;

import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.CombatEntityAPI;
import com.fs.starfarer.api.combat.DamageType;
import com.fs.starfarer.api.combat.DamagingProjectileAPI;
import com.fs.starfarer.api.combat.MissileAPI;
import com.fs.starfarer.api.combat.OnHitEffectPlugin;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.listeners.ApplyDamageResultAPI;
import org.lwjgl.util.vector.Vector2f;
import rsl.combat.RslUtil;

import java.util.List;

/** The chime rings on: an EMP arc to the nearest other enemy missile or fighter within range of the impact. */
public class ChimeBellOnHit implements OnHitEffectPlugin {
    public static final float RANGE = 300f;

    @Override
    public void onHit(DamagingProjectileAPI proj, CombatEntityAPI target, Vector2f point, boolean shieldHit,
                      ApplyDamageResultAPI result, CombatEngineAPI engine) {
        ShipAPI src = proj.getSource();
        if (src == null) return;
        CombatEntityAPI best = null;
        float bestD = RANGE * RANGE;
        List<MissileAPI> ms = engine.getMissiles();
        for (int i = 0; i < ms.size(); i++) {
            MissileAPI m = ms.get(i);
            if (m == target || m.getOwner() == src.getOwner()) continue;
            float d = Vector2f.sub(m.getLocation(), point, null).lengthSquared();
            if (d < bestD) {
                bestD = d;
                best = m;
            }
        }
        if (best == null) best = nearestFighter(engine, src, point, target);
        if (best == null) return;
        engine.spawnEmpArc(src, point, null, best, DamageType.ENERGY, 60f, 150f, RANGE + 100f,
                "system_emp_emitter_impact", 5f, RslUtil.VIOLET, RslUtil.WHITE);
    }

    private static ShipAPI nearestFighter(CombatEngineAPI engine, ShipAPI src, Vector2f p, CombatEntityAPI not) {
        ShipAPI best = null;
        float bestD = RANGE * RANGE;
        List<ShipAPI> ships = engine.getShips();
        for (int i = 0; i < ships.size(); i++) {
            ShipAPI s = ships.get(i);
            if (s == not || !s.isFighter() || s.isHulk() || !RslUtil.isEnemy(src, s)) continue;
            float d = Vector2f.sub(s.getLocation(), p, null).lengthSquared();
            if (d < bestD) {
                bestD = d;
                best = s;
            }
        }
        return best;
    }
}
