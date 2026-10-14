package rsl.combat;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.campaign.CampaignFleetAPI;
import com.fs.starfarer.api.combat.CombatEngineAPI;
import com.fs.starfarer.api.combat.CombatFleetManagerAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.ShipCommand;
import com.fs.starfarer.api.combat.listeners.AdvanceableListener;
import com.fs.starfarer.api.combat.listeners.HullDamageAboutToBeTakenListener;
import com.fs.starfarer.api.fleet.FleetMemberAPI;
import org.lwjgl.util.vector.Vector2f;
import rsl.RslIds;
import rsl.hullmods.Encore;

import java.awt.Color;
import java.util.List;

/**
 * The duel against the Dies Irae, combat side (rsl.campaign.DuelIntel). Active only in a campaign battle while the
 * player fleet carries {@link RslIds#MEM_DUEL_ACTIVE}:
 * <ul>
 * <li>one ship per side: anything but the Virtuoso is taken out of the player's reserves (the campaign side already
 * held every other ship back; this is the safety net);</li>
 * <li>the Lacrimosa yields instead of being disabled: a blow that would disable it is refused (after Encore, if it
 * has it), and the ship breaks off and leaves the field the way vanilla's Phase Anchor emergency dive does - it counts
 * as retreated, so a lost duel never costs the Virtuoso.</li>
 * </ul>
 */
public final class EncoreCombat {
    private static final Color YIELD = new Color(150, 235, 225, 255);
    private float check;

    private EncoreCombat() {
    }

    /** A plugin for this battle, or null if it is not the duel. */
    public static EncoreCombat create(CombatEngineAPI engine) {
        try {
            if (engine == null || !engine.isInCampaign() || Global.getSector() == null) return null;
            CampaignFleetAPI pf = Global.getSector().getPlayerFleet();
            if (pf == null || !pf.getMemoryWithoutUpdate().getBoolean(RslIds.MEM_DUEL_ACTIVE)) return null;
            return new EncoreCombat();
        } catch (Throwable t) {
            return null;
        }
    }

    public void advance(CombatEngineAPI engine, float amount) {
        check -= amount;
        if (check > 0f) return;
        check = 0.25f;
        CombatFleetManagerAPI fm = engine.getFleetManager(0);
        if (fm != null) {
            List<FleetMemberAPI> reserves = fm.getReservesCopy();
            for (int i = 0; i < reserves.size(); i++) {
                FleetMemberAPI m = reserves.get(i);
                if (m.getHullSpec() == null || !RslIds.HULL_VIRTUOSO.equals(m.getHullSpec().getBaseHullId())) {
                    fm.removeFromReserves(m);
                }
            }
        }
        List<ShipAPI> ships = engine.getShips();
        for (int i = 0; i < ships.size(); i++) {
            ShipAPI s = ships.get(i);
            if (s.getOwner() != 0 || s.isFighter() || s.isHulk()) continue;
            if (!RslIds.HULL_VIRTUOSO.equals(s.getHullSpec().getBaseHullId())) continue;
            if (!s.hasListenerOfClass(Yield.class)) s.addListener(new Yield(s));
        }
    }

    /** The Lacrimosa breaks off instead of breaking (after Phase Anchor's emergency dive). */
    static class Yield implements AdvanceableListener, HullDamageAboutToBeTakenListener {
        final ShipAPI ship;
        boolean yielding;
        float t;

        Yield(ShipAPI ship) {
            this.ship = ship;
        }

        @Override
        public boolean notifyAboutToTakeHullDamage(Object param, ShipAPI s, Vector2f point, float damageAmount) {
            if (yielding) return true;
            if (damageAmount < ship.getHitpoints() || Encore.saves(ship)) return false;
            yielding = true;
            ship.setHitpoints(Math.max(1f, ship.getHitpoints()));
            CombatEngineAPI engine = Global.getCombatEngine();
            engine.addFloatingTextAlways(ship.getLocation(), "The Lacrimosa yields", 32f, YIELD, ship, 16f, 3.2f, 1f,
                    0f, 0f, 1f);
            engine.getCombatUI().addMessage(1, YIELD, "Raike: ", Color.WHITE,
                    "\"Not today, captain. Come back when you're ready.\"");
            Global.getSoundPlayer().playSound("system_phase_cloak_activate", 1f, 1f, ship.getLocation(),
                    ship.getVelocity());
            return true;
        }

        @Override
        public void advance(float amount) {
            if (!yielding) return;
            t += amount;
            ship.getMutableStats().getHullDamageTakenMult().modifyMult("rsl_yield", 0f);
            ship.getMutableStats().getArmorDamageTakenMult().modifyMult("rsl_yield", 0f);
            ship.setRetreating(true, false);
            ship.blockCommandForOneFrame(ShipCommand.USE_SYSTEM);
            ship.blockCommandForOneFrame(ShipCommand.FIRE);
            float b = Math.max(0f, 1f - t / 1.5f);
            ship.setExtraAlphaMult2(b);
            ship.setJitter(this, YIELD, 1f - b, 10, 0f, ship.getCollisionRadius() * (1f - b));
            if (t >= 1.5f) ship.getLocation().set(0f, -1000000f);   // off the map: counts as retreated
        }
    }
}
