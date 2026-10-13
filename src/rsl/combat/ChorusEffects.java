package rsl.combat;

import com.fs.starfarer.api.characters.PersonAPI;
import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import rsl.RslIds;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * Battle-wide effects of a whole side (CAMPAIGN.md sections 7 and 9), re-evaluated twice a second by
 * {@link RslCombatPlugin}:
 * <ul>
 * <li><b>Full Chorus</b> (secret #4): a side with one of each of the seven Lattice line hulls on the field gives its
 * Lattice ships {@link #FULL_CHORUS_DAMAGE}% weapon damage and {@link LatticeData#FULL_CHORUS_GAIN}x Resonance
 * gain.</li>
 * <li><b>Concertmaster</b> (Odile Marchetti's unique skill): while her ship is on the field, every allied ship gets
 * {@link #CONCERT_DAMAGE}% weapon damage and {@link #CONCERT_FLUX}% flux dissipation; allied Lattice ships gain
 * Resonance {@link LatticeData#CONCERT_GAIN}x faster and share Sympathy at any range.</li>
 * </ul>
 */
public final class ChorusEffects {
    public static final String[] LINE_HULLS = {"rsl_gracenote", "rsl_refrain", "rsl_staccato", "rsl_cadence",
            "rsl_tremolo", "rsl_halo", "rsl_conductor"};
    public static final float FULL_CHORUS_DAMAGE = 5f;
    public static final float CONCERT_DAMAGE = 5f;
    public static final float CONCERT_FLUX = 10f;
    private static final String MOD_CHORUS = "rsl_full_chorus";
    private static final String MOD_CONCERT = "rsl_concertmaster";

    private final Set<String> seen = new HashSet<String>();
    private final boolean[] chorus = new boolean[2];
    private final boolean[] concert = new boolean[2];
    private final boolean[] announced = new boolean[2];
    private float timer;

    public static boolean isConcertmaster(PersonAPI p) {
        return p != null && !p.isDefault() && p.getStats() != null
                && p.getStats().getSkillLevel(RslIds.SKILL_CONCERTMASTER) > 0;
    }

    public void advance(CombatEngineAPI engine, float amount) {
        status(engine);
        timer -= amount;
        if (timer > 0f) return;
        timer = 0.5f;
        List<ShipAPI> ships = engine.getShips();
        for (int side = 0; side < 2; side++) {
            seen.clear();
            boolean master = false;
            for (int i = 0; i < ships.size(); i++) {
                ShipAPI s = ships.get(i);
                if (s.getOwner() != side || s.isFighter() || s.isHulk() || !s.isAlive()) continue;
                if (s.getHullSpec() != null) seen.add(s.getHullSpec().getBaseHullId());
                if (isConcertmaster(s.getCaptain())) master = true;
            }
            boolean full = true;
            for (String h : LINE_HULLS) {
                if (!seen.contains(h)) {
                    full = false;
                    break;
                }
            }
            chorus[side] = full;
            concert[side] = master;
            if (full && !announced[side]) {
                announced[side] = true;
                ShipAPI flag = side == 0 ? engine.getPlayerShip() : null;
                if (flag != null) {
                    engine.addFloatingText(flag.getLocation(), "Full Chorus", 40f, RslUtil.TEAL, flag, 1f, 2f);
                }
            }
        }
        for (int i = 0; i < ships.size(); i++) {
            ShipAPI s = ships.get(i);
            if (s.isFighter() || s.getOwner() < 0 || s.getOwner() > 1) continue;
            apply(engine, s, chorus[s.getOwner()], concert[s.getOwner()]);
        }
    }

    private void apply(CombatEngineAPI engine, ShipAPI s, boolean full, boolean master) {
        MutableShipStatsAPI st = s.getMutableStats();
        boolean lattice = RslUtil.isLattice(s);
        if (lattice) {
            LatticeData d = LatticeData.get(s);
            d.fullChorus = full;
            d.concertmaster = master;
        }
        if (full && lattice) {
            st.getBallisticWeaponDamageMult().modifyPercent(MOD_CHORUS, FULL_CHORUS_DAMAGE);
            st.getEnergyWeaponDamageMult().modifyPercent(MOD_CHORUS, FULL_CHORUS_DAMAGE);
            st.getMissileWeaponDamageMult().modifyPercent(MOD_CHORUS, FULL_CHORUS_DAMAGE);
        } else {
            st.getBallisticWeaponDamageMult().unmodify(MOD_CHORUS);
            st.getEnergyWeaponDamageMult().unmodify(MOD_CHORUS);
            st.getMissileWeaponDamageMult().unmodify(MOD_CHORUS);
        }
        if (master) {
            st.getBallisticWeaponDamageMult().modifyPercent(MOD_CONCERT, CONCERT_DAMAGE);
            st.getEnergyWeaponDamageMult().modifyPercent(MOD_CONCERT, CONCERT_DAMAGE);
            st.getMissileWeaponDamageMult().modifyPercent(MOD_CONCERT, CONCERT_DAMAGE);
            st.getFluxDissipation().modifyPercent(MOD_CONCERT, CONCERT_FLUX);
        } else {
            st.getBallisticWeaponDamageMult().unmodify(MOD_CONCERT);
            st.getEnergyWeaponDamageMult().unmodify(MOD_CONCERT);
            st.getMissileWeaponDamageMult().unmodify(MOD_CONCERT);
            st.getFluxDissipation().unmodify(MOD_CONCERT);
        }
    }

    /** HUD lines for the player's ship (maintained every frame). */
    private void status(CombatEngineAPI engine) {
        ShipAPI s = engine.getPlayerShip();
        if (s == null || s.getOwner() < 0 || s.getOwner() > 1) return;
        if (chorus[s.getOwner()] && RslUtil.isLattice(s)) {
            engine.maintainStatusForPlayerShip(MOD_CHORUS, "graphics/rsl/icons/hullmods/rsl_conductors_bridge.png",
                    "Full Chorus", "+" + (int) FULL_CHORUS_DAMAGE + "% damage, faster Resonance", false);
        }
        if (concert[s.getOwner()]) {
            engine.maintainStatusForPlayerShip(MOD_CONCERT, "graphics/rsl/icons/skills/rsl_concertmaster.png",
                    "Concertmaster", "+" + (int) CONCERT_DAMAGE + "% damage, +" + (int) CONCERT_FLUX
                            + "% dissipation", false);
        }
    }
}
