package rsl.world;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.campaign.FactionAPI;
import com.fs.starfarer.api.campaign.SectorAPI;
import com.fs.starfarer.api.campaign.rules.MemoryAPI;
import com.fs.starfarer.api.impl.campaign.ids.Factions;
import org.apache.log4j.Logger;
import rsl.RslIds;

/**
 * The Cantorate's starting relations (CAMPAIGN.md section 4), applied once per save.
 *
 * The numbers mirror tools/campaign_data.py RELATIONS, which also feeds Nexerelin's startRelationships. In a new
 * Nexerelin game Nex sets them itself, so this only marks the save; a save that gets the mod mid-game (vanilla or
 * Nex) receives them here exactly once, behind {@link RslIds#MEM_RELATIONS_SET}.
 */
public final class RslRelations {
    private static final Logger log = Global.getLogger(RslRelations.class);

    private static final String[] IDS = {
            Factions.INDEPENDENT, Factions.PERSEAN, Factions.DIKTAT, Factions.TRITACHYON, Factions.HEGEMONY,
            Factions.LUDDIC_CHURCH, Factions.LUDDIC_PATH};
    private static final float[] VALUES = {0.30f, 0.20f, 0f, -0.20f, -0.30f, -0.20f, -0.60f};

    private RslRelations() {
    }

    public static void applyOnce(boolean newGame) {
        SectorAPI sector = Global.getSector();
        MemoryAPI mem = sector.getMemoryWithoutUpdate();
        if (mem.getBoolean(RslIds.MEM_RELATIONS_SET)) return;
        mem.set(RslIds.MEM_RELATIONS_SET, true);
        boolean nex = Global.getSettings().getModManager().isModEnabled(RslIds.MOD_NEXERELIN);
        if (nex && newGame) return;   // Nexerelin applies exerelinFactionConfig/rsl_choir.json startRelationships

        FactionAPI choir = sector.getFaction(RslIds.FACTION_CHOIR);
        if (choir == null) return;
        for (int i = 0; i < IDS.length; i++) {
            if (sector.getFaction(IDS[i]) == null) continue;   // e.g. a total conversion without that faction
            choir.setRelationship(IDS[i], VALUES[i]);
        }
        log.info("Resonance Lattice: Cantorate relations set");
    }
}
