package rsl.weapons;

import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.CombatEntityAPI;
import com.fs.starfarer.api.combat.DamageType;
import com.fs.starfarer.api.combat.DamagingProjectileAPI;
import com.fs.starfarer.api.combat.OnHitEffectPlugin;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.listeners.ApplyDamageResultAPI;
import org.lwjgl.util.vector.Vector2f;
import rsl.RslIds;
import rsl.combat.RslUtil;

import java.util.List;

/** Resonance Bloom: on impact, a ring of {@link #SHARDS} crystal fragments and EMP arcs into up to {@link #ARCS} enemies. */
public class BloomOnHit implements OnHitEffectPlugin {
    public static final int SHARDS = 16;
    public static final int ARCS = 4;
    public static final float ARC_RANGE = 500f;

    @Override
    public void onHit(DamagingProjectileAPI proj, CombatEntityAPI target, Vector2f point, boolean shieldHit,
                      ApplyDamageResultAPI result, CombatEngineAPI engine) {
        ShipAPI src = proj.getSource();
        engine.spawnExplosion(point, new Vector2f(), RslUtil.VIOLET, 220f, 0.8f);
        engine.addSmoothParticle(point, new Vector2f(), 400f, 0.8f, 0.5f, RslUtil.TEAL);
        float off = target != null ? target.getCollisionRadius() * 0.25f : 10f;
        for (int i = 0; i < SHARDS; i++) {
            float a = proj.getFacing() + 360f * i / SHARDS;
            double r = Math.toRadians(a);
            Vector2f p = new Vector2f(point.x + (float) Math.cos(r) * off, point.y + (float) Math.sin(r) * off);
            engine.spawnProjectile(src, null, RslIds.WEAPON_BLOOM_SHARD, p, a, null);
        }
        if (src == null) return;
        int arcs = 0;
        List<ShipAPI> ships = engine.getShips();
        for (int i = 0; i < ships.size() && arcs < ARCS; i++) {
            ShipAPI s = ships.get(i);
            if (s.isHulk() || !RslUtil.isEnemy(src, s)) continue;
            if (Vector2f.sub(s.getLocation(), point, null).length() > ARC_RANGE + s.getCollisionRadius()) continue;
            engine.spawnEmpArc(src, point, null, s, DamageType.ENERGY, 100f, 400f, ARC_RANGE + 300f,
                    "system_emp_emitter_impact", 8f, RslUtil.VIOLET, RslUtil.WHITE);
            arcs++;
        }
    }
}
