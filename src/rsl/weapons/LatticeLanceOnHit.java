package rsl.weapons;

import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.CombatEntityAPI;
import com.fs.starfarer.api.combat.DamageType;
import com.fs.starfarer.api.combat.DamagingProjectileAPI;
import com.fs.starfarer.api.combat.OnHitEffectPlugin;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.WeaponAPI;
import com.fs.starfarer.api.combat.listeners.ApplyDamageResultAPI;
import org.lwjgl.util.vector.Vector2f;
import rsl.combat.RslUtil;

import java.util.HashMap;
import java.util.Map;

/**
 * Lattice Lance (rail): consecutive hits by the same lance on the same ship tune it in. Each hit after the first adds
 * {@link #STEP} bonus damage, up to {@link #MAX_BONUS}; switching targets or a gap of more than {@link #GAP} seconds
 * resets it. State is per weapon, kept in the combat engine's custom data (never in a static).
 */
public class LatticeLanceOnHit implements OnHitEffectPlugin {
    public static final float STEP = 0.15f;
    public static final float MAX_BONUS = 0.75f;
    public static final float GAP = 2.5f;
    private static final String KEY = "rsl_lance_tuning";

    static final class Tuning {
        CombatEntityAPI target;
        int hits;
        float last;
    }

    @Override
    @SuppressWarnings("unchecked")
    public void onHit(DamagingProjectileAPI proj, CombatEntityAPI target, Vector2f point, boolean shieldHit,
                      ApplyDamageResultAPI result, CombatEngineAPI engine) {
        RailFx.impact(proj, target, point, shieldHit, engine);
        WeaponAPI w = proj.getWeapon();
        if (w == null || !(target instanceof ShipAPI) || ((ShipAPI) target).isFighter()) return;
        Object o = engine.getCustomData().get(KEY);
        if (!(o instanceof Map)) {
            o = new HashMap<WeaponAPI, Tuning>();
            engine.getCustomData().put(KEY, o);
        }
        Map<WeaponAPI, Tuning> map = (Map<WeaponAPI, Tuning>) o;
        Tuning t = map.get(w);
        if (t == null) {
            t = new Tuning();
            map.put(w, t);
        }
        float now = RslUtil.now();
        if (t.target != target || now - t.last > GAP) {
            t.target = target;
            t.hits = 0;
        }
        t.last = now;
        float bonus = Math.min(MAX_BONUS, STEP * t.hits);
        t.hits++;
        if (bonus <= 0f || ((ShipAPI) target).isHulk()) return;
        engine.applyDamage(target, point, proj.getDamageAmount() * bonus, DamageType.ENERGY, 0f, false, false,
                proj.getSource(), false);
        engine.addHitParticle(point, target.getVelocity(), 40f + 80f * bonus, 1f, 0.15f, RslUtil.TEAL);
    }
}
