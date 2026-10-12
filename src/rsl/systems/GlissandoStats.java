package rsl.systems;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.combat.BaseEveryFrameCombatPlugin;
import com.fs.starfarer.api.graphics.SpriteAPI;
import com.fs.starfarer.api.combat.ViewportAPI;
import com.fs.starfarer.api.combat.CombatEngineLayers;
import com.fs.starfarer.api.combat.BaseCombatLayeredRenderingPlugin;
import com.fs.starfarer.api.combat.CollisionClass;
import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.DamageType;
import com.fs.starfarer.api.combat.DamagingProjectileAPI;
import com.fs.starfarer.api.combat.MissileAPI;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.ShipSystemAPI;
import com.fs.starfarer.api.impl.combat.BaseShipSystemScript;
import com.fs.starfarer.api.input.InputEventAPI;
import org.lazywizard.lazylib.CollisionUtils;
import org.lazywizard.lazylib.MathUtils;
import org.lwjgl.util.vector.Vector2f;
import rsl.RslIds;
import rsl.combat.LatticeData;
import rsl.combat.RslUtil;
import rsl.hullmods.StolenTime;

import java.awt.Color;
import java.util.ArrayList;
import java.util.EnumSet;
import java.util.List;

/**
 * Virtuoso (and the Unsung, by system id): a steerable blink-dash of {@link #DISTANCE} units in the direction of
 * movement, untargetable mid-dash, paid for in combat readiness. The path stays behind as the String (see {@link StringFx}):
 * a barrier for projectiles, then a snap that damages everything touching it and steals CR.
 */
public class GlissandoStats extends BaseShipSystemScript {
    public static final float DISTANCE = 720f;
    public static final float DASH_TIME = 0.4f;
    /** How fast (radians/s) the dash heading swings towards the direction the ship is being flown. */
    public static final float STEER = 7f;
    /** Maneuverability multiplier while dashing, so thrust input actually bends the dash. */
    public static final float DASH_AGILITY = 3f;
    private static final Color GLOW_VIRTUOSO = new Color(235, 255, 252, 255);
    /** The String's arcs and snap: white with a faint teal fringe (the Unsung's never snaps and stays dim teal). */
    static final Color STRING_WHITE = new Color(225, 250, 248, 255);
    /** Afterimage tints: white on the Virtuoso, teal on the Unsung (drawn additively by {@link Afterimages}). */
    private static final Color IMAGE_VIRTUOSO = new Color(225, 252, 250, 255);
    private static final Color IMAGE_UNSUNG = new Color(80, 205, 195, 255);
    public static final float CR_COST = 0.01f;
    public static final float CR_COST_UNSUNG = 0.015f;
    public static final float MIN_CR = 0.30f;
    public static final float IFRAMES_UNSUNG = 0.2f;
    public static final float ACCENT_TIME = 2f;

    static class Dash {
        Vector2f from, dir;
        float t0, done, imageTimer;
        Afterimages images;
        boolean unsung, overtone;
    }

    static boolean unsung(ShipAPI ship) {
        return ship.getSystem() != null && RslIds.SYSTEM_GLISSANDO_UNSUNG.equals(ship.getSystem().getId());
    }

    @Override
    public boolean isUsable(ShipSystemAPI system, ShipAPI ship) {
        return ship.getCurrentCR() >= MIN_CR;
    }

    @Override
    public String getInfoText(ShipSystemAPI system, ShipAPI ship) {
        return ship.getCurrentCR() < MIN_CR ? "CR TOO LOW" : null;
    }

    @Override
    public void apply(MutableShipStatsAPI stats, String id, State state, float effectLevel) {
        ShipAPI ship = SystemUtil.ship(stats);
        if (ship == null || state == State.COOLDOWN || state == State.IDLE) return;
        LatticeData d = LatticeData.get(ship);
        CombatEngineAPI engine = Global.getCombatEngine();
        float now = RslUtil.now();
        if (!d.systemFired) {
            d.systemFired = true;
            Dash dash = new Dash();
            dash.unsung = unsung(ship);
            dash.from = new Vector2f(ship.getLocation());
            Vector2f dir = new Vector2f(ship.getVelocity());
            if (dir.lengthSquared() < 900f) {
                double r = Math.toRadians(ship.getFacing());
                dir.set((float) Math.cos(r), (float) Math.sin(r));
            }
            dir.normalise();
            dash.dir = dir;
            dash.t0 = now;
            dash.overtone = !dash.unsung && LatticeData.consumeOvertone(ship);
            d.sysObj = dash;
            ship.setCurrentCR(Math.max(0f, ship.getCurrentCR() - (dash.unsung ? CR_COST_UNSUNG : CR_COST)));
            d.accentUntil = now + DASH_TIME + ACCENT_TIME;
            ship.setCollisionClass(CollisionClass.NONE);
            setInvulnerable(stats, id, true);
            stats.getAcceleration().modifyMult(id, DASH_AGILITY);
            stats.getDeceleration().modifyMult(id, DASH_AGILITY);
            stats.getTurnAcceleration().modifyMult(id, DASH_AGILITY);
            stats.getMaxTurnRate().modifyMult(id, 2f);
        }
        if (!(d.sysObj instanceof Dash)) return;
        Dash dash = (Dash) d.sysObj;
        // The dash is added on top of the ship's own movement, and its heading swings towards the direction the ship
        // is being flown (its velocity, which the pilot's thrust controls; boosted agility while dashing): the dash can
        // be bent and turned mid-flight instead of being a fixed line.
        float amount = engine.isPaused() ? 0f : engine.getElapsedInLastFrame();
        Vector2f v = ship.getVelocity();
        if (v.lengthSquared() > 900f && amount > 0f) {
            double cur = Math.atan2(dash.dir.y, dash.dir.x);
            double want = Math.atan2(v.y, v.x);
            double delta = Math.atan2(Math.sin(want - cur), Math.cos(want - cur));
            double maxTurn = STEER * amount;
            cur += Math.max(-maxTurn, Math.min(maxTurn, delta));
            dash.dir.set((float) Math.cos(cur), (float) Math.sin(cur));
        }
        float f = Math.min(1f, (now - dash.t0) / DASH_TIME);
        float e = f * f * (3f - 2f * f);
        float step = (e - dash.done) * DISTANCE;
        dash.done = e;
        Vector2f loc = ship.getLocation();
        loc.x += dash.dir.x * step;
        loc.y += dash.dir.y * step;
        float hw = engine.getMapWidth() * 0.5f - 300f, hh = engine.getMapHeight() * 0.5f - 300f;
        loc.x = Math.max(-hw, Math.min(hw, loc.x));
        loc.y = Math.max(-hh, Math.min(hh, loc.y));
        if (dash.unsung && now - dash.t0 > IFRAMES_UNSUNG) setInvulnerable(stats, id, false);
        if (amount > 0f) {
            engine.addSmoothParticle(new Vector2f(ship.getLocation()), new Vector2f(), ship.getCollisionRadius() * 0.6f,
                    0.087f, 0.35f, dash.unsung ? RslUtil.TEAL_DIM : GLOW_VIRTUOSO);
            // a fading trail of afterimages along the dash, left in place
            if (dash.images == null) {
                dash.images = new Afterimages(ship, dash.unsung ? IMAGE_UNSUNG : IMAGE_VIRTUOSO,
                        dash.unsung ? 0.35f : 0.45f);
                engine.addLayeredRenderingPlugin(dash.images);
            }
            dash.imageTimer -= amount;
            if (dash.imageTimer <= 0f) {
                dash.imageTimer = 0.03f;
                dash.images.snapshot();
            }
        }
    }

    private static void setInvulnerable(MutableShipStatsAPI stats, String id, boolean on) {
        if (on) {
            stats.getHullDamageTakenMult().modifyMult(id, 0f);
            stats.getArmorDamageTakenMult().modifyMult(id, 0f);
            stats.getShieldDamageTakenMult().modifyMult(id, 0f);
            stats.getEmpDamageTakenMult().modifyMult(id, 0f);
        } else {
            stats.getHullDamageTakenMult().unmodify(id);
            stats.getArmorDamageTakenMult().unmodify(id);
            stats.getShieldDamageTakenMult().unmodify(id);
            stats.getEmpDamageTakenMult().unmodify(id);
        }
    }

    @Override
    public void unapply(MutableShipStatsAPI stats, String id) {
        setInvulnerable(stats, id, false);
        stats.getAcceleration().unmodify(id);
        stats.getDeceleration().unmodify(id);
        stats.getTurnAcceleration().unmodify(id);
        stats.getMaxTurnRate().unmodify(id);
        ShipAPI ship = SystemUtil.ship(stats);
        if (ship == null) return;
        LatticeData d = LatticeData.get(ship);
        if (d.sysObj instanceof Dash) {
            Dash dash = (Dash) d.sysObj;
            ship.setCollisionClass(CollisionClass.SHIP);
            Vector2f to = new Vector2f(ship.getLocation());
            Global.getCombatEngine().addPlugin(new StringFx(ship, dash.from, to, dash.unsung, dash.overtone));
            if (dash.overtone && ship.getSystem() != null) refundHalf(ship.getSystem());
        }
        d.sysObj = null;
        d.systemFired = false;
    }

    private static void refundHalf(ShipSystemAPI sys) {
        if (sys.getAmmo() >= sys.getMaxAmmo()) return;
        float p = sys.getAmmoReloadProgress() + 0.5f;
        if (p >= 1f) {
            sys.setAmmo(sys.getAmmo() + 1);
            p -= 1f;
        }
        sys.setAmmoReloadProgress(p);
    }

    @Override
    public StatusData getStatusData(int index, State state, float effectLevel) {
        return index == 0 ? new StatusData("glissando", false) : null;
    }

    /**
     * Afterimages of one dash: snapshots of the hull sprite (position and facing) that stay where they were taken,
     * drawn additively in the ship's tint under the ships, fading out over {@link #LIFE} seconds. Our own renderer
     * rather than ShipAPI.addAfterimage, whose images did not stay in place.
     */
    static class Afterimages extends BaseCombatLayeredRenderingPlugin {
        static final float LIFE = 0.5f;
        static final int MAX = 24;
        private static final EnumSet<CombatEngineLayers> LAYERS = EnumSet.of(CombatEngineLayers.UNDER_SHIPS_LAYER);
        private final SpriteAPI sprite;
        private final Color tint;
        private final float alpha;
        private final ShipAPI ship;
        private final float[] x = new float[MAX], y = new float[MAX], ang = new float[MAX], born = new float[MAX];
        private int n;

        Afterimages(ShipAPI ship, Color tint, float alpha) {
            this.ship = ship;
            this.tint = tint;
            this.alpha = alpha;
            SpriteAPI sp = null;
            try {
                sp = Global.getSettings().getSprite(ship.getHullSpec().getSpriteName());
                if (sp != null && ship.getSpriteAPI() != null) {
                    sp.setCenter(ship.getSpriteAPI().getCenterX(), ship.getSpriteAPI().getCenterY());
                }
            } catch (Throwable ignored) {
                sp = null;
            }
            this.sprite = sp;
        }

        void snapshot() {
            if (n >= MAX) return;
            x[n] = ship.getLocation().x;
            y[n] = ship.getLocation().y;
            ang[n] = ship.getFacing() - 90f;
            born[n] = RslUtil.now();
            n++;
        }

        @Override
        public EnumSet<CombatEngineLayers> getActiveLayers() {
            return LAYERS;
        }

        @Override
        public float getRenderRadius() {
            return 100000f;
        }

        @Override
        public boolean isExpired() {
            return n == 0 || sprite == null || RslUtil.now() - born[n - 1] > LIFE + 0.1f;
        }

        @Override
        public void render(CombatEngineLayers layer, ViewportAPI viewport) {
            if (sprite == null) return;
            float now = RslUtil.now();
            sprite.setColor(tint);
            sprite.setAdditiveBlend();
            for (int i = 0; i < n; i++) {
                float f = 1f - (now - born[i]) / LIFE;
                if (f <= 0f) continue;
                sprite.setAngle(ang[i]);
                sprite.setAlphaMult(alpha * f * f * viewport.getAlphaMult());
                sprite.renderAtCenter(x[i], y[i]);
            }
        }
    }

    /**
     * The String: a taut line between the dash's ends. Blocks enemy projectiles (up to {@link #BARRIER} damage), then
     * snaps at {@link #SNAP_TIME} (twice with Overtone; never for the Unsung): {@link #SNAP_DAMAGE} to enemy ships
     * touching it, fighters and missiles destroyed, CR stolen.
     */
    public static class StringFx extends BaseEveryFrameCombatPlugin {
        public static final float SNAP_TIME = 1.2f;
        public static final float SNAP_DAMAGE = 400f;
        public static final float SNAP_CR = 0.02f;
        public static final float BARRIER = 1500f;

        final ShipAPI ship;
        final Vector2f a, b;
        final boolean unsung;
        final int snaps;
        int snapped;
        float t, fx, barrier = BARRIER;
        final List<DamagingProjectileAPI> kill = new ArrayList<>();

        StringFx(ShipAPI ship, Vector2f a, Vector2f b, boolean unsung, boolean overtone) {
            this.ship = ship;
            this.a = new Vector2f(a);
            this.b = new Vector2f(b);
            this.unsung = unsung;
            this.snaps = unsung ? 0 : (overtone ? 2 : 1);
        }

        @Override
        public void advance(float amount, List<InputEventAPI> events) {
            CombatEngineAPI engine = Global.getCombatEngine();
            if (engine.isPaused()) return;
            t += amount;
            fx += amount;
            float life = unsung ? SNAP_TIME : SNAP_TIME * snaps;
            if (t > life + 0.05f) {
                engine.removePlugin(this);
                return;
            }
            if (fx > 0.12f) {
                fx = 0f;
                engine.spawnEmpArcVisual(a, null, b, null, 5f, unsung ? RslUtil.TEAL_DIM : STRING_WHITE, RslUtil.WHITE);
            }
            if (barrier > 0f) {
                kill.clear();
                List<DamagingProjectileAPI> projs = engine.getProjectiles();
                for (int i = 0; i < projs.size(); i++) {
                    DamagingProjectileAPI p = projs.get(i);
                    if (p.getOwner() == ship.getOwner() || p.getOwner() == 100) continue;
                    if (CollisionUtils.getCollides(a, b, p.getLocation(), p.getCollisionRadius() + 6f)) kill.add(p);
                }
                for (int i = 0; i < kill.size() && barrier > 0f; i++) {
                    DamagingProjectileAPI p = kill.get(i);
                    barrier -= p.getDamageAmount();
                    engine.addHitParticle(p.getLocation(), new Vector2f(), 30f, 1f, 0.15f, STRING_WHITE);
                    engine.removeEntity(p);
                }
            }
            if (snapped < snaps && t >= SNAP_TIME * (snapped + 1)) {
                snapped++;
                snap(engine);
            }
        }

        private void snap(CombatEngineAPI engine) {
            for (int k = 0; k <= 8; k++) {
                Vector2f p = new Vector2f(a.x + (b.x - a.x) * k / 8f, a.y + (b.y - a.y) * k / 8f);
                engine.addHitParticle(p, new Vector2f(), 90f, 1f, 0.3f, STRING_WHITE);
            }
            engine.spawnEmpArcVisual(a, null, b, null, 22f, STRING_WHITE, RslUtil.WHITE);
            List<ShipAPI> ships = engine.getShips();
            for (int i = 0; i < ships.size(); i++) {
                ShipAPI s = ships.get(i);
                if (s.isHulk() || !RslUtil.isEnemy(ship, s) || s.isPhased()) continue;
                if (!CollisionUtils.getCollides(a, b, s.getLocation(), s.getCollisionRadius() * 0.8f)) continue;
                Vector2f p = MathUtils.getNearestPointOnLine(s.getLocation(), a, b);
                if (s.isFighter()) {
                    engine.applyDamage(s, p, 5000f, DamageType.ENERGY, 0f, true, false, ship, true);
                    continue;
                }
                engine.applyDamage(s, p, SNAP_DAMAGE, DamageType.ENERGY, SNAP_DAMAGE * 0.5f, false, false, ship, true);
                if (RslUtil.hasMod(ship, RslIds.HULLMOD_STOLEN_TIME)) StolenTime.stealAmount(ship, s, SNAP_CR);
            }
            List<MissileAPI> missiles = engine.getMissiles();
            kill.clear();
            for (int i = 0; i < missiles.size(); i++) {
                MissileAPI m = missiles.get(i);
                if (m.getOwner() == ship.getOwner()) continue;
                if (CollisionUtils.getCollides(a, b, m.getLocation(), m.getCollisionRadius() + 10f)) kill.add(m);
            }
            for (int i = 0; i < kill.size(); i++) {
                DamagingProjectileAPI m = kill.get(i);
                engine.applyDamage(m, m.getLocation(), 2000f, DamageType.ENERGY, 0f, true, false, ship, false);
            }
        }
    }
}
