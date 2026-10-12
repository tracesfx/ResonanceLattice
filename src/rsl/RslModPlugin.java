package rsl;

import com.fs.starfarer.api.BaseModPlugin;
import com.fs.starfarer.api.Global;
import org.apache.log4j.Logger;

/**
 * Entry point named in mod_info.json "modPlugin".
 *
 * This build is the ships-and-weapons slice: no campaign content is generated (the Choir faction exists for
 * fleet spawning and missions but owns no markets). Everything happens in combat, driven by the hullmods, systems and
 * weapon scripts, plus rsl.combat.RslCombatPlugin registered in data/config/settings.json.
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
}
