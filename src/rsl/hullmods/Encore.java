package rsl.hullmods;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.combat.BaseHullMod;
import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import com.fs.starfarer.api.combat.listeners.AdvanceableListener;
import com.fs.starfarer.api.combat.listeners.HullDamageAboutToBeTakenListener;
import com.fs.starfarer.api.ui.TooltipMakerAPI;
import org.lwjgl.util.vector.Vector2f;
import rsl.combat.LatticeData;
import rsl.combat.RslUtil;

import java.util.List;

/**
 * Encore, the reward for ending the Silence (rsl.campaign.RequiemIntel), built into the player's Virtuoso as a
 * permanent mod. Once per battle, a blow that would disable the ship is refused (as vanilla's Phase Anchor refuses one
 * through HullDamageAboutToBeTakenListener): for {@link #TIME} seconds the ship takes no damage, its hull climbs back
 * to {@link #HEAL} of maximum, and its readiness is restored to full - straight into Bravura.
 */
public class Encore extends BaseHullMod {
    public static final float TIME = 3f;
    public static final float HEAL = 0.4f;
    public static final String SOUND = "rsl_encore";
    private static final String MOD_ID = "rsl_encore";

    @Override
    public void applyEffectsAfterShipCreation(ShipAPI ship, String id) {
        if (!ship.hasListenerOfClass(Script.class)) ship.addListener(new Script(ship));
    }

    /** True while this ship's Encore can still (or right now does) refuse a lethal blow. */
    public static boolean saves(ShipAPI ship) {
        if (ship == null || !ship.hasListenerOfClass(Script.class)) return false;
        List<Script> l = ship.getListeners(Script.class);
        for (int i = 0; i < l.size(); i++) {
            Script s = l.get(i);
            if (!s.used || s.left > 0f) return true;
        }
        return false;
    }

    public static class Script implements AdvanceableListener, HullDamageAboutToBeTakenListener {
        final ShipAPI ship;
        boolean used;
        float left, healPerSecond;

        Script(ShipAPI ship) {
            this.ship = ship;
        }

        @Override
        public boolean notifyAboutToTakeHullDamage(Object param, ShipAPI s, Vector2f point, float damageAmount) {
            if (left > 0f) return true;
            if (used || damageAmount < ship.getHitpoints()) return false;
            used = true;
            left = TIME;
            ship.setHitpoints(1f);
            healPerSecond = (ship.getMaxHitpoints() * HEAL - 1f) / TIME;
            ship.setCurrentCR(Math.max(ship.getCurrentCR(), 1f));
            CombatEngineAPI engine = Global.getCombatEngine();
            Vector2f loc = ship.getLocation();
            Global.getSoundPlayer().playSound(SOUND, 1f, 1f, loc, ship.getVelocity());
            engine.addHitParticle(loc, ship.getVelocity(), ship.getCollisionRadius() * 3f, 1f, 0.6f,
                    RslUtil.BRAVURA_WHITE);
            engine.addFloatingTextAlways(loc, "Encore!", 40f, RslUtil.BRAVURA_WHITE, ship, 16f, 3.2f, 1f, 0f, 0f, 1f);
            LatticeData.get(ship).bravuraFlash = 1f;
            return true;
        }

        @Override
        public void advance(float amount) {
            MutableShipStatsAPI st = ship.getMutableStats();
            if (left <= 0f) return;
            left -= amount;
            if (left <= 0f) {
                st.getHullDamageTakenMult().unmodify(MOD_ID);
                st.getArmorDamageTakenMult().unmodify(MOD_ID);
                st.getEmpDamageTakenMult().unmodify(MOD_ID);
                return;
            }
            st.getHullDamageTakenMult().modifyMult(MOD_ID, 0f);
            st.getArmorDamageTakenMult().modifyMult(MOD_ID, 0f);
            st.getEmpDamageTakenMult().modifyMult(MOD_ID, 0f);
            ship.setHitpoints(Math.min(ship.getMaxHitpoints(), ship.getHitpoints() + healPerSecond * amount));
            ship.setJitter(MOD_ID, RslUtil.BRAVURA_WHITE, left / TIME, 8, 0f, 20f);
        }
    }

    @Override
    public void addPostDescriptionSection(TooltipMakerAPI t, HullSize hullSize, ShipAPI ship, float width,
                                          boolean isForModSpec) {
        Tip.section(t, "Once per battle");
        Tip.good(t, "A blow that would disable the ship is refused. For %s seconds it takes no damage and its hull "
                + "climbs back to %s.", "" + (int) TIME, Tip.pct(HEAL));
        Tip.good(t, "Combat readiness is restored to %s: the Virtuoso enters Bravura.", "100%");
        Tip.note(t, "Taken from the heart of the Silence. Nothing else in the Sector sings after the end.");
        Tip.end(t);
    }
}
