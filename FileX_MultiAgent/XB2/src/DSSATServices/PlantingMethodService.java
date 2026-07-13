package DSSATServices;

import DSSATRepository.PlantingMethodRepository;
import DSSATModel.PlantingMethod;
import DSSATModel.PlantingMethodList;
import java.util.ArrayList;

/**
 *
 * @author Jazzy
 */
public class PlantingMethodService extends DSSATServiceBase {
    private final PlantingMethodRepository plantingMethodRepository;
    public PlantingMethodService(String rootPath) {
        super(rootPath);
        
        this.plantingMethodRepository = new PlantingMethodRepository(rootPath);
    }
    
    @Override
    public void Parse() throws Exception{
        boolean isValid = true;
        
        try {
            ArrayList<String> plantingMethod = this.plantingMethodRepository.Parse();
            PlantingMethodList.Clear();
            
            for(int i = 0;i < plantingMethod.size();i++)
            {
                PlantingMethod plant = new PlantingMethod();
                String tmp = plantingMethod.get(i);

                plant.Code = tmp.substring(0, 5).trim();
                plant.Description = tmp.substring(9, 78).trim();
                PlantingMethodList.AddNew(plant);
            }
        } catch (Exception ex) {
            isValid = false;
        }
        
        if(!isValid){
            throw new Exception("Plating Method parse failed");
        }
    }
    
    @Override
    public String getName() {
        return "Planting Method";
    }
}
