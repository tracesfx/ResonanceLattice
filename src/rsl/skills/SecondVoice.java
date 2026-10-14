package rsl.skills;

import com.fs.starfarer.api.characters.ShipSkillEffect;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;

/**
 * Commander Isolde Raike's unique skill (rsl.campaign.EncoreFleets; data/characters/skills/rsl_second_voice.skill,
 * npc_only): her fifteenth. The pilot who learned a Virtuoso without a chorus: harder hits, a faster system, a faster
 * ship.
 */
public final class SecondVoice {
    private SecondVoice() {
    }

    public static final float DAMAGE = 10f;
    public static final float SYSTEM_REGEN = 25f;
    public static final float SPEED = 10f;

    public static class Level1 implements ShipSkillEffect {
        @Override
        public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
            stats.getDamageToFrigates().modifyPercent(id, DAMAGE);
            stats.getDamageToDestroyers().modifyPercent(id, DAMAGE);
            stats.getDamageToCruisers().modifyPercent(id, DAMAGE);
            stats.getDamageToCapital().modifyPercent(id, DAMAGE);
            stats.getSystemRegenBonus().modifyPercent(id, SYSTEM_REGEN);
            stats.getMaxSpeed().modifyPercent(id, SPEED);
        }

        @Override
        public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
            stats.getDamageToFrigates().unmodify(id);
            stats.getDamageToDestroyers().unmodify(id);
            stats.getDamageToCruisers().unmodify(id);
            stats.getDamageToCapital().unmodify(id);
            stats.getSystemRegenBonus().unmodify(id);
            stats.getMaxSpeed().unmodify(id);
        }

        @Override
        public String getEffectDescription(float level) {
            return "+" + (int) DAMAGE + "% damage to ships, +" + (int) SYSTEM_REGEN + "% ship system recharge rate, +"
                    + (int) SPEED + "% top speed";
        }

        @Override
        public String getEffectPerLevelDescription() {
            return null;
        }

        @Override
        public ScopeDescription getScopeDescription() {
            return ScopeDescription.PILOTED_SHIP;
        }
    }
}
