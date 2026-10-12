package rsl.hullmods;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.combat.BaseHullMod;
import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import rsl.combat.LatticeData;
import rsl.combat.RslUtil;

import java.util.List;

/**
 * Cantor Array: when a petal dies, its Resonance floods the core and the surviving petals (full Resonance, i.e.
 * Overtone) and they gain weapon damage for the rest of the battle. Runs on the core (the station ship), which
 * counts its living modules each frame.
 */
public class PhaseLockedPetals extends BaseHullMod {
    public static final float DAMAGE_BONUS = 25f;
    private static final String ID = "rsl_phase_locked";
    private static final String KEY_ALIVE = "rsl_petals_alive";

    @Override
    public void advanceInCombat(ShipAPI ship, float amount) {
        CombatEngineAPI engine = Global.getCombatEngine();
        if (engine == null || engine.isPaused() || !ship.isAlive() || !ship.isShipWithModules()) return;
        List<ShipAPI> mods = ship.getChildModulesCopy();
        int alive = 0;
        for (int i = 0; i < mods.size(); i++) if (RslUtil.alive(mods.get(i))) alive++;
        Object o = ship.getCustomData().get(KEY_ALIVE);
        int before = o instanceof Integer ? (Integer) o : alive;
        ship.setCustomData(KEY_ALIVE, alive);
        if (alive >= before) return;
        flood(ship);
        for (int i = 0; i < mods.size(); i++) {
            ShipAPI m = mods.get(i);
            if (RslUtil.alive(m)) flood(m);
        }
        engine.addFloatingText(ship.getLocation(), "Phase-locked: the petals resonate", 30f, RslUtil.VIOLET, ship, 1f, 1f);
    }

    private static void flood(ShipAPI s) {
        LatticeData d = LatticeData.get(s);
        d.resonance = LatticeData.MAX;
        d.sinceGain = 0f;
        d.petalBoosted = true;
        MutableShipStatsAPI st = s.getMutableStats();
        st.getEnergyWeaponDamageMult().modifyPercent(ID, DAMAGE_BONUS);
        st.getBallisticWeaponDamageMult().modifyPercent(ID, DAMAGE_BONUS);
        st.getMissileWeaponDamageMult().modifyPercent(ID, DAMAGE_BONUS);
        s.setJitterUnder(ID, RslUtil.VIOLET, 1f, 8, 6f);
    }

    @Override
    public String getDescriptionParam(int index, HullSize hullSize) {
        return index == 0 ? (int) DAMAGE_BONUS + "%" : null;
    }
}
