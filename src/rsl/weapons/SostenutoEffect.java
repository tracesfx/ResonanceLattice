package rsl.weapons;

import com.fs.starfarer.api.combat.BeamAPI;
import com.fs.starfarer.api.combat.BeamEffectPlugin;
import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.CombatEntityAPI;
import com.fs.starfarer.api.combat.FluxTrackerAPI;
import com.fs.starfarer.api.combat.ShipAPI;

/**
 * Sostenuto Beam: {@link #HARD_SHARE} of the flux its damage puts on a shield is converted from soft to hard flux
 * (it adds none: it moves part of the soft flux the beam already caused into the hard pool).
 */
public class SostenutoEffect implements BeamEffectPlugin {
    public static final float HARD_SHARE = 0.35f;

    @Override
    public void advance(float amount, CombatEngineAPI engine, BeamAPI beam) {
        if (engine.isPaused() || !beam.didDamageThisFrame()) return;
        CombatEntityAPI t = beam.getDamageTarget();
        if (!(t instanceof ShipAPI)) return;
        ShipAPI s = (ShipAPI) t;
        if (s.getShield() == null || !s.getShield().isOn() || !s.getShield().isWithinArc(beam.getTo())) return;
        float dps = beam.getWeapon().getDerivedStats().getDps();
        float flux = dps * amount * s.getShield().getFluxPerPointOfDamage() * HARD_SHARE;
        FluxTrackerAPI f = s.getFluxTracker();
        f.setHardFlux(Math.min(f.getCurrFlux(), f.getHardFlux() + flux));
    }
}
