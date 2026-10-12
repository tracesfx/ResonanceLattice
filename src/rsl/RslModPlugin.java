package rsl;

import com.fs.starfarer.api.BaseModPlugin;
import com.fs.starfarer.api.Global;
import org.apache.log4j.Logger;
import rsl.world.RslRelations;

/**
 * Entry point named in mod_info.json "modPlugin".
 *
 * Combat runs through the hullmods, systems and weapon scripts plus rsl.combat.RslCombatPlugin (settings.json).
 * Campaign content (ROADMAP.md) is added stage by stage; everything done on game load is idempotent behind a sector
 * memory flag, so new games and existing saves get it exactly once.
 */
public class RslModPlugin extends BaseModPlugin {
    private static final Logger log = Global.getLogger(RslModPlugin.class);

    @Override
    public void onApplicationLoad() throws Exception {
        if (Global.getSettings().getModManager().isModEnabled("shaderLib")) {
            try {
                RslGraphicsLib.load();
            } catch (Throwable t) {
                log.warn("Resonance Lattice: GraphicsLib maps not loaded", t);
            }
        }
        log.info("Resonance Lattice loaded");
    }

    @Override
    public void onGameLoad(boolean newGame) {
        RslRelations.applyOnce(newGame);
    }
}
