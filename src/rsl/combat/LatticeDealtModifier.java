package rsl.combat;

import com.fs.starfarer.api.combat.ArmorGridAPI;
import com.fs.starfarer.api.combat.BeamAPI;
import com.fs.starfarer.api.combat.CombatEntityAPI;
import com.fs.starfarer.api.combat.DamageAPI;
import com.fs.starfarer.api.combat.DamagingProjectileAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.WeaponAPI;
import com.fs.starfarer.api.combat.listeners.DamageDealtModifier;
import org.lwjgl.util.vector.Vector2f;
import rsl.RslIds;

import java.util.HashMap;
import java.util.Map;

/**
 * Added to every Lattice ship (LatticeCore.applyEffectsAfterShipCreation). Runs before each hit the ship deals:
 * <ul>
 * <li>Sympathetic Strike mark: +20% damage to a marked target.</li>
 * <li>Fracture (Staccato): stacks on the target; the 6th stack shatters the armor at the impact point.</li>
 * <li>Crescendo (Cadence): energy hits add stacks while the system runs.</li>
 * </ul>
 * Beams count at most one stack per {@link #BEAM_STACK_INTERVAL} seconds.
 */
public class LatticeDealtModifier implements DamageDealtModifier {
    public static final String MARK_ID = "rsl_mark_bonus";
    public static final float MARK_BONUS = 20f;
    public static final int FRACTURE_MAX = 5;
    public static final float FRACTURE_TIMEOUT = 6f;
    public static final float FRACTURE_SHATTER = 300f;
    public static final float BEAM_STACK_INTERVAL = 0.5f;
    public static final int CRESCENDO_MAX = 20;

    private final ShipAPI ship;
    private final Map<ShipAPI, Float> lastBeamStack = new HashMap<>();

    public LatticeDealtModifier(ShipAPI ship) {
        this.ship = ship;
    }

    /** Fracture stacks live on the target: {count, lastHitTime}. */
    public static float[] fracture(ShipAPI t) {
        Object o = t.getCustomData().get(RslIds.KEY_FRACTURE);
        if (o instanceof float[]) return (float[]) o;
        float[] f = new float[]{0f, 0f};
        t.setCustomData(RslIds.KEY_FRACTURE, f);
        return f;
    }

    @Override
    public String modifyDamageDealt(Object param, CombatEntityAPI target, DamageAPI damage, Vector2f point,
                                    boolean shieldHit) {
        if (!(target instanceof ShipAPI)) return null;
        ShipAPI t = (ShipAPI) target;
        if (!RslUtil.isEnemy(ship, t)) return null;
        boolean isBeam = param instanceof BeamAPI;
        if (!isBeam && !(param instanceof DamagingProjectileAPI)) return null;
        float now = RslUtil.now();
        boolean countStack = true;
        if (isBeam) {
            Float last = lastBeamStack.get(t);
            countStack = last == null || now - last >= BEAM_STACK_INTERVAL;
            if (countStack) lastBeamStack.put(t, now);
            if (lastBeamStack.size() > 64) lastBeamStack.clear();
        }

        // Crescendo
        if (countStack && ship.getSystem() != null && RslIds.SYSTEM_CRESCENDO.equals(ship.getSystem().getId())
                && ship.getSystem().isActive() && RslUtil.isEnergyWeaponHit(param)) {
            LatticeData d = LatticeData.get(ship);
            if (d.crescendo < CRESCENDO_MAX) d.crescendo++;
        }

        // Fracture
        if (countStack && !shieldHit && !t.isFighter() && RslUtil.hasMod(ship, RslIds.HULLMOD_FRACTURE)) {
            float[] f = fracture(t);
            if (now - f[1] > FRACTURE_TIMEOUT) f[0] = 0f;
            f[1] = now;
            if (f[0] >= FRACTURE_MAX) {
                f[0] = 0f;
                shatter(t, point);
            } else {
                f[0] += 1f;
            }
        }

        // Mark
        Object mark = t.getCustomData().get(RslIds.KEY_MARK_UNTIL);
        if (mark instanceof Float && (Float) mark > now) {
            damage.getModifier().modifyPercent(MARK_ID, MARK_BONUS);
            return MARK_ID;
        }
        return null;
    }

    private void shatter(ShipAPI t, Vector2f point) {
        ArmorGridAPI grid = t.getArmorGrid();
        int[] cell = grid.getCellAtLocation(point);
        if (cell == null) return;
        float[][] g = grid.getGrid();
        float left = FRACTURE_SHATTER;
        for (int dx = -1; dx <= 1; dx++) {
            for (int dy = -1; dy <= 1; dy++) {
                int x = cell[0] + dx, y = cell[1] + dy;
                if (x < 0 || y < 0 || x >= g.length || y >= g[0].length) continue;
                float share = (dx == 0 && dy == 0) ? 0.4f : 0.075f;
                float cut = Math.min(g[x][y], FRACTURE_SHATTER * share);
                grid.setArmorValue(x, y, g[x][y] - cut);
                left -= cut;
            }
        }
        t.syncWithArmorGridState();
        RslUtil.engine().addHitParticle(point, t.getVelocity(), 80f, 1f, 0.25f, RslUtil.VIOLET);
        RslUtil.engine().addFloatingText(point, "Shatter", 22f, RslUtil.VIOLET, t, 0.5f, 0.5f);
    }

    static boolean isEnergy(WeaponAPI w) {
        return w != null && w.getType() == WeaponAPI.WeaponType.ENERGY;
    }
}
