package rsl.weapons;

import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.DamagingProjectileAPI;
import com.fs.starfarer.api.combat.OnFireEffectPlugin;
import com.fs.starfarer.api.combat.WeaponAPI;
import rsl.RslIds;

/** Chime Repeater: every 4th bolt is swapped for a chime (the hidden rsl_chime_bell projectile: EMP + arc). */
public class ChimeRepeaterEffect implements OnFireEffectPlugin {
    public static final int EVERY = 4;

    @Override
    public void onFire(DamagingProjectileAPI proj, WeaponAPI weapon, CombatEngineAPI engine) {
        int n = weapon.getCustom() instanceof Integer ? (Integer) weapon.getCustom() : 0;
        n++;
        if (n >= EVERY && weapon.getShip() != null) {
            n = 0;
            engine.spawnProjectile(weapon.getShip(), weapon, RslIds.WEAPON_CHIME_BELL, proj.getLocation(),
                    proj.getFacing(), weapon.getShip().getVelocity());
            engine.removeEntity(proj);
        }
        weapon.setCustom(n);
    }
}
