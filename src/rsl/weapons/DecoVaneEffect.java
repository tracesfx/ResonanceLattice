package rsl.weapons;

import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.EveryFrameWeaponEffectPlugin;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.WeaponAPI;
import rsl.RslIds;
import rsl.combat.LatticeData;

/**
 * Hinged hull parts. Each swings between its slot angle (rest) and the deployed angle from the art spec
 * ("deco_alt_angle"), interpolating in raw degrees so it sweeps through the outside of the hull:
 * Refrain vanes close over the bow while Sympathetic Ward runs; Conductor blades flex while Sympathetic Strike
 * charges; Virtuoso vanes flare open in Bravura.
 */
public class DecoVaneEffect implements EveryFrameWeaponEffectPlugin {
    private float level;
    private float rest = Float.NaN;
    private float deployed;
    private int kind; // 0 refrain, 1 conductor, 2 virtuoso

    @Override
    public void advance(float amount, CombatEngineAPI engine, WeaponAPI weapon) {
        ShipAPI ship = weapon.getShip();
        if (ship == null) return;
        if (Float.isNaN(rest)) init(weapon);
        float want = 0f;
        if (ship.isAlive() && !ship.isHulk()) {
            if (kind == 2) want = LatticeData.get(ship).bravuraLevel;
            else if (ship.getSystem() != null) want = ship.getSystem().getEffectLevel();
        }
        if (!engine.isPaused()) level += (want - level) * Math.min(1f, amount * (kind == 0 ? 4f : 3f));
        weapon.setCurrAngle(ship.getFacing() + rest + (deployed - rest) * level);
    }

    private void init(WeaponAPI weapon) {
        rest = weapon.getSlot().getAngle();
        String id = weapon.getId();
        deployed = rest;
        kind = 1;
        if (RslIds.WEAPON_DECO_REFRAIN_R.equals(id)) {
            kind = 0;
            deployed = 12f;
        } else if (RslIds.WEAPON_DECO_REFRAIN_L.equals(id)) {
            kind = 0;
            deployed = -12f;
        } else if (RslIds.WEAPON_DECO_CONDUCTOR_R.equals(id)) {
            deployed = 7f;
        } else if (RslIds.WEAPON_DECO_CONDUCTOR_L.equals(id)) {
            deployed = -7f;
        } else if (RslIds.WEAPON_DECO_VIRTUOSO_R.equals(id)) {
            kind = 2;
            deployed = -138.1f;
        } else if (RslIds.WEAPON_DECO_VIRTUOSO_L.equals(id)) {
            kind = 2;
            deployed = 138.1f;
        }
    }
}
