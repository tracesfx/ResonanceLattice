package rsl.weapons;

import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.CombatEntityAPI;
import com.fs.starfarer.api.combat.DamageType;
import com.fs.starfarer.api.combat.DamagingProjectileAPI;
import com.fs.starfarer.api.combat.OnHitEffectPlugin;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.listeners.ApplyDamageResultAPI;
import org.lwjgl.util.vector.Vector2f;
import rsl.RslIds;
import rsl.combat.LatticeData;
import rsl.combat.RslUtil;

/**
 * Sforzando Lance (DESIGN.md 3.9):
 * <ul>
 * <li>+50% damage to fighters and frigates (both lances).</li>
 * <li>Skewer (full Virtuoso): a slug that hits hull or armor (not a shield) passes through at full damage and hits
 * whatever is behind it, up to {@link #MAX_PIERCE} ships in a row.</li>
 * <li>Accent (full Virtuoso; for 2 s after a Glissando, above 80% top speed, or in Bravura): every hit deals +50%
 * damage and arcs EMP into the nearest other enemy within 250 units.</li>
 * </ul>
 */
public class SforzandoOnHit implements OnHitEffectPlugin {
    public static final float SMALL_BONUS = 0.5f;
    /** Ships one slug can pass through (each at full damage) before it stops. */
    public static final int MAX_PIERCE = 6;
    private static final String KEY_PIERCES = "rsl_sforzando_pierces";
    public static final float ACCENT_ARC_RANGE = 250f;
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
        // Skewer: a slug that strikes hull or armor (not a shield) goes straight through at full damage and carries
        // on into whatever is behind, up to MAX_PIERCE ships in a row.
        Object o = proj.getCustomData().get(KEY_PIERCES);
        int pierced = o instanceof Integer ? (Integer) o : 0;
        if (!shieldHit && pierced < MAX_PIERCE) {
            DamagingProjectileAPI next = PierceOnHit.continueThrough(proj, t, point, 1f, engine);
            if (next != null) next.setCustomData(KEY_PIERCES, pierced + 1);
        }
        if (accent) {
            ShipAPI other = RslUtil.nearestEnemy(src, point, ACCENT_ARC_RANGE, true, t);
            if (other != null) {
                engine.spawnEmpArc(src, point, null, other, DamageType.ENERGY, 60f, 250f, ACCENT_ARC_RANGE + 150f,
                        "system_emp_emitter_impact", 6f, d.bravura ? RslUtil.GOLD : RslUtil.VIOLET, RslUtil.WHITE);
            }
        }
    }
}
