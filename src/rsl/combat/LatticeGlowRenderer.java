package rsl.combat;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.combat.BaseCombatLayeredRenderingPlugin;
import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.CombatEngineLayers;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.ViewportAPI;
import com.fs.starfarer.api.combat.WeaponAPI;
import com.fs.starfarer.api.graphics.SpriteAPI;
import org.apache.log4j.Logger;
import org.lwjgl.util.vector.Vector2f;
import rsl.RslIds;

import java.awt.Color;
import java.util.EnumSet;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Draws the lattice seam glow over every Lattice ship and its moving parts, additively, with brightness following
 * Resonance (the Virtuoso follows combat readiness instead, and cross-fades to its gold Bravura sprite). The Grace
 * Note's seams shift towards violet in Discord. Also draws embedded Tuning Spikes.
 *
 * Sprites are listed in settings.json under the "rsl_glow" graphics category (keyed by hull or deco weapon id) so
 * they are loaded at startup.
 */
public class LatticeGlowRenderer extends BaseCombatLayeredRenderingPlugin {
    private static final Logger log = Global.getLogger(LatticeGlowRenderer.class);
    /**
     * Seams draw in BELOW_PHASED_SHIPS_LAYER, the first layer after every hull layer. Drawn inside a hull's own
     * layer the glow never showed in game (most likely it was drawn before the hull sprite).
     */
    private static final EnumSet<CombatEngineLayers> LAYERS = EnumSet.of(CombatEngineLayers.BELOW_PHASED_SHIPS_LAYER,
            CombatEngineLayers.ABOVE_SHIPS_LAYER);
    /** Seam brightness at zero Resonance; full Resonance (or CR on the Virtuoso) adds the rest. */
    private static final float BASE_ALPHA = 0.4f;
    private static final Color DISCORD = new Color(255, 120, 255, 255);

    private final RslCombatPlugin plugin;
    private final Map<String, SpriteAPI> sprites = new HashMap<>();
    private final Vector2f tmp = new Vector2f();
    private boolean broken;

    public LatticeGlowRenderer(RslCombatPlugin plugin) {
        this.plugin = plugin;
    }

    private SpriteAPI sprite(String key) {
        if (sprites.containsKey(key)) return sprites.get(key);
        SpriteAPI s = null;
        try {
            String name = Global.getSettings().getSpriteName(RslIds.GFX_GLOW, key);
            if (name != null) s = Global.getSettings().getSprite(name);
        } catch (Throwable ignored) {
            s = null;
        }
        sprites.put(key, s);
        return s;
    }

    @Override
    public EnumSet<CombatEngineLayers> getActiveLayers() {
        return LAYERS;
    }

    @Override
    public float getRenderRadius() {
        return 1000000f;
    }

    @Override
    public boolean isExpired() {
        return false;
    }

    @Override
    public void advance(float amount) {
        CombatEngineAPI engine = Global.getCombatEngine();
        if (engine == null || engine.isPaused()) return;
        List<ShipAPI> ships = engine.getShips();
        for (int i = 0; i < ships.size(); i++) {
            ShipAPI s = ships.get(i);
            if (!RslUtil.isLattice(s)) continue;
            LatticeData d = LatticeData.get(s);
            float target = isVirtuoso(s) ? clamp((s.getCurrentCR() - 0.3f) / 0.7f) : d.resonance / LatticeData.MAX;
            d.glow += (target - d.glow) * Math.min(1f, amount * 3f);
            float b = d.bravura ? 1f : 0f;
            d.bravuraLevel += (b - d.bravuraLevel) * Math.min(1f, amount * 2f);
        }
    }

    private static boolean isVirtuoso(ShipAPI s) {
        String id = s.getHullSpec().getHullId();
        return RslIds.HULL_VIRTUOSO.equals(id) || RslIds.HULL_UNSUNG.equals(id);
    }

    private static float clamp(float v) {
        return Math.max(0f, Math.min(1f, v));
    }

    @Override
    public void render(CombatEngineLayers layer, ViewportAPI viewport) {
        if (broken) return;
        CombatEngineAPI engine = Global.getCombatEngine();
        if (engine == null) return;
        try {
            if (layer == CombatEngineLayers.ABOVE_SHIPS_LAYER) {
                renderSpikes(viewport);
                return;
            }
            List<ShipAPI> ships = engine.getShips();
            for (int i = 0; i < ships.size(); i++) {
                ShipAPI s = ships.get(i);
                if (!RslUtil.isLattice(s) || s.isHulk() || s.isPhased()) continue;
                if (!viewport.isNearViewport(s.getLocation(), s.getCollisionRadius() + 200f)) continue;
                renderShip(s, viewport);
            }
        } catch (Throwable t) {
            broken = true;
            log.error("Resonance Lattice glow renderer disabled after an error", t);
        }
    }

    private void renderShip(ShipAPI s, ViewportAPI viewport) {
        LatticeData d = LatticeData.get(s);
        float alpha = (BASE_ALPHA + (1f - BASE_ALPHA) * d.glow) * s.getCombinedAlphaMult() * viewport.getAlphaMult();
        String hullId = s.getHullSpec().getHullId();
        Color tint = d.discord ? DISCORD : Color.WHITE;
        float bl = d.bravuraLevel;
        float pulse = 0.85f + 0.15f * (float) Math.sin(RslUtil.now() * 3f);
        SpriteAPI glow = sprite(hullId);
        SpriteAPI shipSprite = s.getSpriteAPI();
        if (glow != null && shipSprite != null) {
            draw(glow, shipSprite.getCenterX(), shipSprite.getCenterY(), s.getLocation(), s.getFacing() - 90f,
                    alpha * (1f - bl), tint);
            if (bl > 0.01f) {
                SpriteAPI gold = sprite(RslIds.HULL_VIRTUOSO + "_bravura");
                if (gold != null) {
                    draw(gold, shipSprite.getCenterX(), shipSprite.getCenterY(), s.getLocation(), s.getFacing() - 90f,
                            Math.min(1f, alpha * 1.2f) * bl * pulse, Color.WHITE);
                }
            }
        }
        List<WeaponAPI> ws = s.getAllWeapons();
        for (int i = 0; i < ws.size(); i++) {
            WeaponAPI w = ws.get(i);
            if (!w.isDecorative()) continue;
            SpriteAPI g = sprite(w.getId());
            if (g == null) continue;
            draw(g, g.getWidth() / 2f, g.getHeight() / 2f, w.getLocation(), w.getCurrAngle() - 90f, alpha * (1f - bl),
                    tint);
            if (bl > 0.01f) {
                SpriteAPI gb = sprite(w.getId() + "_bravura");
                if (gb != null) {
                    draw(gb, gb.getWidth() / 2f, gb.getHeight() / 2f, w.getLocation(), w.getCurrAngle() - 90f,
                            Math.min(1f, alpha * 1.2f) * bl * pulse, Color.WHITE);
                }
            }
        }
    }

    private static void draw(SpriteAPI sp, float cx, float cy, Vector2f loc, float angle, float alpha, Color tint) {
        if (alpha <= 0.005f) return;
        sp.setCenter(cx, cy);
        sp.setAngle(angle);
        sp.setColor(tint);
        sp.setAlphaMult(Math.min(1f, alpha));
        sp.setAdditiveBlend();
        sp.renderAtCenter(loc.x, loc.y);
    }

    private void renderSpikes(ViewportAPI viewport) {
        if (plugin == null || plugin.spikes.isEmpty()) return;
        SpriteAPI sp = null;
        try {
            sp = Global.getSettings().getSprite(RslIds.GFX_FX, "spike");
        } catch (Throwable ignored) {
            return;
        }
        if (sp == null) return;
        float pulse = 0.7f + 0.3f * (float) Math.sin(RslUtil.now() * 9f);
        for (int i = 0; i < plugin.spikes.size(); i++) {
            RslCombatPlugin.Attached a = plugin.spikes.get(i);
            if (a.target == null || a.target.isHulk()) continue;
            Vector2f p = a.world(tmp);
            if (!viewport.isNearViewport(p, 50f)) continue;
            sp.setAngle(a.target.getFacing() + a.angle - 90f);
            sp.setColor(Color.WHITE);
            sp.setAlphaMult(viewport.getAlphaMult());
            sp.setNormalBlend();
            sp.renderAtCenter(p.x, p.y);
            sp.setAdditiveBlend();
            sp.setAlphaMult(0.5f * pulse * viewport.getAlphaMult());
            sp.setColor(RslUtil.TEAL);
            sp.renderAtCenter(p.x, p.y);
        }
    }
}
