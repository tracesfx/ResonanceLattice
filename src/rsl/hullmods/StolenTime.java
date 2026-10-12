package rsl.hullmods;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.combat.BaseHullMod;
import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.ui.TooltipMakerAPI;
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
    /** CR restored for destroying a frigate / destroyer / cruiser / capital (not capped per target). */
    public static final float KILL_CR_FRIGATE = 0.05f;
    public static final float KILL_CR_DESTROYER = 0.08f;
    public static final float KILL_CR_CRUISER = 0.12f;
    public static final float KILL_CR_CAPITAL = 0.18f;
    /** Enhanced (story-pointed built-in): theft and kill refunds x this. */
    public static final float ENHANCED = 1.5f;

    public static boolean isFull(ShipAPI ship) {
        return RslIds.HULL_VIRTUOSO.equals(ship.getHullSpec().getHullId());
    }

    /** Takes up to {@code damage * rate} CR from {@code target} and gives it to {@code ship}. */
    public static void steal(ShipAPI ship, ShipAPI target, float damage) {
        if (ship == null || target == null || target.isFighter() || !RslUtil.isEnemy(ship, target)) return;
        CombatEngineAPI engine = Global.getCombatEngine();
        float amount = damage * CR_PER_DAMAGE * RslUtil.sizeMult(target);
        if (engine.getPlayerShip() != ship) amount *= AI_MULT;
        if (RslUtil.enhanced(ship, MOD_ID)) amount *= ENHANCED;
        stealAmount(ship, target, amount);
    }

    public static void stealAmount(ShipAPI ship, ShipAPI target, float amount) {
        Object o = target.getCustomData().get(RslIds.KEY_STOLEN);
        float taken = o instanceof Float ? (Float) o : 0f;
        amount = Math.min(amount, Math.min(CAP_PER_TARGET - taken, target.getCurrentCR()));
        if (amount <= 0f) return;
        target.setCustomData(RslIds.KEY_STOLEN, taken + amount);
        target.setCurrentCR(target.getCurrentCR() - amount);
        give(ship, amount);
        // a violet wisp from the victim to the thief
        if (Math.random() < 0.35) wisp(ship, target, 22f);
    }

    /** Called once when this ship lands the killing blow on an enemy ship (not fighters). */
    public static void onKill(ShipAPI ship, ShipAPI target) {
        if (ship == null || target == null || target.isFighter() || !RslUtil.isEnemy(ship, target)) return;
        float amount;
        switch (target.getHullSize()) {
            case CAPITAL_SHIP:
                amount = KILL_CR_CAPITAL;
                break;
            case CRUISER:
                amount = KILL_CR_CRUISER;
                break;
            case DESTROYER:
                amount = KILL_CR_DESTROYER;
                break;
            default:
                amount = KILL_CR_FRIGATE;
        }
        if (RslUtil.enhanced(ship, MOD_ID)) amount *= ENHANCED;
        give(ship, amount);
        for (int i = 0; i < 6; i++) wisp(ship, target, 40f);
    }

    /** Adds CR up to the cap; on the full Virtuoso the overflow extends peak performance time. */
    private static void give(ShipAPI ship, float amount) {
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
    }

    private static void wisp(ShipAPI ship, ShipAPI target, float size) {
        Vector2f vel = new Vector2f(ship.getLocation().x - target.getLocation().x,
                ship.getLocation().y - target.getLocation().y);
        vel.scale(0.6f + 0.4f * (float) Math.random());
        Global.getCombatEngine().addSmoothParticle(new Vector2f(target.getLocation()), vel, size, 0.9f, 1.1f,
                RslUtil.VIOLET);
    }

    @Override
    public void addPostDescriptionSection(TooltipMakerAPI t, HullSize hullSize, ShipAPI ship, float width,
                                          boolean isForModSpec) {
        Tip.section(t, "Theft");
        Tip.good(t, "Hull and armor damage dealt to enemy ships steals about %s combat readiness per %s damage "
                + "(scaled by the target's size): the target loses it, this ship gains it.", "1%", "600");
        Tip.good(t, "At most %s can be taken from any one ship.", Tip.pct(CAP_PER_TARGET));
        Tip.section(t, "The kill");
        Tip.good(t, "Destroying an enemy ship restores %s / %s / %s / %s combat readiness at once (frigate to "
                + "capital).", Tip.pct(KILL_CR_FRIGATE), Tip.pct(KILL_CR_DESTROYER), Tip.pct(KILL_CR_CRUISER),
                Tip.pct(KILL_CR_CAPITAL));
        Tip.good(t, "On the full Virtuoso, CR gained above 100%% extends peak performance time instead (%s per 1%%).",
                (int) PEAK_SECONDS_PER_PERCENT + " seconds");
        Tip.badSection(t, "Limits");
        Tip.bad(t, "Theft (not kill refunds) is %s as effective when the ship is not piloted by the player.",
                "half");
        Tip.end(t);
    }

    @Override
    public String getSModDescriptionParam(int index, HullSize hullSize) {
        return index == 0 ? Tip.pct(ENHANCED - 1f) : null;
    }
}
