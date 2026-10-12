package rsl.weapons;

import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.CombatEntityAPI;
import com.fs.starfarer.api.combat.DamagingProjectileAPI;
import com.fs.starfarer.api.combat.OnHitEffectPlugin;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.listeners.ApplyDamageResultAPI;
import org.lwjgl.util.vector.Vector2f;
import rsl.combat.RslCombatPlugin;

/** Crystal Flechette: shards that hit armor or hull keep cutting (damage over time, fixed to the impact point). */
public class FlechetteOnHit implements OnHitEffectPlugin {
    public static final float DOT = 45f;
    public static final float DURATION = 3f;

    @Override
    public void onHit(DamagingProjectileAPI proj, CombatEntityAPI target, Vector2f point, boolean shieldHit,
                      ApplyDamageResultAPI result, CombatEngineAPI engine) {
        RailFx.impact(proj, target, point, shieldHit, engine);
        if (shieldHit || !(target instanceof ShipAPI) || ((ShipAPI) target).isFighter()) return;
        RslCombatPlugin p = RslCombatPlugin.get();
        if (p != null) p.addDot((ShipAPI) target, proj.getSource(), point, DOT, DURATION);
    }
}
