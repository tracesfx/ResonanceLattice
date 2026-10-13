package rsl.hullmods;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.combat.BaseHullMod;
import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import com.fs.starfarer.api.ui.TooltipMakerAPI;
import rsl.RslIds;
import rsl.combat.LatticeData;
import rsl.combat.RslUtil;

import java.util.ArrayList;
import java.util.List;

/**
 * The Hush's fleet hullmod (CAMPAIGN.md section 6, beat 5): when a ship of the Dead Chorus dies, its resonance floods
 * the others - every survivor jumps to full Resonance (Overtone) and gains {@link #DAMAGE_PER_DEAD}% weapon damage per
 * dead sister ship, up to {@link #DAMAGE_CAP}%. Added to Hush ships as a perma mod by rsl.campaign.LacrimosaFleets;
 * the seams of a Dead Chorus ship glow violet (LatticeGlowRenderer).
 *
 * Per-battle state lives in the combat engine's custom data (one {@link Choir} per side), so nothing leaks between
 * battles; the recount runs at most 4 times a second and allocates nothing.
 */
public class DeadChorus extends BaseHullMod {
    public static final float DAMAGE_PER_DEAD = 10f;
    public static final float DAMAGE_CAP = 50f;
    private static final String KEY = "rsl.deadChorus.";
    private static final String MOD_ID = "rsl_dead_chorus";

    /** The Dead Chorus of one side in one battle. */
    private static final class Choir {
        final List<ShipAPI> members = new ArrayList<ShipAPI>();
        int dead;
        float lastCheck = -1f;
    }

    @Override
    public void advanceInCombat(ShipAPI ship, float amount) {
        CombatEngineAPI engine = Global.getCombatEngine();
        if (engine == null || ship == null) return;
        LatticeData.get(ship).hush = true;
        if (ship.isHulk()) return;
        String key = ship.getOwner() == 0 ? KEY + "0" : KEY + "1";
        Object o = engine.getCustomData().get(key);
        Choir c;
        if (o instanceof Choir) {
            c = (Choir) o;
        } else {
            c = new Choir();
            engine.getCustomData().put(key, c);
        }
        if (!c.members.contains(ship)) c.members.add(ship);
        float now = engine.getTotalElapsedTime(false);
        if (now - c.lastCheck >= 0.25f) {
            c.lastCheck = now;
            int dead = 0;
            for (int i = 0; i < c.members.size(); i++) {
                ShipAPI m = c.members.get(i);
                if (m.isHulk() || m.getHitpoints() <= 0f) dead++;
            }
            if (dead > c.dead) {
                c.dead = dead;
                for (int i = 0; i < c.members.size(); i++) {
                    ShipAPI m = c.members.get(i);
                    if (m.isHulk() || m.getHitpoints() <= 0f) continue;
                    if (RslUtil.isLattice(m)) LatticeData.get(m).resonance = LatticeData.MAX;
                }
            }
        }
        float bonus = Math.min(DAMAGE_CAP, DAMAGE_PER_DEAD * c.dead);
        MutableShipStatsAPI s = ship.getMutableStats();
        if (bonus > 0f) {
            s.getBallisticWeaponDamageMult().modifyPercent(MOD_ID, bonus);
            s.getEnergyWeaponDamageMult().modifyPercent(MOD_ID, bonus);
            s.getMissileWeaponDamageMult().modifyPercent(MOD_ID, bonus);
            if (ship == engine.getPlayerShip()) {
                engine.maintainStatusForPlayerShip(MOD_ID, "graphics/icons/hullsys/high_energy_focus.png",
                        "Dead Chorus", "+" + (int) bonus + "% weapon damage", false);
            }
        }
    }

    @Override
    public void addPostDescriptionSection(TooltipMakerAPI t, HullSize hullSize, ShipAPI ship, float width,
                                          boolean isForModSpec) {
        Tip.section(t, "The Hush");
        Tip.good(t, "When a ship with Dead Chorus is destroyed, every other Dead Chorus ship on its side jumps to "
                + "full Resonance.");
        Tip.good(t, "Each dead sister ship adds %s weapon damage to the survivors, up to %s.",
                (int) DAMAGE_PER_DEAD + "%", (int) DAMAGE_CAP + "%");
        Tip.end(t);
    }

    /** Never fitted by the player: the Hush's ships carry it as a permanent mod. */
    @Override
    public boolean showInRefitScreenModPickerFor(ShipAPI ship) {
        return false;
    }

    static boolean has(ShipAPI ship) {
        return ship != null && ship.getVariant() != null && ship.getVariant().hasHullMod(RslIds.HULLMOD_DEAD_CHORUS);
    }
}
