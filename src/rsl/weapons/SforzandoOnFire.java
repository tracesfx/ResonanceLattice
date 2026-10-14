package rsl.weapons;

import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.DamagingProjectileAPI;
import com.fs.starfarer.api.combat.OnFireEffectPlugin;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.WeaponAPI;
import rsl.RslIds;
import rsl.combat.LatticeData;

/**
 * The Virtuoso's colour scheme on its signature guns (user, 2026-10-13: teal normally, white in Bravura). A projectile's
 * colours come from its spec, so in Bravura each fresh teal slug is replaced by the white twin's
 * ({@link RslIds#WEAPON_SFORZANDO_BRAVURA}): spawned through this weapon (so on-hit effects still see the real lance),
 * with the original's damage, and its flight held to the lance's real range by {@link RailFx}.
 */
public class SforzandoOnFire implements OnFireEffectPlugin {

    @Override
    public void onFire(DamagingProjectileAPI proj, WeaponAPI weapon, CombatEngineAPI engine) {
        ShipAPI ship = weapon != null ? weapon.getShip() : null;
        if (ship == null || proj == null || engine == null || !LatticeData.get(ship).bravura) return;
        Object o = engine.spawnProjectile(ship, weapon, RslIds.WEAPON_SFORZANDO_BRAVURA, proj.getLocation(),
                proj.getFacing(), ship.getVelocity());
        if (!(o instanceof DamagingProjectileAPI)) return;
        DamagingProjectileAPI twin = (DamagingProjectileAPI) o;
        twin.setDamageAmount(proj.getDamageAmount());
        RailFx.holdRange(twin, proj.getLocation(), weapon.getRange());
        engine.removeEntity(proj);
    }

    /** The weapon id a skewer continuation must be spawned as, so a white slug stays white through every hull. */
    static String continuationId(DamagingProjectileAPI proj) {
        if (RslIds.PROJ_SFORZANDO_BRAVURA.equals(proj.getProjectileSpecId())) return RslIds.WEAPON_SFORZANDO_BRAVURA;
        return proj.getWeapon().getId();
    }
}
