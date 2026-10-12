package rsl.weapons;

import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.EveryFrameWeaponEffectPlugin;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.WeaponAPI;
import rsl.RslIds;

/**
 * Halo / Cantor ring: turns slowly, faster while the ship system runs (Stillwater Halo, Grand Chorus). The ring is
 * deliberately asymmetric (swept teeth), so its rotation reads in combat.
 */
public class DecoRingEffect implements EveryFrameWeaponEffectPlugin {
    private float angle = Float.NaN;
    private float spin;

    @Override
    public void advance(float amount, CombatEngineAPI engine, WeaponAPI weapon) {
        ShipAPI ship = weapon.getShip();
        if (ship == null) return;
        if (Float.isNaN(angle)) angle = weapon.getSlot().getAngle();
        if (!engine.isPaused()) {
            boolean halo = RslIds.WEAPON_DECO_HALO_RING.equals(weapon.getId());
            float base = halo ? 8f : 3f;
            float boost = halo ? 90f : 40f;
            float level = ship.getSystem() != null ? ship.getSystem().getEffectLevel() : 0f;
            float want = ship.isAlive() && !ship.isHulk() ? base + boost * level : 0f;
            spin += (want - spin) * Math.min(1f, amount * 1.5f);
            angle = (angle + spin * amount) % 360f;
        }
        weapon.setCurrAngle(ship.getFacing() + angle);
    }
}
