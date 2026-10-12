package rsl.systems;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.CombatEntityAPI;
import com.fs.starfarer.api.combat.DamageAPI;
import com.fs.starfarer.api.combat.DamageType;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.ShipSystemAPI;
import com.fs.starfarer.api.combat.listeners.DamageTakenModifier;
import com.fs.starfarer.api.impl.combat.BaseShipSystemScript;
import org.lwjgl.util.vector.Vector2f;
import rsl.combat.LatticeData;
import rsl.combat.RslUtil;

import java.util.List;

/**
 * Refrain: ties its core to an ally within range (the player's targeted ally, else the most endangered one).
 * A DamageTakenModifier on the ally removes {@link #SHARE} of each hit and lands it on the Refrain: as hard flux on
 * the shield if it is up and not near overload, else as hull damage. The vanes swing forward (DecoVaneEffect reads
 * the system's effect level). Overtone: double Resonance from redirected damage, -30% beam damage taken.
 */
public class SympatheticWardStats extends BaseShipSystemScript {
    public static final float RANGE = 800f;
    public static final float LEASH = 1100f;
    public static final float SHARE = 0.4f;
    public static final float BEAM_RESIST = 0.7f;

    /** Picks the ward target: a targeted ally in range, else the ally in most danger. */
    public static ShipAPI pickAlly(ShipAPI ship) {
        ShipAPI t = ship.getShipTarget();
        if (valid(ship, t)) return t;
        CombatEngineAPI engine = Global.getCombatEngine();
        ShipAPI best = null;
        float bestScore = -1f;
        List<ShipAPI> ships = engine.getShips();
        for (int i = 0; i < ships.size(); i++) {
            ShipAPI s = ships.get(i);
            if (!valid(ship, s)) continue;
            float score = s.getFluxLevel() + (1f - s.getHullLevel()) * 1.5f + (s.isFrigate() ? 0f : 0.2f);
            if (score > bestScore) {
                bestScore = score;
                best = s;
            }
        }
        return best;
    }

    static boolean valid(ShipAPI ship, ShipAPI s) {
        if (s == null || s == ship || s.isHulk() || s.isFighter() || s.isStationModule() || s.getOwner() != ship.getOwner()) {
            return false;
        }
        float dx = s.getLocation().x - ship.getLocation().x, dy = s.getLocation().y - ship.getLocation().y;
        return dx * dx + dy * dy <= RANGE * RANGE;
    }

    @Override
    public boolean isUsable(ShipSystemAPI system, ShipAPI ship) {
        return pickAlly(ship) != null;
    }

    @Override
    public String getInfoText(ShipSystemAPI system, ShipAPI ship) {
        if (system.isActive()) return null;
        return pickAlly(ship) == null ? "NO ALLY IN RANGE" : "READY";
    }

    @Override
    public void apply(MutableShipStatsAPI stats, String id, State state, float effectLevel) {
        ShipAPI ship = SystemUtil.ship(stats);
        if (ship == null || state == State.COOLDOWN || state == State.IDLE) return;
        LatticeData d = LatticeData.get(ship);
        CombatEngineAPI engine = Global.getCombatEngine();
        if (!d.systemFired) {
            d.systemFired = true;
            d.overtoneThisUse = LatticeData.consumeOvertone(ship);
            ShipAPI ally = pickAlly(ship);
            d.wardTarget = ally;
            if (ally != null) {
                WardListener l = new WardListener(ship, d.overtoneThisUse);
                d.sysObj = l;
                ally.addListener(l);
            }
        }
        if (d.overtoneThisUse) stats.getBeamDamageTakenMult().modifyMult(id, BEAM_RESIST);
        ShipAPI ally = d.wardTarget;
        if (ally != null && !engine.isPaused() && Math.random() < 0.25) {
            engine.spawnEmpArcVisual(ship.getLocation(), ship, ally.getLocation(), ally, 4f, RslUtil.TEAL_DIM,
                    RslUtil.WHITE);
        }
    }

    @Override
    public void unapply(MutableShipStatsAPI stats, String id) {
        stats.getBeamDamageTakenMult().unmodify(id);
        ShipAPI ship = SystemUtil.ship(stats);
        if (ship == null) return;
        LatticeData d = LatticeData.get(ship);
        if (d.wardTarget != null && d.sysObj instanceof WardListener) d.wardTarget.removeListener(d.sysObj);
        d.wardTarget = null;
        d.sysObj = null;
        d.systemFired = false;
        d.overtoneThisUse = false;
    }

    @Override
    public StatusData getStatusData(int index, State state, float effectLevel) {
        return index == 0 ? new StatusData("warding an ally: sharing its damage", false) : null;
    }

    /** On the warded ally. */
    public static class WardListener implements DamageTakenModifier {
        final ShipAPI refrain;
        final boolean overtone;

        WardListener(ShipAPI refrain, boolean overtone) {
            this.refrain = refrain;
            this.overtone = overtone;
        }

        @Override
        public String modifyDamageTaken(Object param, CombatEntityAPI target, DamageAPI damage, Vector2f point,
                                        boolean shieldHit) {
            if (!RslUtil.alive(refrain) || refrain.getSystem() == null || !refrain.getSystem().isOn()) return null;
            float dx = target.getLocation().x - refrain.getLocation().x;
            float dy = target.getLocation().y - refrain.getLocation().y;
            if (dx * dx + dy * dy > LEASH * LEASH) return null;
            CombatEngineAPI engine = Global.getCombatEngine();
            float amount = damage.getDamage() * damage.getModifier().getModifiedValue();
            if (damage.isDps()) amount *= engine.getElapsedInLastFrame();
            float moved = amount * SHARE;
            if (moved <= 0f) return null;
            if (refrain.getShield() != null && refrain.getShield().isOn() && refrain.getFluxLevel() < 0.9f) {
                refrain.getFluxTracker().increaseFlux(moved * refrain.getShield().getFluxPerPointOfDamage(), true);
            } else {
                engine.applyDamage(refrain, refrain.getLocation(), moved, DamageType.ENERGY, 0f, true, false, refrain,
                        false);
            }
            LatticeData.gain(refrain, moved * 0.01f * (overtone ? 2f : 1f), false);
            String id = "rsl_ward_share";
            damage.getModifier().modifyMult(id, 1f - SHARE);
            return id;
        }
    }
}
