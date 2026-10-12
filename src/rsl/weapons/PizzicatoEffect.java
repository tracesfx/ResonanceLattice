package rsl.weapons;

import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.DamagingProjectileAPI;
import com.fs.starfarer.api.combat.OnFireEffectPlugin;
import com.fs.starfarer.api.combat.WeaponAPI;
import org.lwjgl.util.vector.Vector2f;
import rsl.combat.RslUtil;

/** Pizzicato Lancet: a shot fired after {@link #REST} seconds of silence is plucked for double damage. */
public class PizzicatoEffect implements OnFireEffectPlugin {
    public static final float REST = 2.5f;
    public static final float PLUCK = 2f;

    @Override
    public void onFire(DamagingProjectileAPI proj, WeaponAPI weapon, CombatEngineAPI engine) {
        float now = RslUtil.now();
        float last = weapon.getCustom() instanceof Float ? (Float) weapon.getCustom() : -100f;
        weapon.setCustom(now);
        if (now - last < REST) return;
        proj.setDamageAmount(proj.getDamageAmount() * PLUCK);
        Vector2f vel = weapon.getShip() != null ? weapon.getShip().getVelocity() : new Vector2f();
        engine.addHitParticle(proj.getLocation(), vel, 40f, 1f, 0.15f, RslUtil.WHITE);
    }
}
