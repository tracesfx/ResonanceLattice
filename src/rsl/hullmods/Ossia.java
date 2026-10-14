package rsl.hullmods;

import com.fs.starfarer.api.combat.BaseHullMod;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import com.fs.starfarer.api.ui.TooltipMakerAPI;
import rsl.systems.GlissandoStats;

/**
 * Ossia ("or else": the alternative passage a score offers the soloist), won in the duel against the Dies Irae
 * (rsl.campaign.DuelIntel) and built into the player's Virtuoso as a permanent mod. Read by
 * {@link GlissandoStats}: each dash costs {@link #CR_COST_MULT} of the usual CR, and the String snaps once more.
 */
public class Ossia extends BaseHullMod {
    public static final float CR_COST_MULT = 0.5f;

    @Override
    public void addPostDescriptionSection(TooltipMakerAPI t, HullSize hullSize, ShipAPI ship, float width,
                                          boolean isForModSpec) {
        Tip.section(t, "Glissando");
        Tip.good(t, "Each dash costs %s less combat readiness.", Tip.pct(1f - CR_COST_MULT));
        Tip.good(t, "The String snaps %s more time (twice, or three times with Overtone).", "one");
        Tip.note(t, "Won from Commander Isolde Raike of the Dies Irae, the only other pilot who ever flew a "
                + "Virtuoso.");
        Tip.end(t);
    }
}
