package rsl.weapons;

import com.fs.starfarer.api.combat.BeamAPI;
import com.fs.starfarer.api.combat.BeamEffectPlugin;
import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.CombatEntityAPI;
import com.fs.starfarer.api.combat.DamageType;
import com.fs.starfarer.api.combat.ShipAPI;
import org.lwjgl.util.vector.Vector2f;

/**
 * Lattice Lance: while the beam stays on the same ship, extra damage ramps up to +{@link #MAX_BONUS} over
 * {@link #RAMP} seconds; switching targets resets it. The bonus is applied as additional soft-flux beam damage.
 */
public class LatticeLanceEffect implements BeamEffectPlugin {
    public static final float MAX_BONUS = 0.75f;
    public static final float RAMP = 3f;
    private CombatEntityAPI target;
    private float held;

    @Override
    public void advance(float amount, CombatEngineAPI engine, BeamAPI beam) {
        if (engine.isPaused()) return;
        CombatEntityAPI t = beam.getDamageTarget();
        if (t != target) {
            target = t;
            held = 0f;
        }
        if (!(t instanceof ShipAPI) || beam.getBrightness() < 0.99f || !beam.didDamageThisFrame()) return;
        held += amount;
        float bonus = MAX_BONUS * Math.min(1f, held / RAMP);
        float dps = beam.getWeapon().getDerivedStats().getDps();
        if (bonus <= 0f) return;
        engine.applyDamage(t, new Vector2f(beam.getTo()), dps * bonus * amount, DamageType.ENERGY, 0f, false, true,
                beam.getSource(), false);
        beam.setWidth(12f + 10f * bonus);
    }
}
