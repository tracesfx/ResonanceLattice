package rsl.weapons;

import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.CombatEntityAPI;
import com.fs.starfarer.api.combat.DamagingProjectileAPI;
import com.fs.starfarer.api.combat.OnHitEffectPlugin;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.listeners.ApplyDamageResultAPI;
import org.lwjgl.util.vector.Vector2f;
import rsl.RslIds;
import rsl.combat.RslUtil;

/**
 * Harmonic Driver: a bolt that lands on hull or armor (not shields, not fighters) continues out of the far side of the
 * ship with {@link #KEEP} of its damage. A continued bolt does not pierce again.
 */
public class PierceOnHit implements OnHitEffectPlugin {
    public static final float KEEP = 0.5f;

    @Override
    public void onHit(DamagingProjectileAPI proj, CombatEntityAPI target, Vector2f point, boolean shieldHit,
                      ApplyDamageResultAPI result, CombatEngineAPI engine) {
        RailFx.impact(proj, target, point, shieldHit, engine);
        if (shieldHit || !(target instanceof ShipAPI) || ((ShipAPI) target).isFighter()) return;
        if (proj.getCustomData().containsKey(RslIds.KEY_PIERCED) || proj.getWeapon() == null) return;
        continueThrough(proj, target, point, KEEP, engine);
    }

    /** Spawns the continuation of {@code proj} beyond {@code target}; shared with the Sforzando's Cascade. */
    public static DamagingProjectileAPI continueThrough(DamagingProjectileAPI proj, CombatEntityAPI target,
                                                       Vector2f point, float keep, CombatEngineAPI engine) {
        if (proj.getWeapon() == null) return null;
        Vector2f exit = RslUtil.exitPoint(target, point, proj.getFacing());
        Object o = engine.spawnProjectile(proj.getSource(), proj.getWeapon(), proj.getWeapon().getId(), exit,
                proj.getFacing(), null);
        if (!(o instanceof DamagingProjectileAPI)) return null;
        DamagingProjectileAPI p = (DamagingProjectileAPI) o;
        p.setDamageAmount(proj.getDamageAmount() * keep);
        p.setCustomData(RslIds.KEY_PIERCED, Boolean.TRUE);
        RailFx.inheritRange(proj, p);
        p.addDamagedAlready(target);
        engine.addHitParticle(exit, new Vector2f(), 30f, 0.6f, 0.15f, RslUtil.TEAL);
        return p;
    }
}
