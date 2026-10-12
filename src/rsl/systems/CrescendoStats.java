package rsl.systems;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.DamagingProjectileAPI;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.WeaponAPI;
import com.fs.starfarer.api.impl.combat.BaseShipSystemScript;
import rsl.combat.LatticeData;
import rsl.combat.LatticeDealtModifier;
import rsl.combat.RslUtil;

import java.util.List;

/**
 * Cadence: each energy hit while active adds a stack (counted in LatticeDealtModifier): +5% energy rate of fire and
 * +3% energy flux cost per stack. Overtone: at max stacks every energy weapon fires one extra Fortissimo shot
 * (+50% damage) and the ship sheds 30% of its soft flux.
 */
public class CrescendoStats extends BaseShipSystemScript {
    public static final float ROF_PER_STACK = 5f;
    public static final float FLUX_PER_STACK = 3f;
    public static final float FORTISSIMO_MULT = 1.5f;
    public static final float SOFT_VENT = 0.3f;
    private static final Object STATUS = new Object();

    @Override
    public void apply(MutableShipStatsAPI stats, String id, State state, float effectLevel) {
        ShipAPI ship = SystemUtil.ship(stats);
        if (ship == null || state == State.COOLDOWN || state == State.IDLE) return;
        LatticeData d = LatticeData.get(ship);
        if (!d.systemFired) {
            d.systemFired = true;
            d.crescendo = 0;
            d.overtoneThisUse = LatticeData.consumeOvertone(ship);
            d.sysObj = null;
        }
        stats.getEnergyRoFMult().modifyPercent(id, ROF_PER_STACK * d.crescendo * effectLevel);
        stats.getEnergyWeaponFluxCostMod().modifyPercent(id, FLUX_PER_STACK * d.crescendo * effectLevel);
        CombatEngineAPI engine = Global.getCombatEngine();
        if (ship == engine.getPlayerShip()) {
            engine.maintainStatusForPlayerShip(STATUS, "graphics/rsl/icons/hullsys/rsl_crescendo.png", "Crescendo",
                    d.crescendo + " stacks: +" + (int) (ROF_PER_STACK * d.crescendo) + "% energy rate of fire", false);
        }
        if (d.overtoneThisUse && d.sysObj == null && d.crescendo >= LatticeDealtModifier.CRESCENDO_MAX) {
            d.sysObj = Boolean.TRUE;
            fortissimo(ship);
        }
    }

    private static void fortissimo(ShipAPI ship) {
        CombatEngineAPI engine = Global.getCombatEngine();
        List<WeaponAPI> ws = ship.getAllWeapons();
        for (int i = 0; i < ws.size(); i++) {
            WeaponAPI w = ws.get(i);
            if (w.getType() != WeaponAPI.WeaponType.ENERGY || w.isBeam() || w.isDecorative() || w.isDisabled()) continue;
            Object o = engine.spawnProjectile(ship, w, w.getId(), w.getFirePoint(0), w.getCurrAngle(), ship.getVelocity());
            if (o instanceof DamagingProjectileAPI) {
                DamagingProjectileAPI p = (DamagingProjectileAPI) o;
                p.setDamageAmount(p.getDamageAmount() * FORTISSIMO_MULT);
            }
            engine.addHitParticle(w.getFirePoint(0), ship.getVelocity(), 60f, 1f, 0.2f, RslUtil.WHITE);
        }
        float soft = ship.getFluxTracker().getCurrFlux() - ship.getFluxTracker().getHardFlux();
        if (soft > 0f) ship.getFluxTracker().decreaseFlux(soft * SOFT_VENT);
        engine.addFloatingText(ship.getLocation(), "Fortissimo!", 30f, RslUtil.TEAL, ship, 1f, 1f);
    }

    @Override
    public void unapply(MutableShipStatsAPI stats, String id) {
        stats.getEnergyRoFMult().unmodify(id);
        stats.getEnergyWeaponFluxCostMod().unmodify(id);
        ShipAPI ship = SystemUtil.ship(stats);
        if (ship == null) return;
        LatticeData d = LatticeData.get(ship);
        d.crescendo = 0;
        d.systemFired = false;
        d.overtoneThisUse = false;
        d.sysObj = null;
    }

    @Override
    public StatusData getStatusData(int index, State state, float effectLevel) {
        return null;
    }

    @Override
    public String getDisplayNameOverride(State state, float effectLevel) {
        return null;
    }
}
