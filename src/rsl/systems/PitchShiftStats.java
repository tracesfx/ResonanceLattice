package rsl.systems;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.DamageType;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.ShipCommand;
import com.fs.starfarer.api.impl.combat.BaseShipSystemScript;
import rsl.combat.LatticeData;
import rsl.combat.RslUtil;

import java.util.List;

/**
 * Grace Note, toggle. Off = Harmonic (shields, +25% dissipation, energy hits add EMP via RslDamageListener);
 * on = Discord (shields locked, +30% speed, +20% weapon damage). The script also runs while idle
 * ("runScriptWhileIdle") so Harmonic is applied whenever Discord is not. Overtone: switching releases an EMP pulse.
 */
public class PitchShiftStats extends BaseShipSystemScript {
    public static final float HARMONIC_FLUX = 25f;
    public static final float DISCORD_SPEED = 30f;
    public static final float DISCORD_DAMAGE = 20f;
    public static final float PULSE_RANGE = 450f;
    public static final float PULSE_EMP = 400f;

    @Override
    public void apply(MutableShipStatsAPI stats, String id, State state, float effectLevel) {
        ShipAPI ship = SystemUtil.ship(stats);
        if (ship == null) return;
        LatticeData d = LatticeData.get(ship);
        boolean discord = state == State.IN || state == State.ACTIVE;
        if (discord != d.discord) {
            d.discord = discord;
            if (LatticeData.consumeOvertone(ship)) pulse(ship);
        }
        if (discord) {
            stats.getFluxDissipation().unmodify(id + "_h");
            stats.getMaxSpeed().modifyPercent(id, DISCORD_SPEED * effectLevel);
            stats.getAcceleration().modifyPercent(id, DISCORD_SPEED * effectLevel);
            stats.getEnergyWeaponDamageMult().modifyPercent(id, DISCORD_DAMAGE);
            stats.getBallisticWeaponDamageMult().modifyPercent(id, DISCORD_DAMAGE);
            stats.getMissileWeaponDamageMult().modifyPercent(id, DISCORD_DAMAGE);
            if (ship.getShield() != null && ship.getShield().isOn()) ship.getShield().toggleOff();
            ship.blockCommandForOneFrame(ShipCommand.TOGGLE_SHIELD_OR_PHASE_CLOAK);
        } else {
            unapplyDiscord(stats, id);
            stats.getFluxDissipation().modifyPercent(id + "_h", HARMONIC_FLUX);
        }
    }

    private static void unapplyDiscord(MutableShipStatsAPI stats, String id) {
        stats.getMaxSpeed().unmodify(id);
        stats.getAcceleration().unmodify(id);
        stats.getEnergyWeaponDamageMult().unmodify(id);
        stats.getBallisticWeaponDamageMult().unmodify(id);
        stats.getMissileWeaponDamageMult().unmodify(id);
    }

    @Override
    public void unapply(MutableShipStatsAPI stats, String id) {
        unapplyDiscord(stats, id);
    }

    private static void pulse(ShipAPI ship) {
        CombatEngineAPI engine = Global.getCombatEngine();
        List<ShipAPI> ships = engine.getShips();
        int arcs = 0;
        for (int i = 0; i < ships.size() && arcs < 4; i++) {
            ShipAPI s = ships.get(i);
            if (s.isHulk() || !RslUtil.isEnemy(ship, s)) continue;
            float dx = s.getLocation().x - ship.getLocation().x, dy = s.getLocation().y - ship.getLocation().y;
            if (dx * dx + dy * dy > PULSE_RANGE * PULSE_RANGE) continue;
            engine.spawnEmpArc(ship, ship.getLocation(), ship, s, DamageType.ENERGY, 20f, PULSE_EMP, PULSE_RANGE + 200f,
                    "system_emp_emitter_impact", 6f, LatticeData.get(ship).discord ? RslUtil.VIOLET : RslUtil.TEAL,
                    RslUtil.WHITE);
            arcs++;
        }
        engine.addSmoothParticle(ship.getLocation(), ship.getVelocity(), PULSE_RANGE, 0.6f, 0.4f, RslUtil.VIOLET);
    }

    @Override
    public StatusData getStatusData(int index, State state, float effectLevel) {
        boolean discord = state == State.IN || state == State.ACTIVE;
        if (index == 0) return new StatusData(discord ? "Discord: shields locked" : "Harmonic: +25% dissipation", discord);
        if (index == 1 && discord) return new StatusData("+30% speed, +20% weapon damage", false);
        return null;
    }

    @Override
    public String getDisplayNameOverride(State state, float effectLevel) {
        return state == State.IN || state == State.ACTIVE ? "Pitch Shift: Discord" : "Pitch Shift: Harmonic";
    }
}
