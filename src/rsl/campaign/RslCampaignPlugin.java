package rsl.campaign;

import com.fs.starfarer.api.PluginPick;
import com.fs.starfarer.api.campaign.BaseCampaignPlugin;
import com.fs.starfarer.api.campaign.CampaignFleetAPI;
import com.fs.starfarer.api.campaign.InteractionDialogPlugin;
import com.fs.starfarer.api.campaign.SectorEntityToken;
import rsl.RslIds;
import rsl.rulecmd.RslEncore;

/**
 * Transient (registered on every load by RslModPlugin): interacting with an encore fleet (fleet memory
 * {@link RslIds#MEM_ENCORE}) opens {@link RslEncore} instead of the plain fleet dialog. While the player is engaged,
 * RslEncore has already handed the dialog to vanilla's fleet interaction, so this pick only applies to the first
 * contact.
 */
public class RslCampaignPlugin extends BaseCampaignPlugin {
    @Override
    public String getId() {
        return "rsl_campaign_plugin";
    }

    @Override
    public boolean isTransient() {
        return true;
    }

    @Override
    public PluginPick<InteractionDialogPlugin> pickInteractionDialogPlugin(SectorEntityToken target) {
        if (!(target instanceof CampaignFleetAPI)) return null;
        String role = target.getMemoryWithoutUpdate().getString(RslIds.MEM_ENCORE);
        if (!"duel".equals(role) && !"requiem".equals(role)) return null;
        return new PluginPick<InteractionDialogPlugin>(new RslEncore(role), PickPriority.MOD_SPECIFIC);
    }
}
