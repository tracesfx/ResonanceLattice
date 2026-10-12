package rsl.hullmods;

import com.fs.starfarer.api.combat.BaseHullMod;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import rsl.combat.LatticeDealtModifier;

/** Staccato: the stacks and the shatter are applied by {@link LatticeDealtModifier}; this class only describes it. */
public class Fracture extends BaseHullMod {
    @Override
    public String getDescriptionParam(int index, HullSize hullSize) {
        switch (index) {
            case 0:
                return "" + LatticeDealtModifier.FRACTURE_MAX;
            case 1:
                return (int) LatticeDealtModifier.FRACTURE_TIMEOUT + " seconds";
            case 2:
                return "" + (LatticeDealtModifier.FRACTURE_MAX + 1) + "th";
            case 3:
                return "" + (int) LatticeDealtModifier.FRACTURE_SHATTER;
            default:
                return null;
        }
    }
}
