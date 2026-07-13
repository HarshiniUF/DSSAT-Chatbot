package DSSATServices;

import DSSATRepository.SimulationRepository;
import DSSATModel.CropModel;
import DSSATModel.CropModelList;
import java.util.ArrayList;

/**
 *
 * @author Jazzy
 */
public class SimulationService extends DSSATServiceBase {
    private final SimulationRepository simulationRepository;
    
    public SimulationService(String rootPath) {
        super(rootPath);
   
        this.simulationRepository = new SimulationRepository(rootPath);
    }
    
    @Override
    public void Parse() throws Exception{
        boolean isValid = true;
        
        try {
            ArrayList<String> cropModel = this.simulationRepository.Parse();
            CropModelList.Clear();
            
            for(int i = 0;i < cropModel.size();i++)
            {
                CropModel cModel = new CropModel();
                String tmp = cropModel.get(i);

                cModel.ModelCode = tmp.substring(0, 6).trim();
                cModel.Code = tmp.substring(8, 11).trim();
                try
                {
                    cModel.Description = tmp.substring(14, tmp.length()).trim();
                }
                catch(Exception ex)
                {
                    cModel.Description = "";
                }
                CropModelList.AddNew(cModel);
            }
        } catch (Exception ex) {
            throw ex;
        }
        
        if(!isValid){
            throw new Exception("Crop Model parse failed");
        }
    }
    
    @Override
    public String getName() {
        return "Crop Model";
    }
}
