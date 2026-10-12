package rsl.weapons;

import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.CombatEntityAPI;
import com.fs.starfarer.api.combat.DamagingProjectileAPI;
import com.fs.starfarer.api.combat.OnHitEffectPlugin;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.listeners.ApplyDamageResultAPI;
import org.lwjgl.util.vector.Vector2f;
import rsl.combat.RslCombatPlugin;

/** Tuning Spike: embeds in hull/armor; RslDamageListener detonates it on the next energy weapon hit on that ship. */
public class TuningSpikeOnHit implements OnHitEffectPlugin {
    @Override
    public void onHit(DamagingProjectileAPI proj, CombatEntityAPI target, Vector2f point, boolean shieldHit,
                      ApplyDamageResultAPI result, CombatEngineAPI engine) {
        if (shieldHit || !(target instanceof ShipAPI) || ((ShipAPI) target).isFighter()) return;
        RslCombatPlugin p = RslCombatPlugin.get();
        if (p != null) p.embedSpike((ShipAPI) target, proj.getSource(), point, proj.getFacing());
    }
}
