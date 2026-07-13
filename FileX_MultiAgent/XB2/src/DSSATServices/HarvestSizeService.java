package DSSATServices;

import DSSATRepository.HarvestSizeRepository;
import DSSATModel.HarvestSize;
import DSSATModel.HarvestSizeList;
import java.util.ArrayList;

/**
 *
 * @author Jazzy
 */
public class HarvestSizeService extends DSSATServiceBase {
    private final HarvestSizeRepository harvestSizeRepository;
    
    public HarvestSizeService(String rootPath) {
        super(rootPath);
        
        this.harvestSizeRepository = new HarvestSizeRepository(rootPath);
    }
    
    @Override
    public void Parse() throws Exception{
        boolean isValid = true;
        
        try {
            ArrayList<String> harvestSizeList = this.harvestSizeRepository.Parse();
            HarvestSizeList.Clear();
            
            for(int i = 0;i < harvestSizeList.size();i++)
            {
                HarvestSize harvest = new HarvestSize();
                String tmp = harvestSizeList.get(i);

                try
                {
                    harvest.Code = tmp.substring(0, 5).trim();
                    harvest.Description = tmp.substring(9, tmp.length()-2).trim();
                    HarvestSizeList.AddNew(harvest);
                }
                catch(Exception ex) {
                    isValid = false;
                }
            }
        } catch (Exception ex) {
            throw ex;
        }
        
        if(!isValid){
            throw new Exception("Harvestze parse failed");
        }
    }
    
    @Override
    public String getName() {
        return "Harvest Size";
    }
}
