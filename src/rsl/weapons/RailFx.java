package rsl.weapons;

import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.CombatEntityAPI;
import com.fs.starfarer.api.combat.DamagingProjectileAPI;
import com.fs.starfarer.api.combat.MissileAPI;
import com.fs.starfarer.api.combat.ShieldAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.ViewportAPI;
import org.lwjgl.util.vector.Vector2f;
import rsl.RslIds;
import rsl.combat.RslUtil;

import java.awt.Color;
import java.util.List;

/**
 * Shared visuals and sounds of the Lattice rail weapons (the faction's weapon doctrine: long-range, high-velocity
 * slugs). Trails come from MagicLib (data/config/modFiles/magicTrail_data.csv); this class adds:
 * <ul>
 * <li>{@link #impact}: called from every rail projectile's on-hit. Shields ring - a flash, a ripple of light running
 * along the shield's curve and a spray of glints back towards the shooter; hull and armor crack - sparks, a molten
 * spatter and a puff of crystal dust (the game's own hit sounds play as usual).</li>
 * <li>{@link #advanceProjectiles}: called once per frame by the combat plugin. A fresh slug kicks two vent jets out
 * of the muzzle sideways; slugs in flight shed small glinting motes.</li>
 * </ul>
 * Everything scales with the slug's damage, so a Harmonic Driver bolt lands much harder than a Chime tick.
 */
public final class RailFx {
    private RailFx() {
    }

    private static final Color SPARK = new Color(255, 230, 190, 255);
    private static final Color DUST = new Color(150, 210, 210, 120);
    private static final Color RIPPLE = new Color(140, 245, 235, 255);
    private static final Color MOTE = new Color(120, 240, 230, 200);
    private static final Color VENT = new Color(170, 230, 255, 160);
    private static final float MOTE_INTERVAL = 0.04f;
    private static float moteTimer;

    /** 0.4 (PD tick) .. ~3 (heavy driver): visual and sound weight of a hit. */
    private static float weight(DamagingProjectileAPI proj) {
        float d = proj.getBaseDamageAmount();
        return Math.max(0.4f, Math.min(3f, (float) Math.sqrt(d / 100f)));
    }

    private static boolean visible(CombatEngineAPI engine, Vector2f p, float r) {
        ViewportAPI v = engine.getViewport();
        return v == null || v.isNearViewport(p, r);
    }

    public static void impact(DamagingProjectileAPI proj, CombatEntityAPI target, Vector2f point, boolean shieldHit,
                              CombatEngineAPI engine) {
        impact(proj, target, point, shieldHit, engine, 1f, 1f);
    }

    /** As {@link #impact}, with the hull-hit glow scaled (radius x hullSize, brightness x hullBright). */
    public static void impact(DamagingProjectileAPI proj, CombatEntityAPI target, Vector2f point, boolean shieldHit,
                              CombatEngineAPI engine, float hullSize, float hullBright) {
        if (engine == null || point == null || target instanceof MissileAPI) return;
        float w = weight(proj);
        if (!visible(engine, point, 200f * w)) return;
        Vector2f tv = target.getVelocity();
        double back = Math.toRadians(proj.getFacing() + 180f);
        if (shieldHit && target instanceof ShipAPI && ((ShipAPI) target).getShield() != null) {
            shieldRing(((ShipAPI) target).getShield(), point, tv, back, w, engine);
        } else {
            hullCrack(point, tv, back, w, hullSize, hullBright, engine);
        }
    }

    private static void shieldRing(ShieldAPI shield, Vector2f point, Vector2f tv, double back, float w,
                                   CombatEngineAPI engine) {
        engine.addHitParticle(point, tv, 18f * w, 0.6f, 0.1f, RslUtil.WHITE);
        engine.addSmoothParticle(point, tv, 34f * w, 0.3f, 0.25f, RslUtil.TEAL);
        // the ripple: motes placed on the shield circle either side of the impact, sliding away along it
        Vector2f c = shield.getLocation();
        float r = shield.getRadius();
        double a0 = Math.atan2(point.y - c.y, point.x - c.x);
        int n = 3 + Math.round(2f * w);
        for (int i = 1; i <= n; i++) {
            for (int side = -1; side <= 1; side += 2) {
                double a = a0 + side * i * (0.045 + 0.01 * w);
                Vector2f p = new Vector2f(c.x + (float) Math.cos(a) * r, c.y + (float) Math.sin(a) * r);
                float speed = 60f + 40f * w;
                Vector2f v = new Vector2f(tv.x - (float) Math.sin(a) * side * speed,
                        tv.y + (float) Math.cos(a) * side * speed);
                engine.addHitParticle(p, v, (6f + 3f * w) * (1f - i / (n + 2f)), 0.5f, 0.06f * i + 0.12f, RIPPLE);
            }
        }
        // glints thrown back towards the shooter
        int g = 2 + Math.round(1.5f * w);
        for (int i = 0; i < g; i++) {
            double a = back + (Math.random() - 0.5) * 1.4;
            float s = 120f + (float) Math.random() * 220f * w;
            Vector2f v = new Vector2f(tv.x + (float) Math.cos(a) * s, tv.y + (float) Math.sin(a) * s);
            engine.addHitParticle(point, v, 3f + 1.5f * w, 0.7f, 0.2f + 0.15f * (float) Math.random(), RslUtil.WHITE);
        }
    }

    private static void hullCrack(Vector2f point, Vector2f tv, double back, float w, float gs, float gb,
                                  CombatEngineAPI engine) {
        engine.addHitParticle(point, tv, 16f * w * gs, 0.6f * gb, 0.08f, SPARK);
        engine.addSmoothParticle(point, tv, 28f * w * gs, 0.3f * gb, 0.2f, RslUtil.TEAL);
        int n = 3 + Math.round(2.5f * w);
        for (int i = 0; i < n; i++) {
            double a = back + (Math.random() - 0.5) * 2.2;
            float s = 80f + (float) Math.random() * 260f * w;
            Vector2f v = new Vector2f(tv.x + (float) Math.cos(a) * s, tv.y + (float) Math.sin(a) * s);
            engine.addHitParticle(point, v, 2f + 1.5f * w * (float) Math.random(), 0.8f, 0.25f + 0.3f * (float) Math.random(),
                    i % 3 == 0 ? RslUtil.TEAL : SPARK);
        }
        engine.addNebulaSmokeParticle(point, tv, 10f * w, 1.8f, 0.1f, 0.2f, 0.7f + 0.2f * w, DUST);
    }

    /** Per frame (from {@link rsl.combat.RslCombatPlugin}): muzzle vent jets on new slugs, motes on slugs in flight. */
    public static void advanceProjectiles(CombatEngineAPI engine, float amount) {
        moteTimer += amount;
        boolean motes = moteTimer >= MOTE_INTERVAL;
        if (motes) moteTimer = 0f;
        List<DamagingProjectileAPI> projs = engine.getProjectiles();
        for (int i = 0; i < projs.size(); i++) {
            DamagingProjectileAPI p = projs.get(i);
            if (p instanceof MissileAPI || p.isFading() || p.didDamage()) continue;
            String id = p.getProjectileSpecId();
            if (id == null || !id.startsWith("rsl_")) continue;
            if (!visible(engine, p.getLocation(), 100f)) continue;
            float w = weight(p);
            if (p.getElapsed() <= amount + 0.001f) {
                if (!p.getCustomData().containsKey(RslIds.KEY_PIERCED)) vent(engine, p, w);   // not mid-air pierces
            }
            else if (motes && Math.random() < 0.35f * w) {
                Vector2f v = new Vector2f(p.getVelocity());
                v.scale(0.08f);
                v.x += (float) (Math.random() - 0.5) * 40f;
                v.y += (float) (Math.random() - 0.5) * 40f;
                engine.addSmoothParticle(new Vector2f(p.getLocation()), v, 4f + 3f * w, 0.8f,
                        0.35f + 0.3f * (float) Math.random(), MOTE);
            }
        }
    }

    private static void vent(CombatEngineAPI engine, DamagingProjectileAPI p, float w) {
        Vector2f sv = p.getSource() != null ? p.getSource().getVelocity() : new Vector2f();
        double f = Math.toRadians(p.getFacing());
        for (int side = -1; side <= 1; side += 2) {
            double a = f + side * Math.PI * 0.5 + (Math.random() - 0.5) * 0.4;
            float s = 50f + 40f * w;
            Vector2f v = new Vector2f(sv.x + (float) Math.cos(a) * s, sv.y + (float) Math.sin(a) * s);
            engine.addNebulaParticle(new Vector2f(p.getLocation()), v, 10f * w, 1.8f, 0.05f, 0.2f, 0.45f, VENT);
        }
        engine.addHitParticle(new Vector2f(p.getLocation()), sv, 16f * w, 0.7f, 0.05f, RslUtil.WHITE);
    }
}
