package rsl.weapons;

import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.CombatEntityAPI;
import com.fs.starfarer.api.combat.DamagingProjectileAPI;
import com.fs.starfarer.api.combat.OnHitEffectPlugin;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.listeners.ApplyDamageResultAPI;
import org.lwjgl.util.vector.Vector2f;

/**
 * Sostenuto Rail: a held note on a shield. Each slug that hits a shield adds another {@link #EXTRA_FLUX} of the flux
 * it caused, as hard flux.
 */
public class SostenutoOnHit implements OnHitEffectPlugin {
    public static final float EXTRA_FLUX = 0.35f;

    @Override
    public void onHit(DamagingProjectileAPI proj, CombatEntityAPI target, Vector2f point, boolean shieldHit,
                      ApplyDamageResultAPI result, CombatEngineAPI engine) {
        RailFx.impact(proj, target, point, shieldHit, engine);
        if (!shieldHit || !(target instanceof ShipAPI) || result == null) return;
        ShipAPI s = (ShipAPI) target;
        if (s.getShield() == null) return;
        float flux = result.getDamageToShields() * s.getShield().getFluxPerPointOfDamage() * EXTRA_FLUX;
        if (flux > 0f) s.getFluxTracker().increaseFlux(flux, true);
    }
}
