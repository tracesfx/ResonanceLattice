package rsl.hullmods;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.combat.BaseHullMod;
import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import org.lwjgl.util.vector.Vector2f;
import rsl.RslIds;
import rsl.combat.LatticeData;
import rsl.combat.RslUtil;

/**
 * Virtuoso / Unsung: hull and armor damage dealt to enemy ships steals combat readiness (DESIGN.md 3.9).
 * {@link #steal} is called from {@link rsl.combat.RslDamageListener} and from the Glissando string.
 * The full Virtuoso may climb to 100% CR, and CR stolen beyond that extends peak performance time; the Unsung
 * stops at the CR it deployed with.
 */
public class StolenTime extends BaseHullMod {
    public static final float CR_PER_DAMAGE = 0.01f / 600f;
    public static final float CAP_PER_TARGET = 0.25f;
    public static final float PEAK_SECONDS_PER_PERCENT = 4f;
    public static final float AI_MULT = 0.5f;
    public static final String MOD_ID = "rsl_stolen_time";

    public static boolean isFull(ShipAPI ship) {
        return RslIds.HULL_VIRTUOSO.equals(ship.getHullSpec().getHullId());
    }

    /** Takes up to {@code damage * rate} CR from {@code target} and gives it to {@code ship}. */
    public static void steal(ShipAPI ship, ShipAPI target, float damage) {
        if (ship == null || target == null || target.isFighter() || !RslUtil.isEnemy(ship, target)) return;
        CombatEngineAPI engine = Global.getCombatEngine();
        float amount = damage * CR_PER_DAMAGE * RslUtil.sizeMult(target);
        if (engine.getPlayerShip() != ship) amount *= AI_MULT;
        stealAmount(ship, target, amount);
    }

    public static void stealAmount(ShipAPI ship, ShipAPI target, float amount) {
        Object o = target.getCustomData().get(RslIds.KEY_STOLEN);
        float taken = o instanceof Float ? (Float) o : 0f;
        amount = Math.min(amount, Math.min(CAP_PER_TARGET - taken, target.getCurrentCR()));
        if (amount <= 0f) return;
        target.setCustomData(RslIds.KEY_STOLEN, taken + amount);
        target.setCurrentCR(target.getCurrentCR() - amount);

        float cap = isFull(ship) ? 1f : Math.max(ship.getCRAtDeployment(), 0.7f);
        float cr = ship.getCurrentCR();
        float room = Math.max(0f, cap - cr);
        float gained = Math.min(room, amount);
        ship.setCurrentCR(cr + gained);
        float overflow = amount - gained;
        if (overflow > 0f && isFull(ship)) {
            LatticeData d = LatticeData.get(ship);
            d.peakBonus += overflow * 100f * PEAK_SECONDS_PER_PERCENT;
            ship.getMutableStats().getPeakCRDuration().modifyFlat(MOD_ID, d.peakBonus);
        }
        // a violet wisp from the victim to the thief
        CombatEngineAPI engine = Global.getCombatEngine();
        if (Math.random() < 0.35) {
            Vector2f vel = new Vector2f(ship.getLocation().x - target.getLocation().x,
                    ship.getLocation().y - target.getLocation().y);
            vel.scale(0.9f);
            engine.addSmoothParticle(new Vector2f(target.getLocation()), vel, 22f, 0.9f, 1.1f, RslUtil.VIOLET);
        }
    }

    @Override
    public String getDescriptionParam(int index, HullSize hullSize) {
        switch (index) {
            case 0:
                return "1%";
            case 1:
                return "600";
            case 2:
                return (int) (CAP_PER_TARGET * 100f) + "%";
            case 3:
                return (int) PEAK_SECONDS_PER_PERCENT + " seconds";
            default:
                return null;
        }
    }
}
