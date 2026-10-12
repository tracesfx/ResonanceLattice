package rsl.hullmods;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.combat.BaseHullMod;
import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShieldAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.ShipSystemAPI;
import com.fs.starfarer.api.ui.TooltipMakerAPI;
import rsl.RslIds;
import rsl.combat.LatticeData;
import rsl.combat.RslUtil;
import rsl.weapons.SforzandoOnHit;

import java.awt.Color;

/**
 * Virtuoso: at 100% CR the ship enters Bravura (hysteresis down to 92%). The glow renderer cross-fades the seams to
 * the gold sprite, the wing vanes flare and the shield turns white-teal, all from {@link LatticeData#bravuraLevel}.
 * Locked on the Unsung.
 *
 * Also carries the full Virtuoso's base tuning (applied before ship creation, so refit stat cards show it): a fast
 * shield. (EMP resistance lives in {@link ConcertPitch}.)
 */
public class Bravura extends BaseHullMod {
    public static final float ENTER = 0.995f;
    public static final float EXIT = 0.92f;
    /** Enhanced (story-pointed built-in): Bravura starts and ends lower. */
    public static final float ENTER_ENHANCED = 0.95f;
    public static final float EXIT_ENHANCED = 0.87f;
    public static final float SPEED = 20f;
    public static final float FLUX = 75f;
    public static final float ROF = 50f;
    public static final float SHIELD_DAMAGE = 20f;
    public static final float SYSTEM_REGEN = 100f;
    /** Glissando charges in Bravura; outside it the ship is held one charge below this. */
    public static final int CHARGES = 3;
    /** Hull repaired per second in Bravura, as a fraction of maximum hull. */
    public static final float HULL_REGEN = 0.005f;
    /** Virtuoso base: shield turn rate and shield raise (unfold) rate multipliers. */
    public static final float SHIELD_RATE_MULT = 2f;
    public static final float SHIELD_UNFOLD_MULT = 3f;
    /** Bravura shield: white-teal, mostly white. */
    private static final Color SHIELD_INNER = new Color(205, 245, 240, 90);
    private static final Color SHIELD_RING = new Color(240, 255, 252, 255);
    private static final String ID = "rsl_bravura";
    private static final Object STATUS = new Object();

    @Override
    public void applyEffectsBeforeShipCreation(HullSize hullSize, MutableShipStatsAPI stats, String id) {
        if (stats.getVariant() == null || !RslIds.HULL_VIRTUOSO.equals(stats.getVariant().getHullSpec().getHullId())) {
            return;
        }
        stats.getShieldTurnRateMult().modifyMult(id, SHIELD_RATE_MULT);
        stats.getShieldUnfoldRateMult().modifyMult(id, SHIELD_UNFOLD_MULT);
    }

    @Override
    public void advanceInCombat(ShipAPI ship, float amount) {
        CombatEngineAPI engine = Global.getCombatEngine();
        if (engine == null || !ship.isAlive() || !StolenTime.isFull(ship)) return;
        LatticeData d = LatticeData.get(ship);
        float cr = ship.getCurrentCR();
        boolean enh = RslUtil.enhanced(ship, ID);
        if (!d.bravura && cr >= (enh ? ENTER_ENHANCED : ENTER)) d.bravura = true;
        else if (d.bravura && cr < (enh ? EXIT_ENHANCED : EXIT)) d.bravura = false;
        MutableShipStatsAPI s = ship.getMutableStats();
        if (d.bravura) {
            s.getMaxSpeed().modifyPercent(ID, SPEED);
            s.getAcceleration().modifyPercent(ID, SPEED);
            s.getDeceleration().modifyPercent(ID, SPEED);
            s.getMaxTurnRate().modifyPercent(ID, SPEED);
            s.getTurnAcceleration().modifyPercent(ID, SPEED);
            s.getFluxDissipation().modifyPercent(ID, FLUX);
            s.getEnergyRoFMult().modifyPercent(ID, ROF);
            s.getDamageToTargetShieldsMult().modifyPercent(ID, SHIELD_DAMAGE);
            s.getSystemRegenBonus().modifyPercent(ID, SYSTEM_REGEN);
            if (!engine.isPaused() && ship.getHitpoints() < ship.getMaxHitpoints()) {
                ship.setHitpoints(Math.min(ship.getMaxHitpoints(),
                        ship.getHitpoints() + ship.getMaxHitpoints() * HULL_REGEN * amount));
            }
            if (ship == engine.getPlayerShip()) {
                engine.maintainStatusForPlayerShip(STATUS, "graphics/rsl/icons/hullmods/rsl_bravura.png", "BRAVURA",
                        "full voice: faster, hotter, every lance accented", false);
            }
        } else {
            s.getMaxSpeed().unmodify(ID);
            s.getAcceleration().unmodify(ID);
            s.getDeceleration().unmodify(ID);
            s.getMaxTurnRate().unmodify(ID);
            s.getTurnAcceleration().unmodify(ID);
            s.getFluxDissipation().unmodify(ID);
            s.getEnergyRoFMult().unmodify(ID);
            s.getDamageToTargetShieldsMult().unmodify(ID);
            s.getSystemRegenBonus().unmodify(ID);
        }
        holdCharges(ship.getSystem(), d.bravura);
        tintShield(ship.getShield(), d);
    }

    /** The .system has CHARGES uses; outside Bravura the last one is held back (it cannot refill or be kept). */
    private static void holdCharges(ShipSystemAPI sys, boolean bravura) {
        if (sys == null || bravura) return;
        int cap = Math.min(sys.getMaxAmmo(), CHARGES) - 1;
        if (sys.getAmmo() >= cap) {
            if (sys.getAmmo() > cap) sys.setAmmo(cap);
            sys.setAmmoReloadProgress(0f);
        }
    }

    private static void tintShield(ShieldAPI shield, LatticeData d) {
        if (shield == null) return;
        if (d.shieldInner == null) {
            d.shieldInner = shield.getInnerColor();
            d.shieldRing = shield.getRingColor();
        }
        float t = Math.max(0f, Math.min(1f, d.bravuraLevel));
        shield.setInnerColor(mix(d.shieldInner, SHIELD_INNER, t));
        shield.setRingColor(mix(d.shieldRing, SHIELD_RING, t));
    }

    private static Color mix(Color a, Color b, float t) {
        if (t <= 0.001f) return a;
        return new Color(Math.round(a.getRed() + (b.getRed() - a.getRed()) * t),
                Math.round(a.getGreen() + (b.getGreen() - a.getGreen()) * t),
                Math.round(a.getBlue() + (b.getBlue() - a.getBlue()) * t),
                Math.round(a.getAlpha() + (b.getAlpha() - a.getAlpha()) * t));
    }

    @Override
    public void addPostDescriptionSection(TooltipMakerAPI t, HullSize hullSize, ShipAPI ship, float width,
                                          boolean isForModSpec) {
        addEffects(t);
    }

    /** The Bravura effect list (also shown, greyed, by the Unsung's Bravura (Silent)). */
    static void addEffects(TooltipMakerAPI t) {
        Tip.section(t, "Entering Bravura");
        Tip.good(t, "At %s combat readiness; lasts until CR drops below %s.", "100%", Tip.pct(EXIT));
        Tip.section(t, "In Bravura");
        Tip.good(t, "%s top speed and maneuverability.", "+" + (int) SPEED + "%");
        Tip.good(t, "%s flux dissipation, %s energy weapon rate of fire.", "+" + (int) FLUX + "%",
                "+" + (int) ROF + "%");
        Tip.good(t, "%s damage to shields.", "+" + (int) SHIELD_DAMAGE + "%");
        Tip.good(t, "%s faster system recharge, %s Glissando charges.", (int) SYSTEM_REGEN + "%", "" + CHARGES);
        Tip.good(t, "The Sforzando lances are always Accented: %s damage.",
                "+" + (int) (SforzandoOnHit.ACCENT_DAMAGE * 100f) + "%");
        Tip.good(t, "The hull repairs %s of its maximum per second.", Tip.pct(HULL_REGEN));
        Tip.good(t, "The seams burn gold-white and the shield turns white-teal.");
        Tip.section(t, "Always (Virtuoso hull)");
        Tip.good(t, "Shield turn rate %s, shield raise rate %s.", "x" + (int) SHIELD_RATE_MULT,
                "x" + (int) SHIELD_UNFOLD_MULT);
        Tip.end(t);
    }

    @Override
    public String getSModDescriptionParam(int index, HullSize hullSize) {
        if (index == 0) return Tip.pct(ENTER_ENHANCED);
        if (index == 1) return Tip.pct(EXIT_ENHANCED);
        return null;
    }

}
