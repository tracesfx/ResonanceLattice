package rsl.combat;

import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import org.lwjgl.util.vector.Vector2f;
import rsl.RslIds;

import java.util.List;

/**
 * Per-ship combat state of a Lattice ship (stored in the ship's custom data, so it dies with the battle).
 * Resonance rules (DESIGN.md section 2): 0-100, built by shield absorption and by hull/armor hits dealt, decays out of
 * contact; >= OVERTONE empowers the next system use and spends OVERTONE_COST; Sympathy shares a fraction of every
 * gain with Lattice allies in range.
 */
public class LatticeData {
    public static final float MAX = 100f;
    public static final float OVERTONE = 60f;
    public static final float OVERTONE_COST = 60f;
    public static final float SYMPATHY_RANGE = 1500f;
    public static final float SYMPATHY_SHARE = 0.15f;
    public static final float BRIDGE_RANGE = 2000f;
    public static final float BRIDGE_SHARE = 0.30f;
    public static final float DECAY_DELAY = 5f;
    public static final float DECAY_PER_SEC = 3f;

    public float resonance;
    public float sinceGain = 99f;
    /** Smoothed glow brightness 0..1 (renderer). */
    public float glow = 0.3f;

    // Grace Note
    public boolean discord;
    public boolean prevSystemOn;
    // Cadence
    public int crescendo;
    public float lastCrescendoBeamStack;
    // Virtuoso
    public float accentUntil;
    public boolean bravura;
    public float bravuraLevel;
    public float peakBonus;
    // Tremolo
    public Vector2f waveNode;
    public float waveHull;
    public float[][] waveArmor;
    public float waveStart = -1f;
    public boolean waveTimedOut;
    // Refrain
    public ShipAPI wardTarget;
    // Station petals
    public boolean petalBoosted;
    // generic one-shot latch for system activations
    public boolean systemFired;
    public boolean overtoneThisUse;
    /** Per-use object owned by the ship system script (dash state, ward listener, slowed projectiles...). */
    public Object sysObj;

    public static LatticeData get(ShipAPI ship) {
        Object o = ship.getCustomData().get(RslIds.KEY_DATA);
        if (o instanceof LatticeData) return (LatticeData) o;
        LatticeData d = new LatticeData();
        ship.setCustomData(RslIds.KEY_DATA, d);
        return d;
    }

    public static float resonance(ShipAPI ship) {
        return ship == null ? 0f : get(ship).resonance;
    }

    /** Adds Resonance to a Lattice ship and, if {@code share}, Sympathy to Lattice allies in range. */
    public static void gain(ShipAPI ship, float amount, boolean share) {
        if (ship == null || amount <= 0f || !RslUtil.isLattice(ship)) return;
        LatticeData d = get(ship);
        d.resonance = Math.min(MAX, d.resonance + amount);
        d.sinceGain = 0f;
        if (!share) return;
        CombatEngineAPI e = RslUtil.engine();
        if (e == null) return;
        boolean bridge = RslUtil.hasMod(ship, RslIds.HULLMOD_BRIDGE);
        float range = bridge ? BRIDGE_RANGE : SYMPATHY_RANGE;
        float share2 = bridge ? BRIDGE_SHARE : SYMPATHY_SHARE;
        List<ShipAPI> ships = e.getShips();
        for (int i = 0; i < ships.size(); i++) {
            ShipAPI s = ships.get(i);
            if (s == ship || s.getOwner() != ship.getOwner() || s.isHulk() || s.isFighter() || !RslUtil.isLattice(s)) {
                continue;
            }
            float dx = s.getLocation().x - ship.getLocation().x, dy = s.getLocation().y - ship.getLocation().y;
            if (dx * dx + dy * dy > range * range) continue;
            LatticeData o = get(s);
            o.resonance = Math.min(MAX, o.resonance + amount * share2);
        }
    }

    /** True (and spends the charge) when the ship is in Overtone. Call once per system use. */
    public static boolean consumeOvertone(ShipAPI ship) {
        if (ship == null || !RslUtil.isLattice(ship)) return false;
        LatticeData d = get(ship);
        if (d.resonance < OVERTONE) return false;
        d.resonance -= OVERTONE_COST;
        return true;
    }

    public static boolean inOvertone(ShipAPI ship) {
        return ship != null && get(ship).resonance >= OVERTONE;
    }
}
