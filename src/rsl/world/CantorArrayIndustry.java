package rsl.world;

import com.fs.starfarer.api.impl.campaign.econ.impl.OrbitalStation;

/**
 * The Cantor Array as Coda's defence station: vanilla's {@link OrbitalStation} with the rsl_cantor_Standard variant
 * (industries.csv data). It spawns on the pre-made "Cantor Array" station entity that {@link VellGen} connects to the
 * market (tagged use_station_visual, so the station fleet's sprite is drawn in the campaign).
 *
 * It is never built anywhere else: unique to the Cantorate's capital, hidden from the build menu.
 */
public class CantorArrayIndustry extends OrbitalStation {
    @Override
    public boolean isAvailableToBuild() {
        return false;
    }

    @Override
    public boolean showWhenUnavailable() {
        return false;
    }

    @Override
    public String getUnavailableReason() {
        return "Only the Cantorate can grow a Cantor Array.";
    }
}
