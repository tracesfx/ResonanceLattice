package rsl.weapons;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.combat.BaseEveryFrameCombatPlugin;
import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.CombatEntityAPI;
import com.fs.starfarer.api.combat.DamageType;
import com.fs.starfarer.api.combat.DamagingProjectileAPI;
import com.fs.starfarer.api.combat.OnHitEffectPlugin;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.listeners.ApplyDamageResultAPI;
import com.fs.starfarer.api.input.InputEventAPI;
import org.lwjgl.util.vector.Vector2f;
import rsl.RslIds;
import rsl.combat.LatticeData;
import rsl.combat.RslUtil;

import java.awt.Color;
import java.util.List;

/**
 * Sforzando Lance (DESIGN.md 3.9):
 * <ul>
 * <li>+50% damage to fighters and frigates (both lances).</li>
 * <li>Skewer (full Virtuoso): a slug that hits hull or armor (not a shield) passes through at full damage and hits
 * whatever is behind it, up to {@link #MAX_PIERCE} ships in a row. It bores through the inside of the hull rather than
 * jumping to the far side: {@link SkewerFx} damages the armor along the path.</li>
 * <li>Accent (full Virtuoso; for 2 s after a Glissando, above 80% top speed, or in Bravura): every hit deals +50%
 * damage and arcs EMP into the nearest other enemy within 250 units.</li>
 * </ul>
 */
public class SforzandoOnHit implements OnHitEffectPlugin {
    public static final float SMALL_BONUS = 0.5f;
    static final Color GOLD_WHITE = new Color(255, 245, 210, 255);
    /** Ships one slug can pass through (each at full damage) before it stops. */
    public static final int MAX_PIERCE = 6;
    private static final String KEY_PIERCES = "rsl_sforzando_pierces";
    public static final float ACCENT_ARC_RANGE = 250f;
    /** Inside a skewered hull: every STEP units of path deal INTERNAL x the slug's damage to the armor there. */
    public static final float STEP = 25f;
    public static final float INTERNAL = 0.2f;
    public static final float ACCENT_DAMAGE = 0.5f;

    @Override
    public void onHit(DamagingProjectileAPI proj, CombatEntityAPI target, Vector2f point, boolean shieldHit,
                      ApplyDamageResultAPI result, CombatEngineAPI engine) {
        RailFx.impact(proj, target, point, shieldHit, engine);
        if (!(target instanceof ShipAPI)) return;
        ShipAPI t = (ShipAPI) target;
        ShipAPI src = proj.getSource();
        if (src == null) return;
        boolean small = t.isFighter() || t.isFrigate();
        if (small && !t.isHulk()) {
            engine.applyDamage(t, point, proj.getDamageAmount() * SMALL_BONUS, DamageType.ENERGY, 0f, false, false, src,
                    false);
        }
        String wid = proj.getWeapon() != null ? proj.getWeapon().getId() : null;
        if (!RslIds.WEAPON_SFORZANDO.equals(wid)) return;
        LatticeData d = LatticeData.get(src);
        boolean accent = d.bravura || RslUtil.now() < d.accentUntil
                || src.getVelocity().length() > src.getMaxSpeed() * 0.8f;
        if (accent && !t.isHulk()) {
            engine.applyDamage(t, point, proj.getDamageAmount() * ACCENT_DAMAGE, DamageType.ENERGY, 0f, false, false,
                    src, false);
        }
        // Skewer: a slug that strikes hull or armor (not a shield) bores straight through the ship - a fresh slug
        // carries on from the impact point, tearing the armor along its path inside the hull (SkewerFx) - and on
        // into whatever is behind, up to MAX_PIERCE ships in a row.
        Object o = proj.getCustomData().get(KEY_PIERCES);
        int pierced = o instanceof Integer ? (Integer) o : 0;
        if (!shieldHit && pierced < MAX_PIERCE && proj.getWeapon() != null) {
            double f = Math.toRadians(proj.getFacing());
            Vector2f from = new Vector2f(point.x + (float) Math.cos(f) * 4f, point.y + (float) Math.sin(f) * 4f);
            Object n = engine.spawnProjectile(src, proj.getWeapon(), proj.getWeapon().getId(), from, proj.getFacing(),
                    null);
            if (n instanceof DamagingProjectileAPI) {
                DamagingProjectileAPI next = (DamagingProjectileAPI) n;
                next.setDamageAmount(proj.getDamageAmount());
                next.addDamagedAlready(t);
                next.setCustomData(RslIds.KEY_PIERCED, Boolean.TRUE);
                next.setCustomData(KEY_PIERCES, pierced + 1);
                engine.addPlugin(new SkewerFx(next, t, from, src));
            }
        }
        if (accent) {
            ShipAPI other = RslUtil.nearestEnemy(src, point, ACCENT_ARC_RANGE, true, t);
            if (other != null) {
                engine.spawnEmpArc(src, point, null, other, DamageType.ENERGY, 60f, 250f, ACCENT_ARC_RANGE + 150f,
                        "system_emp_emitter_impact", 6f, d.bravura ? RslUtil.GOLD : RslUtil.VIOLET, RslUtil.WHITE);
            }
        }
    }

    /**
     * Follows one skewering slug while it is inside the ship it pierced: every {@link #STEP} units it travels in the
     * hull it deals {@link #INTERNAL} of its damage to the armor at that spot, with sparks. Ends when the slug leaves
     * the hull, dies, or after 1 second.
     */
    static class SkewerFx extends BaseEveryFrameCombatPlugin {
        private final DamagingProjectileAPI proj;
        private final ShipAPI target, src;
        private final Vector2f last;
        private float carried, age;
        private boolean entered;

        SkewerFx(DamagingProjectileAPI proj, ShipAPI target, Vector2f from, ShipAPI src) {
            this.proj = proj;
            this.target = target;
            this.src = src;
            this.last = new Vector2f(from);
        }

        @Override
        public void advance(float amount, List<InputEventAPI> events) {
            CombatEngineAPI engine = Global.getCombatEngine();
            if (engine == null || engine.isPaused()) return;
            age += amount;
            Vector2f p = proj.getLocation();
            boolean inside = !target.isHulk() && target.isPointInBounds(p);
            if (age > 1f || !engine.isEntityInPlay(proj) || (entered && !inside)) {
                if (entered) engine.addHitParticle(new Vector2f(p), target.getVelocity(), 70f, 1f, 0.15f, GOLD_WHITE);
                engine.removePlugin(this);
                return;
            }
            if (inside) {
                entered = true;
                float dx = p.x - last.x, dy = p.y - last.y;
                float d = (float) Math.sqrt(dx * dx + dy * dy);
                carried += d;
                while (carried >= STEP && d > 0f) {
                    carried -= STEP;
                    float k = 1f - carried / d;
                    Vector2f at = new Vector2f(last.x + dx * k, last.y + dy * k);
                    engine.applyDamage(target, at, proj.getDamageAmount() * INTERNAL, DamageType.ENERGY, 0f, true,
                            false, src, false);
                    engine.addHitParticle(at, target.getVelocity(), 30f, 1f, 0.12f, GOLD_WHITE);
                    for (int i = 0; i < 3; i++) {
                        Vector2f v = new Vector2f(target.getVelocity());
                        v.x += (float) (Math.random() - 0.5) * 300f;
                        v.y += (float) (Math.random() - 0.5) * 300f;
                        engine.addHitParticle(at, v, 4f, 1f, 0.3f + 0.3f * (float) Math.random(), RslUtil.GOLD);
                    }
                }
            }
            last.set(p);
        }
    }
}
