package rsl.systems;

import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.ShipSystemAIScript;
import com.fs.starfarer.api.combat.ShipSystemAPI;
import com.fs.starfarer.api.combat.ShipwideAIFlags;
import com.fs.starfarer.api.util.IntervalUtil;
import org.lazywizard.lazylib.combat.AIUtils;
import org.lwjgl.util.vector.Vector2f;

/**
 * Shared shape of the Lattice system AIs: think a few times per second, decide whether the system should be used
 * (or toggled) now, and press the button only when the engine allows it.
 */
public abstract class RslSystemAI implements ShipSystemAIScript {
    protected ShipAPI ship;
    protected ShipSystemAPI system;
    protected ShipwideAIFlags flags;
    protected CombatEngineAPI engine;
    private final IntervalUtil think = new IntervalUtil(0.25f, 0.4f);

    @Override
    public void init(ShipAPI ship, ShipSystemAPI system, ShipwideAIFlags flags, CombatEngineAPI engine) {
        this.ship = ship;
        this.system = system;
        this.flags = flags;
        this.engine = engine;
    }

    @Override
    public void advance(float amount, Vector2f missileDangerDir, Vector2f collisionDangerDir, ShipAPI target) {
        if (engine == null || engine.isPaused() || ship == null || !ship.isAlive()) return;
        think.advance(amount);
        if (!think.intervalElapsed()) return;
        boolean toggleOff = system.isOn() && system.getSpecAPI() != null && system.getSpecAPI().isToggle();
        if (!toggleOff && (system.isOn() || !AIUtils.canUseSystemThisFrame(ship))) return;
        if (decide(missileDangerDir, collisionDangerDir, target)) ship.useSystem();
    }

    /** True to press the system key now. */
    protected abstract boolean decide(Vector2f missileDangerDir, Vector2f collisionDangerDir, ShipAPI target);

    protected float dist(ShipAPI other) {
        return other == null ? Float.MAX_VALUE : Vector2f.sub(other.getLocation(), ship.getLocation(), null).length();
    }
}
