package rsl.world;

import com.fs.starfarer.api.Global;
import org.apache.log4j.Logger;
import rsl.RslIds;

/**
 * Optional Nexerelin integration. Nex classes are only touched inside {@link NexCalls}, and only after
 * {@link #isEnabled()}, so the JVM never resolves them when Nex is absent (the pattern Tahlan, DA, UAF and LoA use).
 * No reflection: the game's script classloader restricts it.
 */
public final class RslNex {
    private static final Logger log = Global.getLogger(RslNex.class);

    private RslNex() {
    }

    public static boolean isEnabled() {
        return Global.getSettings().getModManager().isModEnabled(RslIds.MOD_NEXERELIN);
    }

    /** True only when Nexerelin is enabled and the sector is a Nex random sector (not Corvus mode). */
    public static boolean isRandomSector() {
        if (!isEnabled()) return false;
        try {
            return NexCalls.isRandomSector();
        } catch (Throwable t) {
            log.warn("Resonance Lattice: could not read Nexerelin's sector mode; assuming Corvus mode", t);
            return false;
        }
    }

    /** The only class that references Nexerelin types. */
    private static final class NexCalls {
        static boolean isRandomSector() {
            exerelin.campaign.SectorManager manager = exerelin.campaign.SectorManager.getManager();
            if (manager != null) return !manager.isCorvusMode();
            // a new game whose Nex plugin has not run yet: the choice made in Nex's new-game dialog
            exerelin.campaign.ExerelinSetupData data = exerelin.campaign.ExerelinSetupData.getInstance();
            return data != null && !data.corvusMode;
        }
    }
}
