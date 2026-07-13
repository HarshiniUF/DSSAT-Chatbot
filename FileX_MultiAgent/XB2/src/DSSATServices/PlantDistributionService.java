package DSSATServices;

import DSSATRepository.PlantDistributionRepository;
import DSSATModel.PlantDistribution;
import DSSATModel.PlantDistributionList;
import java.util.ArrayList;

/**
 *
 * @author Jazzy
 */
public class PlantDistributionService extends DSSATServiceBase {
    private final PlantDistributionRepository plantDistributionRepository;
    
    public PlantDistributionService(String rootPath) {
        super(rootPath);
        
        this.plantDistributionRepository = new PlantDistributionRepository(rootPath);
    }
    
    @Override
    public void Parse() throws Exception{
        boolean isValid = true;
        
        try {
            ArrayList<String> plantDistribution = this.plantDistributionRepository.Parse();
            PlantDistributionList.Clear();
            
            for(int i = 0;i < plantDistribution.size();i++)
            {
                PlantDistribution plant = new PlantDistribution();
                String tmp = plantDistribution.get(i);

                plant.Code = tmp.substring(0, 5).trim();
                plant.Description = tmp.substring(9, 78).trim();
                PlantDistributionList.AddNew(plant);
            }
        } catch (Exception ex) {
            isValid = false;
        }
        
        if(!isValid){
            throw new Exception("Plant Distribtion parse failed");
        }
    }
    
    @Override
    public String getName() {
        return "Plant Distribtion";
    }
}
