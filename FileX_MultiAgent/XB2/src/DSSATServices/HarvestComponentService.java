package DSSATServices;

import DSSATRepository.HarvestComponentRepository;
import DSSATModel.HarvestComponent;
import DSSATModel.HarvestComponentList;
import DSSATModel.Residues;
import DSSATModel.ResiduesList;
import java.util.ArrayList;

/**
 *
 * @author Jazzy
 */
public class HarvestComponentService extends DSSATServiceBase {
    private final HarvestComponentRepository harvestComponentRepository;
    
    public HarvestComponentService(String rootPath) {
        super(rootPath);
        
        this.harvestComponentRepository = new HarvestComponentRepository(rootPath);
    }
    
    @Override
    public void Parse() throws Exception{
        boolean isValid = true;
        
        try {
            ArrayList<String> harvestCompList = this.harvestComponentRepository.Parse();
            HarvestComponentList.Clear();
            
            for(int i = 0;i < harvestCompList.size();i++)
            {
                HarvestComponent harvest = new HarvestComponent();
                String tmp = harvestCompList.get(i);

                try
                {
                    harvest.Code = tmp.substring(0, 5).trim();
                    harvest.Description = tmp.substring(9, tmp.length()-2).trim();
                    //EnvironmentFactorList.factors[i] = env;
                    HarvestComponentList.AddNew(harvest);
                }
                catch(Exception ex) {
                    isValid = false;
                }
            }
        } catch (Exception ex) {
            throw ex;
        }
        
        if(!isValid){
            throw new Exception("Harvest Component parse failed");
        }
    }
    
    @Override
    public String getName() {
        return "Harvest Component";
    }
}
