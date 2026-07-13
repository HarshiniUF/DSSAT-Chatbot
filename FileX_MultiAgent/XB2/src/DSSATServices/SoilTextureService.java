package DSSATServices;

import DSSATRepository.SoilTextureRepository;
import DSSATModel.SoilTexture;
import DSSATModel.SoilTextureList;
import java.util.ArrayList;

/**
 *
 * @author Jazzy
 */
public class SoilTextureService extends DSSATServiceBase {
    private final SoilTextureRepository soilTextureRepository;
    
    public SoilTextureService(String rootPath) {
        super(rootPath);
        
        this.soilTextureRepository = new SoilTextureRepository(rootPath);
    }
    
    @Override
    public void Parse() throws Exception{
        boolean isValid = true;

        try {
            ArrayList<String> soilTextureList = this.soilTextureRepository.Parse();
            SoilTextureList.Clear();

            for(int i = 0;i < soilTextureList.size();i++)
            {
                SoilTexture soil = new SoilTexture();
                String tmp = soilTextureList.get(i);

                soil.Code = tmp.substring(0, 5).trim();
                soil.Description = tmp.substring(9, 78).trim();
                SoilTextureList.AddNew(soil);
            }
        } catch (Exception ex) {
            isValid = false;
        }

        if (!isValid) {
            throw new Exception("Soil Texture parse failed");
        }
    }
    
    @Override
    public String getName() {
        return "Soil Texture";
    }
}
