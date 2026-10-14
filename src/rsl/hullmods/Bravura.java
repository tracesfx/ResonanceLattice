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

import org.lwjgl.util.vector.Vector2f;

import java.awt.Color;

/**
 * Virtuoso: at 100% CR the ship enters Bravura (hysteresis down to 92%). Colour scheme (user, 2026-10-13): teal
 * normally, white in Bravura - the glow renderer cross-fades the seams to the white sprite, the wing vanes flare and the
 * shield turns white, all from {@link LatticeData#bravuraLevel}. The transition is an event: entering flares the seams
 * far past full brightness, then they cool to the Bravura glow ({@link LatticeData#bravuraFlash}), with a white
 * shockwave and a rising chord; leaving vents teal heat with a falling one ({@link LatticeData#bravuraCool}).
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
    /** Bravura shield: white. */
    private static final Color SHIELD_INNER = new Color(225, 235, 250, 90);
    private static final Color SHIELD_RING = new Color(250, 252, 255, 255);
    public static final String SOUND_ON = "rsl_bravura_on";
    public static final String SOUND_OFF = "rsl_bravura_off";
    private static final Color VENT = new Color(120, 225, 215, 110);
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
        if (!d.bravura && cr >= (enh ? ENTER_ENHANCED : ENTER)) {
            d.bravura = true;
            enterFx(ship, d, engine);
            // the Concertmaster at the helm of the Virtuoso (CAMPAIGN.md section 9): once per battle
            if (rsl.combat.ChorusEffects.isConcertmaster(ship.getCaptain())
                    && ship.getCustomData().get("rsl_odile_said") == null) {
                ship.setCustomData("rsl_odile_said", true);
                engine.addFloatingText(ship.getLocation(), "She is in tune at last.", 32f, java.awt.Color.WHITE, ship,
                        1f, 3f);
            }
        }
        else if (d.bravura && cr < (enh ? EXIT_ENHANCED : EXIT)) {
            d.bravura = false;
            exitFx(ship, d, engine);
        }
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
        if (d.bravuraFlash > 0.05f) {   // the hull shivers with light while the seams flare (renderer decays it)
            ship.setJitterUnder(STATUS, RslUtil.BRAVURA_WHITE, d.bravuraFlash * d.bravuraFlash, 10, 0f,
                    16f * d.bravuraFlash);
        }
        holdCharges(ship.getSystem(), d.bravura);
        tintShield(ship.getShield(), d);
    }

    /**
     * Entering Bravura: the seams flare (renderer), a white shockwave rings out from the hull, motes are flung off the
     * sash, the hull shivers with light for a moment, and a rising chord plays. Not at deployment (a ship that starts
     * the battle in Bravura simply is in it).
     */
    private static void enterFx(ShipAPI ship, LatticeData d, CombatEngineAPI engine) {
        if (ship.getFullTimeDeployed() < 1f) {
            d.bravuraLevel = 1f;   // deployed at full CR: already singing, no fanfare
            return;
        }
        d.bravuraFlash = 1f;
        d.bravuraCool = 0f;
        Vector2f loc = ship.getLocation();
        Vector2f vel = ship.getVelocity();
        float r = ship.getCollisionRadius();
        Global.getSoundPlayer().playSound(SOUND_ON, 1f, 1f, loc, vel);
        engine.addHitParticle(loc, vel, r * 2.2f, 0.9f, 0.35f, RslUtil.BRAVURA_WHITE);
        engine.addSmoothParticle(loc, vel, r * 3.2f, 0.5f, 0.9f, RslUtil.BRAVURA_WHITE);
        // the shockwave: a ring of bright motes racing outward
        for (int i = 0; i < 36; i++) {
            double a = Math.PI * 2.0 * i / 36.0;
            float c = (float) Math.cos(a), s = (float) Math.sin(a);
            Vector2f p = new Vector2f(loc.x + c * r * 0.5f, loc.y + s * r * 0.5f);
            Vector2f v = new Vector2f(vel.x + c * 520f, vel.y + s * 520f);
            engine.addHitParticle(p, v, 14f, 1f, 0.55f, RslUtil.BRAVURA_WHITE);
        }
        for (int i = 0; i < 24; i++) {
            double a = Math.random() * Math.PI * 2.0;
            float sp = 60f + (float) Math.random() * 220f;
            Vector2f p = new Vector2f(loc.x + (float) (Math.random() - 0.5) * r * 0.8f,
                    loc.y + (float) (Math.random() - 0.5) * r * 0.8f);
            Vector2f v = new Vector2f(vel.x + (float) Math.cos(a) * sp, vel.y + (float) Math.sin(a) * sp);
            engine.addSmoothParticle(p, v, 5f + (float) Math.random() * 6f, 1f, 0.8f + (float) Math.random() * 0.8f,
                    RslUtil.BRAVURA_WHITE);
        }
        if (ship == engine.getPlayerShip()) {
            engine.addFloatingText(new Vector2f(loc.x, loc.y + r * 0.6f), "BRAVURA", 40f, RslUtil.BRAVURA_WHITE, ship,
                    0.5f, 1.5f);
        }
    }

    /** Leaving Bravura: the white burns off as teal heat venting from the hull, with a falling chord. */
    private static void exitFx(ShipAPI ship, LatticeData d, CombatEngineAPI engine) {
        d.bravuraFlash = 0f;
        d.bravuraCool = 1f;
        Vector2f loc = ship.getLocation();
        Vector2f vel = ship.getVelocity();
        float r = ship.getCollisionRadius();
        Global.getSoundPlayer().playSound(SOUND_OFF, 1f, 1f, loc, vel);
        for (int i = 0; i < 18; i++) {
            double a = Math.random() * Math.PI * 2.0;
            float sp = 40f + (float) Math.random() * 90f;
            Vector2f p = new Vector2f(loc.x + (float) (Math.random() - 0.5) * r * 0.7f,
                    loc.y + (float) (Math.random() - 0.5) * r * 0.7f);
            Vector2f v = new Vector2f(vel.x + (float) Math.cos(a) * sp, vel.y + (float) Math.sin(a) * sp);
            engine.addNebulaParticle(p, v, 40f + (float) Math.random() * 40f, 2f, 0.1f, 0.3f,
                    1.2f + (float) Math.random() * 0.8f, VENT);
        }
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
        Tip.good(t, "The seams, shield, Glissando and lances turn from teal to white.");
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
