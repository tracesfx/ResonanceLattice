package rsl.systems;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.DamagingProjectileAPI;
import com.fs.starfarer.api.combat.GuidedMissileAI;
import com.fs.starfarer.api.combat.MissileAPI;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.impl.combat.BaseShipSystemScript;
import org.lwjgl.util.vector.Vector2f;
import rsl.combat.LatticeData;
import rsl.combat.RslUtil;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * Halo: a zone of still space. Enemy projectiles entering it are slowed once by {@link #SLOW}, enemy guided missiles
 * inside keep losing their target, and the Halo's own dissipation drops while it runs. The ring spins up
 * (DecoRingEffect reads the effect level). Overtone: the damage of every slowed shot becomes Resonance for Lattice
 * allies inside the zone.
 */
public class StillwaterHaloStats extends BaseShipSystemScript {
    public static final float RADIUS = 700f;
    public static final float SLOW = 0.6f;
    public static final float DISSIPATION_MULT = 0.7f;
    public static final float RESONANCE_PER_DAMAGE = 0.004f;

    @Override
    public void apply(MutableShipStatsAPI stats, String id, State state, float effectLevel) {
        ShipAPI ship = SystemUtil.ship(stats);
        if (ship == null || state == State.COOLDOWN || state == State.IDLE) return;
        LatticeData d = LatticeData.get(ship);
        CombatEngineAPI engine = Global.getCombatEngine();
        if (!d.systemFired) {
            d.systemFired = true;
            d.overtoneThisUse = LatticeData.consumeOvertone(ship);
            d.sysObj = new HashSet<DamagingProjectileAPI>();
        }
        stats.getFluxDissipation().modifyMult(id, DISSIPATION_MULT);
        if (engine.isPaused() || effectLevel <= 0f) return;
        @SuppressWarnings("unchecked")
        Set<DamagingProjectileAPI> slowed = (Set<DamagingProjectileAPI>) d.sysObj;
        float r = RADIUS * effectLevel;
        float r2 = r * r;
        float absorbed = 0f;
        List<DamagingProjectileAPI> projs = engine.getProjectiles();
        for (int i = 0; i < projs.size(); i++) {
            DamagingProjectileAPI p = projs.get(i);
            if (p.getOwner() == ship.getOwner() || p.isFading()) continue;
            float dx = p.getLocation().x - ship.getLocation().x, dy = p.getLocation().y - ship.getLocation().y;
            if (dx * dx + dy * dy > r2) continue;
            if (p instanceof MissileAPI) {
                MissileAPI m = (MissileAPI) p;
                if (m.getMissileAI() instanceof GuidedMissileAI) ((GuidedMissileAI) m.getMissileAI()).setTarget(null);
            }
            if (slowed.add(p)) {
                p.getVelocity().scale(1f - SLOW);
                absorbed += p.getDamageAmount();
                if (Math.random() < 0.3) engine.addHitParticle(p.getLocation(), new Vector2f(), 20f, 0.6f, 0.3f, RslUtil.TEAL);
            }
        }
        if (slowed.size() > 400) slowed.clear();
        if (d.overtoneThisUse && absorbed > 0f) {
            List<ShipAPI> ships = engine.getShips();
            for (int i = 0; i < ships.size(); i++) {
                ShipAPI s = ships.get(i);
                if (s.getOwner() != ship.getOwner() || s.isHulk() || s.isFighter() || !RslUtil.isLattice(s)) continue;
                float dx = s.getLocation().x - ship.getLocation().x, dy = s.getLocation().y - ship.getLocation().y;
                if (dx * dx + dy * dy < r2) LatticeData.gain(s, absorbed * RESONANCE_PER_DAMAGE, false);
            }
        }
        if (Math.random() < 0.6) {
            double a = Math.random() * Math.PI * 2;
            Vector2f p = new Vector2f(ship.getLocation().x + (float) Math.cos(a) * r,
                    ship.getLocation().y + (float) Math.sin(a) * r);
            engine.addSmoothParticle(p, ship.getVelocity(), 60f, 0.5f * effectLevel, 0.6f, RslUtil.TEAL_DIM);
        }
    }

    @Override
    public void unapply(MutableShipStatsAPI stats, String id) {
        stats.getFluxDissipation().unmodify(id);
        ShipAPI ship = SystemUtil.ship(stats);
        if (ship == null) return;
        LatticeData d = LatticeData.get(ship);
        d.systemFired = false;
        d.overtoneThisUse = false;
        d.sysObj = null;
    }

    @Override
    public StatusData getStatusData(int index, State state, float effectLevel) {
        if (index == 0) return new StatusData("stillwater: enemy shots slowed", false);
        if (index == 1) return new StatusData("-30% flux dissipation", true);
        return null;
    }
}
