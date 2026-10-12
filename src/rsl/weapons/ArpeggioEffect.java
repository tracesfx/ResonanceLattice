package rsl.weapons;

import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.DamagingProjectileAPI;
import com.fs.starfarer.api.combat.OnFireEffectPlugin;
import com.fs.starfarer.api.combat.WeaponAPI;
import rsl.combat.RslUtil;

/** Arpeggio Pulser: the three notes of each burst deal 80% / 100% / 140% damage. */
public class ArpeggioEffect implements OnFireEffectPlugin {
    public static final float[] NOTES = {0.8f, 1.0f, 1.4f};
    public static final float NEW_BURST_GAP = 0.6f;

    @Override
    public void onFire(DamagingProjectileAPI proj, WeaponAPI weapon, CombatEngineAPI engine) {
        float now = RslUtil.now();
        float[] st = weapon.getCustom() instanceof float[] ? (float[]) weapon.getCustom() : new float[]{-100f, -1f};
        int note = now - st[0] > NEW_BURST_GAP ? 0 : ((int) st[1] + 1) % NOTES.length;
        st[0] = now;
        st[1] = note;
        weapon.setCustom(st);
        proj.setDamageAmount(proj.getDamageAmount() * NOTES[note]);
    }
}
