package rsl.combat;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.combat.BaseEveryFrameCombatPlugin;
import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.DamageType;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.input.InputEventAPI;
import org.apache.log4j.Logger;
import org.lwjgl.util.vector.Vector2f;
import rsl.RslIds;
import rsl.weapons.RailFx;

import java.util.ArrayList;
import java.util.List;

/**
 * One instance per battle (registered in data/config/settings.json). Registers the global damage listener and the
 * glow renderer, and runs the battle-wide effects that outlive a single hit: Crystal Flechette damage-over-time and
 * embedded Tuning Spikes, plus the rail slugs' in-flight effects ({@link RailFx}). Errors disable the plugin for
 * the rest of the battle instead of crashing it.
 */
public class RslCombatPlugin extends BaseEveryFrameCombatPlugin {
    private static final Logger log = Global.getLogger(RslCombatPlugin.class);

    public static final float SPIKE_LIFE = 10f;
    public static final float SPIKE_DAMAGE = 300f;
    public static final int SPIKE_MAX_PER_SHIP = 12;

    /** A point fixed to a ship: offset in the ship's frame, so it moves and turns with the hull. */
    public static class Attached {
        public ShipAPI target;
        public ShipAPI source;
        public float lx, ly, angle, until, amount, tick;

        public Vector2f world(Vector2f out) {
            float rad = (float) Math.toRadians(target.getFacing());
            float c = (float) Math.cos(rad), s = (float) Math.sin(rad);
            out.set(target.getLocation().x + lx * c - ly * s, target.getLocation().y + lx * s + ly * c);
            return out;
        }

        void attach(ShipAPI t, Vector2f p, float worldAngle) {
            target = t;
            float rad = (float) Math.toRadians(-t.getFacing());
            float c = (float) Math.cos(rad), s = (float) Math.sin(rad);
            float dx = p.x - t.getLocation().x, dy = p.y - t.getLocation().y;
            lx = dx * c - dy * s;
            ly = dx * s + dy * c;
            angle = worldAngle - t.getFacing();
        }
    }

    private CombatEngineAPI engine;
    private boolean broken;
    public final List<Attached> dots = new ArrayList<>();
    public final List<Attached> spikes = new ArrayList<>();
    private final Vector2f tmp = new Vector2f();
    private final ChorusEffects chorus = new ChorusEffects();

    public static RslCombatPlugin get() {
        CombatEngineAPI e = Global.getCombatEngine();
        if (e == null) return null;
        Object o = e.getCustomData().get(RslIds.KEY_ENGINE_STATE);
        return o instanceof RslCombatPlugin ? (RslCombatPlugin) o : null;
    }

    /** The duel against the Dies Irae (null in every other battle). */
    private EncoreCombat encore;

    @Override
    public void init(CombatEngineAPI engine) {
        this.engine = engine;
        engine.getCustomData().put(RslIds.KEY_ENGINE_STATE, this);
        engine.getListenerManager().addListener(new RslDamageListener());
        engine.addLayeredRenderingPlugin(new LatticeGlowRenderer(this));
        encore = EncoreCombat.create(engine);
    }

    // ------------------------------------------------------------------------------------------------ API
    public void addDot(ShipAPI target, ShipAPI source, Vector2f point, float total, float duration) {
        Attached a = new Attached();
        a.attach(target, point, 0f);
        a.source = source;
        a.amount = total / duration;
        a.until = RslUtil.now() + duration;
        dots.add(a);
    }

    public void embedSpike(ShipAPI target, ShipAPI source, Vector2f point, float facing) {
        int n = 0;
        for (int i = 0; i < spikes.size(); i++) if (spikes.get(i).target == target) n++;
        if (n >= SPIKE_MAX_PER_SHIP) return;
        Attached a = new Attached();
        a.attach(target, point, facing);
        a.source = source;
        a.until = RslUtil.now() + SPIKE_LIFE;
        spikes.add(a);
    }

    public boolean hasSpikes(ShipAPI target) {
        for (int i = 0; i < spikes.size(); i++) if (spikes.get(i).target == target) return true;
        return false;
    }

    /** Detonates every spike embedded in the target (called on an energy weapon hit). */
    public void detonateSpikes(ShipAPI target) {
        for (int i = spikes.size() - 1; i >= 0; i--) {
            Attached a = spikes.get(i);
            if (a.target != target) continue;
            spikes.remove(i);
            Vector2f p = a.world(new Vector2f());
            engine.applyDamage(target, p, SPIKE_DAMAGE, DamageType.ENERGY, 100f, true, false, a.source, true);
            engine.spawnExplosion(p, target.getVelocity(), RslUtil.TEAL, 70f, 0.4f);
            engine.addHitParticle(p, target.getVelocity(), 90f, 1f, 0.2f, RslUtil.WHITE);
        }
    }

    // ------------------------------------------------------------------------------------------------ frame
    @Override
    public void advance(float amount, List<InputEventAPI> events) {
        if (broken || engine == null || engine.isPaused()) return;
        try {
            float now = RslUtil.now();
            for (int i = dots.size() - 1; i >= 0; i--) {
                Attached a = dots.get(i);
                if (now > a.until || !RslUtil.alive(a.target)) {
                    dots.remove(i);
                    continue;
                }
                a.tick += amount;
                if (a.tick >= 0.25f) {
                    float dmg = a.amount * a.tick;
                    a.tick = 0f;
                    Vector2f p = a.world(tmp);
                    engine.applyDamage(a.target, new Vector2f(p), dmg, DamageType.ENERGY, 0f, true, false, a.source,
                            false);
                    engine.addHitParticle(new Vector2f(p), a.target.getVelocity(), 14f, 0.8f, 0.15f, RslUtil.TEAL);
                }
            }
            for (int i = spikes.size() - 1; i >= 0; i--) {
                Attached a = spikes.get(i);
                if (now > a.until || !RslUtil.alive(a.target)) spikes.remove(i);
            }
            RailFx.advanceProjectiles(engine, amount);
            chorus.advance(engine, amount);
            if (encore != null) encore.advance(engine, amount);
        } catch (Throwable t) {
            broken = true;
            log.error("Resonance Lattice combat plugin disabled after an error", t);
        }
    }
}
