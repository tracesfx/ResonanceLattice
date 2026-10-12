package rsl.combat;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.CombatEntityAPI;
import com.fs.starfarer.api.combat.DamageType;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.listeners.ApplyDamageResultAPI;
import com.fs.starfarer.api.combat.listeners.DamageListener;
import org.apache.log4j.Logger;
import rsl.RslIds;
import rsl.hullmods.StolenTime;

/**
 * Battle-wide damage listener (engine listener manager): sees every damage application after it lands.
 * Resonance gain, Stolen Time, Tuning Spike detonation and the Grace Note's Harmonic EMP all hang off this.
 * Damage this mod applies itself passes the ship (not a projectile/beam) as its source, so it never detonates spikes
 * or re-triggers weapon-only effects.
 */
public class RslDamageListener implements DamageListener {
    private static final Logger log = Global.getLogger(RslDamageListener.class);

    /** Resonance per point of damage absorbed by a Lattice ship's shield. */
    public static final float GAIN_SHIELD = 0.010f;
    /** Resonance per point of hull/armor damage a Lattice ship deals. */
    public static final float GAIN_HIT = 0.015f;
    public static final float HARMONIC_EMP = 0.25f;

    private boolean broken;

    @Override
    public void reportDamageApplied(Object source, CombatEntityAPI target, ApplyDamageResultAPI result) {
        if (broken || !(target instanceof ShipAPI) || result == null) return;
        try {
            ShipAPI t = (ShipAPI) target;
            ShipAPI src = RslUtil.sourceShip(source);
            float shield = result.getDamageToShields();
            float body = result.getDamageToHull() + result.getTotalDamageToArmor();

            if (shield > 0f && RslUtil.isLattice(t)) LatticeData.gain(t, shield * GAIN_SHIELD, true);
            if (src == null || !RslUtil.isEnemy(src, t)) return;
            if (body > 0f && RslUtil.isLattice(src)) {
                LatticeData.gain(src, body * GAIN_HIT * (t.isFighter() ? 0.5f : 1f), true);
            }
            if (body > 0f && !t.isFighter() && RslUtil.hasMod(src, RslIds.HULLMOD_STOLEN_TIME)) {
                StolenTime.steal(src, t, body);
            }
            if (!t.isFighter() && (t.getHitpoints() <= 0f || t.isHulk())
                    && RslUtil.hasMod(src, RslIds.HULLMOD_STOLEN_TIME) && t.getCustomData().get(RslIds.KEY_KILL_CR) == null) {
                t.setCustomData(RslIds.KEY_KILL_CR, Boolean.TRUE);
                StolenTime.onKill(src, t);
            }
            boolean energy = RslUtil.isEnergyWeaponHit(source);
            if (energy && (shield > 0f || body > 0f)) {
                RslCombatPlugin p = RslCombatPlugin.get();
                if (p != null && p.hasSpikes(t)) p.detonateSpikes(t);
            }
            if (energy && body > 0f && src.getSystem() != null
                    && RslIds.SYSTEM_PITCHSHIFT.equals(src.getSystem().getId()) && !LatticeData.get(src).discord) {
                CombatEngineAPI e = Global.getCombatEngine();
                e.applyDamage(t, t.getLocation(), 0f, DamageType.ENERGY, body * HARMONIC_EMP, true, false, src, false);
            }
        } catch (Throwable ex) {
            broken = true;
            log.error("Resonance Lattice damage listener disabled after an error", ex);
        }
    }
}
