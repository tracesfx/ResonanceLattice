package rsl;

import com.fs.starfarer.api.BaseModPlugin;
import com.fs.starfarer.api.Global;
import com.thoughtworks.xstream.XStream;
import org.apache.log4j.Logger;
import rsl.world.CantorArrayIndustry;
import rsl.world.LatticeNurseries;
import rsl.world.RslRelations;
import rsl.world.VellGen;

/**
 * Entry point named in mod_info.json "modPlugin".
 *
 * Combat runs through the hullmods, systems and weapon scripts plus rsl.combat.RslCombatPlugin (settings.json).
 * Campaign content (ROADMAP.md) is generated in onNewGame and, behind sector memory flags, again from onGameLoad, so
 * new games and saves that predate the mod both get it exactly once.
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
    public void onNewGame() {
        VellGen.generate(Global.getSector());
    }

    @Override
    public void onGameLoad(boolean newGame) {
        VellGen.generate(Global.getSector());   // no-op unless this save predates Vell
        RslRelations.applyOnce(newGame);
    }

    /** Classes stored in saves (market industries and conditions). Never rename or move them after release. */
    @Override
    public void configureXStream(XStream x) {
        x.alias("RslCantorArrayIndustry", CantorArrayIndustry.class);
        x.alias("RslLatticeNurseries", LatticeNurseries.class);
    }
}
