package rsl;

import org.dark.shaders.util.ShaderLib;
import org.dark.shaders.util.TextureData;

/**
 * GraphicsLib integration, kept in its own class so the mod loads without GraphicsLib: this class is only touched
 * after RslModPlugin has checked isModEnabled("shaderLib").
 */
final class RslGraphicsLib {
    private RslGraphicsLib() {
    }

    static void load() {
        ShaderLib.init();
        TextureData.readTextureDataCSV("data/lights/rsl_texture_data.csv");
    }
}
