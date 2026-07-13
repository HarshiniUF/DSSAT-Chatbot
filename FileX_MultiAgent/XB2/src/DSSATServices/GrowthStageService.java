package DSSATServices;

import DSSATRepository.GrowthStageRepository;
import DSSATModel.Crop;
import DSSATModel.CropList;
import DSSATModel.GrowthStage;
import DSSATModel.GrowthStageList;
import java.util.ArrayList;

/**
 *
 * @author Jazzy
 */
public class GrowthStageService extends DSSATServiceBase {
    private final GrowthStageRepository growthStageRepository;
    
    public GrowthStageService(String rootPath) {
        super(rootPath);
        
        this.growthStageRepository = new GrowthStageRepository(rootPath);
    }
    
    @Override
    public void Parse() throws Exception{
        ArrayList<String> gStage = this.growthStageRepository.Parse();
        boolean isValid = true;
        GrowthStageList.Clear();
        
        for (int i = 0; i < gStage.size(); i++) {
            GrowthStage growth = new GrowthStage();
            String tmp = gStage.get(i);

            try {
                if (tmp.length() > 82) {
                    growth.Code = tmp.substring(0, 5).trim();
                    growth.Name = tmp.substring(5, 10).trim();
                    growth.Description = tmp.substring(12, 81).trim();

                    Crop crop = CropList.GetAtName(tmp.substring(82, tmp.length()));
                    if (crop != null) {
                        growth.crop = crop;
                        GrowthStageList.AddNew(growth);
                    }
                }
            } catch (Exception ex) {
                isValid = false;
            }
        }
        
        if(!isValid){
            throw new Exception("Growth Stage parse failed");
        }
    }
    
    @Override
    public String getName() {
        return "Growth Stage";
    }
}
