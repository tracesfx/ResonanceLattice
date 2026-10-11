package rsl;

import com.fs.starfarer.api.BaseModPlugin;
import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.campaign.SectorAPI;
import org.apache.log4j.Logger;

/**
 * Entry point named in mod_info.json "modPlugin".
 *
 * Call order (wiki "Miscellaneous modding tidbits"): onApplicationLoad once at startup; then for a new campaign
 * onNewGame -> onNewGameAfterProcGen -> onNewGameAfterEconomyLoad -> onEnabled -> onNewGameAfterTimePass -> onGameLoad.
 * onGameLoad also runs every time a save is loaded, so everything done there must be idempotent.
 */
public class RslModPlugin extends BaseModPlugin {
    private static final Logger log = Global.getLogger(RslModPlugin.class);

    /** Sector memory flag set once this mod's campaign content exists in the current save. */
    public static final String MEM_GENERATED = "$rsl_generated";

    @Override
    public void onApplicationLoad() throws Exception {
        log.info("Resonance Lattice loaded");
    }

    @Override
    public void onNewGame() {
        // New campaigns: create star systems, markets and people here (before the economy loads).
        generateIfNeeded(Global.getSector());
    }

    @Override
    public void onGameLoad(boolean newGame) {
        // Existing saves that predate the mod reach this point without onNewGame; generate once, guarded by a flag.
        // Re-add transient listeners and scripts here (they are not kept in the save unless added as permanent).
        if (!newGame) generateIfNeeded(Global.getSector());
    }

    private static void generateIfNeeded(SectorAPI sector) {
        if (sector == null || sector.getMemoryWithoutUpdate().getBoolean(MEM_GENERATED)) return;
        try {
            // Call your world generation here, e.g. RslWorldGen.generate(sector);
            sector.getMemoryWithoutUpdate().set(MEM_GENERATED, true);
        } catch (Throwable t) {
            // Log and carry on: a failure here must not take the whole campaign down.
            log.error("Resonance Lattice: world generation failed", t);
        }
    }
}
