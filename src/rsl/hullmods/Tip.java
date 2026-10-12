package rsl.hullmods;

import com.fs.starfarer.api.ui.Alignment;
import com.fs.starfarer.api.ui.TooltipMakerAPI;
import com.fs.starfarer.api.util.Misc;

import java.awt.Color;

/**
 * Tooltip layout shared by every Lattice hullmod, in the vanilla style: a short description from hull_mods.csv, then
 * titled sections of bulleted lines with the numbers highlighted (good numbers in the highlight colour, costs in the
 * negative colour). The S-mod section is the game's own (sModDesc column + getSModDescriptionParam).
 */
final class Tip {
    private Tip() {
    }

    static final float PAD = 10f;
    static final float LINE = 3f;

    static void section(TooltipMakerAPI t, String title) {
        t.addSectionHeading(title, Alignment.MID, PAD);
        t.setBulletedListMode("  - ");
    }

    static void badSection(TooltipMakerAPI t, String title) {
        t.addSectionHeading(title, Misc.getNegativeHighlightColor(), Misc.setAlpha(
                Misc.scaleColorOnly(Misc.getNegativeHighlightColor(), 0.4f), 175), Alignment.MID, PAD);
        t.setBulletedListMode("  - ");
    }

    /** One bullet; {@code %s} slots are filled with {@code hl} and highlighted. A literal percent sign is "%%". */
    static void good(TooltipMakerAPI t, String format, String... hl) {
        t.addPara(format, LINE, Misc.getHighlightColor(), hl);
    }

    static void bad(TooltipMakerAPI t, String format, String... hl) {
        t.addPara(format, LINE, Misc.getNegativeHighlightColor(), hl);
    }

    static void note(TooltipMakerAPI t, String format, String... hl) {
        t.addPara(format, LINE, Misc.getGrayColor(), Misc.getHighlightColor(), hl);
    }

    static void end(TooltipMakerAPI t) {
        t.setBulletedListMode(null);
    }

    static String pct(float fraction) {
        float v = fraction * 100f;
        return (v == (int) v ? String.valueOf((int) v) : String.valueOf(v)) + "%";
    }

    static Color story() {
        return Misc.getStoryOptionColor();
    }
}
