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

import java.util.List;

/**
 * Solo Movement (CAMPAIGN.md section 8, Abelard's path): a sidegrade for the full Virtuoso. Alone (no allied ship
 * within {@link #RANGE}) it steals more readiness and hits harder; in company it steals less. The steal rate is read
 * by {@link StolenTime} through {@link #stealMult}; the damage bonus is applied here.
 */
public class SoloMovement extends BaseHullMod {
    public static final float RANGE = 1500f;
    public static final float ALONE_STEAL = 1.25f;
    public static final float COMPANY_STEAL = 0.75f;
    public static final float ALONE_DAMAGE = 10f;
    private static final String MOD_ID = "rsl_solo_movement";

    public static boolean has(ShipAPI ship) {
        return ship != null && ship.getVariant() != null && ship.getVariant().hasHullMod(RslIds.HULLMOD_SOLO_MOVEMENT);
    }

    /** Stolen Time multiplier for a Solo ship (1 without the Movement). */
    public static float stealMult(ShipAPI ship) {
        if (!has(ship)) return 1f;
        return LatticeData.get(ship).soloAlone ? ALONE_STEAL : COMPANY_STEAL;
    }

    @Override
    public void advanceInCombat(ShipAPI ship, float amount) {
        CombatEngineAPI engine = Global.getCombatEngine();
        if (engine == null || ship == null || ship.isHulk()) return;
        LatticeData d = LatticeData.get(ship);
        d.soloTimer -= amount;
        if (d.soloTimer <= 0f) {
            d.soloTimer = 0.5f;
            d.soloAlone = true;
            List<ShipAPI> ships = engine.getShips();
            for (int i = 0; i < ships.size(); i++) {
                ShipAPI s = ships.get(i);
                if (s == ship || s.getOwner() != ship.getOwner() || s.isHulk() || s.isFighter()
                        || s.isStationModule() || s.isShuttlePod()) {
                    continue;
                }
                float dx = s.getLocation().x - ship.getLocation().x, dy = s.getLocation().y - ship.getLocation().y;
                if (dx * dx + dy * dy <= RANGE * RANGE) {
                    d.soloAlone = false;
                    break;
                }
            }
        }
        MutableShipStatsAPI st = ship.getMutableStats();
        if (d.soloAlone) {
            st.getBallisticWeaponDamageMult().modifyPercent(MOD_ID, ALONE_DAMAGE);
            st.getEnergyWeaponDamageMult().modifyPercent(MOD_ID, ALONE_DAMAGE);
            st.getMissileWeaponDamageMult().modifyPercent(MOD_ID, ALONE_DAMAGE);
        } else {
            st.getBallisticWeaponDamageMult().unmodify(MOD_ID);
            st.getEnergyWeaponDamageMult().unmodify(MOD_ID);
            st.getMissileWeaponDamageMult().unmodify(MOD_ID);
        }
        if (ship == engine.getPlayerShip()) {
            engine.maintainStatusForPlayerShip(MOD_ID, "graphics/rsl/icons/hullmods/rsl_solo_movement.png",
                    "Solo Movement", d.soloAlone ? "alone: +" + (int) ALONE_DAMAGE + "% damage, faster theft"
                            : "in company: slower theft", !d.soloAlone);
        }
    }

    @Override
    public boolean isApplicableToShip(ShipAPI ship) {
        return ship != null && RslIds.HULL_VIRTUOSO.equals(ship.getHullSpec().getHullId())
                && !ship.getVariant().hasHullMod(RslIds.HULLMOD_CHORUS_MOVEMENT);
    }

    @Override
    public String getUnapplicableReason(ShipAPI ship) {
        if (ship != null && ship.getVariant().hasHullMod(RslIds.HULLMOD_CHORUS_MOVEMENT)) {
            return "The core can hold only one Movement";
        }
        return "Only the Virtuoso's core can be retuned";
    }

    @Override
    public boolean showInRefitScreenModPickerFor(ShipAPI ship) {
        return ship != null && RslIds.HULL_VIRTUOSO.equals(ship.getHullSpec().getHullId());
    }

    @Override
    public void addPostDescriptionSection(TooltipMakerAPI t, HullSize hullSize, ShipAPI ship, float width,
                                          boolean isForModSpec) {
        Tip.section(t, "Alone");
        Tip.good(t, "With no allied ship within %s units: Stolen Time steals %s more and weapons deal %s more "
                + "damage.", "" + (int) RANGE, Tip.pct(ALONE_STEAL - 1f), (int) ALONE_DAMAGE + "%");
        Tip.badSection(t, "In company");
        Tip.bad(t, "With an allied ship within %s units, Stolen Time steals %s less.", "" + (int) RANGE,
                Tip.pct(1f - COMPANY_STEAL));
        Tip.note(t, "Fighters do not count as company. Cannot be combined with Chorus Movement.");
        Tip.end(t);
    }
}
