package rsl.campaign;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.campaign.CampaignFleetAPI;
import com.fs.starfarer.api.campaign.FactionAPI;
import com.fs.starfarer.api.campaign.SectorEntityToken;
import com.fs.starfarer.api.campaign.TextPanelAPI;
import com.fs.starfarer.api.campaign.comm.IntelInfoPlugin;
import com.fs.starfarer.api.characters.FullName;
import com.fs.starfarer.api.characters.PersonAPI;
import com.fs.starfarer.api.impl.campaign.events.OfficerManagerEvent;
import com.fs.starfarer.api.impl.campaign.events.OfficerManagerEvent.SkillPickPreference;
import com.fs.starfarer.api.impl.campaign.ids.Personalities;
import com.fs.starfarer.api.impl.campaign.ids.Tags;
import com.fs.starfarer.api.impl.campaign.intel.BaseIntelPlugin;
import com.fs.starfarer.api.ui.SectorMapAPI;
import com.fs.starfarer.api.ui.TooltipMakerAPI;
import com.fs.starfarer.api.util.Misc;
import rsl.RslIds;
import rsl.world.SecretsGen;

import java.awt.Color;
import java.util.Random;
import java.util.Set;

/**
 * The Lost Scores (CAMPAIGN.md section 7, secrets #1 and #5): Saskia Venn's eight tuning scores, found in Institute
 * caches across the fringe. Each pays {@link #GLASS} Pitch Glass and is kept here to reread; the fourth hints at the
 * Full Chorus; the eighth is a navigation fix that creates Venn's Rest, where the Concertmaster waits. Saved (aliased).
 */
public class ScoresIntel extends BaseIntelPlugin {
    public static final int GLASS = 15;
    public static final int MARCHETTI_LEVEL = 7;

    public static final String[] TITLES = {"Growth", "Calibration", "The Collar", "The Full Chorus", "The Soloist",
            "Silence", "The Twelve", "Return"};

    public static final String[] SCORES = {
        "Score I - Growth. A crystal grows true only to a clock it can trust, and nothing humans build keeps time "
                + "like a dead star. Seed at the beat, feed at the off-beat, never touch it on the rest. Venn's note "
                + "in the margin: \"I am writing these down because the others will not. They want to forget me. Let "
                + "them remember the scores.\"",
        "Score II - Calibration. Strike the core with the reference pitch and listen for the beat between them; "
                + "tighten until the beat slows to nothing. A tuner who cannot hear the beat should not be trusted "
                + "with a core. A tuner who can hear it for sixteen hours will go deaf by forty. The margin: \"Both "
                + "are true. Write both down.\"",
        "Score III - The Collar. Bone conduction through the jaw, a tone the tuner hums and the core answers. The "
                + "core takes a little of the singer's endurance and gives back its pitch. The margin, underlined "
                + "twice: \"A little. Only ever a little.\"",
        "Score IV - The Full Chorus. Seven voices: the one that leads, the one that guards, the one that strikes, "
                + "the one that builds, the one that waves, the one that holds, and the one that conducts. When all "
                + "seven sing on one field the network locks, and every core in it rings louder than it can alone. "
                + "Field a Grace Note, Refrain, Staccato, Cadence, Tremolo, Fermata and Conductor together.",
        "Score V - The Soloist. One core large enough to carry twelve. It does not share resonance; it lends it, "
                + "and takes it back with interest. The margin: \"The Navy wanted a conductor. I built a soloist and "
                + "told them it was a conductor. Nobody checked the math but me.\"",
        "Score VI - Silence. How to sing a core silent: the reference pitch, inverted, held until nothing in the "
                + "crystal answers. It works on any lattice. The margin, in a different ink: \"It works on the other "
                + "kind of core too. Do not write that down.\"",
        "Score VII - The Twelve. A list of twelve names and twelve ships, each name ticked. Under it, a single "
                + "line, half scratched out: \"They volunteered. I did not tell them what for.\"",
        "Score VIII - Return. Not a tuning score at all: a sequence of pitches that, played into a navigation "
                + "computer, resolves into a position on the fringe. The margin: \"If you have all eight, you know "
                + "enough to judge me. Come and do it.\"",
    };

    public static final String VENN_LAST = "\"Director Saskia Venn, last log. Whoever you are, you have the scores, so "
            + "you know what I built. The Hush was not a malfunction. The raiders would have killed every family in "
            + "the Institute, and the Lacrimosa could stop them only if it took everything twelve crews had. I tuned "
            + "it to do exactly that. The twelve volunteered. I told them it would hurt. I did not tell them it would "
            + "end. My first chair refused the collar order, and I could not make myself force her, so I put her to "
            + "sleep instead and brought her here. I have been waiting for someone to wake her. I find I cannot do it "
            + "myself. Her name is Odile. Tell her I am sorry.\"";

    private int found;
    private SectorEntityToken vennsRest;
    private boolean marchetti;

    public static ScoresIntel get() {
        for (IntelInfoPlugin p : Global.getSector().getIntelManager().getIntel(ScoresIntel.class)) {
            if (!((ScoresIntel) p).isEnded()) return (ScoresIntel) p;
        }
        return null;
    }

    public static ScoresIntel getOrCreate(TextPanelAPI text) {
        ScoresIntel s = get();
        if (s != null) return s;
        s = new ScoresIntel();
        Global.getSector().getIntelManager().addIntel(s, false, text);
        return s;
    }

    public int getFound() {
        return found;
    }

    public SectorEntityToken getVennsRest() {
        return vennsRest;
    }

    public boolean isMarchettiFound() {
        return marchetti;
    }

    /** Reads the next Score: returns its index (0-7), pays the Pitch Glass, and after the eighth reveals Venn's Rest. */
    public int read(TextPanelAPI text) {
        int i = Math.min(found, SCORES.length - 1);
        found = Math.min(found + 1, SCORES.length);
        PitchGlass.add(GLASS);
        if (found >= SCORES.length && vennsRest == null) {
            vennsRest = SecretsGen.createVennsRest(Global.getSector());
            if (vennsRest != null) Misc.makeImportant(vennsRest, "rsl_scores");
        }
        sendUpdate(text);
        return i;
    }

    /** Console testing: {@code runcode rsl.campaign.ScoresIntel.debugReadAll()} reads every remaining Score. */
    public static void debugReadAll() {
        ScoresIntel s = getOrCreate(null);
        while (s.found < SCORES.length) s.read(null);
    }

    /** Secret #5's reward: Concertmaster Odile Marchetti joins the player's fleet as an officer. Once. */
    public PersonAPI wakeMarchetti(TextPanelAPI text) {
        if (marchetti) return null;
        marchetti = true;
        CampaignFleetAPI pf = Global.getSector().getPlayerFleet();
        FactionAPI player = Global.getSector().getPlayerFaction();
        PersonAPI p = OfficerManagerEvent.createOfficer(player, MARCHETTI_LEVEL, SkillPickPreference.ANY, false, pf,
                true, true, MARCHETTI_LEVEL, new Random());
        p.setId(RslIds.PERSON_MARCHETTI);
        p.setGender(FullName.Gender.FEMALE);
        p.setName(new FullName("Odile", "Marchetti", FullName.Gender.FEMALE));
        p.setPortraitSprite("graphics/portraits/portrait_league08.png");
        p.setPersonality(Personalities.STEADY);
        p.getStats().setSkillLevel(RslIds.SKILL_CONCERTMASTER, 1);
        p.getMemoryWithoutUpdate().set("$rsl_marchetti", true);
        pf.getFleetData().addOfficer(p);
        if (vennsRest != null) Misc.makeUnimportant(vennsRest, "rsl_scores");
        if (text != null) {
            text.setFontSmallInsignia();
            text.addParagraph("Concertmaster Odile Marchetti (level " + MARCHETTI_LEVEL + ") has joined your fleet",
                    Misc.getPositiveHighlightColor());
            text.setFontInsignia();
        }
        sendUpdate(text);
        return p;
    }

    private void sendUpdate(TextPanelAPI text) {
        if (text != null) Global.getSector().getIntelManager().addIntelToTextPanel(this, text);
        else sendUpdateIfPlayerHasIntel(null, false);
    }

    @Override
    protected String getName() {
        return "The Lost Scores (" + found + " of " + SCORES.length + ")";
    }

    @Override
    public FactionAPI getFactionForUIColors() {
        return Global.getSector().getFaction(RslIds.FACTION_CHOIR);
    }

    @Override
    public String getIcon() {
        return Global.getSettings().getSpriteName("intel", RslIds.GFX_INTEL_SCORES);
    }

    @Override
    public Set<String> getIntelTags(SectorMapAPI map) {
        Set<String> tags = super.getIntelTags(map);
        tags.add(Tags.INTEL_STORY);
        tags.add(RslIds.FACTION_CHOIR);
        return tags;
    }

    @Override
    protected void addBulletPoints(TooltipMakerAPI info, ListInfoMode mode, boolean isUpdate, Color tc, float initPad) {
        bullet(info);
        if (found < SCORES.length) {
            info.addPara("%s of %s scores recovered", initPad, tc, Misc.getHighlightColor(), "" + found,
                    "" + SCORES.length);
        } else if (!marchetti) {
            info.addPara("The last score is a position: %s", initPad, tc, Misc.getHighlightColor(),
                    SecretsGen.VENNS_REST);
        } else {
            info.addPara("Venn's Rest has given up its last secret", initPad, tc);
        }
        unindent(info);
    }

    @Override
    public void createSmallDescription(TooltipMakerAPI info, float width, float height) {
        float opad = 10f;
        info.addPara("Saskia Venn, director of the Antiphon Institute, wrote down the tuning scores the Cantorate "
                + "now keeps only in memory, and hid them in Institute caches across the fringe. Each is "
                + "engineering; each has her notes in the margin.", opad);
        for (int i = 0; i < found && i < SCORES.length; i++) {
            info.addPara(SCORES[i], Misc.getGrayColor(), opad);
        }
        addBulletPoints(info, ListInfoMode.IN_DESC);
    }

    @Override
    public SectorEntityToken getMapLocation(SectorMapAPI map) {
        return found >= SCORES.length && !marchetti ? vennsRest : null;
    }

    @Override
    public String getSortString() {
        return "Lost Scores";
    }
}
