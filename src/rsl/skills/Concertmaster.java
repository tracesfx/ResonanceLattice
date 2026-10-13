package rsl.skills;

import com.fs.starfarer.api.characters.ShipSkillEffect;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import rsl.combat.ChorusEffects;
import rsl.combat.LatticeData;

/**
 * Odile Marchetti's unique skill (CAMPAIGN.md section 9; data/characters/skills/rsl_concertmaster.skill, tag
 * npc_only so nobody else can learn it). The skill only describes itself here: its battle-wide effect needs the whole
 * battle, so rsl.combat.ChorusEffects applies it to every allied ship while her ship is on the field.
 */
public final class Concertmaster {
    private Concertmaster() {
    }

    /** Fleet-wide bonuses. */
    public static class Level1 implements ShipSkillEffect {
        @Override
        public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
        }

        @Override
        public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
        }

        @Override
        public String getEffectDescription(float level) {
            return "While her ship is deployed, every allied ship in the battle deals +" + (int) ChorusEffects.CONCERT_DAMAGE
                    + "% weapon damage and has +" + (int) ChorusEffects.CONCERT_FLUX + "% flux dissipation";
        }

        @Override
        public String getEffectPerLevelDescription() {
            return null;
        }

        @Override
        public ScopeDescription getScopeDescription() {
            return ScopeDescription.ALL_SHIPS;
        }
    }

    /** Lattice bonuses. */
    public static class Level2 extends Level1 {
        @Override
        public String getEffectDescription(float level) {
            return "Allied Lattice ships gain Resonance " + Math.round((LatticeData.CONCERT_GAIN - 1f) * 100f)
                    + "% faster and share Sympathy at any range";
        }
    }
}
