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
 * <li>Cascade (full Virtuoso): a slug that destroys a fighter or frigate pierces on with 60% damage.</li>
 * <li>Accent (full Virtuoso; for 2 s after a Glissando, above 80% top speed, or in Bravura): a hit on hull pierces
 * as well, and every hit arcs EMP into the nearest other enemy within 250 units.</li>
 * </ul>
 */
public class SforzandoOnHit implements OnHitEffectPlugin {
    public static final float SMALL_BONUS = 0.5f;
    public static final float CASCADE_KEEP = 0.6f;
    public static final float ACCENT_ARC_RANGE = 250f;

    @Override
    public void onHit(DamagingProjectileAPI proj, CombatEntityAPI target, Vector2f point, boolean shieldHit,
                      ApplyDamageResultAPI result, CombatEngineAPI engine) {
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
        if (!RslIds.WEAPON_SFORZANDO.equals(wid) || proj.getCustomData().containsKey(RslIds.KEY_PIERCED)) return;
        LatticeData d = LatticeData.get(src);
        boolean accent = d.bravura || RslUtil.now() < d.accentUntil
                || src.getVelocity().length() > src.getMaxSpeed() * 0.8f;
        boolean killed = t.isHulk() || t.getHitpoints() <= 0f;
        if ((small && killed) || (accent && !shieldHit && !t.isFighter())) {
            PierceOnHit.continueThrough(proj, t, point, CASCADE_KEEP, engine);
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
